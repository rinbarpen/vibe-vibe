#!/usr/bin/env python3
"""Matplotlib chart templates — ready-to-use functions for common chart types."""

import matplotlib.pyplot as plt
import numpy as np

# === Publication Settings ===

PUB_STYLE = {
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'grid.alpha': 0.3,
}

PRESENTATION_STYLE = {
    'font.family': 'sans-serif',
    'font.size': 16,
    'axes.labelsize': 18,
    'axes.titlesize': 20,
    'legend.fontsize': 14,
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'axes.linewidth': 2.0,
    'lines.linewidth': 3.0,
    'lines.markersize': 10,
}

CHINESE_STYLE = {
    'font.sans-serif': ['SimHei', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'axes.unicode_minus': False,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
}

COLORS = ['#6c8ebf', '#82b366', '#d6b656', '#b85450', '#9673a6', '#d79b00', '#6c8ebf', '#b3b3b3']
GRAY_COLORS = ['#333333', '#666666', '#999999', '#bbbbbb', '#444444', '#777777', '#aaaaaa']


def grouped_bar(groups, values_dict, errors=None, xlabel='', ylabel='', title='',
                output='bar_chart.pdf', grayscale=False):
    """Grouped bar chart with optional error bars."""
    plt.rcParams.update(PUB_STYLE)
    colors = GRAY_COLORS if grayscale else COLORS

    n_groups = len(groups)
    n_series = len(values_dict)
    bar_width = 0.8 / n_series
    x = np.arange(n_groups)

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, (name, values) in enumerate(values_dict.items()):
        offset = (i - n_series / 2 + 0.5) * bar_width
        err = errors[name] if errors else None
        ax.bar(x + offset, values, bar_width, label=name, color=colors[i % len(colors)],
               edgecolor='white', linewidth=0.5, yerr=err, capsize=3)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.legend(loc='best')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


def line_chart(x, series_dict, xlabel='X', ylabel='Y', title='', output='line_chart.pdf'):
    """Multi-series line chart."""
    plt.rcParams.update(PUB_STYLE)

    fig, ax = plt.subplots(figsize=(8, 5))
    line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]

    for i, (name, y) in enumerate(series_dict.items()):
        ax.plot(x, y, color=COLORS[i % len(COLORS)], linestyle=line_styles[i % len(line_styles)],
                linewidth=1.5, marker='o', markersize=3, markevery=max(1, len(x) // 10), label=name)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


def scatter_plot(x, y, c=None, xlabel='X', ylabel='Y', title='', output='scatter.pdf'):
    """Scatter plot with optional color mapping."""
    plt.rcParams.update(PUB_STYLE)

    fig, ax = plt.subplots(figsize=(7, 6))
    sc = ax.scatter(x, y, c=c, cmap='viridis', s=40, alpha=0.7, edgecolors='white', linewidth=0.3)

    if c is not None:
        plt.colorbar(sc, ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='datalim')

    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


def heatmap(data, row_labels=None, col_labels=None, annotate=True, cmap='coolwarm',
            title='', output='heatmap.pdf'):
    """Heatmap with annotations."""
    plt.rcParams.update(PUB_STYLE)

    fig, ax = plt.subplots(figsize=(max(6, len(col_labels or []) * 0.8), max(5, len(row_labels or []) * 0.6)))
    im = ax.imshow(data, cmap=cmap, aspect='auto')

    if annotate:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, f'{data[i, j]:.2f}', ha='center', va='center',
                        fontsize=8, color='white' if abs(data[i, j]) > (data.max() + data.min()) / 2 else 'black')

    if row_labels:
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels)
    if col_labels:
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right')

    plt.colorbar(im, ax=ax)
    ax.set_title(title)

    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


def multi_panel(subplots_data, figsize=(12, 8), title='', output='multi_panel.pdf'):
    """Multi-panel figure with N×M subplots."""
    plt.rcParams.update(PUB_STYLE)

    n_rows, n_cols = subplots_data['layout']
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    axes = np.atleast_1d(axes).flatten()

    for i, panel in enumerate(subplots_data['panels']):
        ax = axes[i]
        if panel['type'] == 'bar':
            ax.bar(panel['x'], panel['y'], color=COLORS[i % len(COLORS)])
        elif panel['type'] == 'line':
            ax.plot(panel['x'], panel['y'], color=COLORS[i % len(COLORS)], marker='o', markersize=3)
        elif panel['type'] == 'scatter':
            ax.scatter(panel['x'], panel['y'], s=20, color=COLORS[i % len(COLORS)], alpha=0.7)

        ax.set_title(panel.get('title', ''), fontsize=11)
        ax.set_xlabel(panel.get('xlabel', ''))
        ax.set_ylabel(panel.get('ylabel', ''))
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for j in range(len(subplots_data['panels']), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    return output


# === Example usage ===
if __name__ == '__main__':
    # Example: grouped bar chart
    grouped_bar(
        groups=['A', 'B', 'C', 'D'],
        values_dict={'Method 1': [4.2, 3.8, 5.1, 4.9], 'Method 2': [3.9, 4.1, 4.8, 4.6]},
        xlabel='Category', ylabel='Score', title='Performance Comparison',
        output='/tmp/example_bar.pdf'
    )
    print("Example chart saved to /tmp/example_bar.pdf")
