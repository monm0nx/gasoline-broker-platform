import websocket
import json
import logging

class IceConnector:
    def __init__(self, api_key, base_url="wss://ice-api.ice.com/websocket", contracts=["gasoline", "crude_oil"]):
        self.api_key = api_key
        self.base_url = base_url
        self.contracts = contracts
        self.connection = None
        self.logger = self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    def connect(self):
        if self.connection is not None and self.connection.sock and self.connection.sock.connected:
            self.logger.warning("Already connected.")
            return
        self.connection = websocket.create_connection(self.base_url)
        self.logger.info("Connected to ICE WebSocket API.")

    def authenticate(self):
        auth_message = json.dumps({"action": "authenticate", "api_key": self.api_key})
        self.connection.send(auth_message)
        response = self.connection.recv()
        self.logger.info(f"Authentication response: {response}")
        return response

    def subscribe_to_prices(self):
        for contract in self.contracts:
            subscribe_message = json.dumps({"action": "subscribe", "contract": contract})
            self.connection.send(subscribe_message)
            self.logger.info(f"Subscribed to {contract} prices.")

    def handle_message(self, message):
        data = json.loads(message)
        # Process incoming price data
        self.logger.info(f"Price update: {data}")

    def run(self):
        self.connect()
        self.authenticate()
        self.subscribe_to_prices()

        while True:
            try:
                message = self.connection.recv()
                self.handle_message(message)
            except websocket.WebSocketConnectionClosedException:
                self.logger.error("Connection closed, attempting to reconnect...")
                self.reconnect()
                break
            except Exception as e:
                self.logger.error(f"Error occurred: {e}")
                self.reconnect()
                break

    def reconnect(self):
        self.connection.close()
        self.connect()
        self.authenticate()
        self.subscribe_to_prices()  

# Example usage:
# connector = IceConnector(api_key='YOUR_API_KEY')
# connector.run()