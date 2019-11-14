import socket
import sys
import select


class socketClient():

    def __init__(self, port=10012, server_address="localhost"):
        # Create a TCP/IP socket
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the carServer is listening
        self.server_address = (server_address, port)
        print('Using follwoing connection: %s port %s' % self.server_address)



    def connect(self):
        '''
        Connect to server
        :return:
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server_address)

    def send_data(self, data=None):
        '''
        Send data
        :param data:
        :return:
        '''
        # Send dat
        self.connect()
        bytedata = str(data).encode("UTF-8")

        ready = select.select([self.sock], [], [], 20)

        if ready[0] and self.sock.recv(5).decode("UTF-8") == "READY": # GOT REPLY: "READY"

            self.sock.sendall("length-{}".format(len(bytedata)).encode("UTF-8"))

            ready = select.select([self.sock], [], [], 20)
            if ready[0]:

                answer = self.sock.recv(2).decode(("UTF-8"))

                if answer == "OK":

                    self.sock.sendall(bytedata)

                ready = select.select([self.sock], [], [], 20)
                if ready[0]:
                    answer = self.sock.recv(4).decode(("UTF-8"))

                    if not answer == "NEXT":
                        print("[ERROR] I EXPECTED NEXT...")
                        raise ConnectionError("HALLO")

        self.close_socket()


    def close_socket(self):
        '''
        Close the socket
        :return:
        '''
        self.sock.close()
