import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import random

plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)
# Example data



x = np.array([0, 20, 30, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300,320, 340, 360, 380, 400, 420, 440])
y1 = np.array([float(0.93), float(0.81), float(0.83), float(0.85), float(0.64), float(0.37), float(0.38), float(0.23), float(0.14) , float(0.11), float(0.10), float(0.09), float(0.13), float(0.11), float(0.08), float(0.09), float(0.09), float(0.1), float(0.10), float(0.07), float(0.07), float(0.05), float(0.06), float(0.04)])
y2 = np.array([float(0.93), float(0.64),float(0.43), float(0.22), float(0.15), float(0.10), float(0.08), float(0.07), float(0.05) , float(0.06), float(0.05), float(0.04), float(0.05), float(0.04), float(0.03), float(0.05), float(0.04), float(0.03), float(0.04), float(0.02), float(0.03), float(0.02), float(0.03), float(0.02)])
#y1 = np.array([64, 22, 18, 14, 9, 8, 7, 5, 5, 4, 4, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0])
#y2 = np.array([652, 54, 48, 48, 46, 43, 44, 40, 39, 39, 39, 38, 38, 38, 37, 35, 34, 34, 33, 32, 32, 31, 31, 31])
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
#x_smooth = np.linspace(x.min(), x.max(), 4, endpoint=True)
#y_smooth = interp1d(x, y, kind='linear')(x_smooth)
plt.xlim(0, x.max())
plt.ylim(0, 1)
plt.xlabel(r'\textit{Generation}',fontsize=12)
plt.ylabel(r'\textit{Diversity}',fontsize=12)
plt.title(r'Diversity at each generation for \textbf{dsjc250.1}',fontsize=14)
# Make room for the ridiculously large title.
#plt.subplots_adjust(top=0.8)
plt.plot(x, y1, 'black', linestyle=':', label='Genetic-tabu algorithm')
plt.plot(x, y2, 'red', linestyle=':', label='Genetic-SA algorithm')
plt.legend()

plt.show()