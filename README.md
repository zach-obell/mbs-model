# Agency MBS Prepayment & Convexity Model

**Live model:** https://zach-obell.github.io/mbs-model/

An interactive model of a $100M pool of Fannie Mae 30-year 5.5% mortgage-backed securities. It projects monthly cash flows under a refinancing-driven prepayment curve, prices the pool off current Treasury yields plus the MBS spread, and measures duration and negative convexity.

## What it shows
- **Price vs. rate shock:** how the homeowner's option to refinance caps the MBS price when rates fall (negative convexity), compared with a non-prepaying bond
- **Monthly cash flows:** interest, scheduled principal and prepayments under any rate scenario, including gradual rate paths
- **Prepayment S-curve:** model CPR vs. actual October 2026 FNMA speeds by coupon
- **Rates history:** built automatically from each weekday update

## How it works
1. **Refinancing incentive** = WAC − current mortgage rate
2. **Prepayment speed (CPR)** from an S-curve calibrated to actual agency speeds
3. **Monthly cash flows** for the remaining term: scheduled payment, interest at the coupon, scheduled principal and prepayments
4. **Discounting** at the 5/10-yr Treasury blend + MBS spread to get price per $100
5. **Duration and convexity** from repricing at ±50bp and ±100bp

The model was built first in Excel; this JavaScript version reproduces its numbers exactly.

## Data
| Input | Source | Updates |
|---|---|---|
| 30-yr mortgage rate | Freddie Mac PMMS via FRED (MORTGAGE30US) | Automatic, weekly |
| 5-yr and 10-yr Treasury | U.S. Treasury via FRED (DGS5, DGS10) | Automatic, daily |
| WAC, loan age, prepayment speeds | Agency prepayment reports | Manual, monthly |
| MBS spread | Latest public figure | Manual |

A GitHub Actions workflow runs every weekday at 5:30 p.m. ET, pulls the latest rates from FRED, and saves them to `data/market.json` and `data/history.json`.

## Files
- `index.html`: the interactive page
- `model.js`: the pricing model
- `data/settings.json`: manual inputs, with sources and dates
- `scripts/update_data.py` + `.github/workflows/update.yml`: the automatic data pipeline

## Limitations
Single average pool; one rate scenario at a time (no Monte Carlo/OAS); no burnout or lock-in effects; the MBS spread is held constant between published updates.

---
Built by Zachary O'Bell, Tulane University (A. B. Freeman School of Business). For educational purposes only. Not investment advice.
