# 모듈: server-core

- 경로: `ember/server/` 중 다른 server 모듈에 속하지 않는 파일 (`ember/server/Cargo.toml`, `ember/server/scripts/`, `ember/server/src/{lib,main,auth,events,fork,store,session,session_shim}.rs`, `ember/server/src/projects/`, `ember/server/src/bin/`) ([modules.md](../_raw/modules.md) "server-core")
- 규모: 파일 16개 / 약 5,871줄
- 레이어: 비즈니스 로직 (세션 수명 주기, SQLite 저장소, 인증 미들웨어)
- 한 줄 책임: 세션을 만들고 에이전트 프로세스를 띄우고(또는 shim에 다시 붙고), 모든 이벤트를 SQLite에 먼저 저장한 뒤 클라이언트에 푸시하며, 로컬 리스너를 토큰과 Host/Origin 검사로 지킨다.
- 의존하는 모듈: [server-agents](server-agents.md) (`AgentAdapter`, `proc`), [server-api](server-api.md) (`api::origin`), [server-accounts](server-accounts.md), [server-computers](server-computers.md), [server-collab](server-collab.md), [server-enrol](server-enrol.md) (마이그레이션 상수와 `main.rs` 조립)
- 이 모듈을 쓰는 모듈: 거의 모든 server 모듈. `store.rs` 팬인 41, `events.rs` 22, `session.rs` 21 (`docs/analysis/_raw/fan.tsv`)

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Store` | struct | `ember/server/src/store.rs:81` | SQLite 연결 하나를 `Mutex`로 감싼 저장소. 다른 모듈은 `impl Store` 블록을 자기 파일에 추가해 테이블을 다룬다 (`projects/mod.rs:285`, `fork.rs:107` 등) |
| `Store::conn()` | 함수(pub(crate)) | `ember/server/src/store.rs:230` | 자기 테이블을 가진 모듈이 연결을 직접 잡는 통로 |
| `Store::append` | 함수(pub) | `ember/server/src/store.rs:344` | 이벤트 저장 + 상태 전이 + `native_id` 갱신을 한 트랜잭션에 |
| `Store::events_after` | 함수(pub) | `ember/server/src/store.rs:374` | `seq > after` 이벤트, 오래된 순 |
| `SessionRecord`, `StoredEvent`, `SessionPatch`, `SearchHit` | struct | `ember/server/src/store.rs:18`, `:74`, `:44`, `:55` | 세션 행, 저장된 이벤트, 메타 패치, 검색 결과 |
| `now_ms()` | 함수(pub) | `ember/server/src/store.rs:191` | Unix ms. server 전역에서 시간 기록에 쓴다 |
| `AgentEvent` | enum | `ember/server/src/events.rs:12` | 모든 어댑터가 내보내는 정규화 이벤트 (`kind` 태그, snake_case) |
| `SessionStatus` / `SessionStatus::after` | enum / 함수 | `ember/server/src/events.rs:244`, `:254` | 세션 상태와 전이 규칙 |
| `approval_policy` | 함수(pub) | `ember/server/src/events.rs:132` | 승인 자동 처리 정책 표 하나 |
| `Sessions` | struct | `ember/server/src/session.rs:225` | 세션 수명 주기 관리자. 훅 등록, 전송, 승인, 질문, 유휴 정리, shim 재접속 |
| `Push` | enum | `ember/server/src/session.rs:30` | `/api/push` WebSocket으로 나가는 메시지 (`type` 태그) |
| `SessionError`, `QuestionError` | enum | `ember/server/src/session.rs:57`, `:71` | API가 HTTP 코드로 바꾸는 에러 |
| `auth::protect`, `ServerAuth`, `token_eq`, `agent_cdp_nonce` | 함수/struct | `ember/server/src/auth.rs:176`, `:134`, `:102`, `:112` | 로컬 리스너 보호 (FR-S9, FR-S10) |
| `session_shim::{spawn_shim, attach, attach_or_resume, reattach_all, scan, apply_env, ENV_CLEAR}` | 함수/상수 | `ember/server/src/session_shim.rs:579`, `:536`, `:660`, `:672`, `:635`, `:75`, `:71` | 세션별 shim 프로세스 (FR-S8) |
| `fork::{ForkError, plan_native_fork, completed_turns, transcript}` | enum/함수 | `ember/server/src/fork.rs:51`, `:64`, `:82`, `:91` | 세션 포크 (FR-S5) |
| `projects::{Project, ProjectPatch, ProjectError, DEFAULT_PROJECT_NAME, PERMISSION_MODES}` | struct/enum/상수 | `ember/server/src/projects/mod.rs:51`, `:71`, `:98`, `:24`, `:33` | 프로젝트 행과 설정 |

## 세션 수명 주기 (한눈에)

### 상태 (`SessionStatus`, `ember/server/src/events.rs:244`)

DB 문자열: `idle`, `running`, `waiting_for_approval`, `finished`, `failed` (`ember/server/src/store.rs:195-213`). 모르는 문자열은 `idle`로 읽힌다 (`store.rs:211`).

| 이벤트 | 전이 | 근거 |
|---|---|---|
| `UserMessage` | 무엇이든 → `Running` | `events.rs:256` |
| `ApprovalRequested`, `QuestionAsked` | → `WaitingForApproval` | `events.rs:257-259` |
| `ApprovalResolved` | → `Running` | `events.rs:260` |
| `QuestionAnswered`, `PromptWithdrawn` | `WaitingForApproval`일 때만 → `Running`, 아니면 그대로 | `events.rs:264-270` |
| `TurnEnded{Failed}` | → `Failed` | `events.rs:271` |
| `TurnEnded{Completed|Interrupted}` | → `Finished` | `events.rs:272` |
| 그 밖 (`AssistantDelta`, `ToolCall`, `Notice` 등) | 그대로 | `events.rs:273` |

### 누가 상태를 바꾸나

- 상태는 오직 `Store::append`가 바꾼다: 직전 상태를 읽고 `after(event)`로 계산해 이벤트와 같은 트랜잭션에 쓴다 (`store.rs:344-371`).
- `Store::append`를 부르는 곳은 `Sessions::record` (`session.rs:533`) 하나가 중심이다. 이벤트 펌프(`session.rs:643-703`), `record_event`(A2A 등 외부, `session.rs:528`), `set_approve_all`의 Notice(`session.rs:994`), `drain_turn`(`session.rs:1096-1105`)이 모두 여기로 온다.
- 예외: 서버 시작 시 `Store::reset_live_statuses`가 `running`/`waiting_for_approval`을 SQL로 바로 `idle`로 바꾼다 (`store.rs:482-487`, 호출 `main.rs:112`). 포크는 새 세션을 `finished`로 만든다 (`fork.rs:139`). 새 세션은 `idle` (`store.rs:316`).

### 에이전트 프로세스의 생애

1. 생성: `Sessions::create_with_account` (`session.rs:495`)가 어댑터 존재 확인, 계정 라우터 호출, DB 행 생성, `Push::SessionCreated`와 `Push::ProjectUpdated`를 보낸다. 프로세스는 아직 없다.
2. 첫 메시지: `Sessions::send` (`session.rs:807`) → `ensure_live` (`session.rs:552`). `ensure_live`는 `live` 맵에 없으면 프로세스를 만든다.
   - start 훅(환경 변수), instructions 훅(지시문), `EMBER_SESSION_ID`류 `proc::SESSION_ENV` 추가 (`session.rs:568-574`)
   - `StartRequest` 조립 (`session.rs:575-587`), prepare 훅 대기(프로젝트 마운트, `session.rs:588-591`), start-config 훅 (`session.rs:592-595`)
   - 네이티브 포크 대기 중이면 `fork_from`을 넣어 시작, 실패하면 Notice를 남기고 평범하게 시작 (`session.rs:602-626`)
   - 이전 서버가 저장한 대기 중 승인·질문을 어댑터에 복원 (`session.rs:628-635`)
   - `generation` 번호를 붙여 `live`에 넣고 이벤트 펌프 태스크를 띄운다 (`session.rs:636-703`)
3. 이벤트 펌프: 채널에서 이벤트를 받아 중복 `NativeSession` 생략(`session.rs:657-663`) → `record` → approve-all이면 자동 승인 (`session.rs:670-694`). 채널이 비어 있을 때마다 `gate.commit_if_idle`로 shim 출력 offset을 확정한다 (`session.rs:647`). 채널이 닫히면 자기 `generation`일 때만 `live`에서 지운다 (`session.rs:697-702`).
4. 유휴 정리 (FR-S6): `main.rs:301-315`가 30초마다 `reap_idle(EMBER_IDLE_SECS, 기본 300초)`를 부른다. `reap_idle` (`session.rs:745`)은 lease가 살아 있거나, 마지막 활동이 `idle`보다 최근이거나, 상태가 `Running`/`WaitingForApproval`이면 건너뛰고 나머지를 `release` (`session.rs:1034`, 어댑터 `shutdown`)한다. lease는 클라이언트가 `POST /api/sessions/{id}/lease`로 90초씩 갱신한다 (`ember/server/src/api/mod.rs:666-672`).
5. 다음 메시지: `live`에 없으므로 `ensure_live`가 `rec.native_id`로 네이티브 resume 한다 (`session.rs:577`).
6. 죽은 shim: `ensure_live`는 `proc::shim_died(id)`이면 `live`에서 지우고 새로 시작한다 (`session.rs:556-558`).

### 서버 재시작과 shim (FR-S8)

- 서버는 에이전트를 `ember-shim` 자식 프로세스 아래에서 띄운다 (`session_shim.rs:579-623`, setsid로 분리). 서버가 죽어도 shim과 에이전트는 남는다. shim은 stdout을 최대 64 MiB 버퍼에 쥐고 (`session_shim.rs:49`, `:192-196`) Unix 소켓으로 내보낸다.
- 서버는 저장이 끝난 offset만 `ACK` 한다. 저장된 offset은 `shim_offsets` 테이블에 남는다 (`store.rs:446-478`).
- 새 서버 시작 순서: `reset_live_statuses` (`main.rs:112`) → ... → `auth::protect` → `Sessions::rejoin_shims` (`main.rs:519-524`).
- `rejoin_shims` (`session.rs:1045`): `proc::live_shim_sessions`로 살아 있는 shim을 찾아 모두 동시에 `rejoin_one` (`session.rs:1055`).
  - 어댑터가 `rejoins_shim()`이면 `ensure_live`로 붙는다. 어댑터의 spawn이 `attach_or_resume`으로 저장된 offset부터 이어받는다 (`session.rs:1063-1070`, `ember/server/src/agents/proc.rs:316`).
  - 아니고 `drains_shim()`이며 상태가 `Running`/`WaitingForApproval`이면 `drain_turn`: 남은 줄을 `EMBER_SHIM_DRAIN_SECS`(기본 600초)까지 읽어 `translate_drained`로 저장하고, 턴이 안 끝났으면 `Error` + `TurnEnded{Failed}`를 넣는다 (`session.rs:1074-1108`).
  - 주의: 위 상태 검사는 `reset_live_statuses`가 이미 `idle`로 바꾼 뒤에 일어난다. 아래 "주의할 점" 참고.

## 파일별 요약

### `ember/server/src/main.rs` (약 584줄)
- **목적:** `ember-server` 실행 파일. 저장소, 어댑터, 계정, 컴퓨터, transport, A2A, 브라우저, 스케줄러를 만들고 라우터를 조립해 서비스한다.
- **초기화 순서:** [entrypoints.md](../_raw/entrypoints.md) "ember-server 초기화 순서" 23단계를 본다. 여기서는 반복하지 않는다.
- **환경 변수:** 전체 목록은 doc 주석 `ember/server/src/main.rs:24-77`. 이 파일이 직접 읽는 것은 노트 B절 표에 있다.
- **server-core와 맞닿는 곳:** `Store::open(<data>/ember.db)` (`main.rs:90-94`), shim 런타임 설치 (`main.rs:97-109`), `reset_live_statuses` (`main.rs:112`), 어댑터 등록 (`main.rs:121-136`), `Sessions::new` + `load_settings` (`main.rs:206-208`), 유휴 정리 루프 (`main.rs:301-315`), `auth::protect` (`main.rs:499-518`), `rejoin_shims` (`main.rs:519-524`).
- **부수효과:** 데이터 폴더 생성, 리스너 바인드, 백그라운드 태스크 다수.
- **주의점:** `EMBER_DATA_DIR`이 없으면 `HOME`을 쓰며, `HOME`도 없으면 빈 경로 + `.ember`, 곧 현재 디렉터리 아래가 된다 (`main.rs:90-91`). Windows에서 `HOME`이 없을 수 있다 [확인 필요].

### `ember/server/src/store.rs` (약 805줄)
- **목적:** SQLite 한 파일(`ember.db`)에 세션과 이벤트를 저장하고, 모든 모듈의 마이그레이션을 순서대로 적용한다 (FR-S1, FR-S2).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SCHEMA_V1` | 상수 | 87 | `sessions`, `events` 테이블 |
  | `SHIM_OFFSETS_MIGRATION` | 상수 | 112 | `shim_offsets` |
  | `HARNESS_SETTINGS_MIGRATION` | 상수 | 121 | `harness_settings` |
  | `MIGRATIONS` | 상수 | 133 | 마이그레이션 29개, 순서가 곧 `user_version` |
  | `migrate` | 함수 | 172 | 현재 `user_version`부터 끝까지, 항목마다 트랜잭션 + 버전 올림. 서버보다 새 DB면 거부 (`:174-178`) |
  | `Store::open(path)` | 함수(pub) | 216 | `journal_mode = WAL` 후 마이그레이션 |
  | `Store::open_in_memory()` | 함수(pub) | 223 | 테스트용 |
  | `Store::schema_version` | 함수(pub) | 235 | `PRAGMA user_version` |
  | `harness_setting` / `set_harness_setting` / `clear_harness_setting` / `harness_settings_with_key` | 함수(pub) | 240 / 252 / 262 / 271 | 하네스별 설정 키-값 |
  | `create_session` / `create_session_with_account` | 함수(pub) | 281 / 293 | `projects`에 `INSERT OR IGNORE` 후 `sessions` 행 (`:309-317`) |
  | `session` / `sessions(project)` | 함수(pub) | 323 / 334 | 조회, `updated_at DESC` |
  | `append` | 함수(pub) | 344 | `last_seq+1`로 이벤트 저장, 상태와 `updated_at` 갱신, `NativeSession`이면 `native_id` 갱신 |
  | `events_after` | 함수(pub) | 374 | JSON 역직렬화 실패 시 전체 호출이 에러 |
  | `update_session_meta` | 함수(pub) | 398 | 제목/고정/보관. 빈 제목 거부, `updated_at`은 건드리지 않음 |
  | `search(query, limit)` | 함수(pub) | 419 | FTS5 `messages_fts` 검색, `rank` 순, `«` `»`로 강조 (`:69-71`) |
  | `set_shim_offset` / `shim_offset` / `shim_offsets` / `clear_shim_offset` | 함수(pub) | 446 / 456 / 467 / 475 | FR-S8 offset |
  | `reset_live_statuses` | 함수(pub) | 482 | 시작 시 진행 중 상태를 `idle`로 |
  | `row_to_session` | 함수 | 490 | 모르는 `agent` 문자열은 `AgentKind::Scripted`로 읽음 (`:496`) |
  | `fts_query` | 함수 | 515 | 단어마다 큰따옴표로 감싸고 `*` 접두사 질의, 모두 AND |
