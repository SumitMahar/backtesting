import datetime as dt
from logging import exception
import os.path
import sys
import math

import backtrader as bt


# Utility function for rounding up to the nearest hundred (eg: 33449 => 33400, 33451 => 33500)
def round_to_nearest_100(x):
    return int(round(x/100)) * 100


def calculate_ce_strike(close):
    # eg: if the close value is 35678 round it to 35700 and add 200
    # so the strike will be 35900 CE
    strike = round_to_nearest_100(close) + 200
    return {'strike': strike, 'type': 'CE'}


def calculate_pe_strike(close):
    # eg: if the close value is 35678 round it to 35700 and add 200
    # so the strike will be 35500 PE
    strike = round_to_nearest_100(close) - 200
    return {'strike': strike, 'type': 'PE'}


def calculate_tp(high, low, percent, op_type):
    '''
        high: int (high of the mother candle)
        low: int  (low of the mother candle)
        percent: int
        op_type: string ('CE or PE')
    '''
    tp = (high - low) * (percent/100)
    if op_type == 'CE':
        return high + tp
    elif op_type == 'PE':
        return high - tp


# Strategy Class
class InsideStrategyTest(bt.Strategy):
    def __init__(self):
        # Keep a reference to the "open" "high" "low" "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

    def log(self, text, dt=None):
        '''logging function for the strategy'''
        dt = dt or self.datas[0].datetime.date()
        log_file = open('log_file.txt', 'a')
        log_file.write(f"{dt}: {text}\n")
        log_file.close()

    def next(self):
        self.log(
            f'open: {self.dataopen[0]}')
        self.log(f'high: {self.datahigh[0]}')

        # Inside Candle logic
        if (
            # open of baby should be higher than the close of mother
            self.dataopen[0] > self.dataclose[-1]
            # Close of baby should be lesser than open of the mother
            and self.dataclose[0] < self.dataopen[-1]
            # High of baby should be lesser than the high of the mother
            and self.datahigh[0] < self.datahigh[-1]
            # Low of bbaby should be higher than the low of the mother
            and self.datalow[0] > self.datalow[-1]
        ):
            self.log('\n***Red Mother and Green Baby pattern found***')
            self.log(
                f'***current candle open: {self.dataopen[0]} previous candle close: {self.dataclose[-1]} C C close: {self.dataclose[0]} prev C high: {self.datahigh[-1]} C C high: {self.datahigh[0]} prev C highp: {self.datahigh[-1]} C C low: {self.datalow[0]} prev C low: {self.datalow[-1]}***\n')

            self.buy()

        elif (
            # open of mother should be lower than the close of the baby
            self.dataopen[-1] < self.dataclose[0]
            # close of mother should be higher than open of the baby
            and self.dataclose[-1] > self.dataopen[0]
            # high of baby should be lesser than the hight of the mother
            and self.datahigh[0] < self.datahigh[-1]
            # low of baby should be higher than the low of the mother
            and self.datalow[0] > self.datalow[-1]
        ):
            self.log('\n***Green Mother and Red Baby pattern found***')
            self.sell()

        # Engulfing Candle logic
        # Green Engulfing
        elif (
            # `data[0]` represents current candle and `data[-1]` represents previous candle
            # Open of the mother should be lower than the close of the baby
            self.dataopen[0] < self.dataclose[-1]
            # Close of the mother should be higher than the open of the baby
            and self.dataclose[0] > self.dataopen[-1]
            # High of mother should be higher than the high of the baby
            and self.datahigh[0] > self.datahigh[-1]

        ):  # logic for what to do after the Green Engulfing pattern is found goes here
            self.log('\n***Green Engulfing pattern found***')
            self.buy()
        # Red Engulfing
        elif (
            # Open of the mother should be higher than the close of the baby
            self.dataopen[0] > self.dataclose[-1]
            # Close of the mother should be lower than the open of the baby
            and self.dataclose[0] < self.dataopen[-1]
            # High of mother should be higher than the high of the baby
            and self.datahigh[0] > self.datahigh[-1]
        ):
            self.log('\n***Red Engulfing pattern found***')
            self.sell()


if __name__ == '__main__':
    # creating a `Cerebro` instance
    cerebro = bt.Cerebro()
    # initial dummy cash
    cerebro.broker.setcash(200000)

    # Adding Strategy
    cerebro.addstrategy(InsideStrategyTest)

    # settinig up data path
    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join('datas/HistoData.csv')

    # creating a Data Feed
    try:
        data = bt.feeds.GenericCSVData(
            dataname=datapath,
            fromdate=dt.datetime(2021, 12, 1),
            todate=dt.datetime(2022, 2, 18),
            nullvalue=0.0,
            dtformat=('%Y-%m-%d %H:%M:%S'),
            # columns containg the ohlc etc
            datetime=1,
            open=4,
            high=5,
            low=6,
            close=7,
            volume=8,
            reverse=True
        )

        cerebro.adddata(data)

        with open('log_file.txt', 'a') as log_file:
            log_file.write(
                f'Starting Portfolio Value: {cerebro.broker.getvalue()}\n'
            )
            cerebro.run()
            log_file.write(
                f'Final Portfolio Value: {cerebro.broker.getvalue()}\n'
            )
    except Exception as e:
        print('**Error**:', e)
