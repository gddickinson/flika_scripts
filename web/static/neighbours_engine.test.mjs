// Node test: neighbours_engine.js reproduces getNN (Step_3) and getNNinFrame (Step_8).
import { checks, closeAll, fx } from './fixture.test.mjs';
import { neighbours } from './neighbours_engine.js';

for (const [i, c] of fx.neighbours.entries()) {
  const r = neighbours(c.input);
  closeAll(r.nnDist_nm, c.nnDist_nm, `case ${i} nnDist`);
  for (const [rad, want] of Object.entries(c.counts)) closeAll(r.counts[rad], want, `case ${i} r=${rad}`, 0);
}
console.log(`neighbours_engine: ${checks} values match Python`);
