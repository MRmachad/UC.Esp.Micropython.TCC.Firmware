from arquivos_py.onSd import OnSd
from arquivos_py.faceI2C import FaceI2C
from arquivos_py.acessWifi import AcessWifi


from machine import Pin,RTC
import esp32
import machine
import os

id_esp = 1
rtc = machine.RTC()
acorda = machine.Pin(27, mode = Pin.IN)
deg =  Pin(21, Pin.IN)
led =  Pin(2, Pin.OUT)

def dormindo():
    esp32.wake_on_ext0(pin = acorda, level = esp32.WAKEUP_ANY_HIGH)
    print("Dormindo")
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
            
    
if __name__ == '__main__':
   
    print("\n=> Valor do pino de debug: ", deg.value())
    led.value(deg.value())
    
    mp_esp = FaceI2C(dir = "/", gav = False, scale = 0, freqAmostra = 200)                                                 # mudar para /sd quando montar o filesystem  
    
    if(deg.value() == 1):
        print("debug")
    else:

        if machine.reset_cause() == machine.DEEPSLEEP_RESET:
            print('\n \n woke from a deep sleep \n \n') 
            
            card_SD = OnSd("/", porta_p = 3050)                                   # mudar para /sd quando montar o filesystem                                  
           
            AccX, AccY, AccZ, timer = mp_esp.pega_valor()
            print(len(AccX))
            print(len(AccY))
            print(len(AccZ))
            
            guar_flash(AccX, AccY, AccZ)
            
            
            
            card_SD.preeencheARQ(id_esp, AccX, AccY, AccZ, timer, corte = 85)
            
            print("\n \n quantidade de arquivos gravados \n \n")
            print(len(card_SD.contArq()))
            
            pointWifi = AcessWifi()
            pointWifi.do_connect_STA()
            card_SD.enviaPacs()
            
            dormindo()
            
        else:
            print('power on or hard reset')
            

            #sd = machine.SDCard(slot=2, sck=1, miso=3, mosi=22, cs=23)
            #os.mount(sd, "/sd/data")                                        # mount  Slot 2 uses pins sck=18, cs=5, miso=19, mosi=23 (M PG 96)
            
            if "data" not in os.listdir('/'):
                os.mkdir('./data')                                           # condicionar a criação a somente se não tiver 
            
            pointWifi = AcessWifi()
            pointWifi.do_connect_STA()
            
            mp_esp.Calendario()
            
            mp_esp.MPU6050SelfTest()        
            mp_esp.iniciaMP()                                      # setar timer pra zero aqui e mudar só em pega valor()
            dormindo()
        
       
