class Log:
    def addLog(self, classPath = "", data = ""):
        with open("./Logclass/" + classPath , "a+") as log:
            print((data + "\n"), file=log)