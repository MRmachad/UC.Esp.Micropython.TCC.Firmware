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
<<<<<<< HEAD
        self.rota = _rota
        
=======
    
>>>>>>> master
    def enviaPacs(self):
    
        for LoteX in sorted(os.listdir(self.dir + "/data")):

<<<<<<< HEAD
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
=======
            for packs in sorted(os.listdir(self.dir + "/data/" + LoteX)):
                
                input_file = open((self.dir + "/data/"+ str(LoteX) + "/" + packs), 'r+b')

                try:
                    
                    bytesfile = input_file.read()
                    float_array = array('f', struct.unpack((2*170*3*'f'), bytesfile))

                    pack = [packs[2:packs.rfind("C")],packs[packs.rfind("C")+1:]]
                   
                    
                    
                    for item in self.modelosStringJson(pack[0],float_array[:170*3]):
                        
                        self.esvazia_memoria()
                        self.envia_servico(item)
                    
                    
                    
                    for item in self.modelosStringJson(pack[1],float_array[170*3:170*3*2]):
                        self.esvazia_memoria()
                        self.envia_servico(item)

                    os.remove(self.dir + "/data/" + LoteX + "/"  + packs)
                    
                except Exception as error:
                    print("\n=> Erro no setup de pacote: ", error)                  

                finally:
                    input_file.close()
    
    def envia_servico(self, data_json, _tentativas = 6, sockTimeout = 10):
>>>>>>> master

        
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

