// Regroup puffs into sites: a port of groupSites() from "2014.09.19 Regroup by Radius.py" (Kyle Ellefsen; fixed
// 2026-11 so each puff is in exactly one site). Puffs are visited in order; a puff's neighbourhood (puffs within
// `radius`) starts a new site if none of its puffs is in a site yet. Otherwise each of its puffs not yet in a site
// joins the touched site whose centre (mean x, y of its members before this neighbourhood) is nearest, ties going to
// the earlier site; puffs already in a site stay there.
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

// puffs: [{x, y, t_peak, Amplitude}]. Returns { sites: [[indices]], puffs: [per-puff results] }.
export function groupSites(puffs, radius = Math.SQRT2) {
  const n = puffs.length, sites = [], added = new Set();
  for (let i = 0; i < n; i++) {
    const p = new Set();
    for (let j = 0; j < n; j++) if (Math.sqrt((puffs[j].x - puffs[i].x) ** 2 + (puffs[j].y - puffs[i].y) ** 2) <= radius) p.add(j);
    const touched = sites.map((s, si) => [...p].some(k => s.has(k)) ? si : -1).filter(si => si >= 0);
    if (!touched.length) sites.push(p);
    else {
      const centres = touched.map(si => { const m = [...sites[si]]; return [m.reduce((s, k) => s + puffs[k].x, 0) / m.length, m.reduce((s, k) => s + puffs[k].y, 0) / m.length]; });
      for (const k of [...p].filter(k => !added.has(k)).sort((a, b) => a - b)) {
        let best = 0, bestD = Infinity;
        centres.forEach(([cx, cy], ci) => { const d = Math.sqrt((cx - puffs[k].x) ** 2 + (cy - puffs[k].y) ** 2); if (d < bestD) { bestD = d; best = ci; } });
        sites[touched[best]].add(k);
      }
    }
    for (const k of p) added.add(k);
  }
  const out = puffs.map(q => ({ ...q }));
  sites.forEach((site, si) => {
    const mem = [...site].sort((a, b) => a - b), ps = mem.map(k => puffs[k]);
    const gx = ps.reduce((s, q) => s + q.x, 0) / ps.length, gy = ps.reduce((s, q) => s + q.y, 0) / ps.length;
    const amps = ps.map(q => q.Amplitude), meanAmp = amps.reduce((s, v) => s + v, 0) / amps.length;
    const { m, b } = fitLine(ps.map(q => q.t_peak), amps);
    for (const k of mem) {
      Object.assign(out[k], { 'Group #': si + 1, 'Group x': gx, 'Group y': gy, 'No. Events': ps.length,
        'Max Amp': Math.max(...amps), 'Amplitude Normalized by Site Mean': puffs[k].Amplitude / meanAmp,
        'Amplitude Normalized by Fitted Line': puffs[k].Amplitude / (m * puffs[k].t_peak + b) });
    }
  });
  return { sites: sites.map(s => [...s].sort((a, b) => a - b)), puffs: out };
}
