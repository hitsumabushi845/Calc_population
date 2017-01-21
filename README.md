# Calc_population
励起準位占有数分布計算プログラムです．
## 概要
  太陽風多価イオン衝突における励起準位占有数分布計算プログラムです．
  
  現在， C, N, O の裸イオン， H-like イオンの衝突に対応しています．
  
  今後 He-like イオンまで拡張する予定です．

  ここに上がっているファイル群だけでは正常に計算できません．Web 上にアップロードすることが推奨されないデータセットがあるのが原因です．
  
## 動作確認環境
  - macOS Sierra v10.12.2
  - Python 3.5.1 (Anaconda 4.0.0)
  - matplotlib の backend は Qt4Agg を使っています．

## Features

- Chianti Atomic Database のデータセットを用いた計算が可能
- ほとんどのデータが JSON であり可読性が高い

## Requirement

- numpy
- scipy
- matplotlib
- tqdm
