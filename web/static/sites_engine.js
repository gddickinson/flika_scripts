// Regroup puffs into sites: a port of groupSites() from "2014.09.19 Regroup by Radius.py" (Kyle Ellefsen), kept
// faithful, including how it merges: each puff's neighbourhood (puffs within `radius`) starts a new site or is added
// to the FIRST existing site it touches. When a neighbourhood touches two existing sites they are not merged, so a
// puff can end up in two sites; the script then writes the values of the last one. `inTwoSites` reports that case.
// Checked by sites_engine.test.mjs against tests/fixtures/demo_cases.json.

// np.linalg.lstsq for y = m x + b (the minimum-norm solution when every x is the same).
export function fitLine(x, y) {
  const n = x.length, xm = x.reduce((s, v) => s + v, 0) / n, ym = y.reduce((s, v) => s + v, 0) / n;
  if (x.every(v => v === x[0])) { const t = x[0]; return { m: t * ym / (t * t + 1), b: ym / (t * t + 1) }; }
  let sxy = 0, sxx = 0;
  for (let i = 0; i < n; i++) { sxy += (x[i] - xm) * (y[i] - ym); sxx += (x[i] - xm) ** 2; }
  const m = sxy / sxx;
  return { m, b: ym - m * xm };
}

// puffs: [{x, y, t_peak, Amplitude}]. Returns { sites: [[indices]], puffs: [per-puff results], inTwoSites: [...] }.
export function groupSites(puffs, radius = Math.SQRT2) {
  const n = puffs.length, sites = [], added = new Set();
  for (let i = 0; i < n; i++) {
    const p = new Set();
    for (let j = 0; j < n; j++) if (Math.sqrt((puffs[j].x - puffs[i].x) ** 2 + (puffs[j].y - puffs[i].y) ** 2) <= radius) p.add(j);
    const hit = sites.findIndex(s => [...p].some(k => s.has(k)));
    if (hit < 0) sites.push(p); else for (const k of p) sites[hit].add(k);
    for (const k of p) added.add(k);
  }
  const out = puffs.map(q => ({ ...q })), seen = new Map();
  sites.forEach((site, si) => {
    const mem = [...site].sort((a, b) => a - b), ps = mem.map(k => puffs[k]);
    const gx = ps.reduce((s, q) => s + q.x, 0) / ps.length, gy = ps.reduce((s, q) => s + q.y, 0) / ps.length;
    const amps = ps.map(q => q.Amplitude), meanAmp = amps.reduce((s, v) => s + v, 0) / amps.length;
    const { m, b } = fitLine(ps.map(q => q.t_peak), amps);
    for (const k of mem) {
      seen.set(k, (seen.get(k) || 0) + 1);
      Object.assign(out[k], { 'Group #': si + 1, 'Group x': gx, 'Group y': gy, 'No. Events': ps.length,
        'Max Amp': Math.max(...amps), 'Amplitude Normalized by Site Mean': puffs[k].Amplitude / meanAmp,
        'Amplitude Normalized by Fitted Line': puffs[k].Amplitude / (m * puffs[k].t_peak + b) });
    }
  });
  return { sites: sites.map(s => [...s].sort((a, b) => a - b)), puffs: out,
           inTwoSites: [...seen].filter(([, c]) => c > 1).map(([k]) => k) };
}
