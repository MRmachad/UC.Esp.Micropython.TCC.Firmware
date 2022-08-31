import gc
import os
import time
import socket
import struct
import binascii
import micropython
from array import array
from arquivos_py.model.modelos import Modelos



class AcessServe():

    sock = socket.socket()
    
    def __init__(self, dir = "/", host = "192.168.100.8", porta = 3060):
        self.dir = dir
        self.host = host
        self.porta = porta
        
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
        
    def envia_servico(self, data_json, _tentativas = 6, sockTimeout = 10):
        print(data_json)
        
        tentativas = _tentativas
        while tentativas:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(sockTimeout)
                self.sock.connect((self.host,  self.porta))
                
                headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", len(data_json), (self.host + ":" + str(self.porta))).encode()
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
                
            except Exception as error:
                print("\n=> Tentativa N: ",(_tentativas-tentativas)," ||Conecção com o serviço http em falha, erro: " , error)
                tentativas -= 1
                pass
        return False
    
    def enviaPacs(self):
        
        v_dirs_envio = sorted(os.listdir(self.dir + "/data"))
        
        for LoteX in v_dirs_envio:
            
            realBin = sorted(os.listdir(self.dir + "/data/" + LoteX))
            
            for packs in (realBin):
                
                self.esvazia_memoria()
                input_file = open((self.dir + "/data/"+ str(LoteX) + "/" + packs), 'r+b')

                try:
                    bytesfile = input_file.read()
                    
                    float_array = array('f', struct.unpack((2*170*3*'f'), bytesfile))
                    
                    pack = [packs[2:packs.rfind("C")],packs[packs.rfind("C")+1:]]
                    
                    model = Modelos(pack[0],float_array[:170*3])
                    self.envia_servico(model.jsonString())
                    
                    model = Modelos(pack[1],float_array[170*3:170*3*2])
                    self.envia_servico((model.jsonString()))
                    
                    os.remove(self.dir + "/data/" + LoteX + "/"  + packs)
                        
                except Exception as error:
                    print("\n=> Erro de envio: ", error)                  

                finally:
                    input_file.close()


