"""stiffener implementation"""
# coding:utf-8
# Author: Shun Arahata
from scipy import interpolate
import numpy as np
import math
from unit_convert import ksi2Mpa, mm2inch, mpa2Ksi
from web import Web
import csv


class Stiffener(object):
    """Stiffener class."""

    def __init__(self, thickness, bs1_bottom, bs2_height, web):
        """Constructor.

        :param thickness: stiffener厚さ[mm]
        :param bs1_bottom:stiffener bottom長さ[mm]
        :param bs2_height:stiffener 高さ[mm]
        :param web:このstiffenerが属するwebのクラス
        """
        self.thickness = thickness
        self.bs1_bottom = bs1_bottom
        self.bs2_height = bs2_height
        self.E = ksi2Mpa(10.3 * 10 ** 3)
        self.web = web

    def get_inertia(self):
        """
        Inertia of Stiffener.[mm^4]
        """
        first = self.bs1_bottom * self.thickness ** 3
        second = self.thickness * self.bs2_height ** 3
        third = -self.thickness ** 4
        inertia = 1 / 3 * (first + second + third)
        return inertia

    def get_area(self):
        """ Stiffener断面積.[mm^2]"""
        return (self.bs1_bottom + self.bs2_height) * self.thickness - self.thickness ** 2

    def get_inertia_u(self, he):
        """
        Get Necessary Inertia.
        p11の表参照
        :param he: 桁フランジ断面重心距離[mm]
        """
        de = self.web.width_b  # webのwidth_bとdeは同一
        t = self.web.thickness  # webの厚さ[mm]
        x_value = he / de
        if x_value < 1.0:
            print("too small to get Inertia U in stiffener.py")
            return math.nan

        elif x_value <= 4.0:
            x = np.array([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
            y = np.array([0.1, 0.6, 1.5, 2.5, 3.7, 4.8, 6.2])
            f = interpolate.interp1d(x, y, kind='linear')
            fraction = f(x_value)
            denominator = he * t ** 3
            inertia_necessary = denominator * fraction
            return inertia_necessary

        else:
            print("too large to get Inertia U in stiffener.py")
            return math.nan

    def get_ms(self, he):
        """ MS (I>IU)
        :param he 桁フランジ断面重心距離
        """
        return self.get_inertia() / self.get_inertia_u(he) - 1

    def get_fcy(self):
        """ F_cy of 7075."""
        thickness_in_inch = mm2inch(self.thickness)

        if thickness_in_inch < 0.012:
            print("stiffener thickness too small")
            return math.nan

        elif thickness_in_inch < 0.040:
            return ksi2Mpa(61)

        elif thickness_in_inch < 0.062:
            return ksi2Mpa(62)  # 上と同じ

        elif thickness_in_inch < 0.187:
            return ksi2Mpa(64)

        elif thickness_in_inch < 0.249:
            return ksi2Mpa(65)
        else:
            print("too large in getFcy in stiffener py")
            return math.nan

    def get_x_of_graph(self):
        """Get X of Graph 7075(in page 12)."""

        b_per_t = self.bs1_bottom / self.thickness  # b/t
        x_value = np.sqrt(self.get_fcy() / self.E) * b_per_t
        return x_value

    def get_clippling_stress(self):
        """
        クリップリング応力を求める
        フランジと同じ
        :return Fcc:Fcc[MPa]
        """
        right_axis = self.get_x_of_graph()

        if right_axis < 0.1:
            return math.nan
        elif right_axis < 0.1 * 5 ** (27 / 33):
            # 直線部分
            left_axis = 0.5 * 2 ** (2.2 / 1.5)
        elif right_axis < 10:
            left_axis = 10 ** (-0.20761) * right_axis ** (-0.78427)
        else:
            return math.nan
        denom = mpa2Ksi(self.get_fcy())  # 分母
        # print("left",left_axis)
        # print("denom",denom)
        numer = left_axis * denom
        Fcc = ksi2Mpa(numer)

        return Fcc

    def make_row(self, writer, he):
        """
        :param writer:csv.writer()で取得されるもの
        :param he:桁フランジ断面重心距離
        """
        I_U = self.get_inertia_u(he)
        I = self.get_inertia()
        ms = self.get_ms(he)
        value = [self.web.thickness, self.thickness, self.web.width_b, he,
                 self.bs1_bottom, self.bs2_height, I, I_U, ms]
        writer.writerow(value)


def make_header(writer):
    """
    Make csv header.
    :param writer:csv.writer()で取得されるもの
    """
    header = ["web_thickness[mm]", "スティフナー厚さ", "スティフナー間隔",
              "he", "bs1底", "bs2高さ", "I", "I_U", "M.S"]
    writer.writerow(header)


def main():
    """Test Function."""
    web = Web(625, 1000, 3, 2.03)
    test = Stiffener(2.29, 22, 19.0, web)
    with open('stiffener_test.csv', 'a') as f:
        writer = csv.writer(f)
        make_header(writer)
        test.make_row(writer, 289)


if __name__ == '__main__':
    main()
