import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { PropsWithChildren } from 'react';

export const colors = { bg: '#F4F3ED', ink: '#172B25', muted: '#61716A', green: '#126B4E', line: '#D9E0D8', orange: '#B64A27' };
export function Button({ title, onPress, disabled = false }: { title: string; onPress: () => void; disabled?: boolean }) {
  return <Pressable accessibilityRole="button" accessibilityState={{ disabled }} disabled={disabled} onPress={onPress}
    style={({ pressed }) => [s.button, { opacity: disabled ? 0.4 : pressed ? 0.75 : 1 }]}><Text style={s.buttonText}>{title}</Text></Pressable>;
}
export function Card({ children }: PropsWithChildren) { return <View style={s.card}>{children}</View>; }
export const s = StyleSheet.create({
  page: { flex: 1, backgroundColor: colors.bg },
  content: { padding: 22, gap: 18, paddingBottom: 50, maxWidth: 600, width: '100%', alignSelf: 'center' },
  eyebrow: { color: colors.green, fontSize: 12, fontWeight: '800', letterSpacing: 2 },
  title: { color: colors.ink, fontSize: 32, fontWeight: '800' },
  heading: { color: colors.ink, fontSize: 20, fontWeight: '700' },
  body: { color: colors.muted, fontSize: 15, lineHeight: 23 },
  card: { backgroundColor: '#FFFFFF', borderRadius: 22, padding: 22, gap: 14, borderWidth: 1, borderColor: colors.line },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12 },
  button: { backgroundColor: colors.green, borderRadius: 14, padding: 16, alignItems: 'center', minHeight: 50 },
  buttonText: { color: '#FFFFFF', fontSize: 16, fontWeight: '700' },
});
