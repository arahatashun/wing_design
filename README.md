# 桁構造の設計

文字コードはutf-8に統一

## 改善すべき点

- 最適化において,ただ馬鹿みたいにfor文を回しまくると実行速度がおそすぎるので,
Cython,コンパイラ言語への移植などをする.

- リベットやボルトの設計の際,eやdなどに幾何的な拘束条件があるが,それをきちんとコード化していない.(これは嘘)

- 桁と金具の質量計算表がまだできてない?
