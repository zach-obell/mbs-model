// MBS prepayment & pricing model — mirrors the Excel "MBS Model" tab.
// All rates are decimals (0.0728 = 7.28%).
function priceMBS(p) {
  const n = p.originalTerm - p.wala;            // remaining months (334)
  const r = p.wac / 12;                         // homeowners' monthly rate
  const maxRefi = p.peakCPR - p.baseCPR;
  const steps = Math.max(p.pathMonths, 1);
  const rows = [];
  let bal = p.balance, df = 1, pv = 0, wSum = 0, prinSum = 0;

  for (let t = 1; t <= n; t++) {
    const move = (p.pathBp / 10000) * Math.min(t, steps) / steps;
    const mortRate = p.mortgageRate + p.shockBp / 10000 + move;
    const discYld = p.treasuryBlend + p.spread + p.shockBp / 10000 + move;
    const incentive = p.wac - mortRate;
    const cpr = p.prepayOn ? p.baseCPR + maxRefi / (1 + Math.exp(-p.k * (incentive - p.midpoint))) : 0;
    const smm = 1 - Math.pow(1 - cpr, 1 / 12);
    const left = n - t + 1;
    const pmt = bal * r / (1 - Math.pow(1 + r, -left));
    const interest = bal * p.coupon / 12;
    const schedPrin = pmt - bal * r;
    const prepay = smm * (bal - schedPrin);
    const prin = schedPrin + prepay;
    const cf = interest + prin;
    df = df / (1 + discYld / 12);
    pv += cf * df;
    wSum += t * prin; prinSum += prin;
    rows.push({ t, bal, incentive, cpr, interest, schedPrin, prepay, cf });
    bal -= prin;
  }
  return {
    price: pv / p.balance * 100,
    wal: wSum / prinSum / 12,
    cpr1: rows[0].cpr,
    incentive1: rows[0].incentive,
    rows
  };
}

// Effective duration & convexity from static parallel shocks (±dBp)
function riskMeasures(p, dBp = 50) {
  const at = s => priceMBS({ ...p, shockBp: p.shockBp + s, pathBp: 0 }).price;
  const p0 = at(0), up = at(dBp), dn = at(-dBp), dy = dBp / 10000;
  return {
    duration: (dn - up) / (2 * p0 * dy),
    convexity: (dn + up - 2 * p0) / (p0 * dy * dy)
  };
}

if (typeof module !== "undefined") module.exports = { priceMBS, riskMeasures };
