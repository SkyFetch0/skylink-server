from flask import Flask, render_template, request, jsonify
import sqlite3
import threading
import socket

app = Flask(__name__)

DATABASE = 'devices.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                auth_key TEXT PRIMARY KEY,
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS button_positions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                button_id TEXT,
                button_name TEXT,

                type TEXT,
                left TEXT,
                top TEXT,
                class TEXT,
                data_item TEXT
            )
        ''')
        db.commit()

@app.route('/')
def index():
    auth_key = request.args.get('auth')
    if not auth_key:
        return 'Auth key is required', 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE auth_key = ?", (auth_key,))
    user_data = cursor.fetchone()
    if user_data:
        print("User data from DB:", user_data)
        if len(user_data) == 10:  # auth_key + D0-D8
            device_status = {f'D{i}': user_data[i] for i in range(1, 10)}
            return render_template('panel.html', device_status=device_status)
        else:
            return 'Data format error', 500
    else:
        return 'User not found', 404

@app.route('/save_buttons', methods=['POST'])
def save_buttons():
    button_positions = request.json  

    db = get_db()
    cursor = db.cursor()

    for position in button_positions:
        if position['button_name'] == "TEST":
            continue
        
        print(position['button_name'])
        cursor.execute("SELECT * FROM button_positions WHERE button_id = ?", (position['button_id'],))
        existing_button = cursor.fetchone()

        if existing_button:
            cursor.execute('''
                UPDATE button_positions
                SET user_id=?, button_name=?, type=?, left=?, top=?, class=?, data_item=?
                WHERE button_id=?
            ''', (
                position['id'],
                position['button_name'],
                position['data-contype'],
                position['left'],
                position['top'],
                position['class'],
                position['data-item'],
                position['button_id']
            ))
        else:
            cursor.execute('''
                INSERT INTO button_positions (user_id, button_id, button_name, type, left, top, class, data_item)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position['id'],
                position['button_id'],
                position['button_name'],
                position['data-contype'],
                position['left'],
                position['top'],
                position['class'],
                position['data-item']
            ))

    db.commit()

    return jsonify({'message': 'Button positions saved successfully'}), 200


@app.route('/show_buttons')
def show_buttons():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM button_positions")
    button_positions = cursor.fetchall()
    db.close()

    return render_template('panel.html', button_positions=button_positions)

@app.route('/toggle_device', methods=['POST'])
def toggle_device():
    data = request.json
    print(data)
    auth_code = data['auth_code']
    device = data['device']
    is_checked = data['is_checked']

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT {} FROM users WHERE auth_key = ?".format(device), (auth_code,))
    current_status = cursor.fetchone()[0]

    new_status = 'OFF' if is_checked == 'OFF' else 'ON'

    cursor.execute(f"UPDATE users SET {device} = ? WHERE auth_key = ?", (new_status, auth_code))
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
        cursor.execute(f"UPDATE users SET {device} = ?, D8 = ? WHERE auth_key = ?", (status, message, auth_code))
        db.commit()
        return 'OK', 200
    else:
        return 'Invalid request', 400

def handle_client_connection(conn, addr):
    print('Connected by', addr)
    authenticated = False
    auth_code = None

    while True:
        data = conn.recv(1024)
        if not data:
            break
        message = data.decode().strip()
        if not authenticated:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE auth_key = ?", (message,))
            user = cursor.fetchone()
            if user:
                auth_code = message
                authenticated = True
                conn.sendall(b'Authenticated\n')
            else:
                conn.sendall(b'Invalid auth code\n')
        else:
            if message.startswith('STATUS'):
                device = message.split()[1]
                if device in [f'D{i}' for i in range(0, 9)]:
                    cursor = db.cursor()
                    cursor.execute(f"SELECT {device} FROM users WHERE auth_key = ?", (auth_code,))
                    status = cursor.fetchone()[0] + '\n'
                    conn.sendall(status.encode())
                else:
                    conn.sendall(b'Invalid device\n')
            else:
                conn.sendall(b'Invalid request\n')

    conn.close()
    print('Disconnected by', addr)

def start_tcp_server():
    HOST = '0.0.0.0'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f'TCP server listening on port {PORT}')

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
            client_thread.start()

if __name__ == '__main__':
    init_db()
    threading.Thread(target=start_tcp_server).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
