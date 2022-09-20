from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
from arquivos_py.acessWifi import AcessWifi
from arquivos_py.acessServe import AcessServe
from arquivos_py.dateTimeHoras import DateTimeHoras

from machine import Pin
import micropython
import esp32
import machine
import os

#
#
#
########################### PARAMETROS DE USO ###########################
id_esp = 1
dir_padrao = '/'
_sd = "LUCAS E LEOr"
_passw = "785623ptbr"
set_host = '192.168.100.8'
set_porta = 3060
ContArquivosEnvio =  20
ConjuntoArquivosEnvio =  40
minParaEnvio = 10
FlagEnvio = False
########################### PARAMETROS DE USO ###########################
#
#
#
######################## PARAMETROS DE HARDWARE ###########################
deg = Pin(21, Pin.IN)
led = Pin(2, Pin.OUT)
op = DateTimeHoras() 
acorda = machine.Pin(27, mode = Pin.IN)
card_SD = OnSd(dir_padrao, _ContArquivosEnvio = ContArquivosEnvio)                                              
mp_esp = FaceI2C(dir = dir_padrao, gav = True, scale = 0, freqAmostra = 200, SDA_PIN = 25, SCL_PIN = 26)   
######################## PARAMETROS DE HARDWARE ###########################                                       
#
#
#

def startEnvio():
    acessServe = AcessServe(dir_padrao, host = set_host, porta = set_porta)  

    print("\n=>Entrou no envio")                                                                      
    acessServe.enviaPacs()
    print("\n=>Saiu no envio")    

def verificaIntensidadeEnvio():
    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    return pointWifi.isStrengthRSSI()

def setupEnvio():
    print("123456789")
    if verificaIntensidadeEnvio():
        startEnvio()
        card_SD.reiniciaContagemArquivo()
        op.guardTimerIRQ(mp_esp.Calendario()[1])
        return True
    return False

def setupConfig():
    
    while(deg.value() == 0):
        led.value(1)
        machine.lightsleep(2000)
        led.value(0)
        machine.lightsleep(2000)

    led.value(1)
    
    if "data" not in os.listdir(dir_padrao):
        if "contPasta.txt" in os.listdir(dir_padrao):
            os.remove("./contPasta.txt")
        os.mkdir("./data")                                           


    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    pointWifi.do_connect_STA()

    op.guardTimerIRQ(mp_esp.Calendario()[1])
    
    mp_esp.iniciaMP()                                      
    led.value(0)    
    dormindo()

def encapsulaLaco():           
    AccX, AccY, AccZ, timer = mp_esp.pega_valor()   
    _isEstoturo = card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer, ConjuntoArquivosEnvio)
    
    intervalo = op.intervalo(timer[1])
    print("\n=>Intervalo :" , intervalo)
    
    if (intervalo >= minParaEnvio):
        op.guardTimerIRQ(timer[1])
        return _isEstoturo, True
    else:
        return _isEstoturo, False

def dormindo(islight = False):
    esp32.wake_on_ext0(pin = acorda, level = esp32.WAKEUP_ANY_HIGH)
    
    if(islight):
        print("\n=>Dormindo em lightSleep\n")
        machine.lightsleep()
    else:
        print("\n=> Dormindo em DeepSleep\n")
        machine.deepsleep()

if __name__ == '__main__':
   
    led.value(deg.value())
    
    if(deg.value() == 1):
        print("\n=>Debug\n")

    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n')    
            
            isEstouro, FlagEnvio = encapsulaLaco()
            
            print("\n=>Estouro e flag ", isEstouro, FlagEnvio)
            print(os.listdir("./data"))

            if FlagEnvio == True:  
                setupEnvio()
            else:
                if isEstouro == True:
                    print("\n=>Estouro de Arquivo, preciso enviar...")
                    if setupEnvio():
                        card_SD.clearRECIC()
                    else:
                        card_SD.setRECIC()
                        card_SD.reiniciaContagemArquivo()
            dormindo()
        else:
            print("\n=>Power on or hard reset")
            setupConfig()
        
       




