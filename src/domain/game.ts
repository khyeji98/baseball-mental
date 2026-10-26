export type Play = {
  id: string;
  inning: number;
  outs: number;
  runners: number;
  margin: number;
  label: string;
  baseStress: number;
};

export const games = [
  { id: 'demo-1', away: 'LG', home: '두산', score: '3 : 3', inning: '9회 말', note: '2아웃 · 만루', plays: [
    { id: 'p1', inning: 3, outs: 1, runners: 1, margin: 0, label: '수비 실책', baseStress: 12 },
    { id: 'p2', inning: 5, outs: 0, runners: 2, margin: -1, label: '병살타', baseStress: 18 },
    { id: 'p3', inning: 7, outs: 2, runners: 2, margin: -1, label: '동점 적시타', baseStress: -16 },
    { id: 'p4', inning: 9, outs: 2, runners: 3, margin: 0, label: '끝내기 기회에서 뜬공', baseStress: 14 },
  ] },
  { id: 'demo-2', away: '한화', home: '롯데', score: '2 : 1', inning: '7회 초', note: '1아웃 · 주자 없음', plays: [
    { id: 'p5', inning: 2, outs: 0, runners: 0, margin: 0, label: '땅볼 아웃', baseStress: 6 },
    { id: 'p6', inning: 4, outs: 2, runners: 2, margin: -1, label: '실점을 막은 호수비', baseStress: -12 },
    { id: 'p7', inning: 7, outs: 1, runners: 0, margin: 1, label: '수비 실책', baseStress: 12 },
  ] },
];

// POC heuristic only. Production coefficients need baseball-data validation.
export function stressDelta(play: Play): number {
  const lateClose = play.inning >= 7 && Math.abs(play.margin) <= 2;
  const weight = 1 + (lateClose ? 0.6 : 0) + play.runners * 0.15 + (play.outs === 2 ? 0.2 : 0);
  return Math.round(play.baseStress * weight);
}

export function summarize(plays: Play[]) {
  const unique = [...new Map(plays.map(play => [play.id, play])).values()];
  const deltas = unique.map(stressDelta);
  const raw = deltas.reduce((sum, delta) => sum + delta, 0);
  return { raw, level: Math.max(0, Math.min(100, 30 + raw)), deltas };
}
