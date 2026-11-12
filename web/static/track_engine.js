// Track features: JavaScript ports of the PIEZO1 workflow functions, line for line, so the static site computes what
// the scripts compute. Each function names its source. Checked against the Python originals by
// track_engine.test.mjs (tests/fixtures/demo_cases.json, written by scripts/make_demo_fixture.py).
// A track is { frame: [...], x: [...], y: [...] } in pixels.

const mean = a => a.reduce((s, v) => s + v, 0) / a.length;
const nanmean = a => { const v = a.filter(Number.isFinite); return v.length ? mean(v) : NaN; };
const deg = r => r * 180 / Math.PI;

// np.linalg.eig on a symmetric 2x2 matrix, as LAPACK dgeev computes it (dlanv2's standardisation of the 2x2 block,
// whose rotation becomes the eigenvector matrix). Reproducing it keeps the eigenvector's sign, and so the sign of
// the skewness below, identical to the Python result.
export function eig2(a, b, d) {
  if (b === 0) return { w: [a, d], v: [[1, 0], [0, 1]] };
  const p = 0.5 * (a - d), bcmax = Math.abs(b), bcmis = Math.abs(b), scale = Math.max(Math.abs(p), bcmax);
  let z = p / scale * p + bcmax / scale * bcmis;
  z = p + (p >= 0 ? 1 : -1) * Math.sqrt(scale) * Math.sqrt(z);
  const w0 = d + z, w1 = d - bcmax / z * bcmis, tau = Math.hypot(b, z), cs = z / tau, sn = b / tau;
  return { w: [w0, w1], v: [[cs, -sn], [sn, cs]] };  // v[row][col]; column k is the eigenvector of w[k]
}

// scipy.stats.skew / kurtosis (bias=True, Fisher): NaN when the data are all (numerically) equal.
function moments(a) {
  const m = mean(a), d = a.map(v => v - m);
  const m2 = mean(d.map(v => v * v)), m3 = mean(d.map(v => v * v * v)), m4 = mean(d.map(v => (v * v) * (v * v)));
  const zero = m2 <= (Number.EPSILON * m) ** 2;
  return { skew: zero ? NaN : m3 / m2 ** 1.5, kurt: zero ? NaN : m4 / m2 ** 2 - 3 };
}

// RadiusGyrationAsymmetrySkewnessKurtosis (calcuateRGandFeatures.py and its copies)
export function radiusGyration(pts) {
  const n = pts.length, cx = mean(pts.map(p => p[0])), cy = mean(pts.map(p => p[1]));
  let sxx = 0, sxy = 0, syy = 0;
  for (const [x, y] of pts) { const dx = x - cx, dy = y - cy; sxx += dx * dx; sxy += dx * dy; syy += dy * dy; }
  const { w, v } = eig2(sxx / n, sxy / n, syy / n);
  const rg = Math.sqrt(w[0] + w[1]);
  const asym = -Math.log(1 - (w[0] - w[1]) ** 2 / (2 * (w[0] + w[1]) ** 2));
  const k = w[0] >= w[1] ? 0 : 1, ev = [v[0][k], v[1][k]], n2 = ev[0] ** 2 + ev[1] ** 2;
  const proj = [];
  for (let i = 0; i + 1 < n; i++) proj.push(((pts[i + 1][0] - pts[i][0]) * ev[0] + (pts[i + 1][1] - pts[i][1]) * ev[1]) / n2);
  const { skew, kurt } = moments(proj);
  return { rg, asymmetry: asym, skewness: skew, kurtosis: kurt, eigenvalues: w, dominant: ev, center: [cx, cy] };
}

