from flask import Flask, render_template, jsonify, request, url_for, redirect, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, IntegrityError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from functools import wraps

import secrets
import requests
import io
import qrcode
from PIL import Image

IMAGEKIT_UPLOAD_URL = "https://upload.imagekit.io/api/v1/files/upload"
IMAGEKIT_PRIVATE_KEY = "private_7gFYb6gblSzQWrK9d5X/iVVOJ9E="

DATABASE_URL = "postgresql://neondb_owner:npg_6ZuBlokGxp4b@ep-curly-sea-an9fk0cz-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

ph = PasswordHasher()

translations = {
    'en': {
        'home': 'Home',
        'buy': 'Buy',
        'cart': 'Cart',
        'sell': 'Transactions',
        'settings': 'Settings',
        'appName': 'GreenCoin',
        'login': 'Login',
        'signUp': 'Sign Up',
        'welcomeBack': 'Welcome back! Login to your account',
        'createEcoAccount': 'Create your eco-friendly account',
        'usernameLabel': 'Username',
        'passwordLabel': 'Password',
        'fullNameLabel': 'Full Name',
        'createAccount': 'Create Account',
        'accountCreatedSuccess': 'Account created successfully! Redirecting to login...',
        'alreadyHaveAccount': 'Already have an account?',
        'dontHaveAccount': 'Don\'t have an account?',
        'cartEmpty': 'Your cart is empty',
        'totalCost': 'Total Cost',
        'currentBalanceLabel': 'Current Balance',
        'checkout': 'Checkout',
        'proceedToCheckout': 'Proceed to Checkout',
        'addToCart': 'Add to Cart',
        'addedToCart': 'Added!',
        'itemDescriptionFallback': 'Eco-friendly product',
        'quantityLabel': 'Quantity',
        'buyNow': 'Buy Now',
        'delete': 'Delete',
        'notice': 'Notice',
        'ok': 'OK',
        'comingSoon': 'Coming soon',
        'confirmDelete': 'Delete account permanently?',
        'profileSubtitle': 'In pursuit of protecting the environment',
        'shopSubtitle': 'Redeem your points for recycled materials',
        'cartSubtitle': 'Review items before checkout',
        'logout': 'Logout',
        'lightMode': 'Light Mode',
        'darkMode': 'Dark Mode',
        'manageEco': 'Manage your eco account and earnings',
        'walletBalance': 'Wallet Balance',
        'walletId': 'Wallet ID',
        'profile': 'Profile',
        'profileDesc': 'Update your display name across GreenCoin',
        'language': 'Language',
        'languageDesc': 'Choose your preferred language',
        'security': 'Security',
        'securityDesc': 'Account actions and data management',
        'displayName': 'Display name',
        'saveChanges': 'Save changes',
        'deleteWarning': 'Deleting your account will remove your wallet, transaction history, and profile permanently. Please be sure before continuing.',
        'deleteAccount': 'Delete Account',
        'send': 'Send',
        'receive': 'Receive',
        'scanToReceive': 'Scan this QR code to receive GreenCoins',
        'sendPayment': 'Send Payment',
        'cameraRequired': 'Camera access is required to scan QR codes.',
        'cameraSettings': 'Please allow camera permission in your browser settings, then try again.',
        'tryAgain': 'Try again',
        'paymentSuccess': 'Payment Successful!',
        'thankYou': 'Thank you for helping save the environment with every GreenCoin transfer.',
        'fromLabel': 'From:',
        'toLabel': 'To:',
        'amountLabel': 'Amount:',
        'newBalanceLabel': 'New Balance:',
        'timeLabel': 'Time:',
        'done': 'Done',
        'managePreferences': 'Manage your preferences, language, and security settings',
        'updateDisplayName': 'Update your display name',
        'chooseLanguage': 'Choose preferred language',
        'accountActions': 'Account actions',
        'scanPermissionError': 'Unable to access camera. Please allow camera permission and refresh the page.',
        'thankYouShort': 'Thank you for protecting the environment.',
        'recipientRequired': 'Recipient wallet ID is required.',
        'invalidAmount': 'Invalid amount.',
        'amountGreaterThanZero': 'Amount must be greater than zero.',
        'insufficientBalance': 'Insufficient balance.',
        'recipientNotFound': 'Recipient wallet not found.',
        'selfTransferNotAllowed': 'You cannot send coins to yourself.',
        'transactionSuccess': 'Transaction successful.',
        'scanRecipientFirst': 'Please scan a recipient QR code first.',
        'enterValidAmount': 'Please enter a valid amount.'
    },
    'sw': {
        'home': 'Nyumbani',
        'buy': 'Nunua',
        'cart': 'Kikapu',
        'sell': 'Miamala',
        'settings': 'Mipangilio',
        'appName': 'GreenCoin',
        'login': 'Ingia',
        'signUp': 'Jisajili',
        'welcomeBack': 'Karibu tena! Ingia kwenye akaunti yako',
        'createEcoAccount': 'Unda akaunti yako rafiki wa mazingira',
        'usernameLabel': 'Jina la mtumiaji',
        'passwordLabel': 'Nenosiri',
        'fullNameLabel': 'Jina Kamili',
        'createAccount': 'Unda Akaunti',
        'accountCreatedSuccess': 'Akaunti imeundwa kwa mafanikio! Umeelekezwa kwa kuingia...',
        'alreadyHaveAccount': 'Tayari una akaunti?',
        'dontHaveAccount': 'Hauna akaunti?',
        'cartEmpty': 'Kikapu chako kiko tupu',
        'totalCost': 'Gharama ya Jumla',
        'currentBalanceLabel': 'Salio la Sasa',
        'checkout': 'Maliza',
        'proceedToCheckout': 'Endelea kwa Malipo',
        'addToCart': 'Ongeza kwenye Kikapu',
        'addedToCart': 'Imekuwa imeongezwa!',
        'itemDescriptionFallback': 'Bidhaa rafiki kwa mazingira',
        'quantityLabel': 'Kiasi',
        'buyNow': 'Nunua Sasa',
        'delete': 'Futa',
        'notice': 'Makumbusho',
        'ok': 'Sawa',
        'comingSoon': 'Inakuja hivi karibuni',
        'confirmDelete': 'Futa akaunti kabisa?',
        'profileSubtitle': 'Katika jitihada za kulinda mazingira',
        'shopSubtitle': 'Pata bidhaa kwa pointi zako za mazingira',
        'logout': 'Toka',
        'lightMode': 'Njia ya Mwanga',
        'manageEco': 'Simamia akaunti yako ya mazingira na mapato',
        'walletBalance': 'Salio la Mfuko',
        'walletId': 'Kitambulisho cha Mfuko',
        'profile': 'Profaili',
        'profileDesc': 'Sasisha jina lako la kuonyesha kwenye GreenCoin',
        'language': 'Lugha',
        'languageDesc': 'Chagua lugha unayopendelea',
        'security': 'Usalama',
        'securityDesc': 'Vitendo vya akaunti na usimamizi wa data',
        'displayName': 'Jina la kuonyesha',
        'saveChanges': 'Hifadhi mabadiliko',
        'deleteWarning': 'Kufuta akaunti yako kutafuta mfuko wako, historia ya miamala, na wasifu milele. Tafadhali hakikisha kabla ya kuendelea.',
        'deleteAccount': 'Futa Akaunti',
        'send': 'Tuma',
        'receive': 'Pokea',
        'scanToReceive': 'Piga msimbo huu wa QR kupokea GreenCoins',
        'sendPayment': 'Tuma Malipo',
        'cameraRequired': 'Upatikanaji wa kamera unahitajika skanningi QR.',
        'cameraSettings': 'Tafadhali ruhusu ruhusa ya kamera kwenye mipangilio ya kivinjari, kisha jaribu tena.',
        'tryAgain': 'Jaribu tena',
        'paymentSuccess': 'Malipo Yamefanikiwa!',
        'thankYou': 'Asante kwa kusaidia kuokoa mazingira kwa kila uhamisho wa GreenCoin.',
        'fromLabel': 'Kutoka:',
        'toLabel': 'Kwa:',
        'amountLabel': 'Kiasi:',
        'newBalanceLabel': 'Salio Jipya:',
        'timeLabel': 'Muda:',
        'done': 'Imekamilika',
        'managePreferences': 'Simamia mapendeleo yako, lugha, na usalama',
        'updateDisplayName': 'Sasisha jina lako la kuonyesha',
        'chooseLanguage': 'Chagua lugha unayopendelea',
        'accountActions': 'Vitendo vya akaunti',
        'scanPermissionError': 'Haiwezekani kupata kamera. Tafadhali ruhusu ruhusa ya kamera na upige ukurasa upya.',
        'thankYouShort': 'Asante kwa kulinda mazingira.',
        'recipientRequired': 'Hitaji kitambulisho cha mfuko wa mpokeaji.',
        'invalidAmount': 'Kiasi sio sahihi.',
        'amountGreaterThanZero': 'Kiasi lazima kiwe zaidi ya sifuri.',
        'insufficientBalance': 'Salio halitoshi.',
        'recipientNotFound': 'Mfuko wa mpokeaji haukupatikana.',
        'selfTransferNotAllowed': 'Huwezi kutuma sarafu kwako mwenyewe.',
        'transactionSuccess': 'Miamala imefanikiwa.',
        'scanRecipientFirst': 'Tafadhali piga msimbo wa QR wa mpokeaji kwanza.',
        'enterValidAmount': 'Tafadhali ingiza kiasi halali.'
    },
    'tt': {
        'home': 'Mzinyi',
        'buy': 'Ghua',
        'cart': 'Kikapu',
        'sell': 'Duma',
        'settings': 'Mipangilio',
        'appName': 'GreenCoin',
        'login': 'Ngia',
        'signUp': 'Jisajili',
        'welcomeBack': 'Karibu sena! Ingia kwa akaunti yako',
        'createEcoAccount': 'Poisa akaunti yako ya mazingira',
        'usernameLabel': 'Marina ga mtumiaji',
        'passwordLabel': 'Malagho la siri',
        'fullNameLabel': 'Irina kamili',
        'createAccount': 'Poisa Akaunti',
        'accountCreatedSuccess': 'Akaunti imeundwa kwa mafanikio! Unaelekezwa kwa kuingia...',
        'alreadyHaveAccount': 'tayari koko na akaunti?',
        'dontHaveAccount': 'Ndokune akaunti?',
        'cartEmpty': 'Kikapu chako cheka kiduu',
        'totalCost': 'Gharama Yose',
        'currentBalanceLabel': 'Mabaki gha magome',
        'checkout': 'Ghua',
        'proceedToCheckout': 'Endelea kwa Malipo',
        'addToCart': 'Kumba kikapunyi',
        'addedToCart': 'Chachurilwa!',
        'itemDescriptionFallback': 'Kilambo chelindia azingira',
        'quantityLabel': 'Kiasi',
        'buyNow': 'Ghua itakoni',
        'delete': 'Futa',
        'notice': 'Ughu ni wujumbe',
        'ok': 'Sawa',
        'comingSoon': 'Yawiacha karibuni',
        'confirmDelete': 'Futa akaunti kabisa?',
        'profileSubtitle': 'Katika bidii relindia mazingira',
        'shopSubtitle': 'Pata vilambo kwa pointi rako ra mazingira',
        'cartSubtitle': 'Zighana vilambo kabla ye ghua',
        'logout': 'Fuma',
        'lightMode': 'Mwengere',
        'darkMode': 'Kira',
        'manageEco': 'Simamia akaunti yako ya mazingira na mapato',
        'walletBalance': 'Ibaki',
        'walletId': 'Kitambulisho cha mfuko ghwako',
        'profile': 'Profaili',
        'profileDesc': 'Badilisha irina jako je wonyera kwa greencoin',
        'language': 'Lagha',
        'languageDesc': 'Saghua lugha kukunde',
        'security': 'Wusalama',
        'securityDesc': 'Mabonyo gha akaunti na wusimamizi ghwa data',
        'displayName': 'Irina je wonyera',
        'saveChanges': 'Wika mabadiliko',
        'deleteWarning': 'Kukafuta akaunti yako kofuta wallet, historia ya mabonyo, na kila kilambo putu. Kaiya tayari kabla ye bonya huwo.',
        'deleteAccount': 'Futa akaunti',
        'send': 'Duma',
        'receive': 'Ruda',
        'scanToReceive': 'Wonyera ihi kwa uja mndu wakunda kukudumia magome.',
        'sendPayment': 'Duma magome?',
        'cameraRequired': 'Neka browser ruhusa yefungua kamera yako.',
        'cameraSettings': 'Tafadhali neka browser ruhusa ra kamera kwa settings kabla ye endelea..',
        'tryAgain': 'Tima sena',
        'paymentSuccess': 'Malipo Ghameria!',
        'thankYou': 'Chawucha kwa kutesia environment na kila mabonyo aha GreenCoin!',
        'fromLabel': 'Kufuma kwa:',
        'toLabel': 'Kwenda kwa:',
        'amountLabel': 'Kiasi:',
        'newBalanceLabel': 'Ibaki iwishi:',
        'timeLabel': 'Masaa:',
        'done': 'Dameria',
        'managePreferences': 'Saghua aghaje kukunde, lugha, na wusalama',
        'updateDisplayName': 'Badilisha irina jako je wonyera',
        'chooseLanguage': 'Saghua ija lugha yako kuikunde',
        'accountActions': 'Mabonyo gha akaunti',
        'scanPermissionError': 'Dalemwa ni kupata ruhusa ya kamera,, enda kuneke browser yako ruhusa ima kuwuye kumeria.',
        'thankYouShort': 'Chawucha kwa kulindia mazingira ghedu.',
        'recipientRequired': 'mfuko ghwa mpokeaji ghwakundikana.',
        'invalidAmount': 'Kiasi ichi ndechidimikaa.',
        'amountGreaterThanZero': 'Kiasi lazima chikaiye kibaha zaidi ya huwu.',
        'insufficientBalance': 'Mabaki ghako gha magome ndeghiwekata.',
        'recipientNotFound': 'Mfuko ghwa mpokeaji ndoghuwepatikana.',
        'selfTransferNotAllowed': 'Ndokudimaa kujidumia magome kumoni.',
        'transactionSuccess': 'Mabonyo ghafaulu.',
        'scanRecipientFirst': 'Tafadhali bonya kuwonyero QR ya mbenyu ku scan ima kudume.',
        'enterValidAmount': 'Tafadhali ngira kiasi chidimikaa.'
    }
}

