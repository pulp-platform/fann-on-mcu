import sys
import csv

def mod_train_c(n_layers=4, orig_file=None):

    """
    Adds hidden layers in train.c (perftest_train.c) file to automatically train networks with variable number of layers.
    Takes as input number of hidden layers.
    """

    # Number of input features and num neurons in output layer
    N_in = 100
    N_out = 8

    # Compute the ranges for the list with number of neurons for every layer
    min_n_neurons = 4
    n_neurons_step = 16
    max_n_neurons = min_n_neurons + (n_layers - 1)*n_neurons_step + 1

    list_n_neurons = []
    for i in range(min_n_neurons, max_n_neurons, n_neurons_step):
        list_n_neurons.append(i)
    #print(list_n_neurons)

    orig_file = open(orig_file)

    start_token = 'main'
    stop_token = 'return'
    start_found = 0
    start2_found = 0
    copy = 1
    saveString = "/* Automatically generated train.c file */\n"


    while True:

        line = orig_file.readline()
        if copy == 1:
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
            saveString = saveString[:-3] + str(n_layers) + ';\n'

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

if __name__ == '__main__':


    orig_file = "./perftest_train_orig.c"

    mod_train_c(n_layers=20, orig_file=orig_file)
