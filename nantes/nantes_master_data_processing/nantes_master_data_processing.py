import requests
import json
import zipfile
from lxml import etree
import xml.etree.ElementTree as ET
import os

def get_download_filename() :
    data = requests.get('https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=244400404_tan-arrets-horaires-circuits').json()
    records = data['records']
    fields=records[0]['fields']
    fichier=fields['fichier']
    filename = fichier['filename']
    return filename

def download_unzip(file_name,download,extract) :
    url = 'https://data.nantesmetropole.fr/explore/dataset/244400404_tan-arrets-horaires-circuits/files/16a1a0af5946619af621baa4ad9ee662/download/'
    if(download) :
        r = requests.get(url)
        open(file_name,'wb').write(r.content)

    if(extract) :
        zip_file = zipfile.ZipFile(file_name)
        zip_file.extractall()
        zip_file.close()



def convert_stop_to_EPCIS() :
    #os.mkdir('stop_info')
    attributes = [
        'urn:gs1:epcisapp:bis:stop:id',
        'urn:gs1:epcisapp:bis:stop:stopname',
        'urn:gs1:epcisapp:bis:stop:latitude',
        'urn:gs1:epcisapp:bis:stop:longitude',
        'urn:gs1:epcisapp:bis:stop:buslines'
    ];
    bus_stop_info_file = open('stops.txt','r')
    data = bus_stop_info_file.readline()

    value = {
        "xmlns:epcis": "urn:epcglobal:epcis-masterdata:xsd:1",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "schemaVersion": "1.0",
        "creationDate": "2019-12-08T23:42:00.0Z"
    }

    root = ET.Element('epcis:EPCISMasterDataDocument', value)
    EPCISBody = ET.SubElement(root, 'EPCISBody')
    VocabularyList = ET.SubElement(EPCISBody, 'VocabularyList')
    voctype = ET.Element('Vocabulary')
    voctype.set('type', 'urn:gs1:epcisapp:nantes:bus:stop:info')
    vocelemlist = ET.Element('VocabularyElementList')
    voctype.append(vocelemlist)
    VocabularyList.append(voctype)

    k=0
    for jj in range(50) :
        data = bus_stop_info_file.readline()
        if(data == "") : break
        epcis_data=[]
        data_split = data.split(',')
        stop_id = get_EPCIS_id(data_split[0],'converted_stops.txt')
        epcis_data.append(data_split[0].strip().lower())
        epcis_data.append(data_split[1].strip().lower())
        stop_latitude = data_split[3]
        epcis_data.append(stop_latitude.strip())
        stop_longitude = data_split[4]
        epcis_data.append(stop_longitude.strip())

        if(data_split[8]=="") :
             parent_stop = "0"
        else :
             parent_stop = get_EPCIS_id(data_split[8],'converted_stops.txt')

        # epcis_data.append(parent_stop.strip())
        # if(data_split[9]=="") :
        #     stop_wheechairBoarding = "NA"
        # else :
        #     stop_wheechairBoarding = "A"

        #epcis_data.append(stop_wheechairBoarding)
        #Find lines that belongs to.
        print(data_split[0])
        if(parent_stop == "0") :
            bus_lines = get_buslines_of_stop(data_split[0].strip())
        else :
            bus_lines = "NA"
        print(bus_lines)
        epcis_data.append(str(bus_lines))

        vocElement = etree.Element('VocabularyElement')
        vocElement.set('id', stop_id.strip())
        i=0
        for attribute in attributes :
            e = etree.Element('attribute')
            e.set('id', attribute)
            if (epcis_data == ""):
                e.text = "NA"
            else:
                e.text = epcis_data[i]
            vocElement.append(e)
            i += 1

        output = etree.tostring(vocElement, pretty_print=True, encoding='UTF-8')
        write_string = output.decode('utf-8')
        tree = ET.fromstring(write_string)
        vocelemlist.append(tree)

    output = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    write_string = output.decode('utf-8')
    xml_header = '<?xml version="1.0" encoding="utf-8"?>\n'+'<!DOCTYPE project>\n'
    write_string = xml_header+write_string
    file_name = os.path.join('stop_info','master_stop_info.xml')
    output_file = open(file_name, 'w')
    output_file.write(write_string)


