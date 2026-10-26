# 왜저럴까 — RN / Expo 기술 검증

SwiftUI 개발자가 혼자 iOS·Android 서비스를 관리할 수 있는지 확인하는 작은 앱입니다.
가상 경기 목록 → 상세 → 상황별 멘탈 게이지 → 공유와 알림을 검증합니다.
실제 KBO 데이터 수집, 시즌 통계, 로그인, 서버, 영속 저장은 구현하지 않았습니다.
샘플 이벤트 진행 버튼은 자동 중계 수신을 재현하는 테스트 도구입니다.

## 시작

Node.js 22.23 이상 권장. `npm ci` 후 다음 명령을 사용합니다.

```sh
npm run web       # 화면 미리보기 (푸시 검증 불가)
npm start        # 전용 개발 빌드용 Metro
npm run typecheck
npm run lint
npm test
npx expo export --platform all
```

Expo SDK 58 / React Native 0.88 / TypeScript / Expo Router 기반입니다.
Expo Go 호환 여부에 기대지 않고 development 또는 preview 빌드로 알림을 검증합니다.
번들 생성 성공은 네이티브 빌드나 기기 실행 성공을 의미하지 않습니다.

## Expo 계정 연결과 외부 기기 테스트

1. https://expo.dev/signup 에서 계정을 만듭니다.
2. 프로젝트 폴더에서 `npx eas-cli@latest login` 후 `npx eas-cli@latest init`을 실행합니다.
3. 생성된 `extra.eas.projectId`를 app.json에 반영합니다. 이 식별자는 비밀이 아닙니다.
4. app.json의 임시 bundleIdentifier / android.package를 본인 소유의 고유 ID로 확정합니다. 첫 빌드 전에 결정합니다.
5. Android 원격 푸시는 Firebase Android 앱 등록과 FCM v1 설정이 필요합니다. Firebase의 패키지명은 위 ID와 같아야 합니다.
6. `google-services.json`은 EAS file 환경 변수로 제공하고 app.config.ts의 `GOOGLE_SERVICES_JSON` 경로를 사용합니다. 로컬 사용 시에도 이 파일은 커밋하지 않습니다. FCM 서비스 계정 키는 `npx eas-cli@latest credentials --platform android`로 EAS에 설정하며 Git에 올리지 않습니다.
7. iOS는 Apple Developer 계정으로 서명·APNs 자격 증명을 설정합니다. 내부 배포 기기는 `npx eas-cli@latest device:create`로 등록하고 빌드에 포함합니다.

### 성현님 Galaxy: Metro 없이 설치·실행

```sh
npx eas-cli@latest build --platform android --profile preview
```

빌드가 성공하면 EAS의 APK 다운로드 링크를 전달합니다. 저장소를 클론하거나 PC를 켜둘 필요가 없습니다.
개발자 도구 없이 설치 가능한 standalone preview 빌드입니다. 기기에서 출처 허용이 필요할 수 있습니다.
현재 APK 또는 설치 링크가 생성되어 있지는 않습니다. Expo 로그인·프로젝트 연결이 먼저입니다.
FCM 설정 전에는 화면과 로컬 알림까지, 설정 후에는 원격 푸시까지 확인합니다.

### 본인 iPhone

```sh
npx eas-cli@latest build --platform ios --profile preview
```

등록한 iPhone용 내부 배포 빌드를 설치합니다. 시뮬레이터는 별도의 `simulator` 프로필을 사용합니다.
EAS 빌드는 계정별 무료 할당량과 큐 조건을 확인한 후 실행합니다. 유료 플랜 자동 가입은 하지 않습니다.

## 알림 검증

