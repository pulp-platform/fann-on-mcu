#!/usr/bin/env python
#!/usr/bin/env python
# coding: utf-8

import os
import serial
import sys, argparse
from struct import *
import csv
from collections import OrderedDict
import time

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of csv file where to save the measurements')
    parser.add_argument('--activation', dest='activ', default=True, action='store_true', help='Only for performance measurement purpose. It sets the ACTIVATIONS.')
    parser.add_argument('--no-activation', dest='activ', action='store_false', help='Only for performance measurement purpose. It ignores the ACTIVATIONS, i.e. no activation functions will be applied.')
    args = parser.parse_args()

    if args.input == None:
        parser.error("Missing input filename to save the data. --help for more details.")
    else:
        dict['fname'] = args.input
    
    dict['activ'] = args.activ

    return dict

def modify_train_c(N_in=100, N_out=8, list_n_neurons=None, orig_file=None):

    """
    Adds hidden layers in train.c (perftest_train.c) file to automatically train networks with variable number of layers.
    Takes as input number of hidden layers.
    """

    orig_file = open(orig_file)
    n_layers = len(list_n_neurons)

    start_token = 'main'
    stop_token = 'return'
    start_found = 0
    start2_found = 0
    saveString = "/* Automatically generated train.c file */\n"


    while True:

        line = orig_file.readline()
        saveString = saveString + line
        line_split=line.split()


        if len(line_split) == 0:# and start_found == 0:
            continue

        if (line_split[0] == 'int' and line_split[1]==start_token and start_found == 0):
            start_found=1
            print("start found\n")

        # if start_found == 0:
        #     continue

        # if line_split[0] == stop_token and start_found == 1:
        #     start_found = 0

        if line_split[0] == 'const' and line_split[1] == 'unsigned' and line_split[2] == 'int':
            start2_found = 1

        if start2_found == 1 and line_split[0] != 'const':
            start2_found = 0

        if start_found == 1 and start2_found == 1 and line_split[3] == 'num_input':
            saveString = saveString[:-3] + str(N_in) + ';\n'

        if start_found == 1 and start2_found == 1 and line_split[3] == 'num_output':
            saveString = saveString[:-3] + str(N_out) + ';\n'

        if start_found == 1 and start2_found == 1 and line_split[3] == 'num_layers':
            saveString = saveString[:-3] + str(n_layers+1+1) + ';\n' # FANN
            # counts also the input layer as a layer!

        if start_found == 1 and start2_found == 1 and line_split[3] == 'num_neurons_hidden':
            # Add hidden layers up to n_layers
            for i in range(n_layers):
                if i == 0:
                    # Number of neurons of the first hidden layer
                    saveString = saveString[:-6] + str(i) + ' = ' + str(list_n_neurons[i]) + ';\n'
                else:
                    saveString = saveString + line[:-6] + str(i) + ' = ' + str(list_n_neurons[i]) + ';\n'

        if start_found == 1 and line_split[0] == 'ann':
            #print(line)
            saveString = saveString[:-33]
            #print(saveString[:-33] + 'num_neurons_hidden' + str(i))
            for i in range(n_layers):
                saveString = saveString + 'num_neurons_hidden' + str(i) + ', '
            saveString = saveString + 'num_output);'

        if start_found == 1 and line_split[0] == stop_token:
            break

    orig_file.close()
    saveString = saveString + '\n}'

    try:
        FW = open("./perftest_train.c", "w")
        FW.write(saveString)
        FW.close()
    except IOError:
        print("Could not open write fann_conf.h")
        exit(1)


def decode(port=None, baudrate = 115200, bytesize=8, savedata=None):

    perf_dict = savedata

    #Initialize serial port for reading
    ser=serial.Serial(port = comport, baudrate=baudrate, bytesize=bytesize)
    ser.flushInput()

    #Initialize file to store data: Look for a file called "test_data.csv" and create it if it does not exist; Overwrite data in file ("w")
    ser.reset_input_buffer()
    #f=open("TestLogging_dummy2","w")
    #counter = 0

    print("Decoding")

    while True:
        try:
            ser.read_until(b'####')
            line = ser.readline().decode("utf-8")
            print(line)
            line_split = line.split()
            #print(line_split)

            if line_split[0] == "break":
                break

            if line_split[0] in perf_dict:
                #           print("key exists\n")
                perf_dict[line_split[0]].append(int(line_split[1]))
               #           print(perf_dict)
            else:
                #           print("key doesn't exists\n")
                perf_dict[line_split[0]] = [int(line_split[1])]

            #print(perf_dict)

        except KeyboardInterrupt:
            break

    return perf_dict

    #f.close() #...actually code never reaches this point ^^

def decode_clear(port=None, baudrate = 115200, bytesize=8):

    #Initialize serial port for reading
    ser=serial.Serial(port = comport, baudrate=baudrate, bytesize=bytesize)
    ser.flushInput()

    #Initialize file to store data: Look for a file called "test_data.csv" and create it if it does not exist; Overwrite data in file ("w")
    ser.reset_input_buffer()
    #f=open("TestLogging_dummy2","w")
    counter = 0

    print("Decoding clear")

    while True:
        try:
            ser.read_until(b'####')
            line = ser.readline().decode("utf-8")
            print(line)
            line_split = line.split()
            #print(line_split)

            if line_split[0] == "break":
                break

            counter += 1

            if counter > 1000:
                break
            #print(perf_dict)

        except KeyboardInterrupt:
            break

    return perf_dict



