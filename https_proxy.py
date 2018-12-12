import socket, threading, ssl
import time
import sys

class ProxyThread(threading.Thread):
    
    def __init__(self, clientAddress, clientSocket, port):
        threading.Thread.__init__(self)
        self.csocket = clientSocket
        self.caddress = clientAddress
        self.port=port
        print("New connection added: ", clientAddress)


    def run(self):

        print("Connection from a client: {}".format(self.caddress))
        msg = ''
        request=self.csocket.recv(20000).decode('ascii')
        Request_HOST=request[request.index("CONNECT"):request.index(":443")]
        User_Agent=request[request.index("User-Agent: "):]
        User_Agent=User_Agent[:User_Agent.index("\r\n")+2]
        HOST=Request_HOST[len("CONNECT")+1:]
        serverName=""
        serverPort=443
        serverName=HOST
        #print(serverName, serverPort, User_Agent)
        new_request=""
        new_request="GET / HTTP/1.1\r\nHost: "+serverName+"\r\n"+User_Agent+"\r\n"
        print(new_request)
        clientSocket2=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientSocket2= ssl.wrap_socket(clientSocket2, 
                           certfile='./key/test.com.crt',
                           keyfile='./key/test.com.key'
                        )
        clientSocket2.connect((serverName,serverPort))
        clientSocket2.send(bytes(new_request,"ascii"))

        try:
            while 1:
                data=clientSocket2.recv(20000)
                print(data)
                if(len(data)>0):
                   self.csocket.send(bytes(data,'ascii'))
                else:
                   break

        except:
            print("ERROR")

        finally:
            if(clientSocket2):
                clientSocket2.close()
            if(self.csocket):
                self.csocket.close()

        
def main():

    host = "127.0.0.1"
    port = 4433
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    #server.settimeout(10)
    print("The server has been started")
    print("Waiting to connect with a client")
    try:
        while True:
            
            clientSock, clientAddr = server.accept()
            #wrap the socket in SSL
            """
            ssl_client_sock = ssl.wrap_socket(clientSock,
                                             server_side=True,
                                            certfile='./key/test.com.crt',
                                            keyfile='./key/test.com.key'
                                            )
            """
            newThread = ProxyThread(clientAddr, clientSock, port)
            newThread.daemon=True
            newThread.start()
    except:
        pass
    finally:
        server.close()
        sys.exit(1)


if __name__ in '__main__':
    main()