import sys

class File(object):

    def __init__(self, fname):
        self._fid = open(fname, 'rb')
        self._load_size()

    def _load_size(self):
        self._xdim = np.int64(self.read_at(42, 1, np.int16)[0])
        self._ydim = np.int64(self.read_at(656, 1, np.int16)[0])

    def _load_date_time(self):
        rawdate = self.read_at(20, 9, np.int8)
        rawtime = self.read_at(172, 6, np.int8)
        strdate = ''
        for ch in rawdate :
            strdate += chr(ch)
        for ch in rawtime:
            strdate += chr(ch)
        self._date_time = time.strptime(strdate,"%d%b%Y%H%M%S")

    def get_size(self):
        return (self._xdim, self._ydim)

    def read_at(self, pos, size, ntype):
        self._fid.seek(pos)
        return np.fromfile(self._fid, ntype, size)

    def load_img(self):
        img = self.read_at(4100, self._xdim * self._ydim, np.uint16)
        return img.reshape((self._ydim, self._xdim))

    def close(self):
        self._fid.close()

def load(fname):
    fid = File(fname)
    img = fid.load_img()
    fid.close()
    return img

img = load(r"C:\Users\georgedickinson\Desktop\thunderStorm analysis\002_dNAM-Exp01-wReg_100pM-100uL-30min_Mid-3nM-18mM-Mg 2019 March 04 11_10_26-raw.spe")