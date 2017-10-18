# Calc_population
励起準位占有数分布計算プログラムです．
## 概要
  太陽風多価イオン衝突における励起準位占有数分布計算プログラムです．
  
  現在， C, N, O の裸イオン， H-like イオン，He-like イオンの衝突に対応しています．  

  ここに上がっているファイル群だけでは正常に計算できません．Web 上にアップロードすることが推奨されないデータセット(personal なデータ)があるのが原因です．


## プログラムについて
### Calc_populations.py
  <img src="https://latex.codecogs.com/gif.latex?\frac{\textrm{d}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S})]}{\textrm{d}t}=\sigma_{\mathcal{S}}\cdot&space;v&space;[{\rm&space;X}^{q&plus;}][{\rm&space;Y}]&space;&plus;\sum_{\mathcal{S}'}\left\{A_{\mathcal{S}',&space;\mathcal{S}}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S}')]\right\}&space;-\left\{\sum_{\mathcal{S}''}A_{\mathcal{S},&space;\mathcal{S}''}\right\}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S})]" />
  
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
