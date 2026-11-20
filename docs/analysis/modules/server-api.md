# 모듈: server-api

- 경로: `ember/server/src/api/`, `ember/server/src/ose.rs`, `ember/server/src/browser/`, `ember/server/src/mcp/`
- 규모: 파일 18개 / 약 6,103줄 (`docs/analysis/_raw/modules.md`의 `server-api` 목록)
- 레이어: API
- 한 줄 책임: 네이티브 앱이 쓰는 세션·프로젝트 HTTP 라우트와 push WebSocket, "Open IDE" 대상과 OSE(VS Code 서버) 프로세스·릴레이, 프로젝트별 원격 Chrome(CDP)과 그 egress, 에이전트 세션에 주입되는 중앙 MCP 서버 레지스트리를 제공한다.
- 의존하는 모듈: [server-core](server-core.md) (`session.rs`, `store.rs`, `projects/`, `fork.rs`, `auth.rs`), [server-computers](server-computers.md) (`computers/`), [server-agents](server-agents.md) (`agents::McpServer`, `StartRequest`, `AgentKind`), [server-accounts](server-accounts.md) (`accounts::secrets::SecretBox`, `usage.rs`), [node](node.md) (`ember_node::api::Node`, in-process 노드)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs`, `lib.rs`, `auth.rs`, `store.rs`), [server-computers](server-computers.md) (`computers/mod.rs`, `computers/terms.rs`, `computers/local_node.rs`), [server-enrol](server-enrol.md) (`door/config.rs`, `door/harden.rs`), [server-agents](server-agents.md) (`agents/codex.rs`), [editor](editor.md) (`ember/editor/src/fallback.rs:43`, 주석에서 `percent_encode`와 같은 규칙이라고만 언급)

라우터 조립은 `ember/server/src/main.rs:443-463`이다. 이 모듈의 라우터는 모두 owner 리스너의 `auth::protect` 아래에 merge된다 (`docs/analysis/_raw/routes.md:24`).

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `api::router(sessions)` | 함수(pub) | `ember/server/src/api/mod.rs:78` | 핵심 세션·프로젝트 라우트 23개 + push. `main.rs:443` |
| `api::git::router` | 함수(pub) | `ember/server/src/api/git.rs:65` | 프로젝트별 git 릴레이. `main.rs:450` |
| `api::harnesses::router` | 함수(pub) | `ember/server/src/api/harnesses.rs:30` | 하니스 감지. `main.rs:449` |
| `api::integrations::router` | 함수(pub) | `ember/server/src/api/integrations.rs:72` | GitHub 카드 집계. `main.rs:451` |
| `api::ide::IdeConfig::from_env` | 함수(pub) | `ember/server/src/api/ide.rs:110` | `EMBER_IDE_COMPUTERS`, `EMBER_IDE_URL`, `EMBER_PUBLIC_URL` 읽기. `main.rs:420` |
| `api::ide::router_with_computers_and_ose` | 함수(pub) | `ember/server/src/api/ide.rs:467` | IDE 대상·OSE 릴레이 라우트. `main.rs:452` |
| `api::ide::EmberOseConnection` | 구조체(pub) | `ember/server/src/api/ide.rs:166` | `ose.rs`가 만들어 돌려주는 연결 정보 (`ose.rs:19`) |
| `api::ide_extensions::router` | 함수(pub) | `ember/server/src/api/ide_extensions.rs:38` | OSE 확장 설치. `main.rs:453` |
| `api::origin::host_of` | 함수(pub) | `ember/server/src/api/origin.rs:14` | authority에서 host 추출. `auth.rs:260`, `door/config.rs:7`, `door/harden.rs:17`, `main.rs:514` |
| `api::origin::origin_allowed` / `check_origin` | 함수(pub) | `ember/server/src/api/origin.rs:32`, `:49` | WebSocket Origin 검사. `auth.rs:263`, `computers/terms.rs:153`, `browser/api.rs:195` |
| `ose::OseManager` | 구조체(pub) | `ember/server/src/ose.rs:143` | 로컬 OSE 프로세스 관리. `main.rs:421` |
| `ose::data_root_from` | 함수(pub) | `ember/server/src/ose.rs:218` | OSE 데이터 루트 계산. `computers/local_node.rs:41` |
| `browser::BrowserManager` | 구조체(pub) | `ember/server/src/browser/mod.rs:65` | 프로젝트별 Chrome 관리. `main.rs:320` |
| `browser::BrowserConfig::from_env` | 함수(pub) | `ember/server/src/browser/mod.rs:53` | `EMBER_CHROME_BIN`, `EMBER_BROWSER_HEADFUL` |
| `browser::api::router` | 함수(pub) | `ember/server/src/browser/api.rs:36` | `/api/browsers/*`. `main.rs:461` |
| `browser::agent::from_env` / `start_config_hook` | 함수(pub) | `ember/server/src/browser/agent.rs:139`, `:256` | 에이전트에 브라우저 MCP 주입. `main.rs:329-336` |
| `browser::agent::MCP_NAME` | 상수(pub) | `ember/server/src/browser/agent.rs:39` | `"ember-browser"`. `mcp/mod.rs:42`의 예약 이름 |
| `browser::agent::toml_str` | 함수(pub(crate)) | `ember/server/src/browser/agent.rs:226` | TOML 문자열 이스케이프. `agents/codex.rs:375` |
| `browser::EgressResolver` / `EgressStore` | 트레이트(pub) | `ember/server/src/browser/egress.rs:49`, `:56` | `Computers`(`computers/mod.rs:1408`)와 `Store`(`egress.rs:75`)가 구현 |
| `browser::egress::MIGRATION` | 상수(pub) | `ember/server/src/browser/egress.rs:63` | `browser_egress` 테이블. `store.rs:138` |
| `browser::egress::projects_using_computer` | 함수(pub) | `ember/server/src/browser/egress.rs:115` | 컴퓨터 삭제 가드. `computers/mod.rs:328` |
| `mcp::McpRegistry` | 구조체(pub) | `ember/server/src/mcp/mod.rs:195` | MCP 레지스트리. `main.rs:340-341` |
| `mcp::api::router` | 함수(pub) | `ember/server/src/mcp/api.rs:27` | `/api/mcp`. `main.rs:456` |
| `mcp::schema::MIGRATION` | 상수(pub) | `ember/server/src/mcp/schema.rs:10` | `mcp_servers` 테이블. `store.rs:145` |

## 파일별 요약

### `ember/server/src/api/mod.rs` (약 712줄)
- **목적:** 클라이언트용 핵심 HTTP API와 push WebSocket. 상태는 `Arc<Sessions>` 하나다 (`api/mod.rs:78-105`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `router(sessions)` | 함수(pub) | 78 | 라우트 23개 등록 (`/api/health` 포함) |
  | `ApiError` | 구조체 | 107 | `{error}` JSON. `SessionError`(115), `anyhow::Error`(127), `ProjectError`(133), `QuestionError`(619) 변환 |
  | `coded` / `project_error` | 함수 | 504, 508 | 프로젝트 PATCH 전용 `{error, code}` 응답 |
  | `NOT_YET_PROJECT_FIELDS` | 상수 | 523 | `leader_session`, `archived`는 400 `not_yet` |
  | `EXPORT_VERSION` | 상수(pub) | 410 | 내보내기 파일 버전 1 |
  | `SEARCH_LIMIT`, `SEARCH_LIMIT_MAX` | 상수(pub) | 470, 471 | 50, 500 |
  | `LEASE_TTL` | 상수(pub) | 666 | 90초 |
  | `push_loop` | 함수 | 687 | broadcast를 WebSocket 텍스트로 전달, 지연 시 `{"type":"lagged"}` |
- **라우트와 호출하는 `Sessions`/`Store` 메서드** (Sessions는 `ember/server/src/session.rs`, server-core가 문서화):
  | 메서드 경로 | 핸들러 | 호출 대상 |
  |---|---|---|
  | GET `/api/health` | 클로저 `api/mod.rs:80` | 없음 (`{"ok":true}`) |
  | GET `/api/agents` | `agents` `:148` | `Sessions::probe_agents` `session.rs:468` |
  | GET `/api/agents/settings` | `get_agent_settings` `:154` | `Store::harness_settings_with_key` `store.rs:271` |
  | PUT `/api/agents/{agent}/settings` | `put_agent_settings` `:168` | `Sessions::set_mem_limit_persisted` `session.rs:323` |
  | GET `/api/agents/defaults` | `get_agent_defaults` `:199` | `Sessions::agent_defaults` `session.rs:348` |
  | PUT `/api/agents/defaults` | `put_agent_defaults` `:204` | `Sessions::set_agent_default_key` `session.rs:373`, `agent_defaults` |
  | GET `/api/sessions` | `list_sessions` `:306` | `Store::sessions` `store.rs:334` |
  | POST `/api/sessions` | `create_session` `:324` | `Sessions::create_with_account` `session.rs:495` |
  | GET `/api/sessions/{id}` | `get_session` `:343` | `Store::session` `store.rs:323`, `events_after` `store.rs:374`, `fork::completed_turns` `fork.rs:82`, `fork_origin` `fork.rs:201`, `Sessions::is_live` `session.rs:1110`, `approve_all` `session.rs:972`, `session_usage` `usage.rs:118` |
  | PATCH `/api/sessions/{id}` | `patch_session` `:398` | `Sessions::update_meta` `session.rs:449` |
  | GET `/api/sessions/{id}/export` | `export_session` `:415` | `Store::session`, `events_after` |
  | POST `/api/sessions/{id}/fork` | `fork_session` `:448` | `Sessions::fork` `session.rs:775` |
  | GET `/api/search` | `search` `:474` | `Store::search` `store.rs:419` |
  | GET `/api/usage/summary` | `usage_summary` `:381` | `day_start_ms` `usage.rs:103`, `usage_summary` `usage.rs:143` |
  | GET `/api/sessions/{id}/usage` | `session_usage` `:363` | `session_usage` `usage.rs:118` |
  | GET `/api/projects` | `list_projects` `:479` | `projects` `projects/mod.rs:287` |
  | POST `/api/projects` | `create_project` `:488` | `ensure_project` `projects/mod.rs:402`, `Sessions::publish` `session.rs:444` |
  | GET `/api/projects/{name}` | `get_project` `:499` | `project` `projects/mod.rs:302` |
  | PATCH `/api/projects/{name}` | `patch_project` `:527` | `patch_project` `projects/mod.rs:330`, `publish` |
  | PUT `/api/projects/{name}/computers/{computer_id}` | `assign` `:556` | `assign_computer` `projects/mod.rs:413`, `publish` |
  | DELETE 같은 경로 | `unassign` `:566` | `unassign_computer` `projects/mod.rs:436`, `publish` |
  | GET `/api/sessions/{id}/events` | `events` `:581` | `Store::session`, `events_after` |
  | POST `/api/sessions/{id}/messages` | `send_message` `:595` | `Sessions::send_from_user` `session.rs:836` |
  | POST `/api/sessions/{id}/approvals/{approval_id}` | `answer` `:610` | `Sessions::answer` `session.rs:845` |
  | POST `/api/sessions/{id}/questions/{question_id}/answer` | `answer_question` `:633` | `Sessions::resolve_question_body` `session.rs:877` |
  | PUT `/api/sessions/{id}/approve-all` | `set_approve_all` `:648` | `Sessions::set_approve_all` `session.rs:979` |
  | POST `/api/sessions/{id}/interrupt` | `interrupt` `:657` | `Sessions::interrupt` `session.rs:1026` |
  | POST `/api/sessions/{id}/lease` | `lease` `:668` | `Sessions::lease` `session.rs:737` |
  | GET `/api/push` (WS) | `push` `:676` | `origin::check_origin`, `Sessions::subscribe` `session.rs:439` |
- **입력 → 출력:** JSON 본문 → JSON. 오류는 대부분 `{error}`, 프로젝트 PATCH만 `{error, code}` (`:504-518`).
- **의존:** `session.rs`, `store.rs`, `projects/`, `fork.rs`, `usage.rs`, `agents::AgentKind`, `events::ApprovalDecision`.
- **사용처:** `ember/server/src/main.rs:443`, `lib.rs` (모듈 선언).
- **부수효과:** DB 쓰기(세션 메타, 프로젝트, 하니스 설정), push broadcast(`project_updated`), 에이전트 프로세스에 메시지·인터럽트 전달.
- **주의점:**
  - `push`는 업그레이드 전에 구독한다 (`:682-683`). 순서를 바꾸면 사이에 저장된 이벤트를 잃는다.
  - `put_agent_defaults`에서 `agent`만 지우고 `model`을 안 보내면 `model`도 지운다 (`:282-287`). 숨은 연쇄 동작이다.
  - `put_agent_settings`의 `0`은 범위 검사를 통과하고 저장 후 응답에서 `null`로 보인다 (`:189`, `:193`).
  - `answer_question`은 `auth.rs`에서 면제되지 않아 owner 토큰만 닿는다 (`:631-632` 주석).
  - 모듈 문서 표(`:12-29`)가 라우트 설명의 원본이다. 라우트를 바꾸면 함께 고친다.

### `ember/server/src/api/git.rs` (약 170줄)
- **목적:** `POST /api/projects/{name}/git/{*op}`를 프로젝트의 세션이 있는 컴퓨터의 노드 `/git/<op>`로 그대로 중계한다 (FR-G4).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `OPS` | 상수(pub) | 50 | 허용 op 목록 32개. 테스트 `ember/server/tests/git_relay.rs:118`이 참조 |
  | `router` | 함수(pub) | 65 | 상태 `GitState` |
  | `relay` | 함수 | 80 | op 검사 → 프로젝트 확인 → 세션 선택 → 컴퓨터 결정 → `repo` 추가 후 전달 |
  | `new_local` | 함수(pub(crate)) | 61 | in-process 노드 슬롯. `integrations.rs:39`가 사용 |
  | `local_call` | 함수(pub(crate)) | 150 | `$HOME` 루트의 in-process `ember_node` 라우터를 처음 쓸 때 만들고 `oneshot`으로 호출 |
- **입력 → 출력:** 본문 JSON 객체(없으면 `{}`) + `?session=` → 노드의 상태 코드와 본문 그대로. 원격 노드 실패는 502 (`:136`, `:140`).
- **의존:** `computers::{Computers, LOCAL}`, `ember_node::api::Node`, `ember_node::config::NodeConfig`.
- **사용처:** `main.rs:450`, `api/integrations.rs:39`.
- **부수효과:** 원격 노드 HTTP 호출, 로컬 git 실행(노드 경유).
- **주의점:**
  - 세션 선택은 "아카이브되지 않은 첫 세션, 없으면 첫 세션"이다 (`:107`). 모듈 주석(`:25`)은 "most recent unarchived"라고만 말하고, `integrations.rs:156`은 아카이브 세션으로 떨어지지 않는다. 두 곳의 규칙이 다르다.
  - 컴퓨터 결정: 세션 기록 → 프로젝트에 배정된 첫 원격 컴퓨터 → `LOCAL` (`:114-123`). `integrations.rs:157-160`에 같은 로직이 복사돼 있다.
  - in-process 노드 토큰은 상수 `"local"`이다 (`:151`). 루트는 `HOME` 환경 변수뿐이라 Windows에서 `HOME`이 없으면 루트가 비어 있다 (`:155`) [확인 필요: 이때 노드가 모든 경로를 거부하는지].
  - 응답 본문 상한 64 MiB (`:168`).

### `ember/server/src/api/ide.rs` (약 957줄)
- **목적:** `GET /api/sessions/{id}/ide`로 세션 폴더를 각 IDE(`ember`, `vscode`, `gateway`)로 여는 방법을 돌려주고, `GET /api/computers/{computer}/ide/relay/{launch_id}` WebSocket으로 Ember 에디터와 로컬 OSE 사이 바이트를 중계한다 (FR-L7, FR-W4).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ComputerIde` | 구조체(pub) | 62 | 컴퓨터 하나의 IDE 설정 (`ide_url`, `ssh_*`, `jetbrains_ide_path`, `os`) |
  | `IdeConfig` | 구조체(pub) | 94 | `default_computer`, `server_url`, `computers` |
  | `IdeConfig::from_env` | 함수(pub) | 110 | `EMBER_IDE_COMPUTERS`(인라인 JSON 또는 파일 경로) → 없으면 `local` 하나 + `EMBER_IDE_URL`. `server_url`이 없으면 `EMBER_PUBLIC_URL` |
  | `IdeConfig::parse` | 함수(pub) | 128 | `{`로 시작하면 JSON, 아니면 파일. `default_computer`가 목록에 없으면 오류 |
  | `EmberLaunch`, `EmberOseConnection` | 구조체(pub) | 149, 166 | 에디터용 실행 정보. `EmberOseConnection`의 `Debug`는 토큰을 `[REDACTED]`로 가린다 (`:173-181`) |
  | `Target`, `ComputerRef`, `IdeLaunch` | 구조체(pub) | 184, 207, 288 | 응답 DTO. `targets`는 항상 ember, vscode, gateway 순 |
  | `resolve_computers` | 함수(pub) | 238 | 레지스트리(로컬 + 노드)에 `EMBER_IDE_COMPUTERS` 항목을 id 또는 이름으로 덮어씌움. 맞지 않는 항목은 id=이름인 컴퓨터로 추가 |
  | `find_computer` | 함수(pub) | 283 | id 우선, 그다음 이름·별칭 |
  | `percent_encode` | 함수(pub) | 298 | RFC 3986 unreserved 외 인코딩 |
  | `vscode_web_url`, `gateway_url`, `open_command` | 함수(pub) | 314, 319, 342 | 링크와 OS별 여는 명령 (`open`, `xdg-open`, `cmd /c start`) |
  | `launch_targets_for` | 함수(pub) | 368 | 대상 3개 계산. 로컬 컴퓨터면 `OseManager::connection`을 호출해 OSE를 시작하거나 재사용 |
  | `router`, `router_with_ose`, `router_with_computers`, `router_with_computers_and_ose` | 함수(pub) | 448, 453, 458, 467 | 운영은 마지막 것만 쓴다 (`main.rs:452`). 나머지는 테스트용 (`tests/ide.rs:49`, `tests/fr_w4_ose_relay.rs:584`, `tests/fr_w4_ide_computers.rs:53-55`) |
  | `TokenSubstituter` | 구조체 | 501 | 클라이언트→OSE 스트림 앞 8 KiB에서 placeholder 토큰을 실제 토큰으로 교체. 프레임 경계에 걸친 부분 일치를 보류한다 |
  | `RELAY_SUBSTITUTION_WINDOW` | 상수(pub) | 54 | 8 KiB |
  | `ide_relay` | 함수 | 596 | Origin 검사, 컴퓨터 id 검사, `OseManager::open_relay`로 대상 확보 후 업그레이드 |
  | `pump_ose_relay` | 함수 | 633 | TCP 연결(3초 제한), 양방향 펌프, 텍스트 프레임은 1003으로 닫음, 유휴 감시 |
  | `ide_targets` | 함수 | 771 | 컴퓨터 결정: `?computer=` → 세션의 현재 컴퓨터(암묵 아님) → `default_computer` → `LOCAL` |
- **입력 → 출력:** 세션 id(+`?computer=`) → `IdeLaunch` JSON. 릴레이는 WebSocket 바이너리 ↔ TCP.
- **의존:** `ose.rs`(`valid_computer_id`, `OseManager`, `RelayTarget`), `computers::{Computers, LOCAL, LOCAL_NAME}`, `session.rs`, `store::SessionRecord`.
- **사용처:** `main.rs:420`, `main.rs:452`, `ose.rs:19`.
- **부수효과:** GET 요청인데 로컬 OSE 프로세스를 띄울 수 있다 (`launch_targets_for` `:379-380` → `ose.rs:668`). 경고 로그는 이름당 한 번 (`:790-797`).
- **주의점:**
  - 응답의 `ose.connection_token`은 실제 토큰이 아니라 placeholder다 (`ose.rs:707`). 실제 토큰은 릴레이에서만 바뀐다 (`:652`). 이 대칭을 깨면 에디터가 OSE에 접속하지 못하거나 실제 토큰이 노출된다.
  - `ide_targets`는 async 핸들러 안에서 블로킹 함수 `OseManager::connection_for`를 직접 부른다. 이 함수는 프로세스 맵 mutex를 잡은 채 최대 10초 `std::thread::sleep` 루프를 돈다 (`ose.rs:671`, `ose.rs:719-729`). 그동안 tokio 워커 하나와 `open_relay`(`ose.rs:536`)가 막힌다.
  - `server_url`이 설정되지 않으면 요청 `Host` 헤더로 `http://<Host>`를 만든다 (`:822-827`). https 뒤의 배포에서는 `EMBER_PUBLIC_URL`이 필요하다.
  - OSE는 로컬 컴퓨터만 지원한다. 원격 컴퓨터는 `ember` 대상이 `available: false` (`:381-383`).
- **테스트:** 9개 (`:836-947`). 연결 직렬화와 토큰 가림, OSE 시작·재사용, 퍼센트 인코딩, Gateway URL 형식, OS별 명령, 설정 파싱을 검증한다.

### `ember/server/src/api/integrations.rs` (약 304줄)
- **목적:** Home 연동 영역의 GitHub 카드 데이터 `GET /api/integrations/github` (FR-G13, FR-L35). 프로젝트마다 저장소를 찾아 노드의 `POST /git/github`를 부르고 집계한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CACHE_SECS`, `FAIL_CACHE_SECS`, `DEADLINE_MS` | 상수(pub) | 44, 46, 48 | 90초, 10초, 20,000 ms |
  | `CONCURRENCY` | 상수 | 50 | 동시 4개 |
  | `TIMED_OUT`, `NOT_INSTALLED`, `SIGNED_OUT`, `NO_REPO` | 상수 | 51, 54-56 | 한국어 사용자 문구 |
  | `router` | 함수(pub) | 72 | `EMBER_GITHUB_CACHE_SECS`, `EMBER_GITHUB_DEADLINE_MS`를 시작 시 한 번 읽음 |
  | `router_with_ttl`, `router_with_limits` | 함수(pub) | 80, 85 | 테스트용 (`tests/fr_g13_github_integration.rs:84`, `:256`) |
  | `github` | 함수 | 112 | 캐시 → refresh 락 → 재확인 → `refresh` |
  | `refresh` | 함수 | 151 | (컴퓨터, cwd) 단위로 묶고 4개씩 호출, 마감 시간 후 남은 것은 `TIMED_OUT` |
  | `call_node` | 함수 | 262 | 200 → 요약, 409 + "gh"와 "설치" 포함 → 미설치, 그 외 실패 문자열(200자) |
  | `clean` | 함수 | 99 | 제어 문자 제거, 100자 자름 |
- **입력 → 출력:** 없음 → `{state, reason, account, repos, totals, checked_at}`.
- **의존:** `api::git::{local_call, new_local}`, `computers`, `session.rs`.
- **사용처:** `main.rs:451`.
- **부수효과:** 노드 HTTP 호출(노드가 `gh` 실행), 메모리 캐시.
- **주의점:**
  - 미설치 판정이 노드 오류 문구의 한국어 부분 문자열에 묶여 있다 (`:280`). 노드 쪽 문구를 바꾸면 `off` 대신 실패로 보인다.
  - `git.rs`와 별도의 in-process 노드 슬롯을 만든다 (`:89`). 로컬 노드가 두 개 생긴다.
- **테스트:** 1개 (`:299`), 원격 노드 이름 정리.

### `ember/server/src/api/ide.rs` 외 작은 파일은 맨 끝 표에 있다.

### `ember/server/src/ose.rs` (약 769줄)
- **목적:** Ember 에디터가 붙는 로컬 OSE 서버(VS Code 서버 빌드 `dpx-ose-server`) 프로세스를 (컴퓨터, 폴더)마다 하나씩 띄우고, 연결 토큰 파일, 릴레이 동시성 한도, 확장 설치를 관리한다 (FR-W4, #458, #459, #461, #521).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Process` | 구조체 | 21 | 자식 프로세스, `launch_id`, 주소, 실제 토큰, placeholder, 연결, 활성 릴레이 수, 토큰 파일 |
  | `RelayTarget`, `RelayPermit` | 구조체 | 34, 43 | 릴레이 하나의 대상과 RAII 카운터 |
  | `RelayLookupError` | enum(pub) | 57 | `NotFound`(404), `TooManyRelays`(429) |
  | `write_token_file` | 함수 | 76 | `<tokens>/<폴더 SHA-256 앞 16 hex>.token`, unix에서 0600 `create_new`, 줄바꿈 없음 |
  | `LOCAL_COMPUTER` | 상수(pub) | 119 | `"local"` (`computers::LOCAL`과 같은 값을 따로 정의) |
  | `INSTALL_TIMEOUT`, `OUTPUT_CAP` | 상수(pub) | 121, 123 | 120초, 16 KiB |
  | `RELAY_IDLE_TIMEOUT`, `MAX_RELAYS_PER_LAUNCH`, `MAX_RELAYS_PER_SERVER` | 상수(pub) | 125, 127, 129 | 120초, 16, 64 |
  | `FLAG_LIST_UNVERIFIED` | 상수 | 140 | `#[allow(dead_code)]`, 쓰지 않는 플래그 이름 |
  | `OseManager` | 구조체(pub) | 143 | `binary`, `data_root`, 한도, `installing`, `processes` |
  | `InstallError` | enum(pub) | 158 | `Bad`(400), `NotInstalled`(503), `Busy`(409), `Failed`(502), `Io`(500) |
  | `valid_computer_id` | 함수(pub) | 173 | `[A-Za-z0-9._-]`, 64바이트 이하, `..` 금지 |
  | `extension_spec` | 함수(pub) | 192 | `publisher.name[@x.y.z[-suffix]]` 엄격 검사 |
  | `data_root_from` | 함수(pub) | 218 | `EMBER_OSE_DATA_DIR` → `<EMBER_DATA_DIR 또는 HOME/.ember>/ose-data` |
  | `make_private_dir`, `secure_token_dir` | 함수 | 253, 305 | unix에서 0700, 심볼릭 링크·타 사용자 소유 거부. 비 unix는 `create_dir_all`만 |
  | `ENV_ALLOWLIST`, `ose_command` | 상수, 함수 | 356, 359 | 자식 환경 변수를 `HOME, PATH, LANG, LC_ALL, TMPDIR, USER`로 제한 |
  | `kill_tree` | 함수 | 372 | unix에서 프로세스 그룹 SIGKILL |
  | `OseManager::with_root` | 함수 | 451 | 1초마다 죽은 프로세스를 맵에서 지우는 OS 스레드를 띄움 (`:454-462`) |
  | `register_launch_for_test` | 함수(pub) | 497 | 테스트 전용 (`tests/fr_w4_ose_relay.rs:128` 등) |
  | `open_relay` | 함수(pub) | 535 | (컴퓨터, launch_id)로 살아 있는 프로세스를 찾고 한도 확인 후 permit 발급 |
  | `computer_data_dir` | 함수(pub) | 579 | `<root>/<id>` 0700 |
  | `install_extension` | 함수(pub) | 603 | 블로킹. 셸 없이 `--install-extension`, 컴퓨터당 하나, 시간 초과 시 그룹 kill |
  | `connection_for` | 함수(pub) | 668 | 있으면 재사용, 없으면 포트 할당 → 토큰·placeholder 생성 → 토큰 파일 → 실행 → 10초 안에 TCP 열림 대기 |
  | `server_binary` | 함수 | 735 | `EMBER_OSE_SERVER` → `$HOME/.local/share/dpx-ose-*/bin/dpx-ose-server` 중 정렬 마지막 |
- **입력 → 출력:** 폴더 경로 → `EmberOseConnection {endpoint, relay, connection_token(placeholder)}`.
- **의존:** `api::ide::EmberOseConnection`, `sha2`, `uuid`, `libc`(unix).
- **사용처:** `main.rs:421`, `api/ide.rs:48`, `api/ide_extensions.rs:30`, `computers/local_node.rs:41`.
- **부수효과:** 외부 프로세스 실행, 토큰 파일 쓰기·삭제(`TokenFile` drop `:67-71`), 디렉터리 생성·권한 변경, 로컬 TCP 포트 사용.
- **주의점:**
  - 포트는 `127.0.0.1:0`에 bind 후 바로 놓고 자식이 다시 bind한다 (`:685-687`). 그 사이 다른 프로세스가 포트를 잡을 수 있다.
  - 비 unix(Windows)에서는 토큰 디렉터리 권한 강화가 없고 토큰 파일 모드도 설정되지 않는다 (`:98-102`, `:289-292`, `:346-349`).
  - `HOME`만 보므로 Windows에서 `HOME`이 없으면 바이너리 탐색(`:739`)과 데이터 루트(`:242`)가 실패한다. `EMBER_OSE_SERVER`, `EMBER_OSE_DATA_DIR`이 필요하다.
  - 서버 종료나 패닉이 진행 중인 설치를 죽이지 않는다 (`:602` TODO).
  - 여러 OSE가 한 데이터 디렉터리를 공유할 때 안전한지 모른다고 모듈 주석이 밝힌다 (`:7-8`).
- **테스트:** 파일 안 1개 이상 (`:755`부터), 설치 busy 가드가 패닉에서도 풀리는지 검증한다 [확인 필요: 파일 끝까지 테스트 개수].

### `ember/server/src/browser/mod.rs` (약 290줄)
- **목적:** 프로젝트마다 headless Chromium 하나를 관리하는 `BrowserManager`와 설정 (SPEC §R, INTENT D6). 프로필은 `<data dir>/browser/<project>/profile`.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `BrowserConfig` / `from_env` | 구조체, 함수(pub) | 37, 53 | 루트, Chrome 경로, headless, 창 1280x800, 스크린캐스트 |
  | `BrowserManager` | 구조체(pub) | 65 | `browsers` 맵(tokio Mutex), egress 저장소, 리졸버 |
  | `check_project` | 함수(pub) | 75 | ASCII 영숫자, `-_.`, 128자 이하, `.`/`..` 금지 |
  | `instance` | 함수(pub) | 107 | 없으면 저장된 egress로 만들기만 한다 (시작 안 함) |
  | `set_egress` | 함수(pub) | 133 | 검증 → 저장 → 실행 중이거나 `start`면 재시작 |
  | `open`, `open_with` | 함수(pub) | 159, 168 | 시작 또는 egress 전환 |
  | `list`, `clear_data`, `shutdown` | 함수(pub) | 183, 195, 201 | 목록, 프로필 삭제(FR-R4), 전체 정상 종료 |
- **의존:** `browser/instance.rs`, `browser/egress.rs`, `browser/chrome.rs`.
- **사용처:** `main.rs:13`, `main.rs:320`, `computers/mod.rs:1408`(리졸버 구현).
- **부수효과:** 디렉터리 생성, Chrome 프로세스.
- **주의점:**
  - `check_project`는 ASCII만 허용한다 (`:80`). 한글 등 비 ASCII 이름 프로젝트는 브라우저와 에이전트 브라우저 MCP를 얻지 못한다 (`agent.rs:258`).
  - 맵에서 인스턴스를 지우는 코드가 없다. 한 번 만든 인스턴스는 서버가 끝날 때까지 남고 각각 250 ms 틱 태스크를 가진다 (`instance.rs:227-235`).
  - 프로필 경로는 인스턴스 생성 때 프로젝트 이름으로 정해진다 (`:120`). 프로젝트 이름을 바꾸면 `browser_egress` 행은 옮겨지지만 (`projects/mod.rs:124-125`, `:388-390`) 프로필 디렉터리는 옮겨지지 않는다.
- **테스트:** 3개 (`:239`, `:274`, `:284`). egress가 재시작 후 유지되는지, 해석 불가 컴퓨터가 오류인지, 프로젝트 이름 규칙.

### `ember/server/src/browser/api.rs` (약 373줄)
- **목적:** `/api/browsers/*` HTTP·WebSocket 라우트 (프로토콜 `docs/design/REMOTE-BROWSER.md`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `router` | 함수(pub) | 36 | 라우트 14개 |
  | `requested` | 함수 | 102 | `egress`와 `computer` 동시 지정은 400, `computer:"local"`은 Direct |
  | `some_option` | 함수 | 115 | 필드 없음과 `null` 구분 |
  | `view` / `view_loop` | 함수 | 189, 206 | Origin 검사 후 JPEG 프레임 송신, 텍스트 입력 수신, 연결 시 백그라운드로 시작 |
  | `cdp` / `cdp_agent` / `relay` | 함수 | 258, 270, 279 | 에이전트용 DevTools 릴레이. 명령마다 `agent_command`로 takeover 대기 |
  | `cdp_version`, `cdp_version_agent` | 함수 | 335, 346 | `/json/version` 발견 문서 |
  | `agent_config` | 함수 | 359 | Claude Code·Codex용 MCP 설정 JSON |
  | `base_url` | 함수 | 327 | `Host` 헤더 없으면 `127.0.0.1:8740`, 항상 `http://` |
- **의존:** `browser/agent.rs`, `browser/instance.rs`, `api::origin`.
- **사용처:** `main.rs:461`.
- **부수효과:** Chrome 시작·정지, 프로필 삭제, CDP 메시지 중계.
- **주의점:**
  - `{nonce}` 경로의 nonce는 여기서 검사하지 않는다. `auth.rs:121-127`(`agent_cdp_path_ok`)이 검사한다 (`:46`, `:344-345` 주석). 라우트 이름을 바꾸면 auth 쪽도 바꿔야 한다.
  - nonce는 서버 실행당 하나이고 프로젝트에 묶이지 않는다 (`auth.rs:107-112`). 한 프로젝트 에이전트가 다른 프로젝트 브라우저 URL로 접속할 수 있다.
  - `PUT .../egress`에 둘 다 주면 `requested(Some(None), Some(""))`로 일부러 400을 만든다 (`:152`). 읽기 어려운 우회다.

### `ember/server/src/browser/instance.rs` (약 795줄)
- **목적:** 프로젝트 브라우저 하나의 수명, egress 전환, 스크린캐스트, 입력, 에이전트 상태 (FR-R1~R4).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `AGENT_ACTIVE_WINDOW` | 상수(pub) | 22 | 3초 |
  | `ScreencastOptions` | 구조체(pub) | 26 | 품질 70, 1280x800, 매 프레임 |
  | `ViewState` | 구조체(pub) | 51 | 뷰어에 보내는 상태 (`running`, `egress`, `tabs`, `agent_active`, `takeover`, `viewers`, `error` 등) |
  | `BrowserInfo` | 구조체(pub) | 77 | 목록 항목. `debug_port`는 릴레이를 거치지 않는 직접 포트 |
  | `InputEvent` | enum(pub) | 89 | `mouse`, `wheel`, `key`, `text`, `navigate`, `reload`, `back`, `forward`, `takeover`, `select_tab`, `screencast` |
  | `BrowserInstance::new` | 함수(pub(super)) | 179 | 상태 채널 생성, `agent_active` 끄는 250 ms 틱 태스크 |
  | `resolve_egress` | 함수(pub) | 277 | 컴퓨터를 리졸버로 SOCKS5 URL로 바꾸고 `check_proxy` |
  | `ensure_running` | 함수(pub) | 302 | 죽었으면 정리 후 시작. 해석 실패 시 direct로 대체하지 않는다 (`:311-312`) |
  | `switch_egress` | 함수(pub) | 346 | 같으면 유지, 다르면 정지 후 새 프록시로 시작 |
  | `stop` / `stop_running` | 함수 | 361, 389 | `Browser.close`(5초) 후 대기(10초), 안 되면 kill |
  | `clear_data` | 함수(pub) | 375 | 정지, 프로필 삭제, 실행 중이었으면 재시작 |
  | `input` | 함수(pub) | 422 | 이벤트를 CDP `Input.*`, `Page.*`, `Runtime.evaluate`로 변환 |
  | `evaluate`, `wait_page` | 함수(pub) | 504, 520 | 테스트·진단용 |
  | `agent_command`, `agent_connected` | 함수(pub) | 540, 551 | takeover 중이면 대기, 활동 표시 |
  | `pack_frame` | 함수 | 561 | `[u32 BE 헤더 길이][JSON 헤더][JPEG]` |
  | `ViewerGuard` | 구조체(pub) | 594 | drop 시 뷰어 수 감소 |
  | `drive` / `drive_inner` | 함수 | 616, 631 | 탭 선택·attach, 뷰어가 있을 때만 스크린캐스트, 탭 생성·변경·삭제 추적 |
- **의존:** `browser/cdp.rs`, `browser/chrome.rs`, `browser/egress.rs`.
- **사용처:** `browser/mod.rs:33`, `browser/api.rs:34`.
- **부수효과:** Chrome 프로세스, 프로필 디렉터리 삭제, 네트워크(프록시).
- **주의점:**
  - `Navigate`의 URL을 검사하지 않는다 (`:486-487`). `file://` 등으로 서버 머신의 파일을 화면에 띄울 수 있다. 접근자는 owner 토큰 소유자뿐이다.
  - `drive_inner`의 attach 실패는 탭을 빼고 `continue`한다 (`:667-671`). 탭이 비면 새 탭을 만들고 다시 시도하므로, attach가 계속 실패하면 쉬지 않고 반복한다 [추정].
  - `input`의 마지막 `unreachable!()` (`:496-498`)은 앞의 조기 반환과 짝이다. 조기 반환을 바꾸면 패닉이 된다.

### `ember/server/src/mcp/mod.rs` (약 535줄)
- **목적:** 중앙 MCP 서버 레지스트리 (FR-A7). 사용자가 한 번 등록한 서버를 범위에 맞는 모든 에이전트 시작 요청의 `StartRequest::mcp_servers`에 넣는다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `AAD_PREFIX` | 상수 | 39 | `ember/mcp-env/v1:` + 행 id가 AEAD의 AAD |
  | `RESERVED_NAMES` | 상수(pub) | 42 | `ember-browser` |
  | `McpScope` | enum(pub) | 46 | `all` 또는 `project:<name>` |
  | `McpEntry` | 구조체(pub) | 82 | 클라이언트용. 환경 변수는 이름(`env_keys`)만 |
  | `NewMcp`, `McpPatch` | 구조체(pub) | 98, 122 | 요청 DTO. `Debug` 없음 (비밀 포함) |
  | `McpError` | enum(pub) | 138 | `NotFound`, `BadRequest`, `Conflict`, `Other` |
  | `validate_name`, `validate_env_key` | 함수(pub) | 156, 172 | 이름 1-64자 `[A-Za-z0-9_-]`, 예약 이름 금지. 오류 문구에 값을 넣지 않는다 |
  | `McpRegistry::open` | 함수(pub) | 221 | `<data dir>/secret.key`로 `SecretBox` 열기 (API 공급자 키와 같은 키) |
  | `install` | 함수(pub) | 231 | `Sessions::add_start_config_hook` |
  | `seal_env` / `env_of` | 함수 | 265, 282 | 환경 전체를 JSON 하나로 봉인·해제 |
  | `add`, `update`, `delete`, `list`, `get` | 함수(pub) | 302, 335, 387, 235, 242 | CRUD |
  | `servers_for` | 함수(pub) | 397 | 활성·범위 일치 서버. 해제 실패 서버는 경고 후 제외 |
  | `configure_start` | 함수(pub) | 427 | 이미 같은 이름이 있으면 건너뜀 (브라우저 MCP 우선) |
  | `start_config_hook` | 함수(pub) | 438 | 약한 참조. 레지스트리 오류는 경고만 하고 에이전트는 시작한다 |
- **의존:** `accounts::secrets::SecretBox`, `agents::{McpServer, StartRequest}`, `session.rs`, `store.rs`.
- **사용처:** `main.rs:19`, `main.rs:340-341`, `mcp/api.rs:25`.
- **부수효과:** DB 쓰기(`mcp_servers`), 비밀 키 파일 생성(없을 때, `secrets.rs` 경유).
- **주의점:**
  - 훅 순서가 의미를 가진다. 브라우저 훅 다음에 설치해야 `ember-browser` 이름이 유지된다 (`main.rs:339`).
  - `update`에서 환경 갱신과 나머지 필드 갱신이 트랜잭션 없이 두 문장으로 나뉜다 (`:373-383`).
  - 프로젝트 이름 변경 시 `scope = 'project:<old>'`를 고치지 않는다. 이름 변경 대상 테이블 목록에 `mcp_servers`가 없다 (`projects/mod.rs:124-125`). 이름을 바꾸면 그 서버는 조용히 적용되지 않는다.
- **테스트:** 3개 (`:476`, `:503`, `:517`). 환경 봉인과 병합, 검증·충돌, 범위와 브라우저 다음 순서.

### `ember/server/src/browser/agent.rs` (약 339줄)
- **목적:** 에이전트를 고치지 않고 브라우저를 쓰게 한다 (FR-R3, E2). `EMBER_BROWSER_MCP`가 켜져 있으면 모든 에이전트 시작에 `chrome-devtools-mcp` 또는 `@playwright/mcp`를 `npx`/`bunx`로 붙인다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MCP_STARTUP_TIMEOUT_SECS` | 상수(pub) | 36 | 90초 |
  | `MCP_NAME` | 상수(pub) | 39 | `ember-browser` |
  | `BrowserMcp` | enum(pub) | 44 | `ChromeDevtools`, `Playwright` |
  | `Runner` / `Runner::find` | enum, 함수(pub) | 80, 88 | `EMBER_BROWSER_MCP_RUNNER` → `npx` → `bunx` |
  | `from_env` | 함수(pub) | 139 | 기본 off |
  | `cdp_ws_url`, `agent_cdp_ws_url`, `cdp_version_doc` | 함수(pub) | 157, 170, 177 | 릴레이 URL, nonce 포함 URL, 발견 문서 |
  | `agent_config`, `agent_config_with` | 함수(pub) | 198, 202 | Claude `--mcp-config` JSON, Codex `-c` 오버라이드, TOML |
  | `mcp_server` | 함수(pub) | 241 | 어댑터용 `McpServer` |
  | `start_config_hook` | 함수(pub) | 256 | 환경 변수 `EMBER_BROWSER_CDP_WS`, `EMBER_BROWSER_MCP_CONFIG`와 MCP 서버 추가 |
  | `start_hook` | 함수(pub) | 276 | 이전 방식. 저장소에서 쓰는 곳이 없다 |
- **사용처:** `main.rs:329-336`, `browser/api.rs:33`, `agents/codex.rs:375`, `mcp/mod.rs:42`.
- **부수효과:** 없음 (설정 생성). 실제 실행은 에이전트가 한다.
- **주의점:** 패키지를 `@latest`로 받는다 (`:66-67`). 버전 고정이 없어 공급망 변경이 바로 들어온다. `base`는 `main.rs:333`에서 `http://127.0.0.1:<port>`로 고정된다.
- **테스트:** 3개 (`:294`, `:307`, `:321`). 설정 형식, runner별 명령, 훅이 서버와 환경을 넣는지.

### `ember/server/src/browser/chrome.rs` (약 202줄)
- **목적:** Chrome/Chromium 찾기와 실행.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `find_chrome` | 함수(pub) | 14 | `EMBER_CHROME_BIN` → macOS 앱 번들 → `PATH`의 이름들 → Playwright 캐시 최신 |
  | `LaunchOptions`, `Launched` | 구조체(pub) | 75, 86 | 실행 옵션과 결과 |
  | `check_proxy` | 함수(pub) | 93 | `socks5/socks4/http/https://host:port`, 자격 증명·경로 금지 |
  | `chrome_args` | 함수(pub) | 108 | `--remote-debugging-port=0`, `127.0.0.1`, `--password-store=basic`, 프록시 시 `--proxy-bypass-list=<-loopback>` |
  | `launch` | 함수(pub) | 139 | 프로필의 `DevToolsActivePort` 파일을 30초까지 폴링 |
- **주의점:**
  - Windows 경로를 찾지 않는다. `PATH`에서 확장자 없는 이름만 본다 (`:33-34`). Windows에서는 `EMBER_CHROME_BIN`이 사실상 필수다.
  - DevTools 포트는 인증 없이 127.0.0.1에 열린다 (`:111-112`). 같은 머신의 다른 프로세스는 릴레이(활동 표시, takeover)를 우회할 수 있다 (`instance.rs:80` 주석이 인정).
  - `--password-store=basic`은 OS 키체인 없이 프로필에 비밀을 둔다 (`:119-121`).
- **테스트:** 2개 (`:180`, `:190`). 프록시 검증, loopback도 프록시로 보내는지.

### `ember/server/src/browser/egress.rs` (약 168줄)
- **목적:** 프로젝트 브라우저 egress 선택과 그 영속화 (FR-R1). 컴퓨터 선택은 id로 저장하고 시작할 때마다 다시 해석한다 (루프백 SOCKS5 포트가 매번 바뀌므로, `:3-6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Egress` | enum(pub) | 18 | `Direct`(기본), `Proxy{url}`, `Computer{id}`. serde `kind` 태그 |
  | `EgressResolver` | 트레이트(pub) | 49 | `proxy_for_computer` |
  | `EgressStore` | 트레이트(pub) | 56 | `load`, `save`(Direct면 행 삭제) |
  | `MIGRATION` | 상수(pub) | 63 | migration 5, `browser_egress` 테이블 |
  | `impl EgressStore for Store` | impl | 75 | SQL 구현 |
  | `projects_using_computer` | 함수(pub) | 115 | 컴퓨터 삭제 막기용 |
  | `MemoryEgressStore` | 구조체(pub) | 126 | 테스트·임베딩용. 저장소 안에서 쓰는 곳은 없다 (grep 결과 `egress.rs` 안뿐) |
  | `SharedEgressStore`, `SharedEgressResolver` | 타입(pub) | 144, 145 | `Arc<dyn ...>` |
- **사용처:** `store.rs:138`, `computers/mod.rs:328`, `main.rs:199`.
- **테스트:** 1개 (`:152`), 저장 왕복과 serde.

## 작은 파일

| 파일 | 줄 | 요약 |
|---|---|---|
| `ember/server/src/api/harnesses.rs` | 74 | `POST /api/computers/{id}/harnesses/detect` (`:32`). 로컬만 `Sessions::probe_agents`(`session.rs:468`)로 감지하고, 등록된 원격은 501 `not_implemented`, 모르는 id는 404 (`:41-57`). **[provisional]** (`:10`) |
| `ember/server/src/api/ide_extensions.rs` | 90 | `POST /api/computers/{id}/ide/extensions` (`:40`). `deny_unknown_fields` 본문 `{id, version?}` (`:44-49`), 로컬 외 400, `spawn_blocking`으로 `OseManager::install_extension` (`:74`), `InstallError`를 400/503/409/502/500으로 매핑 (`:79-88`) |
| `ember/server/src/api/origin.rs` | 80 | Origin 없음 허용, `Origin` authority가 `Host`와 같으면 허용, host가 loopback(`localhost`, `*.localhost`, `::1`, 127/8)이면 허용, 나머지(`null` 포함) 403 (`:22-45`). 인증이 아니다 (`:9`). 테스트 1개 (`:71`) |
| `ember/server/src/browser/cdp.rs` | 150 | WebSocket 하나 위의 얇은 CDP 클라이언트. 요청 id → oneshot 맵, 이벤트 broadcast(512), 호출 시간 제한 30초 (`:41`), `send_nowait`는 응답을 기다리지 않음 (`:142`) |
| `ember/server/src/mcp/api.rs` | 71 | `/api/mcp` CRUD 5개 (`:29-30`). 오류 `{error, code}` (`:34-44`) |
| `ember/server/src/mcp/schema.rs` | 24 | migration 11 `mcp_servers` 테이블 (`:10-23`). `env_nonce`(24바이트)와 `env_ciphertext`만 비밀, `env_keys`는 평문 |

## 이 모듈을 수정할 때 주의할 점

- 라우트의 인증 면제는 이 모듈이 아니라 `auth.rs`에 있다. 특히 브라우저 nonce 경로 (`auth.rs:121-127`, `:206`)와 질문 답변 라우트(면제 안 됨, `api/mod.rs:631`). 경로 모양을 바꾸면 `auth.rs`를 함께 고친다.
- `api/origin.rs`는 WebSocket 3곳(`api/mod.rs:681`, `api/ide.rs:602`, `browser/api.rs:195`, `:264`)과 `computers/terms.rs:153`, `auth.rs:260-263`, 도어 설정이 함께 쓴다. 규칙 하나를 바꾸면 모든 리스너에 영향이 간다.
- `git.rs`와 `integrations.rs`에 "세션 → 컴퓨터" 선택 로직이 두 벌 있다 (`git.rs:100-123`, `integrations.rs:155-160`). 아카이브 세션 처리도 다르다.
- `"local"` 문자열이 `computers::LOCAL`(`computers/mod.rs:71`)과 `ose::LOCAL_COMPUTER`(`ose.rs:119`)에 두 번 정의돼 있다. 앱도 따로 정의한다 (`ember/app/src/ui/cr/new_session.rs:31`).
- OSE 토큰 흐름: `connection_for`가 실제 토큰은 파일로만 OSE에 주고 (`ose.rs:694-698`), 클라이언트에는 placeholder만 준다 (`ose.rs:707`). 릴레이가 앞 8 KiB에서 교체한다 (`api/ide.rs:652`). 토큰 길이가 같아야 교체가 켜진다 (`api/ide.rs:520-524`).
- 시작 설정 훅 순서: 브라우저 훅(`main.rs:332`) 다음 MCP 레지스트리 훅(`main.rs:341`). 레지스트리는 이미 있는 이름을 건너뛴다 (`mcp/mod.rs:429`).
- Windows 지원: `HOME` 의존 (`git.rs:155`, `ose.rs:242`, `ose.rs:739`, `chrome.rs:19`)과 unix 전용 권한 처리(`ose.rs:98-102`)가 있다. Windows 노드 서버 작업(#200, 최근 커밋 `71d356e`)과 겹치는 부분이다.
