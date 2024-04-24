import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def one_title_data(data: pd.DataFrame, book_name: str | None = None) -> pd.DataFrame:
    if book_name is None:
        data_filtered = data.copy()
    else:
        data_filtered = data[data.title == book_name].copy()

    data_filtered.duration = pd.to_timedelta(data_filtered.duration)
    data_filtered.start = pd.to_datetime(data_filtered.start)
    data_filtered.end = pd.to_datetime(data_filtered.end)

    return data_filtered


def get_summary_by_day(
        data: pd.DataFrame,
        col: str = 'duration_frac'
) -> pd.DataFrame:
    ####
    temp_ = (
        data
        .groupby(
            by=data.start.dt.floor('d')
        )[col]
        .sum()
    )

    start_date = data.start.dt.floor('d').min()
    end_date = data.end.dt.floor('d').max()

    idx_ = pd.date_range(
        start=start_date,
        end=end_date,
    )

    s = temp_.reindex(idx_, fill_value=0)
    temp_df_ = pd.DataFrame(s).reset_index()
    return temp_df_

##### PLOTTING

def generate_plot(
        data: pd.DataFrame,
        book_name: str,
        x: str='index',
        y: str='duration_frac',
        figsize: tuple=(6,4),
):
    f, ax = plt.subplots(
        figsize=figsize,
    )

    sns.barplot(
        data=data,
        x='index',
        y='duration_frac',
        color='green',
        ax=ax,
    )

    # Axis formatting
    x_dates = [
        t.strftime('%D')
        for t in sorted(
            data['index'].unique().tolist()
        )
    ]
    ax.set_xticklabels(
        labels=x_dates,
    )

    #
    ax.set_title(
        f'Reading Journey of `{book_name}`'
        f'\n{data.duration_frac.sum():.2f}hrs'
        f' over {x_dates[0]} - {x_dates[-1]}'
    )
    ax.set_ylabel('Hours Read')
    ax.set_xlabel('Date')

    f.tight_layout()
    f.autofmt_xdate()
    return f,ax

def get_year_data(data, year=2024):
    df_yr = data[
        (data.start < f'{year+1}-01-01') &
        (data.start >= f'{year}-01-01') 
    ]

    # Add in 'dummy' weeks to fill up the gap
    df_temp = pd.DataFrame(columns=['weekday', 'week', 'activity'])
    df_temp.week = np.arange(0,52)
    df_orig = pd.DataFrame(columns=df_temp.columns)
    # Offset by one for display (starts at zero)
    df_orig['week'] = df_yr.start.dt.strftime('%W').astype(int) - 1
    # Monday is the first day of the week now (starts at zero)
    df_orig['weekday'] = (df_yr.start.dt.strftime('%w').astype(int) - 1) % 7
    df_orig['activity'] = df_yr.duration_frac
    df_new = pd.concat([
        df_temp, 
        df_orig,
    ])

    # Reshape the data and plot it
    df_pivot = df_new.pivot_table(
        columns="week",
        index="weekday",
        values="activity",
        aggfunc='sum',
        dropna=False,
        sort=True,
    )
    df_pivot.fillna(0, inplace=True)

    return df_pivot.sort_values('weekday', ascending=False)
