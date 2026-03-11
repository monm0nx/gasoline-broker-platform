import numpy as np
import pytest

from backend.services.curve_builder.curve_builder import CurveBuilder

MARKET_DATA = [
    {"maturity": 1, "rate": 0.02},
    {"maturity": 2, "rate": 0.025},
    {"maturity": 3, "rate": 0.03},
    {"maturity": 5, "rate": 0.035},
]


@pytest.fixture
def builder():
    return CurveBuilder(MARKET_DATA)


class TestSplineFitting:
    def test_returns_callable(self, builder):
        x = [1, 2, 3, 5]
        y = [0.02, 0.025, 0.03, 0.035]
        cs = builder.spline_fitting(x, y)
        assert callable(cs)

    def test_interpolates_known_points(self, builder):
        x = [1.0, 2.0, 3.0]
        y = [1.0, 4.0, 9.0]
        cs = builder.spline_fitting(x, y)
        assert abs(cs(2.0) - 4.0) < 1e-6


class TestPolynomialInterpolation:
    def test_returns_callable(self, builder):
        x = [1, 2, 3]
        y = [1, 4, 9]
        poly = builder.polynomial_interpolation(x, y, degree=2)
        assert callable(poly)

    def test_degree_1_linear(self, builder):
        x = [0.0, 1.0, 2.0]
        y = [0.0, 2.0, 4.0]
        poly = builder.polynomial_interpolation(x, y, degree=1)
        assert abs(poly(1.5) - 3.0) < 1e-6


class TestBootstrapping:
    def test_returns_list(self, builder):
        result = builder.bootstrapping()
        assert isinstance(result, list)

    def test_length_matches_input(self, builder):
        result = builder.bootstrapping()
        assert len(result) == len(MARKET_DATA)

    def test_discount_factors_decreasing(self, builder):
        result = builder.bootstrapping()
        dfs = [d["discount_factor"] for d in result]
        assert all(dfs[i] > dfs[i + 1] for i in range(len(dfs) - 1))

    def test_discount_factors_between_0_and_1(self, builder):
        result = builder.bootstrapping()
        for d in result:
            assert 0 < d["discount_factor"] < 1

    def test_continuous_compounding_formula(self, builder):
        result = builder.bootstrapping()
        for entry, raw in zip(result, MARKET_DATA):
            expected_df = np.exp(-raw["rate"] * raw["maturity"])
            assert abs(entry["discount_factor"] - expected_df) < 1e-9


class TestForwardCurves:
    def test_returns_list(self, builder):
        result = builder.forward_curves()
        assert isinstance(result, list)

    def test_length_is_n_minus_1(self, builder):
        result = builder.forward_curves()
        assert len(result) == len(MARKET_DATA) - 1

    def test_forward_rates_are_positive(self, builder):
        result = builder.forward_curves()
        for entry in result:
            assert entry["forward_rate"] > 0

    def test_single_instrument_returns_empty(self):
        builder = CurveBuilder([{"maturity": 1, "rate": 0.02}])
        result = builder.forward_curves()
        assert result == []


class TestSwapCurves:
    def test_returns_list(self, builder):
        result = builder.swap_curves()
        assert isinstance(result, list)

    def test_length_is_n_minus_1(self, builder):
        result = builder.swap_curves()
        assert len(result) == len(MARKET_DATA) - 1

    def test_swap_rates_are_positive(self, builder):
        result = builder.swap_curves()
        for entry in result:
            assert entry["swap_rate"] > 0

    def test_swap_rates_less_than_one(self, builder):
        result = builder.swap_curves()
        for entry in result:
            assert entry["swap_rate"] < 1.0


class TestRecalibrate:
    def test_updates_market_data(self, builder):
        new_data = [{"maturity": 1, "rate": 0.05}, {"maturity": 2, "rate": 0.06}]
        result = builder.recalibrate(new_data)
        assert builder.market_data == new_data
        assert len(result) == 2

    def test_returns_bootstrapped_result(self, builder):
        new_data = [{"maturity": 1, "rate": 0.03}, {"maturity": 3, "rate": 0.04}]
        result = builder.recalibrate(new_data)
        expected_df = np.exp(-0.03 * 1)
        assert abs(result[0]["discount_factor"] - expected_df) < 1e-9


class TestCalculateSpread:
    def test_scalar_spread(self, builder):
        assert builder.calculate_spread(100.0, 95.0) == pytest.approx(5.0)

    def test_array_spread(self, builder):
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([0.5, 1.0, 1.5])
        result = builder.calculate_spread(a, b)
        np.testing.assert_allclose(result, [0.5, 1.0, 1.5])


class TestPriceInterpolate:
    def test_uses_curve_callable(self, builder):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 20.0, 30.0, 40.0, 50.0]
        cs = builder.spline_fitting(x, y)
        result = builder.price_interpolate(3.0, cs)
        assert abs(result - 30.0) < 1e-4
