import numpy as np
from Calc_Populations_funcs import *
import matplotlib.pyplot as plt


def plotfromdatafile():

    # H-,He-likeに属する衝突前イオンを定義
    H_like = ['O8+','N7+','C6+']
    He_like = ['O7+','N6+','C5+']

    # データファイルを選択
    print('データファイルを選んでください．')
    datafile = selectFile('datafiles/')

    # データファイルの名前から衝突系を取得
    Collision_system = datafile.split('/')
    Collision_system = Collision_system[-1].split('_')
    Collision_system = Collision_system[2]
    print(Collision_system)

    # 取得された衝突系からイオン種を取得
    if Collision_system[:3] in H_like:
        iontype = 'H'
    elif Collision_system[:3] in He_like:
        iontype = 'He'
    
    # 取得されたイオン種から準位名(グラフの凡例に使用)を取得
    orbitfile = open('./orbits_{0}like.txt'.format(iontype))
    orbits = [i.rstrip('\n') for i in orbitfile.readlines()]

    # 選択されたデータファイルを読み込む
    dataarray = np.loadtxt(datafile, delimiter=',')

    # データの存在する準位の数を取得
    orbit_nums = len(dataarray[0])

    # グラフプロット処理
    fig = plt.figure(figsize=(16,9))
    popfig = fig.add_subplot(1,1,1)

    print('[0] 全ての軌道についての曲線をプロットする\n[1] 指定した軌道のみプロットする')
    plotoption = int(input())

    if plotoption == 0:
        for i in np.arange(2,orbit_nums):
            popfig.plot(dataarray[:,0], dataarray[:,i], label='{0}'.format(orbits[i-2]), linestyle='-')

    elif plotoption == 1:
        # データの存在する軌道一覧を表示する
        for i,orbit in enumerate(orbits[:orbit_nums-2]):
            print('[{0}] {1}'.format(i,orbit))
        # 複数選択された準位の曲線を同時にプロットできるようにしている．whitespace区切りで準位の入力ができる
        orbitnumbers = list(map(int, input().split()))
        for orbitnumber in orbitnumbers:
            popfig.plot(dataarray[:,0], dataarray[:,orbitnumber+2] ,label='{0}'.format(orbits[orbitnumber]),linestyle='-',linewidth=4)

    
    # プロット方式の設定 
    popfig.set_xlabel('Time[s]', fontsize=25)
    
    popfig.set_ylabel('Population', fontsize=25)
    for tick in popfig.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in popfig.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    popfig.ticklabel_format(style='sci',axis='y',scilimits=(0,0))
    popfig.ticklabel_format(style='sci',axis='x',scilimits=(0,0))
    popfig.xaxis.offsetText.set_fontsize(15)
    popfig.yaxis.offsetText.set_fontsize(15)
    popfig.yaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))
    popfig.xaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))

    popfig.legend(loc='best')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plotfromdatafile()
