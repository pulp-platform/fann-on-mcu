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
import scipy.integrate as integrate
import itertools
from matplotlib.legend import Legend
from matplotlib.patches import Polygon
import matplotlib as mpl


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

def plot_per_app(fname, ax=None, xmin=None, En_label_y=None, **kwargs):

    """ get energy number in milliWatt """

    with open(fname) as csvfile:
        for line in csvfile:
            line_split = line.split()
            if len(line_split) == 0:
                continue
            if line_split[0] == '"Scope.points:' or line_split[0] == 'Scope.points:':
                N_points = int(line_split[1][:-1])
            if line_split[0] == '"Scope.tint:' or line_split[0] == 'Scope.tint:':
                T_int = float(line_split[1][:-1])
                break


    #print("DICTIONARY:", info_dict)

    skiprows = np.arange(7)

    stats = pd.read_csv(fname, skiprows=skiprows, nrows=N_points-650) #, float_precision='high')

    

    if 'Current 1' in stats.keys():
        power = stats['Current 1'] * stats['Voltage 1'] * 1000 # in mW
    else:
        power = stats['Current 2'] * stats['Voltage 1'] * 1000 # in mW

    if 'nordic' not in fname:
        # to find the start and the end of the program
        if 'fc' in fname:
            threshold = np.mean(power[0:50])*1.2
        else:
            threshold = np.mean(power[0:50])*1.15
        print("mean power first 100 points {}".format(np.mean(power[0:100])))
        start = (power>threshold).idxmax()
        end = (power[start+1:]>threshold).idxmin()
        if fname[fname.find('/')+3:-4] != 'fc':
            if end - start < 20:
                start = (power[start+1:]>threshold).idxmax()
                end = (power[start+1:]>threshold).idxmin()
    else:
        print("Nordic start and end")
        threshold = np.mean(power[0:500])*1.1
        if 'A' in fname:
            start = 1057
            end = 1921
        if 'B' in fname:
            start = 38
            end = 78
        if 'C' in fname:
            start = 25
            end = 31
        if 'ldo' in fname:
            start = (power>threshold).idxmax()
            end = (power[start+1:]>threshold).idxmin()

    delta_t = end-start
    reserveplace = xmin #int(delta_t * 0.5)
    
    #energy = np.sum(power[start:end])/delta_t*T_int
    energy = np.trapz(power[start:end], dx=T_int)
    #print("#### fname: {}, delta t {}, power_sum {}, start {}, end {}".format(fname, delta_t*T_int, np.sum(power[start:end]), start, end))
    #print("stats[current][0] {0:.8f}".format(stats['Current 1'][start]))

    
    if ax == None:
        print("No ax given")
        return energy
    # fontsize = 4
    #labelsize = 12

    #ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    x = np.arange(start-reserveplace,end+reserveplace)
    power = power[start-reserveplace:end+reserveplace]
    x = x-(start-reserveplace)-reserveplace
    start = 0
    end = start+delta_t
    p = ax.plot(x*T_int*1000, power, label=fname[fname.find('/')+3:-4])
    #print(get_legend_handles_labels)
    #handles=ax.get_handles()
    ax.set_xlabel('Time (ms)')#, fontsize=labelsize)
    ax.set_ylabel('Power (mW)')#, fontsize=labelsize)
    poly = Polygon([(start*T_int*1000, 0), *zip(x[start+reserveplace:end+reserveplace]*T_int*1000, power[start+reserveplace:end+reserveplace]), (end*T_int*1000, 0)], facecolor=p[0].get_color(), **kwargs)
    ax.add_patch(poly)
    mpl.rcParams['hatch.color'] = '0.2'
    mpl.rcParams['hatch.linewidth'] = 1

    if En_label_y == None:
        En_label_y = threshold
    ax.text(0.5 * (start+end)*T_int*1000, En_label_y, s="Energy: {0:.2f} \u03BCJ".format(energy*1000), horizontalalignment='center', va='bottom')
    #if end*T_int*1000 + reserveplace*T_int*1000 > ax.get_xticks()[-1]:
    #    ax.xaxis.set_ticks(np.arange(start*T_int*1000, end*T_int*1000+0.5, 0.5))
    #hlinearrowtext(ax, threshold, start*T_int*1000, end*T_int*1000, label='Energy: {0:.2f} \u03BCJ'.format(energy*1000))
    #ax.fill_between(np.arange(start,end)*T_int*1000,
    #    power[start+reserveplace:end+reserveplace], **kwargs)
    if np.max(power)+0.1*np.max(power) > ax.get_ylim()[1]:
        ax.set_ylim(ymin=0, ymax=np.max(power)+0.05*np.max(power))
    plt.grid(True)
    ax.legend()

    #print(plt.rcParams)
    #print(**kwargs)

    #circ1 = mpatches.Patch(facecolor='r', label="Energy: {0:.2f} \u03BCJ".format(energy), **kwargs)#hatch=hatch,label='Label1')

    #leg = Legend(ax, handles=circ1,loc=(0.5 * (start + end), threshold), labels="Energy: {0:.2f} \u03BCJ", frameon=False)
    #ax.add_artist(leg);
    #ax.legend(handles=[line, circ1])

    return ax


