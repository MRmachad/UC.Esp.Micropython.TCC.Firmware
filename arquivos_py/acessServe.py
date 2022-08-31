
import time
import socket
import binascii


class AcessServe():
 
    host = ""
    porta = 0
    sock = socket.socket()
    
    def __init__(self, host = str('192.168.100.8'), porta = 3040):
        self.host = host
        self.porta = porta
        pass
        
    def envia_servico(self, data_json, _tentativas = 6, sockTimeout = 10):
        tentativas = _tentativas
        while tentativas:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(sockTimeout)
                self.sock.connect((self.host,  self.porta))
                break
            except Exception as error:
                print("\n=> Tentativa N: ",(_tentativas-tentativas)," ||Conecção com o serviço http em falha, erro: " , error)
                tentativas -= 1
                pass

        if tentativas != 0:
        
            content_length = len(data_json)
            headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", content_length, (self.host + ":" + str(self.porta))).encode()

            payload = headers + (data_json + "\r\n").encode()

            
            self.sock.sendall(payload)
            payload = 0
            
            try:
                response = self.sock.recv(1000)
            
            except MemoryError as errin:
                print("\n=> Não foi possivel alocar memoria para resposta", errin)
                pass

            else:
                if "OK" in response.decode():
                    print(response.decode())
                    pass
                else:
                    pass
                    print("\n=> Sem ERRO no micro, mas ERRO no Seriço HTTP\n")            
            finally:    
                self.sock.close()
                return True
        return False

