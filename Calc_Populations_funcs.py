import numpy as np
import os
import sys
import math
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ptick


def rate_eqs(t, Popfuncs, v, Total_Cross_Section, Particle_number, Cross_Sections_dict, A_coefficients_dict, orbitlist):
    '''
        動的なレート方程式
    '''

    dfdt = [0.0] * len(Popfuncs)

    dfdt[0] = -Total_Cross_Section * v * Particle_number * Popfuncs[0]
    for df in range(1, len(dfdt), 1):
        nowOrbit = orbitlist[df-1]
        dfdt[df] = Cross_Sections_dict[nowOrbit]*v*Particle_number*Popfuncs[0]
        if nowOrbit in A_coefficients_dict:
            for finalstate, AC in A_coefficients_dict[nowOrbit].items():
                dfdt[df] -= (AC*Popfuncs[orbitlist.index(nowOrbit)+1])
                dfdt[orbitlist.index(finalstate)+1] += (AC*Popfuncs[orbitlist.index(nowOrbit)+1])

    return dfdt


def readorbitsfile(iontype):
    '''
        iontypenumberで指定されたイオン種に対応するファイルを読み込む．
        読み込むファイル群:
            {iontype}orbits.json:
                各微細構造準位の
                    - 電子配置
                    - 主量子数
                    - スピン多重度
                    - 全角運動量
                    - 全角運動量多重度
                    - 全軌道角運動量
                を格納したjsonファイル．2次元辞書で読み込まれる．

            electron_configuration_{iontype}.json:
                各電子配置において縮退する微細構造準位を格納したjsonファイル．2次元辞書で読み込まれる．

            electron_configuration_{iontype}.txt:
                各電子配置をnlの順に格納したtxtファイル．listで読み込まれる．

            orbits_{iontype}like.txt:
                各微細構造準位を順に格納したtxtファイル．listで読み込まれる．
    '''

    try:
        orbitfile = open('./AtomicOrbitDatasets/{0}orbits.json'.format(iontype))
        orbitdict = json.load(orbitfile)
        orbitfile = open('./AtomicOrbitDatasets/electron_configuration_{0}.json'.format(iontype))
        confdict  = json.load(orbitfile)
        orbitfile = open('./AtomicOrbitDatasets/electron_configuration_{0}.txt'.format(iontype))
        conflist  = [i.rstrip('\n') for i in orbitfile.readlines()]
        orbitfile = open('./AtomicOrbitDatasets/orbits_{0}like.txt'.format(iontype))
        orbitlist = [i.rstrip('\n') for i in orbitfile.readlines()]
    except:
        print('No such file or directory.')
        sys.exit(1)

    return (orbitdict, confdict, conflist, orbitlist)


def selectFile(directory):
    '''
        引数で指定したディレクトリの中のファイルを一覧で表示し，
        それぞれのファイルに付けられたindexを選択するとそのファイルのパスを返す．
    '''
    try:
        Files = os.listdir(directory)
        for i, File in enumerate(Files):
            print('[{0}] {1}'.format(i, File))
        Filenumber = int(input())
        print(Files[Filenumber])
        Filepath = directory + '/' + Files[Filenumber]
    except:
        # 入力したファイル名が間違っているか，ファイルが存在しない場合，プログラムを終了する．
        print('入力したファイルは存在しません．')
        sys.exit(1)

    return Filepath


def make2Ddict(names):
    '''
        2次元辞書を作成する関数．
        引数(str型のlist)をそれぞれkeyとする．
        辞書のvalueは全て0.0(double)に初期化されている．
    '''
    dict_2d = {}

    for x in names:
        for y in names:
            if x in dict_2d:
                dict_2d[x][y] = 0.0
            else:
                dict_2d[x] = {y: 0.0}

    return dict_2d


def convert_energy(col_Energy_kVu):
    '''
        引数に与えられた衝突エネルギー[kV/u]を
        衝突速度[cm/s]に変換する関数．
    '''

    col_Energy_cms = math.sqrt(col_Energy_kVu*10**10*9.64854)*10**2

    return col_Energy_cms


def convert_pressure(pressure=1.0e+03, temperature=300):
    '''
        引数に与えられた圧力(Pa)を粒子数[/cm^3]に変換する関数．
    '''
    pressure_per_cmsquared = pressure/(1.38e-23*temperature)
    return pressure_per_cmsquared


