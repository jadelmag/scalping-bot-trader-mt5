


class CandlePatterns1M:

    # ===============================
    # HELPERS
    # ===============================

    @staticmethod
    def body_size(c):
        return abs(c['close'] - c['open'])

    @staticmethod
    def upper_wick(c):
        return c['high'] - max(c['open'], c['close'])

    @staticmethod
    def lower_wick(c):
        return min(c['open'], c['close']) - c['low']

    @staticmethod
    def candle_range(c):
        return c['high'] - c['low']

    @staticmethod
    def is_bullish(c):
        return c['close'] > c['open']

    @staticmethod
    def is_bearish(c):
        return c['close'] < c['open']

    @staticmethod
    def ratio(x, y):
        return x / y if y != 0 else float('inf')

    # ===============================
    # 1) Hombre colgado (Hanging Man)
    # ===============================
    def is_hanging_man(self, c):
        b = self.body_size(c)
        lw = self.lower_wick(c)
        uw = self.upper_wick(c)
        rng = self.candle_range(c)

        if b == 0 or rng == 0:
            return False

        return (
            lw >= 2.5 * b and          # adaptado a 1M
            uw <= 0.2 * b and          # mecha superior muy pequeña
            self.ratio(max(c['open'], c['close']), c['low']) > 0.6
        )

    # ===============================
    # 2) Estrella fugaz (Shooting Star)
    # ===============================
    def is_shooting_star(self, c):
        b = self.body_size(c)
        uw = self.upper_wick(c)
        lw = self.lower_wick(c)
        rng = self.candle_range(c)

        if b == 0 or rng == 0:
            return False

        return (
            uw >= 2.5 * b and     # más estricto para 1M
            lw <= 0.2 * b and
            uw > lw               # wick superior dominante
        )

    # ===============================
    # 3) Envolvente bajista
    # ===============================
    def is_bearish_engulfing(self, prev, curr):
        if not self.is_bullish(prev) or not self.is_bearish(curr):
            return False

        return (
            curr['open'] >= prev['close'] and
            curr['close'] <= prev['open'] and
            self.body_size(curr) > self.body_size(prev)
        )

    # ===============================
    # 4) Estrella del atardecer (Evening Star)
    # ===============================
    def is_evening_star(self, c1, c2, c3):
        if not self.is_bullish(c1):
            return False

        if self.body_size(c2) > 0.6 * self.body_size(c1):
            return False

        if not self.is_bearish(c3):
            return False

        return c3['close'] < (c1['open'] + c1['close']) / 2

    # ===============================
    # 5) Tres cuervos negros
    # ===============================
    def is_three_black_crows(self, c1, c2, c3):
        if not (self.is_bearish(c1) and self.is_bearish(c2) and self.is_bearish(c3)):
            return False

        if self.body_size(c1) < 0.4 * self.candle_range(c1):
            return False

        return (
            c2['open'] < c1['open'] and
            c2['close'] < c1['close'] and
            c3['open'] < c2['open'] and
            c3['close'] < c2['close']
        )

    # ===============================
    # 6) Cubierta de nube oscura
    # ===============================
    def is_dark_cloud_cover(self, prev, curr):
        if not self.is_bullish(prev) or not self.is_bearish(curr):
            return False

        prev_mid = (prev['open'] + prev['close']) / 2
        return curr['close'] < prev_mid

    # ===============================
    # 7) Tres soldados blancos
    # ===============================
    def is_three_white_soldiers(self, c1, c2, c3):
        if not (self.is_bullish(c1) and self.is_bullish(c2) and self.is_bullish(c3)):
            return False

        if self.body_size(c1) < 0.4 * self.candle_range(c1):
            return False

        return (
            c2['open'] > c1['open'] and c2['open'] < c1['close'] and
            c3['open'] > c2['open'] and c3['open'] < c2['close']
        )

    # ===============================
    # 8) Estrella de la mañana (Morning Star)
    # ===============================
    def is_morning_star(self, c1, c2, c3):
        if not self.is_bearish(c1):
            return False

        if self.body_size(c2) > 0.6 * self.body_size(c1):
            return False

        if not self.is_bullish(c3):
            return False

        return c3['close'] > (c1['open'] + c1['close']) / 2

    # ===============================
    # 9) Penetrante
    # ===============================
    def is_piercing_pattern(self, prev, curr):
        if not self.is_bearish(prev) or not self.is_bullish(curr):
            return False

        prev_mid = (prev['open'] + prev['close']) / 2
        return curr['close'] > prev_mid

    # ===============================
    # 10) Envolvente alcista
    # ===============================
    def is_bullish_engulfing(self, prev, curr):
        if not self.is_bearish(prev) or not self.is_bullish(curr):
            return False

        return (
            curr['open'] <= prev['close'] and
            curr['close'] >= prev['open'] and
            self.body_size(curr) > self.body_size(prev)
        )

    # ===============================
    # 11) Doji
    # ===============================
    def is_doji(self, c, tol_ratio=0.12):  # 1M → 12% mejor
        rng = self.candle_range(c)
        if rng == 0:
            return False
        return self.body_size(c) <= tol_ratio * rng

    # ===============================
    # 12) Trompos (Spinning Tops)
    # ===============================
    def is_spinning_top(self, c, tol_ratio=0.35):
        rng = self.candle_range(c)
        if rng == 0:
            return False

        b = self.body_size(c)
        uw = self.upper_wick(c)
        lw = self.lower_wick(c)

        return (
            b <= tol_ratio * rng and
            uw > 0.2 * rng and
            lw > 0.2 * rng
        )

    # ===============================
    # 13) Triple formación bajista
    # ===============================
    def is_triple_bearish_top(self, peaks):
        if len(peaks) != 3:
            return False

        highs = [p['high'] for p in peaks]
        avg = sum(highs) / 3
        tol = 0.002 * avg

        return max(abs(h - avg) for h in highs) <= tol

    # ===============================
    # 14) Triple formación alcista
    # ===============================
    def is_triple_bullish_bottom(self, valleys):
        if len(valleys) != 3:
            return False

        lows = [v['low'] for v in valleys]
        avg = sum(lows) / 3
        tol = 0.002 * avg

        return max(abs(l - avg) for l in lows) <= tol

    # ===============================
    # 15) Marubozu
    # ===============================
    def is_marubozu(self, c, wick_tol=0.001):
        b = self.body_size(c)
        rng = self.candle_range(c)

        if rng == 0:
            return False

        return (
            self.upper_wick(c) <= wick_tol * rng and
            self.lower_wick(c) <= wick_tol * rng and
            b >= 0.98 * rng
        )

    # ===============================
    # 16) Pinzas inferiores (Tweezer Bottoms)
    # ===============================
    def is_tweezer_bottoms(self, prev, curr, tol=1e-5):
        return (
            abs(prev['low'] - curr['low']) <= tol and
            self.is_bearish(prev) and 
            self.is_bullish(curr)
        )

    # ===============================
    # 17) Pinzas superiores (Tweezer Tops)
    # ===============================
    def is_tweezer_tops(self, prev, curr, tol=1e-5):
        return (
            abs(prev['high'] - curr['high']) <= tol and
            self.is_bullish(prev) and
            self.is_bearish(curr)
        )

    # ===============================
    # 18) Hammer optimizado para 1M
    # ===============================
    def is_hammer(self, c):
        body = self.body_size(c)
        uw = self.upper_wick(c)
        lw = self.lower_wick(c)
        rng = self.candle_range(c)

        if body == 0 or rng == 0:
            return False

        if lw < 2.5 * body:
            return False

        if uw > 0.2 * body:
            return False

        body_top_position = c['high'] - max(c['open'], c['close'])
        return body_top_position <= rng * 0.15

    # ===============================
    # 19) Inverted Hammer
    # ===============================
    def is_inverted_hammer(self, c):
        body = self.body_size(c)
        uw = self.upper_wick(c)
        lw = self.lower_wick(c)
        rng = self.candle_range(c)

        if body == 0 or rng == 0:
            return False

        if uw < 2.5 * body:
            return False

        if lw > 0.2 * body:
            return False

        body_bottom_position = min(c['open'], c['close']) - c['low']
        return body_bottom_position <= rng * 0.15
