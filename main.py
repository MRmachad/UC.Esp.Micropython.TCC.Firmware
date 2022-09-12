from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
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
id_esp = 1
dir_padrao = '/'
_sd = "LUCAS E LEO"
_passw = "785623ptbr"
set_host = '192.168.100.8'
set_porta = 3060
ContArquivosEnvio =  5
########################### PARAMETROS DE USO ###########################
#
#
#
######################## PARAMETROS DE HARDWARE ###########################
deg = Pin(21, Pin.IN)
led = Pin(2, Pin.OUT)
acorda = machine.Pin(27, mode = Pin.IN)
card_SD = OnSd(dir_padrao, _ContArquivosEnvio = ContArquivosEnvio)                                              
mp_esp = FaceI2C(dir = dir_padrao, gav = True, scale = 0, freqAmostra = 200, SDA_PIN = 25, SCL_PIN = 26)   
######################## PARAMETROS DE HARDWARE ###########################                                       
#
#
#

def startEnvio():
    acessServe = AcessServe(dir_padrao, host = set_host, porta = set_porta)  

    print("\n=> entrou no envio")                                                                      
    acessServe.enviaPacs()
    print("\n=> saiu no envio")    



def verificaIntensidadeEnvio():
    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    return pointWifi.isStrengthRSSI()

def setupEnvio(numArquivoVal = 0):

    if numArquivoVal >= ContArquivosEnvio:
        print("Estouro de Arquivo, preciso enviar...")
        while not verificaIntensidadeEnvio():
            machine.lightsleep(10000)
        startEnvio()
    else:
        if verificaIntensidadeEnvio():
            startEnvio()
            card_SD.reiniciaContagemArquivo()
        else:
            print("\n=> Over RSSI")

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
        os.chdir("./data")
        os.mkdir("./0") 

    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    pointWifi.do_connect_STA()
    
    mp_esp.Calendario()
    
    mp_esp.iniciaMP()                                      
    led.value(0)    
    dormindo()

def encapsulaLaco():           
    AccX, AccY, AccZ, timer = mp_esp.pega_valor()    
    return card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer)

def dormindo(islight = False):
    esp32.wake_on_ext0(pin = acorda, level = esp32.WAKEUP_ANY_HIGH)
    
    if(islight):
        print("\n=> Dormindo em lightSleep\n")
        machine.lightsleep()
    else:
        print("\n=> Dormindo em DeepSleep\n")
        machine.deepsleep()

if __name__ == '__main__':
   
    led.value(deg.value())
    
    if(deg.value() == 1):
        print("\n=> Debug\n")

    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n')    

            if encapsulaLaco() == True:
                
                    print("\n=> Pode tentar enviar? Sim")
                    if card_SD.contPasta >= ContArquivosEnvio:
                        setupEnvio(card_SD.contPasta)
                    dormindo()
            else:
                print("\n=> Pode tentar enviar? Não")
                dormindo()
        else:
            print("\n=> Power on or hard reset")
            setupConfig()
        
       