def plot_populations(xaxiss, populations, iontype):
    '''
        ポピュレーションのグラフをプロットする．
        横軸は時間と位置の2つから選ぶことができる．
    '''

    fig = PopGraph(iontype)

    fig.plot(xaxiss, populations)

    fig.setGraph()

    fig.show()

    return fig.popfig, fig.selectXaxis


class PopGraph():
    def __init__(self, iontype):
        self.popfig = plt.figure(figsize=(16, 9))
        self.popfig = self.popfig.add_subplot(1, 1, 1)
        orbitfile = open('./AtomicOrbitDatasets/orbits_{0}like.txt'.format(iontype))
        self.orbits = [i.rstrip('\n') for i in orbitfile.readlines()]
        self.orbits.insert(0, 'Primary Ion')
        self.selectXaxis = 't'

    def plot(self, xaxiss, populations):

        if len(xaxiss) == 2:
            axisflag = True
            while axisflag:
                self.selectXaxis = input('横軸を選んでください(time(t) or position(x))\n> ')
                if self.selectXaxis == 't' or self.selectXaxis == 'time':
                    xaxisarray = xaxiss[0]
                    axisflag = False
                elif self.selectXaxis == 'x' or self.selectXaxis == 'position':
                    xaxisarray = xaxiss[1]
                    axisflag = False
                else:
                    print('正しい値を入力してください．')
        else:
            xaxisarray = xaxiss
            self.selectXaxis = 't'

        isPlotBeforeCollision = input('衝突前のイオンのポピュレーションをプロットしますか?(y/n)\n> ')

        if isPlotBeforeCollision == 'Y' or isPlotBeforeCollision == 'y':
            self.popfig.plot(xaxisarray[::100], populations[::100, 0], label=orbits[0])

        for i in np.arange(1, len(populations[0])):
            self.popfig.plot(xaxisarray[::100], populations[::100, i], label='{0}'.format(self.orbits[i]), linestyle='-')

    def selectionPlot(self, xaxis, populations):
        for i, orbit in enumerate(self.orbits[:len(populations[1:])]):
            print('[{0}] {1}'.format(i, orbit))
        # 複数選択された準位の曲線を同時にプロットできるようにしている．whitespace区切りで準位の入力ができる
        orbitnumbers = list(map(int, input().split()))
        for orbitnumber in orbitnumbers:
            self.popfig.plot(xaxis, populations[:, orbitnumber], label=self.orbits[orbitnumber], linestyle='-', linewidth=4)

    def setGraph(self):
        if self.selectXaxis == 'time' or self.selectXaxis == 't':
            self.popfig.set_xlabel('Time[s]', fontsize=25)
        else:
            self.popfig.set_xlabel('Position[cm]', fontsize=25)

        for tick in self.popfig.xaxis.get_major_ticks():
            tick.label.set_fontsize(20)
        for tick in self.popfig.yaxis.get_major_ticks():
            tick.label.set_fontsize(20)
        self.popfig.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.popfig.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        self.popfig.xaxis.offsetText.set_fontsize(15)
        self.popfig.yaxis.offsetText.set_fontsize(15)
        scale_format = ptick.ScalarFormatter(useMathText=True)
        self.popfig.yaxis.set_major_formatter(scale_format)
        self.popfig.xaxis.set_major_formatter(scale_format)

        self.popfig.legend(loc='best')
        plt.tight_layout()

    def show(self):
        plt.show()


def figoutput(default_output_filename, fig):
    '''
        グラフを画像で保存する．
    '''

    figname = str(input('グラフのファイル名を入力してください．(default={0}_Population.pdf)'.format(default_output_filename)))
    if figname:
        plt.savefig('graphs/{0}.pdf'.format(figname), bbox_inches='tight', pad_inches=0.0)
    else:
        plt.savefig('graphs/{0}_Population.pdf'.format(default_output_filename), bbox_inches='tight', pad_inches=0.0)


def outputjson(parameter_dic, output_filename='lastparameter.json'):
    '''
        プログラムの実行に使ったパラメータ群をjsonファイルに出力
    '''
    output_file = open(output_filename, 'w')
    json.dump(parameter_dic, output_file)


def inputjson(input_filename='lastparameters.json'):
    '''
        前回のプログラム実行に使ったパラメータ群を辞書に格納
    '''
    f = open(input_filename)
    param_dic = json.load(f)

    return param_dic
