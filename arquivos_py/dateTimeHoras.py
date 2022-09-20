from array import array
import struct

class DateTimeHoras():
    
    def __init__(self):
        pass

    def guardTimerIRQ(self, timer = ""):
        dt=[]
        for i in range(timer.decode().count("_")):
                
            dt.append(int(timer[:timer.decode().find("_")]))
            timer = timer[timer.decode().find("_") + 1:]
        dt.append(int(timer.decode()))    
        try:
            print(dt)
            
            float_array = array('i', dt)
            output_file = open("./IRQ", "w+b")
            
            output_file.write(bytes(float_array))
            
            output_file.close()
            
        except Exception as error:
            print("\n=> ", error)
            pass

    def intervalo(self, timer):
        
        print(timer)
        input_file = open("./IRQ", 'r+b')
        bytesfile = input_file.read()
        oldDate = array('i', struct.unpack((7*'i'), bytesfile)) 

    	dt=[]
    	
        for i in range(timer.decode().count("_")):
            
            dt.append(int(timer[:timer.decode().find("_")]))
            timer = timer[timer.decode().find("_") + 1:]
        dt.append(int(timer.decode()))
        
        print(dt)
        print(oldDate)
        sub = self.subtracao([oldDate[0],oldDate[1],oldDate[2],oldDate[3],oldDate[4],(oldDate[5]+oldDate[6]/1000000)],
                             [dt[0],dt[1],dt[2],dt[3],dt[4],(dt[5]+dt[6]/1000000)])
        print(sub)
        return sub[4]

    def subtracao(self, data1, data2):
        tempo = [0,0,0,0,0,0]
        for i in range(6):
            tempo[i] = data2[i] - data1[i]
        # Segundos
        for i in range (2):
            if tempo[5-i] < 0:
                tempo[4-i] = tempo[4-i] - 1
                tempo[5-i] = 60 + tempo[5-i]
        # Horas
        if tempo[3] < 0:
            tempo[2] = tempo[2] - 1
            tempo[3] = 24 + tempo[3]
        # Dias
        if tempo[2] < 0:
            cont = self.descobre_mes(data2[1], data2[0])
            tempo[1] = tempo[1] - 1
            tempo[2] = cont + tempo[2]
        # Mes
        if tempo[1] < 0:
            tempo[0] = tempo[0] - 1
            tempo[1] = 12 + tempo[1]
        
        return tempo

    def transf_segundos(self, data):
        pesos = [12,30,24,60,60,1]
        tempo = 0
        for a in range(6):
            segundos = 1
            for i in range(6-a):
                segundos = segundos * pesos[i+a]
            tempo = data[a] * segundos + tempo
        return tempo

    def descobre_mes(self, mes, ano):
        mes30 = [4, 6, 9, 11]
        mes31 = [1, 3, 5, 7, 8, 10, 12]
        cont = 0
        for mes in mes30:
            cont = 30
        for mes in mes31:
            cont = 31
        if cont == 0:
            res = ano % 4
            if res == 0:
                cont = 29
        if cont == 0:
            cont = 28
        return cont

