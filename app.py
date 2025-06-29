from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
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
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered')
    return render_template('registration.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    patient_name = request.form.get('patient_name')
    mobile = request.form.get('mobile')
    uploaded_file_paths = []
    ai_insights_combined = []

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            uploaded_file_paths.append(filepath)

            # Simulated AI insight for each image
            ai_insight = f"Suspicious region detected in {filename} for {patient_name}. Suggested clinical correlation."
            ai_insights_combined.append(ai_insight)

    return render_template(
        'main-app.html',
        message='Files uploaded successfully',
        image_paths=uploaded_file_paths,
        ai_insights_list=ai_insights_combined,
        patient_name=patient_name,
        mobile=mobile
    )

if __name__ == '__main__':
    app.run(debug=True)

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
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials')
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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered')
    return render_template('registration.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    patient_name = request.form.get('patient_name')
    mobile = request.form.get('mobile')
    language = request.form.get('language', 'English')
    area = request.form.get('area', 'Urban')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Simulate AI Analysis Placeholder
        ai_insights = f"Suspicious region detected in upper left molar for {patient_name}. Suggested clinical correlation."

        # Cost estimation based on area
        cost = 5000 if area == 'Urban' else 3000

        # Education text based on language
        education_text = {
            'English': 'Maintain good oral hygiene and visit your dentist regularly.',
            'Regional': 'स्थानीय भाषा में मरीज शिक्षा संदेश।'  # Replace with actual regional language text
        }.get(language, '')

        return render_template(
            'main-app.html',
            message='File uploaded successfully',
            image_path=filepath,
            ai_insights=ai_insights,
            patient_name=patient_name,
            mobile=mobile,
            cost=cost,
            education_text=education_text,
            language=language,
            area=area
        )
    return render_template('main-app.html', error='No file uploaded')

@app.route('/export-pdf', methods=['POST'])
