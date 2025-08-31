# Cisco Backup Manager

A simple web tool to backup Cisco router and switch configurations easily.  
You can enter device details manually or upload a CSV/YAML file to backup multiple devices at once.

---

## 🚀 Features

- ✅ Backup Cisco devices (routers & switches) via SSH
- ✅ Manual form to enter IP, username, password
- ✅ Upload CSV or YAML file for bulk backup
- ✅ View backup status and logs
- ✅ Clean and user-friendly web interface
- ✅ Save running-config automatically

---

## 🛠️ How to Install

1. **Clone or create the project folder**
   ```bash
   mkdir cisco_backup_app
   cd cisco_backup_app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Create `requirements.txt`** with the following content:
   ```txt
   Flask==3.0.0
   Flask-WTF==1.2.1
   Flask-Bootstrap==3.3.7.1
   python-dotenv==1.0.1
   netmiko==4.4.0
   pyyaml
   ```

4. **Install the packages**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔐 Setup Environment

Create a file named `.env` in your project folder:
```env
SECRET_KEY=your_strong_secret_key_here
BACKUP_DIR=backups
LOG_DIR=logs
```

> Replace `your_strong_secret_key_here` with any random text (e.g., `abc123xyz456`).

---

## 📁 Folder Structure

After setup, your project should look like this:
```
cisco_backup_app/
├── app.py
├── .env
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── manual.html
│   ├── upload.html
│   └── status.html
├── backups/          # Saved configs
├── logs/             # Log files
└── uploads/          # Uploaded CSV/YAML files
```

---

## 🖥️ Run the App

```bash
python app.py
```

Open your browser and go to:  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧩 How to Use

### 1. **Manual Backup**
- Go to **Home Page**
- Enter:
  - Device IP Address
  - Username
  - Password
  - Device Type (e.g., `cisco_ios`)
- Click **Backup Now**

✅ Configuration will be saved in the `backups/` folder.

---

### 2. **Upload CSV or YAML File**

#### 📄 CSV Format (`devices.csv`)
```csv
ip,username,password,device_type
192.168.1.1,admin,pass,cisco_ios
192.168.1.2,admin,pass,cisco_ios
```

#### 📄 YAML Format (`devices.yaml`)
```yaml
- ip: 192.168.1.1
  username: admin
  password: pass
  device_type: cisco_ios
- ip: 192.168.1.2
  username: admin
  password: pass
  device_type: cisco_ios
```

- Go to **Upload File** page
- Upload your CSV or YAML file
- The app will validate and backup all devices

---

### 3. **View Status & Logs**
- Click **Status & Logs**
- See:
  - List of saved backup files
  - Recent logs (success/failure)

---

## ⚠️ Requirements

- Python 3.7 or higher
- SSH access to your Cisco devices
- Devices must allow `show running-config` command
- Enable password (if used) should be set in Netmiko (advanced)

---

## 💡 Tips

- Keep your `.env` file private (don’t share it)
- Regularly backup the `backups/` folder
- Use strong passwords and secure network

---

## 📬 Feedback & Support

If you find any issue or need help, feel free to contact.

Made with ❤️ for Network Engineers.
```

---