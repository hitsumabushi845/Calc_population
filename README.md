# Calc_population

多価イオンと中性粒子の電荷交換衝突について，電子を捕獲したあとのイオンの励起準位占有数分布を計算するプログラムです．太陽風多価イオンの衝突を対象にしています．

## 概要

多価イオン X<sup>q+</sup> が中性粒子 Y から電子を 1 個捕獲すると，X<sup>(q-1)+</sup> の励起準位に電子が入ります．このプログラムは電子捕獲と放射カスケードのレート方程式を解いて，各準位の占有数が時間とともにどう変わるかを求めます．求めた占有数から発光スペクトルもプロットできます．

現在，次の入射イオンの衝突に対応しています．

| 入射イオン | 捕獲後のイオン |
|---|---|
| 裸イオン (C<sup>6+</sup>，N<sup>7+</sup>，O<sup>8+</sup>) | H-like |
| H-like イオン (C<sup>5+</sup>，N<sup>6+</sup>，O<sup>7+</sup>) | He-like |
| He-like イオン (O<sup>6+</sup>) | Li-like |

ここに上がっているファイル群だけでは正常に計算できません．電子捕獲断面積のデータは Web 上にアップロードすることが推奨されないデータセット (personal なデータ) なので，このリポジトリに含めていません．計算するには，断面積のデータを自分で用意します (「1. 断面積データの準備」)．

## セットアップ

Python 3 がインストール済みであることを前提にします．macOS や Linux では，リポジトリのルートで次のコマンドを実行すると，venv の仮想環境 `.venv/` が作られ，`requirements.txt` のパッケージがその中にインストールされます．

```
./setup.sh
```

`requirements.txt` には次のパッケージを書いてあります．バージョンは固定していません．

- numpy
- scipy
- matplotlib
- tqdm
- pandas

使う Python を変えるときは，環境変数 `PYTHON` で指定します．

```
PYTHON=python3.12 ./setup.sh
```

プログラムを実行する前に，シェルを開くたびに仮想環境を有効にします．

```
source .venv/bin/activate        # bash，zsh
source .venv/bin/activate.fish   # fish
```

`.venv/` は `.gitignore` に入れてあります．`.venv/` があるときに `./setup.sh` をもう一度実行すると，仮想環境は作り直さずにパッケージのインストールだけを行います．

`setup.sh` を使わないときは，次のコマンドで同じ環境を作れます．

```
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Windows では `setup.sh` の代わりに `setup.ps1` を使います．PowerShell でリポジトリのルートに移動し，次のコマンドを実行します．

```
powershell -ExecutionPolicy Bypass -File setup.ps1
```

使う Python を変えるときは，`-Python` か環境変数 `PYTHON` で指定します．

```
powershell -ExecutionPolicy Bypass -File setup.ps1 -Python py
```

仮想環境は次のコマンドで有効にします．

```
.venv\Scripts\Activate.ps1    # PowerShell
.venv\Scripts\activate.bat    # コマンドプロンプト
```

PowerShell がスクリプトの実行を許可しない設定になっていると，`Activate.ps1` は実行できません．そのときは `Set-ExecutionPolicy -Scope Process RemoteSigned` を実行してから有効にするか，コマンドプロンプトを使います．

`setup.ps1` と，Windows でのプログラムの動作は確認していません．

動作を確認した環境は次の 2 つです．

- macOS，Python 3.12.13 と 3.15.2，numpy 2.5.5，scipy 1.18.1，matplotlib 3.11.2，tqdm 4.70.1，pandas 3.1.1 (`setup.sh` は Python 3.15.2 で確認)
- macOS Sierra v10.12.5，Python 3.5.1 (Anaconda 4.0.0)，matplotlib の backend は Qt5Agg (開発当初の環境)

## 使い方

どのプログラムもリポジトリのルートで実行します．実行すると画面に質問が出るので，番号や値を入力して進めます．

### 1. 断面積データの準備

`Calc_Populations.py` は `ECCS_json/` に置いた JSON から nl 別の電子捕獲断面積を読み込みます．テキスト形式の表を `tmp/` に置いて次のコマンドを実行すると，`ECCS_json/` に JSON が出力されます．

```
python convertECCStoJSON.py
```

入力と出力のディレクトリを変えるときは，`python convertECCStoJSON.py 入力ディレクトリ 出力ディレクトリ` のように指定します．`tmp/` と `ECCS_json/` は `.gitignore` に入れてあるので，コミットされません．

テキストの表は次の形で書きます．断面積の単位は 10<sup>-16</sup> cm<sup>2</sup> です．

```
O(8+)+He
 E (keV/u)   total   1s   2s   2p   3s   3p   3d   ...
 (衝突エネルギー) (全断面積) (1s の断面積) (2s の断面積) ...
