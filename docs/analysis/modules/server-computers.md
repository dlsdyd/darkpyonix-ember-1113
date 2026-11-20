# 모듈: server-computers

- 경로: `ember/server/src/computers/` (`enrol.rs` 제외), `ember/server/src/devices/`, `ember/server/src/hub/`, `ember/server/src/transport.rs`, `ember/server/src/egress_proxy.rs`
- 규모: 파일 26개 / 약 8,751줄 (그중 `#[cfg(test)]` 단위 테스트 57개)
- 레이어: 비즈니스 로직 (HTTP 라우터 일부 포함)
- 한 줄 책임: 서버가 부릴 수 있는 원격 컴퓨터(ember-node)를 등록하고, 세션을 컴퓨터 사이에서 옮기며(FR-X3), 에이전트의 도구(Bash, 파일, 네트워크)를 현재 컴퓨터로 보낸다. 덧붙여 transport 허용 목록(devices), darkpyonix.dev hub 등록(hub), 서버 transport 바인딩을 맡는다.
- 의존하는 모듈: [node](node.md) (`NodeClient`, `proto`, `egress`, `envinfo`, `api::Node`), [transport](transport.md) (`Dialer`, `PeerAddr`, `PeerGate`, `Transport`), [hub](hub.md) (`ember_hub::*`), [server-core](server-core.md) (`store`, `session`, `events`, `auth`), [server-agents](server-agents.md) (`AgentKind`, `StartRequest`, `RemoteExec`), [server-accounts](server-accounts.md) (`Accounts::secrets`), [server-api](server-api.md) (`api::origin::check_origin`, `browser::EgressResolver`, `ose::data_root_from`)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs`, `session.rs`, `store.rs`, `transfers.rs`, `projects/`), [server-api](server-api.md) (`api/git.rs`, `api/harnesses.rs`, `api/ide.rs`, `api/ide_extensions.rs`, `api/integrations.rs`, `browser/`), [server-collab](server-collab.md) (`a2a/mod.rs`, `a2a/team.rs`), [server-enrol](server-enrol.md) (`computers/enrol.rs`), [server-accounts](server-accounts.md) (`schedules/mod.rs`), [client](client.md) (`ember/client/src/api.rs`가 `transport.rs`를 import)

## 큰 그림

```text
              ┌─ api.rs / terms.rs / fs.rs / metrics.rs / ports.rs  (HTTP, 공용 app)
              │
 Computers ───┼─ Registry (SQLite: computers, session_computer, session_designated)
 (mod.rs)     ├─ Connector → NodeApi (NodeClient over HTTP | transport, LocalNode)
              ├─ 세션 hook 4개: instructions / prepare / start_config / message
              ├─ relay.rs   : Codex app-server → node /exec-server (loopback WS)
              ├─ bridge.rs  : ember-exec shim → peer node (loopback TCP → transport stream)
              ├─ egress.rs  : 원격 브라우저 → node /egress (loopback SOCKS5)
              ├─ mount.rs   : Claude Code 파일 도구 → node 파일 API (NFS | FUSE)
              └─ local_node.rs: 서버 자신의 in-process node (로컬 터미널용)

 egress_proxy.rs : 에이전트 CLI의 API 트래픽 → 세션별 HTTP CONNECT 프록시 → 현재 컴퓨터 (FR-X6)
 devices/        : transport로 서버에 들어올 수 있는 peer 허용 목록 (FR-N3)
 hub/            : darkpyonix.dev 계정에 main_server로 등록, 계정 기기 동기화 (FR-N2)
 transport.rs    : 서버 transport 바인딩, 키 파일, relay 역할, 서비스 이름
