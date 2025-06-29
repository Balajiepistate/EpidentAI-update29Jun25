from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    language = request.form.get('language')
    area = request.form.get('area')

    uploaded_file_paths = []
    ai_insights_list = []

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            uploaded_file_paths.append(filepath)

            insight = f"Suspicious region detected in {filename} for {patient_name}. Suggested clinical correlation."
            ai_insights_list.append(insight)

    cost = 2000 if area == "Urban" else 1500
    education_text = "Please maintain good oral hygiene." if language == "English" else "कृपया अच्छी मौखिक स्वच्छता बनाए रखें।"

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

if __name__ == '__main__':
    app.run(debug=True)
