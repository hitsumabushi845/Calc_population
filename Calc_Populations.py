import numpy as np
import os
import sys
import datetime
import json
from scipy.integrate import ode
from scipy.linalg import block_diag
from tqdm import tqdm
from Calc_Populations_funcs_ECCSjson import *
import matplotlib.pyplot as plt
import platform


def main():
    param_dic = {}
    d = datetime.datetime.today()
    headerstr = d.strftime('Calclation date:%y%m%d %H%M,')
    default_output_filename = d.strftime('%y%m%d_%H%M_')

    # イオン別にディレクトリ分けしてあるので電子捕獲断面積ディレクトリ内部のディレクトリ一覧を表示,選択している
    print('計算したいイオン種の番号を選んでください．')
    ECCSFilePath = selectFile('ECCS_json')

    # 選択されたイオンのディレクトリ内の電子捕獲断面積ファイル一覧を表示，選択している
    print('計算したい衝突系の番号を選んでください．')
    ECCSFilePath = selectFile(ECCSFilePath)
    try:
        ECCSFile = open(ECCSFilePath)
        ECCSdict = json.load(ECCSFile)
    except:
        print('No such file or directory.')
        sys.exit(1)

    # 電子捕獲断面積ファイル内に'iontype'をキーとしてイオン種を記録しているので，対応する電子配列データを読み込む
    orbitdict, confdict, conflist, orbitlist = readorbitsfile(ECCSdict['iontype'])

    # print('iontype = {0}'.format(iontype))
    # ECCSs = np.loadtxt(ECCSFilePath, delimiter=',')

    # ファイル名から衝突系(X^q+ - Y)の文字列を取り出す
    Collision_system = ECCSFilePath.split('/')
    Collision_system = Collision_system[-1].rstrip('.json')
    target_particle = Collision_system.split('+')[-1]

    # header文字列，保存する際のファイル名を設定
    headerstr += 'Collision system: {0},'.format(Collision_system)
    default_output_filename = '{0}{1}_'.format(default_output_filename, Collision_system)

    # 電子捕獲断面積ファイルには複数の衝突エネルギーにおける電子捕獲断面積が格納されているので，選択する.
    Col_energies = [float(e) for e in list(ECCSdict.keys()) if e != 'iontype']
    # この時点では衝突エネルギーが順不同なため，ソートする
    Col_energies.sort()

    # データが格納されている衝突エネルギーの一覧を表示
    print('計算したい衝突エネルギーの番号を選んでください．')
    for (i, Show_Col_E) in enumerate(Col_energies):
        print('[{0}] {1}'.format(i, Show_Col_E))

    # 衝突エネルギー[keV/u]を決める
    Collision_Energy = int(input())
    print('{0} keV/u'.format(Col_energies[Collision_Energy]))

    # header文字列，保存する際のファイル名を設定
    headerstr += 'Collision_Energy: {0}keV/u,'.format(Col_energies[Collision_Energy])
    default_output_filename = '{0}{1}keVu_'.format(default_output_filename, Col_energies[Collision_Energy])

    # 選択された衝突エネルギーから衝突速度計算
    Collision_Speed = convert_energy(Col_energies[Collision_Energy])
    # print('{0} cm/s'.format(Collision_Speed))

    # 衝突エネルギーに対応する電子捕獲断面積をCross_Sections_listに格納，Total_Cross_Sectionに全断面積を格納
    Cross_Sections = ECCSdict[str(Col_energies[Collision_Energy])]
    if '--debug' in sys.argv:
        print('Cross_Sections = {}'.format(Cross_Sections))
    Total_Cross_Section = sum([i for i in ECCSdict[str(Col_energies[Collision_Energy])].values() if isinstance(i, float)]) * 1.e-16
    # print('Total_Cross_Section = {0}'.format(Total_Cross_Section))

    # Cross_Sections_list に格納された電子捕獲断面積を nlJ をキーとする辞書に格納していく
    Cross_Sections_dict = {}
    for nl, nlCrossSection in Cross_Sections.items():
        nlJlist = confdict[nl]
        for nlJ in nlJlist:
            Cross_Sections_dict[nlJ] = orbitdict[nlJ]['total_angularmomentum_multiplicity'] * nlCrossSection * 1.e-16

    if '--debug' in sys.argv:
        print('len(Cross_Sections_dict) = {}'.format(len(Cross_Sections_dict)))

    # イオンに対応するA係数ファイルを開く
    try:
        ACfile = open('AC/ChiantiAC_{0}_{1}like.json'.format(Collision_system[0], ECCSdict['iontype']))
        ACdict = json.load(ACfile)
    except:
        print('No such file or directory.')
        sys.exit(1)

    # 中性粒子の粒子数を入力する．
    particle_number = float(input('{}の粒子数を入力してください(単位cm^-3) > '.format(target_particle)))

    default_output_filename = '{0}{1}cm-3'.format(default_output_filename, particle_number)
    headerstr += 'Neutral Particle Number: {0}/cm^-3,'.format(particle_number)

    # 初期条件設定: primary ionが100%で，衝突後のイオンは存在しない
    f0 = [0.0] * (len(Cross_Sections_dict)+1)
    f0[0] = 1.0
    
    if '--debug' in sys.argv:
        print('f0 = {}'.format(f0))

    # ここから微分方程式の求解に関する処理
    # 計算を行う時間幅，ステップ幅，t0を決める
    # 時間幅は衝突セルの長さ(5cm)から決定  
    tend = 5.0/Collision_Speed
    dt = 1.e-12
    t0 = 0.0

    # 微分方程式ソルバの設定: 求解アルゴリズム，初期値，方程式のパラメータの指定

    # デバッグ時に初期値パラメータを確認できる 
    if '--debug' in sys.argv:
        print('Collision_Speed = {0}'.format(Collision_Speed))
        print('Total_Cross_Section = {}'.format(Total_Cross_Section))
        print('particle_number = {}'.format(particle_number))
        print('Cross_Sections_dict = {}'.format(Cross_Sections_dict))
        print('ACdict = {}'.format(ACdict))
        print('orbitlist = {}'.format(orbitlist))

    # 求解アルゴリズム，初期値の指定．硬い微分方程式なのでBDFを使用
    r = ode(rate_eqs).set_integrator('vode', method='bdf')
    r.set_initial_value(f0, t0).set_f_params(Collision_Speed, Total_Cross_Section, particle_number, Cross_Sections_dict, ACdict, orbitlist)


    # レート方程式を解いていく
    t1 = []
    res = []

    # progress barの設定 
    pbar = tqdm(total=10000)
    pbar.set_description('Processing {0} calculation'.format(Collision_system))
    percent_t = tend/10000.0
    
    
    while r.successful() and r.t < tend:
        if r.t > percent_t:
            pbar.update(1)
            percent_t = percent_t + tend/10000.0
        tmp = r.integrate(r.t+dt)
        t1.append(r.t)
        res.append(tmp)
    pbar.close()

    # macOSで実行している場合は計算が終了したときにNotification Centerから通知
    if platform.system() == 'Darwin':
        os.system("osascript -e 'display notification \"All populations have been calculated.\" with title \"Calc_Populations\" subtitle \"Calculation is complete.\"'")

    if '--debug' in sys.argv:
        print('len(t1) = {}, len(res) = {}'.format(len(t1), len(res)))

    t1 = np.array(t1)
    sol1 = np.array(res)

    x1 = t1 * Collision_Speed

    # データファイル用のarrayの作成
    outputarray = np.c_[t1, sol1]

    # ここから解のプロットに関する処理
    fig, param_dic['Horizontal_axis'] = plot_populations([t1, x1], sol1, ECCSdict['iontype'])

    plt.clf()

    print(default_output_filename)

    # データファイルを保存
    np.savetxt('datafiles/outputdata{0}.csv'.format(default_output_filename), outputarray, delimiter=',', header=headerstr)

if __name__ == '__main__':
    main()