```

## 라우트와 보안 경계

`main.rs`에서 라우터를 두 갈래로 합친다 (`ember/server/src/main.rs:443-498`). 공용 `app`은 로컬 TCP 리스너(`auth::protect`로 토큰과 Origin/Host 검사)와 transport(`devices` gate를 통과한 peer, `main.rs:467`) 양쪽에서 서비스된다. `local_app`에만 합쳐진 라우터는 transport에서는 보이지 않는다.

| 라우터 | 정의 | 합치는 곳 | 노출 |
|---|---|---|---|
| `computers::api::router` | `ember/server/src/computers/api.rs:37` | `main.rs:444` | 공용 `app` (TCP + transport) |
| `computers::terms::router` | `ember/server/src/computers/terms.rs:47` | `main.rs:445` | 공용 `app` |
| `computers::metrics::router` | `ember/server/src/computers/metrics.rs:25` | `main.rs:446` | 공용 `app` |
| `computers::fs::router` | `ember/server/src/computers/fs.rs:47` | `main.rs:447` | 공용 `app` |
| `computers::ports::router` | `ember/server/src/computers/ports.rs:24` | `main.rs:448` | 공용 `app` |
| `hub::api::router` | `ember/server/src/hub/api.rs:51` | `main.rs:462` | 공용 `app` |
| `devices::api::router` | `ember/server/src/devices/api.rs:23` | `main.rs:484` | **로컬 TCP 전용** |
| `hub::api::admin_router` | `ember/server/src/hub/api.rs:60` | `main.rs:486` | **로컬 TCP 전용** |

공용 `app`에 있다는 것은 transport 허용 기기도 컴퓨터를 등록(`POST /api/computers`), 삭제하고, 노드 파일을 읽고(`/fs/*`), 터미널에 붙을 수 있다는 뜻이다. 허용 기기는 소유자와 같은 권한으로 취급된다 (`main.rs:464` 주석 "the same API to allowed devices, without device management").

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `LOCAL` / `LOCAL_NAME` | 상수 | `ember/server/src/computers/mod.rs:71`, `:73` | 서버 자신을 뜻하는 암묵 컴퓨터 id `"local"`과 이름 `"this server"`. a2a, api, projects, browser에서 비교에 쓴다 |
| `Computer` | struct | `ember/server/src/computers/mod.rs:85` | 등록된 노드. `token`은 직렬화하지 않는다 (`:94`) |
| `ComputerError` | enum | `ember/server/src/computers/mod.rs:155` | 모든 API가 쓰는 에러. HTTP 코드 매핑은 `api.rs:50` |
| `Registry` | struct | `ember/server/src/computers/mod.rs:197` | SQLite 저장소. `get`, `list`, `session_computer`를 api/git, ide, harnesses, integrations가 직접 부른다 |
| `Computers` | struct | `ember/server/src/computers/mod.rs:676` | 서비스 본체. `main.rs:215`에서 하나 만든다 |
| `Computers::with_transport` | 함수 | `ember/server/src/computers/mod.rs:736` | 생성자. 등록된 peer를 transport 허용 목록과 주소록에 넣는다 |
| `Computers::install` | 함수 | `ember/server/src/computers/mod.rs:853` | 세션 hook 4개 등록, 폴백 watcher와 마운트 sweep 태스크 시작 |
| `Computers::client` | 함수 | `ember/server/src/computers/mod.rs:824` | 등록 컴퓨터의 `NodeClient`. `LOCAL`이면 `BadRequest` |
| `Computers::local_node_client` | 함수 | `ember/server/src/computers/mod.rs:833` | 서버 자신의 in-process node 클라이언트(처음 호출 때 시작) |
| `Computers::switch` | 함수 | `ember/server/src/computers/mod.rs:1081` | FR-X3 전환. a2a가 팀원 생성 때 쓴다 (`a2a/mod.rs:132` 주석) |
| `Computers::register` / `register_peer` | 함수 | `ember/server/src/computers/mod.rs:895`, `:910` | URL 또는 peer로 등록. enrol과 hub가 부른다 |
| `Computers::remove` | 함수 | `ember/server/src/computers/mod.rs:932` | 삭제와 peer 권한 회수 |
| `node_client` | 함수 | `ember/server/src/computers/mod.rs:543` | `Computer` → `NodeClient` (HTTP 또는 transport). `main.rs:242`의 egress route가 쓴다 |
| `connector` | 함수 | `ember/server/src/computers/mod.rs:567` | 실제 `Connector` 생성 (`main.rs:217`) |
| `find_shim` | 함수 | `ember/server/src/computers/mod.rs:1423` | `ember-exec` 경로 탐색 (`main.rs:211`) |
| `schema::*_MIGRATION` | 상수 | `ember/server/src/computers/schema.rs:8`, `:33`, `:39`, `:54` | `store::MIGRATIONS`에 등록 (`store.rs:136`, `:139`, `:150`, `:162`) |
| `mount::ProjectMounts::from_env` | 함수 | `ember/server/src/computers/mount.rs:383` | `main.rs:223` |
| `mount::ENV_CTL`, `mount::notify_invalidate` | 상수/함수 | `ember/server/src/computers/mount.rs:65`, `:699` | `ember-exec` 바이너리가 쓴다 (`bin/ember-exec.rs:62-63`) |
| `shim::{Plan, ShimEnv, plan, run_remote, ...}` | 모듈 | `ember/server/src/computers/shim.rs` | `ember-exec` 바이너리의 본체 (`bin/ember-exec.rs:16`) |
| `egress::EgressListener` | struct | `ember/server/src/computers/egress.rs:23` | `browser/egress.rs`, `browser/mod.rs` 문서가 참조 |
| `devices::Devices` | struct | `ember/server/src/devices/mod.rs:68` | `main.rs:139`. `gate()`가 transport 리스너를 막는다 |
| `hub::ServerHub` | struct | `ember/server/src/hub/mod.rs:164` | `main.rs:143` |
| `hub::WATCH_PERIOD` | 상수 | `ember/server/src/hub/mod.rs:54` | `main.rs:173` |
| `transport::{bind, load_key, config_with_hub, serve, ServerTransport, SERVER_SERVICE, ENABLE_ENV, enabled_from_env}` | 함수/상수 | `ember/server/src/transport.rs` | `main.rs:141-192`, `:467` |
| `egress_proxy::{SessionEgress, Route}` | struct/type | `ember/server/src/egress_proxy.rs:40`, `:34` | `main.rs:235-249` |

## 파일별 요약

### `ember/server/src/computers/mod.rs` (약 1,767줄, 그중 테스트 1432-1767)
- **목적:** 컴퓨터 등록부(`Registry`)와 서비스(`Computers`). 세션의 현재 컴퓨터를 기록하고 전환하며, 세션 시작마다 에이전트 종류별로 도구 경로를 설정한다. 파일 머리 주석(`:1-36`)이 에이전트별 경로(Codex는 relay, Claude Code는 shim + mount, ACP는 `req.computer`)를 설명한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PROBE_TIMEOUT` / `ENV_TIMEOUT` | 상수 | 76 / 78 | `/health` 5초, `/env` 20초 |
  | `ComputerView`, `ComputerStatus`, `SessionComputer` | struct | 101, 130, 145 | 클라이언트에 보내는 모양. `ComputerStatus.reachable`은 미측정이면 `None` |
  | `DUPLICATE_PEER` | 상수 | 185 | 같은 peer id 재등록 거절 문구 |
  | `AFTER_DUP_CHECK` | static(test) | 192 | 테스트 전용 hook. 중복 검사와 INSERT 사이에 끼어든다 |
  | `Registry::insert_with` | 함수 | 221 | 한 번의 연결 잠금 안에서 peer 중복 검사(인덱스 `:243`, 구 행 폴백 `:254`) 후 INSERT. 제약 위반을 이름/peer 중복으로 번역 (`:283-290`) |
  | `Registry::remove` | 함수 | 316 | 세션이 쓰는 중이면 `InUse`, 브라우저 egress로 쓰이면 `EgressInUse`. `project_computers`도 같이 지운다 (`:335`) |
  | `Registry::set_session_computer` | 함수 | 368 | upsert. 이전 notice를 덮어쓴다 |
  | `Registry::take_notice` | 함수 | 422 | 트랜잭션으로 읽고 NULL로 비운다 (한 번만 전달) |
  | `row_to_computer` | 함수 | 444 | 저장된 `peer_json`을 다시 검증(FR-N6). 실패하면 peer를 버리고 경고 |
  | `NodeApi` | trait | 475 | `health`, `env`, `file_state`. `NodeClient`(`:486`)와 `LocalNode`(`:518`)가 구현 |
  | `Connector` | type | 538 | `Option<&Computer>` → `Arc<dyn NodeApi>`. `None`은 `LOCAL` |
  | `connector` | 함수 | 567 | `LOCAL`은 `$HOME`을 root로 하는 `LocalNode` (`:572`) |
  | `env_description` | 함수 | 583 | 에이전트에게 주는 "# Current computer" 블록 |
  | `switch_notice` / `notice_origin` | 함수 | 629 / 643 | FR-S7 v0 일회성 공지와, 공지 문구에서 출발 컴퓨터 이름을 다시 파싱하는 함수 |
  | `DEFAULT_DEBOUNCE` / `WATCH_INTERVAL` | 상수 | 703 / 705 | 폴백 판정에 필요한 연속 probe 수 2, probe 주기 10초 |
  | `parse_fallback` | 함수 | 716 | `EMBER_FALLBACK_PROBES`, `EMBER_FALLBACK_INTERVAL_SECS` 해석 |
  | `Computers::prepare_start` | 함수 | 790 | Claude Code와 ACP 세션만 cwd를 마운트 (`:795`) |
  | `Computers::egress_proxy` | 함수 | 955 | 브라우저 egress용 SOCKS5 listener를 컴퓨터마다 하나 시작 |
  | `Computers::probe` | 함수 | 992 | `/health`(+`/env`)를 타임아웃과 함께 호출 |
  | `Computers::switch` | 함수 | 1081 | 아래 "전환 흐름" 참고 |
  | `Computers::reconcile` | 함수 | 1223 | 지정 컴퓨터(designated)가 살아 있으면 그쪽, 아니면 `LOCAL`로 옮긴다. `debounce`번 연속 같은 판단일 때만 |
  | `Computers::claude_env` | 함수 | 1265 | `CLAUDE_CODE_SHELL_PREFIX`, `EMBER_EXEC_NODE_URL`, `EMBER_EXEC_NODE_TOKEN`, `EMBER_EXEC_REMOTE_SHELL` |
  | `Computers::configure_start` | 함수 | 1329 | `EMBER_COMPUTER_ID` 추가 후 에이전트별 분기. Antigravity는 원격 불가로 실패 (`:1352`) |
  | `Computers::message_hook` | 함수 | 1389 | 전환 공지와 마운트 장애 공지를 합쳐 다음 메시지 앞에 붙인다 |
- **전환 흐름 (`switch`, `:1081-1186`):** 세션 조회 → 실행 중(`Running`, `WaitingForApproval`)이면 `Busy` (`:1091`) → 이미 그 컴퓨터이고 env가 있으면 no-op (`:1103`) → 대상 probe(+env), 실패면 `Unreachable` (`:1116`) → 이미 한 번 돈 세션(`native_id`가 있음)이면 공지 생성 (`:1139`) → 공지가 미전달 상태가 아니면 관측 파일들을 양쪽에서 해시 비교 (`:1145-1165`) → `set_session_computer` → `sessions.release` (`:1172`) → 마운트 해제 (`:1174`).
- **입력 → 출력:** 컴퓨터 id, 세션 id → `SwitchOutcome`, `CurrentComputer`, `ComputerStatus`.
- **의존:** `ember_node::client::NodeClient`, `ember_transport::{Dialer, PeerAddr}`, `crate::store`, `crate::session`, `crate::agents`, `crate::browser::egress::projects_using_computer` (`:328`).
- **사용처:** `main.rs:14`, `:215-231`, `:242`, `:582`; `api/git.rs:46`, `api/harnesses.rs:21`, `api/ide.rs:47`, `api/ide_extensions.rs:29`, `api/integrations.rs:40`, `transfers.rs:34`, `a2a/mod.rs:472`, `projects/mod.rs:18`.
- **부수효과:** DB 쓰기(`computers`, `session_computer`, `session_designated`, `project_computers`), transport 허용 목록 변경(`allow_peer`, `revoke_peer`, `:746`, `:925`, `:943`), loopback 리스너 생성(relay, bridge, egress, local node), 백그라운드 태스크 2개(`:861`, `:880`), 에이전트 프로세스 해제.
- **주의점:**
  - `install`의 폴백 watcher는 주기를 시작할 때 한 번만 읽는다 (`:862-864`). `set_watch_interval_secs`(`:1189`)는 주석대로 "다음 시작"에만 효과가 있고, 저장소 어디서도 호출하지 않는다.
  - `egress_proxy`는 peer 주소 컴퓨터에도 `NodeClient::new(&c.url, ...)`를 쓴다 (`:963`). peer 컴퓨터의 `url`은 빈 문자열이므로 브라우저 egress는 URL 컴퓨터에서만 동작한다 [확인 필요: `NodeClient::new("")`의 동작].
  - `Registry::remove`는 `session_designated` 행을 지우지 않는다 (`:316-339`). 지정된 컴퓨터가 지워지면 watcher의 `reconcile`이 `resolve`에서 `NotFound`를 내고 10초마다 경고를 남긴다 (`:870-871`, `:1237`).
  - `notice_origin`은 사람이 읽는 공지 문구를 다시 파싱한다 (`:643-646`). `switch_notice` 또는 `observations::switch_notice_with`의 문구를 바꾸면 깨진다.
  - `connector`와 `LocalNode::start`는 root로 `$HOME`만 본다 (`:572`, `local_node.rs:72`). Windows처럼 `HOME`이 없으면 root가 비어 있다.
  - 테스트: 14개. FR-N6 재검증, peer 중복 거절(동시성, 고유 인덱스 포함), 세션 공지 1회 전달, env 블록 문구, Claude 세션 cwd 마운트.

### `ember/server/src/computers/api.rs` (약 158줄)
- **목적:** 컴퓨터 목록, 등록, 삭제와 세션의 현재/지정 컴퓨터 HTTP API. 머리 주석에 표(`:4-12`)가 있다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `router` | 함수(pub) | 37 | 라우트 4개 |
  | `ApiError` | struct | 46 | `NotFound`→404, `Busy`/`InUse`/`EgressInUse`→409, `Unreachable`→502, `BadRequest`→400 (`:50-58`) |
  | `PeerSpec` | enum | 93 | `peer`는 64 hex id 또는 `PeerAddr` JSON (untagged) |
  | `register` | 핸들러 | 98 | `url`과 `peer` 중 정확히 하나 (`:108`) |
  | `remove` | 핸들러 | 117 | 삭제 후 할당됐던 프로젝트마다 `Push::ProjectUpdated` 발행 (`:121-125`) |
- **사용처:** `main.rs:444`.
- **부수효과:** 등록부 쓰기, 이벤트 발행.
- **주의점:** 공용 `app`에 있으므로 transport 기기도 등록과 삭제를 할 수 있다. 테스트 없음 (통합 테스트 `ember/server/tests/computers.rs`).

### `ember/server/src/computers/relay.rs` (약 203줄)
- **목적:** codex app-server(WebSocket, Text 프레임 하나에 JSON-RPC 한 개)와 노드의 `/exec-server`(바이트 스트림) 사이의 loopback 중계. 경로에 무작위 비밀을 넣어 다른 로컬 프로세스를 막는다 (`:16-17`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ExecServerRelay::start` | 함수(pub) | 42 | `127.0.0.1:0` 바인딩, 비밀 경로 `/{uuid}` (`:48-50`) |
  | `serve` | 함수 | 84 | 경로 검사(`:85-93`) 후 양방향 복사. codex→node는 메시지마다 `\n` 추가 (`:107`) |
  | `LineFramer` | struct(pub) | 143 | 바이트 스트림을 줄 단위로 자른다 |
- **사용처:** `computers/mod.rs:1289` (`relay_url`).
- **부수효과:** loopback 리스너, 연결마다 노드에 `/exec-server` 스트림(= 노드 쪽 codex 프로세스) 하나.
- **주의점:** codex가 URL 경로를 유지하는지는 `[U]`(미확인)로 적혀 있다 (`:17`). 테스트: 2개 (프레이머, 잘못된 경로 404).

### `ember/server/src/computers/shim.rs` (약 528줄, 테스트 401-528)
- **목적:** `ember-exec` 바이너리(`src/bin/ember-exec.rs`)의 논리. Claude Code의 Bash 명령(마지막 인자, `... && pwd -P >| <cwd-file>`로 끝남)을 노드 `/exec`로 보내고, 노드의 최종 cwd를 로컬 cwd 파일에 적는다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ENV_NODE_URL` 외 4개 | 상수 | 40-48 | shim이 읽는 환경 변수 이름 |
  | `DEFAULT_FORWARD` | 상수 | 50 | 노드로 넘기는 변수 기본 목록 |
  | `MARK_START` / `MARK_END` / `CWD_STEP` | 상수 | 52-54 | stderr cwd 표식과 Claude의 cwd 단계 문자열 |
  | `classify` | 함수 | 97 | 끝의 cwd 단계를 찾아 `BashTool` 또는 `Other` |
  | `unquote_word` | 함수 | 111 | shell-quote 한 단어 되돌리기 |
  | `remote_command` | 함수 | 140 | 본문 뒤에 cwd 표식 출력 추가 |
  | `MarkerFilter` | struct | 146 | stderr에서 표식을 청크 경계와 무관하게 제거 |
  | `plan` | 함수 | 250 | 로컬/원격 결정. 훅과 MCP 실행은 기본 로컬 (`ENV_NON_TOOL`) |
  | `run_remote` | 함수 | 283 | stdin 전달, 신호 전달(유닉스 `:326`, 그 외는 Ctrl-C만 `:345`), 출력 스트리밍, 종료 코드 |
- **사용처:** `ember/server/src/bin/ember-exec.rs:16`; 상수는 `computers/mod.rs:1274-1278`.
- **부수효과:** 노드에 명령 실행, 로컬 cwd 파일 쓰기 (`:394`), stderr 출력.
- **주의점:** Claude Code 2.1.288의 명령 형식에 맞춘 문자열 파싱이다 (`:4-14`). `classify`는 cwd 파일 경로가 `/`로 시작할 때만 Bash 도구로 본다 (`:102`). 연결 실패는 종료 코드 255. 테스트: 7개.

### `ember/server/src/computers/mount.rs` (약 934줄, 테스트 709-934)
- **목적:** 원격 세션의 cwd를 서버에 같은 절대 경로로 마운트해 Claude Code의 Read/Edit/Write/Glob/Grep이 노드 파일 API를 쓰게 한다. macOS는 loopback NFSv3(`mount-nfs`), Linux는 FUSE(`mount-fuse`). 두 기능 모두 없거나 `EMBER_MOUNT=off`이면 아무것도 마운트하지 않는다 (`:15-16`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ENV_MOUNT` / `ENV_SHADOW` / `ENV_TTL_MS` / `ENV_CTL` | 상수 | 59-65 | 환경 변수 이름 |
  | `MountSettings::from_vars` | 함수 | 90 | 기본 메커니즘은 빌드 기능으로 결정 (`:91-97`), op timeout 4초, idle grace 120초 (`:112`) |
  | `Mounter` / `ActiveMount` | trait | 128 / 122 | 메커니즘 추상화. `NoMount`(`:137`)는 항상 실패 |
  | `NfsMounter` / `FuseMounter` | struct | 193 / 239 | feature cfg로만 컴파일 |
  | `mounter_for` | 함수 | 275 | 설정 → 메커니즘 |
  | `node_fs` | 함수 | 299 | 컴퓨터 → `NodeFs`(deadline 적용 `NodeClient`) |
  | `MountError` | enum | 312 | 사용자에게 보이는 마운트 실패 문구 |
  | `ProjectMounts::acquire` | 함수 | 430 | 덮는 마운트가 있으면 공유, 다른 컴퓨터면 `Conflict`, 포함 관계면 `Nested`. 노드에서 디렉터리 확인 후 마운트 지점 준비, 마운트 |
  | `prepare_mount_point` | 함수 | 501 | 잔여 마운트 강제 해제, 없는 디렉터리 생성 (만든 것만 기억했다가 지운다) |
  | `ProjectMounts::sweep` | 함수 | 583 | 살아 있는 세션이 없는 채 `idle_grace`가 지나면 해제 |
  | `ProjectMounts::outage_notice` | 함수 | 623 | 장애마다 한 번 에이전트에게 공지. `try_lock`으로 동기 hook에서 기다리지 않는다 |
  | `CtlSocket` | struct | 654 | 임시 디렉터리(0700)의 유닉스 datagram 소켓. `invalidate`를 받으면 모든 캐시 무효화 (`:673`) |
- **사용처:** `main.rs:223`, `computers/mod.rs:772-808`, `bin/ember-exec.rs:62-63`, `session.rs:181`(문서).
- **부수효과:** 외부 명령 실행(`/sbin/mount_nfs`, `/bin/mount`, `umount`, `fusermount3`, 20초 제한 `:159`), 디렉터리 생성과 삭제, 임시 소켓 파일.
- **주의점:**
  - 비 유닉스에서는 `CtlSocket::start`가 실패하므로(`:682-684`) `enable_mounts`가 실패하고 마운트가 꺼진다 (`main.rs:224-226`이 경고만 남김).
  - `EMBER_MOUNT=nfs`나 `fuse`를 해당 feature 없이 주면 `NoMount`가 선택되고(`:284`), 원격 Claude Code 세션 시작이 모두 실패한다.
  - `ProjectMounts::list`(`:413`)는 정의만 있고 호출하는 곳이 없다.
  - 테스트: 9개 (공유와 해제, 충돌과 중첩, 다른 프로젝트로 이동, 에러 문구, 비어 있지 않은 디렉터리, sweep, 장애 공지 1회, ctl 소켓).

### `ember/server/src/computers/mount/remote_fs.rs` (약 1,315줄, 테스트 827-1315)
- **목적:** 프로토콜 중립 파일 시스템. 노드 파일 API 위에 자체 inode 표와 짧은 캐시를 둔다. NFS와 FUSE 어댑터가 이것을 번역만 한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ROOT_ID` | 상수 | 36 | 루트 inode 1 |
  | `FsErr` | enum | 40 | errno 대응 (`errno` `:109`, `is_outage` `:137`, `From<ClientError>` `:142`) |
  | `NodeFs` | trait | 169 | 노드 파일 API 추상화. `NodeClient` 구현 `:196` |
  | `CacheConfig` | struct | 310 | 기본값 TTL 1초, op timeout 4초, 통째 캐시 4 MiB 이하, 총 64 MiB (`:321-330`) |
  | `RemoteFs::call` | 함수 | 471 | 모든 노드 호출에 deadline, 장애 기록 (`Outage`) |
  | `RemoteFs::child_path` | 함수 | 497 | 이름 검사: 빈 이름, `/`, NUL, `.`, `..` 거절, 255바이트 제한 |
  | `RemoteFs::read` | 함수 | 654 | 작은 파일은 통째로 읽어 크기와 mtime이 같을 동안 메모리에서 |
  | `store_content` | 함수 | 692 | 예산 초과 시 임의 항목부터 버린다 (`:702`) |
- **사용처:** `mount.rs:56`, `mount/nfs.rs`, `mount/fuse.rs`.
- **부수효과:** 노드 파일 API 호출(읽기와 쓰기 모두: `pwrite`, `create_new`, `mkdir`, `remove`, `rename`, `symlink`, `setattr`).
- **주의점:** inode 표는 마운트 수명 동안 경로마다 하나씩 늘며 `remove` 때만 줄어든다 (`Inodes::forget_tree` `:366`). 테스트: 9개 (캐시, TTL과 무효화, 생성과 쓰기, rename id 유지, symlink, 이름 검사).

### `ember/server/src/computers/mount/nfs.rs` (약 324줄)
- **목적:** `RemoteFs`를 `nfsserve` 0.11 파일 시스템으로 노출하고 `127.0.0.1:<임시 포트>`에서 서비스 (feature `mount-nfs`).
- **주요 심볼:** `NfsAdapter`(`:25`, 모든 파일을 서버 프로세스 uid/gid 소유로 보고 `:37-41`), `nfs_status`(`:89`), `set_of`(`:111`), `NfsServer::start`(`:249`), `NfsServer::stop`(`:262`).
- **사용처:** `mount.rs:223` (`NfsMounter::mount`).
- **부수효과:** loopback TCP NFS 서버.
- **주의점:** 머리 주석이 "**not compiled**"라고 적는다 (`:5-6`). CI 워크플로에 `mount-nfs`를 켜는 곳이 없다 (`.github/` grep 결과 없음). NFS 서버에는 인증이 없어 같은 기계의 다른 로컬 사용자가 포트에 붙을 수 있다 [추정: nfsserve가 AUTH_SYS를 검사하지 않음]. 테스트: 4개.

### `ember/server/src/computers/mount/fuse.rs` (약 349줄)
- **목적:** `RemoteFs`를 `fuser` 0.18 `Filesystem`으로 노출 (feature `mount-fuse`, Linux 전용, `fusermount3`).
- **주요 심볼:** `FuseAdapter`(`:29`), `errno`(`:46`), `file_attr`(`:58`), `impl Filesystem`(`:88-308`), `FuseMount::mount`(`:329`, `NoDev`, `NoSuid`, `DefaultPermissions`, 스레드 2개), `FuseMount::unmount`(`:343`).
- **사용처:** `mount.rs:265`.
- **부수효과:** 커널 FUSE 마운트.
- **주의점:** 머리 주석이 "**not compiled**"라고 적는다 (`:10-11`). 요청마다 tokio 태스크로 처리한다. `AllowOther`가 없어 마운트한 사용자만 접근한다. 테스트 없음.

### `ember/server/src/computers/mount/cmd.rs` (약 343줄)
- **목적:** mount/umount 명령줄과 마운트 지점 검사. 순수 함수로 만들어 정확한 명령을 단위 테스트한다.
- **주요 심볼:** `NfsOptions::new`(`:40`, timeo 5초, retrans 2, deadtimeout 60초), `worst_case_wait`(`:53`), `Os::current`(`:85`, macOS와 Linux 외에는 `None`), `nfs_mount`(`:97`), `unmount`(`:147`), `MountPoint`(`:180`), `MountPointError`(`:191`), `inspect`(`:202`, 장치 번호로 마운트 여부 판단), `setup_hint`(`:259`, `ember/server/scripts/ember-mount-setup.sh` 안내).
- **사용처:** `mount.rs:55`, `:162-189`, `:501-545`.
- **주의점:** 옵션 이름은 "기억과 README에서" 가져왔고 실제 장비에서 `[U]`라고 적혀 있다 (`:18-19`). 테스트: 5개.

### `ember/server/src/computers/observations.rs` (약 190줄)
- **목적:** FR-S7. 에이전트가 읽거나 고친 파일을 저장된 도구 호출에서 찾고, 전환 때 양쪽 해시를 비교해 달라진 파일만 다시 읽으라고 공지한다.
- **주요 심볼:** `MAX_FILES`(`:17`, 100), `FILE_TOOLS`(`:20`, `Read`, `Edit`, `Write`, `MultiEdit`, `NotebookEdit`), `FileState`(`:24`), `observed_paths`(`:32`), `compare`(`:64`), `hash_all`(`:80`, 파일을 하나씩 순서대로 해시), `switch_notice_with`(`:90`).
- **사용처:** `computers/mod.rs:1148-1167`, `:480`.
- **주의점:** `/`로 시작하는 경로만 센다 (`:43`). 해시는 직렬로 최대 100개 x 2대이고, 각각 노드 왕복이다 (`:82-84`). 테스트: 5개.

### `ember/server/src/computers/terms.rs` (약 236줄)
- **목적:** 노드의 영속 터미널(`/terms`)을 서버가 노드 토큰으로 대신 호출하고, attach WebSocket을 프레임 단위로 중계 (FR-P3, FR-P6).
- **주요 심볼:** `router`(`:47`), `Failure`(`:61`), `node`(`:98`, `LOCAL`이면 `local_node_client`), 핸들러 `list`/`create`/`one`/`snapshot`/`control`/`kill`/`remove`(`:105-144`), `attach`(`:146`, 업그레이드 전에 `check_origin` `:153`), `relay`(`:163`, 첫 프레임은 `TermHello`).
- **사용처:** `main.rs:445`.
- **부수효과:** 노드 HTTP/WS 호출, 첫 로컬 사용 때 in-process node 시작.
- **주의점:** 서버는 터미널 상태를 갖지 않는다 (`:6-7`). 파싱 못 한 입력은 버린다 (`:205-206`). 테스트 없음 (통합 `tests/terms_relay.rs`, `fr_w4_local_terms.rs`).

### `ember/server/src/computers/local_node.rs` (약 96줄)
- **목적:** 서버 자신의 기계를 위한 in-process node. 로컬 터미널 attach가 실제 URL을 요구해서 loopback 리스너로 띄운다 (FR-W4, #455).
- **주요 심볼:** `denied_paths`(`:28`, 서버 데이터 디렉터리와 OSE 데이터 루트 거부), `denied_from_env`(`:49`), `LocalNode::start`(`:69`, 토큰은 UUID 두 개 `:71`, root는 `$HOME` `:72`), `client`(`:93`).
- **사용처:** `computers/mod.rs:836`.
- **주의점:** 거부 목록은 `/fs` API만 좁힌다. 터미널과 에이전트는 셸로 읽을 수 있다 (`:26-27`). 테스트 없음 (통합 `fr_w4_local_node_denied.rs`).

### `ember/server/src/computers/egress.rs` (약 86줄)
- **목적:** 원격 브라우저(Chrome)의 SOCKS5 프록시. loopback에서 받은 연결마다 노드 `/egress` WebSocket을 열고 바이트를 그대로 복사한다 (FR-R1).
- **주요 심볼:** `EgressListener::start`(`:37`), `proxy_url`(`:83`, `socks5://127.0.0.1:<port>`), `addr`(`:78`, 쓰는 곳 없음).
- **사용처:** `computers/mod.rs:964`.
- **주의점:** 인증이 없다. 같은 기계의 모든 로컬 프로세스가 리스너가 사는 동안 이 컴퓨터를 통해 밖으로 나갈 수 있다 (`:12-14`, 의도된 경계).

### `ember/server/src/computers/bridge.rs` (약 82줄)
- **목적:** peer 주소 노드에 대해 `ember-exec` shim(HTTP 전용, transport 신원 없음)에게 loopback HTTP 주소를 준다. TCP 연결 하나를 transport 스트림 하나로 그대로 나른다.
- **주요 심볼:** `NodeBridge::start`(`:39`), `url`(`:79`).
- **사용처:** `computers/mod.rs:1306`.
- **주의점:** loopback 포트를 찾은 로컬 프로세스도 노드 토큰 없이는 얻는 것이 없다 (`:16-17`).

### `ember/server/src/devices/mod.rs` (약 235줄)
- **목적:** transport로 서버에 들어올 수 있는 peer 허용 목록(FR-N3). 테이블이 `PeerGate`의 허용 목록이 된다. 손으로 넣은 행(`local`)과 hub 동기화 행(`hub`)을 `source`로 구분한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SOURCE_LOCAL` / `SOURCE_HUB` | 상수 | 39 / 40 | `"local"`, `"hub"` |
  | `Devices::open` | 함수 | 75 | 테이블에서 gate를 채운다 |
  | `Devices::add` | 함수 | 107 | upsert. 기존 hub 행도 `local`로 바뀐다 (`:115`) |
  | `Devices::sync_from_hub` | 함수 | 126 | hub 행만 추가, 이름 변경, 회수. 손으로 넣은 행은 손대지 않는다 |
  | `Devices::remove` | 함수 | 167 | 행이 없어도 gate에서 회수 후 `NotFound` |
- **사용처:** `main.rs:139`, `:467`, `:484`; `hub/mod.rs:817`; `transfers.rs`.
- **부수효과:** DB 쓰기, gate의 열린 연결 즉시 종료.
- **주의점:** 테스트: 2개 (gate 반영, hub 동기화 규칙).

### `ember/server/src/devices/api.rs` (약 72줄)
- **목적:** 기기 관리 HTTP API. **로컬 TCP 전용** (`:1-2`).
- **주요 심볼:** `router`(`:23`), `ApiError`(`:30`), `parse_peer`(`:49`), `list`/`add`/`remove`(`:53`, `:63`, `:68`).
- **사용처:** `main.rs:484`.

### `ember/server/src/hub/mod.rs` (약 836줄)
- **목적:** 서버를 darkpyonix.dev 계정의 `main_server`로 등록하고(디바이스 링크), 토큰을 `secret.key`로 봉인해 저장하며, 철회 감시, 계정 기기를 컴퓨터로 추가, 사용자 코드 승인, 기기 허용 목록 동기화를 한다 (FR-N2).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SYNC_DEVICES_ENV` | 상수 | 52 | `EMBER_HUB_SYNC_DEVICES` |
  | `AAD_PREFIX` / `RESOLVE_AAD_PREFIX` | 상수 | 56 / 57 | 봉인 AAD. 바꾸면 저장된 토큰을 못 연다 |
  | `HubApiError` | enum | 65 | HTTP 매핑은 `hub/api.rs:73-98` |
  | `ServerHub::registration` | 함수 | 241 | 행을 읽고 device 토큰과 resolve 토큰을 연다 |
  | `ServerHub::save_registration` | 함수 | 287 | 봉인 후 upsert (id = 1 고정) |
  | `ServerHub::mark_revoked` | 함수 | 337 | `revoked_at` 기록, transport 디렉터리 토큰 해제 |
  | `ServerHub::leave` | 함수 | 357 | hub에서 자기 기기 삭제 후 로컬 행 삭제 (`local_only`면 hub 생략) |
  | `ServerHub::start_link` | 함수 | 501 | `DeviceLink::start(... Role::MainServer)`, pending 저장 |
  | `ServerHub::follow_link` | 함수 | 539 | 백그라운드에서 승인 대기 후 `complete` |
  | `ServerHub::complete` | 함수 | 591 | resolve 토큰 확보, 저장, `/config` 발견, app 보고, transport에 hub 디렉터리와 relay 적용 |
  | `ServerHub::spawn_watch` | 함수 | 635 | long-poll(`GET /devices?wait=`) 또는 `WATCH_PERIOD`마다 `/me` |
  | `ServerHub::add_computer` | 함수 | 741 | 계정 기기를 peer id만으로 컴퓨터 등록 |
  | `ServerHub::decide_code` | 함수 | 786 | 사용자 코드 승인. 403이면 브라우저 승인 안내 |
  | `ServerHub::sync_list` | 함수 | 813 | 자기 자신을 뺀 계정 기기 전체를 `devices`의 hub 행으로 |
  | `default_name` | 함수 | 825 | `hostname` 명령 실행 결과로 이름 |
- **사용처:** `main.rs:143-191`; `hub/api.rs`.
- **부수효과:** 외부 HTTP(hub), DB 쓰기(`hub_registration`, `hub_pending_link`, `devices`), transport 설정 변경, 외부 프로세스(`hostname`).
- **주의점:**
  - 머리 주석의 "The router ([`api`]) is local only (TCP)"(`:28`)는 현재 코드와 다르다. `hub::api::router`는 공용 `app`에 합쳐진다 (`main.rs:462`).
  - `forget`(`:377`)은 정의만 있고 호출하는 곳이 없다 (`DELETE /api/hub/registration`은 `leave`를 부른다, `hub/api.rs:183`).
  - `sync_devices`를 켜면 계정의 모든 기기(노드 포함)가 서버 API에 들어올 수 있다 (`:813-817`).
  - 테스트 없음 (통합 `tests/hub.rs`, `fr_n3_revocation_bound.rs`).

### `ember/server/src/hub/api.rs` (약 249줄)
- **목적:** hub HTTP API. 공용 `router`(상태, 계정 기기, 기기를 컴퓨터로 추가)와 로컬 전용 `admin_router`(링크, 확인, 탈퇴, 기기 삭제, 코드 승인, 동기화).
- **주요 심볼:** `router`(`:51`), `admin_router`(`:60`), `ApiError`(`:71`), `hub`(`:111`, hub가 꺼졌으면 503), `hub_or_503!`(`:121`), 핸들러 `:134-249`.
- **사용처:** `main.rs:462`, `:486`.
- **주의점:** hub가 꺼진 상태(`hub == None`)에서는 모든 라우트가 503이다 (`:112-118`). 공용 `add_computer`(`:205`)는 transport 기기도 부를 수 있다.

### `ember/server/src/transport.rs` (약 137줄)
- **목적:** 서버 transport. 영속 키(`<data dir>/transport.key`), 노드로 나가는 `Dialer`, 클라이언트에게 API를 서비스(`SERVER_SERVICE`), letify 백엔드에서 main server relay 역할.
- **주요 심볼:** `SERVER_SERVICE`(`:24`, `"ember-server"`), `ENABLE_ENV`(`:28`), `KEY_FILE`(`:29`), `RELAY_PORT_ENV`(`:33`), `RELAY_ROLE_ENV`(`:35`), `DEFAULT_RELAY_PORT`(`:37`, 7443), `with_main_server_roles`(`:55`, `0.0.0.0:<port>`에 relay와 관측자), `enabled_from_env`(`:75`), `bind`(`:84`), `load_key`(`:90`), `config_with_hub`(`:99`), `ServerTransport`(`:114`), `serve`(`:127`).
- **사용처:** `main.rs:141-192`, `:467`; `computers/mod.rs:550`, `:921`; `hub/mod.rs:61`; `ember/client/src/api.rs`.
- **주의점:** letify 백엔드에서 transport를 켜면 기본으로 모든 인터페이스의 TCP와 UDP 7443을 연다 (`:59-61`). `EMBER_SERVER_RELAY=off`로 끈다.

### `ember/server/src/egress_proxy.rs` (약 266줄)
- **목적:** 에이전트 CLI 자체의 API 트래픽을 세션의 현재 컴퓨터로 내보낸다 (FR-X6, D19). 세션마다 loopback HTTP CONNECT 프록시 하나와 무작위 비밀번호. CONNECT마다 경로를 다시 묻기 때문에 전환 후 새 연결은 새 컴퓨터를 따른다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Route` | type | 34 | 세션 id → `None`(직접) 또는 노드 클라이언트 |
  | `MAX_HEAD` / `HEAD_TIMEOUT` | 상수 | 36 / 37 | 요청 머리 16 KiB, 30초 |
  | `SessionEgress::env_for` | 함수 | 67 | `HTTPS_PROXY`, `HTTP_PROXY`(대소문자 모두), `NO_PROXY=localhost,127.0.0.1,::1` |
  | `SessionEgress::proxy_url` | 함수 | 80 | 첫 사용 때 리스너 시작 |
  | `start_hook` / `end_hook` | 함수 | 134 / 129 | 세션 시작 때 env 추가, 끝날 때 프록시 종료 |
  | `serve` | 함수 | 165 | Basic 인증, CONNECT만 허용, `200 Connection Established` 후 양방향 복사 |
  | `open` | 함수 | 228 | 직접 TCP 또는 노드 `/egress` 위 SOCKS5 핸드셰이크 |
- **사용처:** `main.rs:235-249` (`EMBER_AGENT_EGRESS`가 `off`가 아니면).
- **주의점:** 비밀번호 비교가 상수 시간이 아니다 (`:191`). 평문 `http://` 프록시는 지원하지 않는다 (`:15-16`). 테스트 없음 (통합 `tests/fr_x6_egress.rs`).

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/server/src/computers/schema.rs` | 59 | `computers`, `session_computer` 생성 (`:8`), `peer_json` 추가 (`:33`), `peer_id`와 부분 UNIQUE 인덱스 (`:39`), `session_designated` (`:54`). 테스트 없음 |
| `ember/server/src/computers/fs.rs` | 132 | 읽기 전용 파일 연산 7개(`stat`, `lstat`, `read`, `list`, `readlink`, `glob`, `grep`)만 노드로 중계 (`:94`). 본문 1 MiB 제한 (`:45`). 경로 검사는 노드에 맡긴다 (`:22-25`). `LOCAL`은 400 |
| `ember/server/src/computers/metrics.rs` | 54 | `GET /api/computers/{id}/metrics?top=` 중계 (`:33`). 서버는 샘플을 저장하지 않는다 |
| `ember/server/src/computers/ports.rs` | 52 | `GET /api/computers/{id}/ports` 중계 (`:32`) |
| `ember/server/src/devices/schema.rs` | 12 | `devices(peer_id, name, created_at)` (`:7`). `source` 열은 `hub/schema.rs:18`이 추가 |
| `ember/server/src/hub/schema.rs` | 36 | `hub_registration`(단일 행 `id = 1`, 토큰 nonce/ciphertext) (`:7`), `devices.source` (`:18`), resolve 토큰 열과 `hub_pending_link` (`:27-35`) |

## 이 모듈을 수정할 때 주의할 점

- **라우터 위치가 보안 경계다.** 새 라우트를 `computers::api` 같은 공용 라우터에 넣으면 transport 허용 기기에게도 열린다. 기기나 서버 등록 자체를 바꾸는 라우트는 `devices::api::router`나 `hub::api::admin_router`처럼 `local_app`에만 합친다 (`main.rs:482-487`).
- **에러 → HTTP 매핑이 다섯 번 복제돼 있다.** `api.rs:50`, `fs.rs:58`, `metrics.rs:38`, `ports.rs:36`, `terms.rs:73`. `ComputerError`에 변형을 추가하면 모두 확인한다. 노드의 `ClientError::Api`를 그대로 넘기는 코드도 네 곳이다 (`fs.rs:68`, `metrics.rs:47-51`, `ports.rs:45-49`, `terms.rs:85`).
- **공지 문구가 데이터다.** `notice_origin`(`mod.rs:643`)은 `"(moved from \""`라는 문구를 파싱한다. `switch_notice`(`mod.rs:629`)와 `switch_notice_with`(`observations.rs:90`)는 같은 앞부분을 유지해야 한다.
- **세션 hook 순서 의존.** `install`(`mod.rs:853`)은 instructions, prepare, start_config, message hook을 등록한다. `instructions_hook`은 에러를 삼키고(`mod.rs:1368-1371`), 같은 레코드를 읽는 `start_hook`이 에러로 시작을 실패시킨다는 가정에 기댄다.
- **노드 토큰이 에이전트 프로세스 환경에 들어간다.** Claude Code 세션은 `EMBER_EXEC_NODE_TOKEN`을 받는다 (`mod.rs:1275`). 에이전트와 그 자식 프로세스는 이 토큰으로 노드 API 전체를 쓸 수 있다.
- **loopback 리스너는 컴퓨터 삭제 때만 정리된다.** relay, bridge, egress는 `Computers::remove`(`mod.rs:946-948`)에서 맵을 비울 때 `Drop`으로 닫힌다. 컴퓨터의 URL이나 토큰을 바꾸는 경로는 없으므로 바뀐 노드에는 옛 클라이언트가 남는다 [추정].
- **마운트 코드 대부분은 기본 빌드에 없다.** `nfs.rs`, `fuse.rs`, `NfsMounter`, `FuseMounter`는 feature cfg 뒤에 있고 CI가 그 feature로 빌드하지 않는다. 이 부분을 고치면 해당 플랫폼과 feature로 직접 빌드해야 한다.
- **마이그레이션 번호 주석이 실제와 다르다.** `store::MIGRATIONS` 순서(`store.rs:133-163`)로 보면 `PEER_MIGRATION`은 5→6, `devices::schema::MIGRATION`은 6→7, `hub::schema::MIGRATION`은 9→10인데 주석은 각각 "4 to 5"(`computers/schema.rs:30`), "5 to 6"(`devices/schema.rs:3`), "7 to 8"(`hub/schema.rs:3`)이다. 마이그레이션은 추가만 한다 (`store.rs:131-132`).
- **봉인 AAD는 바꾸지 않는다.** `hub/mod.rs:56-57`의 접두사를 바꾸면 저장된 hub 토큰을 열 수 없다.
