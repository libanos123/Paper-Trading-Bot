
import ccxt
import pandas as pd
import time
from datetime import datetime
from Strategy_Bank import SMA_Strategy as Strategy


#------- (LIVE)-------------
class MarketData:
    def __init__(self, exchange, symbol, timeframe="1s", limit=50):
        self.exchange = exchange
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit

    def fetch(self):
        ohlcv = self.exchange.fetch_ohlcv(
            self.symbol,
            timeframe=self.timeframe,
            limit=self.limit)

        return pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"])




class Position:
    def __init__(self, side, entry_price, position_size, leverage):
        self.side = side
        self.entry_price = entry_price
        self.position_size = position_size
        self.leverage = leverage

    def unrealized_pnl(self, price):
        if self.side == "LONG":
            return (price - self.entry_price) * self.position_size * self.leverage
        else:
            return (self.entry_price - price) * self.position_size * self.leverage

    def liquidation_price(self):
        if self.side == "LONG":
            return self.entry_price * (1 - 1 / self.leverage)
        else:
            return self.entry_price * (1 + 1 / self.leverage)


#--------Account(Risk and Fees)---------

class Account:
    def __init__(self, balance, risk_per_trade=0.01, fee_rate=0.0004):
        self.balance = balance
        self.equity = balance
        self.risk_per_trade = risk_per_trade
        self.fee_rate = fee_rate
        self.position = None

        # stats
        self.trade_log = []

    def calculate_position_size(self, price, leverage):
        risk_amount = self.balance * self.risk_per_trade
        return risk_amount / price

    def open_position(self, side, price, leverage):
        size = self.calculate_position_size(price, leverage)
        fee = size * price * self.fee_rate

        self.balance -= fee
        self.position = Position(side, price, size, leverage)

        print(f"[OPEN {side}] @ {price:.2f} | Size: {size:.4f}")

    def close_position(self, price):
        pnl = self.position.unrealized_pnl(price)
        fee = self.position.position_size * price * self.fee_rate

        self.balance += pnl - fee

        self.trade_log.append(pnl)

        print(
            f"[CLOSE] @ {price:.2f} | "
            f"PnL: {pnl:.2f} | Balance: {self.balance:.2f}")

        self.position = None


#-------Paper Trading Engine--------


class PaperFuturesEngine:
    def __init__(self, market, strategy, account, leverage=10):
        self.market = market
        self.strategy = strategy
        self.account = account
        self.leverage = leverage
        self.last_timestamp = None

    def run(self):
        print("🚀 PAPER FUTURES BOT STARTED\n")

        while True:
            try:
                data = self.market.fetch()
                latest = data.iloc[-1]
                ts = latest["timestamp"]

                # only one trade per candle
                if ts == self.last_timestamp:
                    time.sleep(2)
                    continue

                self.last_timestamp = ts
                price = latest["close"]

                # update equity
                if self.account.position:
                    self.account.equity = (
                        self.account.balance
                        + self.account.position.unrealized_pnl(price)
                    )

                    # liquidation check
                    liq = self.account.position.liquidation_price()
                    if (
                        self.account.position.side == "LONG" and price <= liq
                    ):
                        print("💀 LIQUIDATED")
                        break

                signal = self.strategy.generate_signal(data)

                if signal == "BUY" and self.account.position is None:
                    self.account.open_position("LONG", price, self.leverage)

                elif signal == "SELL" and self.account.position:
                    self.account.close_position(price)

                print(
                    f"[{datetime.utcnow().strftime('%H:%M:%S')}] "
                    f"Price: {price:.2f} | "
                    f"Equity: {self.account.equity:.2f}"
                )

                time.sleep(2)

            except KeyboardInterrupt:
                print("\n🛑 Bot stopped manually")
                break

exchange = ccxt.bitget({
    "options": {"defaultType": "future"}
})

market = MarketData(exchange, "BTC/USDT", timeframe="1m")
strategy = Strategy(2,3)
account = Account(balance=1000)

engine = PaperFuturesEngine(market, strategy, account)
engine.run()

import numpy as np

trades = account.trade_log

if len(trades) == 0:
    print("No trades executed.")
else:
    total_trades = len(trades)
    wins = len([p for p in trades if p > 0])
    losses = total_trades - wins

    win_rate = wins / total_trades * 100
    total_pnl = sum(trades)
    avg_pnl = np.mean(trades)
    max_win = max(trades)
    max_loss = min(trades)

    print("📊 TRADE STATISTICS\n")
    print(f"Total Trades : {total_trades}")
    print(f"Win Rate     : {win_rate:.2f}%")
    print(f"Total PnL    : {total_pnl:.2f}")
    print(f"Avg PnL      : {avg_pnl:.2f}")
    print(f"Max Win      : {max_win:.2f}")
    print(f"Max Loss     : {max_loss:.2f}")
    print(f"Final Equity : {account.balance:.2f}")
