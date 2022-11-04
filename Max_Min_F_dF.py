import cv2
from matplotlib import pyplot as plt
import numpy as py
from skimage import io

import sys
import os.path

import scipy.ndimage

Colormap=['gray','Greys','summer','winter','hot','bone','hsv']

##########################################################   
argc_no = len(sys.argv)
if (argc_no < 2):
   print("No input!");
   print(" -i input file name");
   print(" -all (output all images)")
   print(" -ns (turn off the median filter smoothing)")           
   print(" -wmmf (generate a max(F)-min(F) image in PNG format")
   print(" -wmmdf (generate a differnece max-min image in PNG format")
   print(" -top (set the maximum percentile as the maximum (default=100)")          
   print(" -fmax xxx (the maximum display value for max_min(F)");
   print(" -fmin xxx (the minimum display value for max_min(F)");
   print(" -dfmax xxx (the maximum display value for max_min(dF)");
   print(" -dfmin xxx (the minimum display value for max_min(dF)");
   print(" -noblank turn off the blank checking procedure");
   exit()
################# Set parameters ################
input_file = " "

fmax = 0
fmin = 0
dfmax = 0
dfmin = 0

################# Switch to turn on/off the smoothing ##############
smoothing_sp = 1
write_mmf_sp = 0
write_mmdf_sp = 0
bar_sp = 0
all_sp = 0
noblank_sp =0

top_sp = 0
top_per = 100

L_st = 0
L_end = 0

######### Extract the input parameters from argv ###########
i=1

while (i<argc_no ):
   if (sys.argv[i] == "-i"):
      input_file = sys.argv[i+1]
      i += 2
   elif (sys.argv[i] == "-start"):
      L_st = (int)(sys.argv[i+1])
      i += 2
   elif (sys.argv[i] == "-end"):
      L_end = (int)(sys.argv[i+1])
      i += 2
   elif (sys.argv[i] == "-ns"):
      smoothing_sp = 0
      i += 1
   elif (sys.argv[i] == "-noblank"):
      noblank_sp = 1
      i += 1
   elif (sys.argv[i] == "-wmmf"):
      write_mmf_sp = 1
      i += 1
   elif (sys.argv[i] == "-wmmdf"):
      write_mmdf_sp = 1
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

par_str = ""
if (smoothing_sp == 1):
   par_str += ".sm"   ### sm: smoothing
else:
   par_str += ".ns"   ### ns: non-smoothing

if (noblank_sp == 1):
   par_str += ".nc"   ### nc: no blank check
else:
   par_str += ".cb"   ### nc: blank check

if top_sp ==0:
   par_str += ".p100" ### p: percentile
else:
   par_str += ".p"+str(top_per)

if (write_mmf_sp == 1):
   out_dff_file = input_file + par_str + ".Max_Min.png"

if (write_mmdf_sp == 1):
   out_dff_file = input_file + par_str + ".Max_Min_df.png"

if (all_sp == 1):
   out_dff_file = input_file + par_str + ".Max_Min.png"
   out_max_file = input_file + par_str + ".Max.png"
   out_min_file = input_file + par_str + ".Min.png"

   out_ddfdf_file = input_file + par_str + ".Max_Min_df.png"
   out_df_max_file = input_file + par_str + ".Max_df.png"
   out_df_min_file = input_file + par_str + ".Min_df.png"

images = io.imread(input_file)
length = images.shape[0]   # total video frame number 
for i in range(length):
   images[i] = (images[i]).astype(py.int32)
ROW, COL = images[0].shape

if L_end == 0:
   L_end = length

print("Start frame = ",L_st,"   end frame= ",L_end)

##################################################################################
### Keyboard pause
##################################################################################
the_key = None
def press(event):
   global the_key
   the_key = event.key

##################################################################################
### Denoising raw image frames by the median filter
##################################################################################

if (smoothing_sp == 1):
   print("Median filter smoothing\n")
   for i in range(L_st,L_end):
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

   for i in range(L_st,L_end):
      if (py.mean(py.abs(images[i])) < 5):
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

   print("Checking complete!")
####################################################################################

x=py.swapaxes(py.reshape(images,(length,ROW,COL)),0,2)
x= py.swapaxes(x,0,1)
print(x.shape)
print("Start frame = ",L_st,"   end frame= ",L_end)

IP_max = py.zeros((ROW,COL),dtype=py.int32)
IP_min = py.zeros((ROW,COL),dtype=py.int32)

for i in range(ROW):
   print("*",end="",flush=True)
   for j in range(COL):
      y = py.array(x[i][j][L_st:L_end])
      if top_sp == 0 :
         IP_max[i][j] = py.max(y)
         IP_min[i][j] = py.min(y)
      else:
         IP_max[i][j] = py.percentile(y,top_per)
         IP_min[i][j] = py.min(y)
         if IP_min[i][j] > IP_max[i][j]:
            IP_min[i][j] = IP_min[i][j]-(py.max(y)-IP_max[i][j])
print("")

all_max = py.max(IP_max)*1.1
all_min = py.min(IP_max)*0.9

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(F) "+ "("+par_str+")")
plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min)

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
plt.title(input_file+" Min(F)"+ "("+par_str+")")
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
plt.title(input_file+" Max(F)-Min(F)"+ "("+par_str+")")

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

if write_mmf_sp == 1 or all_sp == 1:
   plt.axis('off')
   plt.imsave(out_dff_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

####################################################################################
print("\n\nCalculating the differences between frames")

df_images = py.zeros((length,ROW,COL),dtype=int)

for i in range(L_st+1,L_end):
   df_images[i] = py.abs(images[i].astype('int32') - images[i-1].astype('int32'))

df_images[1] = df_images[2]
df_images[0] = df_images[1]
 
x=py.swapaxes(py.reshape(df_images,(length,ROW,COL)),0,2)
x= py.swapaxes(x,0,1)
print(x.shape)
print("Start frame = ",L_st,"   end frame= ",L_end)

for i in range(ROW):
   print("*",end="",flush=True)
   for j in range(COL):
      y = py.array(x[i][j][L_st:L_end])
      IP_max[i][j] = py.max(y)
      IP_min[i][j] = py.min(y)
print("")

all_max = py.max(IP_max)*1.1
all_min = py.min(IP_max)*0.9

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(|dF|)"+ "("+par_str+")")
plt.imshow(IP_max,cmap=plt.cm.hot,vmax=all_max,vmin=all_min) 

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
plt.title(input_file+" Min(dF)"+ "("+par_str+")")
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
   plt.imsave(out_df_min_file,IP_min,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)

IP_max=IP_max-IP_min

plt.figure(input_file,figsize=(8,6))
plt.title(input_file+" Max(dF)-Min(dF)"+ "("+par_str+")")

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

if write_mmdf_sp == 1 or all_sp==1:
   plt.axis('off')
   plt.imsave(out_ddfdf_file,IP_max,vmax=all_max,vmin=all_min,cmap=plt.cm.hot)
quit()

