"""Tested option-pricing formulas (stdlib only). Import these instead of
re-deriving from memory; a hand-derived Curran produced negative prices.

All functions take `times`: the list of monitoring times in YEARS, e.g.
[T*i/n for i in range(1, n+1)]. Rates are continuously compounded, no dividends
(pass q for Black-Scholes). Calls only; for average-rate puts use parity:
    put = call - discount(r, T) * (asian_forward(S0, r, times) - K)
"""

import math
import random

SQRT2 = math.sqrt(2.0)


def norm_cdf(x):
    return 0.5 * math.erfc(-x / SQRT2)


def discount(r, T):
    return math.exp(-r * T)


def bs_call(S, K, T, r, sigma, q=0.0):
    if T <= 0 or sigma <= 0:
        return max(S * math.exp(-q * T) - K * math.exp(-r * T), 0.0)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)


def bs_put(S, K, T, r, sigma, q=0.0):
    return bs_call(S, K, T, r, sigma, q) - S * math.exp(-q * T) + K * math.exp(-r * T)


def _log_moments(S0, r, sigma, times):
    """Per-date log-moments and geometric-average moments under GBM."""
    n = len(times)
    mu = [math.log(S0) + (r - 0.5 * sigma * sigma) * t for t in times]  # E[ln S_i]
    mu_g = sum(mu) / n                                                  # E[ln G]
    # xi_i = Cov(ln S_i, ln G); var_g = Var(ln G)
    xi = []
    var_g = 0.0
    for i, ti in enumerate(times):
        cov_sum = sum(sigma * sigma * min(ti, tj) for tj in times) / n
        xi.append(cov_sum)
        var_g += cov_sum
    var_g /= n
    return mu, mu_g, xi, var_g


def geometric_asian_call(S0, K, r, sigma, times):
    """Exact price of a discrete-monitoring geometric-average call."""
    _, mu_g, _, var_g = _log_moments(S0, r, sigma, times)
    sd_g = math.sqrt(var_g)
    T = times[-1]
    d2 = (mu_g - math.log(K)) / sd_g
    d1 = d2 + sd_g
    return discount(r, T) * (math.exp(mu_g + 0.5 * var_g) * norm_cdf(d1) - K * norm_cdf(d2))


def asian_forward(S0, r, times):
    """E[arithmetic average] = (1/n) sum S0*exp(r*t_i)."""
    return sum(S0 * math.exp(r * t) for t in times) / len(times)


def levy_asian_call(S0, K, r, sigma, times):
    """Levy / Turnbull-Wakeman style: match first two moments of the
    arithmetic average to a lognormal, then Black-style formula."""
    n = len(times)
    T = times[-1]
    m1 = asian_forward(S0, r, times)
    m2 = 0.0
    for ti in times:
        for tj in times:
            m2 += math.exp(r * (ti + tj) + sigma * sigma * min(ti, tj))
    m2 *= S0 * S0 / (n * n)
    v = math.log(m2 / (m1 * m1))          # variance of fitted lognormal (log space)
    if v <= 0:
        return max(discount(r, T) * (m1 - K), 0.0)
    sd = math.sqrt(v)
    d1 = (math.log(m1 / K) + 0.5 * v) / sd
    d2 = d1 - sd
    return discount(r, T) * (m1 * norm_cdf(d1) - K * norm_cdf(d2))


def curran_asian_call(S0, K, r, sigma, times):
    """Curran (1994) geometric-conditioning approximation for a
    discrete-monitoring arithmetic-average call. Floored at the exact
    geometric-conditioning lower bound, so it can never go negative."""
    n = len(times)
    T = times[-1]
    mu, mu_g, xi, var_g = _log_moments(S0, r, sigma, times)
    sd_g = math.sqrt(var_g)
    lnK = math.log(K)

    def conditioning_price(k_adj):
        d = (mu_g - math.log(k_adj)) / sd_g
        s = 0.0
        for i, ti in enumerate(times):
            vi = sigma * sigma * ti
            s += math.exp(mu[i] + 0.5 * vi) * norm_cdf(d + xi[i] / sd_g)
        return discount(r, T) * (s / n - K * norm_cdf(d))

    # Curran's adjusted strike: K_hat = 2K - E[A | ln G = ln K]
    e_a_given_g = 0.0
    for i, ti in enumerate(times):
        vi = sigma * sigma * ti
        e_a_given_g += math.exp(mu[i] + (xi[i] / var_g) * (lnK - mu_g)
                                + 0.5 * (vi - xi[i] * xi[i] / var_g))
    e_a_given_g /= n
    k_hat = 2.0 * K - e_a_given_g

    lower_bound = conditioning_price(K)  # exact lower bound (Curran/Rogers-Shi)
    if k_hat <= 0:                        # deep in the money: bound is tight
        return max(lower_bound, discount(r, T) * (asian_forward(S0, r, times) - K))
    return max(conditioning_price(k_hat), lower_bound)


def mc_asian_calls(S0, K, r, sigma, times, n_paths=100000, seed=0):
    """Monte Carlo arithmetic & geometric call prices with standard error.
    Returns (arith_price, arith_stderr, geo_price). Antithetic variates."""
    rng = random.Random(seed)
    T = times[-1]
    dts = [times[0]] + [times[i] - times[i - 1] for i in range(1, len(times))]
    drift = [(r - 0.5 * sigma * sigma) * dt for dt in dts]
    vols = [sigma * math.sqrt(dt) for dt in dts]
    df = discount(r, T)
    tot_a = tot_a2 = tot_g = 0.0
    half = n_paths // 2
    for _ in range(half):
        zs = [rng.gauss(0.0, 1.0) for _ in dts]
        for sign in (1.0, -1.0):
            lnS = math.log(S0)
            s_sum = 0.0
            ln_sum = 0.0
            for j in range(len(dts)):
                lnS += drift[j] + sign * vols[j] * zs[j]
                s_sum += math.exp(lnS)
                ln_sum += lnS
            pay_a = df * max(s_sum / len(times) - K, 0.0)
            pay_g = df * max(math.exp(ln_sum / len(times)) - K, 0.0)
            tot_a += pay_a
            tot_a2 += pay_a * pay_a
            tot_g += pay_g
    m = 2 * half
    mean_a = tot_a / m
    var_a = max(tot_a2 / m - mean_a * mean_a, 0.0)
    return mean_a, math.sqrt(var_a / m), tot_g / m


def validate_asian_row(geo_exact, levy, curran, mc_arith, mc_geo, mc_se):
    """Return list of violated sanity checks (empty list = OK). Run this on
    EVERY output row before writing files; a negative Curran price shipped
    once because this check was skipped."""
    bad = []
    if not geo_exact > 0: bad.append("geo_exact <= 0")
    if not levy > 0: bad.append("levy <= 0")
    if not curran > 0: bad.append("curran <= 0")
    if not geo_exact < mc_arith + 6 * mc_se: bad.append("geo not < arith (+tol)")
    if abs(geo_exact - mc_geo) > max(6 * mc_se, 0.02 * geo_exact):
        bad.append("geo_exact far from MC geo")
    if abs(curran - mc_arith) > max(8 * mc_se, 0.02 * mc_arith):
        bad.append("curran far from MC arith")
    return bad
