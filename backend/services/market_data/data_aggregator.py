class MarketDataAggregator:
    def __init__(self):
        self.sources = ['ICE', 'NYMEX', 'brokers']
        self.data = []

    def fetch_data(self):
        # Normally this would fetch data from the defined sources
        # Simulated fetch for the example
        for source in self.sources:
            data_from_source = self.get_data_from_source(source)
            self.data.extend(data_from_source)    

    def get_data_from_source(self, source):
        # Placeholder for the actual data fetching logic
        # Return simulated data
        return [{'source': source, 'value': 100}]

    def validate_data_quality(self):
        # Implement validation logic to check data quality
        return [d for d in self.data if d['value'] > 0]  # Example validation

    def handle_outliers(self):
        # Logic to identify and handle outliers
        # Placeholder logic
        return [d for d in self.data if d['value'] <= 150]

    def normalize_data(self):
        normalized_data = self.validate_data_quality()
        normalized_data = self.handle_outliers()
        return normalized_data

    def store_normalized_data(self, normalized_data):
        # Logic to store normalized data
        pass  # Placeholder for actual storage logic

    def run(self):
        self.fetch_data()
        normalized_data = self.normalize_data()
        self.store_normalized_data(normalized_data)

# Example usage:
if __name__ == '__main__':
    aggregator = MarketDataAggregator()
    aggregator.run()