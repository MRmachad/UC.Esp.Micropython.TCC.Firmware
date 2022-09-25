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
set_host = '45.166.184.6'
set_porta = 2041
rota = "pink-ws/producao/comportamento"
ContArquivosEnvio =  2
ConjuntoArquivosEnvio =  2
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
    acessServe = AcessServe(dir_padrao, host = set_host, porta = set_porta, _rota = rota)  

    print("\n=> entrou no envio")                                                                      
    acessServe.enviaPacs()
    print("\n=> saiu no envio")    

def verificaIntensidadeEnvio():
    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    return pointWifi.isStrengthRSSI()

def setupEnvio():
    if verificaIntensidadeEnvio():
        startEnvio()
        card_SD.reiniciaContagemArquivo()
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


    pointWifi = AcessWifi(sd = _sd, passw = _passw, tryDefault = True)
    pointWifi.do_connect_STA()
    
    mp_esp.Calendario()
    
    mp_esp.iniciaMP()                                      
    led.value(0)    
    dormindo()

def encapsulaLaco():           
    AccX, AccY, AccZ, timer = mp_esp.pega_valor()    
    return card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer, ConjuntoArquivosEnvio)

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
            
            isEstouro, FlagEnvio = encapsulaLaco()
            
            print("estouro e flag ", isEstouro, FlagEnvio)
            print(os.listdir("./data"))

            if isEstouro == True:
                    print("Estouro de Arquivo, preciso enviar...")
                    if setupEnvio():
                        card_SD.clearRECIC()
                    else:
                        card_SD.setRECIC()
                        card_SD.reiniciaContagemArquivo()
            else:
                if FlagEnvio == True:  
                    setupEnvio()
                
            dormindo()
        else:
            print("\n=> Power on or hard reset")
            setupConfig()
        
       




