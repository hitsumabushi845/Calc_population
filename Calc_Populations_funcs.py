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
        # 他の準位からのカスケードによる流入が先に加算されていることがあるので，代入ではなく加算する
        dfdt[df] += Cross_Sections_dict[nowOrbit]*v*Particle_number*Popfuncs[0]
        if nowOrbit in A_coefficients_dict:
            dfdt[df] -= sum(A_coefficients_dict[nowOrbit].values())*Popfuncs[df]
            for finalstate, AC in A_coefficients_dict[nowOrbit].items():
                dfdt[orbitlist.index(finalstate)+1] += (AC*Popfuncs[df])

    return dfdt


def create_rate_matrix(numberOfStates, v, Total_Cross_Section, Particle_number, Cross_Sections_dict, A_coefficients_dict, orbitlist):
    '''
        レート方程式 df/dt = M f の係数行列を，流入と流出に分けて返す．
            gains[i][j]: 準位 j から準位 i への流入レート(全て 0 以上，対角は 0)
            losses[j]  : 準位 j からの流出レート(全て 0 以上)
        M = gains - diag(losses) であり，rate_eqs() と同じ方程式を表す．
        index 0 が衝突前のイオン，index i (i >= 1) が orbitlist[i-1] に対応する．
    '''

    index = {orbit: i + 1 for i, orbit in enumerate(orbitlist[:numberOfStates - 1])}
    gains = np.zeros((numberOfStates, numberOfStates))
    losses = np.zeros(numberOfStates)

    losses[0] = Total_Cross_Section * v * Particle_number
    for df in range(1, numberOfStates):
        nowOrbit = orbitlist[df-1]
        gains[df][0] = Cross_Sections_dict[nowOrbit] * v * Particle_number
        if nowOrbit in A_coefficients_dict:
            losses[df] = sum(A_coefficients_dict[nowOrbit].values())
            for finalstate, AC in A_coefficients_dict[nowOrbit].items():
                gains[index[finalstate]][df] += AC

    return gains, losses


def expm1_matrix(M, dt):
    '''
        Q = exp(M dt) - I を，単位行列を足さずに直接計算する．

        ゆっくり変化する準位(衝突前のイオン，基底状態，準安定状態)では exp(M dt) の対角がほぼ 1 になる．
        1 に近い数として持つと 1 ステップの変化量の下の桁が丸められ，その誤差が毎ステップ同じ向きに積もる．
        変化量 Q だけを持てば，小さい変化量もその大きさに見合った桁数で表せる．

        h = dt / 2^s と小さく取ってテイラー級数 Q(h) = M h + (M h)^2/2! + ... を求め，
        exp(2x) - 1 = 2(exp(x) - 1) + (exp(x) - 1)^2 を s 回使って Q(dt) に戻す．
    '''

    numberOfStates = len(M)
    norm = np.abs(M).sum(axis=0).max() * dt
    if norm == 0.0:
        return np.zeros((numberOfStates, numberOfStates))

    # ||M h|| <= 1 となるように刻みを 2^s 分の 1 にする
    doublings = max(0, int(math.ceil(math.log2(norm))))
    Mh = M * (dt / 2**doublings)

    # 新しい項が全ての要素で丸め誤差以下になったら打ち切る
    term = Mh.copy()
    Q = Mh.copy()
    for k in range(2, 200):
        term = term @ Mh / k
        Q += term
        if np.all(np.abs(term) <= np.finfo(float).eps * np.abs(Q)):
            break
    else:
        raise RuntimeError('exp(M h) - I のテイラー級数が収束しませんでした．')

    for i in range(doublings):
        Q = 2.0 * Q + Q @ Q

    return Q


def solve_rate_eqs_expm(f0, dt, numberOfSteps, gains, losses):
    '''
        レート方程式を行列指数で解く．
        係数が時間によらない線形の方程式なので，f(t + dt) = exp(M dt) f(t) が厳密に成り立つ．
        時刻 dt, 2dt, ..., numberOfSteps*dt の解を返す．

        丸め誤差を抑えるため，f(t + dt) = f(t) + Q f(t) (Q = exp(M dt) - I) の形で進め，
        足し込みには Kahan の補償付き加算を使う(加算で丸められた分を次のステップに繰り越す)．
    '''

    Q = expm1_matrix(gains - np.diag(losses), dt)

    f = np.array(f0, dtype=float)
    carry = np.zeros(len(f))
    times = dt * np.arange(1, numberOfSteps + 1)
    solution = np.empty((numberOfSteps, len(f)))
    for step in range(numberOfSteps):
        increment = Q @ f - carry
        updated = f + increment
        carry = (updated - f) - increment
        f = updated
        solution[step] = f

    return times, solution


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
        引数に与えられた衝突エネルギー[keV/u](核子あたりの運動エネルギー)を
        衝突速度[cm/s]に変換する関数．
        E = (1/2)mv^2 より v = sqrt(2E/m)．9.64854e7 は e/u [C/kg]．
    '''

    col_Energy_cms = math.sqrt(2*col_Energy_kVu*10**10*9.64854)*10**2

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
            self.popfig.plot(xaxisarray[::100], populations[::100, 0], label=self.orbits[0])

        for i in np.arange(1, len(populations[0])):
            self.popfig.plot(xaxisarray[::100], populations[::100, i], label='{0}'.format(self.orbits[i]), linestyle='-')

    def selectionPlot(self, xaxis, populations):
        for i, orbit in enumerate(self.orbits[:populations.shape[1]]):
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

        self.popfig.tick_params(axis='both', labelsize=20)
        self.popfig.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.popfig.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        self.popfig.xaxis.offsetText.set_fontsize(15)
        self.popfig.yaxis.offsetText.set_fontsize(15)
        scale_format = ptick.ScalarFormatter(useMathText=True)
        self.popfig.yaxis.set_major_formatter(scale_format)
        self.popfig.xaxis.set_major_formatter(scale_format)

        isshowlegend = input('凡例(legend)を表示しますか?[y|n] > ')
        if isshowlegend == 'y' or isshowlegend == 'Y':
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

def print_varsize():
    import types
    print('{}{: >15}{}{: >10}{}'.format('|','Variable Name', '|','  Size','|'))
    print('-----------------------------')
    for k, v in globals().items():
        if hasattr(v, 'size') and not k.startswith('_') and not isinstance(v, types.ModuleType):
            print('{}{: >15}{}{: >10}{}'.format('|',k,'|',str(v.size),'|'))
        elif hasattr(v, '__len__') and not k.startswith('_') and not isinstance(v.types.ModuleType):
            print('{}{: >15}{}{: >10}{}'.format('|', k, '|', str(len(v)), '|'))
