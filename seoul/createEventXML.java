import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.io.FileWriter;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.text.DecimalFormat;
import java.util.Calendar;
import java.util.Date;
import java.text.DateFormat;
import java.util.TimeZone;
import java.text.SimpleDateFormat;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.InputSource;

public class createEventXML {

    public static void createEventData(String fileName, Document doc, String busLineID) throws IOException {
        // Length of itemList
        int len = doc.getElementsByTagName("itemList").getLength();
        DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
        TimeZone tz;
        tz = TimeZone.getTimeZone("Asia/Seoul");
        dateFormat.setTimeZone(tz);
        Date now = new Date();
        String time = dateFormat.format(now) + "+09:00";
        StringBuilder sb = new StringBuilder("");

        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n");
        sb.append("<!DOCTYPE project>\n");
        sb.append(
                "<epcis:EPCISDocument xmlns:epcis=\"urn:epcglobal:epcis:xsd:1\" xmlns:arrival=\"http://ns.example.com/epcis\"\n");
        sb.append("     creationDate=\"2005-07-11T11:30:47.0Z\" schemaVersion=\"1.2\">\n");

        sb.append("     <EPCISBody>\n");
        sb.append("         <EventList>\n");

        for (int i = 0; i < len; i++) {
            String arsId = doc.getElementsByTagName("arsId").item(i).getTextContent();
            String exps1 = doc.getElementsByTagName("exps1").item(i).getTextContent();
            String stNm = doc.getElementsByTagName("stNm").item(i).getTextContent();
            String plainNo1 = doc.getElementsByTagName("plainNo1").item(i).getTextContent();
            stNm = stNm.replaceAll("&","");

            sb.append("             <ObjectEvent>\n");
            sb.append(String.format("                 <eventTime>%s</eventTime>\n", time));
            sb.append("                 <eventTimeZoneOffset>+09:00</eventTimeZoneOffset>\n");
            sb.append("                 <epcList>\n");
            sb.append(
                    "                     <epc>urn:epc:id:sgln:880002695.101." + arsId + "|" + busLineID + "</epc>\n");
            sb.append("                 </epcList>\n");
            sb.append("                 <action>OBSERVE</action>\n");
            sb.append("                 <bizStep>urn:gs1:epcisapp:bus:btt:arriving</bizStep>\n");
            sb.append("                 <arrival:stopID>urn:ecp:id:sgln:880002695.100." + arsId + "</arrival:stopID>\n");
            sb.append("                 <arrival:stopName>" + stNm + "</arrival:stopName>\n");
            sb.append("                 <arrival:lineID>urn:ecp:id:gsrn:880002695.100." + busLineID + "</arrival:lineID>\n");
            sb.append("                 <arrival:busID>" + plainNo1 + "</arrival:busID>\n");
            sb.append("                 <arrival:estimatedTime>" + exps1 + "</arrival:estimatedTime>\n");
            sb.append("             </ObjectEvent>\n");
        }
        sb.append("         </EventList>\n");
        sb.append("     </EPCISBody>\n");
        sb.append("</epcis:EPCISDocument>\n");

        System.out.println(sb.toString());
        System.out.printf("%s successfully downloaded.", fileName);
        System.out.println(time);
        BufferedWriter bw = new BufferedWriter(new FileWriter(fileName));
        bw.write(sb.toString());
        bw.close();
    }

    public static void main(String[] args) throws IOException {

        try{
            // busLineID = 3412, busRouteId = 100100224
            String busLineID = "3412";
            String busRouteId = "100100224";
            String key = "wl%2F6H6OFvcb73eW4QW6Ci8Ag47%2FVjULPbi5MOjqtcQch6iKhSV95WrEBWEiQgk8vcPNcoG5q79qnQWjByR3j9Q%3D%3D";
            
            StringBuilder urlBuilder = new StringBuilder("http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRouteAll"); /*URL*/
            urlBuilder.append("?" + URLEncoder.encode("ServiceKey","UTF-8") + "=" + key); /*Service Key*/
            urlBuilder.append("&" + URLEncoder.encode("busRouteId","UTF-8") + "=" + URLEncoder.encode(busRouteId, "UTF-8"));

            URL url = new URL(urlBuilder.toString());
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Content-type", "application/json");
            System.out.println("Response code: " + conn.getResponseCode());

            BufferedReader rd;
            if(conn.getResponseCode() >= 200 && conn.getResponseCode() <= 300) {
                rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            } else {
                rd = new BufferedReader(new InputStreamReader(conn.getErrorStream()));
            }
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = rd.readLine()) != null) {
                sb.append(line);
            }

            rd.close();
            conn.disconnect();

            DocumentBuilder builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            InputSource src = new InputSource();
            src.setCharacterStream(new StringReader(sb.toString()));
            Document doc = builder.parse(src);

            // Create event data into XML
            String fileName = "./created_event.xml";
            createEventData(fileName, doc, busLineID);
            // postXMLData(fileName);

        }catch(Exception e){
            System.out.println(e.getMessage());
        }
    }
}
