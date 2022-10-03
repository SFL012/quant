import pandas.io.data as web

""" Download prices from an external data source """


class MarketDataSource:
    def __init__(self):
        self.event_tick = None
        self.ticker, self.source = None, None
        self.start, self.end = None, None
        self.md = MarketData()


def start_market_simulation(self):
    data = web.DataReader(self.ticker, self.source, self.start, self.end)


for time, row in data.iterrows():
    self.md.add_last_price(time, self.ticker, row["Close"], row["Volume"])
    self.md.add_open_price(time, self.ticker, row["Open"])

if not self.event_tick is None:
    self.event_tick(self.md)
