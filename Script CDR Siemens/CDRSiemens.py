import os
import sys
import re
from CDRLine import CDRLine

'''
script que recive 4 argumentos que son la carpeda de los archivos y las extensiones que quiere revisar 
'''
class CDRSimens:

    def __init__(self):
        PathAbs = ""
        OriginFolder = ""
        DestinationFolder = ""
        ExtenLen = 0
        FileExtention = ""
        ActualFileName = ""
        
    def CDRSiemens(self):
        try:
            listaArg = sys.argv

            if len(listaArg) == 5:
                obj.OriginFolder = os.path.abspath(listaArg[1])
                obj.DestinationFolder = os.path.abspath(listaArg[2])
                obj.FileExtention = listaArg[3]
                obj.ExtenLen = listaArg[4]

                validacionInicial = ""
                if not(os.path.isdir(obj.OriginFolder)):
                    validacionInicial = "Error campo OriginFolder no existe"

                if (len(obj.OriginFolder) > 0 and len(obj.DestinationFolder) > 0  and  obj.ExtenLen.isdigit()  and len(obj.FileExtention) > 0):

                    
                    self.InicioProceso()
                else:
                    print("No es posible continuar con el proceso"+validacionInicial)
            else:
                print("\tERROR: el numero de parametros no es correcto, se esparaban 3 parametros")            

        except Exception as e :
            print ("\tError en el método: CDRSiemens: "+str(e))
            return
    
    def InicioProceso(self):
        try:
            
            if (os.path.exists(obj.OriginFolder)):
                listaArchivos = [x for x in os.listdir(obj.OriginFolder) if x.endswith(obj.FileExtention)]
                
                if (len(listaArchivos )> 0):
                    for arch in listaArchivos:
                        
                        obj.ActualFileName = arch
                        self.ProcesaArchivo()
                else:
                    print("Lista de archivos esta vacia")
        except Exception as e :
            print("\tERROR en el método InicioProceso: "+str(e))
            return

    def ProcesaArchivo(self):
        try:
            
            pathArchivoActual = os.path.join(obj.OriginFolder,obj.ActualFileName)

            if (os.path.isfile(pathArchivoActual)):
                dataFile = open(pathArchivoActual,'r')

                self.ProcesarLineas(dataFile) 
                dataFile.close()   
            else:
                print("\tERROR: Error en el procesamiento del archivo. " + pathArchivoActual)            
        except Exception as e :
            print("ERROR en el método ProcesaArchivo: " + pathArchivoActual + str(e))        
            return

    def ProcesarLineas(self,dataFile):
        try:
            for  line in dataFile:
                
                line = re.sub('\n',' ',line)
                self.ValidaLinea(line)

        except Exception as e :
            print("\tERROR en LeerArchivo: "+str(e))
            return

    def ValidaLinea(self,line):
        try:
            
            regex = r"\s*(?P<exten>52[\d]{10})\s{1,}(?P<dir>[^\s]{1,2})\s{1,}(?P<no>\d{1,})\s*(?P<fecha>\d{4}-\d{2}-\d{2})\s{1,}(?P<hora>\d{2}:\d{2})\s{1,}(?P<dur>\d{2}:\d{2}:\d{2})\s{1,}(?P<cod>\d{1,})?\s{1,}\s*(?P<tro>[eE][pP]_.*)?\s*"
            
            objMatch = re.match(regex,line)
           
            if (objMatch != None):

                objCDRLine = CDRLine();

                objCDRLine.Line = line
                objCDRLine.Exten = objMatch.group("exten")
                objCDRLine.Dir = objMatch.group("dir")
                objCDRLine.No = objMatch.group("no")
                objCDRLine.Fecha = objMatch.group("fecha")
                objCDRLine.Hora = objMatch.group("hora")
                objCDRLine.Dur = objMatch.group("dur")
                objCDRLine.Cod = objMatch.group("cod")
                objCDRLine.Tro = objMatch.group("tro")
                    
                if(objCDRLine.Cod == None):
                    objCDRLine.Cod = ""

                if(objCDRLine.Tro == None):
                    objCDRLine.Tro = ""
                

                self.ProcesarLlamada(objCDRLine)
                
                stringRes = objCDRLine.Exten+","+objCDRLine.Dir+","+objCDRLine.No+","+objCDRLine.Fecha+","+objCDRLine.Hora+","+objCDRLine.Dur+","+objCDRLine.Cod+","+objCDRLine.Tro

                if(objCDRLine.TipoLlamada == "SALIDA"):
                    print(objCDRLine.Line)
                    print(stringRes)
                self.CreaArchivoSalida(stringRes)
                

                
        except Exception as e :
            print("\tError en ValidaLinea: " +str(e))
            return

    def ProcesarLlamada(self,objCDRLine):
        try:

            inicioExten  = len(objCDRLine.Exten)-int(obj.ExtenLen)
            inicioNo  = len(objCDRLine.No)-int(obj.ExtenLen)

            if(len(objCDRLine.Exten.strip()) == 12 and objCDRLine.Exten.startswith("52") and len(objCDRLine.No.strip()) == 12 and objCDRLine.No.startswith("52")):
                objCDRLine.TipoLlamada = "ENLACE"
                
                objCDRLine.Exten =  objCDRLine.Exten[inicioExten:]
                objCDRLine.No =  objCDRLine.No[inicioNo:]
            
                if (objCDRLine.Tro == ""):
                    troncalDefault = "4013"
                    objCDRLine.Tro = troncalDefault

            elif (objCDRLine.No.startswith("1") and len(objCDRLine.No) == 11):
                objCDRLine.TipoLlamada = "INTERNACIONAL"

                objCDRLine.Exten = objCDRLine.Exten[inicioExten:]
                objCDRLine.No = "00"+ objCDRLine.No

            elif (len(objCDRLine.No) == 10):
                objCDRLine.TipoLlamada = "ENTRADA"

                objCDRLine.Exten =  objCDRLine.Exten[inicioExten:]
                objCDRLine.No =  objCDRLine.No[inicioNo:]


                campoAux = objCDRLine.Exten
                objCDRLine.Exten = objCDRLine.No
                objCDRLine.No = campoAux

            else:
                objCDRLine.TipoLlamada = "SALIDA"

                objCDRLine.Exten =  objCDRLine.Exten[inicioExten:]
        except Exception as e :
            print("\tError en BuscaTipoLlamada: "+ str(e))
            return
    
    def CreaArchivoSalida(self,stringRes):
        try:
            destinationPathArchivo =  os.path.join(obj.DestinationFolder,obj.ActualFileName) 

            if not (os.path.isdir(obj.DestinationFolder)):
                os.mkdir(obj.DestinationFolder)
            
            f =   open(destinationPathArchivo, 'a+')
            f.write(stringRes+"\n")
            f.close()
            
        except Exception as e :
            print("\tERROR en método CrearArchivoSalida: " + str(e))
            return

obj = CDRSimens();
obj.CDRSiemens()

