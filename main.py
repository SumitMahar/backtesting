import datetime as dt
from logging import exception
import os.path
import sys
import math

import backtrader as bt


# Utility function for rounding up to next hundred (eg: 33427 => 33500)
def roundup_to_next_100(x):
    return int(math.ceil(x/100)) * 100


# Strategy Class
class InsideStrategyTest(bt.Strategy):
    def log(self, text, dt=None):
        '''logging function for the strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        log_file = open('log_file.txt', 'a')
        log_file.write(f"{dt}: {text}\n")
        log_file.close()

    def __init__(self):
        # Keep a reference to the "open" "high" "low" "close" line in the data[0] dataseries
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.dataclose = self.datas[0].close

    def next(self):
        self.log(
            f'open: {self.dataopen[0]}')
        self.log(f'high: {self.datahigh[0]}')
        # open of baby should be higher than the close of mother
        if (self.dataopen[0] > self.dataclose[-1]
                # Close of baby should be lesser than open of the mother
                    and self.dataclose[0] < self.dataopen[-1]
                # High of baby should be lesser than the high of the mother
                    and self.datahigh[0] < self.datahigh[-1]
                    # Low of bbaby should be higher than the low of the mother
                    and self.datalow[0] > self.datalow[-1]
                ):
            self.log('\n***Red Mother and Green Baby pattern found***')
            self.log(
                f'***open0:{self.dataopen[0]} closep1:{self.dataclose[-1]} close0:{self.dataclose[0]} highp1:{self.datahigh[-1]} high0:{self.datahigh[0]} highp1:{self.datahigh[-1]} low0:{self.datalow[0]} lowp1{self.datalow[-1]}***\n')

            self.buy()
            # open of mother should be lower than the close of the baby
        elif (self.dataopen[-1] < self.dataclose[0]
              # close of mother should be higher than open of the baby
                and self.dataclose[-1] > self.dataopen[0]
                # high of baby should be lwsser than the hight of the mother
                and self.datahigh[0] < self.datahigh[-1]
                # low of baby should be higher than the low of the mother
                and self.datalow[0] > self.datalow[-1]
              ):
            self.log('\n***Green Mother and Red Baby pattern found***')
            self.sell()


if __name__ == '__main__':
    # creating a `Cerebro` instance
    cerebro = bt.Cerebro()
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
            reverse=False
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
