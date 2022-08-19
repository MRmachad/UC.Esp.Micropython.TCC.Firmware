from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
from arquivos_py.acessWifi import AcessWifi


from machine import Pin,RTC
import micropython
import _thread
import esp32
import machine
import os
import gc


acorda = machine.Pin(27, mode = Pin.IN)
deg =  Pin(21, Pin.IN)
led =  Pin(2, Pin.OUT)
lock = _thread.allocate_lock()

id_esp = 1
rtc = machine.RTC()
ContArquivosEnvio = 11


def dormindo(islight = False):
    esp32.wake_on_ext0(pin = acorda, level = esp32.WAKEUP_ANY_HIGH)
    
    if(islight):
        print("\n=> Dormindo em lightSleep\n")
        machine.lightsleep()
    else:
        print("\n=> Dormindo em DeepSleep\n")
        machine.deepsleep()
        

def guar_flash(AccX = [0], AccY = [0], AccZ = [0]):
    
    if "Csvs" not in os.listdir('/'):
        os.mkdir('./Csvs')
    
    guard_ACCX = open(("Csvs/ACCX"+".csv"), 'a')
    guard_ACCY = open(("Csvs/ACCY"+".csv"), 'a')
    guard_ACCZ = open(("Csvs/ACCZ"+".csv"), 'a')

    for i in range(len(AccX)):
        
        guard_ACCX.write(str(AccX[i]).replace(".",",") + "\n")
        guard_ACCY.write(str(AccY[i]).replace(".",",") + "\n")
        guard_ACCZ.write(str(AccZ[i]).replace(".",",") + "\n")
    
    guard_ACCX.close()
    guard_ACCY.close()
    guard_ACCZ.close()
    
def encapsulaLaco(mp_esp, card_SD):
    lock.acquire()
    
    AccX, AccY, AccZ, timer = mp_esp.pega_valor()
            
    #guar_flash(AccX, AccY, AccZ)
    
    card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer, corte = 85)
    
    lock.release()
    
def esvazia_memoria():
    gc.collect()
    micropython.mem_info()
    print('\n-----------------------------')
    print('Initial free: {} allocated: {}\n'.format(gc.mem_free(), gc.mem_alloc()))
    
    
    
if __name__ == '__main__':
   
    print("\n=> Valor do pino de debug: ", deg.value())
    led.value(deg.value())
    
    mp_esp = FaceI2C(dir = "/", gav = False, scale = 0, freqAmostra = 200)                                                 # mudar para /sd quando montar o filesystem  
    
    if(deg.value() == 1):
        print("\n=> Debug\n")
    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n=> Woke from a deep sleep \n') 
            
            card_SD = OnSd("/", _ContArquivosEnvio = ContArquivosEnvio)                                                 #mudar para /sd quando montar o filesystem                                  
           
            encapsulaLaco(mp_esp, card_SD)
            
            N_arqui_val = card_SD.contPasta
            print("\n=> Quantidade de arquivos validos gravados em \data\JSONx: ")
            print(N_arqui_val)
            
            if N_arqui_val >= ContArquivosEnvio: ####
                
                card_SD_envio = OnSd("/", porta_p = 3060)                                   # mudar para /sd quando montar o filesystem      
                pointWifi = AcessWifi()
                pointWifi.do_connect_STA()
                
                card_SD_envio.enviaPacs()
                #_thread.start_new_thread(card_SD_envio.enviaPacs, ())
                
                #machine.lightsleep(2000)
                #while(not(card_SD.reconheceTermino())):
                #    led.value(0)
                #    dormindo(True)  
                #    led.value(1)
                #    esvazia_memoria()
                #    encapsulaLaco(mp_esp, card_SD)
                     
                dormindo()
            else:
                dormindo()
            
        else:
            print("\n=> Power on or hard reset")
            
            print("\n=> Valor do pino de debug: ", deg.value())
            led.value(deg.value())
            
            while(deg.value() == 0):
                led.value(1)
                machine.lightsleep(1000)
                led.value(0)
                machine.lightsleep(1000)

            #sd = machine.SDCard(slot=2, sck=1, miso=3, mosi=22, cs=23)
            #os.mount(sd, "/sd/data")                                        # mount  Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23 (M PG 96)
            
            if "data" not in os.listdir('/'):
                if "contPasta.txt" in os.listdir('/'):
                    os.remove("./contPasta.txt")
                os.mkdir("./data")                                           # condicionar a criação a somente se não tiver 
                os.chdir("./data")
                os.mkdir("./JSON0") 

            pointWifi = AcessWifi()
            pointWifi.do_connect_STA()
            
            mp_esp.Calendario()
            
            mp_esp.MPU6050SelfTest()        
            mp_esp.iniciaMP()                                      # setar timer pra zero aqui e mudar só em pega valor()
            dormindo()
        
       