def get_buslines_of_stop(stop_name) :
    route_trip_info = open('converted_route_id_trip_ids2.txt','r')
    trip_stop_info = open('converted_line_id_stop_ids.txt','r')
    bus_lines=[]
    stop_id_len = len(stop_name)
    while 1 :
        data=route_trip_info.readline()
        if(data == "") : break
        data_s = data.split('>>')
        route_id = data_s[0]
        trip_id = data_s[1].split(',')[0]
        while 1 :
            trip_data  = trip_stop_info.readline()
            if(trip_data == "") : break
            trip_data_s = trip_data.split('>>')
            if(trip_id == trip_data_s[0]) :
                stops = trip_data_s[1].split(',')
                for stop in stops :
                    if(stop[0:stop_id_len] == stop_name) :
                        bus_lines.append(get_EPCIS_id(route_id.strip(),'converted_routes.txt').strip())
        trip_stop_info.seek(0,0)

    return bus_lines



def convert_line_to_EPCIS() :
    #os.mkdir('line_info')
    attributes = [
        'urn:gs1:epcisapp:bis:line:id',
        'urn:gs1:epcisapp:bis:line:direction',
        'urn:gs1:epcisapp:bis:line:refbusstops',
        'urn:gs1:epcisapp:bis:line:refstartbusstop',
        'urn:gs1:epcisapp:bis:line:refendbusstop',
        'urn:gs1:epcisapp:bis:line:starttime',
        'urn:gs1:epcisapp:bis:line:endtime',
        'urn:gs1:epcisapp:bis:line:tripduration',
        'urn:gs1:epcisapp:bis:line:timezone'
    ]
    line_info_file = open('converted_route_id_trip_ids_dir.txt','r')

    value = {
        "xmlns:epcis": "urn:epcglobal:epcis-masterdata:xsd:1",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "schemaVersion": "1.0",
        "creationDate": "2019-12-08T23:42:00.0Z"
    }

    root = ET.Element('epcis:EPCISMasterDataDocument', value)
    EPCISBody = ET.SubElement(root, 'EPCISBody')
    VocabularyList = ET.SubElement(EPCISBody, 'VocabularyList')
    voctype = ET.Element('Vocabulary')
    voctype.set('type', 'urn:gs1:epcisapp:nantes:bus:line:info')
    vocelemlist = ET.Element('VocabularyElementList')
    voctype.append(vocelemlist)
    VocabularyList.append(voctype)

    for k in range(20) :
        epcis_data = []
        data = line_info_file.readline()
        if(data == "") : break;
        data_split = data.split('>>')
        raw_line_id = data_split[0]
        direction = data_split[1]
        if(direction != "") :
            trip_ids = data_split[2].split(',')
            head_trip = trip_ids[0]
            tail_trip = trip_ids[len(trip_ids)-1]
            if(tail_trip.strip() == "") :
                tail_trip = trip_ids[len(trip_ids)-2]


            line_id = get_EPCIS_id(raw_line_id,'converted_routes.txt')
            line_id_split = line_id.split('.')
            line_id_s = line_id_split[len(line_id_split)-1]
            epcis_data.append(raw_line_id.strip())
            epcis_data.append(direction.strip())

            ref_bus_stop = get_ref_busstops_by_line_id_dir(raw_line_id,int(direction))
            ref_bus_stops = ref_bus_stop.split(',')

            bus_stop_ids = []
            for bus_stop in ref_bus_stops :
                bus_stop_id = get_EPCIS_id(bus_stop.rstrip(),'converted_stops.txt')
                bus_stop_ids.append(bus_stop_id.rstrip())

            epcis_data.append(str(bus_stop_ids))
            start_bus_stop = str(bus_stop_ids[0])
            epcis_data.append(start_bus_stop)
            end_bus_stop    = str(bus_stop_ids[len(bus_stop_ids)-1])
            epcis_data.append(end_bus_stop)
            epcis_data.append(str(get_trip_startTime(head_trip.strip())))
            epcis_data.append(str(get_trip_endTime(tail_trip.strip())))
            epcis_data.append("")
            epcis_data.append("+01:00")



            vocElement = etree.Element('VocabularyElement')
            vocElement.set('id', line_id.strip())
            i = 0
            for attribute in attributes:
                e = etree.Element('attribute')
                e.set('id', attribute)
                if (epcis_data[i] == ""):
                    e.text = "NA"
                else:
                    e.text = epcis_data[i]

                vocElement.append(e)
                i += 1


            output = etree.tostring(vocElement, pretty_print=True, encoding='UTF-8')
            write_string = output.decode('utf-8')
            tree = ET.fromstring(write_string)
            vocelemlist.append(tree)

    output = ET.tostring(root)
    write_string = output.decode('utf-8')
    xml_header = '<?xml version="1.0" encoding="utf-8"?>\n'+'<!DOCTYPE project>\n'
    write_string = xml_header+write_string
    file_name = os.path.join('line_info', 'master_line_info.xml')
    output_file = open(file_name, 'w')
    output_file.write(write_string)


