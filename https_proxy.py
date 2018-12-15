import socket, threading, ssl
import time
import sys
import os

thread_lock = threading.Lock()

class ProxyThread(threading.Thread):
    
    def __init__(self, clientAddress, clientSocket, port):
        threading.Thread.__init__(self)
        self.csocket = clientSocket
        self.caddress = clientAddress
        self.port=port
        print("New connection added: ", clientAddress)


    def run(self):
        try:
            print("Connection from a client: {}".format(self.caddress))
            request=self.csocket.recv(20000).decode('ascii')
            Request_HOST=request[request.index("CONNECT"):request.index(":443")]
            User_Agent=request[request.index("User-Agent: "):]
            User_Agent=User_Agent[:User_Agent.index("\r\n")+2]
            HOST=Request_HOST[len("CONNECT")+1:]
            serverName=""
            serverPort=443
            serverName=HOST
            
            self.csocket.send(bytes("HTTP/1.1 200 Connection established\r\n\r\n",'ascii'))

        except:
            if(self.csocket):
                self.csocket.close()
            return
       
        certfile=("./cert/%s.pem"%serverName)
     
        if not os.path.exists(certfile):
            thread_lock.acquire()
            os.system('cd cert && sh _make_site.sh ' + serverName)
            thread_lock.release()
        
        self.csocket=ssl.wrap_socket(self.csocket, certfile=certfile, server_side=True)

        new_request=self.csocket.recv(20000).decode('ascii')
        
        ssl_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_send.connect((serverName,serverPort))
        clientSocket2= ssl.wrap_socket(ssl_send)
        clientSocket2.send(bytes(new_request,"ascii"))

        try:
            while 1:
                data=clientSocket2.recv(20000)
                #print(data)
                if(len(data)>0):
                   self.csocket.send(data)
                else:
                   break

        except:
            print("ERROR")

        finally:
            if(clientSocket2):
                clientSocket2.close()
            if(self.csocket):
                self.csocket.close()

def usage():
    print("syntax: python3 https_proxy <port>");
    print("sample: python3 https_proxy 4433");


def main():
    
    if(len(sys.argv)!=2):
        usage()
        return -1
    
    host = "127.0.0.1"
    port=int(sys.argv[1])
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    server.settimeout(10)
    print("The server has been started")
    print("Waiting to connect with a client")

    #only the first time!
    #os.system('cd cert && sh _clear_site.sh')
    #os.system('cd cert && sh _init_site.sh')

    try:
        while True:            
            clientSock, clientAddr = server.accept()
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