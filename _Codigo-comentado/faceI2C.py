from machine import I2C, Pin, RTC
import binascii
import time
import os
import json


"""
Esta classe tem o intuito de configurar e receber os dados do acelerometro e tudo que é nescessario para manter a ordem nesse sistema.
"""
"""
dir - diretorio utilizado para guardar os valores de ccorreção de eixo
SDA_PIN - Pino suportavel para comunicação I2C
SCL_PIN - Pino suportavel para comunicação I2C
FREQ_I2C - Pino suportavel para comunicação I2C
gav - Define se se o valor de aceleração esta em função da gravidade ou nao
scale - Define a escala de amostra da aceleração  |2G - 0 | 4G - 1 | 8G - 2 | 16G - 3| 
freqAmostra - Pode assumir valores de 0 a 256, setando a frequencia de amostra como (1kHz/freqAmostra)
"""    
class FaceI2C():

"""
Definição dos endereço I2C em decimal dos Registradores da placa MP6050 utilisados
"""

    MPU = 107
    MPU2 = 108
    ADDR = 104
    RATED = 25
    FIFO_DATA = 116
    OVERW_FIF0 = 26
    FIFO_EN_OP = 106                                            
    FUNDO_SCALE = 28
    FIFO_EN_ACC = 35
    SELF_TEST_s = 13
    I2C_MST_CTRL = 36
    FIFO_OFLOW_INT = 56
    
"""
    def __init__(self, dir):
        Atraves da classe I2C podemos manipular e cria uma comunicação I2C via software utilizando dos software, qual se queira.
        O contrutor cria um objeto IC2 utilizando pinos 26 e 25 (por padrão) e um baudrate de 5k....Alem do mais ele cria um objeto RTC para uso de sua memoria(unica que não se perde com o deep sleep) 
        É possivel ainda parmetrizar as instancias dessa classe com funionalidade diferente como:

        dir = "/"  -> Path do endereço qual pode ser utilizado para salvar ou obter arquivos em disco
        SDA_PIN = 25,  -> Pino de comunicação I2C (data)
        SCL_PIN = 26, -> Pino de comunicação I2C (clock)
        FREQ_I2C = 5000, -> frequencia de comunicação I2C (não utrapassara 10K)
        gav = False, -> Formato de dado de aceleração a ser configurado, em função (true) ou nao (false) da gravidade
        scale = 0, -> fundo de escala dos dados ( 0 -> 2g | 1 -> 4g | 2 -> 8g | 3 -> 16g |)
        freqAmostra = 250 -> Frequencia de amostragem qual o mp6050 irar bufferizar os dados ate estourar dada por (1000/freqAmostra) hz
"""
    
    def __init__(self, dir = "/", SDA_PIN = 25, SCL_PIN = 26, FREQ_I2C = 5000, gav = False, scale = 0, freqAmostra = 250):
        
        if scale == 0:
            self.LSB = 16384
        elif scale == 1 :
            self.LSB = 8192
        elif scale == 2 :
            self.LSB = 4096
        elif scale == 3 :
            self.LSB = 2048
            
        self.dir = dir
        
        self.setScale = scale << 3
        
        self.convToGav = ((9.80/ self.LSB) if (gav == False) else ((1/ self.LSB)))

        self.ratedFreq = freqAmostra - 1 
                 
        self.i2c = I2C(1, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=FREQ_I2C)
        
        self.endereco  = self.i2c.scan()
        
        self.rtc = RTC()

    
"""
    def writeto_mem_bit(self, end, Regis , data , destr):
        Rotina responsavel  puramente por escrever os dados no registrador enviado. recebe como parametro o endereço I2C, o Registrador para escrita, o dado e o sinal "destr".
        destr é foi criado para dizer se o byte vai destruir o existente no registrador ou não.
"""    
    def writeto_mem_bit(self, end, Regis , data , destr = 0):
        
        aux_ex = self.i2c.readfrom_mem(end, Regis, 1)

        if destr == 1:
            real_Data = data
        else:
            real_Data = data| aux_ex[0]
            
        self.i2c.writeto_mem(end, Regis,  bytes([real_Data]))


"""
    def ContagemPilha(self):
        Rotina responsavel pela contagem do dos bytes virgente na pilha do MP6050, como são dois bytes ele os concatena pra obter os 16bits
"""
    
    def ContagemPilha(self):
        Cont = self.i2c.readfrom_mem(self.ADDR, 114, 2)
        count = Cont[0] << 8 | Cont[1]
        return count


"""
    def twos_comp(self, val):
        Faz um complemento de 2 com a word enviada para pegar os valores negativos da aceleração
"""
    def twos_comp(self, val):
        bits = 16
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

