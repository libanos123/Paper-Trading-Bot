
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

