# 📒 Vyapar : DigiKhata - Digital Business Ledger & SME Tool suite

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![UI Engine](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Database Engine](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Theme Integration](https://img.shields.io/badge/UI--Theme-Light%20Blue%20%7C%20Dark%20Compatible-0284C7)](#)

**Vyapar: DigiKhata** is a full-stack digital ledger, inventory controller, and automated financial tracking software engineered to modernize retail accounting for small-to-medium enterprises (SMEs) and shopkeepers. Replacing traditional, physical book notebooks (*Bahi Khata*), the application provides relational transaction logging, smart credit management, automated notification prompts, and real-time operational analytics.

---

## 📌 Core System Modules & Architecture

### 📊 1. Relational Digital Ledger & Customer Hub
- **Credit & Debit Tracking:** Instantly record transactions mapping customer parameters to specific business transaction flags (`Credit` / `Debit`) without risk of mathematical errors.
- **Dynamic Ledger Balances:** Automatically computes aggregated net balances per consumer profile, identifying high-priority debtors at a glance.
- **Supplier Balancing Terminal:** Contains dedicated data structures to manage merchant-to-vendor relationships, auditing totals due against total historical payments.

### 🔔 2. Multi-Stage Automated Recovery Engine
- **Overdue Threshold Scanners:** Background logic continuously updates customer logs, checking the chronological gap since the last payment entry.
- **Tone-Adjusted Notifications:** Generates contextual notification logs via **WhatsApp/SMS format templates** categorized by risk levels:
  - **Day 10 (Reminder):** Light, supportive payment alerts.
  - **Day 20 (Important):** Business-standard balance requests.
  - **Day 30+ (Urgent):** Immediate attention demands.

### 📦 3. Live Inventory Monitor & Email Alerts
- **Stock Tracking:** Continuous auditing of unit quantities, item names, and cost parameters.
- **SMTP Notification Pipeline:** Hooks directly into Python’s built-in `smtplib` and `MIME` multipart formatting to transmit immediate Low Stock alerts and customer ledger summaries straight to the merchant's registered email.

### 📈 4. Administrative Insights & Portability
- **Dynamic Visualization:** Leverages robust data parsing libraries to display interactive historical sales logs, operational charts, and performance trends over adjustable date filters.
- **Single-Click Backups:** Features automated file mapping through memory buffers, allowing administrators to export complete business profiles directly to `.csv` spreadsheets.

---

## 🛠️ Project Architecture

```text
├── app.py                  # Main orchestration script & system styling config
├── login.py                # Onboarding authentication portal & email format checkers
├── sign_up.py              # Retail registration engine & session initializing managers
├── dashboard.py            # Analytics layouts, chart rendering, and transactional hubs
├── settings.py             # Shop properties, configurations, and notification alerts
├── database.py             # Core SQLite3 schema deployments & structural SQL queries
├── auto_reminders.py       # Recovery timing calculations & message templates
├── email_helper.py         # SMTP network controllers & HTML email structure generators
└── add_test_data.py        # Automated testing suite to initialize clean sandbox data
