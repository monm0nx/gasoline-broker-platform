from fastapi import FastAPI, HTTPException

app = FastAPI()

# Prices Endpoint
@app.get("/prices")
async def get_prices():
    return {"prices": "List of prices"}

# Curves Endpoint
@app.get("/curves")
async def get_curves():
    return {"curves": "List of curves"}

# Spreads Endpoint
@app.get("/spreads")
async def get_spreads():
    return {"spreads": "List of spreads"}

# Messaging Endpoint
@app.post("/messages")
async def send_message(message: dict):
    return {"message": "Message sent", "data": message}