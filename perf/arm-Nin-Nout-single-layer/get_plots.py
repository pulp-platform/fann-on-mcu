import sys, argparse
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc
from collections import OrderedDict

def get_args():

    dict = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='the name of csv file to be plotted')
    parser.add_argument('--compare', dest='compare', choices=['pulp', 'armfloat', 'both'], default=None, help='Compare the input measurement with the same measurements taken with pulp and/or with arm float version.')
    
    args = parser.parse_args()

    if args.input == None:
        parser.error("Missing input filename to save the data. --help for more details.")
    else:
        dict['fname'] = args.input

    dict['compare'] = args.compare

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


def heatmap(data, row_labels, col_labels, labelsize, ax=None,
            cbar_kw={}, cbarlabel="", xlabel="", ylabel="", fig_title=None, **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    plt.title(fig_title, fontsize=labelsize)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, aspect=50, fraction=0.0175, pad=0.11, orientation='horizontal', **cbar_kw)
    cbar.ax.set_xlabel(cbarlabel, rotation=0, ha='center', va='top', fontsize=labelsize)
    cbar.ax.tick_params(labelsize=labelsize)
    cbar.outline.set_visible(False)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontsize=labelsize)
    ax.set_yticklabels(row_labels, fontsize=labelsize)

    # Set the label names
    ax.set_xlabel(xlabel = xlabel, fontsize=labelsize)
    ax.set_ylabel(ylabel = ylabel, fontsize=labelsize)

    # Let the horizontal axes labeling appear on top.
    #ax.tick_params(top=True, bottom=False,
    #               labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-45, ha="left",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

def newline(p1, p2):
    ax = plt.gca()
    xmin, xmax = ax.get_xbound()
    print(xmin, xmax)

    if(p2[0] == p1[0]):
        xmin = xmax = p1[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmax-p1[0])
        ymin = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmin-p1[0])

    l = mlines.Line2D([xmin,xmax], [ymin,ymax])
    ax.add_line(l)
    return l

def addlines(ax, corners=None, lines=None, y_axis_size=None, **kwargs):
    # lines = [[(4.5, 5.5), (4.5, 6.5)], [(4.5, 6.5), (5.5, 6.5)], [(5.5, 6.5),
    # (6.5, 6.5)]]

    lines = []
    for i in range(len(corners)):
        # put all other corners
        blx = corners[i][0] # bottom left corner x axis
        bly = y_axis_size-1-corners[i][1] # bottom left corner y axis
        lines.append([(blx, bly), (blx+1, bly)])
        lines.append([(blx, bly), (blx, bly-1)])
        #lines.append([(blx+1, bly-1), (blx, bly-1)])
        #lines.append([(blx+1, bly-1), (blx+1, bly)])

    lc = mc.LineCollection(lines, **kwargs)
    ax.add_collection(lc)


