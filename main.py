import os
import fnmatch
import zipfile 
import xml.etree.ElementTree as et
import csv

class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

interest_fields = ['.//nfe:infNFe','.//nfe:ide/nfe:natOp', './/nfe:ide/nfe:dhEmi',
                    './/nfe:emit/nfe:xNome', './/nfe:dest/nfe:xNome',
                   './/nfe:total//nfe:vICMS', './/nfe:total//nfe:vNF']

namespaces = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}


with open ('data.csv', 'w', newline='') as csvfile:
    fieldsname = list(
        map(
            lambda a : a.split(':')[-1],
            interest_fields
        )
    )
    fieldsname = [ x + str(i) for i, x in enumerate(fieldsname)]

    interestTofieldName = dict(zip(interest_fields,fieldsname))

    writer = csv.DictWriter(csvfile, fieldnames=fieldsname)
    writer.writeheader()

    for path, dirs, files in os.walk('.',False):
        for file in fnmatch.filter(files,'*.zip'):
            zip_path = os.path.join(path,file)
            print(C.GREEN+f"processando caminho: {zip_path}: ..."+C.ENDC)
            with zipfile.ZipFile(zip_path, 'r') as zip_file:

                docs = {
                    "skiped" : 0,
                    "processed" : 0
                }

                for zip_info in zip_file.infolist():
                    if not fnmatch.fnmatch(zip_info.filename, "*[0-9].xml"): 
                        docs['skiped'] += 1
                        continue
                    
                    docs['processed'] +=1

                    # print(C.BLUE +f"\tprocessando arquivo {zip_info.filename} ..."+C.ENDC)
                    data = {}
                    with zip_file.open(zip_info) as arq:
                        xml_data = arq.read()
                        root = et.fromstring(xml_data)
                        for field in interest_fields:
                            element = root.find(field, namespaces)
                            if field == './/nfe:infNFe':
                                if element.get('Id') == "NFe50250452005378000696550020007934251344263166":
                                    f = open("arq.xml", 'w')
                                    f.write(xml_data.decode('utf-8'))
                                    f.close()
                                data[interestTofieldName[field]] = element.get('Id').replace(',','.') if element else ''
                            else:
                                data[interestTofieldName[field]] = element.text.replace(',','') if element != None else ''
                           

                    # for k, v in data.items():
                    #     print(C.CYAN+f"\t\t {k} : {v}"+C.ENDC)
                        
                    writer.writerow(data)

                print(C.WARNING+f"\tskiped: {docs['skiped']}"+C.ENDC)
                print(C.GREEN+f"\tprocessed: {docs['processed']}"+C.ENDC)


