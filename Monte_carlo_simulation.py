"""
Project: Corporate Credit Risk Analysis Framework (Merton Model & Monte Carlo)
Author: Mai Tran
Description: Automated tool to calculate Distance to Default and PD using 
             Black-Scholes-Merton equations and Monte Carlo Stress Testing.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import fsolve

class MertonCreditModel:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.T = 1.0  # 1-year horizon

    def fetch_data(self):
        """1. Fetch Real-time Market & Financial Data (Enhanced for Global Markets)"""
        print(f"\n--- [1/3] Fetching Data for {self.ticker} ---")
        t = yf.Ticker(self.ticker)
        
        # 1. Market Cap (Equity)
        self.E = t.info.get('marketCap') or t.info.get('enterpriseValue')
        if not self.E:
            raise ValueError(f"Could not find Market Value for {self.ticker}.")

        # 2. Get Balance Sheet (Quarterly or Annual)
        bs = t.quarterly_balancesheet
        if bs.empty:
            bs = t.balancesheet
        
        # Helper function to find row names that might differ between companies
        def get_row(possible_names):
            for name in possible_names:
                if name in bs.index:
                    return bs.loc[name].iloc[0]
            return None

        # 3. Calculate Debt Threshold (D)
        st_debt = get_row(['Short Long Term Debt', 'Current Debt', 'ShortTermDebt']) or 0
        lt_debt = get_row(['Long Term Debt', 'LongTermDebt']) or 0
        
        if st_debt + lt_debt > 0:
            self.D = st_debt + (0.5 * lt_debt)
        else:
            # Fallback to Total Assets - Equity if debt breakdown is missing
            assets = get_row(['Total Assets', 'TotalAssets'])
            equity = get_row(['Stockholders Equity', 'Total Equity Gross Minority Interest'])
            if assets and equity:
                self.D = (assets - equity) * 0.5
            else:
                # Last resort fallback
                total_liab = get_row(['Total Liab', 'Total Liabilities Net Minority Interest'])
                self.D = (total_liab * 0.5) if total_liab else None

        if not self.D:
            raise ValueError(f"Financial data (Debt/Assets) unavailable for {self.ticker}.")

        # 4. Volatility (sigma_E)
        hist = t.history(period="1y")
        if hist.empty: raise ValueError(f"No price history for {self.ticker}.")
        self.sigma_E = hist['Close'].pct_change().std() * np.sqrt(252)

        # 5. Risk-free rate
        try:
            r_data = yf.Ticker("^IRX").history(period="1d")
            self.r = r_data['Close'].iloc[-1] / 100
        except:
            self.r = 0.04 # Default 4% if API fails. 
          """This is based on historical average of SOFR during 2025 - 2026, 
          ensuring model still have benchmark if API cannot fetch data."""

        print(f"Equity: {self.E:,.0f} | Debt: {self.D:,.0f} | Vol: {self.sigma_E:.2%}")

    def solve_merton(self): 
        """2. Solve Merton Simultaneous Equations"""
        def equations(vars):
            V, sigma_V = vars
            d1 = (np.log(V/self.D) + (self.r + 0.5 * sigma_V**2) * self.T) / (sigma_V * np.sqrt(self.T))
            d2 = d1 - sigma_V * np.sqrt(self.T)
            eq1 = V * norm.cdf(d1) - self.D * np.exp(-self.r * self.T) * norm.cdf(d2) - self.E
            eq2 = (V / self.E) * norm.cdf(d1) * sigma_V - self.sigma_E
            return [eq1, eq2]

        # Initial guess: V = E+D, sigma_V = sigma_E
        self.V, self.sigma_V = fsolve(equations, [self.E + self.D, self.sigma_E])
        
        # Distance to Default (DD) & Probability of Default (PD)
        self.DD = (np.log(self.V/self.D) + (self.r - 0.5 * self.sigma_V**2) * self.T) / (self.sigma_V * np.sqrt(self.T))
        self.PD = norm.cdf(-self.DD)
        
        print(f"Asset Value (V): {self.V:,.0f} | DD: {self.DD:.2f} | PD: {self.PD:.4%}")

    def run_monte_carlo(self, iterations=10000):
        """3. Monte Carlo Simulation"""
        Z = np.random.standard_normal(iterations)
        V_T = self.V * np.exp((self.r - 0.5 * self.sigma_V**2) * self.T + self.sigma_V * np.sqrt(self.T) * Z)
        
        
        pd_simulated = np.mean(V_T < self.D)
        print(f"\n--- Monte Carlo Results for {self.ticker} ---")
        print(f"Theoretical PD (Merton): {self.PD:.4%}")
        print(f"Simulated PD (Monte Carlo): {pd_simulated:.4%}")
        
        plt.figure(figsize=(10, 5))
        plt.hist(V_T, bins=60, color='navy', alpha=0.6, label="Asset Value Scenarios")
        plt.axvline(self.D, color='red', linestyle='--', label=f"Debt Threshold")
        plt.title(f"Simulation: {self.ticker}")
        plt.xlabel("Projected Asset Value (T=1)")
        plt.ylabel("Frequency")
        plt.legend()
        plt.show()

# --- MAIN EXECUTION (MULTI-TICKER READY) ---
if __name__ == "__main__":
    user_input = input("Enter stock tickers, separated by commas (e.g., AAPL,MSFT,TSLA): ")
    ticker_list = [t.strip().upper() for t in user_input.split(',')]
    
    portfolio_results = []

    for ticker in ticker_list:
        try:
            model = MertonCreditModel(ticker)
            model.fetch_data()
            model.solve_merton()
            
            # Show simulation only if PD > 1%, otherwise it's too many pop-ups
            if model.PD > 0.01: 
                print(f"High Risk Detected for {ticker}. Running Monte Carlo Stress Test...")
                model.run_monte_carlo()
            else:
                print(f"{ticker} is safe. Skipping simulation.")
            
            portfolio_results.append({
                "Ticker": ticker,
                "MarketCap": model.E,
                "Debt": model.D,
                "AssetValue": model.V,
                "AssetVol": model.sigma_V,
                "DistanceToDefault": model.DD,
                "ProbOfDefault": model.PD
            })
        except Exception as e:
            print(f"ERROR on {ticker}: {str(e)}")

    if portfolio_results:
        df = pd.DataFrame(portfolio_results)
        df.to_csv("Portfolio_Risk_Report.csv", index=False)
        print("\n" + "="*40)
        print("SUCCESS: Project by Mai Tran.")
        print("Final Report saved to: Portfolio_Risk_Report.csv")
        print("="*40)
        print(df[['Ticker', 'DistanceToDefault', 'ProbOfDefault']])