// FractalDimension: throws for collinear points, as the script does. The largest distance between convex-hull
// vertices equals the largest distance between any two points, which is what is computed here.
export function fractalDimension(pts) {
  const [x0, y0] = pts[0];
  const others = pts.filter(([x, y]) => x !== x0 || y !== y0);
  const slopes = others.map(([x, y]) => (x !== x0 ? (y - y0) / (x - x0) : null));
  if (slopes.every(s => s === slopes[0])) throw new Error('Fractal Dimension cannot be calculated for points that are collinear');
  let total = 0, largest = 0;
  for (let i = 1; i < pts.length; i++) total += Math.sqrt((pts[i][0] - pts[i - 1][0]) ** 2 + (pts[i][1] - pts[i - 1][1]) ** 2);
  for (let i = 0; i < pts.length; i++) for (let j = i + 1; j < pts.length; j++)
    largest = Math.max(largest, Math.sqrt((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2));
  const n = pts.length;
  return Math.log(n) / Math.log(n * largest / total);
}

// NetDisplacementEfficiency
export function netDisplacement(pts) {
  const n = pts.length, net = Math.hypot(pts[0][0] - pts[n - 1][0], pts[0][1] - pts[n - 1][1]);
  let ss = 0;
  for (let i = 1; i < n; i++) ss += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) ** 2;
  return { netDispl: net, efficiency: net ** 2 / ((n - 1) * ss) };
}

// SummedSinesCosines: consecutive repeated positions are dropped, then the sine and cosine of each turn.
export function sinesCosines(pts) {
  const p = pts.filter((q, i) => !(i + 1 < pts.length && pts[i + 1][0] === q[0] && pts[i + 1][1] === q[1]));
  const sin = [], cos = [];
  for (let i = 0; i + 2 < p.length; i++) {
    const ab = [p[i + 1][0] - p[i][0], p[i + 1][1] - p[i][1]], bc = [p[i + 2][0] - p[i + 1][0], p[i + 2][1] - p[i + 1][1]];
    const mag = Math.hypot(ab[0], ab[1]) * Math.hypot(bc[0], bc[1]);
    cos.push((ab[0] * bc[0] + ab[1] * bc[1]) / mag);
    sin.push((ab[0] * bc[1] - ab[1] * bc[0]) / mag);
  }
  return { sin_mean: sin.length ? mean(sin) : NaN, sin_vals: sin, cos_mean: cos.length ? mean(cos) : NaN, cos_vals: cos };
}

// calculate_direction (addDirectionOfTravel.py): degrees 0-360 with the y axis inverted (image rows grow down).
export function direction(x1, y1, x2, y2) {
  const dx = x2 - x1, dy = -(y2 - y1);
  if (dx === 0 && dy === 0) return NaN;
  const a = deg(Math.atan2(dy, dx));
  return a < 0 ? a + 360 : a;
}

// calculate_directional_persistence: 1 - mean absolute turn / 180.
export function persistence(angles) {
  if (angles.length < 2 || angles.every(Number.isNaN)) return NaN;
  const v = angles.filter(a => !Number.isNaN(a));
  if (v.length < 2) return NaN;
  const diffs = [];
  for (let i = 1; i < v.length; i++) { let d = Math.abs(v[i] - v[i - 1]); if (d > 180) d = 360 - d; diffs.push(d); }
  return 1 - mean(diffs) / 180;
}

// addLocalizationError (Step_11): distance of each point from the track's mean position, and its mean.
export function localizationError(t) {
  const mx = nanmean(t.x), my = nanmean(t.y);
  const d = t.x.map((x, i) => Math.sqrt((mx - x) ** 2 + (my - t.y[i]) ** 2));
  return { distanceFromMean: d, meanLocDistanceFromCenter: nanmean(d) };
}

// addLagDisplacementToDF: step length to the next point (NaN on the last), its mean and sum, Rg scaled by both.
export function lags(t, rg) {
  const n = t.x.length, lag = t.x.map((x, i) => (i + 1 < n ? Math.sqrt((t.x[i + 1] - x) ** 2 + (t.y[i + 1] - t.y[i]) ** 2) : NaN));
  const meanLag = nanmean(lag), trackLength = lag.filter(Number.isFinite).reduce((s, v) => s + v, 0);
  return { lag, meanLag, track_length: trackLength, rg_scaled: rg / meanLag, rg_scaled_trackLength: rg / trackLength };
}

