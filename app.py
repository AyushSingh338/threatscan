import os, re, time, hashlib, requests
import numpy as np
import joblib
import psycopg2
import psycopg2.extras
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from scipy.sparse import hstack

app = Flask(__name__)
CORS(app)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.pkl")
VEC_PATH   = os.path.join(BASE_DIR, "data", "vectorizer.pkl")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.tmykgjyitaxyzkpfizct:AyushSingh123@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres"
)

VT_API_KEY    = os.environ.get("VT_API_KEY",    "0c89738d45857549cc6ce5426bc35b06d5c9187ed6c32c846efdd57a3551e569")
IPQS_KEY      = os.environ.get("IPQS_KEY",      "OH0N4O20oTkASaoYUjQVV7r7YlNtgImx")
NUMVERIFY_KEY = os.environ.get("NUMVERIFY_KEY", "9dbd1336acc3d7d8251def39272dc042")
VT_BASE       = "https://www.virustotal.com/api/v3"

model = None
vectorizer = None

def load_model():
    global model, vectorizer
    if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VEC_PATH)
        print("Model loaded")
    else:
        print("Model not found - run train.py first")

load_model()

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Supabase DB ready!")
    except Exception as e:
        print("DB Error:", e)

init_db()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def extract_features(text):
    links = len(re.findall(r'http[s]?://', text))
    sus_w = len(re.findall(r'(free|win|urgent|offer|click|bank|verify|password)', text.lower()))
    return [links, sus_w, len(text)]

