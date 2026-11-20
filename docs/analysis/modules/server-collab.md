# 모듈: server-collab

- 경로: `ember/server/src/a2a/`, `ember/server/src/channels/`, `ember/server/src/guest_door.rs`, `ember/server/src/guest_door/` (`join.html`, `join.js`, `.gitattributes`), `ember/server/src/members.rs`
- 규모: 파일 22개 / 약 10,631줄 (테스트 포함, `docs/analysis/_raw/modules.md:321`)
- 레이어: 비즈니스 로직 (HTTP 라우트 포함)
- 한 줄 책임: 에이전트 세션 사이 메시징(A2A), 팀, 터미널 도구, 채널(그룹 대화, 피드, 초대, 게스트, 허용), 게스트 문(별도 리스너), 팀원 정의(하네스, 계정, 모델 프록시)를 담당한다.
- 의존하는 모듈: [server-core](server-core.md) (`session.rs`, `store.rs`, `events.rs`, `auth.rs`), [server-agents](server-agents.md) (`AgentKind`, `McpServer`, `StartRequest`, codex·antigravity 프록시 상수), [server-computers](server-computers.md) (`computers::LOCAL`), [server-accounts](server-accounts.md) (`schedules::HEADER_TAG`, `schedules/timing.rs`), [server-enrol](server-enrol.md) (`door/` 공용 문 코드)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs`, `store.rs` 마이그레이션, `session.rs` push 타입, `bin/ember-a2a.rs`), [server-accounts](server-accounts.md) (`schedules/api.rs`가 런타임 토큰 인증에 `A2a` 사용), [server-enrol](server-enrol.md) (`door/limits.rs`가 `guest_door` 상수를, `computers/enrol.rs`가 `channels::invites`를 import), [client](client.md) (`ember/client/src/wire.rs:453` 이하가 같은 JSON 모양을 다시 정의)

이 문서는 두 개로 나뉜다. 이 문서는 개요, 공개 인터페이스, `a2a/` 전체를 다룬다. `channels/`, 게스트 문, `members.rs`, 수정 시 주의점 후반은 [server-collab-2.md](server-collab-2.md)에 있다.

## 한눈에 보기

| 개념 | 핵심 파일 | 저장소 | SPEC |
|---|---|---|---|
| 세션 간 메시지 | `a2a/mod.rs`, `a2a/store.rs`, `a2a/api.rs` | `a2a_*` 테이블 (별도 연결, 같은 `ember.db`) | FR-T2 ~ FR-T6 |
| 에이전트 측 CLI `ember-a2a` | `a2a/client.rs`, `ember/server/src/bin/ember-a2a.rs` | 없음 (HTTP 클라이언트) | FR-T2 |
| MCP 서버 `ember-channels` (`channel_post` 도구 하나) | `a2a/mcp.rs` | 없음 | FR-T12 |
| 팀(리더, 팀원, 작업, 메일) | `a2a/team.rs` | `teams`, `team_members`, `team_tasks`, `team_mail` (메인 `Store`) | FR-T7 |
| 터미널 도구(읽기, 입력, 인터럽트) | `a2a/terminal.rs` | `a2a_terminal_grants` | FR-T9 |
| 세션 작성기 멘션 `@@` | `a2a/mention.rs` | `a2a_messages` | FR-T6 |
| 채널 메시지를 에이전트에 전달 | `a2a/channel.rs` | `a2a_messages` (origin 열) | FR-T12, FR-T13, FR-T17 |
| 채널, 피드, 읽음 커서 | `channels/mod.rs`, `channels/feed.rs`, `channels/api.rs` | `channels`, `channel_agents`, `channel_messages`, `channel_reads` | FR-T10, FR-T11, FR-L12 |
| 채널 멘션 `@` | `channels/mention.rs` | `channel_messages.mentions` | FR-T12, FR-T13 |
| 초대, 게스트, 허용 | `channels/invites.rs`, `channels/allowance.rs`, `channels/guest.rs` | `channel_invites`, `channel_guests` | FR-T14, FR-T15, FR-T17 |
| 채널별 JSONL | `channels/jsonl.rs` | `<data dir>/channels/<id>.jsonl` | FR-T16 |
| 게스트 문 리스너, `/join` 페이지 | `guest_door.rs`, `guest_door/join.*` | 없음 | FR-T14 |
| 팀원 정의, 모델 프록시 | `members.rs` | `session_proxy` | FR-A9, FR-U6 |

### 인증 경계 세 가지

| 호출자 | 자격 | 어디서 검사 | 해당 라우트 |
|---|---|---|---|
| 소유자(UI, 클라이언트) | 서버 토큰 `Authorization: Bearer <server-token>` | `auth::protect` (`ember/server/src/auth.rs:176`), 로컬 TCP 라우터에만 적용. 트랜스포트로 서비스되는 라우터는 기기 게이트가 대신한다 (`auth.rs:5-7`) | `/api/channels/*` (아래 예외 제외), `/api/a2a/settings`, `/api/sessions/{id}/a2a`, `/api/sessions/{id}/mentions`, `/api/sessions/{id}/team`, `/api/sessions/{id}/terminal-grants`, `/api/teams/*`, `/api/guest-door` |
| 에이전트 프로세스 | 런타임 토큰 `EMBER_RUNTIME_TOKEN` | `auth.rs:212`가 `/api/a2a/*`(단 `/api/a2a/settings` 제외)와 `POST /api/channels/<id>/post`(`auth.rs:191`)를 서버 토큰에서 면제하고, 핸들러가 `a2a::api::caller` (`a2a/api.rs:114`)로 직접 검사 | `/api/a2a/*`, `POST /api/channels/{id}/post` |
| 게스트 | 게스트 자격 `dpg_...` | 게스트 라우터의 `require_guest` (`channels/guest.rs:292`). 이 라우터는 게스트 문 리스너에서만 서비스된다 (`main.rs:429-441`) | `/api/guest/*`, `GET /join` |

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `A2a` | 구조체 | `a2a/mod.rs:163` | A2A 서비스 본체. `main.rs:285`에서 하나 만들고 라우터들에 `Arc`로 넘긴다 |
| `A2a::new(sessions, store, config)` | 함수(pub) | `a2a/mod.rs:374` | 생성. `main.rs:285` |
| `A2a::install()` | 함수(pub) | `a2a/mod.rs:398` | 세션 매니저에 훅 5개 등록, 턴 감시 태스크와 최초 flush 시작. `main.rs:398` (리스너 bind 뒤) |
| `A2a::set_computer_setter` | 함수(pub) | `a2a/mod.rs:391` | 팀원을 다른 컴퓨터에 놓는 콜백. `main.rs:289` |
| `A2a::authenticate(token)` | 함수(pub) | `a2a/mod.rs:697` | 런타임 토큰 → 세션 id. `schedules/api.rs:156`, `a2a/api.rs:122` |
| `A2aConfig`, `A2aConfig::new`, `cli_next_to_current_exe` | 구조체/함수 | `a2a/mod.rs:83`, `:95`, `:105` | `main.rs:278-279` |
| `A2aStore::open` | 함수(pub) | `a2a/store.rs:133` | `main.rs:285` |
| `a2a::api::router(a2a)` | 함수(pub) | `a2a/api.rs:59` | `main.rs:458` |
| `a2a::api::caller` | 함수(pub(crate)) | `a2a/api.rs:114` | 런타임 토큰 헤더 검사. `channels/api.rs:292` |
| `a2a::client::run(args)` | 함수(pub) | `a2a/client.rs:454` | `ember-a2a` 진입점. `bin/ember-a2a.rs:5` |
| `a2a::team::MIGRATION` | 상수 | `a2a/team.rs:41` | `store.rs:147` |
| `a2a::team::TeamView` | 구조체 | `a2a/team.rs:228` | `session.rs:40` `Push::TeamUpdated` |
| `A2a::send_from_person`, `send_from_guest`, `check_channel_post` | 함수(pub) | `a2a/channel.rs:175`, `:192`, `:234` | `channels/api.rs:304`, `channels/guest.rs:528`, `channels/api.rs:300` |
| `a2a::channel::sanitize_label` | 함수(pub) | `a2a/channel.rs:39` | `channels/guest.rs:66` |
| `channels::MIGRATION`, `READS_MIGRATION`, `MENTIONS_MIGRATION`, `invites::MIGRATION` | 상수 | `channels/mod.rs:29`, `:55`, `:66`, `channels/invites.rs:16` | `store.rs:153-157` |
| `channels::Message` | 구조체 | `channels/mod.rs:121` | `session.rs:53` `Push::ChannelMessage` |
| `channels::api::router_with_a2a_door` | 함수(pub) | `channels/api.rs:123` | `main.rs:457` |
| `channels::guest::guest_router_with_a2a` | 함수(pub) | `channels/guest.rs:242` | `main.rs:431` |
| `channels::jsonl::JsonlLog::new(...).recover(&store)` | 함수(pub) | `channels/jsonl.rs:161`, `:236` | `main.rs:119` (시작 시 동기 실행) |
| `channels::invites::{new_secret, is_forbidden_name_char}` | 함수(pub) | `channels/invites.rs:73`, `:87` | `computers/enrol.rs:84` |
| `GuestDoor` (`from_env`, `bind`, `is_remote`, `wrap_limited`, `limits`, `serve`) | 구조체/함수 | `guest_door.rs:149`, `:161`, `:211`, `:258`, `:194`, `:199`, `:216` | `main.rs:256`, `:362-377`, `:429-441`, `:534` |
| `guest_door::{ACCEPT_PATH, ACCEPT_PER_*, GLOBAL_*, MAX_IN_FLIGHT, MAX_TRACKED_ADDRS, ...}` | 상수 | `guest_door.rs:59-78` | `door/limits.rs:17-18` (역방향 의존, 순환) |
| `members::install(&sessions)` | 함수(pub) | `members.rs:204` | `main.rs:210` |
| `members::MIGRATION` | 상수 | `members.rs:24` | `store.rs:151` |

## 파일별 요약 (a2a)

### `ember/server/src/a2a/mod.rs` (약 1,758줄, 그중 테스트 약 650줄)
- **목적:** A2A 서비스 본체. 에이전트 프로세스에 자격과 안내문을 넣고, 메시지를 저장한 뒤 대상 세션에 사용자 메시지처럼 넣으며, 루프 방지와 on/off 스위치를 적용한다 (`a2a/mod.rs:1-13`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CLI_NAME` = `"ember-a2a"` | 상수 | 40 | CLI 이름. 안내문과 오류 문장에 들어간다 |
  | `CHANNEL_MCP_SERVER` = `"ember-channels"`, `CHANNEL_POST_TOOL` = `"mcp__ember-channels__channel_post"` | 상수 | 43, 47 | MCP 서버 이름과 Claude Code 쪽 도구 이름. 테스트가 세 상수가 어긋나지 않는지 본다 (`:1160`) |
  | `CHANNEL_POSTS_PER_MINUTE` = 6, `CHANNEL_MENTION_WINDOW` = 30분 | 상수 | 53, 56 | 에이전트의 채널 답글 제한 |
  | `HEADER_TAG` = `"[ember a2a]"` | 상수 | 58 | 배달된 메시지 첫 줄 표지 |
  | `Limits` (기본 600초 창, 세션당 20, 쌍당 10) | 구조체 | 64, 72 | 루프 방지 (FR-T5) |
  | `A2aError` | enum | 113 | `Unauthorized`, `Disabled`, `RateLimited`, `NotFound`, `BadRequest`, `Forbidden`, `Other`. HTTP 매핑은 `a2a/api.rs:93` |
  | `ComputerSetter` | 타입 | 133 | `(session, computer)` → 이동 future |
  | `Target`, `Delivery`, `Receipt` | 구조체/enum | 138, 148, 157 | 대상 목록 항목, `delivered`/`queued`, 송신 영수증 |
  | `A2a` | 구조체 | 163 | 잠금 여러 개와 메모리 상태 (`awaiting`, `last_notice`, `channel_posts`, `channel_fallback`) |
  | `ClaudeConfigSources::from_env` | 함수(pub) | 204 | `HOME`, `CLAUDE_CONFIG_DIR`, 관리형 MCP 파일 두 경로 |
  | `NameCheck`, `channel_server_name_taken` | enum/함수(pub) | 236, 304 | 사용자 Claude Code 설정에 `ember-channels`가 이미 있는지 검사. 읽을 수 없으면 `Unsure` (fail closed) |
  | `read_config_json` | 함수 | 257 | `O_NONBLOCK`으로 열고 `fstat`으로 일반 파일, 4 MiB 이하만 읽는다 |
  | `A2a::install` | 함수(pub) | 398 | start 훅(`runtime_env`), instructions 훅, start-config 훅(`channel_tool_config`), end 훅, user-message 훅(`deliver_mentions`) 등록 후 `watch_turns`와 `flush_all` 시작 |
  | `channel_reply_by_tool` / `channel_reply_eligible` | 함수 | 460, 466 | Claude Code이고 CLI가 있고 로컬 컴퓨터일 때만 MCP 도구로 답하게 한다 |
  | `channel_tool_config` | 함수 | 498 | `StartRequest`에 `ember-channels` MCP 서버와 허용 규칙 하나를 넣는다. 충돌이면 넣지 않고 안내문을 CLI 문장으로 되돌린다 |
  | `runtime_env` | 함수 | 562 | 프로세스 시작마다 새 토큰 발급. `EMBER_URL`, `EMBER_SESSION_ID`, `EMBER_RUNTIME_TOKEN`, `EMBER_A2A_BIN`, `PATH` |
  | `instructions_with` | 함수 | 598 | 에이전트에게 주는 영어 안내문 (메시징, 터미널, 팀, 스케줄, 채널) |
  | `check_caller` | 함수 | 732 | 서버 전체 스위치와 호출 세션 스위치 |
  | `team_scope_denial` | 함수 | 748 | 활성 팀원은 자기 팀과만 주고받는다 |
  | `targets`, `send`, `deliver` | 함수(pub) | 776, 800, 853 | 대상 목록, 송신(저장 후 배달 시도), 배달 결과 판정 |
  | `check_limits`, `notify_rejection` | 함수 | 873, 916 | 루프 방지와 양쪽 세션 알림(쌍당 60초에 한 번) |
  | `flush`, `settle_awaiting`, `flush_all` | 함수 | 950, 983, 1010 | 대상이 바쁘지 않으면 대기 메시지를 묶어 `Sessions::send`로 넣고 `delivered_at` 기록 |
  | `render` | 함수 | 1022 | 메시지 묶음을 사용자 메시지 텍스트로 만든다. 세션발, 사람(채널)발, 게스트발 세 형식 |
  | `watch_turns` | 함수 | 1082 | `TurnEnded` 푸시마다 해당 대상 flush. 지연(`Lagged`)이면 전체 flush |
- **입력 → 출력:** 송신 요청(발신 세션, 대상, 텍스트) → `a2a_messages` 행 → 대상 세션의 사용자 메시지. 세션 시작 → 환경 변수와 안내문, MCP 서버 설정.
- **의존:** `ember/server/src/session.rs` (`Sessions`, `Push`), `ember/server/src/store.rs` (`SessionRecord`, `session_computer` 테이블 직접 조회 `a2a/mod.rs:483`), `ember/server/src/agents/` (`AgentKind`, `McpServer`, `StartRequest`), `ember/server/src/computers/` (`LOCAL`), `ember/server/src/schedules/` (`HEADER_TAG`).
- **사용처:** `ember/server/src/main.rs:11`, `:285`, `:289`, `:398`; `ember/server/src/schedules/api.rs:48`, `:156`; `ember/server/src/channels/api.rs:96`, `channels/guest.rs:207`.
- **부수효과:** DB 쓰기(토큰, 메시지, 배달 시각), 세션 이벤트 기록(`AgentEvent::Notice`), 에이전트 프로세스 깨우기(`Sessions::send`), 파일 읽기(사용자 Claude Code 설정, `a2a/mod.rs:257`), tokio 태스크 생성(`:434-436`).
- **주의점:**
  - `send`는 저장을 먼저 하고 배달은 그 뒤에 시도한다 (`a2a/mod.rs:845-849`). 배달 실패는 로그만 남기고 대기열에 남는다 (`:1004-1008`).
  - 중복 배달 방지는 `awaiting` 맵이 맡는다. `flush` 직전에 대상의 `last_seq`를 넣고 (`:968-971`), 그 뒤 `TurnEnded`가 보여야 다음 배달을 한다 (`:983-1002`). 이 순서를 바꾸면 한 턴에 두 번 들어갈 수 있다.
  - `channel_fallback`은 메모리에만 있다. 재시작 뒤에는 비어서 살아남은 에이전트가 다시 "도구로 답하라"는 안내를 받는다 (`:180-188`).
  - `channel_tool_config`는 instructions 훅이 먼저 만든 안내문을 문자열 치환으로 고친다 (`:531-533`, `:543-546`). 안내문 문구를 바꾸면 치환이 둘 다 같은 함수에서 나오므로 함께 맞는다. 다만 훅 실행 순서(instructions → start-config)에 의존한다 [추정: 순서는 `session.rs`가 정한다, 확인 필요].
  - 사람의 채널 메시지와 게스트 메시지는 `from_session`이 `channel:<id>`이다 (`a2a/store.rs:57`, `:240`). 루프 방지 카운트에서 세션 id와 섞이지 않는다.
- **테스트:** 33개 (`channel_tool_tests`, `a2a/mod.rs:1109`). FR-T12 MCP 등록 훅, 이름 충돌 검사(fail closed, FIFO, 심볼릭 링크), 안내문 문구, 사람·게스트 메시지 꼬리말을 검증한다.

### `ember/server/src/a2a/store.rs` (약 527줄)
- **목적:** A2A 전용 SQLite 테이블. 메인 `Store`와 같은 `ember.db` 파일이지만 자기 연결을 따로 연다 (`a2a/store.rs:1-6`, `:133`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SCHEMA` | 상수 | 16 | `a2a_tokens`, `a2a_messages`, `a2a_terminal_grants`, `a2a_switches` (`CREATE TABLE IF NOT EXISTS`) |
  | `ADDED_COLUMNS`, `migrate` | 상수/함수 | 53, 63 | `origin_channel`, `origin_label`, `origin_guest_until`를 `ALTER TABLE`로 추가. 다른 연결과의 경합에서 "duplicate column"은 무시 |
  | `CHANNEL_SENDER_PREFIX` = `"channel:"` | 상수 | 57 | 사람·게스트 메시지의 `from_session` 접두사 |
  | `A2aMessage` | 구조체 | 107 | 메시지 행. origin 필드는 없으면 직렬화하지 않는다 |
  | `A2aStore::open` / `open_in_memory` | 함수(pub) | 133, 143 | busy_timeout 5초, WAL |
  | `issue_token` | 함수(pub) | 154 | `ember_rt_` + UUID 두 개. SHA-256 해시만 저장, 세션당 한 행(재발급 시 교체) |
  | `session_for_token` | 함수(pub) | 169 | 해시로 세션 조회 |
  | `insert_message`, `insert_channel_message`, `insert_guest_message` | 함수(pub) | 182, 207, 219 | 세션발, 사람발, 게스트발 |
  | `pending_for`, `sessions_with_pending`, `mark_delivered` | 함수(pub) | 289, 300, 308 | 대기열 |
  | `sent_since`, `pair_since`, `channel_mention_since` | 함수(pub) | 323, 343, 332 | 슬라이딩 창 카운트. 메시지 행이 곧 이력이므로 재시작 뒤에도 유지 |
  | `global_enabled`, `session_enabled` (기본 on) | 함수(pub) | 376, 385 | `a2a_switches`의 `global`, `session:<id>` |
  | `terminal_granted`, `set_terminal_grant`, `terminal_grants` | 함수(pub) | 394, 409, 426 | FR-T9 허가 |
- **입력 → 출력:** 행 단위 CRUD.
- **의존:** `rusqlite`, `sha2`, `uuid`.
- **사용처:** `a2a/mod.rs` 전반, `a2a/team.rs:1143`, `:1206`, `a2a/terminal.rs:62`, `:72`, `a2a/api.rs:378`, `main.rs:285`.
- **부수효과:** DB 쓰기.
- **주의점:**
  - 토큰 행과 메시지 행을 지우는 코드가 없다 (`a2a_tokens`, `a2a_messages`를 저장소 전체에서 grep, 삭제문 없음). 세션이 끝나도 토큰은 유효하고 메시지 표는 계속 자란다.
  - 메인 `Store`의 마이그레이션 목록(`store.rs:147-157`)과 달리 이 파일은 `IF NOT EXISTS` + `ALTER` 방식을 쓴다. 두 방식이 한 DB 파일에 섞여 있다.
- **테스트:** 4개 (`a2a/store.rs:449`). 토큰 해시 저장과 교체, 대기열과 카운트, origin 열 마이그레이션, 스위치 기본값.

### `ember/server/src/a2a/api.rs` (약 394줄)
- **목적:** A2A HTTP 라우트 23개. 상단 주석이 경로와 본문 형식을 표로 적는다 (`a2a/api.rs:1-44`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `router(a2a)` | 함수(pub) | 59 | 라우트 등록 |
  | `impl IntoResponse for A2aError` | impl | 93 | `{error, code}`. 401/403/429/404/400/403/500 |
  | `caller(a2a, headers)` | 함수(pub(crate)) | 114 | `Authorization: Bearer <runtime token>` → 세션 id |
  | `targets`, `send`, `message` | 핸들러 | 125, 137, 147 | 에이전트용. `message`는 송수신자만 볼 수 있다 (`:154`) |
  | `get_settings`/`put_settings`, `get_session_switch`/`put_session_switch` | 핸들러 | 164-190 | 사용자용 스위치. 인증 없이 핸들러에 들어온다 (서버 토큰은 바깥 `auth::protect`가 본다) |
  | 팀 핸들러 `my_team` ~ `user_end_member` | 핸들러 | 194-310 | 에이전트용(`caller` 사용)과 사용자용(`/api/sessions/{id}/team`, `/api/teams/*`) |
  | `mentions` | 핸들러 | 321 | 사용자 작성기 자동완성 후보 |
  | `terminal_read`/`terminal_text`/`terminal_interrupt`, `list_terminal_grants`/`put_terminal_grant` | 핸들러 | 338-394 | FR-T9 |
- **입력 → 출력:** HTTP JSON → `A2a` 메서드 호출 → JSON.
- **의존:** `a2a/mod.rs`, `a2a/team.rs`.
- **사용처:** `main.rs:458`, `channels/api.rs:292` (`caller`).
- **부수효과:** 없음(위임).
- **주의점:**
  - 이 라우터는 사용자 라우트와 에이전트 라우트를 한 `Router`에 섞는다. 어떤 것이 런타임 토큰으로 열리는지는 경로 접두사 `/api/a2a/`만으로 `auth.rs:212`가 정한다. 사용자 라우트를 `/api/a2a/` 아래에 새로 만들면 서버 토큰 검사가 빠진다 (`/api/a2a/settings`만 예외로 막혀 있다).
  - `update_task`는 `#3`처럼 `#`을 허용한다 (`:240-243`).
- **테스트:** 없음 (통합 테스트는 `ember/server/tests/a2a_flow.rs` 등).

### `ember/server/src/a2a/team.rs` (약 1,352줄)
- **목적:** 팀(FR-T7). 리더가 팀원 세션을 만들고, 팀이 작업 목록과 메일함을 공유한다. 규칙은 파일 머리 주석에 정리돼 있다 (`a2a/team.rs:1-23`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MIGRATION` | 상수 | 41 | `teams`, `team_members`(PK `session_id`: 세션은 평생 한 팀), `team_tasks`, `team_mail` |
  | `MAX_TEAMMATES` = 8, `LEADER_NAME` = `"lead"`, `MAIL_PAGE` = 20, `MAIL_PAGE_MAX` = 200, `NAME_MAX` = 32 | 상수 | 83-89 | |
  | `Role`, `TaskStatus` | enum | 93, 117 | `TaskStatus::parse`는 `todo`, `doing`, `canceled`도 받는다 (`:137`) |
  | `MemberRow`, `TeamRow`, `Member`, `Task`, `Mail`, `TeamView` | 구조체 | 151, 172, 182, 194, 212, 228 | 행과 뷰 |
  | `SpawnRequest` | 구조체 | 240 | `name`, `agent`, `account`, `pipeline`, `proxy`, `computer`, `title`, `prompt` |
  | `impl Store` 팀 저장 함수 | 함수(pub) | 352-624 | `team_member`, `team_row`, `team_members`, `active_team_members`, `create_team`, `add_team_member`, `end_team_member`, `team_joins_since`, `insert_team_task`(번호는 트랜잭션 안 `MAX+1`, `:483`), `update_team_task`, `insert_team_mail`, `team_mail` |
  | `valid_name` | 함수 | 626 | 1~32자 ASCII 영숫자, `-`, `_`. `lead`, `all` 금지 |
  | `team_view`, `team_of`, `publish_team` | 함수 | 671, 706, 714 | 뷰 생성, `Push::TeamUpdated` 발행 |
  | `membership`, `require_leader`, `resolve_member` | 함수 | 725, 739, 752 | 이름(대소문자 무시), 세션 id, 4자 이상 유일 접두사 |
  | `spawn_teammate` | 함수(pub) | 780 | 아래 흐름 참고 |
  | `end_teammate`, `end_teammate_by_user`, `end_member` | 함수 | 927, 937, 953 | 종료 표시 → interrupt → release → `session_ended` → 안내 이벤트 → 발행 |
  | `tasks`, `add_task`, `update_task` | 함수(pub) | 988, 996, 1031 | 팀원은 미배정이거나 자기 것만 고치고 자기에게만 배정한다 |
  | `announce_assignment`, `notify` | 함수 | 1110, 1126 | 루프 방지를 통과하면 A2A로 알림 (best effort) |
  | `send_mail`, `read_mail`, `mail_of` | 함수(pub) | 1146, 1224, 1241 | 수신자별 A2A 메시지로도 넣는다. 루프 방지는 수신자 수만큼 센다 |
  | `teammate_instructions` | 함수(pub(crate)) | 1259 | 활성 팀원에게만 붙는 안내문 |
- **`spawn_teammate` 흐름 (`a2a/team.rs:780-914`):** `check_caller` → 이름·프롬프트 검사 → 호출자가 리더/팀원/전 팀원인지 판정 → 기존 팀이면 인원(8)·이름 중복·생성 속도(`Limits::per_session` 재사용, `:813-822`) 검사 → `members::create_member_session`으로 세션 생성 → 첫 생성이면 `create_team` → `add_team_member`(실패 시 세션 보관) → `computer`가 있으면 `ComputerSetter` 호출(실패 시 종료·보관) → 발행 → 첫 프롬프트를 리더발 A2A 메시지로 저장·배달(루프 방지 미적용, `:899-901`).
- **입력 → 출력:** 에이전트·사용자 요청 → 팀 테이블 변경, 새 세션, A2A 메시지, `Push::TeamUpdated`.
- **의존:** `a2a/mod.rs`, `ember/server/src/members.rs`, `ember/server/src/session.rs`, `ember/server/src/store.rs`, `ember/server/src/computers/`.
- **사용처:** `a2a/api.rs:56`, `a2a/mod.rs:688-694`, `a2a/terminal.rs:77`, `a2a/channel.rs:221`, `store.rs:147`, `session.rs:40`.
- **부수효과:** DB 쓰기, 세션 생성·보관, 에이전트 중단, 컴퓨터 이동, 푸시 발행.
- **주의점:**
  - 세션 생성은 팀 생성보다 먼저다 (`:855`, `:867-870`). `create_team`이 실패하면 만든 세션이 보관되지 않고 남는다 (`add_team_member` 실패만 `archive`, `:871-877`).
  - 에이전트가 보내는 `SpawnRequest.proxy`가 그대로 `MemberDef.proxy`로 간다 (`:840-845`). 보안 영향은 [server-collab-2.md의 members.rs](server-collab-2.md#emberserversrcmembersrs-약-313줄) 참고.
  - `send_mail`은 메일 행을 먼저 넣고 수신자별 A2A 행을 넣는다 (`:1190-1205`). 중간 실패 시 일부만 남을 수 있다.
- **테스트:** 3개 (`a2a/team.rs:1285`). 행 왕복, 팀별 작업 번호와 패치, 메일 가시성과 페이지.

### `ember/server/src/a2a/client.rs` (약 1,080줄)
- **목적:** 에이전트 측 CLI `ember-a2a`. 의존성 없이 TCP 위에 손으로 쓴 HTTP/1.1 클라이언트로 서버 API를 부른다 (`a2a/client.rs:1-5`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `USAGE` | 상수 | 14 | 도움말 전문 |
  | `BAD_BASE_URL` | 상수 | 72 | URL을 에러에 넣지 않는 고정 문장 |
  | `Client::new(base_url, token)` | 함수(pub) | 85 | `http://host[:port][/prefix]`만 허용. userinfo, `\`, `?`, `#`, 잘못된 포트 거부 |
  | `Client::from_env` | 함수(pub) | 138 | `EMBER_URL`, `EMBER_RUNTIME_TOKEN` |
  | `Client::request` | 함수(pub) | 148 | 연결마다 `Connection: close`, 읽기 타임아웃 120초 |
  | API 래퍼 (`targets` ~ `remove_schedule`) | 함수(pub) | 191-273 | 각 라우트 한 줄 |
  | `channel_post_path`, `path_seg` | 함수 | 278, 282 | 경로 조각 퍼센트 인코딩 |
  | `parse_args`, `text_or_stdin` | 함수 | 303, 339 | `-` 또는 빈 텍스트면 stdin |
  | `parse_duration_secs`, `schedule_add_body` | 함수(pub) | 354, 373 | 스케줄 인자 |
  | `parse_response`, `dechunk` | 함수 | 401, 433 | 응답 파싱, chunked 해제 |
  | `run`, `run_inner` | 함수 | 454, 499 | `mcp`는 stdout을 프로토콜에 쓰므로 먼저 분기 (`:456-462`). 종료 코드 0/1/2 |
  | `run_terminal`, `run_team`, `run_task`, `run_channel`, `run_channel_post`, `run_mail`, `run_schedule` | 함수 | 549-870 | 하위 명령 |
  | `format_*` | 함수 | 757-920 | 사람이 읽는 출력 |
- **입력 → 출력:** 명령줄 인자, 환경 변수 → HTTP 요청 → stdout 문장 또는 JSON.
- **의존:** `a2a/mcp.rs` (`mcp` 분기), `ember/server/src/schedules/timing.rs` (`docs/analysis/_raw/imports.tsv`).
- **사용처:** `ember/server/src/bin/ember-a2a.rs:5`, `a2a/mcp.rs:25`.
- **부수효과:** 네트워크(평문 HTTP, 토큰 포함), stdin 읽기, stdout/stderr 출력, 프로세스 종료 코드.
- **주의점:** `team spawn`은 `pipeline`과 `proxy`를 보내지 않는다 (`:600-607`). 서버는 받는다 (`a2a/team.rs:250-254`). 응답 본문 크기 상한이 없다 (`:174-176`).
- **테스트:** 9개 (`a2a/client.rs:921`). URL 파싱과 거부, 인자 파싱, 출력 형식, 스케줄 인자, `channel post` 경로, chunked 응답.

### `ember/server/src/a2a/mcp.rs` (약 948줄, 그중 테스트 약 560줄)
- **목적:** `ember-a2a mcp`. stdio JSON-RPC 2.0 MCP 서버로 도구 `channel_post` 하나만 제공한다. 실제 호출은 `ember-a2a channel post`와 같은 라우트다 (`a2a/mcp.rs:1-19`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SUPPORTED_VERSIONS` | 상수 | 28 | `2025-11-25` 외 3개 |
  | `TOOL_NAME`, `MAX_LINE_BYTES` (1 MiB), `MAX_TEXT_BYTES` (8192), `MAX_CHANNEL_ID` (128) | 상수 | 30-37 | |
  | `PostRefusal`, `ChannelPoster` | 구조체/트레이트 | 45, 56 | 테스트가 가짜 poster를 넣는다 |
  | `refusal_from_failure`, `refusal_from_response` | 함수(pub) | 63, 72 | 서버 에러 본문을 모델에 넘기지 않고 고정 문장만 준다 |
  | `sentence_for_code`, `sentence_for_status` | 함수 | 82, 98 | 코드별, 상태별 고정 문장 |
  | `non_loopback_host` | 함수(pub) | 117 | 루프백이 아니면 경고용 호스트(문자 치환) |
  | `EnvPoster` | 구조체 | 155 | 호출마다 환경 변수를 읽는다 |
  | `run_stdio`, `serve` | 함수(pub) | 172, 188 | 진입점, 프레임 루프 |
  | `read_frame`, `write_frame` | 함수 | 219, 257 | 1 MiB 넘는 줄은 버리고 `-32600` |
  | `handle` | 함수 | 281 | `initialize`, `ping`, `tools/list`, `tools/call`, 나머지 `-32601` |
  | `valid_channel`, `validate_arguments` | 함수 | 359, 366 | 채널 id 문자 집합, `.`만으로 된 id 거부 |
- **입력 → 출력:** stdin 프레임 → stdout 프레임. 도구 호출 → `POST /api/channels/{id}/post`.
- **의존:** `a2a/client.rs` (`Client`, `channel_post_path`).
- **사용처:** `a2a/client.rs:461` (`run_stdio`). 서버는 `a2a/mod.rs:549-555`에서 이 명령을 MCP 서버로 등록한다.
- **부수효과:** 네트워크, stdout 쓰기, stderr 경고 한 줄.
- **주의점:** `MAX_TEXT_BYTES`는 `channels/guest.rs:82`와 같은 값을 따로 정의한다. 서버의 에이전트 라우트(`channels/api.rs:283`)에는 길이 상한이 없으므로 CLI 경로(`ember-a2a channel post`)는 8192바이트보다 긴 글도 보낼 수 있다.
- **테스트:** 31개 (`a2a/mcp.rs:391`). 프레임 처리, 프로토콜 버전, 인자 검증, 거부 문장이 서버 텍스트를 흘리지 않는지, 비루프백 경고.

### 작은 파일 (a2a)

| 파일 | 줄 | 요약 |
|---|---|---|
| `ember/server/src/a2a/mention.rs` | 252 | 세션 작성기 멘션 `@@<id>`, `@@<title>`, `@@"<title>"` (`:3-4`). `parse_mentions` (`:31`), `resolve` (id → 4자 이상 유일 접두사 → 유일 제목, `:74`), `mention_candidates` (`:111`, `CANDIDATES` 20/최대 200), `deliver_mentions` (`:130`, 루프 방지 미적용, 결과는 원래 세션에 notice). 원문 전체를 복사해 보낸다 (`:168-171`). 테스트 2개: 파싱, 해석 |
| `ember/server/src/a2a/channel.rs` | 265 | 채널 메시지의 A2A 쪽. `sanitize_label` (`:39`, 제어·서식 문자 제거, 공백 정리, 64자), `neutralize_guest_text` (`:65`, 게스트 블록 표지 위조 제거, 최대 1000회 재검사), `find_marker` (`:81`, 공백 무시, 전각 접기), `reply_hint` (`:115`), `guest_message_text(_for)` (`:130`, `:143`, UNTRUSTED 블록), `send_from_person`/`send_from_guest` (`:175`, `:192`, 루프 방지 미적용), `check_channel_target` (`:206`), `check_channel_post` (`:234`, 멤버 → 30분 안 멘션 → 분당 6회). 세션 자신의 A2A 스위치는 보지 않는다 (`:232-233`). 테스트 없음 |
| `ember/server/src/a2a/terminal.rs` | 154 | FR-T9. 기본 거부, 사용자 허가 또는 같은 팀 활성 리더만 (`check_terminal`, `:66`). `terminal_read` (`:97`, 기본 50줄, 최대 1000, 최대 30초 대기, 25ms 폴링), `terminal_send_text` (`:131`), `terminal_interrupt` (`:145`). 사용할 때마다 대상 기록에 `[terminal] ...` notice (`:86`). 테스트 없음 |

## 이 모듈을 수정할 때 주의할 점 (a2a 부분)

- **라우트 인증은 경로 모양이 정한다.** `/api/a2a/` 아래 새 라우트는 자동으로 서버 토큰 면제다 (`auth.rs:212`). 사용자 전용이면 `/api/a2a/` 밖에 두거나 `auth.rs`의 예외 목록을 고친다. `/api/channels/` 아래는 `<id>/post` 하나만 면제다 (`auth.rs:191`).
- **훅 순서 의존.** `A2a::install`은 리스너 bind 뒤에 불러야 한다 (`main.rs:397-398`, 깨운 에이전트가 API에 닿아야 한다). `subscribe`를 최초 `flush_all`보다 먼저 한다 (`a2a/mod.rs:432-436`).
- **두 저장소, 한 파일.** `a2a_*`는 `A2aStore` 연결(`a2a/store.rs:133`), `team_*`·`channel_*`·`session_proxy`는 메인 `Store` 연결이다. 한 트랜잭션으로 묶을 수 없다. 예: 팀 메일 행(메인)과 A2A 메시지 행(A2A)은 따로 커밋된다 (`a2a/team.rs:1190-1205`).
- **같은 값이 두 번 정의된 곳.** 메시지 최대 8192바이트 (`a2a/mcp.rs:35`, `channels/guest.rs:82`, `guest_door/join.js:10`). 채널 id 최대 128 (`a2a/mcp.rs:37`, `channels/jsonl.rs:148`). 30분·분당 6회는 상수(`a2a/mod.rs:53`, `:56`)와 별개로 `a2a/mcp.rs:84`, `:321`, `a2a/client.rs:62`의 문장 안에 숫자로 다시 적혀 있다.
- **클라이언트 와이어 정의.** `TeamView`, `Mail`, `Task`, `Target` 모양은 `ember/client/src/wire.rs:453` 이하에서 따로 정의된다 [확인 필요: 필드 일치 여부는 [client.md](client.md) 참고]. 필드를 바꾸면 클라이언트도 바꾼다.
