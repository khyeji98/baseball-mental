import { Stack, router } from 'expo-router';
import { useEffect } from 'react';
import { Platform } from 'react-native';
import { colors } from '../ui';
import { games } from '../domain/game';
import type { NotificationResponse } from 'expo-notifications';

export default function Layout() {
  useEffect(() => {
    if (Platform.OS === 'web') return;
    let cleanup: (() => void) | undefined;
    let active = true;
    void import('expo-notifications').then(N => {
      if (!active) return;
      N.setNotificationHandler({ handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: true, shouldSetBadge: false }) });
      const open = (response: NotificationResponse | null) => {
        const id = response?.notification.request.content.data?.gameId;
        if (typeof id === 'string' && games.some(game => game.id === id)) {
          router.push({ pathname: '/game/[id]', params: { id } });
          void N.clearLastNotificationResponseAsync();
        }
      };
      const sub = N.addNotificationResponseReceivedListener(open);
      cleanup = () => sub.remove();
      void N.getLastNotificationResponseAsync().then(response => { if (active) open(response); }).catch(() => {});
    }).catch(() => {});
    return () => { active = false; cleanup?.(); };
  }, []);
  return <Stack screenOptions={{ headerStyle: { backgroundColor: colors.bg }, headerTintColor: colors.ink, contentStyle: { backgroundColor: colors.bg } }}>
    <Stack.Screen name="index" options={{ title: '왜저럴까 · 기술 검증' }} />
    <Stack.Screen name="game/[id]" options={{ title: '오늘의 멘탈' }} />
    <Stack.Screen name="notifications" options={{ title: '알림 검증' }} />
  </Stack>;
}