```

- 表の前の行に衝突系を書きます (`O(8+)+He`，`C^(5+)-H2` など)．1 つのファイルに複数の表を入れられます．
- 衝突系の行がない表は，ファイル名を衝突系として扱います (`O7+He.txt` など)．
- 列名の行は `(keV/u)` を含む必要があります．`total` の列はなくてもかまいません．

変換では次の処理をします．

- `total` の列は出力しません．nl 別の値の和が `total` を上回る行は，警告として表示します．
- 途中で切れている行を含む表は，全ての行に共通する殻までで切り詰めます．`total` の列に届かずに切れた行は省略します．
- データにない低い準位は 0.0 で補完します．`Calc_Populations.py` が準位リストの先頭から連続して断面積が入っていることを前提にしているためです．

出力される JSON は次の形です．JSON を直接書いて `ECCS_json/` に置くこともできます．

```
ECCS_json/Hlike/O8+He.json
{
  "iontype": "H",
  "1.0": {"1s": 0.0, "2s": 0.0, "2p": 0.0, ...},
  "1.5": {...}
}
```

- ファイル名は衝突系です．先頭の 1 文字 (元素記号) で A 係数のファイルを選び，`+` より後ろを標的の名前として表示します．
- `iontype` は捕獲後のイオンの種類で，`H`，`He`，`Li` のどれかです．
- そのほかのキーは衝突エネルギー (keV/u) で，`str(float)` の形 (`"1.0"`，`"1.5"`) で書きます．
- nl のキーは `AtomicOrbitDatasets/electron_configuration_{iontype}.json` のキーに合わせます．H-like は `2p`，He-like は `1s2p`，Li-like は `1s1s2p` です．

### 2. 占有数の計算

```
python Calc_Populations.py
```

次の順に質問に答えます．

1. イオン種 (`ECCS_json/` の中のディレクトリ) の番号
2. 衝突系の番号
3. 衝突エネルギーの番号
4. 標的の粒子数 (単位は cm<sup>-3</sup>)
5. グラフの横軸 (時間 `t` か位置 `x`)
6. 衝突前のイオンをプロットするかどうか
7. 凡例を表示するかどうか

計算が終わると占有数のグラフが表示されます．グラフのウィンドウを閉じると，解のデータファイルが `datafiles/` に保存されます．

| オプション | 動作 |
|---|---|
| `--bdf` | 行列指数の代わりに，従来の数値積分 (BDF) で解きます．結果の比較用です． |
| `--debug` | 計算に使うパラメータを表示します． |

データファイルは `datafiles/outputdata{日時}_{衝突系}_{衝突エネルギー}keVu_{粒子数}cm-3.csv` という名前の CSV です．

- 1 行目は `#` で始まるコメントで，計算日時，衝突系，衝突エネルギー，粒子数が入ります．
- 1 列目は時刻 (s)，2 列目は衝突前のイオンの占有数です．3 列目以降は各準位の占有数で，`AtomicOrbitDatasets/orbits_{iontype}like.txt` の順に並びます．
- 行は 10<sup>-12</sup> s ごとで，衝突セルを通り抜ける時刻まで続きます．ファイルは数十 MB から数百 MB になります．`datafiles/` も `.gitignore` に入れてあります．

### 3. 占有数のプロット

```
python plotfromdatafile.py
```

`datafiles/` のデータファイルを選び，占有数の曲線をプロットします．全ての準位をプロットするか，番号で選んだ準位だけをプロットするかを選べます．準位を選ぶときは，番号を空白で区切って複数入力できます．

### 4. 発光スペクトルのプロット

```
python plot_spectrum_from_population.py
```

データファイルと時刻を選ぶと，その時刻の占有数から発光スペクトルをプロットします．横軸はエネルギー (eV) か波長 (nm) を選べます．各遷移の強度は上の準位の占有数に A 係数と固定の時間幅 4.55×10<sup>-9</sup> s を掛けた値です．

```
python gaussian_convolution.py
```

`spectrumdatafiles/` に置いたスペクトルのデータファイルを読み，各輝線をガウス関数にして重ね合わせます．検出器で得られたスペクトルと比較することを想定しているので，半値幅を入力できます．データファイルは 1 列目が強度，2 列目が波長の CSV です．

### そのほかのプログラム

| プログラム | 内容 |
|---|---|
| `check_ode_stiffness.py` | `Calc_Populations.py` で解く連立微分方程式の係数行列から硬度比 (stiffness ratio) を計算し，Stiff かどうかをチェックします． |
| `makeArbitraryProductionRatioDatafile.py` | He-like イオンにおける singlet，triplet の生成比を自由に設定したデータファイルを作ります．一律で設定するか，各 nl ごとに設定するかを選べます． |

## 計算モデル

衝突前のイオンに関する方程式

