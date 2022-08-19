from arquivos_py.acessServe import AcessServe
import micropython
import _thread
import json
import os
import gc


lock = _thread.allocate_lock()


class OnSd(AcessServe):
    
    def __init__(self, dir = "/", host_p = str('192.168.100.8'), porta_p = 3040, _ContArquivosEnvio = 0):
        super().__init__(host = host_p, porta = porta_p)
        
        self.dir = dir
        self.ControleDeArquivos = _ContArquivosEnvio
        
        if "contPasta.txt" in os.listdir(self.dir):
            self.contPasta = int(open(self.dir + "/contPasta.txt").read())    
        else:
            self.contPasta = 0
            
        #print("\n=> Valor de contPasta", self.contPasta, "\n")
            
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
        print('\n-----------------------------')
        print('Initial free: {} allocated: {}\n'.format(gc.mem_free(), gc.mem_alloc()))
    
    def auxSalvaJson(self, timers = [], DataACCdic = {}):
        
        f = open((self.dir + "/data/JSON"+str(self.contPasta) +"/"+ str(timers[0]+ "--" + timers[1])+ ".txt"), 'a')
        f.write(json.dumps((DataACCdic)) + ",,")
        f.close()
        
    def AumentaContPasta(self):
        
        if  len(os.listdir(self.dir + "/data/JSON"+str(self.contPasta))) == 10: ########
            if (self.contPasta+1) == self.ControleDeArquivos:
                
                f = open((self.dir + "/contPasta.txt"), 'w')
                f.write(str(0))
                f.close()
                
                self.contPasta+=1
                
            else:
                f = open((self.dir + "/contPasta.txt"), 'w')
                f.write(str(self.contPasta + 1))
                f.close()
                
                self.contPasta+=1
                
                if ("JSON" + str(self.contPasta)) not in os.listdir(self.dir + "/data"):
                    os.chdir("./data")
                    os.mkdir("./JSON" + str(self.contPasta))
    
    def contArq(self):
        
        v_dirs = sorted(os.listdir(self.dir + "/data"))
        #print(v_dirs)
        return v_dirs
    
    def reconheceTermino(self):
        
        if "threadOK_.txt" in os.listdir(self.dir):
            os.remove(self.dir + "/threadOK_.txt")
            #print("\n=> Thread Finalizada\n")
            return True
        else:
            #print("\n=> Thread Ainda não Finalizada\n")
            return False
        
    def enviaTermino(self):
        f = open((self.dir + "/threadOK_.txt"), 'a')
        f.write("OK")
        f.close()
            
    def preeencheARQ(self, id_esp = 0, AccX = [], AccY = [], AccZ = [], timer = [], corte = 5):        
        
        DataACC = {("0A_TIMER_INI"): str(timer[0]),("0A_TIMER_FIN"): str(timer[1]), ("0A_ID_ESP"): str(id_esp)}
        
        self.auxSalvaJson(timer, DataACC)
        DataACC = {}
        
        i = 0
        
        while i != len(AccX):
            for lote in range(corte):
                
                data = {str(i) + "_AccX": str(AccX[i]), str(i) + "_AccY": str(AccY[i]),  str(i) + "_AccZ" : str(AccZ[i])}
                DataACC.update(data)
                i+=1
                #print(i)
                if i >= len(AccX):
                    #print("\n=> Ultimo envio Quebrado\n")
                    break
                
            self.auxSalvaJson(timer, DataACC)
            DataACC = {}
        
        self.AumentaContPasta()
        
    def enviaPacs(self):
        
        v_dirs_envio = self.contArq()
        print(v_dirs_envio)

        
        for JOSNx in v_dirs_envio:
            
            realJSON = sorted(os.listdir(self.dir + "/data/" + JOSNx))
            #print("\n=> Quantidade de aruivos dentro do json corrente: ", len(realJSON))
            
            for lt in (realJSON):
                
                self.esvazia_memoria()
                lock.acquire()
                DataACC = open(self.dir + "/data/"+ str(JOSNx) + "/" + lt).read().split(",,")
                
                for pac in DataACC:
                    if pac != "":
                        #print("\n\n\n dados:" , pac,"###")
                        self.envia_servico(pac)
                        
                os.remove(self.dir + "/data/" + str(JOSNx) + "/"  + lt)
                lock.release()
            #os.remove(self.dir + "/data/" + str(JOSNx))
                
        self.enviaTermino()
        
