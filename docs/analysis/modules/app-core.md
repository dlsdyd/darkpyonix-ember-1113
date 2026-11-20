# 모듈: app-core

- 경로: `ember/app/` 중 `src/ui/`와 `tests/`를 뺀 나머지 (`ember/app/src/*.rs` 14개, `Cargo.toml`, `Dioxus.toml`, `README.md`, `assets/`, `scripts/linux-gui/`)
- 규모: 파일 33개 / Rust 약 8,370줄 (나머지는 자산, 스크립트, 설정)
- 레이어: 인프라 + 비즈니스 로직 (UI 아래의 전부: 런타임, 서비스 싱글턴, 서버 API, 브리지, 뷰모델, 설정)
- 한 줄 책임: 창이 열리기 전에 tokio 런타임, `ember_client::Client`, 추가 서버 API, 메시지 outbox를 만들어 `Services` 전역으로 두고, 클라이언트 변경을 UI 신호로 바꾼다.
- 의존하는 모듈: [client](client.md) (`ember_client`), [editor-conn](editor-conn.md) (`ember-editor-conn`), `ember-editor` (문서 없음 [확인 필요]). 아래로는 `crate::ui::*`와 순환한다 (주의점 참조).
- 이 모듈을 쓰는 모듈: `app-ui` (`ember/app/src/ui/**`, `services()` 호출 426곳, 36개 파일), `ember/app/tests/*`.
- 시작 순서는 [entrypoints.md](../_raw/entrypoints.md)의 "ember-app 초기화 순서"에 있다. 되풀이하지 않는다.

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Services`, `services()`, `try_services()`, `install()` | struct, fn | `ember/app/src/services.rs:28`, `:55`, `:60`, `:48` | 전역 싱글턴과 접근자 |
| `run`, `run_shared`, `save_prefs` | fn | `services.rs:236`, `:253`, `:264` | 워커 결과를 UI로 되돌리는 도우미, 설정 저장 |
| `Live`, `use_live`, `use_bridge`, `start_shared` | struct, fn | `ember/app/src/bridge.rs:42`, `:61`, `:104`, `:93` | 클라이언트 변경을 신호로 바꾸는 브리지 |
| `request_usage_summary`, `request_project_day`, `request_github_summary`, `rescan_agents` | fn | `bridge.rs:276`, `:374`, `:294`, `:331` | 화면이 열릴 때 부르는 요청 |
| `ServerApi` + 데이터 타입 | struct | `ember/app/src/server.rs:352` | `ember_client`가 감싸지 않은 서버 엔드포인트 |
| `Outbox`, `merge_computers`, `session_row`, `project_cards` 외 | struct, fn | `ember/app/src/model.rs:454`, `:403`, `:274`, `:295` | 순수 뷰모델 |
| `Prefs`, `load`, `save` | struct, fn | `ember/app/src/prefs.rs:33`, `:119`, `:136` | 기기별 UI 설정 파일 |
| `AppConfig`, `safe_file_stem` | struct, fn | `ember/app/src/config.rs:17`, `:73` | 서버 URL, 데이터 경로 |
| `DemoSource`, `active_from_env` 외 | struct, fn | `ember/app/src/demo.rs:694`, `:164` | 서버 없는 데모 데이터 |
| `IdeKind`, `open_external`, `spawn_editor_target`, `parse_editor_args` | enum, fn | `ember/app/src/ide.rs:20`, `:103`, `:170`, `:114` | Open IDE, 별도 에디터 창 프로세스 |
| `EditorHost`, `HostCommand`, `HostState` | struct, enum | `ember/app/src/editor_host.rs:199`, `:10`, `:41` | 원격 에디터 세션 소유자 |
| `export_session`, `build` | fn | `ember/app/src/export.rs:31`, `:18` | 대화 내보내기 |
| `start`, `start_view`, `TerminalHandle`, `TerminalState` | fn, struct | `ember/app/src/terminal_stream.rs:713`, `:862`, `:655`, `:393` | 서버 터미널 릴레이 연결 |
| `launch`, `shutdown` | fn | `ember/app/src/lib.rs:39`, `:152` | 진입, 종료 flush |

## 파일별 요약

### `ember/app/src/services.rs` (332줄)

목적: UI 아래의 모든 것을 한 곳에 두고 어느 컴포넌트에서든 `services()`로 접근한다 (`services.rs:1-14`). UI 스레드는 I/O를 하지 않는다. 네트워크와 파일 일은 tokio 워커에서 돌고, 결과는 두 방식 중 하나로 UI에 온다: (a) 워커가 sync 신호를 쓴다 (`bridge`), (b) `run`이 UI 태스크에서 `JoinHandle`을 기다린다 (`services.rs:236-247`).

`Services` 필드 (`services.rs:28-42`):

| 필드 | 타입 | 뜻 | 쓰는 곳 |
|---|---|---|---|
| `config` | `AppConfig` | 서버 URL, 데이터 디렉터리 | 5개 파일 6곳 (`lib.rs:154` 등) |
| `rt` | `tokio::runtime::Runtime` | 워커 2개 (`lib.rs:51`) | `spawn`, `enter`, 터미널과 에디터 호스트 등 6개 파일 |
| `client` | `ember_client::Client` | 동기화 엔진, 상태 리듀서 | 24개 파일 102곳 |
| `server` | `ServerApi` | 클라이언트가 안 감싼 엔드포인트 | 4개 파일 14곳 |
| `demo` | `Option<DemoSource>` | `Some`이면 서버 없이 자체 데이터 (#199). 데모와 서버를 가르는 단 하나의 자리 | 17개 파일 47곳 |
| `outbox` | `Arc<Mutex<Outbox>>` | 보내기 대기열 (FR-L6) | 5개 파일 11곳 |
| `initial_prefs` | `Prefs` | 시작 때 디스크에서 읽은 값. 이후 소유는 `ui.prefs` | 3개 파일 12곳 (`lib.rs:144`, `:189`) |
| `ui` | `SharedUi` | compose-rust 컴포저블이 공유하는 UI와 live 상태 (#220) | 5개 파일 20곳 (`services().ui`) |
| `live` | `OnceLock<Live>` | Dioxus 루트가 마운트될 때 채우는 sync 신호 (`bridge::use_bridge`). 기본 실행 경로에서는 비어 있다 | `bridge.rs`, `reset_demo`, `bump_outbox` |

도우미 (화면이 호출하는 것 전부):

| 이름 | 줄 | 동작 | 호출처 예 |
|---|---|---|---|
| `install` / `services` / `try_services` | 48 / 55 / 60 | 한 번만 설치 (두 번이면 panic `"ember-app services installed twice"`). `try_services`는 단위 테스트에서 `None` | `try_services` 16개 파일 72곳 |
| `Services::spawn` | 66 | 런타임에 fire-and-forget | 8개 파일 19곳 |
| `Services::enter` | 75 | 런타임 컨텍스트 안에서 실행. `Client::open_session`이 내부에서 `tokio::spawn`하기 때문 | `open_session`, `close_session` |
| `open_session(id)` | 81 | 데모면 `DemoSource::open`, 아니면 `client.open_session` (대화 로드, seen 표시, lease 갱신) | `ember/app/src/ui/cr/session.rs:161`, `ui/cr/conversation.rs:2181` |
| `close_session(id)` | 89 | 데모면 `Input::Closed` 적용 | `ui/cr/session.rs:165` |
| `drive_outbox(id)` | 99 | 세션 busy 여부와 `last_seq`로 `Outbox::next`를 부르고, 풀려난 메시지를 워커에서 `client.send_message`로 보낸다. 실패하면 `warn` 로그 후 `Outbox::failed`와 `bump_outbox`. 어느 스레드에서 몇 번을 불러도 안전 | `ui/cr/conversation.rs:335`, `ui/cr/home.rs:692`, `ui/cr/session.rs:1245`, `bridge.rs` |
| `answer(sid, approval_id, decision)` | 128 | 승인 응답. 데모면 상태만 바꾼다 | `ui/cr/conversation.rs:1665` |
| `answer_question(sid, qid, reply)` | 144 | 질문 응답 (FR-T11). 오류는 종류만 (`QuestionCallError::from_error`), 서버 문구는 UI에 가지 않는다 | `ui/cr/conversation.rs:1343` |
| `create_session(body)` | 161 | `ServerApi::create_session` 후 `Input::SessionLoaded`로 클라이언트 상태에 넣는다 | `ui/cr/home.rs:662`, `ui/cr/new_session.rs:233` |
| `patch_session(id, patch)` | 171 | 이름 변경, 고정, 보관 | `ui/cr/launcher.rs:159`, `ui/cr/conversation.rs:1095` |
| `set_approve_all(id, enabled)` | 180 | 모두 승인. 데모면 `Input::ApproveAllLoaded` | `ui/cr/session.rs:429`, `ui/cr/home.rs:671` |
| `demo_blocked()` | 190 | 데모면 토스트 `"데모에서는 쓸 수 없습니다"`를 띄우고 `true`. 호출자는 서버 호출 없이 돌아간다 (#202) | `ui/cr/launcher.rs:247`, `ui/cr/search.rs:86` |
| `reset_demo()` | 202 | 데모 상태, outbox, 세션 pane 설정을 초기 시드로. 데모가 아니면 `false` | `ui/cr/shell.rs:391`, `ui/cr/routines.rs:3475` |
| `bump_outbox()` | 225 | 대기 메시지 표시기를 다시 그리게 한다 (`ui.live.outbox`와 `live.outbox`) | `ui/cr/home.rs:690`, `ui/cr/conversation.rs:334` |
| `run(work, then)` | 236 | 워커에서 `work`, UI 스레드에서 `then`. Dioxus 스코프 안에서만 쓴다 (`dioxus_core::spawn`). 태스크 실패면 토스트 `"Background task failed: …"` | 이 모듈 밖 호출을 확인하지 못함 [확인 필요] |
| `run_shared(work, then)` | 253 | 스코프 밖(compose-rust)용. `then`은 워커에서 돌며 `MutableState`를 쓴다 | 16개 파일 99곳 |
| `save_prefs(_)` | 264 | 인자는 쓰지 않는다. `ui.prefs` 최신 값을 읽어 `prefs_write_lock` 아래 `prefs::save` (오래된 스냅샷이 새것을 덮지 못하게 직렬화) | `ui/coexist.rs:266`, `ui/mod.rs:132` |
| `prefs_write_lock` | 270 | 정적 `Mutex<()>`. `lib.rs:152`의 `shutdown`도 쓴다 | |
| `test_services`, `test_guard` | 284, 324 | 테스트용: 데모 데이터, `http://127.0.0.1:9`, `.scratch/test-data` | 테스트 전용 |

