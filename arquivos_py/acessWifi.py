import network
import ntptime

class AcessWifi():
    
    def __init__(self, sd = "LUCAS E LEO", passw = "785623ptbr"):
        self.sd = sd
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
        
        try:
            ntptime.settime()
        except OSError as errontp:
            print("\n=> Nao foi possivel sincronizar horario.\n", errontp)
            pass
        
    def isStrengthRSSI(self, parametro = -90):
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
  
        VecTupRedes =  wlan.scan()
        rssi = 0
        for tup in VecTupRedes:
            if tup[0].decode() == self.sd:
                rssi = tup[3]
                print("\n=> RSSI: ", rssi)
                if  rssi > parametro:
                    self.do_connect_STA()
                    return True
        
        wlan.active(False)
        return False
