from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, IntegrityError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
import requests
import os
import qrcode
from PIL import Image
from io import BytesIO

# =========================
# CONFIG
# =========================

IMAGEKIT_PUBLIC_KEY = "public_EqxvibXcdPomqMQkfO3NaE2Gwuc="
IMAGEKIT_PRIVATE_KEY = "private_7gFYb6gblSzQWrK9d5X/iVVOJ9E="
IMAGEKIT_ENDPOINT = "https://ik.imagekit.io/75wdreowf"

DATABASE_URL = "YOUR_DATABASE_URL"
engine = create_engine(DATABASE_URL)

ph = PasswordHasher()

# =========================
# FLASK INIT
# =========================

app = Flask(__name__, static_folder='templates/static')
app.secret_key = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# =========================
# USER MODEL
# =========================

class User(UserMixin):
    def __init__(self, id, gc_id, name, balance, role, preference, pic, lang, qr):
        self.id = id
        self.greencoin_id = gc_id
        self.name = name
        self.balance = balance
        self.role = role
        self.preference = preference
        self.pic = pic
        self.lang = lang
        self.qrim = qr   # 🔥 QR available here

# =========================
# LOAD USER
# =========================

@login_manager.user_loader
def load_user(user_id):
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text("""
                    SELECT greencoin_id, nam, ballance, role, preference, pic, lang, qr
                    FROM users
                    WHERE username = :u
                """),
                {"u": user_id}
            ).fetchone()

            if row:
                return User(user_id, *row)

    except Exception:
        return None

    return None

# =========================
# QR GENERATOR WITH LOGO
# =========================

def generate_qr_with_logo(data):
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="#16a34a", back_color="white").convert("RGB")

    logo_path = os.path.join(os.path.dirname(__file__), "images", "logo.png")
    logo = Image.open(logo_path)

    qr_w, qr_h = qr_img.size
    logo_size = qr_w // 4
    logo = logo.resize((logo_size, logo_size))

    pos = ((qr_w - logo_size)//2, (qr_h - logo_size)//2)
    qr_img.paste(logo, pos, mask=logo if logo.mode == "RGBA" else None)

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

# =========================
# IMAGEKIT UPLOAD
# =========================

def upload_to_imagekit(file, filename):
    try:
        files = {"file": file}
        data = {
            "fileName": filename,
            "folder": "/qr_codes",
            "useUniqueFileName": "true"
        }

        response = requests.post(
            IMAGEKIT_UPLOAD_URL,
            data=data,
            files=files,
            auth=(IMAGEKIT_PRIVATE_KEY, "")
        )

        return response.json()

    except Exception as e:
        return {"error": str(e)}

# =========================
# ACCOUNT MANAGER
# =========================

class AccountManager:

    @staticmethod
    def generate_gc_id():
        raw = secrets.token_hex(8).upper()
        return f"GC-{raw[:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"

    @staticmethod
    def Login(username, password):
        try:
            with engine.connect() as conn:
                row = conn.execute(
                    text("""
                        SELECT pass, greencoin_id, nam, ballance, role, preference, pic, lang, qr
                        FROM users
                        WHERE username = :u
                    """),
                    {"u": username}
                ).fetchone()

                if not row:
                    return "wrong username"

                hashed, gc_id, name, balance, role, pref, pic, lang, qr = row

                try:
                    ph.verify(hashed, password)

                    return {
                        "username": username,
                        "gc_id": gc_id,
                        "name": name,
                        "balance": balance,
                        "role": role,
                        "preference": pref or "light",
                        "pic": pic or "no",
                        "lang": lang or "en",
                        "qr": qr
                    }

                except VerifyMismatchError:
                    return "wrong password"

        except OperationalError:
            return "connection failed"

    @staticmethod
    def SignUp(username, password, name, lang):
        hashed = ph.hash(password)
        gc_id = AccountManager.generate_gc_id()

        # 🔥 Generate QR
        qr_image = generate_qr_with_logo(gc_id)

        upload = upload_to_imagekit(qr_image, f"{username}_qr.png")

        if "url" not in upload:
            return "qr upload failed"

        qr_url = upload["url"]

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO users
                        (username, pass, nam, greencoin_id, ballance, role, preference, pic, lang, qr)
                        VALUES (:u, :p, :n, :g, :b, :r, :pr, :pic, :lang, :qr)
                    """),
                    {
                        "u": username,
                        "p": hashed,
                        "n": name,
                        "g": gc_id,
                        "b": 0,
                        "r": "user",
                        "pr": "light",
                        "pic": "no",
                        "lang": lang,
                        "qr": qr_url
                    }
                )

            return "account creation successful"

        except IntegrityError:
            return "username exists!"

# =========================
# ROUTES
# =========================

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login")
def login():
    return render_template("login.html")

# =========================
# LOGIN
# =========================

@app.route("/Login", methods=["POST"])
def ingia():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    result = AccountManager.Login(username, password)

    if isinstance(result, dict):
        user = User(
            result["username"],
            result["gc_id"],
            result["name"],
            result["balance"],
            result["role"],
            result["preference"],
            result["pic"],
            result["lang"],
            result["qr"]
        )

        login_user(user)

        return jsonify({
            "message": "logged in",
            "location": url_for("home"),
            "qr": result["qr"]
        })

    return jsonify({"message": result}), 401

# =========================
# SIGNUP
# =========================

@app.route("/Signup", methods=["POST"])
def create():
    data = request.get_json()

    result = AccountManager.SignUp(
        data.get("username"),
        data.get("password"),
        data.get("full_name"),
        data.get("lang", "en")
    )

    if result == "username exists!":
        return jsonify({"message": result}), 400

    return jsonify({
        "message": "account created",
        "location": url_for("login")
    })

# =========================
# LOGOUT
# =========================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)