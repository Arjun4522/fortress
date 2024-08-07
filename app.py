# Step 1: Install necessary packages

# Step 2: Import libraries
import pandas as pd
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import nest_asyncio

# Step 3: Define the FastAPI app
app = FastAPI()

class PredictionInput(BaseModel):
    pktcount: int
    bytecount: int
    dur: int
    dur_nsec: int
    tot_dur: int
    flows: int
    packetins: int
    pktperflow: int
    byteperflow: int
    pktrate: int
    Pairflow: int
    Protocol: str
    port_no: int
    tx_bytes: int
    rx_bytes: int
    tx_kbps: int
    rx_kbps: int
    tot_kbps: int

@app.post("/predict")
def predict(input_data: PredictionInput):
    # Load the trained model and selected features
    model = joblib.load('model.joblib')
    selected_features = joblib.load('selected_features.joblib')
    
    # Prepare the input data
    input_df = pd.DataFrame([input_data.dict()])
    
    # Encode the Protocol feature
    input_df = pd.get_dummies(input_df, columns=['Protocol'])
    
    # Ensure all expected columns are present
    for col in selected_features:
        if col not in input_df.columns:
            input_df[col] = 0
    
    # Select only the relevant features
    input_df = input_df[selected_features]
    
    # Predict using the model
    prediction = model.predict(input_df)
    
    return {"prediction": int(prediction[0])}

# Allow nested asyncio loops
nest_asyncio.apply()

# Step 4: Run the API
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
