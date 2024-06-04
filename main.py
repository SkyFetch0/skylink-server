import threading
from web_app import app, init_db
import server

if __name__ == '__main__':
    init_db()
    tcp_thread = threading.Thread(target=server.start_tcp_server)
    tcp_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
