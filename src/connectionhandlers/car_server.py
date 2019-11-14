import socket
import csv
import json
import select

import threading

#####################
## VERY SIMPLE MESSAGE RECEIVER FOR ABM CAR
#####################


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)
    return d


class carServer():

    def __init__(self, port=10011, bind="localhost", outfile="stream.csv"):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.server_address = (bind, port)

    def start(self):

        def handle_connection(connection, client_address):
            outfile = open("stream_{}.csv".format(client_address[0]), 'a', newline='', encoding='UTF-8')
            csv_writer = csv.writer(outfile, delimiter=',')
            timeout_in_seconds = 20

            connection.sendall("READY".encode(("UTF-8")))

            ready = select.select([connection], [], [], timeout_in_seconds) # WAITING FOR LENGTH INFO
            if ready[0]:

                # FIRST: RECEIVING LENGTH OF THE UPCOMING MESSAGE
                data = connection.recv(12)

                data = data.decode("UTF-8")

                if len(data) > 0:

                    next_message_length = int(str(data[7:]))

                    # CONFIRM THAT I RECEIVED THE LENGTH INFO
                    connection.sendall("OK".encode("UTF-8"))

                    # WAIT FOR MESSAGE
                    ready = select.select([connection], [], [], timeout_in_seconds)
                    if ready[0]:

                        # RECEIVE DATA
                        data = connection.recv(next_message_length)

                        dictionary = eval(data.decode("UTF-8"))

                        csv_writer.writerow([str(dictionary)])
                        outfile.close()

                        # CONFIRM I AM READY FOR NEXT CONNECTION
                        connection.sendall("NEXT".encode("UTF-8"))
                        connection.close()



        print("starting up on {} port {}".format(self.server_address[0], self.server_address[1]))
        self.sock.bind(self.server_address)

        # Listen for incoming connections
        self.sock.listen(1)

        while True:
            # Wait for a connection
            #print('waiting for a connection')
            connection, client_address = self.sock.accept()

            #print('connection from {}'.format(client_address))

            t = threading.Thread(target=handle_connection, args=(connection, client_address,))
            t.start()

            # self.csv_writer.writerow(incoming_dictionary)

# Clean up the connection


