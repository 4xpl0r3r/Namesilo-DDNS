import requests,time,sys,re
from bs4 import BeautifulSoup
import logging
# Run once every-boot

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT,filename='./ddns-log.txt')

session = requests.Session()
session.trust_env = False

API = 'https://www.namesilo.com/api/'

def get_rrid(key,superDomain,subDomain):
    r = session.get(API+'dnsListRecords',params={
        'version':'1',
        'type':'xml',
        'key':key,
        'domain':superDomain
    },timeout=10)
    soup = BeautifulSoup(r.text,'xml')
    return soup.find(text=subDomain+'.'+superDomain).parent.parent.record_id.string

def get_IP():
    r = session.get('http://cip.cc',headers={
        'User-Agent':'curl/7.64.1'
    },timeout=10)
    return re.search(r'((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)',r.text)[0]

def update_record(key,superDomain,subDomain,rrid,myIP):
    r = session.get(API+'dnsUpdateRecord',params={
        'version':'1',
        'type':'xml',
        'key':key,
        'domain':superDomain,
        'rrid':rrid,
        'rrhost':subDomain,
        'rrvalue': myIP,
        'rrttl':3600
    },timeout=10)
    if 'success' in r.text:
        logging.info("DNS updated successfully, IP: {}".format(myIP))
    else:
        logging.critical("DNS update failed! IP: {}".format(myIP))

if __name__ == "__main__":
    logging.debug("Program Started")
    key=sys.argv[1]
    domain=sys.argv[2]
    subDomain = domain[:domain.find('.')]
    superDomain = domain[domain.find('.')+1:]
    while True:
        try:
            myIP = get_IP()
            rrid = get_rrid(key,superDomain,subDomain)
            update_record(key,superDomain,subDomain,rrid,myIP)
        except BaseException:
            time.sleep(1)
        else:
            break
    logging.debug("Program Finished")