"""
    def Calendario(self):
        Calendario é uma rotina pensada para se utilizar de uma referencia temporal das amostras... Atraves do objeto tipo RTC ele lê o horario atual e o guarda na memoraia do RTC
        Assim quando ele acorda do deepSleep ele tem tanto a refencia do tempo atual, pela nova leitura que é feita, quanto a referencia do tempo passado(que foi salva na memoria do rtc,
        pois ela não se perde ao dormir)
"""
    def Calendario(self):
        
        Horario = self.rtc.datetime()
        
        timer = [0]*2
        
        AmD = "{}_{}_{}".format(Horario[0], Horario[1], Horario[2])
        HmS = "_{}_{}_{}_{}".format(Horario[4], Horario[5], Horario[6], Horario[7])
        
        timer[0] = self.rtc.memory()        #Memoria antiga
        self.rtc.memory(AmD + HmS)          #Coloca na memoria a referencia de memoria nova
        timer[1] = self.rtc.memory()        #Quarda o novo horario na memoria do rtc
        
        return timer
    
"""
    def pega_valor(self):
        Rotina principal da CLasse I2C, fica responsavel por pegar e tratar os dados do buffer ou pilha do MP6050.
"""
    def pega_valor(self):
        
        AccX = [0]*170 
        AccY = [0]*170 
        AccZ = [0]*170
        time = []
        
        valores = self.i2c.readfrom_mem(self.ADDR, self.FIFO_DATA, 1020)
        time = self.Calendario()

        for i in range(170):
            
            AccX[i] = (self.twos_comp((valores[0 + (6*i)] << 8 | valores[1 + (6*i)])) * self.convToGav) 
            AccY[i] = (self.twos_comp((valores[2 + (6*i)] << 8 | valores[3 + (6*i)])) * self.convToGav) 
            AccZ[i] = (self.twos_comp((valores[4 + (6*i)] << 8 | valores[5 + (6*i)])) * self.convToGav) 
            
        valores = self.i2c.readfrom_mem(self.ADDR,self. FIFO_DATA, 4)          ### Desconsidera XY que sobra
        
        
        return AccX, AccY, AccZ, time
    
"""
    def iniciaMP(self):
        Esta rotina é executada uma unica vez, na primeira vez em que a rotina main é executada, ela configura todos os regitradores nescessarios para que o MP6050 execute conforme foi parametrizado no construtor
            MPU = 107
            MPU2 = 108
            ADDR = 104
            RATED = 25
            FIFO_DATA = 116
            OVERW_FIF0 = 26
            FIFO_EN_OP = 106                                            
            FUNDO_SCALE = 28
            FIFO_EN_ACC = 35
            SELF_TEST_s = 13
            I2C_MST_CTRL = 36
            FIFO_OFLOW_INT = 56

            (Olhar DataSheet)
"""
    
    def iniciaMP(self):
        
        self.writeto_mem_bit(self.ADDR, self.MPU, 0, 1)                        ### Energiza a MP6050
        
        self.writeto_mem_bit(self.ADDR, self.OVERW_FIF0, 70, 1)                ### DESABILITA SOBREESCRITA DA FILA QUANDO CHEIA e ativa o DLF para fr ser 1kz
        
        self.writeto_mem_bit(self.ADDR, self.FUNDO_SCALE, self.setScale , 1)   ### SETA FUNDO DE ESCALA 2g
        
        self.writeto_mem_bit(self.ADDR, self.RATED, self.ratedFreq, 1)         ### DEFINE FREQUENCIA DE AMOSTRAGEM 1kHz/ (1 + BYTE ENVIADO) = 4 Hz
        
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_OP, 64, 1)                ### HABILITA A INTERFACE ENTRE BUFFER E SERIAL
        
        self.i2c.readfrom_mem(self.ADDR, self.FIFO_DATA, 1024)                 ### Limpa a Pilha
        
        
        self.writeto_mem_bit(self.ADDR, self.FIFO_OFLOW_INT, 16 ,1) ### Habilita pino de interrup莽茫o da FIFO
        self.Calendario()
        
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_ACC, 8, 1)     ### HaBILITA O BUFFER DA aCELERA脟脙O
        
        FrequenciaAmostragem = (1000/(self.ratedFreq+1))
        TempoEstipuladoDormir = (1024/(FrequenciaAmostragem*6))
        
        print("\n=> Conversão pra gravidade ? ", self.convToGav)
        print("\n=> Frequencia de amostragem : ", FrequenciaAmostragem, "Hz")
        print("\n=> Tempo estipulado para dormir: ", TempoEstipuladoDormir, " s\n")
        print("\n=> Tempo estipulado para Envio(P/ 110 conjunto de amostras): ", (TempoEstipuladoDormir*110)/3600, " H\n")
        print("\n=> Escala de aceleração : ", (self.setScale>>3))
        print("\n=>Inicialização close\n")

