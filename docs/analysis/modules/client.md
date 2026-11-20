# 모듈: client

- 경로: `ember/client/` (크레이트 `ember-client`, `ember/client/Cargo.toml:2`)
- 규모: 파일 11개 / 약 6,961줄 (`Cargo.toml` 33줄 + `src/*.rs` 10개)
- 레이어: 데이터 접근
- 한 줄 책임: UI 아래의 네이티브 클라이언트 코어. 메인 서버 `/api`를 부르는 HTTP 클라이언트(`Api`), push WebSocket 동기화 엔진(`Client`), 순수 리듀서(`State`, `Transcript`), 서버 토큰 탐색, 콜드 스타트 캐시를 담는다 (`ember/client/src/lib.rs:1-14`).
- 의존하는 모듈: [transport](transport.md) (`ember-transport`의 `http` 기능만, `ember/client/Cargo.toml:14`; `Dialer`, `PeerAddr`, `PowerState`, `ember_transport::http::http1_handshake`, `ember/client/src/api.rs:13`, `api.rs:792`)
- 이 모듈을 쓰는 모듈: [app-core](app-core.md), [app-ui](app-ui.md), [app-ui-collab](app-ui-collab.md), [app-ui-dev](app-ui-dev.md), [app-ui-cr](app-ui-cr.md), [app-ui-cr-session](app-ui-cr-session.md), [app-ui-cr-work](app-ui-cr-work.md), [tests](tests.md) (`ember/client/tests/*.rs`). 서버는 dev-dependency로만 링크된다 (`ember/client/Cargo.toml:30`).

