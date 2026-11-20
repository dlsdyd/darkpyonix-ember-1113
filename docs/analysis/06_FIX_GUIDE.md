# 수정 가이드

- 기준 커밋: `ffe9825` / 작성: 2026-11-13
- "함께 고쳐야 하는 곳"은 각 모듈 문서의 "이 모듈을 수정할 때 주의할 점"에서 모았다. 경로 표기는 [01_FEATURE_MAP.md](01_FEATURE_MAP.md)와 같다 (`cr/`는 `ember/app/src/ui/cr/`).

## 1. 수정 절차 (항상 이 순서로)

1. **위치 찾기:** [01_FEATURE_MAP.md](01_FEATURE_MAP.md)에서 화면 문구나 기능을 검색해 핸들러와 API 위치를 찾는다. 앱 화면은 `cr/`에, 그 화면이 쓰는 문구 상수·계산·API 호출은 같은 이름의 `ember/app/src/ui/<파일>.rs`에 있는 경우가 많다.
2. **이름 확인:** [02_GLOSSARY.md](02_GLOSSARY.md)에서 관련 이름의 뜻을 확인한다. 환경 변수와 상태 enum은 [02_GLOSSARY-2.md](02_GLOSSARY-2.md).
3. **영향 범위 확인:** 고칠 함수의 사용처를 모두 찾는다 (에디터 "모든 참조 찾기" 또는 `git grep -n <이름> -- ember`).
   - 사용처 1곳: 바로 고친다.
   - 사용처 여러 곳: 시그니처를 바꾸지 말고 옵션 인자나 새 함수를 더한다.
   - `ember/app/src/ui/<파일>.rs`의 함수: Dioxus 화면과 `cr/` 화면이 함께 쓴다. `cr/` 쪽 `pub use` 목록이 이름에 묶여 있다.
4. **스펙 먼저:** 저장소 규칙상 동작 변경은 `docs/SPEC.md`에 ID가 먼저 있어야 하고, 실패하는 테스트를 먼저 쓴다 (`AGENTS.md` "Spec and tests first").
5. **재현:** 고치기 전에 재현 방법을 적어 둔다. 서버 없이 화면만 볼 때는 데모 모드(`EMBER_DEMO_DATA=1`, 서버 URL 없이)를 쓴다. 데모 모드에서는 서버 호출이 `self.demo` 분기로 빠지므로 실제 서버 동작은 재현되지 않는다.
6. **작게 고친다:** 한 번에 한 문제, 커밋도 하나씩. 브랜치 `feat/<topic>`, PR은 `develop`으로 (`AGENTS.md` "Git").
7. **검사 실행:** 아래 표. 저장소 규칙상 빌드는 한 번에 하나, `CARGO_BUILD_JOBS=2`로.
8. **검증:** 원래 문제가 풀렸는지, 3단계에서 찾은 사용처 화면, 그리고 "2. 기본 점검 목록".

| 무엇을 고쳤나 | 돌릴 명령 |
|---|---|
| Rust 크레이트 `ember/<crate>` | `cd ember/<crate> && cargo test --locked` (빠르게는 `cargo check --locked`) |
| 특정 기능(SPEC ID) | `cd ember/<crate> && cargo test --locked <id 접두사, 예: fr_l31>`. 어떤 파일인지는 [modules/tests-2.md](modules/tests-2.md) 역색인 |
| `ember/node` 또는 `ember/server`를 고쳤다 | 의존하는 크레이트(`server`는 `node`에, `client`는 `server`에 경로 의존)도 빌드해 `Cargo.lock`을 같은 PR에 커밋 (`AGENTS.md`) |
| proxy | `cd ember/proxy && python3 -m unittest` |
| VS Code 확장 | `cd extensions/vscode-darkpyonix && npm ci && npm run typecheck && npm test` |
| IntelliJ 플러그인 | `cd extensions/intellij-darkpyonix && ./gradlew --no-daemon test` |
| 문서·문구 | `bash .github/scripts/checks/check-no-em-dash.sh` (U+2014 금지) |
| 앱 UI | `bash .github/scripts/checks/check-no-webview.sh` (런처·대화 UI 웹뷰 금지) |

## 2. 기본 점검 목록 (수정 후 매번)

[03_FLOWS.md](03_FLOWS.md)의 핵심 흐름과 같다.

