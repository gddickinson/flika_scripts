// Node test: the highlighter keeps every character and every line of the source.
import assert from 'node:assert/strict';
import { highlight } from './highlight.js';

const src = 'def f(a, b=2):\n    """doc\n    more"""\n    return a  # note\n\nx = "s\'t" + f(1.5e3)\n';
const lines = highlight(src);
assert.equal(lines.length, src.split('\n').length);
const plain = lines.map(l => l.replace(/<[^>]+>/g, '').replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')).join('\n');
assert.equal(plain, src);
assert.ok(lines[0].includes('tk-k') && lines[0].includes('tk-f'));
assert.ok(lines[3].includes('tk-c'));
console.log('highlight: lines and text preserved');
