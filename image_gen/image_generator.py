"""
Description:    Generate images for LES gradient-based optimization validation study
Author:         Jared J. Thomas, Austin Schenk
Date:           2017
Affiliation:    Brigham Young University, FLOW Lab

"""

import numpy as np
from math import radians
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import ttest_ind
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.patches import Ellipse, Rectangle, Polygon
import pandas as pd
import seaborn as sns
import re
from time import sleep


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", use_cbar=True, **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Arguments:
        data       : A 2D numpy array of shape (N,M)
        row_labels : A list or array of length N with the labels
                     for the rows
        col_labels : A list or array of length M with the labels
                     for the columns
    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    if use_cbar:
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
    else:
        cbar = None

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=False, labelbottom=True)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-0, ha="center",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "black"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Arguments:
        im         : The AxesImage to be labeled.
    Optional arguments:
        data       : Data used to annotate. If None, the image's data is used.
        valfmt     : The format of the annotations inside the heatmap.
                     This should either use the string format method, e.g.
                     "$ {x:.2f}", or be a :class:`matplotlib.ticker.Formatter`.
        textcolors : A list or array of two color specifications. The first is
                     used for values below a threshold, the second for those
                     above.
        threshold  : Value in data units according to which the colors from
                     textcolors are applied. If None (the default) uses the
                     middle of the colormap as separation.

    Further arguments are passed on to the created text labels.
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
        valfmt = ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[im.norm(data[i, j]) > threshold])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def plot_windrose(direction, values, ticks, minor_ticks=0, tick_angle=-32., unit='', title='', show=True, save=False,
                  file_name='figure1.pdf', plot_radius=None, bottom=0.):
    if plot_radius == None:
        plot_radius = max(ticks)

    direction += 270.
    for i in range(len(direction)):
        direction[i] = radians(direction[i]) * -1.

    N = direction.size
    # bottom = 0.
    # max_height = max(ws)
    # N = 36

    width = (2 * np.pi) / N

    direction -= width / 2.

    ax = plt.subplot(111, polar=True)

    tick_labels = list()

    minor_tick_distance = (ticks[1] - ticks[0]) / (minor_ticks + 1.)

    for major_tick_count in np.arange(0, len(ticks)):
        tick_labels.append('%.1f %s' % (ticks[major_tick_count], unit))
        circle_radius = ticks[major_tick_count]
        circle = plt.Circle((0.0, 0.0), circle_radius, transform=ax.transData._b,
                            facecolor=None, edgecolor='k', fill=False, alpha=0.2,
                            linestyle='-')
        ax.add_artist(circle)

    if minor_ticks > 0 and len(ticks) > 1:

        for major_tick_count in range(0, len(ticks)):

            if major_tick_count < (len(ticks)):
                for minor_tick_count in range(0, minor_ticks):
                    circle_radius = ticks[major_tick_count] + (minor_tick_count + 1) * minor_tick_distance
                    circle = plt.Circle((0.0, 0.0), circle_radius, transform=ax.transData._b,
                                        facecolor=None, edgecolor='k', fill=False, alpha=0.2,
                                        linestyle=':')
                    ax.add_artist(circle)
    #
    # ticks.append(plot_radius)
    # tick_labels.append('')
    # ticks.append(5.0)
    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]
    bars = ax.bar(direction, values, width=width, bottom=bottom, alpha=0.75, color=colors[1], edgecolor=None)
    print(ticks)
    print(tick_labels)
    ax.set_rgrids(ticks, angle=tick_angle)
    ax.yaxis.grid(linestyle='-', alpha=1.0)
    # tick_labels.append("5")
    ax.set_yticklabels(tick_labels)

    plt.title(title, y=1.07)

    ax.set_xticks([0, np.pi/4, np.pi/2, np.pi*3/4, np.pi, 5*np.pi/4, 3*np.pi/2, 7*np.pi/4])
    ax.set_xticklabels(['', '', 'N', '', '', '', '', ''])


    if save:
        plt.savefig(file_name, transparent=True)
    if show:
        plt.show()


def make_windrose_plots(filename, save_figs, show_figs, presentation=False, dirs=20):

    # load data
    data_directory = './image_data/'
    if dirs == 12:
        data_file = 'nantucket_wind_rose_for_LES.txt'
    elif dirs == 20:
        data_file = 'directional_windrose.txt'
    elif dirs == 36:
        data_file = 'nantucket_windrose_ave_speeds.txt'
    elif dirs == 72:
        data_file = 'windrose_amalia_directionally_averaged_speeds.txt'

    plot_data = np.loadtxt(data_directory + data_file)
    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]

    # parse data
    direction = plot_data[:, 0]
    speed = plot_data[:, 1]
    frequency = plot_data[:, 2]

    # set plot params
    print(np.min(speed))
    if dirs == 12:
        spacing = 5
        minor_ticks = spacing - 1
    elif dirs == 20:
        spacing = 5
        minor_ticks = spacing - 1
    elif dirs == 36:
        spacing = 2
        minor_ticks = spacing - 1
    elif dirs == 72:
        spacing = 1
        minor_ticks = 4
    ticks = list(np.arange(0, np.ceil(np.max(frequency)*100.0+spacing/2), spacing))
    
    print(ticks)
    plot_windrose(direction=np.copy(direction) - 0.5*360/dirs, values=frequency * 100., ticks=ticks, tick_angle=-45.0, unit='%', show=show_figs,
                  save=save_figs, file_name="freq"+filename, minor_ticks=minor_ticks)

    fig = plt.gcf()
    plt.close(fig)
    if dirs == 12:
        spacing = 5
    elif dirs == 20:
        spacing = 5
    elif dirs == 36:
        spacing = 2
    elif dirs == 72:
        spacing = 5

    ticks = list(np.arange(0, np.ceil(np.max(speed)+spacing/2), spacing))
    print(ticks)
    plot_windrose(direction=direction - 0.5*360/dirs, values=speed, ticks=ticks, tick_angle=-45.0, unit='m/s', show=show_figs,
                  save=save_figs, file_name='speed'+filename, minor_ticks=spacing-1)

def get_statistics_38_turbs():

    # data_ps_mstart = np.loadtxt("./image_data/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
    # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    # data_snopt_mstart = np.loadtxt("./image_data/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    # data_snopt_relax = np.loadtxt("./image_data/snopt_relax_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all_tolgens1200.txt")
    data_snopt_mstart = np.loadtxt("./image_data/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    data_snopt_relax = np.loadtxt("./image_data/snopt_relax_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
    # aep run opt (kW), run time (s), obj func calls, sens func calls
    sr_id = data_snopt_relax[:, 0]
    sr_ef = data_snopt_relax[:, 1]
    sr_orig_aep = data_snopt_relax[0, 5]
    # sr_run_start_aep = data_snopt_relax[0, 7]
    sr_run_end_aep = data_snopt_relax[sr_ef==1, 7]
    sr_run_time = data_snopt_relax[:, 8]
    sr_fcalls = data_snopt_relax[:, 9]
    sr_scalls = data_snopt_relax[:, 10]

    sr_run_improvement = sr_run_end_aep / sr_orig_aep - 1.
    sr_mean_run_improvement = np.average(sr_run_improvement)
    sr_std_improvement = np.std(sr_run_improvement)

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    sm_id = data_snopt_mstart[:, 0]
    sm_ef = np.ones_like(sm_id)
    sm_orig_aep = data_snopt_mstart[0, 4]
    # sr_run_start_aep = data_snopt_relax[0, 7]
    sm_run_end_aep = data_snopt_mstart[:, 6]
    sm_run_time = data_snopt_mstart[:, 7]
    sm_fcalls = data_snopt_mstart[:, 8]
    sm_scalls = data_snopt_mstart[:, 9]

    # sm_run_improvement = sm_run_end_aep / sm_orig_aep - 1.
    sm_run_improvement = sm_run_end_aep / sr_orig_aep - 1.
    sm_mean_run_improvement = np.average(sm_run_improvement)
    sm_std_improvement = np.std(sr_run_improvement)

    # sr_tfcalls = np.zeros(200)
    # sr_tscalls = np.zeros(200)
    # for i in np.arange(0, 200):
    #     sr_tfcalls[i] = np.sum(sr_fcalls[sr_id == i])
    #     sr_tscalls[i] = np.sum(sr_scalls[sr_id == i])

    sr_tfcalls = sr_fcalls[sr_ef == 1]
    sr_tscalls = sr_fcalls[sr_ef == 1]

    # get variables
    nTurbines = 38
    nvars = 2*nTurbines
    nCons = 741
    scale_aep = 1E-6

    # get fcalls: med, ave, std-dev
    # s
    s_med_fcalls = np.median(sm_fcalls)
    s_ave_fcalls = np.average(sm_fcalls)
    s_std_fcalls = np.std(sm_fcalls)
    s_low_fcalls = np.min(sm_fcalls)
    s_high_fcalls = np.max(sm_fcalls)

    # sr
    sr_med_fcalls = np.median(sr_tfcalls+sr_tscalls)
    sr_ave_fcalls = np.average(sr_tfcalls+sr_tscalls)
    sr_std_fcalls = np.std(sr_tfcalls+sr_tscalls)
    sr_low_fcalls = np.min(sr_tfcalls+sr_tscalls)
    sr_high_fcalls = np.max(sr_tfcalls+sr_tscalls)

    # get aep: base, med, ave, std-dev, low, high
    # s
    s_base_aep = sm_orig_aep*scale_aep
    s_med_aep = np.median(sm_run_end_aep)*scale_aep
    s_ave_aep = np.average(sm_run_end_aep)*scale_aep
    s_std_aep = np.std(sm_run_end_aep)*scale_aep
    s_low_aep = np.min(sm_run_end_aep)*scale_aep
    s_high_aep = np.max(sm_run_end_aep)*scale_aep
    s_best_layout = sm_id[np.argmax(sm_run_end_aep)]

    # sr
    sr_base_aep = sr_orig_aep*scale_aep
    sr_med_aep = np.median(sr_run_end_aep)*scale_aep
    sr_ave_aep = np.average(sr_run_end_aep)*scale_aep
    sr_std_aep = np.std(sr_run_end_aep)*scale_aep
    sr_low_aep = np.min(sr_run_end_aep)*scale_aep
    sr_high_aep = np.max(sr_run_end_aep)*scale_aep
    sr_best_layout = sr_id[np.argmax(sr_run_end_aep)]

    print( "nturbs: ", nTurbines)
    print( "nvars: ", nvars)
    print( "ncons: ", nCons)

    print( " ")

    print( "snopt mstart results: ")
    print( "med fcalls: ", s_med_fcalls)
    print( "ave fcalls: ", s_ave_fcalls)
    print( "std fcalls: ", s_std_fcalls)
    print( "low fcalls: ", s_low_fcalls)
    print( "high fcalls: ", s_high_fcalls)
    print( "base aep: ", s_base_aep)
    print( "med aep: ", s_med_aep)
    print( "ave aep: ", s_ave_aep)
    print( "std aep: ", s_std_aep)
    print( "low aep: ", s_low_aep)
    print( "high aep: ", s_high_aep)
    print( "best layout: ", s_best_layout)

    print( " ")

    print( "snopt relax results: ")
    print( "med fcalls: ", sr_med_fcalls)
    print( "ave fcalls: ", sr_ave_fcalls)
    print( "std fcalls: ", sr_std_fcalls)
    print( "low fcalls: ", sr_low_fcalls)
    print( "high fcalls: ", sr_high_fcalls)
    print( "base aep: ", sr_base_aep)
    print( "med aep: ", sr_med_aep)
    print( "ave aep: ", sr_ave_aep)
    print( "std aep: ", sr_std_aep)
    print( "low aep: ", sr_low_aep)
    print( "high aep: ", sr_high_aep)
    print( "best layout: ", sr_best_layout)

    print( " ")

    return

def get_statistics_case_studies(turbs, dirs=None, fnamstart="", save_figs=False, show_figs=True, lt0=True):

    if turbs == 16:
        # resdir = "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/"
        resdir = "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/"
        data_ps_mstart = np.loadtxt(resdir + "ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
        data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
        data_snopt_relax = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")

    elif turbs == 38:
        # resdir = "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/"
        resdir = "./image_data/opt_results/20200821-38-turbs-36-dir-fcall-and-conv-history/"
        data_ps_mstart = np.loadtxt(resdir + "ps/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
        data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
        data_snopt_relax = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")

        if dirs == 12:
            # resdir = "./image_data/20200602-38-turbs-12-dir-nsteps-maxweca9/"
            resdir = "./image_data/opt_results/20200821-38-turbs-12-dir-fcall-and-conv-history/"
            data_ps_mstart = np.loadtxt(
                resdir + "ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
            data_snopt_mstart = np.loadtxt(
                resdir + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            data_snopt_relax = np.loadtxt(
                resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")


    elif turbs == 60:
        # resdir = "./image_data/opt_results/20200527-60-turbs-72-dir-amalia-maxwecd3-nsteps6/"
        resdir = "./image_data/opt_results/20200824-60-turbs-72-dir-fcall-and-conv-history/"
        data_ps_mstart = np.loadtxt(resdir + "ps/ps_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
        data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
        data_snopt_relax = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")

    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
    # aep run opt (kW), run time (s), obj func calls, sens func calls
    sr_id = data_snopt_relax[:, 0]
    sr_ef = data_snopt_relax[:, 1]
    sr_orig_aep = data_snopt_relax[0, 5]
    sr_run_ti = data_snopt_relax[:, 3]
    # sr_run_start_aep = data_snopt_relax[0, 7]
    sr_run_end_aep = data_snopt_relax[sr_run_ti==5, 7]
    sr_run_time = data_snopt_relax[:, 8]
    sr_fcalls = data_snopt_relax[:, 9]
    sr_scalls = data_snopt_relax[:, 10]

    sr_run_improvement = sr_run_end_aep / sr_orig_aep - 1.
    sr_mean_run_improvement = np.average(sr_run_improvement)
    sr_std_improvement = np.std(sr_run_improvement)

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    sm_id = data_snopt_mstart[:, 0]
    sm_ef = np.ones_like(sm_id)
    sm_orig_aep = data_snopt_mstart[0, 4]
    sm_run_ti = data_snopt_mstart[:, 2]
    # sr_run_start_aep = data_snopt_relax[0, 7]
    sm_run_end_aep = data_snopt_mstart[sm_run_ti==5, 6]
    sm_run_time = data_snopt_mstart[:, 7]
    sm_fcalls = data_snopt_mstart[:, 8]
    sm_scalls = data_snopt_mstart[:, 9]

    # sm_run_improvement = sm_run_end_aep / sm_orig_aep - 1.
    sm_run_improvement = sm_run_end_aep / sr_orig_aep - 1.
    sm_mean_run_improvement = np.average(sm_run_improvement)
    sm_std_improvement = np.std(sr_run_improvement)

    # sr_tfcalls = np.zeros(200)
    # sr_tscalls = np.zeros(200)
    # for i in np.arange(0, 200):
    #     sr_tfcalls[i] = np.sum(sr_fcalls[sr_id == i])
    #     sr_tscalls[i] = np.sum(sr_scalls[sr_id == i])

    sr_tfcalls = sr_fcalls[sr_ef == 1]
    sr_tscalls = sr_fcalls[sr_ef == 1]

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    ps_id = data_ps_mstart[:, 0]
    ps_ef = np.ones_like(ps_id)
    ps_orig_aep = data_ps_mstart[0, 4]
    ps_run_ti = data_ps_mstart[:, 2]
    # sr_run_start_aep = data_snopt_relax[0, 7]
    ps_run_end_aep = data_ps_mstart[ps_run_ti == 4, 6]
    ps_run_time = data_ps_mstart[:, 7]
    ps_fcalls = data_ps_mstart[:, 8]
    ps_scalls = data_ps_mstart[:, 9]

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_improvement = ps_run_end_aep / sr_orig_aep - 1.
    ps_mean_run_improvement = np.average(ps_run_improvement)
    ps_std_improvement = np.std(sr_run_improvement)

    # get variables
    nTurbines = turbs
    nvars = 2*nTurbines
    nCons = int(((nTurbines - 1.) * nTurbines / 2.)) + 1 * nTurbines
    scale_aep = 1E-6

    # get fcalls: med, ave, std-dev
    # s
    s_med_fcalls = np.median(sm_fcalls)
    s_ave_fcalls = np.average(sm_fcalls)
    s_std_fcalls = np.std(sm_fcalls)
    s_low_fcalls = np.min(sm_fcalls)
    s_high_fcalls = np.max(sm_fcalls)

    # sr
    sr_med_fcalls = np.median(sr_tfcalls+sr_tscalls)
    sr_ave_fcalls = np.average(sr_tfcalls+sr_tscalls)
    sr_std_fcalls = np.std(sr_tfcalls+sr_tscalls)
    sr_low_fcalls = np.min(sr_tfcalls+sr_tscalls)
    sr_high_fcalls = np.max(sr_tfcalls+sr_tscalls)

    # get fcalls: med, ave, std-dev
    # ps
    ps_med_fcalls = np.median(ps_fcalls)
    ps_ave_fcalls = np.average(ps_fcalls)
    ps_std_fcalls = np.std(ps_fcalls)
    ps_low_fcalls = np.min(ps_fcalls)
    ps_high_fcalls = np.max(ps_fcalls)

    # get aep: base, med, ave, std-dev, low, high
    # s
    s_base_aep = sm_orig_aep*scale_aep
    s_med_aep = np.median(sm_run_end_aep)*scale_aep
    s_ave_aep = np.average(sm_run_end_aep)*scale_aep
    s_std_aep = np.std(sm_run_end_aep)*scale_aep
    s_low_aep = np.min(sm_run_end_aep)*scale_aep
    s_high_aep = np.max(sm_run_end_aep)*scale_aep
    s_best_layout = sm_id[np.argmax(sm_run_end_aep)]

    # sr
    sr_base_aep = sr_orig_aep*scale_aep
    sr_med_aep = np.median(sr_run_end_aep)*scale_aep
    sr_ave_aep = np.average(sr_run_end_aep)*scale_aep
    sr_std_aep = np.std(sr_run_end_aep)*scale_aep
    sr_low_aep = np.min(sr_run_end_aep)*scale_aep
    sr_high_aep = np.max(sr_run_end_aep)*scale_aep
    sr_best_layout = sr_id[np.argmax(sr_run_end_aep)]

    # get aep: base, med, ave, std-dev, low, high
    # ps
    ps_base_aep = ps_orig_aep * scale_aep
    ps_med_aep = np.median(ps_run_end_aep) * scale_aep
    ps_ave_aep = np.average(ps_run_end_aep) * scale_aep
    ps_std_aep = np.std(ps_run_end_aep) * scale_aep
    ps_low_aep = np.min(ps_run_end_aep) * scale_aep
    ps_high_aep = np.max(ps_run_end_aep) * scale_aep
    ps_best_layout = ps_id[np.argmax(ps_run_end_aep)]

    print( "nturbs: ", nTurbines)
    print( "nvars: ", nvars)
    print( "ncons: ", nCons)

    print( " ")

    print( "snopt mstart results: ")
    print( "med fcalls: ", s_med_fcalls)
    print( "ave fcalls: ", s_ave_fcalls)
    print( "std fcalls: ", s_std_fcalls)
    print( "low fcalls: ", s_low_fcalls)
    print( "high fcalls: ", s_high_fcalls)
    print( "base aep: ", s_base_aep)
    print( "med aep: ", s_med_aep)
    print( "ave aep: ", s_ave_aep)
    print( "std aep: ", s_std_aep)
    print( "low aep: ", s_low_aep)
    print( "high aep: ", s_high_aep)
    print( "best layout: ", s_best_layout)

    print( " ")

    print( "snopt relax results: ")
    print( "med fcalls: ", sr_med_fcalls)
    print( "ave fcalls: ", sr_ave_fcalls)
    print( "std fcalls: ", sr_std_fcalls)
    print( "low fcalls: ", sr_low_fcalls)
    print( "high fcalls: ", sr_high_fcalls)
    print( "base aep: ", sr_base_aep)
    print( "med aep: ", sr_med_aep)
    print( "ave aep: ", sr_ave_aep)
    print( "std aep: ", sr_std_aep)
    print( "low aep: ", sr_low_aep)
    print( "high aep: ", sr_high_aep)
    print( "best layout: ", sr_best_layout)

    print(" ")

    print("ALPSO mstart results: ")
    print("med fcalls: ", ps_med_fcalls)
    print("ave fcalls: ", ps_ave_fcalls)
    print("std fcalls: ", ps_std_fcalls)
    print("low fcalls: ", ps_low_fcalls)
    print("high fcalls: ", ps_high_fcalls)
    print("base aep: ", ps_base_aep)
    print("med aep: ", ps_med_aep)
    print("ave aep: ", ps_ave_aep)
    print("std aep: ", ps_std_aep)
    print("low aep: ", ps_low_aep)
    print("high aep: ", ps_high_aep)
    print("best layout: ", ps_best_layout)

    print(" ")

    labels = ["SNOPT", "SNOPT+WECD", "ALPSO"]
    fig, ax = plt.subplots(1)

    if not lt0:
        sm_run_improvement = sm_run_improvement[sm_run_improvement>=0]
        sr_run_improvement = sr_run_improvement[sr_run_improvement>=0]
        ps_run_improvement = ps_run_improvement[ps_run_improvement>=0]

    impdata = list([sm_run_improvement * 100, sr_run_improvement*100, ps_run_improvement*100])
    ax.boxplot(impdata, meanline=True, labels=labels)

    ax.set_ylabel('AEP Improvement (%)')
    # ax.set_ylim([0.0, np.max(impdata)+1])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    plt.tight_layout()
    if save_figs:
        plt.savefig(fnamstart + '_percentaep.pdf', transparent=True)

    if show_figs:
        plt.show()


def plot_max_wec_const_nstep_results(filename, save_figs, show_figs, nturbs=38, from_convergence_history=True, wecdonly=True):

    if nturbs == 38:

        # set max wec values for each method
        wavals = np.append(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), np.arange(10, 41, 5))
        wdvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])
        whvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])

        # 202003
        nwa = np.size(wavals)
        nwd = np.size(wdvals)
        nwh = np.size(whvals)

        nwaarray = np.zeros(nwa)
        nwdarray = np.zeros(nwd)
        nwharray = np.zeros(nwh)

        # prepare to store max aep percent improvement values
        max_aepi = np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()])

        # prepare to store min aep percent improvement values
        min_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        med_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        mean_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store standard deviation of aep percent improvement values
        std_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # set results directory
        # rdir = "./image_data/opt_results/202004011312-max-wec-const-nsteps6/"
        rdir = "./image_data/opt_results/20200520-38-turbs-12-dir-nsteps6-maxwec/"
        psrdir = "./image_data/opt_results/202101042132-alpso-runs-random-seed/ps/"
        srdir = "./image_data/opt_results/20200821-38-turbs-12-dir-fcall-and-conv-history/snopt/"
        # set wec method directory perfixes
        wadirp = "snopt_wec_angle_max_wec_"
        wddirp = "snopt_wec_diam_max_wec_"
        whdirp = "snopt_wec_hybrid_max_wec_"

        approaches = np.array([wadirp,wddirp,whdirp])

        # set base file name
        bfilename = "snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt"

        wec_step_ranges = np.array([wavals,wdvals,whvals])

    else:
        ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)

    # load baseline data
    base_data = np.loadtxt(rdir + wadirp + "%i_nsteps_" %(5) + "6.000" + "/" + bfilename)

    # store baseline aep value
    orig_aep = base_data[0, 5]

    # define maximum AEP
    max_possible_aep = 189.77548752 * 1E6  # GWh -> kWh

    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]
    # loop through each wec approach
    for i in np.arange(0,np.size(approaches)):
        approach = approaches[i]
        max_wec_range = wec_step_ranges[i]
        # print(approach)
        print(max_wec_range)
        print('size of wec range', np.size(max_wec_range))
        # loop through each max wec value for current approach
        for j in np.arange(0, np.size(max_wec_range)):
            # print(max_wec_range[j])
            wec_val = max_wec_range[j]

            # load data set
            data_file = rdir + approach + "%i_nsteps_" %(wec_val) + "%.3f" %(6) + "/" + bfilename
            try:
                data_set = np.loadtxt(data_file)
            except:
                print("Failed to find data for ", data_file)
                print("Setting values to None")
                max_aepi[i][j] = None
                min_aepi[i][j] = None
                med_aepi[i][j] = None
                std_aepi[i][j] = None
                continue
            print("loaded data for %i, %i" %(i,j))
            # compile data from all intermediate wec values
            id = data_set[:, 0]
            ef = data_set[:, 1]
            ti_opt = data_set[:, 3]
            run_end_aep = data_set[ti_opt == 5, 7]
            run_time = data_set[:, 8]
            fcalls = data_set[:, 9]
            scalls = data_set[:, 10]

            tfcalls = fcalls[ti_opt == 5]
            tscalls = fcalls[ti_opt == 5]

            # compute percent improvement from base for current set
            run_wake_loss = 100*(1.0 - run_end_aep / max_possible_aep)

            # store max percent improvement from base for current set
            max_run_wake_loss = np.max(run_wake_loss)
            max_aepi[i][j] = max_run_wake_loss
            # if i==2:
            #     print(max_aepi[i][j])

            # store min percent improvement from base for current set
            min_run_wake_loss = np.min(run_wake_loss)
            min_aepi[i][j] = min_run_wake_loss

            # store average percent improvement from base for current set
            mean_run_wake_loss = np.average(run_wake_loss)
            mean_aepi[i][j] = mean_run_wake_loss

            # store median percent improvement from base for current set
            median_run_wake_loss = np.median(run_wake_loss)
            med_aepi[i][j] = median_run_wake_loss

            # store std percent improvement from base for current set
            std_run_wake_loss = np.std(run_wake_loss)
            std_aepi[i][j] = std_run_wake_loss
            # if i==2:
            #     print(std_aepi[i][j])

        # end loop through wec values

    # end loop through methods

    if from_convergence_history:

        # load data
        prescaleaep = 1E-3 # convert from Wh to kWh
        resdir = "./image_data/opt_results/202103041633-mined-opt-results-from-conv-hist/"
        data_snopt_mstart = np.loadtxt(resdir+"snopt_results_%smodel_%iturbs_%idirs.txt" %("BPA", nturbs, 12))
        snw_id = data_snopt_mstart[:, 0]
        snw_orig_aep = data_snopt_mstart[:, 1]*prescaleaep
        snw_run_end_aep = data_snopt_mstart[:, 2]*prescaleaep
        snw_tfcalls = data_snopt_mstart[:, 3]
        snw_tscalls = np.zeros_like(snw_tfcalls)

        data_ps_mstart = np.loadtxt(resdir+"alpso_results_%smodel_%iturbs_%idirs.txt" %("BPA", nturbs, 12))
        ps_id = data_ps_mstart[:, 0]
        ps_orig_aep = data_ps_mstart[:, 1]*prescaleaep
        ps_run_end_aep = data_ps_mstart[:, 2]*prescaleaep
        ps_fcalls = data_ps_mstart[:, 3]
        
        scale_aep = 1E-6
    else:
        # load SNOPT data
        data_snopt_no_wec = np.loadtxt(
            srdir+"snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

        # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
        # run time (s), obj func calls, sens func calls
        snw_id = data_snopt_no_wec[:, 0]
        snw_ef = np.ones_like(snw_id)
        snw_orig_aep = data_snopt_no_wec[0, 4]
        # swa_run_start_aep = data_snopt_relax[0, 7]
        snw_run_end_aep = data_snopt_no_wec[:, 6]
        snw_run_time = data_snopt_no_wec[:, 7]
        snw_fcalls = data_snopt_no_wec[:, 8]
        snw_scalls = data_snopt_no_wec[:, 9]

        # load ALPSO data
        data_ps = np.loadtxt(psrdir+"ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
        ps_id = data_ps[:, 0]
        ps_ef = np.ones_like(ps_id)
        ps_orig_aep = data_ps[0, 4]
        # swa_run_start_aep = data_ps[0, 7]
        ps_run_end_aep = data_ps[:, 6]
        ps_run_time = data_ps[:, 7]
        ps_fcalls = data_ps[:, 8]
        ps_scalls = data_ps[:, 9]

    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_wake_loss = 100*(1.0 - snw_run_end_aep / max_possible_aep)
    snw_mean_wake_loss = np.average(snw_run_wake_loss)
    snw_std_wake_loss = np.std(snw_run_wake_loss)
    snw_max_wake_loss = np.max(snw_run_wake_loss)
    snw_min_wake_loss = np.min(snw_run_wake_loss)

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_wake_loss = 100*(1.0 - ps_run_end_aep / max_possible_aep)
    ps_mean_wake_loss = np.average(ps_run_wake_loss)
    ps_median_wake_loss = np.median(ps_run_wake_loss)
    ps_std_wake_loss = np.std(ps_run_wake_loss)
    ps_max_wake_loss = np.max(ps_run_wake_loss)
    ps_min_wake_loss = np.min(ps_run_wake_loss)

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()
    ax2 = ax1.twiny()
    # colors = ['tab:red', 'tab:blue', 'tab:blue', 'k']
    colors = ["#F5793A", "#0F2080", "#85C0F9", "#BDB8AD", "#A95AA1", "#382119"]

    ax1.set_xlabel('Max WEC Value', color=colors[1])
    ax1.tick_params(axis='x', labelcolor=colors[1])

    ax2.set_xlabel('Max WEC Angle (deg.)', color=colors[0])
    ax2.tick_params(axis='x', labelcolor=colors[0])

    ax1.set_ylabel("Minimum Wake Loss (%)")

    if wecdonly:
        labels = ["WEC-A", "SNOPT+WEC", "WEC-H", 'ALPSO', 'SNOPT']
    else:
        labels = ["WEC-A", "WEC-D", "WEC-H", 'ALPSO', 'SNOPT']

    aplt, = ax2.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
    dplt, = ax1.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    hplt, = ax1.plot(wec_step_ranges[2], min_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none")
    pplt, = ax1.plot([2,10], [ps_min_wake_loss, ps_min_wake_loss], '--', label=labels[3], color=colors[3])
    splt, = ax1.plot([2,10], [snw_min_wake_loss, snw_min_wake_loss], ':', label=labels[4], color=colors[2])
    # ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
    plt.ylim([11, 16])
    # ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax1.yaxis.set_ticks_position('left')
    ax2.yaxis.set_ticks_position('left')
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_min.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    plt.gcf().clear()
    

    if wecdonly:
        fig, ax1 = plt.subplots(figsize=(6,3))

        ax1.set_xlabel('Max WEC Value', color='k')
        ax1.tick_params(axis='x', labelcolor='k')

        ax1.set_ylabel("Mean Wake Loss (%)")

        pplt, = ax1.plot([2,10], [ps_mean_wake_loss, ps_mean_wake_loss], '--k', label=labels[3], color=colors[3])
        splt, = ax1.plot([2,10], [snw_mean_wake_loss, snw_mean_wake_loss], ':k', label=labels[4], color=colors[2])
        dplt, = ax1.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
        # ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[pplt, splt, dplt], frameon=False)
        plt.ylim([13, 17])
        plt.xlim([1.6, 10.4])
        plt.xticks([2,4,6,8,10])
        # ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.yaxis.set_ticks_position('left')
        plt.tight_layout()

    else:
        fig, ax1 = plt.subplots()
        ax2 = ax1.twiny()

        ax1.set_xlabel('Max WEC Value', color=colors[1])
        ax1.tick_params(axis='x', labelcolor=colors[1])

        ax1.set_ylabel("Mean Wake Loss (%)")

        ax2.set_xlabel('Max WEC Angle (deg.)', color=colors[0])
        ax2.tick_params(axis='x', labelcolor=colors[0])

        aplt, = ax2.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
        dplt, = ax1.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
        hplt, = ax1.plot(wec_step_ranges[2], mean_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none")
        pplt, = ax1.plot([2,10], [ps_mean_wake_loss, ps_mean_wake_loss], '--k', label=labels[3], color=colors[3])
        splt, = ax1.plot([2,10], [snw_mean_wake_loss, snw_mean_wake_loss], ':k', label=labels[4], color=colors[2])
        # ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
        plt.ylim([13, 20])
        # ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax1.yaxis.set_ticks_position('left')
        ax2.yaxis.set_ticks_position('left')
        plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_mean.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()
    ax2 = ax1.twiny()


    ax1.set_ylabel("Standard Deviation of Wake Loss (%)")
    
    ax1.set_xlabel('Max WEC Value', color=colors[1])
    ax1.tick_params(axis='x', labelcolor=colors[1])

    ax2.set_xlabel('Max WEC Angle (deg.)', color=colors[0])
    ax2.tick_params(axis='x', labelcolor=colors[0])

    aplt, = ax2.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
    dplt, = ax1.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    hplt, = ax1.plot(wec_step_ranges[2], std_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none")
    pplt, = ax1.plot([2,10], [ps_std_wake_loss, ps_std_wake_loss], '--', label=labels[3], color=colors[3])
    splt, = ax1.plot([2,10], [snw_std_wake_loss, snw_std_wake_loss], ':', label=labels[4], color=colors[2])

    # ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=[aplt, dplt, hplt, pplt, splt], frameon=False)
    plt.ylim([0.0, 2.0])
    plt.tight_layout()
    # ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax1.yaxis.set_ticks_position('left')
    ax2.yaxis.set_ticks_position('left')
    # ax1.xaxis.set_ticks_position('bottom')

    if save_figs:
        plt.savefig(filename+'_std.pdf', transparent=True)

    if show_figs:
        plt.show()
    #
    # # plot min percent improvement
    #
    # # set up plots
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Minimum Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], min_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_min_improvement, ps_min_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot average percent improvement
    # # set up plots
    # fig, ax1 = plt.subplots()
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Mean Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    # print(max_aepi[2])
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    #
    # # plot median percent improvement
    #
    # # plot std percent improvement
    # fig, ax1 = plt.subplots()
    #
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Std. of Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0, 1], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    # ax2.plot([0, 1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot ranges?

    return

def plot_maxwec3_nstep_results(filename, save_figs, show_figs, nturbs=38, from_convergence_history=True, wecdonly=True):

    if nturbs == 38:

        # set max wec values for each method
        wavals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])
        wdvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])
        whvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])

        # 202003
        nwa = np.size(wavals)
        nwd = np.size(wdvals)
        nwh = np.size(whvals)

        nwaarray = np.zeros(nwa)
        nwdarray = np.zeros(nwd)
        nwharray = np.zeros(nwh)

        # prepare to store max aep percent improvement values
        max_aepi = np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()])

        # prepare to store min aep percent improvement values
        min_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        med_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        mean_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store standard deviation of aep percent improvement values
        std_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # set results directory
        # rdir = "./image_data/opt_results/202004080902-nsteps-maxwec-3/"
        rdir = "./image_data/opt_results/20200602-38-turbs-12-dir-nsteps-maxweca9/"
        psrdir = "./image_data/opt_results/202101042132-alpso-runs-random-seed/ps/"
        srdir = "./image_data/opt_results/20200821-38-turbs-12-dir-fcall-and-conv-history/snopt/"
        
        # set wec method directory prefixes
        wadirp = "snopt_wec_angle_max_wec_9_nsteps_"
        wddirp = "snopt_wec_diam_max_wec_3_nsteps_"
        whdirp = "snopt_wec_hybrid_max_wec_3_nsteps_"

        approaches = np.array([wadirp,wddirp,whdirp])

        # set base file name
        bfilename = "snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt"

        wec_step_ranges = np.array([wavals,wdvals,whvals])

    else:
        ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)

    # load baseline data
    base_data = np.loadtxt(rdir + wadirp + "10.000" + "/" + bfilename)

    # store baseline aep value
    orig_aep = base_data[0, 5]

    # define maximum AEP
    max_possible_aep = 189.77548752 * 1E6  # GWh

    # loop through each wec approach
    for i in np.arange(0,np.size(approaches)):
        approach = approaches[i]
        max_wec_range = wec_step_ranges[i]
        # print(approach)
        print(max_wec_range)
        print('size of wec range', np.size(max_wec_range))
        # loop through each max wec value for current approach
        for j in np.arange(0, np.size(max_wec_range)):
            # print(max_wec_range[j])
            wec_val = max_wec_range[j]

            # load data set
            data_file = rdir + approach + "%.3f" %(wec_val) + "/" + bfilename
            try:
                data_set = np.loadtxt(data_file)
            except:
                print("Failed to find data for ", data_file)
                print("Setting values to None")
                max_aepi[i][j] = None
                min_aepi[i][j] = None
                med_aepi[i][j] = None
                std_aepi[i][j] = None
                continue
            print("loaded data for %i, %i" %(i,j))
            # compile data from all intermediate wec values
            id = data_set[:, 0]
            ef = data_set[:, 1]
            ti_opt = data_set[:, 3]
            run_end_aep = data_set[ti_opt == 5, 7]
            run_time = data_set[:, 8]
            fcalls = data_set[:, 9]
            scalls = data_set[:, 10]

            tfcalls = fcalls[ti_opt == 5]
            tscalls = fcalls[ti_opt == 5]

            # compute percent improvement from base for current set
            run_wake_loss = 100*(1.0 - run_end_aep / max_possible_aep)

            # store max percent improvement from base for current set
            max_run_improvement = np.max(run_wake_loss)
            max_aepi[i][j] = max_run_improvement
            # if i==2:
            #     print(max_aepi[i][j])

            # store min percent improvement from base for current set
            min_run_improvement = np.min(run_wake_loss)
            min_aepi[i][j] = min_run_improvement

            # store average percent improvement from base for current set
            mean_run_improvement = np.average(run_wake_loss)
            mean_aepi[i][j] = mean_run_improvement

            # store median percent improvement from base for current set
            median_run_improvement = np.median(run_wake_loss)
            med_aepi[i][j] = median_run_improvement

            # store std percent improvement from base for current set
            std_improvement = np.std(run_wake_loss)
            std_aepi[i][j] = std_improvement
            # if i==2:
            #     print(std_aepi[i][j])

        # end loop through wec values

    # end loop through methods
    if from_convergence_history:

        # load data
        prescaleaep = 1E-3 # convert from Wh to kWh
        resdir = "./image_data/opt_results/202103041633-mined-opt-results-from-conv-hist/"
        data_snopt_mstart = np.loadtxt(resdir+"snopt_results_%smodel_%iturbs_%idirs.txt" %("BPA", nturbs, 12))
        snw_id = data_snopt_mstart[:, 0]
        snw_orig_aep = data_snopt_mstart[:, 1]*prescaleaep
        snw_run_end_aep = data_snopt_mstart[:, 2]*prescaleaep
        snw_tfcalls = data_snopt_mstart[:, 3]
        snw_tscalls = np.zeros_like(snw_tfcalls)

        data_ps_mstart = np.loadtxt(resdir+"alpso_results_%smodel_%iturbs_%idirs.txt" %("BPA", nturbs, 12))
        ps_id = data_ps_mstart[:, 0]
        ps_orig_aep = data_ps_mstart[:, 1]*prescaleaep
        ps_run_end_aep = data_ps_mstart[:, 2]*prescaleaep
        ps_fcalls = data_ps_mstart[:, 3]
        
        scale_aep = 1E-6
    else:
        # load SNOPT data
        data_snopt_no_wec = np.loadtxt(
            srdir+"snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

        # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
        # run time (s), obj func calls, sens func calls
        snw_id = data_snopt_no_wec[:, 0]
        snw_ef = np.ones_like(snw_id)
        snw_orig_aep = data_snopt_no_wec[0, 4]
        # swa_run_start_aep = data_snopt_relax[0, 7]
        snw_run_end_aep = data_snopt_no_wec[:, 6]
        snw_run_time = data_snopt_no_wec[:, 7]
        snw_fcalls = data_snopt_no_wec[:, 8]
        snw_scalls = data_snopt_no_wec[:, 9]
        
        # load ALPSO data
        data_ps = np.loadtxt(psrdir+"ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
        ps_id = data_ps[:, 0]
        ps_ef = np.ones_like(ps_id)
        ps_orig_aep = data_ps[0, 4]
        # swa_run_start_aep = data_ps[0, 7]
        ps_run_end_aep = data_ps[:, 6]
        ps_run_time = data_ps[:, 7]
        ps_fcalls = data_ps[:, 8]
        ps_scalls = data_ps[:, 9]

    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_wake_loss = 100*(1.0 - snw_run_end_aep / max_possible_aep)
    snw_mean_wake_loss = np.average(snw_run_wake_loss)
    snw_std_wake_loss = np.std(snw_run_wake_loss)
    snw_max_wake_loss = np.max(snw_run_wake_loss)
    snw_min_wake_loss = np.min(snw_run_wake_loss)

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_wake_loss = 100*(1.0 - ps_run_end_aep / max_possible_aep)
    ps_mean_wake_loss = np.average(ps_run_wake_loss)
    ps_median_wake_loss = np.median(ps_run_wake_loss)
    ps_std_wake_loss = np.std(ps_run_wake_loss)
    ps_max_wake_loss = np.max(ps_run_wake_loss)
    ps_min_wake_loss = np.min(ps_run_wake_loss)

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()

    # colors = ['tab:red', 'tab:blue', 'tab:blue', 'k']
    colors = ["#F5793A", "#0F2080", "#85C0F9", "#BDB8AD", "#A95AA1", "#382119"]
    ax1.set_xlabel('Number of WEC Steps', color='k')
    ax1.set_ylabel("Minimum Wake Loss (%)")

    if wecdonly:
        labels = ["WEC-A", "SNOPT+WEC", "WEC-H", 'ALPSO', 'SNOPT']
    else:
        labels = ["WEC-A", "WEC-D", "WEC-H", 'ALPSO', 'SNOPT']
    
    wechms = 6

    ax1.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
    ax1.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[2], min_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none", markersize=wechms)
    ax1.plot([2,10], [ps_min_wake_loss, ps_min_wake_loss], '--', label=labels[3], color=colors[3])
    ax1.plot([2,10], [snw_min_wake_loss, snw_min_wake_loss], ':', label=labels[4], color=colors[2])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1, frameon=False)
    ax1.set_ylim([11, 15])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_min.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    plt.gcf().clear()

    if wecdonly:
        fig, ax1 = plt.subplots(figsize=(6,3))

        ax1.set_xlabel('Number of WEC Steps', color='k')
        ax1.set_ylabel("Mean Wake Loss (%)")
        ax1.plot([2,10], [ps_mean_wake_loss, ps_mean_wake_loss], '--', label=labels[3], color=colors[3])
        ax1.plot([2,10], [snw_mean_wake_loss, snw_mean_wake_loss], ':', label=labels[4], color=colors[2])
        ax1.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
        ax1.set_ylim([13, 17])
        plt.xticks([2,4,6,8,10])
    else:
        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Number of WEC Steps', color='k')
        ax1.set_ylabel("Mean Wake Loss (%)")

        ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
        ax1.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
        ax1.plot(wec_step_ranges[2], mean_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none", markersize=wechms)
        ax1.plot([2,10], [ps_mean_wake_loss, ps_mean_wake_loss], '--', label=labels[3], color=colors[3])
        ax1.plot([2,10], [snw_mean_wake_loss, snw_mean_wake_loss], ':', label=labels[4], color=colors[2])
        ax1.set_ylim([13, 17])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1, frameon=False)
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_mean.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Number of WEC Steps', color='k')
    ax1.set_ylabel("Standard Deviation of Wake Loss (%)")

    ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0], markerfacecolor="none")
    ax1.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[2], std_aepi[2], 'x', label=labels[2], color=colors[1], markerfacecolor="none", markersize=wechms)
    ax1.plot([2, 10], [ps_std_wake_loss, ps_std_wake_loss], '--k', label=labels[3])
    ax1.plot([2, 10], [snw_std_wake_loss, snw_std_wake_loss], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.set_ylim([0.3, 1.1])
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1, frameon=False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_std.pdf', transparent=True)

    if show_figs:
        plt.show()
    #
    # # plot min percent improvement
    #
    # # set up plots
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Minimum Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], min_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_min_improvement, ps_min_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot average percent improvement
    # # set up plots
    # fig, ax1 = plt.subplots()
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Mean Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    # print(max_aepi[2])
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    #
    # # plot median percent improvement
    #
    # # plot std percent improvement
    # fig, ax1 = plt.subplots()
    #
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Std. of Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0, 1], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    # ax2.plot([0, 1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot ranges?

    return