if __name__ == '__main__':

    """
    Runs generate.py
    Compiles and flashes into the board (ARM Cortex)
    Reads from serial port and decodes the data
    Saves the data into a csv file given as input with -i
    """

    args_dict = get_args();

    # change directory to FANN-on-MCU
    os.chdir("../..")
    homedir = os.getcwd()

    N_test = 1 # Number of test samples
    # for averaging performance use NUM_REPEAT in main.c file

    # Number of input features and num neurons in output layer
    N_in = 100
    N_out = 8

    os.chdir(homedir+"/perf/arm-vs-num-layers")
    # Generate stimuli, i.e. generate data (float) used for training
    os.system("python3 gen_stimuli.py generated_data/perftest {} {} {}".format(N_test, N_in, N_out))

    # For reading the measurements from serial port
    comport = '/dev/ttyACM0'
    baudrate = 115200
    bytesize = 8

    # Save the measurements
    perf_dict = OrderedDict()
    perf_dict["num_hidden_layers"] = []

    decode_clear(port=comport, baudrate=baudrate, bytesize=bytesize)

    for n_layers in range(1, 41, 1):
        print("n_layers {}".format(n_layers))

        perf_dict["num_hidden_layers"].append(n_layers)

        # Compute the ranges for the list with number of neurons for every layer
        min_n_neurons = 8
        n_neurons_step = 8
        max_n_neurons = min_n_neurons + int((n_layers - 1)*n_neurons_step/2) + 1

        list_n_neurons = []
        for i in range(min_n_neurons, max_n_neurons, n_neurons_step):
            list_n_neurons.append(i)
            list_n_neurons.append(i)
        list_n_neurons = list_n_neurons[:n_layers]
        print(list_n_neurons)

        os.chdir(homedir+"/perf/arm-vs-num-layers")
        # Generate train.c depending on the number of hidden layers
        orig_file = "./perftest_train_orig.c"
        modify_train_c(N_in=N_in, N_out=N_out, list_n_neurons=list_n_neurons, orig_file=orig_file)

        # In Mr. Wolf, L2 shared memory is 448KB.
        # Estimate the size used in L2 as function of number of hidden layers:
        # - input_data: N_test * N_in = Number of test samples saved in L2 * sizeof(datatype)
        # - fann_neurons: N_neurons [n_in + 1 + n_out + 1 of each layer] * sizeof(datatype) * 4 [i.e. int, int, fann_type, enum fann_activationfunc_enum]
        # - fann_weights: ((n_in + 1) * n_out) of each layer * sizeof(datatype)
        # - fann_layers: Number of layers (hidden + output) * 2 * sizeof(datatype)
        # - neuron_values[NUM_NEURONS]: Number of total neurons [n_in + 1 + n_out
        # + 1 of each layer] * sizeof(datatype)
        L2_size_estm = 4*N_in*N_test + (n_layers + 1) * 2 * 4
        n_tot_neurons = 0
        for layer_i in range(0, len(list_n_neurons)-1, 1):
            L2_size_estm = L2_size_estm + 4 * (list_n_neurons[layer_i] + 1) * list_n_neurons[layer_i+1]
            n_tot_neurons = n_tot_neurons + (list_n_neurons[layer_i] + 1 + list_n_neurons[layer_i+1]+1)
        L2_size_estm = L2_size_estm + n_tot_neurons * 4 * 4 + n_tot_neurons * 4
        print(L2_size_estm)
        if L2_size_estm  > 400000:
            print(L2_size_estm)
            continue


        os.system("sleep 3")
        os.system("make clean all onlytrain &>/dev/null")
        os.system("sleep 3")
        #print("---- \t ---- \t ---- \t ----\n\n")

        # run on arm
        os.chdir(homedir)

        #print("#### run on arm");
        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        #print("I am here! " + homedir)
        if args_dict["activ"]: # True, i.e. use activation
            os.system("python3 generate.py -i ./perf/arm--vs-num-layers/perftest_fixed -p arm")
        else:
            os.system("python3 generate.py -i ./perf/arm-vs-num-layers/perftest_fixed -p arm --no-activation")

        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        os.system("mv -f ./output/*.c -t ./stm32l475-onDeviceTest-linux/Src")
        os.system("mv -f ./output/*.h -t ./stm32l475-onDeviceTest-linux/Inc")
        os.system("sleep 2")
        os.chdir("./stm32l475-onDeviceTest-linux/")
        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        os.system("make")
        os.system("make flash")

        #os.system("sleep 1")

        # Start the decode of the data from serial port and save to dictionary
        os.chdir(homedir+"/perf/arm-vs-num-layers")
        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        perf_dict_tmp = decode(port=comport, baudrate=baudrate, bytesize=bytesize, savedata=perf_dict)
        perf_dict.update(perf_dict_tmp)
        #os.chdir(homedir+"/stm32l475-onDeviceTest-linux/")
        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        #os.system("make flash")
        #print("\n"+os.getcwd())
        #print("---- \t ---- \t ---- \t ----\n\n")

        print(perf_dict)

        #os.system("sleep 1")

    os.chdir(homedir+"/perf/arm-vs-num-layers")
    keys = perf_dict.keys()
    print(keys)
    with open(args_dict["fname"]+".csv", "w") as outfile:
        writer = csv.writer(outfile, delimiter = ",")
        writer.writerow(list(keys))#(list(perf_dict.keys()))
        writer.writerows(zip(*[perf_dict[key] for key in keys]))#perf_dict.values()))



