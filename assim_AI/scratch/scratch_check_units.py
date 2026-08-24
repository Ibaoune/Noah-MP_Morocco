# Author: M. EL Aabaribaoune (@um6p)
import pandas as pd
import numpy as np

def check_units():
    df = pd.read_parquet('data/processed/monthly_pixel_dataset_2016_2020_static.parquet')
    print("Rainf_tavg_OPL summary:")
    print(df['Rainf_tavg_OPL'].describe())
    print("Evap_tavg_OPL summary:")
    print(df['Evap_tavg_OPL'].describe())
    print("Qs_tavg_OPL summary:")
    print(df['Qs_tavg_OPL'].describe())
    print("Qsb_tavg_OPL summary:")
    print(df['Qsb_tavg_OPL'].describe())

if __name__ == "__main__":
    check_units()
