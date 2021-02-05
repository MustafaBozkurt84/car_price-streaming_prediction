import streamlit as st
import pandas as pd
import re
import numpy as np
import pickle
import os
html_temp = """
    <div style="background:#025246 ;padding:10px">
    <h2 style="color:white;text-align:center;"> Arac Fiyat Tahmin Uygulaması</h2>
    </div>
    """
page11 =st.sidebar.radio("Sayfalar", ("Fırsatlar","Arac fiyat tahmini"))
st.markdown(html_temp, unsafe_allow_html = True)
pickle_in = open('class_obj.pkl', 'rb')
class_obj = pickle.load(pickle_in)
pickle_in = open('encode_list.pkl', 'rb')
encode_list = pickle.load(pickle_in)
pickle_in = open('col_after_endoded_all.pkl', 'rb')
col_after_endoded_all = pickle.load(pickle_in)
os.system("git clone https://github.com/MustafaBozkurt84/streamarabamCOM.git")
df = pd.read_csv("./streamarabamCOM/arabam_stream_.csv")
df.dropna(inplace=True,axis=0)
df.drop_duplicates(subset=['İlan No:'], keep='last', inplace=True)

if page11=="Fırsatlar":
    #df = df.drop(columns=["Unnamed: 0"],axis=1)
    df=df.reset_index(drop=True)
    df.columns = ['ilan No', 'ilan Tarihi', 'marka', 'seri', 'model',
           'yıl', 'yakıt tipi', 'vites Tipi', 'motor hacmi', 'motor gücü',
           'kilometre', 'car_link', 'price', 'boya_degisen', 'aciklama']

    modeldf=df.loc[:,"marka"]
    seridf=df.loc[:,"seri"]
    kmdf=df.loc[:,"kilometre"]
    dffilter=df
    dftest=df
    df["marka_model"] = df["marka"]+df["seri"]+df["model"]
    df.drop(columns=["marka","seri","model"],inplace=True,axis =1)
    df_len_min=df.shape[0]-500

    df=df.iloc[df_len_min:,:]
    st.write(df.shape)
    df=df.reset_index(drop=True)
    for col in ["kilometre","price"]:
        for i in range(0,len(df[col])):
            df[col][i] = "".join(re.sub(r'[^\w]|km|USD|TL', '' ,df[col][i]))
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
    y_predd=[]
    for i in y_pred:
        y_predd.append(round(i))
    table=pd.DataFrame()
    table["model"]=modeldf
    table["seri"]=seridf
    table["marka model"] = marka_model
    table["kilometre"]=kmdf
    table["yıl"]=df["yıl"]
    table["tahmin"] = y_predd
    table["gercek deger"] = y
    table["link"] = dffilter.loc[:,'car_link']

    for i in range(0,len(table["gercek deger"])):
        if table["gercek deger"][i] > table["tahmin"][i]:
            table.drop(index=i,axis=0,inplace=True)
    table.reset_index(drop=True,inplace=True)
    st.write(table.shape)
    markalar=list(table["model"].value_counts().index)
    marka_ = st.selectbox("Marka Seçin",(markalar))
    st.cache()
    seriler = list(table[table["model"]==marka_]["seri"].value_counts().index)
    serii = st.selectbox("Model Seçin",(seriler))
    table = table[(table["model"]==marka_)&(table["seri"]==serii)]
    table.drop(["model","seri"],axis=1,inplace=True)

    st.table(table.set_index("marka model"))

    #os.system("python app_scraping-stream.py")
