import requests
import xml.etree.cElementTree as ET
import datetime
import json

posturl = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/VocabularyCapture'
validationurl = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/EPCISMasterDataDocumentValidation'

headers = {
    'AccountKey' : '0pSoqNHQQz6P1LCtlhFTLW=='
}

url1 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops'
url2 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=500'
url3 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=1000'
url4 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=1500'
url5 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=2000'
url6 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=2500'
url7 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=3000'
url8 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=3500'
url9 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=4000'
url10 = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip=4500'

response= []
values  = []
response.append(requests.get(url=url1, headers=headers))
response.append(requests.get(url=url2, headers=headers))
response.append(requests.get(url=url3, headers=headers))
response.append(requests.get(url=url4, headers=headers))
response.append(requests.get(url=url5, headers=headers))
response.append(requests.get(url=url6, headers=headers))
response.append(requests.get(url=url7, headers=headers))
response.append(requests.get(url=url8, headers=headers))
response.append(requests.get(url=url9, headers=headers))
response.append(requests.get(url=url10, headers=headers))

for i in range(0, 10):
    values.append(response[i].json()['value'])

dt = datetime.datetime.now().replace(microsecond=0).isoformat()

def postXMLData(filename):
    print('Attempting to post: ' + filename)
    isValidated = False

    with open(filename) as xml:
        r = requests.post(validationurl, data=xml)
        validationResponse = r.json()
        isValidated = validationResponse['isValidated']

    if isValidated is True:
        with open(filename) as final_xml:
            r1 = requests.post(posturl, data=final_xml)
            return r1.content

    else:
        print('Results not validated, check your xml structure!')
        return isValidated

def getbusroute():
    url = 'http://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=15000'
    headers = {'AccountKey' : '0pSoqNHQQz6P1LCtlhFTLW==', 'accept':'application/json'}
    r = requests.get(url=url, headers=headers)
    return json.dumps(r.json(), indent=4)

route = json.loads(getbusroute())

value = {
    "xmlns:ns0": "urn:epcglobal:epcis-masterdata:xsd:1",
    "schemaVersion": "1.0",
    "creationDate": dt
}

id = 'urn:epc:id:sgln:88002694.102.'

root = ET.Element('ns0:EPCISMasterDataDocument', value)
# EPCISHeader = ET.SubElement(root, 'EPCISHeader')
# p_StandardBusinessDocumentHeader = ET.SubElement(EPCISHeader, 'p:StandardBusinessDocumentHeader')
# ET.SubElement(p_StandardBusinessDocumentHeader, 'p:HeaderVersion').text = '1.2'
# p_Sender = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:Sender')
#
# p_Identifier = ET.SubElement(p_Sender, 'p:Identifier')
# p_Identifier.text = 'p:Identifier'
# p_Identifier.set('Authority', '')
#
# p_Receiver = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:Receiver')
#
# p_Identifier = ET.SubElement(p_Receiver, 'p:Identifier')
# p_Identifier.text = 'p:Identifier'
# p_Identifier.set('Authority', '')
#
# p_DocumentIdentification = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:DocumentIdentification')
# ET.SubElement(p_DocumentIdentification, 'p:Standard').text = 'EPCglobal'
# ET.SubElement(p_DocumentIdentification, 'p:TypeVersion').text = '1.2'
# ET.SubElement(p_DocumentIdentification, 'p:InstanceIdentifier').text = 'p:InstanceIdentifier'
# ET.SubElement(p_DocumentIdentification, 'p:Type').text = 'MasterData'
# ET.SubElement(p_DocumentIdentification, 'p:MultipleType').text = 'true'
# ET.SubElement(p_DocumentIdentification, 'p:CreationDateAndTime').text = dt
# extension = ET.SubElement(EPCISHeader, 'extension')
# EPCISMasterData = ET.SubElement(extension, 'EPCISMasterData')
EPCISBody = ET.SubElement(root, 'EPCISBody')
VocabularyList = ET.SubElement(EPCISBody, 'VocabularyList')

VocabularyType = ET.SubElement(VocabularyList, 'Vocabulary', )#, ="urn:gs1:epcisapp:singapore:bus:stops:info")
VocabularyType.set('type', 'urn:gs1:epcisapp:singapore:bus:stop:info')
VocabularyElementList = ET.SubElement(VocabularyType, 'VocabularyElementList')

BusStops = []
for element in route['value']:
    serviceNo = element['ServiceNo']
    if serviceNo == '518':
        BusStops.append(element['BusStopCode'])
count = 0
for i in range(0,10):
    value = values[i]
    for v in value:
        for busstops in BusStops:
            if busstops == v['BusStopCode']:
                mid = id + str(v['BusStopCode'])
                VocabularyElement = ET.SubElement(VocabularyElementList, 'VocabularyElement')
                VocabularyElement.set('id', mid)

                et_subelement = ET.SubElement(VocabularyElement, 'attribute')
                et_subelement.text = str(v['BusStopCode'])
                et_subelement.set('id', 'urn:gs1:epcisapp:bis:stop:id')

                et_subelement = ET.SubElement(VocabularyElement, 'attribute')
                et_subelement.text = str(v['Description'])
                et_subelement.set('id', 'urn:gs1:epcisapp:bis:stop:stopname')

                et_subelement = ET.SubElement(VocabularyElement, 'attribute')
                et_subelement.text = str(v['Latitude'])
                et_subelement.set('id', 'urn:gs1:epcisapp:bis:stop:latitude')

                et_subelement = ET.SubElement(VocabularyElement, 'attribute')
                et_subelement.text = str(v['Longitude'])
                et_subelement.set('id', 'urn:gs1:epcisapp:bis:stop:longitude')

                et_subelement = ET.SubElement(VocabularyElement, 'attribute')
                et_subelement.text = 'urn:epc:id:gsrn:88002694.101.518'
                et_subelement.set('id', 'urn:gs1:epcisapp:bis:stop:buslines')

                count = count + 1
print("count", count)
# EPCISBody = ET.SubElement(root, 'EPCISBody')
# ET.SubElement(EPCISBody, 'EventList')

tree = ET.ElementTree(root)
tree.write('BusStops518.xml', encoding='utf-8')

print(postXMLData('BusStops518.xml'))