app = Flask(__name__, static_folder="templates/static")
app.secret_key = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, gc_id, name, balance, role, preference, pic, lang):
        self.id = id
        self.greencoin_id = gc_id
        self.name = name
        self.balance = balance
        self.role = role
        self.preference = preference
        self.pic = pic
        self.lang = lang
        self.qrim = None

@login_manager.user_loader
def load_user(user_id):
    try:
        with engine.connect() as conn:
            row = conn.execute(text("""
                SELECT greencoin_id, nam, ballance, role, preference, pic, lang, qrim
                FROM users WHERE username = :u
            """), {"u": user_id}).fetchone()

            if row:
                user = User(user_id, *row[:-1])
                user.qrim = row[-1]
                return user
    except:
        return None
    return None


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapped(*args, **kwargs):
        if not getattr(current_user, 'role', None) == 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_translations():
    lang = 'en'
    if current_user.is_authenticated:
        lang = getattr(current_user, 'lang', 'en') or 'en'
    tr = translations.get(lang, translations['en'])
    return {'tr': tr, 'current_lang': lang}

def upload_to_imagekit(file):
    try:
        files = {"file": file}
        data = {
            "fileName": f"avatar_{secrets.token_hex(6)}.jpg",
            "folder": "/avatars",
            "useUniqueFileName": "true"
        }
        res = requests.post(IMAGEKIT_UPLOAD_URL, data=data, files=files, auth=(IMAGEKIT_PRIVATE_KEY, ""))
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def generate_qr(data):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=14, border=8)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    target_size = max(img.size[0], 800)
    img = img.resize((target_size, target_size), Image.NEAREST)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

