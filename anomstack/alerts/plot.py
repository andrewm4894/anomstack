"""
Helper functions to plot alerts.
"""

from matplotlib import pyplot as plt


def make_plot(df, metric_name):
    
    fig, axes = plt.subplots(
        nrows=2, 
        ncols=1, 
        figsize=(20, 10), 
        gridspec_kw={'height_ratios': [2, 1]}
    )
    df_plot = df.set_index('metric_timestamp').sort_index()
    ax1 = df_plot['metric_value'].plot(title=metric_name, ax=axes[0], style='-o')
    x_axis = ax1.axes.get_xaxis()
    x_axis.set_visible(False)
    ax2 = df_plot[['metric_score_smooth','metric_alert']].plot(
        title='metric_score_smooth', 
        ax=axes[1], 
        rot=45, 
        style=['--','o'], 
        x_compat=True
    )
    ax2.axhline(0.8, color='lightgrey', linestyle='-.')
    ax2.set_xticks(range(len(df_plot)))
    ax2.set_xticklabels([f'{item}' for item in df_plot.index.tolist()], rotation=45)
    
    return fig
