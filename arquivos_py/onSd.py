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
        print(conjutoFloat)
        
        for i in range(len(AccX)):
            conjutoFloat.append(AccX[i])
            conjutoFloat.append(AccY[i])
            conjutoFloat.append(AccZ[i])
        
        return self.auxSalvaDados(conjutoFloat, _controleAmostras)

    def auxSalvaDados(self, _conjutoFloat = [], controleAmostras = 10):
        
        dir_corrente = (self.dir + "/data")
        on_diretorio_cor = os.listdir(dir_corrente)
        peso_dir = len(on_diretorio_cor)
        
        print("\n=>self.contPasta = " , self.contPasta)
        print("\n=>peso_dir = " , peso_dir)
        print("\n=> RECIC: ", self.RECIC)
        
        if peso_dir == 0:
            float_array = array('f', _conjutoFloat)
            self.finaliza_transicao((dir_corrente + "/0"), float_array)
            
        else:
            if self.RECIC == 0:

                input_file = open((dir_corrente +"/"+ on_diretorio_cor[-1]), 'a')
                numbytes = input_file.seek(0,2)
                
                if (numbytes/2100) != controleAmostras :
                    print("\n=> Numero de bytes: ", numbytes)

                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    
                    numbytes = input_file.tell()
                    print("\n=> numero de bytes pos insert", input_file.tell())

                    input_file.close()

                else:
                    numbytes = 2100
                    print("\n=> arquivo novo")
                    float_array = array('f', _conjutoFloat)
                    self.finaliza_transicao((dir_corrente +"/"+ str(peso_dir)), float_array)
                
                if (numbytes/2100) == controleAmostras:
                    self.incrimentaContagemArquivo()
                    
                    if self.contPasta >= self.ControleDeArquivos:
                        return True
            else:

                input_file = open((dir_corrente +"/"+ str(self.contPasta)), 'a')
                numbytes = input_file.seek(0,2)
                
                if (numbytes/2100) != controleAmostras :
                    print("\n=> Numero de bytes no RECIC: ", numbytes)
                    
                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    numbytes = input_file.tell()
                    
                    print("\n=> numero de bytes pos insert no RECIC", input_file.tell())
                    
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
                print("\n=> ", error)
                pass

    
    def reiniciaContagemArquivo(self):
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write("0")
        f.close()
        
        f = open((self.dir + "/data/0"), 'w')
        f.close()
    
    def incrimentaContagemArquivo(self):
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta + 1))
        f.close()
            

    def _incrimentaContagemArquivo(self):
        print("noREC")
        
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
        
        if self.contPasta != self.ControleDeArquivos:
            f = open((self.dir + "/data/" + str(self.contPasta)), 'w')
            f.close()
            


    def contArq(self):
        return sorted(os.listdir(self.dir + "/data"))
    
    
        
        

                
                
                
       
        

