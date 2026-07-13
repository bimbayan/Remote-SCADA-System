import time
import random
import pandas as pd

def generate_data():
    temperature = random.uniform(25, 45)
    irradiance = random.uniform(400, 1000)
    voltage = random.uniform(30, 40)
    current = random.uniform(5, 10)
    power = voltage * current
    timestamp = pd.Timestamp.now()

    return {
        "timestamp": timestamp,
        "temperature": temperature,
        "irradiance": irradiance,
        "voltage": voltage,
        "current": current,
        "power": power
    }

if __name__ == "__main__":
    csv_file = "sensor_data.csv"
    df = pd.DataFrame(columns=["timestamp", "temperature", "irradiance", "voltage", "current", "power"])
    df.to_csv(csv_file, index=False)

    while True:
        data = generate_data()
        df = pd.DataFrame([data])
        df.to_csv(csv_file, mode="a", header=False, index=False)
        print(data)
        time.sleep(2)