<<<<<<< HEAD
            headers = ("POST /{} HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format(self.rota,"application/json", len(data_json), (self.host + ":" + str(self.porta)))
            self.esvazia_memoria()
            print(headers)
            print(data_json)
            self.sock.sendall('{}{}'.format(headers, data_json).encode())
            payload = 0

            try:
                response = self.sock.recv(1000)
                print("resposta", response.decode())
                 
=======
            headers = ("POST /envio HTTP/1.1\r\nContent-Type: {}\r\nContent-Length: {}\r\nHost: {}\r\nAccept: */*\r\nConnection: close\r\n\r\n").format("application/json", len(data_json), (self.host + ":" + str(self.porta)))
            self.esvazia_memoria()
            
            print(len(data_json))
            self.sock.sendall('{}{}'.format(headers, data_json).encode())
            payload = 0
            
            try:
                response = self.sock.recv(1000)
            
>>>>>>> master
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
     

<<<<<<< HEAD
    def modelosStringJson(self, float_array, temperatura = 0):
        print("AQUI")
        _id = int(float_array[0])

        data = []
        aux =  0
        for cont in range(15,len(float_array), 3):
            data.append({"hora": "" , "aceleracaoX": float_array[cont], "aceleracaoY": float_array[cont+1],  "aceleracaoZ" : float_array[cont+2], "temperatura": temperatura})
            aux+=1

        idVaca = {"idVaca": _id}
        
   
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
=======
    def modelosStringJson(self, pack, float_array, temperatura = 0, corte = 85):
        _id = pack[pack.rfind("B")+1:]
        TIni = self.pegaDate(pack[:pack.rfind("A")])
        TFim = self.pegaDate(pack[pack.rfind("A")+1:pack.rfind("B")])

        TDist = self.DistTimeStanp(TIni,TFim)
        
        processado = []
        data = []
        aux =  0
        for cont in range(0,len(float_array), 3):
            data.append({"horario": TDist[aux] ,"aceleracaoX": float_array[cont], "aceleracaoY": float_array[cont+1],  "aceleracaoZ" : float_array[cont+2], "temperatura": temperatura})
            aux+=1

        processado.append(self.juntaLinha(_id, data[:corte]))
        processado.append(self.juntaLinha(_id, data[corte:]))    
        return processado
    
    def juntaLinha(self, _id, data):
        
        idVaca = {"idVaca": int(_id)}
        comportamentos = {"comportamentos": data}
        quantidade = {"quantidade": len(data)}

        quantidade.update(idVaca)
        quantidade.update(comportamentos)
        return json.dumps(quantidade)
            
    def pegaDate(self, DAT = "2022_7_22_2_6_2"):
        
        print(DAT)
        
        date = []
        for i in range(DAT.count("_")):
            date.append(DAT[:DAT.find("_")])
            DAT = DAT[DAT.find("_") + 1:]
           
        return [int(date[0]), int(date[1]), int(date[2]), int(date[3]), int(date[4]), float(date[5] + "." + DAT)]

    def DistTimeStanp(self, TIni = {}, TFim = {}):

        dif = self.divisao(self.subtracao(TIni, TFim), 170)

        print("\n=> resto da divisão", dif)

        aux = ["{}-{}-{} {}:{}:{}".format(TIni[0],TIni[1],TIni[2],TIni[3],TIni[4],TIni[5])]        
        for i in range(170):
            TIni = self.soma(TIni, dif)
            aux.append("{}-{}-{} {}:{}:{}".format(TIni[0],TIni[1],TIni[2],TIni[3],TIni[4],TIni[5]))
        
        #print("\n => saida do DistTimeStanp", aux)
        return aux 

    def subtracao(self, data1, data2):
        tempo = [0,0,0,0,0,0]
        for i in range(6):
            tempo[i] = data2[i] - data1[i]
        # Segundos
        for i in range (2):
            if tempo[5-i] < 0:
                tempo[4-i] = tempo[4-i] - 1
                tempo[5-i] = 60 + tempo[5-i]
        # Horas
        if tempo[3] < 0:
            tempo[2] = tempo[2] - 1
            tempo[3] = 24 + tempo[3]
        # Dias
        if tempo[2] < 0:
            cont = self.descobre_mes(data2[1], data2[0])
            tempo[1] = tempo[1] - 1
            tempo[2] = cont + tempo[2]
        # Mes
        if tempo[1] < 0:
            tempo[0] = tempo[0] - 1
            tempo[1] = 12 + tempo[1]
        
        return tempo

    def soma(self, data1, valor):
        tempo = [0,0,0,0,0,0]
        for i in range(6):
            tempo[i] = data1[i] + valor[i]
        for i in range(2):
            if tempo[5-i] >= 60:
                tempo[5-i] = tempo[5-i] - 60
                tempo[4-i] = tempo[4-i] + 1
        if tempo[3] >= 24:
            tempo[3] = tempo[3] - 24
            tempo[2] = tempo[2] + 1
        cont = self.descobre_mes(data1[1], data1[0])
        if tempo[2] > cont:
            tempo[2] = tempo[2] - cont
            tempo[1] = tempo[1] + 1
        if tempo[1] > 12:
            tempo[1] = tempo[1] - 12
            tempo[0] = tempo[0] + 1

        return tempo

    def divisao(self, data1, valor):
        tempo = self.transf_segundos(data1)
        div = tempo / valor
        data = [0,0,0,0,0,0]
        pesos = [12,30,24,60,60,1]
        for a in range(6):
            pesos_div = 1
            for i in range(6-a):
                pesos_div = pesos_div * pesos[i+a]
            data[a] = int(div // pesos_div)
            div = div % pesos_div
        data[5] = data[5] + div
        return data

    def transf_segundos(self, data):
        pesos = [12,30,24,60,60,1]
        tempo = 0
        for a in range(6):
            segundos = 1
            for i in range(6-a):
                segundos = segundos * pesos[i+a]
            tempo = data[a] * segundos + tempo
        return tempo

    def descobre_mes(self, mes, ano):
        mes30 = [4, 6, 9, 11]
        mes31 = [1, 3, 5, 7, 8, 10, 12]
        cont = 0
        for mes in mes30:
            cont = 30
        for mes in mes31:
            cont = 31
        if cont == 0:
            res = ano % 4
            if res == 0:
                cont = 29
        if cont == 0:
            cont = 28
        return cont
>>>>>>> master

        quantidade.update(ano2)
        quantidade.update(mes2)
        quantidade.update(dia2)
        quantidade.update(hora2)
        quantidade.update(minuto2)
        quantidade.update(segundo2)
        quantidade.update(milisegundo2)

        return json.dumps(quantidade)
    