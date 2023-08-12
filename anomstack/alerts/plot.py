"""
Helper functions to plot alerts.
"""

from matplotlib import pyplot as plt


def make_plot(df, metric_name, threshold=0.8):

    fig, axes = plt.subplots(
        nrows=2, 
        ncols=1, 
        figsize=(20, 10), 
        gridspec_kw={'height_ratios': [2, 1]}
    )
    
    df_plot = df.set_index('metric_timestamp').sort_index()
    n = len(df_plot)
    
    # Top subplot
    ax1 = df_plot['metric_value'].plot(
        title=metric_name, 
        ax=axes[0], 
        style='-o', 
        color='royalblue'
    )
    ax1.axes.get_xaxis().set_visible(False)
    ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax1.set_ylabel(metric_name)
    
    # Bottom subplot
    ax2 = df_plot['metric_score_smooth'].plot(
        title='Anomaly Score', 
        ax=axes[1], 
        rot=45, 
        linestyle='--', 
        color='seagreen', 
        label='Score Smooth'
    )
    alert_points = df_plot[df_plot['metric_alert'] == 1]
    ax2.scatter(alert_points.index, alert_points['metric_alert'], color='red', label='Alerts')
    ax2.axhline(threshold, color='lightgrey', linestyle='-.', label=f'Threshold ({threshold})')
    ax2.xaxis.set_major_locator(plt.MaxNLocator(n))
    ax2.set_xticklabels([f'{item.strftime("%Y-%m-%d %H:%M")}' for item in df_plot.index.tolist()], rotation=45)
    ax2.set_ylabel('Score')
    ax2.set_ylim(0, 1)
    ax2.legend(loc='upper left')
    ax2.grid(False)
    
    # Add point shading for alert regions
    for idx in alert_points.index:
        ax1.axvline(idx, color='yellow', alpha=0.3)
        ax2.axvline(idx, color='yellow', alpha=0.3)
    
    plt.tight_layout()
    
    return fig
