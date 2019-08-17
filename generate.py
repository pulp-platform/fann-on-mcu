#!/usr/bin/env python2

#Copyright (c) 2018 ETH Zurich, Ferdinand von Hagen, Michele Magno, Lukas Cavigelli, Xiaying Wang

import os
import sys, argparse
from math import log

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of .data file and .net file exported from FANN and to be converted, e.g. sample-data/myNetwork')
    parser.add_argument('-d', '--datatype', dest='dtype', choices=['float', 'fixed'], help='Select floating point or fixed point computation, default is fixed. This argument will be ignored if the input filename contains "fixed" or "float", in which case the computation mode will be based on the input filename, e.g. diabetes_float or diabetes_fixed.')
    parser.add_argument('-p', '--platform', dest='platform', default='arm', choices=['arm','pulp'], help='Select the mcu platform, curretly supported ones are arm and pulp platforms, default is arm')
#    parser.add_argument('-pv', '--platform_version', dest='pversion', choices=['wolfe', 'gap8'], default='wolfe', help='In case pulp platform is selected, which version of pulp platform? Currently tested ones are Mr. Wolf (wolfe) and GAP8, default is wolfe')
    parser.add_argument('-c', '--computation', dest='comp', choices=['single', 'parallel'], default='parallel', help='In case pulp platform is selected, single core computation or parallel computation? Default is parallel')
    parser.add_argument('-dm', '--domain', dest='domain', choices=['fc', 'cluster'], default='cluster', help='In case pulp platform and singlecore computation are selected, which domain do you want to use? Fabric Controller (fc) or Cluster? Default is cluster')
    parser.add_argument('--activation', dest='activ', default=True, action='store_true', help='Only for performance measurement purpose. It sets the ACTIVATIONS.')
    parser.add_argument('--no-activation', dest='activ', action='store_false', help='Only for performance measurement purpose. It ignores the ACTIVATIONS, i.e. no activation functions will be applied.')
    args = parser.parse_args()

    if args.input == None:
        parser.error("Missing input filename of the files to be converted. --help for more details.")
    elif '.data' in args.input or '.net' in args.input:
        parser.error("Insert only the filename without .data or .net extentions.")
    else:
        dict['fname'] = args.input

    if args.dtype == None:
        if "float" in args.input or "FLOAT" in args.input:
            args.dtype = 'float'
        elif "fixed" in args.input or "FIXED" in args.input:
            args.dtype = 'fixed'
        else:
            parser.error("-m argument required. Floating point or fixed point operations? --help for more details.")
    else:
        if ("float" in args.input or "FLOAT" in args.input) and args.dtype != 'float':
            parser.error("-m ambiguous computation mode. Floating point of fixed point? --help for more details.")
        if ("fixed" in args.input or "FIXED" in args.input) and args.dtype != 'fixed':
            parser.error("-m ambiguous computation mode. Floating point of fixed point? --help for more details.")

    dict['dtype'] = args.dtype

    dict['platform'] = args.platform

    if args.platform == 'pulp':
        if args.dtype == 'float':
            parser.error("currently no float support with pulp")
        if args.comp == 'parallel' and args.domain == 'fc':
            parser.error("Fabric Controller doesn't have multiple cores")
        #dict['pversion'] = args.pversion
        #if args.domain == 'fc' and args.comp == 'parallel':
        #    parser.error("Fabric Controller doesn't have multiple cores")
        dict['comp'] = args.comp
        dict['domain'] = args.domain

    dict['activ'] = args.activ

    return dict


def mapToStringOfDType(dtype, arr):#dtype = "float" or "int"
    inputIsArray = hasattr(arr, '__iter__') and not type(arr) == str
    if not inputIsArray: arr = [arr]
    
    if type(arr[0]) == str:
        arr = [float(v) for v in arr]
    
    if dtype == "int":
        outp = ['%d' % (v,) for v in arr]
    else: # float network
        outp = ['%10.10ff' % (v,) for v in arr]
        
    if not inputIsArray: outp = outp[0]
    
    return outp

#if len(sys.argv) != 2:
#    print("Missing argument for filename that should be converted. For example xor_fixed or xor_float!")
#    exit(-1)

#print(sys.argv)
#fname = sys.argv[1]

args_dict = get_args();
print("\nInput arguments:\n{}\n".format(args_dict))
fname = args_dict['fname']

