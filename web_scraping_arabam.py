import requests
from bs4 import BeautifulSoup
import pandas as pd
import gc
import time
from contextlib import contextmanager


@contextmanager
def timer(title):
    t0 = time.time()
    yield
    print("{} - done in {:.0f}s".format(title, time.time() - t0))


def Convert(a):
    it = iter(a)
    res_dct = dict(zip(it, it))
    return res_dct


with timer('arabam_com_scraping'):
    df1 = pd.DataFrame(columns=['İlan No:', 'İlan Tarihi:', 'Marka:', 'Seri:', 'Model:', 'Yıl:',
                                'Yakıt Tipi:', 'Vites Tipi:', 'Motor Hacmi:', 'Motor Gücü:',
                                'Kilometre:', 'Boya-değişen:', 'Takasa Uygun:', 'Kimden:'])
    url1 = "https://www.arabam.com/ikinci-el/otomobil"
    r1 = requests.get(url1)
    soup1 = BeautifulSoup(r1.content, 'html.parser')
    table2 = soup1.find("ul", attrs={"class": "category-facet-selection-wrapper scrollable"})
    markalar = table2.find_all("a", attrs={"class": "list-item"})
    for marka in markalar:

        car_Link1 = marka.get("href")
        car_Link1 = "https://www.arabam.com/" + car_Link1 + "?take=50&page=1"
        r = requests.get(car_Link1)
        soup = BeautifulSoup(r.content, 'html.parser')
        page_num = soup.find_all("div", attrs={"class": "listing-new-pagination cb tac mt16 pt16"})

        for i in page_num:
            page_n = int(i.text.split(" ")[1])
        if len(page_num) > 0:
            page_n = page_n
        else:
            page_n = 1

        print("marka {} toplam sayfa sayısı {}".format(marka.text, page_n))
        print("--" * 20)
        print("bitirilen sayfalar :", end=' ')

        for page in range(1, (page_n + 1)):
            print(page, end=' ')
            url = car_Link1 + "?take=50&page=" + str(page)

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
                    # car_r=requests.get(car_Link)
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
                except:
                    pass

        df1.to_csv('arabam_all_4subat.csv')
