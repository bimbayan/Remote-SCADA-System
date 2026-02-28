import pandas as pd
import os 
import time 

DATA_FILE = "data/pvgis.csv"
LIVE_FILE = "data/live/current_row.csv"


def stream_from_dataset (delay = 5): 
    df = pd.read_csv(DATA_FILE)

    os.makedirs("data/live", exist_ok = True) #os code to make sure that the file exists 

    for i in range (len(df)):
        row = df.iloc[i:i+1] #one row dataframe 
        row.to_csv(LngV_FILE, index = False)
        print(f"[LIVE] Sent row {i+1}/{len(df)}: {row.to_dict('records')[0]}")
        time.sleep(delay)


if __name__ == "main":
    stream_from_dataset(delay = 5)  #basically update every 5 seconds 