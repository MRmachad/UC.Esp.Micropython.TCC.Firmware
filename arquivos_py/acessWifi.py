from arquivos_py.dateTime import DateTime
from machine import RTC
import network
import ntptime

class AcessWifi():
    
    def __init__(self, sd = "LUCAS E LEO", passw = "785623ptbr", tryDefault = False):
        self.sd = sd
        self.tryDefault = tryDefault
        self.passw = passw
    
    def do_connect_STA(self):
        
        wlan = network.WLAN(network.STA_IF)
        rtc = RTC()
        
        if wlan.active() == False:
            wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(self.sd, self.passw)
            while not wlan.isconnected():
                pass
        print('network config:', wlan.ifconfig())
        
        try:
            ntptime.settime()
            
            print(rtc.datetime())
            dt = rtc.datetime()
            cr = self.corrigeHorario((dt[0],dt[1],dt[2],dt[4],dt[5],dt[6]))
            print(dt,cr)
            rtc.datetime((cr[0],cr[1],cr[2],dt[3],cr[3],cr[4],cr[5],dt[7]))

            print("Hora Setada", rtc.datetime())
            
        except OSError as errontp:
            print("\n=> Nao foi possivel sincronizar horario.\n", errontp)
            if self.tryDefault == True:
                rtc.datetime((1967, 1, 1, 1, 0, 0, 0, 0))
                print("Hora Setada", rtc.datetime())
            pass
        
    def isStrengthRSSI(self, parametro = -90):
        
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