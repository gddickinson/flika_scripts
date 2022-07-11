from scipy import ndimage

#Synthetic data:
n = 10
l = 256
im = np.zeros((l, l))
points = l*np.random.random((2, n**2))
im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
im = ndimage.gaussian_filter(im, sigma=l/(4.*n))

original = Window(im, 'Original') 

mask = im > im.mean()

#Label connected components: ndimage.label:
label_im, nb_labels = ndimage.label(mask)
nb_labels # how many regions?

labelled = Window(label_im, 'Labelled') 

#Compute size, mean_value, etc. of each region:
sizes = ndimage.sum(mask, label_im, range(nb_labels + 1))
mean_vals = ndimage.sum(im, label_im, range(1, nb_labels + 1))

#Clean up small connect components:
mask_size = sizes < 1000
remove_pixel = mask_size[label_im]
remove_pixel.shape

label_im[remove_pixel] = 0
labelled2 = Window(label_im, 'Labelled2')   

#Now reassign labels with np.searchsorted:
labels = np.unique(label_im)
label_im = np.searchsorted(labels, label_im)

#Find region of interest enclosing object:
slice_x, slice_y = ndimage.find_objects(label_im==4)[0]
roi = im[slice_x, slice_y]
rois = Window(roi, 'ROIs')