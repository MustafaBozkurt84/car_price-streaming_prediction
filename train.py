
import pandas as pd
import numpy as np
import re
import pickle
import xgboost
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
df = pd.read_csv("arabam_all_4subat.csv")


df = df.drop(columns=["Unnamed: 0"] ,axis=1)
df =df.reset_index(drop=True)
df=df.iloc[:,0:19]
df.drop(["Takasa Uygun:","Kimden:","Boya-değişen:","Motor Hacmi:","Motor Gücü:",' Takasa Uygun Değil   '],axis=1,inplace=True)

df.columns = ['ilan No', 'ilan Tarihi', 'marka', 'seri', 'model',
              'yıl', 'yakıt tipi', 'vites Tipi','kilometre', 'car_link', 'price', 'aciklama', 'boya_degisen']

df["marka_model"] = df["marka" ] +df["seri" ] +df["model"]

df.drop(columns=["marka" ,"seri" ,"model"] ,inplace=True ,axis =1)

df.dropna(inplace=True ,axis=0)
df =df.reset_index(drop=True)
for col in ["kilometre" ,"price"]:
    for i in range(0 ,len(df[col])):

        df[col][i] = "".join(re.sub(r'[^\w]|km|USD|TL', '' ,df[col][i]))


    df[col ] =df[col].astype(int)



df.drop(["ilan No" ,"ilan Tarihi"] ,axis=1 ,inplace=True)
print(df.head())
def feature_engineering_word(col ,words):
    for key in words:
        df[col +key ] =np.zeros(df.shape[0])

        for i in range(0 ,len(df[col])):
            try:
                if  df[col][i].split().index(key ) >1:
                    df[col +key][i ]= df[col][i].split().index(key)
                else:
                    df[col +key][i ] =0


            except:

                df[col +key][i ] =-1




feature_engineering_word("boya_degisen" ,["Değişmiş" ,"Boyanmış" ,"Orijinal"])

def feature_engineering_word1(col ,words):
    for key in words:
        df[col +key ] =np.zeros(df.shape[0])

        for i in range(0 ,len(df[col])):
            try:
                if  df[col][i].split().index(key ) >0:
                    df[col +key][i ]= df[col][i].split().index(key)
                else:
                    df[col +key][i ] =0


            except:

                df[col +key][i ] =-1


feature_engineering_word1("aciklama" ,["FULL" ,"HASARLI" ,"HATASIZ" ,"AĞIR HASAR PERT KAYDI YOKTUR."])


df.drop(["aciklama" ,"boya_degisen" ,"car_link"] ,axis=1 ,inplace=True)

df =df.reset_index(drop=True)


target_column ="price"
y = df.loc[:, target_column]
X = df.drop([target_column], axis=1)
df = X
encode_list = []
def allonehotencoding(df):

    for i in X.columns:
        if (np.dtype(df[i]) == "object"):
            for categories in (df[i].value_counts().sort_values(ascending=False).index):
                df[i + categories] = np.where(df[i] == categories, 1, 0)
                encode_list.append(i  + categories)

    return df ,encode_list
num_cat_col =len(df.select_dtypes(include=["object"]).columns)
allonehotencoding(df)

for i in df.columns:
    if (np.dtype(df[i]) == "object"):
        df = df.drop([i], axis=1)
col_after_endoded_all =df.columns


from sklearn.ensemble import RandomForestRegressor
#class_obj =RandomForestRegressor()
class_obj=xgboost.XGBRegressor()
#class_obj = LinearRegression()
#class_obj  =KNeighborsRegressor()

from sklearn.model_selection import cross_val_score ,KFold, GroupKFold
from sklearn.model_selection import train_test_split
fold = KFold(n_splits=5)
#score = cross_val_score(class_obj ,df ,y ,cv = fold ,scoring="neg_root_mean_squared_error")
#print(f"score : {score.mean()}")

class_obj.fit(df ,y)

def pickle_all(key ,value):
    pickle_out = open(key +".pkl", "wb")
    pickle.dump(value, pickle_out)
    pickle_out.close()
pickle_all("class_obj" ,class_obj)
pickle_all("class_obj" ,class_obj)
pickle_all("encode_list" ,encode_list)
pickle_all("col_after_endoded_all" ,col_after_endoded_all)
#score.mean()




