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

dir_padrao = "/"
_sd = "LUCAS E LEOr"
_passw = "785623ptbr"
set_host = '45.166.184.6'
rota = "pink-ws/producao/comportamento"

id_esp = 1
set_porta = 2041
_zonePointHour = (0,7,12,18,22)
ContArquivosEnvio =  2
ConjuntoArquivosEnvio =  2

FlagEnvio = False

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
    acessServe = AcessServe(dir_padrao, host = set_host, porta = set_porta,  _rota = rota)  

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
    _isEstoturo = card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer, ConjuntoArquivosEnvio)
    
    if (isInMancha(timer[1], _zonePointHour) and card_SD.contPasta >= 1):
        return _isEstoturo, True
    else:
        return _isEstoturo, False

def isInMancha(timer = "", zonePointHour = []):

    dt=[]
    for i in range(timer.decode().count("_")):
            
        dt.append(int(timer[:timer.decode().find("_")]))
        timer = timer[timer.decode().find("_") + 1:]
    dt.append(int(timer.decode()))    

    print("Hora: ", dt[3])
    for pointHour in zonePointHour:

        if dt[3] in (sub(pointHour, 1), pointHour, summ(pointHour, 1)):
            return True
    return False

def summ(hour = 0, add = 0):
    tempo = hour + add
    if tempo >= 24:
        tempo -= 24
    print(tempo)
    return tempo

def sub(hour = 0, menus = 0):
    tempo = hour - menus
    if tempo < 0:
        tempo += 24
    print(tempo)
    return tempo

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

            if isEstouro == True:
                    print("\n=>Estouro de Arquivo, preciso enviar...")
                    if setupEnvio():
                        card_SD.clearRECIC()
                    else:
                        card_SD.setRECIC()
                        card_SD.reiniciaContagemArquivo()
            else:
                if FlagEnvio == True:  
                    print(setupEnvio())

            dormindo()
        else:
            print("\n=>Power on or hard reset")
            setupConfig()
        
       




