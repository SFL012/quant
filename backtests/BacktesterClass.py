import datetime as dt
import pandas as pd


class Backtester:
    def __init__(self, symbol, start_date, end_date, data_source="google"):
        self.target_symbol = symbol
        self.data_source = data_source
        self.start_dt = start_date
        self.end_dt = end_date
        self.strategy = None
        self.unfilled_orders = []
        self.positions = dict()
        self.current_prices = None
        self.rpnl, self.upnl = pd.DataFrame(), pd.DataFrame()

    def get_timestamp(self):
        return self.current_prices.get_timestamp(self.target_symbol)

    def get_trade_date(self):
        timestamp = self.get_timestamp()
        return timestamp.strftime("%Y-%m-%d")

    def update_filled_position(self, symbol, qty, is_buy, price, timestamp):
        position = self.get_position(symbol)
        position.event_fill(timestamp, is_buy, qty, price)
        self.strategy.event_position(self.positions)
        self.rpnl.loc[timestamp, "rpnl"] = position.realized_pnl

        print(
            self.get_trade_date(),
            "Filled:",
            "BUY" if is_buy else "SELL",
            qty,
            symbol,
            "at",
            price,
        )

    def get_position(self, symbol):
        if symbol not in self.positions:
            position = Position()
            position.symbol = symbol
            self.positions[symbol] = position

        return self.positions[symbol]

    def evthandler_order(self, order):
        self.unfilled_orders.append(order)

        print(
            self.get_trade_date(),
            "Received order:",
            "BUY" if order.is_buy else "SELL",
            order.qty,
            order.symbol,
        )

    def match_order_book(self, prices):
        if len(self.unfilled_orders) > 0:
            self.unfilled_orders = [
                order
                for order in self.unfilled_orders
                if self.is_order_unmatched(order, prices)
            ]

    def is_order_unmatched(self, order, prices):
        symbol = order.symbol
        timestamp = prices.get_timestamp(symbol)

        if order.is_market_order and timestamp > order.timestamp:
            # Order is matched and filled.
            order.is_filled = True
            open_price = prices.get_open_price(symbol)
            order.filled_timestamp = timestamp
            order.filled_price = open_price
            self.update_filled_position(
                symbol, order.qty, order.is_buy, open_price, timestamp
            )
            self.strategy.event_order(order)
            return False

            return True

    def print_position_status(self, symbol, prices):
        if symbol in self.positions:
            position = self.positions[symbol]
            close_price = prices.get_last_price(symbol)
            position.update_unrealized_pnl(close_price)
            self.upnl.loc[self.get_timestamp(), "upnl"] = position.unrealized_pnl

            print(
                self.get_trade_date(),
                "Net:",
                position.net,
                "Value:",
                position.position_value,
                "UPnL:",
                position.unrealized_pnl,
                "RPnL:",
                position.realized_pnl,
            )

    def evthandler_tick(self, prices):
        self.current_prices = prices
        self.strategy.event_tick(prices)
        self.match_order_book(prices)
        self.print_position_status(self.target_symbol, prices)

    def start_backtest(self):
        self.strategy = MeanRevertingStrategy(self.target_symbol)
        self.strategy.event_sendorder = self.evthandler_order

        mds = MarketDataSource()
        mds.event_tick = self.evthandler_tick
        mds.ticker = self.target_symbol
        mds.source = self.data_source
        mds.start, mds.end = self.start_dt, self.end_dt

        print("Backtesting started...")
        mds.start_market_simulation()
        print("Completed.")
