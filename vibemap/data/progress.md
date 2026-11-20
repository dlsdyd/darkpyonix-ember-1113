# vibemap 진행 기록

대상: darkpyonix-ember (commit 876186d7)
실행 위치: 저장소 루트에서 `uv run vibemap/scripts/<script>.py` 로 실행한다.
저장소 루트의 `vibemap/` (사용자 승인 2026-11-20, AGENTS.md 기록). `vibemap/` 자체는 config.json으로 추출에서 뺀다.

## 단계
- [x] 0. 추출 (파일 657개, 모듈 후보 69개)
- [x] 1. 지도 (모듈 15개, 층 5개)
- [x] 2. 명함
- [x] 3. 증상 지도
- [x] 4. 흐름·이름
- [x] 5. 문제점

## 명함 우선순위 (used_by 많은 곳 → 사용자 접점 순)
- [x] server.agents (서버 모듈 대부분이 사용)
- [x] server.core
- [x] server.computers
- [x] app
- [x] client
- [x] node
- [x] server.comm
- [x] transport
- [x] editor
- [x] proxy
- [x] hub
- [x] extensions
- [x] bridge
- [x] ose
- [x] repo

## 메모
- 크레이트 간 의존(Cargo path 의존)은 import로 잡히지 않아 뷰어 연결선에 안 나온다. 흐름(4단계)에서 보완한다.
- 2~5단계 완료 (2026-11-20): 명함 15 (carded), 증상 20, 흐름 5, 이름 21, 이슈 11 (높음 2).
- 이슈 I1·I2는 docs/analysis/05_ISSUES.md의 I-004/I-005, I-003을 코드로 다시 확인한 것.
- 아직 verified 상태 모듈은 없다. 시작점을 사람이 열어 보고 올린다.
