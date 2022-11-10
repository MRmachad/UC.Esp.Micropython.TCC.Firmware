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
LOGIN =  "LUCAS E LEO"
SENHA = "785623ptbr"
HOST = '45.166.184.6'
URL = "comportamento"

ID_VACA = 16
PORTA = 2037
ZONEPOINTHOUR = (2,6,16,22)
QTDARQUIVOS = 21
QTDACONJUNTO = 39

########################### PARAMETROS DE USO ###########################
#
#
#
######################## PARAMETROS DE HARDWARE ###########################
OB_Pino_Debug = Pin(25, Pin.IN)
OB_Pino_Led = Pin(14, Pin.OUT)
OB_Pino_INT = machine.Pin(13, mode = Pin.IN)
OB_Card = OnSd(DIR_PADRAO, _ContArquivosEnvio = QTDARQUIVOS)                                              
OB_Interface_I2C = FaceI2C(dir = DIR_PADRAO, gav = True, scale = 0, freqAmostra = 100, SDA_PIN = 21, SCL_PIN = 22)     
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

def SetupEnvio(FlagEstouro, FlagEnvio):

    OB_Interface_WF = AcessWifi(sd = LOGIN, passw = SENHA)

    if FlagEstouro == True:

        print("\n=>Estouro de Arquivo, preciso enviar...")

        if OB_Interface_WF.isStrengthRSSI():
            acessServe = AcessServe(DIR_PADRAO, host = HOST, porta = PORTA,  _rota = URL, ConjAmostra = QTDACONJUNTO)                                                              
            point_pasta, Reinicia = acessServe.enviaPacs()
            
            print("POINT PASTA",point_pasta)
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

        if FlagEnvio == True:  

            if OB_Interface_WF.isStrengthRSSI():
                acessServe = AcessServe(DIR_PADRAO, host = HOST, porta = PORTA,  _rota = URL, ConjAmostra = QTDACONJUNTO)                                                              
                point_pasta, Reinicia = acessServe.enviaPacs()

                if point_pasta != QTDARQUIVOS:
                    print("envio incompleto ou completo", point_pasta)
                    print(OB_Card.contArq())
                    OB_Card.clearRECIC()
                    if Reinicia == True:
                        OB_Card.reiniciaContagemArquivo(point_pasta)


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

def EncapsulaLaco():           

    AccX, AccY, AccZ, timer = OB_Interface_I2C.pega_valor()   

    return OB_Card.preeencheARQ(ID_VACA, AccX, AccY, AccZ, timer, QTDACONJUNTO), (isInMancha(timer[1], ZONEPOINTHOUR) and OB_Card.contPasta >= 2)

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

        if dt[3] in (OB_DateTime.sub(pointHour, 1), pointHour):
            return True
    return False

def dormindo():

    esp32.wake_on_ext0(pin = OB_Pino_INT, level = esp32.WAKEUP_ANY_HIGH)

    print("\n=> Dormindo em DeepSleep\n")

    machine.deepsleep()

if __name__ == '__main__':
    OB_Pino_Led.value(0)
    OB_Pino_Led.value(OB_Pino_Debug.value())
    
    if(OB_Pino_Debug.value() == 1):
        print("\n=>Debug\n")

    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n')    
            
            FlagEstouro, FlagEnvio = EncapsulaLaco()
            
            print("\n=>Estouro e flag ", FlagEstouro, FlagEnvio)
            print(OB_Card.contArq())

            SetupEnvio(FlagEstouro, FlagEnvio)

            dormindo()

        else:

            print("\n=>Power on or hard reset")
            SetupConfig()
        
       




