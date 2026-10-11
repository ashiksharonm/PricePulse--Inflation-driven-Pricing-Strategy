# PricePulse: Inflation-driven Pricing Strategy

## Project Overview
This project analyzes US CPI data (8 BLS CPI series: Headline CPI, Food, Energy, Gasoline, Shelter, Apparel, New Vehicles, Used Cars and Trucks; see `src/extract_bls.py`) to build forecasting models and derive pricing strategies.

## Data Source
- US Bureau of Labor Statistics (BLS)

## Structure
- `data/`: Raw and processed data.
- `src/`: Source code for extraction, transformation, and modeling.
- `notebooks/`: Jupyter notebooks for analysis and strategy.
- `outputs/`: Generated forecasts and plots.
- `excel_model/`: ROI simulation models.
- `deck/`: Executive presentation.

## How to Run

1. **Setup**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Data Pipeline**:
   ```bash
   python src/extract_bls.py   # Fetch Data
   python src/transform.py     # Clean & Feature Engineer
   python src/train_forecast.py # Train Models & Forecast
   python src/backtest.py      # Seasonal-naive vs SARIMAX backtest (optional)
   ```

3. **Analysis & Strategy**:
   - Open `notebooks/01_insights.ipynb` for EDA.
   - Open `notebooks/02_strategy.ipynb` for strategy logic.

4. **Generate Deliverables**:
   ```bash
   python src/create_roi_model.py # Creates excel_model/pricing_roi_model.xlsx
   python src/create_deck.py      # Creates deck/PricePulse_Executive_Deck.pdf
   ```

## Outputs
- **Forecasts**: `outputs/forecast.csv`
- **ROI Model**: `excel_model/pricing_roi_model.xlsx` (Simulate pricing impact)
- **Executive Deck**: `deck/PricePulse_Executive_Deck.pdf` (Consulting-style summary)

## Forecast Backtest
`src/backtest.py` compares a seasonal-naive baseline (same month last year) against the SARIMAX(1,0,1)(1,0,0,12) spec in `train_forecast.py`, using expanding-window one-step-ahead forecasts of MoM inflation over the last 24 months per series (BLS data through 2026-08). Output: `outputs/backtest.csv`.

| Series | Seasonal-naive MAE | SARIMAX MAE |
|---|---|---|
| Apparel | 1.1182 | 1.1195 |
| Energy | 2.5108 | 1.8603 |
| Food | 0.1717 | 0.1672 |
| Gasoline | 5.0116 | 3.4582 |
| Headline CPI | 0.2437 | 0.1919 |
| New Vehicles | 0.1668 | 0.1386 |
| Shelter | 0.1338 | 0.1133 |
| Used Cars and Trucks | 1.1920 | 0.6018 |
| **Mean** | **1.3186** | **0.9564** |

MAE is in percentage points of month-over-month inflation. SARIMAX is better on 7 of 8 series (Apparel is a tie, marginally worse); the mean MAE is 27% lower. This is a single backtest with no significance test, so treat it as indicative.

## CI/CD Pipeline
This project includes a GitHub Actions workflow (`.github/workflows/pipeline.yml`) that:
- **CI**: Verifies code integrity on every push.
- **CD**: Runs automatically on the **15th of every month** to fetch the latest BLS data, retrain models, and regenerate the Executive Deck.