def plot_wec_nstep_results(filename, save_figs, show_figs, nturbs=38):

    if nturbs == 38:

        # set max wec values for each method
        wavals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])
        wdvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])
        whvals = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10])

        # 202003
        nwa = np.size(wavals)
        nwd = np.size(wdvals)
        nwh = np.size(whvals)

        nwaarray = np.zeros(nwa)
        nwdarray = np.zeros(nwd)
        nwharray = np.zeros(nwh)

        # prepare to store max aep percent improvement values
        max_aepi = np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()])

        # prepare to store min aep percent improvement values
        min_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        med_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        mean_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store standard deviation of aep percent improvement values
        std_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # set results directory
        # rdir = "./image_data/opt_results/202003261328-wec-nsteps/"
        rdir = "./image_data/opt_results/20200512-38-turbs-12-dir-nsteps-maxwec3/"

        # set wec method directory perfixes
        wadirp = "snopt_wec_angle_max_wec_10_nsteps_"
        wddirp = "snopt_wec_diam_max_wec_4_nsteps_"
        whdirp = "snopt_wec_hybrid_max_wec_3_nsteps_"

        approaches = np.array([wadirp,wddirp,whdirp])

        # set base file name
        bfilename = "snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt"

        wec_step_ranges = np.array([wavals,wdvals,whvals])

    else:
        ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)

    # load baseline data
    base_data = np.loadtxt(rdir + wadirp + "10.000" + "/" + bfilename)

    # store baseline aep value
    orig_aep = base_data[0, 5]

    # loop through each wec approach
    for i in np.arange(0,np.size(approaches)):
        approach = approaches[i]
        max_wec_range = wec_step_ranges[i]
        # print(approach)
        print(max_wec_range)
        print('size of wec range', np.size(max_wec_range))
        # loop through each max wec value for current approach
        for j in np.arange(0, np.size(max_wec_range)):
            # print(max_wec_range[j])
            wec_val = max_wec_range[j]

            # load data set
            data_file = rdir + approach + "%.3f" %(wec_val) + "/" + bfilename
            try:
                data_set = np.loadtxt(data_file)
            except:
                print("Failed to find data for ", data_file)
                print("Setting values to None")
                max_aepi[i][j] = None
                min_aepi[i][j] = None
                med_aepi[i][j] = None
                std_aepi[i][j] = None
                continue
            print("loaded data for %i, %i" %(i,j))
            # compile data from all intermediate wec values
            id = data_set[:, 0]
            ef = data_set[:, 1]
            ti_opt = data_set[:, 3]
            run_end_aep = data_set[ti_opt == 5, 7]
            run_time = data_set[:, 8]
            fcalls = data_set[:, 9]
            scalls = data_set[:, 10]

            tfcalls = fcalls[ti_opt == 5]
            tscalls = fcalls[ti_opt == 5]

            # compute percent improvement from base for current set
            run_improvement = 100*(run_end_aep / orig_aep - 1.)

            # store max percent improvement from base for current set
            max_run_improvement = np.max(run_improvement)
            max_aepi[i][j] = max_run_improvement
            # if i==2:
            #     print(max_aepi[i][j])

            # store min percent improvement from base for current set
            min_run_improvement = np.min(run_improvement)
            min_aepi[i][j] = min_run_improvement

            # store average percent improvement from base for current set
            mean_run_improvement = np.average(run_improvement)
            mean_aepi[i][j] = mean_run_improvement

            # store median percent improvement from base for current set
            median_run_improvement = np.median(run_improvement)
            med_aepi[i][j] = median_run_improvement

            # store std percent improvement from base for current set
            std_improvement = np.std(run_improvement)
            std_aepi[i][j] = std_improvement
            # if i==2:
            #     print(std_aepi[i][j])

        # end loop through wec values

    # end loop through methods

    # load SNOPT data
    data_snopt_no_wec = np.loadtxt(
        rdir+"snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    snw_id = data_snopt_no_wec[:, 0]
    snw_ef = np.ones_like(snw_id)
    snw_orig_aep = data_snopt_no_wec[0, 4]
    # swa_run_start_aep = data_snopt_relax[0, 7]
    snw_run_end_aep = data_snopt_no_wec[:, 6]
    snw_run_time = data_snopt_no_wec[:, 7]
    snw_fcalls = data_snopt_no_wec[:, 8]
    snw_scalls = data_snopt_no_wec[:, 9]

    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_improvement = 100*(snw_run_end_aep / orig_aep - 1.)
    snw_mean_run_improvement = np.average(snw_run_improvement)
    snw_std_improvement = np.std(snw_run_improvement)
    snw_max_improvement = np.max(snw_run_improvement)
    snw_min_improvement = np.min(snw_run_improvement)

    # load ALPSO data
    data_ps = np.loadtxt(rdir+"ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    ps_id = data_ps[:, 0]
    ps_ef = np.ones_like(ps_id)
    ps_orig_aep = data_ps[0, 4]
    # swa_run_start_aep = data_ps[0, 7]
    ps_run_end_aep = data_ps[:, 6]
    ps_run_time = data_ps[:, 7]
    ps_fcalls = data_ps[:, 8]
    ps_scalls = data_ps[:, 9]

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_improvement = 100*(ps_run_end_aep / orig_aep - 1.)
    ps_mean_run_improvement = np.average(ps_run_improvement)
    ps_median_run_improvement = np.median(ps_run_improvement)
    ps_std_improvement = np.std(ps_run_improvement)
    ps_max_improvement = np.max(ps_run_improvement)
    ps_min_improvement = np.min(ps_run_improvement)

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()

    colors = ['tab:red', 'tab:blue']
    ax1.set_xlabel('Number of WEC Steps', color='k')
    ax1.set_ylabel("Maximum Improvement (%)")

    labels = ["angle", "diam", "hybrid", 'ALPSO', 'SNOPT']

    ax1.plot(wec_step_ranges[0], max_aepi[0], '^', label=labels[0], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[1], max_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[2], max_aepi[2], 's', label=labels[2], color=colors[1], markerfacecolor="none")
    ax1.plot([2,10], [ps_max_improvement, ps_max_improvement], '--k', label=labels[3])
    ax1.plot([2,10], [snw_max_improvement, snw_max_improvement], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_max.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()

    colors = ['tab:red', 'tab:blue']
    ax1.set_xlabel('Number of WEC Steps', color='k')
    ax1.set_ylabel("Mean Improvement (%)")

    labels = ["angle", "diam", "hybrid", 'ALPSO', 'SNOPT']

    ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1], markerfacecolor="none")
    ax1.plot([2,10], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    ax1.plot([2,10], [snw_mean_run_improvement, snw_mean_run_improvement], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_mean.pdf', transparent=True)

    if show_figs:
        plt.show()

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()

    colors = ['tab:red', 'tab:blue']
    ax1.set_xlabel('Number of WEC Steps', color='k')
    ax1.set_ylabel("Standard Deviation of Improvement (%)")

    labels = ["angle", "diam", "hybrid", 'ALPSO', 'SNOPT']

    ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1], markerfacecolor="none")
    ax1.plot(wec_step_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1], markerfacecolor="none")
    ax1.plot([2,10], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    ax1.plot([2,10], [snw_std_improvement, snw_std_improvement], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), handles=handles1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_std.pdf', transparent=True)

    if show_figs:
        plt.show()
    #
    # # plot min percent improvement
    #
    # # set up plots
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Minimum Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], min_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_min_improvement, ps_min_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot average percent improvement
    # # set up plots
    # fig, ax1 = plt.subplots()
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Mean Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    # print(max_aepi[2])
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    #
    # # plot median percent improvement
    #
    # # plot std percent improvement
    # fig, ax1 = plt.subplots()
    #
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Std. of Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0, 1], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    # ax2.plot([0, 1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot ranges?

    return

def plot_wec_step_results(filename, save_figs, show_figs, nturbs=38):

    if nturbs == 38:

        # set max wec values for each method
        wavals = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        wdvals = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0])
        whvals = np.array([0.8, 0.9, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0])

        # 202003
        nwa = np.size(wavals)
        nwd = np.size(wdvals)
        nwh = np.size(whvals)

        nwaarray = np.zeros(nwa)
        nwdarray = np.zeros(nwd)
        nwharray = np.zeros(nwh)

        # prepare to store max aep percent improvement values
        max_aepi = np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()])

        # prepare to store min aep percent improvement values
        min_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        med_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        mean_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store standard deviation of aep percent improvement values
        std_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # set results directory
        rdir = "./image_data/opt_results/202003120725-wec-step-val/"

        # set wec method directory perfixes
        wadirp = "snopt_wec_angle_max_wec_10_wec_step_"
        wddirp = "snopt_wec_diam_max_wec_4_wec_step_"
        whdirp = "snopt_wec_hybrid_max_wec_3_wec_step_"

        approaches = np.array([wadirp,wddirp,whdirp])

        # set base file name
        bfilename = "snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt"

        wec_step_ranges = np.array([wavals,wdvals,whvals])

    else:
        ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)

    # load baseline data
    base_data = np.loadtxt(rdir + wadirp + "10.000" + "/" + bfilename)

    # store baseline aep value
    orig_aep = base_data[0, 5]

    # loop through each wec approach
    for i in np.arange(0,np.size(approaches)):
        approach = approaches[i]
        max_wec_range = wec_step_ranges[i]
        # print(approach)
        print(max_wec_range)
        print('size of wec range', np.size(max_wec_range))
        # loop through each max wec value for current approach
        for j in np.arange(0, np.size(max_wec_range)):
            # print(max_wec_range[j])
            wec_val = max_wec_range[j]

            # load data set
            data_file = rdir + approach + "%.3f" %(wec_val) + "/" + bfilename
            try:
                data_set = np.loadtxt(data_file)
            except:
                print("Failed to find data for ", data_file)
                print("Setting values to None")
                max_aepi[i][j] = None
                min_aepi[i][j] = None
                med_aepi[i][j] = None
                std_aepi[i][j] = None
                continue
            print("loaded data for %i, %i" %(i,j))
            # compile data from all intermediate wec values
            id = data_set[:, 0]
            ef = data_set[:, 1]
            ti_opt = data_set[:, 3]
            run_end_aep = data_set[ti_opt == 5, 7]
            run_time = data_set[:, 8]
            fcalls = data_set[:, 9]
            scalls = data_set[:, 10]

            tfcalls = fcalls[ti_opt == 5]
            tscalls = fcalls[ti_opt == 5]

            # compute percent improvement from base for current set
            run_improvement = 100*(run_end_aep / orig_aep - 1.)

            # store max percent improvement from base for current set
            max_run_improvement = np.max(run_improvement)
            max_aepi[i][j] = max_run_improvement
            # if i==2:
            #     print(max_aepi[i][j])

            # store min percent improvement from base for current set
            min_run_improvement = np.min(run_improvement)
            min_aepi[i][j] = min_run_improvement

            # store average percent improvement from base for current set
            mean_run_improvement = np.average(run_improvement)
            mean_aepi[i][j] = mean_run_improvement

            # store median percent improvement from base for current set
            median_run_improvement = np.median(run_improvement)
            med_aepi[i][j] = median_run_improvement

            # store std percent improvement from base for current set
            std_improvement = np.std(run_improvement)
            std_aepi[i][j] = std_improvement
            # if i==2:
            #     print(std_aepi[i][j])

        # end loop through wec values

    # end loop through methods

    # load SNOPT data
    data_snopt_no_wec = np.loadtxt(
        rdir+"snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    snw_id = data_snopt_no_wec[:, 0]
    snw_ef = np.ones_like(snw_id)
    snw_orig_aep = data_snopt_no_wec[0, 4]
    # swa_run_start_aep = data_snopt_relax[0, 7]
    snw_run_end_aep = data_snopt_no_wec[:, 6]
    snw_run_time = data_snopt_no_wec[:, 7]
    snw_fcalls = data_snopt_no_wec[:, 8]
    snw_scalls = data_snopt_no_wec[:, 9]

    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_improvement = 100*(snw_run_end_aep / orig_aep - 1.)
    snw_mean_run_improvement = np.average(snw_run_improvement)
    snw_std_improvement = np.std(snw_run_improvement)
    snw_max_improvement = np.max(snw_run_improvement)
    snw_min_improvement = np.min(snw_run_improvement)

    # load ALPSO data
    data_ps = np.loadtxt(rdir+"ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    ps_id = data_ps[:, 0]
    ps_ef = np.ones_like(ps_id)
    ps_orig_aep = data_ps[0, 4]
    # swa_run_start_aep = data_ps[0, 7]
    ps_run_end_aep = data_ps[:, 6]
    ps_run_time = data_ps[:, 7]
    ps_fcalls = data_ps[:, 8]
    ps_scalls = data_ps[:, 9]

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_improvement = 100*(ps_run_end_aep / orig_aep - 1.)
    ps_mean_run_improvement = np.average(ps_run_improvement)
    ps_median_run_improvement = np.median(ps_run_improvement)
    ps_std_improvement = np.std(ps_run_improvement)
    ps_max_improvement = np.max(ps_run_improvement)
    ps_min_improvement = np.min(ps_run_improvement)

    # set up plots
    plt.gcf().clear()
    fig, ax1 = plt.subplots()

    colors = ['tab:red', 'tab:blue']
    ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    ax1.set_ylabel("Maximum Improvement (%)")
    ax1.tick_params(axis='x', labelcolor=colors[0])

    ax2 = ax1.twiny()
    # ax2.set_ylim([0, 10])
    # plot max percent improvement
    labels = ["angle", "diam", "hybrid", 'ALPSO', 'SNOPT']


    ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    ax2.tick_params(axis='x', labelcolor=colors[1])



    ax1.plot(wec_step_ranges[0], max_aepi[0], 'o', label=labels[0], color=colors[0], markerfacecolor="none")
    ax2.plot(wec_step_ranges[1], max_aepi[1], '^', label=labels[1], color=colors[1], markerfacecolor="none")
    ax2.plot(wec_step_ranges[2], max_aepi[2], 's', label=labels[2], color=colors[1], markerfacecolor="none")
    ax2.plot([0,4], [ps_max_improvement, ps_max_improvement], '--k', label=labels[3])
    ax2.plot([0,4], [snw_max_improvement, snw_max_improvement], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    print(handles2)
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # lgd = ax2.legend([handles1,handles2], labels, loc='upper center', bbox_to_anchor=(0.5, -0.1))
    fig.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=False, ncol=1)
    fig.tight_layout()






    if save_figs:
        plt.savefig(filename+'_time.pdf', transparent=True)

    if show_figs:
        plt.show()
    #
    # # plot min percent improvement
    #
    # # set up plots
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Minimum Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], min_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_min_improvement, ps_min_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot average percent improvement
    # # set up plots
    # fig, ax1 = plt.subplots()
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Mean Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0,1], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    # ax2.plot([0,1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    # print(max_aepi[2])
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    #
    # # plot median percent improvement
    #
    # # plot std percent improvement
    # fig, ax1 = plt.subplots()
    #
    #
    # ax1.set_xlabel('Wake Spreading Angle Step (deg.)', color=colors[0])
    # ax1.set_ylabel("Std. of Improvement (%)")
    # ax1.tick_params(axis='x', labelcolor=colors[0])
    #
    # ax2 = ax1.twiny()
    # # ax2.set_ylim([0, 10])
    # # plot max percent improvement
    #
    # ax2.set_xlabel('Diameter Multiplier Step', color=colors[1])
    # ax2.tick_params(axis='x', labelcolor=colors[1])
    #
    # ax1.plot(wec_step_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0])
    # ax2.plot(wec_step_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1])
    # ax2.plot(wec_step_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1])
    # ax2.plot([0, 1], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    # ax2.plot([0, 1], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    #
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # print(handles2)
    # fig.legend()
    # fig.tight_layout()
    #
    # if save_figs:
    #     plt.savefig(filename + '_time.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # # plot ranges?

    return