- [ ] 앱이 켜지고 첫 화면에 캐시된 프로젝트·세션이 보인다. 서버에 붙으면 목록이 갱신된다 (흐름 1).
- [ ] 세션에서 메시지를 보내면 에이전트 응답이 흘러 들어오고 턴이 끝나면 상태가 바뀐다. 바쁠 때 보낸 글은 "N개 대기 중"으로 쌓였다가 순서대로 나간다 (흐름 2).
- [ ] 도구 승인 카드의 "한 번 허용"/"거부"가 동작하고, 정지 버튼으로 턴을 멈출 수 있다 (흐름 3).
- [ ] 다른 컴퓨터가 등록돼 있다면 그 컴퓨터에서 도구가 돈다 (흐름 4).
- [ ] 세션 화면의 "IDE 열기"가 브라우저에서 VS Code Web을 연다 (흐름 6).
- [ ] 창 폭을 560dp 이하, 561~1279dp, 1280dp 이상으로 바꿔 하단 탭, 레일, 사이드바가 모두 그려진다 ([01_FEATURE_MAP.md](01_FEATURE_MAP.md) "창 크기").
- [ ] 라이트·다크 테마 둘 다에서 바뀐 화면을 본다.
- [ ] 서버를 재시작해도 진행 중이던 세션이 이어진다 (shim, FR-S8). 서버를 고쳤을 때만.

화면과 실제 하드웨어·네트워크가 필요한 확인은 사람이 직접 한다 (`AGENTS.md` "Verification").

## 3. 기능별 수정 포인트

### 셸과 내비게이션

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 메뉴 추가, 이름, 순서 | `ember/app/src/ui/shell.rs:17` `NavMenu`, `:30-39` `ALL`, `label` | `screen_for`(`ui/shell.rs:114`), `BOTTOM_TABS`(`:142`), `MORE_MENUS`(`:151`), `cr/shell.rs:638-672` 사슬, `choose`(`cr/shell.rs:69-89`), 아이콘 `ember/app/assets/nav/*.svg` | `ui/shell.rs`의 테스트가 라벨 순서를 고정한다 |
| 하단 탭·레일·사이드바 전환 폭 | `BAR_MAX_DP`(`ui/shell.rs:201`), `RAIL_MAX_DP`(`:199`) | 화면별 폭 분기(`cr/home.rs:156`, `cr/channels.rs:236`, `cr/components.rs:760-770`) | 셸과 화면 안 분기 기준이 따로 있다 |
| 사이드바·레일 너비 | `SIDE_W`, `RAIL_W` (`cr/theme.rs:299-300`) | `ember/app/src/ui/theme.rs`의 같은 토큰 | 토큰이 두 곳에 있다 |
| 사용자 이름 표시 | `cr/shell.rs:285`, `cr/home.rs:1073-1074` | `ember/app/src/ui/shell.rs`의 `DEMO_USER` | 지금은 데모 사용자 "BREW"가 실제 모드에도 보인다 ([05_ISSUES.md](05_ISSUES.md)) |

### 테마·문구

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 색, 간격, 반경, 글꼴 크기 | `cr/theme.rs` | `ember/app/src/ui/theme.rs` | `cr::theme::{LIGHT, DARK}`가 툴킷 팔레트의 원천이다(`ember/app/src/ui/fonts.rs:55`). 한쪽만 바꾸면 기본 위젯과 화면 색이 어긋난다 |
| 화면 문구 | 대개 `cr/<화면>.rs` 안의 문자열, 또는 `ember/app/src/ui/home.rs`, `enrol_flow.rs`, `channels.rs`의 상수 | `cr/ko.rs`는 상태, 포크, 연결 배너 문구만 갖는다 | 원본 상수를 바꾸면 Dioxus 쪽 테스트가 깨질 수 있다 |
| 버튼 접근성 라벨 | `cr/a11y.rs` | 같은 문구를 쓰는 `FocusOverlay` 라벨 | 아이콘 버튼 대부분에 이름이 없다 ([05_ISSUES.md](05_ISSUES.md)) |
| VS Code 테마 색 | `extensions/vscode-darkpyonix-theme/themes/*.json` | `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/editor/CellDecorator.kt:31-37` | 팔레트가 두 번 정의돼 있다 |

