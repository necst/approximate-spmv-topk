#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:06:01 2020
@author: aparravi
"""

import scipy.stats as st
import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import os
from scipy.stats.mstats import gmean
from functools import reduce

##############################
# Colors #####################
##############################

# Define some colors for later use.
# Tool to create paletters: https://color.adobe.com/create
# Guide to make nice palettes: https://earthobservatory.nasa.gov/blogs/elegantfigures/2013/08/05/subtleties-of-color-part-1-of-6/
COLORS = dict(

    c1 = "#b1494a",
    c2 = "#256482",
    c3 = "#2f9c5a",
    c4 = "#28464f",
    
    r1 = "#FA4D4A",
    r2 = "#FA3A51",
    r3 = "#F41922",
    r4 = "#CE1922",
    r5 = "#F07B71",
    r6 = "#F0A694",
    r7 = "#F78177",
    
    b1 = "#97E6DB",
    b2 = "#C6E6DB",
    b3 = "#CEF0E4",
    b4 = "#9CCFC4",
    b5 = "#AEDBF2",
    b6 = "#B0E6DB",
    b7 = "#B6FCDA",
    b8 = "#7bd490",
    
    # Another blue-green palette;
    bb0 = "#FFA685",
    bb1 = "#75B0A2",
    bb2 = "#CEF0E4",  # Same as b3; 
    bb3 = "#B6FCDA",  # Same as b7;
    bb4 = "#7ED7B8",
    bb5 = "#7BD490",
    
    y1 = "#FFA728",
    y2 = "#FF9642",
    y3 = "#FFAB69",
    
    peach1 = "#FF9868",
    
    bt1 = "#55819E",
    bt2 = "#538F6F",
    blue_klein = "#002fa7",
    )

##############################
# Functions ##################
##############################

def get_exp_label(val, prefix="", decimal_remaining_val: bool=False) -> str: 
    """
    :param val: numeric label to format
    :return: label formatted in scientific notation
    
    Format a label in scientific notation, using Latex math font.
    For example, 10000 -> 10^4;
    """
    # Get the power of 10
    exp_val = 0
    remaining_val = int(val)
    while (remaining_val % 10 == 0 and remaining_val > 0):
        exp_val += 1
        remaining_val = remaining_val // 10
    if remaining_val > 1 and exp_val >= 1:
        if decimal_remaining_val and remaining_val > 0:
            return r"$\mathdefault{" + prefix + str(remaining_val / 10) + r"\!·\!{10}^{" + str(exp_val + 1) + r"}}$"
        else:
            return r"$\mathdefault{" + prefix + str(remaining_val) + r"\!·\!{10}^{" + str(exp_val) + r"}}$"
    elif remaining_val > 1 and exp_val == 0:
        print(val)
        return r"$\mathdefault{" + prefix + str(val) + r"}$"
    else:
        return r"$\mathdefault{" + prefix + r"{10}^{" + str(exp_val) + r"}}$"
    

def fix_label_length(labels: list, max_length: int=20) -> list:
    """
    :param labels: a list of textual labels
    :return: a list of updated labels
    
    Ensure that all labels are shorter than a given length;
    """
    fixed_labels = []
    for l in labels:
        if len(l) <= max_length:
            fixed_labels += [l]
        else:
            fixed_labels += [l[:max_length-3] + "..."]
    return fixed_labels


def remove_outliers(data, sigmas: int=3):
    """
    :param data: a sequence of numerical data, iterable
    :param sigmas: number of standard deviations outside which a value is consider to be an outlier
    :return: data without outliers
    
    Filter a sequence of data by keeping only values within "sigma" standard deviations from the mean.
    This is a simple way to filter outliers, it is more useful for visualizations than for sound statistical analyses;
    """
    return data[np.abs(st.zscore(data)) < sigmas]


def remove_outliers_df(data: pd.DataFrame, column: str, reset_index: bool = True, drop_index: bool = True, sigmas: int = 3) -> pd.DataFrame:
    """
    :param data: a pd.DataFrame
    :param column: name of the column where data are filtered
    :param reset_index: if True, reset the index after filtering
    :param drop_index: if True, drop the index column after reset
    :param sigmas: number of standard deviations outside which a value is consider to be an outlier
    :return: data without outliers
    
    Filter a sequence of data by keeping only values within "sigma" standard deviations from the mean.
    This is a simple way to filter outliers, it is more useful for visualizations than for sound statistical analyses;
    """
    col = data[column]
    res = data.loc[remove_outliers(col, sigmas).index]
    if reset_index:
        res = res.reset_index(drop=drop_index)
    return res


def remove_outliers_df_grouped(data: pd.DataFrame, column: str, group: list, reset_index: bool = True, drop_index: bool = True, sigmas: int = 3) -> pd.DataFrame:
    """
    Same as "remove_outliers_df", but also filter values after divided by group;
    """
    filtered = []
    for i, g in data.groupby(group, sort=False):
        filtered += [remove_outliers_df(g, column, reset_index, drop_index, sigmas)]
    return pd.concat(filtered)


def compute_speedup(X: pd.DataFrame, col_slow: str, col_fast: str, col_speedup: str) -> None:
    """
    Add a column to a dataframe that represents a speedup,
    and "col_slow", "col_fast" are execution times (e.g. CPU and GPU execution time);
    """
    X[col_speedup] = X[col_slow] / X[col_fast]
    
    
def get_ci_size(x, ci=0.95, estimator=np.mean):
    """
    :param x: a sequence of numerical data, iterable
    :param ci: confidence interval to consider
    :return: size of upper confidence interval, size of lower confidence interval, mean
    
    Compute the size of the upper confidence interval,
    i.e. the size between the top of the bar and the top of the error bar as it is generated by seaborn.
    Useful for adding labels above error bars, or to create by hand the error bars;
    """ 
    center = estimator(x)
    ci_lower, ci_upper = st.t.interval(ci, len(x) - 1, loc=center, scale=st.sem(x))
    return ci_upper - center, center - ci_lower, center


def get_upper_ci_size(x, ci=0.95, estimator=np.mean):
    return get_ci_size(x, ci, estimator=estimator)[0]
    
    
def add_labels(ax: plt.Axes, labels: list=None, vertical_offsets: list=None,
               patch_num: list=None, fontsize: int=14, rotation: int=0,
               vertical_coords: list=None,
               skip_zero: bool=False, format_str: str="{:.2f}x",
               label_color: str="#2f2f2f", max_only=False, skip_bars: int=0, max_bars: int=None):
    """
    :param ax: current axis, it is assumed that each ax.Patch is a bar over which we want to add a label
    :param labels: optional labels to add. If not present, add the bar height
    :param vertical_offsets: additional vertical offset for each label.
      Useful when displaying error bars (see @get_upper_ci_size), and for fine tuning
    :param patch_num: indices of patches to which we add labels, if some of them should be skipped
    :param fontsize: size of each label
    :param rotation: rotation of the labels (e.g. 90°)
    :param skip_zero: if True, don't put a label over the first bar
    :param format_str: format of each label, by default use speedup (e.g. 2.10x)
    :param label_color: hexadecimal color used for labels
    :param max_only: add only the label with highest value
    :param skip_bars: start adding labels after the specified number of bars
    :param max_bars: don't add labels after the specified bar
    
    Used to add labels above barplots;
    """
    if not vertical_offsets:
        # 5% above each bar, by default;
        vertical_offsets = [ax.get_ylim()[1] * 0.05] * len(ax.patches)
    if not labels:
        labels = [p.get_height() for p in ax.patches]
        if max_only:
            argmax = np.argmax(labels)
    patches = []
    if not patch_num:
        patches = ax.patches
    else:
        patches = [p for i, p in enumerate(ax.patches) if i in patch_num]
    
    # Iterate through the list of axes' patches
    for i, p in enumerate(patches[skip_bars:max_bars]):
        if labels[i] and (i > 0 or not skip_zero) and (not max_only or i == argmax) and i < len(labels) and i < len(vertical_offsets):
            ax.text(p.get_x() + p.get_width()/2., (vertical_offsets[i] + p.get_height()) if not vertical_coords else vertical_coords[i],
                    format_str.format(labels[i]), 
                    fontsize=fontsize, color=label_color, ha='center', va='bottom', rotation=rotation)
        

def update_width(ax: plt.Axes, width: float=1):
    """
    Given an axis with a barplot, scale the width of each bar to the provided percentage,
      and align them to their center;
    """
    for i, patch in enumerate(ax.patches):
        current_width = patch.get_width()
        diff = current_width - width
        # Change the bar width
        patch.set_width(width)
        # Recenter the bar
        patch.set_x(patch.get_x() + 0.5 * diff)
        
        
def transpose_legend_labels(labels, patches, max_elements_per_row=6, default_elements_per_col=2):
    """
    Matplotlib by defaults places elements in the legend from top to bottom.
    In most cases, placing them left-to-right is more readable (you know, English is read left-to-right, not top-to-bottom)
    This function transposes the elements in the legend, allowing to set the maximum number of values you want in each row.
    
    :param labels: list of labels in the legend
    :param patches: list of patches in the legend
    :param max_elements_per_row: maximum number of legend elements per row
    :param default_elements_per_col: by default, try having default_elements_per_col elements in each col (could be more if max_elements_per_row is reached) 
    """
    elements_per_row = min(int(np.ceil(len(labels) / default_elements_per_col)), max_elements_per_row)  # Don't add too many elements per row;
    labels = np.concatenate([labels[i::elements_per_row] for i in range(elements_per_row)], axis=0)
    patches = np.concatenate([patches[i::elements_per_row] for i in range(elements_per_row)], axis=0)
    return labels, patches

        
def save_plot(directory: str, filename: str, date: str = "", create_date_dir: bool = True, extension: list = ["pdf", "png"]):
    """
    :param directory: where the plot is stored
    :param filename: should be of format 'myplot_{}.{}', where the first placeholder is used for the date and the second for the extension,
        or 'myplot.{}', or 'myplot.extension'
    :param date: date that should appear in the plot filename
    :param create_date_dir: if True, create a sub-folder with the date
    :param extension: list of extension used to store the plot
    """
    
    output_folder = os.path.join(directory, date) if create_date_dir else directory
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        
    for e in extension:
        plt.savefig(os.path.join(output_folder, filename.format(date, e) if date else filename.format(e)), dpi=300)
        
    
def compute_speedup_df(data, key, baseline_filter_col, baseline_filter_val,  
                    speedup_col_name="speedup", time_column="exec_time",
                    baseline_col_name="baseline_time",
                    correction=True, aggregation=np.median):
    
    # Initialize speedup values;
    data[speedup_col_name] = 1
    data[baseline_col_name] = 0
    
    grouped_data = data.groupby(key, as_index=False)
    for group_key, group in grouped_data:
        # Compute the median baseline computation time;
        indices = [data[data[i] == j].index for i, j in zip(baseline_filter_col, baseline_filter_val)]
        reduced_index = reduce(lambda x, y: x.intersection(y), indices)
        
        median_baseline = aggregation(data.loc[reduced_index, time_column])
        # Compute the speedup for this group;
        group.loc[:, speedup_col_name] = median_baseline / group[time_column]
        group.loc[:, baseline_col_name] = median_baseline
        data.loc[group.index, :] = group
    
        # Guarantee that the geometric mean of speedup referred to the baseline is 1, and adjust speedups accordingly;
        if correction:
            gmean_speedup = gmean(data.loc[reduced_index, speedup_col_name])
            group.loc[:, speedup_col_name] /= gmean_speedup
            data.loc[group.index, :] = group