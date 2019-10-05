#!/usr/bin/env python
# coding: utf-8

import os
import sys, argparse
from struct import *
import csv
from collections import OrderedDict
import time

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', dest='target', default=None, help='folder name of the target application')
    parser.add_argument('-p', '--platform', dest='platform', default='both', choices=['arm','pulp', 'both'], help='Select the mcu platform, curretly supported ones are arm and pulp platforms, default is arm')
    parser.add_argument('--activation', dest='activ', default=True, action='store_true', help='Only for performance measurement purpose. It sets the ACTIVATIONS.')
    parser.add_argument('--no-activation', dest='activ', action='store_false', help='Only for performance measurement purpose. It ignores the ACTIVATIONS, i.e. no activation functions will be applied.')
    parser.add_argument('-ni', '--n_input', dest='n_input', type=int, nargs=1, help='Number of input features')
    parser.add_argument('-hu', '--hidden_units_every_layer', dest='hidden', type=int, nargs='+', help='Number of hidden units for everylayer')
    parser.add_argument('-no', '--n_output', dest='n_output', type=int, nargs=1, help='Number of output classes')
    args = parser.parse_args()

    dict['activ'] = args.activ

    dict['platform'] = args.platform

    dict['n_input'] = args.n_input
    dict['hidden'] = args.hidden
    dict['n_output'] = args.n_output

    dict['target'] = args.target

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


def only_sigmoid_stepwise(orig_file=None):

    """
    Modify fann.c to get only sigmoidal activation.
    """

    start_token = 'FIXEDFANN'
    stop_token = '#endif'
    start_token2 = 'FANN_SIGMOID_STEPWISE:'
    end_token2 = 'break;'
    start_found = 0
    start_found2 = 0
    start_delete = 0
    saveString = "/* Automatically generated fann.c file with modified activation functions part */\n"

    with open(orig_file, "r") as f:
        lines = f.readlines()
    with open(orig_file, "w") as f:
        for line in lines:
            line_split=line.split()
            #if line.strip("\n") != "nickname_to_delete":
            #    f.write(line)

            if len(line_split) == 0:# and start_found == 0:
                f.write(line)
                continue
            elif line_split[0] == 'if(activation_function':
                f.write('if(steepness != last_steepness)\n')
                continue
            elif line_split[0] == 'case' and line_split[1] == start_token2:
                start_found2 = 1
                start_delete = 0
                continue
            elif start_found2 == 1 and line_split[0] == end_token2:
                start_found2 = 0
                start_delete = 1
                continue
            elif line_split[0] == 'switch' and line_split[1] == '(activation_function)':
                start_delete = 1
                continue
            elif line_split[0] == 'last_steepness':
                f.write('}\n\n' + line)
                start_delete = 0
            elif line_split[0][0:13] == 'neuron_values':
                #print("HEEEEERE", line_split[0][0:13])
                start_delete = 0
            elif start_delete == 0 or start_found2 == 1:
                f.write(line)



