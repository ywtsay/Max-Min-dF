import cv2
from matplotlib import pyplot as plt
import time
import numpy as py
from numpy import linalg as LA
import sys
"""
from scipy.signal import find_peaks, peak_prominences
from scipy import signal
"""
from scipy.signal import convolve2d
from skimage import color, data, restoration

import math
from skimage import io
import os.path

import scipy.ndimage

Colormap=['gray','Greys','summer','winter','hot','bone','hsv']

##########################################################   
argc_no = len(sys.argv)
if (argc_no < 2):
   print("No input!");
   print(" -i input file name");
   print(" -all (output all images)")
   print(" -ns (no parameter to turn off the median filter smoothing)")           
   print(" -out (generate a max(F)-min(F) image in PNG format")
   print(" -wdff (generate a max(F)-min(F) image in PNG format")
   print(" -wddfdf (generate a differnece max-min image in PNG format")
   print(" -top (set the maximum percentile as the maximum (default=100)")          
   print(" -fmax the maximum display value for max_min(F)");
   print(" -fmin the minimum display value for max_min(F)");
   print(" -dfmax the maximum display value for max_min(dF)");
   print(" -dfmin the minimum display value for max_min(dF)");
   print(" -noblank turn off the blank checking procedure");
   exit()
################# Set parameters ################
input_file = " "

fmax = 0
fmin = 0
dfmax = 0
dfmin = 0

minT = 0
window_size = 1000

start_frame = 0
end_frame = -1 

################# Switch to turn on/off the smoothing ##############
smoothing_sp = 1
write_dff_sp = 0
write_ddfdf_sp = 0
write_video_sp = 0
bar_sp = 0
all_sp = 0
noblank_sp =0
top_sp = 0
top_per = 100
######### Extract the input parameters from argv ###########
i=1

while (i<argc_no ):
   if (sys.argv[i] == "-i"):
      input_file = sys.argv[i+1]
      i += 2
   elif (sys.argv[i] == "-ns"):
      smoothing_sp = 0
      i += 1
   elif (sys.argv[i] == "-noblank"):
      noblank_sp = 1
      i += 1
   elif (sys.argv[i] == "-out"):
      write_dff_sp = 1
      i += 1
   elif (sys.argv[i] == "-wdff"):
      write_dff_sp = 1
      i += 1
   elif (sys.argv[i] == "-wddfdf"):
      write_ddfdf_sp = 1
      i += 1
   elif (sys.argv[i] == "-all"):
      all_sp = 1
      i += 1
   elif (sys.argv[i] == "-top"):
      top_per = int(sys.argv[i+1])
      top_sp = 1
      i += 2
   elif (sys.argv[i] == "-bar"):
      bar_sp = 1
      i += 1
   elif (sys.argv[i] == "-fmax"):
      fmax = int(sys.argv[i+1])
      i += 2
   elif (sys.argv[i] == "-fmin"):
      fmin = int(sys.argv[i+1])
      i += 2
   elif (sys.argv[i] == "-dfmax"):
      dfmax = int(sys.argv[i+1])
      i += 2
   elif (sys.argv[i] == "-dfmin"):
      dfmin = int(sys.argv[i+1])
      i += 2
   else:
      i += 2
##################################################################################
###    Check input parameters ###########
##################################################################################
if (input_file == " "):
    print("No input")
    exit()

if (write_dff_sp == 1):
   out_dff_file = input_file + ".Max_Min.dff.png"
if (write_ddfdf_sp == 1):
   out_ddfdf_file = input_file + ".Max_Min.ddfdf.png"

if (all_sp == 1):
   out_dff_file = input_file + ".Max_Min.dff.png"
   out_max_file = input_file + ".Max.png"
   out_min_file = input_file + ".Min.png"

   out_ddfdf_file = input_file + ".Max_Min.ddfdf.png"
   out_df_max_file = input_file + ".Max_ddf.png"
   out_df_min_file = input_file + ".Min_ddf.png"

images = io.imread(input_file)
length = images.shape[0]   # total video frame number 
for i in range(length):
   images[i] = (images[i]).astype(py.int32)
ROW, COL = images[0].shape

##################################################################################
### Keyboard pause
##################################################################################
the_key = None
def press(event):
   global the_key
   the_key = event.key

##################################################################################
### Denoising raw image frames by the median filter
### scipy.ndimage.median_filter: too slow
###   images[i] = scipy.ndimage.median_filter(images[i],size=5)
### 
##################################################################################
if (smoothing_sp == 1):
   print("Median filter smoothing\n")
   for i in range(length):
      images[i] = cv2.medianBlur(images[i],5)
else:
   print("No smoothing\n")

####################################################################################
### Check blank frame and replace by the last non-blank one
####################################################################################
if (noblank_sp == 1):
   print("No checking blank frame procedure!")
else:
   print("Check blank?")
   blank_list = [] 
   Too_bright_list = []

   for i in range(length):
      if (py.mean(images[i]) < 5):
         print("The ",i,"th frame is blank!")
         blank_list.append(i)
   if (len(blank_list)==0):
      print("No blank frame\n")
   else:
      for i in range(len(blank_list)):
         j = blank_list[i-1]
         if j == length-1:
            images[j] = images[j-1]
         else:
            images[j] = images[j+1]
   """
   max_int = py.max(images)
   for i in range(length):
      if (py.mean(images[i]) > 0.85*max_int):
         print("The ",i,"th frame is whole bright!")
         Too_bright_list.append(i)
   if (len(Too_bright_list)==0):
      print("No too bright frame\n")
   else:
      for i in range(len(Too_bright_list)):
         j = Too_bright_list[i-1]
         if j == length-1:
            images[j] = images[j-1]
         else:
            images[j] = images[j+1]
   """
   print("Checking complete!")
