import os
import struct
from array import array
from arquivos_py.log import Log

"""
Classe responsavel pelo armazamento e por chamar o envio dos dados ao serviço http, esta é uma classe filha da "AcessServe" e portanto tem seus metodos 
"""

class OnSd(Log):

"""
    def __init__(self, dir = "/"):
        O diretorio aqui diz para qual lugar os dados vão ser salvos, por padrão "/" se refere ao sd do proprio esp, ao usar um micro sd, o parametro que vai ser passado dentro da intancia (na rotina main.py) será /sd
"""
    
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

"""
    def preeencheARQ(self, AccX = [], AccY = [], AccZ = [], timer = []):
        Recebe atraves da main.py vetores contendo os dados em x, y e z, tempo de referencia e o parametro de corte.
        Essa rotina faz um pré trtamento dos dados convertendo o array de tempo em bytes para seserem gravados em disco assim como concatenando os dados de aceleração
        na seguencia Accx, Accy e AccZ, qual serão gravados.
        feito isso ele entrega esses dados pré processados a rotina auxiliar  auxSalvaDadosqual fara prorpriamente dito a inserção dos dados em disco
"""     
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

"""
    def auxSalvaDados(self, _conjutoFloat = [], controleAmostras = 10):
        Esta rotina implemnta duas funcionalidade:
            Inserção e controle dos dados da flash 
            Controle de fluxo de memoria (MEMORIA CIRCULAR)

        Por padrão cada arquivo guarda somente uma quantidade definada por controleAmostras de conjuntos de dados. 
        Isso é feito para que se possa manipular a quantidade de conjunto por arquivo evitando referencia de stream muito grande ou diversos arquivos em disco

        O fluxo de dados é feito da seguinte maneira: todo arquivo é composto  e inserto pelo numero de conjunto de amostras em controleAmostras,
        cada arquivo recebe um nome seguencial de zero a diante (0,1,2....), quando um arquivo esta completo, ou seja, possui o numero de conjuto de amostras definido por parametro
        em controleAmostras, incrementase a variavel aulixiar de controle 'contPasta'... asssim na proxima inserção o arquivo a ser inserido seria um novo com o numero de referencia contpasta

        Este é o processo continuo de manipulação de memoria. No caso em que o controle de arquivos tenha se excedido, e por principio considerando que o esp não suporta mais armazenamento
        a memoria passa a ser circular, apagando os dados mais antigos e e inserindo novos dados nestes arquivos. 
"""
    def auxSalvaDados(self, _conjutoFloat = [], controleAmostras = 10):
        
         
        dir_corrente = (self.dir + "/data")
        on_diretorio_cor = self.contArq()
        peso_dir = len(on_diretorio_cor)
        
        print("\n=>self.contPasta = " , self.contPasta)
        print("\n=>peso_dir = " , peso_dir)
        print("\n=> RECIC: ", self.RECIC)
        
        # CASO NÃO TENHA ARQUIVO EM DISCO

        if peso_dir == 0:
            float_array = array('f', _conjutoFloat)
            self.finaliza_transicao((dir_corrente + "/0"), float_array)
            
        else:
            if self.RECIC == 0:

                

                print("\n=> ultimo Diretorio ", on_diretorio_cor[-1])

                input_file = open((dir_corrente +"/"+ str(on_diretorio_cor[-1])), 'a')              #Pega sempre o ultimo arquivo em disco ordenado de forma numerica
                numbytes = input_file.seek(0,2)


                # CASO TENHA ARQUIVO EM DISCO, NÃO ESTEJA EM RECIULAÇÃO E O ARQUIVO NÃO ESTEJA COMPLETO

                if (numbytes/2100) != controleAmostras :

                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    
                    numbytes = input_file.tell()
                    print("\n=> numero de bytes pos insert", input_file.tell())

                else:

                    # CASO TENHA ARQUIVO EM DISCO, NÃO ESTEJA EM RECIULAÇÃO E O ARQUIVO ESTEJA COMPLETO (usa-se a referencia do peso em disco pois esta esta sempre e uma unidade a frente do contpast)

                    numbytes = 2100
                    float_array = array('f', _conjutoFloat)
                    self.finaliza_transicao((dir_corrente +"/"+ str(peso_dir)), float_array)

                
                input_file.close()
                
                if (numbytes/2100) == controleAmostras:


                    # Caso o numero de conjuto de bytes seja igual ao controle de bytes deve fazer o incremento da referencia de arquivo atraves do contpast utilizando neste caso 'incrimentaContagemArquivo' 
                    
                    self.incrimentaContagemArquivo()        

                    # Caso self.contPasta >= self.ControleDeArquivos seja verdadeira, deve-se setar a flag de estouro retornando true para main para que seja feita a tentativa de envio dos dados

                    if self.contPasta >= self.ControleDeArquivos:
                        return True
            else:


                # CASO A MEMORIA ESTEJA EM RECICULAÇÃO ( neste momento fazemo tanto o incremento quanto a referencia de pasta pelo cont pasta, pois ele aqui funciona como um ponteiro de pasta ao qual se deseja sobreescrever )

                input_file = open((dir_corrente +"/"+ str(self.contPasta)), 'a')
                numbytes = input_file.seek(0,2)
                
                if (numbytes/2100) != controleAmostras :
                    
                    float_array = array('f', _conjutoFloat)
                    input_file.write(bytes(float_array))

                    input_file.seek(0,2)
                    numbytes = input_file.tell()
                    
                input_file.close()
                    
                if (numbytes/2100) == controleAmostras:

                     # O incremento de arquivo deve ser um pouco diferente pois neste momento existe tanto o arquivo aatual qual se escreveu quanto o proximo pois a memoria esta em recirculação
                     # Para isso utilizase o '_incrimentaContagemArquivo' que faz tanto incremento da referencia de pasta a escrever "contPasta" quanto a limpeza do dado seguinte a fim de liberar espaço
                    
                    self._incrimentaContagemArquivo()    

                    if self.contPasta >= self.ControleDeArquivos:
                        return True

        return False
    