1. 앱의 알림 검증 화면에서 **5초 뒤 테스트 알림** 실행 → 배경 전환 → 수신 → 탭 후 경기 화면 이동 확인.
2. **푸시 토큰 받기**로 자신의 테스트 기기 토큰 발급. 토큰은 기록·공개하지 않습니다.
3. 터미널 환경 변수 `EXPO_PUSH_TOKEN`에 토큰을 넣고 `npm run push:test`를 실행합니다.
4. Expo push security를 켰다면 `EXPO_ACCESS_TOKEN`도 환경 변수로 제공합니다. 앱에 넣지 않습니다.
5. 출력된 receipt ID를 `EXPO_RECEIPT_ID` 환경 변수에 넣어 같은 명령으로 영수증을 조회합니다. 아직 영수증이 없으면 잠시 뒤 다시 조회합니다.
6. ticket/receipt 성공과 실제 수신을 구분합니다. 두 기기 모두 전경·배경·종료 상태의 수신과 탭 이동을 확인합니다.

스크립트는 `.env`를 자동으로 읽지 않습니다. 셸 환경이나 비밀 관리 도구에서 주입해주세요.
비밀값을 셸 히스토리에 남기지 않도록 입력하며, 채팅·이슈·스크린샷에도 올리지 않습니다.

## 공개 저장소와 비밀 관리

- `.env*`, 인증서, 서명키, Firebase 설정, credentials.json은 Git에서 제외합니다.
- 앱 번들에 포함되는 `EXPO_PUBLIC_*` 값과 app config의 extra 값은 비밀 저장소가 아닙니다.
- EAS Secret으로 넣어도 앱 코드에 삽입하면 사용자가 추출할 수 있습니다. 서비스 계정·서버 키는 서버나 빌드 자격 증명으로만 사용합니다.
- 사용자/실제 선수 정보나 외부 서비스 인증 정보 없이 가상 데이터만 제공합니다.

## SwiftUI 개발자용 코드 지도

| 익숙한 개념 | 이번 구현 |
|---|---|
| NavigationStack | src/app/_layout.tsx의 Expo Router Stack |
| 화면 View | src/app/index.tsx, game/[id].tsx, notifications.tsx |
| @State | React useState |
| 계산 모델 | src/domain/game.ts의 순수 함수 |
| 공통 View·스타일 | src/ui.tsx |

기술 선택 전 직접 해볼 작업: 기본 멘탈 30을 변경하고, 이벤트 하나 추가하고, 화면 문구를 바꾸고,
타입 오류를 하나 직접 해결해보세요. 변경 위치를 이해하고 설명할 수 있는지 확인합니다.

## 검증 현황 (2026-10-26)

- 화면과 알림 등록/탭 이동 코드 구현.
- iOS·Android·웹 JavaScript 번들 생성 성공. 네이티브 실행 성공은 아직 미확인.
- 타입 검사·lint·도메인 테스트는 실제 실행 결과를 기준으로 CI에서도 확인합니다.
- Expo 계정, APNs/FCM 설정, 기기 설치·수신·공유·뒤로 가기 검증: 대기.
- Android SDK가 기본 경로에 없으므로 외부 Galaxy는 EAS preview APK로 검증 예정.
- npm audit: Expo CLI의 node-forge/Zod 경로에 high 경고 5건. SDK 44로 강제 다운그레이드하는 자동 제안은 적용하지 않았습니다. 출시 전에 SDK 호환 패치/상위 패키지 업데이트 검토가 필요합니다.

## 합격 기준

양쪽 기기에서 설치 → 목록 → 상세 → 이벤트 → 공유 → 뒤로 가기, 알림 거절/허용, 원격 푸시 수신과
콜드 스타트 탭 이동을 확인합니다. 네이티브 오류 해결 시간을 기록하고 위의 직접 수정 과제를 수행한 뒤 스택을 확정합니다.
경기 데이터 수집 POC 합격 여부는 이 앱 검증과 별도입니다.

공식 참고: [푸시 설정](https://docs.expo.dev/push-notifications/push-notifications-setup/),
[내부 배포](https://docs.expo.dev/build/internal-distribution/).