주의: 데모 분기가 helper마다 흩어져 있어 (`open_session`, `close_session`, `answer`, `create_session` 등) 새 helper를 만들 때 `self.demo` 분기를 빠뜨리기 쉽다.

### `ember/app/src/server.rs` (703줄, 테스트 14개)

목적: `ember_client`가 아직 감싸지 않은 메인 서버 엔드포인트 (계정 FR-U1/U2, 컴퓨터 FR-X3, Open IDE 대상 FR-L7, 에이전트 기본값 FR-L20). 응답은 관대하게 디코드한다 (모르는 필드 무시, 선택 필드 기본값) (`server.rs:1-12`). `TODO(ember-client)`: 클라이언트 크레이트가 커지면 `ember_client::api`로 옮긴다 (`server.rs:9`).

`ServerApi` (`server.rs:352`)는 `reqwest::Client`와 base URL만 가진다. `url(path)`는 `{base}/api{path}` (`:393`). 토큰은 `ember_client::token`으로 한 번 읽고 루프백이거나 `EMBER_TOKEN_HOSTS`에 든 호스트에만 `Authorization`을 붙인다 (FR-S11, `:360-382`). 비성공 응답은 `status_error`로 바뀐다: 401은 `ServerError::Unauthorized`, 나머지는 `Status { status, message }`이며 `message`는 본문 JSON의 `error` 값이거나 원문이다 (`:494-503`). 경로 조각은 `seg`가 퍼센트 인코딩한다 (`:523`).

