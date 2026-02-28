import sys, os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils import load_data, split_features_labels


import pickle
from sklearn.linear_model import LinearRegression


def train_and_save_model(data_path, target_column, model_path):
    df = load_data(data_path)
    X, y = split_features_labels(df, target_column)

    model = LinearRegression()
    model.fit(X, y)

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print("Model trained and saved successfully!")

if __name__ == "__main__":
    train_and_save_model("data/your_dataset1.csv", "Output", "trainedmodel.pkl")

