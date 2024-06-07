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
    container_key = None

    while True:
        try:
            data = conn.recv(1024)
            print(data)
            if not data:
                print(f'No data received, closing connection from {addr}')
                break

            message = data.decode().strip()
            
            if not authenticated:
                print("Not Auth(if)")
                parts = message.split()
                if len(parts) != 3 or parts[0] != "AUTH":
                    conn.sendall(b'Invalid request format\n')
                    continue

                auth_key = parts[1]
                container_key = parts[2]
                print(auth_key)
                print("AUTH_KEY: "+ auth_key +" | Container_key:  " + container_key)
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM users WHERE user_key = ?", (auth_key,))
                user = cursor.fetchone()
                if user:
                    cursor.execute("SELECT * FROM container WHERE auth_key = ? AND container_key = ?", (auth_key, container_key))
                    container = cursor.fetchone()
                    if container:
                        auth_code = auth_key
                        authenticated = True
                        print("Auth True")
                        conn.sendall(b'Authenticated\n')

                    else:
                        print("Invalid Container Key")
                        conn.sendall(b'Invalid container key\n')
                else:
                    print("Invalid Auth Key")
                    conn.sendall(b'Invalid auth key\n')
            else:
                parts = message.split()
                if len(parts) != 2:
                    conn.sendall(b'Invalid request format\n')
                    continue

                command = parts[0]
                container_key = parts[1]
                print("Komut : " + command + " | Container : "+container_key)

                if command == 'STATUS':
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT D0, D1, D2, D3, D4, D5, D6, D7, D8 FROM container WHERE auth_key = ? AND container_key = ?", (auth_code, container_key))
                    user_status = cursor.fetchone()
                    if user_status:
                        status_message = ','.join([f"D{i}={user_status[i]}" for i in range(9)]) + '\n'
                        conn.sendall(status_message.encode())
                    else:
                        print("No Status Availeblae")
                        conn.sendall(b'No status available\n')
                else:
                    print("Invalid Status Commands")
                    conn.sendall(b'Invalid request\n')
        except Exception as e:
            print(f'Error: {e}')
            break

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
