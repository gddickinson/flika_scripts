// movingaverage() from piezo1_analysis/workFlow_3/testing_misc/smoothing.py (also in Step_10): a running mean over
// `window` points ('valid' convolution) padded at both ends with the edge values to the input length.
// Checked by signal_engine.test.mjs against tests/fixtures/demo_cases.json.
export function movingAverage(y, window = 10) {
  const w = Math.trunc(window), n = y.length;
  if (w < 1 || w > n) throw new Error(`window must be between 1 and ${n}`);
  const smooth = [];
  for (let i = 0; i + w <= n; i++) { let s = 0; for (let k = 0; k < w; k++) s += y[i + k] * (1 / w); smooth.push(s); }
  const start = Math.trunc((n - smooth.length) / 2), end = n - (start + smooth.length);
  return [...new Array(start).fill(smooth[0]), ...smooth, ...new Array(end).fill(smooth[smooth.length - 1])];
}
