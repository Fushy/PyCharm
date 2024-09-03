import pandas as pd
from openpyxl.reader.excel import load_workbook
from pandas import DataFrame

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

def from_excel_to_dataframe(file_name: str) -> DataFrame:
    workbook = load_workbook(file_name)
    data = workbook.active.values
    headers = next(data)
    return pd.DataFrame(data, columns=headers)

# df.rename(columns={'OldColumnName': 'NewColumnName'})
# qa = dataframe.groupby('questions')['answers'].agg(list).to_dict()