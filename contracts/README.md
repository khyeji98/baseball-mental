# API 계약

`openapi.json`은 FastAPI에서 생성한 현재 서버 API 명세다. 직접 수정하지 않는다.

```sh
cd apps/server
uv run python export_openapi.py
```

서버 API 변경과 스키마 변경을 같은 커밋에 포함한다. CI에서 재생성 후 차이가 없는지 검사한다. 모바일은 아직 샘플 데이터로 동작하며, 이 계약을 통한 실제 앱 연결과 TypeScript 클라이언트 생성은 미완료다.
