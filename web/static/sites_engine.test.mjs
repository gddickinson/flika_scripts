// Node test: sites_engine.js reproduces groupSites() from "2014.09.19 Regroup by Radius.py".
import assert from 'node:assert/strict';
import { checks, close, fx } from './fixture.test.mjs';
import { groupSites } from './sites_engine.js';

const key = p => `${p.x}|${p.y}|${p.t_peak}`;
function check(puffs, run) {
  const r = groupSites(puffs, run.radius), byKey = new Map(r.puffs.map(p => [key(p), p]));
  assert.deepEqual(r.sites.flat().sort((a, b) => a - b), puffs.map((_, i) => i), 'each puff in exactly one site');
  assert.equal(run.result.length, puffs.length);
  for (const want of run.result) {
    const got = byKey.get(key(want));
    assert.ok(got, `puff ${key(want)} missing`);
    for (const k of ['Group #', 'No. Events']) assert.equal(got[k], want[k], `r=${run.radius} ${k}`);
    for (const k of ['Group x', 'Group y', 'Max Amp', 'Amplitude Normalized by Site Mean', 'Amplitude Normalized by Fitted Line'])
      close(got[k], want[k], `r=${run.radius} ${k}`);
  }
}
const { puffs, runs, line } = fx.sites;
for (const run of runs) check(puffs, run);
// Puff 2's neighbourhood touches both sites: before the fix it was in two; now 0-2 and 1-3 stay disjoint.
check(line.puffs, line.run);
assert.deepEqual(groupSites(line.puffs, 3).sites, [[0, 2], [1, 3]]);
console.log(`sites_engine: ${runs.length} radii, ${checks} values match Python`);
