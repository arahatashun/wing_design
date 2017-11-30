# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from  scipy import interpolate

sm_df=pd.read_csv("SandM.csv")

def getHf(sta):
    """
    sta hoge における前桁高さHfを返す
    """
    x=np.array([625,5000])
    y=np.array([320,130])
    f = interpolate.interp1d(x, y,kind='linear')
    hf=f(sta)
    return hf

def getStiffnerCounts(rib_distance,stiffner_distance):
    """
    :param rib_distance:リブの間隙
    :param stiffner_distance:スティフナーの距離
    """
    stiffner_counts=rib_distance//stiffner_distance
    return stiffner_counts

def calcsta625():
    sta625=625
    y=sm_df.ix[0][1]
    Sf=sm_df.ix[0][4]
    #print("Sf",Sf)
    Mf=sm_df.ix[0][5]
    #print("Mf",Mf)
    #print(getHf(685))
    """
    以下パラメーターの設定
    """
    stiffner_thickness=2.03#mm
    stiffner_bs1=65
    stiffner_bs2=20
    web_thickness=18
    web_distance=60
    hf=getHf(sta625+web_distance)
    print(hf)






if __name__ == '__main__':
    calcsta625()
