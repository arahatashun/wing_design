"""Flange(compression) implementation."""
# coding:utf-8
# Author: Hirotaka Kondo
import numpy as np
import math
from web import Web
from unit_convert import ksi2Mpa, mm2inch, mpa2Ksi
from flange import Flange
import csv


class CompressionFlange(Flange):
    """Flange (Compression) Class."""

    def __init__(self, thickness, b_bottom, b_height, web):
        """ Constructor.

        :param thickness:フランジ厚さ[mm]
        :param b_bottom:フランジ底長さ[mm]
        :param b_height:フランジ高さ[mm]
        :param web:このflangeが属するwebのクラス
        """
        super().__init__(thickness, b_bottom, b_height)
        self.E = ksi2Mpa(10.3 * 10 ** 3)
        self.web = web

    def get_fcy(self):
        """
        Get fcy of 7075.
        p.25の表参照
        :return:[MPa]
        """
        thickness_in_inch = mm2inch(self.thickness)

        if thickness_in_inch < 0.499:
            return ksi2Mpa(68)
        elif thickness_in_inch < 5.000:
            return ksi2Mpa(69)
        else:
            return math.nan

    def get_b_per_t(self):
        """Get b/t."""
        return self.b_bottom / self.thickness

    def get_x_of_graph(self):
        """X axis of graph."""
        return np.sqrt(self.get_fcy() / self.E) * self.get_b_per_t()

    def get_fcc(self):
        """
        7075 graph in page 12.
        :return:[MPa]
        """
        right_axis = self.get_x_of_graph()

        if right_axis < 0.1:
            return math.nan
        elif right_axis < 0.1 * 5 ** (27 / 33):
            # 一定部分
            # print("フランジ 直線部分")
            left_axis = 0.5 * 2 ** (2.2 / 1.5)
        elif right_axis < 10:
            left_axis = 10 ** (-0.20761) * right_axis ** (-0.78427)
        else:
            return math.nan
        lower = mpa2Ksi(self.get_fcy())  # 分母
        upper = left_axis * lower  # 分子
        fcc = ksi2Mpa(upper)

        return fcc

    def get_ms(self, momentum, h_e):
        """M.S. = Fcc/fc -1."""
        ms = self.get_fcc() / self.get_stress_force(momentum, h_e, self.web.thickness) - 1
        return ms

    def make_row(self, momentum, h_e):
        """
        :param momentum:前桁分担曲げモーメント[N*m]
        :param h_e:桁フランジ断面重心距離[mm]
        """
        fcc = self.get_fcc()
        ms = self.get_ms(momentum, h_e)
        p = self.get_axial_force(momentum, h_e)
        a = self.get_area(self.web.thickness)
        fc = self.get_stress_force(momentum, h_e, self.web.thickness)
        sqrt = self.get_x_of_graph()  # p12グラフのx軸の値
        value = [self.web.y_left, self.web.y_right, self.web.thickness, momentum, self.thickness,
                 self.b_bottom, self.b_height, p, a, fc, sqrt, fcc, ms]
        with open('results/compression_flange.csv', 'a', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(value)


def make_cflange_header():
    header = ["左端STA[mm]", "右端STA[mm]", "web thickness[mm]", "Momentum[N*m]",
              "$t_f$[mm]", "b bottom f1[mm]", "b height f2[mm]", "P[N]", "A[${mm}^2$]", "fc[MPa]", "√(Fcy/E)(b/t)",
              "$F_{cc}$[MPa]", "M.S."]
    with open('results/compression_flange.csv', 'a', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def main():
    """Test function."""
    web = Web(625, 1000, 3, 2.03)
    test = CompressionFlange(6.0, 34.5, 34.5, web)
    make_cflange_header()
    test.make_row(74623, 297)


if __name__ == '__main__':
    main()
