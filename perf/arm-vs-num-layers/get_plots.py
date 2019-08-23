import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


if __name__=='__main__':


    """
    Plots heatmap of perf measurements. N_in vs. N_out.
    Input: filename of csv file containing the measurements.
    """

    fname = sys.argv[1]

    stats = pd.read_csv(fname)

    fontsize = 4
    labelsize = 6


    # perfname = "mean_cycles_"
    core_list = ["fc", "singleriscy", "multiriscy"]

    num_hidden_layers = stats["num_hidden_layers"]
    mean_cycles_fc = stats["mean_cycles_fc"]
    mean_cycles_singleriscy = stats["mean_cycles_singleriscy"]
    mean_cycles_multiriscy = stats["mean_cycles_multiriscy"]

    use_dma_i = 0
    neuron_wise_i = 0
    for i in range(len(num_hidden_layers)-1):
        if stats["use_dma"][i] == 0 and stats["use_dma"][i+1] == 1:
            use_dma_i = i + 1
        if stats["neuron_wise"][i] == 0 and stats["neuron_wise"][i+1] == 1:
            neuron_wise_i = i + 1


    fig, ax = plt.subplots()

    #ax.plot(num_hidden_layers[:use_dma_i], mean_cycles_fc[:use_dma_i]/1000, "^", mfc="darkorange", mec="darkorange", label="Single-Ibex Core, no dma")
    #ax.plot(num_hidden_layers[use_dma_i:neuron_wise_i], mean_cycles_fc[use_dma_i:neuron_wise_i]/1000, "b^", label="Single-Ibex Core, layer-wise dma")
    #ax.plot(num_hidden_layers[neuron_wise_i:],
    #mean_cycles_fc[neuron_wise_i:]/1000, "g^", label="Single-Ibex Core,
    #neuron-wise dma")
    ax.plot(num_hidden_layers, mean_cycles_fc/1000, "^", label="Single-Ibex Core")
    ax.plot(num_hidden_layers, mean_cycles_singleriscy/1000, "s", label="Single-Ri5cy Core")
    ax.plot(num_hidden_layers, mean_cycles_multiriscy/1000, "o", label="Multi-Ri5cy Cores")

    ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

    #legend_elements = [Line2D([0], [0], marker="^", label='Single-Ibex Core'), Line2D([0], [0], marker='s', label='Single-Ri5cy Core'), Line2D([0], [0], marker='o', label='Multi-Ri5cy Core'), Patch(facecolor='orange', label='Color Patch')]

    ax.legend()
    ax.set_xlabel("Number of hidden layers")
    ax.set_ylabel("Number of cycles in unit of thousands")
    plt.title("Number of cycles")

    # Draw vertical lines to separate no use dma, use dma layer wise, use dma
    # neuron wise
    if use_dma_i != 0:
        ax.axvline(x=use_dma_i, color="k", linewidth=1)
    if neuron_wise_i !=0:
        ax.axvline(x=neuron_wise_i, color="k", linewidth=1)

    fig.tight_layout()
    #plt.show()

    fig.savefig('./plots/'+fname[:-4]+'_num_cycles.pdf', bbox_inches='tight')


    fig, ax = plt.subplots()

    ax.plot(num_hidden_layers, mean_cycles_fc/mean_cycles_singleriscy, "o", label="Single-Ri5cy/Single-Ibex")
    ax.plot(num_hidden_layers, mean_cycles_singleriscy/mean_cycles_multiriscy, "o", label="Multi-Ri5cy/Single-Ri5cy")

    #print(mean_cycles_fc/mean_cycles_singleriscy)
    #print(mean_cycles_singleriscy/mean_cycles_multiriscy)

    ax.set_xticks(num_hidden_layers)#range(1, len(num_hidden_layers)+1))

    ax.legend()
    ax.set_xlabel("Number of hidden layers")
    ax.set_ylabel("Speedup")
    plt.title("Speedup")

    # Draw vertical lines to separate no use dma, use dma layer wise, use dma
    # neuron wise
    if use_dma_i != 0:
        ax.axvline(x=use_dma_i, color="k", linewidth=1)
    if neuron_wise_i !=0:
        ax.axvline(x=neuron_wise_i, color="k", linewidth=1)

    fig.tight_layout()
    #plt.show()

    fig.savefig('./plots/'+fname[:-4]+'_speedup.pdf', bbox_inches='tight')
    
