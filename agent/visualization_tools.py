"""
Advanced visualization tools for the Olist Data Analyzer Agent.
These tools create visualizations using matplotlib and seaborn.
Saves images to disk and returns full file paths.
"""

import json
import os
import uuid
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create output directory for visualizations
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'viz_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create output directory for visualizations
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'viz_outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _parse_data(data):
    """Parse data from various formats into a list of dictionaries."""
    # If it's already a list or dict, return as-is
    if isinstance(data, (list, dict)):
        return data
    
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            # If it's not valid JSON, try to parse it as a Python literal
            import ast
            try:
                return ast.literal_eval(data)
            except:
                raise ValueError(f"Could not parse data. Expected JSON string or list of dicts. Got: {data[:100]}")
    return data


def _save_figure(fig):
    """Save matplotlib figure to disk and return the full file path."""
    # Generate unique filename
    filename = f"viz_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Save figure
    fig.savefig(filepath, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    # Return the full absolute path
    return os.path.abspath(filepath)


def create_bar_chart(data: str, x_column: str, y_column: str, 
                     title: str, x_label: str = "", y_label: str = "",
                     orientation: str = 'v') -> str:
    """
    Create a bar chart visualization.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Chart title
        x_label: X-axis label (optional)
        y_label: Y-axis label (optional)
        orientation: 'v' for vertical, 'h' for horizontal
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if orientation == 'h':
        ax.barh(df[x_column], df[y_column], color='steelblue')
        ax.set_xlabel(y_label or y_column)
        ax.set_ylabel(x_label or x_column)
    else:
        ax.bar(df[x_column], df[y_column], color='steelblue')
        ax.set_xlabel(x_label or x_column)
        ax.set_ylabel(y_label or y_column)
        plt.xticks(rotation=45, ha='right')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    if orientation == 'h':
        for i, v in enumerate(df[y_column]):
            ax.text(v, i, f' {v:,.0f}', va='center')
    else:
        for i, v in enumerate(df[y_column]):
            ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    return _save_figure(fig)


def create_line_chart(data: str, x_column: str, y_columns: str,
                      title: str, x_label: str = "", y_label: str = "") -> str:
    """
    Create a line chart with one or more lines.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        x_column: Column name for x-axis (typically time)
        y_columns: Comma-separated column names for y-axis values
        title: Chart title
        x_label: X-axis label (optional)
        y_label: Y-axis label (optional)
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    y_cols = [col.strip() for col in y_columns.split(',')]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    for col in y_cols:
        if col in df.columns:
            ax.plot(df[x_column], df[col], marker='o', linewidth=2, markersize=6, label=col)
    
    ax.set_xlabel(x_label or x_column, fontsize=12)
    ax.set_ylabel(y_label or 'Value', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return _save_figure(fig)


def create_pie_chart(data: str, values_column: str, names_column: str,
                     title: str) -> str:
    """
    Create a pie chart.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        values_column: Column name for values
        names_column: Column name for labels
        title: Chart title
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = sns.color_palette('Set3', len(df))
    
    wedges, texts, autotexts = ax.pie(
        df[values_column], 
        labels=df[names_column],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
    
    plt.tight_layout()
    return _save_figure(fig)


def create_heatmap(data: str, x_column: str, y_column: str,
                   value_column: str, title: str) -> str:
    """
    Create a heatmap visualization.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        x_column: Column for x-axis
        y_column: Column for y-axis
        value_column: Column for values (colors)
        title: Chart title
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    pivot_df = df.pivot_table(
        index=y_column,
        columns=x_column,
        values=value_column,
        aggfunc='sum'
    )
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(pivot_df, annot=True, fmt='.0f', cmap='YlOrRd', 
                linewidths=0.5, ax=ax, cbar_kws={'label': value_column})
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel(x_column, fontsize=12)
    ax.set_ylabel(y_column, fontsize=12)
    
    plt.tight_layout()
    return _save_figure(fig)


def create_scatter_plot(data: str, x_column: str, y_column: str,
                        title: str, x_label: str = "", y_label: str = "") -> str:
    """
    Create a scatter plot.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        x_column: Column for x-axis
        y_column: Column for y-axis
        title: Chart title
        x_label: X-axis label (optional)
        y_label: Y-axis label (optional)
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ax.scatter(df[x_column], df[y_column], alpha=0.6, s=100, color='steelblue')
    
    ax.set_xlabel(x_label or x_column, fontsize=12)
    ax.set_ylabel(y_label or y_column, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return _save_figure(fig)


def create_histogram(data: str, column: str, title: str, bins: int = 30) -> str:
    """
    Create a histogram showing data distribution.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        column: Column name to analyze
        title: Chart title
        bins: Number of bins for histogram
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    sns.histplot(df[column], bins=bins, kde=True, ax=ax, color='steelblue')
    
    ax.set_xlabel(column, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return _save_figure(fig)


def create_box_plot(data: str, value_column: str, 
                    category_column: str = "", title: str = "") -> str:
    """
    Create box plots to show distribution and outliers.
    
    Args:
        data: JSON string containing list of dictionaries with the data
        value_column: Column with numeric values
        category_column: Column to group by (optional)
        title: Chart title
    
    Returns:
        Full absolute file path to the saved PNG image.
        Extract just the filename and include it in your response using the format: [VIZ:filename.png]
        
    """
    data_list = _parse_data(data)
    df = pd.DataFrame(data_list)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    if category_column and category_column in df.columns:
        sns.boxplot(data=df, x=category_column, y=value_column, ax=ax, palette='Set2')
        plt.xticks(rotation=45, ha='right')
        final_title = title or f'Distribution of {value_column} by {category_column}'
    else:
        sns.boxplot(data=df, y=value_column, ax=ax, color='steelblue')
        final_title = title or f'Distribution of {value_column}'
    
    ax.set_title(final_title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return _save_figure(fig)
