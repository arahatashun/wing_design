"""SとMを計算"""
# -*- coding: utf-8 -*-
# Author: Hirotaka Kondo
import numpy as np
from scipy import interpolate
from scipy.integrate import quad
import csv
import matplotlib.pyplot as plt

C_L = 1.4  # 最大揚力係数
C_ROOT = 2.13 * 1000  # rootのchord長[mm]
C_TIP = 1.07 * 1000  # tipのroot長[mm]
ALPHA_F = np.deg2rad(14.5)  # [rad]
W = 1500 * 9.8  # 自重[N]
N_Z = 6  # 最大荷重倍数
HALF_SPAN = 5000  # [mm]

Y_REP_FOR_C = np.array(
    [0, 1000, 2000, 3000, 4000, 4500, 4750, 4875, 5000])  # [mm]
C_LA_REP = np.array([0.835, 1.021, 1.095, 1.089, 0.993,
                     0.833, 0.662, 0.548, 0])  # [no dim]
C_LB_REP = np.array([0.049, 0.044, 0.005, -0.033, -
0.062, -0.067, -0.056, -0.043, 0])  # [no dim]
C_D_REP = np.array([0.1679, 0.1303, 0.1105, 0.1065, 0.1163,
                    0.1314, 0.1354, 0.1302, 0])  # [no dim]

CHORD_ARRAY = [C_ROOT, C_TIP]  # [mm]
STA_FOR_CHORD = [0, HALF_SPAN]  # [mm]

Y_REP_FOR_W = np.array(
    [625, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750,
     5000])  # [mm]
Y_DISTANCE_FOR_W = np.array([Y_REP_FOR_W[i + 1] - Y_REP_FOR_W[i]
                             for i in range(0, len(Y_REP_FOR_W) - 1)])
W_REP = 9.8 * np.array([15, 12, 11, 7, 6, 5, 4, 4, 3,
                        4, 4, 3, 3, 3, 2, 2, 2, 1])  # [N]
RHO_REP = W_REP / Y_DISTANCE_FOR_W
RHO_REP = np.append(RHO_REP, [0])  # y=5000での線密度を0として便宜上追加

ETA_A = 4039.29  # get_etaaで計算済み,計算モデルが変わったらget_etaa()で計算し直すこと


def _get_cla(y):
    """
    yに於けるclaを計算
    :param y:
    :return: cla[no dim]
    """
    f = interpolate.interp1d(Y_REP_FOR_C, C_LA_REP, kind='linear')
    return f(y)


def _get_clb(y):
    """
    yに於けるclbを計算
    :param y:
    :return: clb[no dim]
    """
    f = interpolate.interp1d(Y_REP_FOR_C, C_LB_REP, kind='linear')
    return f(y)


def _get_cd(y):
    """
    yに於けるcdを計算
    :param y:
    :return: cd[no dim]
    """
    f = interpolate.interp1d(Y_REP_FOR_C, C_D_REP, kind='linear')
    return f(y)


def _get_cl(y):
    """
    yに於けるclを計算
    :param y:
    :return: cl[no dim]
    """
    return C_L * _get_cla(y) + _get_clb(y)


def _get_cz(y):
    """
    yに於けるczを計算
    :param y:
    :return: cz[no dim]
    """
    return _get_cl(y) * np.cos(ALPHA_F) + _get_cd(y) * np.sin(ALPHA_F)


def _get_chord(y):
    """
    yに於けるchord長を計算
    :param y:
    :return: chord[mm]
    """
    f = interpolate.interp1d(STA_FOR_CHORD, CHORD_ARRAY, kind='linear')
    return f(y)


def _get_ccz(y):
    """
    yに於けるc*czを計算
    :param y:
    :return: c*cz[mm]
    """
    return _get_chord(y) * _get_cz(y)


"""
def get_etaa():
    integral = quad(get_ccz, 0, HALF_SPAN)
    return 1 / 2 * N_Z * W / (integral[0] / 1000 / 1000)  # 単位をmに揃える
"""


def _get_sa(y_w, limit_div=50):
    """
    y_wに於けるsaを計算
    :param y_w:
    :param limit_div:
    :return: sa[N]
    """
    integral = quad(_get_ccz, y_w, HALF_SPAN, limit=limit_div)
    return ETA_A * integral[0] / 1000 / 1000  # 単位をmに揃える


def _get_rho(y):
    """
    yに於ける荷重分布rho[N/mm]を計算
    :param y:
    :return:rho[N/mm]
    """
    f = interpolate.interp1d(Y_REP_FOR_W, RHO_REP, kind='zero')
    return f(y)