- **테이블과 마이그레이션 전체:** 아래 "마이그레이션 표" 절.
- **입력 → 출력:** 이벤트 → `(StoredEvent, SessionStatus)`; 질의 → 레코드.
- **의존:** `ember/server/src/agents/mod.rs` (`AgentKind`), `ember/server/src/events.rs`, 마이그레이션 상수를 가진 11개 모듈 (`store.rs:133-163`).
- **사용처:** 팬인 41 (`docs/analysis/_raw/fan.tsv`). 대표: `ember/server/src/main.rs:94`, `ember/server/src/session.rs:534`, `ember/server/src/api/mod.rs:310`.
- **부수효과:** DB 쓰기. 모든 쿼리가 `Mutex<Connection>` 하나를 지나므로 직렬화된다 (`store.rs:82`).
- **주의점:** `MIGRATIONS`는 덧붙이기만 한다 (`store.rs:131-132`). 중간에 넣거나 고치면 기존 DB의 `user_version`과 어긋난다. 테스트는 위치로 찾는다 (`store.rs:167`).
- **테스트:** 12개. 재열기 후 seq·상태 유지, 마이그레이션 전 DB 제자리 갱신, 메타 패치와 검색 이스케이프, 새 스키마 거부, 재시작 상태 리셋 등.

