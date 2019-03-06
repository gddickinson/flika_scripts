from flika.utils.io import tifffile
from flika.process.file_ import get_permutation_tuple

filename = r"C:\Users\George\Dropbox\UCI\multiColor\2bin_200slices_0.11slicestep_single_MMStack_Pos0.ome.tif"

Tiff = tifffile.TiffFile(str(filename))

A = Tiff.asarray()
Tiff.close()
axes = [tifffile.AXES_LABELS[ax] for ax in Tiff.series[0].axes]
target_axes = ['channel','depth', 'width', 'height']
perm = get_permutation_tuple(axes, target_axes)
A = np.transpose(A, perm)

B = A[0]
C = A[1]

channel_1 = Window(B,'Channel 1')
channel_2 = Window(C,'Channel 2')