def _get_si(y_w, limit_div=50):
    """
    y_wに於ける慣性力s1を計算
    :param y_w:
    :param limit_div:
    :return: s1[N]
    """
    integral = quad(_get_rho, y_w, HALF_SPAN, limit=limit_div)
    return N_Z * integral[0]  # 単位をmに揃える


def get_s(y_w, limit_div=50):
    """
    y_wにおけるせん断力を計算
    :param y_w:
    :param limit_div:
    :return:
    """
    s = _get_sa(y_w, limit_div) - _get_si(y_w, limit_div)
    return s


def get_sf(y_w, limit_div=50):
    """
    y_wにおける前桁負担分せん断力を計算
    :param y_w:
    :param limit_div:
    :return:
    """
    return get_s(y_w, limit_div) * 1.5 * 0.8


def get_m(y_w, limit_div=50):
    """
    y_wに於ける曲げモーメントMを計算
    :param y_w:
    :param limit_div: quadによる積分計算の分割幅を調整(defaultは50,大きくすると計算時間長くなる)
    :return:
    """
    integral = quad(lambda yp, y: (ETA_A * _get_ccz(yp) / 1000 - N_Z * _get_rho(yp) * 1000) * (yp - y) / 1000, y_w,
                    HALF_SPAN, args=y_w, limit=limit_div)
    return integral[0] / 1000


def get_mf(y_w, limit_div=50):
    """
    y_wに於ける前桁負担分曲げモーメントMfを計算
    :param y_w:
    :param limit_div: quadによる積分計算の分割幅を調整(defaultは50,大きくすると計算時間長くなる)
    :return:
    """
    return get_m(y_w, limit_div) * 1.5 * 0.8


def _get_csv():
    """
    全部の値をSTA625からSTA5000まで1刻みに出力
    :return:
    """
    with open('sm_graph.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["y[mm]", "cla", "clb", "cd", "cl", "cz", "C[mm]", "C*cz[mm]", 'w[kg/mm]',
             'sa[N]', 'si[N]',
             'S[N]', 'M[N*m]'])
        for i in range(625, 5001):
            writer.writerow(
                [i, _get_cla(i), _get_clb(i), _get_cd(i), _get_cl(i), _get_cz(i), _get_chord(i), _get_ccz(i),
                 _get_rho(i),
                 _get_sa(i, 1), _get_si(i, 1), get_s(i, 1), get_m(i, 1)])


def _make_table():
    """table 作成."""
    LEFT_ARRAY = [625, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500]
    with open('sm_table.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["y[mm]", "cla", "clb", "cd", "cl", "cz", "C[mm]", "C*cz[mm]", 'w[kg/mm]',
             'sa[N]', 'si[N]',
             'S[N]', 'M[N*m]', 'Sf[N]', 'Mf[N*m]'])
        for i in LEFT_ARRAY:
            writer.writerow(
                [i, _get_cla(i), _get_clb(i), _get_cd(i), _get_cl(i), _get_cz(i), _get_chord(i), _get_ccz(i),
                 _get_rho(i),
                 _get_sa(i, 1), _get_si(i, 1), get_s(i, 1), get_m(i, 1), get_sf(i, 1), get_mf(i, 1)])


def plot_sm():
    y_list = np.array([i for i in range(625, 5001)])
    s, m, s_rep, m_rep, y_rep = [], [], [], [], []
    for i in y_list:
        s.append(get_s(i, 1))
        m.append(get_m(i, 1))
        print(i, s[-1], m[-1])
        if i == 625 or i % 500 == 0:
            s_rep.append(s[-1])
            m_rep.append(m[-1])
            y_rep.append(i)
    plt.plot(y_rep, s_rep, marker='o', label='S[N]', ls='None', color='b')
    plt.plot(y_rep, m_rep, marker='^', label='M[N*m]', ls='None', color='g')
    plt.plot(y_list, s, color='b')
    plt.plot(y_list, m, color='g')
    plt.legend()
    plt.xlim(625, 5000)
    plt.ylim(0, 70000)
    plt.xticks([625, 1000, 2000, 3000, 4000, 5000])
    plt.xlabel('STA')
    plt.ylabel('S[N] & M[N*m]')
    plt.show()


if __name__ == "__main__":
    # _make_table()
    _get_csv()
    # for i in range(625, 5000):
    # print("M at STA{0} is {1} [N*m]".format(i, get_m(i, 1)))
    # plot_sm()