#### 마이그레이션 표 (`MIGRATIONS`, `ember/server/src/store.rs:133-163`)

항목 `i`(0부터)는 `user_version`을 `i`에서 `i+1`로 올린다 (`store.rs:131`). `REFERENCES`는 적혀 있지만 `PRAGMA foreign_keys`를 켜는 코드가 없어 강제되지 않는다 [확인 필요: `grep -rn foreign_keys ember/server/src` 결과 없음].

| # (→버전) | 상수 | 정의 위치 | 만드는 것 / 바꾸는 것 |
|---|---|---|---|
| 0 (→1) | `SCHEMA_V1` | `ember/server/src/store.rs:87` | `sessions`(id PK, project, agent, cwd, model, native_id, status, title, created_at, updated_at, last_seq), `events`(session_id FK, seq, at, event JSON, PK(session_id, seq)) |
| 1 (→2) | `accounts::schema::MIGRATION` | `ember/server/src/accounts/schema.rs:4` | `accounts`(id, agent, label, config_dir, status, is_default, limited_until, limit_reason, created_at) + 하네스당 기본 하나 유니크 인덱스; `sessions`에 `account_id`, `account_reason` 열과 인덱스; `events_usage_by_time` 부분 인덱스 (`kind = 'usage'`); `api_providers`(키는 `key_nonce`/`key_ciphertext`로 암호화) |
| 2 (→3) | `computers::schema::MIGRATION` | `ember/server/src/computers/schema.rs:8` | `computers`(id, name UNIQUE, url, token, created_at), `session_computer`(session_id PK, computer_id, env_json, notice, switched_at) |
| 3 (→4) | `chatgpt::schema::MIGRATION` | `ember/server/src/chatgpt/schema.rs:4` | `chatgpt_accounts`(토큰 암호화 열 포함, (client_id, subject) 유니크), `chatgpt_host`(행 1개), `chatgpt_usage`(account_id, day) |
| 4 (→5) | `browser::egress::MIGRATION` | `ember/server/src/browser/egress.rs:63` | `browser_egress`(project PK, kind `proxy`/`computer`, value, updated_at) |
| 5 (→6) | `computers::schema::PEER_MIGRATION` | `ember/server/src/computers/schema.rs:33` | `computers.peer_json` 열 |
| 6 (→7) | `devices::schema::MIGRATION` | `ember/server/src/devices/schema.rs:4` | `devices`(peer_id PK, name, created_at) |
| 7 (→8) | `projects::schema::MIGRATION` | `ember/server/src/projects/schema.rs:11` | `projects`(name PK, created_at), 기존 세션의 project로 채움; `project_computers`(project, computer_id, assigned_at) + 컴퓨터별 인덱스 |
| 8 (→9) | `projects::schema::META_FTS_MIGRATION` | `ember/server/src/projects/schema.rs:39` | `sessions.pinned`, `sessions.archived`; FTS5 `messages_fts`(text, session_id/seq/kind UNINDEXED, `unicode61 remove_diacritics 2`), 기존 메시지로 채움; 트리거 `events_messages_fts` (`user_message`/`assistant_message` 삽입 시 색인) |
| 9 (→10) | `hub::schema::MIGRATION` | `ember/server/src/hub/schema.rs:4` | `hub_registration`(행 1개, 토큰 암호화), `devices.source` 열 (기본 `local`) |
| 10 (→11) | `hub::schema::RESOLVE_MIGRATION` | `ember/server/src/hub/schema.rs:27` | `hub_registration.resolve_nonce`/`resolve_ciphertext`, `hub_pending_link`(행 1개) |
| 11 (→12) | `mcp::schema::MIGRATION` | `ember/server/src/mcp/schema.rs:10` | `mcp_servers`(name UNIQUE, command, args, env_keys, env 암호화, enabled, scope, ...) |
| 12 (→13) | `schedules::schema::MIGRATION` | `ember/server/src/schedules/schema.rs:13` | `schedules`(cron 등 17열) + 인덱스 2개, `schedule_runs` + 인덱스 2개 |
| 13 (→14) | `a2a::team::MIGRATION` | `ember/server/src/a2a/team.rs:41` | `teams`, `team_members`(활성 이름 유니크), `team_tasks`, `team_mail` |
| 14 (→15) | `fork::MIGRATION` | `ember/server/src/fork.rs:18` | `session_forks`(session_id PK, parent_id, parent_seq, forked_at, seeded) + 부모 인덱스 |
| 15 (→16) | `fork::NATIVE_MIGRATION` | `ember/server/src/fork.rs:32` | `session_forks.native_pending`, `parent_native_id`, `keep_turns` |
| 16 (→17) | `computers::schema::DESIGNATED_MIGRATION` | `ember/server/src/computers/schema.rs:54` | `session_designated`(session_id PK, computer_id) |
| 17 (→18) | `members::MIGRATION` | `ember/server/src/members.rs:24` | `session_proxy`(session_id PK, endpoint, key_env) |
| 18 (→19) | `SHIM_OFFSETS_MIGRATION` | `ember/server/src/store.rs:112` | `shim_offsets`(session_id PK, offset) |
| 19 (→20) | `channels::MIGRATION` | `ember/server/src/channels/mod.rs:29` | `channels`(프로젝트당 기본 하나), `channel_agents`, `channel_messages`(seq AUTOINCREMENT) |
| 20 (→21) | `channels::READS_MIGRATION` | `ember/server/src/channels/mod.rs:55` | `channel_reads`(channel_id, reader, last_seq) |
| 21 (→22) | `channels::MENTIONS_MIGRATION` | `ember/server/src/channels/mod.rs:66` | `channel_messages.mentions` (기본 `'[]'`) |
| 22 (→23) | `projects::schema::SETTINGS_MIGRATION` | `ember/server/src/projects/schema.rs:67` | `projects.repository`, `default_branch`, `member_defaults`(기본 `'{}'`), `character_style`, `archived` |
| 23 (→24) | `channels::invites::MIGRATION` | `ember/server/src/channels/invites.rs:16` | `channel_invites`(token_hash UNIQUE), `channel_guests`(credential_hash UNIQUE) |
| 24 (→25) | `projects::schema::PROFILE_OVERRIDES_MIGRATION` | `ember/server/src/projects/schema.rs:78` | `projects.profile_overrides` |
| 25 (→26) | `computers::enrol::MIGRATION` | `ember/server/src/computers/enrol.rs:89` | `enrol_codes`(code_hash UNIQUE, name, created_ms, expires_ms, used_ms, computer_id) |
| 26 (→27) | `computers::enrol::CONFIRM_MIGRATION` | `ember/server/src/computers/enrol.rs:108` | `enrol_codes`에 `state`(기본 `waiting`) 등 9열, 기존 행 상태 채움 |
| 27 (→28) | `HARNESS_SETTINGS_MIGRATION` | `ember/server/src/store.rs:121` | `harness_settings`(harness, key, value, updated_ms, PK(harness, key)) |
| 28 (→29) | `computers::schema::PEER_ID_UNIQUE_MIGRATION` | `ember/server/src/computers/schema.rs:39` | `computers.peer_id` 열, `peer_json`에서 64자 peer를 소문자로 채움, 부분 유니크 인덱스 |