설계 메모
- UI 독립, 모바일 안전: tokio 비동기 I/O만 쓰고 TLS를 넣지 않는다. 원격 서버는 P2P 전송으로 닿는다 (`ember/client/Cargo.toml:8-11`).
- 서버 타입은 공유하지 않고 모양을 복사한다 (`ember/client/src/wire.rs:1-5`, `ember/client/src/channels.rs:1-2`). 서버 DTO가 바뀌면 여기도 손으로 고쳐야 한다.

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Client` | struct | `ember/client/src/client.rs:96` | 동기화 엔진 핸들. `Arc<Inner>` 공유, clone 저렴 |
| `ClientConfig` | struct | `ember/client/src/client.rs:35` | base URL, 캐시 경로, lease 주기(30s), backoff(250ms..30s), resync 지연(250ms), 캐시 debounce(500ms) (`client.rs:53-63`) |
| `Api` | struct | `ember/client/src/api.rs:685` | 메인 서버 `/api` HTTP 클라이언트. HTTP 또는 P2P 전송 두 경로 |
| `ApiError`, `ApiResult` | enum, type | `ember/client/src/api.rs:37`, `api.rs:179` | 에러 분류. `code()`, `status()` (`api.rs:157`, `api.rs:165`) |
| `QuestionReply`, `QuestionCallError`, `question_error_ko` | enum, fn | `ember/client/src/api.rs:64`, `api.rs:93`, `api.rs:143` | 질문 답변 본문과 고정 한국어 에러 문구 |
| `ProjectPatchError`, `HubCallError`, `EnrolCallError` | enum | `ember/client/src/api.rs:1994`, `api.rs:2271`, `api.rs:2464` | 호출별 타입화된 에러 |
| Git/GitHub/포트/메트릭/사용량/하네스/허브/등록 DTO | struct/enum | `ember/client/src/api.rs:186-656`, `api.rs:1462-1510`, `api.rs:1561-1665`, `api.rs:1900-1960`, `api.rs:2166`, `api.rs:2233-2268`, `api.rs:2352-2462` | `Api` 메서드의 응답 타입 |
| `State`, `Input`, `Changes`, `LauncherStatus`, `ConnectionState` | struct/enum | `ember/client/src/state.rs:169`, `state.rs:66`, `state.rs:96`, `state.rs:18`, `state.rs:55` | 순수 리듀서와 입력, 변경 알림 (`lib.rs:27`에서 재수출) |
| `Computer`, `Reachability`, `ProjectView`, `SessionView`, `CacheSnapshot`, `CACHE_FORMAT` | struct/enum/const | `ember/client/src/state.rs:44`, `state.rs:33`, `state.rs:138`, `state.rs:145`, `state.rs:153`, `state.rs:166` | 런처 화면용 읽기 뷰와 캐시 구조 |
| `Transcript`, `TranscriptItem`, `ApprovalState`, `QuestionState`, `Applied` | struct/enum | `ember/client/src/transcript.rs:83`, `transcript.rs:17`, `transcript.rs:43`, `transcript.rs:54`, `transcript.rs:73` | 한 세션 대화의 리듀서 |
| `wire::*` | struct/enum | `ember/client/src/wire.rs` | 서버 JSON 타입 (`SessionRecord`, `AgentEvent`, `Push`, `Project`, `TeamView`, `Schedule` 등). 팬인 28 |
| `channels::*` | struct/fn | `ember/client/src/channels.rs` | 채널 API 타입과 경로 함수 |
| `push::decode`, `push::Backoff`, `push::SKIPPED_TYPES` | fn/struct/const | `ember/client/src/push.rs:74`, `push.rs:118`, `push.rs:70` | push 프레임 해석과 재연결 backoff |
| `token::{server_token, server_token_from_env, token_allowed_for, token_allowed_for_hosts, auth_headers, bearer_header}` | fn | `ember/client/src/token.rs:15`, `token.rs:177`, `token.rs:132`, `token.rs:138`, `token.rs:168`, `token.rs:186` | 서버 토큰 탐색과 전송 허용 판정. app의 `ServerApi`, `terminal_stream`도 쓴다 (`ember/app/src/server.rs:362-375`, `ember/app/src/terminal_stream.rs:776-815`) |
| `cache::{load, save}` | fn | `ember/client/src/cache.rs:21`, `cache.rs:36` | 스냅샷 파일 읽기/원자적 쓰기 |

## `Api` 메서드 → HTTP 라우트 표

`Api::send`가 모든 경로 앞에 `/api`를 붙인다 (`ember/client/src/api.rs:781`, 전송 경로는 `api.rs:795`). 아래 "경로"는 그 뒤 부분이다. 경로 조각은 `seg()`로 퍼센트 인코딩된다 (`api.rs:1435`). 서버 쪽 라우트 위치는 `docs/analysis/_raw/routes.md`를 따른다. "app 사용"은 `ember/app/src` 안에서 `api().<이름>(` 또는 `Client`를 통한 호출을 grep으로 찾은 결과다.

### 연결, 세션

| 메서드 | 줄 | HTTP | 경로 | 본문/쿼리 | 응답 | 비고 |
|---|---|---|---|---|---|---|
| `new(base_url)` | 703 | - | - | - | `Api` | 로컬(또는 허용) 호스트면 환경에서 토큰을 읽는다 (`api.rs:705`) |
| `with_token(base_url, token)` | 711 | - | - | - | `Api` | `http(s)://`가 아니면 `BadUrl` (`api.rs:713`) |
| `over_transport(dialer, addr)` | 731 | - | - | - | `Api` | base는 `peer:<id>`, 토큰 없음 (`api.rs:733`) |
| `base_url()`, `peer()` | 737, 742 | - | - | - | - | 조회 |
| `set_power_state`, `resume_transport` | 752, 760 | - | - | - | - | 전송 경로일 때만 동작 |
| `push_url()` | 767 | - | `ws(s)://…/api/push` | - | - | 전송 경로는 `ws://ember-server/api/push` |
| `open_push()` | 863 | GET(WS) | `/push` | Bearer 헤더(HTTP 경로) | `PushSocket` | `wss://`는 지원하지 않는다 (`api.rs:869`) |
| `health()` | 896 | GET | `/health` | - | `Health` | push 연결 전 프로브 (`client.rs:561`) |
| `agents()` | 900 | GET | `/agents` | - | `Vec<DetectedAgent>` | |
| `sessions(project)` | 905 | GET | `/sessions[?project=]` | - | `Vec<SessionRecord>` | |
| `session(id)` | 915 | GET | `/sessions/{id}` | - | `SessionDetail` | |
| `create_session(new)` | 919 | POST | `/sessions` | `NewSession` | `SessionRecord` | |
| `events(id, after)` | 925 | GET | `/sessions/{id}/events?after=` | - | `Vec<StoredEvent>` | gap 복구 (`client.rs:429`) |
| `send_message(id, text)` | 929 | POST | `/sessions/{id}/messages` | `{text}` | `()` | |
| `answer(id, approval_id, decision)` | 934 | POST | `/sessions/{id}/approvals/{approval_id}` | `{decision}` | `()` | |
| `answer_question(id, qid, reply)` | 943 | POST | `/sessions/{id}/questions/{qid}/answer` | `{answers}` 또는 `{decline:true}` (`api.rs:84-89`) | `()` | |
| `set_approve_all(id, enabled)` | 950 | PUT | `/sessions/{id}/approve-all` | `{enabled}` | `()` | |
| `interrupt(id)` | 956 | POST | `/sessions/{id}/interrupt` | `{}` | `()` | |
| `lease(id)` | 962 | POST | `/sessions/{id}/lease` | `{}` | `Lease{ttl_secs}` | `Client::open_session`이 주기 호출 |
| `patch_session(id, patch)` | 1344 | PATCH | `/sessions/{id}` | `SessionPatch` | `SessionRecord` | |
| `search(query, limit)` | 1350 | GET | `/search?q=&limit=` | - | `Vec<SearchHit>` | |
| `usage(days)` | 1361 | GET | `/usage[?days=]` | - | `Vec<DailyUsage>` | app 사용 |
| `export_session(id)` | 1366 | GET | `/sessions/{id}/export` | - | `serde_json::Value` | app 사용 |
| `fork_session(id, turn_seq)` | 1372 | POST | `/sessions/{id}/fork` | `{turn_seq?}` (`api.rs:148`) | `SessionRecord` | |
| `session_team(id)` | 1380 | GET | `/sessions/{id}/team` | - | `Option<TeamView>` | |
| `team(team_id)` | 1384 | GET | `/teams/{team_id}` | - | `TeamView` | 저장소 안 호출 1곳 [확인 필요: 실제 UI 사용 여부] |
| `team_mail(team_id, after, limit)` | 1390 | GET | `/teams/{team_id}/mail?after=&limit=` | - | `Vec<TeamMail>` | |
| `end_teammate(team_id, session_id)` | 1400 | POST | `/teams/{team_id}/members/{session_id}/end` | `{}` | `TeamMember` | |
| `mention_candidates(id, q, limit)` | 1407 | GET | `/sessions/{id}/mentions?q=&limit=` | - | `Vec<MentionCandidate>` | |
| `usage_summary(period, project)` | 1979 | GET | `/usage/summary?days=\|day=&project=` (`api.rs:1964`) | - | `UsageSummary` | app 사용 |
| `session_usage(id)` | 1984 | GET | `/sessions/{id}/usage` | - | `SessionUsage` | `ember/` 안 호출 없음 (테스트 제외) |

### 프로젝트, GitHub

| 메서드 | 줄 | HTTP | 경로 | 본문 | 응답 | 비고 |
|---|---|---|---|---|---|---|
| `github_summary()` | 970 | GET | `/integrations/github` | - | `GithubSummary` | 서버가 90초 캐시 |
| `projects()` | 975 | GET | `/projects` | - | `Vec<Project>` | |
| `create_project(name)` | 980 | POST | `/projects` | `{name}` | `Project` | |
| `assign_computer(project, cid)` | 985 | PUT | `/projects/{name}/computers/{cid}` | 없음 | `Project` | |
| `unassign_computer(project, cid)` | 991 | DELETE | `/projects/{name}/computers/{cid}` | 없음 | `Project` | |
| `patch_project(name, patch)` | 2038 | PATCH | `/projects/{name}` | `ProjectPatch` | `Project` | 에러는 `ProjectPatchError` (`api.rs:2023`) |

### Git (`POST /projects/{name}/git/{op}`, 서버가 `repo`를 채워 노드로 넘긴다)

모든 git 호출은 `git_post`(`ember/client/src/api.rs:999`)를 지난다. 노드 쪽 처리는 [node-git](node-git.md) 참고.

| 메서드 | 줄 | `op` | 본문 | 응답 |
|---|---|---|---|---|
| `git_raw(project, op, body)` | 1006 | 임의 | 그대로 | `serde_json::Value` (204는 `Null`). app의 VCS 화면이 이것만 쓴다 (`ember/app/src/ui/vcs.rs:1142`) |
| `git_status` | 1016 | `status` | `{}` | `GitStatus` |
| `git_diff` | 1021 | `diff` | `{path, staged}` (`api.rs:644`) | `GitDiff` |
| `git_diff_untracked` | 1027 | `diff` | `{path:null, staged:false, include_untracked:true}` | `GitDiff` |
| `git_stage` / `git_unstage` | 1032 / 1038 | `stage` / `unstage` | `{paths}` | `()` |
| `git_apply` | 1044 | `apply` | `{patch, reverse}` | `()` |
| `git_commit` | 1050 | `commit` | `{summary, description, amend}` (`api.rs:654`) | `GitCommitted` |
| `git_checkout` | 1061 | `checkout` | `{branch}` | `()` |
| `git_branch` | 1067 | `branch` | `{name, from}` | `()` |
| `git_fetch` / `git_pull` / `git_push` | 1072 / 1077 / 1081 | `fetch` / `pull` / `push` | `{remote}` | `GitOutput` |
| `git_conflicts` | 1086 | `conflicts` | `{}` | `GitConflicts` |
| `git_log` | 1091 | `log` | `{limit, skip, branch}` | `GitLog` |
| `git_commit_show` | 1096 | `commit/show` | `{sha}` | `GitCommitDetail` |
| `git_revert` / `git_cherry_pick` | 1101 / 1106 | `revert` / `cherry-pick` | `{sha, confirm:true}` | `GitCommitApplied` |
| `git_merge_state` | 1111 | `merge` | `{}` | `GitMergeState` |
| `git_merge_abort` | 1116 | `merge/abort` | `{confirm:true}` | `GitMergeAborted` |
| `git_merge_commit` | 1121 | `merge/commit` | `{confirm:true}` | `GitCommitApplied` |
| `git_branches` | 1126 | `branches` | `{}` | `GitBranches` |
| `git_prs` | 1132 | `prs` | `{state, limit}` | `GitPrs` |
| `git_pr` | 1137 | `pr` | `{number}` | `GitPrDetail` |
| `git_pr_review` | 1143 | `pr/review` | `{number, action, body, confirm:true}` | `GitPrReviewed` |
| `git_pr_merge` | 1151 | `pr/merge` | `{number, method, delete_branch, head_sha, confirm:true}` | `GitPrMerged` |
| `git_pr_create` | 1157 | `pr/create` | `{title, body, base, head, draft, confirm:true}` | `GitPrCreated` |
| `git_stash_list` | 1161 | `stash/list` | `{}` | `Vec<GitStashEntry>` |
| `git_stash_push` | 1165 | `stash/push` | `{message, include_untracked}` | `()` |
| `git_stash_apply` / `_pop` / `_drop` | 1170 / 1175 / 1180 | `stash/apply` / `stash/pop` / `stash/drop` | `{index}` | `()` |
| `git_conflict` | 1185 | `conflict` | `{path}` | `GitConflict` |
| `git_resolve` | 1189 | `resolve` | `{path, content}` | `()` |

타입 있는 `git_*` 메서드는 `ember/app/src`에서 직접 부르는 곳이 없다 (grep `\.git_status(` 등 0건). 테스트(`ember/client/tests/git_flow.rs`)만 쓴다.

### 채널, 초대, 게스트

| 메서드 | 줄 | HTTP | 경로 | 본문 | 응답 |
|---|---|---|---|---|---|
| `channels(project)` | 1197 | GET | `/channels[?project=]` (`channels.rs:330`) | - | `Vec<Channel>` |
| `create_channel(new)` | 1202 | POST | `/channels` | `NewChannel` | `Channel` |
| `channel(id)` | 1208 | GET | `/channels/{id}` | - | `Channel` |
| `channel_messages(id, q)` | 1213 | GET | `/channels/{id}/messages[?after=]` (`channels.rs:338`) | - | `Vec<ChannelMessage>` |
| `post_channel_message(id, new)` | 1217 | POST | `/channels/{id}/messages` | `NewChannelMessage` | `ChannelMessage` |
| `preview_channel_mentions(id, text)` | 1223 | POST | `/channels/{id}/mentions/preview` | `{text}` | `MentionPreview` (app 호출 없음) |
| `mark_channel_read(id, upto)` | 1229 | POST | `/channels/{id}/read` | `{seq?}` | `Channel` |
| `guest_door()` | 1236 | GET | `/guest-door` (`channels.rs:85`) | - | `GuestDoorState` |
| `channel_feed(id)` | 1242 | GET | `/channels/{id}/feed` | - | `Vec<FeedItem>` (app 호출 없음) |
| `answer_channel_feed(id, aid, d)` | 1247 | POST | `/channels/{id}/feed/{aid}/answer` | `{decision}` | `()` (app 호출 없음) |
| `create_invite(channel, ttl)` | 1257 | POST | `/channels/{id}/invites` | `{ttl_hours?}` | `CreatedInvite` (토큰은 이 응답에만) |
| `invites(channel)` | 1263 | GET | `/channels/{id}/invites` | - | `Vec<Invite>` |
| `revoke_invite(channel, iid)` | 1268 | DELETE | `/channels/{id}/invites/{iid}` | - | `()` |
| `guests(channel)` | 1274 | GET | `/channels/{id}/guests` | - | `Vec<Guest>` |
| `remove_guest(channel, gid)` | 1279 | DELETE | `/channels/{id}/guests/{gid}` | - | `()` |
| `set_allowance(channel, gid, hours)` | 1285 | PUT | `/channels/{id}/guests/{gid}/allow` | `{hours}` | `Allowance` |
| `clear_allowance(channel, gid)` | 1292 | DELETE | `/channels/{id}/guests/{gid}/allow` | - | `()` |

서버에는 있지만 클라이언트가 감싸지 않은 채널 라우트: `POST /api/channels/{id}/post`, `POST /api/channels/{id}/questions/{question_id}/answer` (`docs/analysis/_raw/routes.md`의 `ember/server/src/channels/api.rs:153`, `:158`).

### 스케줄

| 메서드 | 줄 | HTTP | 경로 | 본문 | 응답 |
|---|---|---|---|---|---|
| `schedules(project)` | 1300 | GET | `/schedules[?project=]` | - | `Vec<Schedule>` |
| `create_schedule(new)` | 1307 | POST | `/schedules` | `NewSchedule` | `Schedule` |
| `update_schedule(id, patch)` | 1312 | PATCH | `/schedules/{id}` | `SchedulePatch` | `Schedule` |
| `delete_schedule(id)` | 1317 | DELETE | `/schedules/{id}` | - | `()` (app 호출 없음) |
| `pause_schedule` / `resume_schedule` | 1322 / 1326 | POST | `/schedules/{id}/pause` / `/resume` | `{}` | `Schedule` |
| `run_schedule(id)` | 1331 | POST | `/schedules/{id}/run` | `{}` | `ScheduleRun` (서버 202) |
| `schedule_runs(id, limit)` | 1336 | GET | `/schedules/{id}/runs[?limit=]` | - | `Vec<ScheduleRun>` |

### 컴퓨터, 허브, 등록

| 메서드 | 줄 | HTTP | 경로 | 본문 | 응답 |
|---|---|---|---|---|---|
| `computer_ports(cid)` | 1514 | GET | `/computers/{id}/ports` | - | `Ports` |
| `metrics(cid, top)` | 1669 | GET | `/computers/{id}/metrics?top=` | - | `MetricsSample` |
| `detect_harnesses(cid)` | 2187 | POST | `/computers/{id}/harnesses/detect` | `{}` | `Vec<DetectedHarness>` (다른 컴퓨터는 501) |
| `hub_devices()` | 2302 | GET | `/hub/devices` | - | `Vec<HubDevice>`, 503은 `HubCallError::Off` (`api.rs:2285-2293`) |
| `enrol_mint(name)` | 2542 | POST | `/computers/enrol-codes` | `{name}` | `EnrolMinted` |
| `enrol_status(id)` | 2546 | GET | `/computers/enrol-codes/{id}` | - | `EnrolStatus` |
| `enrol_confirm(id, name, fp)` | 2552 | POST | `/computers/enrol-codes/{id}/confirm` | `{name, expect_fingerprint?}` | `EnrolConfirmed` |
| `enrol_deny(id)` | 2556 | POST | `/computers/enrol-codes/{id}/deny` | `{}` | `()` |
| `enrol_cancel(id)` | 2562 | DELETE | `/computers/enrol-codes/{id}` | - | `()` |

`app`이 `ember-client`로 감싸지 않고 자체 `ServerApi`로 부르는 서버 API(계정, 컴퓨터 목록, IDE 대상 등)는 `ember/app/src/server.rs:1-10`에 TODO로 적혀 있다.

## 파일별 요약

### `ember/client/src/api.rs` (약 2,653줄)
- **목적:** 메인 서버 `/api` HTTP 클라이언트. 같은 메서드가 TCP(`reqwest`)와 P2P 전송(hyper over stream) 두 경로로 동작한다 (`api.rs:1-9`, `api.rs:678-681`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SERVER_SERVICE` | const(pub) | 31 | 전송 서비스 이름 `"ember-server"`. 서버의 같은 상수와 맞춰야 한다 |
  | `PEER_HOST` | const | 34 | 전송 경로 요청의 Host `"ember-server"` |
  | `ApiError` | enum(pub) | 37 | `Transport`, `Peer`, `Status{status,message,code}`, `Unauthorized`, `NotAMember`, `Decode`, `Push`, `BadUrl` |
  | `Reach` | enum | 678 | `Http(reqwest::Client)` 또는 `Peer{dialer, addr}` |
  | `Api` | struct(pub) | 685 | `reach`, `base`, `auth`(민감 표시된 헤더) |
  | `Api::send` | 함수 | 778 | 모든 요청의 공통 경로. 전송 경로는 요청마다 새 bi 스트림 + HTTP/1 핸드셰이크 (`api.rs:790-792`) |
  | `Api::check` | 함수 | 813 | 비성공 응답을 `ApiError`로. 401은 `Unauthorized`, 400 `not_a_member`는 `NotAMember` |
  | `Api::open_push` | 함수(pub) | 863 | push WebSocket. HTTP 경로는 `TcpStream`에 직접 붙고 `ws://`만 지원 |
  | `seg` | 함수(crate) | 1435 | 경로 조각 퍼센트 인코딩 |
  | `authority_addr` | 함수 | 1418 | `host:port` 분해(IPv6 괄호 제거, 기본 80) |
  | `QuestionCallError::text_ko` | 함수(pub) | 130 | 질문 답변 실패의 고정 한국어 문구 |
  | `ProjectPatchError::from_answer` | 함수(crate) | 2023 | `{error, code}` 본문 해석 |
  | `EnrolCallError` `From<ApiError>` | impl | 2499 | 409의 `message`(서버 본문의 `error` 키)로 세부 종류를 고른다 |
- **입력 → 출력:** 메서드 인자 → JSON 요청 → 서버 응답을 타입으로 디코드하거나 `ApiError`.
- **의존:** `ember/client/src/wire.rs`, `ember/client/src/channels.rs`, `ember/client/src/token.rs`, `ember-transport`.
- **사용처:** `ember/client/src/client.rs:25`, app 전반(`ember/app/src/services.rs`, `ember/app/src/ui/**`). 팬인 27 (`docs/analysis/_raw/fan.tsv`).
- **부수효과:** 네트워크(HTTP, WebSocket, P2P 스트림). 상태를 갖지 않는다.
- **주의점:**
  - 토큰은 `Reach::Http`에서만 붙는다. 전송 경로는 기기 키로 인증한다 (`api.rs:689-692`, `api.rs:890`).
  - `open_push`는 `wss://`를 거부한다 (`api.rs:867-869`). `https://` base로 만든 `Api`는 HTTP 호출은 되지만 push는 실패한다.
  - `EnrolCallError`는 `code`가 아니라 `message`로 분기한다 (`api.rs:2504-2509`). 등록 라우트가 `{"error": "<key>", "message": ...}` 모양으로 답하기 때문이다 (`ember/server/src/computers/enrol.rs:1446-1448`). 다른 라우트는 `{error, code}`를 쓰므로 두 규칙이 섞여 있다.
  - `ProjectPatchError`는 `Api::check`를 거치지 않고 직접 해석한다 (`api.rs:2040-2043`). 400 `not_a_member` 처리 같은 공통 규칙이 적용되지 않는다.
- 테스트: 39개. 경로 인코딩, 토큰 헤더 유무, 401/409/503 매핑, DTO 디코드 관용성.

### `ember/client/src/client.rs` (약 608줄)
- **목적:** 동기화 엔진. push 소켓 유지(지수 backoff), 재연결과 `lagged` 뒤 gap 복구, 열린 세션 lease 갱신, 캐시 debounce 쓰기 (`client.rs:1-12`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Client::new(config)` | 함수(pub) | 103 | `Api::new` + 캐시 로드. 네트워크는 아직 안 쓴다 |
  | `Client::with_api(config, api)` | 함수(pub) | 110 | 준비된 `Api`(예: `over_transport`) 사용 |
  | `Client::start` | 함수(pub) | 138 | push 루프, resync 워커, 캐시 writer 시작. `resync_rx`를 `take`하므로 한 번만 동작 |
  | `Client::stop` | 함수(pub) | 149 | 모든 태스크와 lease 중단, 상태는 `Offline` |
  | `pause_push` / `resume_push` / `reconnect_push` | 함수(pub) | 160 / 170 / 180 | 백그라운드 전환, 복귀, 네트워크 변경 |
  | `read` / `subscribe` / `watch_revision` / `api` / `apply` | 함수(pub) | 189 / 194 / 199 / 203 / 208 | UI 바인딩 |
  | `open_session` / `close_session` | 함수(pub) | 221 / 240 | 세션 열기(lease 주기 갱신 태스크 생성) |
  | 액션 래퍼 | 함수(pub) | 249-382 | `create_session`, `send_message`, `answer`, `answer_question`, `set_approve_all`, `load_approve_all`, `fork_session`, `load_fork_info`, `interrupt`, `agents`, `patch_session`, `load_projects`, `patch_project`, `assign_computer`, `unassign_computer`, `search`, `load_team`, `team_mail`, `end_teammate`, `mention_candidates` |
  | `refresh` | 함수(pub) | 385 | `Resync::All` 요청 |
  | `Inner::apply` | 함수 | 391 | 리듀서 호출 후 `Changes`에 따라 resync/persist/revision/broadcast |
  | `Inner::resync_all` | 함수 | 443 | 세션 목록, 프로젝트(404는 무시), 열린 세션 이벤트와 팀 재조회 |
  | `resync_worker` | 함수 | 472 | 요청 묶기(coalesce). 실패하면 push 재연결 |
  | `cache_writer` | 함수 | 508 | `persist` 알림마다 저장 후 debounce 대기 |
  | `push_loop` / `connect_and_run` | 함수 | 525 / 556 | `/health` 프로브 → push 열기 → 메시지 루프 |
- **입력 → 출력:** 서버 push, API 응답 → `State` 갱신 → `Changes` broadcast와 revision watch.
- **의존:** `ember/client/src/api.rs`, `cache.rs`, `push.rs`, `state.rs`, `wire.rs`, `ember_transport::PowerState`.
- **사용처:** `ember/client/src/lib.rs:26`(재수출), `ember/app/src/services.rs`, `ember/app/src/lib.rs` [app 쪽 상세는 app-core 문서].
- **부수효과:** tokio 태스크 생성, 네트워크, 캐시 파일 쓰기, `tracing` 로그.
- **주의점:**
  - `stop()` 뒤 `start()`는 아무것도 하지 않는다. `resync_rx`가 이미 `take`되어 `None`이기 때문이다 (`client.rs:139`). 재시작하려면 새 `Client`가 필요하다.
  - 연결 직후 `Resync::All`을 두 번 보낸다(즉시, `resync_settle` 뒤). 서버가 업그레이드 완료 뒤에야 구독하기 때문이다 (`client.rs:44-47`, `client.rs:573-580`).
  - lease 태스크는 `interval`의 첫 tick이 즉시 오므로 열자마자 한 번 lease를 보낸다 (`client.rs:226-233`). 실패는 debug 로그만 남긴다.
  - resync 실패는 push 재연결로 바뀐다 (`client.rs:500-504`). 404는 실패로 치지 않는다 (`client.rs:459`, `client.rs:492`).
  - `pause_push`에 OS 저전력 모드 연결이 TODO로 남아 있다 (`client.rs:164`, #229).
- 테스트: 파일 안 0개. `ember/client/tests/server_flow.rs`, `transport_flow.rs` 등이 통합으로 검증한다.

### `ember/client/src/state.rs` (약 1,016줄)
- **목적:** 메인 서버에 대한 클라이언트 전체 뷰를 순수 리듀서로 유지한다. I/O 없음 (`state.rs:1-6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `LauncherStatus` | enum(pub) | 18 | 서버 상태 + `FinishedUnread` |
  | `Reachability`, `Computer` | enum/struct(pub) | 33, 44 | 컴퓨터 목록(FR-L3) |
  | `ConnectionState` | enum(pub) | 55 | `Offline`, `Connecting`, `Connected`, `Reconnecting` |
  | `Input` | enum(pub) | 66 | 리듀서 입력 14종 |
  | `Changes` | struct(pub) | 96 | 다시 그릴 부분과 resync 요청 |
  | `CacheSnapshot`, `CACHE_FORMAT=1` | struct/const(pub) | 153, 166 | 디스크 캐시 구조 |
  | `State` | struct(pub) | 169 | 세션, 대화, 열린 세션, `last_seen`, 프로젝트, 팀, approve-all, fork 정보, 연결 상태, revision |
  | `State::apply` | 함수(pub) | 348 | 리듀서 본체 |
  | `upsert` | 함수 | 489 | 더 새 레코드(`last_seq` 큰 쪽)를 지킨다 |
  | `on_event` | 함수 | 520 | 이벤트로 레코드와 대화를 갱신, 모르는 세션이면 `resync_all` |
  | `put_team` / `unlink_session` | 함수 | 562 / 580 | 팀 색인 |
  | `derive_computer_projects` | 함수 | 588 | 프로젝트 배정에서 컴퓨터별 프로젝트 목록 계산 |
  | `mark_seen` | 함수 | 608 | `last_seen`을 레코드의 `last_seq`로 |
- **입력 → 출력:** `Input` → 내부 상태 변경 + `Changes`.
- **의존:** `ember/client/src/transcript.rs`, `ember/client/src/wire.rs`.
- **사용처:** `ember/client/src/client.rs:28`, `ember/client/src/cache.rs:9`, app(`ember/app/src/model.rs`, `ember/app/src/ui/**`). 팬인 18.
- **부수효과:** 없음(순수).
- **주의점:**
  - `SessionsLoaded`는 upsert만 하고 지우지 않는다 (`state.rs:351-354`). 서버에서 사라진 세션은 캐시와 상태에 남는다 [확인 필요: 서버에 세션 삭제 API가 있는지].
  - 첫 목록 로드 전(`baselined == false`)에는 기존 기록을 읽음으로 친다 (`state.rs:491-495`). 캐시에 `baselined`가 저장되어 콜드 스타트 뒤에도 유지된다.
  - `SessionUpdated` push는 제목, 핀, 보관만 받는다 (`wire.rs:200-206`). 활동 필드는 이벤트가 소유한다.
  - 팀, approve-all, fork 정보는 캐시하지 않는다 (`state.rs:181-190`).
  - `ChannelMessage` push는 리듀서가 무시한다 (`state.rs:434-435`). 채널 UI가 API로 직접 읽는다.
- 테스트: 16개. 상태 전이, finished-unread 유지, gap resync, 프로젝트-컴퓨터 파생, 팀 색인, 이름 변경.

### `ember/client/src/transcript.rs` (약 471줄)
- **목적:** 한 세션의 대화를 저장된 이벤트에서 순서대로 줄인다. 중복은 무시, 앞선 이벤트는 보류하고 gap으로 보고 (`transcript.rs:1-6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `TranscriptItem` | enum(pub) | 17 | `User`, `Assistant{streaming}`, `ToolCall`, `Approval`, `Question`, `TurnEnded`, `Error`, `Notice` |
  | `ApprovalState`, `QuestionState` | enum(pub) | 43, 54 | `Pending`, `Resolved`/`Answered`/`Skipped`, `Abandoned`, `Withdrawn` |
  | `Usage` | struct(pub) | 66 | 누적 토큰 |
  | `Applied` | enum(pub) | 73 | `Changed`, `Duplicate`, `Gap{expected}` |
  | `Transcript` | struct(pub) | 83 | `items`, `usage`, `last_seq`, 보류 버퍼와 색인 |
  | `apply_seq` | 함수(pub) | 130 | 순서 규칙 |
  | `reduce` | 함수 | 145 | 이벤트별 변환. `TurnEnded`가 남은 승인과 질문을 `Abandoned`로 (`transcript.rs:253-263`) |
  | `pending_approvals`, `pending_questions`, `has_gap` | 함수(pub) | 108, 115, 122 | 조회 |
- **입력 → 출력:** `StoredEvent` → `items` 변경 + `Applied`.
- **의존:** `ember/client/src/wire.rs`.
- **사용처:** `ember/client/src/state.rs:12`, app 대화 화면 (`ember/app/src/ui/cr/conversation.rs` 등). 팬인 7.
- **부수효과:** 없음.
- **주의점:**
  - 보류 버퍼 `held`에 상한이 없다 (`transcript.rs:90`, `transcript.rs:135`). gap이 메워지지 않으면 계속 쌓인다.
  - `Notice`는 스트리밍을 끝내지 않는다 (`transcript.rs:268-271`). `Error`도 끝내지 않는다 (`transcript.rs:265-267`).
- 테스트: 11개. delta 조립, 순서 보장, 중복, 승인/질문 상태 전이.

### `ember/client/src/wire.rs` (약 756줄)
- **목적:** 메인 서버 JSON 타입을 클라이언트 쪽에 복사한 것. 알 수 없는 이벤트 종류와 상태는 `Unknown`으로 받는다 (`wire.rs:1-5`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `EmberOseConnection`, `EmberLaunch` | struct(pub) | 11, 25 | 에디터 실행 정보. `Debug`가 `connection_token`을 가린다 (`wire.rs:16-21`) |
  | `AgentEvent` | enum(pub) | 67 | `kind` 태그. `#[serde(other)] Unknown` |
  | `Question`, `QuestionOption`, `QuestionAnswer` | struct(pub) | 97, 113, 122 | `QuestionAnswer`의 `Debug`는 값을 `***`로 |
  | `ApprovalDecision`, `TurnOutcome` | enum(pub) | 139, 147 | `Unknown` 변형이 없다 |
  | `SessionStatus` | enum(pub) | 157 | `idle`, `running`, `waiting_for_approval`, `finished`, `failed`, `Unknown` |
  | `SessionRecord` (+`take_meta`) | struct(pub) | 169 (200) | 세션 레코드 |
  | `Project`, `MemberDefaults`, `ProjectPatch`, `SessionPatch` | struct(pub) | 211, 247, 266, 292 | 프로젝트 설정(FR-L26) |
  | `DailyUsage`, `SearchHit`, `SNIPPET_OPEN/CLOSE` | struct/const(pub) | 304, 331, 325-327 | 사용량, 검색. 표식 문자 `«` `»` |
  | `StoredEvent`, `SessionDetail`, `ForkOrigin`, `ForkInfo` | struct(pub) | 356, 365, 384, 394 | 이벤트와 세션 상세 |
  | `DetectedAgent`, `NewSession` | struct(pub) | 408, 423 | |
  | `Push` | enum(pub) | 435 | push 메시지 8종 |
  | `TeamRole`, `TaskStatus`, `TeamMember`, `TeamTask`, `TeamView`, `TeamMail`, `MentionCandidate` | enum/struct(pub) | 457-582 | 팀과 멘션 |
  | `ScheduleKind`, `ScheduleTarget`, `Schedule`, `RunStatus`, `ScheduleRun`, `NewSchedule`, `SchedulePatch` | enum/struct(pub) | 597-702 | 스케줄 |
- **입력 → 출력:** serde 직렬화/역직렬화 타입만 있다.
- **의존:** `ember/client/src/channels.rs` (`Push::ChannelMessage`, `wire.rs:450`).
- **사용처:** 팬인 28. `api.rs`, `state.rs`, `push.rs`, `transcript.rs`, `client.rs`, app 전반, `ember/app/src/server.rs:15`.
- **부수효과:** 없음.
- **주의점:**
  - `ApprovalDecision`, `TurnOutcome`에는 `#[serde(other)]`가 없다 (`wire.rs:137-151`). 서버가 새 값을 보내면 그 이벤트가 든 `events` 응답 전체가 `Decode` 에러가 된다. 파일 머리의 "관용 디코드" 원칙과 어긋난다.
  - 서버 타입과 짝: `ember/server/src/{events,store}.rs` (`wire.rs:1`). 한쪽만 바꾸면 조용히 필드가 빠진다.
- 테스트: 5개. OSE 연결 왕복과 토큰 가림, 질문 디코드와 `Debug` 가림.

### `ember/client/src/channels.rs` (약 605줄)
- **목적:** 채널 API 타입과 경로 함수 (`channels.rs:1-2`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `USER` | const(pub) | 7 | 사람 작성자 `from` 값 `"user"` |
  | `Member`, `ChannelMessage`, `Channel`, `ChannelGuest` | struct(pub) | 11, 24, 47, 68 | 채널 모델 |
  | `NewInvite`, `GUEST_DOOR_PATH`, `GuestDoorState`, `CreatedInvite`, `Invite`, `Guest`, `AllowanceBody`, `Allowance` | struct/const(pub) | 77-176 | 초대와 게스트 |
  | `invites_path` .. `guest_allow_path` | 함수(pub) | 179-201 | 경로 생성 |
  | `new_invite_body` | 함수(pub) | 204 | TTL 없으면 `{}` |
  | `NewChannel`, `MessagesQuery`, `NewChannelMessage`, `ReadBody` | struct(pub) | 209-237 | 요청 본문 |
  | `FeedAgent`, `FeedItem`, `FeedDecision`, `FeedAnswer` | struct/enum(pub) | 241-290 | 피드 |
  | `MentionPreviewRequest`, `MentionTarget`, `MentionPreview` | struct(pub) | 294-312 | 멘션 미리보기 |
  | `mentions_preview_path`, `feed_path`, `feed_answer_path`, `list_path`, `messages_path` | 함수(crate) | 315-345 | 경로 생성 |
- **의존:** `ember/client/src/api.rs` (`seg`).
- **사용처:** `ember/client/src/api.rs:27`, `ember/client/src/push.rs:59`, `ember/client/src/wire.rs:450`, app 채널 화면.
- **부수효과:** 없음.
- **주의점:** `FeedDecision`(`channels.rs:278`)은 `wire::ApprovalDecision`(`wire.rs:139`)과 같은 세 값을 다시 정의한다.
- 테스트: 22개. 경로, 본문 모양, 디코드 관용성.

### `ember/client/src/token.rs` (약 408줄)
- **목적:** 서버 토큰(FR-S11) 탐색과, 토큰을 보내도 되는 호스트 판정 (`token.rs:1-6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `server_token(env, data_dir, home)` | 함수(pub) | 15 | 우선순위: 환경 변수 → `<data_dir>/server-token` → `<home>/.ember/server-token`. 첫 줄만, trim |
  | `read_token_file_with` | 함수 | 61 | 심볼릭 링크, FIFO, 비정규 파일 거부. 열린 핸들과 경로의 dev/inode 비교, 권한 `0o077` 거부, 폴더 소유자 일치 (unix) |
  | `O_NONBLOCK` | const(unix) | 51 | `libc` 없이 플랫폼별 값을 직접 적는다 |
  | `token_allowed_for` / `token_allowed_for_hosts` | 함수(pub) | 132 / 138 | loopback, `localhost`, 또는 `EMBER_TOKEN_HOSTS` 항목 |
  | `entry_matches` | 함수 | 151 | 맨 호스트는 `https`만, 스킴이 있으면 스킴/호스트/포트 정확히 일치 |
  | `auth_headers` | 함수(pub) | 168 | `Authorization: Bearer`, 민감 표시 |
  | `server_token_from_env` | 함수(pub) | 177 | `EMBER_SERVER_TOKEN`, `EMBER_DATA_DIR`, `HOME` |
  | `bearer_header` | 함수(pub) | 186 | `"Bearer {token}"` |
- **사용처:** `ember/client/src/api.rs:705`, `api.rs:718-720`, `ember/app/src/server.rs:362-375`, `ember/app/src/terminal_stream.rs:776-815`.
- **부수효과:** 파일 읽기(최대 64KiB, `token.rs:117`), 환경 변수 읽기, 거부 사유 `warn` 로그(토큰 값은 남기지 않는다).
- **주의점:**
  - 홈 경로를 `HOME`에서만 찾는다 (`token.rs:181`). Windows에서는 보통 `HOME`이 없어 `~/.ember/server-token` 대체가 동작하지 않을 수 있다 [확인 필요: Windows에서 서버가 토큰 파일을 어디에 쓰는지].
  - 권한과 소유자 검사는 `#[cfg(unix)]`에만 있다 (`token.rs:101-114`). Windows는 파일 종류 검사만 한다.
- 테스트: 14개. 우선순위, trim, 헤더 민감 표시, 호스트 허용 규칙, 권한/심볼릭 링크/FIFO/경로 바꿔치기 거부.

### `ember/client/src/push.rs` (약 289줄)
- **목적:** push 텍스트 프레임 해석과 재연결 backoff (`push.rs:1-4`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `DecodeError` | enum(pub) | 13 | `UnknownType`, `Skipped`, `Malformed` |
  | `SKIPPED_TYPES` | const(pub) | 70 | `schedule_created`, `schedule_updated`, `schedule_deleted`, `schedule_run`: 알지만 쓰지 않는 종류 |
  | `decode(text)` | 함수(pub) | 74 | `type`별로 `Push` 생성. 처리 종류: `session_created`, `event`, `session_updated`, `project_updated`, `team_updated`, `approve_all`, `channel_message`, `lagged` |
  | `Backoff` | struct(pub) | 118 | `min`부터 2배씩, `max` 상한, ±12.5% 지터(현재 시각 나노초로, RNG 없음) |
- **사용처:** `ember/client/src/client.rs:27`, `client.rs:584`.
- **부수효과:** 없음(`SystemTime::now` 읽기만).
- **주의점:** 모듈 문서는 "버전 확인"을 말하지만 (`lib.rs:5`) 프로토콜에는 버전이 없다 (`push.rs:3`). `lib.rs` 설명이 낡았다.
- 테스트: 8개. 각 push 종류 디코드, 알 수 없는 종류와 필드, backoff 증가와 상한.

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/client/Cargo.toml` | 33 | `ember-client` 크레이트. 의존: `ember-transport`(`http` 기능), `reqwest`(json, TLS 없음), `hyper` http1, `tokio-tungstenite`, `serde_urlencoded`. dev: `ember-server`, `axum`, `tempfile` (`Cargo.toml:12-33`) |
| `ember/client/src/lib.rs` | 27 | 모듈 선언과 `Client`, `ClientConfig`, `Changes`, `ConnectionState`, `Input`, `LauncherStatus`, `State` 재수출 (`lib.rs:16-27`) |
| `ember/client/src/cache.rs` | 95 | `load`(`cache.rs:21`): 없거나 깨지거나 형식이 다르면 `None`. `save`(`cache.rs:36`): 부모 폴더 생성, 프로세스 id와 순번이 붙은 임시 파일(`cache.rs:52-58`)에 쓰고 rename. 테스트 2개(동시 저장, 손상 내성) |

## 이 모듈을 수정할 때 주의할 점

- **서버 DTO와 두 번 정의된 곳.** `wire.rs`, `channels.rs`, `api.rs`의 DTO는 서버 타입의 손 복사본이다 (`wire.rs:1-5`, `channels.rs:1-2`). 서버 필드를 바꾸면 여기도 고치고, 새 필드는 `#[serde(default)]`로 받아야 구버전 서버와 맞는다.
- **`SERVER_SERVICE`는 서버의 `ember_server::transport::SERVER_SERVICE`와 같은 문자열이어야 한다** (`api.rs:30-31`). 한쪽만 바꾸면 전송 경로가 끊긴다.
- **에러 본문 규칙이 둘이다.** 대부분 `{error, code}`(`api.rs:818-832`), 등록 라우트는 `{error: <key>, message}`(`api.rs:2504-2509`). 서버 쪽 형식을 바꾸면 `EnrolCallError` 매핑이 조용히 `Api(..)`로 떨어진다.
- **확인 문구 없는 위험 호출.** `git_revert`, `git_cherry_pick`, `git_merge_*`, `git_pr_review`, `git_pr_merge`, `git_pr_create`는 `confirm: true`를 항상 보낸다 (`api.rs:1102`, `api.rs:1144`, `api.rs:1152`, `api.rs:1158`). 사람의 확인은 UI가 먼저 받아야 한다.
- **app은 git을 `git_raw`로만 부른다** (`ember/app/src/ui/vcs.rs:1142`). 타입 있는 `git_*`의 시그니처를 바꿔도 app은 깨지지 않지만, 본문 모양을 바꾸면 app이 직접 만든 본문과 어긋난다.
- **토큰 전송 범위.** `Api::with_token`은 토큰이 있어도 허용 호스트가 아니면 버린다 (`api.rs:717-720`). 새 요청 경로를 만들면 `auth` 헤더 처리(`api.rs:722-724`, `api.rs:890-892`)를 똑같이 따라야 한다.
- **리듀서는 순수해야 한다.** `State::apply`에 I/O를 넣지 말고, 필요한 재조회는 `Changes.resync`/`resync_all`로 요청한다 (`state.rs:94-115`, `client.rs:400-405`).
- **캐시 형식.** `CacheSnapshot`에 필드를 더하면 `#[serde(default)]`를 붙이거나 `CACHE_FORMAT`을 올린다 (`state.rs:161-166`, `cache.rs:24`). 형식이 다르면 캐시는 버려진다.
