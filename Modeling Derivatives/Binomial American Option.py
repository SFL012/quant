import math
import numpy as np


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


class BinomialTreeOption(StockOption):
    def _setup_parameters_(self):
        self.u = 1 + self.pu  # Expected value in the up state
        self.d = 1 - self.pd  # Expected value in the down state
        self.qu = (math.exp((self.r - self.div) * self.dt) - self.d) / (self.u - self.d)
        self.qd = 1 - self.qu

    def _initialize_stock_price_tree_(self):
        # Initialize a 2D tree at T=0
        self.STs = [np.array([self.S0])]

        # Simulate the possible stock prices path
        for i in range(self.N):
            prev_branches = self.STs[-1]
            st = np.concatenate((prev_branches * self.u, [prev_branches[-1] * self.d]))
            self.STs.append(st)  # Add nodes at each time step

    def _initialize_payoffs_tree_(self):
        # The payoffs when option expires
        return np.maximum(
            0,
            (self.STs[self.N] - self.K)
            if self.is_call
            else (self.K - self.STs[self.N]),
        )

    def __check_early_exercise__(self, payoffs, node):
        early_ex_payoff = (
            (self.STs[node] - self.K) if self.is_call else (self.K - self.STs[node])
        )

        return np.maximum(payoffs, early_ex_payoff)

    def _traverse_tree_(self, payoffs):
        for i in reversed(range(self.N)):
            # The payoffs from NOT exercising the option
            payoffs = (payoffs[:-1] * self.qu + payoffs[1:] * self.qd) * self.df

            # Payoffs from exercising, for American options
            if not self.is_european:
                payoffs = self.__check_early_exercise__(payoffs, i)

        return payoffs

    def __begin_tree_traversal__(self):
        payoffs = self._initialize_payoffs_tree_()
        return self._traverse_tree_(payoffs)

    def price(self):
        self._setup_parameters_()
        self._initialize_stock_price_tree_()
        payoffs = self.__begin_tree_traversal__()

        return payoffs[0]


""" RUN """
from sys import argv

if __name__ == "__main__":
    am_option = BinomialTreeOption(
        int(argv[1]),
        int(argv[2]),
        float(argv[3]),
        float(argv[4]),
        int(argv[5]),
        {"pu": 0.2, "pd": 0.2, "is_call": False},
    )
    print(am_option.price())
