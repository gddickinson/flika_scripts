fileName = r"C:\Users\George\Dropbox\UCI\puffDetection\testImage.tif"

open_file(fileName)

subtract(120)

#data_window=ratio(150,300,'average'); #ratio(first_frame, nFrames, ratio_type), now we are in F/F0

data_window = g.win

data_window.setName('Data Window dF/F0')

#butterworth_filter(1,.03,1,keepSourceWindow=True)

duplicate()
filtered_window = g.win
I = filtered_window.image #get current window image stack
window_length = 5
polyorder = 2
filtered = scipy.signal.savgol_filter(I, window_length, polyorder)
filtered_window.imageview.setImage(filtered)
filtered_window.setName('Data Window dF/F0 - Savgol Filtered')


ratio(100,100,'standard deviation')  #ratio(first_frame, nFrames, ratio_type), now the standard devation of the noise is 1.

norm_window=set_value(0,0,100) #to get rid of butterworth artifact at the beginning of the movie
norm_window=set_value(0,mt-150,mt-1) #to get rid of butterworth artifact at the end of the movie
norm_window.setName('Normalized Window')

blurred_window=gaussian_blur(2, norm_edges = True)