### 프로젝트·세션·대화

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 입력창 힌트, 대기열 문구 | `cr/conversation.rs:765-769`, `:928-938` | 없음 | 단순 문구 |
| 보내기 대기열 규칙 (바쁠 때 쌓기) | `ember/app/src/model.rs:454` `Outbox`, `ember/app/src/services.rs:99` `drive_outbox` | 대기열을 바꾸는 곳은 `bump_outbox`와 `drive_outbox`를 함께 부른다 (`cr/conversation.rs:334-335`) | 보내기·중단 로직이 세 곳에 중복돼 있다 ([05_ISSUES.md](05_ISSUES.md)) |
| 세션 상태 추가 (예: 새 대기 상태) | `ember/server/src/events.rs:244` `SessionStatus`, 전이 `events.rs:256-273` | DB 문자열 변환 `ember/server/src/store.rs:195-213`, 클라이언트 `ember/client/src/wire.rs`, 앱의 상태별 표시(`cr/ko.rs` 상태 문구, 세션 행) | 모르는 문자열은 `idle`로 읽힌다(`store.rs:211`). 구버전 앱과 맞추려면 `#[serde(default)]` |
| 승인 버튼 동작 | `cr/conversation.rs:1654-1675` `answer` | `ember/server/src/session.rs:845`, 어댑터별 승인 처리 ([modules/server-agents.md](modules/server-agents.md)) | Antigravity는 HTTP 훅으로 받는다 |
| 대화 화면 메뉴(고정, 내보내기, 포크, 컴퓨터) | `cr/conversation.rs:567-692`, `:1073-1199` | 세션 화면 `cr/session.rs:2467`의 `embedded` | 지금은 닿을 수 없는 코드다. 살리려면 세션 화면 쪽에 진입점을 만든다 |
| 새 팀원 시트 | `cr/session.rs:3952-4034` | 서버 A2A 팀 API ([modules/server-collab.md](modules/server-collab.md)) | 에이전트와 컴퓨터 목록이 고정값이다 (`:3975`) |
| "IDE 열기" 대상 | `ember/server/src/api/ide.rs:771` | `EMBER_IDE_COMPUTERS`, `EMBER_IDE_URL`, `EMBER_PUBLIC_URL`; 앱 `ember/app/src/server.rs:452` | 노드가 IDE 주소를 보고하면 그것이 우선한다 |

### 채널

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 메시지 최대 길이 (8192바이트) | `ember/server/src/channels/guest.rs:82` | `ember/server/src/a2a/mcp.rs:35`, `ember/server/src/guest_door/join.js:10` | 세 곳에 같은 값이 있다 |
| 채널 id 최대 길이 (128) | `ember/server/src/channels/jsonl.rs:148` | `ember/server/src/a2a/mcp.rs:37` | |
| 게스트가 쓸 수 있는 라우트 | `ember/server/src/channels/guest.rs:259-264` | guest door 가드 `ember/server/src/door/` | 보안 경계. owner API를 guest 라우터에 섞지 않는다 (`ember/server/src/main.rs:427-439`) |

### 루틴 (일정)

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 실행 알림 문구, 표시 개수 | `cr/routines.rs:59-62` | `ember/app/src/ui/routines.rs`의 같은 상수 (`RUN_NOTICE`, `NO_CWD_NOTICE`, `RUNS_SHOWN`) | 두 곳에 정의돼 있다 |
| 일정 계산 (cron, 시간대) | `ember/server/src/schedules/timing.rs` | `schedules/mod.rs` 스케줄러, 테이블 `schedules`, `schedule_runs` | 서버가 꺼져 있던 동안 놓친 실행은 첫 tick에서 보고한다 (`ember/server/src/main.rs:399`) |
| 루틴을 특정 컴퓨터에서 실행 | `ember/server/src/main.rs:401-416` (`set_computer_placer`) | `Computers::switch` (`ember/server/src/computers/mod.rs:1081`) | |

### 버전 관리 (git)

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 화면 배치 | `cr/vcs.rs` (그리기만) | 없음 | 호출과 계산은 `ember/app/src/ui/vcs.rs`에 있다 |
| 위험 동작 확인 시간 | `AMEND_CONFIRM_DELAY_MS`(`ember/app/src/ui/vcs.rs:1203`), `STASH_ARM_TIMEOUT_MS`(`:2781`) | 접근성 라벨 | |
| git 동작 추가 | 노드 `ember/node/src/git*.rs` ([modules/node-git.md](modules/node-git.md)) | 라우터 `ember/node/src/api.rs:154-234`의 `authed` 안, 머리 주석 표, `ember/node/src/client.rs`, `ember/node/src/proto.rs`, `ember/client/src/api.rs`의 DTO, 앱 `ui/vcs.rs` | `authed` 밖에 넣으면 인증이 없다 (`api.rs:227`) |
| `gh` 호출 환경 | `ember/node/src/git_prs.rs:286` | `ember/node/src/git_github.rs:98` | 실행기와 한국어 오류 표가 두 벌이다 (`git_prs.rs:242`, `git_github.rs:72`) |

