from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import sqlite3
import hashlib
import random
import string
app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'devices.db'


def generate_text():
    def random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    part1 = random_string(10)
    part2 = random_string(10)
    part3 = random_string(10)
    
    password = f"{part1}-{part2}-{part3}"
    return password

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                auth_key TEXT,
                D0 TEXT,
                D1 TEXT,
                D2 TEXT,
                D3 TEXT,
                D4 TEXT,
                D5 TEXT,
                D6 TEXT,
                D7 TEXT,
                D8 TEXT
            )
        ''')
        db.commit()
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_auth_key ON users_data (auth_key)')
        db.commit()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS button_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_auth TEXT,
                container_key TEXT,
                user_id TEXT,
                button_id TEXT,
                button_name TEXT,
                type TEXT,
                left TEXT,
                top TEXT,
                class TEXT,
                data_item TEXT,
                data_status TEXT
            )
        ''')
        db.commit()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_pass TEXT,
                user_mail TEXT,
                user_type TEXT,
                user_key TEXT
            )
        ''')
        db.commit()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS container (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                container_key TEXT,
                container_name TEXT,
                auth_key TEXT,
                container_type TEXT
            )
        ''')
        db.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))


# Register System
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_key = hashlib.md5(email.encode()).hexdigest()
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("INSERT INTO users (user_name, user_pass, user_mail, user_type, user_key) VALUES ( ?, ?, ?, ?, ?)", (username, hashed_password, email, 'user', user_key))
        db.commit()
        cursor.execute("INSERT INTO users_data (auth_key) VALUES ( ?)", (user_key,))
        db.commit()
        db.close()
        
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/panel')
def panel():
    if 'auth_key' in session:
        auth_key = session['auth_key']
        user_id = session['user_id']

        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_key = ?", (auth_key,))
        user_data = cursor.fetchone()
        
        if user_data:
            cursor.execute("SELECT * FROM button_positions WHERE user_id = ?", (auth_key,))
            button_positions = cursor.fetchall()
            cursor.execute("SELECT * FROM container WHERE user_id = ? AND auth_key = ?", (user_id,auth_key))
            container = cursor.fetchall()

            db.close()
            print("Giriş Ok")
            return render_template('panel.html', button_positions=button_positions, session=session , container=container)
        else:
            db.close()
            print("Geçersiz Oturum. Lütfen Tekrar Giriş Yapınız")
            flash('Geçersiz oturum. Lütfen tekrar giriş yapınız.', 'danger')
            return redirect(url_for('login'))
    else:
        print("Auth Key Bulunamadı")
        flash('Lütfen giriş yapınız.', 'danger')
        return redirect(url_for('index'))

# Login System
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_mail = ? AND user_pass = ?", (email, hashed_password))
        user = cursor.fetchone()
        db.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[4]

            session['auth_key'] = user[5]
            flash('Giriş başarılı!', 'success')
            print("Giriş Başarılı")
            return redirect(url_for('panel'))
        else:
            flash('Geçersiz e-posta veya şifre.', 'danger')
            print("Geçersiz Oturum")
            return redirect(url_for('login'))
    print("NO POST")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Çıkış başarılı!', 'success')
    return redirect(url_for('login'))

