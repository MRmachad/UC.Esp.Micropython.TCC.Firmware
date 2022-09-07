import gc
import os
import json
import socket
import struct
import micropython
from array import array


class AcessServe():

    sock = socket.socket()
    
    def __init__(self, dir = "/", host = "192.168.100.8", porta = 3060):
        self.dir = dir
        self.host = host
        self.porta = porta
        
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()

    def enviaPacs(self):
    
        for LoteX in sorted(os.listdir(self.dir + "/data")):

            for packs in sorted(os.listdir(self.dir + "/data/" + LoteX)):
                
                input_file = open((self.dir + "/data/"+ str(LoteX) + "/" + packs), 'r+b')

                try:
                    
                    bytesfile = input_file.read()
                    float_array = array('f', struct.unpack((2*170*3*'f'), bytesfile))

                    pack = [packs[2:packs.rfind("C")],packs[packs.rfind("C")+1:]]
                   
                    self.envia_servico(self.modelosStringJson(pack[0],float_array[:170*3]))
                    
                    self.envia_servico(self.modelosStringJson(pack[1],float_array[170*3:170*3*2]))

                    os.remove(self.dir + "/data/" + LoteX + "/"  + packs)
                    
                except Exception as error:
                     print("\n=> Erro no setup de pacote: ", error)                  

                finally:
                     input_file.close()
                
    def modelosStringJson(self, pack, float_array, temperatura = 0):
        _id = pack[pack.rfind("B")+1:]
        TIni = self.pegaDate(pack[:pack.rfind("A")])
        TFim = self.pegaDate(pack[pack.rfind("A")+1:pack.rfind("B")])
        
        data = []
        for i in range(0, (len(float_array)) , 3):
            data.append({"aceleracaoX": float_array[i], "aceleracaoY": float_array[i+1],  "aceleracaoZ" : float_array[i+2], "temperatura": temperatura})
            
        
        idVaca = {"idVaca": int(_id)}
        horaFin = {"horaFin": TFim }
        horaIni = {"horaIni" : TIni}
        comportamentos = {"comportamentos": data}
        quantidade = {"quantidade":int(len(float_array)/3)}

        quantidade.update(comportamentos)
        quantidade.update(horaFin)
        quantidade.update(horaIni)
        quantidade.update(idVaca)

        return json.dumps(quantidade)
    
    def pegaDate(self, DAT = "2022_7_22_2_6_2"):
        
        date = []
        for i in range(DAT.count("_")):
            date.append(DAT[:DAT.find("_")])
            DAT = DAT[DAT.find("_") + 1:]
           
        return "{}-{}-{} {}:{}:{}.{}".format(date[0], date[1], date[2], date[3],  date[4], date[5], DAT)
    
    def envia_servico(self, data_json, _tentativas = 6, sockTimeout = 10):

        self.esvazia_memoria()

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

            headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", len(data_json), (self.host + ":" + str(self.porta)))
            
            self.sock.sendall('{}{}'.format(headers, data_json).encode())
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

