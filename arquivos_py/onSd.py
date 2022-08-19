from arquivos_py.acessServe import AcessServe
import json
import os

class OnSd(AcessServe):
    
    def __init__(self, dir = "/", host_p = str('192.168.100.8'), porta_p = 3040):
        super().__init__(host = host_p, porta = porta_p)
        self.dir = dir
        
    def auxSalvaJson(self, timers = [], DataACCdic = {}):
        
        f = open((self.dir + "/data/JSON_"+ str(timers[0]+ "--" + timers[1])+ ".txt"), 'a')
        f.write(json.dumps((DataACCdic)) + ",,")
        f.close()
        
        
    def preeencheARQ(self, id_esp = 0, AccX = [], AccY = [], AccZ = [], timer = [], corte = 5):
        
        DataACC = {("0A_TIMER_INI"): str(timer[0]),("0A_TIMER_FIN"): str(timer[1]), ("0A_ID_ESP"): str(id_esp)}
        
        self.auxSalvaJson(timer, DataACC)
        DataACC = {}
        
        print(timer[0])
        print(timer[1])
        
        i = 0
        
        while i != len(AccX):
            for lote in range(corte):
                
                data = {str(i) + "_AccX": str(AccX[i]), str(i) + "_AccY": str(AccY[i]),  str(i) + "_AccZ" : str(AccZ[i])}
                DataACC.update(data)
                i+=1
                print(i)
                if i >= len(AccX):
                    print("Ultimo envio Quebrado")
                    break
                
            self.auxSalvaJson(timer, DataACC)
            DataACC = {}
            
        
    def contArq(self):
        v_dirs = sorted(os.listdir(self.dir + "/data"))
        print(v_dirs)
        return v_dirs
        
    def enviaPacs(self):
        
        for lt in (self.contArq()):
            DataACC = open(self.dir + "/data/" + lt).read().split(",,")
            
            
            for pac in DataACC:
                if pac != "":
                    #print("\n\n\n dados:" , pac,"###")
                    self.envia_servico(pac)
            
            os.remove(self.dir + "/data/" + lt)
            self.contArq()

            
