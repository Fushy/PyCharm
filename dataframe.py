import pandas as pd

def add_times_datas(df, column="time", index=False):
    date_emplacement = df.index if index else df[column]
    df["datetime"] = pd.to_datetime(date_emplacement, format="%Y-%m-%d %H:%M:%S")
    df["month"], df["day_name"], df["day"], df["hour"], df["minute"], df["second"] = (
        df["datetime"].apply(lambda x: x.month),
        df["datetime"].apply(lambda x: x.strftime("%A")),
        df["datetime"].apply(lambda x: x.day),
        df["datetime"].apply(lambda x: x.hour),
        df["datetime"].apply(lambda x: x.minute),
        df["datetime"].apply(lambda x: x.second))
    return df