| 메서드 | 줄 | HTTP 호출 | 서버 핸들러 (`_raw/routes.md`) | 쓰는 곳 |
|---|---|---|---|---|
| `accounts()` | 406 | `GET /api/accounts` | `ember/server/src/accounts/api.rs:36` `list` | `bridge.rs:473`, `ui/cr/agents.rs:1351` |
| `set_default_account(id)` | 411 | `POST /api/accounts/{id}/default` | `accounts/api.rs:39` `set_default` | `ui/cr/agents.rs:1333` |
| `create_account(agent, label)` | 417 | `POST /api/accounts` 본문 `{agent, label}` | `accounts/api.rs:36` `create` | `ui/cr/agents.rs:1598` |
| `check_account(id)` | 423 | `POST /api/accounts/{id}/check` | `accounts/api.rs:40` `check` | `ui/cr/agents.rs:1632` |
| `chatgpt_accounts()` | 429 | `GET /api/chatgpt/accounts` (404면 로그인 꺼짐) | `ember/server/src/chatgpt/api.rs:38` `list` | `bridge.rs:484` |
| `computers(probe)` | 434 | `GET /api/computers?probe=` | `ember/server/src/computers/api.rs:39` `list` | `bridge.rs:468`, `:531`, `ui/cr/add_computer.rs:306` |
| `session_computer(id)` | 439 | `GET /api/sessions/{id}/computer` | `computers/api.rs:41` `current` | `ui/cr/session.rs:1120`, `:4477` |
| `switch_computer(id, cid)` | 444 | `PUT /api/sessions/{id}/computer` 본문 `{computer_id}` | `computers/api.rs:41` `switch` | `ui/cr/home.rs:666`, `ui/cr/new_session.rs:238` |
| `ide_targets(id, computer)` | 452 | `GET /api/sessions/{id}/ide?computer=` | `ember/server/src/api/ide.rs:483` `ide_targets` | `ui/cr/project.rs:904` |
| `create_session(body)` | 460 | `POST /api/sessions` | `ember/server/src/api/mod.rs:86` `create_session` | `services.rs:166` |
| `agent_defaults()` / `put_agent_defaults()` | 466 / 471 | `GET`, `PUT /api/agents/defaults` | `api/mod.rs:84` | `bridge.rs:520`, `ui/cr/agents.rs:107` |
| `agent_settings()` | 477 | `GET /api/agents/settings` | `api/mod.rs:83` | `bridge.rs:521` |
| `put_agent_mem_limit(agent, mb)` | 482 | `PUT /api/agents/{agent}/settings` 본문 `{mem_limit_mb}` (`None`이나 0이면 해제) | `api/mod.rs:85` | `ui/cr/agents.rs:139` |

데이터 타입: `Account`(`:35`), `Login`(`:51`, `Debug`가 로그인 명령을 찍지 않는다 `:60`), `AccountWithLogin`(`:69`), `WeeklyCap`(`:79`), `ChatGptAccount`(`:90`), `ComputerStatus`(`:112`), `CurrentComputer`(`:136`), `SwitchOutcome`(`:150`), `IdeTarget`/`IdeComputer`/`IdeLaunch`(`:161`/`:177`/`:185`), `EditorConnection`(`:232`), `AgentDefaults`(`:310`), `AgentSettingsResponse`(`:323`), `CreateSession`(`:338`, `account`가 `None`이면 서버 라우터가 고른다, FR-U3). `IdeLaunch::editor_target`(`:199`), `editor_connection`(`:208`)은 OSE 엔드포인트에서 스킴을 벗기고 토큰을 싣는다 (FR-L31). 오류 문구: `request failed: …`, `server answered {status}: {message}`, `authentication failed: the server refused the token (…)` (`:19-26`).

### `ember/app/src/bridge.rs` (553줄)

목적: 클라이언트 `State` 변경을 UI가 다시 그릴 신호로 바꾼다. 신호가 두 벌이다.

- `SharedLive` (`ember/app/src/ui/coexist.rs:39`, `MutableState`들)는 기본 실행 경로(compose-rust 셸)가 읽는 실제 신호이고 `Services.ui.live`에 있다. 필드: `launcher`, `transcripts`, `outbox`, `teams`, `accounts`, `chatgpt`, `agents`, `agents_rescan`, `agents_checked_ms`, `agent_defaults`, `agent_store_rev`, `usage`, `usage_summary`, `github`, `project_day`.
- `Live` (`bridge.rs:42`, `SyncSignal`들: `launcher`, `transcripts`, `outbox`, `teams`, `accounts`, `chatgpt`, `agents`, `usage`)는 옛 Dioxus 루트용이다. `Live::use_live()`는 `ui/mod.rs:209`에서만 부르는데, 이 Dioxus 루트 `app`은 어디서도 호출되지 않는다 ([entrypoints.md](../_raw/entrypoints.md) 중요 문단). 기본 경로에서 `Services.live`는 비어 있고 코드의 `live.or_else(...)` 분기는 `None`으로 돈다.

| 심볼 | 줄 | 설명 |
|---|---|---|
| `start_shared()` | 93 | `BRIDGE_STARTED`(`OnceLock`, `:89`)로 한 번만. `changes_task`와 `refresh_task`를 런타임에 띄운다. 기본 경로의 진입 (`lib.rs:143`) |
| `use_bridge(live)` | 104 | 같은 두 태스크를 Dioxus 루트에서 시작하고 `Services.live`를 채운다 |
| `changes_task` | 128 | `client.subscribe()`의 `Changes`를 받는다. 처음에 `bump_all`, `Lagged(n)`이면 `lagged=true`로 전부 다시 그린다. `watch_revision`이 바뀌고 `lagged`였다면 `bump_all`, `refresh.notify_one()`, 열린 세션마다 `drive_outbox` |
| `Fingerprints` | 169 | 세션별 `(LauncherStatus, 문자열, 문자열, bool, bool, i64)` 지문 (`:172`). 스트리밍 델타는 `last_seq`와 `updated_at`을 매번 바꾸므로 지문이 바뀔 때만 런처를 다시 그린다. 시간 표시는 30초 단위 (`LAUNCHER_TIME_STEP_MS`, `:175`) |
| `on_changes` | 202 | `Changes`를 신호로: 세션 지문 변경, 프로젝트 목록 변경 (세션 변경 없이 `ch.projects`), `computers`, `connection`이면 `launcher`. `transcripts`가 비어 있지 않으면 `transcripts`. `teams`면 `teams`. 마지막에 변경된 세션마다 `drive_outbox` (턴 경계는 상태 변화로 드러난다) |
| `refresh_task` | 232 | `REFRESH_EVERY` 30초 (`:37`)마다 `full=true`로 `refresh_once`. `refresh` 알림이 오면 300ms 합친 뒤 `full=false` |
| `refresh_once` | 252 | `full`이면 `refresh_slow`, 아니면 `client.load_projects()`만 (데모는 건너뜀) |
| `refresh_slow` | 442 | 아래 문단 |
| `request_usage_summary` | 276 | 화면 마운트 때 한 번 (`fetch_usage_summary`) |
| `request_project_day(project)` | 374 | 프로젝트당 첫 호출만 요청하고 `WATCHED_PROJECTS`(`:272`)에 넣어 느린 타이머가 갱신 |
| `request_github_summary` | 294 | Home 열림 때 `force=true`. 데모나 `github_sample_from_env`면 건너뜀 |
| `fetch_github` | 307 | `client.api().github_summary()` (서버 `/api/integrations/github` [확인 필요: 라우트 표 미대조]). 타이머는 서버 캐시 시간 `GITHUB_MIN_GAP`(주석상 90초)에 묶인다. 실패하면 마지막 답을 유지 |
| `rescan_agents` | 331 | `client.api().detect_harnesses("local")` (`POST /api/computers/local/harnesses/detect`, FR-A6.1). `agents_rescan`에 `Running`, 끝나면 `Done(문장)`, 6초 뒤 `Idle`. 데모는 `" (예시)"`를 붙인다 |
| `settle` | 388 | 새 데이터 또는 실패. 이전 데이터가 있으면 실패해도 유지 |