def get_EPCIS_id(raw_id,file_name) :
    ref_file1 = open(file_name,'r')
    while(1) :
        data = ref_file1.readline()
        if(data == "") :
            print('No Corresponding ID :',raw_id)
            break
        data_split = data.split('>>')
        if(data_split[0].strip() == raw_id.strip()) :
            ref_file1.seek(0,0)
            return data_split[1]
    return 0


def get_trip_startTime(trip_id) :
    ref_file = open('stop_times.txt','r')
    ref_file.readline()
    while(1) :
        data = ref_file.readline()
        if(data=='') :
            print('Not found id :',trip_id)
        data_s = data.split(',')
        ref_trip_id =  data_s[0]
        if(ref_trip_id == trip_id) :
            return data_s[1]


def get_trip_endTime(trip_id) :
    ref_file = open('stop_times.txt','r')
    ref_file.readline()
    while(1) :
        data = ref_file.readline()
        if(data == "") :
            print('Not found id',trip_id)
            return 0
        data_s = data.split(',')
        ref_trip_id =  data_s[0]
        if(ref_trip_id == trip_id) :
            while(1) :
                prev_offset = ref_file.tell()
                data = ref_file.readline()
                data_s = data.split(',')
                if(trip_id != data_s[0]) :
                    ref_file.seek(prev_offset-len(data),0)
                    break
            data = ref_file.readline()
            data_s = data.split(',')
            return data_s[1]



# def convert_bus_stops() :
#     file = open('stops.txt','r')
#     data = file.readline()
#     data_type = data.split(',')
#     xml_header = '<?xml version="1.0" encoding="UTF-8">\n'
#     j=0
#     for k in range(2) :
#         data = file.readline()
#         if data == "" : break
#         data_list = data.split(',')
#         r_data = [data_list[0], data_list[1], data_list[3], data_list[4], data_list[7], data_list[8], data_list[9]]
#         root = etree.Element('Vocabulary')
#         root.set('type','urn:gs1:epcisapp:nantes:bus:stop:info')
#         sub_root = etree.Element('VocabularyElementList')
#         attributes = ['urn:gs1:ecpisapp:BIS:stopid',
#                       'urn:gs1:ecpisapp:BIS:stopname',
#                       'urn:gs1:ecpisapp:BIS:latitude',
#                       'urn:gs1:ecpisapp:BIS:longitude',
#                       'urn:gs1:ecpisapp:BIS:locationtype',
#                       'urn:gs1:ecpisapp:BIS:parentstation',
#                       'urn:gs1:ecpisapp:BIS:wheelchairboarding'
#                       ]
#         i=0
#         for attrtibute in attributes :
#             e = etree.Element('attribute')
#             e.set('id',attrtibute)
#             if(r_data[i] == ""  or r_data[i] =="\n") :
#                 e.text="NA"
#             else :
#                 e.text=r_data[i]
#             sub_root.append(e)
#             i = i + 1
#         root.append(sub_root)
#         output = etree.tostring(root,pretty_print=True,encoding='UTF-8')
#         write_data = xml_header + output.decode('utf-8')
#         file_name =  'test' + str(j)
#         file_path = os.path.join('stopinfo',file_name)
#         w_file = open(file_path,'w',encoding='utf-8')
#         w_file.write(write_data)
#         j+=1


