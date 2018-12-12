import socket, threading, ssl
import time
import sys

class ClientThread(threading.Thread):
    
    def __init__(self, clientAddress, clientSocket):
        threading.Thread.__init__(self)
        self.csocket = clientSocket
        self.caddress = clientAddress
        print("New connection added: ", clientAddress)


    def run(self):

        print("Connection from a client: {}".format(self.caddress))
        msg = ''

        while True:

            data = self.csocket.recv(1024)
            msg = data.decode('ascii')
            print("Clients at address: {}, message is: {}".format(self.caddress, msg))            
            #self.csocket.send(bytes("HAPPYHAPPY",'ascii'))   
            if(len(data)>0):
                send_msg=input("GET MESSAGE: ")
                self.csocket.send(bytes(send_msg,'ascii'))   
                break
            elif(len(data)==0):
                break
        print("client at {} disconnected".format(self.caddress))


def main():
    host = "127.0.0.1"
    port = 443
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.settimeout(10)
    print("The server has been started")
    print("Waiting to connect with a client")
    try:
        while True:
            server.listen(1)
            clientSock, clientAddr = server.accept()
            
            #wrap the socket in SSL

            ssl_client_sock = ssl.wrap_socket(clientSock,
                                             server_side=True,
                                            certfile='./key/test.com.crt',
                                            keyfile='./key/test.com.key'
                                            )
            
            newThread = ClientThread(clientAddr, ssl_client_sock)
            newThread.daemon=True
            newThread.start()
    except:
        pass
    finally:
        server.close()
        sys.exit(1)


if __name__ in '__main__':
    main()