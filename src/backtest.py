"""Backtest: seasonal-naive vs. the SARIMAX spec used in train_forecast.py.

Expanding-window, one-step-ahead evaluation of MoM inflation over the last
N_TEST months per category. Reports MAE for each model. Real BLS data only;
no significance testing is performed.
"""
import os
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")

N_TEST = 24  # months held out per category


def backtest_category(ts: pd.Series, n_test: int = N_TEST):
    """Return (seasonal_naive_mae, sarimax_mae) over the last n_test months."""
    ts = ts.copy()
    ts.index = pd.date_range(start=ts.index[0], periods=len(ts), freq="MS")
    naive_err, sarimax_err = [], []
    for i in range(len(ts) - n_test, len(ts)):
        train, actual = ts.iloc[:i], ts.iloc[i]
        naive_err.append(abs(actual - train.iloc[-12]))  # same month last year
        model = SARIMAX(train, order=(1, 0, 1), seasonal_order=(1, 0, 0, 12), trend="c",
                        enforce_stationarity=False, enforce_invertibility=False)
        pred = model.fit(disp=False).forecast(1).iloc[0]
        sarimax_err.append(abs(actual - pred))
    return float(np.mean(naive_err)), float(np.mean(sarimax_err))


def main(input_file="data/processed/inflation_features.csv", output_file="outputs/backtest.csv"):
    df = pd.read_csv(input_file, parse_dates=["date"])
    rows = []
    for cat, g in df.groupby("category"):
        ts = g.sort_values("date").set_index("date")["MoM_Inflation"].dropna()
        if len(ts) < 24 + N_TEST:
            continue
        naive, sarimax = backtest_category(ts)
        rows.append({"category": cat, "seasonal_naive_mae": naive, "sarimax_mae": sarimax,
                     "sarimax_vs_naive_pct": 100 * (naive - sarimax) / naive})
    out = pd.DataFrame(rows).round(4)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    out.to_csv(output_file, index=False)
    print(out.to_string(index=False))
    print(f"\nMean MAE  seasonal-naive: {out.seasonal_naive_mae.mean():.4f}  "
          f"SARIMAX: {out.sarimax_mae.mean():.4f}  (pp of MoM inflation, {N_TEST} one-step origins)")


if __name__ == "__main__":
    main()
