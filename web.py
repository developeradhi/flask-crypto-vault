import os
import tempfile
import secrets
from flask import Flask, request, send_file, render_template, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from core.models import db, User, AuditLog, EphemeralMessage
from core.crypto import generate_key, encrypt_file, decrypt_file, encrypt_text, decrypt_text
from core.rsa_utils import generate_rsa_keypair, sign_message, verify_signature
from core.hmac_utils import generate_file_hmac, verify_file_hmac
from core.shredder import shred_file

load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Google OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID', 'placeholder-client-id'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET', 'placeholder-client-secret'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

# SMTP Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-app-password')

with app.app_context():
    db.create_all()

@app.before_request
def check_auth():
    public_endpoints = ['landing', 'login', 'register', 'api_login', 'api_register', 'static', 'read_burn_message', 'login_google', 'auth_google', 'forgot_password', 'reset_password']
    if request.endpoint in public_endpoints:
        return
    
    # Check if logged in
    if not session.get('user_id'):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))
        
    # Check if 2FA is required but not verified
    user = User.query.get(session['user_id'])
    if user and user.totp_enabled and not session.get('2fa_verified'):
        if request.endpoint not in ['two_factor_auth', 'api_verify_2fa', 'logout']:
            if request.path.startswith('/api/'):
                return jsonify({"error": "2FA Required"}), 401
            return redirect(url_for('two_factor_auth'))

@app.route('/login', methods=['GET'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('login.html', mode='login')

@app.route('/register', methods=['GET'])
def register():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return render_template('login.html', mode='register')

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({'error': 'Username, email and password required'}), 400
        
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
        
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
        
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        aes_key=generate_key(),
        totp_secret=pyotp.random_base32()
    )
    # Generate RSA keys
    private_pem, public_pem = generate_rsa_keypair()
    user.rsa_private_key = private_pem
    user.rsa_public_key = public_pem
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful'})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['2fa_verified'] = False
        
        # Audit Log Success
        log = AuditLog(user_id=user.id, ip_address=request.remote_addr, user_agent=request.user_agent.string, action="LOGIN_SUCCESS")
        db.session.add(log)
        db.session.commit()
        
        return jsonify({"success": True, "requires_2fa": user.totp_enabled})
        
    # Audit Log Failed
    log = AuditLog(user_id=user.id if user else None, ip_address=request.remote_addr, user_agent=request.user_agent.string, action="LOGIN_FAILED")
    db.session.add(log)
    db.session.commit()
    
    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/2fa', methods=['GET'])
def two_factor_auth():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('2fa.html')

@app.route('/api/auth/verify-2fa', methods=['POST'])
def api_verify_2fa():
    code = request.json.get('code')
    user = User.query.get(session.get('user_id'))
    
    if not user:
        return jsonify({"error": "User not found"}), 400
        
    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(code):
        session['2fa_verified'] = True
        return jsonify({"success": True})
    return jsonify({"error": "Invalid 2FA code"}), 400

@app.route('/api/auth/enable-2fa', methods=['POST'])
def api_enable_2fa():
    user = User.query.get(session['user_id'])
    code = request.json.get('code')
    
    if not code:
        # Return the provisioning URI to generate QR Code on frontend
        totp = pyotp.TOTP(user.totp_secret)
        uri = totp.provisioning_uri(name=user.username, issuer_name="Ultimate Security Suite")
        return jsonify({"uri": uri})
    else:
        # Verify and enable
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code):
            user.totp_enabled = True
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"error": "Invalid verification code"}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/')
def landing():
    # If already logged in and verified, redirect to dashboard
    if session.get('user_id') and session.get('2fa_verified'):
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    user = User.query.get(session['user_id'])
    
    # Calculate Security Score
    score = 20 # Base score
    if user.totp_enabled: score += 40
    # Add points for using the vault (we can check if they have audit logs)
    if AuditLog.query.filter_by(user_id=user.id).count() > 2: score += 40
    
    logs = AuditLog.query.filter_by(user_id=user.id).order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', user=user, score=score, logs=logs)

# ===============================
# GOOGLE OAUTH ROUTES
# ===============================
@app.route('/login/google')
def login_google():
    # Hardcoding the redirect URI ensures it exactly matches what is configured in Google Cloud Console,
    # regardless of whether the user accesses the app via localhost or 127.0.0.1
    redirect_uri = "http://127.0.0.1:5001/auth/callback"
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_google():
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token, nonce=None)
    
    email = user_info.get('email')
    google_id = user_info.get('sub')
    name = user_info.get('name', email.split('@')[0])
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=name + '_' + google_id[:4],
            email=email,
            google_id=google_id,
            aes_key=generate_key(),
            totp_secret=pyotp.random_base32()
        )
        private_pem, public_pem = generate_rsa_keypair()
        user.rsa_private_key = private_pem
        user.rsa_public_key = public_pem
        db.session.add(user)
        db.session.commit()
    
    session['user_id'] = user.id
    session['2fa_verified'] = True # Bypass 2FA for Google Login for simplicity
    
    log = AuditLog(user_id=user.id, ip_address=request.remote_addr, user_agent=request.user_agent.string, status='SUCCESS (Google)')
    db.session.add(log)
    db.session.commit()
    
    return redirect(url_for('dashboard'))