def plot_max_wec_results(filename, save_figs, show_figs, nturbs=38):

    if nturbs == 38:

        # 202003
        nwa = 8
        nwd = 9
        nwh = 9

        nwaarray = np.zeros(nwa)
        nwdarray = np.zeros(nwd)
        nwharray = np.zeros(nwh)

        # prepare to store max aep percent improvement values
        max_aepi = np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()])

        # prepare to store min aep percent improvement values
        min_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        med_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store median aep percent improvement values
        mean_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # prepare to store standard deviation of aep percent improvement values
        std_aepi = np.copy(np.array([nwaarray.copy(),nwdarray.copy(),nwharray.copy()]))

        # set results directory
        rdir = "./image_data/opt_results/202003061434-max-wec-val/"

        # set wec method directory perfixes
        wadirp = "snopt_wec_angle_max_wec_"
        wddirp = "snopt_wec_diam_max_wec_"
        whdirp = "snopt_wec_hybrid_max_wec_"

        approaches = np.array([wadirp,wddirp,whdirp])

        # set base file name
        bfilename = "_snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt"

        # set max wec values for each method
        wavals = np.array([10,20,30,40,50,60,70,80])
        wdvals = np.array([2,3,4,5,6,7,8,9,10])
        whvals = np.array([2,3,4,5,6,7,8,9,10])

        max_wec_ranges = np.array([wavals,wdvals,whvals])

    else:
        ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)

    # load baseline data
    base_data = np.loadtxt(rdir + wadirp + "10" + "/" + wadirp + "10" + bfilename)

    # store baseline aep value
    orig_aep = base_data[0, 5]

    # loop through each wec approach
    for i in np.arange(0,np.size(approaches)):
        approach = approaches[i]
        max_wec_range = max_wec_ranges[i]
        # print(approach)
        print(max_wec_range)
        print(np.size(max_wec_range))
        # loop through each max wec value for current approach
        for j in np.arange(0, np.size(max_wec_range)):
            # print(max_wec_range[j])
            print(j)
            wec_val = max_wec_range[j]

            # load data set
            data_file = rdir + approach + str(wec_val) + "/" + approach + str(wec_val) + bfilename
            try:
                data_set = np.loadtxt(data_file)
            except:
                print("Failed to find data for ", data_file)
                print("Setting values to None")
                max_aepi[i][j] = None
                min_aepi[i][j] = None
                med_aepi[i][j] = None
                std_aepi[i][j] = None
                continue

            # compile data from all intermediate wec values
            id = data_set[:, 0]
            ef = data_set[:, 1]
            ti_opt = data_set[:, 3]
            run_end_aep = data_set[ti_opt == 5, 7]
            run_time = data_set[:, 8]
            fcalls = data_set[:, 9]
            scalls = data_set[:, 10]

            tfcalls = fcalls[ti_opt == 5]
            tscalls = fcalls[ti_opt == 5]

            # compute percent improvement from base for current set
            run_improvement = 100*(run_end_aep / orig_aep - 1.)

            # store max percent improvement from base for current set
            max_run_improvement = np.max(run_improvement)
            max_aepi[i][j] = max_run_improvement
            # if i==2:
            #     print(max_aepi[i][j])

            # store min percent improvement from base for current set
            min_run_improvement = np.min(run_improvement)
            min_aepi[i][j] = min_run_improvement

            # store average percent improvement from base for current set
            mean_run_improvement = np.average(run_improvement)
            mean_aepi[i][j] = mean_run_improvement

            # store median percent improvement from base for current set
            median_run_improvement = np.median(run_improvement)
            med_aepi[i][j] = median_run_improvement

            # store std percent improvement from base for current set
            std_improvement = np.std(run_improvement)
            std_aepi[i][j] = std_improvement
            # if i==2:
            #     print(std_aepi[i][j])

        # end loop through wec values

    # end loop through methods

    # load SNOPT data
    data_snopt_no_wec = np.loadtxt(
        rdir+"snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    snw_id = data_snopt_no_wec[:, 0]
    snw_ef = np.ones_like(snw_id)
    snw_orig_aep = data_snopt_no_wec[0, 4]
    # swa_run_start_aep = data_snopt_relax[0, 7]
    snw_run_end_aep = data_snopt_no_wec[:, 6]
    snw_run_time = data_snopt_no_wec[:, 7]
    snw_fcalls = data_snopt_no_wec[:, 8]
    snw_scalls = data_snopt_no_wec[:, 9]

    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_improvement = 100*(snw_run_end_aep / orig_aep - 1.)
    snw_mean_run_improvement = np.average(snw_run_improvement)
    snw_std_improvement = np.std(snw_run_improvement)
    snw_max_improvement = np.max(snw_run_improvement)
    snw_min_improvement = np.min(snw_run_improvement)

    # load ALPSO data
    data_ps = np.loadtxt(rdir+"ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    ps_id = data_ps[:, 0]
    ps_ef = np.ones_like(ps_id)
    ps_orig_aep = data_ps[0, 4]
    # swa_run_start_aep = data_ps[0, 7]
    ps_run_end_aep = data_ps[:, 6]
    ps_run_time = data_ps[:, 7]
    ps_fcalls = data_ps[:, 8]
    ps_scalls = data_ps[:, 9]

    # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
    ps_run_improvement = 100*(ps_run_end_aep / orig_aep - 1.)
    ps_mean_run_improvement = np.average(ps_run_improvement)
    ps_median_run_improvement = np.median(ps_run_improvement)
    ps_std_improvement = np.std(ps_run_improvement)
    ps_max_improvement = np.max(ps_run_improvement)
    ps_min_improvement = np.min(ps_run_improvement)

    # set up plots
    fig, ax1 = plt.subplots()

    colors = ['tab:red', 'tab:blue']
    ax1.set_xlabel('Wake Spreading Angle (deg.)', color=colors[0])
    ax1.set_ylabel("Maximum Improvement (%)")
    ax1.tick_params(axis='x', labelcolor=colors[0])

    ax2 = ax1.twiny()
    # ax2.set_ylim([0, 10])
    # plot max percent improvement
    labels = ["angle", "diam", "hybrid", 'ALPSO', 'SNOPT']


    ax2.set_xlabel('Diameter Multiplier', color=colors[1])
    ax2.tick_params(axis='x', labelcolor=colors[1])



    ax1.plot(max_wec_ranges[0], max_aepi[0], '^', label=labels[0], color=colors[0])
    ax2.plot(max_wec_ranges[1], max_aepi[1], 'o', label=labels[1], color=colors[1])
    ax2.plot(max_wec_ranges[2], max_aepi[2], 's', label=labels[2], color=colors[1])
    ax2.plot([2, 10], [ps_max_improvement, ps_max_improvement], '--k', label=labels[3])
    ax2.plot([2, 10], [snw_max_improvement, snw_max_improvement], ':k', label=labels[4])
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    print(handles2)
    # box = ax2.get_position()
    # ax2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # fig.legend()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_time.pdf', transparent=True)

    if show_figs:
        plt.show()

    # plot min percent improvement

    # set up plots
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Wake Spreading Angle (deg.)', color=colors[0])
    ax1.set_ylabel("Minimum Improvement (%)")
    ax1.tick_params(axis='x', labelcolor=colors[0])

    ax2 = ax1.twiny()
    # ax2.set_ylim([0, 10])
    # plot max percent improvement

    ax2.set_xlabel('Diameter Multiplier', color=colors[1])
    ax2.tick_params(axis='x', labelcolor=colors[1])

    ax1.plot(max_wec_ranges[0], min_aepi[0], '^', label=labels[0], color=colors[0])
    ax2.plot(max_wec_ranges[1], min_aepi[1], 'o', label=labels[1], color=colors[1])
    ax2.plot(max_wec_ranges[2], min_aepi[2], 's', label=labels[2], color=colors[1])
    ax2.plot([2, 10], [ps_min_improvement, ps_min_improvement], '--k', label=labels[3])
    ax2.plot([2, 10], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    print(handles2)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename + '_time.pdf', transparent=True)

    if show_figs:
        plt.show()

    # plot average percent improvement
    # set up plots
    fig, ax1 = plt.subplots()

    ax1.set_xlabel('Wake Spreading Angle (deg.)', color=colors[0])
    ax1.set_ylabel("Mean Improvement (%)")
    ax1.tick_params(axis='x', labelcolor=colors[0])

    ax2 = ax1.twiny()
    # ax2.set_ylim([0, 10])
    # plot max percent improvement

    ax2.set_xlabel('Diameter Multiplier', color=colors[1])
    ax2.tick_params(axis='x', labelcolor=colors[1])

    ax1.plot(max_wec_ranges[0], mean_aepi[0], '^', label=labels[0], color=colors[0])
    ax2.plot(max_wec_ranges[1], mean_aepi[1], 'o', label=labels[1], color=colors[1])
    ax2.plot(max_wec_ranges[2], mean_aepi[2], 's', label=labels[2], color=colors[1])
    ax2.plot([2, 10], [ps_mean_run_improvement, ps_mean_run_improvement], '--k', label=labels[3])
    ax2.plot([2, 10], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])
    print(max_aepi[2])
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename + '_time.pdf', transparent=True)

    if show_figs:
        plt.show()


    # plot median percent improvement

    # plot std percent improvement
    fig, ax1 = plt.subplots()


    ax1.set_xlabel('Wake Spreading Angle (deg.)', color=colors[0])
    ax1.set_ylabel("Std. of Improvement (%)")
    ax1.tick_params(axis='x', labelcolor=colors[0])

    ax2 = ax1.twiny()
    # ax2.set_ylim([0, 10])
    # plot max percent improvement

    ax2.set_xlabel('Diameter Multiplier', color=colors[1])
    ax2.tick_params(axis='x', labelcolor=colors[1])

    ax1.plot(max_wec_ranges[0], std_aepi[0], '^', label=labels[0], color=colors[0])
    ax2.plot(max_wec_ranges[1], std_aepi[1], 'o', label=labels[1], color=colors[1])
    ax2.plot(max_wec_ranges[2], std_aepi[2], 's', label=labels[2], color=colors[1])
    ax2.plot([2, 10], [ps_std_improvement, ps_std_improvement], '--k', label=labels[3])
    ax2.plot([2, 10], [snw_min_improvement, snw_min_improvement], ':k', label=labels[4])

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    print(handles2)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename + '_time.pdf', transparent=True)

    if show_figs:
        plt.show()

    # plot ranges?

    return

