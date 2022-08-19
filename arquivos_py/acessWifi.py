import network
import ntptime

class AcessWifi():
    
    def __init__(self, sd = "LUCAS E LEO", passw = "785623ptbr"):
        self.sd = sd
        self.passw = passw
    
    def do_connect_STA(self):
        
        wlan = network.WLAN(network.STA_IF)
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
            #print(errontp)
            pass
        
    def rssi_strength(self):
        
        is_rssi = network.AbstractNIC()
        
        if is_rssi(is_rssi.scan(ssid = self.sd)) > 0:
            #print("Pode enviar")
            pass
        else:
            #print("verificar na proxima enviar")
            pass