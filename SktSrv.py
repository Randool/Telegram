import queue
import socket
import time

import _thread


hostname = socket.gethostname()
port = 12345

"""
The info stored in the queue should be like this:
"sender|receiver|timestamp|msg"
and all item is str.
"""
MsgQ = {}


def Sender(sock, UserID):
    """
    Fetch 'info' from queue send to UserID.
    """
    Q = MsgQ[UserID]
    try:
        while True:
            # get methord will be blocked if empty
            info = Q.get()
            sock.send(info.encode())
    except Exception as e:
        print(e)
        sock.close()
        _thread.exit_thread()


def Receiver(sock):
    """
    Receive 'msg' from UserID and store 'info' into queue.
    """
    try:
        while True:
            info = sock.recv(1024).decode()
            print(info)
            info_unpack = info.split("|")
            receiver = info_unpack[1]
            
            exit_cmd = receiver == "SEVER" and info_unpack[3] == "EXIT"
            assert not exit_cmd, "{} exit".format(info_unpack[0]) 
            
            if receiver not in MsgQ:
                MsgQ[receiver] = queue.Queue()
            MsgQ[receiver].put(info)

    except Exception as e:
        print(e)
        sock.close() 
        _thread.exit_thread()


class Server:
    def __init__(self):
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Sock.bind((hostname, port))
        self.Sock.listen()
        # self.threads = []

    def run(self):
        print("\033[35;40m[ Server is running ]\033[0m")
        # print("[ Server is running ]")
        while True:
            sock, _ = self.Sock.accept()

            # Register for new Client
            UserID = sock.recv(1024).decode()
            print("Connect to {}".format(UserID))

            # Build a message queue for new Client
            if UserID not in MsgQ:
                MsgQ[UserID] = queue.Queue()

            # Start two threads
            _thread.start_new_thread(Sender, (sock, UserID))
            _thread.start_new_thread(Receiver, (sock,))

    def close(self):
        self.Sock.close()


if __name__ == "__main__":
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt as e:
        server.close()
        print("Server exited")
