from multiprocessing import Process
from apipricescraper import *
from projecttoolbox import *
from scraper_mqtt_sql import *


def apiscraper(coinlist=['bitcoin', 'ripple', 'ethereum','binancecoin','dogecoin']):
    scraper=pricescraper(coinlist)
    scraper.scrapepricedata()

def listener():
    mqttsubber=mqtttosql()
    mqttsubber.listenscrapers(forever=False,verbose=True)
    mqttsubber.sqlupdater()

if __name__=='__main__':
    p2 = Process(target = listener)
    p2.start()
    time.sleep(2)
    p1 = Process(target = apiscraper)
    p1.start()