"""
    def setRECIC(self):
        utilizado para configurar o modo de reciculação. Esta responsabiliade é dada a main, pois a ciencia de status de envio (falha ou sucesso é dela) é dela
"""
    def setRECIC(self):
        f = open((self.dir + "/RECIC.txt"), 'w')
        f.write("1")
        f.close()
        
"""
    def clearRECIC(self):
        utilizado para configurar o modo de reciculação. Esta responsabiliade é dada a main, pois a ciencia de status de envio (falha ou sucesso é dela) é dela
"""
    def clearRECIC(self):
        f = open((self.dir + "/RECIC.txt"), 'w')
        f.write("0")
        f.close()
        
"""
    def getRECIC(self):
        Retorna o parametro de RECIC armazenado em disco para que não se perce em deepsleep
"""
    def getRECIC(self):
        return int(open(self.dir + "/RECIC.txt").read())    
 
"""
    def finaliza_transicao(self, dirNameDateDataId = "", float_array = []):
        Auxiliar responsavel por guarda os arquivos em disco em formato de bytes
"""
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
    
"""
    def reiniciaContagemArquivo(self, naPasta = 0):
        Reinicia a contagem dereferencia de pasta. Por padrão ele é retornado para zero, no entanto no caso em que não se consiga manda somente parte dos arquivos, a referencia de pasta 
        se torna o complementar do mesmo. Desta forma de 10 arquivos caso seja enviado 5 a refencia guardada para inserção dos dados na memoria sera o 6 arquivo. 
        caso seja todos os 10 enviado a contagem volta a zero

"""
    def reiniciaContagemArquivo(self, naPasta = 0):
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(naPasta))
        f.close()
        
        f = open((self.dir + "/data/" + str(naPasta)), 'w')
        f.close()
    
"""
    def incrimentaContagemArquivo(self):
        Incrementa a refencia de arquivo cont past para que o sistema avançe para um novo arquivo
"""
    def incrimentaContagemArquivo(self):
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
            
"""
    def _incrimentaContagemArquivo(self):
        No modo de reciculção esta rotina Incrementa a refencia de arquivo cont past para que o sistema avançe para um novo arquivo limpando o proximo arquivo com um simples open("w")
"""
    def _incrimentaContagemArquivo(self):
        
        self.contPasta+=1
        
        f = open((self.dir + "/contPasta.txt"), 'w')
        f.write(str(self.contPasta))
        f.close()
        
        if self.contPasta < self.ControleDeArquivos:
            f = open((self.dir + "/data/" + str(self.contPasta)), 'w')
            f.close()

"""
    def contArq(self):
        Retorna um vetor contendo o nome dos arquivos gravados em disco que contem o conjunto de dados
"""  
            
    def contArq(self):
        on_diretorio_cor = [int(i) for i in os.listdir(self.dir + "/data")]
        on_diretorio_cor.sort()
        return [str(i) for i in on_diretorio_cor]
    
    
        
        

                
                
                
       
        

