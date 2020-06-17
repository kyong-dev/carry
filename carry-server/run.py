from carry import app
from threading import Thread
from carry.socket import background_thread

if __name__ == '__main__':
    """Main"""
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port='5000')
