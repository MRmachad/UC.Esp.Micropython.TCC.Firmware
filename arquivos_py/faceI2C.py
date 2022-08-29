from machine import I2C, Pin, RTC
import binascii
import time
import os
import json


class FaceI2C():

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
        

        
            
    def writeto_mem_bit(self, end, Regis , data , destr = 0):
        #print("---------------")
        
        aux_ex = self.i2c.readfrom_mem(end, Regis, 1)
        #print(end)
        #print(Regis)
        #print("Valor lido ", aux_ex[0])
        #print("Valor a inserir ", data)
        
        
        if destr == 1:
            real_Data = data
        else:
            real_Data = data| aux_ex[0]
            
        #print("Valor colocado ", real_Data)
        
        self.i2c.writeto_mem(end, Regis,  bytes([real_Data]))
    
    def ContagemPilha(self):
        Cont = self.i2c.readfrom_mem(self.ADDR, 114, 2)
        count = Cont[0] << 8 | Cont[1]
        #print("Contagem Pilha ",count)
        return count
        
    def twos_comp(self, val):
        bits = 16
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val
    
    def Calendario(self):
        
        Horario = self.rtc.datetime()
        #print("horário", Horario)
        
        
        timer = [0]*2
        
        #print(len(timer))
        
        Ano = Horario[0]
        Mes = Horario[1]
        dia = Horario[2]
        hora = Horario[4]
        min = Horario[5]
        seg = Horario[6]
        
        AmD = "{}-{}-{}".format(Ano, Mes, dia)
        HmS = "_{}:{}:{}".format(hora, min, seg)
        
        timer[0] = self.rtc.memory()
        self.rtc.memory(AmD + HmS)
        timer[1] = self.rtc.memory()
       
        
        return timer
    
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
        print("\n=>Inicialização close")