if __name__=='__main__':


    """
    Plots heatmap of perf measurements. N_in vs. N_out.
    Input: filename of csv file containing the measurements.
    """

    args_dict = get_args()

    fname = args_dict['fname']

    stats = pd.read_csv(fname)
    in_start = 4 #stats["NUM_INPUT_fc"][0]
    in_end = 709 #stats["NUM_INPUT_fc"][len(stats)-1]
    in_step = 32 #stats["NUM_INPUT_fc"][1]-stats["NUM_INPUT_fc"][0]
    in_maxsize = len(range(in_start,in_end,in_step))
    out_start = 4 #stats["NUM_OUTPUT_fc"][0]
    out_end = 709 #stats["NUM_OUTPUT_fc"][len(stats)-1]
    out_step = 32 #stats["NUM_OUTPUT_fc"][1]-stats["NUM_OUTPUT_fc"][0]
    out_maxsize = len(range(out_start, out_end, out_step))
    fontsize = 4
    labelsize = 6


    # perfname = "mean_cycles_"
    #core_list = ["fc", "singleriscy", "multiriscy"]

    # savetoflash for info on memory size
    savetoflash_dict = get_stats_savetoflash(fname[:-4]+'.txt')
    # Update the dictionary with info on memory size
    stats = dict_update(stats, savetoflash_dict)
    savetoflash = []


    # Initialize
    stats_2d_tmp = np.empty((in_maxsize, out_maxsize))
    stats_2d_tmp[:] = np.nan

    # Parse through all the measurements
    for i in range(len(stats)):
        n_in = int((stats["NUM_INPUT"][i] - in_start)/in_step)
        n_out = int((stats["NUM_OUTPUT"][i] - out_start)/out_step)
        stats_2d_tmp[n_in, n_out] = stats["mean_cycles"][i]
        if stats["savetoflash"][i] == 1:
            savetoflash.append((n_out-0.5, n_in-0.5))
        #if stats["neuron_wise"][i] == 1:
        #    neuron_wise.append((n_out-0.5, n_in-0.5))

    # Sort the labels
    in_labels = np.sort(np.unique(stats["NUM_INPUT"].to_numpy()))
    out_labels = np.sort(np.unique(stats["NUM_OUTPUT"].to_numpy()))

    # Fit the matrix to the real size cutting the edges where the network
    # doesn't fit anymore into L1
    #stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]
    # Comment: in order to fit into a single column of the paper, we cut
    # away also the asymmetric part. Comment out the next lines and
    # uncomment the previous one if you want to plot all the data.
    if len(in_labels) > len(out_labels):
        in_labels = in_labels[:len(out_labels)]
    else:
        out_labels = out_labels[:len(in_labels)]
    stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]

    title_tmp = "Cortex-M4"

    fig, ax = plt.subplots()

    im, cbar = heatmap(np.flip(stats_2d/1000, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="PuBu", cbarlabel="Number of cycles in units of thousands", xlabel="Output size", ylabel="Input size", fig_title="Runtime Measurements of Single-Layer MLP on "+title_tmp)
    texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize-1)

    # Lines to separate use_dma and neuron_wise
    addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), linewidth=0.8, color="steelblue")

    fig.tight_layout()
    #plt.show()

    #fig.savefig('./plots/'+fname[:-4]+'_'+core+'.png', bbox_inches='tight')
    fig.savefig('./plots/'+fname[:-4]+'.pdf', bbox_inches='tight')

    ######   ------------   Comparison with PULP and/or ARM float version    -----------    ######

    stats_arm = stats_2d

    if args_dict['compare'] == 'pulp' or args_dict['compare'] == 'both':

        # read pulp stats
        stats = pd.read_csv("../Nin-Nout-single-layer/"+fname)

        # perfname = "mean_cycles_"
        core_list = ["fc", "singleriscy", "multiriscy"]

        use_dma = []
        neuron_wise = []
        use_shared_L2 = []

        for core in core_list:

            # Initialize
            stats_2d_tmp = np.empty((in_maxsize, out_maxsize))
            stats_2d_tmp[:] = np.nan

            # Parse through all the measurements
            for i in range(len(stats)):
                n_in = int((stats["NUM_INPUT_"+core][i] - in_start)/in_step)
                n_out = int((stats["NUM_OUTPUT_"+core][i] - out_start)/out_step)
                stats_2d_tmp[n_in, n_out] = stats["mean_cycles_"+core][i]
                if stats["use_dma"][i] == 1:
                    use_dma.append((n_out-0.5, n_in-0.5))
                if stats["neuron_wise"][i] == 1:
                    neuron_wise.append((n_out-0.5, n_in-0.5))
                if stats["use_shared_L2"][i] == 1:
                    use_shared_L2.append((n_out-0.5, n_in-0.5))

            # Sort the labels
            in_labels = np.sort(np.unique(stats["NUM_INPUT_"+core].to_numpy()))
            out_labels = np.sort(np.unique(stats["NUM_OUTPUT_"+core].to_numpy()))

            # Fit the matrix to the real size cutting the edges where the network
            # doesn't fit anymore into L1
            #stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]
            # Comment: in order to fit into a single column of the paper, we cut
            # away also the asymmetric part. Comment out the next lines and
            # uncomment the previous one if you want to plot all the data.
            if len(in_labels) > len(out_labels):
                in_labels = in_labels[:len(out_labels)]
            else:
                out_labels = out_labels[:len(in_labels)]
            stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]

            if core == "fc":
                #stats_2d_fc = stats_2d
                speedup_arm_fc = stats_arm/stats_2d

                fig, ax = plt.subplots()

                im, cbar = heatmap(np.flip(speedup_arm_fc, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Single-Layer MLP on Single-Ibex Core wrt. Cortex-M4")
                texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

                # Lines for ibex core private or shared L2
                addlines(ax, corners=use_shared_L2, y_axis_size=len(in_labels), linewidth=0.8, color="mediumpurple", ls=(0, (1, 1)))
                # Lines to separate savetoram or savetoflash
                addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), linewidth=0.8, color="steelblue")

                fig.tight_layout()
                #plt.show()

                #fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.png', bbox_inches='tight')
                fig.savefig('./plots/'+fname[:-4]+'_speedup_arm_fc.pdf', bbox_inches='tight')

            if core == "singleriscy":
                speedup_arm_singleriscy = stats_arm/stats_2d
                #stats_2d_sr = stats_2d

                fig, ax = plt.subplots()

                im, cbar = heatmap(np.flip(speedup_arm_singleriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Single-Layer MLP on Single-Ri5cy Core wrt. Cortex-M4")
                texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

                # Lines to separate use_dma and neuron_wise
                addlines(ax, corners=neuron_wise, y_axis_size=len(in_labels), linewidth=0.8, color="dimgray", ls='dashdot')
                addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), linewidth=0.8, color="steelblue")

                fig.tight_layout()
                #plt.show()

                #fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.png', bbox_inches='tight')
                fig.savefig('./plots/'+fname[:-4]+'_speedup_arm_singleriscy.pdf', bbox_inches='tight')

            if core == "multiriscy":
                speedup_arm_multiriscy = stats_arm/stats_2d

                fig, ax = plt.subplots()

                im, cbar = heatmap(np.flip(speedup_arm_multiriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Single-Layer MLP on Multi-Ri5cy Cores wrt. Cortex-M4")
                texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

                # Lines to separate use_dma and neuron_wise
                addlines(ax, corners=neuron_wise, y_axis_size=len(in_labels), linewidth=0.8, color="dimgray", ls='dashdot')
                addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), linewidth=0.8, color="steelblue")

                fig.tight_layout()
                #plt.show()

                #fig.savefig('./plots/'+fname[:-4]+'_speedup_single_multiriscy.png', bbox_inches='tight')
                fig.savefig('./plots/'+fname[:-4]+'_speedup_arm_multiriscy.pdf', bbox_inches='tight')


    if args_dict['compare'] == 'armfloat' or args_dict['compare'] == 'both':

        savetoflash_fixed = savetoflash

        # read pulp stats
        stats = pd.read_csv("../arm-Nin-Nout-single-layer/"+fname[:-4]+"_float.csv")

        # savetoflash for info on memory size
        savetoflash_dict = get_stats_savetoflash(fname[:-4]+'_float.txt')
        # Update the dictionary with info on memory size
        stats = dict_update(stats, savetoflash_dict)
        savetoflash = []


        # Initialize
        stats_2d_tmp = np.empty((in_maxsize, out_maxsize))
        stats_2d_tmp[:] = np.nan

        # Parse through all the measurements
        for i in range(len(stats)):
            n_in = int((stats["NUM_INPUT"][i] - in_start)/in_step)
            n_out = int((stats["NUM_OUTPUT"][i] - out_start)/out_step)
            stats_2d_tmp[n_in, n_out] = stats["mean_cycles"][i]
            if stats["savetoflash"][i] == 1:
                savetoflash.append((n_out-0.5, n_in-0.5))

        # Sort the labels
        in_labels = np.sort(np.unique(stats["NUM_INPUT"].to_numpy()))
        out_labels = np.sort(np.unique(stats["NUM_OUTPUT"].to_numpy()))

        # Fit the matrix to the real size cutting the edges where the network
        # doesn't fit anymore into L1
        #stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]
        # Comment: in order to fit into a single column of the paper, we cut
        # away also the asymmetric part. Comment out the next lines and
        # uncomment the previous one if you want to plot all the data.
        if len(in_labels) > len(out_labels):
            in_labels = in_labels[:len(out_labels)]
        else:
            out_labels = out_labels[:len(in_labels)]
        stats_2d = stats_2d_tmp[0:len(in_labels), 0:len(out_labels)]

        title_tmp = "Cortex-M4 Floating Point"

        fig, ax = plt.subplots()

        im, cbar = heatmap(np.flip(stats_2d/1000, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="PuBu", cbarlabel="Number of cycles in units of thousands", xlabel="Output size", ylabel="Input size", fig_title="Runtime Measurements of Single-Layer MLP on "+title_tmp)
        texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize-1)

        # Lines to separate use_dma and neuron_wise
        addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), color="dimgray")

        fig.tight_layout()
        #plt.show()

        #fig.savefig('./plots/'+fname[:-4]+'_'+core+'.png', bbox_inches='tight')
        fig.savefig('./plots/'+fname[:-4]+'_float.pdf', bbox_inches='tight')

        ### ---------- Compare arm fixed with float version ---------- ###

        #stats_2d_fc = stats_2d
        speedup_fixed_float = stats_2d/stats_arm

        fig, ax = plt.subplots()

        im, cbar = heatmap(np.flip(speedup_fixed_float, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Cortex-M4 Fixed Point wrt. Floating Point")
        texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

        # Lines to separate use_dma and neuron_wise
        addlines(ax, corners=savetoflash_fixed, y_axis_size=len(in_labels), color="dimgray")
        addlines(ax, corners=savetoflash, y_axis_size=len(in_labels), color="steelblue")

        fig.tight_layout()
        #plt.show()

        #fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.png', bbox_inches='tight')
        fig.savefig('./plots/'+fname[:-4]+'_speedup_arm_fixed_float.pdf', bbox_inches='tight')

