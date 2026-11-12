// Node test: signal_engine.js reproduces movingaverage() from testing_misc/smoothing.py.
import { checks, closeAll, fx } from './fixture.test.mjs';
import { movingAverage } from './signal_engine.js';

for (const run of fx.smoothing.runs) closeAll(movingAverage(fx.smoothing.y, run.window), run.result, `window ${run.window}`);
console.log(`signal_engine: ${checks} values match Python`);
