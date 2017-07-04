import numpy as np
import sys
import json
from Calc_Populations_funcs_ECCSjson import *

def create_coefficient_matrix(numberOfStates, v, Total_Cross_Section, Particle_number, Cross_Sections_dict, A_coefficients_dict, orbitlist):
    '''
        係数行列を作成して返す関数
    '''

    coefficient_matrix = np.zeros((numberOfStates,numberOfStates))
    coefficient_matrix[0][0] = -Total_Cross_Section * v * Particle_number

    for df in range(1, numberOfStates, 1):
        nowOrbit = orbitlist[df-1]
        coefficient_matrix[df][0] = Cross_Sections_dict[nowOrbit]*v*Particle_number
        if nowOrbit in A_coefficients_dict:
            coefficient_matrix[df][df] -= sum(A_coefficients_dict[nowOrbit].values())
            for finalstate, AC in A_coefficients_dict[nowOrbit].items():
                coefficient_matrix[df][orbitlist.index(finalstate)+1] += AC

    return coefficient_matrix


def main():
    print('計算を行う微分方程式の硬度比(stiffness ratio)を計算します． \n\
Stiff な微分方程式ではGear法や後退微分法(BDF)を求解アルゴリズムとすることが推奨されます．\n')
    # イオン別にディレクトリ分けしてあるので電子捕獲断面積ディレクトリ内部のディレクトリ一覧を表示,選択している
    print('計算したいイオン種の番号を選んでください．')
    ECCSFilePath = selectFile('ECCS_json')

    # 選択されたイオンのディレクトリ内の電子捕獲断面積ファイル一覧を表示，選択している
    print('計算したい衝突系の番号を選んでください．')
    ECCSFilePath = selectFile(ECCSFilePath)
    # 電子捕獲断面積ファイル内に'iontype'をキーとしてイオン種を記録している
    try:
        ECCSFile = open(ECCSFilePath)
        ECCSdict = json.load(ECCSFile)
    except:
        print('No such file or directory.')
        sys.exit(1)

    orbitdict, confdict, conflist, orbitlist = readorbitsfile(ECCSdict['iontype'])

    Collision_system = ECCSFilePath.split('/')
    Collision_system = Collision_system[-1].rstrip('.json')
    # 電子捕獲断面積ファイルには複数の衝突エネルギーにおける電子捕獲断面積が格納されているので，選択する.
    Col_energies = [float(e) for e in list(ECCSdict.keys()) if e != 'iontype']
    Col_energies.sort()
    print('計算したい衝突エネルギーの番号を選んでください．')
    for (i, Show_Col_E) in enumerate(Col_energies):
        print('[{0}] {1}'.format(i, Show_Col_E))

    # 衝突エネルギー[keV/u]を決める
    Collision_Energy = int(input())
    print('{0} keV/u'.format(Col_energies[Collision_Energy]))
    # 選択された衝突エネルギーから衝突速度計算
    Collision_Speed = convert_energy(Col_energies[Collision_Energy])

    # 衝突エネルギーに対応する電子捕獲断面積をCross_Sections_listに格納，Total_Cross_Sectionに全断面積を格納
    Cross_Sections = ECCSdict[str(Col_energies[Collision_Energy])]
    Total_Cross_Section = sum([i for i in ECCSdict[str(Col_energies[Collision_Energy])].values() if isinstance(i, float)]) * 1.e-16
    # print('Total_Cross_Section = {0}'.format(Total_Cross_Section))
    Cross_Sections_dict = {}
    for conf in conflist[:len(Cross_Sections)]:
        tmp = confdict[conf]
        for orbit in tmp:
            if conf in Cross_Sections:
                Cross_Sections_dict[orbit] = orbitdict[orbit]['total_angularmomentum_multiplicity'] * Cross_Sections[conf] * 1.e-16
            else:
                Cross_Sections_dict[orbit] = 0.0

    if '--debug' in sys.argv:
        print('len(Cross_Sections_dict) = {}'.format(len(Cross_Sections_dict)))
        print('AC/ChiantiAC_{0}_{1}like.json'.format(Collision_system[0], ECCSdict['iontype']))

    # イオンに対応するA係数ファイルを開く
    try:
        ACfile = open('AC/ChiantiAC_{0}_{1}like.json'.format(Collision_system[0], ECCSdict['iontype']))
        ACdict = json.load(ACfile)
    except:
        print('No such file or directory.')
        sys.exit(1)

    # 中性粒子の粒子数を入力する．
    He = float(input('Heの粒子数を入力してください(単位cm^-3) > '))

    # 初期条件設定: primary ionが100%で，衝突後のイオンは存在しない
    f0 = [0.0] * (len(Cross_Sections_dict)+1)
    if '--debug' in sys.argv:
        print('f0 = {}'.format(f0))

    coefficient_matrix = create_coefficient_matrix(len(Cross_Sections_dict)+1,Collision_Speed, Total_Cross_Section, He, Cross_Sections_dict, ACdict, orbitlist)

    if '--debug' in sys.argv:
        print(coefficient_matrix)

    la, v = np.linalg.eig(coefficient_matrix)

    print('!---------EigenValues---------!')
    print(la)

    print('!---------Stiffness Ratio-----!')
    _la = np.abs(la)
    maximum = _la[0]
    minimum = _la[0]
    for eigenvalue in _la:
        #print('maximum = {}, minimum = {}, eigenvalue = {}'.format(maximum,minimum, eigenvalue))
        if eigenvalue != 0.0 and eigenvalue < minimum:
            minimum = eigenvalue
        if eigenvalue != 0.0 and eigenvalue > maximum:
            maximum = eigenvalue

    #print(maximum,minimum)

    stiffness_ratio = maximum/minimum
    print('{:1.3e}'.format(stiffness_ratio))

    if stiffness_ratio > 1.e+4:
        print('This ODE is stiff.')

if __name__ == '__main__':
    main()

