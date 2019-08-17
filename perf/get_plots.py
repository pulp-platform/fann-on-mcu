import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib import collections  as mc



def heatmap(data, row_labels, col_labels, labelsize, ax=None,
            cbar_kw={}, cbarlabel="", xlabel="", ylabel="", **kwargs):
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

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", fontsize=labelsize)
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

def addlines(ax, lines):
    #lines = [[(4.5, 5.5), (4.5, 6.5)], [(4.5, 6.5), (5.5, 6.5)], [(5.5, 6.5), (6.5, 6.5)]]

    lc = mc.LineCollection(lines, color="k", linewidths=1)
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

    for core in core_list:
        stats_2d = np.empty((in_maxsize, out_maxsize))
        stats_2d[:] = np.nan
        for i in range(len(stats)):
            n_in = int(stats["NUM_INPUT_"+core][i]/in_step) - int(in_start/in_step)
            n_out = int(stats["NUM_OUTPUT_"+core][i]/out_step) - int(out_start/out_step)
            stats_2d[n_in, n_out] = stats["mean_cycles_"+core][i]
        in_labels = np.sort(np.unique(stats["NUM_INPUT_"+core].to_numpy()))
        out_labels = np.sort(np.unique(stats["NUM_OUTPUT_"+core].to_numpy()))
        if core == "fc":
            stats_2d_fc = stats_2d
        if core == "singleriscy":
            speedup_fc_singleriscy = stats_2d_fc/stats_2d
            stats_2d_sr = stats_2d

            fig, ax = plt.subplots()

            im, cbar = heatmap(np.flip(speedup_fc_singleriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Number of cycles", xlabel="Output size", ylabel="Input size")
            texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

            fig.tight_layout()
            #plt.show()

            #fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.png', bbox_inches='tight')
            fig.savefig('./plots/'+fname[:-4]+'_speedup_fc_singleriscy.pdf', bbox_inches='tight')

        if core == "multiriscy":
            speedup_single_multiriscy = stats_2d_sr/stats_2d

            fig, ax = plt.subplots()

            im, cbar = heatmap(np.flip(speedup_single_multiriscy, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Number of cycles", xlabel="Output size", ylabel="Input size")
            texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

            fig.tight_layout()
            #plt.show()

            #fig.savefig('./plots/'+fname[:-4]+'_speedup_single_multiriscy.png', bbox_inches='tight')
            fig.savefig('./plots/'+fname[:-4]+'_speedup_single_multiriscy.pdf', bbox_inches='tight')


        fig, ax = plt.subplots()

        im, cbar = heatmap(np.flip(stats_2d/1000, 0), np.flip(in_labels), out_labels, labelsize, ax=ax, cmap="YlGn", cbarlabel="Number of cycles in units of thousands", xlabel="Output size", ylabel="Input size")
        texts = annotate_heatmap(im, valfmt="{x:.1f}", fontsize=fontsize)

        fig.tight_layout()
        #plt.show()

        #fig.savefig('./plots/'+fname[:-4]+'_'+core+'.png', bbox_inches='tight')
        fig.savefig('./plots/'+fname[:-4]+'_'+core+'.pdf', bbox_inches='tight')
