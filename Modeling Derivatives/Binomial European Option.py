""" Store common attributes of a stock option """
import math


class StockOption(object):
    def __init__(self, S0, K, r, T, N, params):
        self.S0 = S0
        self.K = K
        self.r = r
        self.T = T
        self.N = max(1, N)  # Ensure N have at least 1 time step
        self.STs = None  # Declare the stock prices tree
        """ Optional parameters used by derived classes """
        self.pu = params.get("pu", 0)  # Probability of up state
        self.pd = params.get("pd", 0)  # Probability of down state

        self.div = params.get("div", 0)  # Dividend yield
        self.sigma = params.get("sigma", 0)  # Volatility
        self.is_call = params.get("is_call", True)  # Call or put
        self.is_european = params.get("is_eu", True)  # Eu or Am
        """ Computed values """
        self.dt = T / float(N)  # Single time step, in years
        self.df = math.exp(-(r - self.div) * self.dt)  # Discount factor


""" Price a European option by the binomial tree model """
from StockOption import StockOption

import math
import numpy as np


class BinomialEuropeanOption(StockOption):
    def __setup_parameters__(self):
        """ Required calculations for the model """
        self.M = self.N + 1  # Number of terminal nodes of tree
        self.u = 1 + self.pu  # Expected value in the up state
        self.d = 1 - self.pd  # Expected value in the down state
        self.qu = (math.exp((self.r - self.div) * self.dt) - self.d) / (self.u - self.d)
        self.qd = 1 - self.qu

    def _initialize_stock_price_tree_(self):
        # Initialize terminal price nodes to zeros
        self.STs = np.zeros(self.M)
        # Calculate expected stock prices for each node
        for i in range(self.M):
            self.STs[i] = self.S0 * (self.u ** (self.N - i)) * (self.d ** i)

    def _initialize_payoffs_tree_(self):
        # Get payoffs when the option expires at terminal nodes
        payoffs = np.maximum(
            0, (self.STs - self.K) if self.is_call else (self.K - self.STs)
        )
        return payoffs

    def _traverse_tree_(self, payoffs):
        # Starting from the time the option expires, traverse
        # backwards and calculate discounted payoffs at each node
        for i in range(self.N):
            payoffs = (payoffs[:-1] * self.qu + payoffs[1:] * self.qd) * self.df
        return payoffs

    def __begin_tree_traversal__(self):
        payoffs = self._initialize_payoffs_tree_()
        return self._traverse_tree_(payoffs)

    def price(self):
        """ The pricing implementation """
        self.__setup_parameters__()
        self._initialize_stock_price_tree_()
        payoffs = self.__begin_tree_traversal__()
        return payoffs[0]  # Option value converges to first node


""" RUN """
from sys import argv

if __name__ == "__main__":
    eu_option = BinomialEuropeanOption(
        int(argv[1]),
        int(argv[2]),
        float(argv[3]),
        float(argv[4]),
        int(argv[5]),
        {"pu": 0.2, "pd": 0.2, "is_call": False},
    )
    print(eu_option.price())