### 에이전트·계정

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 서버에 저장되는 기본값 | `cr/agents.rs`가 쓰는 `ember/app/src/ui/agents.rs` | `sync_from_server`, `LocalStore::to_server_defaults` 양쪽 | 지금 서버에 저장되는 것은 기본 하네스, 모델, 추론 강도, 권한 모드, 메모리 한도, 기본 계정뿐 |
| 모델 목록 | `cr/agents.rs:1249-1310` | `cr/home.rs:834-844` | 두 곳에 있다 |
| 에이전트 CLI 추가 | `ember/server/src/main.rs:123-136` | `AgentKind`의 `as_str`/`parse`/`BUILTIN_NAMES` (`ember/server/src/agents/mod.rs:53`, `:111`, `:122`), `history::import_file`의 `match` (`ember/server/src/history/mod.rs:106`) | `AgentKind` 문자열은 DB `sessions.agent`에 저장된다. 기존 문자열을 바꾸지 않는다 |
| 에이전트 CLI 실행 인자 | 어댑터 파일 ([modules/server-agents.md](modules/server-agents.md) "어댑터별 실행 방식") | 실제 CLI 버전으로 통합 테스트 | 저장소 규칙: 실제 CLI 동작으로 검증 (`AGENTS.md` 규칙 4) |

### 컴퓨터·노드

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 노드 HTTP 라우트 추가 | `ember/node/src/api.rs` `router` | 머리 주석 표, `client.rs`, `proto.rs`, `ember/client/src/api.rs` | `authed` 라우터 안에 |
| 터미널 프로토콜 | `ember/node/src/proto.rs` `TermInput`/`TermEvent`/`TermHello` | `ember-term`, `api.rs`의 attach 루프, `ember/server/src/computers/terms.rs`, 앱 `terminal_stream.rs` | |
| 등록 코드 TTL, 형식 | `Enrol::mint` (`ember/server/src/computers/enrol.rs:911`) | 노드 `ember/node/src/enrol_cli.rs`, `ember/server/tests/fr_c2_enrol_node.rs` | 보안 경계 ([modules/server-enrol.md](modules/server-enrol.md)) |
| `"local"` 컴퓨터 id | `ember/server/src/computers/mod.rs:71` | `ember/server/src/ose.rs:119`, `cr/new_session.rs:31` | 세 곳에 따로 정의 |

### 서버 공통

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| 서버 응답 필드 | 서버의 해당 api 파일 | `ember/client/src/wire.rs`, `channels.rs`, `api.rs`의 손 복사본 DTO; 앱 `ember/app/src/server.rs` 타입 | 새 필드는 클라이언트에서 `#[serde(default)]`로 받아야 구버전과 맞는다 |
| 인증 면제 경로 | `ember/server/src/auth.rs` (예: `:121-127`, `:202`, `:206`) | 경로 모양을 바꾼 라우트 | ChatGPT 콜백 경로 `CALLBACK_PATH`와 면제가 묶여 있다 |
| Origin/Host 규칙 | `ember/server/src/api/origin.rs` | WebSocket 핸들러들 (`api/mod.rs:681`, `api/ide.rs:602`, `browser/api.rs:195`, `:264`), `computers/terms.rs:153`, `auth.rs:260-263`, door 설정 | 모든 리스너에 영향 |
| 앱 전역 서비스 필드 | `ember/app/src/services.rs` `Services` | `ember/app/src/lib.rs:105` `install`, `services.rs:307` `test_services` | 서버 호출 helper는 `self.demo` 분기를 같이 둔다 |

### 에디터·IDE·proxy·확장

