# 모듈: bridge

- 경로: `ember/bridge/` (크레이트 `ember-bridge`, `ember/bridge/Cargo.toml:2`) + 데이터 `ember/vectors/` (`bridge/`, `transcripts/`)
- 규모: 소스 6개 / 약 840줄 (`src/*.rs` 5개 831줄, `Cargo.toml` 12줄). 벡터는 `ember/vectors/` 파일 44개(JSON, JSONL, 마크다운)
- 레이어: 공용 (IDE 창 브리지 프로토콜) + 테스트 데이터(`vectors`)
- 한 줄 책임: VS Code Web 웹뷰(`detach.js`)와 네이티브 셸이 주고받는 창 분리 메시지의 형식, 인코딩, 처리 로직을 정의한다 (`ember/bridge/src/lib.rs:1-14`, SPEC FR-B1~B4).
- 의존하는 모듈: 외부 크레이트만 (`serde`, `serde_json`, `thiserror`, `tracing`, `ember/bridge/Cargo.toml:8-11`). 저장소의 다른 크레이트를 쓰지 않는다.
- 이 모듈을 쓰는 모듈: 없다. `ember-bridge`를 의존하는 `Cargo.toml`은 자기 자신뿐이고 (`grep ember-bridge`), `ember_bridge`를 쓰는 Rust 소스도 없다. `ember/app/src/bridge.rs`, `ember/editor/src/bridge.rs`는 이름만 같고 이 크레이트를 쓰지 않는다 [확인 필요: 두 파일은 읽지 않았고 import 그래프와 grep 결과만 근거]. 웹 쪽 짝은 `ember/proxy/static/detach.js`다 (`ember/bridge/src/messages.rs:14`).

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `HANDLER_NAME` (`"emberBridge"`) | const | `ember/bridge/src/messages.rs:24` | 네이티브가 등록하는 메시지 핸들러 이름 |
| `KIND_TAB_DETACH`, `KIND_SIBLING_WINDOW_CLOSED`, `KIND_OPEN_WINDOW` | const | `ember/bridge/src/messages.rs:26-28` | `kind` 문자열 |
| `Position`, `Range`, `Scroll`, `ScreenPoint`, `Workspace` | struct | `ember/bridge/src/messages.rs:32`, `:40`, `:47`, `:55`, `:63` | 위치(0 기반 줄, 열), 범위, 스크롤, 화면 좌표, 작업 폴더 |
| `TabDetach` | struct | `ember/bridge/src/messages.rs:71` | 웹뷰에서 네이티브로: 탭을 끌어냈다. `latency_ms` (`:101`) |
| `SiblingWindowClosed` | struct | `ember/bridge/src/messages.rs:109` | 네이티브에서 웹뷰로: 다른 창이 닫혔다 |
| `OpenWindow` | struct | `ember/bridge/src/messages.rs:119` | 새 창 열기 요청. `from_detach` (`:140`), `vscode_web_path` (`:161`) |
| `BridgeMessage`, `Inbound`, `DecodeError`, `encode`, `decode` | enum/fn | `ember/bridge/src/messages.rs:185`, `:224`, `:242`, `:211`, `:266` | 와이어 변환 |
| `WebviewBridge`, `LoopbackBridge`, `BridgeError` | trait/struct/enum | `ember/bridge/src/bridge.rs:27`, `:44`, `:20` | 플랫폼 브리지 트레이트와 시험용 구현 |
| `WindowOpener`, `BridgeHost`, `HostOutcome`, `notify_sibling_closed` | trait/struct/enum/fn | `ember/bridge/src/host.rs:13`, `:29`, `:18`, `:99` | 네이티브 호스트 로직 |

## 파일별 요약

### `ember/bridge/src/lib.rs` (29줄)
- 목적: 모듈 선언 `bridge`, `host`, `messages`, `url`(비공개, `ember/bridge/src/lib.rs:19-22`)과 재노출. "No platform webview implementation lives here yet" (`:11`)라고 적혀 있다.