def plot_optimization_results(filename, save_figs, show_figs, nturbs=16, model="BPA", ps=True, ps_wec=False):

    if model == "BPA":
        if nturbs == 9:
            # 202002
            data_snopt_no_wec = np.loadtxt(
                "./image_data/opt_results/202002240836/no_wec_snopt_multistart_rundata_9turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_snopt_weca = np.loadtxt(
                "./image_data/opt_results/202002240836/angle_wec_snopt_multistart_rundata_9turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                "./image_data/opt_results/202002240836/diam_wec_snopt_multistart_rundata_9turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_snopt_wech = np.loadtxt(
                "./image_data/opt_results/202002240836/hybrid_wec_snopt_multistart_rundata_9turbs_directionalWindRose_20dirs_BPA_all.txt")
            # data_ps = np.loadtxt(
            #     "./image_data/opt_results/202002240836/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            data_ps = np.loadtxt(
                "./image_data/opt_results/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")

        if nturbs == 16:
            data_snopt_no_wec = np.loadtxt(
                # "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                # "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_ps = np.loadtxt(
                # "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                # "./image_data/opt_results/20200804-16-turbs-20-dir-ALPSO/ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
            if ps_wec:
                data_ps_wec = np.loadtxt(
                    # "./image_data/opt_results/20200804-16-turbs-20-dir-ALPSO/ps_wec_diam_max_wec_3_nsteps_6.000/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                    "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/ps_wec_diam_max_wec_3_nsteps_6.000/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")

            tmax_aep = 5191363.5933961 * nturbs # kWh

        elif nturbs == 38:
                    # load data
            # data_snopt_no_wec = np.loadtxt(
            #     "./image_data/opt_results/snopt_no_wec_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            # data_snopt_weca = np.loadtxt(
            #     "./image_data/opt_results/snopt_weca_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            # data_snopt_wecd = np.loadtxt(
            #     "./image_data/opt_results/snopt_wecd_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            # data_ps = np.loadtxt(
            #     "./image_data/opt_results/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

            # 202005
            data_snopt_no_wec = np.loadtxt(
                # "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-38-turbs-36-dir-fcall-and-conv-history/snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                # "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-38-turbs-36-dir-fcall-and-conv-history/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
            data_ps = np.loadtxt(
                # "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/ps/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                "./image_data/opt_results/20200821-38-turbs-36-dir-fcall-and-conv-history/ps/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
            tmax_aep = 1630166.61601323 * nturbs # kWh
            ps_wec = False
        elif nturbs == 60:
                    # load data
            data_snopt_no_wec = np.loadtxt(
                # "./image_data/opt_results/20200527-60-turbs-72-dir-amalia-maxwecd3-nsteps6/snopt/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                "./image_data/opt_results/20200824-60-turbs-72-dir-fcall-and-conv-history/snopt/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
            # data_snopt_weca = np.loadtxt(
            #     "./image_data/opt_results/snopt_wec_angle_rundata_60turbs_amaliaWindRose_36dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                # "./image_data/opt_results/20200527-60-turbs-72-dir-amalia-maxwecd3-nsteps6/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                "./image_data/opt_results/20200824-60-turbs-72-dir-fcall-and-conv-history/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
            data_ps = np.loadtxt(
                # "./image_data/opt_results/20200527-60-turbs-72-dir-amalia-maxwecd3-nsteps6/ps/ps_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                "./image_data/opt_results/20200824-60-turbs-72-dir-fcall-and-conv-history/ps/ps_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
            tmax_aep = 6653047.52233728  * nturbs # kWh
            ps_wec = False
        else:
            ValueError("please include results for %i turbines before rerunning the plotting script" % nturbs)
    elif model == "JENSEN":
        if nturbs == 16:
            data_snopt_no_wec = np.loadtxt(
                "./image_data/opt_results/20200805-jensen-16-turbs-20-dir-maxwecd3-nsteps6/snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                "./image_data/opt_results/20200805-jensen-16-turbs-20-dir-maxwecd3-nsteps6/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
            # data_ps = np.loadtxt(
            #     "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")

            tmax_aep = 5904352.21200323 * nturbs  # kWh
            ps_wec = False
        elif nturbs == 38:
            # 202005
            data_snopt_no_wec = np.loadtxt(
                "./image_data/opt_results/20200805-jensen-38-turbs-12-dir-maxwecd3-nsteps6/snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            data_snopt_wecd = np.loadtxt(
                "./image_data/opt_results/20200805-jensen-38-turbs-12-dir-maxwecd3-nsteps6/snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
            # data_ps = np.loadtxt(
            #     "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/ps/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
            tmax_aep = 5679986.82794711 * nturbs  # kWh
            ps_wec = False
    # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # run time (s), obj func calls, sens func calls
    snw_id = data_snopt_no_wec[:, 0]
    snw_ef = np.ones_like(snw_id)
    snw_ti_opt = data_snopt_no_wec[:, 2]
    snw_orig_aep = data_snopt_no_wec[0, 4]
    # swa_run_start_aep = data_snopt_relax[0, 7]
    if model == "BPA":
        snw_run_end_aep = data_snopt_no_wec[snw_ti_opt == 5, 6]
    else:
        snw_run_end_aep = data_snopt_no_wec[:, 6]
    snw_run_time = data_snopt_no_wec[:, 7]
    snw_fcalls = data_snopt_no_wec[:, 8]
    snw_scalls = data_snopt_no_wec[:, 9]

    snw_tfcalls = np.zeros_like(snw_run_end_aep)
    snw_tscalls = np.zeros_like(snw_run_end_aep)
    for i in np.arange(0, snw_tfcalls.size):
        snw_tfcalls[i] = np.sum(snw_fcalls[snw_id == i])
        snw_tscalls[i] = np.sum(snw_scalls[snw_id == i])

    snw_ctfcalls = snw_tfcalls + snw_tscalls
    # snw_run_improvement = snw_run_end_aep / snw_orig_aep - 1.
    snw_run_wake_loss = 100.0 * (1.0 - (snw_run_end_aep[snw_ctfcalls>0] / tmax_aep))
    snw_mean_wake_loss = np.average(snw_run_wake_loss)
    snw_std_wake_loss = np.std(snw_run_wake_loss)
    snw_meadian_wake_loss = np.median(snw_run_wake_loss)
    snw_max_wake_loss = np.max(snw_run_wake_loss)
    snw_min_wake_loss = np.min(snw_run_wake_loss)

    snw_meadian_ctfcalls = np.median(snw_ctfcalls[snw_ctfcalls>0])
    snw_max_ctfcalls = np.max(snw_ctfcalls[snw_ctfcalls>0])
    snw_min_ctfcalls = np.min(snw_ctfcalls[snw_ctfcalls > 0])
    print("")
    print("SNOPT:")
    print("Max Wake Loss (\%): ", snw_max_wake_loss)
    print("Min Wake Loss (\%): ", snw_min_wake_loss)
    print("Ave. Wake Loss (\%): ", snw_mean_wake_loss)
    print("Med. Wake Loss (\%): ", snw_meadian_wake_loss)
    print("Std Wake Loss (\%): ", snw_std_wake_loss)
    print("Max fcalls (\%): ", snw_max_ctfcalls)
    print("Min fcalls (\%): ", snw_min_ctfcalls)
    print("Median fcalls (\%): ", snw_meadian_ctfcalls)

    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
    # aep run opt (kW), run time (s), obj func calls, sens func calls
    # swa_id = data_snopt_weca[:, 0]
    # swa_ef = data_snopt_weca[:, 1]
    # swa_ti_opt = data_snopt_weca[:, 3]
    # swa_orig_aep = data_snopt_weca[0, 5]
    # # swa_run_start_aep = data_snopt_weca[0, 7]
    # swa_run_end_aep = data_snopt_weca[swa_ti_opt==5, 7]
    # swa_run_time = data_snopt_weca[:, 8]
    # swa_fcalls = data_snopt_weca[:, 9]
    # swa_scalls = data_snopt_weca[:, 10]
    #
    # swa_tfcalls = swa_fcalls[swa_ti_opt == 5]
    # swa_tscalls = swa_fcalls[swa_ti_opt == 5]
    #
    # swa_run_improvement = swa_run_end_aep / swa_orig_aep - 1.
    # swa_mean_run_improvement = np.average(swa_run_improvement)
    # swa_std_improvement = np.std(swa_run_improvement)

    swd_id = data_snopt_wecd[:, 0]
    swd_ef = data_snopt_wecd[:, 1]
    swd_ti_opt = data_snopt_wecd[:, 3]
    swd_orig_aep = data_snopt_wecd[0, 5]
    # swd_run_start_aep = data_snopt_weca[0, 7]
    if model == "BPA":
        swd_run_end_aep = data_snopt_wecd[swd_ti_opt == 5, 7]
    else:
        swd_run_end_aep = data_snopt_wecd[swd_ef == 1, 7]
    swd_run_time = data_snopt_wecd[:, 8]

    swd_fcalls = data_snopt_wecd[:, 9]
    swd_scalls = data_snopt_wecd[:, 10]

    swd_tfcalls = np.zeros_like(swd_run_end_aep)
    swd_tscalls = np.zeros_like(swd_run_end_aep)
    for i in np.arange(0, swd_tfcalls.size):
        swd_tfcalls[i] = np.sum(swd_fcalls[swd_id == i])
        swd_tscalls[i] = np.sum(swd_scalls[swd_id == i])

    swd_ctfcalls = swd_tfcalls + swd_tscalls
    swd_run_wake_loss = 100.0*(1.0 - (swd_run_end_aep[snw_ctfcalls > 0] / tmax_aep))
    swd_mean_run_wake_loss = np.average(swd_run_wake_loss)
    swd_std_wake_loss = np.std(swd_run_wake_loss)
    swd_meadian_wake_loss = np.median(swd_run_wake_loss)
    swd_max_wake_loss = np.max(swd_run_wake_loss)
    swd_min_wake_loss = np.min(swd_run_wake_loss)
    swd_t, swd_p = ttest_ind(snw_run_wake_loss, swd_run_wake_loss, equal_var=False)


    swd_meadian_ctfcalls = np.median(swd_ctfcalls[snw_ctfcalls>0])
    swd_max_ctfcalls = np.max(swd_ctfcalls[snw_ctfcalls>0])
    swd_min_ctfcalls = np.min(swd_ctfcalls[snw_ctfcalls>0])
    print("")
    print("SNOPT+WEC-D:")
    print("Max Wake Loss (\%): ", swd_max_wake_loss)
    print("Min Wake Loss (\%): ", swd_min_wake_loss)
    print("Ave. Wake Loss (\%): ", swd_mean_run_wake_loss)
    print("Med. Wake Loss (\%): ", swd_meadian_wake_loss)
    print("Std Wake Loss (\%): ", swd_std_wake_loss)
    print("Welch's t-test t: ", swd_t)
    print("Welch's t-test p: ", swd_p)
    print("Max fcalls (\%): ", swd_max_ctfcalls)
    print("Min fcalls (\%): ", swd_min_ctfcalls)
    print("Median fcalls (\%): ", swd_meadian_ctfcalls)

    # swh_id = data_snopt_wech[:, 0]
    # swh_ef = data_snopt_wech[:, 1]
    # swh_ti_opt = data_snopt_wech[:, 3]
    # swh_orig_aep = data_snopt_wech[0, 5]
    # # swh_run_start_aep = data_snopt_wech[0, 7]
    # swh_run_end_aep = data_snopt_wech[swh_ti_opt == 5, 7]
    # swh_run_time = data_snopt_wech[:, 8]
    # swh_fcalls = data_snopt_wech[:, 9]
    # swh_scalls = data_snopt_wech[:, 10]
    #
    # swh_tfcalls = swh_fcalls[swh_ti_opt == 5]
    # swh_tscalls = swh_fcalls[swh_ti_opt == 5]
    #
    # swh_run_improvement = swh_run_end_aep / swa_orig_aep - 1.
    # swh_mean_run_improvement = np.average(swh_run_improvement)
    # swh_std_improvement = np.std(swh_run_improvement)

    if ps:
        ps_id = data_ps[:, 0]
        ps_ef = np.ones_like(ps_id)
        ps_orig_aep = data_ps[0, 4]
        # swa_run_start_aep = data_ps[0, 7]
        ps_run_end_aep = data_ps[:, 6]
        ps_run_time = data_ps[:, 7]
        ps_fcalls = data_ps[:, 8]
        ps_scalls = data_ps[:, 9]


        ps_ctfcalls = ps_fcalls + ps_scalls
        # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
        ps_run_wake_loss = 100.0 * (1.0 - (ps_run_end_aep[ps_ctfcalls>0] / tmax_aep))
        ps_mean_wake_loss = np.average(ps_run_wake_loss)
        ps_std_wake_loss = np.std(ps_run_wake_loss)

        ps_meadian_wake_loss = np.median(ps_run_wake_loss)
        ps_max_wake_loss = np.max(ps_run_wake_loss)
        ps_min_wake_loss = np.min(ps_run_wake_loss)

        ps_meadian_ctfcalls = np.median(ps_ctfcalls[ps_ctfcalls>0])
        ps_max_ctfcalls = np.max(ps_ctfcalls[ps_ctfcalls>0])
        ps_min_ctfcalls = np.min(ps_ctfcalls[ps_ctfcalls>0])
        print("")
        print("ALPSO:")
        print("Max Wake Loss (\%): ", ps_max_wake_loss)
        print("Min Wake Loss (\%): ", ps_min_wake_loss)
        print("Ave. Wake Loss (\%): ", ps_mean_wake_loss)
        print("Med. Wake Loss (\%): ", ps_meadian_wake_loss)
        print("Std Wake Loss (\%): ", ps_std_wake_loss)
        print("Max fcalls (\%): ", ps_max_ctfcalls)
        print("Min fcalls (\%): ", ps_min_ctfcalls)
        print("Median fcalls (\%): ", ps_meadian_ctfcalls)

        if ps_wec:
            ps_wec_id = data_ps_wec[:, 0]
            ps_wec_ef = data_ps_wec[:, 1]
            ps_wec_ti_opt = data_ps_wec[:, 3]
            ps_wec_orig_aep = data_ps_wec[0, 5]
            # ps_wec_run_start_aep = data_ps_wec[0, 7
            ps_wec_run_end_aep = data_ps_wec[ps_wec_ti_opt == 4, 7]
            ps_wec_run_time = data_ps_wec[:, 8]

            ps_wec_fcalls = data_ps_wec[:, 9]
            ps_wec_scalls = data_ps_wec[:, 10]

            ps_wec_tfcalls = np.zeros_like(ps_wec_run_end_aep)
            ps_wec_tscalls = np.zeros_like(ps_wec_run_end_aep)
            for i in np.arange(0, ps_wec_tfcalls.size):
                ps_wec_tfcalls[i] = np.sum(ps_wec_fcalls[ps_wec_id == i])
                ps_wec_tscalls[i] = np.sum(ps_wec_scalls[ps_wec_id == i])

            ps_wec_ctfcalls = ps_wec_tfcalls + ps_wec_tscalls

            ps_wec_run_wake_loss = 100.0 * (1.0 - (ps_wec_run_end_aep[ps_wec_ctfcalls>0] / tmax_aep))
            ps_wec_mean_wake_loss = np.average(ps_wec_run_wake_loss)
            ps_wec_std_wake_loss = np.std(ps_wec_run_wake_loss)

            ps_wec_meadian_wake_loss = np.median(ps_wec_run_wake_loss)
            ps_wec_max_wake_loss = np.max(ps_wec_run_wake_loss)
            ps_wec_min_wake_loss = np.min(ps_wec_run_wake_loss)

            ps_wec_t, ps_wec_p = ttest_ind(ps_run_wake_loss, ps_wec_run_wake_loss, equal_var=False)

            ps_wec_meadian_ctfcalls = np.median(ps_wec_ctfcalls[ps_wec_ctfcalls>0])
            ps_wec_max_ctfcalls = np.max(ps_wec_ctfcalls[ps_wec_ctfcalls>0])
            ps_wec_min_ctfcalls = np.min(ps_wec_ctfcalls[ps_wec_ctfcalls>0])
            print("")
            print("ALPSO+WEC-D:")
            print("Max Wake Loss (\%): ", ps_wec_max_wake_loss)
            print("Min Wake Loss (\%): ", ps_wec_min_wake_loss)
            print("Ave. Wake Loss (\%): ", ps_wec_mean_wake_loss)
            print("Med. Wake Loss (\%): ", ps_wec_meadian_wake_loss)
            print("Std Wake Loss (\%): ", ps_wec_std_wake_loss)
            print("Welch's t-test t: ", ps_wec_t)
            print("Welch's t-test p: ", ps_wec_p)
            print("Max fcalls (\%): ", ps_wec_max_ctfcalls)
            print("Min fcalls (\%): ", ps_wec_min_ctfcalls)
            print("Median fcalls (\%): ", ps_wec_meadian_ctfcalls)

    fig, ax = plt.subplots(1)

    # labels = list(['SNOPT', 'SNOPT Relax', 'ALPSO', 'NSGA II'])
    # labels = list(['SNOPT', 'WEC-A', 'WEC-D', 'WEC-H', 'ALPSO'])
    if ps:
        labels = list(['SNOPT', 'SNOPT+WEC-D', 'ALPSO'])
        if ps_wec:
            labels = list(['SNOPT', 'SNOPT+WEC-D', 'ALPSO', 'ALPSO+WEC-D'])
    else:
        labels = list(['SNOPT', 'SNOPT+WEC-D'])

    # labels = list('abcd')
    # data = list([snw_run_improvement, swa_run_improvement, ps_run_improvement, ga_run_improvement])
    aep_scale = 1E-6
    # data = list([snw_run_end_aep*aep_scale, swa_run_end_aep*aep_scale, swd_run_end_aep*aep_scale, swh_run_end_aep*aep_scale,  ps_run_end_aep*aep_scale])
    if ps:
        data = list([snw_run_end_aep*aep_scale, swd_run_end_aep*aep_scale, ps_run_end_aep*aep_scale])
        if ps_wec:
            data = list([snw_run_end_aep * aep_scale, swd_run_end_aep * aep_scale, ps_run_end_aep * aep_scale, ps_wec_run_end_aep * aep_scale])
    else:
        data = list([snw_run_end_aep * aep_scale, swd_run_end_aep * aep_scale])
    bp = ax.boxplot(data, meanline=True, labels=labels, patch_artist=True)

    plt.setp(bp['boxes'], edgecolor='k', facecolor='none')
    plt.setp(bp['whiskers'], color='k')
    plt.setp(bp['fliers'], markeredgecolor='k')
    plt.setp(bp['medians'], color='b')
    plt.setp(bp['caps'], color='k')

    ax.set_ylabel('AEP (GWh)')
    # ax.set_ylabel('Count')
    # ax.set_xlim([0, 0.1])
    # ax.set_ylim([300, 400])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')

    plt.tight_layout()
    if save_figs:
        plt.savefig(filename+'_aep.pdf', transparent=True)

    if show_figs:
        plt.show()

    fig, ax = plt.subplots(1)

    # data = list([snw_run_improvement*100, swa_run_improvement*100, swd_run_improvement*100, swh_run_improvement*100, ps_run_improvement*100])
    if ps:
        data = list([snw_run_wake_loss, swd_run_wake_loss, ps_run_wake_loss])
        if ps_wec:
            data = list([snw_run_wake_loss, swd_run_wake_loss, ps_run_wake_loss, ps_wec_run_wake_loss])
    else:
        data = list([snw_run_wake_loss, swd_run_wake_loss])
    bp = ax.boxplot(data, meanline=True, labels=labels, patch_artist=True)

    plt.setp(bp['boxes'], edgecolor='k', facecolor='none')
    plt.setp(bp['whiskers'], color='k')
    plt.setp(bp['fliers'], markeredgecolor='k')
    plt.setp(bp['medians'], color='b')
    plt.setp(bp['caps'], color='k')

    ax.set_ylabel('Optimized Wake Loss (%)')
    # ax.set_ylim([-15, 15.0])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')

    plt.tight_layout()
    if save_figs:
        plt.savefig(filename+'_percent_wake_loss.pdf', transparent=True)

    if show_figs:
        plt.show()
    #
    # if nturbs == 38:
    #     ymax = 30
    #     ymin = 22
    # elif nturbs == 60:
    #     ymax = 14
    #     ymin = 8
    fig, ax = plt.subplots(1)
    if ps:
        data = list([snw_run_wake_loss, swd_run_wake_loss, ps_run_wake_loss])
        if ps_wec:
            data = list([snw_run_wake_loss, swd_run_wake_loss, ps_run_wake_loss, ps_wec_run_wake_loss])
    else:
        data = list([snw_run_wake_loss, swd_run_wake_loss])
    bp = ax.boxplot(data, meanline=True, labels=labels, patch_artist=True, showfliers=False)

    plt.setp(bp['boxes'], edgecolor='k', facecolor='none')
    plt.setp(bp['whiskers'], color='k')
    plt.setp(bp['fliers'], markeredgecolor='k')
    plt.setp(bp['medians'], color='b')
    plt.setp(bp['caps'], color='k')

    ax.set_ylabel('Optimized Wake Loss (%)')
    # ax.set_ylim([-15, 15.0])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')
    # ax.set_ylim([0, 15])

    plt.tight_layout()
    if save_figs:
        plt.savefig(filename + '_percent_wake_loss_zoom.pdf', transparent=True)

    if show_figs:
        plt.show()

    fig, ax = plt.subplots(1)

    scale_by = 1E4
    # data = np.array([snw_fcalls+snw_scalls, swa_fcalls+swa_scalls, ps_fcalls, ga_fcalls])/scale_by
    # data = list([(snw_fcalls+snw_scalls)/scale_by, (swa_tfcalls+swa_tscalls)/scale_by, (swd_tfcalls+swd_tscalls)/scale_by, (swh_tfcalls+swh_tscalls)/scale_by, (ps_fcalls+ps_scalls)/scale_by])
    if ps:
        data = list([(snw_fcalls+snw_scalls)/scale_by, (swd_tfcalls+swd_tscalls)/scale_by, (ps_fcalls+ps_scalls)/scale_by])
        if ps_wec:
            data = list([(snw_fcalls + snw_scalls) / scale_by, (swd_tfcalls + swd_tscalls) / scale_by,
                         (ps_fcalls + ps_scalls) / scale_by, (ps_wec_fcalls + ps_wec_scalls) / scale_by])
    else:
        data = list([(snw_fcalls + snw_scalls) / scale_by, (swd_tfcalls + swd_tscalls) / scale_by])
    bp = ax.boxplot(data, meanline=True, labels=labels, patch_artist=True)
    # ax.hist(snw_fcalls+snw_scalls, bins=25, alpha=0.25, color='r', label='SNOPT', range=[0., 5E3])
    # ax.hist((swa_fcalls+swa_scalls)[swa_ef==1.], bins=25, alpha=0.25, color='b', label='SNOPT Relax', range=[0., 5E3])
    # ax.hist(ps_fcalls, bins=25, alpha=0.25, color='g', label='ALPSO', range=[0., 5E3])
    # ax.hist(ga_fcalls, bins=25, alpha=0.25, color='y', label='NSGA II', range=[0., 5E3])

    plt.setp(bp['boxes'], edgecolor='k', facecolor='none')
    plt.setp(bp['whiskers'], color='k')
    plt.setp(bp['fliers'], markeredgecolor='k')
    plt.setp(bp['medians'], color='b')
    plt.setp(bp['caps'], color='k')

    if model == "BPA":
        ax.set_ylabel('Function Calls ($10^5$)')
    else:
        ax.set_ylabel('Function Calls ($10^4$)')
    # ax.set_ylabel('Count')
    # ax.set_xlim([1, 10])
    # ax.set_ylim([-10, 100])
    # ax.legend(ncol=1, loc=1, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')
    plt.tight_layout()
    if save_figs:
        plt.savefig(filename+'_fcalls.pdf', transparent=True)

    if show_figs:
        plt.show()

    fig, ax = plt.subplots(1)

    scale_by = 1E3

    # data = list([(snw_fcalls + snw_scalls)/ scale_by, (swa_tfcalls + swa_tscalls)/ scale_by, (swd_tfcalls + swd_tscalls)/ scale_by, (swh_tfcalls + swh_tscalls)/ scale_by, (ps_fcalls + ps_scalls)/ scale_by])
    if ps:
        data = list([(snw_fcalls + snw_scalls)/ scale_by, (swd_tfcalls + swd_tscalls)/ scale_by, (ps_fcalls + ps_scalls)/ scale_by])
        if ps_wec:
            data = list([(snw_fcalls + snw_scalls) / scale_by, (swd_tfcalls + swd_tscalls) / scale_by,
                         (ps_fcalls + ps_scalls) / scale_by, (ps_wec_fcalls + ps_wec_scalls) / scale_by])
    else:
        data = list([(snw_fcalls + snw_scalls) / scale_by, (swd_tfcalls + swd_tscalls) / scale_by])
    bp = ax.boxplot(data, meanline=True, labels=labels)

    ## change outline color, fill color and linewidth of the boxes
    linewidth = 2
    for box in bp['boxes']:
        # change outline color
        box.set(linewidth=linewidth)

    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(linewidth=linewidth)

    ## change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(linewidth=linewidth)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(linewidth=linewidth)

    ## change the style of fliers and their fill
    # for flier in bp['fliers']:
    #     flier.set(marker='o', alpha=0.5)

    ax.set_ylabel('Function Calls ($10^3$)')
    # ax.set_ylabel('Count')
    # ax.set_xlim([1, 10])
    # ax.set_ylim([-1, 14])
    # ax.legend(ncol=1, loc=1, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    # plt.tick_params(top='off', right='off')
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                 ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(30)

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename + '_fcalls_snopt.pdf', transparent=True)

    if show_figs:
        plt.show()

    fig, ax = plt.subplots(1)
    #
    # swa_time = np.zeros(200)
    # for i in np.arange(0, 200):
    #     swa_time[i] = np.sum(swa_run_time[swa_id==i])

    swd_time = np.zeros(200)
    for i in np.arange(0, 200):
        swd_time[i] = np.sum(swd_run_time[swd_id == i])
    #
    # swh_time = np.zeros(200)
    # for i in np.arange(0, 200):
    #     swh_time[i] = np.sum(swh_run_time[swh_id == i])

    # data = list([snw_run_time/60., swa_time/60., ps_run_time/60., ga_run_time/60.])
    # data = list([snw_run_time/60., swa_time/60., swd_time/60., swh_time/60., ps_run_time/60.])
    if ps:
        data = list([snw_run_time/60., swd_time/60., ps_run_time/60.])
        if ps_wec:
            data = list([snw_run_time / 60., swd_time / 60., ps_run_time / 60., ps_wec_run_time / 60.])
    else:
        data = list([snw_run_time / 60., swd_time / 60.])

    bp = ax.boxplot(data, meanline=True, labels=labels, patch_artist=True)
    # y_formatter = ticker.ScalarFormatter(useOffset=True)
    # ax.yaxis.set_major_formatter(y_formatter)
    # ax.hist(snw_run_time/60, bins=25, alpha=0.25, color='r', label='SNOPT', range=[0., 80], log=True)
    # ax.hist(swa_time/60, bins=25, alpha=0.25, color='b', label='SNOPT Relax', range=[0., 80], log=True)
    # ax.hist(ps_run_time/60, bins=25, alpha=0.25, color='g', label='ALPSO', range=[0., 80], log=True)
    # ax.hist(ga_run_time/60, bins=25, alpha=0.25, color='y', label='NSGA II', range=[0., 80], log=True)
    plt.setp(bp['boxes'], edgecolor='k', facecolor='none')
    plt.setp(bp['whiskers'], color='k')
    plt.setp(bp['fliers'], markeredgecolor='k')
    plt.setp(bp['medians'], color='b')
    plt.setp(bp['caps'], color='k')
    ax.set_ylabel('Run Time (m)')
    # ax.set_ylabel('Count')
    # ax.set_xlim([1, 10])
    # ax.set_ylim([0.3, 1.0])
    # ax.legend(ncol=1, loc=1, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_time.pdf', transparent=True)

    if show_figs:
        plt.show()

    return

def plot_optimization_results_38_turbs_hist(filename, save_figs, show_figs):

    # load data
    # data_snopt_mstart = np.loadtxt("./image_data/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    data_snop_relax = np.loadtxt("./image_data/snopt_relax_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    data_ps = np.loadtxt("./image_data/ps_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
    # aep run opt (kW), run time (s), obj func calls, sens func calls
    sr_id = data_snop_relax[:, 0]
    sr_ef = data_snop_relax[:, 1]
    sr_orig_aep = data_snop_relax[0,4]
    sr_ti_opt = data_snop_relax[:,3]
    # sr_run_start_aep = data_snop_relax[0, 7]
    sr_run_end_aep = data_snop_relax[sr_ti_opt==5, 6]
    sr_run_time = data_snop_relax[:, 8]
    sr_fcalls = data_snop_relax[:, 9]
    sr_scalls = data_snop_relax[:, 10]

    sr_tfcalls = sr_fcalls[sr_ti_opt == 5]
    sr_tscalls = sr_fcalls[sr_ti_opt == 5]

    sr_run_improvement = sr_run_end_aep / sr_orig_aep - 1.
    sr_mean_run_improvement = np.average(sr_run_improvement)
    sr_std_improvement = np.std(sr_run_improvement)

    # # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
    # # run time (s), obj func calls, sens func calls
    # sm_id = data_snopt_mstart[:, 0]
    # sm_ef = np.ones_like(sm_id)
    # sm_orig_aep = data_snopt_mstart[0, 4]
    # # sr_run_start_aep = data_snop_relax[0, 7]
    # sm_run_end_aep = data_snopt_mstart[:, 6]
    # sm_run_time = data_snopt_mstart[:, 7]
    # sm_fcalls = data_snopt_mstart[:, 8]
    # sm_scalls = data_snopt_mstart[:, 9]

    # sm_run_improvement = sm_run_end_aep / sm_orig_aep - 1.
    # sm_run_improvement = sm_run_end_aep / sr_orig_aep - 1.
    # sm_mean_run_improvement = np.average(sm_run_improvement)
    # sm_std_improvement = np.std(sr_run_improvement)

    # fig, ax = plt.subplots(1)
    #
    # # labels = list(['SNOPT', 'SNOPT Relax', 'ALPSO', 'NSGA II'])
    # labels = list(['SNOPT+WEC'])
    # # labels = list('abcd')
    # # data = list([sm_run_improvement, sr_run_improvement, ps_run_improvement, ga_run_improvement])
    # aep_scale = 1E-6
    # data = list([sm_run_end_aep*aep_scale, sr_run_end_aep*aep_scale])
    # ax.boxplot(data, meanline=True, labels=labels)
    #
    # ax.set_ylabel('AEP (GWh)')
    # # ax.set_ylabel('Count')
    # # ax.set_xlim([0, 0.1])
    # # ax.set_ylim([300, 400])
    # # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # # tick_spacing = 0.01
    # # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')
    #
    # if save_figs:
    #     plt.savefig(filename+'_aep.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()
    #
    # fig, ax = plt.subplots(1)
    #
    # data = list([sm_run_improvement*100, sr_run_improvement*100])
    # ax.boxplot(data, meanline=True, labels=labels)
    #
    # ax.set_ylabel('AEP Improvement (%)')
    # # ax.set_ylim([-15, 15.0])
    # # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # # tick_spacing = 0.01
    # # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')
    #
    # if save_figs:
    #     plt.savefig(filename+'_percentaep.pdf', transparent=True)
    #
    # if show_figs:
    #     plt.show()

    fig, ax = plt.subplots(1)

    scale_by = 1E5
    # data = np.array([sm_fcalls+sm_scalls, sr_fcalls+sr_scalls, ps_fcalls, ga_fcalls])/scale_by
    # data = list([(sm_fcalls+sm_scalls)/scale_by, (sr_tfcalls+sr_tscalls)/scale_by])
    # ax.boxplot(data, meanline=True, labels=labels)
    print( sr_run_improvement)
    # ax.hist(sm_fcalls+sm_scalls, bins=25, alpha=0.25, color='r', label='SNOPT', range=[0., 5E3])
    ax.hist(100*sr_run_improvement, bins=25, alpha=0.75, color='b', label='SNOPT Relax', histtype=u'step')
    # ax.hist(ps_fcalls, bins=25, alpha=0.25, color='g', label='ALPSO', range=[0., 5E3])
    # ax.hist(ga_fcalls, bins=25, alpha=0.25, color='y', label='NSGA II', range=[0., 5E3])

    ax.set_ylabel('Count')
    ax.set_xlabel('Improvement from the Base Case ($\%$)')
    # ax.set_ylabel('Count')
    # ax.set_xlim([1, 10])
    # ax.set_ylim([-10, 100])
    # ax.legend(ncol=1, loc=1, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')
    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+'_aep.pdf', transparent=True)

    if show_figs:
        plt.show()


def plot_round_farm_finish_pres(filename, save_figs, show_figs):

    data_directory = './image_data/'

    # get bounds
    data_file = 'nTurbs38_spacing5_layout_0.txt'
    # parse data
    plot_data = np.loadtxt(data_directory + data_file)
    turbineX = (plot_data[:, 0]) + 1.#0.5
    turbineY = (plot_data[:, 1]) + 1.#0.5
    plot_data = np.loadtxt(data_directory + data_file)

    # set domain
    xmax = np.max(turbineX)
    xmin = np.min(turbineX)
    ymax = np.max(turbineY)
    ymin = np.min(turbineY)

    # define wind farm area
    boundary_center_x = turbineX[0]
    boundary_center_y = turbineY[0]
    boundary_radius = (xmax - turbineX[0]) + 0.5

    data_snop_relax = np.loadtxt("./image_data/snopt_relax_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
    # aep run opt (kW), run time (s), obj func calls, sens func calls
    # sr_id = data_snop_relax[:, 0]
    sr_ef = data_snop_relax[:, 1]
    sr_id = data_snop_relax[sr_ef == 1, 0]
    sr_run_end_aep = data_snop_relax[sr_ef == 1, 7]

    sr_best_layout_id = sr_id[np.argmax(sr_run_end_aep)]

    print( sr_best_layout_id)

    # define turbine dimensions
    rotor_diameter = 126.4

    data_directory = './image_data/layouts/38_turbs/'

    # load layouts
    data_file_sr = 'snopt_multistart_locations_38turbs_nantucketWindRose_12dirs_BPA_run%i_EF1.000_TItype5.txt' % sr_best_layout_id
    # data_file_sm = 'snopt_multistart_locations_38turbs_nantucketWindRose_12dirs_BPA_run%i.txt' % sm_best_layout_id

    extensions = ['sr']

    for data_file, ext in zip([data_file_sr], extensions):
        # parse data
        plot_data = np.loadtxt(data_directory + data_file)
        turbineX = (plot_data[:, 2])/rotor_diameter + 0.5
        turbineY = (plot_data[:, 3])/rotor_diameter + 0.5


        # create figure and axes
        fig, ax = plt.subplots()

        # create and add domain boundary
        # les_domain = plt.Rectangle([0., 0.], 5000., 5000., facecolor='none', edgecolor='b', linestyle=':', label='Domain')
        # ax.add_patch(les_domain)

        # create and add wind farm boundary
        boundary_circle = plt.Circle((boundary_center_x, boundary_center_y),
                                     boundary_radius, facecolor='none', edgecolor='r', linestyle='--', linewidth=2)
        ax.add_patch(boundary_circle)
        constraint_circle = plt.Circle((boundary_center_x, boundary_center_y),
                                     boundary_radius-0.5, facecolor='none', edgecolor='r', linestyle=':', linewidth=2)
        # ax.add_patch(constraint_circle)

        # create and add wind turbines
        for x, y in zip(turbineX, turbineY):
            circle_start = plt.Circle((x, y), 1./2., facecolor='none', edgecolor='k', linestyle='-', label='Start', linewidth=2)
            ax.add_artist(circle_start)

        # pretty the plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        plt.tick_params(top='off', right='off')
        plt.axis('equal')
        # ax.legend([circle_start, boundary_circle, constraint_circle], ['Turbines', 'Farm Boundary', 'Boundary Constraint'],
        #           ncol=1, frameon=False, loc=1)
        # ax.set_xlabel('Turbine X Position ($X/D_r$)')
        # ax.set_ylabel('Turbine Y Position ($Y/D_r$)')

        ax.set_aspect('equal', adjustable='box')
        xhigh = np.max(turbineX)+5
        xlow = np.min(turbineX) -5
        yhigh = np.max(turbineY) + 5
        ylow = np.min(turbineY) - 5
        ax.set_xlim([xlow, xhigh])
        ax.set_ylim([ylow, yhigh])

        # plt.yticks([])
        # plt.xticks([])

        plt.tight_layout()

        if save_figs:
            plt.savefig('./images/'+ext+'_'+filename, transparent=True)
        if show_figs:
            plt.show()

    return


def get_statistics_nruns():

    return

def plot_results_nruns(filename, save_figs, show_figs):

    # import regular expresions package
    import re

    path_to_directories = '../project-code/optimizations/'

    # Spencer M. EDIT: Because of multiple optimization runs ('tries'), I've needed to add more data directories. Thus,
    # adding in directory string to identify which optimization run to pull the data from. NOTE: The very first try
    # is saved in a folder that has an empty "try" string.
    # FURTHER EDIT: From "try6" onwards, I've appended the OPTIMIZATION directories with the try number and left the
    # data directories alone.
    # TODO: Adjust logic in code so that I don't have to refactor code with "whichOptimizationTry" in order to switch
    # between optimization data sets. Maybe change names of the directories to match this new source tree
    # organization method?
    whichOptimizationTry = '_try6'

    # optimization_directories = ['no_local_ti_nrel_5mw', 'no_local_ti_vestas_v80', 'yes_local_ti_nrel_5mw',
    #                             'yes_local_ti_vestas_v80', 'yes_local_ti_and_ef10_nrel_5mw',
    #                             'no_then_yes_local_ti_nrel_5mw', 'no_then_yes_local_ti_vestas_v80',
    #                             'no_then_yes_local_ti_nrel_5mw_compare_LES_0',
    #                             'no_then_yes_local_ti_nrel_5mw_compare_LES_1']
    #
    # data_directories = ['output_files_snopt', 'output_files_snopt_wec']

    # Choose which plot to create.
    plotAllModels = False
    plotJensenAndBPA = True
    plotJensen = False
    plotFLORIS = False
    plotBPA = False

    if plotAllModels:

        optimization_directories = ['JENSEN_wec_opt', 'FLORIS_wec_opt', 'BPA_wec_opt']

        data_directoriesElse = ['output_files_snopt_wec'+whichOptimizationTry, 'output_files_snopt'+whichOptimizationTry]
        data_directoriesBPA = ['output_files_snopt_wec'+whichOptimizationTry, 'output_files_snopt_TI0'+whichOptimizationTry,
                               'output_files_snopt_TI5'+whichOptimizationTry]

        model = ['JENSEN', 'JENSEN', 'FLORIS', 'FLORIS', 'BPA', 'BPA', 'BPA']
        labels = ['Jensen WEC', 'Jensen', 'FLORIS WEC', 'FLORIS', 'BPA WEC TI0', 'BPA TI5', 'BPA TI0']

        # Since all the models are being plotted, make the figure size a little bigger.
        figSize = (10, 10)

    # TODO: pull the right data from the supercomputer. Test FLORISSE with 3-turbine case. Semester report due at end
    # of next week, have my results ready to go and written up so Jared can include it in our report. Treat this
    # results section as another case study (similar to the case study in Jared's WEC paper). Include the 3-turbine
    # case and the 38-turbine case for JENSEN and FLORISSE.
    elif plotJensenAndBPA:

        optimization_directories = ['JENSEN_wec_opt'+whichOptimizationTry, 'BPA_wec_opt'+whichOptimizationTry]

        data_directoriesElse = ['output_files_snopt_wec', 'output_files_snopt']
        data_directoriesBPA = ['output_files_snopt_wec', 'output_files_snopt_TI0',
                               'output_files_snopt_TI5']

        model = ['JENSEN', 'JENSEN', 'BPA', 'BPA', 'BPA']
        labels = ['Jensen WEC', 'Jensen', 'BPA WEC TI0', 'BPA TI5', 'BPA TI0']

        # Since all the models are being plotted, make the figure size a little bigger.
        figSize = (10, 10)

    elif plotJensen:

        optimization_directories = ['JENSEN_wec_opt']

        data_directoriesElse = ['output_files_snopt'+whichOptimizationTry,
                                'output_files_snopt_wec'+whichOptimizationTry]
        data_directoriesBPA = ['output_files_snopt_wec'+whichOptimizationTry, 'output_files_snopt_TI0'+whichOptimizationTry,
                               'output_files_snopt_TI5'+whichOptimizationTry]

        model = ['JENSEN', 'JENSEN']
        labels = ['Jensen', 'Jensen WEC']

        # Since only one model is being plotted, maybe make the figure size a little smaller.
        figSize = (10, 10)

    aep_scale = 1E-6

    # initialize list to contain labels
    # labels = list([])

    data_aep = list([])
    data_run_time = list([])
    data_fcalls = list([])
    data_improvement = list([])

    plot_num = 0
    for opt_dir in optimization_directories:

        if ((opt_dir == 'BPA_wec_opt') or (opt_dir == 'BPA_wec_opt'+whichOptimizationTry)):
            data_directories = data_directoriesBPA
        else:
            data_directories = data_directoriesElse

        for data_dir in data_directories:

            # load data
            filename = 'snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_%s_all.txt' % model[plot_num]
            data = np.loadtxt(path_to_directories+opt_dir+'/'+data_dir+'/'+filename)

            # if plot_num == 0:
            #     labels = [opt_dir+'_snopt']
            # else:
            #     labels.append(opt_dir+'_snopt')

            # adjust for wake expansion continuation
            if plot_num == 1:
                shift = 1
            else:
                shift = 1
            # if 'wec' in data_dir:
            #
            #     # shift to account for ef location in array
            #     shift = 1
            #
            #     ef = data[:, 1]
            #
            #     if 'no_then_yes' in opt_dir:
            #         data = data[ef == 1, :]
            #         ti_opt = data[:, 3]
            #         data = data[ti_opt == 5, :]
            #     else:
            #         data = data[ef == 1, :]
            #
            #     labels[plot_num] = model[plot_num]
            #     # labels[plot_num] = str(labels[plot_num]) + '_wec'
            #
            # else:
            #     shift = 1

            # parse data into desired parts
            # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
            # run time (s), obj func calls, sens func calls
            id = data[:, 0]
            orig_aep = data[0, 3+shift]
            end_aep = data[:, 5+shift]
            run_time = data[:, 7+shift]
            fcalls = data[:, 8+shift]
            scalls = data[:, 9+shift]

            # get some basic stats
            improvement = end_aep / orig_aep - 1.
            mean_improvement = np.average(improvement)
            std_improvement = np.std(improvement)
            max_improvement = np.max(improvement)
            max_aep = np.max(end_aep)
            max_aep_id = id[np.argmax(end_aep)]

            print( labels[plot_num], "mean imp:", mean_improvement, "std. imp:", std_improvement)
            print( "max imp:", max_improvement, 'max AEP:', max_aep, 'max AEP run:', max_aep_id)

            data_aep.append(end_aep*aep_scale)
            data_run_time.append(run_time)
            data_fcalls.append(fcalls+scalls)
            data_improvement.append(improvement)

            plot_num += 1

    # set xtick label angle
    angle = 90

    plt.rcParams.update({'font.size': 26})
    fig, ax = plt.subplots(figsize=figSize)

    # Boxplot
    ax.boxplot(data_aep, meanline=True, labels=labels)
    ax.set_ylabel('AEP (GWh)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for tick in ax.get_xticklabels():
        tick.set_rotation(angle)
    plt.tight_layout()

    # Histogram.
    # ax.hist(data_aep, label=labels)
    # ax.set_xlabel('AEP (GWh)')
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    # for tick in ax.get_xticklabels():
    #     tick.set_rotation(angle)
    # plt.tight_layout()

    # SPENCER M. EDIT: To get the correct axis label, changing the data_improvement to be 100 times its original
    # value. This is to get the percent improvement from decimal form to percentage form.
    for i in range(0, len(data_improvement)):
        data_improvement[i] *= 100.0

    # Create new figure and axes.
    fig, ax = plt.subplots(figsize=figSize)

    # Boxplot.
    ax.boxplot(data_improvement, meanline=True, labels=labels)
    ax.set_ylabel('AEP Improvement (%)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # ax.set_ylim([-0.15, 0.1])
    for tick in ax.get_xticklabels():
        tick.set_rotation(angle)
    plt.tight_layout()

    # Histogram.
    # ax.hist(data_improvement, bins=100, label=labels, alpha=0.75)
    # ax.set_xlabel('AEP Improvement (%)')
    # ax.set_ylabel('Count')
    # ax.spines['right'].set_visible(False)
    # ax.spines['top'].set_visible(False)
    # # for tick in ax.get_xticklabels():
    # #     tick.set_rotation(angle)
    # plt.tight_layout()

    fig, ax = plt.subplots(figsize=figSize)
    ax.boxplot(data_run_time, meanline=True, labels=labels)
    ax.set_ylabel('Run Time (min)')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for tick in ax.get_xticklabels():
        tick.set_rotation(angle)
    plt.tight_layout()

    fig, ax = plt.subplots(figsize=figSize)
    ax.boxplot(data_fcalls, meanline=True, labels=labels)
    ax.set_ylabel('Function Calls')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    for tick in ax.get_xticklabels():
        tick.set_rotation(angle)
    plt.tight_layout()

    # ax.set_ylabel('Count')
    # ax.set_xlim([0, 0.1])
    # ax.set_ylim([300, 400])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))



    # if save_figs:
    #     plt.savefig('./images/' + ext + '_' + filename, transparent=True)

    if show_figs:
        plt.show()
    return

def plot_shear_fit(filename, save_figs, show_figs):

    # load data
    data_directory = './image_data/'
    data_file_func = 'shear_data_func.txt'
    data_file_les = 'shear_data_les.txt'
    plot_data_func = np.loadtxt(data_directory + data_file_func)
    plot_data_les = np.loadtxt(data_directory + data_file_les)

    fig, ax = plt.subplots(1, figsize=(6,3))

    ax.plot(plot_data_les[:, 1], plot_data_les[:, 0], 'o', label='LES')
    ax.plot(plot_data_func[:, 1], plot_data_func[:, 0], label='Shear Func')
    # print( plot_data_les, plot_data_func)
    ax.set_xlabel('Wind Speed, m/s')
    ax.set_ylabel('Height, m')
    ax.set_xlim([0, 13])

    ax.legend(loc=2, frameon=False, ncol=1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')
    plt.tight_layout()
    # show plot
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_1_rotor_point(filename, save_figs=False, show_figs=True):

    fig, ax = plt.subplots(1)
    x, y = np.array([0.0, 0.0])
    ax.plot([-0.55, 0.55], [-0.5, 0.6], 'w', alpha=0.0)
    points = ax.scatter(x * 0.5, y * 0.5)
    circle = plt.Circle((0.0, 0.0), 0.5, color='b', alpha=0.08)
    ax.add_artist(circle)
    # ax.set_xlim([-0.6, 0.6])
    # ax.set_ylim([-0.6, 0.65])
    ax.axis("square")
    plt.xlabel('Horizontal Distance From Hub ($\Delta X/D_r$)')
    plt.ylabel('Vertical Distance From Hub ($\Delta Z/D_r$)')

    ax.legend([points, circle], ["Sampling point", "Rotor swept area"], loc=2, frameon=False, ncol=1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    # show plot
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_100_rotor_points(filename, save_figs=False, show_figs=True, npoints=100):

    def sunflower_points(n, alpha=1.0):
        # this function generates n points within a circle in a sunflower seed pattern
        # the code is based on the example found at
        # https://stackoverflow.com/questions/28567166/uniformly-distribute-x-points-inside-a-circle

        def radius(k, n, b):
            if (k + 1) > n - b:
                r = 1.  # put on the boundary
            else:
                r = np.sqrt((k + 1.) - 1. / 2.) / np.sqrt(n - (b + 1.) / 2.)  # apply squareroot

            return r

        x = np.zeros(n)
        y = np.zeros(n)

        b = np.round(alpha * np.sqrt(n))  # number of boundary points

        phi = (np.sqrt(5.) + 1.) / 2.  # golden ratio

        for k in np.arange(0, n):
            r = radius(k, n, b)

            theta = 2. * np.pi * (k + 1) / phi ** 2

            x[k] = r * np.cos(theta)
            y[k] = r * np.sin(theta)

        return x, y

    fig, ax = plt.subplots(1)
    x, y = sunflower_points(npoints)
    ax.plot([-0.55, 0.55], [-0.5, 0.6], 'w', alpha=0.0)
    points = ax.scatter(x * 0.5, y * 0.5)
    circle = plt.Circle((0.0, 0.0), 0.5, color='b', alpha=0.08)
    ax.add_artist(circle)
    # ax.set_xlim([-0.6, 0.6])
    # ax.set_ylim([-0.6, 0.65])
    ax.axis("square")
    plt.xlabel('Horizontal Distance From Hub ($\Delta X/D_r$)')
    plt.ylabel('Vertical Distance From Hub ($\Delta Z/D_r$)')

    ax.legend([points, circle], ["Sampling points", "Rotor swept area"], loc=2, frameon=False, ncol=1)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    plt.tight_layout()

    # show plot
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_model_contours_vertical(filename, save_figs, show_figs, before=False):

    font = {'family': 'normal',
            'weight': 'bold',
            'size': 15}

    plt.rc('font', **font)

    # define turbine dimensions
    rotor_diameter = 0.15
    hub_height = 0.125/rotor_diameter
    yaw = np.array([0.0])

    # load data
    data_directory = './image_data/'
    if before:
        data_file = 'model_contour_vertical_2016_before.txt'
    else:
        data_file = 'model_contour_vertical_2016_after.txt'

    plot_data = np.loadtxt(data_directory+data_file)
    x = plot_data[::2, 0]/rotor_diameter
    z = plot_data[::8, 1]/rotor_diameter
    v = plot_data[::8, 2::2]
    xmax = np.max(x)
    xmin = np.min(x)
    zmax = np.max(z)
    zmin = np.min(z)

    print( x.shape, z.shape, v.shape)
    colormap = "YlOrBr_r"
    colormap = "YlOrRd_r"
    colormap = "Blues_r"
    colormap = "Reds_r"
    colormap = "Greens_r"
    colormap = "Greys_r"
    colormap = "hot"
    colormap = "BuGn_r"
    colormap = "GnBu_r"
    # colormap = "YlGn_r"

    if before:
        for i in np.arange(0, x.size):
            if x[i] < 0.34581857901067325 and x[i] > 0:
                v[:, i] = None

    # define scale limits
    vmin = 1
    vmax = 2.5

    # create figure and axes
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 4), dpi=80)
    ax.set_ylim([0.0, 2.0])

    # add data to axes
    ax.pcolormesh(x, z, np.round(v, 1), vmin=vmin, vmax=vmax, cmap=colormap)

    # add turbine to axes
    ax.plot([0., 0.], [hub_height - .5, hub_height + .5], linewidth=5, linestyle='-',
            color='k')  # plot the wind turbine

    # add contours
    nContours = 1.5 / 0.1
    CF = ax.contourf(x, z, v, int(nContours), cmap=colormap)
    CS = ax.contour(x, z, v, int(nContours), colors='k')
    manual_locations = np.array([(5.75, 0.5), (5.0, 0.6), (4.25, 0.75),
                        (8, 0.25), (10, 0.5), (10.75, 0.75), (11.5, 1), (12.5, 1.1), (13.5, 1.35), (14.5, 1.45), (15.5, 1.65)])
    ax.clabel(CS, inline=1, fmt='%.1f', c='k', ticks=(np.linspace(vmin, vmax, nContours)), colors='k',
              manual=manual_locations)


    # add colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='1%', pad=-5)
    im = ax.imshow(v, vmin=vmin, vmax=vmax, extent=[xmin, xmax, zmin, zmax], aspect=2, cmap=colormap)
    # add colorbar
    cbar = fig.colorbar(im, ax=ax, cax=cax, orientation='vertical', ticks=(1, 1.5, 2., 2.5), cmap=colormap)
    cax.tick_params(length=0)
    cbar.add_lines(CS)


    # add labels
    # plt.title('Bastankhah: Side View down Center-line (Yaw = %i (Degrees))' % (yaw[0]))
    cbar.set_label('wind speed (m/s)', fontsize=18)
    ax.set_xlabel('Downstream Distance $(x/d)$', fontsize=18)
    ax.set_ylabel('Height $(z/d)$', fontsize=18)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    if before:
        from matplotlib import patches
        rect = patches.Rectangle([0, 0], 0.34581857901067325 / rotor_diameter, 2, linewidth=0, edgecolor='none',
                             facecolor='w')
        ax.add_patch(rect)

    # scale and finish plot
    # plt.autoscale(True)
    plt.tight_layout()

    # show plot
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_power_direction_horns_rev(filename, save_figs=False, show_figs=True, nrpt=1):


    # load data
    our_model = np.loadtxt("./image_data/power_direction_res_%irotorpts_2016model.txt" % nrpt)
    npa_les = np.loadtxt("./image_data/power_by_direction_niayifar_les.txt", delimiter=',')
    npa_model = np.loadtxt("./image_data/power_by_direction_niayifar_model.txt", delimiter=',')

    fig, ax = plt.subplots(1)

    ax.plot(npa_les[:, 0], npa_les[:, 1], label="NP LES", c='c', marker='o')
    ax.plot(npa_model[:, 0], npa_model[:, 1], label="NP Model", c='g')

    ax.plot(our_model[:, 0], our_model[:, 1], label="No local TI",
            c='k', linestyle='--')
    ax.plot(our_model[:, 0], our_model[:, 2], label="Hard max TI",
            c='b', linestyle='-')
    ax.plot(our_model[:, 0], our_model[:, 3], label="Smooth max TI",
            c='r', linestyle='--')

    ax.set_xlabel('Wind Direction (deg.)')
    ax.set_ylabel('Normalized Directional Power')
    ax.set_xlim([160, 360])
    ax.set_ylim([0.1, 1.0])
    ax.legend(ncol=2, loc=3, frameon=False, )  # show plot
    tick_spacing = 20
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    print( "for horns rev directional")
    # print( "no ti error" (our_model[our_model[:, 0]==npa_les[:,0], 1]-npa_les[:, 1])/npa_les[:, 1])
    # print( "hard max error"(our_model[:, 2] - npa_les[:, 1]) / npa_les)
    # print( "smooth max error"(our_model[:, 3] - npa_les[:, 1]) / npa_les)

    return

def plot_power_direction_error_horns_rev(filename, save_figs=False, show_figs=True):


    # load data
    # error_data_our_model = np.loadtxt("./image_data/sampling_error_results_to1000_stepsize50.txt")
    # error_data_our_model = np.loadtxt("./image_data/sampling_error_results_to500_stepsize10.txt")
    error_data_our_model = np.loadtxt("./image_data/sampling_error_results_to1000_stepsizeVaries.txt")
    # error_data_our_model = np.loadtxt("./image_data/sampling_error_results_tips_and_hub.txt")
    ave_error_npa_model = 0.0296786273592*100
    max_error_npa_model = 0.0745257894155*100

    nRotorPoints = error_data_our_model[:, 0]
    max_error_results = error_data_our_model[:, 1:4]*100
    ave_error_results = error_data_our_model[:, 4:]*100

    figsize=(7,4)
    fig, ax = plt.subplots(figsize=figsize)

    plt.plot([0, np.max(nRotorPoints)], [max_error_npa_model, max_error_npa_model], c='c', label='NP')
    plt.plot(nRotorPoints, max_error_results[:, 0], c='k', linestyle='--', label='No local TI')
    plt.plot(nRotorPoints, max_error_results[:, 1], c='b', linestyle='-', label='Hard max TI')
    plt.plot(nRotorPoints, max_error_results[:, 2], c='r', linestyle='--', label='Smooth max TI')

    ax.set_xlabel('Rotor-swept area sample points')
    ax.set_ylabel('Maximum Error, $\%$')
    ax.set_xlim([1, 500])
    # ax.set_ylim([0.1, 1.0])
    ax.legend(ncol=2, loc=0, frameon=False)  # show plot
    tick_spacing = 50
    majors = np.append(np.array([1]), np.arange(tick_spacing, 501, tick_spacing))
    ax.xaxis.set_major_locator(ticker.FixedLocator(majors))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+"max_error.pdf", transparent=True)

    if show_figs:
        plt.show()

    fig, ax = plt.subplots(figsize=figsize)

    plt.plot([0, np.max(nRotorPoints)], [ave_error_npa_model, ave_error_npa_model], c='c', label='NP')
    plt.plot(nRotorPoints, ave_error_results[:, 0], c='k', linestyle='--', label='No local TI')
    plt.plot(nRotorPoints, ave_error_results[:, 1], c='b', linestyle='-', label='Hard max TI')
    plt.plot(nRotorPoints, ave_error_results[:, 2], c='r', linestyle='--', label='Smooth max TI')

    ax.set_xlabel('Rotor-swept area sample points')
    ax.set_ylabel('Average Error, $\%$')
    ax.set_xlim([1, 500])
    # ax.set_ylim([0.1, 1.0])
    ax.legend(ncol=2, loc=0, frameon=False)  # show plot
    tick_spacing = 50
    majors = np.append(np.array([1]), np.arange(tick_spacing, 501, tick_spacing))
    ax.xaxis.set_major_locator(ticker.FixedLocator(majors))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename+"ave_error.pdf", transparent=True)

    if show_figs:
        plt.show()

    # print( "for horns rev directional")
    # print( "no ti error" (our_model[our_model[:, 0]==npa_les[:,0], 1]-npa_les[:, 1])/npa_les[:, 1])
    # print( "hard max error"(our_model[:, 2] - npa_les[:, 1]) / npa_les)
    # print( "smooth max error"(our_model[:, 3] - npa_les[:, 1]) / npa_les)

    return

def plot_power_row_horns_rev(filename, save_figs=False, show_figs=True, nrpt=1):

    # load data
    our_model = np.loadtxt("./image_data/power_line_res_%irotorpts_2016model.txt" % nrpt)
    npa_les = np.loadtxt("./image_data/niayifar-normalized-power-les.txt", delimiter=',')
    npa_model = np.loadtxt("./image_data/niayifar-normalized-power-model.txt", delimiter=',')

    fig, ax = plt.subplots(1)

    ax.plot(np.round(npa_les[:, 0]), npa_les[:, 1], label="NP LES", c='c', marker='o')
    ax.plot(np.round(npa_model[:, 0]), npa_model[:, 1], label="NP Model", c='g', marker='v')
    ax.plot(our_model[:, 0]+1, our_model[:, 1], label="No local TI",
            c='k', linestyle='--', marker='o')
    ax.plot(our_model[:, 0]+1, our_model[:, 2], label="Hard max TI",
            c='b', linestyle='-', marker='o')
    ax.plot(our_model[:, 0] + 1, our_model[:, 3], label="Smooth max TI",
            c='r', linestyle='--', marker='o')


    ax.set_xlabel('Row Number')
    ax.set_ylabel('Normalized Power')
    ax.set_xlim([1, 10])
    ax.set_ylim([0., 1.0])
    ax.legend(ncol=1, loc=1, frameon=False, )  # show plot
    tick_spacing = 1
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    print( "for horns rev by row")
    print( "npa ave error", np.average(np.abs(((npa_model[:, 1]-npa_les[:, 1])/npa_les[:, 1]))))
    print( "npa max error", np.max(np.abs((npa_model[:, 1]-npa_les[:, 1]))/npa_les[:, 1]))
    print( "no ti ave error", np.average(np.abs((our_model[:, 1]-npa_les[:, 1]))/npa_les[:, 1]))
    print( "no ti max error", np.max(np.abs((our_model[:, 1]+1-npa_les[:, 1]))/npa_les[:, 1]))
    print( "hard max ave error", np.average(np.abs((our_model[:, 2]-npa_les[:, 1])/npa_les[:, 1])))
    print( "hard max max error", np.max(np.abs((our_model[:, 2]-npa_les[:, 1])/npa_les[:, 1])))
    print( "smooth max ave error", np.average(np.abs((our_model[:, 3]-npa_les[:, 1])/npa_les[:, 1])))
    print( "smooth max maxerror", np.max(np.abs((our_model[:, 3]-npa_les[:, 1])/npa_les[:, 1])))

    return

def plot_turb_power_error_baseline(filename, save_figs=False, show_figs=True):
    # based on https://matplotlib.org/gallery/images_contours_and_fields/image_annotated_heatmap.html#sphx-glr-gallery-images-contours-and-fields-image-annotated-heatmap-py

    input_directory = "./image_data/"

    windDirections = np.array([10., 40., 70., 100., 130., 160., 190., 220., 250., 280., 310., 340.])
    nDirections = windDirections.size
    bp_turb_data = np.loadtxt(input_directory+"bp_turb_power_baseline.txt")
    nTurbines = bp_turb_data[:, 0].size
    sowfa_data = np.loadtxt(input_directory + 'BaselineSOWFADirectionalPowerOutputGenerator.txt')

    sowfa_turb_powers = np.zeros([nTurbines, nDirections])
    for dir, i in zip(windDirections, np.arange(0, nDirections)):
        sowfa_turb_powers[:, i] = sowfa_data[sowfa_data[:, 0] == dir, 4] / 1000.

    print( sowfa_turb_powers[sowfa_turb_powers[:, 23:26]==310, 23:26])
    quit()
    turb_error = ((bp_turb_data - sowfa_turb_powers)/sowfa_turb_powers)
    fig, ax = plt.subplots(figsize=(12,12))
    im, cbar = heatmap(turb_error, np.arange(nTurbines), windDirections, ax=ax,
                       cmap="bwr", cbarlabel="Turbine Power Error", vmin=-2.5, vmax=2.5, interpolation='none', cbar_kw={"shrink": 1.0, "aspect": 50}, aspect="auto")
    texts = annotate_heatmap(im, valfmt="{x:.2f}")

    ax.set_xlabel('Direction')
    ax.set_ylabel('Turbine')

    fig.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return


def plot_dir_power_error_baseline(filename, save_figs=False, show_figs=True):
    # based on https://matplotlib.org/gallery/images_contours_and_fields/image_annotated_heatmap.html#sphx-glr-gallery-images-contours-and-fields-image-annotated-heatmap-py

    input_directory = "./image_data/"

    windDirections = np.array([10., 40., 70., 100., 130., 160., 190., 220., 250., 280., 310., 340.])

    nDirections = windDirections.size
    bp_turb_data = np.loadtxt(input_directory + "bp_turb_power_baseline.txt")

    nTurbines = bp_turb_data[:, 0].size
    sowfa_data = np.loadtxt(input_directory + 'BaselineSOWFADirectionalPowerOutputGenerator.txt')

    sowfa_dir_powers = np.zeros([nDirections])
    bp_dir_powers = np.zeros([nDirections])

    for dir, i in zip(windDirections, np.arange(0, nDirections)):
        sowfa_dir_powers[i] = np.sum(sowfa_data[sowfa_data[:, 0] == dir, 4] / 1000.)
        bp_dir_powers[i] = np.sum(bp_turb_data[:, i])

    dir_error = ((bp_dir_powers - sowfa_dir_powers) / sowfa_dir_powers)
    fig, ax = plt.subplots(figsize=(9,1.5))
    im, cbar = heatmap(np.array([dir_error]), [''], windDirections, ax=ax,
                       cmap="bwr", cbarlabel="Turbine Power Error", vmin=-2.5, vmax=2.5, interpolation='none',
                       cbar_kw={"shrink": 1.50}, aspect="auto", use_cbar=False)
    texts = annotate_heatmap(im, valfmt="{x:.2f}")

    ax.set_xlabel('Direction')

    fig.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_farm(filename, save_figs, show_figs, layout='start', turb_nums=False):
    # font = {'size': 13}
    # plt.rc('font', **font)
    #
    # plt.rcParams['xtick.major.pad'] = '8'
    # plt.rcParams['ytick.major.pad'] = '8'

    # define turbine dimensions
    rotor_diameter = 126.4

    # set domain
    xmax = 5500.
    xmin = -500.0
    ymax = 6000.
    ymin = -500.0

    # define wind farm area
    boundary_center_x = 2500.
    boundary_center_y = 2500.
    boundary_radius = 2000.

    # load data
    data_directory = './image_data/layouts/38_turbs/'
    if layout == 'start':
        data_file = 'nTurbs38_spacing5_layout_0.txt'
        plot_data = np.loadtxt(data_directory + data_file)

        # parse data
        turbineX = (plot_data[:, 0])*rotor_diameter - boundary_radius + rotor_diameter/2. + boundary_center_x
        turbineY = (plot_data[:, 1])*rotor_diameter - boundary_radius + rotor_diameter/2. + boundary_center_y
    elif layout == 'finish':
        data_file = 'snopt_multistart_locations_38turbs_nantucketWindRose_12dirs_BPA_run0_EF1.000_TItype5.txt'
        plot_data = np.loadtxt(data_directory + data_file)

        # parse data
        turbineX = (plot_data[:, 2])- boundary_radius  + boundary_center_x
        turbineY = (plot_data[:, 3])- boundary_radius  + boundary_center_x
    else:
        raise ValueError('incorrect layout specified')

    print( np.average(turbineX))

    print( turbineX, turbineY)

    nTurbines = turbineX.size

    # create figure and axes
    fig, ax = plt.subplots()

    # create and add domain boundary
    les_domain = plt.Rectangle([0., 0.], 5000., 5000., facecolor='none', edgecolor='b', linestyle=':', label='Domain')
    ax.add_patch(les_domain)

    # create and add wind farm boundary
    boundary_circle = plt.Circle((boundary_center_x, boundary_center_y),
                                 boundary_radius, facecolor='none', edgecolor='r', linestyle='--')
    ax.add_patch(boundary_circle)

    # create and add wind turbines
    for x, y in zip(turbineX, turbineY):
        circle_start = plt.Circle((x, y), rotor_diameter/2., facecolor='none', edgecolor='k', linestyle='-', label='Start')
        ax.add_artist(circle_start)

    if turb_nums:
        for i in np.arange(nTurbines):
            ax.annotate(i, (turbineX[i]+rotor_diameter/2., turbineY[i]+rotor_diameter/2.))

    # pretty the plot
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')
    plt.axis('equal')
    ax.legend([boundary_circle, les_domain], ['LES Domain','Farm Boundary'],
              ncol=2, frameon=False, loc=2)
    ax.set_xlabel('Turbine X Position (m)')
    ax.set_ylabel('Turbine Y Position (m)')
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)
    if show_figs:
        plt.show()

def plot_any_farm(filename, save_figs, show_figs, nturbs=60):

    from plantenergy import visualization_tools as vt
    from plantenergy.GeneralWindFarmComponents import calculate_boundary

    data_file = './image_data/layouts/%i_turbs/nTurbs%i_spacing5_layout_0.txt' % (nturbs, nturbs)
    layout_data = np.loadtxt(data_file)

    rotor_diam = 80.
    turb_x = layout_data[:, 0]*rotor_diam
    turb_y = layout_data[:, 1]*rotor_diam

    boundaryVertices, boundaryNormals = calculate_boundary(layout_data * rotor_diam)

    farm_plot = vt.wind_farm_plot(turb_x, turb_y, rotor_diam, boundaryVertices[:, 0],boundaryVertices[:, 1])
    farm_plot.plot_wind_farm()
    farm_plot.legend.remove()
    plt.tight_layout()
    if save_figs:
        farm_plot.save_wind_farm(filename)
    if show_figs:
        farm_plot.show_wind_farm()




def plot_farm(filename, save_figs, show_figs, layout='start', turb_nums=False, turbs=16):
    # font = {'size': 13}
    # plt.rc('font', **font)
    #
    # plt.rcParams['xtick.major.pad'] = '8'
    # plt.rcParams['ytick.major.pad'] = '8'

    # define turbine dimensions
    rotor_diameter = 80.
    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]
    # load data

    data_directory = './image_data/layouts/%i_turbs/' % (turbs)
    if layout == 'start':
        data_file = 'nTurbs%i_spacing5_layout_0_start.txt' % (turbs)
        plot_data = np.loadtxt(data_directory + data_file)

        # parse data
        turbineX = (plot_data[:, 0])*rotor_diameter
        turbineY = (plot_data[:, 1])*rotor_diameter

    elif layout == 'finish':

        data_file = 'nTurbs%i_finish.txt' % (turbs)
        plot_data = np.loadtxt(data_directory + data_file)

        # parse data
        turbineX = (plot_data[:, 2])
        turbineY = (plot_data[:, 3])

    else:
        raise ValueError('incorrect layout specified')

    # create figure and axes
    fig, ax = plt.subplots()

    if turbs == 16:
        bmin = 0.0
        bmax = 16.0
        # plt.plot([bmin, bmin, bmax, bmax, bmin], [bmin, bmax, bmax, bmin, bmin], '-b')

        bmin += 0.5
        bmax -= 0.5
        plt.plot([bmin, bmin, bmax, bmax, bmin], [bmin, bmax, bmax, bmin, bmin], '--', color=colors[1])

    elif turbs == 38:

        # define wind farm area
        boundary_center_x = 80.0*2000./126.4 - 40.0
        boundary_center_y = 80.0*2000./126.4 - 40.0
        boundary_radius = 80.0*(2000.0)/126.4

        # boundary_circle = plt.Circle((boundary_center_x/rotor_diameter, boundary_center_y/rotor_diameter),
        #                              boundary_radius/rotor_diameter, facecolor='none', edgecolor='b', linestyle='-')
        constraint_circle = plt.Circle((boundary_center_x / rotor_diameter, boundary_center_y / rotor_diameter),
                                     boundary_radius / rotor_diameter - 0.5, facecolor='none', edgecolor=colors[1], linestyle='--')

        # ax.add_patch(boundary_circle)
        ax.add_patch(constraint_circle)

    elif turbs == 60.0:

        from plantenergy.GeneralWindFarmComponents import calculate_boundary
        from shapely.geometry import LineString

        boundaryVertices, boundaryNormals = calculate_boundary(plot_data)
        boundaryVertices = np.concatenate([boundaryVertices, [boundaryVertices[0]]])
        constraint = LineString(boundaryVertices)
        boundary = constraint.parallel_offset(0.5, 'right', join_style=2)

        def plot_line(ax, ob, color='r', style="-"):
            parts = hasattr(ob, 'geoms') and ob or [ob]
            for part in parts:
                x, y = part.xy
                ax.plot(x, y, style, color=color, solid_capstyle='round', zorder=1)

        plot_line(ax, constraint, color=colors[1], style="--")
        # plot_line(ax, boundary, color='b')

        # plt.plot(boundaryVertices[:, 0], boundaryVertices[:, 1], 'r', linestyle=(10, (5, 1)))
        # plt.plot([boundaryVertices[0,0], boundaryVertices[-1, 0]], [boundaryVertices[0, 1], boundaryVertices[-1, 1]], 'r--')

    nTurbines = turbineX.size

    # create and add domain boundary
    # les_domain = plt.Rectangle([0., 0.], 5000., 5000., facecolor='none', edgecolor='b', linestyle=':', label='Domain')
    # ax.add_patch(les_domain)

    # create and add wind farm boundary

    # create and add wind turbines
    for x, y in zip(turbineX/rotor_diameter, turbineY/rotor_diameter):
        circle_start = plt.Circle((x, y), 1/2., facecolor='none', edgecolor='k', linestyle='-', label='Start')
        ax.add_artist(circle_start)

    if turb_nums:
        for i in np.arange(nTurbines):
            ax.annotate(i, (turbineX[i]/rotor_diameter+1.0/2., turbineY[i]/rotor_diameter+1.0/2.))

    # pretty the plot
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.yaxis.set_ticks_position('left')
    # ax.xaxis.set_ticks_position('bottom')

    # if turbs == 60.0:
    plt.axis("equal")
    #     plt.xticks([min(turbineX) / rotor_diameter, max(turbineX) / rotor_diameter])
    #     plt.yticks([min(turbineY) / rotor_diameter, max(turbineY) / rotor_diameter])
    # elif turbs == 38:
    #     plt.axis('square')
    #     plt.xticks([(boundary_center_x - boundary_radius)/rotor_diameter, (boundary_center_x + boundary_radius)/rotor_diameter])
    #     plt.yticks([(boundary_center_x - boundary_radius)/rotor_diameter, (boundary_center_x + boundary_radius)/rotor_diameter])

    # ax.set_xlabel('Turbine X Position ($x/D_r$)')
    # ax.set_ylabel('Turbine Y Position ($y/D_r$)')
    # ax.set_xlim([xmin, xmax])
    # ax.set_ylim([ymin, ymax])

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)
    if show_figs:
        plt.show()

def plot_smoothing_visualization_w_wec_wo_wec(filename, save_figs, show_figs, wec_method="D", wake_model="BPA"):
    # from mpltools import color
    # load data
    if wake_model == "BPA":
        data = np.loadtxt("./image_data/smoothing_bpa_WEC-%s.txt" %wec_method)
        if wec_method == "A":
            wec_values = np.array([1, 3.0, 5.0, 7.0, 9.0])
            xt = [-1.6, -1.45, -2.]
            yt = [31.5, 25.25, 23]

        elif wec_method == "D":
            wec_values = np.array([1, 1.5, 2.0, 2.5, 3.0])
            xt = [-1.6, -1.5, -2.75]
            yt = [31.5, 24.5, 22.25]

        elif wec_method == "H":
            wec_values = np.array([1, 1.5, 2.0, 2.5, 3.0])
            xt = [-1.6, -1.35, -2.25]
            yt = [31.5, 25, 22.5]
    elif wake_model == "JENSEN":
        data = np.loadtxt("./image_data/smoothing_jensen_WEC-%s.txt" % wec_method)
        if wec_method == "D":
            wec_values = np.array([1, 1.5, 2.0, 2.5, 3.0])
            xt = [-1.6, -1.6, -1.6]
            yt = [30.85, 29.7, 28]
    else:
        ValueError("Invalid model selection")

    location = data[:, 0]

    fig, ax = plt.subplots(1)

    # Change color cycle specifically for `ax2`
    # color.cycle_cmap(len(wec_values), cmap='Blues, ax=ax)
    # colors = plt.cm.winter(np.linspace(0.2, 0.8, 3))
    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]
    
    # colors = ['k', 'b', 'r', 'c', 'g']


    plot_vals = np.arange(1, len(wec_values)+1, 2)
    print(wec_values)
    print(plot_vals)
    for i in np.arange(0, len(plot_vals)):
        print(wec_values[plot_vals[i]-1])
        ax.plot(location, data[:, plot_vals[i]]/1E6, color=colors[i], linestyle=linetypes[i])
        if wec_method == "A":
            text_label = r"$\theta_\xi$ = %.1f" % wec_values[plot_vals[i] - 1]
        else:
            text_label = r"$\xi$ = %.1f" %wec_values[plot_vals[i]-1]
        plt.text(xt[i], yt[i], text_label, color=colors[i], fontsize=14)
    # xi = 1
    # plt.text(-1., data[location==0, 1]/1E6+0.25, "No WEC", color=colors[0])
    # xi = 4
    # plt.text(-1.75, data[location==0, 4]/1E6+0.25, "Moderate WEC", color=colors[1])
    # # xi = 5
    # # plt.text(-1, data[location==0, xi]/1E6+0.5, "$\\xi = %i$" % xi, color=colors[2])
    # xi = 7
    # plt.text(-1, data[location==0, 6]/1E6-.25, "High WEC", color=colors[2])

    ax.set_xlabel("Downstream Turbine's \n Cross-wind Offset ($\Delta y/d$)")
    ax.set_ylabel('Annual Energy Production (GWh)')
    if wake_model == "BPA":
        ax.set_ylim([20, 35])
        ax.set_xlim([-4, 4])
        plt.yticks([20, 35])
        plt.xticks([-4, 0, 4])
    elif wake_model == "JENSEN":
        ax.set_ylim([27, 34])
        ax.set_xlim([-4, 4])
        plt.yticks([27, 34])
        plt.xticks([-4, 0, 4])
    # ax.legend(ncol=2, loc=2, frameon=False, )  # show plot
    # tick_spacing = 1
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')

    #
    plt.tight_layout()
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_smoothing_visualization(filename, save_figs, show_figs):

    # load data
    data = np.loadtxt("./image_data/smoothing_initial_test.txt")

    location = data[:, 0]

    fig, ax = plt.subplots(1)

    for i in np.arange(1, 8):
        ax.plot(location, data[:, i]/1E6, label="$\\xi = %i$" % i)

    ax.set_xlabel("Downstream Turbine's Crosswind Location ($X/D_r$)")
    ax.set_ylabel('AEP (GWh)')
    # ax.set_xlim([10, 20])
    ax.set_ylim([10, 23])
    ax.legend(ncol=3, loc=2, frameon=False, )  # show plot
    # tick_spacing = 1
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tick_params(top='off', right='off')
    #
    plt.tight_layout()
    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_wec_methods(filename, save_figs, show_figs):

    def x0_func(d, gamma, ct, alpha_star, beta_star, I):
        num = d * np.cos(gamma) * (1. + np.sqrt(1 - ct))
        den = (np.sqrt(2.) * (alpha_star * I + beta_star * (1. - np.sqrt(1 - ct))))
        x0 = num / den
        return x0

    def xd_func(x0, d, ky, kz, gamma, ct):
        root_term = np.sqrt((ky + kz * np.cos(gamma)) ** 2 - 4. * ky * kz * (ct - 1.) * np.cos(gamma))
        num = ky + kz * np.cos(gamma) - root_term
        den = 2. * ky * kz * np.sqrt(8.)
        xd = x0 + d * num / den
        return xd

    def spread_func(x, x0, xd, d, ky, kz, gamma):
        sigmay = np.zeros_like(x)
        sigmaz = np.zeros_like(x)
        i = 0
        sigmay0 = d * np.cos(gamma) / np.sqrt(8.)
        sigmaz0 = d * np.cos(gamma) / np.sqrt(8.)

        sigmayd = ky * (xd - x0) + d * np.cos(gamma) / np.sqrt(8.)
        sigmazd = kz * (xd - x0) + d / np.sqrt(8.)
        for xx in x:
            if x[i] > x0:
                sigmay[i] = ky * (x[i] - x0) + d * np.cos(gamma) / np.sqrt(8.)
                sigmaz[i] = kz * (x[i] - x0) + d / np.sqrt(8.)
            else:
                sigmay[i] = (x[i] / x0) * (sigmay0 - sigmayd) + sigmayd
                sigmaz[i] = (x[i] / x0) * (sigmaz0 - sigmazd) + sigmazd
            i += 1
        return sigmay, sigmaz

    def spread_func_original_wec(x, x0, xd, d, ky, kz, gamma, wec_factor):
        sigmay = np.zeros_like(x)
        sigmaz = np.zeros_like(x)
        i = 0
        sigmay0 = d * np.cos(gamma) / np.sqrt(8.)
        sigmaz0 = d * np.cos(gamma) / np.sqrt(8.)

        sigmayd = ky * (xd - x0) + d * np.cos(gamma) / np.sqrt(8.)
        sigmazd = kz * (xd - x0) + d / np.sqrt(8.)

        for xx in x:
            if x[i] > x0:
                sigmay[i] = ky * (x[i] - x0) + d * np.cos(gamma) / np.sqrt(8.)
                sigmaz[i] = kz * (x[i] - x0) + d / np.sqrt(8.)
            else:
                sigmay[i] = (x[i] / x0) * (sigmay0 - sigmayd) + sigmayd
                sigmaz[i] = (x[i] / x0) * (sigmaz0 - sigmazd) + sigmazd
            i += 1
        return wec_factor * sigmay, wec_factor * sigmaz

    def spread_func_wec_angle_test(x, x0, xd, d, ky, kz, gamma, wec_angle):
        sigmay = np.zeros_like(x)
        sigmaz = np.zeros_like(x)
        i = 0
        sigmay0_orig = d*np.cos(gamma)/np.sqrt(8.)
        sigmaz0_orig = d * np.cos(gamma) / np.sqrt(8.)

        sigmayd = ky*(xd-x0)+d*np.cos(gamma)/np.sqrt(8.)
        sigmazd = kz * (xd - x0) + d / np.sqrt(8.)

        theta_k_near_wake = wec_angle * np.pi / 180.0
        k_spread = np.tan(theta_k_near_wake)
        ky_near_wake = (sigmay0_orig - sigmayd) / x0

        if k_spread > ky_near_wake:
            ky_near_wake = k_spread

        sigmay0_new = ky_near_wake * x0 + sigmayd
        sigmaz0 = d * np.cos(gamma) / np.sqrt(8.)

        for xx in x:
            if x[i] > x0:
                if ky > ky_near_wake:
                    sigmay[i] = ky * (x[i] - x0) + sigmay0_new
                else:
                    sigmay[i] = ky_near_wake * (x[i] - x0) + sigmay0_new
                sigmaz[i] = kz * (x[i] - x0) + d / np.sqrt(8.)
            else:
                sigmay[i] = ky_near_wake * x[i] + sigmazd
                sigmaz[i] = (x[i] / x0) * (sigmaz0 - sigmazd) + sigmazd
            i += 1
        return sigmay, sigmaz

    def spread_func_wech(x, x0, xd, d, ky, kz, gamma, wec_factor):
        sigmay = np.zeros_like(x)
        sigmaz = np.zeros_like(x)
        i = 0
        sigmay0 = d * np.cos(gamma) / np.sqrt(8.)
        sigmaz0 = d / np.sqrt(8.)

        sigmay0WEC = wec_factor * d * np.cos(gamma) / np.sqrt(8.)
        sigmaz0WEC = wec_factor * d / np.sqrt(8.)

        for xx in x:
            if x[i] > x0:
                sigmay[i] = wec_factor * (ky * (x[i] - x0) + d * np.cos(gamma) / np.sqrt(8.))
                sigmaz[i] = wec_factor * (kz * (x[i] - x0) + d / np.sqrt(8.))
            else:
                sigmay[i] = ((sigmay0WEC - sigmay0) / (x0)) * x[i] + sigmay0
                sigmaz[i] = ((sigmaz0WEC - sigmaz0) / (x0)) * x[i] + sigmaz0
            i += 1
        return sigmay, sigmaz

    I = 0.1  # ambient turbulence intensity
    u_inf = 10  # inflow velocity (m/s)
    ky = 0.3871 * I + 0.003678
    kz = 0.3871 * I + 0.003678

    d = 80.0  # rotor diameter
    ct = 0.8  # thrust coefficient
    gamma = 0  # yaw angle

    beta_star = 0.154
    alpha_star = 2.32

    wec_angle = 6
    wec_factor_d = 4
    wec_factor_h = 3

    turbine_color = "k"

    # end of near wake
    x0 = x0_func(d, gamma, ct, alpha_star, beta_star, I)

    # discontinuity point
    xd = xd_func(x0, d, ky, kz, gamma, ct)

    # plot results
    x = np.arange(0, 8 * d, 10)

    sigmay_original, sigmaz_original = spread_func(x, x0, xd, d, ky, kz, gamma)

    sigmay_a, sigmaz_a = spread_func_wec_angle_test(x, x0, xd, d, ky, kz, gamma, wec_angle)

    sigmay_d, sigmaz_d = spread_func_original_wec(x, x0, xd, d, ky, kz, gamma, wec_factor_d)

    sigmay_h, sigmaz_h = spread_func_wech(x, x0, xd, d, ky, kz, gamma, wec_factor_h)
    
    sigma_scaler = 1.5
    sigmay_original *= sigma_scaler
    sigmay_a *= sigma_scaler
    sigmay_d *= sigma_scaler
    sigmay_h *= sigma_scaler

    # plot
    fig, ax = plt.subplots(1)

    colors = ["#F5793A", "#0F2080", "#85C0F9", "#BDB8AD", "#A95AA1", "#382119"]
    line1 = ax.plot(x / d, sigmay_original / d, colors[3])
    line2 = ax.plot(x / d, -sigmay_original / d, colors[3])
    line3 = ax.plot(x / d, np.zeros_like(x), '--', color=colors[3], zorder=0)
    ax.text(3, 0.3*sigma_scaler, 'Original wake',
             verticalalignment='top', horizontalalignment='left',
             color=colors[3], fontsize=15)

    line4 = ax.plot(x / d, sigmay_a / d, colors[0])
    line5 = ax.plot(x / d, -sigmay_a / d, colors[0])
    ax.text(3., 0.72*sigma_scaler, 'WEC-A',
             verticalalignment='bottom', horizontalalignment='left',
             color=colors[0], fontsize=15)

    line6 = ax.plot(x / d, sigmay_d / d, colors[1])
    line7 = ax.plot(x / d, -sigmay_d / d, colors[1])
    ax.text(1, 1.4*sigma_scaler, 'WEC-D',
             verticalalignment='bottom', horizontalalignment='left',
             color=colors[1], fontsize=15)

    line8 = ax.plot(x / d, sigmay_h / d, colors[2])
    line9 = ax.plot(x / d, -sigmay_h / d, colors[2])
    ax.text(1, 0.8*sigma_scaler, 'WEC-H',
             verticalalignment='bottom', horizontalalignment='left',
             color=colors[2], fontsize=15)

    #  plot turbine
    blade1 = Ellipse((0.0, 0.25), 0.1, 0.5, 0.0, visible=True, fill=True, ec="none", fc=turbine_color)
    blade2 = Ellipse((0.0, -0.25), 0.1, 0.5, 0.0, visible=True, fill=True, ec="none", fc=turbine_color)
    hub = Ellipse((0.0,0.0), 0.2, 0.1, visible=True, fill=True, ec="none", fc=turbine_color)
    nacelle = Rectangle((0.0,-0.05), 0.1, 0.1, visible=True, fill=True, ec="none", fc=turbine_color, joinstyle='round')
    ax.add_artist(blade1)
    ax.add_artist(blade2)
    ax.add_artist(hub)
    ax.add_artist(nacelle)

    plt.xlabel('Downwind distance ($\Delta x/d$)')
    plt.ylabel('Crosswind distance ($\Delta y/d$)')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.xticks([0,4, 8])
    plt.yticks([-2,0,2])

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_ct_curve(filename, save_figs, show_figs):

    data = np.loadtxt("../project-code/input_files/mfg_ct_vestas_v80_niayifar2016.txt", delimiter=",")

    fig, ax = plt.subplots(1)

    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]

    plt.plot(data[:,0], data[:,1], 'o', mfc="none", mec=colors[2])


    plt.xticks([0, 5, 10, 15, 20])
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])

    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Thrust Coefficient')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_cp_curve(filename, save_figs, show_figs):
    air_density = 1.225
    rotor_diameter = 80.0
    Ar = 0.25 * np.pi * rotor_diameter ** 2
    data = np.loadtxt("../project-code/input_files/niayifar_vestas_v80_power_curve_observed.txt", delimiter=",")
    data[:,1] *= (1E6) / (0.5 * air_density * data[:, 0] ** 3 * Ar)
    fig, ax = plt.subplots(1)

    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]

    plt.plot(data[:,0], data[:,1], 'o', mfc="none", mec=colors[2])

    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Power Coefficient')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xticks([0, 5, 10, 15, 20])
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])

    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    plt.tight_layout()


    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return