def construct_EPCIS_id(readfile,destfile,gs1_type,prefix,convert_id_header_,data_pos,padding) :
    s_file = open(readfile,'r')
    d_file = open(destfile,'w')
    d = s_file.readline()
    d_type = d.split(',')
    convert_id_header = 'urn:epc:id:'+gs1_type+':88002692.'+prefix+'.'
    j = 0
    while(1) :
        d = s_file.readline()
        if(d=="") : break
        split_d = d.split(',')
        origianl_id = split_d[data_pos]
        convert_id = convert_id_header + origianl_id.lower()
        write_data = origianl_id + ">>" + convert_id+"\n"
        d_file.write(write_data)
        j+=1


def construct_ref_id_2_target_ids(source_file,dest_file,ref_pos,target_pos) :
    s_file = open(source_file,'r')
    d_file = open(dest_file,'w')
    d = s_file.readline()
    d_type = d.split(',')
    while(1) :
        d =s_file.readline()
        if(d=="") : break
        d_split = d.split(',')
        ref_id = d_split[ref_pos]
        target_ids = d_split[target_pos]
        while(1) :
            prev_offset = s_file.tell()
            new_d = s_file.readline()
            new_d_split = new_d.split(',')
            new_ref_id = new_d_split[ref_pos]
            if(ref_id != new_ref_id) :
                s_file.seek(prev_offset,0)
                break
            target_ids =target_ids+","+new_d_split[target_pos]
        write_data = ref_id + '>>' + str(target_ids) + "\n"
        d_file.write(write_data)




def construct_ref_id_2_target_ids2(source_file,dest_file,ref_pos,target_pos,target_pos2) :
    s_file = open(source_file,'r')
    d_file = open(dest_file,'w')
    d = s_file.readline()
    d_type = d.split(',')
    while(1) :
        d =s_file.readline()
        if(d=="") : break
        d_split = d.split(',')
        ref_id = d_split[ref_pos]
        target_ids = d_split[target_pos]
        target_ids2 = ""
        target_id2 = d_split[target_pos2]
        new_target_id2 = ""
        while(1) :
            prev_offset = s_file.tell()
            new_d = s_file.readline()
            if(new_d =="")  : break
            new_d_split = new_d.split(',')
            new_ref_id = new_d_split[ref_pos]
            new_ref_id2 = new_d_split[target_pos2]
            if(ref_id != new_ref_id) :
                s_file.seek(prev_offset,0)
                break
            if(target_id2 == new_ref_id2) :
                target_ids =target_ids+","+new_d_split[target_pos]
            else :
                target_ids2 = target_ids2 + new_d_split[target_pos] + ","
                if(new_target_id2 == "") :
                    new_target_id2 = new_ref_id2

        write_data1 = ref_id +'>>'+ target_id2 + '>>' + str(target_ids) + "\n"
        write_data2 = ref_id +'>>'+ new_target_id2 + '>>' + str(target_ids2) + "\n"
        d_file.write(write_data1)
        d_file.write(write_data2)