`refresh_slow` 순서 (`bridge.rs:442-538`): 데모면 `demo::accounts/chatgpt_accounts/usage/agents`로 신호를 채우고 끝 (요청 없음). 아니면 (1) 첫 회에만 `computers(false)`를 `merge_computers` 후 `Input::ComputersLoaded`로 적용 (FR-L3: 도달성 모르는 채 먼저 그림), (2) `accounts()`, (3) `chatgpt_accounts()` (실패는 빈 목록), (4) `client.api().usage(Some(14))`, (5) `fetch_usage_summary`, (6) 첫 회가 아니면 `fetch_github(false)`, (7) 보는 프로젝트의 오늘 사용량, (8) `client.agents()`와 `agents_checked_ms`, (9) `agent_defaults`와 `agent_settings`를 받아 `ui::cr::agents::sync_from_server`, (10) 마지막에 `computers(true)` 프로브 (모든 노드에 묻느라 오래 걸릴 수 있어 끝에 둔다). 실패는 `tracing::debug!`로만 남고 화면에 가지 않는다.

`request_github_summary`(`:294`)와 `github_request_count`(`:289`)는 `#[cfg(test)]` 계수와 함께 있고, `ui/cr/home.rs:2487`의 테스트가 쓴다.

### `ember/app/src/model.rs` (1,051줄, 테스트 18개)

목적: 화면에 보일 것을 `State`와 서버 답에서 계산하는 순수 함수. UI 타입도 I/O도 없다 (`model.rs:1-5`). 쓰는 곳: `ui/coexist.rs:20`, `ui/compat.rs:5`, `bridge.rs:33` 등.

| 이름 | 줄 | 설명 |
|---|---|---|
| `status_rank`, `status_label`, `is_busy` | 19, 31, 44 | 프로젝트 배지 우선순위 (승인 대기가 실행 중보다 높다, FR-L2), 라벨 `Idle`, `Running` 등. `is_busy`는 `drive_outbox`가 쓴다 |
| `approve_all_banner`, `approve_all_menu_label`, `FORK_MENU_LABEL`(`"Fork from last turn"`), `FORK_TURN_LABEL`(`"Fork from here"`), `fork_menu_enabled`, `fork_turn_enabled`, `fork_origin_label` | 50-80 | 모두 승인과 포크 메뉴 문구와 활성 조건 |
| `Tone`, `ProjectSummary` | 87, 97 | 상태 개수 집계, `badges()` |
| `relative_time`, `one_line`, `preview`, `json_summary`, `json_pretty` | 151-212 | 시각과 미리보기 문자열 |
| `ProjectCard`, `SessionRow`, `RowContext`, `session_row`, `project_cards`, `project_sessions`, `recent_sessions` | 219-402 | 런처 카드와 행. 계정 라벨은 `account_labels`(`:243`), ChatGPT 사용 줄은 `chatgpt_usage_line`(`:249`) |
| `SearchResult`, `search_results` | 333, 345 | 서버 검색 히트(`SearchHit`)와 상태를 합침 |
| `merge_computers`, `reachability_label`, `connection_banner` | 403, 424, 433 | `GET /computers`를 클라이언트 컴퓨터 목록으로. `reachable: None`이면 이전 도달성 유지 (없으면 `Unknown`, 라벨 "Checking…"). 오프라인 컴퓨터도 남는다. `projects`는 이전 값 유지. 연결 상태 배너 |
| `Outbox` | 454 | 아래 |
| `latest_cwd`, `index_of`, `dedup`, `is_assigned`, `join_projects` | 517-539 | 새 세션 기본값 (FR-L8) 등 |
| `typed_mention`, `filter_mentions`, `mention_token`, `apply_mentions`, `TypedMention` | 548-621 | `@` 멘션 입력 |
| `TeamMemberRow`, `team_member_rows`, `task_line` | 623-690 | 팀 패널 행 (FR-T7) |

`Outbox` (`model.rs:454`): 필드 `queues`(세션 → 대기 `VecDeque<String>`), `in_flight`(세션 → 보낸 시점 `last_seq`), `errors`. 메시지는 바쁜 동안 쌓이고 턴 경계마다 하나씩 나간다. 모든 전송이 여기를 지나므로 idle일 때 친 메시지는 즉시, 다음 것은 그 턴이 끝난 뒤 나간다. `next(id, busy, last_seq)`(`:485`): busy면 `in_flight`를 지우고 `None`. `in_flight`가 있고 `last_seq`가 그 값 이하면 `None` (아직 전달 확인 전), 넘으면 해제. 그다음 큐 앞에서 하나를 꺼내 `in_flight`에 현재 `last_seq`를 넣는다. 전달 확정은 "세션이 busy로 관측됨" 또는 "`last_seq`가 전진함" (busy를 못 본 짧은 턴 대비). `failed`(`:506`)는 메시지를 큐 앞에 되돌리고 오류를 기억한다. `push`(`:462`)는 오류를 지운다. 공개 메서드: `push`, `queued`, `queued_texts`, `clear`, `error`, `next`, `failed`.

### `ember/app/src/prefs.rs` (293줄, 테스트 9개)

목적: 기기별 UI 선택. 고정, 보관, 제목 (FR-L9)과 컴퓨터 배정 (FR-L4)은 서버에 있다. 옛 파일의 `pinned`, `archived`, `titles` 키는 읽을 때 무시하고 다음 저장 때 사라진다 (`prefs.rs:3-7`).

위치: `{data_dir}/prefs.json`. `data_dir`은 `EMBER_DATA_DIR`이거나 `dirs::data_dir()/ember` (`config.rs:33-46`, `:52`). `load`는 파일이 없거나 깨졌거나 `format`이 다르면 기본값이다 (시작을 막지 않는다, `prefs.rs:119-134`). `save`는 임시 파일 `.tmp`에 쓰고 rename한다 (`:136-147`).