def plot_simple_design_space(filename, save_figs, show_figs):
    
    turbine_y = -np.array([0.0, 3.0, 7.0])
    turbine_x = np.array([-1.0, 1.0, 0.0])
    diameter = 1.0

    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]

    fig, ax = plt.subplots(1, figsize=(5, 6))

    # show downstream turbine movement
    steps = 5
    alphas = np.linspace(0.9, 0.5, steps)
    locs = np.linspace(min(turbine_x)-3.0, turbine_x[2], steps)
    for i in np.arange(0, steps-1):
        blade1 = Ellipse((locs[i]+diameter/4, turbine_y[2]), diameter / 2, diameter/12, facecolor='%f' %(alphas[i]), edgecolor='none', fill=True,
                            alpha=1.0, linestyle='-', visible=True)
        blade2 = Ellipse((locs[i]-diameter/4, turbine_y[2]), diameter / 2, diameter / 12, facecolor='%f' %(alphas[i]), edgecolor='none', fill=True,
                         alpha=1.0, linestyle='-', visible=True)
        hub = Rectangle((locs[i] - diameter / 16, turbine_y[2]-diameter/8), diameter / 8, diameter / 4, facecolor='%f' %(alphas[i]),
                         edgecolor='none', fill=True, alpha=1.0, linestyle='-', visible=True, joinstyle='round')
        clip1 = Rectangle((locs[i] +1/16.0 , turbine_y[2] - diameter / 8), diameter, diameter / 4,
                          facecolor='none',
                          edgecolor='none', fill=True, alpha=alphas[i], linestyle='-', visible=True, joinstyle='round')
        clip2 = Rectangle((locs[i] - diameter * 17 / 16, turbine_y[2] - diameter / 8), diameter, diameter / 4,
                        facecolor='none',
                        edgecolor='none', fill=True, alpha=alphas[i], linestyle='-', visible=False, joinstyle='round')
        ax.add_artist(blade1)
        ax.add_artist(blade2)
        ax.add_artist(hub)
        ax.add_artist(clip1)
        ax.add_artist(clip2)
        blade1.set_clip_path(clip1)
        blade2.set_clip_path(clip2)

    tc = 'k'
    # plot turbine locations
    for i in np.arange(0, 3):

        # plt.plot([turbine_x[i]-0.5, turbine_x[i]-1.5], [turbine_y[i], turbine_y[i]-9.0], ':k', alpha=0.25)
        # plt.plot([turbine_x[i]+0.5, turbine_x[i]+1.5], [turbine_y[i], turbine_y[i]-9.0], ':k', alpha=0.25)
        wake = Polygon(np.array([[turbine_x[i]-0.5, turbine_y[i]],
                                 [turbine_x[i]-1.5, turbine_y[i]-9.0],
                                 [turbine_x[i]+1.5, turbine_y[i]-9.0],
                                 [turbine_x[i]+0.5, turbine_y[i]]]), color=colors[1], alpha=0.2, closed=True)
        ax.add_artist(wake)

        blade1 = Ellipse((turbine_x[i]+diameter/4, turbine_y[i]), diameter / 2, diameter / 12, facecolor=tc, edgecolor='none', fill=True,
                         alpha=1.0, linestyle='-', visible=True)
        blade2 = Ellipse((turbine_x[i] - diameter / 4, turbine_y[i]), diameter / 2, diameter / 12, facecolor=tc,
                         edgecolor='none', fill=True,
                         alpha=1.0, linestyle='-', visible=True)
        hub = Rectangle((turbine_x[i]-diameter/16, turbine_y[i] - diameter / 8), diameter / 8, diameter / 4,
                        facecolor=tc,
                        edgecolor='none', fill=True, alpha=1.0, linestyle='-', visible=True, joinstyle='round')
        ax.add_artist(blade1)
        ax.add_artist(blade2)
        ax.add_artist(hub)

    # add arrow to indicate movement
    plt.arrow(turbine_x[2]+.75, turbine_y[2], 1.5, 0.0, width=0.05, color='k', fc='k', ec='k')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    plt.xlabel("$\Delta y/d$")

    plt.xticks([-4.0, 0.0, 4.0])
    plt.yticks([])

    plt.axis("equal")
    plt.ylim([-10.0, 5.0])
    plt.xlim([-5.0, 5.0])

    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('bottom')
    #
    plt.tight_layout()


    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return


