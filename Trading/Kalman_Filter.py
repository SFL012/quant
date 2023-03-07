""" Dynamic Hedge Ratio Between ETF Pairs Using the Kalman Filter               """

from __future__ import print_function

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as pdr
from pykalman import KalmanFilter


def draw_date_coloured_scatterplot(etfs, prices):
    """
    Create a scatterplot of the two ETF prices, which is
    coloured by the date of the price to indicate the
    changing relationship between the sets of prices
    """
    # Create a yellow-to-red colourmap where yellow indicates
    # early dates and red indicates later dates
    plen = len(prices)
    colour_map = plt.cm.get_cmap("YlOrRd")
    colours = np.linspace(0.1, 1, plen)

    # Create the scatterplot object
    scatterplot = plt.scatter(
        prices[etfs[0]],
        prices[etfs[1]],
        s=30,
        c=colours,
        cmap=colour_map,
        edgecolor="k",
        alpha=0.8,
    )

    # Add a colour bar for the date colouring and set the
    # corresponding axis tick labels to equal string-formatted dates
    colourbar = plt.colorbar(scatterplot)
    colourbar.ax.set_yticklabels(
        [str(p.date()) for p in prices[::plen // 9].index]
    )
    plt.xlabel(etfs[0])
    plt.ylabel(etfs[1])
    plt.show()


def calc_slope_intercept_kalman(etfs, prices):
    """
    Utilise the Kalman Filter from the PyKalman package
    to calculate the slope and intercept of the regressed
    ETF prices.
    """
    delta = 1e-5
    trans_cov = delta / (1 - delta) * np.eye(2)
    obs_mat = np.vstack([prices[etfs[0]], np.ones(prices[etfs[0]].shape)]).T[
              :, np.newaxis
              ]

    kf = KalmanFilter(
        n_dim_obs=1,
        n_dim_state=2,
        initial_state_mean=np.zeros(2),
        initial_state_covariance=np.ones((2, 2)),
        transition_matrices=np.eye(2),
        observation_matrices=obs_mat,
        observation_covariance=1.0,
        transition_covariance=trans_cov,
    )
    state_means, state_covs = kf.filter(prices[etfs[1]].values)
    return state_means, state_covs


def draw_slope_intercept_changes(prices, state_means):
    """
    Plot the slope and intercept changes from the
    Kalman Filter calculated values.

    Args:
    - prices (pd.DataFrame): DataFrame containing the prices.
    - state_means (np.ndarray): Array containing the Kalman Filter state means.
    """
    pd.DataFrame(
        dict(
            slope=state_means[:, 0],
            intercept=state_means[:, 1]
        ), index=prices.index
    ).plot(subplots=True)
    plt.show()


if __name__ == "__main__":
    # Choose the ETF symbols to work with along with
    # start and end dates for the price histories
    etf_symbols = ['TLT', 'IEI']
    start = "2010-8-01"
    end = "2016-08-01"

    # Obtain the adjusted closing prices from Yahoo finance
    try:
        etf_df1 = pdr.get_data_yahoo(etf_symbols[0], start, end)
        etf_df2 = pdr.get_data_yahoo(etf_symbols[1], start, end)
    except Exception as e:
        print(f"Error getting data from Yahoo Finance: {e}")
        exit(1)

    prices = pd.DataFrame(index=etf_df1.index)
    prices[etf_symbols[0]] = etf_df1["Adj Close"]
    prices[etf_symbols[1]] = etf_df2["Adj Close"]

    draw_date_coloured_scatterplot(etf_symbols, prices)
    state_means, state_covs = calc_slope_intercept_kalman(etf_symbols, prices)
    draw_slope_intercept_changes(prices, state_means)