def get_xlim(fname, prev_xmin, prev_xmax):

    """ get x axis limit """

    with open(fname) as csvfile:
        for line in csvfile:
            line_split = line.split()
            if len(line_split) == 0:
                continue
            if line_split[0] == '"Scope.points:' or line_split[0] == 'Scope.points:':
                N_points = int(line_split[1][:-1])
            if line_split[0] == '"Scope.tint:' or line_split[0] == 'Scope.tint:':
                T_int = float(line_split[1][:-1])
                break


    #print("DICTIONARY:", info_dict)

    skiprows = np.arange(7)

    stats = pd.read_csv(fname, skiprows=skiprows, nrows=N_points-650) #, float_precision='high')

    

    if 'Current 1' in stats.keys():
        power = stats['Current 1'] * stats['Voltage 1'] * 1000 # in mW
    else:
        power = stats['Current 2'] * stats['Voltage 1'] * 1000 # in mW

    if 'nordic' not in fname:
        # to find the start and the end of the program
        if 'fc' in fname:
            threshold = np.mean(power[0:50])*1.2
        else:
            threshold = np.mean(power[0:50])*1.15
        print("mean power first 100 points {}".format(np.mean(power[0:100])))
        start = (power>threshold).idxmax()
        end = (power[start+1:]>threshold).idxmin()
        if fname[fname.find('/')+3:-4] != 'fc':
            if end - start < 20:
                start = (power[start+1:]>threshold).idxmax()
                end = (power[start+1:]>threshold).idxmin()
    else:
        print("Nordic start and end")
        threshold = np.mean(power[0:500])*1.1
        if 'A' in fname:
            start = 1057
            end = 1921
        if 'B' in fname:
            start = 38
            end = 78
        if 'C' in fname:
            start = 25
            end = 31
        if 'ldo' in fname:
            start = (power>threshold).idxmax()
            end = (power[start+1:]>threshold).idxmin()

    delta_t = end-start
    reserveplace = int(delta_t * 0.5)
    #print("Start {} and reserveplace {}".format(start, reserveplace))
    if reserveplace > start:
        #print("Start {} shorter than reserveplace {}".format(start, reserveplace))
        reserveplace = start
    #print("prev xmin = {}, reserveplace = {}, start = {}".format(prev_xmin, reserveplace, start))
    if prev_xmin < reserveplace:
        xmin = prev_xmin
    else:
        xmin = reserveplace
    if end+reserveplace > prev_xmax:
        xmax = end+reserveplace
    else:
        xmax = prev_xmax

    return xmin, xmax



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
        # only print the energy
        print(get_energy(fname))

    else:
        power_dict = OrderedDict()
        filelist = [f for f in listdir(dirname) if f.endswith('.csv')] #str(voltage)+
        #for k,v in itertools.groupby(filelist,key=lambda x:x.split('_')[0]): #lambda x:x[:1]):
        #    print(k, list(v))
        app_dict = dict()
        for fname in filelist:
            if fname.split('_')[0] not in app_dict.keys():
                app_dict[fname.split('_')[0]] = [fname]
            else:
                app_dict[fname.split('_')[0]].append(fname)

        hatches = {'fc':'-', 'Single-RI5CY':'/', 'Multi-RI5CY':'.', 'dcdc':'/', 'ldo':'.'}
        for key in app_dict.keys():
            fig_fc, ax_fc = plt.subplots()
            fig_Ri5cy, ax_Ri5cy = plt.subplots()
            fig_nordic, ax_nordic = plt.subplots()
            #fig, (ax_fc, ax_Ri5cy, ax_nordic) = plt.subplots(3, 1, sharex=True)
            #fig.suptitle('Power measurements\nApplication '+key)
            #plt.subplots_adjust(hspace=0.5)
            xmin_p = 4096
            xmax_p = 0
            for fname in app_dict[key]:
                if 'nordic' in fname:
                    continue
                xmin_p, xmax_p = get_xlim(join(dirname, fname), xmin_p, xmax_p)
            xmin_n = 4096
            xmax_n = 0
            for fname in app_dict[key]:
                if 'nordic' not in fname:
                    continue
                xmin_n, xmax_n = get_xlim(join(dirname, fname), xmin_n, xmax_n)

            xmin = np.min([xmin_p, xmin_n])
            xmax = np.max([xmax_p, xmax_n])

            # plot
            for fname in app_dict[key]:

                fname_split = fname.split('_')
                if 'nordic' in fname:
                    hatch_key = fname_split[2][:-4]
                else:
                    hatch_key = fname_split[1][:-4]

                if 'fc' in fname:
                    ax = plot_per_app(join(dirname, fname), ax=ax_fc, xmin=xmin, hatch=hatches[hatch_key], alpha=0.1)
                    ax.title.set_text('Application '+key+' Mr. Wolf w/o cluster')
                    fig = fig_fc
                    if args_dict['plot']:
                        plt.show()
                    if args_dict['saveplot']:
                        fig.tight_layout()
                        fig.savefig(dirname+'/'+fname.split('_')[0]+'_fc'+'_per_app.pdf', bbox_inches='tight')


                if 'RI5CY' in fname:
                    if 'Multi' in fname:
                        En_label_y = 28
                    else:
                        En_label_y = 11
                    ax = plot_per_app(join(dirname, fname), ax=ax_Ri5cy, xmin=xmin, En_label_y=En_label_y, hatch=hatches[hatch_key], alpha=0.3)
                    ax.title.set_text('Application '+key+' Mr. Wolf with cluster')
                    if 'A' in fname:
                        ax.set_xticks(np.arange(0, 7.5, 0.5))
                    else:
                        ax.set_xticks(np.arange(0, 2, 0.5))
                    #ax.set_xticklabels(np.arange(0, ax.get_xticks()[-1],
                    #0.5))#, rotation = 45, ha="right")
                    ax.grid(True, color='lightgray', alpha=0.4, linewidth=0.5)
                    fig = fig_Ri5cy
                    if args_dict['plot']:
                        plt.show()
                    if args_dict['saveplot']:
                        fig.tight_layout()
                        fig.savefig(dirname+'/'+fname.split('_')[0]+'_RI5CY'+'_per_app.pdf', bbox_inches='tight')

                if 'nordic' in fname:
                    ax = plot_per_app(join(dirname, fname), ax=ax_nordic, xmin=xmin, hatch=hatches[hatch_key], alpha=0.1)
                    ax.title.set_text('Application '+key+' Nordic')
                    fig = fig_nordic
                    if args_dict['plot']:
                        plt.show()
                    if args_dict['saveplot']:
                        fig.tight_layout()
                        fig.savefig(dirname+'/'+fname.split('_')[0]+'_nordic'+'_per_app.pdf', bbox_inches='tight')

            
