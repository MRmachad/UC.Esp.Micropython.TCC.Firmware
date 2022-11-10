from arquivos_py.dateTime import DateTime
from arquivos_py.log import Log
from machine import RTC
import network
import ntptime

class AcessWifi(Log):
    
    def __init__(self, sd = "LUCAS E LEO", passw = "785623ptbr", tryDefault = False):
        self.sd = sd
        self.tryDefault = tryDefault
        self.passw = passw
    
    def do_connect_STA(self):
        
        wlan = network.WLAN(network.STA_IF)
        
        
        if wlan.active() == False:
            wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(self.sd, self.passw)
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())
        
        if  self.tryDefault == True:
            
            error = ""
            
            while True:
                try:
                    self.sincronizaHorario()
                    break
                except OSError as errontp:
                        
                    error = ("\n=> Nao foi possivel sincronizar horario.\n" + str(errontp))         
                    pass
                
            if error != "": 
                self.addLog("AcessWifi.txt",error)  

        else:
            
            try:
                self.sincronizaHorario()
            except OSError as errontp:

                error = ("\n=> Nao foi possivel sincronizar horario.\n" + str(errontp))
                self.addLog("AcessWifi.txt",error)
                
                pass
    
    def sincronizaHorario(self):
        ntptime.settime()
        rtc = RTC()

        dt = rtc.datetime()
        cr = self.corrigeHorario((dt[0],dt[1],dt[2],dt[4],dt[5],dt[6]))

        rtc.datetime((cr[0],cr[1],cr[2],dt[3],cr[3],cr[4],cr[5],dt[7]))

        print("\n=>Hora Setada", rtc.datetime())

    def isStrengthRSSI(self, parametro = -95):

        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
  
        VecTupRedes =  wlan.scan()
        rssi = 0
        for tup in VecTupRedes:
            if tup[0].decode() == self.sd:
                rssi = tup[3]
                print("\n=> RSSI de wifi: ", rssi)
                if  rssi > parametro:
                    self.do_connect_STA()
                    return True
        
        wlan.active(False)
        return False
        
    def corrigeHorario(self, dt = []):

        dateTime = DateTime()

        dt = dateTime.subtracao([0,0,0,3,0,0],dt)
            
        return (dt[0],dt[1],dt[2],dt[3],dt[4],dt[5])