def plot_jensen_diagram(filename, save_figs, show_figs):
    from matplotlib.patches import Ellipse, Rectangle, Polygon, Circle

    # define variables
    r0 = 0.5
    dx = 4.0
    dy = -1.0
    beta = 20.0*np.pi/180.0
    z = r0/np.tan(beta)
    theta = np.arctan(dy/(dx+z))
    n = np.pi/beta
    r = (dx+z)*np.tan(beta)

    # define colors
    constructionline_color = 'k'
    wakeline_color = 'b'
    turbine_color = 'k'

    # initialize the figure
    fig, ax = plt.subplots(1, figsize=(9,7))

    # plot centerline
    ax.plot([-z, dx+1.0], [0.0, 0.0], '-.', color=constructionline_color, alpha=0.5)

    # plot lines from fulcrum to blade tips
    ax.plot([-z, 0.0], [0.0, 0.5], '--', color=constructionline_color, alpha=0.5)
    ax.plot([-z, 0.0], [0.0, -0.5], '--', color=constructionline_color, alpha=0.5)

    # plot wake
    wake = Polygon(np.array([[0.0, 0.5],
                             [dx+1.0, (dx+z+1.0)*np.tan(beta)],
                             [dx+1.0, -(dx+z+1.0)*np.tan(beta)],
                             [0.0, -0.5]]), color='b', alpha=0.05, closed=True)
    ax.add_artist(wake)

    # plot position and position lines
    ax.plot([-z, dx], [0.0, dy], ':', color=constructionline_color, alpha=0.5)
    ax.plot([dx, dx], [r, -r], ':', color=constructionline_color, alpha=0.5)
    location = Circle((dx, dy), 0.05, color=turbine_color)
    ax.add_artist(location)


    # plot turbine
    blade1 = Ellipse((0.0, 0.25), 0.1, 0.5, 0.0, visible=True, fill=True, ec="none", fc=turbine_color)
    blade2 = Ellipse((0.0, -0.25), 0.1, 0.5, 0.0, visible=True, fill=True, ec="none", fc=turbine_color)
    hub = Ellipse((0.0,0.0), 0.2, 0.1, visible=True, fill=True, ec="none", fc=turbine_color)
    nacelle = Rectangle((0.0,-0.05), 0.1, 0.1, visible=True, fill=True, ec="none", fc=turbine_color, joinstyle='round')
    ax.add_artist(blade1)
    ax.add_artist(blade2)
    ax.add_artist(hub)
    ax.add_artist(nacelle)

    # annotate
    def annotate_dim(ax, xyfrom, xyto, text=None, text_buffer=0.05):

        if text is None:
            text = str(np.sqrt((xyfrom[0] - xyto[0]) ** 2 + (xyfrom[1] - xyto[1]) ** 2))

        ax.annotate("", xyfrom, xyto, arrowprops=dict(arrowstyle='<->'))
        ax.text((xyto[0] + xyfrom[0]) / 2, (xyto[1] + xyfrom[1]) / 2 + text_buffer, text, fontsize=16)

    def annotate_dim2(ax, xyfrom, xyto, text=None, text_buffer=0.05, line_buffer=0.05, dir_type='x', cap_length=0.1,
                      cap_buffer=0.05, cap_on=[True, True], arc_radius=0.25, angle_text_buffer =4):

        if text is None:
            text = str(np.sqrt((xyfrom[0] - xyto[0]) ** 2 + (xyfrom[1] - xyto[1]) ** 2))


        if dir_type == 'x':
            x = np.array([xyfrom[0], xyto[0]])
            y = np.array([xyfrom[1], xyto[1]])
            y[:] = np.max(y)

            # dimension line
            ax.annotate("", [x[0],y[0]+line_buffer+cap_length/2], [x[1],y[1]+line_buffer+cap_length/2], arrowprops=dict(arrowstyle='<|-|>', color='k'))

            # extension lines
            if cap_on[0]:
                ax.plot([xyfrom[0], xyfrom[0]], [xyfrom[1]+cap_buffer, xyto[1] + line_buffer+cap_length], 'k', linewidth=1.0)
            if cap_on[1]:
                ax.plot([xyto[0], xyto[0]], [xyto[1]+cap_buffer, xyto[1] + line_buffer+cap_length], 'k', linewidth=1.0)

            # text
            ax.text((x[0] + x[1]) / 2, (y[0] + y[1]) / 2 + text_buffer + line_buffer + cap_length/2, text, fontsize=16)

        if dir_type == 'y':
            x = np.array([xyfrom[0], xyto[0]])
            y = np.array([xyfrom[1], xyto[1]])
            x[:] = np.max(x)

            # dimension line
            ax.annotate("", [x[0] + line_buffer + cap_length / 2, y[0]], [x[1]+ line_buffer + cap_length / 2, y[1] ],
                        arrowprops=dict(arrowstyle='<|-|>', color='k'))

            # extension caps
            if cap_on[0]:
                ax.plot([xyfrom[0] + cap_buffer, xyfrom[0] + line_buffer + cap_length ], [xyfrom[1] , xyfrom[1] ], 'k',
                    linewidth=1.0)
            if cap_on[1]:
                ax.plot([xyto[0] + cap_buffer, xyto[0]+ line_buffer + cap_length], [xyto[1] , xyto[1] ], 'k', linewidth=1.0)

            # text
            ax.text((x[0] + x[1]) / 2 + text_buffer + line_buffer + cap_length / 2, (y[0] + y[1]) / 2 , text,
                    fontsize=16)

        if dir_type == 'angle':
            from matplotlib.patches import Arc

            # parse input
            center_point = xyfrom
            arc_start = xyto[0]
            arc_end = xyto[1]

            # draw arc
            arc = Arc(center_point, arc_radius, arc_radius, angle=0.0, theta1=arc_start, theta2=arc_end)
            ax.add_artist(arc)

            # add text
            text_angle = np.pi*(arc_start - angle_text_buffer + (arc_end - arc_start)/2.0)/180.0
            xt = (arc_radius + text_buffer -0.9)*np.cos(text_angle) + center_point[0]
            yt = (arc_radius + text_buffer -0.9)*np.sin(text_angle) + center_point[1]
            ax.text(xt, yt, text, fontsize=16)


    # add dimensions
    annotate_dim2(ax, [-z, 0.0], [0.0, 0.5], "$z$")
    annotate_dim2(ax, [0.0, 0.5], [dx, 0.5], "$\Delta x$", cap_on=[True, False])
    annotate_dim2(ax, [dx, 0.0], [dx, r], "$r$", dir_type='y', cap_on=[False, True], line_buffer=0.1, cap_buffer=0.05)
    annotate_dim2(ax, [0.0, 0.0], [0.0, r0], "$r_0$", dir_type='y', cap_on=[False, True], line_buffer=0.1, cap_buffer=0.05)
    annotate_dim2(ax, [dx, 0.0], [dx, dy], r"$\Delta y$", dir_type='y', cap_on=[False, True], line_buffer=0.1, cap_buffer=0.1)
    annotate_dim2(ax, [-z, 0.0], [theta*180.0/np.pi, 0.0], r"$\theta$", dir_type='angle', arc_radius=2.0, text_buffer=0.0)
    annotate_dim2(ax, [-z, 0.0], [0.0, beta*180.0/np.pi], r"$\beta$", dir_type='angle', arc_radius=1.5, text_buffer=0.2)

    plt.xticks([])
    plt.yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)\

    plt.axis("equal")
    plt.ylim([-r-1.5, r+1.5])
    plt.xlim([-z-1.0, dx+1])

    ax.yaxis.set_ticks_position('none')
    ax.xaxis.set_ticks_position('none')
    #
    plt.tight_layout()


    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return

def plot_jensen_profiles(filename, save_figs, show_figs):

    jcsdata = np.loadtxt("./image_data/wake-model-visualization-data/model-profile-jensen-CosineFortran.txt")
    jthdata = np.loadtxt("./image_data/wake-model-visualization-data/model-profile-jensen-TopHat.txt")

    colors = ["#0F2080", "#85C0F9", "#F5793A"]
    lines = ["-", "--"]

    fig, ax = plt.subplots(1, figsize=(3,5))

    maxspeed = np.max(jcsdata[:,2])

    ax.plot(100*(maxspeed - jthdata[:,2])/maxspeed, jthdata[:,1]/40, linestyle=lines[1], color=colors[1])
    ax.annotate("Top Hat", (11, 1.4), ha='center', va='center', color=colors[1])
    
    ax.plot(100*(maxspeed - jcsdata[:,2])/maxspeed, jcsdata[:,1]/40, linestyle=lines[0], color=colors[0])
    ax.annotate("Cosine", (5.6, 0.8), ha='center', va='center', color=colors[0])

    ax.set_ylim([-3, 3])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    plt.yticks(np.array([-3, 0, 3]))
    plt.xticks(np.array([0, 5, 10, 15]))

    plt.ylabel(r"Offset ($\Delta y/d$)")
    plt.xlabel("Wake Deficit (%)")

    plt.tight_layout()

    if save_figs:
        plt.savefig(filename, transparent=True)

    if show_figs:
        plt.show()

    return


def plot_convergence_history(filename="", save_figs=False, show_figs=True, nturbs=38, ndirs=12, wakemodel="BPA", logplot=False):

    # indicate how many optimization runs are to be plotted
    runs = 200

    labels = ["SNOPT+WEC", 'SNOPT', "ALPSO"]
    colors = ["#0F2080", "#85C0F9", "#F5793A"]
    alpha = 0.08
    markeralpha = 0.5

    if wakemodel == "BPA":
        if nturbs == 60:
            date = 20200824
            aept = 6653047.52233728*nturbs*1E3 #Wh
            psscale = -1E5
        elif nturbs == 38:
            date = 20200821
            if ndirs == 12:
                labels = ["SNOPT+WEC", 'SNOPT', "ALPSO", "ALPSO+WEC"]
                colors = ["#0F2080", "#85C0F9", "#F5793A", "#A95AA1"]
                aept = 4994091.77684705*nturbs*1E3 #Wh
                psscale = -1E5
                pswscale = 1E0
            elif ndirs == 36:
                aept = 1630166.61601323*nturbs*1E3 # Wh
                psscale = -1E5
        elif nturbs == 16:
            date = 20200821
            aept = 5191363.5933961*nturbs*1E3 # Wh
            psscale = -1E4
        base_input_directory = "./image_data/opt_results/%i-%i-turbs-%i-dir-fcall-and-conv-history/" % (date, nturbs, ndirs)
        ps_input_directory = "./image_data/opt_results/202101042132-alpso-runs-random-seed/"
    elif wakemodel == "JENSEN":
        if nturbs == 38:
            date = 20201110
            if ndirs == 12:
                aept = 5679986.827947*nturbs*1E3 #Wh
                psscale = 1E5
            else:
                raise(EnvironmentError("Invalid Model and Case combination"))
        else:
            raise(EnvironmentError("Invalid Model and Case combination"))
        base_input_directory = "./image_data/opt_results/%i-jensen-%i-turbs-%i-dir-fcal-and-conv-history/" % (date, nturbs, ndirs)
        ps_input_directory = base_input_directory
    else:
        raise(EnvironmentError("Invalid Model and Case combination"))
    # print(aept)
    # Define input location
    
    input_directory_wec = base_input_directory + "snopt_wec_diam_max_wec_3_nsteps_6.000/"
    input_directory_snopt = base_input_directory + "snopt/"
    input_directory_ps = ps_input_directory + "ps/"
    input_directory_pswec = ps_input_directory + "pswec/"

    # Specify output file name
    input_file_wec = input_directory_wec + "convergence_histories.txt"
    input_file_snopt = input_directory_snopt + "convergence_histories.txt"
    input_file_ps = input_directory_ps + "convergence_histories_%iturbs_%idirs.txt" %(nturbs, ndirs)
    input_file_pswec = input_directory_pswec + "convergence_histories.txt"
    
    # store initial AEP values
    aepinit = np.zeros(runs)
    aepinitdata = np.zeros(runs)
    aepfinaldata = np.zeros(runs)
    fcallsdata = np.zeros(runs)

    # initalize plot
    fig1, ax1 = plt.subplots(1)
    # print("initialization complete")

    # find how many entries are in the longest SNOPT convergence history
    f = open(input_file_snopt)
    maxlength = 0
    rownum = -1
    for row in f.readlines():
        if rownum < 0:
            rownum += 1
            continue
        data = np.fromstring(row, sep=" ")
        if data.size > maxlength:
            maxlength = data.size
    f.close()

    aepinitdata[:] = 0.0
    aepfinaldata[:] = 0.0
    fcallsdata[:] = 0.0
    
    # extract SNOPT convergence histories to a data frame
    rownum = -1
    run = 0
    f = open(input_file_snopt)
    for row in f.readlines():
        if rownum < 0:
            rownum += 1
            continue

        data = np.fromstring(row, sep=" ")
        # print(data.size)
        if rownum % 2 == 0:
            # dfcalc.(run, run, pd.Series(data, name=rownum))
            s = pd.Series(data, name=rownum)
        else:
            s = pd.Series(data, name=rownum)
            aepinit[run] = s[0]
            aepinitdata[run] = s.iloc[0]
            aepfinaldata[run] = s.iloc[-1]
            fcallsdata[run] = (s.size)*2
            run += 1

            loss = 100*(1-s/aept)
            functioncalls = np.arange(1, s.size+1)*2
            functioncalls[0] = 1
            if logplot:
                ax1.semilogx(functioncalls, 100*(1-s/aept), alpha=alpha, color=colors[1], zorder=1)
            else:
                ax1.plot(functioncalls, 100*(1-s/aept), alpha=alpha, color=colors[1], zorder=1)

            ax1.scatter(s.size*2, 100*(1 - s.iloc[-1] / aept), marker='o', edgecolor='k', color=colors[1], zorder=10, alpha=markeralpha)
            
        rownum += 1
    f.close()

    np.savetxt("snopt_results_%smodel_%iturbs_%idirs.txt" %(model, nturbs, ndirs), np.c_[np.arange(0,runs), aepinitdata, aepfinaldata, fcallsdata], header="snopt results: id, AEP init (Whr), AEP final (Whr), fcalls total")
    

    # print("snopt complete")

    # find how many entries are in the longest WEC convergence history
    f = open(input_file_wec)
    maxlength = 0
    rownum = -1
    for row in f.readlines():
        if rownum < 0:
            rownum += 1
            continue
        data = np.fromstring(row, sep=" ")
        if data.size > maxlength:
            maxlength = data.size
    f.close()

    # extract WEC convergence histories to a data frame
    rownum = -1
    run = 0
    f = open(input_file_wec)
    for row in f.readlines():
        if rownum < 0:
            rownum += 1
            continue

        data = np.fromstring(row, sep=" ")
        if rownum % 2 == 0:
            s = pd.Series(data, name=rownum)
        else:
            s = pd.Series(data, name=rownum)
            functioncalls = np.arange(1, s.size+1)*2
            functioncalls[0] = 1
            if logplot:
                ax1.semilogx(functioncalls, 100*(1-s/aept), alpha=alpha, color=colors[0], zorder=1)
            else:
                ax1.plot(functioncalls, 100*(1-s/aept), alpha=alpha, color=colors[0], zorder=1)
            ax1.scatter(s.size*2, 100*(1-s.iloc[-1]/aept), marker='o', edgecolor='k', color=colors[0], zorder=10, alpha=markeralpha)
            
            # save key data for file
            aepinitdata[run] = s.iloc[0]
            aepfinaldata[run] = s.iloc[-1]
            fcallsdata[run] = (s.size)*2

            run += 1

        rownum += 1
    f.close()

    # np.savetxt("snopt_wec_results_%smodel_%iturbs_%idirs.txt" %(model, nturbs, ndirs), np.c_[np.arange(0,runs), aepinitdata, aepfinaldata, fcallsdata], header="snopt wec results: id, AEP init (Whr), AEP final (Whr), fcalls total")
    
    # print("WEC complete")

    
    if wakemodel == "BPA" and ndirs == 12:
        #  find how many entries are in the longest ALPSO+WEC convergence history
        f = open(input_file_pswec)
        maxlength = 0
        rownum = 0
        maxcalls = 0
        for row in f.readlines():
            if rownum < 1:
                rownum += 1
                continue

            data = np.fromstring(row, sep=" ")
            if rownum % 2 != 0:
                datamaxcalls = data[-1]
                if datamaxcalls > maxcalls:
                    maxcalls = datamaxcalls
                    datamax = data
            if data.size > maxlength:
                maxlength = data.size
            rownum += 1
        f.close()

        rownum = 0
        run = 0
        aepinitdata[:] = 0.0
        aepfinaldata[:] = 0.0
        fcallsdata[:] = 0.0
        f = open(input_file_pswec)
        for row in f.readlines():
            if rownum < 1:
                rownum += 1
                continue

            data = np.fromstring(row, sep=" ")
            # print(data.size)
            if rownum % 2 == 0:
                # dfcalc.(run, run, pd.Series(data, name=rownum))
                
                sall = pd.Series(data, name=rownum)
                slist = [aepinit[run]/pswscale]
                slist[1:] = sall
                s = pd.Series(slist)
                aepinitdata[run] = s.iloc[0]*pswscale
                aepfinaldata[run] = s.iloc[-1]*pswscale
                fcallsdata[run] = fcalls.iloc[-1]
                # s = pd.Series(data, name=rownum)
                # if rownum == 2:
                #     print(s.max())
                # else:
                #     dfcalc_ps.insert(run, run, pd.Series(data, name=rownum))
                if logplot:
                    ax1.semilogx(fcalls, 100*(1-s*pswscale/aept), alpha=alpha, color=colors[3], zorder=1)
                else:
                    ax1.plot(fcalls, 100*(1-s*pswscale/aept), alpha=alpha, color=colors[3], zorder=1)
                ax1.scatter(fcalls.iloc[-1], 100*(1 - s.iloc[-1]*pswscale / aept), marker='o', edgecolor='k', color=colors[3], zorder=10, alpha=markeralpha)
                run += 1
            else:
                fcallsall = pd.Series(data, name=rownum)
                fcallslist = [1]
                fcallslist[1:] = fcallsall 
                fcalls = pd.Series(fcallslist)
                # fcalls = pd.Series(data, name=rownum)

            rownum += 1
        f.close()
        # print("ps+wec complete")
        np.savetxt("alpso_wec_results_%smodel_%iturbs_%idirs.txt" %(model, nturbs, ndirs), np.c_[np.arange(0,runs), aepinitdata, aepfinaldata, fcallsdata], header="alpso wec results: id, AEP init (Whr), AEP final (Whr), fcalls total")
    

    # find how many entries are in the longest ps convergence history
    f = open(input_file_ps)
    maxlength = 0
    rownum = 0
    maxcalls = 0
    for row in f.readlines():
        if rownum < 1:
            rownum += 1
            continue

        data = np.fromstring(row, sep=" ")
        if rownum % 2 != 0:
            datamaxcalls = data[-1]
            if datamaxcalls > maxcalls:
                maxcalls = datamaxcalls
                datamax = data
        if data.size > maxlength:
            maxlength = data.size
        rownum += 1
    f.close()

    aepinitdata[:] = 0.0
    aepfinaldata[:] = 0.0
    fcallsdata[:] = 0.0

    rownum = 0
    run = 0
    f = open(input_file_ps)
    for row in f.readlines():
        if rownum < 1:
            rownum += 1
            continue

        data = np.fromstring(row, sep=" ")
        # print(data.size)
        if rownum % 2 == 0:
            # dfcalc.(run, run, pd.Series(data, name=rownum))
            
            sall = pd.Series(data, name=rownum)
            slist = [aepinit[run]/psscale]
            slist[1:] = sall
            s = pd.Series(slist)
            aepinitdata[run] = s.iloc[0]*psscale
            aepfinaldata[run] = s.iloc[-1]*psscale
            fcallsdata[run] = fcalls.iloc[-1]
            # s = pd.Series(data, name=rownum)
            # if rownum == 2:
            #     print(s.max())
            # else:
            #     dfcalc_ps.insert(run, run, pd.Series(data, name=rownum))
            if logplot:
                ax1.semilogx(fcalls, 100*(1-s*psscale/aept), alpha=alpha, color=colors[2], zorder=1)
            else:
                ax1.plot(fcalls, 100*(1-s*psscale/aept), alpha=alpha, color=colors[2], zorder=1)
            ax1.scatter(fcalls.iloc[-1], 100*(1 - s.iloc[-1]*psscale / aept), marker='o', edgecolor='k', color=colors[2], zorder=10, alpha=markeralpha)
            run += 1
        else:
            fcallsall = pd.Series(data, name=rownum)
            fcallslist = [1]
            fcallslist[1:] = fcallsall 
            fcalls = pd.Series(fcallslist)
            # fcalls = pd.Series(data, name=rownum)

        rownum += 1
    f.close()
    np.savetxt("alpso_results_%smodel_%iturbs_%idirs.txt" %(model, nturbs, ndirs), np.c_[np.arange(0,runs), aepinitdata, aepfinaldata, fcallsdata], header="alpso results: id, AEP init (Whr), AEP final (Whr), fcalls total")
    
    # print("ps complete")
    
    import matplotlib.patheffects as PathEffects
    lineweight = 2
    if nturbs == 16:
        txt0 = plt.text(2E2, 4, labels[0], color=colors[0]) # snopt + wec
        # txt0.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        txt1 = plt.text(3E1, 6, labels[1], color=colors[1]) # snopt
        # txt1.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        txt2 = plt.text(5E3, 5, labels[2], color=colors[2]) # alpso
        # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        plt.ylim([0, 40])
    if nturbs == 38:
        if ndirs == 12:
            if wakemodel == "BPA":
                txt0 = plt.text(3E2, 9, labels[0], color=colors[0]) # snopt + wec
                # txt0.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                txt1 = plt.text(5E1, 12, labels[1], color=colors[1]) # snopt
                # txt1.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                txt2 = plt.text(7E3, 10, labels[2], color=colors[2]) # alpso
                # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                txt3 = plt.text(1.75E3, 26, labels[3], color=colors[3]) # alpso + wec
                # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                plt.ylim([5, 40])
            elif wakemodel == "JENSEN":
                txt0 = plt.text(2E2, 16, labels[0], color=colors[0]) # snopt + wec
                # txt0.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                txt1 = plt.text(2E1, 17, labels[1], color=colors[1]) # snopt
                # txt1.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                txt2 = plt.text(6E3, 21.5, labels[2], color=colors[2]) # alpso
                # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
                plt.ylim([15,35])
        if ndirs == 36:
            txt0 = plt.text(1.25E3, 18, labels[0], color=colors[0]) # snopt + wec
            # txt0.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
            txt1 = plt.text(2E2, 18, labels[1], color=colors[1]) # snopt
            # txt1.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
            txt2 = plt.text(5E3, 25.5, labels[2], color=colors[2]) # alpso
            # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
            plt.ylim([15, 45])
    if nturbs == 60:
        txt0 = plt.text(4E1, 6.75, labels[0], color=colors[0]) # snopt + wec
        # txt0.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        txt1 = plt.text(9E2, 7.0, labels[1], color=colors[1]) # snopt
        # txt1.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        txt2 = plt.text(5E3, 6.75, labels[2], color=colors[2]) # alpso
        # txt2.set_path_effects([PathEffects.withStroke(linewidth=lineweight, foreground='k')])
        plt.ylim([5, 25])


    # print("plot settings complete")

    tick_spacing = 5
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    # print("tick locater complete")

    # plt.text(labels[0])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # print("spines complete")

    plt.xlabel("Function Calls")
    plt.ylabel("Wake Loss (%)")

    # print("labels complete")

    plt.tight_layout()

    # print("tight layout complete")

    if save_figs:
        plt.savefig(filename, transparent=True)

        # print("save complete")
    if show_figs:
        plt.show()

    return

