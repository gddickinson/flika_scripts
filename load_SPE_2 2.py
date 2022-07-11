import sys
sys.path.insert(0, r'C:\Users\georgedickinson\Dropbox\BSU\flika_scripts')

from pyWinSpec import SpeFile

SpeFile(r"C:\Users\georgedickinson\Desktop\thunderStorm analysis\002_dNAM-Exp01-wReg_100pM-100uL-30min_Mid-3nM-18mM-Mg 2019 March 04 11_10_26-raw.spe")

array = SpeFile(r"C:\Users\georgedickinson\Desktop\thunderStorm analysis\002_dNAM-Exp01-wReg_100pM-100uL-30min_Mid-3nM-18mM-Mg 2019 March 04 11_10_26-raw.spe").data

Window(array)