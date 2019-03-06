from subprocess import Popen, PIPE, STDOUT 

## test command: python volumeViewConverter.py C:\Users\George\Desktop\testRun\george_1color C:\Users\George\Desktop\testRun\results2 200 1 45 False False False False 1

scriptPath = "C:\\Users\\George\\.FLIKA\\plugins\\onTheFly_Reconstruction\\volumeViewConverter.py"

recordingFolder = "C:\\Users\\George\\Desktop\\testRun\\george_1color"
exportFolder = "C:\\Users\\George\\Desktop\\testRun\\results2"  
nSteps = "200"
shift_factor = "1"
theta = "45"
triangle_scan = "False"
interpolate = "False"
trim_last_frame = "False"
zscan = "False"
nChannels = "1"

volume = "2"

args = nSteps + ' ' + shift_factor + ' ' + theta + ' ' + triangle_scan + ' ' + interpolate + ' ' + trim_last_frame + ' ' + zscan + ' ' + nChannels + ' ' + volume + ' ' + recordingFolder + ' ' + exportFolder


cmd = 'python' + ' ' + scriptPath + ' ' + args
#cmd = 'python' + ' ' + scriptPath

p = Popen(cmd)

#to get widow output
#p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)      
#output = p.stdout.read() 
#print (output)