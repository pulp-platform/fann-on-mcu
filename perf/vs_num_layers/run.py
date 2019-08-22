#!/usr/bin/env python


import os
import sys
import argparse
#import numpy as np

def get_args():

    get_args_dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('--activation', dest='activ', default=True, action='store_true', help='Only for performance measurement purpose. It sets the ACTIVATIONS.')
    parser.add_argument('--no-activation', dest='activ', action='store_false', help='Only for performance measurement purpose. It ignores the ACTIVATIONS, i.e. no activation functions will be applied.')
    args = parser.parse_args()

    get_args_dict['activ'] = args.activ

    return get_args_dict


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


if __name__=='__main__':

    '''
	run.py runs the generate.py with
	- python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm fc
	- python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm cluster
	- python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c parallel

	For each, it copies the output to the corresponding folder in wolfe-onBoardTest/ and runs `make clean all run`

    '''

    args_dict = get_args()

    os.chdir("../..")
    homedir = os.getcwd()

    # Number of repeatition for averaging the performance
    N_test =1

    # Number of input features and num neurons in output layer
    N_in = 100
    N_out = 8

    os.chdir(homedir+"/perf/vs_num_layers")
    # Generate stimuli, i.e. generate data (float) used for training
    os.system("python3 gen_stimuli.py generated_data/perftest {} {} {}".format(N_test, N_in, N_out))

    for n_layers in range(1, 41, 1):
        print("n_layers {}".format(n_layers))

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

        os.chdir(homedir+"/perf/vs_num_layers")
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

        os.system("make clean all onlytrain &>/dev/null")
        print("---- \t ---- \t ---- \t ----\n\n")
        # run on fc
        os.chdir(homedir)
        #print("#### run on fc");
        if args_dict["activ"]: # True, i.e. use activation
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm fc")
        else:
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm fc --no-activation")
        os.system("mv -f ./output/* -t ./wolfe-onBoardTest/fc/")
        os.chdir("./wolfe-onBoardTest/fc/")
        os.system("make clean all run")
        print("\n"+os.getcwd())
        print("---- \t ---- \t ---- \t ----\n\n")

        # run on cluster single core
        #print("#### run on singleriscy");
        os.chdir(homedir)
        # Estimate if even single neuron dma transfer will be too big for
        # L1 size
        # In Mr. Wolf, L1 memory is 64KB.
        ## It will be done in generate.py ##

        
        if args_dict['activ']: # True, i.e. use activation
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm cluster")
        else:
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c single -dm cluster --no-activation")
        os.system("mv -f ./output/* -t ./wolfe-onBoardTest/cluster/singlecore/")
        os.chdir("./wolfe-onBoardTest/cluster/singlecore")
        os.system("make clean all run")
        print("\n"+os.getcwd())
        print("---- \t ---- \t ---- \t ----\n\n")

        # run on cluster parallel
        #print("#### run on multiriscy");
        os.chdir(homedir)
        # Estimate if even single neuron (times max num cores) dma transfer
        # will be too big for L1 size
        # In Mr. Wolf, L1 memory is 64KB.
        ## It will be done in generate.py ##

        if args_dict['activ']: # True, i.e. use activation
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c parallel")
        else:
            os.system("python3 generate.py -i ./perf/vs_num_layers/perftest_fixed -p pulp -c parallel --no-activation")
        os.system("mv -f ./output/* -t ./wolfe-onBoardTest/cluster/multicore/")
        os.chdir("./wolfe-onBoardTest/cluster/multicore")
        os.system("make clean all run")
        print(os.getcwd())
        print("---- \t ---- \t ---- \t ----\n\n")


    print("END");

    os.system("")

