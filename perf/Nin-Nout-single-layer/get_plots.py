import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc



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

    fname = sys.argv[1]

    stats = pd.read_csv(fname)
    in_start = 4 #stats["NUM_INPUT_fc"][0]
    in_end = 1025 #stats["NUM_INPUT_fc"][len(stats)-1]
    in_step = 32 #stats["NUM_INPUT_fc"][1]-stats["NUM_INPUT_fc"][0]
    in_maxsize = len(range(in_start,in_end,in_step))
    out_start = 4 #stats["NUM_OUTPUT_fc"][0]
    out_end = 1025 #stats["NUM_OUTPUT_fc"][len(stats)-1]
    out_step = 32 #stats["NUM_OUTPUT_fc"][1]-stats["NUM_OUTPUT_fc"][0]
    out_maxsize = len(range(out_start, out_end, out_step))
    fontsize = 4
    labelsize = 6


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
            stats_2d_fc = stats_2d
        if core == "singleriscy":
            speedup_fc_singleriscy = stats_2d_fc/stats_2d
            stats_2d_sr = stats_2d

            fig, ax = plt.subplots()

            im, cbar = heatmap(np.flip(speedup_fc_singleriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Single-Layer MLP on Single-Ri5cy Core wrt. Single-Ibex Core")
            texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

            # Lines for ibex core private or shared L2
            addlines(ax, corners=use_shared_L2, y_axis_size=len(in_labels), linewidth=0.8, color="mediumpurple", ls=(0, (1, 1)))
            # Lines to separate use_dma and neuron_wise
            addlines(ax, corners=neuron_wise, y_axis_size=len(in_labels), linewidth=0.8, color="dimgray", ls='dashdot')

            fig.tight_layout()
            #plt.show()

            #fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.png', bbox_inches='tight')
            fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.pdf', bbox_inches='tight')

        if core == "multiriscy":
            speedup_single_multiriscy = stats_2d_sr/stats_2d

            fig, ax = plt.subplots()

            im, cbar = heatmap(np.flip(speedup_single_multiriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Speedup", xlabel="Output size", ylabel="Input size", fig_title="Speedup of Single-Layer MLP on Multi-Ri5cy Cores wrt. Single-Ri5cy Core")
            texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

            # Lines to separate use_dma and neuron_wise
            addlines(ax, corners=neuron_wise, y_axis_size=len(in_labels), linewidth=0.8, color="dimgray", ls='dashdot')

            fig.tight_layout()
            #plt.show()

            #fig.savefig('./plots/'+fname[:-4]+'_speedup_single_multiriscy.png', bbox_inches='tight')
            fig.savefig('./plots/'+fname[:-4]+'_speedup_single_multiriscy.pdf', bbox_inches='tight')

        if core == "fc":
            title_tmp = "Single-Ibex Core"
        elif core == "singleriscy":
            title_tmp = "Single-Ri5cy Core"
        else:
            title_tmp = "Multi-Ri5cy Cores"

        fig, ax = plt.subplots()

        im, cbar = heatmap(np.flip(stats_2d/1000, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="PuBu", cbarlabel="Number of cycles in units of thousands", xlabel="Output size", ylabel="Input size", fig_title="Number of Cycles of Single-Layer MLP on "+title_tmp)
        texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize-1)

        if core == "fc":
            addlines(ax, corners=use_shared_L2, y_axis_size=len(in_labels), linewidth=0.8, color="mediumpurple", ls=(0, (1, 1)))
        else:
            # Lines to separate use_dma and neuron_wise
            addlines(ax, corners=neuron_wise, y_axis_size=len(in_labels), linewidth=0.8, color="dimgray", ls='dashdot')

        fig.tight_layout()
        #plt.show()

        #fig.savefig('./plots/'+fname[:-4]+'_'+core+'.png', bbox_inches='tight')
        fig.savefig('./plots/'+fname[:-4]+'_'+core+'.pdf', bbox_inches='tight')
