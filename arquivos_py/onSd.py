from arquivos_py.acessServe import AcessServe
from array import array

import micropython
import struct
import json
import os
import gc


class OnSd(AcessServe):
    
    def __init__(self, dir = "/", host_p = str('192.168.100.8'), porta_p = 3040, _ContArquivosEnvio = 0):
        super().__init__(host = host_p, porta = porta_p)
        
        self.dir = dir
        self.ControleDeArquivos = _ContArquivosEnvio
        
        if "contPasta.txt" in os.listdir(self.dir):
            self.contPasta = int(open(self.dir + "/contPasta.txt").read())    
        else:
            self.contPasta = 0
            
<<<<<<< HEAD
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
    
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
        
        if  len(NaPasta) >= 10: ########
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
        v_dirs = sorted(os.listdir(self.dir + "/data"))
=======
        #print("\n=> Valor de contPasta", self.contPasta, "\n")
            
    def esvazia_memoria(self):
        gc.collect()
        micropython.mem_info()
        print('\n-----------------------------')
        print('Initial free: {} allocated: {}\n'.format(gc.mem_free(), gc.mem_alloc()))
    

        
    def AumentaContPasta(self):
        
        if  len(os.listdir(self.dir + "/data/"+str(self.contPasta))) >= 10: ########
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
        
        v_dirs = sorted(os.listdir(self.dir + "/data"))
        #print(v_dirs)
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        return v_dirs
    
    
    def auxSalvaDados(self, nameDateDataId = "", floatlist = []):
        
<<<<<<< HEAD
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
=======
        print((self.dir + "/data/"+str(self.contPasta) +"/"+ nameDateDataId))
        
        output_file = open((self.dir + "/data/"+str(self.contPasta) +"/"+ nameDateDataId), "w+b")
        
        float_array = array('f', floatlist)

        #print("\n=> ", float_array.buffer_info())

        output_file.write(bytes(float_array))
        output_file.close()
            
    def preeencheARQ(self, id_esp = 0, AccX = [], AccY = [], AccZ = [], timer = []):        
        
        nameDateDataId = (str(timer[0]) + "-" + str(timer[1])+ "-" + str(id_esp))
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        
        floatlist = []
        
        for Nacc in range(len(AccX)):
            floatlist.append(AccX[Nacc])
            floatlist.append(AccY[Nacc])
            floatlist.append(AccZ[Nacc])
        
        self.auxSalvaDados(nameDateDataId, floatlist)
        
        self.AumentaContPasta()
        
<<<<<<< HEAD
    def auxEnviaPacs(self, pack, float_array):
        
        T_ini = pack[:pack.rfind("A")]
        T_fim = pack[pack.rfind("A")+1:pack.rfind("B")]
        id = pack[pack.rfind("B")+1:]
        
        DataACCdic = {("0A_TIMER_INI"): T_ini,("0A_TIMER_FIN"): T_fim, ("0A_ID_ESP"): id}
        
        self.envia_servico(json.dumps((DataACCdic)))
        
        DataACCdic = {}
        
        num = 0
        for i in range(0, (len(float_array)) , 3):
            
            data = {str(num) + "X": str(float_array[i]), str(num) + "Y": str(float_array[i+1]),  str(num) + "Z" : str(float_array[i+2])}
            DataACCdic.update(data)
            num+=1
            
            if (num) == 85:
                self.envia_servico(json.dumps((DataACCdic)))
                DataACCdic = {}
                self.esvazia_memoria()
                
        self.envia_servico(json.dumps((DataACCdic)))
=======
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        
        
    def enviaPacs(self):
        
        v_dirs_envio = self.contArq()
<<<<<<< HEAD
=======
        print(v_dirs_envio)
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
        
        for LoteX in v_dirs_envio:
            
            realBin = sorted(os.listdir(self.dir + "/data/" + LoteX))
<<<<<<< HEAD
            
            for packs in (realBin):
                
                self.esvazia_memoria()
                input_file = open((self.dir + "/data/"+ str(LoteX) + "/" + packs), 'r+b')

                try:
                    bytesfile = input_file.read()
                    print("\n => TM :",  len(bytesfile))
                    float_array = array('f', struct.unpack((2*170*3*'f'), bytesfile))
                    
                    pack = [packs[2:packs.rfind("C")],packs[packs.rfind("C")+1:]]
                    
                    self.auxEnviaPacs(pack[0],float_array[:170*3])
                    self.auxEnviaPacs(pack[1],float_array[170*3:170*3*2])
                    
                    os.remove(self.dir + "/data/" + str(LoteX) + "/"  + packs)
                    
                except Exception as error:
                    print("\n=> Erro de envio: ",error)                  

                finally:
=======
            #print("\n=> Quantidade de aruivos dentro do json corrente: ", len(realJSON))
            
            for pack in (realBin):
                
                self.esvazia_memoria()
                input_file = open((self.dir + "/data/"+ str(LoteX) + "/" + pack), 'r+b')

                try:
                           
                    float_array = array('f')
                    
                    float_array = struct.unpack((170*3*'f'), input_file.read())
                    
                    print("\n=> ", float_array[0])
                    
                    ##colocar em string json
                    
                    T_ini = pack[:pack.rfind("b")-1]
                    T_fim = pack[pack.rfind("b"):pack.rfind("-")]
                    id = pack[pack.rfind("-")+1:]
                    
                    print(T_ini," ",T_fim," ", id)
                    
                    DataACCdic = {("0A_TIMER_INI"): T_ini,("0A_TIMER_FIN"): T_fim, ("0A_ID_ESP"): id}
                    
                    self.envia_servico(json.dumps((DataACCdic)))
                    
                    DataACCdic = {}
                    
                    print((len(float_array)/3))
                    num = 0
                    for i in range(0, (len(float_array)) , 3):
                        
                        data = {str(num) + "X": str(float_array[i]), str(num) + "Y": str(float_array[i+1]),  str(num) + "Z" : str(float_array[i+2])}
                        DataACCdic.update(data)
                        num+=1
                        
                        if (num) == 85:
                            self.envia_servico(json.dumps((DataACCdic)))
                            DataACCdic = {}
                            self.esvazia_memoria()
                            
                    self.envia_servico(json.dumps((DataACCdic)))    
                    os.remove(self.dir + "/data/" + str(LoteX) + "/"  + pack)
                    
                except Exception as error:
                    print("\n=>",error)                  

                finally:
                
>>>>>>> 881c3b25a038aaddb79c94899165f1ce170535a9
                    input_file.close()
                
                
                
       
        

