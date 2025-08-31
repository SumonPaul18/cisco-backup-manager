# Cisco Backup Manager

A simple web-based tool to backup Cisco routers and switches. You can manually enter device details or upload a CSV/YAML file to backup multiple devices at once.

🌐 **Live Demo**: [Coming Soon]  
🛠️ **Built with**: Python, Flask, Netmiko  
📁 **GitHub Repo**: https://github.com/SumonPaul18/cisco-backup-manager.git

---

## 📥 How to Download and Run the App

Follow these easy steps to run the Cisco Backup Manager on your computer.

### Step 1: Clone the Repository

Open your terminal (or Command Prompt) and run:

```bash
git clone https://github.com/SumonPaul18/cisco-backup-manager.git
cd cisco-backup-manager
```

---

## Now Open Terminal from the Project Folder

### Step 2: Create a Virtual Environment

It's best to keep the app's files separate from your system.

```bash
python -m venv venv
```

#### Activate the Virtual Environment:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

---

### Step 3: Install Required Packages

Install all the needed tools using `pip`:

```bash
pip install -r requirements.txt
```

> 💡 If you get an error with `pyyaml`, try:
> ```bash
> pip install --only-binary=pyyaml pyyaml
> ```

---

### Step 4: Configure the App

1. Open the `.env` file in a text editor.
2. Change the `SECRET_KEY` to any random text (e.g., `abc123xyz`).
3. Save the file.

> 🔐 This key keeps your app secure. Don't share it!

---

### Step 5: Run the Application

Start the web server:

```bash
python app.py
```

You will see something like:

```
 * Running on http://127.0.0.1:5000
```

---

### Step 6: Open in Your Browser

Go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

You can now:
- Enter device info and click **Backup Now**
- Upload a CSV or YAML file for bulk backup
- View backup status and logs

---

## 📁 Where Are Backups Saved?

All backup files are saved in the `backups/` folder.  
Each file is named like: `192.168.1.1_20250405_142301.cfg`

---

## 📄 File Format Examples

### CSV File (`devices.csv`)
```csv
ip,username,password,device_type
192.168.1.1,admin,secret,cisco_ios
192.168.1.2,admin,secret,cisco_nxos
```

### YAML File (`devices.yaml`)
```yaml
- ip: 192.168.1.1
  username: admin
  password: secret
  device_type: cisco_ios
- ip: 192.168.1.2
  username: admin
  password: secret
  device_type: cisco_nxos
```

> ✅ Supported file types: `.csv`, `.yaml`, `.yml`

---

## 🛠️ Features

- ✅ Manual device backup via web form
- ✅ Upload CSV or YAML for bulk backup
- ✅ Backup status and logs
- ✅ Secure and easy-to-use interface
- ✅ Works with Cisco IOS, NX-OS, and more

---

## ⚠️ Requirements

- Python 3.7 or higher
- SSH access to your Cisco devices
- Devices must allow SSH login with username/password

---

## 📝 Notes

- Make sure your computer can reach the Cisco devices via network.
- For security, never commit `.env` or password files to GitHub.
- Logs are saved in the `logs/` folder.

---

## 🙌 Support

Have questions or need help?  
Open an issue on GitHub:  
👉 https://github.com/SumonPaul18/cisco-backup-manager/issues

---

## 📜 License

This project is open source and available for personal and commercial use.

---

🚀 Thank you for using **Cisco Backup Manager**!

---