# ===============================
# FORGOT PASSWORD ROUTES
# ===============================
def send_reset_email(to_email, reset_url):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = "Password Reset - Ultimate Security Suite"
        
        body = f"Click the following link to reset your password. This link expires in 15 minutes.\n\n{reset_url}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate Token
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            from datetime import timedelta
            user.reset_token_expiration = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            
            reset_url = url_for('reset_password', token=token, _external=True)
            # In a real app, send_reset_email(email, reset_url) is called
            # For local demonstration without a real SMTP, we print it
            print(f"--- EMAIL SENT TO {email} ---")
            print(f"Reset URL: {reset_url}")
            send_reset_email(email, reset_url)
            
            flash('If an account exists with that email, a reset link has been sent. (Check console for the link in Dev mode!)')
            return redirect(url_for('login'))
        else:
            flash('If an account exists with that email, a reset link has been sent.')
            return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expiration < datetime.utcnow():
        flash('Invalid or expired reset token.')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        new_password = request.form.get('password')
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Password successfully reset! You can now login.')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html', token=token)

# ===============================
# CORE SECURITY TOOLS
# ===============================

@app.route('/api/process', methods=['POST'])
def process_file():
    user = User.query.get(session['user_id'])
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    action = request.form.get('action', 'encrypt')
    shred = request.form.get('shred') == 'true'
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        if action == 'encrypt':
            success, msg = encrypt_file(temp_path, user.aes_key)
            result_path = temp_path + '.enc'
            if success and shred:
                shred_file(temp_path)
        elif action == 'decrypt':
            success, msg = decrypt_file(temp_path, user.aes_key)
            result_path = temp_path[:-4] if temp_path.endswith('.enc') else temp_path
        else:
            return jsonify({"error": "Invalid action"}), 400

        if not success:
            return jsonify({"error": msg}), 400

        return send_file(result_path, as_attachment=True, download_name=os.path.basename(result_path))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/text', methods=['POST'])
def process_text():
    user = User.query.get(session['user_id'])
    action = request.json.get('action')
    text = request.json.get('text')
    
    if action == 'encrypt':
        success, result = encrypt_text(text, user.aes_key)
    elif action == 'decrypt':
        success, result = decrypt_text(text, user.aes_key)
    else:
        return jsonify({"error": "Invalid action"}), 400
        
    if success:
        return jsonify({"result": result})
    else:
        return jsonify({"error": result}), 400

@app.route('/api/rsa', methods=['POST'])
def process_rsa():
    user = User.query.get(session['user_id'])
    action = request.json.get('action')
    message = request.json.get('message')
    
    if action == 'sign':
        success, result = sign_message(user.rsa_private_key, message)
    elif action == 'verify':
        signature = request.json.get('signature')
        # Can verify against own public key, or a provided one. Defaulting to own for simplicity.
        public_key = request.json.get('public_key') or user.rsa_public_key
        success, result = verify_signature(public_key, message, signature)
    else:
        return jsonify({"error": "Invalid action"}), 400
        
    if success:
        return jsonify({"result": result, "public_key": user.rsa_public_key})
    else:
        return jsonify({"error": result}), 400

@app.route('/api/hmac', methods=['POST'])
def process_hmac():
    user = User.query.get(session['user_id'])
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    action = request.form.get('action')
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        if action == 'generate':
            success, result = generate_file_hmac(temp_path, user.aes_key)
        elif action == 'verify':
            expected_hmac = request.form.get('hmac')
            success, result = verify_file_hmac(temp_path, user.aes_key, expected_hmac)
        else:
            return jsonify({"error": "Invalid action"}), 400
            
        if success:
            return jsonify({"result": result})
        else:
            return jsonify({"error": result}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# GEN-Z TOOLS
# ===============================
@app.route('/api/burn/create', methods=['POST'])
def create_burn_message():
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "Text is required"}), 400
        
    # Encrypt text using app secret key
    from cryptography.fernet import Fernet
    import base64
    f = Fernet(base64.urlsafe_b64encode(app.secret_key.encode('utf-8')[:32].ljust(32, b'0')))
    encrypted = f.encrypt(text.encode('utf-8')).decode('utf-8')
    
    msg_id = str(uuid.uuid4())
    burn_msg = EphemeralMessage(id=msg_id, encrypted_content=encrypted)
    db.session.add(burn_msg)
    db.session.commit()
    
    url = f"{request.host_url}burn/{msg_id}"
    return jsonify({"url": url})

@app.route('/burn/<msg_id>', methods=['GET'])
def read_burn_message(msg_id):
    msg = EphemeralMessage.query.get(msg_id)
    if not msg:
        return render_template('burn.html', error="Message not found or has already been destroyed.")
        
    # Decrypt
    from cryptography.fernet import Fernet
    import base64
    f = Fernet(base64.urlsafe_b64encode(app.secret_key.encode('utf-8')[:32].ljust(32, b'0')))
    try:
        decrypted_text = f.decrypt(msg.encrypted_content.encode('utf-8')).decode('utf-8')
    except:
        decrypted_text = "Error decrypting message."
        
    # BURN IT
    db.session.delete(msg)
    db.session.commit()
    
    return render_template('burn.html', message=decrypted_text)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
