from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
import sqlite3
import io
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLite DB for users
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('main-app.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            flash(f"Welcome back, {user[1]}!")
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'warning')
    return render_template('registration.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    patient_name = request.form.get('patient_name')
    mobile = request.form.get('mobile')
    language = request.form.get('language')
    area = request.form.get('area')

    if not files or all(f.filename == '' for f in files):
        flash('No files selected for upload', 'danger')
        return redirect(url_for('home'))

    uploaded_file_paths = []
    ai_insights_list = []

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            uploaded_file_paths.append(filepath)

            # Simulated Epident AI insight per image
            insight = f"Suspicious region detected in {filename} for {patient_name}. Suggested clinical correlation."
            ai_insights_list.append(insight)

    # Cost based on area toggle
    cost = 2000 if area == "Urban" else 1500

    # Patient education text based on language toggle
    education_text = "Please maintain good oral hygiene and visit regularly." if language == "English" else "कृपया अच्छी मौखिक स्वच्छता बनाए रखें और नियमित रूप से जांच कराएं।"

    return render_template(
        'main-app.html',
        message='Files uploaded successfully',
        image_paths=uploaded_file_paths,
        ai_insights_list=ai_insights_list,
        patient_name=patient_name,
        mobile=mobile,
        cost=cost,
        education_text=education_text,
        language=language,
        area=area
    )

@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    patient_name = request.form.get('patient_name')
    mobile = request.form.get('mobile')
    ai_insights = request.form.get('ai_insights')
    education_text = request.form.get('education_text')
    cost = request.form.get('cost')
    language = request.form.get('language')
    area = request.form.get('area')

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(600, 800))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 760, "Epident AI - Dental Assistant Report")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Patient Name: {patient_name}")
    c.drawString(50, 710, f"Mobile: {mobile}")
    c.drawString(50, 690, f"Language: {language}")
    c.drawString(50, 670, f"Area: {area}")
    c.drawString(50, 650, "Suggested Treatment Plan:")
    text = c.beginText(70, 630)
    for line in ai_insights.split(", "):
        text.textLine(line)
    c.drawText(text)
    c.drawString(50, 590, "Patient Education:")
    text2 = c.beginText(70, 570)
    for line in education_text.split("\n"):
        text2.textLine(line)
    c.drawText(text2)
    c.drawString(50, 540, f"Cost Estimate: ₹{cost}")
    c.showPage()
    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='treatment_plan.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
