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
    
    # Save to history if user info is provided
    try:
        user_email = request.headers.get('X-User-Email')
        if user_email:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id FROM users WHERE email = %s", (user_email,))
                user = cursor.fetchone()
                if user:
                    text_preview = text[:200] + "..." if len(text) > 200 else text
                    cursor.execute("""
                        INSERT INTO analysis_history (user_id, text_preview, flesch_score, fog_score)
                        VALUES (%s, %s, %s, %s)
                    """, (user['id'], text_preview, results['flesch_reading_ease'], results['gunning_fog']))
                    conn.commit()
                cursor.close()
                conn.close()
    except Exception as e:
        print(f"Error saving history: {e}")

    results["original_text"] = text
    results["file_saved"] = file_saved
    if file_saved:
        results["saved_filename"] = os.path.basename(saved_path)
        
    return jsonify(results), 200

@app.route('/api/history', methods=['GET'])
def get_history():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"message": "Email is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT h.* FROM analysis_history h
            JOIN users u ON h.user_id = u.id
            WHERE u.email = %s
            ORDER BY h.created_at DESC
        """, (user_email,))
        history = cursor.fetchall()
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/export-pdf', methods=['POST'])
def export_pdf():
    data = request.json
    text = data.get('text', '')
    flesch = data.get('flesch', 'N/A')
    fog = data.get('fog', 'N/A')
    
    if not text:
        return jsonify({"message": "Text is required"}), 400

    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="ClauseEase Analysis Report", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Readability Scores", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(200, 10, txt=f"Flesch Reading Ease: {flesch}", ln=True)
        pdf.cell(200, 10, txt=f"Gunning Fog Index: {fog}", ln=True)
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Original Text Preview", ln=True)
        pdf.set_font("Arial", size=10)
        # Limit text to avoid huge PDF
        pdf.multi_cell(0, 10, txt=text[:2000] + ("..." if len(text) > 2000 else ""))
        
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"report_{int(time.time())}.pdf")
        pdf.output(pdf_path)
        
        # In a real app, we'd return the file, but for now we'll return the filename
        return jsonify({"message": "PDF generated", "filename": os.path.basename(pdf_path)}), 200
    except ImportError:
        return jsonify({"message": "fpdf library not installed"}), 500
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Warning: Could not initialize DB: {e}")
    
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
