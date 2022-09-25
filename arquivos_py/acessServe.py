import gc
import os
import json
import time
import socket
import struct
import micropython
from array import array




class AcessServe():

    sock = socket.socket()
    
    def __init__(self, dir = "/", host = "45.166.184.6", _rota = "pink-ws/producao/comportamento", porta = 2041):
        self.dir = dir
        self.host = host
        self.porta = porta
        self.rota = _rota
        
    def enviaPacs(self):
    
        for LoteX in sorted(os.listdir(self.dir + "/data")):

            pacBytes = ((170*3) + 15)
            input_file = open((self.dir + "/data/" + LoteX), 'r+b')
            nBytes = input_file.seek(0,2)
            input_file.seek(0)

            try:
                while input_file.tell() != nBytes:
                    
                    bytesfile = input_file.read(pacBytes*4)
                    float_array = array('f', struct.unpack((pacBytes*'f'), bytesfile))               
                    
                    self.esvazia_memoria()
                    self.envia_servico(self.modelosStringJson(float_array))
                        
                    print("\n=> ponteiro atual envio :" ,  input_file.tell())
                    
            except Exception as error:
                print("\n=> Erro no setup de pacote: ", error)                  

            finally:
                input_file.close()
                    
            os.remove(self.dir + "/data/" + LoteX)
    
    def envia_servico(self, data_json, _tentativas = 2, sockTimeout = 10):

        
        print("\nEntrou aqui\n")
        
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

            headers = ("POST /{} HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format(self.rota,"application/json", len(data_json), (self.host + ":" + str(self.porta)))
            self.esvazia_memoria()
            print(headers)
            print(len(data_json))
            self.sock.sendall('{}{}'.format(headers, data_json).encode())
            payload = 0

            try:
                response = self.sock.recv(1000)
                print("resposta", response.decode())
                 
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

    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
     

    def modelosStringJson(self, float_array, temperatura = 0):
        print("AQUI")
        _id = int(float_array[0])

        TIni = "{}-{}-{} {}:{}:{}".format(int(float_array[1]), int(float_array[2]), int(float_array[3]), int(float_array[4]), int(float_array[5]), (float_array[6] + float_array[7]/10000))  
        TFim = "{}-{}-{} {}:{}:{}".format(int(float_array[8]), int(float_array[9]), int(float_array[10]), int(float_array[11]), int(float_array[12]), (float_array[13] + float_array[14]/10000))
  
        data = []
        aux =  0
        for cont in range(15,len(float_array), 3):
            data.append({"hora": "" , "aceleracaoX": float_array[cont], "aceleracaoY": float_array[cont+1],  "aceleracaoZ" : float_array[cont+2], "temperatura": temperatura})
            aux+=1

        idVaca = {"idVaca": _id}
        horaFin = {"horaFim": TFim }
        horaIni = {"horaInicio" : TIni}
        comportamentos = {"comportamentos": data}
        quantidade = {"quantidade":int(len(float_array[15:])/3)}

        quantidade.update(comportamentos)
        quantidade.update(horaFin)
        quantidade.update(horaIni)
        quantidade.update(idVaca)

        return json.dumps(quantidade)
    