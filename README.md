# 🛡️ ThreatScan — AI-Powered Security Intelligence Platform

<div align="center">

![ThreatScan Banner](https://img.shields.io/badge/ThreatScan-Security%20Intelligence-00d4ff?style=for-the-badge&logo=shield&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A comprehensive cybersecurity platform that detects threats across email, URLs, IPs, files, and phone numbers using AI and real-time threat intelligence APIs.**

[🌐 Live Demo](https://threatsca-v6fh.onrender.com) • [📋 Report Bug](https://github.com/AyushSingh338/threatscan/issues) • [✨ Request Feature](https://github.com/AyushSingh338/threatscan/issues)

</div>

---

## 📸 Screenshots

| Login Page | Dashboard | Phone Analyzer |
|---|---|---|
| Secure login/signup | Multi-tab scanner | Number fraud detection |

---

## ✨ Features

- 🔐 **User Authentication** — Secure login/signup with SHA-256 hashed passwords
- 📧 **Email/Phishing Analyzer** — AI-powered spam & phishing detection using Random Forest ML
- 🔗 **URL Scanner** — Real-time URL reputation check via VirusTotal (70+ AV engines)
- 🌐 **IP Address Lookup** — IP threat intelligence and geolocation
- 📁 **File Scanner** — Multi-engine malware scanning via VirusTotal
- 📞 **Phone Number Analyzer** — Fraud detection via IPQualityScore + NumVerify
- 👤 **Admin Panel** — View all registered users at `/admin/users`
- 📄 **Report Generation** — Download security scan reports
- ☁️ **Cloud Deployed** — Live on Render.com with Supabase PostgreSQL

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.0.3, Gunicorn |
| **ML** | scikit-learn, TF-IDF, Random Forest |
| **Database** | SQLite (local) / PostgreSQL via Supabase (cloud) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **APIs** | VirusTotal v3, IPQualityScore, NumVerify |
| **Deployment** | Render.com + GitHub CI/CD |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/AyushSingh338/threatscan.git
cd threatscan
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Train the ML model
```bash
python train.py --dataset your_dataset.csv
```
> Dataset must have `text` and `label` columns (spam/ham or 1/0)

### 5. Run the app
```bash
python app.py
```

Open browser: **http://localhost:5000**

Admin panel: **http://localhost:5000/admin/users**

---

## 📁 Project Structure

```
threatscan/
├── app.py              ← Main Flask server (routes, auth, API proxy)
├── train.py            ← ML model training script
├── index.html          ← Frontend single-page application
├── requirements.txt    ← Python dependencies
├── Dockerfile          ← Container config for cloud deployment
├── .gitignore
└── data/
    ├── users.db        ← SQLite database (auto-created)
    ├── model.pkl       ← Trained Random Forest model
    └── vectorizer.pkl  ← TF-IDF vectorizer
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve main web app |
| `POST` | `/auth/register` | User registration |
| `POST` | `/auth/login` | User login |
| `GET` | `/admin/users` | Admin — view all users |
| `POST` | `/analyze_email` | ML email/phishing analysis |
| `POST` | `/analyze_number` | Phone fraud detection |
| `GET/POST` | `/vt/<path>` | VirusTotal API proxy |
| `POST` | `/save_report` | Generate scan report |

---

## 🤖 Machine Learning

The email analyzer uses a **Random Forest Classifier** trained on labeled spam datasets:

- **Vectorization:** TF-IDF with 5,000 features (English stop words removed)
- **Custom Features:** Link count, suspicious keyword count, message length
- **Model:** 150 decision trees, trained with scikit-learn
- **Accuracy:** ~96.8% on test set

```
Email Text
    ↓
TF-IDF Vectorizer + Custom Features
    ↓
Random Forest (150 trees)
    ↓
SPAM / PHISHING   or   SAFE
```

---

## 🔑 API Keys

The following API keys are required (free tiers available):

| API | Purpose | Get Key |
|---|---|---|
| VirusTotal | URL, IP, File scanning | [virustotal.com](https://virustotal.com) |
| IPQualityScore | Phone fraud detection | [ipqualityscore.com](https://ipqualityscore.com) |
| NumVerify | Phone validation | [numverify.com](https://numverify.com) |

Set as environment variables or update directly in `app.py`:
```bash
export VT_API_KEY=your_virustotal_key
export IPQS_KEY=your_ipqualityscore_key
export NUMVERIFY_KEY=your_numverify_key
```

---

## ☁️ Deploy to Render.com

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repository
4. Set build & start commands:
   ```
   Build:  pip install -r requirements.txt
   Start:  gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Add environment variables (API keys)
6. Deploy! 🚀

---

## 🗄️ Database

**Local (SQLite):** Auto-created at `data/users.db` — no setup needed.

**Cloud (Supabase PostgreSQL):**
1. Create project at [supabase.com](https://supabase.com)
2. Get connection string from Settings → Database
3. Set as `DATABASE_URL` environment variable on Render

**View users locally:**
```bash
# Option 1: VS Code — install "SQLite Viewer" extension, click users.db
# Option 2: Terminal
sqlite3 data/users.db "SELECT id, name, email, created_at FROM users;"
```

---

## 🔒 Security

- Passwords hashed with **SHA-256** before storage
- API keys stored as **environment variables** (never in frontend)
- Flask backend acts as **secure proxy** for all external API calls
- **CORS** enabled for controlled cross-origin access
- Input validation on all endpoints

---

## 🚧 Known Limitations

- SQLite data may be lost on Render free tier restarts (use Supabase for persistence)
- VirusTotal free tier: 4 requests/minute limit
- IPQualityScore free tier may not return state/region for all countries
- Admin panel has no authentication (protect in production)

---

## 🔮 Future Enhancements

- [ ] Real-time threat dashboard with charts
- [ ] Browser extension for one-click scanning
- [ ] Two-factor authentication (2FA)
- [ ] Email inbox integration (Gmail/Outlook)
- [ ] Mobile app (React Native)
- [ ] Webhook alerts (Slack/Discord)
- [ ] SIEM integration (Splunk/IBM QRadar)
- [ ] Rate limiting on all endpoints

---

## 👨‍💻 Author

**Ayush Singh**
- Email: ayushsingh19091@gmail.com
- GitHub: [@AyushSingh338](https://github.com/AyushSingh338)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- [VirusTotal](https://virustotal.com) — Threat intelligence platform
- [IPQualityScore](https://ipqualityscore.com) — Fraud detection APIs
- [NumVerify](https://numverify.com) — Phone validation API
- [scikit-learn](https://scikit-learn.org) — Machine learning library
- [Flask](https://flask.palletsprojects.com) — Web framework
- [Render](https://render.com) — Cloud deployment platform
- [Supabase](https://supabase.com) — Open source PostgreSQL database

---

<div align="center">
Made with ❤️ by Ayush Singh | ThreatScan v1.0
</div>