####################################################################################
x=py.swapaxes(py.reshape(images,(length,ROW,COL)),0,2)
x= py.swapaxes(x,0,1)
print(x.shape)

IP_max = py.zeros((ROW,COL),dtype=py.int32)
IP_min = py.zeros((ROW,COL),dtype=py.int32)

for i in range(ROW):
   print("*",end="",flush=True)
   for j in range(COL):
      y = py.array(x[i][j][:])
      if top_sp == 0 :
         IP_max[i][j] = py.max(y)
         IP_min[i][j] = py.min(y)
      else:
         IP_max[i][j] = py.percentile(y,top_per)
         IP_min[i][j] = py.min(y)
         if IP_min[i][j] > IP_max[i][j]:
            IP_min[i][j] = IP_min[i][j]-(py.max(y)-IP_max[i][j])
print("")
"""
IP_max = scipy.ndimage.median_filter(IP_max,size=5)
IP_min = scipy.ndimage.median_filter(IP_min,size=5)
"""
all_max = py.max(IP_max)*1.1
all_min = py.min(IP_max)*0.9

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(F)")
plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min)
##plt.imshow(IP_max,cmap=plt.cm.hot)
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")
plt.waitforbuttonpress()
plt.close()

if (all_sp == 1):
   plt.axis('off')
   plt.imsave(out_max_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Min(F)")
plt.imshow(IP_min,cmap=plt.cm.hot,vmax=all_max,vmin=all_min)
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")
plt.waitforbuttonpress()
plt.close()
if (all_sp == 1):
   plt.axis('off')
   plt.imsave(out_min_file,IP_min,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

IP_max = IP_max - IP_min

all_max = py.max(IP_max)*1.1
all_min = py.min(IP_max)*0.9

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(F)-Min(F)")
if fmax > 0:
   plt.imshow(IP_max,cmap=plt.cm.hot,vmax=fmax,vmin=fmin)
else:
   plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min)
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")

plt.waitforbuttonpress()
plt.close()

#########################################################################
### Image Deconvolution
### Ref: https://scikit-image.org/docs/dev/auto_examples/filters/plot_deconvolution.html
#########################################################################

dff_file = input_file + ".Max_Min.diff.enhanced.png"
plt.axis('off')
plt.imsave(dff_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

from PIL import Image
from PIL import ImageEnhance
img=Image.open(dff_file)    # Opening Image
img_shr_obj=ImageEnhance.Sharpness(img)
factor=5    # Specified Factor for Enhancing Sharpness
e_i=img_shr_obj.enhance(factor)    #Enhances Image
"""
e_i.show()   # Shows Enhanced Image
"""
plt.figure(input_file,figsize=(8,6))
plt.title(input_file+"ImageEnhance.Sharpness of Max(F)-Min(F)")
plt.imshow(e_i,cmap=plt.cm.hot)
plt.waitforbuttonpress()
plt.close()

e_i.save(dff_file)

if write_dff_sp == 1 or all_sp == 1:
   plt.axis('off')
   plt.imsave(out_dff_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

####################################################################################
print("\n\nCalculating the differences between frames")

df_images = py.zeros((length,ROW,COL),dtype=int)
for i in range(1,length):
   df_images[i] = py.abs(images[i].astype('int32') - images[i-1].astype('int32'))
   ## df_images[i] =images[i+1].astype('int32')- images[i].astype('int32')

df_images[1] = df_images[2]
df_images[0] = df_images[1]
 
x=py.swapaxes(py.reshape(df_images,(length,ROW,COL)),0,2)
x= py.swapaxes(x,0,1)
print(x.shape)

for i in range(ROW):
   print("*",end="",flush=True)
   for j in range(COL):
      y = py.array(x[i][j][:])
      IP_max[i][j] = py.max(y)
      IP_min[i][j] = py.min(y)
print("")
"""
IP_max = scipy.ndimage.median_filter(IP_max,size=5)
IP_min = scipy.ndimage.median_filter(IP_min,size=5)
"""
all_max = py.max(IP_max)*1.1
all_min = py.min(IP_max)*0.9

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(|dF|)")
plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min) 
##plt.imshow(IP_max,cmap=plt.cm.hot) 
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")
plt.waitforbuttonpress()
plt.close()

if (all_sp == 1):
   plt.axis('off')
   plt.imsave(out_df_max_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Min(dF)")
plt.imshow(IP_min,cmap=plt.cm.hot,vmax=all_max,vmin=all_min) 
#plt.imshow(IP_min,cmap=plt.cm.hot) 
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")
plt.waitforbuttonpress()
plt.close()
if (all_sp == 1):
   plt.axis('off')
   plt.imsave(out_df_min_file,IP_min,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

IP_max=IP_max-IP_min

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(dF)-Min(dF)")
if dfmax >0:
   plt.imshow(IP_max,cmap=plt.cm.hot,vmax=dfmax,vmin=dfmin)
else:
   plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min) 
if (bar_sp >0):
   if (ROW == COL):
      plt.colorbar()
   else:
      plt.colorbar(orientation="horizontal")
plt.waitforbuttonpress()
plt.close()

if write_ddfdf_sp == 1 or all_sp==1:
   plt.axis('off')
   plt.imsave(out_ddfdf_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)
quit()

