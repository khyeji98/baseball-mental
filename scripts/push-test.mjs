// Runs only when explicitly invoked with a test-device token in the environment.
const token = process.env.EXPO_PUSH_TOKEN;
if (!token || !/^(ExponentPushToken|ExpoPushToken)\[.+\]$/.test(token)) {
  throw new Error('Set EXPO_PUSH_TOKEN to the token shown on your test device.');
}
const headers = { 'Content-Type': 'application/json' };
if (process.env.EXPO_ACCESS_TOKEN) headers.Authorization = `Bearer ${process.env.EXPO_ACCESS_TOKEN}`;
async function post(path, body) {
  const response = await fetch(`https://exp.host/--/api/v2/push/${path}`, { method: 'POST', headers, body: JSON.stringify(body), signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error(`Expo HTTP ${response.status}`);
  const result = await response.json();
  if (result.errors?.length) throw new Error(JSON.stringify(result.errors));
  return result.data;
}
if (process.env.EXPO_RECEIPT_ID) {
  console.log(JSON.stringify(await post('getReceipts', { ids: [process.env.EXPO_RECEIPT_ID] }), null, 2));
} else {
  const ticket = await post('send', { to: token, title: '오늘은 마음을 단단히!', body: '[원격 푸시 검증] 눌러서 샘플 경기를 열어주세요.', sound: 'default', channelId: 'game-reminders', data: { gameId: 'demo-1' } });
  if (ticket.status !== 'ok') throw new Error(JSON.stringify(ticket));
  console.log(`Expo accepted the request. Receipt ID: ${ticket.id}`);
  console.log('This is NOT confirmation of device delivery. Check the device, then query receipts with EXPO_RECEIPT_ID.');
}