@app.route('/')
def index():
    html_path = os.path.join(BASE_DIR, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return Response(f.read(), mimetype='text/html; charset=utf-8')

@app.route('/auth/register', methods=['POST'])
import re

def register():
    try:
        d = request.get_json(force=True)
        name = str(d.get('name','')).strip()
        email = str(d.get('email','')).strip().lower()
        pw = str(d.get('password','')).strip()
        if not name or not email or not pw:
            return jsonify({"error": "All fields required"}), 400
        
        # Email format validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Invalid email format (e.g. user@example.com)"}), 400
        
        if len(pw) < 6:
            return jsonify({"error": "Password min 6 characters"}), 400
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            cur.close(); conn.close()
            return jsonify({"error": "Email already registered"}), 409
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hash_pw(pw)))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({"message": "Account created", "name": name, "email": email}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        d = request.get_json(force=True)
        email = str(d.get('email','')).strip().lower()
        pw = str(d.get('password','')).strip()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, hash_pw(pw)))
        user = cur.fetchone()
        cur.close(); conn.close()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        return jsonify({"message": "Login successful", "name": user["name"], "email": user["email"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/users')
def admin_users():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id DESC")
        users = cur.fetchall()
        cur.close(); conn.close()
        rows = "".join(f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['created_at']}</td></tr>" for u in users)
        html = f"""<!DOCTYPE html><html><head><title>ThreatScan Admin</title>
<style>body{{font-family:monospace;background:#050810;color:#e2e8f0;padding:2rem;}}
h2{{color:#00d4ff;}}table{{width:100%;border-collapse:collapse;margin-top:1rem;}}
th{{background:#0e1428;color:#00d4ff;padding:10px 14px;text-align:left;font-size:0.78rem;}}
td{{padding:9px 14px;border-bottom:1px solid #1a2440;font-size:0.78rem;}}
tr:hover td{{background:#0a0f1e;}}.badge{{display:inline-block;background:rgba(0,212,255,0.1);
border:1px solid rgba(0,212,255,0.3);border-radius:20px;padding:3px 14px;font-size:0.68rem;color:#00d4ff;}}
a{{color:#00d4ff;}}</style></head><body>
<h2>ThreatScan Admin Panel</h2>
<div class="badge">Supabase Cloud | Total Users: {len(users)}</div>
<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Registered At</th></tr></thead>
<tbody>{rows or '<tr><td colspan=4 style="color:#4a5568;padding:1rem;">No users yet.</td></tr>'}</tbody></table>
<p style="color:#4a5568;font-size:0.65rem;margin-top:1.5rem;">Passwords: SHA-256 hashed | <a href="/">Back to App</a></p>
</body></html>"""
        return Response(html, mimetype='text/html')
    except Exception as e:
        return Response(f"<h2 style='color:red;font-family:monospace;padding:2rem;'>DB Error: {e}</h2>", mimetype='text/html')

@app.route('/analyze_email', methods=['POST'])
def analyze_email():
    try:
        text = str(request.get_json(force=True).get("email","")).strip()
        if not text:
            return jsonify({"error": "No email content provided"}), 400

        # Model nahi hai toh bhi basic analysis karo
        reasons = []
        if "http" in text: reasons.append("Contains suspicious links")
        if re.search(r'(urgent|immediate|action required)', text.lower()): reasons.append("Urgent language detected")
        if re.search(r'(bank|password|verify)', text.lower()): reasons.append("Sensitive info request")
        if re.search(r'(free|win|prize|lottery|offer)', text.lower()): reasons.append("Promotional/scam keywords found")

        if not model:
            # Model ke bina bhi basic result do
            score = len(reasons) * 25
            score = min(score, 95)
            risk = "HIGH" if score > 75 else "MEDIUM" if score > 25 else "LOW"
            prediction = "SPAM / PHISHING" if score > 25 else "SAFE"
            return jsonify({
                "prediction": prediction,
                "confidence": round(score / 100, 3),
                "risk_level": risk,
                "score": score,
                "reasons": reasons if reasons else ["No suspicious patterns found"],
                "detected_urls": re.findall(r'https?://\S+', text)
            })

        Xt = vectorizer.transform([text])
        X = hstack((Xt, np.array([extract_features(text)])))
        pred = model.predict(X)[0]
        conf = model.predict_proba(X)[0].max()
        score = int(conf * 100)
        risk = "HIGH" if score > 75 else "MEDIUM" if score > 40 else "LOW"
        return jsonify({
            "prediction": "SPAM / PHISHING" if pred == 1 else "SAFE",
            "confidence": round(float(conf), 3),
            "risk_level": risk,
            "score": score,
            "reasons": reasons if reasons else ["No suspicious patterns found"],
            "detected_urls": re.findall(r'https?://\S+', text)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze_number', methods=['POST'])
def analyze_number():
    try:
        number = str(request.get_json(force=True).get("number","")).strip()
        if not number:
            return jsonify({"error": "No number provided"}), 400
        num_data = requests.get(f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={number}", timeout=8).json()
        ipqs_data = requests.get(f"https://ipqualityscore.com/api/json/phone/{IPQS_KEY}/{number}", timeout=8).json()
        valid = num_data.get("valid", False)
        carrier = num_data.get("carrier") or ipqs_data.get("carrier")
        country = num_data.get("country_name") or ipqs_data.get("country")
        fraud_score = ipqs_data.get("fraud_score", 0)
        recent_abuse = ipqs_data.get("recent_abuse", False)
        voip = ipqs_data.get("VOIP", False)
        risk_score = 0; reasons = []
        if not valid: risk_score += 50; reasons.append("Invalid number")
        if voip: risk_score += 30; reasons.append("VOIP number")
        if fraud_score > 75: risk_score += 50; reasons.append("High fraud score")
        if recent_abuse: risk_score += 40; reasons.append("Recently reported for abuse")
        if not carrier: risk_score += 10; reasons.append("Unknown carrier")
        return jsonify({"number": number, "valid": valid, "country": country, "carrier": carrier,
            "line_type": ipqs_data.get("line_type","unknown"), "fraud_score": fraud_score,
            "recent_abuse": recent_abuse, "voip": voip, "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score > 80 else "MEDIUM" if risk_score > 40 else "LOW",
            "reasons": reasons})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vt/<path:path>', methods=['GET','POST'])
def vt_proxy(path):
    headers = {'x-apikey': VT_API_KEY}

    path_map = {
        'url':    'urls',
        'ip':     'ip_addresses',
        'domain': 'domains',
    }

    parts = path.split('/')
    parts[0] = path_map.get(parts[0], parts[0])
    fixed_path = '/'.join(parts)
    url = f"{VT_BASE}/{fixed_path}"

    if request.method == 'POST':
        if 'file' in request.files:
            f = request.files['file']
            r = requests.post(url, headers=headers, files={'file': (f.filename, f.stream, f.mimetype)})
        else:
            # Form data properly parse karke bhejo
            form_data = request.form.to_dict()
            if not form_data:
                try:
                    form_data = request.get_json(force=True) or {}
                except:
                    form_data = {}
            r = requests.post(url, headers=headers, data=form_data, params=request.args)
    else:
        r = requests.get(url, headers=headers, params=request.args)

    return Response(r.content, status=r.status_code, content_type=r.headers.get('Content-Type','application/json'))

@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json
    fname = f"report_{int(time.time())}.txt"
    with open(fname, "w") as f:
        f.write("==== ThreatScan Report ====\n\n")
        for k, v in data.items(): f.write(f"{k}: {v}\n")
    return jsonify({"file": fname})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