| 필드 | 타입 | 기본 | 뜻 |
|---|---|---|---|
| `format` | `u32` | `PREFS_FORMAT = 1` (`:12`) | 다르면 파일 전체를 무시 |
| `last_used` | `BTreeMap<project, LastUsed>` | 빈 맵 | 프로젝트별 새 세션 조합: `agent`, `account`, `computer`, `model`, `cwd` (FR-L8, `:15-27`) |
| `last_project` | `Option<String>` | `None` | 마지막 선택 프로젝트 |
| `ide_target` | `Option<String>` | `None` | `ember`, `vscode`, `gateway` |
| `theme` | `ThemePref` | System | System, Light, Dark (FR-L28). 옛 파일에 없으면 System |
| `session_view` | `Option<String>` | `None` | `multi`, `single`, `status` (FR-L18) |
| `panes` | `BTreeMap<project, ProjectPanes>` | 빈 맵 | 프로젝트별 pane 탭 |
| `character_styles` | `BTreeMap<project, CharStyle>` | 빈 맵 | 팀 캐릭터 스타일, 없으면 몽글 (FR-L22). `TODO(server)`: 서버에 필드가 생기면 서버가 가진다 (`:54`) |
| `keymap` | `Keymap` | VS Code | 에디터 단축키 세트 (FR-L30) |

