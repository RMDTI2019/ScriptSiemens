import os
import sys
import re
from CDRLine import CDRLine

'''
Last Update: 20190705
    //Se agrega regla a las llamadas que comienzan con 1 y riene 11 digitos, cortar el campo extension
Script Siemmens



Este Script se encarga de procesar el CDR Crudo de Siemmens, es script devera de recibir 4 parametros en el siguiente orden
Carpeta Origen (Relativa al archivo .py)
Carpeta Destino (Relativa al archivo .py)
Extension de los archivos a procesar(. log se validan los campos con ayuda de una expresion regular)
Longuitud de las extensiones (cantidad de digitos que se cortaran para obtener la extensión)


Ejemplo Ejecucion
    "python CDRSiemens.py CDR CDRSalida  .log 4"
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
                print("\tERROR: el numero de parametros no es correcto, se esparaban 5 parametros")            

        except Exception as e :
            print ("\tError en el método: CDRSiemens: "+str(e))
            return
    
    def InicioProceso(self):
        try:
            
            if (os.path.exists(obj.OriginFolder)):
                listaArchivos = [x for x in os.listdir(obj.OriginFolder) if x.endswith(obj.FileExtention)]

                if (len(listaArchivos )> 0):
                    for arch in listaArchivos:

                        if(os.path.isfile(os.path.join(obj.DestinationFolder,arch))):
                         os.remove(os.path.join(obj.DestinationFolder,arch))
                         #print("Se Borra  archivo en salida: "+arch)

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

                
                if(objCDRLine.TipoLlamada != "INVALIDA"):
                    self.CreaArchivoSalida(stringRes)
                

                
        except Exception as e :
            print("\tError en ValidaLinea: " +str(e))
            return
    '''Metodo aplica reglas sobre los campos'''
    def ProcesarLlamada(self,objCDRLine):
        try:

            inicioExten  = len(objCDRLine.Exten)-int(obj.ExtenLen)
            inicioNo  = len(objCDRLine.No)-int(obj.ExtenLen)
            
            ''''R1:
                    Exten: start =>52 && len 12
                    No: start =>52 && len = 12
            '''
            if(len(objCDRLine.Exten.strip()) == 12 and objCDRLine.Exten.startswith("52") and len(objCDRLine.No.strip()) == 12 and objCDRLine.No.startswith("52")):
                objCDRLine.TipoLlamada = "ENLACE"
                
                objCDRLine.Exten =  objCDRLine.Exten[inicioExten:]
                objCDRLine.No =  objCDRLine.No[inicioNo:]

                '''
                    tro = vacio 
                    dir == "8"
                        se mofifica tro por 4013
                '''
                if (objCDRLine.Tro == ""  and objCDRLine.Dir == "8"):
                    troncalDefault = "4013"
                    objCDRLine.Tro = troncalDefault
            
            
            elif (objCDRLine.No.startswith("1") and len(objCDRLine.No) == 11):
                objCDRLine.TipoLlamada = "ENLACE"


                if(objCDRLine.No.startswith("11") and len(objCDRLine.Cod) == 0):
                    objCDRLine.Exten = objCDRLine.Exten[inicioExten:]

                elif(objCDRLine.No.startswith("1800") == False and objCDRLine.No[0:2] != "11"):
                    objCDRLine.No = "900" + objCDRLine.No
                    objCDRLine.Exten = objCDRLine.Exten[inicioExten:]
                    
                elif(  len(objCDRLine.Cod) > 0 or   objCDRLine.No.startswith("1800")   ):
                    objCDRLine.Exten = objCDRLine.Exten[inicioExten:]
                    objCDRLine.No = "90" + objCDRLine.No


                
                else:
                    objCDRLine.TipoLlamada = "INVALIDA"                    

            elif ( ((len(objCDRLine.No) == 10) and (objCDRLine.Dir == "EE") ) or(objCDRLine.No.startswith("1234567890") ) ):
                objCDRLine.TipoLlamada = "ENTRADA"

                objCDRLine.Exten =  objCDRLine.Exten[inicioExten:]
                
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

