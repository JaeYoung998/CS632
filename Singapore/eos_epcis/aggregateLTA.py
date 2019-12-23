import json

import requests

if __name__ == '__main__':
    def getbusroute():
        url = 'http://datamall2.mytransport.sg/ltaodataservice/BusRoutes?$skip=15000'
        headers = {'AccountKey': '0pSoqNHQQz6P1LCtlhFTLw==',
                   'accept': 'application/json'}
        r = requests.get(url=url, headers=headers)

        return json.dumps(r.json(), indent=4)


    def getbusarrival(busstopcode):
        url = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2'
        headers = {'AccountKey': '0pSoqNHQQz6P1LCtlhFTLw==',
                    'accept': 'application/json'}
        params = dict(BusStopCode=busstopcode, ServiceNo='518')

        r = requests.get(url=url, headers=headers, params=params)

        return json.dumps(r.json(), indent=4)

    route = json.loads(getbusroute())
    count = 0
    for element in route['value']:
        serviceNo = element['ServiceNo']
        if serviceNo == '518':
            print(serviceNo, element['BusStopCode'])
            print(getbusarrival(element['BusStopCode']))
            count=count+1

    print(count)





