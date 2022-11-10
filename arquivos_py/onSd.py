import os
import struct
from array import array
from arquivos_py.log import Log

class OnSd(Log):
    
    def __init__(self, dir = "/", _ContArquivosEnvio = 0):
        
        self.dir = dir
        self.ControleDeArquivos = _ContArquivosEnvio
        
        if "contPasta.txt" in os.listdir(self.dir):
            self.contPasta = int(open(self.dir + "/contPasta.txt").read())  
        else:
            self.contPasta = 0

        if "RECIC.txt" in os.listdir(self.dir):
            self.RECIC = int(open(self.dir + "/RECIC.txt").read())    
        else:
            self.RECIC = 0

    def preeencheARQ(self, id_esp = 0, AccX = [], AccY = [], AccZ = [], timers = [], _controleAmostras = 10):        
        
        conjutoFloat = []

        conjutoFloat.append(float(id_esp))

        for timer in timers:
            for i in range(timer.decode().count("_")):
                
                conjutoFloat.append(float(timer[:timer.decode().find("_")]))
                timer = timer[timer.decode().find("_") + 1:]
                
            conjutoFloat.append(float(timer[:timer.decode().find("_")]))    
        
        for i in range(len(AccX)):
            conjutoFloat.append(AccX[i])
            conjutoFloat.append(AccY[i])
            conjutoFloat.append(AccZ[i])
        
        return self.auxSalvaDados(conjutoFloat, _controleAmostras)

    def auxSalvaDados(self, _conjutoFloat = [], controleAmostras = 10):

        
         
        dir_corrente = (self.dir + "/data")
        on_diretorio_cor = self.contArq()
        peso_dir = len(on_diretorio_cor)
        
        print("\n=>self.contPasta = " , self.contPasta)
        print("\n=>peso_dir = " , peso_dir)
        print("\n=> RECIC: ", self.RECIC)
        
        if peso_dir == 0:
            float_array = array('f', _conjutoFloat)
            self.finaliza_transicao((dir_corrente + "/0"), float_array)
            
        else:
            if self.RECIC == 0:
                
                print("\n=> ultimo Diretorio ", on_diretorio_cor[-1])

                input_file = open((dir_corrente +"/"+ str(on_diretorio_cor[-1])), 'a')
                numbytes = input_file.seek(0,2)
                
                if (numbytes/2100) != controleAmostras :

                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    
                    numbytes = input_file.tell()
                    print("\n=> numero de bytes pos insert", input_file.tell())

                else:
                    numbytes = 2100
                    float_array = array('f', _conjutoFloat)
                    self.finaliza_transicao((dir_corrente +"/"+ str(peso_dir)), float_array)

                
                input_file.close()
                
                if (numbytes/2100) == controleAmostras:
                    self.incrimentaContagemArquivo()
                    
                    if self.contPasta >= self.ControleDeArquivos:
                        return True
            else:

                input_file = open((dir_corrente +"/"+ str(self.contPasta)), 'a')
                numbytes = input_file.seek(0,2)
                
                if (numbytes/2100) != controleAmostras :
                    
                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    numbytes = input_file.tell()
                    
                input_file.close()
                    
                if (numbytes/2100) == controleAmostras:
                    self._incrimentaContagemArquivo()
                    
                    if self.contPasta >= self.ControleDeArquivos:
                        return True

        return False
    
    def setRECIC(self):
        f = open((self.dir + "/RECIC.txt"), 'w')
        f.write("1")
        f.close()
        
    def clearRECIC(self):
        f = open((self.dir + "/RECIC.txt"), 'w')
        f.write("0")
        f.close()
        
    def getRECIC(self):
        return int(open(self.dir + "/RECIC.txt").read())    
 
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
                self.addLog("onSD.txt", str(error)) 
                pass
    
    def reiniciaContagemArquivo(self, naPasta = 0):
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(naPasta))
        f.close()
        
        f = open((self.dir + "/data/" + str(naPasta)), 'w')
        f.close()
    
    def incrimentaContagemArquivo(self):
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
            
    def _incrimentaContagemArquivo(self):
        
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
        
        if self.contPasta < self.ControleDeArquivos:
            f = open((self.dir + "/data/" + str(self.contPasta)), 'w')
            f.close()
            
    def setContagemArquivo(self , cont = 0):
        
        self.contPasta = cont
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
        
    def contArq(self):
        on_diretorio_cor = [int(i) for i in os.listdir(self.dir + "/data")]
        on_diretorio_cor.sort()
        return [str(i) for i in on_diretorio_cor]

    
        
        

                
                
                
       
        

