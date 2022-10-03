from BacktesterClass import Backtester

backtester = Backtester("AAPL", dt.datetime(2019, 1, 1), dt.datetime(2019, 12, 31))

backtester.start_backtest()