// addDiffusiontoDF (Step_5) and addVelocitytoDF (Step_6) for one track, with `lag` from lags().
export function diffusionVelocity(t, lag) {
  const n = t.frame.length, minF = Math.min(...t.frame), i0 = t.frame.indexOf(minF);
  const zx = t.x.map(x => x - t.x[i0]), zy = t.y.map(y => y - t.y[i0]);
  const lagNumber = t.frame.map(f => f - minF), dist = zx.map((x, i) => Math.sqrt(x * x + zy[i] * zy[i]));
  const dydt = [0];
  for (let i = 1; i < n; i++) dydt.push((dist[i] - dist[i - 1]) / (lagNumber[i] - lagNumber[i - 1]));
  const dt = t.frame.map((f, i) => { const d = (i + 1 < n ? t.frame[i + 1] : 0) - f; return d <= 0 ? NaN : d; });
  const velocity = lag.map((l, i) => l / dt[i]);
  const dirOrigin = zx.map((x, i) => { const a = Math.atan2(zy[i], x) / Math.PI * 180; return a < 0 ? 360 + a : a; });
  return { zeroed_X: zx, zeroed_Y: zy, lagNumber, distanceFromOrigin: dist, d_squared: dist.map(d => d * d), dydt, dt,
           velocity, direction_origin: dirOrigin, meanVelocity: nanmean(velocity) };
}

// Everything the demo shows for one track.
export function analyseTrack(t) {
  const pts = t.x.map((x, i) => [x, t.y[i]]);
  const rg = radiusGyration(pts);
  let fd, fdError = null;
  try { fd = fractalDimension(pts); } catch (e) { fd = NaN; fdError = e.message; }
  const dirs = [];
  for (let i = 0; i + 1 < pts.length; i++) dirs.push(direction(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]));
  const lg = lags(t, rg.rg);
  return { ...rg, fracDimension: fd, fdError, ...netDisplacement(pts), ...sinesCosines(pts), directions: dirs,
           persistence: persistence(dirs), ...localizationError(t), ...lg, ...diffusionVelocity(t, lg.lag) };
}

// Synthetic tracks for the demo (seeded; not data). kind: 'free' | 'confined' | 'directed'.
export function simulateTrack(rand, { n = 60, kind = 'free', step = 1, drift = 0.6, confine = 0.3 } = {}) {
  const gauss = () => { let u = 0, v = 0; while (!u) u = rand(); while (!v) v = rand(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const x = [0], y = [0], ang = rand() * 2 * Math.PI;
  for (let i = 1; i < n; i++) {
    let dx = gauss() * step, dy = gauss() * step;
    if (kind === 'directed') { dx += Math.cos(ang) * drift; dy += Math.sin(ang) * drift; }
    if (kind === 'confined') { dx -= confine * x[i - 1]; dy -= confine * y[i - 1]; }
    x.push(x[i - 1] + dx); y.push(y[i - 1] + dy);
  }
  return { frame: x.map((_, i) => i), x: x.map(v => v + 50), y: y.map(v => v + 50) };
}

// Parse "frame,x,y" (or "x,y") text; a header row is skipped.
export function parseTrack(text) {
  const rows = text.trim().split(/\r?\n/).map(l => l.split(/[,\t; ]+/).filter(Boolean).map(Number));
  const body = rows.filter(r => r.length >= 2 && r.every(Number.isFinite));
  if (body.length < 3) throw new Error('Need at least 3 rows of numbers: frame,x,y (or x,y).');
  const three = body.every(r => r.length >= 3);
  return { frame: body.map((r, i) => (three ? r[0] : i)), x: body.map(r => (three ? r[1] : r[0])), y: body.map(r => (three ? r[2] : r[1])) };
}
