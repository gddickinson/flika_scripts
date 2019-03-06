# Instructions:
# First, open a window.
# Trim the window in time.
# Then black level subtract: 90 for LLS, 520 for TIRF. 
# Set parameters.
# Run script.

####################################
###      Set post-filter type	####
####################################
#postFilterType = 'butterworth'
postFilterType = 'savgol'


################################
####    Parameters  ############
################################
sigma = 2 				# Change this number if you want to vary the sigma of the gaussian blur
sampling_interval = 10  # frame duration in ms
q = 0.06  				# for LLS: 10ms frame duration, q=0.02; 20ms frame duration, q=0.05
             			# for TIRF: 10ms frame duration, q=0.1902

#Butterworth filter options
low_cutoff = 1  	# Hz
high_cutoff = 20  	# Hz
filter_order = 3  	# Increasing filter order increases the steepness of the filter rolloff

#Sav-Gol filter options
window_length = 21	# The length of the filter window (i.e. the number of coefficients). Must be a positive odd integer.
polyorder = 5 		# The order of the polynomial used to fit the samples. polyorder must be less than window_length.

#Convolution filter options
boxcar_width = 150  # boxcar width in terms of ms


#######################################
## Run after specifying parameters  ###
#######################################
from scipy.ndimage.filters import convolve
sampling_rate = 1/(sampling_interval/1000)  # in Hz

try:
    assert high_cutoff <= .5 * sampling_rate
except AssertionError:
    print('High Frequency Cutoff is above the Nyquist frequency. Lower your high frequency cutoff')

high_cutoff_scaled = high_cutoff / (sampling_rate/2)
low_cutoff_scaled = low_cutoff / (sampling_rate/2)
boxcar_frames = int(np.round(boxcar_width / sampling_interval))

#For testing
#A = np.sqrt(10) * np.random.randn(10000, 10,10) + 10
#Window(A, 'original image')

nFrames = g.win.mt
prefilter = gaussian_blur(sigma, keepSourceWindow=True)

A = prefilter.image

if postFilterType == 'butterworth':
    postfilter = butterworth_filter(filter_order, low_cutoff_scaled, high_cutoff_scaled, keepSourceWindow=True)
    B = postfilter.image

prefilter.close()
#postfilter.close()
Window(A, 'original image -> gaussian blur')

if postFilterType == 'savgol':

    if window_length % 2 != 1 or window_length < 1:
        raise TypeError("window_length size must be a positive odd number")

    if window_length < polyorder + 2:
        raise TypeError("window_length is too small for the polynomials order")

    B = scipy.signal.savgol_filter(A, window_length, polyorder, axis=0) 
    Window(B, 'original image -> gaussian blur -> savgol filtered')


mean_A = convolve(A, weights=np.full((boxcar_frames,1,1),1.0/boxcar_frames))
mean_B = convolve(B, weights=np.full((boxcar_frames,1,1),1.0/boxcar_frames))

B2 = B**2  # B squared
mean_B2 = convolve(B2, weights=np.full((boxcar_frames,1,1),1.0/boxcar_frames))
variance_B = mean_B2 - mean_B**2
stdev_B = np.sqrt(variance_B)

mean_A[mean_A<0] = 0 #removes negative values

Window(stdev_B - np.sqrt(q*mean_A), 'stdev minus sqrt mean')