if page11=="Arac fiyat tahmini":
    df = pd.read_csv("arabam_all_4subat.csv")

    df=df.loc[:,["Marka:","Seri:","Model:","Yıl:","Vites Tipi:","Kilometre:","aciklama","boya_degisen","Yakıt Tipi:"]]

    marka = st.selectbox("Marka",(list(df["Marka:"].value_counts().index)))
    Seri=st.selectbox("Seri",(list(df[df["Marka:"]==marka]["Seri:"].value_counts().index)))
    model = st.selectbox("Model",(list(df[(df["Marka:"]==marka) & (df["Seri:"]==Seri)]["Model:"].value_counts().index)))
    yakıt = st.selectbox("Model",(list(df[(df["Marka:"]==marka) & (df["Seri:"]==Seri) &(df["Model:"]==model)]["Yakıt Tipi:"].value_counts().index)))
    vites = st.selectbox("Model",(list(df[(df["Marka:"]==marka) & (df["Seri:"]==Seri) &(df["Model:"]==model)&(df["Yakıt Tipi:"]==yakıt)]["Vites Tipi:"].value_counts().index)))
    yıl =st.text_input("Yıl",key=int,value=2020)
    kilometre=st.text_input("Kilometre",key=int,value=0)
    aciklama = st.text_input("Acıklama")
    boya_degisen = st.text_input("Boya Degisen")
    del df
    if st.button("Predict"):
        dftest = pd.DataFrame()
        dftest["marka"]=[marka]
        dftest["seri"] = [Seri]
        dftest["model"]=[model]
        dftest["yakıt"]=[yakıt]
        dftest["yıl"]=[int(yıl)]
        dftest["kilometre"]=[int(kilometre)]
        dftest["aciklama"]=[aciklama]
        dftest["boya-degisen"]=[boya_degisen]
        dftest["yakıt tipi"]=[yakıt]
        dftest["vites Tipi"]=[vites]


        dftest["marka_model"] = dftest["marka"] + dftest["seri"] + dftest["model"]

        dftest.drop(["marka","model","seri"],axis=1,inplace=True)
        arac_bilgileri=dftest

        def feature_engineering_word(col, words,df):
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


        feature_engineering_word("boya-degisen", ["Değişmiş", "Boyanmış", "Orijinal"],dftest)


        def feature_engineering_word1(col, words,df):
            for key in words:
                df[col + key] = np.zeros(df.shape[0])

                for i in range(0, len(df[col])):
                    try:
                        if df[col][i].split().index(key) > 0:
                            df[col + key][i] = df[col][i].split().index(key)
                        else:
                            df[col + key][i] = 0


                    except:

                        df[col + key][i] = -1


        feature_engineering_word1("aciklama", ["FULL", "HASARLI", "HATASIZ", "AĞIR HASAR PERT KAYDI YOKTUR."],dftest)

        dftest.drop(["aciklama","boya-degisen"],axis=1,inplace=True)
        def allonehotencoding_test(df):
            for i in encode_list:
                try:
                    for categories in df[i]:
                        df[i] = np.where(df[i] == categories, 1, 0)
                except:
                    df[i] = np.where(False, 1, 0)

            return df


        allonehotencoding_test(dftest)

        for i in col_after_endoded_all:
            if i not in dftest.columns:
                dftest[i] = np.where(False, 1, 0)


        dftest = dftest.loc[:, col_after_endoded_all]





        X = dftest
        y_pred = class_obj.predict(dftest)
        html_temp1 = f"""
            <div style="background:#025246 ;padding:10px">
            <h2 style="color:white;text-align:center;"> ARACINIZIN TAHMİNİ FİYATI:  {round(y_pred[0])} TL</h2>
            </div>
            """
        html_temp2 = f"""
                    <div style="background:#025246 ;padding:10px">
                    <h2 style="color:white;text-align:left;"> {arac_bilgileri["marka_model"][0]} </h2>
                    </div>
                    """
        html_temp3 = f"""
                            <div style="background:#025246 ;padding:10px">
                            <h2 style="color:white;text-align:left;">{arac_bilgileri["yıl"][0]} model / {vites} vites / {yakıt}</h2>
                            </div>
                            """
        st.markdown(html_temp2, unsafe_allow_html=True)
        st.markdown(html_temp3, unsafe_allow_html=True)
        st.markdown(html_temp1, unsafe_allow_html=True)






