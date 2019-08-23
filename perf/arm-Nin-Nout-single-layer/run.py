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

def gen_Makefile(num_input, num_output):
    print("generating Makefile...")

    f = open('Makefile', 'w')

    f.write("GCC=gcc\nCFLAGS=-I ~/fann/src/include\nLDFLAGS=-L ~/fann/src/\n\nTARGETS = perftest_train perftest_test perftest_test_fixed\nDEBUG_TARGETS = perftest_debug\n\nall: $(TARGETS)\n\n%: %.c Makefile\n\t$(GCC) $(CFLAGS) $(LDFLAGS) -O3 $< -o $@ -lfann -lm\n\n%_fixed: %.c Makefile\n\t$(GCC) $(CFLAGS) $(LDFLAGS) -O3 -DFIXEDFANN $< -o $@ -lfixedfann -lm\n\nclean:\n\trm -f $(TARGETS) $(DEBUG_TARGETS) perftest_fixed.data *.net *~ *.obj *.exe *.tds noscale.txt withscale.txt scale_test_results.txt\n\nonlytrain: perftest_train\n\t@echo\n\t@echo Training network\n\t./perftest_train {} {}\n".format(num_input, num_output))

    f.close()

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

    # For reading the measurements from serial port
    comport = '/dev/ttyACM0'
    baudrate = 115200
    bytesize = 8

    # Save the measurements
    perf_dict = OrderedDict()

    decode_clear(port=comport, baudrate=baudrate, bytesize=bytesize)

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

            # I would like to keep them (pulp and arm) completely separate, therefore I copy files like gen_stimuli.py into this folder
            os.chdir(homedir+"/perf/arm-Nin-Nout-single-layer")
            gen_Makefile(N_in,N_out)
            #sys.stdout.flush()
            #print("wait for 5 seconds")
            #time.sleep(5)
            os.system("python3 gen_stimuli.py generated_data/perftest {} {} {}".format(N_test, N_in, N_out))
            #sys.stdout.flush()
            #print("wait for 5 seconds")
            #time.sleep(5)
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
                os.system("python3 generate.py -i ./perf/arm-Nin-Nout-single-layer/perftest_fixed -p arm")
            else:
                os.system("python3 generate.py -i ./perf/arm-Nin-Nout-single-layer/perftest_fixed -p arm --no-activation")

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
            os.chdir(homedir+"/perf/arm-Nin-Nout-single-layer")
            #sys.stdout.flush()
            #print("wait for 5 seconds")
            #time.sleep(5)
            perf_dict = decode(port=comport, baudrate=baudrate, bytesize=bytesize, savedata=perf_dict)
            #os.chdir(homedir+"/stm32l475-onDeviceTest-linux/")
            #sys.stdout.flush()
            #print("wait for 5 seconds")
            #time.sleep(5)
            #os.system("make flash")
            #print("\n"+os.getcwd())
            #print("---- \t ---- \t ---- \t ----\n\n")

            print(perf_dict)

            #os.system("sleep 1")

    os.chdir(homedir+"/perf/arm-Nin-Nout-single-layer")
    keys = perf_dict.keys()
    #print(keys)
    with open(args_dict["fname"]+".csv", "w") as outfile:
        writer = csv.writer(outfile, delimiter = ",")
        writer.writerow(list(keys))#(list(perf_dict.keys()))
        writer.writerows(zip(*[perf_dict[key] for key in keys]))#perf_dict.values()))