try:
    netF = open(fname + '.net', 'r')
    # find out whether it's a fixed or float version
    fann = {}
    firstL = netF.readline()
#    if "FIXED" in firstL:
#        print("nettype: fixed")
#        fann["nettype"] = "int"
#        args_dict['dtype']="fixed"
#    elif "FLOAT" in firstL:
#        print("nettype: float")
#        fann["nettype"] = "float"
#        args_dict['dtype']="float"
#    else:
    if args_dict['dtype'] == 'float':
        print("nettype: float")
        fann["nettype"] = "float"
    else: # args_dict['dtype'] == 'fixed':
        print("nettype: fixed")
        fann["nettype"] = "int"


    file = netF.readlines()
    for line in file:
        parts = line.strip('\n').split('=')

        # if it is not split then we have an invalid line without an '='
        if(len(parts) != 2):
            continue

        # neuron and connection data have specifiers we need to remove
        if(len(parts[0].split(" ")) > 1):
            parts[0] = parts[0].split(" ")[0]
        
        # store all variables in dictionary
        fann[parts[0]] = parts[1]

    # currently no networks with a connection_rate below 1 are supported
    if float(fann["connection_rate"]) < 1.0:
        print("Currently no networks with a connection_rate below 1.0 are supported")
        exit(-1)

    # reformat neurons and connections
    fann["neurons"] = fann["neurons"].strip("()\r\n ").split(") (")
    fann["connections"] = fann["connections"].strip("()\r\n ").split(") (")

    tot_connections = 0
    fann["generated_neurons"] = []
    for neuron in fann["neurons"]:
        
        neuron = neuron.split(', ')
        num_inputs, activation_function, activation_steepness = neuron

        first_connection = tot_connections
        last_connection = first_connection + int(num_inputs)
        activation_steepness = mapToStringOfDType(fann["nettype"], activation_steepness)

        fann["generated_neurons"].append("{" + ', '.join((str(first_connection), 
            str(last_connection), activation_steepness, activation_function)) + "}")

        tot_connections = last_connection

    if tot_connections != len(fann["connections"]):
        print("ERROR: tot_connections != len(connections)")
        print(tot_connections)
        print(len(fann["connections"]))
        exit(-1)

    fann["generated_connections"] = []
    for connection in fann["connections"]:
        connection = connection.split(", ")
        fann["generated_connections"].append(connection[1])

    fann["generated_layers"] = []
    layer_num = 0
    # largest layer including input layer
    largest_layer = 0
    # to find the layer with the most number of weights
    previous_layer_num = 0
    # the largest number of weights in a layer
    largest_layer_weights = 0
    fann['layer_sizes'] = fann['layer_sizes'].strip()
    for layer in fann['layer_sizes'].split(' '):
        fann["generated_layers"].append('{' + str(layer_num) + ', ' + str(layer_num + int(layer)) + '}')
        layer_num = layer_num + int(layer)
        if int(layer) > largest_layer:
            largest_layer = int(layer)
        if previous_layer_num*(int(layer)-1) > largest_layer_weights:
            largest_layer_weights = previous_layer_num*(int(layer)-1)
        previous_layer_num = int(layer)


    if "decimal_point" not in fann:
        fann['decimal_point'] = "1"

    fann["multiplier"] = 1 << int(fann["decimal_point"])
        
    fann["num_input"] = str(int(fann['layer_sizes'].split(' ')[0]) - 1)
    fann["num_output"] = str(int(fann['layer_sizes'].strip(' ').split(' ')[-1]) - 1)

    # calculate sigmoid functions
    multiplier = int(fann["multiplier"])
    precalc_fixed = {}
    precalc_fixed["SIGMOID_RESULTS_0"] = max(int(multiplier / 200.0 + 0.5), 1)
    precalc_fixed["SIGMOID_RESULTS_1"] = max(int(multiplier / 20.0 + 0.5), 1)
    precalc_fixed["SIGMOID_RESULTS_2"] = max(int(multiplier / 4.0 + 0.5), 1)
    precalc_fixed["SIGMOID_RESULTS_3"] = min(multiplier - int(multiplier / 4.0 + 0.5), multiplier - 1)
    precalc_fixed["SIGMOID_RESULTS_4"] = min(multiplier - int(multiplier / 20.0 + 0.5), multiplier - 1)
    precalc_fixed["SIGMOID_RESULTS_5"] = min(multiplier - int(multiplier / 200.0 + 0.5), multiplier - 1)

    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_0"] = max(int((multiplier / 100.0) - multiplier - 0.5), int(1 - multiplier))
    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_1"] = max(int((multiplier / 10.0) - multiplier - 0.5), int(1 - multiplier))
    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_2"] = max(int((multiplier / 2.0) - multiplier - 0.5), int(1 - multiplier))
    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_3"] = min(multiplier - int(multiplier / 2.0 + 0.5), multiplier - 1)
    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_4"] = min(multiplier - int(multiplier / 10.0 + 0.5), multiplier - 1)
    precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_5"] = min(multiplier - int(multiplier / 100.0 + 1.0), multiplier - 1)

    for i in range(0, 6):
        precalc_fixed["SIGMOID_VALUES_" + str(i)] = int(((log(multiplier / float(precalc_fixed["SIGMOID_RESULTS_" + str(i)]) - 1) * float(multiplier)) / (-2.0)) * float(multiplier))
        precalc_fixed["SIGMOID_SYMMETRIC_VALUES_" + str(i)] = int(((log((multiplier - float(precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_" + str(i)])) / float(precalc_fixed["SIGMOID_SYMMETRIC_RESULTS_" + str(i)] + multiplier)) * float(multiplier)) / (-2.0)) * float(multiplier))

    # generate file contents for fann_conf.h
    saveString = '#ifndef FANN_FANN_CONF_H_\n'
    saveString = saveString + '#define FANN_FANN_CONF_H_\n\n'

    # if args_dict['platform'] == "arm":
    #     print("ARM platform\n")
    #     saveString = saveString + '#define ARMFANN\n'
    # elif args_dict['platform'] == "pulp":
    #     print("PULP platform\n")
    #     saveString = saveString + '#define PULPFANN\n'
    #     #if args_dict['pversion'] == "gap8":
    #     #    print("gap8 is used\n")
    #     #    saveString = saveString + '#define GAP8FANN\n'

    if fann["nettype"] == "int":
        saveString = saveString + '#define FIXEDFANN\n\n'

    for x in precalc_fixed:
        saveString = saveString + '#define ' + x + ' ' + str(precalc_fixed[x]) + '\n'

    saveString = saveString + '\n#define NUM_NEURONS ' + str(len(fann["generated_neurons"])) + '\n'
    saveString = saveString + '#define MULTIPLIER ' + str(fann["multiplier"]) + '\n'
    saveString = saveString + '#define DECIMAL_POINT ' + fann["decimal_point"] + '\n'
    saveString = saveString + '#define NUM_INPUT ' + fann["num_input"] + '\n'
    saveString = saveString + '#define NUM_OUTPUT ' + fann["num_output"] + '\n'
    saveString = saveString + '#define NUM_LAYERS ' + str(len(fann["generated_layers"])) + '\n'
    saveString = saveString + '#define CONNECTION_RATE ' + fann["connection_rate"] + '\n\n'

    #if args_dict["comp"] == "parallel":
    #    saveString = saveString + '#define nPE 8\n\n'
    # Conflict with plp_math uint32_t nPE; plp_math.h:111,126,147,168

    if args_dict["activ"] == True:
        saveString = saveString + '#define ACTIVATIONS\n\n'
    print("\n#### use_activ {}\n".format(args_dict["activ"]));

    saveString = saveString + '\n#endif // FANN_FANN_CONF_H_\n'


    try:
        FW = open("output/fann_conf.h", "w")
        FW.write(saveString)
        FW.close()
    except IOError:
        print("Could not open write fann_conf.h")
        exit(1)
        
    # generate neurons
    generatedNeurons = fann["generated_neurons"]
    generatedConnections = mapToStringOfDType(fann["nettype"], fann["generated_connections"])

    # DONE use_dma - precision --> estimate memory size
    # - test_data_input: len(ins)/len(outs)
    # - fann_neurons: len(fann["generated_neurons"]) * 4 * sizeof(datatype) [int,
    # int, fann_type, enum fann_activationfunc_enum]
    # - fann_weights: len(generatedConnections) * sizeof(fann_type)
    # - fann_layers: len(fann["generated_layers"]) * 2 * sizeof(int)
    # - neuron_values: 2*largest_layer
    # - weights_loc_buff: 2*largest_layer_weights

    try:
        import functools

        dataF = open(fname + '.data', 'r')

        # parse data parameters
        firstLine = dataF.readline().strip(' \r\n').split(' ')
        numSamples = int(firstLine[0])
        numInputs = int(firstLine[1])
        numOutputs = int(firstLine[2])

        #read data
        contents = dataF.readlines()
        inValues  = [[float(v) for v in line.strip().split(' ')] for i, line in enumerate(contents) if i % 2 == 0]
        outValues = [[float(v) for v in line.strip().split(' ')] for i, line in enumerate(contents) if i % 2 == 1]
        outValues = [lineVals.index(max(lineVals)) for lineVals in outValues] # convert to classification output

        #flatten input list of lists
        inValues = functools.reduce(lambda x, y: x + y, inValues)

        #map values to string
        ins = mapToStringOfDType(fann["nettype"], inValues)
        outs = mapToStringOfDType("int", outValues)
    except IOError:
        print("Could not open " + fname + ".data or ")
        print("Failed to generate test_data from file")
        exit(-1)

    estimated_memory_size = int((len(ins)/len(outs)) + (len(fann["generated_neurons"])*(4+4+4+4)) + (len(generatedConnections)*4) + (len(fann["generated_layers"])*2*4) + (2*largest_layer) + (2*largest_layer_weights))
    print("estimated_memory_size {}".format(estimated_memory_size))
    if estimated_memory_size < 62000:
        use_dma = False
    else:
        use_dma = True
    #use_dma = True
    print("\n#### use_dma {}".format(use_dma))

    # generate file contents for fann_net.h
    saveString = '#ifndef FANN_FANN_NET_H_\n'
    saveString = saveString + '#define FANN_FANN_NET_H_\n\n'

    #insert includes
    if args_dict['platform'] == "pulp":
        saveString = saveString + '#include "rt/rt_api.h"\n'
    saveString = saveString + '#include "fann.h" \n'
    saveString = saveString + '#include "fann_structs.h" \n\n'

    # Declare the variables with const member attribute if platform is arm
    if args_dict['platform'] == "arm":
        saveString = saveString + 'const enum fann_nettype_enum network_type = ' + fann["network_type"] + ';\n\n'
        saveString = saveString + 'const fann_neuron fann_neurons[' + str(len(fann["generated_neurons"])) + '] = {' + ', '.join(generatedNeurons) + '};\n\n'
        saveString = saveString + 'const fann_type fann_weights[' + str(len(generatedConnections)) + '] = {' + ', '.join(generatedConnections) + '};\n\n'
        saveString = saveString + 'const fann_layer fann_layers[' + str(len(fann["generated_layers"])) + '] = {' + ', '.join(fann["generated_layers"]) + '};\n'
        saveString = saveString + 'fann_type neuron_values[NUM_NEURONS];\n\n'

    # If platform is pulp and the data are declared in L1 (without using dma,
    # i.e. use_dma = False, the const attribute can't be used because of error:
    # fann_net.h:10:30: error: fann_neurons causes a section type conflict with neuron_values)
    else: # in case of pulp platform #if args_dict['platform'] == "pulp":
        if args_dict['domain'] == "cluster" and not use_dma:
            saveString = saveString + 'RT_CL_DATA enum fann_nettype_enum network_type = ' + fann["network_type"] + ';\n\n'
            saveString = saveString + 'RT_CL_DATA fann_neuron fann_neurons[' + str(len(fann["generated_neurons"])) + '] = {' + ', '.join(generatedNeurons) + '};\n\n'
            saveString = saveString + 'RT_CL_DATA fann_type fann_weights[' + str(len(generatedConnections)) + '] = {' + ', '.join(generatedConnections) + '};\n\n'
            saveString = saveString + 'RT_CL_DATA fann_layer fann_layers[' + str(len(fann["generated_layers"])) + '] = {' + ', '.join(fann["generated_layers"]) + '};\n\n'
            saveString = saveString + 'RT_CL_DATA fann_type neuron_values[NUM_NEURONS];\n\n'

            ## Copy fann_struct.h with RT_CL_DATA to output/ folder
            #os.system("cp ./pulp/cluster/fann_structs.h ./output/")
            ## Comment: it doesn't help anyways even thought fann_layers and
            #fann_neurons are in RT_CL_DATA, typedef can't have attribute
            #RT_CL_DATA. Accessing activation is anyways an external load access.

            # Also copy the right fann.c, fann_utils.c, and fann_utils.h to the
            # output/ folder
            if args_dict['comp'] == "parallel":
                print("\ncopying ./pulp/cluster/no_dma/parallel/* ./output/\n")
                os.system("cp ./pulp/cluster/no_dma/parallel/* ./output/")
            else:
                print("\ncopying ./pulp/cluster/no_dma/single/* ./output/\n")
                os.system("cp ./pulp/cluster/no_dma/single/* ./output/")

        elif args_dict['domain'] == "cluster" and use_dma:

            saveString = saveString + 'RT_L2_DATA enum fann_nettype_enum network_type = ' + fann["network_type"] + ';\n\n'
            saveString = saveString + 'RT_L2_DATA fann_neuron fann_neurons[' + str(len(fann["generated_neurons"])) + '] = {' + ', '.join(generatedNeurons) + '};\n\n'
            saveString = saveString + 'RT_L2_DATA fann_type fann_weights[' + str(len(generatedConnections)) + '] = {' + ', '.join(generatedConnections) + '};\n\n'
            # fann_layers in CL_DATA
            saveString = saveString + 'RT_CL_DATA fann_layer fann_layers[' + str(len(fann["generated_layers"])) + '] = {' + ', '.join(fann["generated_layers"]) + '};\n\n'

            # saveString largest_layer for buffer size for the dma trasfer
            # (neuron_values)
            saveString = saveString + '#define NUM_NEURONS_BIGGEST_LAYER ' + str(largest_layer) + '\n'
            saveString = saveString + 'RT_CL_DATA fann_type neuron_values[2][NUM_NEURONS_BIGGEST_LAYER];\n\n'
            saveString = saveString + '#define BIGGEST_NUM_WEIGHTS_LAYER ' + str(largest_layer_weights) + '\n'
            saveString = saveString + 'RT_CL_DATA fann_type weights_loc_buff[2][BIGGEST_NUM_WEIGHTS_LAYER];\n\n'

            ## Copy fann_struct.h with RT_CL_DATA to output/ folder
            #os.system("cp ./pulp/cluster/fann_structs.h ./output/")
            ## Comment: it doesn't help since fann_neurons and fann_layers are
            #in L2

            # Also copy the right fann.c, fann_utils.c, and fann_utils.h to the
            # output/ folder
            if args_dict['comp'] == "parallel":
                print("\ncopying ./pulp/cluster/with_dma/parallel/* ./output/\n")
                os.system("cp ./pulp/cluster/with_dma/parallel/* ./output/")
            else:
                print("\ncopying ./pulp/cluster/with_dma/single/* ./output/\n")
                os.system("cp ./pulp/cluster/with_dma/single/* ./output/")

        else: # on fabric controller

            saveString = saveString + 'const enum fann_nettype_enum network_type = ' + fann["network_type"] + ';\n\n'
            saveString = saveString + 'fann_neuron fann_neurons[' + str(len(fann["generated_neurons"])) + '] = {' + ', '.join(generatedNeurons) + '};\n\n'
            saveString = saveString + 'fann_type fann_weights[' + str(len(generatedConnections)) + '] = {' + ', '.join(generatedConnections) + '};\n\n'
            saveString = saveString + 'const fann_layer fann_layers[' + str(len(fann["generated_layers"])) + '] = {' + ', '.join(fann["generated_layers"]) + '};\n\n'
            saveString = saveString + 'fann_type neuron_values[NUM_NEURONS];\n\n'

            # Also copy the right fann.c to the
            # output/ folder
            print("\ncopying ./pulp/fc/* ./output/\n")
            os.system("cp ./pulp/fc/* ./output/")

            # DONE RT_L2_DATA fann_net.h for fc private memory (const) or
            # shared memory (RT_L2_DATA)
            # done because "cluster" and not use_dma and "cluster" and use_dma
            # cover both the cases cluster singlecore and multicore

    saveString = saveString + '\n#endif // FANN_FANN_NET_H_\n'

    try:
        FW = open("output/fann_net.h", "w")
        FW.write(saveString)
        FW.close()
    except IOError:
        print("Could not open write fann_net.h")
        exit(1)

    print("generated fann_net.h in folder output/")
    print("generated fann_conf.h in folder output/")
    print("NETWORK converted. Please copy the files and/or recompile")
except IOError:
    print("Could not open " + fname + ".net")
    print("Failed to generate network from file")


# generate test data file
try:
    import functools
    
    dataF = open(fname + '.data', 'r')

    # parse data parameters
    firstLine = dataF.readline().strip(' \r\n').split(' ')
    numSamples = int(firstLine[0])
    numInputs = int(firstLine[1])
    numOutputs = int(firstLine[2])

    #read data
    contents = dataF.readlines()
    inValues  = [[float(v) for v in line.strip().split(' ')] for i, line in enumerate(contents) if i % 2 == 0]
    outValues = [[float(v) for v in line.strip().split(' ')] for i, line in enumerate(contents) if i % 2 == 1]
    outValues = [lineVals.index(max(lineVals)) for lineVals in outValues] # convert to classification output
    
    #flatten input list of lists
    inValues = functools.reduce(lambda x, y: x + y, inValues)
    
    #map values to string
    ins = mapToStringOfDType(fann["nettype"], inValues)
    outs = mapToStringOfDType("int", outValues)

    print("TEST data extracted")

    saveString = '#ifndef FANN_FANN_TEST_DATA_H_\n'
    saveString = saveString + '#define FANN_FANN_TEST_DATA_H_\n\n'


    # Declare the variables with const member attribute if platform is arm
    if args_dict['platform'] == "arm":
        saveString = saveString + "const int NUM_TESTS = " + str(len(outs)) + ";\n\n"
        saveString = saveString + "fann_type test_data_input[" + str(len(ins)) + "] = {" + ', '.join(ins) + "};\n\n"
        saveString = saveString + "const int test_data_output[" + str(len(outs)) + "] = {" + ', '.join(outs) + "};\n\n"

    # If platform is pulp and the data are declared in L1 (without using dma,
    # i.e. use_dma = False, the const attribute can't be used because of error:
    # test_data.h:4:22: error: NUM_TESTS causes a section type conflict with test_data_output
    else: # in case of pulp platform #if args_dict['platform'] == "pulp":
        saveString = saveString + '#include "rt/rt_api.h"\n'
        if args_dict['domain'] == "cluster" and not use_dma:
            saveString = saveString + "RT_CL_DATA int NUM_TESTS = " + str(len(outs)) + ";\n\n"
            saveString = saveString + "RT_L2_DATA fann_type test_data_input[" + str(len(ins)) + "] = {" + ', '.join(ins) + "};\n\n"
            saveString = saveString + "RT_L2_DATA int test_data_output[" + str(len(outs)) + "] = {" + ', '.join(outs) + "};\n\n"

        elif args_dict['domain'] == "cluster" and use_dma:
            # no const with RT_L2_DATA attribute
            saveString = saveString + "RT_CL_DATA int NUM_TESTS = " + str(len(outs)) + ";\n\n"
            saveString = saveString + "RT_L2_DATA fann_type test_data_input[" + str(len(ins)) + "] = {" + ', '.join(ins) + "};\n\n"
            saveString = saveString + "RT_L2_DATA int test_data_output[" + str(len(outs)) + "] = {" + ', '.join(outs) + "};\n\n"
        else:
            # no const with RT_L2_DATA attribute
            saveString = saveString + "const int NUM_TESTS = " + str(len(outs)) + ";\n\n"
            saveString = saveString + "fann_type test_data_input[" + str(len(ins)) + "] = {" + ', '.join(ins) + "};\n\n"
            saveString = saveString + "const int test_data_output[" + str(len(outs)) + "] = {" + ', '.join(outs) + "};\n\n"

            # DONE RT_L2_DATA test_data.h for fc private memory (const) or
            # shared memory (RT_L2_DATA)
            # done because "cluster" and not use_dma and "cluster" and use_dma
            # cover both the cases cluster singlecore and multicore
    
    saveString = saveString + '\n#endif // FANN_FANN_TEST_DATA_H_\n'

    try:
        FW = open("output/test_data.h", "w")
        FW.write(saveString)
        FW.close()
    except IOError:
        print("Could not create test_data.h")
        exit(1)

    print("generated test_data.h in folder output/")
except IOError:
    print("Could not open " + fname + ".data or ")
    print("Failed to generate test_data from file")
    exit(-1)


# Copy other header files to output/ folder
#os.system("cp ./fann.h ./output/")
#os.system("cp ./fann_structs.h ./output/")
