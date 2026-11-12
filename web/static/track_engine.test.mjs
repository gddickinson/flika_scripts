// Node test: track_engine.js reproduces the PIEZO1 track-feature functions on the fixture tracks.
// Run: node web/static/track_engine.test.mjs
import assert from 'node:assert/strict';
import { checks, close, closeAll, fx } from './fixture.test.mjs';
import { analyseTrack } from './track_engine.js';

for (const c of fx.tracks) {
  const r = analyseTrack(c.input), name = c.input.name;
  for (const k of ['rg', 'asymmetry', 'skewness', 'kurtosis', 'netDispl', 'efficiency', 'sin_mean', 'cos_mean',
    'persistence', 'meanLocDistanceFromCenter', 'meanLag', 'track_length', 'rg_scaled', 'rg_scaled_trackLength',
    'meanVelocity']) close(r[k], c[k], `${name} ${k}`);
  if (typeof c.fracDimension === 'string') assert.equal(r.fdError, c.fracDimension, `${name} collinear error`);
  else close(r.fracDimension, c.fracDimension, `${name} fracDimension`);
  for (const k of ['sin_vals', 'cos_vals', 'directions', 'distanceFromMean', 'lag', 'distanceFromOrigin', 'lagNumber',
    'd_squared', 'velocity', 'dt', 'dydt', 'direction_origin']) closeAll(r[k], c[k], `${name} ${k}`);
}
console.log(`track_engine: ${fx.tracks.length} tracks, ${checks} values match Python`);
