from machine import RTC
from array import array
import struct

"""
    Dado que em 08/10/2022 a linguagem micropython não tem suporte a datetime e manipulção propriamente dita de data
    Para  diversas operações e manipulações da mesma foi criada esta classe que implenta uma serie de metodos capazes 
    de contruir opeções com a mesma
"""

class DateTime():

"""
def subtracao(self, data1, data2):
    Retorna um vetor com as informações de ano, mes, dia, hora, minuto e segundo da operação (data2 - data1) de datas
"""

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

"""
def soma(self, data1, data2):
    Retorna um vetor com as informações de ano, mes, dia, hora, minuto e segundo da operação (data1 + data_valor) de datas
"""
    def soma(self, data1, valor):
        tempo = [0,0,0,0,0,0]
        for i in range(6):
            tempo[i] = data1[i] + valor[i]
        for i in range(2):
            if tempo[5-i] >= 60:
                tempo[5-i] = tempo[5-i] - 60
                tempo[4-i] = tempo[4-i] + 1
        if tempo[3] >= 24:
            tempo[3] = tempo[3] - 24
            tempo[2] = tempo[2] + 1
        cont = self.descobre_mes(data1[1], data1[0])
        if tempo[2] > cont:
            tempo[2] = tempo[2] - cont
            tempo[1] = tempo[1] + 1
        if tempo[1] > 12:
            tempo[1] = tempo[1] - 12
            tempo[0] = tempo[0] + 1

        return tempo

"""
def divisao(self, data1, data2):
    Retorna um vetor com as informações de ano, mes, dia, hora, minuto e segundo da operação (data1 / data_valor) de datas
"""
    def divisao(self, data1, valor):
        tempo = self.transf_segundos(data1)
        div = tempo / valor
        data = [0,0,0,0,0,0]
        pesos = [12,30,24,60,60,1]
        for a in range(6):
            pesos_div = 1
            for i in range(6-a):
                pesos_div = pesos_div * pesos[i+a]
            data[a] = int(div // pesos_div)
            div = div % pesos_div
        data[5] = data[5] + div
        return data

"""
def transf_segundos(self, data):
    Rotina auxiliar que retorna o valor da data em segundos
"""
    def transf_segundos(self, data):
        pesos = [12,30,24,60,60,1]
        tempo = 0
        for a in range(6):
            segundos = 1
            for i in range(6-a):
                segundos = segundos * pesos[i+a]
            tempo = data[a] * segundos + tempo
        return tempo

"""
def descobre_mes(self, mes, ano):
    Rotina auxiliar que retorna o valor de referencia de mes
"""
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

"""
def summ(self, hour = 0, add = 0):
    Rotina auxiliar que retorna o valor de hora acrecido de (add), implemntada para fazer o incremento de horas do dia
"""

    def summ(self, hour = 0, add = 0):
        tempo = hour + add
        if tempo >= 24:
            tempo -= 24
        return tempo

"""
def summ(self, hour = 0, menus = 0):
    Rotina auxiliar que retorna o valor de hora subtraida de (menus), implemntada para fazer o incremento de horas do dia
"""
    def sub(self, hour = 0, menus = 0):
        tempo = hour - menus
        if tempo < 0:
            tempo += 24
        return tempo

"""
    def GuardaHorarioCorrente(self, cr = []):
        Guarda em disco a data contida em cr
"""
    def GuardaHorarioCorrente(self, cr = []):
        rtc = RTC()
        dt = rtc.datetime()
        print(dt)
        print(cr)
        float_array = array('i', [cr[0],cr[1],cr[2],dt[3],cr[3],cr[4],cr[5],cr[6]])
        
        try:
            output_file = open("./DataCorrente", "wb")
            output_file.write(bytes(float_array))

        except Exception as error:
            self.addLog("DateTime.txt", str(error)) 
            pass
        finally:
            output_file.close()

"""
    def GuardaHorarioCorrente(self, cr = []):
        Recupera do disco a data guardada
"""
    def RecuperaHorarioCorrente(self):
        rtc = RTC()
        
        input_file = open("./DataCorrente", 'r+b')
        bytesfile = input_file.read()
        int_array = array('i', struct.unpack((8*'i'), bytesfile))
        print(int_array)
        
        rtc.datetime((int_array[0],int_array[1],int_array[2],int_array[3],int_array[4],int_array[5],int_array[6],int_array[7]))
        print("\n=>Hora Setada", rtc.datetime())
       