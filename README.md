# PricePulse: Inflation-driven Pricing Strategy

## Project Overview
This project analyzes US CPI data to build forecasting models and derive pricing strategies.

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

## CI/CD Pipeline
This project includes a GitHub Actions workflow (`.github/workflows/pipeline.yml`) that:
- **CI**: Verifies code integrity on every push.
- **CD**: Runs automatically on the **15th of every month** to fetch the latest BLS data, retrain models, and regenerate the Executive Deck.
