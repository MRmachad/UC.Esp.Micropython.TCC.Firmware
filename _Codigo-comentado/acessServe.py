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

"""
Classe destinada a interface com o serviço remoto via HTTP, aqui são definido tanto a porta de entrada quanto o endereço web do host pra que possamos envia os dados com requisição 
POST utilizando jsons para enpacotar os dados 
"""
class AcessServe(Log):

    sock = socket.socket()
 
"""
def __init__(self, host = str('192.168.100.8'), porta = 3040):
        Por padrão setamos a porta e o ip da maquina ontem o serviço esta rodando como 45.166.184.6 e porta 2041 ( que são as vias publicas do serviço que roda na fazenda)
        estes agumentos podem ser passados como paramentro na instacialização do objeto "AcessServe".
        Alem disso criamos um objeto(OB__card) do qual se fara uso para ler os dados armazenados em disco
"""   
    def __init__(self, dir = "/", host = "45.166.184.6", _rota = "pink-ws/producao/comportamento", porta = 2041):
        self.dir = dir
        self.host = host
        self.porta = porta
        self.rota = _rota
        self.OB_Card = OnSd(self.dir)      
  
"""
    def enviaPacs(self):
        É por meio deste metodo que os dados são lidos da flash e então são enviados. Isto é feito abrindo arquivo por arquivo os dados que são guardado e iterando conjunto por  conjunto no arquivo este
        e estes dados em formato de bytes são direcionados ao metodo modelosStringJson para que esse bytes sejam retornados para o Envia_servico  em formato de json string
"""
    def enviaPacs(self):

        aux_rename = 0
        flag_falha = False
    
        for LoteX in self.OB_Card.contArq():    # Recebe um vetor com os arquivos com a referencia dos arquivos nesta pasta
            
            print("Lotex :", LoteX)

            pacBytes = ((170*3) + 15)
            input_file = open((self.dir + "/data/" + LoteX), 'r+b')
            nBytes = input_file.seek(0,2)
            input_file.seek(0)

            try:
                while input_file.tell() != nBytes:
                    
                    bytesfile = input_file.read(pacBytes*4)                                #Lê os dados interando com o tmanho dos conjuntos de daods  e transforma isso em uma cadeia de array
                    float_array = array('f', struct.unpack((pacBytes*'f'), bytesfile))               
                    
                    self.esvazia_memoria()
                    if not(self.envia_servico(self.modelosStringJson(float_array))):
                        flag_falha = True                                                  #Caso ocorra algum erro no envio ao serviço ele seta a flag de flash e para a iteranção do arquivo corrente pra se lançar em outro        
                        break

            except Exception as errorENV:

                error = ("\n=> Erro no setup de pacote: " + str(errorENV))  
                self.addLog("AcessServe.txt", error)                

            finally:
                input_file.close()


            if not(flag_falha):    

                os.remove(self.dir + "/data/" + LoteX)                                      #caso não aja falha ele remove o arquivo e libera armazenamento

            else:

                if str(aux_rename) not in self.OB_Card.contArq():

                    os.rename((self.dir + "/data/" + LoteX), (self.dir + "/data/" + str(aux_rename)))   #Caso tenha ocorrido algum erro ele envia o arquivo para o começo da seguencia da pasta renomenado e incrmentando a partir de zero
                    aux_rename+=1

                else:
                    aux_rename+=1                                   #Caso a numeração do arquivo ainda esteja na refencia de pasta quer dizer que o erro foi nele e desta forma apenas se incrmenta o auxiliar de rename para que caso ocorrora algum erro posterior em outro arquivo ele seja colocado depois e em seguencia do mesmo 

        return aux_rename

"""
    def envia_servico(self, data_json):
        Cria uma instancia do obejto "socket" que funciona como especie de curso ou browser da internet, nele podemos fazer requisiçoes web montando cabeçalho e dados comos se queira.
"""
    def envia_servico(self, data_json, _tentativas = 2, sockTimeout = 2):

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
                 
            except MemoryError as errorMEM:
                error = ("\n=> Não foi possivel alocar memoria para resposta" + str(errorMEM))
                self.addLog("AcessServe.txt",error)   
                pass

            else:
                if "OK" in response.decode():
                    print(response.decode())
                    pass
                else:
                    print("\n=> Sem ERRO no micro, mas ERRO no Seriço HTTP\n")            
                    pass
            finally:    
                self.sock.close()
                return True
        else:
            error = ("\n=> falha na conecção com o serviço")
            self.addLog("AcessServe.txt",error)   
        return False

"""
    Força a coleta do GC

"""
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
     
"""
    def modelosStringJson(self, float_array, temperatura = 0):
        Esta classe recebe e trata os dados referente ao conjunto de dados e o tranforma em uma string json 
"""
    def modelosStringJson(self, float_array, temperatura = 0):

        _id = int(float_array[0])

        data = []
        aux =  0

        # Cria um dicionario com repectivamente  com os dados de acereleção no formato esperado pelo serviço  e em seguida com catena com as demais partes 
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

        #Este ultimo comando pega todo o dicionario criado e o transforma em uma string no fato json

        return json.dumps(quantidade)
    