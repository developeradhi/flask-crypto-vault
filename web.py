from flask import Flask, request, send_file, render_template, jsonify, session, redirect, url_for
import os
import tempfile
import secrets
from core.crypto import generate_key, encrypt_file, decrypt_file, encrypt_text, decrypt_text, KEY_FILE
from core.auth import is_password_set, set_password, verify_password
from core.shredder import shred_file
from core.stego import hide_in_image, extract_from_image

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

@app.before_request
def check_auth():
    if request.endpoint in ['login', 'static', 'api_login', 'api_setup']:
        return
    if not session.get('logged_in'):
        if request.path.startswith('/api/'):
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('login.html', is_setup_needed=not is_password_set())

@app.route('/api/auth/setup', methods=['POST'])
def api_setup():
    if is_password_set():
        return jsonify({"error": "Password already set"}), 400
    password = request.json.get('password')
    if not password:
        return jsonify({"error": "Password required"}), 400
    set_password(password)
    session['logged_in'] = True
    return jsonify({"success": True})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    password = request.json.get('password')
    if verify_password(password):
        session['logged_in'] = True
        return jsonify({"success": True})
    return jsonify({"error": "Invalid password"}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    key_exists = os.path.exists(KEY_FILE)
    return render_template('index.html', key_exists=key_exists)

@app.route('/api/generate-key', methods=['POST'])
def api_generate_key():
    success, msg = generate_key()
    if success:
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": msg}), 400

@app.route('/api/process', methods=['POST'])
def process_file():
    if not os.path.exists(KEY_FILE):
        return jsonify({"error": "Key file not found. Generate one first."}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    action = request.form.get('action', 'encrypt')
    shred = request.form.get('shred') == 'true'
    
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    file.save(temp_path)

    try:
        if action == 'encrypt':
            success, msg = encrypt_file(temp_path)
            result_path = temp_path + '.enc'
            if success and shred:
                shred_file(temp_path)
        elif action == 'decrypt':
            success, msg = decrypt_file(temp_path)
            if temp_path.endswith('.enc'):
                result_path = temp_path[:-4]
            else:
                result_path = temp_path
        else:
            return jsonify({"error": "Invalid action"}), 400

        if not success:
            return jsonify({"error": msg}), 400

        return send_file(result_path, as_attachment=True, download_name=os.path.basename(result_path))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/text', methods=['POST'])
def process_text():
    if not os.path.exists(KEY_FILE):
        return jsonify({"error": "Key file not found."}), 400
    action = request.json.get('action')
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "Text is required"}), 400
        
    if action == 'encrypt':
        success, result = encrypt_text(text)
    elif action == 'decrypt':
        success, result = decrypt_text(text)
    else:
        return jsonify({"error": "Invalid action"}), 400
        
    if success:
        return jsonify({"result": result})
    else:
        return jsonify({"error": result}), 400

@app.route('/api/stego', methods=['POST'])
def process_stego():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
        
    image = request.files['image']
    action = request.form.get('action')
    
    temp_dir = tempfile.gettempdir()
    image_path = os.path.join(temp_dir, image.filename)
    image.save(image_path)
    
    if action == 'hide':
        text = request.form.get('text')
        if not text:
            return jsonify({"error": "Text to hide is required"}), 400
            
        output_path = os.path.join(temp_dir, 'secret_' + image.filename)
        success, msg = hide_in_image(image_path, text, output_path)
        if success:
            return send_file(output_path, as_attachment=True, download_name='secret_' + image.filename)
        else:
            return jsonify({"error": msg}), 400
            
    elif action == 'extract':
        success, msg = extract_from_image(image_path)
        if success:
            return jsonify({"result": msg})
        else:
            return jsonify({"error": msg}), 400
    else:
        return jsonify({"error": "Invalid action"}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