def upload_qr(buf):
    files = {"file": ("qr.png", buf, "image/png")}
    data = {"fileName": f"qr_{secrets.token_hex(6)}.png", "folder": "/qr"}
    res = requests.post(IMAGEKIT_UPLOAD_URL, data=data, files=files, auth=(IMAGEKIT_PRIVATE_KEY, ""))
    return res.json()

class AccountManager:

    @staticmethod
    def generate_gc_id():
        raw = secrets.token_hex(8).upper()
        return f"GC-{raw[:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}"

    @staticmethod
    def Login(username, password):
        try:
            with engine.connect() as conn:
                row = conn.execute(text("""
                    SELECT pass, greencoin_id, nam, ballance, role, preference, pic, lang, qrim
                    FROM users WHERE username = :u
                """), {"u": username}).fetchone()

                if not row:
                    return "wrong username"

                hashed, gc_id, name, balance, role, pref, pic, lang, qrim = row
                ph.verify(hashed, password)

                if not qrim or qrim == "no":
                    print("Generating QR... please wait")
                    qr_buf = generate_qr(gc_id)
                    upload = upload_qr(qr_buf)
                    if "url" in upload:
                        qrim = upload["url"]
                        with engine.begin() as conn2:
                            conn2.execute(text("UPDATE users SET qrim=:q WHERE username=:u"),
                                          {"q": qrim, "u": username})

                return {
                    "username": username,
                    "gc_id": gc_id,
                    "name": name,
                    "balance": balance,
                    "role": role,
                    "preference": pref or "light",
                    "pic": pic or "no",
                    "lang": lang or "en",
                    "qrim": qrim
                }

        except VerifyMismatchError:
            return "wrong password"
        except OperationalError:
            return "connection failed"

    @staticmethod
    def SignUp(username, password, name, lang):
        hashed = ph.hash(password)
        gc_id = AccountManager.generate_gc_id()

        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO users
                    (username, pass, nam, greencoin_id, ballance, role, preference, pic, lang, qrim)
                    VALUES (:u,:p,:n,:g,:b,:r,:pr,:pic,:lang,:q)
                """), {
                    "u": username, "p": hashed, "n": name, "g": gc_id,
                    "b": 0, "r": "user", "pr": "light",
                    "pic": "no", "lang": lang, "q": "no"
                })
            return "account creation successful"
        except IntegrityError:
            return "username exists!"

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/buy")
@login_required
def buy():
    return render_template("buy.html")

@app.route("/cart")
@login_required
def cart():
    return render_template("cart.html")

@app.route("/sell")
@login_required
def sell():
    return render_template("sell.html")

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM available_items ORDER BY id DESC"))
        items = [dict(r) for r in rows.mappings()]
    return render_template('admin_dashboard.html', items=items)

@app.route('/admin/stats')
@admin_required
def admin_stats():
    with engine.connect() as conn:
        user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        product_count = conn.execute(text("SELECT COUNT(*) FROM available_items")).scalar() or 0
        total_balance = conn.execute(text("SELECT COALESCE(SUM(ballance), 0) FROM users")).scalar() or 0
        admin_count = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'")).scalar() or 0
    return render_template('admin_stats.html', stats={
        'user_count': user_count,
        'product_count': product_count,
        'total_balance': total_balance,
        'admin_count': admin_count
    })

@app.route('/admin/mint')
@admin_required
def admin_mint():
    return render_template('admin_mint.html')

@app.route('/admin/upload-product', methods=['POST'])
@admin_required
def admin_upload_product():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    price = data.get('price')
    link_image = data.get('link_image', '').strip() or 'https://via.placeholder.com/280x180?text=GreenCoin'
    seller = data.get('seller', 'GreenCoin Team').strip() or 'GreenCoin Team'

    if not name or price is None:
        return jsonify({'message': 'Missing item name or price.'}), 400

    try:
        price_value = float(price)
    except (TypeError, ValueError):
        return jsonify({'message': 'Invalid price.'}), 400

    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO available_items (name, price, link_image, seller) VALUES (:name, :price, :link_image, :seller)"
        ), {
            'name': name,
            'price': price_value,
            'link_image': link_image,
            'seller': seller
        })

    return jsonify({'message': 'success'})

@app.route("/Buy")
def Nunua():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM available_items"))
        return jsonify({"items": [dict(r) for r in rows.mappings()]})

@app.route("/Add-To-Cart", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO cart (username,item_id,name,price,link_image,seller,quantity)
            VALUES (:u,:i,:n,:p,:l,:s,:q)
        """), {
            "u": current_user.id,
            "i": data["itemId"],
            "n": data["name"],
            "p": data["price"],
            "l": data["link_image"],
            "s": data["seller"],
            "q": data.get("quantity",1)
        })
    return jsonify({"message":"success"})

