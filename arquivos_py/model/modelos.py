import json

class Modelos:
    def __init__(self, pack, float_array, temperatura = 0):
        
        _id = pack[pack.rfind("B")+1:]
        TIni = self.pegaDate(pack[:pack.rfind("A")])
        TFim = self.pegaDate(pack[pack.rfind("A")+1:pack.rfind("B")])
        
        data = []
        for i in range(0, (len(float_array)) , 3):
            data.append({"aceleracaoX": float_array[i], "aceleracaoY": float_array[i+1],  "aceleracaoZ" : float_array[i+2], "temperatura": temperatura})
            
        
        self.idVaca = {"idVaca": int(_id)}
        self.horaFin = {"horaFin": TFim }
        self.horaIni = {"horaIni" : TIni}
        self.comportamentos = {"comportamentos": data}
        self.quantidade = {"quantidade":int(len(float_array)/3)}
        
    def pegaDate(self, DAT = "2022_7_22_2_6_2"):
        
        print(DAT)
        
        date = []
        for i in range(DAT.count("_")):
            date.append(DAT[:DAT.find("_")])
            DAT = DAT[DAT.find("_") + 1:]
           
        return "{}-{}-{} {}:{}:{}.{}".format(date[0], date[1], date[2], date[3],  date[4], date[5], DAT)
    
    def jsonString(self):
        
        self.quantidade.update(self.comportamentos)
        self.quantidade.update(self.horaFin)
        self.quantidade.update(self.horaIni)
        self.quantidade.update(self.idVaca)
        return json.dumps(self.quantidade)
        