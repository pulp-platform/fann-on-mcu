#!/usr/bin/env python

import sys
import random
import numpy as np

def write_header(f, num_samples, num_input, num_output):
    f.write('%s %s %s\n' % (num_samples, num_input, num_output))

def write_arr_int(f, arr, length):

    for i in range(0, length):
        v = arr[i]
        f.write('%d ' % (v))
    f.write('\n')
    return

def write_arr_float(f, arr, length):

    for i in range(0, length):
        v = arr[i]
        f.write('%.6f ' % (v))
    f.write('\n')
    return

################################################################################

def gen_stimuli(name, num_samples, num_input, num_output):
    f = open(name, 'w')

    write_header(f, num_samples, num_input, num_output)

    for i in range(num_samples):
        input_arr = np.random.uniform(-1, 1, num_input)
        output_arr = np.random.randint(0, num_output, num_output)
        # print("max input arr {}, min input arr {}, max output arr {}, min output arr {}".format(max(input_arr), min(input_arr), max(output_arr), min(output_arr)))

        write_arr_float(f, input_arr, num_input)
        write_arr_int(f, output_arr, num_output)

    f.close()


if __name__=='__main__':

    """
    input
    first argument: file_name [string]
    second argument: num_samples [string]
    third argument: num_input [integer]
    fourth argument: num_output [int]
    """

    file_name = str(sys.argv[1])
    num_samples = int(sys.argv[2])
    num_input = int(sys.argv[3])
    num_output = int(sys.argv[4])



    gen_stimuli(file_name+".test", num_samples, num_input, num_output)
    gen_stimuli(file_name+".train", num_samples, num_input, num_output)


