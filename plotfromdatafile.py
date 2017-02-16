import numpy as np
from Calc_Populations_funcs_ECCSjson import *
import matplotlib.pyplot as plt


def plotfromdatafile():

    # H-,He-likeに属する衝突前イオンを定義
    H_like = ['O8+','N7+','C6+']
    He_like = ['O7+','N6+','C5+']
    Li_like = ['O6+','N5+','C4+']

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
    elif Collision_system[:3] in Li_like:
        iontype = 'Li'
    
    # 取得されたイオン種から準位名(グラフの凡例に使用)を取得
    orbitfile = open('./orbits_{0}like.txt'.format(iontype))
    orbits = [i.rstrip('\n') for i in orbitfile.readlines()]

    # 選択されたデータファイルを読み込む
    dataarray = np.loadtxt(datafile, delimiter=',')

    print(dataarray)

    # データの存在する準位の数を取得
    orbit_nums = len(dataarray[0][2:])

    # グラフプロット処理
    fig = PopGraph(iontype)

    print('[0] 全ての軌道についての曲線をプロットする\n[1] 指定した軌道のみプロットする')
    plotoption = int(input())

    if plotoption == 0:
        fig.plot(dataarray[:,0], dataarray[:,1:])

    elif plotoption == 1:
        # データの存在する軌道一覧を表示する
        fig.selectionPlot(dataarray[:,0],dataarray[:,1:])

    
    # プロット方式の設定 
    fig.setGraph()

    fig.show()

if __name__ == '__main__':
    plotfromdatafile()
