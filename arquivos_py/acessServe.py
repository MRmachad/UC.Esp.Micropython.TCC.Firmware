
import time
import socket
import binascii


class AcessServe():
 
    host = ""
    porta = 0
    sock = socket.socket()
    
    def __init__(self, host = str('192.168.100.8'), porta = 3040):
        #print(porta)
        self.host = host
        self.porta = porta
        pass
        
    def envia_servico(self, data_json):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host,  self.porta))

        
        content_length = len(data_json)
        #print("TAM ", len(data_json))
        headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", content_length, (self.host + ":" + str(self.porta))).encode()

        payload = headers + (data_json + "\r\n").encode()
        
                 
        
        self.sock.sendall(payload)
        payload = 0
        
        try:
            #print("\n######################################\n######################################")
            response = self.sock.recv(14100)
        
        except MemoryError as errin:
            #print(errin)
            pass

        else:
            if "OK" in response.decode():
                #print(response.decode())
                pass
            else:
                pass
                #print("\nSem ERRO no micro, mas ERRO no Seriço HTTP\n")            
        finally:    
            self.sock.close()


