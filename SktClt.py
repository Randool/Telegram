import socket
import sys, os
import time
import base64
import _thread
from SktSrv import hostname, port

b64decode = lambda x: base64.b64decode(x.encode()).decode()
b64encode = lambda x: base64.b64encode(x.encode()).decode()


def Receiver(sock):
    from_id = ""
    fr = None   # file handle
    while True:
        info = sock.recv(1024).decode()
        info_unpacks = info.split("||")[:-1]
        for info_unpack in info_unpacks:
            sender, _, timestamp, msg = info_unpack.split("|")
            msg = b64decode(msg)    # base64解码

            # Start a new session
            if from_id != sender:
                from_id = sender
                print("==== {} ====".format(sender))
            
            if msg[:5] == "@FILE":  # FILENAME,FILE,FILEEND
                # print(msg)
                if msg[:10] == "@FILENAME:":
                    print("++Recvive {}".format(msg[9:]))
                    fr = open(msg[10:]+".txt", "w")
                elif msg[:9] == "@FILEEND:":
                    fr.close()
                    print("++Recvive finish")
                elif msg[:6] == "@FILE:":
                    fr.write(msg[6:])
                continue

            show = "{}\t{}".format(timestamp, msg)
            print("\033[1;36;40m{}\033[0m".format(show))


class Client:
    def __init__(self, UserID: str=None):
        if UserID is not None:
            self.UserID = UserID
        else:
            self.UserID = input("login with userID >> ")
        self.Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_addr = (hostname, port)

    def Sender(self):
        """ 
        Send info: "sender|receiver|timestamp|msg"
        Change to name: '@switch:name'
        Trans file: '@trans:filename'
        """
        targetID = input("Chat with > ")
        while True:
            msg = input()
            if not len(msg):
                continue

            lt = time.localtime()
            timestamp = "{}:{}:{}".format(lt.tm_hour, lt.tm_min, lt.tm_sec)

            if msg == "@exit":          # 退出
                print("Bye~")
                return

            elif msg == "@help":
                continue

            elif msg[:8] == "@switch:": # 切换聊天对象
                targetID = msg.split(":")[1]
                print("++Switch to {}".format(targetID))
                continue
            
            elif msg[:7] == "@trans:":  # 发送文件
                filename = msg.split(":")[1]
                if not os.path.exists(filename):
                    print("!!{} no found".format(filename))
                    continue
                print("++Transfer {} to {}".format(filename, targetID))
                head = "{}|{}|{}|{}||".format(self.UserID, targetID, timestamp, b64encode("@FILENAME:"+filename))
                self.Sock.send(head.encode())
                with open(filename, "r") as fp:
                    while True:
                        chunk = fp.read(512)
                        if not chunk:
                            break
                        chunk = "{}|{}|{}|{}||".format(self.UserID, targetID, timestamp, b64encode("@FILE:"+chunk))
                        self.Sock.send(chunk.encode())
                tail = "{}|{}|{}|{}||".format(self.UserID, targetID, timestamp, b64encode("@FILEEND:"+filename))
                self.Sock.send(tail.encode())
                print("++Done.")
                continue
            
            info = "{}|{}|{}|{}||".format(self.UserID, targetID, timestamp, b64encode(msg))
            self.Sock.send(info.encode())

    def run(self):
        try:
            self.Sock.connect(self.server_addr)
            print("\033[35;40m[ Client is running ]\033[0m")
            # print("[ Client is running ]")

            # Register UserID
            self.Sock.send(self.UserID.encode())

            # Start Receiver threads
            _thread.start_new_thread(Receiver, (self.Sock,))
            self.Sender()   # Use for Send message

        except BrokenPipeError:
            print("\033[1;31;40mMissing connection\033[0m")

        finally:
            print("\033[1;33;40mYou are offline.\033[0m")
            self.exit_client()
            self.Sock.close()

    def exit_client(self):
        bye = "{}|{}|{}|{}".format(self.UserID, "SEVER", "", "EXIT")
        self.Sock.send(bye.encode())


if __name__ == "__main__":
    client = Client()
    client.run()
