import lightgbm as lgb
import numpy as np
import pandas as pd

if __name__ == "__main__":
    # data can be downloaded from here: https://www.openml.org/d/1169
    df = pd.read_csv("data/airline_data.csv")
    y = df.pop("Delay")
    for c in ["Airline", "Flight", "AirportFrom", "AirportTo"]:
        df[c], _ = df[c].factorize()
    df.to_csv("data/airline_data_factorized.csv")

    dataset = lgb.Dataset(
        df.astype(np.float32), label=y, categorical_feature=[0, 1, 2, 3]
    )
    model = lgb.train({"objective": "binary"}, dataset)
    model.save_model("../tests/models/airline/model.txt")