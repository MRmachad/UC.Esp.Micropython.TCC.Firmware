from arquivos_py.dateTime import DateTime
from arquivos_py.log import Log
from machine import RTC
import network
import ntptime


"""
Os modulos de micro python aqui usado nos possibilitam cria uma conecção Wifi (network) e sincronizar atraves do acesso a internet WIFI data e hora (ntptime).
"""

class AcessWifi(Log):
    
    def __init__(self, sd = "LUCAS E LEO", passw = "785623ptbr", tryDefault = False):
        self.sd = sd
        self.tryDefault = tryDefault
        self.passw = passw
    
"""
    def do_connect_STA(self):  
        Cria um propriamente o objeto network, ativa o hardware referente ao wifi e tenta conectar ao wifi caso ainda não esteja conectado.
        Para caso seja este metodo seja executado em setup, o objeto AcessWifi deve ser criado com o parametro tryDefault = True, o que forçara 
        tanto a espera do esp com o wifi quanto a sincronização do horario via ntp, caso não ele so faz uma tentativa para este ultimo pois ele já foi sincronizado outrora
"""
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

"""
    def isStrengthRSSI(parametro = -60): 
        verifica a intensidade do sinal wifi atraves da escala de rssi, e retorna o valor de boleano da operação de verificaçao se ele é maior que o parametro
"""

    def isStrengthRSSI(self, parametro = -60):
        
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

"""
    def corrigeHorario(self, dt = []): 
        Corrige a data horario (dt) para o horario brasileiro(o ntp sincroniza com horario americano)
"""
    def corrigeHorario(self, dt = []):

        dateTime = DateTime()

        dt = dateTime.subtracao([0,0,0,3,0,0],dt)
            
        return (dt[0],dt[1],dt[2],dt[3],dt[4],dt[5])