# Save User Button
@app.route('/save_buttons', methods=['POST'])
def save_buttons():
    button_positions = request.json

    db = get_db()
    cursor = db.cursor()

    for position in button_positions:
        if position['button_name'] == "TEST":
            continue

        cursor.execute("SELECT * FROM users WHERE user_key = ?", (position['auth'],))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'Invalid user key'}), 400

        cursor.execute("SELECT * FROM button_positions WHERE button_id = ?", (position['button_id'],))
        existing_button = cursor.fetchone()

        if existing_button:
            cursor.execute('''
                UPDATE button_positions
                SET user_id=?, button_name=?, type=?, left=?, top=?, class=?, data_item=?, data_status=?
                WHERE button_id=?
            ''', (
                position['id'],
                position['button_name'],
                position['data-contype'],
                position['left'],
                position['top'],
                position['class'],
                position['data-item'],
                position['data-status'],
                position['button_id']
            ))
        else:
            cursor.execute('''
                INSERT INTO button_positions (user_auth,container_key,user_id, button_id, button_name, type, left, top, class, data_item, data_status)
                VALUES (?,?,?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position['auth'],
                position['container'],
                position['user_id'],

                position['button_id'],
                position['button_name'],
                position['data-contype'],
                position['left'],
                position['top'],
                position['class'],
                position['data-item'],
                position['data-status']
            ))

    db.commit()
    db.close()

    return jsonify({'message': 'Button positions saved successfully'}), 200

# Create Container
@app.route('/create_container', methods=['POST'])
def create_container():
    data = request.json

    required_keys = ['user_auth', 'projectName', 'type','user_id']

    if all(key in data and data[key] for key in required_keys):
        user_auth = data['user_auth']
        projectName = data['projectName']
        type = data['type']
        user_id = data['user_id']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE user_key = ? AND id = ?", (user_auth,user_id))
        user = cursor.fetchone()

        if not user:
            return jsonify({'status': 'false','message': 'Invalid user key'}), 400
        new_key = generate_text()
        cursor.execute('''
                INSERT INTO container (user_id,auth_key,container_key, container_name, container_type)
                VALUES (?,?,?,?,?)
            ''', (
                user_id,
                user_auth,
                new_key,
                projectName,
                type
            ))
        db.commit()
        db.close()

        return jsonify({'status': 'success','cid': new_key}), 200
    else:
        return "Error: Missing or empty field(s)", 400


@app.route('/container/<container_key>', methods=['GET'])
def container(container_key):
    if container_key:
        if 'auth_key' in session:
            auth_key = session['auth_key']
            user_id = session['user_id']
            
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT * FROM users WHERE user_key = ?", (auth_key,))
            user_data = cursor.fetchone()
            
            if user_data:
                cursor.execute("SELECT * FROM container WHERE container_key = ? AND auth_key = ? AND user_id = ?", (container_key, auth_key, user_id))
                container_data = cursor.fetchone()
                

                if container_data:
                    cursor.execute("SELECT * FROM button_positions WHERE container_key = ? AND user_auth = ? AND user_id = ? ", (container_key,auth_key,user_id))
                    button_positions = cursor.fetchall()
                    print(auth_key)
                    print(container_key)
                    print(button_positions)
                    db.close()

                    return render_template('test.html', container_data=container_data, session=session,button_positions=button_positions)
                else:
                    return "Not Found Container", 404
            else:
                db.close()
                return "Not Found user Data", 404
        else:
            return redirect(url_for('index'))
    else:
        return "Not Found", 404

 

@app.route('/toggle_device', methods=['POST'])
def toggle_device():
    data = request.json
    auth_code = data['auth_code']
    device = data['device']
    type = data['type']

    action = data['action']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT {} FROM users_data WHERE auth_key = ?".format(device), (auth_code,))
    current_status = cursor.fetchone()[0]
    if type == "message":
        new_status = action
    else:
        new_status = 'OFF' if action == 'OFF' else 'ON'

   

    cursor.execute(f"UPDATE users_data SET {device} = ? WHERE auth_key = ?", (new_status, auth_code))
    db.commit()

    return 'OK', 200

@app.route('/set_device', methods=['POST'])
def set_device():
    auth_code = request.form['auth_code']
    status = request.form['status']
    device = request.form['device']
    message = request.form['message']

    if status in ["ON", "OFF"] and device in [f'D{i}' for i in range(0, 9)]:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f"UPDATE users_data SET {device} = ?, D8 = ? WHERE auth_key = ?", (status, message, auth_code))
        db.commit()
        return 'OK', 200
    else:
        return 'Invalid request', 400
