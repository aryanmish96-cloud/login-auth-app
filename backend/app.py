from flask import Flask, request, jsonify
from flask_cors import CORS
from db_config import get_db_connection, init_db
from nlp_service import analyze_readability
import os
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend is running 🚀"}), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({"message": "All fields are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        return jsonify({"message": "Registered successfully ✅"}), 201
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        
        if user:
            return jsonify({"message": "Login successful ✅", "user": {"name": user['name'], "email": user['email']}}), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    text = ""
    file_saved = False
    saved_path = None
    
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.name if hasattr(file, 'name') else file.filename)
        
            timestamp = int(time.time())
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
        
            file_content = file.read()
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            file_saved = True
            saved_path = filepath
            
            if unique_filename.endswith('.pdf'):
                from nlp_service import extract_text_from_pdf
                text = extract_text_from_pdf(file_content)
            else:
                text = file_content.decode('utf-8', errors='ignore')
    else:
        data = request.json
        text = data.get('text', '')
    
    if not text:
        return jsonify({"message": "No text provided or file is empty"}), 400
    
    results = analyze_readability(text)
    
    results["original_text"] = text
    results["file_saved"] = file_saved
    if file_saved:
        results["saved_filename"] = os.path.basename(saved_path)
        
    return jsonify(results), 200

if __name__ == '__main__':
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Could not initialize DB: {e}")
    
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
