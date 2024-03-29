# Python imports
import threading, socket, time
from multiprocessing.connection import Listener, Client

# Lib imports

# Application imports


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()
    return wrapper




class IPCServer:
    ''' Create a listener so that other instances send requests back to existing instance. '''
    def __init__(self):
        self.is_ipc_alive   = False
        self.ipc_authkey    = b'pytop-ipc'
        self.ipc_address    = '127.0.0.1'
        self.ipc_port       = 8888
        self.ipc_timeout    = 15.0

    @threaded
    def create_ipc_server(self):
        listener          = Listener((self.ipc_address, self.ipc_port), authkey=self.ipc_authkey)
        self.is_ipc_alive = True
        while True:
            conn       = listener.accept()
            start_time = time.time()

            print(f"New Connection: {listener.last_accepted}")
            while True:
                msg = conn.recv()
                if debug:
                    print(msg)

                if "FILE|" in msg:
                    file = msg.split("FILE|")[1].strip()
                    if file:
                        event_system.push_gui_event([None, "handle_file_from_ipc", (file,)])

                    conn.close()
                    break


                if msg == 'close connection':
                    conn.close()
                    break
                if msg == 'close server':
                    conn.close()
                    break

                # NOTE: Not perfect but insures we don't lockup the connection for too long.
                end_time = time.time()
                if (end - start) > self.ipc_timeout:
                    conn.close()

        listener.close()


    def send_ipc_message(self, message="Empty Data..."):
        try:
            conn = Client((self.ipc_address, self.ipc_port), authkey=self.ipc_authkey)
            conn.send(message)
            conn.send('close connection')
        except Exception as e:
            print(repr(e))
