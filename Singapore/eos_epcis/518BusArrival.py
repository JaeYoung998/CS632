import datetime
import json
import requests
import xml.etree.cElementTree as ET

headers = {
    'AccountKey': '0pSoqNHQQz6P1LCtlhFTLW=='
}
lineID = '518'
giai = 'urn:epc:id:giai:88002694.124.' + lineID
action = 'OBSERVE'
bizStep = 'urn:gs1:epcisapp:bus:btt:arriving'
id = 'urn:epc:id:sgln:88002694.102.'
posturl = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/EventCapture'
validationurl = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/EPCISDocumentValidation'

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

# for i in range(0,10):
#     value = values[i]
#     for v in value:
#         print(v['RoadName'] + ' ' + v['BusStopCode'])

def getbusarrival(busstopcode):
    url = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2'
    headers = {'AccountKey': '0pSoqNHQQz6P1LCtlhFTLw==',
               'accept': 'application/json'}
    params = dict(BusStopCode=busstopcode, ServiceNo=lineID)

    r = requests.get(url=url, headers=headers, params=params)

    return json.dumps(r.json(), indent=4)


def getbusroute():
    url = 'http://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=15000'
    headers = {'AccountKey': '0pSoqNHQQz6P1LCtlhFTLW==', 'accept': 'application/json'}
    r = requests.get(url=url, headers=headers)
    return json.dumps(r.json(), indent=4)


def buildeventdata(busresponse):
    dt = datetime.datetime.now().replace(microsecond=0).isoformat()
    busdata = json.loads(busresponse)
    busstopid = busdata['BusStopCode']
    ibd = busdata['Services']

    value = {
        "xmlns:epcis": "urn:epcglobal:epcis:xsd:1",
        "xmlns:p": "http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader",
        "xmlns:example": "http://ns.example.com/epcis",
        "xmlns:arrival": "https://ns.example.com/epcis",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "creationDate": dt,
        "schemaVersion": "1.2"
    }
    root = ET.Element('epcis:EPCISDocument', value)
    EPCISBody = ET.SubElement(root, 'EPCISBody')
    EPCISEventList = ET.SubElement(EPCISBody, 'EventList')
    ObjectEvent = ET.SubElement(EPCISEventList, 'ObjectEvent')
    ET.SubElement(ObjectEvent, 'eventTime').text = dt
    ET.SubElement(ObjectEvent, 'eventTimeZoneOffset').text = "+08:00"
    EPCList = ET.SubElement(ObjectEvent, 'epcList')
    ET.SubElement(EPCList, 'epc').text = id + lineID + busstopid
    ET.SubElement(ObjectEvent, 'action').text = action
    ET.SubElement(ObjectEvent, 'bizStep').text = bizStep
    # EPCISReadPoint = ET.SubElement(ObjectEvent, 'readPoint')
    # ET.SubElement(EPCISReadPoint, 'id').text = id + busstopid
    ET.SubElement(ObjectEvent, 'arrival:stopID').text = busstopid

    BusName = 'nil'
    for i in range(0, 10):
        value = values[i]
        for v in value:
            if busstopid == v['BusStopCode']:
                BusName = v['RoadName']
                break

    ET.SubElement(ObjectEvent, 'arrival:stopName').text = BusName
    ET.SubElement(ObjectEvent, 'arrival:lineID').text = lineID
    for i in ibd:
        for y in i:
            if 'Next' in y:
                # print(i[y])
                estimatedArrival = i[y]['EstimatedArrival']
                if estimatedArrival != '':
                    ET.SubElement(ObjectEvent, 'arrival:estimatedTime').text = estimatedArrival
                else:
                    ET.SubElement(ObjectEvent, 'arrival:estimatedTime').text = 'nil'
    tree = ET.ElementTree(root)
    filename = 'BusArrival518_' + busdata['BusStopCode'] + '_EventData.xml'
    tree.write(filename, encoding='utf-8')
    return filename

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
            #return ""

    else:
        print('Results not validated, check your xml structure!')
        return isValidated



route = json.loads(getbusroute())

BusStops = []
for element in route['value']:
    serviceNo = element['ServiceNo']
    if serviceNo == '518':
        BusStops.append(element['BusStopCode'])

count = 0
for busstops in BusStops:
    arrival = getbusarrival(busstops)
    #print(arrival)
    print(postXMLData(buildeventdata(arrival)))
    # count = count + 1
    # if count == 2:
    #     print(postXMLData(buildeventdata(arrival)))
    #     break
