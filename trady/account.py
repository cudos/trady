# -*- coding: utf-8 -*-



class Account(object):
    """The portfolio account.

    Args:
        cash (float): Total amount of cash available for trading
            stocks with. A negative cash value indicates that you are
            borrowing from your margin account.
        margin (float): ...

    """
    def __init__(self, cash, commission, day=0, margin_rate=None):
        self.cash = float(cash)
        self.day = day
        self.margin_rate = float(margin_rate)
        self.commission = commission
        self.starting_account_value = self.account_value

    def trade_stock(self):
        pass

    def trade_option(self):
        pass

    def short_stock(self):
        pass

    def increase_day(self):
        self.day += 1

    @property
    def buying_power(self):
        """The total value of your cash and margin accounts that can be used
        to trade stocks. Negative buying power indicates that no
        further trading can be performed and that margin call will
        occur.

        """
        return self.cash + (self.market_value_of_stocks * self.margin_rate) - (self.market_value_of_short_stocks * (1.0 + self.margin_rate))

    @property
    def account_value(self):
        """Your portfolio's current value.

        """
        return self.cash + self.value_of_stocks + self.value_of_options - self.value_of_short_stocks

    @property
    def market_value_of_stocks(self):
        return 0

    @property
    def market_value_of_options(self):
        return 0

    @property
    def market_value_of_short_stocks(self):
        return 0

    @property
    def annual_return(self):
        """Amount of returns generated if your current rate of returns were
        extrapolated for an entire year.

        """
        return math.pow(self.account_value / self.starting_account_value, 365.0 / self.day) - 1

    def set_stop_loss(self, stop_amount):
        """Set a safety stop loss for both long and short positions.

        Args:
            stop_amount (float): The safety stop in dollar.

        """
        pass

    def set_profit_target(self, profit_amount):
        """Set a profit target for both long and short positions.

        Args:
            profit_amount (float): The profit target in dollar.

        """
        pass

    def market_position(self, n):
        """Returns whether the strategy is currently flat, short, or long on
        the current bar or for `n` closed positions ago.

        Returns: int: The market position. Values are: -1 for a short
            position. 1 for a long position. 0 for flat (no position).

        """
        pass
