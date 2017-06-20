# Calc_population
励起準位占有数分布計算プログラムです．
## 概要
  太陽風多価イオン衝突における励起準位占有数分布計算プログラムです．
  
  現在， C, N, O の裸イオン， H-like イオン，He-like イオンの衝突に対応しています．  

  ここに上がっているファイル群だけでは正常に計算できません．Web 上にアップロードすることが推奨されないデータセット(personal なデータ)があるのが原因です．
  
## 動作確認環境
  - macOS Sierra v10.12.5
  - Python 3.5.1 (Anaconda 4.0.0)
  - matplotlib の backend は Qt4Agg を使っています．

## Features

- CHIANTI Atomic Database のデータセットを用いた計算
- ほとんどのデータが JSON であり可読性・拡張性が高い

## Requirement

- numpy
- scipy
- matplotlib
- tqdm