### `ember/bridge/src/messages.rs` (414줄)
- 목적: 와이어 형식. 모든 메시지는 문자열 `kind`가 있는 JSON 객체이고 나머지 필드는 같은 객체에 camelCase로 펼쳐진다 (`ember/bridge/src/messages.rs:3-5`). 버전 필드는 없다 (INTENT D15, `:8`). 선택 필드 추가는 항상 호환되고 알 수 없는 필드는 무시, 알 수 없는 `kind`는 로그 후 `Inbound::UnknownKind`로 보존한다 (`:8-10`). 위치는 0 기반 (`:11`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `TabDetach` | struct | 71 | `source_window_id`, `file_uri` 필수. `workspace`, `cursor`, `scroll`, `selection`는 `#[serde(default)]`. `screen`, `label`, `editor`, `state_source`, `sent_at_ms`는 FR-B4 추가 필드 |
| `OpenWindow::from_detach` | fn | 140 | `TabDetach`에서 새 창 요청 생성 |
| `OpenWindow::vscode_web_path` | fn | 161 | `/?folder=<enc>&payload=<enc JSON>` 경로 생성. 폴더가 없으면 `None`. 커서가 있고 URI에 `?`나 `#`가 없으면 `openFile`에 `:줄:열`(1 기반)과 `gotoLineMode`를 넣는다. 선택 범위와 스크롤은 이 경로로 전달되지 않는다 (`:157-160`) |
| `encode` | fn | 211 | `kind`를 넣은 객체를 JSON 문자열로 |
| `decode` | fn | 266 | JSON 파싱, `kind` 확인, 알 수 없는 kind는 `tracing::warn!` 후 보존, 필드 오류는 `DecodeError::Invalid` |
- 부수효과: `tracing::warn!` 로그 (`:271-282`).
- 주의점: 머리 주석은 `ember/proxy/static/detach.js`(`buildDetachMessage`, `buildWorkspaceQuery`)와 동기를 유지하라고 한다 (`:14-15`). `TabDetach`의 `workspace`, `cursor` 등은 `skip_serializing_if`가 없어 `None`이 `null`로 직렬화된다 (`:75-82`) [추정: `serde` 기본 동작]. 테스트 7개 (`:311-401`), 이 중 `browser_url_matches_shared_vectors`는 `ember/vectors/bridge/detach_vectors.json`을 읽는다 (`:388-401`).

### `ember/bridge/src/host.rs` (235줄)
- 목적: 네이티브 호스트의 처리 (FR-B3, FR-B4). 셸은 웹뷰가 보낸 문자열을 `BridgeHost::handle_from_webview`에 넘긴다 (`ember/bridge/src/host.rs:3`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `WindowOpener` | trait | 13 | 셸이 구현. `open_window(&mut self, &OpenWindow)` |
| `HostOutcome` | enum | 18 | `Opened`, `OpenFailed{request,error}`, `Ignored{kind,reason}`, `Rejected(String)` |
| `BridgeHost` | struct | 29 | `new(opener, id_prefix)`, `handle_from_webview` (`:68`). 창 id는 `<prefix>-<n>` (`:49-53`) |
| `notify_sibling_closed` | fn | 99 | `SiblingWindowClosed`를 `post_to_webview`로 푸시 |
- 동작: `TabDetach`는 새 id를 붙여 `OpenWindow::from_detach`로 열고, `OpenWindow`는 `window_id`가 비면 id를 배정한다. 웹뷰가 `SiblingWindowClosed`를 보내면 `Ignored`다 (`:68-96`).
- 주의점: 더럽힌(dirty) 탭을 분리하지 않는 일은 `detach.js` 쪽 책임이다 (`:7`). `next_id`는 `u64` 증가형이라 `BridgeHost`가 프로세스 안에서만 고유하다. 테스트 7개.

### `ember/bridge/src/bridge.rs` (117줄)
- 목적: 플랫폼 브리지 트레이트. macOS와 iOS는 `WKScriptMessageHandler`와 `evaluateJavaScript`, Windows는 `WebMessageReceived`와 `PostWebMessageAsString`으로 매핑한다 (`ember/bridge/src/bridge.rs:3-8`).
- `WebviewBridge` (`:27`): `send_to_native`, `send_to_webview`는 구현자가 채우고, `post_to_native`, `post_to_webview`는 `encode`를 거치는 기본 메서드 (`:33-38`). `LoopbackBridge` (`:44`)는 방향별 큐를 `Mutex<Vec<String>>`에 쌓고 `close()` 후에는 `BridgeError::Closed`를 돌려준다. 테스트 3개 (객체 안전성 포함).

### `ember/bridge/src/url.rs` (36줄)
- `encode_uri_component` (`ember/bridge/src/url.rs:9`, `pub(crate)`): JS `encodeURIComponent`와 같은 결과. 비예약 문자 집합은 `A-Z a-z 0-9 - _ . ! ~ * ' ( )` (`:5-7`). `OpenWindow::vscode_web_path`만 쓴다. 테스트 1개.

### `ember/bridge/Cargo.toml` (12줄)
- 설명 문구가 "versioned webview <-> native messages"인데 (`ember/bridge/Cargo.toml:5`) 코드는 버전을 두지 않는다 (`ember/bridge/src/messages.rs:8`, D15).

### `ember/vectors/` (데이터, 폴더당 한 줄)

| 폴더 | 내용 |
|---|---|
| `ember/vectors/bridge/` | `detach_vectors.json` 1개(105줄). `tab_detach` 입력과 기대 경로 `expectedPath`(없으면 `null`). `ember/proxy/tests/js/detach.test.js`와 `ember/bridge/src/messages.rs`가 함께 읽는다 (파일 안 `$comment`) |
| `ember/vectors/transcripts/` | `SCHEMA.md`(83줄)가 정규화 형식을 정의한다 (`native_id`, `cwd`, `title`, `messages[role,text,tool_name,tool_call_id,is_error]`). 사용처는 `.github/scripts/checks/test-transcript-vectors.sh`, `ember/server/src/history/mod.rs`, `ember/proxy/tests/test_transcript_vectors.py` |
| `ember/vectors/transcripts/claude-code/` | 사례 9개 (`empty`, `malformed-truncated`, `multiline-unicode`, `plain-chat`, `sidechain`, `summary-compaction`, `summary-title`, `tool-use`, `unknown-types`), 각각 `input.jsonl`과 `expected.json` |
| `ember/vectors/transcripts/codex/` | 사례 7개 (`compaction`, `empty`, `malformed-truncated`, `multiline-unicode`, `plain-chat`, `tool-use`, `unknown-types`), 각각 `input.jsonl`과 `expected.json` |

## 동작 지도

UI 모듈이 아니라 프로토콜 라이브러리이므로 사용자 동작은 웹뷰 쪽(`detach.js`)에서 시작한다. 이 크레이트 안에서의 흐름만 적는다.

| 사용자 동작 | 화면 문구 | 핸들러 | 호출 API |
|---|---|---|---|
| 탭을 탭 줄 밖으로 끌어낸다 | 없음 (이 크레이트는 화면 문구를 만들지 않는다) | `BridgeHost::handle_from_webview` `ember/bridge/src/host.rs:68` | `WindowOpener::open_window` `ember/bridge/src/host.rs:14` |
| 다른 창이 닫힘 | 없음 | `notify_sibling_closed` `ember/bridge/src/host.rs:99` | `WebviewBridge::post_to_webview` `ember/bridge/src/bridge.rs:36` |

사용자에게 보이는 에러 메시지는 없다. 호출자에게 돌려주는 오류 문구는 다음과 같다.

| 원문 | 위치 | 조건 |
|---|---|---|
| `bridge message is not JSON: {0}` | `ember/bridge/src/messages.rs:243` | JSON이 아님 |
| `bridge message is not a JSON object with a string "kind"` | `ember/bridge/src/messages.rs:245` | `kind`가 없거나 문자열이 아님 |
| `bridge message {kind} has invalid fields: {source}` | `ember/bridge/src/messages.rs:247` | 필수 필드 누락 등 |
| `the webview or window is gone` | `ember/bridge/src/bridge.rs:21` | 브리지가 닫힘 |

## 데이터와 설정

- DB, 환경 변수, 저장 파일 없음. 외부 연동: 웹뷰 쪽 `ember/proxy/static/detach.js`와 VS Code Web의 `workbench.ts`, `environmentService.ts` 동작에 의존한다 (`ember/bridge/src/messages.rs:165-169`).
- 벡터 데이터는 소스 한 곳이 아니라 여러 러너(Rust, JS, Python)가 공유한다 (위 표).

## 이 모듈을 수정할 때 주의할 점

- `messages.rs`의 필드나 `vscode_web_path` 규칙을 바꾸면 `ember/proxy/static/detach.js`와 `ember/vectors/bridge/detach_vectors.json`, `ember/proxy/tests/js/detach.test.js`를 같이 고친다.
- `ember/vectors/transcripts/`의 기대값을 바꾸면 Rust(`ember/server/src/history/`)와 Python(`ember/proxy/dpx/agents/`) 파서 양쪽이 통과해야 한다 (`.github/scripts/checks/test-transcript-vectors.sh`).
- `.jsonl` 벡터는 실제 CLI에서 캡처한 기록이므로 em-dash 검사에서 제외된다 (AGENTS.md).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 의존자 없음 | 중간 | `ember/bridge/Cargo.toml` | `ember-bridge`를 쓰는 크레이트가 저장소에 없다. 진입점이 없는 죽은 크레이트이거나 셸이 아직 붙지 않은 상태다 (`ember/bridge/src/lib.rs:11`, "No platform webview implementation lives here yet") | 의존할 셸을 정하거나 상태를 문서에 적는다 |
| 문서 불일치 | 낮음 | `ember/bridge/Cargo.toml:5` | "versioned"라고 적었지만 코드는 버전 없음 (D15) | 설명 수정 |
| 하드코딩 | 낮음 | `ember/bridge/src/messages.rs:165-169` | VS Code Web 내부 동작(`openFile`, `gotoLineMode`)에 묶여 있다 | VS Code 갱신 때 벡터로 회귀 확인 |
| 직렬화 일관성 | 낮음 | `ember/bridge/src/messages.rs:75-82` | `TabDetach`/`OpenWindow`의 일부 선택 필드가 `null`로 직렬화된다 [추정] | `skip_serializing_if` 통일 여부 결정 |
| 타입 | 낮음 | `ember/bridge/src/messages.rs:84-97` | `sent_at_ms`가 `f64`다 (밀리초 에포크는 `f64`로 정확하지만 비교, 직렬화 때 정수 표현이 아님) | 현재는 JS `Date.now()`와 맞춘 것으로 보임 [추정] |
| TODO/FIXME | 낮음 | `ember/bridge/src/` | 0개 (grep) | 없음 |