@app.route("/Get-Cart")
@login_required
def get_cart():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM cart WHERE username=:u"),
                            {"u": current_user.id})
        return jsonify({"cart":[dict(r) for r in rows.mappings()]})

@app.route("/Remove-From-Cart", methods=["POST"])
@login_required
def remove_cart():
    data = request.get_json()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM cart WHERE username=:u AND item_id=:i"),
                     {"u": current_user.id, "i": data["itemId"]})
    return jsonify({"message":"removed"})

@app.route("/Get_Balance")
@login_required
def balance():
    return jsonify({"bal": current_user.balance})

@app.route("/wallet-info")
@login_required
def wallet_info():
    return jsonify({
        "qrim": current_user.qrim,
        "greencoin_id": current_user.greencoin_id,
        "balance": current_user.balance,
        "name": current_user.name
    })

@app.route("/sendCoins", methods=["POST"])
@login_required
def send_coins():
    data = request.get_json() or {}
    recipient_id = data.get("recipientId") or data.get("recipient")
    amount_value = data.get("amount")

    if not recipient_id:
        return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["recipientRequired"]}), 400

    try:
        amount = float(amount_value)
    except (TypeError, ValueError):
        return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["invalidAmount"]}), 400

    if amount <= 0:
        return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["amountGreaterThanZero"]}), 400

    if amount > float(current_user.balance):
        return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["insufficientBalance"]}), 400

    with engine.connect() as conn:
        recipient = conn.execute(text(
            "SELECT username, nam, ballance FROM users WHERE greencoin_id = :rid"
        ), {"rid": recipient_id}).fetchone()

        if not recipient:
            return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["recipientNotFound"]}), 404

        recipient_username, recipient_name, recipient_balance = recipient

        if recipient_username == current_user.id:
            return jsonify({"message": translations.get(current_user.lang or 'en', translations['en'])["selfTransferNotAllowed"]}), 400

    with engine.begin() as conn:
        conn.execute(text(
            "UPDATE users SET ballance = ballance - :amt WHERE username = :u"
        ), {"amt": amount, "u": current_user.id})
        conn.execute(text(
            "UPDATE users SET ballance = ballance + :amt WHERE username = :u"
        ), {"amt": amount, "u": recipient_username})

    current_user.balance = float(current_user.balance) - amount
    return jsonify({
        "message": translations.get(current_user.lang or 'en', translations['en'])["transactionSuccess"],
        "balance": current_user.balance,
        "recipientName": recipient_name,
        "recipientId": recipient_id,
        "senderName": current_user.name,
        "senderPic": current_user.pic if current_user.pic and current_user.pic != 'no' else None
    })

