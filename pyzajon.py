import json
import time
import re
from datetime import datetime
from itertools import takewhile
from zabbix.api import ZabbixAPI

# groupid=932 - solaris 11 zones
# groupid=930 - solaris LDOMS
# groupid=931 - solaris LDOMS
# groupid=929 - solaris hosts
# hostid = 17923 swan06

zapi = ZabbixAPI ( url='http://test-zabbix/zabbix' , user='tem_user' , password='1234' )

z11hosts = zapi.host.get ( groupids=[ 930 ] , output=('name' , 'hostid') )

# Regexps for key search
r1 = re.compile ( 'item1\\.property\\[.*?\\,property\\]" )
r2 = re.compile ( 'item2\\.property\\[.*?\\,property\\]' )
r3 = re.compile ( 'item3\\.property\\[.*?\\,property\\]' )
r4 = re.compile ( '' )

# Get ldomids,ldomnames,and query zabbix for some key for this ldoms
ldomids = [ d.values ()[ 0 ] for d in z11hosts ]
ldomnames = [ d.values ()[ 1 ] for d in z11hosts ]


# cast state,hname,zname dict for zone
ldms = {}
ldmlist = {}

#initialize lists to hold
vmstates = [ ]
list1 = [ ]
list2 = [ ]
list3 = [ ]

# function to get hostname from hostid
def gethost(hid):
    for d in z11hosts:
        if d[ 'hostid' ] == str ( hid ):
            return d[ 'name' ]


def zoneget(hid):
    zstate = zapi.item.get ( hostids=hid , search={"key_": "clerk.property"} ,
                             output=('key_' , 'name' , 'hostid' , 'lastvalue') )
    return zstate

# construct dict of ldoms-zones-names-statuses
for l in ldomids:
    ldomo = gethost ( l )
    zstate = zoneget ( l )
    #print json.dumps(zstate, sort_keys=True, indent=4, separators=(',', ': '))
    list1 = [ ]
    vms = {}
    for i in zstate:
        for v in i.values ():
            if r3.match ( v ):
                list1.append ( i[ 'lastvalue' ] )
    for i in list1:
        r4 = re.compile ( 'clerk\\.property\\[' + i + '\\,.*?\\]' )
        r5 = re.compile ( 'clerk\\.property\\[' + i + '\\,state\\]' )
        r6 = re.compile ( 'clerk\\.property\\[' + i + '\\,hostname\\]' )
        vms[ i ] = {}
        for j in zstate:
            for v in j.values ():
                if r5.match ( v ):
                    vms[ i ][ 'zonestate:' ] = (j[ 'lastvalue' ])
                if r6.match ( v ):
                    vms[ i ][ 'hostname:' ] = (j[ 'lastvalue' ])
    ldms[ ldomo ] = vms
print json.dumps ( ldms , sort_keys=True , indent=4 , separators=(',' , ': ') )
