# Gasoline Broker Platform

## Architecture Diagram
![Architecture Diagram](path/to/architecture_diagram.png)

## Tech Stack
- **Frontend**: React.js
- **Backend**: Node.js, Express
- **Database**: MongoDB
- **API integration**: ICE API

## Installation Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/monm0nx/gasoline-broker-platform.git
   cd gasoline-broker-platform
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory and set the following variables:
   ```plaintext
   PORT=3000
   ICE_API_KEY=your_api_key_here
   ```

4. **Start the application**
   ```bash
   npm run start
   ```

## ICE API Integration Guide

### Configuration

1. **Sign up for ICE API**: Visit [ICE API](https://iceapi.com) and sign up for an account to obtain your API key.

2. **Adding the API Key to your application**: Use the above instructions to set your API key in the `.env` file.

### Authentication Flow Example

1. **Requesting a token**
   Make a POST request to the following endpoint:
   ```http
   POST https://api.ice.com/auth/token
   ```
   **Request Body**
   ```json
   {
      "api_key": "your_api_key_here"
   }
   ```
   **Response**
   ```json
   {
      "token": "your_jwt_token_here"
   }
   ```

2. **Using the token**
   Include the token in the header of your subsequent requests:
   ```http
   GET https://api.ice.com/data
   Authorization: Bearer your_jwt_token_here
   ```

### Conclusion
Follow the steps outlined above to successfully set up the Gasoline Broker Platform and integrate with ICE APIs.
