import sqlite3
import threading
import socket

DATABASE = 'devices.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

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
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT D0, D1, D2, D3, D4, D5, D6, D7, D8 FROM users WHERE auth_key = ?", (auth_code,))
                user_status = cursor.fetchone()
                if user_status:
                    status_message = ','.join([f"D{i}={user_status[i]}" for i in range(9)]) + '\n'
                    conn.sendall(status_message.encode())
                else:
                    conn.sendall(b'No status available\n')
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
    start_tcp_server()
