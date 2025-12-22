
# ================= STRATEGY =================
class SMA_Strategy:
    def __init__(self, swindow=5, lwindow=7):
        self.swindow = swindow
        self.lwindow = lwindow

    def generate_signal(self, data):
        if len(data) < self.lwindow:
            return "HOLD"

        short_ma = data["close"].rolling(self.swindow).mean().iloc[-1]
        long_ma = data["close"].rolling(self.lwindow).mean().iloc[-1]

        if short_ma > long_ma:
            return "BUY"
        elif short_ma < long_ma:
            return "SELL"
        return "HOLD"

class EnvelopeStrategy:
    def __init__(self, window=20, envelope_pct=0.02):
        self.window = window
        self.envelope_pct = envelope_pct

    def generate_signal(self, prices):
        if len(prices) < self.window:
            return "Hold"

        average = prices[-self.window:].mean()
        price = prices.iloc[-1]

        lower_band = average * (1 - self.envelope_pct)
        upper_band = average * (1 + self.envelope_pct)

        if price < lower_band:
            return "Buy"
        elif price > upper_band:
            return "Sell"
        else:
            return "Hold"
            