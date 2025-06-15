import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import streamlit as st

CONFIG = {'template': 'plotly_dark', 'plot_bgcolor': 'rgba(0,0,0,0)', 
          'paper_bgcolor': 'rgba(0,0,0,0)', 'font': dict(family="Inter")}

def plot_distribution(vals: np.ndarray, price: float, curr: str = 'USD'):
    """Combined distribution & KDE plot"""
    fig = go.Figure()
    
    # Histogram + KDE
    fig.add_histogram(x=vals, nbinsx=50, marker_color='rgba(197,132,247,0.6)', 
                  name='Value Distribution')
    kde_x = np.linspace(vals.min(), vals.max(), 100)
    kde_y = stats.gaussian_kde(vals)(kde_x) * len(vals) * (vals.max() - vals.min()) / 50
    fig.add_scatter(x=kde_x, y=kde_y, mode='lines', line=dict(color='#c584f7', width=3),
                name='Probability Density')
    
    # Reference lines
    for v, c, d, t in [(price, "#f87171", "dash", "Current"), 
                       (vals.mean(), "#4ade80", "dot", "Mean"),
                       (np.median(vals), "#60a5fa", "dot", "Median")]:
        fig.add_vline(x=v, line_dash=d, line_color=c, annotation_text=f"{t}: {v:.2f}")
    
    fig.update_layout(**CONFIG, height=500, title="Fair Value Distribution",
                     xaxis_title=f"Fair Value ({curr})", yaxis_title="Frequency")
    return fig

def plot_percentiles(res: dict, price: float, curr: str = 'USD'):
    """Percentile plot with confidence band"""
    fig = go.Figure()
    pctls = [5, 10, 25, 50, 75, 90, 95]
    vals = [res['percentiles'][f'p{p}'] for p in pctls]
    
    # Main line + confidence band
    fig.add_scatter(x=pctls, y=vals, mode='lines+markers',
                   line=dict(color='#c584f7', width=3), marker=dict(size=10),
                   name='Valuation Percentile')
    fig.add_scatter(x=pctls+pctls[::-1], 
                   y=[res['percentiles']['p5']]*len(pctls)+[res['percentiles']['p95']]*len(pctls),
                   fill='toself', fillcolor='rgba(197,132,247,0.2)', line=dict(width=0),
                   name='90% Confidence Band')
    
    fig.add_hline(y=price, line_dash="dash", line_color="#f87171",
                 annotation_text=f"Current: {price:.2f}")
    
    fig.update_layout(**CONFIG, height=400, title="Valuation Percentiles",
                     xaxis_title="Percentile", yaxis_title=f"Fair Value ({curr})",
                     showlegend=True)
    return fig

def plot_waterfall(base: float, scen: dict, curr: str = 'USD'):
    """Scenario waterfall"""
    fig = go.Figure()
    vals = [base, scen['bear']-base, scen['base']-scen['bear'], 
            scen['bull']-scen['base'], scen['expected']]
    
    fig.add_waterfall(
        x=["Current", "Bear", "Base", "Bull", "Expected"], y=vals,
        measure=["absolute", "relative", "relative", "relative", "total"],
        decreasing={"marker": {"color": "#f87171"}},
        increasing={"marker": {"color": "#4ade80"}},
        totals={"marker": {"color": "#c584f7"}}
    )
    
    fig.update_layout(**CONFIG, height=400, title="Scenario Analysis",
                     yaxis_title=f"Price ({curr})", showlegend=False)
    return fig

def plot_sensitivity(res: dict, params: dict):
    """Sensitivity tornado"""
    fig = go.Figure()
    base = res['mean']
    sens = [('Growth Rate', 0.04), ('Discount Rate', 0.04), 
            ('Terminal Growth', 0.02), ('FCF Margin', 0.06)]
    
    for i, (param, pct) in enumerate(sorted(sens, key=lambda x: x[1], reverse=True)):
        impact = base * pct
        fig.add_bar(y=[param], x=[-impact], orientation='h', marker_color='#f87171',
                   name='Negative Impact' if i == 0 else None, showlegend=i==0)
        fig.add_bar(y=[param], x=[impact], orientation='h', marker_color='#4ade80',
                   name='Positive Impact' if i == 0 else None, showlegend=i==0)
    
    fig.add_vline(x=0, line_dash="solid", line_color="white", line_width=2)
    fig.update_layout(**CONFIG, height=400, title="Sensitivity Analysis",
                     xaxis_title="Impact on Valuation", barmode='overlay')
    return fig

def display_summary(res: dict, price: float, curr: str = 'USD'):
    """Streamlined results display"""
    vals = res['per_share_values']
    up_prob = (vals > price).mean() * 100
    
    # Metrics
    metrics = [
        ("Mean Fair Value", f"{curr} {res['mean']:.2f}", f"{(res['mean']/price-1)*100:+.1f}%"),
        ("Median Fair Value", f"{curr} {res['median']:.2f}", f"{(res['median']/price-1)*100:+.1f}%"),
        ("Upside Probability", f"{up_prob:.1f}%", "vs current"),
        ("Value at Risk (P10)", f"{curr} {res['percentiles']['p10']:.2f}", 
         f"{(res['percentiles']['p10']/price-1)*100:+.1f}%")
    ]
    
    cols = st.columns(4)
    for col, (l, v, d) in zip(cols, metrics):
        col.metric(l, v, d)
    
    # Dashboard
    fig = make_subplots(rows=1, cols=2,
                       subplot_titles=('Fair Value Distribution', 'Risk-Return Profile'),
                       specs=[[{"type": "histogram"}, {"type": "scatter"}]])
    
    # Distribution
    fig.add_histogram(x=vals, nbinsx=50, marker_color='rgba(197,132,247,0.6)', row=1, col=1)
    
    # Risk-Return
    pctls = np.arange(10, 91, 10)
    rr = [(np.percentile(vals, p), p) for p in pctls]
    fig.add_scatter(x=[r[1] for r in rr], y=[r[0] for r in rr],
                   mode='lines+markers', marker=dict(size=8, color='#c584f7'), row=1, col=2)
    
    fig.update_layout(**CONFIG, height=400, showlegend=False)
    fig.update_xaxes(title_text=f"Fair Value ({curr})", row=1, col=1)
    fig.update_xaxes(title_text="Confidence Level (%)", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=1)
    fig.update_yaxes(title_text=f"Fair Value ({curr})", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)