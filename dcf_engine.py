import numpy as np
from scipy import stats

class DCFEngine:
    """DCF valuation engine"""
    
    def __init__(self, rf: float = 0.045, mp: float = 0.065):
        self.rf = max(0, rf)
        self.mp = max(0, mp)
    
    def calculate_value(self, p: dict) -> dict:
        """Single DCF calculation"""
        # WACC calc
        ce = self.rf + max(0.1, p['beta']) * self.mp
        we = 1 / (1 + max(0, p['debt_to_equity']))
        wacc = max(0.01, we * ce + (1 - we) * max(0, p['cost_of_debt']) * (1 - max(0, min(1, p['tax_rate']))))
        
        # Cash flows
        fcf = []
        current_fcf = p['base_fcf']
        
        for g in p['growth_rates']:
            if isinstance(g, (tuple, list)):
                g = np.mean(g)
            current_fcf *= (1 + g)
            fcf.append(current_fcf)
        
        # Terminal value
        term_g = p['terminal_growth']
        if isinstance(term_g, (tuple, list)):
            term_g = np.mean(term_g)
        term_g = min(term_g, wacc - 0.001)
        
        tv = fcf[-1] * (1 + term_g) / (wacc - term_g) if wacc > term_g + 0.001 else fcf[-1] * 15
        
        # Present value
        pv_fcf = sum(f / (1 + wacc)**(i+1) for i, f in enumerate(fcf))
        pv_tv = tv / (1 + wacc)**len(fcf)
        
        return {
            'enterprise_value': max(0, pv_fcf + pv_tv),
            'wacc': wacc,
            'terminal_value': tv,
            'fcf_projections': fcf
        }
    
    def monte_carlo(self, base: dict, n: int = 10000, unc: dict = None) -> dict:
        """Monte Carlo simulation"""
        np.random.seed(42)
        u = unc or {'fcf_growth_std': 0.03, 'terminal_growth_std': 0.005, 'beta_std': 0.1}
        n = max(100, min(100000, n))
        
        # Check range inputs
        g_range = isinstance(base['growth_rates'][0], (tuple, list))
        t_range = isinstance(base['terminal_growth'], (tuple, list))
        
        # Generate random params
        betas = np.clip(np.random.normal(base['beta'], u['beta_std'], n), 0.3, 2.5)
        
        if g_range:
            growths = np.array([[np.random.uniform(max(-0.3, g[0]), min(0.5, g[1])) 
                                for g in base['growth_rates']] for _ in range(n)])
        else:
            growths = np.clip(np.random.normal(base['growth_rates'], u['fcf_growth_std'], 
                                              (n, len(base['growth_rates']))), -0.3, 0.5)
        
        if t_range:
            term_g = np.random.uniform(max(0, base['terminal_growth'][0]), 
                                     min(0.04, base['terminal_growth'][1]), n)
        else:
            term_g = np.clip(np.random.normal(base['terminal_growth'], 
                                             u['terminal_growth_std'], n), 0, 0.04)
        
        # Simulation
        evs = []
        for i in range(n):
            params = {**base, 'beta': betas[i], 'growth_rates': growths[i], 
                     'terminal_growth': term_g[i]}
            ev = self.calculate_value(params)['enterprise_value']
            if ev > 0:
                evs.append(ev)
        
        # Results
        evs = np.array(evs) if evs else [self.calculate_value(base)['enterprise_value']] * 100
        ps_vals = np.maximum(evs - base.get('net_debt', 0), 0) / max(1, base.get('shares_outstanding', 1))
        
        # Remove outliers
        q1, q3 = np.percentile(ps_vals, [25, 75])
        iqr = q3 - q1
        mask = (ps_vals >= q1 - 3*iqr) & (ps_vals <= q3 + 3*iqr)
        ps_vals = ps_vals[mask] if mask.any() else ps_vals
        
        pctls = [5, 10, 25, 50, 75, 90, 95]
        
        return {
            'per_share_values': ps_vals,
            'mean': ps_vals.mean(),
            'median': np.median(ps_vals),
            'std': ps_vals.std(),
            'skew': stats.skew(ps_vals) if len(ps_vals) > 3 else 0,
            'kurtosis': stats.kurtosis(ps_vals) if len(ps_vals) > 3 else 0,
            'percentiles': {f'p{p}': np.percentile(ps_vals, p) for p in pctls},
            'n_simulations': len(ps_vals)
        }