`rename_project_keys(old, new)`는 `last_used`, `panes`, 캐릭터 스타일, `last_project`를 새 이름으로 옮기고, 새 이름에 이미 항목이 있으면 그것을 지킨다 (FR-L26, #412). 이 파일은 `crate::ui::theme`, `ui::session`, `ui::characters`, `ui::keymap` 타입에 의존한다. 쓰기 경로: `SharedUi::update_prefs`(`ui/coexist.rs:258`) → `save_prefs` → `prefs::save`. 종료 때 `lib.rs:152`의 `shutdown`이 한 번 더 저장한다.

### `ember/app/src/config.rs` (122줄)

`AppConfig { server_url, data_dir }` (`config.rs:17`). `from_env`(`:24`)는 `EMBER_SERVER_URL` (공백과 끝 `/` 제거, 비면 `DEFAULT_SERVER_URL = "http://127.0.0.1:8740"`), `EMBER_DATA_DIR`, `dirs::data_dir()`를 읽는다. `cache_path()`는 `client-cache.json`, `prefs_path()`는 `prefs.json`, `export_dir()`는 `exports/` (데이터 디렉터리가 없으면 `temp_dir()/ember-exports`). `client_config()`는 캐시 경로와 lease 30초를 채운다 (`:63-69`). `safe_file_stem`(`:73`)은 영숫자와 `-`, `_` 외를 `-`로 바꾸고 48자로 자르며 비면 `"session"`이다.

### `ember/app/src/demo.rs` (3,025줄, 테스트 59개, 모양만)

`EMBER_DEMO_DATA=1`이고 `EMBER_SERVER_URL`이 없거나 빈 값일 때만 켜진다 (`demo::active`, `demo.rs:159`). 서버 없는 Windows PC에서 모든 화면을 보여주려는 용도다 (#199). 구조:

- 고정 데이터 함수: `projects`(`:296`), `computers`(`:357`), `agents`(`:389`), `accounts`(`:412`), `chatgpt_accounts`(`:433`), `usage`(`:195`), `usage_summary`(`:218`), `metrics_sample`(`:316`), `ports`(`:377`), `github_state`(`:214`), `second_team`(`:263`).
- `DemoSource` (`:694`): 필드 `events`(세션별 `StoredEvent`), `created`(만든 세션 수), `data_dir`, `git`(프로젝트별 가짜 git 상태, `GitState`, `DemoFile`, `DemoBranch` 등 `:1152-1273`). 메서드: `new`, `with_data_dir` (`demo-project`, `second-project` 폴더 준비), `reset`, `sessions`, `inputs` (클라이언트에 넣을 `Input` 목록), `events_for`, `open`, `send_message`, `answer`, `answer_question`, `create_session`, `create_project`, `git`, `github_summary`, `patch_session`.
- 서버로 갈 동작을 상태 변경으로 대체한다 (`Services`의 각 helper가 `self.demo` 분기로 호출). 서버가 필요한 동작은 `UNAVAILABLE = "데모에서는 쓸 수 없습니다"`(`:44`)를 띄운다. 알림 문구 `DEMO_NOTICE = "데모 모드입니다"`(`:38`).
- 환경 변수 `EMBER_DEMO_DATA`(`DEMO_ENV`, `:32`), `EMBER_DEMO_OSE`(`DEMO_OSE_ENV`, `:60`). 데모 폴더는 `data_dir` 아래이고 없으면 `temp_dir()/ember-demo` (`lib.rs:77-80`). 데모 캐시는 쓰지 않는다 (`lib.rs:158`).
- 테스트 59개가 이 파일에 있고 UI 화면 구성을 검증한다 (`demo.rs:2107` 이후 `cfg(test)`). 사용처: `services.rs`, `bridge.rs`, `lib.rs`, UI 17개 파일 (`.demo` 47곳).

### `ember/app/src/lib.rs` (214줄), `main.rs` (9줄)

`lib.rs`는 모듈 선언 (`:14-25`)과 `launch`(`:39`), `shutdown`(`:152`), `flush_before_exit`(`:169`), `launch_builder`(`:183`, 창 제목 "Ember", 글꼴 테마)다. 순서는 [entrypoints.md](../_raw/entrypoints.md)를 본다. 추가로 확인한 것: 서버 URL이 잘못되면 `ember-app: {e}. Set EMBER_SERVER_URL to the main server, e.g. http://127.0.0.1:8740`를 찍고 종료 코드 2 (`lib.rs:64-68`), `ServerApi::new` 실패도 종료 코드 2 (`:101-102`), 데모 폴더 생성 실패는 `expect("데모 폴더를 만들 수 없습니다")` panic (`:80`). `EMBER_CR_SIZE=WxH`는 별도 에디터 창 크기 (`:121-125`, 기본 1280x820), 창 제목은 `Box::leak`한 `"{project} - Ember"` (`:129`). `main.rs`는 `ember_app::launch()`만 부르고 Windows에서 콘솔을 띄우지 않는다 (`windows_subsystem = "windows"`).

### `ember/app/src/ide.rs` (304줄), `export.rs` (72줄), `editor_host.rs` (463줄)

- `ide.rs` (테스트 3개): `IdeKind`(`Ember`, `VsCode`, `Gateway`, `:20`)와 `plan`(`:62`)은 서버가 준 `IdeTarget`을 `IdeAction`(`OpenUrl`, `EmberPlaceholder`, `Unavailable`)으로 바꾼다. `allowed_url`(`:80`)은 VS Code에 `http(s)`, Gateway에 `jetbrains-gateway://`와 `jetbrains://`만 허용해 서버 답이 임의 프로그램을 열지 못하게 한다. `open_command`(`:90`)는 macOS `open`, Windows `rundll32 url.dll,FileProtocolHandler` (`cmd /c start`는 `&`에서 갈라지므로 쓰지 않음), 그 외 `xdg-open`. 별도 에디터 프로세스: `EDITOR_ARG = "--editor"`, 인자 `<project> [folder] [endpoint]`를 `parse_editor_args`(`:114`)가 읽고, 토큰, 서버 URL, 컴퓨터 ID는 argv가 아니라 환경 변수 `EMBER_EDITOR_TOKEN`, `EMBER_EDITOR_SERVER`, `EMBER_EDITOR_COMPUTER`로 자식에게 넘긴다 (`:124-128`, `:170-178`). 사용자 문구: `"Ember 에디터: 새 창에서 여는 중입니다"`, `"Ember 에디터: 열지 못했습니다: {e}"` (`:187-199`), 거부 사유 `"the server offers no {label} target"`, `"refusing to open {url:?}: unexpected scheme"`.
- `export.rs` (테스트 1개): `export_session`(`:31`)이 `Api::export_session` (`GET /api/sessions/{id}/export`)으로 서버 파일을 받고 `build`(`:18`)로 클라이언트 리듀서가 만든 `transcript`를 덧붙여 `{exports}/{safe_file_stem(title)}-{id 앞 8자}.json`에 쓴다 (FR-L9). 파일 쓰기는 `spawn_blocking`. 사용처 `ui/cr/launcher.rs:252`. 오류 문자열 `"export has no readable events: …"`, `"export is not a JSON object"`.
- `editor_host.rs` (테스트 6개): 원격 에디터 세션을 런타임에서 소유한다. `EditorHost::start(target, revision)`(`:205`)이 `EditorSession::connect_tcp`로 연결하고 (`app_language = "ko"` `:219`, 토큰은 비면 없음), 루트 폴더를 `read_dir`한 뒤 명령 루프에서 `HostCommand`(`:10`: `List`, `Open`, `Close`, `Focus`, `Widget`, `Resync`, 파일 만들기, 이름 바꾸기, 삭제, 복사, 이동, `IndexFiles`, `ExecuteCommand`, `Search`/`SearchNow`/`CancelSearch`/`Replace`, `DiscardFile`)를 처리한다. 상태 `HostState`(`:41`)는 `Mutex`로 공유하고 UI는 `revision` 신호로 깨운다. 인덱스 상한은 파일 20,000개와 디렉터리 5,000개 (`:128-131`). 문구 `"서버에 연결할 수 없습니다"`(`:66`). 사용처 `ui/editor_workbench.rs`, `ui/editor_scm.rs`, `ui/editor_search.rs`. `crate::ui::*` 타입 (`EditorTarget`, `FileDiff`, `SearchResults`, `palette::Item`)에 의존한다.

### `ember/app/src/terminal_stream.rs` (1,204줄)와 `terminal_screen.rs` (625줄)

`terminal_stream.rs:9-10`이 `#[path = "terminal_screen.rs"] mod screen;`으로 `terminal_screen.rs`를 자기 하위 모듈로 포함한다. 그래서 `lib.rs`에는 `terminal_screen` 모듈 선언이 없다.

`terminal_stream.rs` (테스트 19개): 서버의 터미널 릴레이에 붙는다. 서버가 노드에 영속 세션을 만들거나 키로 다시 붙이고 (`POST /api/computers/{computer}/terms`), `GET /api/computers/{computer}/terms/{id}/attach` WebSocket으로 노드 이벤트가 내려오고 입력 프레임이 올라간다 (`:1-7`). 노드 JSON 모양은 이 파일에 복제해 노드 크레이트에 의존하지 않는다.

| 이름 | 줄 | 설명 |
|---|---|---|
| `terms_url`, `attach_url`, `terms_list_url`, `session_key` | 47-77 | URL 생성. 세션 키는 `"<project>:<folder>"` |
| `TermCreateRequest`, `TermInfo`, `TermClient`, `TermRefusal`, `TermHello`, `TermEvent`, `TermPick`, `pick_agent_terminal` | 97-210 | 와이어 타입. 거부 사유 `Controlled`, `ReadOnly`, `NotRunning` |
| `input_frame`, `resize_frame`, `take_control_frame`, `release_control_frame`, `detach_frame`, `key_bytes`, `text_bytes`, `Modifiers` | 252-375 | 위로 올리는 프레임, 키를 바이트(CSI)로 |
| `TerminalState`, `TerminalSession`, `TerminalUpdate`, `apply_event` | 393-583 | 패널이 보이는 상태: 디코드된 화면, 제어자, 종료, 오류 |
| `TerminalHandle`, `start`, `start_view` | 655, 713, 862 | `start`는 폴더용 에디터 터미널을 붙이고 (없으면 만든다), `start_view`는 프로젝트의 에이전트 터미널을 보기 전용(`TermHello::viewer`, `:173`)으로 붙는다. 둘 다 `services().rt.spawn`으로 `run`/`view` 태스크를 돌린다 |
| `stream` | 802 | WebSocket. 토큰이 있으면 `Authorization` 헤더 |
| `decode_screen` | 597 | `screen::Screen` (alacritty 에뮬레이터)으로 바이트를 줄 목록으로 |

화면 문구 (`terminal_stream.rs:436-490`): `"터미널이 연결되지 않았습니다."`, `"터미널에 연결하는 중입니다."`, `"다른 기기가 입력 중입니다: {device}"`, `"다른 기기가 입력 중입니다."`, `"읽기 전용으로 연결되어 입력할 수 없습니다."`, `"터미널이 실행 중이 아닙니다."`, `"프로세스가 종료되었습니다. (종료 코드 {code})"`, `"프로세스가 종료되었습니다. (시그널 {signal})"`, `"터미널 오류: {e}"`. 사용처 `ui/term_pane.rs`, `ui/editor_workbench.rs`, `ui/cr/session.rs`.

`terminal_screen.rs` (테스트 7개): PTY가 낸 모든 바이트를 `alacritty_terminal`에 먹여 나중에 붙은 클라이언트도 같은 화면을 얻게 하는 모델이다. `Screen::snapshot`(`:202`)은 새 터미널에 쓰면 스크롤백, 보이는 화면 (주 화면과 대체 화면), 커서, 펜, 입력 모드, 제목을 재현하는 바이트열이다. 스크롤백은 SGR로 인코딩한 줄의 링이고 상한은 `SCROLLBACK_LINES = 10_000` (`:36`), `SCROLLBACK_BYTES = 3 MiB` (`:39`), 줄당 256 KiB (`:44`). 재현하지 못하는 것 (스크롤 영역 DECSTBM, 원점 모드, DECSC, 문자셋, 탭 정지, OSC 8, 밑줄 색)은 파일 머리 주석에 있고, TUI가 다음 전체 repaint에서 다시 그린다. `vt100` 대신 alacritty를 고른 이유는 스크롤백 접근과 `clear_history`가 되기 때문이다.

### 작은 파일과 비코드 파일

| 파일 | 줄 | 설명 |
|---|---|---|
| `ember/app/Cargo.toml` | 56 | 크레이트 `ember-app`, lib `ember_app` + bin `ember-app`, edition 2024, Rust 1.85. `compose-rust`(git tag `v0.0.6`), `dioxus-compose`(git rev), 경로 의존 `ember-client`, `ember-editor`, `ember-editor-conn`, `alacritty_terminal 0.26`, `tokio-tungstenite 0.28`, `reqwest 0.12`(TLS 없음), `dirs 6` |
| `ember/app/Dioxus.toml` | 16 | 패키저용 번들 메타데이터: 이름 Ember, 식별자 `dev.darkpyonix.ember`. 아이콘은 아직 없다 (TODO, `Dioxus.toml:3`) |
| `ember/app/README.md` | 108 | 실행 방법과 환경 변수 표 |
| `ember/app/assets/fonts/*` | OFL 2개 + otf 6개 | Inter, Pretendard (`ui/fonts.rs`가 `include_bytes!`) |
| `ember/app/assets/editor/{editor,page,style}.css` | 133, 10, 582 | 에디터 창 CSS (`ui/editor_workbench.rs:276-278`이 `include_str!`) |
| `ember/app/assets/code-oss/{actionWidget,titlebarpart,views}.css`, `pristine/*`, `LICENSE-Code-OSS.txt` | 639, 545, 376 (pristine은 같은 세 개) | Code-OSS의 `:has()` 규칙을 상태 클래스로 고친 CSS와 원본. `workbench-has.patch`(85줄)를 `ember/ose/vendor-workbench-css.sh`가 `patch -p1`로 적용한다 (패치 머리 주석). `ui/workbench.rs:10`이 `include_str!` |
| `ember/app/assets/brand`, `assets/nav` | SVG | 로고와 내비게이션 아이콘 (내용은 읽지 않음) |
| `ember/app/scripts/linux-gui/{Dockerfile,start.sh,capture.sh,click.sh,key.sh}` | 7, 7, 6, 4, 4 | Docker + Xvfb + openbox로 Linux에서 `EMBER_DEMO_DATA=1` 앱을 띄우고 스크린샷을 `.scratch/linux-gui/`에 저장하는 검증 도구. `start.sh`는 컨테이너 안에서 `cargo build --release --locked`를 돌린다 (사람이 부르는 스크립트, 에이전트는 실행하지 않는다) |

## 동작 지도

UI 아래 서비스 계층이므로 "서비스 helper → 서버 호출" 표로 둔다. 화면 문구와 핸들러는 app-ui 쪽에서 본다.

| 동작 | helper | 호출 | 서버 라우트 |
|---|---|---|---|
| 세션 열기 | `Services::open_session` (`services.rs:81`) | `Client::open_session` | 대화 로드와 `POST /api/sessions/{id}/lease` (클라이언트 내부, [client](client.md)) |
| 메시지 보내기 | `drive_outbox` (`:99`) | `Client::send_message` | `POST /api/sessions/{id}/messages` |
| 승인 응답 | `answer` (`:128`) | `Client::answer` | `POST /api/sessions/{id}/approvals/{approval_id}` |
| 질문 응답 | `answer_question` (`:144`) | `Client::answer_question` | `POST /api/sessions/{id}/questions/{question_id}/answer` |
| 세션 만들기 | `create_session` (`:161`) | `ServerApi::create_session` | `POST /api/sessions` |
| 이름, 고정, 보관 | `patch_session` (`:171`) | `Client::patch_session` | `PATCH /api/sessions/{id}` |
| 모두 승인 | `set_approve_all` (`:180`) | `Client::set_approve_all` | `PUT /api/sessions/{id}/approve-all` |
| 컴퓨터 바꾸기 | `ServerApi::switch_computer` | `server.rs:444` | `PUT /api/sessions/{id}/computer` |
| 계정 지정, 생성, 점검 | `ServerApi` | `server.rs:411`, `:417`, `:423` | `POST /api/accounts/{id}/default`, `POST /api/accounts`, `POST /api/accounts/{id}/check` |
| 에이전트 기본값, 메모리 제한 | `ServerApi` | `server.rs:471`, `:482` | `PUT /api/agents/defaults`, `PUT /api/agents/{agent}/settings` |
| 대화 내보내기 | `export::export_session` | `Api::export_session` | `GET /api/sessions/{id}/export` |
| 터미널 붙기 | `terminal_stream::start` | `POST .../terms`, WebSocket | `/api/computers/{computer}/terms`, `/terms/{id}/attach` |

사용자에게 보이는 에러 메시지 (주요한 것):

| 원문 | 위치 | 조건 |
|---|---|---|
| `데모에서는 쓸 수 없습니다` | `ember/app/src/demo.rs:44` | 데모에서 서버 필요 동작 (`demo_blocked`) |
| `Background task failed: {e}` | `services.rs:245` | `run`의 워커 태스크가 패닉이나 취소 |
| `authentication failed: the server refused the token (…)` | `server.rs:25` | 서버가 401 |
| `server answered {status}: {message}` | `server.rs:22` | 비성공 응답 |
| `Ember 에디터: 열지 못했습니다: {e}` | `ide.rs:197` | `--editor` 프로세스 spawn 실패 |
| `서버에 연결할 수 없습니다` | `editor_host.rs:66` | 에디터 엔드포인트가 비었거나 연결 실패 (원인을 덧붙임) |
| `터미널 오류: {e}` | `terminal_stream.rs:482` | 터미널 attach 실패 |
| `ember-app: {e}. Set EMBER_SERVER_URL …` | `lib.rs:64` | 잘못된 서버 URL, 종료 코드 2 (콘솔 없는 Windows 빌드에서는 사용자가 못 볼 수 있다 [추정]) |

## 데이터와 설정

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_SERVER_URL` | `config.rs:26`, `demo.rs:167` | 메인 서버 | `http://127.0.0.1:8740` |
| `EMBER_DATA_DIR` | `config.rs:27` | 데이터 디렉터리 덮어쓰기 | `{OS 데이터}/ember` |
| `EMBER_DEMO_DATA` | `demo.rs:32` | `1`이고 서버 URL 없음이면 데모 | 꺼짐 |
| `EMBER_DEMO_OSE` | `demo.rs:60` | 데모 IDE 대상 | 없음 |
| `EMBER_LOG` | `lib.rs:42` | tracing 필터 | `warn,ember_app=info,ember_client=info` |
| `EMBER_CR_SIZE` | `lib.rs:122` | `--editor` 창 크기 `WxH` | 1280x820 |
| `EMBER_EDITOR_TOKEN`, `EMBER_EDITOR_SERVER`, `EMBER_EDITOR_COMPUTER` | `ide.rs:124-128` | 부모가 자식 에디터 프로세스에 넘기는 접속 정보 (값은 기록하지 않음 `***`) | 빈 문자열 |
| `EMBER_TOKEN_HOSTS`, 서버 토큰 환경 변수 | `ember_client::token` ([client](client.md)) | 서버 토큰을 보낼 호스트 | 루프백만 |
| 파일 | `{data_dir}/prefs.json`, `client-cache.json`, `exports/` | 설정, 클라이언트 콜드스타트 캐시, 내보내기 | 데이터 디렉터리가 없으면 설정과 캐시 없이 실행 |

외부 연동: 메인 서버 HTTP, 터미널 릴레이 WebSocket (`ws`만, TLS 없음), OS URL 핸들러 (`open`, `rundll32`, `xdg-open`). GitHub 요약은 서버 경유다.

## 이 모듈을 수정할 때 주의할 점

- `Services`에 필드를 더하면 `lib.rs:105`의 `install`과 `services.rs:307`의 `test_services` 두 곳을 함께 고친다.
- 서버 호출 helper를 더할 때는 `self.demo` 분기를 같이 둔다. 빠뜨리면 데모에서 존재하지 않는 서버를 부른다.
- 신호 수정은 `SharedLive`(`ui/coexist.rs:39`)와 `Live`(`bridge.rs:42`) 둘 다 필요한지 확인한다. 기본 경로는 `SharedLive`만 읽는다.
- 대기열을 바꾸는 코드(`Outbox::push`, `clear`)는 `bump_outbox`와 `drive_outbox`를 함께 부른다 (`ui/cr/conversation.rs:334-335`).
- `refresh_slow`의 호출 순서는 의미가 있다: 컴퓨터 첫 목록은 프로브 없이 먼저, 프로브는 끝에 (`bridge.rs:466`, `:531`).
- 설정 필드를 더하면 `#[serde(default)]`를 붙이고 `Default` 구현과 `rename_project_keys`를 점검한다. `format`을 올리면 기존 파일 전체가 버려진다 (`prefs.rs:122-125`).
- 서버 모양이 바뀌면 `server.rs` 타입이 `ember/server/src/{accounts,computers}/api.rs`, `api/ide.rs` 응답과 맞는지 함께 확인한다.
- `terminal_screen.rs`는 `terminal_stream.rs`에 `#[path]`로 포함되므로 `lib.rs`에 모듈 선언을 더하지 않는다.
- 토큰 헤더 로직이 `ServerApi`, `terminal_stream::stream`, 에디터 연결에 따로 있어 하나를 고치면 나머지를 확인한다. `terminal_stream::ClientError`와 `ServerError`는 별개 타입이다.
- `prefs.rs`, `model.rs`, `ide.rs`, `editor_host.rs`가 `crate::ui::*` 타입에 의존해 `app-core`와 `app-ui`가 순환한다. 옮길 때 함께 본다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 문서 불일치 | 중간 | `ember/app/README.md:36-37` | README는 dioxus-compose를 `branch = "develop"`로 쓴다고 하나 `Cargo.toml`은 `tag v0.0.6`과 `rev`로 고정한다 | README 갱신 |
| 거대 파일 | 중간 | `ember/app/src/demo.rs` (3,025줄) | 데이터, 상태 기계, 가짜 git, 테스트 59개가 한 파일. 프로덕션 코드가 데모 분기를 가진다 | `demo/` 하위 모듈로 분리 |
| 순환 의존 | 중간 | `prefs.rs`, `model.rs`, `ide.rs`, `editor_host.rs` | 하위 계층이 UI 타입 (`ThemePref`, `ProjectPanes`, `CharStyle`, `Keymap`, `EditorTarget`, `FileDiff`)에 의존 | 공용 타입을 UI 밖으로 이동 |
| 죽은 경로 | 중간 | `bridge.rs:42-87`, `use_bridge`(`:104`), `services.rs:236` `run`, `Services.live` | Dioxus 루트 `ui::app`이 호출되지 않아 `Live`, `use_bridge`, `live` 분기가 기본 실행에서 동작하지 않는다. `run`의 이 모듈 밖 호출은 확인하지 못했다 | 옛 UI 정리 때 함께 제거 [확인 필요] |
| 오류 은닉 | 중간 | `bridge.rs:468-537` | 계정, 사용량, 에이전트, 컴퓨터 새로고침 실패가 `tracing::debug!`로만 남고 UI는 모른다. `chatgpt_accounts`는 실패를 빈 목록으로 삼킨다 (`:484`). 기본 로그 수준 `warn`에서는 보이지 않는다 | 연결 배너 등으로 표면화 |
| 보안 | 낮음 | `terminal_stream.rs:774`, `:812` (TODO #333) | WebSocket이 평문 `ws`이고 토큰도 평문이다 (루프백이 아닌 호스트는 `EMBER_TOKEN_HOSTS`로 허용 가능) | TLS 지원 (#333) |
| 미완 기능 | 중간 | `terminal_stream.rs:724` (TODO #334), `:827` (TODO #336) | PTY 크기가 80x24로 고정, 재연결과 프로토콜 오류 표시 없음 (파싱 못한 프레임은 로그만) | 이슈대로 구현 |
| 중복 | 낮음 | `terminal_stream.rs:34`, `server.rs:523` | `encode_segment`와 `seg`가 같은 퍼센트 인코딩을 따로 가진다. `start`와 `start_view`의 `Shared` 생성도 같은 코드 | 공용 함수로 합침 |
| 하드코딩 | 낮음 | `editor_host.rs:219`, `lib.rs:121-129` | `app_language = "ko"` 고정, 에디터 창 크기 1280x820 고정, 창 제목 `Box::leak` | 설정화 또는 주석으로 의도 명시 |
| TODO | 낮음 | `ide.rs:109`, `:151`, `lib.rs:132`, `prefs.rs:54`, `server.rs:9`, `terminal_stream.rs` 4개 | Rust 소스 TODO 9개 (`dioxus-compose#152`, `#161`, `ember-client` 이관, 서버 캐릭터 스타일, `#333`, `#334`, `#336`) | 추적 |
| 시그니처 | 낮음 | `services.rs:264` `save_prefs(_prefs)` | 인자를 무시하고 `ui.prefs`를 다시 읽는다. 인자 있는 시그니처가 오해를 부른다 | 인자 제거 |
| 종료 | 중간 | `lib.rs:64-68`, `:101-102` | 콘솔 없는 Windows 빌드에서 `eprintln!` 후 종료하면 사용자는 아무것도 보지 못한다 [추정] | 대화 상자나 로그 파일 |
| 테스트 | 낮음 | `services.rs`, `main.rs` | 직접 단위 테스트 없음 (`services.rs`는 테스트 보조만). 나머지는 `ember/app/tests/`와 UI 테스트가 다룬다 | |
