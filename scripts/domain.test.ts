import assert from 'node:assert/strict';
import test from 'node:test';
import { games, stressDelta, summarize } from '../src/domain/game.ts';

test('a late close-game bases-loaded out is more stressful than an early out', () => {
  const play = games[0].plays[3];
  assert.ok(stressDelta(play) > stressDelta({ ...play, inning: 1, outs: 0, runners: 0 }));
});
test('replaying the same event does not double count, and correction replaces it', () => {
  const play = games[0].plays[0];
  assert.deepEqual(summarize([play, play]), summarize([play]));
  const corrected = { ...play, baseStress: 0 };
  assert.equal(summarize([play, corrected]).raw, 0);
});
test('recovery reduces stress and clipping preserves raw history', () => {
  assert.ok(stressDelta(games[0].plays[2]) < 0);
  const huge = { ...games[0].plays[0], baseStress: 1000 };
  assert.equal(summarize([huge]).level, 100);
  assert.ok(summarize([huge]).raw > 100);
  assert.equal(summarize([{ ...huge, baseStress: -1000 }]).level, 0);
});
