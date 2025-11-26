# app.py
import os
import csv
import yaml
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from netmiko import ConnectHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# Create directories
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'backup.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Form Classes
class DeviceForm(FlaskForm):
    ip = StringField('IP Address', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    device_type = StringField('Device Type (e.g., cisco_ios)', default='cisco_ios')
    submit = SubmitField('Backup Now')

class UploadForm(FlaskForm):
    file = FileField('Upload CSV or YAML', validators=[
        DataRequired(),
        FileAllowed(['csv', 'yaml', 'yml'], 'Only CSV and YAML files allowed!')
    ])
    submit = SubmitField('Upload & Backup')

# Helper: Validate and parse CSV
def parse_csv(file_path):
    devices = []
    try:
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('ip') or not row.get('username') or not row.get('password'):
                    return False, "CSV missing required fields (ip, username, password)"
                devices.append({
                    'ip': row['ip'],
                    'username': row['username'],
                    'password': row['password'],
                    'device_type': row.get('device_type', 'cisco_ios')
                })
        return True, devices
    except Exception as e:
        return False, str(e)

# Helper: Validate and parse YAML
def parse_yaml(file_path):
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
            if not isinstance(data, list):
                return False, "YAML must contain a list of devices"
            for dev in data:
                if not dev.get('ip') or not dev.get('username') or not dev.get('password'):
                    return False, "YAML device missing required fields"
            return True, data
    except Exception as e:
        return False, str(e)

# Helper: Backup a single device
def backup_device(device_info):
    try:
        connection = ConnectHandler(
            device_type=device_info['device_type'],
            host=device_info['ip'],
            username=device_info['username'],
            password=device_info['password']
        )
        connection.enable()
        output = connection.send_command("show running-config")
        connection.disconnect()

        # Save backup
        filename = f"{device_info['ip']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
        filepath = os.path.join(BACKUP_DIR, filename)
        with open(filepath, 'w') as f:
            f.write(output)

        logging.info(f"Backup successful for {device_info['ip']}")
        return True, f"Backup saved as {filename}"
    except Exception as e:
        error_msg = f"Failed to backup {device_info['ip']}: {str(e)}"
        logging.error(error_msg)
        return False, error_msg

@app.route('/')
def index():
    return render_template('index.html', year=datetime.now().year)

@app.route('/manual', methods=['GET', 'POST'])
def manual_backup():
    form = DeviceForm()
    if form.validate_on_submit():
        device = {
            'ip': form.ip.data,
            'username': form.username.data,
            'password': form.password.data,
            'device_type': form.device_type.data
        }
        success, msg = backup_device(device)
        if success:
            flash(f"✅ Backup successful: {msg}", "success")
        else:
            flash(f"❌ Backup failed: {msg}", "danger")
        return redirect(url_for('manual_backup'))
    return render_template('manual.html', form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        if file.filename.endswith('.csv'):
            valid, data = parse_csv(filepath)
        elif file.filename.endswith('.yaml') or file.filename.endswith('.yml'):
            valid, data = parse_yaml(filepath)
        else:
            flash("❌ Unsupported file type.", "danger")
            return redirect(url_for('upload_file'))

        if not valid:
            flash(f"❌ File validation failed: {data}", "danger")
            return redirect(url_for('upload_file'))

        # Start backup for all devices
        results = []
        for device in data:
            success, msg = backup_device(device)
            status = "✅ Success" if success else "❌ Failed"
            results.append(f"{device['ip']} - {status}: {msg}")

        for res in results:
            flash(res, "info")

        return redirect(url_for('upload_file'))

    return render_template('upload.html', form=form)

@app.route('/status')
def status():
    backups = os.listdir(BACKUP_DIR)
    backups.sort(reverse=True)
    log_content = ""
    log_path = os.path.join(LOG_DIR, 'backup.log')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_content = f.readlines()[-50:]  # last 50 lines
    return render_template('status.html', backups=backups, logs=log_content)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)