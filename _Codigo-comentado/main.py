from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
from arquivos_py.dateTime import DateTime
from arquivos_py.acessWifi import AcessWifi
from arquivos_py.acessServe import AcessServe


from machine import Pin
import micropython
import esp32
import machine
import os

#
#
#
########################### PARAMETROS DE USO ###########################

DIR_PADRAO = "/"
LOGIN =  "LUCAS E LEOr"
SENHA = "785623ptbr"
HOST = '192.168.100.8'
URL = "envio"

ID_VACA = 1
PORTA = 3060
ZONEPOINTHOUR = (2,6,13,18)
QTDARQUIVOS =  21
QTDACONJUNTO =  39

########################### PARAMETROS DE USO ###########################
#
#
#
######################## PARAMETROS DE HARDWARE ###########################
OB_Pino_Debug = Pin(21, Pin.IN)
OB_Pino_Led = Pin(2, Pin.OUT)
OB_Pino_INT = machine.Pin(27, mode = Pin.IN)
OB_Card = OnSd(DIR_PADRAO, _ContArquivosEnvio = QTDARQUIVOS)                                              
OB_Interface_I2C = FaceI2C(dir = DIR_PADRAO, gav = True, scale = 0, freqAmostra = 100, SDA_PIN = 25, SCL_PIN = 26)     
######################## PARAMETROS DE HARDWARE ###########################                                       
#
#
#
######################## PARAMETROS VARIAVEIS ###########################    
FlagEnvio = False
FlagEstouro = False
######################## PARAMETROS VARIAVEIS ###########################                                       
#
#
#

"""
    def SetupEnvio(FlagEstouro, FlagEnvio):
        Reponsavel por tratar os estados das flags. Caso estouro esteja setada como True é feita a tentativa de envio (verificando o RSSI e posteriormente caso sucesso, chamando a rotina de envio de dados ao servico
        enviaPacs)
        Caso o RSSI estea fraco ele seta a recirculação e reinicia a contagem. Caso ele consiga se connectar no wifi e tenha feito a tentativa de envio ao serviço, ele receberar do envia enviaPacs um inteiro que indicara
        o estado de sucesso dessa operação e sera a referencia do armazaenamento em pastas dali em diante.
"""

def SetupEnvio(FlagEstouro, FlagEnvio):

    OB_Interface_WF = AcessWifi(sd = LOGIN, passw = SENHA)

    if FlagEstouro == True:

        print("\n=>Estouro de Arquivo, preciso enviar...")

        if OB_Interface_WF.isStrengthRSSI():
            acessServe = AcessServe(DIR_PADRAO, host = HOST, porta = PORTA,  _rota = URL)                                                              
            point_pasta = acessServe.enviaPacs()

            if point_pasta != QTDARQUIVOS:
                print("envio incompleto ou completo", point_pasta)
                OB_Card.clearRECIC()
                OB_Card.reiniciaContagemArquivo(point_pasta)
            else:
                print("Não conseguiu enviar nenhum dos arquivos, como estou em estouro vou recircular")
                OB_Card.setRECIC()
                OB_Card.reiniciaContagemArquivo()
                
        
        else:
            print("RSSI fraco, como estou em estouro irei recicular")
            OB_Card.setRECIC()
            OB_Card.reiniciaContagemArquivo()
    else:

        # Caso a flag de envio esteja acionada é feita uma unica tentativa de envio verificando tanto as condições de acesso ao wifi quanto ao sucesso da operção de envio

        if FlagEnvio == True:  

            if OB_Interface_WF.isStrengthRSSI():
                acessServe = AcessServe(DIR_PADRAO, host = HOST, porta = PORTA,  _rota = URL)                                                              
                point_pasta = acessServe.enviaPacs()

                if point_pasta != QTDARQUIVOS:
                    print("envio incompleto ou completo", point_pasta)
                    OB_Card.clearRECIC()
                    OB_Card.reiniciaContagemArquivo(point_pasta)
                else:
                    print("Não conseguiu enviar nenhum dos arquivos, como estou em estouro vou recircular")
                    OB_Card.setRECIC()
                    OB_Card.reiniciaContagemArquivo()

"""
    def SetupConfig():
        Responsavel por fazer as configurações iniciais  ele verifica se o arquivo de data ja em esta em disco. Caso seja verdadeiro, se faz a entender que o sistema ja foi executado pois exite dados em disco
        neste caso ira apenas continuar o povoamento dos dados.
        No caso em que não tenha nada ele crias as pastas padrão do sistema para que elas possam ser escritas posteriormente e faz as devidas chegcagem de connectividade e sincronização

"""

