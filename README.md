# DCF Valuation Tool

A sophisticated web-based Discounted Cash Flow (DCF) valuation tool built with Streamlit that uses Monte Carlo simulation to estimate the intrinsic value of stocks.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![GitHub](https://img.shields.io/badge/GitHub-dafahentra-181717?logo=github)](https://github.com/dafahentra)

## 🎯 Features

- **Real-time Beta Calculation**: Automatically fetch and calculate beta coefficients from market data
- **Monte Carlo Simulation**: Run thousands of simulations to account for uncertainty in valuations
- **Multi-Market Support**: Works with stocks from US, UK, Germany, Japan, Hong Kong, India, and China markets
- **Interactive Visualizations**: Beautiful charts showing value distributions, percentiles, and sensitivity analysis
- **Flexible Growth Modeling**: Support for both fixed and range-based growth rate projections
- **Export Functionality**: Download valuation results in JSON format

## 📊 Screenshots

The application provides:
- Fair value distribution charts
- Scenario analysis (Bear/Base/Bull cases)
- Sensitivity analysis tornado charts
- Risk-return profiles
- Percentile-based valuation ranges

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dafahentra/dcf-valuation-tool.git
cd dcf-valuation-tool
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run main.py
```

4. Open your browser and navigate to `http://localhost:8501`

## 💻 Usage

### Basic Workflow

1. **Enter Company Information**
   - Company name and ticker symbol
   - Current stock price
   - Number of shares outstanding

2. **Set Financial Structure**
   - Total debt and cash position
   - Cost of debt and tax rate

3. **Input Historical Data**
   - Revenue for past 3-5 years
   - Free cash flow for past 3-5 years

4. **Configure Growth Assumptions**
   - Choose between fixed rates or ranges
   - Set growth rates for projection period
   - Define terminal growth rate

5. **Run Valuation**
   - Click "Run DCF Valuation"
   - View results across multiple tabs

### Advanced Features

- **Beta Fetching**: Click "Fetch Beta" to automatically retrieve beta from market data
- **Monte Carlo Settings**: Adjust number of simulations (1,000 to 50,000)
- **Market Parameters**: Customize risk-free rate and market risk premium

## 📁 Project Structure

```
dcf-valuation-tool/
│
├── main.py              # Main Streamlit application
├── dcf_engine.py        # DCF calculation engine
├── beta_fetcher.py      # Beta coefficient fetcher
├── visualization.py     # Plotting functions
├── styles.py           # UI styling and formatting
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Configuration

### Market Parameters

Default market parameters by region:

| Market | Index | Market Premium | Risk-Free Rate |
|--------|-------|----------------|----------------|
| US     | S&P 500 | 6.5% | 4.5% |
| UK     | FTSE 100 | 6.0% | 4.0% |
| Germany | DAX | 5.5% | 2.5% |
| Japan  | Nikkei 225 | 5.0% | 0.1% |
| Hong Kong | HSI | 6.5% | 4.0% |
| India  | BSE SENSEX | 8.0% | 7.0% |
| China  | SSE Composite | 7.0% | 2.5% |

### Simulation Parameters

- **Default simulations**: 10,000
- **Projection years**: 3-10 years (default: 5)
- **Growth rate bounds**: -30% to 50%
- **Terminal growth cap**: 4%

## 📈 Methodology

### DCF Calculation

1. **WACC Calculation**:
   ```
   WACC = We × Ce + Wd × Cd × (1 - Tax Rate)
   ```
   Where:
   - We = Weight of equity
   - Ce = Cost of equity (Risk-free rate + Beta × Market premium)
   - Wd = Weight of debt
   - Cd = Cost of debt

2. **Free Cash Flow Projection**: Projects FCF based on historical growth patterns

3. **Terminal Value**: Calculated using the Gordon Growth Model

4. **Monte Carlo Simulation**: Varies key parameters within reasonable bounds to generate a distribution of possible valuations

## 🐛 Troubleshooting

### Common Issues

1. **Beta fetch fails**: 
   - Ensure ticker symbol is correct
   - Check internet connection
   - Manually input beta if automatic fetch fails

2. **Import errors**:
   - Run `pip install -r requirements.txt` again
   - Ensure Python version is 3.8+

3. **Streamlit not loading**:
   - Clear browser cache
   - Try different port: `streamlit run main.py --server.port 8502`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Financial data from [yfinance](https://github.com/ranaroussi/yfinance)
- Visualizations powered by [Plotly](https://plotly.com/)

## ⚠️ Disclaimer

This tool is for educational and research purposes only. It should not be used as the sole basis for investment decisions. Always conduct thorough due diligence and consult with financial professionals before making investment decisions.

## 📧 Contact

For questions, suggestions, or issues, please open an issue on GitHub or contact:
- **Email**: dapahentra@gmail.com
- **GitHub**: [dafahentra](https://github.com/dafahentra)