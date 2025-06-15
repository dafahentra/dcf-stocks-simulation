# DCF Valuation Simulator

A Monte Carlo simulation tool for enterprise valuation using discounted cash flow (DCF) analysis. This interactive web application helps financial analysts and investors understand valuation uncertainty through probabilistic modeling.

## Features

- **Monte Carlo Simulation**: Run thousands of simulations to generate probability distributions of enterprise value
- **Interactive Dashboard**: Real-time parameter adjustment with immediate visual feedback
- **Sensitivity Analysis**: 2D heatmaps and 3D surface plots showing how WACC and growth rates impact valuation
- **Statistical Insights**: Comprehensive statistics including mean, median, confidence intervals, and percentiles
- **Data Export**: Download simulation results as CSV for further analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dafahentra/dcf-valuation-simulator.git
cd dcf-valuation-simulator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Requirements

```
streamlit==1.28.0
numpy==1.24.3
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.17.0
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run simulation.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Adjust parameters in the sidebar:
   - **WACC**: Weighted Average Cost of Capital (8% - 16%)
   - **Growth Rate**: Revenue growth rate (3% - 10%)
   - **Margin**: Operating margin (10% - 20%)
   - **Terminal Growth**: Long-term growth rate (2% - 6%)

4. Click "Run Simulation" to generate valuation distribution

5. Use "Run Sensitivity Analysis" to explore how WACC and growth rate combinations affect valuation

## How It Works

### DCF Model Components

The simulator implements a 5-year DCF model with terminal value:

1. **Revenue Projection**: `Revenue(t) = Revenue(0) × ∏(1 + growth(t))`
2. **NOPAT Calculation**: `NOPAT(t) = Revenue(t) × Margin(t)`
3. **Asset Calculation**: `Assets(t) = Revenue(t) / Asset_Turnover`
4. **Free Cash Flow**: `FCFF(t) = NOPAT(t) - Net_Investment(t)`
5. **Terminal Value**: `TV = FCFF(5) × (1 + g) / (WACC - g)`
6. **Enterprise Value**: `EV = Σ[FCFF(t) / (1 + WACC)^t]`

### Monte Carlo Simulation

Each simulation run:
- Randomly generates growth rates from Normal(μ_growth, σ_growth)
- Randomly generates margins from Normal(μ_margin, σ_margin)
- Randomly generates terminal growth from Normal(μ_terminal, σ_terminal)
- Calculates enterprise value using the DCF formula

## Parameters

### Primary Parameters
- **Initial Revenue**: Starting revenue (default: 100)
- **Initial Assets**: Starting assets (default: 80)
- **Assets Turnover**: Revenue/Assets ratio (default: 1.3)
- **WACC**: Discount rate for cash flows

### Volatility Parameters
- **Growth Std Dev**: Standard deviation of growth rate
- **Margin Std Dev**: Standard deviation of operating margin
- **Terminal Growth Std Dev**: Standard deviation of terminal growth

## Output

### Simulation Results
- **Distribution Plot**: Histogram showing probability density of valuations
- **Summary Statistics**: Count, mean, std dev, min, max, and percentiles
- **Box Plot**: Visual representation of quartiles and outliers
- **Confidence Intervals**: 95% CI for valuation estimates

### Sensitivity Analysis
- **2D Heatmap**: Valuation matrix for WACC vs Growth Rate combinations
- **3D Surface Plot**: Three-dimensional visualization of valuation surface

## Example Output

```
Expected Value: 312.45
95% Confidence Interval: [245.32, 389.78]
Median: 308.91
Standard Deviation: 42.18
```

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Author

Dafa Hentra Anjana

## Acknowledgments

- Built with Streamlit for rapid web development
- Inspired by traditional DCF valuation methods in corporate finance