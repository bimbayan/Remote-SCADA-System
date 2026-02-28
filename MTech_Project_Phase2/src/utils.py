import pandas as pd

def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def split_features_labels(df, target_column):
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y
