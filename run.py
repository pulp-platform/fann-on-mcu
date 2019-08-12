#!/usr/bin/env python


import os
import sys

if __name__=='__main__':

    '''
	run.py runs the generate.py with
	- python3 generate.py -i sample-data/diabetes_fixed -p pulp -c single -dm fc
	- python3 generate.py -i sample-data/diabetes_fixed -p pulp -c single -dm cluster
	- python3 generate.py -i sample-data/diabetes_fixed -p pulp -c parallel

	For each, it copies the output to the corresponding folder in wolfe-onBoardTest/ and runs `make clean all run`

    '''

    # file_name = sys.argv[1]
    # data_type = sys.argv[2]
    # n_bits = int(sys.argv[3])
    # min_value = int(sys.argv[4])
    # max_value = int(sys.argv[5])
    # v_len = int(sys.argv[6])

    homedir = os.getcwd()

    # run on fc
    os.system("python3 generate.py -i sample-data/diabetes_fixed -p pulp -c single -dm fc")
    os.system("mv -f ./output/* ./wolfe-onBoardTest/fc/")
    os.chdir("./wolfe-onBoardTest/fc/")
    os.system("make clean all run")
    print("\n"+os.getcwd())
    print("#### \t #### \t #### \t ####\n\n")

    # run on cluster single core 
    os.chdir(homedir)
    os.system("python3 generate.py -i sample-data/diabetes_fixed -p pulp -c single -dm cluster")
    os.system("mv -f ./output/* ./wolfe-onBoardTest/cluster/singlecore/")
    os.chdir("./wolfe-onBoardTest/cluster/singlecore")
    os.system("make clean all run")
    print("\n"+os.getcwd())
    print("#### \t #### \t #### \t ####\n\n")

    # run on cluster parallel
    os.chdir(homedir)
    os.system("python3 generate.py -i sample-data/diabetes_fixed -p pulp -c parallel")
    os.system("mv -f ./output/* ./wolfe-onBoardTest/cluster/multicore/")
    os.chdir("./wolfe-onBoardTest/cluster/multicore")
    os.system("make clean all run")
    print(os.getcwd())
    print("#### \t #### \t #### \t ####\n\n")