def construct_ref_id_2_traget_ids3(source_file1,source_file2,dest_file,source_pos,source_pos2,target_pos) :
    source1 = open(source_file1,'r')
    source2 = open(source_file2,'r')
    dest    = open(dest_file,'w')
    source1.readline()
    source2.readline()
    while(1) :
        data = source1.readline()
        if(data == "") : break
        data_s = data.split(',')
        ref_id = data_s[source_pos].strip()
        target_ids = ""
        while(1) :
            data2 = source2.readline()
            if(data2 == "") : break
            data2_s = data2.split(',')
            if(ref_id == data2_s[source_pos2].strip()) :
                target_ids = target_ids + data2_s[target_pos] + ','
        source2.seek(0,0)
        write_data = ref_id + '>>' + str(target_ids) + '\n'
        dest.write(write_data)


def get_ref_busstops_by_line_id(line_id) :
    ref_file1 = open('converted_route_id_trip_ids.txt','r')
    ref_file2 = open('converted_line_id_stop_ids.txt','r')
    while(1) :
        d = ref_file1.readline()
        if(d =="") :
            print('line_id not found\n')
            break
        d_split = d.split('>>')
        if(d_split[0] == line_id) :
            trip_ids = d_split[1]
            trip_id = trip_ids.split(',')[0]
            break

    while(1) :
        d = ref_file2.readline()
        if(d=="") :
            print('trip_id not found\n')
            return 0
        d_split = d.split('>>')
        if(d_split[0]==trip_id) :
            return d_split[1]

def get_ref_busstops_by_line_id_dir(line_id,dir) :
    ref_file1 = open('converted_route_id_trip_ids_dir.txt','r')
    ref_file2 = open('converted_line_id_stop_ids.txt','r')
    while(1) :
        d = ref_file1.readline()
        if(d =="") :
            print('line_id not found\n')
            break
        d_split = d.split('>>')
        if(d_split[0] == (line_id)  and d_split[1] == str(dir)) :
            trip_ids = d_split[2]
            trip_id = trip_ids.split(',')[0]
            break

    while(1) :
        d = ref_file2.readline()
        if(d=="") :
            print('trip_id not found\n')
            return 0
        d_split = d.split('>>')
        if(d_split[0]==trip_id) :
            return d_split[1]

def postMasterxml(file_path,file_name) :
    file_name = os.path.join(file_path,file_name)
    print(file_name)
    with open(file_name,'r',encoding='utf-8') as final_xml :
        final_xml.seek(0,2)
        size = final_xml.tell()
        final_xml.seek(0,0)
        print(size)
        data = final_xml.read(size)
        r1 = requests.post('http://13.53.171.124:8080/epcis/Service/VocabularyCapture',data=data)
        print(r1)













if __name__ == '__main__' :
    #file_name = get_download_filename()
    #download_unzip(file_name,0,0)  # If download = 1 --> will download new file
    #construct_EPCIS_id('stops.txt','converted_stops.txt','sgln','101','800',0,4)
    #construct_EPCIS_id('routes.txt','converted_routes.txt','gsrn','100','303',0,4)
    #construct_EPCIS_id('trips.txt','converted_trip_ids.txt','gsrn','102','301',2,8)
    #construct_EPCIS_id('stops.txt','converted_stopname.txt','sgln','103','302',1,3)
    #construct_ref_id_2_target_ids('stop_times.txt','converted_line_id_stop_ids.txt',0,3)
    #construct_ref_id_2_target_ids('trips.txt','converted_route_id_trip_ids.txt',0,2)
    #construct_ref_id_2_target_ids2('trips.txt','converted_route_id_trip_ids_dir.txt',0,2,4)
    #construct_ref_id_2_traget_ids3('routes.txt','trips.txt','converted_route_id_trip_ids2.txt',0,0,2)
    #convert_line_to_EPCIS()
    #convert_stop_to_EPCIS()
    #print(get_buslines_of_stop('ABCH'))
    #convert_stop_to_EPCIS()
    postMasterxml('line_info','master_line_info.xml')
    postMasterxml('stop_info','master_stop_info.xml')
    #postEventxml()


#def download_zipfile():

