"""
Classe auxiliar que é herdada nas classe principais para fazer o log de algum eventual erro sem para a execução do codigo
"""

class Log:
    def addLog(self, classPath = "", data = ""):
        with open("./Logclass/" + classPath , "a+") as log:
            print((data + "\n"), file=log)