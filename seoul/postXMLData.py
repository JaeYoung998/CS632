import requests


def postXMLData(filename):
    print('Posting %s' % (filename))
    isVal = False
    headers = {'Content-Type': 'text/xml; charset=utf-8', }
    with open(filename) as xml:
        r = requests.post(validationURL, headers = headers, data = xml)
        print(r)
        response = r.json()
        isVal = response['isValidated']
    
    if isVal is True:
        print('Validation was successful, now posting(capturing!)')
        with open(filename) as final_xml:
            r1 = requests.post(postURL, headers = headers, data=final_xml)
            print(r1.status_code)
            return r1.content
    else:
        print('Not successful!!!')
        return isVal


#validationURL = 'http://210.93.116.66/epcis/Service/EPCISDocumentValidation'
#postURL = 'http://210.93.116.66/epcis/Service/EventCapture'

validationURL = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/EPCISDocumentValidation'
postURL = 'http://ec2-3-1-103-13.ap-southeast-1.compute.amazonaws.com:8080/epcis/Service/EventCapture'

filename = './created_event.xml'
print(postXMLData(filename))
