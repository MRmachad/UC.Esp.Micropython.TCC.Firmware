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
    
    
    
    def __init__(self, dir):
        self.i2c = I2C(1, sda=Pin(25), scl=Pin(26), freq=5000)
        self.endereco  = self.i2c.scan()
        self.rtc = RTC()
        self.accel_bias = [0]*3
        self.dir = dir

        if "corr.txt" in os.listdir(dir):
            correct = open(self.dir + "/corr.txt").read().split(",")                         
            
            self.accel_bias[0] = float(correct[0][(correct[0].find(":") + 3):correct[0].rfind("\"")])
            self.accel_bias[1] = float(correct[1][(correct[1].find(":") + 3):correct[1].rfind("\"")])
            self.accel_bias[2] = float(correct[2][(correct[2].find(":") + 3):correct[2].rfind("\"")])
            
    def writeto_mem_bit(self, end, Regis , data , destr = 0):
        print("---------------")
        
        aux_ex = self.i2c.readfrom_mem(end, Regis, 1)
        print(end)
        print(Regis)
        print("Valor lido ", aux_ex[0])
        print("Valor a inserir ", data)
        
        
        if destr == 1:
            real_Data = data
        else:
            real_Data = data| aux_ex[0]
            
        print("Valor colocado ", real_Data)
        
        self.i2c.writeto_mem(end, Regis,  bytes([real_Data]))
    
    def ContagemPilha(self):
        Cont = self.i2c.readfrom_mem(self.ADDR, 114, 2)
        count = Cont[0] << 8 | Cont[1]
        print("Contagem Pilha ",count)
        return count
        
    def twos_comp(self, val):
        bits = 16
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val
    
    def Calendario(self):
        
        Horario = self.rtc.datetime()
        print("horário", Horario)
        
        
        timer = [0]*2
        
        print(len(timer))
        
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
            
            AccX[i] = (self.twos_comp((valores[0 + (6*i)] << 8 | valores[1 + (6*i)])) * 9.80/ 16384) - self.accel_bias[0]
            AccY[i] = (self.twos_comp((valores[2 + (6*i)] << 8 | valores[3 + (6*i)])) * 9.80/ 16384) - self.accel_bias[1] 
            AccZ[i] = (self.twos_comp((valores[4 + (6*i)] << 8 | valores[5 + (6*i)])) * 9.80/ 16384) - self.accel_bias[2]
            
        valores = self.i2c.readfrom_mem(self.ADDR,self. FIFO_DATA, 4)                           #Desconsidera XY que sobra
        
        
        return AccX, AccY, AccZ, time
    
    def iniciaMP(self):
        
        self.writeto_mem_bit(self.ADDR, self.MPU, 0, 1)             ### Energiza a MP6050
        self.writeto_mem_bit(self.ADDR, self.FUNDO_SCALE, 0 , 1)     ### SETA FUNDO DE ESCALA 2g
        self.writeto_mem_bit(self.ADDR, self.RATED, 249, 1)         ### DEFINE FREQUENCIA DE AMOSTRAGEM 1kHz/ (1 + BYTE ENVIADO) = 4 Hz
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_OP, 64, 1)     ### HABILITA A INTERFACE ENTRE BUFFER E SERIAL
        self.i2c.readfrom_mem(self.ADDR, self.FIFO_DATA, 1024)            ### Limpa a Pilha
        self.writeto_mem_bit(self.ADDR, self.OVERW_FIF0, 70, 1)     ### DESABILITA SOBREESCRITA DA FILA QUANDO CHEIA e ativa o DLF para fr ser 1kz
        self.writeto_mem_bit(self.ADDR, self.FIFO_OFLOW_INT, 16 ,1) ### Habilita pino de interrup莽茫o da FIFO
        self.Calendario()
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_ACC, 8, 1)     ### HaBILITA O BUFFER DA aCELERA脟脙O
         
        print("Inicialização close")

    def MPU6050SelfTest(self):
        rawData = [0]*4 
        selfTest = [0]*3 
        factoryTrim = [0]*3 
        destination = [0]*3 
                                                                                                  ## Configure the accelerometer for self-test

        self.writeto_mem_bit(self.ADDR, self.FUNDO_SCALE,  240)                                    ## Enable self test on all three axes and set accelerometer range to +/- 8 g
        time.sleep(0.25)                                                                               ## Delay a while to let the device execute the self-test

        rawData = self.i2c.readfrom_mem(self.ADDR, self.SELF_TEST_s, 4)                                                   ## X-axis self-test results
                                                                                                     ## Mixed-axis self-test results
                                                                                                  ## Extract the acceleration test results first
        print('TEStANDO')
        selfTest[0] = (rawData[0] >> 3) | (rawData[3] and 0x30) >> 4                                ## XA_TEST result is a five-bit unsigned integer
        selfTest[1] = (rawData[1] >> 3) | (rawData[3] and 0x0C) >> 2                                ## YA_TEST result is a five-bit unsigned integer
        selfTest[2] = (rawData[2] >> 3) | (rawData[3] and 0x03) >> 0                                ## ZA_TEST result is a five-bit unsigned integer

        print(selfTest[0])
        print(selfTest[1])
        print(selfTest[2])
                                                                                                  ## Extract the gyration test results first
        factoryTrim[0] = (4096.0*0.34)*(pow( (0.92/0.34) , ((selfTest[0] - 1.0)/30.0)))    ## FT[Xa] factory trim calculation
        factoryTrim[1] = (4096.0*0.34)*(pow( (0.92/0.34) , ((selfTest[1] - 1.0)/30.0)))    ## FT[Ya] factory trim calculation
        factoryTrim[2] = (4096.0*0.34)*(pow( (0.92/0.34) , ((selfTest[2] - 1.0)/30.0)))    ## FT[Za] factory trim calculation

                                                                                                       ## Report results as a ratio of (STR - FT)/FT  the change from Factory Trim of the Self-Test Response
                                                                                                       ## To get to percent, must multiply by 100 and subtract result from 100
        for i in range(3): 
            destination[i] = 100.0 + 100.0*(selfTest[i] - factoryTrim[i])/factoryTrim[i]               ## Report percent differences


        print("x-axis self test: Aceleração trim com : ", destination[0]) 
        print("y-axis self test: Aceleração trim com : ", destination[1]) 
        print("z-axis self test: Aceleração trim com : ", destination[2]) 


        if(destination[0] < 1.0 and destination[1] < 1.0 and destination[2] < 1.0):
            print("\n\n Pass Selftest! \n\n")  
            time.sleep(1)
            self.calibrateMPU6050()                                                       ## Calibrate gyro and accelerometers, load biases in

    def calibrateMPU6050(self):
     
        self.writeto_mem_bit(self.ADDR, self.MPU,  128)                     ### escreve no bit 7, o reset do dispositivo
        time.sleep(0.1)
            
                                                                                    #vai setar o clk e colocar o Pll com o x do giroscópio de referência
        self.writeto_mem_bit(self.ADDR, self.MPU,  1)
        self.writeto_mem_bit(self.ADDR, self.MPU2,  0)
        time.sleep(0.2)
            
        self.writeto_mem_bit(self.ADDR, self.FIFO_OFLOW_INT,  0)            # desabilita todas as interrupções
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_ACC,  0)                   # Desabilita o FIFO
        self.writeto_mem_bit(self.ADDR, self.MPU,  0)                       # USA O CLK INTERNO 8 KHZ
        self.writeto_mem_bit(self.ADDR, self.I2C_MST_CTRL,  0)              # Desabilitando o I2C master
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_OP,  0)
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_OP,  12)            # Reseta o FIFO 
        time.sleep(0.1)
            
            #Configurando o acelerômetro
            
        self.writeto_mem_bit(self.ADDR, self.OVERW_FIF0,  1)               # set o filtro em 188Hz
        self.writeto_mem_bit(self.ADDR, self.RATED,  0)  # set sample rate to 1 Hz
        self.writeto_mem_bit(self.ADDR, self.FUNDO_SCALE, 0)
        time.sleep(0.5)
            
        accelsensitivity = 16384
            
            # configura o fifo pra capturar a aceleração
            
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_OP,  64)# habilita o FIFO
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_ACC,  8) # habilita o sensor para pegar a aceleração e o giroscópio
        time.sleep(0.08)
            
            #At end of sample accumulation turn off fifo sensor
        self.writeto_mem_bit(self.ADDR, self.FIFO_EN_ACC,  0)
            
        packet_count = self.ContagemPilha()/6
        print('\n aqui ', packet_count)
            
        for i in range(packet_count):
            
            data = self.i2c.readfrom_mem(self.ADDR, self.FIFO_DATA, 6)
            self.accel_bias[0] += ((data[0] << 8) | data[1])
            self.accel_bias[1] += ((data[2] << 8) | data[3])
            self.accel_bias[2] += (((data[4] << 8) | data[5]))
            if(self.accel_bias[2] > 0):
                self.accel_bias[2] -= accelsensitivity
            else:
                self.accel_bias[2] += accelsensitivity
                
        print("\n\n BIAS: \n\n")    
        print(self.accel_bias[0])
        print(self.accel_bias[1])
        print(self.accel_bias[2])
            
        if packet_count != 0:
            self.accel_bias[0] /= packet_count
            self.accel_bias[1] /= packet_count
            self.accel_bias[2] /= packet_count
            
        print("\n\n BIAS: \n\n")   
        print(self.accel_bias[0])
        print(self.accel_bias[1])
        print(self.accel_bias[2])
        
        print("\n\n calibrando \n\n")
        time.sleep(1)
        
        #########################################
        accel_bias_reg = [0]*3
        data = [0]*6
        data = self.i2c.readfrom_mem(self.ADDR, 6, 6)
        
        accel_bias_reg[0] = ((data[0] << 8) | data[1])
            
        accel_bias_reg[1] = ((data[2] << 8) | data[3])
            
        accel_bias_reg[2] = ((data[4] << 8) | data[5])
        ########################################
        
        self.accel_bias[0] = self.accel_bias[0] / accelsensitivity
        self.accel_bias[1] = self.accel_bias[1] / accelsensitivity
        self.accel_bias[2] = self.accel_bias[2] / accelsensitivity
        
        data = {"_AccX_Corr": str(self.accel_bias[0]), "_AccY_Corr": str(self.accel_bias[1]), "_AccZ_Corr" : str(self.accel_bias[2])}
            
        
        f = open((self.dir + "/corr" + ".txt"), 'w')
        f.write(json.dumps(data))
        f.close()
        
        print("\n\n",accel_bias_reg[0],accel_bias_reg[1],accel_bias_reg[2], "\n\n")
            
