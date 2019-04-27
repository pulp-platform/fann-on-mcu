Copyright (c) 2018 ETH Zurich, Lukas Cavigelli, Xiaying Wang, Ferdinand von Hagen, Philipp Mayer, Michele Magno

# FANN-on-ARM: Optimized FANN Inference for ARM Cortex M-series

This repository contains optimized code to perform 
inference of FANN-trained neural network on the 
ARM Cortex M-series platform.  

Given a data file and pre-trained network in FANN's format, 
all necessary files to run and test the network on the 
microcontroller are generated. 

### Reference/Attribution
If this code is helpful for your research, please cite 
> M. Magno, L. Cavigelli, P. Mayer, F. von Hagen, L. Benini, "FANNCortexM: An Open Source Toolkit for Deployment of Multi-layer Neural Networks on ARM Cortex-M Family Microcontrollers", in Proc. IEEE WF-IoT, 2019.

### Prerequisites
You should have data and a pre-trained network in the FANN format. 
To run the script, python needs to be installed. 
This code has been tested with TI's MSP432 platform and ST's STM32L475VG.

### Usage
First, you need to export your data in the FANN default format
and train a neural network with FANN. How to do this is 
explained [here](http://leenissen.dk/fann/html/files2/gettingstarted-txt.html).
You should end up with two files, a `.data` file and a `.net` file. 
An example can be found in the `sample-data` folder.

Then, you can use the `generate.py` script to generate the 
files to run on the microcontroller, e.g. 
> python generate.py sample-data/myNetwork

Now all the *.h and *.c files can be copied to you project. 
They include all the data and code to run the network. 
To call it from your code, just include `fann.h` and call 
`fann_type *fann_run(fann_type * input);`, where
`fann_type` is `float` or `int` depending on whether you started
with a fixed-point model or not. Don't forget to include the files 
in your build scripts/makefile/project.

### Fixed-Point Remarks
FANN allows to train your model and export it in fixed-point format easily. 
After training with `fann_train_on_data` and potentially saving the 
floating-point model with `fann_save`, just run

```
decimal_point = fann_save_to_fixed(ann, "myNetwork_fixed.net");
```
You can also convert your training or test data to fixed-point representation this way: 

```
test_data = fann_read_train_from_file("./diabetes_test.data");
fann_save_train_to_fixed(test_data, "diabetes_test_fixed.data", decimal_point);
```
However, once you are running the code in-system, don't forget to rescale the input
data by scaling it accordingly: `int x_fixed = x * (1 << DECIMAL_POINT);`. The decimal point constant is provided through fann\_conf.h. 

Furthermore, make sure that the data on which you are previously training your full-precision network is scaled to the [-1,1] interval including a potential safety-margin and that this scaling is also applied during on-device data preparation. FANN's network quantization method assumes the data is normalized this way and quantizes using worst-case data scaling assumptions. Thus training the network or feeding it non-normalized data is likely to introduce overflows. 

### Performance Optimizations
The generator script makes sure your code runs efficiently on your ARM Cortex-M processor. However, depending on the circumstance you can optimize further, e.g. by removing the const attributes for the fann\_weights and fann\_neurons variables in the fann\_net.h file. Const variables are stored and read from flash, removing the const attribute moves them to the initialized\_rw/.data memory section in RAM whereby the values are copied from flash to RAM at boot-up. RAM is often a scarce resource, though, hence the default is to have these variables const. 

### File Description
Constant files:

- `generate.py`: the script generating the network and data-specific code files based an FANN-format data
- `fann_structs.h` and `fann.c`: contain the implementation of the NN building blocks.
- `fann.h`: the header file to be included in your code providing the `fann_type *fann_run(fann_type * input);` function declaration. 
- `sample-data/{myNetwork.net, myNetwork.data}`: sample data and network pre-trained with FANN. 
- `test.c`: contains a test iterating over the exported test data. Serves as an example for 2-class classification. 

Generated files:

- `fann_net.h`: contains the trained parameters and the network structure. 
- `fann_conf.h`: contains some more meta information on the network; #layers, fixed-point parameters (if applicable), ...
- `test_data.h`: contains the test input data and expected result


### License and Attribution
Please refer to the LICENSE file for the licensing of our code. 
We rely on the interfaces, specifications, and some code of the FANN project. 




