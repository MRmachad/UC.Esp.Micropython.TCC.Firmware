from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
from arquivos_py.acessWifi import AcessWifi


from machine import Pin,RTC
import micropython
import esp32
import machine
import os



id_esp = 1
dir_padrao = '/'
_sd = "LUCAS E LEO"
_passw = "785623ptbr"
set_host = '192.168.100.8'
set_porta = 3060

rtc = machine.RTC()
deg = Pin(21, Pin.IN)
led = Pin(2, Pin.OUT)
ContArquivosEnvio =  27
acorda = machine.Pin(27, mode = Pin.IN)
mp_esp = FaceI2C(dir = dir_padrao, gav = True, scale = 0, freqAmostra = 200, SDA_PIN = 25, SCL_PIN = 26)                                                 # mudar para /sd quando montar o filesystem  
card_SD = OnSd(dir_padrao, _ContArquivosEnvio = ContArquivosEnvio, host_p = set_host, porta_p = set_porta)                                                            # mudar para /sd quando montar o filesystem 
card_SD_envio = OnSd(dir_padrao, host_p = set_host, porta_p = set_porta)                                                                              # mudar para /sd quando montar o filesystem  


def dormindo(islight = False):
    esp32.wake_on_ext0(pin = acorda, level = esp32.WAKEUP_ANY_HIGH)
    
    if(islight):
        print("\n=> Dormindo em lightSleep\n")
        machine.lightsleep()
    else:
        print("\n=> Dormindo em DeepSleep\n")
        machine.deepsleep()
        
    
def encapsulaLaco():        
    
    AccX, AccY, AccZ, timer = mp_esp.pega_valor()
            
    card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer)
    
    return card_SD.contPasta

def setupEnvio():
    
    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    pointWifi.do_connect_STA()
    
    card_SD_envio.enviaPacs()
         
    dormindo()

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
        os.mkdir("./data")                                           # condicionar a criação a somente se não tiver 
        os.chdir("./data")
        os.mkdir("./0") 

    pointWifi = AcessWifi(sd = _sd, passw = _passw)
    pointWifi.do_connect_STA()
    
    mp_esp.Calendario()
    
    mp_esp.iniciaMP()                                      # setar timer pra zero aqui e mudar só em pega valor()
    led.value(0)    
    dormindo()

if __name__ == '__main__':
   
    led.value(deg.value())
    
    if(deg.value() == 1):
        print("\n=> Debug\n")
    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n') 
                 
            N_arqui_val = encapsulaLaco()
            print("\n=> Quantidade de arquivos validos gravados em \data\JSONx: ", N_arqui_val)
            
            if N_arqui_val >= ContArquivosEnvio: 
          
                setupEnvio()
            else:
                dormindo()
            
        else:
            print("\n=> Power on or hard reset")
            
            setupConfig()
        
       




