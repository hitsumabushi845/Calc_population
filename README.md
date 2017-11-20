# Calc_population
励起準位占有数分布計算プログラムです．
## 概要
  太陽風多価イオン衝突における励起準位占有数分布計算プログラムです．
  
  現在， C, N, O の裸イオン， H-like イオン，He-like イオンの衝突に対応しています．  

  ここに上がっているファイル群だけでは正常に計算できません．Web 上にアップロードすることが推奨されないデータセット(personal なデータ)があるのが原因です．


## プログラムについて
### Calc_populations.py
  衝突前のイオンに関する方程式


  <img src="https://latex.codecogs.com/gif.latex?\frac{\textrm{d}[{\rm&space;X}^{q&plus;}]}{\textrm{d}t}=-\sigma_{\mathrm{total}}\cdot&space;v&space;[{\rm&space;X}^{q&plus;}][{\rm&space;Y}]" />


  衝突後のイオンに関する方程式


  <img src="https://latex.codecogs.com/gif.latex?\frac{\textrm{d}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S})]}{\textrm{d}t}=\sigma_{\mathcal{S}}\cdot&space;v&space;[{\rm&space;X}^{q&plus;}][{\rm&space;Y}]&space;&plus;\sum_{\mathcal{S}'}\left\{A_{\mathcal{S}',&space;\mathcal{S}}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S}')]\right\}&space;-\left\{\sum_{\mathcal{S}''}A_{\mathcal{S},&space;\mathcal{S}''}\right\}[{\rm&space;X}^{(q-1)&plus;}(\mathcal{S})]" />
  
  からなる連立微分方程式を解きます

### check_ode_stiffness.py
  Calc_populations.pyで計算する連立微分方程式が Stiff かどうかをチェックします

### plotfromdatafile.py
  Calc_populations.py で生成された解データファイルから曲線をプロットします

### plot_spectrum_from_population.py
  Calc_populations.py で生成された解データファイルから，発光スペクトルをプロットします

### gaussian_convolution.py
  plot_spectrum_from_population.py で生成されたスペクトルをそれぞれガウス関数で重ね合わせます．
  検出器で得られたスペクトルと比較することを想定しているので，半値幅を入力できるようになっています．


## 動作確認環境
  - macOS Sierra v10.12.5
  - Python 3.5.1 (Anaconda 4.0.0)
  - matplotlib の backend は Qt5Agg を使っています．

## Features

- CHIANTI Atomic Database のデータセットを用いた計算
- ほとんどのデータが JSON であり可読性・拡張性が高い

## Requirement

- numpy
- scipy
- matplotlib
- tqdm
