import numpy as np
import pandas as pd
import textwrap

from matplotlib import pyplot as plt

from datamapplot.palette_handling import (
    palette_from_datamap,
    deep_palette,
    pastel_palette,
)
from datamapplot.plot_rendering import render_plot


def labelled_static_plot(
    umap_coords,
    labels,
    title=None,
    sub_title=None,
    noise_label="Unlabelled",
    noise_color="#999999",
    color_label_text=True,
    label_wrap_width=16,
    label_color_map=None,
    figsize=(12, 12),
    dynamic_label_size=False,
    dpi=plt.rcParams["figure.dpi"],
    force_matplotlib=False,
    darkmode=False,
    **render_plot_kwds,
):
    cluster_label_vector = np.asarray(labels)
    unique_non_noise_labels = [
        label for label in np.unique(cluster_label_vector) if label != noise_label
    ]
    label_locations = np.asarray(
        [
            umap_coords[cluster_label_vector == i].mean(axis=0)
            for i in unique_non_noise_labels
        ]
    )
    label_text = [
        textwrap.fill(x, width=label_wrap_width, break_long_words=False)
        for x in unique_non_noise_labels
    ]

    # If we don't have a color map, generate one
    if label_color_map is None:
        palette = palette_from_datamap(umap_coords, label_locations)
        label_to_index_map = {
            name: index for index, name in enumerate(unique_non_noise_labels)
        }
        color_list = [
            palette[label_to_index_map[x]] if x in label_to_index_map else noise_color
            for x in cluster_label_vector
        ]
        label_color_map = {
            x: (
                palette[label_to_index_map[x]]
                if x in label_to_index_map
                else noise_color
            )
            for x in np.unique(cluster_label_vector)
        }
    else:
        color_list = [
            label_color_map[x] if x != noise_label else noise_color
            for x in cluster_label_vector
        ]

    # Darken and reduce chroma of label colors to get text labels
    if color_label_text:
        if darkmode:
            label_text_colors = pastel_palette(
                [label_color_map[x] for x in unique_non_noise_labels]
            )
        else:
            label_text_colors = deep_palette(
                [label_color_map[x] for x in unique_non_noise_labels]
            )
    else:
        label_text_colors = None

    if dynamic_label_size:
        cluster_sizes = np.sqrt(pd.Series(cluster_label_vector).value_counts())
        label_size_adjustments = cluster_sizes - cluster_sizes.min()
        label_size_adjustments /= label_size_adjustments.max()
        label_size_adjustments *= render_plot_kwds.get("label_font_size", 10) + 2
        label_size_adjustments = dict(label_size_adjustments - 2)
        label_size_adjustments = [
            label_size_adjustments[x] for x in unique_non_noise_labels
        ]
    else:
        label_size_adjustments = [0.0] * len(unique_non_noise_labels)

    # Heuristics for point size and alpha values
    n_points = umap_coords.shape[0]
    if umap_coords.shape[0] < 100_000 or force_matplotlib:
        magic_number = np.clip(128 * 4 ** (-np.log10(n_points)), 0.05, 64)
        point_size = magic_number
        alpha = np.clip(magic_number, 0.05, 1)
    else:
        point_size = int(np.sqrt(figsize[0] * figsize[1]) * dpi) // 2048
        alpha = 1.0

    if "point_size" in render_plot_kwds:
        point_size = render_plot_kwds.pop("point_size")

    if "alpha" in render_plot_kwds:
        alpha = render_plot_kwds.pop("alpha")

    fig, ax = render_plot(
        umap_coords,
        color_list,
        label_text,
        label_locations,
        title=title,
        sub_title=sub_title,
        point_size=point_size,
        alpha=alpha,
        label_colors=None if not color_label_text else label_text_colors,
        figsize=figsize,
        noise_color=noise_color,
        label_size_adjustments=label_size_adjustments,
        dpi=dpi,
        force_matplotlib=force_matplotlib,
        darkmode=darkmode,
        **render_plot_kwds,
    )

    return fig, ax
