import gc
import os
import json
import time
import socket
import struct
import micropython
from array import array

from arquivos_py.log import Log
from arquivos_py.onSd import OnSd



class AcessServe(Log):

    sock = socket.socket()
    
    def __init__(self, dir = "/", host = "45.166.184.6", _rota = "pink-ws/producao/comportamento", porta = 2041, ConjAmostra = 10):
        self.dir = dir
        self.host = host
        self.porta = porta
        self.rota = _rota
        self.ConjAmostra = ConjAmostra
        self.OB_Card = OnSd(self.dir)      
        
    def enviaPacs(self):

        aux_rename = 0
    
        for LoteX in self.OB_Card.contArq():
            
            flag_falha = False
            print("\nLotex :", LoteX)

            pacBytes = ((170*3) + 15)
            input_file = open((self.dir + "/data/" + LoteX), 'r+b')
            nBytes = input_file.seek(0,2)
            input_file.seek(0)

            try:
                while input_file.tell() != nBytes:
                    
                    bytesfile = input_file.read(pacBytes*4)
                    float_array = array('f', struct.unpack((pacBytes*'f'), bytesfile))               
                    
                    self.esvazia_memoria()
                    
                    status_res = self.envia_servico(self.modelosStringJson(float_array))
                    print("Retornor de resposta ", status_res)
                    if status_res == False:
                        flag_falha = True
                        break

            except Exception as errorENV:

                error = ("\n=> Erro no setup de pacote: " + str(errorENV))  
                self.addLog("AcessServe.txt", error)
                flag_falha = True

            finally:
                input_file.close()


            if flag_falha == False:    
                print("flag_falha ", flag_falha)
                print("\nREMOVENDO\n")
                os.remove(self.dir + "/data/" + LoteX)

            else:
                if nBytes >= self.ConjAmostra*2100:
                    print("aux_rename",aux_rename)
                    if str(aux_rename) not in self.OB_Card.contArq():

                        os.rename((self.dir + "/data/" + LoteX), (self.dir + "/data/" + str(aux_rename)))
                        aux_rename+=1

                    else:
                        aux_rename+=1
                else:
                    
                    if str(aux_rename) not in self.OB_Card.contArq():
                        os.rename((self.dir + "/data/" + LoteX), (self.dir + "/data/" + str(aux_rename)))
                    
                    return aux_rename, False
                
        return aux_rename, True

    def envia_servico(self, data_json, _tentativas = 2, sockTimeout = 10.0):
        
        status = False
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
            print("nas tentativas")
            headers = ("POST /{} HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format(self.rota,"application/json", len(data_json), (self.host + ":" + str(self.porta)))
            self.esvazia_memoria()

            self.sock.sendall('{}{}'.format(headers, data_json).encode())
            payload = 0

            try:
                self.sock.settimeout(sockTimeout)
                response = self.sock.recv(1000)
                 
            except Exception as errorRecev:
                error = ("\n=> Não foi possivel alocar memoria para resposta" + str(errorRecev))
                self.addLog("AcessServe.txt",error)   
                pass

            else:
                self.sock.settimeout(sockTimeout)
                result = response.decode()
                print(result)
                if result.count("OK") == 2:
                    status = True

                else:
                    print("\n=> Sem ERRO no micro, mas ERRO no Seriço HTTP\n")            
                    pass
            finally:    
                self.sock.close()
                
        else:
            error = ("\n=> falha na conecção com o serviço")
            self.addLog("AcessServe.txt",error)
        print("\n=>status de envio de pacote: ",status)    
        return status

    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
     
    def modelosStringJson(self, float_array, temperatura = 0):

        _id = int(float_array[0])

        data = []
        aux =  0
        for cont in range(15,len(float_array), 3):
            data.append({"hora": "" , "aceleracaoX": float_array[cont], "aceleracaoY": float_array[cont+1],  "aceleracaoZ" : float_array[cont+2], "temperatura": temperatura})
            aux+=1

        idVaca = {"id_vaca": _id}
        
   
        ano1 = {"ano1":int(float_array[1])}
        mes1 = {"mes1":int(float_array[2])}
        dia1 = {"dia1":int(float_array[3])}
        hora1 = {"hora1":int(float_array[4])}
        minuto1 = {"minuto1":int(float_array[5])}
        segundo1 = {"segundo1":int(float_array[6])}
        milisegundo1 = {"milisegundo1":int(float_array[7]/100)}

        ano2 = {"ano2":int(float_array[8])}
        mes2 = {"mes2":int(float_array[9])}
        dia2 = {"dia2":int(float_array[10])}
        hora2 = {"hora2":int(float_array[11])}
        minuto2 = {"minuto2":int(float_array[12])}
        segundo2 = {"segundo2":int(float_array[13])}
        milisegundo2 = {"milisegundo2":int(float_array[14]/100)}
        
        comportamentos = {"comportamentos": data}
        quantidade = {"quantidade":int(len(float_array[15:])/3)}

        quantidade.update(comportamentos)

        quantidade.update(idVaca)

        quantidade.update(ano1)
        quantidade.update(mes1)
        quantidade.update(dia1)
        quantidade.update(hora1)
        quantidade.update(minuto1)
        quantidade.update(segundo1)
        quantidade.update(milisegundo1)

        quantidade.update(ano2)
        quantidade.update(mes2)
        quantidade.update(dia2)
        quantidade.update(hora2)
        quantidade.update(minuto2)
        quantidade.update(segundo2)
        quantidade.update(milisegundo2)

        return json.dumps(quantidade)
    
