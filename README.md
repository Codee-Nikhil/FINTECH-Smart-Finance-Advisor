# FinTech — Smart Finance Advisor 💰

> A full-stack AI-powered personal finance advisor built for India.
> **Frontend:** HTML, CSS, JavaScript | **Backend:** Python Flask + SQLite | **AI:** Claude (Anthropic)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Claude AI](https://img.shields.io/badge/Claude%20AI-Anthropic-FF6B35?style=flat)

---

## 📌 Project Overview

**FinTech** is a complete full-stack personal finance management web app that uses **Claude AI** to give personalized financial advice based on the user's actual income, expenses, and goals — designed specifically for the **Indian financial market**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Auth System | Register / Login with JWT token authentication |
| 📊 Dashboard | Health score, income, expenses, savings metrics |
| 💸 Budget Planner | 10 default + unlimited custom expense categories |
| 🎯 Goals Tracker | Financial goals with progress bars and projections |
| 📈 SIP Calculator | Mutual fund SIP calculator with visual charts |
| 🏦 Investment Guide | PPF, FD, NPS, ELSS, RD option cards |
| 🤖 AI Advisor | Claude AI chatbot with chat history saved to DB |
| 💾 Auto Save | Budget auto-saves to database as you type |
| 📱 Responsive | Works on mobile, tablet, and desktop |

---

## 📁 Project Structure

```
smart-finance-advisor/
├── login.html                  ← Login / Register page
├── index.html                  ← Main dashboard (protected)
├── css/
│   └── style.css
├── js/
│   ├── api.js                  ← All API calls to Flask backend
│   ├── state.js                ← Data model & computed values
│   ├── charts.js               ← Chart.js visualizations
│   ├── ui.js                   ← DOM rendering
│   ├── advisor.js              ← AI chat helpers
│   └── app.js                  ← App init + backend integration
└── backend/
    ├── app.py                  ← Flask entry point
    ├── config.py               ← Config (DB, JWT, API key)
    ├── database.py             ← SQLAlchemy instance
    ├── models.py               ← User, Budget, Expense, Goal, ChatLog
    ├── requirements.txt        ← Python packages
    ├── .env.example            ← Env variable template
    └── routes/
        ├── auth.py             ← Register, login, profile
        ├── budget.py           ← Income & expenses CRUD
        ├── goals.py            ← Financial goals CRUD
        ├── advisor.py          ← Claude AI chat
        └── dashboard.py        ← Summary & health score
```

---

## 🚀 Setup Guide (Step by Step)

### Prerequisites
- Python 3.8+ installed
- VS Code with Live Server extension
- Free Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

---

### Step 1 — Open the backend folder in terminal

```bash
cd smart-finance-advisor/backend
```

### Step 2 — Create and activate virtual environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

### Step 3 — Install Python packages

```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

```bash
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

Open `.env` and fill in:

```env
SECRET_KEY=any-random-string
JWT_SECRET_KEY=another-random-string
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 5 — Run the Flask backend

```bash
python app.py
```

You'll see:
```
✅ Database tables created.
 * Running on http://127.0.0.1:5000
```

**Keep this terminal open.**

### Step 6 — Open the frontend

- Right-click `login.html` → **Open with Live Server**
- Browser opens at `http://127.0.0.1:5500/login.html`
- Register an account and start using FinTech!

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login and get JWT |
| GET | `/api/auth/profile` | Get user profile |
| GET | `/api/budget/` | Get budget for a month |
| POST | `/api/budget/save` | Bulk save all expenses |
| GET | `/api/goals/` | Get all goals |
| POST | `/api/goals/` | Add new goal |
| DELETE | `/api/goals/<id>` | Delete a goal |
| POST | `/api/advisor/chat` | Send message to Claude AI |
| GET | `/api/advisor/history` | Get chat history |
| GET | `/api/dashboard/summary` | Full dashboard data |

---

## 🗄️ Database Schema

```
users      → id, name, email, password_hash, city_type, created_at
budgets    → id, user_id, month, year, income
expenses   → id, budget_id, category, actual, budget_amt
goals      → id, user_id, name, target, saved, goal_type, target_date
chat_logs  → id, user_id, role, message, created_at
```

---

## 🐙 Push to GitHub

```bash
git init
git add .
git commit -m "FinTech: Full Stack Finance Advisor — Final Year Project"
git remote add origin https://github.com/YOUR_USERNAME/smart-finance-advisor.git
git branch -M main
git push -u origin main
```

> ⚠️ Never push your `.env` file — it's already in `.gitignore`!

---

## 🎓 Academic Info

- **Project:** Final Year Project — B.Tech / BCA / MCA
- **Domain:** FinTech, Full Stack Web Dev, AI Integration
- **Stack:** Python Flask, SQLAlchemy, JWT, HTML/CSS/JS, Claude AI

---

## 👨‍💻 Author

**[Your Name]** · [Your College] · [Branch] · [Roll No]

> Built with ❤️ for India | Python Flask + Claude AI (Anthropic)

---

## 🚀 Deployment Guide (Live URL for Resume)

### Backend → Railway.app (Free)

**Step 1** — Go to [railway.app](https://railway.app) and sign up with GitHub

**Step 2** — Push your code to GitHub first:
```bash
git init
git add .
git commit -m "FinTech v3.0 - Full Stack Finance Advisor"
git remote add origin https://github.com/YOUR_USERNAME/smart-finance-advisor.git
git branch -M main
git push -u origin main
```

**Step 3** — On Railway:
1. Click **"New Project"**
2. Click **"Deploy from GitHub repo"**
3. Select your `smart-finance-advisor` repo
4. Set **Root Directory** to `backend`
5. Railway auto-detects Flask and deploys!

**Step 4** — Add PostgreSQL database:
1. In Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway auto-sets `DATABASE_URL` environment variable

**Step 5** — Set environment variables in Railway:
```
SECRET_KEY          = any-random-string
JWT_SECRET_KEY      = another-random-string
GEMINI_API_KEY      = your-gemini-key
EMAIL_USER          = your-gmail@gmail.com
EMAIL_PASS          = your-app-password
```

**Step 6** — Get your live URL:
- Railway gives you: `https://your-app.up.railway.app`
- Test it: `https://your-app.up.railway.app/api/health`

---

### Frontend → Netlify (Free)

**Step 1** — Go to [netlify.com](https://netlify.com) and sign up

**Step 2** — Update `js/api.js` — replace the Railway URL:
```javascript
: 'https://YOUR-APP-NAME.up.railway.app/api';
```

**Step 3** — Deploy:
1. Click **"Add new site"** → **"Import from Git"**
2. Connect GitHub → select your repo
3. **Build command:** leave empty
4. **Publish directory:** `/` (root)
5. Click **"Deploy site"**

**Step 4** — Get your live URL:
- Netlify gives you: `https://fintech-yourname.netlify.app`

---

### Your Resume Line (after deploy):
```
FinTech — Full Stack Finance Advisor
Live: https://fintech-yourname.netlify.app
GitHub: https://github.com/YOUR_USERNAME/smart-finance-advisor
Stack: Python Flask, SQLAlchemy, JWT Auth, Gemini AI, PostgreSQL, Chart.js
```
