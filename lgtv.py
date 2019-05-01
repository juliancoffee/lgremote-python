#!/usr/bin/env python3
#Full list of commands
#http://developer.lgappstv.com/TV_HELP/index.jsp?topic=%2Flge.tvsdk.references.book%2Fhtml%2FUDAP%2FUDAP%2FAnnex+A+Table+of+virtual+key+codes+on+remote+Controller.htm
import http.client
import xml.etree.ElementTree as etree
import socket
import re
import sys


lgtv = {}
dialogMsg =""
headers = {"Content-Type": "application/atom+xml"}
lgtv["pairingKey"] = "704129"


def getip():
    print("Searching Tv...")
    strngtoXmit =   'M-SEARCH * HTTP/1.1' + '\r\n' + \
                    'HOST: 239.255.255.250:1900'  + '\r\n' + \
                    'MAN: "ssdp:discover"'  + '\r\n' + \
                    'MX: 2'  + '\r\n' + \
                    'ST: urn:schemas-upnp-org:device:MediaRenderer:1'  + '\r\n' +  '\r\n'

    bytestoXmit = strngtoXmit.encode()
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.settimeout(3)
    found = False
    gotstr = 'notyet'
    i = 0
    ipaddress = None
    sock.sendto( bytestoXmit,  ('239.255.255.250', 1900 ) )
    
    while not found and i <= 5 and gotstr == 'notyet':
        try:
            gotbytes, addressport = sock.recvfrom(512)
            gotstr = gotbytes.decode()
        except:
            i += 1
            sock.sendto( bytestoXmit, ( '239.255.255.250', 1900 ) )
        if re.search('LG', gotstr):
            ipaddress, _ = addressport
            found = True
        else:
            gotstr = 'notyet'
        i += 1
    sock.close()
    if not found : 
        sys.exit("Lg TV not found")
    print("Tv found")
    print(ipaddress)
    return ipaddress


def displayKey():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    reqKey = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthKeyReq</type></auth>"
    conn.request("POST", "/roap/api/auth", reqKey, headers=headers)
    httpResponse = conn.getresponse()
    if httpResponse.reason != "OK" :
        sys.exit("Network error")
        print(httpResponse.reason)
    return httpResponse.reason


def getSessionid():
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    pairCmd = "<?xml version=\"1.0\" encoding=\"utf-8\"?><auth><type>AuthReq</type><value>" \
            + lgtv["pairingKey"] + "</value></auth>"
    conn.request("POST", "/roap/api/auth", pairCmd, headers=headers)
    httpResponse = conn.getresponse()
    print(httpResponse.reason)
    if httpResponse.reason != "OK" :
        return httpResponse.reason
    tree = etree.XML(httpResponse.read())
    return tree.find('session').text


def getPairingKey():
    displayKey()
    lgtv["pairingKey"] = input("enter key: ")

    
def handleCommand(cmdcode):
    conn = http.client.HTTPConnection( lgtv["ipaddress"], port=8080)
    cmdText = "<?xml version=\"1.0\" encoding=\"utf-8\"?><command>" \
                + "<name>HandleKeyInput</name><value>" \
                + cmdcode \
                + "</value></command>"
    conn.request("POST", "/roap/api/command", cmdText, headers=headers)
    httpResponse = conn.getresponse()

    
if __name__ == "__main__":
    lgtv["ipaddress"] = getip()
    theSessionid = getSessionid()
    while theSessionid == "Unauthorized" :
        getPairingKey()
        theSessionid = getSessionid()
    if len(theSessionid) < 8 : 
        sys.exit("Could not get Session Id: " + theSessionid)
    lgtv["session"] = theSessionid


    #displayKey()
    result = str(sys.argv[1])
    handleCommand(result)