$$\frac{\mathrm{d}[\mathrm{X}^{q+}]}{\mathrm{d}t} = -\sigma_{\mathrm{total}} \cdot v\,[\mathrm{X}^{q+}][\mathrm{Y}]$$

衝突後のイオンに関する方程式

$$\frac{\mathrm{d}[\mathrm{X}^{(q-1)+}(\mathcal{S})]}{\mathrm{d}t} = \sigma_{\mathcal{S}} \cdot v\,[\mathrm{X}^{q+}][\mathrm{Y}] + \sum_{\mathcal{S}'} A_{\mathcal{S}',\mathcal{S}}\,[\mathrm{X}^{(q-1)+}(\mathcal{S}')] - \left\lbrace \sum_{\mathcal{S}''} A_{\mathcal{S},\mathcal{S}''} \right\rbrace [\mathrm{X}^{(q-1)+}(\mathcal{S})]$$

からなる連立微分方程式を解きます．$\sigma_{\mathcal{S}}$ は準位 $\mathcal{S}$ への電子捕獲断面積，$\sigma_{\mathrm{total}}$ はその和，$v$ は衝突速度，$[\mathrm{Y}]$ は標的の粒子数，$A_{\mathcal{S}',\mathcal{S}}$ は準位 $\mathcal{S}'$ から $\mathcal{S}$ への遷移の A 係数です．

計算では次のように扱います．

- 扱う過程は一電子捕獲と放射遷移です．
- 初期条件は衝突前のイオンの占有数が 1，衝突後のイオンの占有数が 0 です．
- 衝突速度は核子あたりの運動エネルギー E (keV/u) から $v = \sqrt{2E/m}$ で求めます．
- 計算する時間は長さ 5 cm の衝突セルを通り抜ける時刻までです．標的の粒子数と衝突速度はその間一定とします．
- nl 別の断面積は `AtomicOrbitDatasets/{iontype}orbits.json` の `total_angularmomentum_multiplicity` の比で微細構造準位に割り振ります．

## 解法

レート方程式は係数が時間によらない線形の連立方程式なので，係数行列を M とすると

$$f(t + \Delta t) = \exp(M \Delta t)\, f(t)$$

が厳密に成り立ちます．`Calc_Populations.py` は数値積分をせずにこの関係で解きます．丸め誤差を抑えるために，次の 2 つを行っています．

- $\exp(M \Delta t)$ ではなく $Q = \exp(M \Delta t) - I$ を直接計算し，$f + Qf$ の形で進めます．ゆっくり変化する準位の小さな変化量が，1 に近い数に埋もれて丸められるのを防ぎます．
- 足し込みに Kahan の補償付き加算を使います．

`--bdf` を付けると，`scipy.integrate.ode` の BDF 法 (既定の許容誤差) で解きます．

H-like，He-like，Li-like の 5 ケースで，60 桁精度の行列指数 (mpmath) を参照解として 2 つの解法を比べました．

| | 行列指数 | BDF |
|---|---|---|
| 全準位の相対誤差の最大値 | 6×10<sup>-16</sup> 以下 | 2×10<sup>-3</sup> から 3×10<sup>-2</sup> |
| 解く部分の所要時間 (72 準位，約 36 万ステップ) | 0.74 秒 | 155 秒 |

## データファイル

A 係数とエネルギー準位は CHIANTI Atomic Database のデータセットを使っています．ほとんどのデータが JSON であり，可読性・拡張性が高いです．

| 場所 | 内容 |
|---|---|
| `AC/` | A 係数です．上の準位，下の準位の順にキーを引きます．`Calc_Populations.py` と `check_ode_stiffness.py` が `ChiantiAC_{元素}_{iontype}like.json` を読みます． |
| `ACtoPlotSpectrum/` | `plot_spectrum_from_population.py` が読む A 係数です． |
| `EnergyLevels/` | 各準位のエネルギー (eV) です．`plot_spectrum_from_population.py` が読みます． |
| `AtomicOrbitDatasets/` | 準位の定義です．微細構造準位ごとの量子数と重み，電子配置と微細構造準位の対応，準位の並び順が入っています． |
| `ECCS_json/` | 電子捕獲断面積です．リポジトリには含めていません． |

## 既知の制約

- N<sup>5+</sup> (捕獲後が Li-like) は計算できません．`AC/ChiantiAC_N_Lilike.json` がないためです．
- `makeArbitraryProductionRatioDatafile.py` が出力する生成比のファイルを，`Calc_Populations.py` は読み込みません．
- `gaussian_convolution.py` が読むスペクトルのデータファイルを出力する処理は，`plot_spectrum_from_population.py` の中でコメントアウトされています．
- `check_ode_stiffness.py` は標的が何であっても，粒子数の質問に「He の粒子数」と表示します．
