import numpy as np
import json
import sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from Calc_Populations_funcs import *


def plot_spectrum_from_population():

    Hlike = ['O8+','N7+','C6+']
    Helike = ['O7+','N6+','C5+']
    Lilike = ['O6+','N5+','C4+']

    print('スペクトルをプロットするデータファイルを選んでください．')
    datafilename = selectFile('./datafiles')

    Collision_system = datafilename.split('_')[2]
    print(Collision_system)
    if Collision_system[:3] in Hlike:
        ACfile = open('./ACtoPlotSpectrum/ChiantiAC_{0}_Hlike.json'.format(Collision_system[0]))
        orbitfile = open('./orbits_Hlike.txt')
        Energyfile = open('./EnergyLevels/EnergyLevel_{0}_Hlike.json'.format(Collision_system[0]))
    elif Collision_system[:3] in Helike:
        ACfile = open('./ACtoPlotSpectrum/ChiantiAC_{0}_Helike.json'.format(Collision_system[0]))
        orbitfile = open('./orbits_Helike.txt')
        Energyfile = open('./EnergyLevels/EnergyLevel_{0}_Helike.json'.format(Collision_system[0]))
    elif Collision_system[:3] in Lilike:
        ACfile = open('./ACtoPlotSpectrum/ChiantiAC_{0}_Lilike.json'.format(Collision_system[0]))
        orbitfile = open('./orbits_Lilike.txt')
        Energyfile = open('./EnergyLevels/EnergyLevel_{0}_Lilike.json'.format(Collision_system[0]))
    else:
        print('undefined ion type.')
        sys.exit()
    ACdict = json.load(ACfile)
    orbits = [i.rstrip('\n') for i in orbitfile.readlines()]
    Energydict = json.load(Energyfile)
    data = np.loadtxt(datafilename,delimiter=',')

    print('スペクトルをプロットするポイントを指定してください．({0} - {1})'.format(data[0][0],data[-1][0]))
    plotpoint = float(input())

    dt = 4.55e-9

    for i,pops in enumerate(data):
        if pops[0] >= plotpoint:
            plotindex = i
            break
    #print(data[plotindex])

    poplations = data[plotindex,2:]
    popdict = {}

    for i in range(0,len(poplations)):
        popdict[orbits[i]] = poplations[i]

    #print(popdict)
    
    spectrum_list = []

    for key, val in popdict.items():
        if key in ACdict:
            for fin, AC in ACdict[key].items():
                #print('{0} to {1} : val*BR = {2}, Energy = {3}'.format(key,fin,(val*BR),(Energydict[key]-Energydict[fin])))
                spectrum_list.append([(val*AC*dt),(Energydict[key]-Energydict[fin])])

    #print(spectrum_list)
    spectrum = np.array(spectrum_list)

    print(spectrum_list)

    #specdatafilename = input('スペクトルデータを保存するファイル名を入力してください．> ')
    #specdatafile = open(specdatafilename,'w')
    #np.savetxt(specdatafile, spectrum_list, delimiter=',')

    fig = plt.figure(figsize=(16,9))
    esp = fig.add_subplot(1,1,1)
    esp.stem(spectrum[:,1],spectrum[:,0])
    esp.set_xlabel('Energy[eV]', fontsize=30)
    esp.set_ylabel('Intensity', fontsize=27)
    esp.tick_params(labelleft='off')
    for tick in esp.xaxis.get_major_ticks():
        tick.label.set_fontsize(23)
    for tick in esp.yaxis.get_major_ticks():
        tick.label.set_fontsize(23)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    plot_spectrum_from_population()
