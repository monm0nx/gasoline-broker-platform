import numpy as np
from scipy.interpolate import CubicSpline, interp1d


class CurveBuilder:
    def __init__(self, market_data):
        self.market_data = market_data  # Market data for curve building

    def spline_fitting(self, x, y):
        """Fit a cubic spline to the given points x, y."""
        cs = CubicSpline(x, y)
        return cs

    def polynomial_interpolation(self, x, y, degree=3):
        """Fit a polynomial of specified degree."""
        p = np.polyfit(x, y, degree)
        return np.poly1d(p)

    def bootstrapping(self):
        """Bootstrap a discount-factor / zero curve from market instruments.

        Expects ``self.market_data`` to be a list of dicts with keys:
            ``maturity`` (float, years) and ``rate`` (float, annualised decimal).

        Returns a list of dicts with ``maturity`` and ``discount_factor``.
        """
        instruments = sorted(self.market_data, key=lambda d: d["maturity"])
        bootstrapped = []
        for inst in instruments:
            t = float(inst["maturity"])
            r = float(inst["rate"])
            # Simple continuous compounding: DF = e^(-r*t)
            df = float(np.exp(-r * t))
            bootstrapped.append({"maturity": t, "discount_factor": df})
        return bootstrapped

    def recalibrate(self, new_data):
        """Recalibrate the existing curves based on new data."""
        self.market_data = new_data
        return self.bootstrapping()

    def forward_curves(self):
        """Construct a forward-rate curve from bootstrapped discount factors.

        Returns a list of dicts with ``maturity`` and ``forward_rate``.
        """
        bootstrapped = self.bootstrapping()
        if len(bootstrapped) < 2:
            return []

        forward_rates = []
        for i in range(1, len(bootstrapped)):
            t1 = bootstrapped[i - 1]["maturity"]
            t2 = bootstrapped[i]["maturity"]
            df1 = bootstrapped[i - 1]["discount_factor"]
            df2 = bootstrapped[i]["discount_factor"]
            dt = t2 - t1
            if dt > 0 and df2 > 0:
                # Continuously compounded forward rate between t1 and t2
                forward_rate = float(np.log(df1 / df2) / dt)
            else:
                forward_rate = 0.0
            forward_rates.append({"maturity": float(t2), "forward_rate": forward_rate})
        return forward_rates

    def swap_curves(self):
        """Construct par-swap rates from the bootstrapped discount-factor curve.

        Returns a list of dicts with ``maturity`` and ``swap_rate``.
        """
        bootstrapped = self.bootstrapping()
        if not bootstrapped:
            return []

        maturities = np.array([d["maturity"] for d in bootstrapped])
        discount_factors = np.array([d["discount_factor"] for d in bootstrapped])

        swap_rates = []
        for i in range(1, len(bootstrapped)):
            # Annuity = sum of discount factors from period 1 … i
            annuity = float(np.sum(discount_factors[: i + 1]))
            df_final = float(discount_factors[i])
            if annuity > 0:
                # Par swap rate: S = (1 - DF_n) / annuity
                swap_rate = (1 - df_final) / annuity
            else:
                swap_rate = 0.0
            swap_rates.append({"maturity": float(maturities[i]), "swap_rate": float(swap_rate)})
        return swap_rates

    def calculate_spread(self, curve_a, curve_b):
        """Calculate spreads between two curves (numpy arrays or callables)."""
        return curve_a - curve_b

    def price_interpolate(self, maturity, curve):
        """Interpolate price at a specific maturity using a callable curve."""
        return curve(maturity)


# Sample usage (outside class):
# market_data = [{"maturity": 1, "rate": 0.02}, {"maturity": 2, "rate": 0.025}]
# curve_builder = CurveBuilder(market_data)