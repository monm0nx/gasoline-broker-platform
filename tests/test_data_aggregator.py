import pytest
from backend.services.market_data.data_aggregator import MarketDataAggregator


@pytest.fixture
def aggregator():
    agg = MarketDataAggregator()
    agg.fetch_data()
    return agg


class TestFetchData:
    def test_populates_data(self, aggregator):
        assert len(aggregator.data) > 0

    def test_all_sources_present(self, aggregator):
        sources = {d["source"] for d in aggregator.data}
        assert sources == {"ICE", "NYMEX", "brokers"}


class TestValidateDataQuality:
    def test_removes_non_positive_values(self):
        agg = MarketDataAggregator()
        agg.data = [{"source": "ICE", "value": 100}, {"source": "ICE", "value": -5}]
        result = agg.validate_data_quality()
        assert all(d["value"] > 0 for d in result)

    def test_keeps_positive_values(self, aggregator):
        result = aggregator.validate_data_quality()
        assert len(result) > 0


class TestHandleOutliers:
    def test_removes_outliers_above_150(self):
        agg = MarketDataAggregator()
        agg.data = [
            {"source": "ICE", "value": 100},
            {"source": "ICE", "value": 200},
        ]
        result = agg.handle_outliers()
        assert all(d["value"] <= 150 for d in result)

    def test_keeps_values_at_boundary(self):
        agg = MarketDataAggregator()
        agg.data = [{"source": "ICE", "value": 150}]
        result = agg.handle_outliers()
        assert len(result) == 1


class TestNormalizeData:
    def test_returns_only_valid_data(self, aggregator):
        result = aggregator.normalize_data()
        assert all(0 < d["value"] <= 150 for d in result)

    def test_returns_list(self, aggregator):
        assert isinstance(aggregator.normalize_data(), list)


class TestRun:
    def test_run_completes_without_error(self):
        agg = MarketDataAggregator()
        agg.run()  # Should not raise


class TestGetDataFromSource:
    def test_returns_list(self):
        agg = MarketDataAggregator()
        result = agg.get_data_from_source("ICE")
        assert isinstance(result, list)

    def test_source_label_in_result(self):
        agg = MarketDataAggregator()
        result = agg.get_data_from_source("NYMEX")
        assert all(d["source"] == "NYMEX" for d in result)
