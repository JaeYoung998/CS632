import requests
import xml.etree.cElementTree as ET
import datetime

headers = {
    'AccountKey' : '0pSoqNHQQz6P1LCtlhFTLW=='
}
url = 'http://datamall2.mytransport.sg/ltaodataservice/BusStops'
response = requests.get(url=url, headers=headers)

values = response.json()['value']
dt = datetime.datetime.now().replace(microsecond=0).isoformat()

# data = {
#     'root':  'schema Version =\"1.2\" creationData =\"2019-11-13\" xmlns:xsi = \"http://www.w3.org/2001/XMLSchema-instance\" xmlns:example=\"http://ns.example.com/epcis\" xmlns:p=\"http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader\" xmlns:epcis=\"urn:epcglobal:epcis:xsd:1\"'),
#     'vocabularyType' : "urn:gs1:epcisapp:singapore:bus:stops:info";
#     'vocabularyElement': "urn:epc:id:gsrn:88000264.101.30300001";
#     'attribute1' : "urn:gs1:epcisapp:BIs:line:BusStopCode";
#     'attribute2' : "urn:gs1:epcisapp:BIs:line:Latitude";
#     'attribute3' : "urn:gs1:epcisapp:BIs:line:Longitude";
# }

value = {
    "xmlns:epcis": "urn:epcglobal:epcis:xsd:1",
    "xmlns:p": "http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader",
    "xmlns:example": "http://ns.example.com/epcis",
    "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "creationDate": dt,
    "schemaVersion": "1.2"
}

id = 'urn:epc:id:gsrn:8800264.124.'

root = ET.Element('epcis:EPCISDocument', value)
EPCISHeader = ET.SubElement(root, 'EPCISHeader')
p_StandardBusinessDocumentHeader = ET.SubElement(EPCISHeader, 'p:StandardBusinessDocumentHeader')
ET.SubElement(p_StandardBusinessDocumentHeader, 'p:HeaderVersion').text = '1.2'
p_Sender = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:Sender')

p_Identifier = ET.SubElement(p_Sender, 'p:Identifier')
p_Identifier.text = 'p:Identifier'
p_Identifier.set('Authority', '')

p_Receiver = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:Receiver')

p_Identifier = ET.SubElement(p_Receiver, 'p:Identifier')
p_Identifier.text = 'p:Identifier'
p_Identifier.set('Authority', '')

p_DocumentIdentification = ET.SubElement(p_StandardBusinessDocumentHeader, 'p:DocumentIdentification')
ET.SubElement(p_DocumentIdentification, 'p:Standard').text = 'EPCglobal'
ET.SubElement(p_DocumentIdentification, 'p:TypeVersion').text = '1.2'
ET.SubElement(p_DocumentIdentification, 'p:InstanceIdentifier').text = 'p:InstanceIdentifier'
ET.SubElement(p_DocumentIdentification, 'p:Type').text = 'MasterData'
ET.SubElement(p_DocumentIdentification, 'p:MultipleType').text = 'true'
ET.SubElement(p_DocumentIdentification, 'p:CreationDateAndTime').text = dt
extension = ET.SubElement(EPCISHeader, 'extension')
EPCISMasterData = ET.SubElement(extension, 'EPCISMasterData')
VocabularyList = ET.SubElement(EPCISMasterData, 'VocabularyList')

VocabularyType = ET.SubElement(VocabularyList, 'Vocabulary', )#, ="urn:gs1:epcisapp:singapore:bus:stops:info")
VocabularyType.set('type', 'urn:gs1:epcisapp:singapore:bus:stops:info')
VocabularyElementList = ET.SubElement(VocabularyType, 'VocabularyElementList')

# count = 0
for v in values:
#     if count == 2:
#         break

    mid = id + str(v['BusStopCode'])
    VocabularyElement = ET.SubElement(VocabularyElementList, 'VocabularyElement')
    VocabularyElement.set('id', mid)
    et_subelement = ET.SubElement(VocabularyElement, 'attribute')
    et_subelement.text = str(v['BusStopCode'])
    et_subelement.set('id', 'urn:gs1:epcisapp:BIS:line:BusStopCode')

    et_subelement = ET.SubElement(VocabularyElement, 'attribute')
    et_subelement.text = str(v['Latitude'])
    et_subelement.set('id', 'urn:gs1:epcisapp:BIS:line:Latitude')

    et_subelement = ET.SubElement(VocabularyElement, 'attribute')
    et_subelement.text = str(v['Longitude'])
    et_subelement.set('id', 'urn:gs1:epcisapp:BIS:line:Longitude')
    #count = count+1

EPCISBody = ET.SubElement(root, 'EPCISBody')
ET.SubElement(EPCISBody, 'EventList')

tree = ET.ElementTree(root)
tree.write('BusStops.xml', encoding='utf-8')



