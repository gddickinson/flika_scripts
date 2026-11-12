// Node test: sites_engine.js reproduces groupSites() from "2014.09.19 Regroup by Radius.py".
import assert from 'node:assert/strict';
import { checks, close, fx } from './fixture.test.mjs';
import { groupSites } from './sites_engine.js';

const { puffs, runs } = fx.sites;
const key = p => `${p.x}|${p.y}|${p.t_peak}`;
for (const run of runs) {
  const r = groupSites(puffs, run.radius), byKey = new Map(r.puffs.map(p => [key(p), p]));
  for (const want of run.result) {
    const got = byKey.get(key(want));
    assert.ok(got, `puff ${key(want)} missing`);
    for (const k of ['Group #', 'No. Events']) assert.equal(got[k], want[k], `r=${run.radius} ${k}`);
    for (const k of ['Group x', 'Group y', 'Max Amp', 'Amplitude Normalized by Site Mean', 'Amplitude Normalized by Fitted Line'])
      close(got[k], want[k], `r=${run.radius} ${k}`);
  }
}
// The merge quirk: A-i and M-k form sites first, then i's neighbourhood touches both.
const q = [0, 3, 1, 2].map((x, i) => ({ x, y: 0, t_peak: i, Amplitude: 1 }));
assert.deepEqual(groupSites(q, 1).inTwoSites.sort(), [1, 3]);
console.log(`sites_engine: ${runs.length} radii, ${checks} values match Python`);
