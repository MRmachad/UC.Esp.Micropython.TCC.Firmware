
import time
import socket
import binascii


class AcessServe():
 
    host = ""
    porta = 0
    sock = socket.socket()
    
    def __init__(self, host = str('192.168.100.8'), porta = 3040):
<<<<<<< HEAD
=======
        #print(porta)
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        self.host = host
        self.porta = porta
        pass
        
    def envia_servico(self, data_json, _tentativas = 6, sockTimeout = 10):
<<<<<<< HEAD
=======
        print("\n=>Chamou dnv\n")
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        tentativas = _tentativas
        while tentativas:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(sockTimeout)
                self.sock.connect((self.host,  self.porta))
                break
            except Exception as error:
<<<<<<< HEAD
                print("\n=> Tentativa N: ",(_tentativas-tentativas)," ||Conecção com o serviço http em falha, erro: " , error)
=======
                print("\n=>Tentativa N: ",(_tentativas-tentativas)," ||Conecção com o serviço http em falha, erro: " , error)
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
                tentativas -= 1
                pass

        if tentativas != 0:
        
            content_length = len(data_json)
<<<<<<< HEAD
            headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", content_length, (self.host + ":" + str(self.porta))).encode()

            payload = headers + (data_json + "\r\n").encode()

=======
            #print("TAM ", len(data_json))
            headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", content_length, (self.host + ":" + str(self.porta))).encode()

            payload = headers + (data_json + "\r\n").encode()
            
                     
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
            
            self.sock.sendall(payload)
            payload = 0
            
            try:
<<<<<<< HEAD
                response = self.sock.recv(1000)
            
            except MemoryError as errin:
                print("\n=> Não foi possivel alocar memoria para resposta", errin)
=======
                #print("\n######################################\n######################################")
                response = self.sock.recv(14100)
            
            except MemoryError as errin:
                print(errin)
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
                pass

            else:
                if "OK" in response.decode():
<<<<<<< HEAD
                    print(response.decode())
                    pass
                else:
                    pass
                    print("\n=> Sem ERRO no micro, mas ERRO no Seriço HTTP\n")            
=======
                    #print(response.decode())
                    pass
                else:
                    pass
                    print("\nSem ERRO no micro, mas ERRO no Seriço HTTP\n")            
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
            finally:    
                self.sock.close()
                return True
        return False

