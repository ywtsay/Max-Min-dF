# Max-Min-dF
A program for detecting calcium imaging by max-min intensity methods in Python. Calcium imaging has been widely applied to infer neuron activity in different brain regions in vivo. Following with several major kernel methods being developed, several state-of-art computational tools and pipelines for analyzing the calcium imaging video data have been proposed and the prediction results were usually shown over a “reference” image, such as the mean and local max-correlation images. However, these reference images sometime may not look like as the those shown in the original videos by visual inspection. Moreover, how to examine and select the neurons of interest from several hundreds or thousands of predicted candidates for further study may not be easy for users.
## Usage
```Python
python3 E0_Max_Min_dF_ddfF_deconv.py -all -i example.tif
```
## Argument
* -i  assign input file name or path
* 
