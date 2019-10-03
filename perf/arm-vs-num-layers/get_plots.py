import sys, argparse
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from collections import OrderedDict

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of csv file to be plotted')
    parser.add_argument('--compare', dest='compare', choices=['pulp', 'armfloat', 'both', 'vs_gvsoc'], default=None, help='Compare the input measurement with the same measurements taken with pulp and/or with arm float version.')
    parser.add_argument('--comparegvsoc', dest='comparegvsoc', default=None, help='Compare the input measurement with the same measurements taken on gvsoc.')
    
    args = parser.parse_args()

    if args.input == None:
        parser.error("Missing input filename to save the data. --help for more details.")
    else:
        dict['fname'] = args.input

    dict['compare'] = args.compare

    dict['comparegvsoc'] = args.comparegvsoc

    return dict

def get_stats_savetoflash(fname):

    start_token2 = 'nettype:'
    stop_token2 = 'copying'
    start_found = 0

    log_file = open(fname)

    perf_dict = OrderedDict()

    while True:

        line = log_file.readline()
        line_split=line.split()
        #    if len(line_split) == 0 and start_found == 1:
        #        break;
        if len(line_split) == 0:# and start_found == 0:
            continue
            # line = log_file.readline()
            # line_split=line.split()
            # if len(line_split) == 0:
            #     break
        if line_split[0]=="END":
            break
        # The information of use_dma, neuron_wise, etc. are the same for all the
        # computations (fc, single, multicore riscy). If this repeatition is not
        # taken into consideration, it overwrites the information of next lines,
        # i.e. the info of use_dma and neuron_wise will be wrong
        if (line_split[0]==start_token2 and start_found == 0):
            start_found=1
            print("start found True or False\n")

        if start_found == 0:
            continue
        if ((line_split[0]==stop_token2) and start_found == 1):
            start_found=0
            print("end found True or False\n")
        if start_found == 1 and line_split[0]=='####':
            if (line_split[2] == "True" or line_split[2] == "False"):

                line_split[2] = int(line_split[2] == 'True')

            if line_split[1] in perf_dict:
                #           print("key exists\n")
                perf_dict[line_split[1]].append(int(line_split[2]))
               #           print(perf_dict)
            else:
                #           print("key doesn't exists\n")
                perf_dict[line_split[1]] = [int(line_split[2])]

    return perf_dict

def dict_update(dictA, dictB):
    #keysA = dictA.keys()
    keysB = dictB.keys()
    #keys = keysA + list(set(keysB) - set(keysA))

    dictC = dictA
    for key in keysB:
        if key not in dictA:
            dictC[key] = dictB[key]

    return dictC

def hlinearrowtext(y, xmin, xmax, label='', head_width=10, **kwargs):
    ax.hlines(y, xmin+0.25, xmax-0.3, label=label, linewidth=0.8, linestyle='dotted', **kwargs)
    ax.text(xmax - (xmax-xmin+0.5)/2, y, label, ha='center', va='bottom', **kwargs)
    ax.arrow(xmax-0.3, y, 0.2, 0, linewidth=0.8, head_width=head_width, head_length=0.25, length_includes_head=True, fc='white', **kwargs)
    ax.arrow(xmin+0.25, y, -0.2, 0, linewidth=0.8, head_width=head_width, head_length=0.25, length_includes_head=True, fc='white', **kwargs)

