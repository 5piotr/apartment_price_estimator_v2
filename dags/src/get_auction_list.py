import os
import requests
import datetime
import time
from mysql import connector
from bs4 import BeautifulSoup
import pytz
import my_lib

def get_list():
    
    start = time.time()

    # flat_size = [[0,30],[30,35],[35,37],[37,40],[40,42],[42,45],[45,47],[47,50],
    #              [50,52],[52,55],[55,57],[57,60],[60,62],[62,65],[65,70],[70,75],
    #              [75,80],[80,90],[90,100],[100,120],[120,1000]]

    flat_size = [[0,15]]

    warsaw_tz = pytz.timezone('Europe/Warsaw') 
    timestamp = datetime.datetime.now(warsaw_tz).strftime('%Y-%m-%d_%H:%M:%S')
    auction_list = []

    # iterating over flat size ranges
    for mi,ma in flat_size:
        url = f'https://gratka.pl/nieruchomosci/mieszkania?powierzchnia-w-m2:min={mi}&powierzchnia-w-m2:max={ma}'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        pagination = soup.find_all(class_="pagination__input")

        # iterating over result pages
        for i in range(int(pagination[0]["max"])):
            url = f'https://gratka.pl/nieruchomosci/mieszkania?page={i+1}&powierzchnia-w-m2:min={mi}&powierzchnia-w-m2:max={ma}'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            links = soup.find_all(class_="teaserUnified")

            # iterating over apartment links
            for link in links:
                auction_list.append((timestamp, link['data-href']))

    insert_multiple_records = "INSERT INTO apt_links (date, link) VALUES (%s, %s)"

    with connector.connect(
        host = 'mysql_apt_db',
        user = 'piotr',
        password = os.environ['MYSQL_PASSWORD'],
        database = 'apt_db'
    ) as database:
        with database.cursor() as cursor:
            cursor.executemany(insert_multiple_records, auction_list)
            database.commit()

    print(f'PIOTR: mi={mi} ma={ma} complete, auction list has now {len(auction_list)} links')

    stop = time.time()
    print('PIOTR: task duration', my_lib.time_format(stop-start))

if __name__=='__main__':
    get_list()