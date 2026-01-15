from fpdf import FPDF
import pandas as pd
import os

class ExecutiveDeck(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'PricePulse: Executive Strategy Deck', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_deck(forecast_file, output_file):
    print("Creating Exective Deck...")
    pdf = ExecutiveDeck()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Load Forecast Data for Summary
    df = pd.read_csv(forecast_file)
    top_inflation = df.groupby('category')['forecast_value'].mean().sort_values(ascending=False).head(3)

    # Slide 1: Title
    pdf.add_page()
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 40, "Inflation-driven Pricing Strategy", 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, "Using BLS CPI Data & SARIMAX Forecasting", 0, 1, 'C')
    pdf.ln(20)
    pdf.cell(0, 10, "Objective: Proactive pricing and inventory management based on 6-month inflation forecasts.", 0, 1, 'C')

    # Slide 2: Executive Summary
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Executive Summary", 0, 1, 'L')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    
    # Dynamic text based on data
    highest_cat = top_inflation.index[0]
    highest_val = top_inflation.values[0]
    
    summary_points = [
        f"1. Inflation Drivers: {highest_cat} is projected to have the highest inflation ({highest_val:.2f}% MoM).",
        "2. Volatility: Energy and Transportation sectors show highest volatility, requiring flexible contracts.",
        "3. Pricing Action: Immediate price adjustments recommended for high-inflation categories to protect margins.",
        "4. Opportunity: Stable categories offer chances for promotional volume growth."
    ]
    
    for point in summary_points:
        pdf.multi_cell(0, 10, point)
        pdf.ln(5)

    # Slide 3: Inflation Forecasts
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Inflation Forecasts (Next 6 Months)", 0, 1, 'L')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 10, "Category", 1)
    pdf.cell(50, 10, "Avg MoM Forecast (%)", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 10)
    all_cats = df.groupby('category')['forecast_value'].mean().sort_values(ascending=False)
    for cat, val in all_cats.items():
        pdf.cell(80, 10, str(cat), 1)
        pdf.cell(50, 10, f"{val:.2f}%", 1)
        pdf.ln()

    # Slide 4: Strategic Recommendations
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Strategic Recommendations", 0, 1, 'L')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 11)
    recommendations = [
        ("High Inflation (>0.5% MoM)", "Increase Prices, Stockpile Inventory, Lock Supplier Rates"),
        ("Moderate Inflation (0-0.5% MoM)", "Monitor Margins, Selective Price Increases"),
        ("Deflation (<0% MoM)", "Run Promotions, renegotiate supplier contracts down")
    ]
    
    for condition, action in recommendations:
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, f"Scenario: {condition}", 0, 1)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, f"Action: {action}")
        pdf.ln(5)

    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    pdf.output(output_file)
    print(f"Created Deck at {output_file}")

if __name__ == "__main__":
    FORECAST_FILE = "outputs/forecast.csv"
    OUTPUT_FILE = "deck/PricePulse_Executive_Deck.pdf"
    
    if os.path.exists(FORECAST_FILE):
        create_deck(FORECAST_FILE, OUTPUT_FILE)
    else:
        print(f"Error: {FORECAST_FILE} not found.")
