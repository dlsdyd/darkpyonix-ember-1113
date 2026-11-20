# 사용되지 않는 파일 후보 (Phase 3)

> 팬인 0이고 진입점·테스트·정적 자원이 아닌 코드 파일. 추출기는 정규식 기반이라 매크로, `include_str!`, `#[path]`, 동적 import, HTML의 `<script src>`는 보지 못한다. 확정은 Phase 4 모듈 분석에서 한다.

| 경로 | 라인수 | 비고 |
|---|---|---|
| `.github/scripts/bench/summarize-matrix.py` | 233 | 스크립트 진입점. `.github/scripts/bench/tests/summarize-matrix.test.sh`가 실행한다. 고아 아님 |
| `docs/guide/assets/guide.js` | 84 | `docs/guide/en/*.html`의 `<script src>`가 불러온다. 고아 아님 |
| `ember/ose/regression/regress.py` | 93 | `ember/ose/regress.sh`가 실행한다. 고아 아님 |
| `ember/proxy/dpx/hub/server.py` | 361 | 별도 앱 진입점: `uvicorn dpx.hub.server:app` (`ember/proxy/docs/HUB.md:42`). 고아 아님 |
| `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/actions/NotebookActions.kt` | 73 | `plugin.xml` 등록 여부 [확인 필요] |
| `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/protocol/CellSync.kt` | 144 | 테스트(`CellSyncTest.kt`)만 참조한다. 제품 코드 사용처 [확인 필요] |
| `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/protocol/Models.kt` | 234 | 파일명과 다른 클래스(`CellLock`, `CellCursor` 등)를 담아 추출기가 놓쳤다. Phase 4에서 확인 |
| `extensions/vscode-darkpyonix/esbuild.mjs` | 27 | 빌드 설정 (npm 스크립트). 고아 아님 |
| `extensions/vscode-darkpyonix/vitest.config.mjs` | 8 | 테스트 설정 (vitest가 읽는다). 고아 아님 |
