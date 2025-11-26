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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_strong_secret_key_here")
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
    device_type = StringField('Device Type', default='cisco_ios')
    submit = SubmitField('Backup Now')

class UploadForm(FlaskForm):
    file = FileField('Upload CSV or YAML', validators=[
        DataRequired(),
        FileAllowed(['csv', 'yaml', 'yml'], 'Only CSV and YAML files allowed!')
    ])
    submit = SubmitField('Upload & Backup')

# Helper: Parse CSV
def parse_csv(file_path):
    devices = []
    try:
        with open(file_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get('ip') or not row.get('username') or not row.get('password'):
                    return False, "CSV missing required fields"
                devices.append({
                    'ip': row['ip'],
                    'username': row['username'],
                    'password': row['password'],
                    'device_type': row.get('device_type', 'cisco_ios')
                })
        return True, devices
    except Exception as e:
        return False, str(e)

# Helper: Parse YAML
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

# Scheduled Backup Function
def scheduled_backup_job(devices):
    for device in devices:
        success, msg = backup_device(device)
        if success:
            logging.info(f"Scheduled Backup Success: {device['ip']} - {msg}")
        else:
            logging.error(f"Scheduled Backup Failed: {device['ip']} - {msg}")

# Initialize Scheduler
scheduler = BackgroundScheduler()
scheduled_job = None  # Global variable to track the job

@app.route('/')
def index():
    year = datetime.now().year
    return render_template('index.html', year=year)

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

        results = []
        for device in data:
            success, msg = backup_device(device)
            status = "✅ Success" if success else "❌ Failed"
            results.append(f"{device['ip']} - {status}: {msg}")

        for res in results:
            flash(res, "info")

        return redirect(url_for('upload_file'))

    return render_template('upload.html', form=form)

@app.route('/schedule', methods=['GET', 'POST'])
def schedule_backup():
    global scheduled_job  # ✅ শুধুমাত্র একবার

    if request.method == 'POST':
        hour = request.form.get('hour')
        minute = request.form.get('minute')

        if not hour or not minute:
            flash("❌ Please select both hour and minute.", "danger")
            return redirect(url_for('schedule_backup'))

        try:
            hour = int(hour)
            minute = int(minute)
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError
        except ValueError:
            flash("❌ Invalid time selected.", "danger")
            return redirect(url_for('schedule_backup'))

        sample_devices = [
            {'ip': '192.168.1.1', 'username': 'admin', 'password': 'secret', 'device_type': 'cisco_ios'},
            {'ip': '192.168.1.2', 'username': 'admin', 'password': 'secret', 'device_type': 'cisco_ios'}
        ]

        # Remove old job
        if scheduled_job:
            scheduler.remove_job(scheduled_job.id)

        # Add new job
        job = scheduler.add_job(
            func=scheduled_backup_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[sample_devices],
            id='cisco_backup_job',
            replace_existing=True,
            name='Daily Cisco Backup'
        )

        scheduled_job = job  # ✅ শুধু অ্যাসাইন

        flash(f"✅ Backup scheduled daily at {hour:02d}:{minute:02d}!", "success")
        return redirect(url_for('schedule_backup'))

    next_run = scheduled_job.next_run_time.strftime('%H:%M') if scheduled_job else "Not set"
    return render_template('schedule.html', next_run=next_run)

@app.route('/cancel_schedule')
def cancel_schedule():
    global scheduled_job
    if scheduled_job:
        scheduler.remove_job(scheduled_job.id)
        scheduled_job = None
        flash("⏸️ Backup schedule canceled.", "info")
    else:
        flash("❌ No active schedule to cancel.", "warning")
    return redirect(url_for('schedule_backup'))

@app.route('/status')
def status():
    backups = os.listdir(BACKUP_DIR)
    backups.sort(reverse=True)
    log_content = ""
    log_path = os.path.join(LOG_DIR, 'backup.log')
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_content = f.readlines()[-50:]
    return render_template('status.html', backups=backups, logs=log_content)

# Start scheduler when app starts
if not scheduler.running:
    scheduler.start()

# Shut down the scheduler when exiting
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)