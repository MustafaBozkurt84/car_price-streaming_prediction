import streamlit as st
import pandas as pd
import re
import numpy as np
import pickle
import os

pickle_in = open('class_obj.pkl', 'rb')
class_obj = pickle.load(pickle_in)
pickle_in = open('encode_list.pkl', 'rb')
encode_list = pickle.load(pickle_in)
pickle_in = open('col_after_endoded_all.pkl', 'rb')
col_after_endoded_all = pickle.load(pickle_in)
df = pd.read_csv("arabam_stream_.csv")
df.dropna(inplace=True,axis=0)
df.drop_duplicates(subset=['İlan No:'], keep='last', inplace=True)


#df = df.drop(columns=["Unnamed: 0"],axis=1)
df=df.reset_index(drop=True)
df.columns = ['ilan No', 'ilan Tarihi', 'marka', 'seri', 'model',
       'yıl', 'yakıt tipi', 'vites Tipi', 'motor hacmi', 'motor gücü',
       'kilometre', 'car_link', 'price', 'boya_degisen', 'aciklama']
df["marka_model"] = df["marka"]+df["seri"]+df["model"]
modeldf=df.loc[:,"marka"]
seridf=df.loc[:,"seri"]
kmdf=df.loc[:,"kilometre"]
dffilter=df
df.drop(columns=["marka","seri","model"],inplace=True,axis =1)


df=df.reset_index(drop=True)
for col in ["kilometre","price"]:
    for i in range(0,len(df[col])):
        df[col][i] = "".join(re.sub(r'[^\w]|km| |TL', '',df[col][i]))
    df[col]=df[col].astype(int)
df.drop(["motor gücü","motor hacmi"],axis=1,inplace=True)
df.drop(["ilan No","ilan Tarihi"],axis=1,inplace=True)
y = df.loc[:,"price"]
marka_model=df["marka_model"]


def feature_engineering_word(col, words):
    for key in words:
        df[col + key] = np.zeros(df.shape[0])

        for i in range(0, len(df[col])):
            try:
                if df[col][i].split().index(key) > 1:
                    df[col + key][i] = df[col][i].split().index(key)
                else:
                    df[col + key][i] = 0


            except:

                df[col + key][i] = -1


feature_engineering_word("boya_degisen",["Değişmiş","Boyanmış","Orijinal"])
def feature_engineering_word1(col,words):
    for key in words:
        df[col+key]=np.zeros(df.shape[0])

        for i in range(0,len(df[col])):
            try:
                if  df[col][i].split().index(key)>0:
                    df[col+key][i]= df[col][i].split().index(key)
                else:
                    df[col+key][i]=0


            except:

                df[col+key][i]=-1
feature_engineering_word1("aciklama",["FULL","HASARLI","HATASIZ","AĞIR HASAR PERT KAYDI YOKTUR."])
df.drop(["aciklama","boya_degisen","car_link"],axis=1,inplace=True)
df = df.reset_index(drop=True)


def allonehotencoding_test(df):
    for i in encode_list:
        try:
            for categories in df[i]:
                df[i] = np.where(df[i] == categories, 1, 0)
        except:
            df[i] = np.where(False, 1, 0)

    return df


allonehotencoding_test(df)
for i in col_after_endoded_all:
    if i not in df.columns:
        df[i] = np.where(False, 1, 0)

df = df.loc[:, col_after_endoded_all]
df = df.drop(df.select_dtypes("object").columns, axis=1)

for i in df.columns:
    if (np.dtype(df[i]) == "object"):
        df = df.drop([i], axis=1)

X = df
y_pred = class_obj.predict(X)
table=pd.DataFrame()
table["model"]=modeldf
table["seri"]=seridf
table["marka model"] = marka_model
table["kilometre"]=kmdf
table["yıl"]=df["yıl"]
table["tahmin"] = y_pred
table["gercek deger"] = y
table["link"] = dffilter.loc[:,'car_link']

for i in range(0,len(table["gercek deger"])):
    if table["gercek deger"][i] > table["tahmin"][i]:
        table.drop(index=i,axis=0,inplace=True)
table.reset_index(drop=True,inplace=True)
markalar=list(table["model"].value_counts().index)
marka_ = st.selectbox("Marka Seçin",(markalar))
seriler = list(table[table["model"]==marka_]["seri"].value_counts().index)
serii = st.selectbox("Model Seçin",(seriler))
table = table[(table["model"]==marka_)&(table["seri"]==serii)]
table.drop(["model","seri"],axis=1,inplace=True)
st.table(table)

#os.system("python app_scraping-stream.py")