@app.route('/updateLanguage', methods=['POST'])
@login_required
def update_language():
    data = request.get_json() or {}
    lang = data.get('lang', 'en')
    if lang not in translations:
        lang = 'en'
    with engine.begin() as conn:
        conn.execute(text("UPDATE users SET lang=:lang WHERE username=:u"),
                     {"lang": lang, "u": current_user.id})
    current_user.lang = lang
    return jsonify({"message": "Language updated.", "lang": lang})

@app.route("/togglePreference", methods=["POST"])
@login_required
def togglePreference():
    with engine.begin() as conn:
        row = conn.execute(text("SELECT preference FROM users WHERE username=:u"),
                           {"u": current_user.id}).fetchone()
        current = row[0] if row else "light"
        new = "dark" if current=="light" else "light"
        conn.execute(text("UPDATE users SET preference=:p WHERE username=:u"),
                     {"p": new, "u": current_user.id})
    return jsonify({"preference":new})

@app.route("/updateProfilePic", methods=["POST"])
@login_required
def update_profile_pic():
    file = request.files.get("file")
    upload = upload_to_imagekit(file)
    url = upload.get("url")

    with engine.begin() as conn:
        conn.execute(text("UPDATE users SET pic=:p WHERE username=:u"),
                     {"p": url, "u": current_user.id})

    current_user.pic = url
    return jsonify({"url":url})

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/Login", methods=["POST"])
def login_route():
    data = request.get_json()
    result = AccountManager.Login(data.get("username"), data.get("password"))

    if isinstance(result, dict):
        user = User(result["username"], result["gc_id"], result["name"],
                    result["balance"], result["role"],
                    result["preference"], result["pic"], result["lang"])
        user.qrim = result["qrim"]
        login_user(user)
        redirect_url = url_for("admin_dashboard") if result["role"] == "admin" else url_for("home")
        return jsonify({"location": redirect_url, "qrim": user.qrim})

    return jsonify({"message": result}), 401

@app.route("/Signup", methods=["POST"])
def signup_route():
    data = request.get_json()
    result = AccountManager.SignUp(
        data.get("username"),
        data.get("password"),
        data.get("full_name"),
        data.get("lang","en")
    )
    return jsonify({"message": result})

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory("images", filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)