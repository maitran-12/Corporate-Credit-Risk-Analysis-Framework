
# 🛡️ Corporate Credit Risk Analytics Framework
**An Automated End-to-End Pipeline: Merton Model & Monte Carlo Stress Testing**

## 🎯 Project Overview
This project establishes a robust, automated engine to evaluate corporate credit risk. By shifting from static accounting ratios to dynamic market-driven data, the framework provides forward-looking quantitative insights into **Distance to Default (DD)** and **Probability of Default (PD)**.

---

## ⚙️ Core Engine Logic

The backbone of this project is the `Merton Credit Model`, which executes a 3-step data and analytics pipeline:

### 1. Automated Data Engineering (`fetch_data`)
The engine dynamically synchronizes with market reality via the `yfinance` API:
* **Market Inputs:** Retrieves real-time Market Capitalization and calculates annualized Equity Volatility ($\sigma_E$) from the most recent 252 trading days.
* **Financial Parsing:** Automatically scans Quarterly and Annual Balance Sheets to extract Short-term and Long-term debt for the strike price ($D$).
* **Macro Environment:** Pulls the latest Risk-Free Rate ($r$) from the 13-week Treasury Bill (`^IRX`).
* **Debt Extraction:** Scans Balance Sheets to define the Default Barrier ($D$), where:
    $$D = \text{Short-term Debt} + 0.5 \times \text{Long-term Debt}$$
  
* (Note: If a granular breakdown is unavailable, the engine uses $$0.5 \times (\text{Total Assets} - \text{Equity})$$ as a conservative proxy).*
### 2. Numerical Optimization Solver (`solve_merton`)
Since Asset Value ($V$) and Asset Volatility ($\sigma_V$) are unobservable, the engine applies a sophisticated numerical approach:
* **Simultaneous Equations:** Defines the Black-Scholes-Merton non-linear system where Equity is treated as a Call Option on company assets.
* **Optimization:** Utilizes `scipy.optimize.fsolve` to find the convergence point for $V$ and $\sigma_V$. This transforms raw market cap into the true intrinsic value of the firm's assets.

* $$E = V \Phi(d_1) - De^{-rT} \Phi(d_2)$$
* $$\sigma_E = \left( \frac{V}{E} \right) \Phi(d_1) \sigma_V$$

*Where:*
* $d_1 = \frac{\ln(V/D) + (r + \sigma_V^2/2)T}{\sigma_V \sqrt{T}}$
* $d_2 = d_1 - \sigma_V \sqrt{T}$

### 3. Dynamic Stress Testing (`run_monte_carlo`)
To assess resilience under extreme volatility:
* **Trigger-based Execution:** To optimize performance, the engine intelligently triggers a simulation only for high risk tickers (where PD > 0.01 \%).
* **Stochastic Simulation:** Generates 10,000 random scenarios for future asset values using **Geometric Brownian Motion (GBM)**.
* $$V_T = V_0 \exp\left( \left(\mu - \frac{\sigma_V^2}{2}\right)T + \sigma_V W_T \right)$$

* **Distance to Default (DD):** Calculated as the number of standard deviations the asset value is from the debt floor:
    $$DD = \frac{\ln(V/D) + (r - \sigma_V^2/2)T}{\sigma_V \sqrt{T}}$$
* **Probability of Default (PD):** Defined as $PD = \Phi(-DD)$.

---
> **Note on Versatility:** The engine is built for **global scalability**. While the initial tests were performed on specific tickers (AAPL, RR.L, U11.SI, BP.L, D05.SI, AAL), the code logic is designed to process **any publicly traded company** worldwide. Users can input any ticker supported by Yahoo Finance to perform on-demand credit analysis.

## 📊 Interactive Analytics (Power BI)

* The engine was tested with 6 stocks from different countries:
* **USA (NYSE/NASDAQ):** Tested with **AAPL** (Apple Inc.) and **AAL** (American Airlines). 
* **United Kingdom (LSE):** Tested with **RR.L** (Rolls-Royce Holdings) and **BP.L** (BP plc). 
* **Singapore (SGX):** Tested with **D05.SI** (DBS Group) and **U11.SI** (United Overseas Bank).

The processed output (`Portfolio_Risk_Report.csv`) is visualized through an interactive Power BI Dashboard:
* **Risk Monitoring:** Uses **Gauge Charts** to provide an instant visual of a firm's proximity to the Default Zone.
* **Credit Rating System:** Categorizes firms from **AAA (Prime)** to **C (High Risk)** based on calculated Distance to Default metrics.
* **Regional Analysis:** Interactive slicers allow for risk segmentation across global markets (Singapore, UK, USA).

[Dashboard Preview](https://github.com/maitran-12/Corporate-Credit-Risk-Analysis-Framework/raw/75f9fb891d0f3bbcba55387078044a493756dcbd/Power%20BI%20dashboard.gif)

[Monte Carlo for the stock detected with high risk](https://github.com/maitran-12/Corporate-Credit-Risk-Analysis-Framework/raw/75f9fb891d0f3bbcba55387078044a493756dcbd/Monte%20carlo%20for%20AAL.png)

[Result from Python execution](https://github.com/maitran-12/Corporate-Credit-Risk-Analysis-Framework/raw/75f9fb891d0f3bbcba55387078044a493756dcbd/Python%20execution.png)

---

## 🛠️ Tech Stack
* **Language:** Python 
* **Library:** Pandas, NumPy, Scipy, Matplotlib
* **API:** Yahoo Finance (yfinance)
* **BI Tool:** Power BI Desktop

---
`Developed by Ngoc Mai Tran, to turn raw market data into actionable investment insights.`
