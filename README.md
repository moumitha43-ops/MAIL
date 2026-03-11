# 🎂 Birthday Wishes App — BIT

A Flask-based web application that automatically detects student/staff birthdays from a CSV file and sends personalised birthday card emails via the Gmail API.

---

## 📁 Project Structure

```
birthday_wishes_project/
├── app.py                  # Flask routes & entry point
├── helpers.py              # Config, logging, date utilities
├── matcher.py              # CSV parsing & birthday matching
├── scheduler.py            # APScheduler background scheduler
├── send.py                 # Gmail API email sending + Playwright card rendering
├── config.json             # Runtime configuration (auto-generated)
├── template.html           # Birthday card HTML template (editable via UI)
├── sample_data.csv         # Example CSV to test with
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Full-featured admin dashboard (single-page app)
├── static/                 # Static assets (CSS/JS if needed)
├── uploads/                # Uploaded CSV files stored here
├── output/                 # Rendered HTML cards + PNG screenshots
└── logs/
    ├── app.log             # Rotating application log
    └── sent_today.log      # Duplicate-send guard log
```

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Chromium (for card rendering)

```bash
playwright install chromium
```

### 3. Set Up Gmail API

The app uses the Gmail API (OAuth2) to send emails — **not** SMTP.

**Steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable **Gmail API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Run the one-time auth flow to get a `token.json`
5. Export the token as an environment variable:

```bash
# Linux/macOS
export GOOGLE_TOKEN_JSON='{"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"..."}'

# Windows PowerShell
$env:GOOGLE_TOKEN_JSON = '{"token":"...","refresh_token":"...",...}'
```

Or create a `.env` file in the project root:
```
GOOGLE_TOKEN_JSON={"token":"...","refresh_token":"...","token_uri":"...","client_id":"...","client_secret":"..."}
```

### 4. Run the App

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 🖥️ Dashboard Features

### 🔐 Authentication Gate
- **Sign In** — email + password (stored locally in browser localStorage)
- **Sign Up** — 3-step wizard:
  - Step 1: Name, email, password (with strength meter)
  - Step 2: Gmail address + App Password
  - Step 3: Review & confirm
- Auto-login on page reload via session token
- Sign Out clears session and stops auto-refresh

### 🏠 Dashboard
- Today's birthday matches shown in a table
- Stats: matches today / total rows / skipped rows
- **Send Birthday Wishes** button with live progress bar
- **Auto-Refresh toggle** — polls `/api/matches` every 30 seconds
- **Preview Cards** button — opens card preview modal

### 🎴 Card Preview Modal
- Select any person from today's birthday list
- Live renders the HTML template with `{{name}}` substituted
- Click 🎴 in any table row to preview that specific person

### 📋 CSV Manager
- Drag-and-drop or click-to-upload CSV files
- Inline validation results table (valid rows + error rows)
- Required columns: `name`, `email`, `dob` (or `date_of_birth`)
- Optional column: `rollnumber` (or `roll_number`)

### 🎨 Card Template Editor
- Upload images → get base64 data URIs to embed in the template
- Edit HTML directly in the browser
- Use `{{name}}` placeholder for personalisation
- Save changes live

### ⚙️ Settings
- SMTP server, port, sender email, Gmail App Password
- Auto-send scheduler: enable/disable, set send time, timezone
- Shows next scheduled run time

### 📜 Logs
- Live log viewer — last 150 lines
- Colour-coded: sent (green), errors (red), warnings (yellow), info (blue)

---

## 📄 CSV Format

```csv
name,email,dob,rollnumber
Arjun Kumar,arjun.kumar@example.com,07-03-2000,21CS001
Priya Sharma,priya.sharma@example.com,15-06-2001,21CS002
```

| Column | Required | Format | Notes |
|--------|----------|--------|-------|
| `name` | ✅ | Text | Full name |
| `email` | ✅ | Valid email | Recipient address |
| `dob` | ✅ | DD-MM-YYYY or DD/MM/YYYY | Date of birth |
| `rollnumber` | ❌ | Text | Student/staff roll number |

---

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the dashboard |
| POST | `/api/csv/upload` | Upload a CSV file |
| GET | `/api/csv/validate` | Validate current CSV |
| GET | `/api/matches` | Get today's birthday matches |
| POST | `/api/send` | Trigger email sending |
| GET | `/api/send/status` | Poll send job progress |
| GET | `/api/settings` | Get current settings |
| POST | `/api/settings` | Update settings |
| GET | `/api/template` | Get card template HTML |
| POST | `/api/template` | Save card template HTML |
| POST | `/api/template/upload-image` | Upload image → base64 URI |
| GET | `/api/logs?lines=N` | Get last N log lines |

---

## 🌐 Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_TOKEN_JSON` | Gmail OAuth2 token JSON string (required for sending) |
| `PORT` | Server port (default: `5000`) |
| `SMTP_SERVER` | SMTP server (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `EMAIL_SENDER` | Sender email address |
| `EMAIL_APP_PASSWORD` | Gmail App Password |
| `SEND_TIME` | Default send time `HH:MM` (default: `08:00`) |
| `TIMEZONE` | Timezone string (default: `Asia/Kolkata`) |

---

## 🏗️ How It Works

```
Browser (index.html)
      │
      ▼
Flask (app.py)
   ├── /api/matches ──► matcher.py ──► reads CSV, compares today's date
   ├── /api/send   ──► send.py
   │                     ├── Playwright renders template.html → PNG
   │                     └── Gmail API sends email with PNG attachment
   └── /api/settings ──► helpers.py ──► config.json
         │
         └── scheduler.py (APScheduler) ──► runs daily at configured time
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `werkzeug` | File handling utilities |
| `apscheduler` | Background task scheduler |
| `playwright` | Headless Chromium for card rendering |
| `google-auth` | Gmail API OAuth2 authentication |
| `google-api-python-client` | Gmail API client |
| `python-dotenv` | `.env` file support |

---

## 🔒 Security Notes

- **Gmail App Password** is stored in `config.json` on disk — protect this file
- **Auth is localStorage-only** (browser-side) — suitable for local/intranet deployment
- For production multi-user deployments, replace with server-side auth (Flask-Login / JWT)
- The `GOOGLE_TOKEN_JSON` env var contains sensitive credentials — never commit to git

---

*Built for Bannari Amman Institute of Technology (BIT)*
