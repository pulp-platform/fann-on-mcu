#!/usr/bin/env python


import os
import sys, argparse
#import numpy as np

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('--activation', dest='activ', default=True, action='store_true', help='Only for performance measurement purpose. It sets the ACTIVATIONS.')
    parser.add_argument('--no-activation', dest='activ', action='store_false', help='Only for performance measurement purpose. It ignores the ACTIVATIONS, i.e. no activation functions will be applied.')
    args = parser.parse_args()

    dict['activ'] = args.activ

    return dict

def gen_Makefile(num_input, num_output):
    print("generating Makefile...")

    f = open('Makefile', 'w')

    f.write("GCC=gcc\nCFLAGS=-I ~/fann/src/include\nLDFLAGS=-L ~/fann/src/\n\nTARGETS = perftest_train perftest_test perftest_test_fixed\nDEBUG_TARGETS = perftest_debug\n\nall: $(TARGETS)\n\n%: %.c Makefile\n\t$(GCC) $(CFLAGS) $(LDFLAGS) -O3 $< -o $@ -lfann -lm\n\n%_fixed: %.c Makefile\n\t$(GCC) $(CFLAGS) $(LDFLAGS) -O3 -DFIXEDFANN $< -o $@ -lfixedfann -lm\n\nclean:\n\trm -f $(TARGETS) $(DEBUG_TARGETS) perftest_fixed.data *.net *~ *.obj *.exe *.tds noscale.txt withscale.txt scale_test_results.txt\n\nonlytrain: perftest_train\n\t@echo\n\t@echo Training network\n\t./perftest_train {} {}\n".format(num_input, num_output))

    f.close()


if __name__=='__main__':

    '''
	run.py runs the generate.py with
	- python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm fc
	- python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm cluster
	- python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c parallel

	For each, it copies the output to the corresponding folder in wolfe-onBoardTest/ and runs `make clean all run`

    '''

    args_dict = get_args();

    homedir = os.getcwd()
    os.chdir("../..")
    homedir = os.getcwd()

    N_test = 1 # Number of test samples to be saved in L2 memory
    # For averaging the performance use NUM_REPEAT in test.c or cluster.c

    #print(np.logspace(0.1, 2.7, 20, endpoint=True)*2)


    for N_in in range(4, 709, 32): # 4, 1025, 32
        for N_out in range(4, 709, 32): # 4, 1025, 32
            # In Mr. Wolf, L2 shared memory is 448KB.
            # Estimate the size used in L2 as function of N_in and N_out:
            # 4 = int32_t in bytes
            # N_test * N_in = Number of test samples saved in L2
            # (N_in + 1)* N_out = number of weights per layer
            # (N_in + 1) + (N_out + 1) = number of neurons per layer
            # 2*2 = fann_layers struct per layer
            L2_size_estm = 4* (N_test * N_in + (N_in + 1)* N_out + (N_in + 1) + (N_out + 1) + 2*2)
            if L2_size_estm  > 400000:
                print(L2_size_estm)
                continue

            # In Mr. Wolf, L1 memory is 64KB.
            # Estimate the size used in L2 as function of N_in and N_out:
            # 4 = int32_t in bytes
            # 2 * N_in = local_data_buffer
            # 2 * max(N_in, N_out) = neuron buffer
            # 2 * N_in * N_out = weights buffer
            #L1_size_estm = 4 * (2 * N_in + 2 * max(N_in, N_out) + 2 * N_in * N_out)
            #if L1_size_estm  > 59170:
            #    print(L1_size_estm)
            #    continue

            os.chdir(homedir+"/perf/Nin-Nout-single-layer")
            gen_Makefile(N_in,N_out)
            os.system("python3 gen_stimuli.py generated_data/perftest {} {} {}".format(N_test, N_in, N_out))
            os.system("make clean all onlytrain &>/dev/null")
            print("---- \t ---- \t ---- \t ----\n\n")
            # run on fc
            os.chdir(homedir)
            #print("#### run on fc");
            if args_dict["activ"]: # True, i.e. use activation
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm fc")
            else:
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm fc --no-activation")
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
            # Estimate the size used in L2 as function of N_in and N_out:
            # 4 = int32_t in bytes
            # 2 * N_in = local_data_buffer
            # 2 * max(N_in, N_out) = neuron buffer
            # 2 * N_in * N_out = weights buffer
            L1_size_estm = 4 * (2 * N_in + 2 * max(N_in, N_out) + 2 * (N_in+1))
            if L1_size_estm  > 59170:
                print("Singlecore riscy: Net size too large {}".format(L1_size_estm))
                continue
            # Proceed if net size not too large
            if args_dict['activ']: # True, i.e. use activation
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm cluster")
            else:
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c single -dm cluster --no-activation")
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
            # Estimate the size used in L2 as function of N_in and N_out:
            # 4 = int32_t in bytes
            # 2 * N_in = local_data_buffer
            # 2 * max(N_in, N_out) = neuron buffer
            # 2 * N_in * N_out = weights buffer
            L1_size_estm = 4 * (2 * N_in + 2 * max(N_in, N_out) + 2 * (N_in+1) * 8) # max num cores = 8
            if L1_size_estm  > 59170:
                print("Multicore riscy: Net size too large {}".format(L1_size_estm))
                continue

            if args_dict['activ']: # True, i.e. use activation
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c parallel")
            else:
                os.system("python3 generate.py -i ./perf/Nin-Nout-single-layer/perftest_fixed -p pulp -c parallel --no-activation")
            os.system("mv -f ./output/* -t ./wolfe-onBoardTest/cluster/multicore/")
            os.chdir("./wolfe-onBoardTest/cluster/multicore")
            os.system("make clean all run")
            print(os.getcwd())
            print("---- \t ---- \t ---- \t ----\n\n")


    print("END");

    os.system("")