def SetupConfig():
    
    OB_Interface_WF = AcessWifi(sd = LOGIN, passw = SENHA, tryDefault = True)
    
    if "data" not in os.listdir(DIR_PADRAO):
        os.mkdir("./data") 

        if "contPasta.txt" in os.listdir(DIR_PADRAO):
            os.remove("./contPasta.txt")

        if "Logclass" not in os.listdir(DIR_PADRAO):                                       
            os.mkdir("./Logclass")

        print("\n=>Setup Inicial")
        
        OB_Pino_Led.value(1)
        machine.lightsleep(2000)

        OB_Interface_WF.do_connect_STA()

    else:
        
        print("\n=>Continuando amostragem")
        
        if OB_Interface_WF.isStrengthRSSI():
            pass
        else:
            OB_DateTime = DateTime()
            OB_DateTime.RecuperaHorarioCorrente()
            
        OB_Pino_Led.value(1)
        machine.lightsleep(2000)

    OB_Interface_I2C.Calendario()
    
    OB_Interface_I2C.iniciaMP()   

    OB_Pino_Led.value(0)    

    dormindo()

"""
Pega os dados atrav3es da interface I2C e guarda esses dados devidamente em disco(Que pode retorna falg de estouro de arquivo) e tabem retorna com a função 'isInMancha' a flag de envio por zona de tempo
"""

def EncapsulaLaco():           

    AccX, AccY, AccZ, timer = OB_Interface_I2C.pega_valor()   

    return OB_Card.preeencheARQ(ID_VACA, AccX, AccY, AccZ, timer, QTDACONJUNTO), (isInMancha(timer[1], ZONEPOINTHOUR) and OB_Card.contPasta >= 1)


"""

    def isInMancha(_timer = "", _zonePointHour = []):
        Recebe a zona de tempo (uma tupla contendo as horas do dia em que se deseja enviar) e a referencia de tempo atual mais atualizada
        Alem de guarda a referencia de dado mais aatual em disco ele verifica se se esta referencia esta na zona de hora de envio com uma abertura de 1hora a frente e atras

"""

def isInMancha(_timer = "", _zonePointHour = []):

    OB_DateTime = DateTime()

    dt=[]
    for i in range(_timer.decode().count("_")):
    
        dt.append(int(_timer[:_timer.decode().find("_")]))
        _timer = _timer[_timer.decode().find("_") + 1:]

    dt.append(int(_timer.decode()))    
    
    ###
    OB_DateTime.GuardaHorarioCorrente(dt)
    ###
    
    print("\n=>Hora atual: ", dt[3])

    for pointHour in _zonePointHour:

        if dt[3] in (OB_DateTime.sub(pointHour, 1), pointHour, OB_DateTime.summ(pointHour, 1)):
            return True
    return False

"""
    def dormindo():
        Seta o pino de interrupção do deepsleep (qual receberar o acionamentos do mp6050 quando houver estou do buffer do mesmo).
        Entra em estado de deep sleep
"""

def dormindo():

    esp32.wake_on_ext0(pin = OB_Pino_INT, level = esp32.WAKEUP_ANY_HIGH)

    print("\n=> Dormindo em DeepSleep\n")

    machine.deepsleep()


"""

if __name__ == '__main__':
    De forma geral o funcionamento perpetuo de execução e da seguinte maneira:
        .Verifica-se o acionamento do pino de debug (colocado em harware para encerrar a execução do programa)
        .Verifica a causa de 'acordamento do dispositivo controlador'.
            Caso seja por Deeepsleep, que dizer que o espe esperou todo um conjunto de amostra ser bufferizada no mp6050 e agora esta disponivel para ser capturados os dados do mesmo
            Caso acorde por 'Hard Reset', o sistema ou esta ligando pela primeira vez ou esta religando por algum motivo

"""

if __name__ == '__main__':
   
    OB_Pino_Led.value(OB_Pino_Debug.value())    #Led a indicar a parada por pino de debug
    
    if(OB_Pino_Debug.value() == 1):
        print("\n=>Debug\n")

    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n')    
            
            #Captura os dados do MP6050 , os insere em disco e retorna as flags de sistema 

            FlagEstouro, FlagEnvio = EncapsulaLaco()
            
            print("\n=>Estouro e flag ", FlagEstouro, FlagEnvio)
            print(OB_Card.contArq())

            #Aqui são tradatadas os estados de flag e tomada as devidas decisões

            SetupEnvio(FlagEstouro, FlagEnvio)

            #Retorna ao estado de deep sleep
            dormindo()

        else:

            print("\n=>Power on or hard reset")

            #Tratamento e configuração inicial do esp e mp6050 (EXECUTADO A PRIORI UMA UNICA VEZ CASO O SISTEMA NÃO SEJA RELIGADO)

            SetupConfig()
        
       