if __name__ == '__main__':

    """
    Trains 
    Runs generate.py
    Compiles and flashes into the board (ARM Cortex)
    Reads from serial port and decodes the data
    Saves the data into a csv file given as input with -i
    """

    args_dict = get_args();
    platform = args_dict['platform']

    # change directory to FANN-on-MCU
    os.chdir("..")
    homedir = os.getcwd()

    N_test = 1 # Number of test samples
    # for averaging performance use NUM_REPEAT in main.c file

    # Number of input features and num neurons in output layer
    N_in = args_dict['n_input'][0]
    N_out = args_dict['n_output'][0]
    list_n_neurons = args_dict['hidden']

    print("number input features are {}, hidden layers are {}, output classes are {}".format(N_in, list_n_neurons, N_out))

    os.chdir(homedir+"/applications")
    # Generate stimuli, i.e. generate data (float) used for training
    os.system("python3 gen_stimuli.py generated_data/perftest {} {} {}".format(N_test, N_in, N_out))

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
    n_layers = len(list_n_neurons)
    L2_size_estm = 4*N_in*N_test + (n_layers + 1) * 2 * 4
    n_tot_neurons = 0
    for layer_i in range(0, len(list_n_neurons)-1, 1):
        L2_size_estm = L2_size_estm + 4 * (list_n_neurons[layer_i] + 1) * list_n_neurons[layer_i+1]
        n_tot_neurons = n_tot_neurons + (list_n_neurons[layer_i] + 1 + list_n_neurons[layer_i+1]+1)
        L2_size_estm = L2_size_estm + n_tot_neurons * 4 * 4 + n_tot_neurons * 4
        print("Estimated network size: {}".format(L2_size_estm)) # TODO check
        # it with the calculations on generate.py
    if L2_size_estm  > 440000:
        print("Estimated network size bigger than 400kB: {}".format(L2_size_estm))


    os.system("sleep 3")
    os.system("make clean all onlytrain &>/dev/null")
    os.system("sleep 3")

    if platform == 'arm' or platform == 'both':
        # run on arm
        os.chdir(homedir)

        #print("#### run on arm");
        #sys.stdout.flush()
        #print("wait for 5 seconds")
        #time.sleep(5)
        #print("I am here! " + homedir)
        if args_dict["activ"]: # True, i.e. use activation
            os.system("python3 generate.py -i ./applications/perftest_fixed -p arm --activation")
        else:
            os.system("python3 generate.py -i ./applications/perftest_fixed -p arm --no-activation")

        # mv the generated files except for fann.c and fann.h because already
        # in the applications/<xx>/stm and applications/<xx>/wolfe folders with
        # only one case of sigmoidal activation (from
        # 3-human_activity_classification fpga paper).
        only_sigmoid_stepwise("./output/fann.c")
        os.system("mv -f ./output/* -t ./applications/output/arm")
        # copy to the target application folder if given
        if args_dict['target'] != None:
            os.system("cp -f ./applications/output/arm/*.c -t ./applications/"+args_dict['target']+"/stm32/Src")
            os.system("cp -f ./applications/output/arm/*.h -t ./applications/"+args_dict['target']+ "/stm32/Inc")


    if platform == 'pulp' or platform == 'both':

        os.chdir(homedir)
        #print("#### run on fc");
        if args_dict["activ"]: # True, i.e. use activation
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c single -dm fc")
        else:
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c single -dm fc --no-activation")
        
        # mv the generated files except for fann.c and fann.h because already
        # in the applications/<xx>/stm and applications/<xx>/wolfe folders with
        # only one case of sigmoidal activation (from
        # 3-human_activity_classification fpga paper).
        only_sigmoid_stepwise("./output/fann.c")
        os.system("mv -f ./output/* -t ./applications/output/pulp/fc/")
        # copy to the target application folder if given
        if args_dict['target'] != None:
            os.system("cp -f ./applications/output/pulp/fc/* -t ./applications/"+args_dict['target']+"/wolfe/fc")

        # run on cluster single core
        #print("#### run on singleriscy");
        os.chdir(homedir)

        if args_dict['activ']: # True, i.e. use activation
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c single -dm cluster")
        else:
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c single -dm cluster --no-activation")
        only_sigmoid_stepwise("./output/fann.c")
        os.system("mv -f ./output/* -t ./applications/output/pulp/cluster/singlecore/")
        # copy to the target application folder if given
        if args_dict['target'] != None:
            os.system("cp -f ./applications/output/pulp/cluster/singlecore/* -t ./applications/"+args_dict['target']+"/wolfe/cluster/singlecore")

        # run on cluster parallel
        #print("#### run on multiriscy");
        os.chdir(homedir)
        # Estimate if even single neuron (times max num cores) dma transfer
        # will be too big for L1 size
        # In Mr. Wolf, L1 memory is 64KB.
        ## It will be done in generate.py ##

        if args_dict['activ']: # True, i.e. use activation
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c parallel")
        else:
            os.system("python3 generate.py -i ./applications/perftest_fixed -p pulp -c parallel --no-activation")
        only_sigmoid_stepwise("./output/fann.c")
        os.system("mv -f ./output/* -t ./applications/output/pulp/cluster/multicore/")
        # copy to the target application folder if given
        if args_dict['target'] != None:
            os.system("cp -f ./applications/output/pulp/cluster/multicore/* -t ./applications/"+args_dict['target']+"/wolfe/cluster/multicore")