def tot_hidden_units(x):
        num_hidden_units_list=np.empty((1,1), int)
        #print("direct", x)
        #print(num_hidden_units_list.shape, np.array([0]).shape)
        for i in range(len(x)):
            x1 = int(np.squeeze(x[i]))
            if x1 == 0:
                num_hidden_units_list = np.append(num_hidden_units_list, np.array([[0]]), axis=0)
                #print(num_hidden_units_list)
            else:
                num_hidden_units=0
                for l in np.arange(1,x1+1):
                    num_hidden_units += (l%2 + int(l//2))*8
                num_hidden_units_list = np.append(num_hidden_units_list, np.array([[num_hidden_units]]), axis=0)

        #print(num_hidden_units_list[1:])
        return num_hidden_units_list[1:]


if __name__=='__main__':


    """
    Plots heatmap of perf measurements. N_in vs. N_out.
    Input: filename of csv file containing the measurements.
    """

    args_dict = get_args()

    fname = args_dict['fname']

    stats = pd.read_csv(fname)

    fontsize = 4
    labelsize = 6

    num_hidden_layers = stats["num_hidden_layers"]
    mean_cycles = stats["mean_cycles"]

    # savetoflash for info on memory size
    savetoflash_dict = get_stats_savetoflash(fname[:-4]+'.txt')
    # Update the dictionary with info on memory size
    stats = dict_update(stats, savetoflash_dict)
    #print(stats)
    savetoflash_i = 0

    for i in range(len(num_hidden_layers)-1):
        if stats["savetoflash"][i] == 0 and stats["savetoflash"][i+1] == 1:
            savetoflash_i = i + 1

    fig, ax = plt.subplots()

    ax.plot(num_hidden_layers, mean_cycles/1000, "v", label="Cortex-M4")

    ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

    #legend_elements = [Line2D([0], [0], marker="^", label='Single-Ibex Core'), Line2D([0], [0], marker='s', label='Single-Ri5cy Core'), Line2D([0], [0], marker='o', label='Multi-Ri5cy Core'), Patch(facecolor='orange', label='Color Patch')]

    ax.legend()
    ax.set_xlabel("Number of hidden layers")
    ax.set_ylabel("Number of cycles in unit of thousands")
    plt.title("Runtime Measurements")

    # Draw vertical lines to separate when data saved to RAM when to FLASH
    if savetoflash_i != 0:
        ax.axvline(x=savetoflash_i+0.5, color="k", ls='-.', linewidth=0.8)

    fig.tight_layout()
    #plt.show()

    fig.savefig('./plots/'+fname[:-4]+'_arm_num_cycles.pdf', bbox_inches='tight')


    ######   ---------------------      Comparison with PULP    ---------------------      ######

    mean_cycles_arm = mean_cycles

    if args_dict['compare'] == 'pulp' or args_dict['compare'] == 'both':

        # read pulp stats
        stats = pd.read_csv("../vs_num_layers/"+fname)

        # perfname = "mean_cycles_"
        core_list = ["fc", "singleriscy", "multiriscy"]

        num_hidden_layers = stats["num_hidden_layers"]
        mean_cycles_fc = stats["mean_cycles_fc"]
        mean_cycles_singleriscy = stats["mean_cycles_singleriscy"]
        mean_cycles_multiriscy = stats["mean_cycles_multiriscy"]

        num_hidden_units = (tot_hidden_units(num_hidden_layers)).flatten()

        use_dma_i = 0
        neuron_wise_i = 0
        use_shared_L2_i = 0
        for i in range(len(num_hidden_layers)-1):
            if stats["use_dma"][i] == 0 and stats["use_dma"][i+1] == 1:
                use_dma_i = i + 1
            if stats["neuron_wise"][i] == 0 and stats["neuron_wise"][i+1] == 1:
                neuron_wise_i = i + 1
            if stats["use_shared_L2"][i] == 0 and stats["use_shared_L2"][i+1] == 1:
                use_shared_L2_i = i + 1


        fig, ax = plt.subplots()

        ax.plot(num_hidden_layers, mean_cycles_arm/1000, "v", label="Cortex-M4")
        ax.plot(num_hidden_layers, mean_cycles_fc/1000, "^", label="Single-Ibex Core")
        ax.plot(num_hidden_layers, mean_cycles_singleriscy/1000, "s", label="Single-Ri5cy Core")
        ax.plot(num_hidden_layers, mean_cycles_multiriscy/1000, "o", label="Multi-Ri5cy Cores")

        ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

        ax.legend()
        ax.set_xlabel("Number of hidden layers")
        ax.set_ylabel("Number of cycles in unit of thousands", fontsize=12)
        #plt.title("Runtime Measurements")

        # Draw vertical lines to separate no use dma, use dma layer wise, use dma
        # neuron wise. For ARM when in RAM when in FLASH
        if use_dma_i != 0:
            ax.axvline(x=use_dma_i+0.5, color="k", ls='--', linewidth=0.8)
            hlinearrowtext(650, 1, use_dma_i+0.5, label='L1', color='dimgray')
            hlinearrowtext(650, use_dma_i+0.5, 24, label='L2', color='dimgray')
        if neuron_wise_i !=0:
            ax.axvline(x=neuron_wise_i+0.5, color="k", ls=(0, (1, 1)), linewidth=0.8)
            hlinearrowtext(525, use_dma_i+0.5, neuron_wise_i+0.5, label='layer-wise', color='dimgray')
            hlinearrowtext(525, neuron_wise_i+0.5, 24, label='neuron-wise', color='dimgray')
        if use_shared_L2_i !=0:
            ax.axvline(x=use_shared_L2_i+0.5, color="k", ls=(0, (1, 10)), linewidth=0.8)
            hlinearrowtext(400, 1, use_shared_L2_i+0.5, label='private L2', color='dimgray')
            hlinearrowtext(400, use_shared_L2_i+0.5, 24, label='shared L2', color='dimgray')
        if savetoflash_i != 0:
            ax.axvline(x=savetoflash_i+0.5, color="k", ls="-.", linewidth=0.8)
            hlinearrowtext(125, 1, savetoflash_i+0.5, label='RAM', color='dimgray')
            hlinearrowtext(125, savetoflash_i+0.5, 24, label='FLASH', color='dimgray')

        plt.grid(True, color='lightgray', alpha=0.4, linewidth=0.5)

        ax2 = ax.twiny()
        ax2.set_xlim(ax.get_xlim())
        #print(tot_hidden_units(list_hidden_units).flatten())
        #ax2.set_xticks(list_hidden_units)
        ax2.set_xticks(num_hidden_layers)
        ax2.set_xticklabels(num_hidden_units, rotation=45)
        ax2.set_xlabel("Total number of hidden units")

        fig.tight_layout()
        #plt.show()

        fig.savefig('./plots/'+fname[:-4]+'_num_cycles.pdf', bbox_inches='tight')


        fig, ax = plt.subplots()

        ax.plot(num_hidden_layers, mean_cycles_arm/mean_cycles_fc, "v", label="Single-Ibex/Cortex-M4")
        ax.plot(num_hidden_layers, mean_cycles_arm/mean_cycles_singleriscy, "s", label="Single-Ri5cy/Cortex-M4")
        ax.plot(num_hidden_layers, mean_cycles_arm/mean_cycles_multiriscy, "o", label="Multi-Ri5cy/Cortex-M4")

        #print(mean_cycles_fc/mean_cycles_singleriscy)
        #print(mean_cycles_singleriscy/mean_cycles_multiriscy)

        ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))
        #ax.set_yticks(max((mean_cycles_arm/mean_cycles_fc, )))
        plt.ylim(0.1, int(max(ax.get_yticks())))
        ax.set_yticks(np.arange(1,max(ax.get_yticks()), 1))

        ax.legend()
        ax.set_xlabel("Number of hidden layers")
        ax.set_ylabel("Speedup", fontsize=12)
        #plt.title("Speedup")

        # Draw vertical lines to separate no use dma, use dma layer wise, use dma
        # neuron wise
        if use_dma_i != 0:
            ax.axvline(x=use_dma_i+0.5, color="k", ls='--', linewidth=0.8)
            hlinearrowtext(8.5, 1, use_dma_i+0.5, label='L1', head_width=0.1, color='dimgray')
            hlinearrowtext(8.5, use_dma_i+0.5, 24, label='L2', head_width=0.1, color='dimgray')
        if neuron_wise_i !=0:
            ax.axvline(x=neuron_wise_i+0.5, color="k", ls=(0, (1, 1)), linewidth=0.8)
            hlinearrowtext(7.5, use_dma_i+0.5, neuron_wise_i+0.5, label='layer-wise', head_width=0.1, color='dimgray')
            hlinearrowtext(7.5, neuron_wise_i+0.5, 24, label='neuron-wise', head_width=0.1, color='dimgray')
        if use_shared_L2_i !=0:
            ax.axvline(x=use_shared_L2_i+0.5, color="k", ls=(0, (1, 10)), linewidth=0.8)
            hlinearrowtext(5.5, 1, use_shared_L2_i+0.5, label='private L2', head_width=0.1, color='dimgray')
            hlinearrowtext(5.5, use_shared_L2_i+0.5, 24, label='shared L2', head_width=0.1, color='dimgray')
        if savetoflash_i != 0:
            ax.axvline(x=savetoflash_i+0.5, color="k", ls="-.", linewidth=0.8)
            hlinearrowtext(3, 1, savetoflash_i+0.5, label='RAM', head_width=0.1, color='dimgray')
            hlinearrowtext(3, savetoflash_i+0.5, 24, label='FLASH', head_width=0.1, color='dimgray')

        plt.grid(True, color='lightgray', alpha=0.4, linewidth=0.5)

        ax2 = ax.twiny()
        ax2.set_xlim(ax.get_xlim())
        #print(tot_hidden_units(list_hidden_units).flatten())
        #ax2.set_xticks(list_hidden_units)
        ax2.set_xticks(num_hidden_layers)
        ax2.set_xticklabels(num_hidden_units, rotation=45)
        ax2.set_xlabel("Total number of hidden units")

        fig.tight_layout()
        #plt.show()

        fig.savefig('./plots/'+fname[:-4]+'_speedup.pdf', bbox_inches='tight')

    #####     ---------------------      Comparison with FLOAT    ---------------------      ######

    if args_dict['compare'] == 'armfloat' or args_dict['compare'] == 'both':

        savetoflash_i_fixed = savetoflash_i

        # read pulp stats
        stats = pd.read_csv("../arm-vs-num-layers/"+fname[:-4]+"_float.csv")

        num_hidden_layers = stats["num_hidden_layers"]
        mean_cycles = stats["mean_cycles"]

        # savetoflash for info on memory size
        savetoflash_dict = get_stats_savetoflash(fname[:-4]+'_float.txt')
        # Update the dictionary with info on memory size
        stats = dict_update(stats, savetoflash_dict)
        #print(stats)
        savetoflash_i = 0

        for i in range(len(num_hidden_layers)-1):
            if stats["savetoflash"][i] == 0 and stats["savetoflash"][i+1] == 1:
                savetoflash_i = i + 1

        ### --- only float version --- ###

        fig, ax = plt.subplots()

        ax.plot(num_hidden_layers, mean_cycles/1000, "v", label="Cortex-M4 Floating Point")

        ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

        #legend_elements = [Line2D([0], [0], marker="^", label='Single-Ibex Core'), Line2D([0], [0], marker='s', label='Single-Ri5cy Core'), Line2D([0], [0], marker='o', label='Multi-Ri5cy Core'), Patch(facecolor='orange', label='Color Patch')]

        ax.legend()
        ax.set_xlabel("Number of hidden layers")
        ax.set_ylabel("Number of cycles in unit of thousands")
        plt.title("Runtime Measurements")

        # Draw vertical lines to separate when data saved to RAM when to FLASH
        if savetoflash_i != 0:
            ax.axvline(x=savetoflash_i+0.5, color="k", ls="-.", linewidth=0.8)

        fig.tight_layout()
        #plt.show()

        fig.savefig('./plots/'+fname[:-4]+'_arm_num_cycles_float.pdf', bbox_inches='tight')

        ### --- both fixed and float versions --- ###

        fig, ax = plt.subplots()

        ax.plot(num_hidden_layers, mean_cycles/1000, "v", label="Cortex-M4 Floating Point")
        ax.plot(num_hidden_layers, mean_cycles_arm/1000, "v", label="Cortex-M4 Fixed Point")

        ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

        #legend_elements = [Line2D([0], [0], marker="^", label='Single-Ibex Core'), Line2D([0], [0], marker='s', label='Single-Ri5cy Core'), Line2D([0], [0], marker='o', label='Multi-Ri5cy Core'), Patch(facecolor='orange', label='Color Patch')]

        ax.legend()
        ax.set_xlabel("Number of hidden layers")
        ax.set_ylabel("Number of cycles in unit of thousands")
        plt.title("Runtime Measurements")

        # Draw vertical lines to separate when data saved to RAM when to FLASH
        if savetoflash_i_fixed != savetoflash_i:
            if savetoflash_i_fixed != 0:
                ax.axvline(x=savetoflash_i+0.5, color="k", ls="--", linewidth=0.8)
        if savetoflash_i != 0:
            ax.axvline(x=savetoflash_i+0.5, color="k", ls="-.", linewidth=0.8)

        fig.tight_layout()
        #plt.show()

        fig.savefig('./plots/'+fname[:-4]+'_arm_num_cycles_fixed_float.pdf', bbox_inches='tight')


        fig, ax = plt.subplots()

        ax.plot(num_hidden_layers, mean_cycles/mean_cycles_arm, "v", label="Cortex-M4 Floating Point/Fixed point")

        #print(mean_cycles_fc/mean_cycles_singleriscy)
        #print(mean_cycles_singleriscy/mean_cycles_multiriscy)

        ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

        ax.legend()
        ax.set_xlabel("Number of hidden layers")
        ax.set_ylabel("Speedup")
        plt.title("Speedup")

        # Draw vertical lines to separate no use dma, use dma layer wise, use dma
        # neuron wise
        if savetoflash_i_fixed != savetoflash_i:
            if savetoflash_i_fixed != 0:
                ax.axvline(x=savetoflash_i+0.5, color="k", ls="--", linewidth=0.8)
        if savetoflash_i != 0:
            ax.axvline(x=savetoflash_i+0.5, color="k", ls="-.", linewidth=0.8)

        fig.tight_layout()
        #plt.show()

        fig.savefig('./plots/'+fname[:-4]+'_arm_speedup_fixed_float.pdf', bbox_inches='tight')
