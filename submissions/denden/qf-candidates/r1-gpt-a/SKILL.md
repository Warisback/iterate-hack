---
name: qf-bench-output-integrity
description: Prevents common quantitative-finance bench failures: schedule/parameter mismatches, off-by-one calibration counts, and missing final response.
---
R1: Always write a non-empty final assistant message after creating outputs; if the task is file-based, the final message must at least state which files were written.
R2: Do not invent strategy mechanics; implement exactly what params.json specifies (rebalance frequency, start days, leverage/caps, per-stock weights, cost units).
R3: For “monthly” rebalancing, define rebalance days as the first available trading date of each calendar month within the dataset, then filter by trade_start_day index; do not shift by an extra day.
R4: Compute signals using only information available at decision time; if trades occur on day t, signals must be computed from data up to t-1 unless explicitly stated otherwise.
R5: Do not fill missing returns with 0.0 unless explicitly instructed; default cleaning is forward-fill within each column then remaining NaNs to 0 only if still present, and report nan_count from raw matrix before filling.
R6: Use sample statistics where specified: any reported/used standard deviation must be ddof=1; Sharpe uses mean/std of daily strategy returns then annualize by sqrt(annualization_factor).
R7: Max drawdown must be computed from the strategy equity curve (cumprod(1+r)), and reported as a positive magnitude (peak-to-trough / peak).
R8: Factor regression must be OLS with an intercept on the specified factor_names and aligned by date; annualized_alpha = intercept * annualization_factor; tracking_error_annual = std(residuals, ddof=1)*sqrt(annualization_factor).
R9: For GBM calibration, set n_prices to the number of close prices in the CSV (not the number of returns); returns count is n_prices-1.
R10: Monte Carlo pricing must use exactly the required path count and discrete monitoring count; ensure all reported prices (geo_exact, levy_arith, curran_arith, mc_arith, mc_geo) are strictly positive by using max(payoff,0) and discounting once by exp(-rT).
R11: If the agent encounters an API/LLM transport error mid-run, rerun locally from the last saved script/output state; do not exit without producing the required output files and final message.
