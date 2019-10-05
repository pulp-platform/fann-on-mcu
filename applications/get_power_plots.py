#!/usr/bin/env python
# coding: utf-8

from os import listdir
from os.path import isfile, join
import sys, argparse
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import csv
from collections import OrderedDict


def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of csv file to be plotted')
    parser.add_argument('-d', '--inputdir', help='the name of the directory containing all the csv files')
    #parser.add_argument('-v', '--voltage', dest='voltage', default=18, choices=[18, 33], type=int, help='Pulp voltage switch')
    parser.add_argument('--plot', dest='plot', default=False, action='store_true', help='Plot power measurements.')
    parser.add_argument('--saveplot', dest='saveplot', default=False, action='store_true', help='Save power measurements plots.')
    args = parser.parse_args()

    if args.input == None and args.inputdir == None:
        parser.error("Missing input filename or directory name containing csv files. --help for more details.")
    else:
        dict['fname'] = args.input
        dict['dirname'] = args.inputdir

    #dict['voltage'] = args.voltage
    dict['plot'] = args.plot
    dict['saveplot'] = args.saveplot

    return dict

def hlinearrowtext(ax, y, xmin, xmax, label='', **kwargs):
    xlim=ax.get_xlim()
    head_length=(xlim[1]-xlim[0])*0.015
    ylim=ax.get_ylim()
    head_width=(ylim[1]-ylim[0])*0.015
    ax.hlines(y, xmin+head_length, xmax-head_length*1.2, label=label, linewidth=0.8, linestyle='dotted', **kwargs)
    ax.text(xmax - (xmax-xmin)/2, y, label, ha='center', va='bottom', **kwargs)
    ax.arrow(xmax-head_length*1.2, y, head_length*0.8, 0, linewidth=0.8, head_width=head_width, head_length=head_length, length_includes_head=True, fc='white', **kwargs)
    ax.arrow(xmin+head_length, y, -head_length*0.8, 0, linewidth=0.8, head_width=head_width, head_length=head_length, length_includes_head=True, fc='white', **kwargs)

def get_energy(fname, plotpower=False, saveplot=False):

    """ get energy number in milliWatt """
    info_dict = dict()
    with open(fname) as csvfile:
        for line in csvfile:
            line_split = line.split()
            if len(line_split) == 0:
                continue
            if line_split[0] == '"Scope.points:' or line_split[0] == 'Scope.points:':
                info_dict['points'] = int(line_split[1][:-1])
            if line_split[0] == '"Scope.tint:' or line_split[0] == 'Scope.tint:':
                info_dict['tint'] = float(line_split[1][:-1])
                break


    #print("DICTIONARY:", info_dict)

    skiprows = np.arange(7)

    stats = pd.read_csv(fname, skiprows=skiprows, nrows=info_dict['points']-650)

    power = stats['Current 1'] * stats['Voltage 1']*1000

    # to find the start and the end of the program
    threshold = np.mean(power[0:100])*1.2
    start = (power>threshold).idxmax()
    end = (power[start+1:]>threshold).idxmin()
    delta_t = end-start
    reserveplace = int(delta_t * 0.25)

    energy = np.sum(power[start:end])*delta_t*info_dict['tint']

    if plotpower or saveplot:
        # fontsize = 4
        #labelsize = 12

        fig, ax = plt.subplots()
        #ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        x = np.arange(start-reserveplace,end+reserveplace)
        ax.plot(x*info_dict['tint']*1000, power[start-reserveplace:end+reserveplace])
        plt.title('Power measurements\nApplication '+fname[fname.find('/')+1:-4])
        ax.set_xlabel('Time (ms)')#, fontsize=labelsize)
        ax.set_ylabel('Power (mW)')#, fontsize=labelsize)
        hlinearrowtext(ax, threshold, start*info_dict['tint']*1000, end*info_dict['tint']*1000, label='Energy: {0:.2f} mJ'.format(energy))

        if plotpower:
            plt.show()
        if saveplot:
            fig.tight_layout()
            fig.savefig('./'+fname[:-4]+'_power.pdf', bbox_inches='tight')


    return energy



if __name__=='__main__':


    """
    Plots power measurements
    Input: filename of csv file containing the measurements.
    """

    args_dict = get_args()

    fname = args_dict['fname']
    dirname= args_dict['dirname']
    #voltage = args_dict['voltage']

    if dirname == None:
        print(get_energy(fname))

    else:
        power_dict = OrderedDict()
        filelist = [f for f in listdir(dirname) if f.endswith('.csv')] #str(voltage)+
        for fname in filelist:
            energy = get_energy(join(dirname, fname), plotpower=args_dict['plot'], saveplot=args_dict['saveplot'])
            print(fname, energy)
            power_dict[fname[:-4]] = energy