`harness_settings`의 키: 하네스별 `mem_limit_mb` (`session.rs:198`), 가상 하네스 `_defaults`의 `agent`, `model`, `effort`, `mode` (`session.rs:209-213`).

### `ember/server/src/session.rs` (약 1,182줄)
- **목적:** 세션 수명 주기 (FR-S1-S3, FR-S6). 위 "세션 수명 주기" 절이 동작을 설명한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Push` | enum | 30 | `SessionCreated`, `Event{status, event}`, `SessionUpdated`, `ProjectUpdated`, `TeamUpdated`, `ScheduleCreated/Updated/Deleted`, `ScheduleRun`, `ApproveAll`, `ChannelMessage`. 변형은 추가만 한다 (`:27`) |
  | `SessionError` | enum | 57 | `NotFound`, `AgentUnavailable`, `Account`, `Other` |
  | `QuestionError` | enum | 71 | `NoSession`, `NotPending`, `Invalid`, `NoAgent`, `BadBody`, `Other` |
  | `QuestionAnswerBody::choice` | 함수(pub) | 114 | `answers`와 `decline:true` 중 정확히 하나 |
  | `NewSession` | struct | 128 | project, agent, cwd, model, title |
  | `LiveRun` | struct | 140 | 실행 중 어댑터 + 펌프로 가는 송신자 + `generation` |
  | 훅 타입 9종 | type | 151-195 | `StartHook`(환경), `EndHook`, `EventHook`, `AccountRouter`, `InstructionsHook`, `StartConfigHook`, `PrepareHook`(async), `MessageHook`(1회 노트), `UserMessageHook`(async) |
  | `MEM_LIMIT_*`, `DEFAULTS_HARNESS_ID`, `DEFAULT_*_KEY`, `EFFORT_LEVELS` | 상수 | 198-214 | 하네스 설정 키와 범위 (256..=262144 MiB) |
  | `Sessions::new` | 함수(pub) | 255 | 어댑터를 `kind()`로 맵에 넣음, push 브로드캐스트 용량 1024 |
  | `load_settings` / `set_mem_limit_persisted` / `mem_limit_mb` | 함수(pub) | 297 / 323 / 342 | 메모리 제한 (FR-L20, FR-S8). 저장 먼저, 메모리 나중 |
  | `agent_defaults` / `set_agent_default_key` | 함수(pub) | 348 / 373 | 새 팀원 기본값. 잘못된 행은 무시 |
  | `add_*_hook`, `set_account_router` | 함수(pub) | 382-433 | 훅 등록 (사용처는 노트 C절) |
  | `session_ended` | 함수(pub) | 392 | 질문 키 해제 + end 훅 실행 |
  | `subscribe` / `publish` | 함수(pub) | 439 / 444 | 브로드캐스트 |
  | `update_meta` | 함수(pub) | 449 | 메타 패치 + `SessionUpdated` |
  | `detect_agents` | 함수(pub) | 455 | 저장소 어디서도 쓰지 않음 (노트 A) |
  | `probe_agents` | 함수(pub) | 468 | 어댑터별 `detect` + 실행 파일 경로 |
  | `create` / `create_with_account` | 함수(pub) | 489 / 495 | 세션 생성. `create`는 테스트에서만 쓰인다 |
  | `record_event` / `record` | 함수 | 528 / 533 | 저장 → 질문 키 해제 → `touch` → 이벤트 훅 → push |
  | `ensure_live` | 함수 | 552 | 프로세스 시작 또는 재사용, 펌프 생성 |
  | `pending_approvals` / `pending_questions` | 함수 | 710 / 717 | 저장된 이벤트를 처음부터 훑어 대기 중인 것 계산 |
  | `lease` / `reap_idle` | 함수(pub) | 737 / 745 | FR-S6 |
  | `fork` | 함수(pub) | 775 | `Store::fork_session` 후 네이티브 포크 계획 저장, `SessionCreated` |
  | `send` / `send_from_user` | 함수(pub) | 807 / 836 | 노트(포크 시드, 메시지 훅) → `SystemNotice`, `UserMessage` 기록 → 어댑터 `send(노트+본문)` |
  | `answer` | 함수(pub) | 845 | `ApprovalResolved`를 펌프에 넣고 어댑터 `answer` |
  | `answer_question` / `resolve_question_body` / `decline_question` / `resolve_question` | 함수 | 865 / 877 / 897 / 901 | 질문 답: 검증 → 키 선점 → 어댑터 먼저 → 성공 시 기록(비밀은 `***`) |
  | `approve_all` / `set_approve_all` | 함수(pub) | 972 / 979 | 메모리에만 저장, 켜면 대기 중 승인을 바로 허용 |
  | `interrupt` / `release` | 함수(pub) | 1026 / 1034 | 어댑터 `interrupt` / `shutdown` |
  | `rejoin_shims` / `rejoin_one` / `drain_turn` | 함수 | 1045 / 1060 / 1085 | FR-S8 |
  | `is_live` | 함수(pub) | 1110 | `live` 맵에 있는지 |
  | `pending_approvals_of` | 함수 | 1117 | 순수 함수 |
- **입력 → 출력:** API·A2A·스케줄러의 호출 → 어댑터 호출, DB 이벤트, `Push`.
- **의존:** `ember/server/src/agents/mod.rs`, `ember/server/src/agents/proc.rs`, `events.rs`, `store.rs`, `fork.rs`, `projects/mod.rs`, `schedules`, `a2a::team`, `channels` (`Push` 변형 타입).
- **사용처:** 팬인 21. 라우트에서 부르는 지점은 노트 C절 표.
- **부수효과:** 외부 프로세스 시작·종료(어댑터 통해), DB 쓰기, 브로드캐스트.
- **주의점:** 아래 "수정할 때 주의할 점".
- **테스트:** 2개 (`pending_tests`, `session.rs:1135`). 저장된 `needs_person` 플래그 복원과 플래그 없는 옛 행.

### `ember/server/src/session_shim.rs` (약 692줄)
- **목적:** 세션별 shim (FR-S8, INTENT D17). 에이전트 stdio를 쥐고 서버보다 오래 산다. Unix 전용: Windows에서는 모든 함수가 "only supported on Unix" 에러다 (`session_shim.rs:281-283`, `:506-532`, `:572-575`, `:625-632`).
- **shim 디렉터리 파일** (`<data>/shims/`, `main.rs:99`): `<id>.sock`(제어 소켓), `<id>.json`(`ShimMeta`), `<id>.log`(stderr), `<id>.spec.json`(`ShimSpec`, 0600, 읽은 뒤 삭제) (`session_shim.rs:9-14`, `:94-105`, `:146-147`).
- **소켓 프로토콜** (`session_shim.rs:16-24`): 클라이언트 → shim `ATTACH <offset>`, `IN <len>\n<bytes>`, `ACK <offset>`, `KILL`, `CLOSE`; shim → 클라이언트 `O <start> <len>\n<bytes>`, `X <reason>` (`exit:<code>`, `signal:<n>`, `memory-limit`, `error:<e>`, `exit:unknown`, `:223-233`). 새 `ATTACH`가 이전 연결을 대신한다 (`generation`, `:270`, `:360`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `BUFFER_CAP` | 상수 | 49 | 64 MiB. 넘치면 오래된 미확인 바이트를 버리고 `base`를 올림 |
  | `ShimSpec` | struct | 53 | program, args, cwd, env, mem_limit_bytes, mem_poll_ms(기본 1000), linger_secs(기본 3600) |
  | `ENV_CLEAR` / `apply_env` | 상수 / 함수(pub) | 71 / 75 | `EMBER_ENV_CLEAR` 표식이 있으면 `env_clear` 후 나머지만 설정 (허용 목록, FR-A10) |
  | `linger_secs` | 함수(pub) | 83 | spec → `EMBER_SHIM_LINGER_SECS` → 3600 |
  | `ShimMeta` | struct | 88 | session, shim_pid, agent_pid |
  | `run_shim` | 함수(pub) | 145 | shim 본체: spec 읽고 삭제, 에이전트를 새 프로세스 그룹으로 실행, stdout 리더, 종료 대기, 메모리 감시, 소켓 accept 루프 |
  | `kill_group` | 함수 | 286 | 프로세스 그룹에 SIGKILL |
  | `tree_rss_bytes` | 함수 | 297 | `ps -A -o pid=,ppid=,rss=`로 자손 RSS 합 |
  | `serve` / `read_commands` | 함수 | 331 / 406 | 연결 하나의 송신 루프와 명령 처리. `ACK`가 끝까지 오고 종료가 기록됐으면 정리 후 `exit(0)` (`:442-447`) |
  | `ShimEvent` | enum | 462 | `Output{start, data}`, `Exited(reason)` |
  | `ShimClient` | struct | 472 | 서버 쪽 연결. `send_stdin`, `ack`, `close_stdin`, `kill` |
  | `attach` | 함수(pub) | 536 | 연결하고 프레임을 `ShimEvent`로 바꾸는 태스크 |
  | `spawn_shim` | 함수(pub) | 579 | spec을 0600으로 쓰고 `ember-shim --dir --id`를 setsid로 실행, 50 ms 간격 100번 attach 시도 (`:616-622`) |
  | `scan` / `attach_or_resume` / `reattach_all` | 함수(pub) | 635 / 660 / 672 | 메타 파일 목록, 붙거나 정리 후 `Resume`, 시작 시 일괄 |
  | `pid_alive` | 함수(pub) | 684 | `kill(pid, 0)` |
- **사용처:** `ember/server/src/agents/proc.rs:182-184`, `:290`, `:316`, `:376`, `:580`, `:606`; `ember/server/src/agents/acp.rs:125`; `ember/server/src/bin/ember-shim.rs:12`.
- **부수효과:** 프로세스 생성(setsid, 프로세스 그룹), Unix 소켓, 파일 쓰기·삭제, `ps` 실행, `std::process::exit`.
- **주의점:** 종료 후 linger(기본 1시간)가 지나면 ACK 여부와 관계없이 파일을 지우고 끝난다 (`session_shim.rs:240-242`). 소켓 파일 권한을 따로 좁히지 않는다 (노트 A).
- **테스트:** 이 파일 안에는 없다. 통합 테스트 `ember/server/tests/fr_s8_wiring.rs`가 다룬다.

### `ember/server/src/auth.rs` (약 385줄, 보안)
- **목적:** 로컬 TCP 리스너의 서버 토큰과 Host/Origin 검사 (FR-S9, FR-S10; INTENT D37, #338).
- **적용 범위:** `main.rs:517`에서 `local_app` 전체(폴백 포함)에 한 번 적용된다. transport로 서비스하는 `app`은 감싸지 않는다: transport의 장치 게이트(FR-N3, FR-N7)가 이미 인증했다고 본다 (`auth.rs:5-7`, `main.rs:499-500`). guest door와 enrol door는 각자의 리스너라 이 미들웨어 밖이다 (`auth.rs:21-23`, 테스트 `:355-376`).
- **토큰:** `<data dir>/server-token`. 없거나 비었으면 UUIDv4 두 개(simple, 64 hex)로 새로 만든다 (`auth.rs:57-59`, `:63-87`). Unix에서는 0600으로 만들고 읽을 때마다 0600으로 다시 맞춘다 (`:70`, `:80`, `:89-93`). Unix가 아니면 `restrict`가 아무것도 하지 않는다 (`:95-98`). 값은 로그에 쓰지 않고 경로만 쓴다 (`main.rs:503-506`).
- **검사 순서 (`guard`, `auth.rs:251-282`):**
  1. Host: `Host` 헤더(없으면 URI authority)의 호스트 부분(`api::origin::host_of`, `ember/server/src/api/origin.rs:14`)이 `host_allowed`여야 한다. 아니면 403 `{"error":"host not allowed"}` (`auth.rs:254-262`).
  2. Origin: `api::origin::origin_allowed` (`ember/server/src/api/origin.rs:32`). `Origin`이 없으면 통과, 있으면 `Host`와 같은 authority이거나 loopback 호스트여야 한다. 아니면 403 `{"error":"origin not allowed"}` (`auth.rs:263-265`).
  3. 토큰: 면제 경로가 아니면 `Authorization: Bearer <token>`, WebSocket 업그레이드면 `Sec-WebSocket-Protocol`의 `ember.token.<token>` 항목도 받는다. 쿼리 문자열은 받지 않는다. 비교는 `token_eq`. 틀리면 401 `{"error":"missing or wrong server token"}` + `WWW-Authenticate: Bearer` (`auth.rs:180-186`, `:232-249`, `:266-271`).
  4. 클라이언트가 `ember.v1`을 제안했고 101 응답에 프로토콜 헤더가 없으면 `ember.v1`을 넣는다. 토큰 항목을 되돌려 보내지 않기 위해서다 (`auth.rs:272-280`).
- **`host_allowed` 규칙** (`auth.rs:156-172`): (a) 설정된 추가 호스트(`EMBER_ALLOWED_HOSTS` 쉼표 목록 + `EMBER_AGENT_URL`의 호스트, `main.rs:507-516`), (b) 리슨 IP와 같은 IP 리터럴, (c) 리스너가 loopback 또는 미지정 주소면 `localhost`와 loopback IP, (d) 리스너가 미지정 주소(`0.0.0.0`)면 아무 IP 리터럴. 이름은 설정해야만 통과한다 (DNS rebinding 방어, `:169-171`).
- **토큰 면제 (`token_exempt`, `auth.rs:200-214`).** 면제여도 1, 2단계는 거친다.
  | 경로 | 메서드 | 이유 / 실제 인증 |
  |---|---|---|
  | `/api/health` | GET | 서버가 떠 있는지 확인 *[provisional]* (`auth.rs:10`, `:202`) |
  | `crate::chatgpt::oauth::CALLBACK_PATH` (`/auth/callback`) | GET | 브라우저 리다이렉트라 헤더 불가. 핸들러가 `state` 검사 (`auth.rs:18-19`, `:202`) |
  | `/api/browsers/<project>/cdp/<nonce>` 와 `.../json/version` | GET | 에이전트 MCP 서버는 헤더를 못 붙인다. 프로세스마다 새 nonce(`agent_cdp_nonce`, 메모리에만, `auth.rs:112-115`)를 경로에 넣고 상수 시간 비교 (`auth.rs:121-131`) |
  | `/api/channels/<id>/post` (정확히 4 세그먼트) | POST | 에이전트가 런타임 토큰으로 멘션에 답함, 핸들러가 검사 (`auth.rs:191-197`) |
  | `/api/a2a/*` (단 `/api/a2a/settings` 제외) | 모든 메서드 | 세션 런타임 토큰을 핸들러가 검사 (`auth.rs:212`) |
  | `crate::agents::antigravity::HOOK_ROUTE` | 모든 메서드 | Antigravity PreToolUse 훅, 핸들러가 검사 (`auth.rs:213`) |
- **`token_eq`** (`auth.rs:102-105`): 두 값을 SHA-256으로 32바이트로 만든 뒤 XOR 누적 비교. 길이와 첫 차이 위치에 시간이 의존하지 않는다.
- **사용처:** `ember/server/src/main.rs:502-517`, `ember/server/src/browser/agent.rs:171` (nonce를 에이전트 설정에 넣음), `ember/server/src/channels/invites.rs:352`, `ember/server/src/computers/enrol.rs:240` (`token_eq` 재사용).
- **주의점:** 면제 목록에 경로를 더하면 그 경로는 서버 토큰 없이 열린다. 테스트가 열면 안 되는 경로 집합을 고정한다 (`auth.rs:288-376`). `/api/a2a/` 접두사 규칙은 메서드를 가리지 않으므로 그 아래 새 라우트는 모두 핸들러가 직접 런타임 토큰을 검사해야 한다 (`auth.rs:212`).
- **테스트:** 7개. 채널 아래 `post`만 면제, 질문·승인 답 라우트 비면제, guest·settings·enrol 경로 비면제, `token_eq` 전체 비교.

### `ember/server/src/events.rs` (약 506줄)
- **목적:** 모든 어댑터가 내보내는 정규화 이벤트 모델 (FR-A3). 저장, 푸시, UI, A2A는 이 모델만 본다 (`events.rs:1-5`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `AgentEvent` | enum | 12 | `native_session`, `user_message`, `system_notice`, `assistant_delta`, `assistant_message`, `tool_call`, `tool_result`, `approval_requested`(needs_person), `approval_resolved`, `usage`, `rate_limited`, `turn_ended`, `error`, `turn_error`(code `auth_required`/`quota_exceeded`), `notice`, `question_asked`, `question_answered`, `prompt_withdrawn` |
  | `Question`, `QuestionOption`, `QuestionAnswer` | struct | 70, 85, 107 | 질문 구조 (secret, multi_select, allow_other) |
  | `clean_question_text` | 함수(pub) | 92 | 제어·bidi 문자 제거, 공백 접기 |
  | `ApprovalPolicy` / `approval_policy` | struct / 함수(pub) | 115 / 132 | `AskUserQuestion`은 자동 금지, `ExitPlanMode`는 자동 허용 + Notice, `needs_person`이면 자동 금지, 나머지 자동 허용·기억 |
  | `QUESTION_WAITS_NOTICE`, `PLAN_AUTO_APPROVED_NOTICE` | 상수 | 125, 127 | 한국어 Notice 문구 |
  | `ANSWER_VALUES_MAX`, `ANSWER_VALUE_CHARS_MAX` | 상수 | 146, 147 | 8개, 1000자 |
  | `AnswerInvalid` / `validate_question_answers` | enum / 함수(pub) | 152 / 170 | 답 검증. 에러 문구는 API로 그대로 나간다 |
  | `redact_secret_answers` | 함수(pub) | 200 | 저장용 답: secret 값은 `***`, 나머지는 `clean_question_text` |
  | `is_user_question_tool` | 함수(pub) | 220 | `AskUserQuestion` 정확 일치 |
  | `ApprovalDecision`, `TurnOutcome`, `SessionStatus` | enum | 226, 235, 244 | 위 상태 표 |
- **사용처:** 팬인 22 (`docs/analysis/_raw/fan.tsv`).
- **주의점:** 직렬화 형식(`kind` 태그와 필드명)이 DB `events.event` JSON이고 FTS 트리거가 `$.kind`, `$.text`를 읽는다 (`ember/server/src/projects/schema.rs:55-60`). 변형 이름이나 `text` 필드를 바꾸면 옛 행 역직렬화와 검색이 깨진다.
- **테스트:** 11개. 늦은 답이 끝난 세션을 다시 열지 않음, 승인이 running보다 우선, `kind` 태그 직렬화, 정책 표와 답 검증 등.

### `ember/server/src/fork.rs` (약 239줄)
- **목적:** 세션 포크 (FR-S5). 부모의 완료된 턴까지 이벤트를 새 세션에 복사하고 `session_forks`에 기록한다. 에이전트가 네이티브 포크를 지원하면 그것을 먼저 쓰고, 안 되면 복사한 대화를 첫 메시지 앞에 `SystemNotice`로 넣는다 (`fork.rs:1-8`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MIGRATION`, `NATIVE_MIGRATION` | 상수 | 18, 32 | 위 마이그레이션 표 14, 15 |
  | `SEED_MAX_CHARS` | 상수 | 39 | 100,000자, 최신 쪽을 남김 |
  | `ForkOrigin`, `ForkError` | struct/enum | 43, 51 | `NotFound`, `BadTurn`, `Other` |
  | `plan_native_fork` | 함수(pub) | 64 | `NativeFork::None/AtTurn/Latest`와 마지막 턴 여부·뒤따르는 사용자 메시지로 `ForkFrom` 결정 |
  | `completed_turns` / `transcript` | 함수(pub) | 82 / 91 | 완료 턴 seq 목록, `User:` / `Assistant:` 평문 |
  | `Store::fork_session` | 함수(pub) | 109 | 새 세션 `finished` 상태로 생성, `NativeSession` 빼고 복사, seq 다시 매김 |
  | `set_native_fork` / `pending_native_fork` / `settle_native_fork` | 함수(pub) | 163 / 173 / 192 | 네이티브 포크 대기 상태 관리 |
  | `fork_origin` / `forks_of` / `take_fork_seed` | 함수(pub) | 201 / 213 / 223 | 출처, 자식 목록, 1회용 시드 노트 |
- **사용처:** `ember/server/src/session.rs:602`, `:609`, `:614`, `:775-805`, `:812`; `ember/server/src/api/mod.rs:350`, `:356`, `:454`.
- **부수효과:** DB 쓰기.
- **주의점:** 복사된 이벤트도 `events` 삽입 트리거로 `messages_fts`에 다시 색인된다 (`projects/schema.rs:55-60`), 그래서 검색에서 부모와 포크가 같이 나온다 [추정]. 복사 시 직렬화 실패를 빈 문자열로 넣는다 (`fork.rs:146`).
- **테스트:** 이 파일 안에는 없다 [확인 필요: `ember/server/tests/`에 포크 테스트가 있는지].

### `ember/server/src/projects/mod.rs` (약 483줄)
- **목적:** 프로젝트 행, 컴퓨터 배정(다대다), 프로젝트 설정 (FR-L1, FR-L3, FR-L4, FR-L26).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `DEFAULT_PROJECT_NAME` | 상수 | 24 | `"기본 프로젝트"`. 클라이언트에도 같은 문자열이 두 번 있다 (`:21-23`) |
  | `NAME_MAX_CHARS`, `CHARACTER_STYLES`, `PERMISSION_MODES` | 상수 | 27, 30, 33 | 64자; 6가지 스타일; `ask`, `edits`, `plan`, `bypass` |
  | `MemberDefaults`, `Project`, `ProjectPatch` | struct | 38, 51, 71 | `ProjectPatch`는 `deny_unknown_fields`, `nullable`로 생략과 `null` 구분 (`:89-95`) |
  | `ProjectError` | enum | 98 | `NotFound`, `ComputerNotFound`, `BadRequest`, `Protected`, `NameTaken`, `Other` |
  | `RENAMED_TABLES` | 상수 | 124 | 이름 변경 시 따라 바꾸는 표 6개 |
  | `check_new_name` 등 검증 함수 | 함수 | 155-276 | 이름, 저장소, 브랜치, 기본값, 오버라이드, 스타일 |
  | `validate_name` | 함수(pub) | 278 | 빈 이름만 거부 |
  | `Store::projects` / `project` | 함수(pub) | 287 / 302 | 배정 목록 포함, 사라진 계정 오버라이드는 `null` |
  | `Store::project_account_override` | 함수(pub) | 317 | 사용처 `ember/server/src/members.rs:237` |
  | `Store::patch_project` | 함수(pub) | 330 | 한 트랜잭션. 이름 변경은 새 행 삽입 → 6개 표 갱신(`browser_egress`는 `UPDATE OR REPLACE`) → 옛 행 삭제 (`:372-394`) |
  | `Store::ensure_project` / `assign_computer` / `unassign_computer` / `projects_of_computer` | 함수(pub) | 402 / 413 / 436 / 448 | 생성, 배정(멱등), 해제(멱등), 역조회 |
- **사용처:** `ember/server/src/api/mod.rs:480-571`, `ember/server/src/computers/api.rs:119`, `ember/server/src/session.rs:368`, `:521`.
- **주의점:** 새 이름 규칙(`check_new_name`, 64자, `/` 금지)은 이름 변경에만 쓰이고, 생성(`ensure_project`, `create_session_with_account`)은 빈 이름만 거부한다 (`projects/mod.rs:278-283`, `store.rs:309-312`). `archived` 열은 있지만 `ProjectPatch`에 필드가 없어 API로 바꿀 수 없다 (`projects/mod.rs:71-86`).
- **테스트:** 1개. 세션 생성이 프로젝트를 만들고 배정이 다대다인지.

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/server/src/lib.rs` | 38 | 크레이트 루트. 모듈 29개를 `pub mod`로 연다 (`lib.rs:5-33`). 유닉스 테스트에서 `tests/common/mod.rs`를 `test_exec`로 공유 (`lib.rs:35-38`) |
| `ember/server/src/projects/schema.rs` | 80 | 프로젝트 관련 마이그레이션 4개: `MIGRATION`(`:11`), `META_FTS_MIGRATION`(`:39`), `SETTINGS_MIGRATION`(`:67`), `PROFILE_OVERRIDES_MIGRATION`(`:78`). 파일 머리 주석은 "migrations 8 and 9"만 말한다 (`:1-2`) |
| `ember/server/src/bin/ember-shim.rs` | 16 | `ember-shim --dir <dir> --id <session>`. 인자가 없으면 종료 코드 2, `run_shim` 에러면 1 (`ember-shim.rs:7-14`) |
| `ember/server/src/bin/ember-exec.rs` | 68 | Claude Code의 Bash 도구를 세션 노드에서 실행 (`CLAUDE_CODE_SHELL_PREFIX`). `computers::shim::plan`이 Local이면 `$SHELL -c`(Unix exec) 또는 `%COMSPEC% /C`, Remote면 노드에서 실행 후 `EMBER_MOUNT_CTL` 소켓으로 마운트 캐시 무효화 (`ember-exec.rs:18-68`). 인자 오류 2, 셸 실행 실패 127, 런타임 실패 255 |
| `ember/server/src/bin/ember-a2a.rs` | 6 | `a2a::client::run(args)`의 종료 코드로 끝남 (`ember-a2a.rs:3-6`) |
| `ember/server/Cargo.toml` | 73 | 의존성. `rusqlite` bundled (`:31`), 선택 기능 `mount-nfs`, `mount-fuse`, `letify` (`:61-67`) |
| `ember/server/scripts/ember-mount-setup.sh` | 59 | 프로젝트 마운트 지점을 sudo로 한 번 만드는 스크립트. `--dry-run` 지원, macOS에서 `/etc/auto_master` 수정과 `/etc/synthetic.conf` 추가를 할 수 있다 (`:41-53`) |
| `ember/server/scripts/real-server-smoke.sh` | 655 | 서버+노드+앱 실기 스모크. 하위 명령 `check`, `up`, `steps`, `status`, `app`, `server-restart`, `server-update`, `down`, `reset` (`:6-14`, `:645-653`). 실행 디렉터리는 저장소 안이어야 한다 (`:40-43`). 서버를 `EMBER_SCRIPTED_AGENT=1 EMBER_HUB_URL=off EMBER_SERVER_RELAY=off`로 띄운다 (`:174-175`) |

## 이 모듈을 수정할 때 주의할 점

- **저장 먼저, 푸시 나중.** `record`는 `append`가 성공해야 push 한다 (`session.rs:533-549`). 이벤트 훅은 펌프 안에서 동기로 돈다, 느린 훅은 그 세션의 모든 이벤트를 늦춘다 (`session.rs:157-159`).
- **사용자 메시지 순서.** 노트와 `UserMessage`는 펌프 채널로 먼저 넣고, 어댑터 `send`는 나중에 부른다 (`session.rs:814-830`). 저장 순서가 실제 순서가 되게 하려는 설계다 (`session.rs:136-138`).
- **`ensure_live`는 `live` 맵 잠금을 쥔 채 prepare 훅(마운트)과 `adapter.start`를 기다린다** (`session.rs:553`, `:588-626`). 느린 시작 하나가 다른 모든 세션의 `send`, `answer`, `is_live`, `reap_idle`을 막는다.
- **재시작 순서 의존.** `reset_live_statuses`(`main.rs:112`)가 `rejoin_shims`(`main.rs:520`)보다 먼저라서, `rejoin_one`의 "진행 중이면 drain" 조건(`session.rs:1074-1076`)이 실제 시작에서는 거짓이 된다. 통합 테스트는 리셋 없이 `rejoin_shims`를 부른다 (`ember/server/tests/fr_s8_wiring.rs:476`, `:546`). 또 다시 붙은 실행 중 턴은 상태가 `idle`로 보이고 `reap_idle`의 busy 검사를 통과한다 (`session.rs:757-761`). 순서를 바꾸거나 재접속 대상만 리셋에서 빼는 방향을 검토해야 한다 [확인 필요: 실제 재시작으로 검증].
- **approve-all은 메모리에만 있다** (`session.rs:241-243`). 재시작하면 모두 꺼진다.
- **`pending_approvals`, `pending_questions`, `set_approve_all`은 세션 이벤트 전체를 매번 처음부터 읽는다** (`session.rs:711`, `:719`, `:997`). 긴 세션에서 느려진다.
- **`answer`는 `ApprovalResolved`를 먼저 기록하고 어댑터 호출은 나중이다** (`session.rs:854-858`). 어댑터가 실패해도 기록은 남는다. 질문 답(`resolve_question`)은 반대로 어댑터가 받아야 기록한다 (`session.rs:924-953`).
- **마이그레이션은 덧붙이기만.** 다른 모듈의 상수를 지우거나 순서를 바꾸면 안 된다 (`store.rs:131-132`).
- **`AgentKind`를 지우거나 이름을 바꾸면** 그 세션은 `Scripted`로 읽힌다 (`store.rs:496`). ACP 에이전트 설정을 빼도 같은 일이 생긴다 [추정: `AgentKind::from_stored`가 ACP 이름을 등록 목록으로 찾는다면].
- **같은 값이 두 곳에.** `DEFAULT_PROJECT_NAME`은 클라이언트 `ember/app/src/ui/project.rs`, `ember/app/src/ui/home.rs`에도 있다 (`projects/mod.rs:21-23`). `PERMISSION_MODES`는 `api/mod.rs:274`와 `session.rs:368`에서 재사용된다.
- **인증 경계.** `auth::protect`는 로컬 TCP 라우터에만 걸린다. transport 쪽 `app`에 새 라우트를 넣으면 장치 게이트만 거친다 (`main.rs:499-500`).
