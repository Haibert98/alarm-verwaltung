from jinja2 import Environment, FileSystemLoader
from Webseite.tokengenerator import TokenGenerator
import os

class WebSiteTemplateEngine():
    def __init__(self, picDir: str, locDir: str):
        self.token = None
        self.tuerCode1 = None
        self.tuerCode2 = None
        self.OUTPUTFILE = "Webserver/seite/index.php"
        self.picDir = picDir
        self.locDir = locDir
        self.dirMap = {picDir: "/res/photos", locDir: "/res/location"}
        
    def createWebSite(self, data, tuerCode):
        if tuerCode == None:
            raise
        dict = data
        tmp = self.tuerCodeSpalten(tuerCode)
        self.tuerCode1 = tmp[0]
        self.tuerCode2 = tmp[1]
        dict["tuerCode1"] = self.tuerCode1
        dict["tuerCode2"] = self.tuerCode2
        self.token = TokenGenerator.generiere()
        dict["token"] = self.token
        if dict["bild"] == "ja":
            self.getBilder(self.picDir, dict, "bilder")
        if dict["position"] == "ja":
            self.getBilder(self.locDir, dict, "positionbilder")
        if self.render(dict):
            return "https://192.168.167.54:8443/index.php?token=" + self.token
        else:
            raise
        

    def updateWebsite(self, data):
        dict = data
        dict["tuerCode1"] = self.tuerCode1
        dict["tuerCode2"] = self.tuerCode2
        dict["token"] = self.token
        if dict["bild"] == "ja":
            self.getBilder(self.picDir, dict, "bilder")
        if dict["position"] == "ja":
            self.getBilder(self.locDir, dict, "positionbilder")
        if os.path.exists(self.OUTPUTFILE):
            os.remove(self.OUTPUTFILE)
        if self.render(dict):
            pass
        else:
            raise
        

    def render(self, dict):
        templateLoader = FileSystemLoader(searchpath="./")
        templateEnv = Environment(loader=templateLoader)
        TEMPLATE_FILE = "Webseite/vorlage.php"
        template = templateEnv.get_template(TEMPLATE_FILE)
        dict = self.boolToString(dict)
        try:
            f = open(self.OUTPUTFILE, "wb")
            out = template.render(dict)
            f.write(out.encode("utf-8"))
            f.close()
            return True
        except Exception:
            print(str(repr(Exception.__cause__)))
            return False

    def boolToString(self, dict):
        if dict["fahrstuhl"]:
            dict["fahrstuhl"] = "Ja"
        else:
            dict["fahrstuhl"] = "Nein"
        return dict

    def tuerCodeSpalten(self, code):
        return code.split("|", 1)
    
    def deleteWebsite(self):
        if os.path.exists(self.OUTPUTFILE):
            os.remove(self.OUTPUTFILE)
    
    def getBilder(self, path, data, key):
        # tmp = []
        serverPath = self.dirMap[path]
        if os.path.exists(path):
            for file in os.listdir(path):
                if key not in data:
                    data[key] = [os.path.join(serverPath,file)] 
                else:
                    # tmp.append(file)
                    data[key].append(os.path.join(serverPath,file))

