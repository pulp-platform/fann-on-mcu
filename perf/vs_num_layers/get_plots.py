import sys, argparse
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of csv file to be plotted')
    parser.add_argument('--comparegvsoc', dest='comparegvsoc', default=None, help='Compare the input measurement with the same measurements taken on gvsoc.')
    
    args = parser.parse_args()

    if args.input == None:
        parser.error("Missing input filename to save the data. --help for more details.")
    else:
        dict['fname'] = args.input

    dict['comparegvsoc'] = args.comparegvsoc

    return dict

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

def tot_hidden_units_inv(x):
        num_hidden_layers_list=np.empty((1,1), int)
        for i in range(len(x)):
            x1 = int(x[i])
            if x1 == 0:
                num_hidden_layers_list = np.append(num_hidden_layers_list, np.array([[0]]), axis=0)
            else:
                num_hidden_units=0
                l = 1
                while l < l+1:
                    num_hidden_units += (l%2 + l//2)*8
                    #print(num_hidden_units, x1[0])
                    if num_hidden_units == x1:
                        #print("here", num_hidden_units, l)
                        break
                    else:
                        l += 1
                num_hidden_layers_list = np.append(num_hidden_layers_list, np.array([[l]]), axis=0)
        return num_hidden_layers_list[1:]

    #print(tot_hidden_units_inv(tot_hidden_units(num_hidden_layers)))

    #secax = ax.secondary_xaxis('top', functions=(tot_hidden_units, tot_hidden_units_inv))
    #print(list_xticklabels)
    #secax.set_xticks(list_xticklabels)
    #secax.set_xticklabels(list_xticklabels)
    #secax.set_xlabel("Total number of hidden units")


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

    #ax.plot(num_hidden_layers[:use_dma_i], mean_cycles_fc[:use_dma_i]/1000, "^", mfc="darkorange", mec="darkorange", label="Single-IBEX Core, no dma")
    #ax.plot(num_hidden_layers[use_dma_i:neuron_wise_i], mean_cycles_fc[use_dma_i:neuron_wise_i]/1000, "b^", label="Single-IBEX Core, layer-wise dma")
    #ax.plot(num_hidden_layers[neuron_wise_i:],
    #mean_cycles_fc[neuron_wise_i:]/1000, "g^", label="Single-IBEX Core,
    #neuron-wise dma")
    ax.plot(num_hidden_layers, mean_cycles_fc/1000, "^", label="Single-IBEX Core")
    ax.plot(num_hidden_layers, mean_cycles_singleriscy/1000, "s", label="Single-RI5CY Core")
    ax.plot(num_hidden_layers, mean_cycles_multiriscy/1000, "o", label="Multi-RI5CY Cores")

    ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

    #legend_elements = [Line2D([0], [0], marker="^", label='Single-IBEX Core'), Line2D([0], [0], marker='s', label='Single-RI5CY Core'), Line2D([0], [0], marker='o', label='Multi-RI5CY Core'), Patch(facecolor='orange', label='Color Patch')]

    ax.legend()
    ax.set_xlabel("Number of hidden layers")
    ax.set_ylabel("Number of cycles in unit of thousands", fontsize=12)
    #plt.title("Number of cycles")


    # Draw vertical lines to separate no use dma, use dma layer wise, use dma
    # neuron wise
    if use_dma_i != 0:
        ax.axvline(x=use_dma_i+0.5, color="k", ls='--', linewidth=0.8)
        hlinearrowtext(700, 1, use_dma_i+0.5, label='L1', color='dimgray')
        hlinearrowtext(700, use_dma_i+0.5, 24, label='L2', color='dimgray')
    if neuron_wise_i !=0:
        ax.axvline(x=neuron_wise_i+0.5, color="k", ls=(0, (1, 1)), linewidth=0.8)
        hlinearrowtext(600, use_dma_i+0.5, neuron_wise_i+0.5, label='layer-wise', color='dimgray')
        hlinearrowtext(500, neuron_wise_i+0.5, 24, label='neuron-wise', color='dimgray')
    if use_shared_L2_i !=0:
        ax.axvline(x=use_shared_L2_i+0.5, color="k", ls=(0, (1, 10)), linewidth=0.8)
        hlinearrowtext(500, 1, use_shared_L2_i+0.5, label='private L2', color='dimgray')
        hlinearrowtext(400, use_shared_L2_i+0.5, 24, label='shared L2', color='dimgray')

    if args_dict['comparegvsoc'] is not None:

        fname_gvsoc = args_dict['comparegvsoc']

        stats_gvsoc = pd.read_csv(fname_gvsoc)

        num_hidden_layers_gvsoc = stats_gvsoc["num_hidden_layers"]
        mean_cycles_fc_gvsoc = stats_gvsoc["mean_cycles_fc"]
        mean_cycles_singleriscy_gvsoc = stats_gvsoc["mean_cycles_singleriscy"]
        mean_cycles_multiriscy_gvsoc = stats_gvsoc["mean_cycles_multiriscy"]

        ax.plot(num_hidden_layers_gvsoc, mean_cycles_fc_gvsoc/1000, "^", markeredgecolor="None", markerfacecolor='#1f77b4', alpha=0.3)
        ax.plot(num_hidden_layers_gvsoc, mean_cycles_singleriscy_gvsoc/1000, "s", markeredgecolor="None", markerfacecolor='#ff7f0e', alpha=0.3)
        ax.plot(num_hidden_layers_gvsoc, mean_cycles_multiriscy_gvsoc/1000, "o", markeredgecolor="None", markerfacecolor='#2ca02c', alpha=0.3)

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

    if args_dict['comparegvsoc'] is not None:
        fig.savefig('./plots/'+fname[:-4]+'_num_cycles_vs_gvsoc.pdf', bbox_inches='tight')
    else:
        fig.savefig('./plots/'+fname[:-4]+'_num_cycles.pdf', bbox_inches='tight')


    fig, ax = plt.subplots()

    ax.plot(num_hidden_layers, mean_cycles_fc/mean_cycles_singleriscy, "s", label="Single-RI5CY/Single-IBEX")
    ax.plot(num_hidden_layers, mean_cycles_singleriscy/mean_cycles_multiriscy, "o", label="Multi-RI5CY/Single-RI5CY")

    #print(mean_cycles_fc/mean_cycles_singleriscy)
    #print(mean_cycles_singleriscy/mean_cycles_multiriscy)

    ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))
    
    #ax.set_xticklabels(list_xticklabels, rotation=-60, ha='left')
    plt.ylim(0.8, max(ax.get_yticks())+0.4)
    #plt.ylim(1, max(ax.get_yticks())+0.2)
    ax.set_yticks(np.arange(1,max(ax.get_yticks()), 0.5))

    ax.legend(loc='upper left')
    #ax.set_xlabel("Number of hidden layers - Total number of hidden units")
    ax.set_xlabel("Number of hidden layers")
    ax.set_ylabel("Speedup", fontsize=12)
    #plt.title("Speedup")

    
    # Draw vertical lines to separate no use dma, use dma layer wise, use dma
    # neuron wise
    if use_dma_i != 0:
        ax.axvline(x=use_dma_i+0.5, color="k", ls='--', linewidth=0.8)
        hlinearrowtext(4, 1, use_dma_i+0.5, label='L1', head_width=0.05, color='dimgray')
        hlinearrowtext(4, use_dma_i+0.5, 24, label='L2', head_width=0.05, color='dimgray')
    if neuron_wise_i !=0:
        ax.axvline(x=neuron_wise_i+0.5, color="k", ls=(0, (1, 1)), linewidth=0.8)
        hlinearrowtext(3.5, use_dma_i+0.5, neuron_wise_i+0.5, label='layer-wise', head_width=0.05, color='dimgray')
        hlinearrowtext(3.5, neuron_wise_i+0.5, 24, label='neuron-wise', head_width=0.05, color='dimgray')
    if use_shared_L2_i !=0:
        ax.axvline(x=use_shared_L2_i+0.5, color="k", ls=(0, (1, 10)), linewidth=0.8)
        hlinearrowtext(2.5, 1, use_shared_L2_i+0.5, label='private L2', head_width=0.05, color='dimgray')
        hlinearrowtext(2.5, use_shared_L2_i+0.5, 24, label='shared L2', head_width=0.05, color='dimgray')
    
    if args_dict['comparegvsoc'] is not None:

        ax.plot(num_hidden_layers_gvsoc, mean_cycles_fc_gvsoc/mean_cycles_singleriscy_gvsoc, "s", markeredgecolor="None", markerfacecolor='#1f77b4', alpha=0.3)
        ax.plot(num_hidden_layers_gvsoc, mean_cycles_singleriscy_gvsoc/mean_cycles_multiriscy_gvsoc, "o", markeredgecolor="None", markerfacecolor='#ff7f0e', alpha=0.3)

    plt.grid(True, color='lightgray', alpha=0.4, linewidth=0.5)

    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    #print(tot_hidden_units(list_hidden_units).flatten())
    #ax2.set_xticks(list_hidden_units)
    ax2.set_xticks(num_hidden_layers)
    ax2.set_xticklabels(num_hidden_units, rotation=45)
    ax2.set_xlabel("Total number of hidden units")
    #print(ax2.get_xlim())
    #ax2.set_xticklabels(tot_hidden_units(list_hidden_units).flatten())


    fig.tight_layout()
    #plt.show()

    if args_dict['comparegvsoc'] is not None:
        fig.savefig('./plots/'+fname[:-4]+'_speedup_vs_gvsoc.pdf', bbox_inches='tight')
    else:
        fig.savefig('./plots/'+fname[:-4]+'_speedup.pdf', bbox_inches='tight')
    
