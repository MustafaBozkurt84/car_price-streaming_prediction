import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import gc
import time
from contextlib import contextmanager
df1 = pd.DataFrame()
def Convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct
while True:
    for page in range(1, 6):
        print(page, end=' ')
        url = "https://www.arabam.com/ikinci-el/otomobil-sahibinden?take=50&page=" + str(page)


        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        table = soup.find("table", attrs={"class": "table listing-table w100 border-grey2"})
        cars = table.find_all("a", attrs={"class": "listing-text-new word-break val-middle color-black2018"})
        for car in cars:
            try:
                car_link = []
                car_Link = car.get("href")
                car_Link = "https://www.arabam.com/" + car_Link
                car_link.append(car_Link)

                soup = BeautifulSoup(requests.get(car_Link).content, 'html.parser')
                table1 = soup.find_all("span", attrs={"class": "bli-particle"})
                att = []

                for i in table1:
                    att.append(i.text)
                price = soup.find("div", attrs={"class": "mb8"}).text
                aciklama = soup.find("div",
                                     attrs={"class": "overflow-wrap-controller tac horizontal-double-padder"}).text
                boya_degisen = soup.find("div", attrs={"class": "cf p20"}).text

                data = Convert(att)
                df = pd.DataFrame.from_dict(data, orient="index").T
                df["car_link:"] = car_link
                df["price"] = price
                df["aciklama"] = aciklama
                df["boya_degisen"] = boya_degisen
                df1 = pd.concat([df1, df], ignore_index=True, join="outer")

                df1 = df1.loc[:, ['İlan No:', 'İlan Tarihi:', 'Marka:', 'Seri:', 'Model:', 'Yıl:', 'Yakıt Tipi:',
                                  'Vites Tipi:', 'Motor Hacmi:', 'Motor Gücü:', "Kilometre:", 'car_link:', "price",
                                  "boya_degisen", "aciklama"]]
                df1.drop_duplicates(axis=0,inplace=True,keep="last")


                df1.to_csv('arabam_stream_.csv', sep=',', index=False)


            except:
                pass
    time.sleep(300)
