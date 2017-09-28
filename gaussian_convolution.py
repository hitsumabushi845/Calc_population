import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ptick
import pandas as pd
from Calc_Populations_funcs_ECCSjson import selectFile

def gaussian_convolution():
    print('スペクトルのデータファイルを選んでください．')
    datafilename = selectFile('./spectrumdatafiles')

    spectrumdata = pd.read_csv(datafilename,header=None)
    spectrumdata = spectrumdata.values

    print('半値幅を入力してください．')
    fwhm = float(input())
    sigma = fwhm/2.35482    # sigma = FWHM/(2*sqrt(2*ln(2))) 

    wavelengthrange = np.arange(0.0,spectrumdata[-1][1]+spectrumdata[-1][1]*0.1,0.01)
    gaussianspectrum = 0 * wavelengthrange

    for spectrum in spectrumdata:
        gaussian = spectrum[0] * np.exp(-(wavelengthrange-spectrum[1])**2/(2*(sigma**2)))
        gaussianspectrum += gaussian
        

    gaussianfigure = plt.figure(figsize=(16,9))
    gaussianfigure = gaussianfigure.add_subplot(1,1,1)
    gaussianfigure.set_xlabel('Wavelength / nm', fontsize=25)
    gaussianfigure.set_ylabel('Intensity / arb. units', fontsize=25)

    
    for tick in gaussianfigure.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    for tick in gaussianfigure.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)
    gaussianfigure.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    gaussianfigure.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
    gaussianfigure.xaxis.offsetText.set_fontsize(15)
    gaussianfigure.yaxis.offsetText.set_fontsize(15)
    scale_format = ptick.ScalarFormatter(useMathText=True)
    gaussianfigure.yaxis.set_major_formatter(scale_format)
    gaussianfigure.xaxis.set_major_formatter(scale_format)
    plt.tight_layout()

    gaussianfigure.plot(wavelengthrange, gaussianspectrum)
    plt.show()


if __name__ == '__main__':
    gaussian_convolution()
