import os
import struct
from array import array

class OnSd():
    
    def __init__(self, dir = "/", _ContArquivosEnvio = 0):
        
        self.dir = dir
        self.ControleDeArquivos = _ContArquivosEnvio
        
        if "contPasta.txt" in os.listdir(self.dir):
            self.contPasta = int(open(self.dir + "/contPasta.txt").read())    
        else:
            self.contPasta = 0
            

    
    
    def finaliza_transicao(self, dirNameDateDataId = "", float_array = []):
        while True:
                try:
                    output_file = open(dirNameDateDataId, "w+b")
                    try:
                        output_file.write(bytes(float_array))
                    finally:
                         output_file.close()
                    break
                except Exception as error:
                    print("\n=> ", error)
                    pass
            
        
    def AumentaContPasta(self):
        
        NaPasta = os.listdir(self.dir + "/data/"+str(self.contPasta))
        
        if  len(NaPasta) >= 2: ########
            if len(NaPasta[-1]) > 60:
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
                    
                    if (str(self.contPasta)) not in os.listdir(self.dir + "/data"):
                        os.chdir("./data")
                        os.mkdir("./" + str(self.contPasta))
    
    def contArq(self):
        return sorted(os.listdir(self.dir + "/data"))
    
    
    def auxSalvaDados(self, nameDateDataId = "", floatlist = []):
        
        dir_corrente = (self.dir + "/data/"+str(self.contPasta))
        on_diretorio_cor = os.listdir(dir_corrente)
        peso_dir = len(on_diretorio_cor)
        
        if peso_dir == 0:

            float_array = array('f', floatlist)
            self.finaliza_transicao((dir_corrente +"/0_"+ nameDateDataId), float_array)
            
        else:
            if len(on_diretorio_cor[-1]) <= len("0_"+ nameDateDataId) + 5 :

                input_file = open((dir_corrente +"/"+ on_diretorio_cor[-1]), 'r+b')

                float_array_odd = array('f', struct.unpack((170*3*'f'), input_file.read()))
                
                float_array = array('f', floatlist)
                
                self.finaliza_transicao((dir_corrente +"/"+ on_diretorio_cor[-1] + "C" + nameDateDataId ), float_array + float_array_odd)
                
                os.remove((dir_corrente +"/"+ on_diretorio_cor[-1]))
            
            else:
                float_array = array('f', floatlist)
                self.finaliza_transicao((dir_corrente +"/"+ str(peso_dir) + "_" + nameDateDataId), float_array)

 
    def preeencheARQ(self, id_esp = 0, AccX = [], AccY = [], AccZ = [], timer = []):        
        
        
        nameDateDataId =(timer[0].decode("utf-8").replace(":","_").replace("-","_") + "A" +
                         timer[1].decode("utf-8").replace(":","_").replace("-","_")+ "B" + str(id_esp))
        
        floatlist = []
        
        for Nacc in range(len(AccX)):
            floatlist.append(AccX[Nacc])
            floatlist.append(AccY[Nacc])
            floatlist.append(AccZ[Nacc])
        
        self.auxSalvaDados(nameDateDataId, floatlist)
        
        self.AumentaContPasta()
        
 
        
        

                
                
                
       
        

