#!/usr/bin/env python
# coding: utf-8

import os
import serial
import sys, argparse
from struct import *
import csv
from collections import OrderedDict
import time


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

if __name__ == '__main__':

    # For reading the measurements from serial port
    comport = '/dev/ttyACM0'
    baudrate = 115200
    bytesize = 8

    perf_dict = OrderedDict()

    perf_dict = decode(port=comport, baudrate=baudrate, bytesize=bytesize, savedata=perf_dict)
    print(perf_dict)