| 바꾸고 싶은 것 | 고칠 위치 | 함께 고쳐야 하는 곳 | 주의 |
|---|---|---|---|
| Code-OSS 버전 | `ember/ose/VERSION` | `ember/editor-conn/src/rpc_ids.rs` 재생성 | CI "Editor-conn pin matches OSE"가 비교한다 ([modules/editor-conn.md](modules/editor-conn.md)) |
| 에디터 세션 입력·업데이트 타입 | `ember/editor/src/engine.rs` | `ember/editor/src/bridge.rs:161`, 앱 `editor_host.rs`, `ui/editor_workbench.rs` | |
| 장식 레코드 형식 (44바이트) | `ember/editor/src/widget.rs:31`, `:164` | compose-rust FR-38 `DECORATION_LEN` | 외부 저장소와 맞춰야 한다 |
| proxy의 websockets 버전 | `ember/proxy/requirements.txt` (12.0 고정) | `ember/proxy/dpx/vscode/proxy.py:116`, `ember/proxy/dpx/terms/api.py:173`의 `extra_headers` | 올리면 둘 다 `additional_headers`로 |
| VS Code Web 업스트림 포트 | `XMO_UPSTREAM_PORT` (`ember/proxy/dpx/config.py:16`) | serve-web 실행 포트 | 기본 9092 |
| IDE 창 분리 메시지 | `ember/bridge/src/messages.rs` | `ember/proxy/static/detach.js`, `ember/vectors/bridge/detach_vectors.json`, `ember/proxy/tests/js/detach.test.js` | |
| 노트북 포맷 규칙 | `extensions/vscode-darkpyonix/src/format/parser.ts` | `extensions/intellij-darkpyonix/.../format/NotebookFormat.kt`, 커널 `_parser.py`(darkpyonix-core), 두 쪽 테스트 | 세 곳이 어긋나면 stale 판정이 틀린다 |
| 대화 기록 가져오기 형식 | `ember/vectors/transcripts/` | Rust `ember/server/src/history/`, Python `ember/proxy/dpx/agents/` | `.github/scripts/checks/test-transcript-vectors.sh` |

## 4. 건드리면 위험한 곳

| 위치 | 이유 | 수정이 필요할 때 |
|---|---|---|
| `ember/server/src/auth.rs`, `ember/server/src/main.rs:483-518` | owner 리스너의 토큰과 Origin/Host 검사. 로컬 전용 라우트(기기, hub 관리, Antigravity 훅, enrol 발급)가 `local_app`에만 붙는다 | 라우트를 공용 `app`에 넣으면 transport로도 열린다. 어느 라우터에 붙는지 먼저 정한다 |
| `ember/server/src/guest_door.rs`, `enrol_door.rs`, `door/` | 별도 리스너의 보안 경계. guest·enrol 라우터는 `app`에 절대 합치지 않는다 (`main.rs:427-442`) | 가드(본문 크기, 속도 제한)를 함께 본다 ([modules/server-enrol.md](modules/server-enrol.md)) |
| `ember/server/src/accounts/secrets.rs` | 자격 증명 암호화 키 | 키 형식을 바꾸면 기존 계정을 못 읽는다. Windows 권한 검사가 비어 있다 |
| `ember/server/src/store.rs` (팬인 41) | 모든 세션과 이벤트. 상태 전이는 `Store::append`에서만 일어난다 (`store.rs:344-371`) | 스키마 변경은 마이그레이션과 함께. 기존 DB 파일이 있는 설치를 생각한다 |
| `ember/server/src/session_shim.rs`, `agents/proc.rs` | 서버보다 오래 사는 에이전트 프로세스 (FR-S8) | 서버 재시작 시나리오로 시험한다 |
| `ember/node/src/api.rs:227` `authed` 라우터 | 노드 인증 | 새 라우트는 반드시 안쪽에 |
| `ember/node/src/policy.rs`, `egress.rs` | 노드 파일 접근 루트와 외부 접속 출구 | 기본 egress 정책은 모든 목적지를 허용한다 ([modules/node.md](modules/node.md)) |
| `ember/client/src/wire.rs` (팬인 28), `ember/node/src/proto.rs` (팬인 25) | 프로세스 사이 계약 | 양쪽을 함께 바꾸고 하위 호환을 지킨다 |
| `ember/app/src/ui/<파일>.rs` 전반 | 이름은 옛 Dioxus 화면이지만 살아 있는 `cr/` 화면이 로직을 가져다 쓴다 | [modules/app-ui.md](modules/app-ui.md)의 "바깥에서 쓰이는 항목"을 먼저 본다 |
| `ember/editor-conn/src/rpc_ids.rs` | Code-OSS 버전에 묶인 RPC id | 손으로 고치지 않는다. `ember/ose/VERSION`과 함께 재생성 |

## 5. 사용자 테스트 피드백 대응

`docs/analysis/_feedback.md`가 아직 없다. 피드백을 그 파일에 적으면 다음 갱신 때 이 절에 "피드백 | 원인 추정 위치 | 수정 방법 | 영향 범위 | 확신도" 표로 채운다.
