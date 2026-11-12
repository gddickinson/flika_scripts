// Neighbours in a frame: ports of getNN (Step_3_nearestNeighbour.py: distance to the nearest other localisation in
// the same frame, in nm) and getNNinFrame (Step_8_addNNcounts.py: how many others lie within r pixels, r included).
// The scripts use a scikit-learn KDTree; a direct search gives the same distances. Checked by
// neighbours_engine.test.mjs against tests/fixtures/demo_cases.json.

const groups = frame => { const g = new Map(); frame.forEach((f, i) => { if (!g.has(f)) g.set(f, []); g.get(f).push(i); }); return g; };

// pts: { frame: [...], x: [...], y: [...] } in pixels. Returns per-row NN distance (nm) and counts per radius.
export function neighbours(pts, { pixelSize = 108, radii = [3, 5, 10, 20, 30] } = {}) {
  const n = pts.x.length, nn = new Array(n).fill(NaN), counts = Object.fromEntries(radii.map(r => [r, new Array(n).fill(0)]));
  for (const idx of groups(pts.frame).values()) {
    for (const i of idx) {
      const dnm = [], dpx = [];
      for (const j of idx) {
        dnm.push(Math.sqrt((pts.x[i] * pixelSize - pts.x[j] * pixelSize) ** 2 + (pts.y[i] * pixelSize - pts.y[j] * pixelSize) ** 2));
        dpx.push(Math.sqrt((pts.x[i] - pts.x[j]) ** 2 + (pts.y[i] - pts.y[j]) ** 2));
      }
      if (idx.length >= 2) nn[i] = dnm.sort((a, b) => a - b)[1];  // k=2: the first is the point itself
      for (const r of radii) counts[r][i] = dpx.filter(d => d <= r).length - 1;  // minus itself
    }
  }
  return { nnDist_nm: nn, counts };
}