def plot_distributions(fnamstart="", save_figs=False, show_figs=True, nturbs=38, ndirs=12, wakemodel="BPA", plotcorrelations=False, makelatextable=False, from_convergence_history=True):

    # initialize lists to hold data
    impdata = list()
    labels = list()
    boxcolors = list()
    df = pd.DataFrame()
    counter=0
    onepcaept = np.zeros(5)
    case = 0
    for wakemodel in ["BPA", "JENSEN"]:
        for nturbs, ndirs in zip(np.array([16, 38, 38, 60]), np.array([20, 12, 36, 72])):
            if from_convergence_history:

                # set theoretical AEP and ps scale
                if wakemodel == "JENSEN":
                    if nturbs == 38 and ndirs ==12:
                        aept = 5679986.827947*nturbs*1E3 #Wh
                        psscale = 1E5
                    else:
                        continue
                elif wakemodel == "BPA":
                    if nturbs == 16:
                        aept = 5191363.5933961*nturbs*1E3 # Wh
                        psscale = -1E4
                    elif nturbs == 38:
                        if ndirs == 12:
                            aept = 4994091.77684705*nturbs*1E3 #Wh
                            psscale = -1E5
                        elif ndirs == 36:
                            aept = 1630166.61601323*nturbs*1E3 # Wh
                            psscale = -1E5
                    elif nturbs == 60:
                        aept = 6653047.52233728*nturbs*1E3 #Wh
                        psscale = -1E5

                # load data
                prescaleaep = 1E-3 # convert from Wh to kWh
                resdir = "./image_data/opt_results/202103041633-mined-opt-results-from-conv-hist/"
                data_snopt_mstart = np.loadtxt(resdir+"snopt_results_%smodel_%iturbs_%idirs.txt" %(wakemodel, nturbs, ndirs))
                sm_id = data_snopt_mstart[:, 0]
                sm_orig_aep = data_snopt_mstart[:, 1]*prescaleaep
                sm_run_end_aep = data_snopt_mstart[:, 2]*prescaleaep
                sm_tfcalls = data_snopt_mstart[:, 3]
                sm_tscalls = np.zeros_like(sm_tfcalls)

                data_snopt_wec = np.loadtxt(resdir+"snopt_wec_results_%smodel_%iturbs_%idirs.txt" %(wakemodel, nturbs, ndirs))
                sw_id = data_snopt_wec[:, 0]
                sw_orig_aep = data_snopt_wec[:, 1]*prescaleaep
                sw_run_end_aep = data_snopt_wec[:, 2]*prescaleaep
                sw_tfcalls = data_snopt_wec[:, 3]
                sw_tscalls = np.zeros_like(sw_tfcalls)

                data_ps_mstart = np.loadtxt(resdir+"alpso_results_%smodel_%iturbs_%idirs.txt" %(wakemodel, nturbs, ndirs))
                ps_id = data_ps_mstart[:, 0]
                ps_orig_aep = data_ps_mstart[:, 1]*prescaleaep
                ps_run_end_aep = data_ps_mstart[:, 2]*prescaleaep
                ps_fcalls = data_ps_mstart[:, 3]
                
                if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                    data_ps_wec = np.loadtxt(resdir+"alpso_wec_results_%smodel_%iturbs_%idirs.txt" %(wakemodel, nturbs, ndirs))
                    psw_id = data_ps_wec[:, 0]
                    psw_orig_aep = data_ps_wec[:, 1]*prescaleaep
                    psw_run_end_aep = data_ps_wec[:, 2]*prescaleaep
                    psw_tfcalls = data_ps_wec[:, 3]
                
                # get AEP 
                start_aep = np.copy(sm_orig_aep)
                scale_aep = 1E-6
                onepcaept[case] = (aept/100)*1E-9
                case += 1
            else:
                if wakemodel == "BPA":
                    psdir = "./image_data/opt_results/202101042132-alpso-runs-random-seed/"
                    if nturbs == 16:
                        # resdir = "./image_data/opt_results/20200527-16-turbs-20-dir-maxwecd3-nsteps6/"
                        resdir = "./image_data/opt_results/20200821-16-turbs-20-dir-fcall-and-conv-history/"
                        data_ps_mstart = np.loadtxt(psdir + "ps/ps_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                        data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                        data_snopt_wec = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
                        aept = 5191363.5933961*nturbs*1E3 # Wh
                        psscale = -1E4
                    elif nturbs == 38:
                        if ndirs == 36:
                            # resdir = "./image_data/opt_results/20200527-38-turbs-36-dir-maxwecd3-nsteps6/"
                            resdir = "./image_data/opt_results/20200821-38-turbs-36-dir-fcall-and-conv-history/"
                            data_ps_mstart = np.loadtxt(psdir + "ps/ps_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                            # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                            data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                            data_snopt_wec = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                            aept = 1630166.61601323*nturbs*1E3 # Wh
                            psscale = -1E5
                        elif ndirs == 12:
                            # resdir = "./image_data/20200602-38-turbs-12-dir-nsteps-maxweca9/"
                            resdir = "./image_data/opt_results/20200821-38-turbs-12-dir-fcall-and-conv-history/"
                            data_ps_mstart = np.loadtxt(
                                psdir + "ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                            data_ps_wec = np.loadtxt(
                                psdir + "pswec/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                            # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                            data_snopt_mstart = np.loadtxt(
                                resdir + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                            data_snopt_wec = np.loadtxt(
                                resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                            aept = 4994091.77684705*nturbs*1E3 #Wh
                            psscale = -1E5
                        else:
                            continue

                    elif nturbs == 60:
                        # resdir = "./image_data/opt_results/20200527-60-turbs-72-dir-amalia-maxwecd3-nsteps6/"
                        resdir = "./image_data/opt_results/20200824-60-turbs-72-dir-fcall-and-conv-history/"
                        data_ps_mstart = np.loadtxt(psdir + "ps/ps_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
                        data_snopt_mstart = np.loadtxt(resdir + "snopt/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                        data_snopt_wec = np.loadtxt(resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
                        aept = 6653047.52233728*nturbs*1E3 #Wh
                        psscale = -1E5
                    else:
                        continue

                elif wakemodel == "JENSEN":
                    if ndirs == 12 and nturbs == 38:
                        resdir = "./image_data/opt_results/20201110-jensen-38-turbs-12-dir-fcal-and-conv-history/"
                        data_ps_mstart = np.loadtxt(
                            resdir + "ps/ps_multistart_rundata_38turbs_nantucketWindRose_12dirs_JENSEN_all.txt")
                        # data_ga_mstart = np.loadtxt("./image_data/ga_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
                        data_snopt_mstart = np.loadtxt(
                            resdir + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_JENSEN_all.txt")
                        data_snopt_wec = np.loadtxt(
                            resdir + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_JENSEN_all.txt")
                        aept = 5679986.827947*nturbs*1E3 #Wh
                        psscale = 1E5
                    else:
                        continue
                        # raise(EnvironmentError("Invalid Model and Case combination"))

                # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
                # aep run opt (kW), run time (s), obj func calls, sens func calls
                sw_id = data_snopt_wec[:, 0]
                sw_ef = data_snopt_wec[:, 1]
                sw_orig_aep = data_snopt_wec[0, 5]
                sw_run_ti = data_snopt_wec[:, 3]
                # sw_run_start_aep = data_snopt_wec[0, 7]
                sw_run_end_aep = data_snopt_wec[sw_run_ti==5, 7]
                sw_run_time = data_snopt_wec[:, 8]
                sw_fcalls = data_snopt_wec[:, 9]
                sw_scalls = data_snopt_wec[:, 10]

                sw_run_improvement = sw_run_end_aep / sw_orig_aep - 1.
                sw_mean_run_improvement = np.average(sw_run_improvement)
                sw_std_improvement = np.std(sw_run_improvement)

                sw_tfcalls = np.zeros(200)
                sw_tscalls = np.zeros(200)
                for i in np.arange(0, 200):
                    sw_tfcalls[i] = np.sum(sw_fcalls[sw_id == i])
                    sw_tscalls[i] = np.sum(sw_scalls[sw_id == i])

                for i in range(200):
                    if sw_tscalls[i] + sw_tfcalls[i] == 0:
                        print("Zero function call for SNOPT+WEC run %i" %i)

                # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
                # run time (s), obj func calls, sens func calls
                sm_id = data_snopt_mstart[:, 0]
                sm_ef = np.ones_like(sm_id)
                sm_orig_aep = data_snopt_mstart[0, 4]
                sm_run_ti = data_snopt_mstart[:, 2]
                # sw_run_start_aep = data_snopt_wec[0, 7]
                sm_run_end_aep = data_snopt_mstart[sm_run_ti==5, 6]
                sm_run_time = data_snopt_mstart[:, 7]
                sm_fcalls = data_snopt_mstart[:, 8]
                sm_scalls = data_snopt_mstart[:, 9]

                # sm_run_improvement = sm_run_end_aep / sm_orig_aep - 1.
                sm_run_improvement = sm_run_end_aep / sw_orig_aep - 1.
                sm_mean_run_improvement = np.average(sm_run_improvement)
                sm_std_improvement = np.std(sm_run_improvement)

                sm_tfcalls = np.zeros(200)
                sm_tscalls = np.zeros(200)
                for i in np.arange(0, 200):
                    sm_tfcalls[i] = np.sum(sm_fcalls[sm_id == i])
                    sm_tscalls[i] = np.sum(sm_scalls[sm_id == i])
                for i in range(200):
                    if sm_tscalls[i] + sm_tfcalls[i] == 0:
                        print("Zero function call for SNOPT run %i" %i)
                        sleep(2)
                # sw_tfcalls = sw_fcalls[sw_ef == 1]
                # sw_tscalls = sw_fcalls[sw_ef == 1]

                # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW),
                # run time (s), obj func calls, sens func calls
                ps_id = data_ps_mstart[:, 0]
                ps_ef = np.ones_like(ps_id)
                ps_orig_aep = data_ps_mstart[0, 4]
                ps_run_ti = data_ps_mstart[:, 2]
                start_aep = data_ps_mstart[:, 3]
                ps_run_end_aep = data_ps_mstart[ps_run_ti == 4, 6]
                ps_run_time = data_ps_mstart[:, 7]
                ps_fcalls = data_ps_mstart[:, 8]
                ps_scalls = data_ps_mstart[:, 9]

                # ps_run_improvement = ps_run_end_aep / ps_orig_aep - 1.
                ps_run_improvement = ps_run_end_aep / sw_orig_aep - 1.
                ps_mean_run_improvement = np.average(ps_run_improvement)
                ps_std_improvement = np.std(ps_run_improvement)


                # ps + wec results
                if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                    # # run number, exp fac, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW),
                    # aep run opt (kW), run time (s), obj func calls, sens func calls
                    psw_id = data_ps_wec[:, 0]
                    psw_ef = data_ps_wec[:, 1]
                    psw_orig_aep = data_ps_wec[0, 5]
                    psw_run_ti = data_ps_wec[:, 3]
                    # sw_run_start_aep = data_snopt_wec[0, 7]
                    psw_run_end_aep = data_ps_wec[psw_run_ti==5, 7]
                    psw_run_time = data_ps_wec[:, 8]
                    psw_fcalls = data_ps_wec[:, 9]
                    psw_scalls = data_ps_wec[:, 10]
                    psw_tfcalls = np.zeros(200)
                    psw_tscalls = np.zeros(200)
                    for i in np.arange(0, 200):
                        psw_tfcalls[i] = np.sum(psw_fcalls[psw_id == i])
                        psw_tscalls[i] = np.sum(psw_scalls[psw_id == i])
                        if psw_tscalls[i] > 0:
                            raise(ValueError("sensitivity calls recorded for ALPSO+WEC"))
                    psw_run_improvement = psw_run_end_aep / sw_orig_aep - 1.
                    psw_mean_run_improvement = np.average(psw_run_improvement)
                    psw_std_improvement = np.std(psw_run_improvement)
                scale_aep = 1E-6
            # get variables
            nTurbines = nturbs
            nvars = 2*nTurbines
            nCons = int(((nTurbines - 1.) * nTurbines / 2.)) + 1 * nTurbines
            

            # get fcalls: med, ave, std-dev
            # s
            s_med_fcalls = np.median(sm_tfcalls+sm_tscalls)
            s_ave_fcalls = np.average(sm_tfcalls+sm_tscalls)
            s_std_fcalls = np.std(sm_tfcalls+sm_tscalls)
            s_low_fcalls = np.min(sm_tfcalls+sm_tscalls)
            s_high_fcalls = np.max(sm_tfcalls+sm_tscalls)

            # sr
            sw_med_fcalls = np.median(sw_tfcalls+sw_tscalls)
            sw_ave_fcalls = np.average(sw_tfcalls+sw_tscalls)
            sw_std_fcalls = np.std(sw_tfcalls+sw_tscalls)
            sw_low_fcalls = np.min(sw_tfcalls+sw_tscalls)
            sw_high_fcalls = np.max(sw_tfcalls+sw_tscalls)

            # ps
            ps_med_fcalls = np.median(ps_fcalls)
            ps_ave_fcalls = np.average(ps_fcalls)
            ps_std_fcalls = np.std(ps_fcalls)
            ps_low_fcalls = np.min(ps_fcalls)
            ps_high_fcalls = np.max(ps_fcalls)

            # ps + wec
            if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                psw_med_fcalls = np.median(psw_tfcalls)
                psw_ave_fcalls = np.average(psw_tfcalls)
                psw_std_fcalls = np.std(psw_tfcalls)
                psw_low_fcalls = np.min(psw_tfcalls)
                psw_high_fcalls = np.max(psw_tfcalls)

            # get aep: base, med, ave, std-dev, low, high
            # s
            if from_convergence_history:
                s_base_aep = sm_orig_aep[0]*scale_aep
            else:
                s_base_aep = sm_orig_aep*scale_aep
            s_med_aep = np.median(sm_run_end_aep)*scale_aep
            s_ave_aep = np.average(sm_run_end_aep)*scale_aep
            s_std_aep = np.std(sm_run_end_aep)*scale_aep
            s_low_aep = np.min(sm_run_end_aep)*scale_aep
            s_high_aep = np.max(sm_run_end_aep)*scale_aep
            s_best_layout = sm_id[np.argmax(sm_run_end_aep)]

            # sr
            if from_convergence_history:
                sw_base_aep = sw_orig_aep[0]*scale_aep
            else:
                sw_base_aep = sw_orig_aep*scale_aep
            sw_med_aep = np.median(sw_run_end_aep)*scale_aep
            sw_ave_aep = np.average(sw_run_end_aep)*scale_aep
            sw_std_aep = np.std(sw_run_end_aep)*scale_aep
            sw_low_aep = np.min(sw_run_end_aep)*scale_aep
            sw_high_aep = np.max(sw_run_end_aep)*scale_aep
            sw_best_layout = sw_id[np.argmax(sw_run_end_aep)]

            # ps
            if from_convergence_history:
                ps_base_aep = ps_orig_aep[0]*scale_aep
            else:
                ps_base_aep = ps_orig_aep * scale_aep
            ps_med_aep = np.median(ps_run_end_aep) * scale_aep
            ps_ave_aep = np.average(ps_run_end_aep) * scale_aep
            ps_std_aep = np.std(ps_run_end_aep) * scale_aep
            ps_low_aep = np.min(ps_run_end_aep) * scale_aep
            ps_high_aep = np.max(ps_run_end_aep) * scale_aep
            ps_best_layout = ps_id[np.argmax(ps_run_end_aep)]
            
            # ps + wec
            if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                if from_convergence_history:
                    psw_base_aep = psw_orig_aep[0]*scale_aep
                else:
                    psw_base_aep = psw_orig_aep * scale_aep
                psw_med_aep = np.median(psw_run_end_aep) * scale_aep
                psw_ave_aep = np.average(psw_run_end_aep) * scale_aep
                psw_std_aep = np.std(psw_run_end_aep) * scale_aep
                psw_low_aep = np.min(psw_run_end_aep) * scale_aep
                psw_high_aep = np.max(psw_run_end_aep) * scale_aep
                psw_best_layout = psw_id[np.argmax(psw_run_end_aep)]

            # get wake loss statistics
            # base 
            wake_loss_original = (aept - start_aep*1E3)/aept

            # snopt
            sm_wake_loss = (aept - sm_run_end_aep*1E3)/aept
            s_wake_loss_mean = np.average(sm_wake_loss)
            s_wake_loss_med = np.median(sm_wake_loss)
            s_wake_loss_std = np.std(sm_wake_loss)
            s_wake_loss_low = np.min(sm_wake_loss)
            s_wake_loss_high = np.max(sm_wake_loss)

            # snopt + wec
            sw_wake_loss = (aept - sw_run_end_aep*1E3)/aept
            sw_wake_loss_mean = np.average(sw_wake_loss)
            sw_wake_loss_med = np.median(sw_wake_loss)
            sw_wake_loss_std = np.std(sw_wake_loss)
            sw_wake_loss_low = np.min(sw_wake_loss)
            sw_wake_loss_high = np.max(sw_wake_loss)
            sw_t, sw_p = ttest_ind(sm_wake_loss, sw_wake_loss, equal_var=False)

            # ps
            ps_wake_loss = (aept - ps_run_end_aep*1E3)/aept
            ps_wake_loss_mean = np.average(ps_wake_loss)
            ps_wake_loss_med = np.median(ps_wake_loss)
            ps_wake_loss_std = np.std(ps_wake_loss)
            ps_wake_loss_low = np.min(ps_wake_loss)
            ps_wake_loss_high = np.max(ps_wake_loss)

            # ps + wec
            if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                psw_wake_loss = (aept - psw_run_end_aep*1E3)/aept
                psw_wake_loss_mean = np.average(psw_wake_loss)
                psw_wake_loss_med = np.median(psw_wake_loss)
                psw_wake_loss_std = np.std(psw_wake_loss)
                psw_wake_loss_low = np.min(psw_wake_loss)
                psw_wake_loss_high = np.max(psw_wake_loss)
                psw_t, psw_p = ttest_ind(ps_wake_loss, psw_wake_loss, equal_var=False)

            if makelatextable:
                # collect statistics for table
                medfcalls = np.array([s_med_fcalls, sw_med_fcalls, ps_med_fcalls], dtype=int)
                lowfcalls = np.array([s_low_fcalls, sw_low_fcalls, ps_low_fcalls], dtype=int)
                highfcalls = np.array([s_high_fcalls, sw_high_fcalls, ps_high_fcalls], dtype=int)
                meanwl = np.array([s_wake_loss_mean, sw_wake_loss_mean, ps_wake_loss_mean])
                medwl = np.array([s_wake_loss_med, sw_wake_loss_med, ps_wake_loss_med])
                stdwl = np.array([s_wake_loss_std, sw_wake_loss_std, ps_wake_loss_std])
                lowwl = np.array([s_wake_loss_low, sw_wake_loss_low, ps_wake_loss_low])
                highwl = np.array([s_wake_loss_high, sw_wake_loss_high, ps_wake_loss_high])
                pcutoff = 0.001
                p = np.empty(len(meanwl), dtype=object)
                p[:] = np.nan
                if sw_p >= pcutoff:
                    p[1] = sw_p
                else:
                    p[1] = "$< %.3f$" %(pcutoff)

                if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                    medfcalls = np.append(medfcalls, int(psw_med_fcalls))
                    lowfcalls = np.append(lowfcalls, int(psw_low_fcalls))
                    highfcalls = np.append(highfcalls, int(psw_high_fcalls))
                    meanwl = np.append(meanwl, psw_wake_loss_mean)
                    medwl = np.append(medwl, psw_wake_loss_med)
                    stdwl = np.append(stdwl, psw_wake_loss_std)
                    lowwl = np.append(lowwl, psw_wake_loss_low)
                    highwl = np.append(highwl, psw_wake_loss_high)
                    if sw_p >= pcutoff:
                        p = np.append(p, psw_p)
                    else:
                        p = np.append(p, "$< %.3f$" %(pcutoff))

                # put data in array for adding to dataframe
                data = np.array([medfcalls, lowfcalls, highfcalls, medwl*100, meanwl*100, stdwl*100, lowwl*100, highwl*100, p])

                # row names
                rows = ["SNOPT", "SNOPT+WEC", "ALPSO"]
                if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                    rows.append("ALPSO+WEC")

                # column names (two levels)
                cols0 = ["Function Calls", "Function Calls", "Function Calls", "Wake Loss (%)", "Wake Loss (%)", "Wake Loss (%)", "Wake Loss (%)", "Wake Loss (%)", "Wake Loss (%)"]
                cols1 = ["Median", "Low", "High", "Median", "Mean", "SD", "Low", "High", "p"]

                # combine column names into tuples for handing to pandas Multiindex
                colstuples = list(zip(cols0,cols1))

                # create multi-level column names
                colsindex = pd.MultiIndex.from_tuples(colstuples, names=["", ""])

                # generate pandas dataframe
                df = pd.DataFrame(data.T, index=rows, columns=colsindex)

                # set up formatter function to get correct format for each element
                def formatter(element):
                    if type(element) is float:
                        return "%.3f" % element
                    elif type(element) is int:
                        return "%i" % element
                    else:
                        return element

                formatters = [formatter, formatter, formatter, formatter, formatter, formatter, formatter, formatter, formatter]

                # generate latex table code of data frame
                print(df.to_latex(caption="Optimization Results for %s Model: %i Turbines, %i Directions" %(wakemodel, nturbs, ndirs), na_rep="", column_format="lrrrrrrrrr", formatters=formatters, float_format="{:0.3f}".format, multicolumn_format='c'))
                
            # print results
            print(" #################### Results for Case Study with %s, %i Turbs, %i Dirs ))###############" %(wakemodel, nturbs, ndirs))
            print( "nturbs: ", nTurbines)
            print( "nvars: ", nvars)
            print( "ncons: ", nCons)

            print("")
            print("aept for %i turbs %i dirs (GWh): " %(nturbs,ndirs), aept*1E-9)
            print("1pc aept for %i turbs %i dirs (GWh): " %(nturbs,ndirs), (aept/100.0)*1E-9)
            print( " ")

            print( "snopt mstart results: ")
            print( "med fcalls: ", s_med_fcalls)
            print( "ave fcalls: ", s_ave_fcalls)
            print( "std fcalls: ", s_std_fcalls)
            print( "low fcalls: ", s_low_fcalls)
            print( "high fcalls: ", s_high_fcalls)
            print( "base aep: ", s_base_aep)
            print( "med aep: ", s_med_aep)
            print( "ave aep: ", s_ave_aep)
            print( "std aep: ", s_std_aep)
            print( "low aep: ", s_low_aep)
            print( "high aep: ", s_high_aep)
            print("mean wakeloss: ", s_wake_loss_mean)
            print("std wakeloss: ", s_wake_loss_std)
            print("low wakeloss: ", s_wake_loss_low)
            print("high wakeloss: ", s_wake_loss_high)
            print( "best layout: ", s_best_layout)   
            print( " ")

            print( "snopt wec results: ")
            print( "med fcalls: ", sw_med_fcalls)
            print( "ave fcalls: ", sw_ave_fcalls)
            print( "std fcalls: ", sw_std_fcalls)
            print( "low fcalls: ", sw_low_fcalls)
            print( "high fcalls: ", sw_high_fcalls)
            print( "base aep: ", sw_base_aep)
            print( "med aep: ", sw_med_aep)
            print( "ave aep: ", sw_ave_aep)
            print( "std aep: ", sw_std_aep)
            print( "low aep: ", sw_low_aep)
            print( "high aep: ", sw_high_aep)
            print("mean wakeloss: ", sw_wake_loss_mean)
            print("std wakeloss: ", sw_wake_loss_std)
            print("low wakeloss: ", sw_wake_loss_low)
            print("high wakeloss: ", sw_wake_loss_high)
            print( "best layout: ", sw_best_layout)

            print(" ")

            print("ALPSO mstart results: ")
            print("med fcalls: ", ps_med_fcalls)
            print("ave fcalls: ", ps_ave_fcalls)
            print("std fcalls: ", ps_std_fcalls)
            print("low fcalls: ", ps_low_fcalls)
            print("high fcalls: ", ps_high_fcalls)
            print("base aep: ", ps_base_aep)
            print("med aep: ", ps_med_aep)
            print("ave aep: ", ps_ave_aep)
            print("std aep: ", ps_std_aep)
            print("low aep: ", ps_low_aep)
            print("high aep: ", ps_high_aep)
            print("mean wakeloss: ", ps_wake_loss_mean)
            print("std wakeloss: ", ps_wake_loss_std)
            print("low wakeloss: ", ps_wake_loss_low)
            print("high wakeloss: ", ps_wake_loss_high)
            print("best layout: ", ps_best_layout)

            if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                print(" ")
                print("ALPSO + WEC results: ")
                print("med fcalls: ", psw_med_fcalls)
                print("ave fcalls: ", psw_ave_fcalls)
                print("std fcalls: ", psw_std_fcalls)
                print("low fcalls: ", psw_low_fcalls)
                print("high fcalls: ", psw_high_fcalls)
                print("base aep: ", psw_base_aep)
                print("med aep: ", psw_med_aep)
                print("ave aep: ", psw_ave_aep)
                print("std aep: ", psw_std_aep)
                print("low aep: ", psw_low_aep)
                print("high aep: ", psw_high_aep)
                print("mean wakeloss: ", psw_wake_loss_mean)
                print("std wakeloss: ", psw_wake_loss_std)
                print("low wakeloss: ", psw_wake_loss_low)
                print("high wakeloss: ", psw_wake_loss_high)
                print("best layout: ", psw_best_layout)

            print(" ")

            impdata.append(list(wake_loss_original*100))
            impdata.append(list(sm_wake_loss*100))
            impdata.append(list(sw_wake_loss*100))
            impdata.append(list(ps_wake_loss*100))
            dftemp = pd.DataFrame()
            # print(np.shape(impdata))
            # print(counter)
            if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
                itlabels = ["Start", "SNOPT", "SNOPT+WEC", "ALPSO", "ALPSO+WEC"]
                # itboxcolors = ["k", "c", "b", "r", "peru"]
                itboxcolors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1"]
                impdata.append(list(psw_wake_loss*100))
                for i in np.arange(0, len(itlabels)):
                    dftemp[itlabels[i]] = pd.Series(np.transpose(impdata[counter]))
                    counter += 1
                
            else:
                itlabels = ["Start", "SNOPT", "SNOPT+WEC", "ALPSO"]
                # itboxcolors = ["violet", "c", "b", "r"]
                itboxcolors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A"]
                for i in np.arange(0, len(itlabels)):
                    dftemp[itlabels[i]] = pd.Series(np.transpose(impdata[counter]))
                    counter += 1


            labels.extend(itlabels)
            boxcolors.extend(itboxcolors)
            if plotcorrelations:
                df = df.append(dftemp)

                # report correlation 
                print("correlation for %s, %i Turbs, %i Dirs" %(wakemodel, nturbs, ndirs))
                print(dftemp.corr())
                axes = pd.plotting.scatter_matrix(dftemp, figsize=(10,10)) #diagonal='kde',

                plt.suptitle("correlation for %s, %i Turbs, %i Dirs" %(wakemodel, nturbs, ndirs))
                corr = dftemp.corr().to_numpy()
                for i, j in zip(*plt.np.triu_indices_from(axes, k=1)):
                    axes[i, j].annotate("%.3f" %corr[i,j], (0.8, 0.8), xycoords='axes fraction', ha='center', va='center')
                plt.tight_layout()
                if save_figs:
                    plt.savefig(fnamstart + "scatter_matrix_%s_%iTurbs_%iDirs.pdf" %(wakemodel, nturbs, ndirs), transparent=True)
    # set up dataframe to plot distributions and calculate corelation and covariance 
    # for each case study, do this
    #   snopt snopt+wec alpso alpso+wec
    # 0  
    # 1
    # :
    # create dataframe with snopt results
    # df = pd.DataFrame()
    # print(len(labels))
    # for i in range(5):
    #     for j in range()
    # for i in np.arange(0, len(labels)):
    #     df[labels[i]+("%i" %(i))] = pd.Series(np.transpose(impdata[i]))
    #     # s = pd.Series(np.transpose(impdata[i]), name=labels[i])
    #     # dftemp = pd.DataFrame(s)
    #     # df = df.append(s)
    #     # print(dftemp.head())
    if plotcorrelations:
        print("Overall Correlation")
        print(df.corr())
        axes = pd.plotting.scatter_matrix(df, diagonal='kde', figsize=(10,10))
        plt.suptitle("correlation for all studies")
        corr = df.corr().to_numpy()
        for i, j in zip(*plt.np.triu_indices_from(axes, k=1)):
            axes[i, j].annotate("%.3f" %corr[i,j], (0.8, 0.8), xycoords='axes fraction', ha='center', va='center')
        plt.tight_layout()

    fig, ax = plt.subplots(1, figsize=(13,8.5))
    # if wakemodel == "BPA" and nturbs == 38 and ndirs == 12:
    #     labels = ["Start", "SNOPT", "SNOPT+WEC", "ALPSO", "ALPSO+WEC"]
    #     # impdata = list([sm_run_improvement * 100, sw_run_improvement*100, ps_run_improvement*100, psw_run_improvement*100])
    #     impdata = list([wake_loss_original*100, sm_wake_loss*100, sw_wake_loss*100, ps_wake_loss*100, psw_wake_loss*100])
    
    
    # for i in np.arange(0, 5):
    #     boxplt = ax.boxplot(impdata[i], meanline=True, labels=labels[i], patch_artist=True)
    #     for item in ['boxes', 'whiskers', 'caps']:
    #         plt.setp(boxplt[item], color=boxcolors[i])
    #     ax.get_xticklabels()[i].set_color(boxcolors[i])

    for i in np.arange(0, len(labels)):
        # change outline color
        ax.boxplot(np.array(impdata[i]), positions=[i+1], meanline=False, labels=[labels[i]], 
            medianprops=dict(color="gray"), whiskerprops=dict(color=boxcolors[i]), capprops=dict(color=boxcolors[i]),
            flierprops=dict(markeredgecolor=boxcolors[i]), boxprops=dict(color=boxcolors[i]), widths=0.6)
        ax.get_xticklabels()[i].set_color(boxcolors[i])

    # boxplot = ax.boxplot(impdata, meanline=False, labels=labels, medianprops=dict(color="gray"))
    # boxes = boxplot['boxes']
    # whiskers = boxplot['whiskers']
    # caps = boxplot['caps']
    # fliers = boxplot['fliers']
    # wccount = 0
    # for i in np.arange(0, len(labels)):
    #     # change outline color
    #     boxes[i].set(color=boxcolors[i], linewidth=1)
    #     whiskers[wccount].set(color=boxcolors[i], linewidth=1)
    #     whiskers[wccount+1].set(color=boxcolors[i], linewidth=1)
    #     caps[wccount].set(color=boxcolors[i], linewidth=1)
    #     caps[wccount+1].set(color=boxcolors[i], linewidth=1)
    #     ax.get_xticklabels()[i].set_color(boxcolors[i])
    #     wccount += 2
    #     # change fill color
    #     # box.set(facecolor = 'green' )
    #     # change hatch
    #     # box.set(hatch = '/')

    # separate groups of boxes
    [ax.axvline(x, color = 'gray', linestyle='--') for x in [4.5, 9.5, 13.5, 17.5]]

    # rotate tick labels
    plt.xticks(rotation=90)

    # label y axis
    ax.set_ylabel('Wake Loss (%)')

    # identify groups of box plots       
    font_size = 14    
    shift = 0.1
    ax.annotate("Case 1\nBPA Model\n16 Turbines\n20 Directions\n"+r"$1\%\approx$"+"%.3f GWh" %(onepcaept[0]), (1.35+shift, 25), color='k', ma='left', size=font_size) # 16 turbs, 20 dirs, BPA model
    ax.annotate("Case 2\nBPA Model\n38 Turbines\n12 Directions\n"+r"$1\%\approx$"+"%.3f GWh" %(onepcaept[1]), (6+shift, 25), color='k', ma='left', size=font_size) # 38 turbs, 12 dirs, BPA model
    ax.annotate("Case 3\nBPA Model\n38 Turbines\n36 Directions\n"+r"$1\%\approx$"+"%.3f GWh" %(onepcaept[2]), (10.35+shift, 25), color='k', ma='left', size=font_size) # 38 turbs, 36 dirs, BPA model
    ax.annotate("Case 4\nBPA Model\n60 Turbines\n72 Directions\n"+r"$1\%\approx$"+"%.3f GWh" %(onepcaept[3]), (14.35+shift, 25), color='k', ma='left', size=font_size) # 60 turbs, 72 dirs, BPA model
    ax.annotate("Case 2\nJensen Model\n38 Turbines\n12 Directions\n"+r"$1\%\approx$"+"%.3f GWh" %(onepcaept[4]), (18.35+shift, 25), color='k', ma='left', size=font_size) # 38 turbs, 12 dirs, Jensen model

    # ax.set_ylim([0.0, np.max(impdata)+1])
    # ax.legend(ncol=1, loc=2, frameon=False, )  # show plot
    # tick_spacing = 0.01
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # plt.tick_params(top='off', right='off')
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    # ax.set_ylim([5,40])

    plt.tight_layout()
    if save_figs:
        plt.savefig(fnamstart + 'boxpercentwakeloss.pdf', transparent=True)

    # calculate correlation and plot distributions 
    # ax1, fig1 = plt.subplots(1)

    # put all starting points in a bin and all ending points in a bin 


    if show_figs:
        plt.show()

    return

def parse_alpso_files(filename):
    with open(filename) as f:
        fcalls = re.findall('(?<=EVALUATIONS: ).\d+',f.read(),re.MULTILINE)
    with open(filename) as f:
        obj = re.findall('(?<=F = -).*',f.read(),re.MULTILINE)
    return obj, fcalls

def plot_alpso_tests(filename="", save_figs=False, show_figs=True):

    directory = "./image_data/alpso-tuning/"

    nturbs = np.array([16, 38, 38, 60])
    ndirs = np.array([20, 12, 36, 72])
    scaler = np.array([1E2, 1E3, 1E3, 1E3])
    aept = np.array([5191363.5933961, 4994091.77684705, 1630166.61601323, 6653047.52233728])*nturbs*1E-6 # from kWh to GWh
    windrose = ["directional", "nantucket", "nantucket", "amalia"]
    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    linetypes = ["-", "--", ":", "-.", (0, (3, 2, 1, 2, 1, 2)), (0, (3, 2, 3, 2, 1, 2))]
    ylims = [(12, 15),(12, 24),(21, 28),(8, 14)]
    # aept = 4994091.77684705*nturbs*1E-6 #GWh
    for i in np.arange(0,4):
        fig, ax = plt.subplots(1)
        for ii, j in zip(np.arange(5,31,5), range(6)):
            datafile = directory+"ALPSO_summary_multistart_%iturbs_%sWindRose_%idirs_BPAModel_RunID0_TItype4_II%i_print.out" %(nturbs[i],windrose[i],ndirs[i],ii)
            obj, fcalls = parse_alpso_files(datafile)
            obj = np.asfarray(obj,float)
            fcalls = np.asfarray(fcalls,float)
            ax.plot(fcalls, 100.0*(aept[i] - obj*scaler[i])/aept[i], label="II = %i" %(ii), color=colors[j], linestyle=linetypes[j])
        ax.set_ylabel("Wake Loss (%)")
        ax.set_xlabel("Function Calls")
        ax.legend(loc=1,frameon=False)
        ax.set_xlim([0,20000])    
        ax.set_ylim(ylims[i])
    
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.set_ticks_position('left')
        ax.xaxis.set_ticks_position('bottom')

        if save_figs:
            plt.tight_layout()
            filename = "./images/alpso_test_%iturbs_%idirs.pdf" %(nturbs[i], ndirs[i])
            plt.savefig(filename, transparent=True)

        if show_figs:
            plt.show()

    return

def analyze_fcalls_per_step(filename="", save_figs=False, show_figs=True):

    # load data
    case_1_data_path = "./image_data/opt_results/20201002-wec-steps/16turbs-20dirs/"
    case1_snopt_data = np.loadtxt(case_1_data_path + "snopt/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")
    case1_wec_data = np.loadtxt(case_1_data_path + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_16turbs_directionalWindRose_20dirs_BPA_all.txt")

    case_2_data_path = "./image_data/opt_results/20201002-wec-steps/38turbs-12dirs/"
    case2_snopt_data = np.loadtxt(case_2_data_path + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")
    case2_wec_data = np.loadtxt(case_2_data_path + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_BPA_all.txt")

    case_3_data_path = "./image_data/opt_results/20201002-wec-steps/38turbs-36dirs/"
    case3_snopt_data = np.loadtxt(case_3_data_path + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")
    case3_wec_data = np.loadtxt(case_3_data_path + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_36dirs_BPA_all.txt")

    case_4_data_path = "./image_data/opt_results/20201002-wec-steps/60turbs-72dirs/"
    case4_snopt_data = np.loadtxt(case_4_data_path + "snopt/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")
    case4_wec_data = np.loadtxt(case_4_data_path + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_60turbs_amaliaWindRose_72dirs_BPA_all.txt")

    case2_jensen_data_path ="./image_data/opt_results/20201110-jensen-38-turbs-12-dir-fcal-and-conv-history/"
    case2_jensen_snopt_data = np.loadtxt(case2_jensen_data_path + "snopt/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_JENSEN_all.txt")
    case2_jensen_wec_data = np.loadtxt(case2_jensen_data_path + "snopt_wec_diam_max_wec_3_nsteps_6.000/snopt_multistart_rundata_38turbs_nantucketWindRose_12dirs_JENSEN_all.txt")

    # print(np.shape(case2_jensen_snopt_data))
    
    snopt_data = [case1_snopt_data, case2_snopt_data, case3_snopt_data, case4_snopt_data, case2_jensen_snopt_data]
    wec_data = [case1_wec_data, case2_wec_data, case3_wec_data, case4_wec_data, case2_jensen_wec_data]

    nruns = 200
    ncases = len(snopt_data)

    # # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW), run time (s), obj func calls, sens func calls
    # # run number, ti calc, ti opt, aep init calc (kW), aep init opt (kW), aep run calc (kW), aep run opt (kW), run time (s), obj func calls, sens func calls
    sdata = np.zeros((ncases, nruns, 4))
    wdata = np.zeros((ncases, nruns, 9))

    for c in np.arange(0, ncases):
        for i in np.arange(0, nruns):
        
            # get non-wec data
            case_data = snopt_data[c][snopt_data[c][:,0]==i, :]
            fcalls_noti = case_data[case_data[:,2]==0,8] + case_data[case_data[:,2]==0,9]
            fcalls_ti = case_data[case_data[:,2]==5,8] + case_data[case_data[:,2]==5,9]
            fcalls_total = fcalls_noti + fcalls_ti

            # save non-wec data
            sdata[c,i,0] = i
            sdata[c,i,1] = 100*fcalls_noti/fcalls_total
            sdata[c,i,2] = 100*fcalls_ti/fcalls_total
            sdata[c,i,3] = 100*fcalls_total/fcalls_total

            # get wec data
            case_data = wec_data[c][wec_data[c][:,0]==i, :]
            fcalls_step1 = case_data[case_data[:,1]==3.0,9] + case_data[case_data[:,1]==3.0,10]
            fcalls_step2 = case_data[case_data[:,1]==2.6,9] + case_data[case_data[:,1]==2.6,10]
            fcalls_step3 = case_data[case_data[:,1]==2.2,9] + case_data[case_data[:,1]==2.2,10]
            fcalls_step4 = case_data[case_data[:,1]==1.8,9] + case_data[case_data[:,1]==1.8,10]
            fcalls_step5 = case_data[case_data[:,1]==1.4,9] + case_data[case_data[:,1]==1.4,10]
            case_data_wec_1 = case_data[case_data[:,1]==1.0, :]
            fcalls_step6 = case_data_wec_1[case_data_wec_1[:,3]==0.0,9] + case_data_wec_1[case_data_wec_1[:,3]==0.0,10]
            fcalls_stepTI = case_data[case_data[:,3]==5.0,9] + case_data[case_data[:,3]==5.0,10]
            fcalls_total = fcalls_step1 + fcalls_step2 + fcalls_step3 + fcalls_step4 + fcalls_step5 + fcalls_step6 + fcalls_stepTI
            
            # save wec data
            wdata[c,i,0] = i
            try:
                wdata[c,i,1] = 100*fcalls_step1/fcalls_total
            except:
                wdata[c,i,1] = np.nan
            try:
                wdata[c,i,2] = 100*fcalls_step2/fcalls_total
            except:
                wdata[c,i,2] = np.nan
            try:
                wdata[c,i,3] = 100*fcalls_step3/fcalls_total
            except:
                wdata[c,i,3] = np.nan
            try:
                wdata[c,i,4] = 100*fcalls_step4/fcalls_total
            except:
                wdata[c,i,4] = np.nan
            try:
                wdata[c,i,5] = 100*fcalls_step5/fcalls_total
            except:
                wdata[c,i,5] = np.nan
            try:
                wdata[c,i,6] = 100*fcalls_step6/fcalls_total
            except:
                wdata[c,i,6] = np.nan
            try:
                wdata[c,i,7] = 100*fcalls_stepTI/fcalls_total
            except:
                wdata[c,i,7] = np.nan
            try:
                wdata[c,i,8] = 100*fcalls_total/fcalls_total
            except:
                wdata[c,i,8] = np.nan

    # make data frames
    # sdata = np.zeros((4, nruns, 4))
    c1sdf = pd.DataFrame(sdata[0])
    c1wdf = pd.DataFrame(wdata[0])

    c2sdf = pd.DataFrame(sdata[1])
    c2wdf = pd.DataFrame(wdata[1])

    c3sdf = pd.DataFrame(sdata[2])
    c3wdf = pd.DataFrame(wdata[2])

    c4sdf = pd.DataFrame(sdata[3])
    c4wdf = pd.DataFrame(wdata[3])

    c2jsdf = pd.DataFrame(sdata[4])
    c2jwdf = pd.DataFrame(wdata[4])  

    # if save_figs:
    #     plt.tight_layout()
    #     filename = "./images/alpso_test_%iturbs_%idirs.pdf" %(nturbs[i], ndirs[i])
    #     plt.savefig(filename, transparent=True)

    c1wdf.columns = ['run', '1', '2', '3', '4', '5', '6', '7', 'Total']
    c2wdf.columns = ['run', '1', '2', '3', '4', '5', '6', '7', 'Total']
    c3wdf.columns = ['run', '1', '2', '3', '4', '5', '6', '7', 'Total']
    c4wdf.columns = ['run', '1', '2', '3', '4', '5', '6', '7', 'Total']
    c2jwdf.columns = ['run', '1', '2', '3', '4', '5', '6', '7', 'Total']

    c1sdf.columns = ['run', '1', '2', 'Total']
    c2sdf.columns = ['run', '1', '2', 'Total']
    c3sdf.columns = ['run', '1', '2', 'Total']
    c4sdf.columns = ['run', '1', '2', 'Total']
    c2jsdf.columns = ['run', '1', '2', 'Total']

    c1wdf.set_index('run', inplace=True)
    c2wdf.set_index('run', inplace=True)
    c3wdf.set_index('run', inplace=True)
    c4wdf.set_index('run', inplace=True)
    c2jwdf.set_index('run', inplace=True)

    c1sdf.set_index('run', inplace=True)
    c2sdf.set_index('run', inplace=True)
    c3sdf.set_index('run', inplace=True)
    c4sdf.set_index('run', inplace=True)
    c2jsdf.set_index('run', inplace=True)

    c1wdf.dropna(inplace=True)
    c2wdf.dropna(inplace=True)
    c3wdf.dropna(inplace=True)
    c4wdf.dropna(inplace=True)
    c2jwdf.dropna(inplace=True)

    c1sdf.dropna(inplace=True)
    c2sdf.dropna(inplace=True)
    c3sdf.dropna(inplace=True)
    c4sdf.dropna(inplace=True)
    c2jsdf.dropna(inplace=True)

    # colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    # # df2 = pd.concat([c1wdf, c2wdf, c3wdf, c4wdf, c2jwdf],ignore_index=True)
    # # df2.columns = ['Case 1 (BPA)', 'Case 2 (BPA)', 'Case 3 (BPA)', 'Case 4 (BPA)', 'Case 2 (Jensen)']
    # c1wdf.plot.box()
    # plt.show() 

    mwdf1 = pd.DataFrame(c1wdf.mean())
    mwdf2 = pd.DataFrame(c2wdf.mean())
    mwdf3 = pd.DataFrame(c3wdf.mean())
    mwdf4 = pd.DataFrame(c4wdf.mean())
    mwdf2j = pd.DataFrame(c2jwdf.mean())

    # whigh = [c1wdf.max(), c2wdf.max(), c3wdf.max(), c4wdf.max(), c2jwdf.max()]
    # wlow = [c1wdf.min(), c2wdf.min(), c3wdf.min(), c4wdf.min(), c2jwdf.min()]

    msdf1 = pd.DataFrame(c1sdf.mean())
    msdf2 = pd.DataFrame(c2sdf.mean())
    msdf3 = pd.DataFrame(c3sdf.mean())
    msdf4 = pd.DataFrame(c4sdf.mean())
    msdf2j = pd.DataFrame(c2jsdf.mean())

    # shigh = [c1sdf.max(), c2sdf.max(), c3sdf.max(), c4sdf.max(), c2jsdf.max()]
    # slow = [c1sdf.min(), c2sdf.min(), c3sdf.min(), c4sdf.min(), c2jsdf.min()]
    # print(shigh[0][0])

    colors = ["#BDB8AD",  "#85C0F9", "#0F2080", "#F5793A", "#A95AA1", "#382119"]
    df = pd.concat([mwdf1.T, mwdf2.T, mwdf3.T, mwdf4.T, mwdf2j.T],ignore_index=True).T
    df.columns = ['Case 1 (BPA)', 'Case 2 (BPA)', 'Case 3 (BPA)', 'Case 4 (BPA)', 'Case 2 (Jensen)']
    df.drop(index=['Total'], inplace=True)
    ax = df.plot.bar(color=colors, width=0.7, legend=False)#, yerr=(wlow, whigh))
    ax.set_ylabel("Mean Function Call Percentage")
    ax.set_xlabel("Optimization")
    plt.xticks(rotation=None)
    # plt.legend(frameon=False, bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_ylim([0,50])
    plt.tight_layout()
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
        
    if save_figs:
        plt.savefig(filename+"-with-wec.pdf", transparent=True)

    if show_figs:
        plt.show()

    df = pd.concat([msdf1.T, msdf2.T, msdf3.T, msdf4.T, msdf2j.T],ignore_index=True).T
    df.columns = ['Case 1 (BPA)', 'Case 2 (BPA)', 'Case 3 (BPA)', 'Case 4 (BPA)', 'Case 2 (Jensen)']
    df.drop(index=['Total'], inplace=True)
    ax = df.plot.bar(color=colors)#, yerr=(slow, shigh))
    ax.set_ylabel("Mean Function Call Percentage")
    ax.set_xlabel("Optimization")
    ax.set_ylim([0,80])
    plt.xticks(rotation=None)
    plt.legend(frameon=False, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    
    if save_figs:
        plt.savefig(filename+"-without-wec.pdf", transparent=True)

    if show_figs:
        plt.show()
        

    return

    

if __name__ == "__main__":

    show_figs = True
    save_figs = True

    for_presentation = False

    if for_presentation:
        font = {'size': 24}
        plt.rc('font', **font)

        plt.rcParams['xtick.major.pad'] = '8'
        plt.rcParams['ytick.major.pad'] = '8'

        mpl.rcParams['lines.linewidth'] = 2
    else:
        font = {'size': 15}
        plt.rc('font', **font)

        plt.rcParams['xtick.major.pad'] = '8'
        plt.rcParams['ytick.major.pad'] = '8'

    filename = ''

    # get_statistics_38_turbs()
    # get_statistics_case_studies(turbs=16, dirs=36, lt0=False)
    # plot_distributions(fnamstart="./images/dist_", save_figs=True, show_figs=True, plotcorrelations=False, makelatextable=True)

    # filename = "./images/16turbs_results_alpso"
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=16, ps_wec=False)

    # filename = "./images/38turbs_results_alpso"
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=38)

    # filename = "./images/60turbs_results_alpso"
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=60)

    # plot_optimization_results(filename, save_figs, show_figs, nturbs=9)
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=38)

    # filename = "./images/16turbs_results_bpa_wec"
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=16, model="BPA", ps=True)

    # filename = "./38turbs_results_"
    # plot_optimization_results(filename, save_figs, show_figs, nturbs=38, model="JENSEN", ps=False, ps_wec=False)


    # plot_max_wec_results(filename, save_figs, show_figs, nturbs=38)
    # plot_wec_step_results(filename, save_figs, show_figs, nturbs=38)
    # plot_wec_nstep_results(filename, save_figs, show_figs, nturbs=38)
    # filename = './images/maxwec_const_nsteps6'
    # plot_max_wec_const_nstep_results(filename, save_figs, show_figs, nturbs=38)
    # filename = './images/nsteps_const_maxwec'
    # plot_maxwec3_nstep_results(filename, save_figs, show_figs, nturbs=38)

    # filename = './images/wec-methods.pdf'
    # filename = './images/Figure_1.pdf'
    # plot_wec_methods(filename, save_figs, show_figs)

    # filename = "./images/38turbs_results_hist"
    # plot_optimization_results_38_turbs_hist(filename, save_figs, show_figs)

    # filename = "round_farm_38Turbines_5DSpacing_finish_pres.pdf"
    # plot_round_farm_finish_pres(filename, save_figs, show_figs)
    
    # filename = "16_turb_start.pdf"
    # filename = "Figure_8.pdf"
    # filename = "38_turb_start.pdf"
    # filename = "Figure_10.pdf"
    # filename = "60_turb_start.pdf"
    # filename = "Figure_14.pdf"
    
    # plot_farm(filename, save_figs, show_figs, layout='start', turb_nums=False, turbs=16)

    # dirs = 20 
    # Figure_9.pdf # freq

    # dirs = 12 
    # Figure_11.pdf # freq

    # dirs = 36
    # Figure_12.pdf # freq 
    # Figure_13.pdf # wind speed 

    # dirs = 72
    # Figure_15.pdf # freq 
    # Figure_16.pdf # wind speed 

    # filename = "windrose_%i_dir.pdf" %dirs
    # make_windrose_plots(filename, save_figs, show_figs, presentation=False, dirs=dirs)

    # filename = "round_farm_38Turbines_5DSpacing_finish.pdf"
    # plot_farm(filename, save_figs, show_figs, layout='finish',turb_nums=True)

    # filename = "round_farm_38Turbines_5DSpacing_finish_pres.pdf"
    # plot_results_nruns(filename, save_figs, show_figs)

    # filename = "amalia_farm_60Turbines_5DSpacing_start.pdf"
    # plot_any_farm(filename, save_figs, show_figs, nturbs=60)

    # filename = "./images/one_hundred_sampling_points.pdf"
    # plot_100_rotor_points(filename, save_figs, show_figs, npoints=40)

    # filename = "./images/four_sampling_points.pdf"
    # plot_1_rotor_point(filename, save_figs, show_figs)

    # filename = "./images/shear_fit.pdf"
    # plot_shear_fit(filename, save_figs, show_figs)

    # filename = "./images/power_by_dir_horns_rev_1rpt.pdf"
    # plot_power_direction_horns_rev(filename, save_figs, show_figs, nrpt=1)

    # filename = "./images/power_by_dir_horns_rev_100rpt.pdf"
    # plot_power_direction_horns_rev(filename, save_figs, show_figs, nrpt=100)

    # filename = "./images/power_by_row_horns_rev_1rpt.pdf"
    # plot_power_row_horns_rev(filename, save_figs, show_figs, nrpt=1)

    # filename = "./images/power_by_row_horns_rev_100rpt.pdf"
    # plot_power_row_horns_rev(filename, save_figs, show_figs, nrpt=100)

    # filename = "./images/power_by_dir_vs_rpts_"
    # plot_power_direction_error_horns_rev(filename, save_figs, show_figs)

    # filename = "./images/sowfa_compare_pow_by_turb_dir.pdf"
    # plot_turb_power_error_baseline(filename, save_figs=save_figs, show_figs=show_figs)

    # filename = "./images/sowfa_compare_pow_by_dir.pdf"
    # plot_dir_power_error_baseline(filename, save_figs=save_figs, show_figs=show_figs)

    # filename = "./images/model_contours_vertical_before.pdf"
    # plot_model_contours_vertical(filename, save_figs, show_figs, before=True)

    # filename = "./images/model_contours_vertical_after.pdf"
    # plot_model_contours_vertical(filename, save_figs, show_figs, before=False)

    # filename = "./images/smoothing_jensen_wec_d.pdf"
    # filename = "./images/Figure_7b.pdf"
    # plot_smoothing_visualization_w_wec_wo_wec(filename, save_figs, show_figs, wec_method="D", wake_model="JENSEN")

    # filename = "./images/smoothing_bpa_wec_d.pdf"
    # filename = "./images/Figure_6b.pdf"
    # plot_smoothing_visualization_w_wec_wo_wec(filename, save_figs, show_figs, wec_method="D", wake_model="BPA")

    # filename = "./images/cp_curve_v80.pdf"
    # filename = "./images/Figure_4.pdf"
    # plot_cp_curve(filename, save_figs, show_figs)

    # filename = "./images/ct_curve_v80.pdf"
    # filename = "./images/Figure_5.pdf"
    # plot_ct_curve(filename, save_figs, show_figs)

    # filename = "./images/3turb-design-space.pdf"
    # filename = "./images/Figure_6a.pdf"
    # filename = "./images/Figure_7a.pdf"
    # plot_simple_design_space(filename, save_figs, show_figs)

    # filename = "./images/jensen_diagram.pdf"
    # filename = "./images/Figure_2.pdf"
    # plot_jensen_diagram(filename, save_figs, show_figs)
    
    # filename = "./images/jensen_profiles.pdf"
    # filename = "./images/Figure_3.pdf"
    # plot_jensen_profiles(filename, save_figs, show_figs)

    # nturbs = 38
    # ndirs = 12
    # model = "JENSEN"
    # filename = "./images/convergence_history_%smodel_%iturbs_%idirs.pdf" % (model, nturbs, ndirs)
    # plot_convergence_history(filename, save_figs=save_figs, show_figs=show_figs, nturbs=nturbs, ndirs=ndirs, wakemodel=model, logplot=True)

    # plot_alpso_tests(save_figs=save_figs,show_figs=show_figs)

    # filename = "./images/fcall-bar-plot"
    # analyze_fcalls_per_step(filename, save_figs, show_figs)