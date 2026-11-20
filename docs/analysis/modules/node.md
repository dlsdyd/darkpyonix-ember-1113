# 모듈: node

- 경로: `ember/node/` 중 `src/{api,client,config,egress,envinfo,exec,exec_server,fs,hub,jobs,lib,main,metrics,policy,ports,proto,transport}.rs`, `Cargo.toml`, `service/*` (git, term, enrol 파일과 `tests/`는 제외)
- 규모: 파일 20개 / 약 7,080줄 (`docs/analysis/_raw/modules.md`)
- 레이어: API (노드 데몬 `ember-node`의 HTTP/WebSocket 서버와 그 타입 클라이언트)
- 한 줄 책임: 각 컴퓨터에서 도는 실행 데몬으로, 서버가 시킨 파일 조작, 명령 실행, 백그라운드 잡, 터미널, git, 브라우저 SOCKS5 출구를 토큰 인증과 경로 정책 뒤에서 수행한다. 에이전트 CLI는 돌리지 않고 대화 기록도 저장하지 않는다 (`ember/node/src/lib.rs:4-5`).
- 의존하는 모듈: [node-git](node-git.md) (`ember/node/src/lib.rs:35-36`, `ember/node/src/api.rs:34-38`), [node-term](node-term.md) (`api.rs:42`, `config.rs:49` 설정의 `pty_keeper`), [node-enrol](node-enrol.md) (`config.rs:98-108`, `main.rs`의 `enrol` 하위 명령), 외부 크레이트 `ember-transport`, `ember-hub` (`transport.rs:23-24`, `hub.rs:28-31`)
- 이 모듈을 쓰는 모듈: [server-computers](server-computers.md)가 `ember_node::client`/`proto`/`egress`를 가장 많이 쓴다 (`ember/server/src/computers/*.rs`, 서버 쪽 import 집계: client 19, proto 28, egress 4). 서버는 `ember_node::api::Node`/`router`로 노드를 프로세스 안에 내장하기도 한다 (`ember/server/src/computers/local_node.rs:17-19`, `ember/server/src/api/git.rs:40-41`, `:156`). `envinfo::describe`, `fs::sha256_file`, `exec::SIGINT`도 서버가 직접 쓴다 (`ember/server/src/computers/mod.rs:524`, `:529`, `ember/server/src/computers/shim.rs:348`). 기동 순서는 [entrypoints.md](../_raw/entrypoints.md)의 "ember-node 초기화 순서"를 본다 (여기서 반복하지 않는다).

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Node` | struct | `ember/node/src/api.rs:112` | 데몬 상태 (`Inner`, 99: 토큰, 경로 정책, 잡, 터미널, egress 정책, 쓰기 락). `Node::new(NodeConfig)` (115)는 빈 토큰이면 실패한다 (116) |
| `router(Node)` | fn | `ember/node/src/api.rs:155` | 전체 라우터. `/health`만 인증 밖이고 나머지는 `route_layer(auth)` 안 (`api.rs:227-229`) |
| `serve(listener, node)` | fn | `ember/node/src/api.rs:147` | 임의의 `axum::serve::Listener` 위에서 같은 라우터를 서빙 (TCP, 피어 투 피어 transport 공용) |
| `NodeConfig` | struct | `ember/node/src/config.rs:12` | 토큰, roots, denied, state_dir, pty_keeper, egress. `from_env()` (`config.rs:53`) |
| `LocalEndpoint` | struct | `ember/node/src/config.rs:144` | `<state_dir>/local.json`. 같은 컴퓨터의 `ember-term`과 VS Code 확장이 데몬을 찾는 파일 |
| `PathPolicy` | struct | `ember/node/src/policy.rs:31` | 허용 root와 거부 경로. `resolve_existing`/`resolve_for_write`/`resolve_nofollow` |
| `EgressPolicy`, `Target`, `SocksAuth` | struct/enum | `ember/node/src/egress.rs:131`, `:210`, `:201` | 출구 정책과 SOCKS5 서버 |
| `NodeClient` | struct | `ember/node/src/client.rs:150` | 서버가 쓰는 타입 클라이언트(HTTP 또는 transport). 라우트마다 메서드 하나 |
| `ClientError` | enum | `ember/node/src/client.rs:60` | `errno()`, `is_transport()`, `is_timeout()`, `code()`, `precondition_actual()` |
| `proto::*` | 타입 모음 | `ember/node/src/proto.rs` | 서버와 노드가 공유하는 JSON 와이어 타입 (바이트는 base64, `proto.rs:13`) |
| `Jobs` | struct | `ember/node/src/jobs.rs:58` | 잡 테이블과 노드 이벤트 로그 (터미널 시작/종료 이벤트도 여기에 실린다) |
| `exec::{spawn_pipes, spawn_pty, kill_group}` | fn | `ember/node/src/exec.rs:141`, `:192`, `:82` | 명령 실행 (pipe 또는 PTY), 프로세스 그룹 종료 |
| `fs::*` | fn | `ember/node/src/fs.rs:187-527` | 블로킹 파일 조작 14종 |
| `transport::{bind, serve, allowed_peers}` | fn | `ember/node/src/transport.rs:138`, `:145`, `:117` | transport로 같은 API를 서빙, 허용 피어 목록 |
| `hub::cli` | fn | `ember/node/src/hub.rs:388` | `ember-node hub register/status/forget` |
| `metrics::sample`, `ports::listening`, `envinfo::describe` | fn | `metrics.rs:60`, `ports.rs:258`, `envinfo.rs:141` | 모니터, 포트 목록, 환경 설명 |
| `ember-node` 바이너리 | bin | `ember/node/src/main.rs:44` | 하위 명령 `__keep-pty`, `exec-server`, `hub`, `enrol`, 없으면 데몬 |

## 파일별 요약

### `ember/node/src/api.rs` (971줄)
- 목적: 노드 HTTP/WebSocket API 전부. 라우터, 토큰 인증 미들웨어, 에러 변환, 핸들러. 파일 머리 주석(`api.rs:1-72`)이 라우트 표이나 `/metrics`는 표에 없다 (`api.rs:158`).
- 의존: `config`, `exec`, `fs`, `git`(+하위), `jobs`, `policy`, `proto`, `term`, `egress`, `exec_server`, `metrics`, `ports`, `envinfo`.
- 사용처: `main.rs`, `egress.rs`/`exec_server.rs`(`Node` 접근자 129-141), `transport.rs`, 서버의 내장 노드.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Inner`/`Node` | struct | 99, 112 | `token`, `policy`, `jobs`, `terms`, `egress`, `write_lock`(tokio Mutex, 107) |
| `router` | fn | 155 | 라우트 등록 156-228, `DefaultBodyLimit` 64 MiB (231) |
| `token_eq` | fn | 236 | 상수 시간 비교. 길이가 다르면 즉시 false (길이는 노출됨) |
| `auth` | fn | 240 | `Authorization: Bearer <token>`이 아니면 401 `unauthorized` (250) |
| `ApiError` + `From<PolicyError/FsError/GitError>` | struct/impl | 258, 277, 290, 318 | 오류를 `ErrorBody`와 상태 코드로 변환 (EEXIST/ENOTEMPTY는 409, ENOTDIR 등은 400, 정책 위반은 403 `forbidden_path`, 사전조건 실패는 412+`actual_sha256`) |
| `blocking` | fn | 336 | `spawn_blocking`으로 fs 함수 실행 |
| `exec_session` | fn | 643 | `/exec` WebSocket 세션. 첫 텍스트 프레임이 `ExecRequest`, 연결이 끊기면 프로세스 그룹에 SIGKILL (717-718) |
| `events_session` | fn | 744 | 백로그 재전송 후 broadcast 구독. lag이면 소켓을 닫아 클라이언트가 `after`로 재접속하게 한다 |
| `list_ports` | fn | 796 | 실행 중인 터미널과 잡의 pid를 root로 모아 `ports::listening` 호출 |
| `term_attach_session` | fn | 863 | `TermHello` 수신, `Session::attach`, 입력/이벤트 중계. 뒤처진 클라이언트에는 `dropped:` 에러 이벤트 (933) |
- 부수효과: 파일 변경 계열(`write`, `symlink`, `mkdir`, `remove`, `rename`, `setattr`, `pwrite`)과 index를 바꾸는 git 핸들러는 `write_lock`을 잡는다 (`api.rs:373`, `:394-412`, `:565-571`, 그 외 git 468-559, 947-968). fetch/push/pull의 네트워크 구간은 잡지 않는다 (`api.rs:415-419` 주변 주석).
- 주의점: 파일 하나에 파일, git, 잡, 터미널 핸들러가 섞여 있다. git 핸들러(422-558, 942-971)는 [node-git](node-git.md)에 설명이 있다.

### `ember/node/src/main.rs` (208줄)
- 목적: 바이너리 진입점. 하위 명령 분기(`main.rs:44-70`)와 데몬 `serve()`. 순서는 [entrypoints.md](../_raw/entrypoints.md) 참조.
- 핵심: `EMBER_NODE_SOCKS_LISTEN`이면 SOCKS5 리스너를 별도로 띄운다. TCP와 transport 서버를 `select_all`로 묶고, 종료 신호에서 `terms.shutdown()`으로 터미널 스냅샷을 저장한다. SIGHUP(유닉스)은 허용 피어 목록과 hub 등록을 다시 읽는다.
- 부수효과: `local.json`에 토큰과 주소를 쓴다 (`LocalEndpoint::for_addr(...).write`). 허용 피어가 없으면 경고 후 모든 transport 연결을 거절한다. transport 모드에서 피어 id와 주소를 stdout에 출력한다.

### `ember/node/src/config.rs` (312줄)
- 목적: 환경 변수 기반 설정과 `local.json`.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `NodeConfig::from_env` | fn | 53 | 토큰 출처 로그에는 출처만 남기고 값은 남기지 않는다 (58-68) |
| `token_with_source` | fn | 104 | `EMBER_NODE_TOKEN`(비어 있지 않음)이 `enrol.json`의 `node_token`보다 우선, 둘 다 없으면 오류 |
| `parse_deny` | fn | 118 | `EMBER_NODE_DENY`를 PATH 규칙으로 분리 |
| `default_state_dir` | fn | 126 | `EMBER_NODE_STATE_DIR` 또는 `$HOME/.ember/node` |
| `LocalEndpoint::{write,read,discover}` | fn | 167, 185, 192 | 로컬 엔드포인트 파일. `discover`는 `EMBER_NODE_URL`+`EMBER_NODE_TOKEN`을 먼저 본다 (190-194) |
- 테스트 있음 (`config.rs:213` 이하, FR-C2 포함).

### `ember/node/src/policy.rs` (271줄) [보안]
- 목적: 모든 경로가 허용 root 안에 있는지 확인하는 `PathPolicy`.
- 동작: 절대 경로만 허용 (`NotAbsolute`, 21-). 경로를 canonicalize(심볼릭 링크와 `..` 해석)한 뒤 root에 속하고 denied에 속하지 않을 때만 통과 (`check`, 85-92). 아직 없는 쓰기 대상은 가장 가까운 기존 조상을 canonicalize하고 나머지를 붙이되 `..`는 거부한다 (`resolve_for_write`, 104-142). `resolve_nofollow`는 마지막 성분을 따라가지 않아 root 밖을 가리키는 링크도 보이고 지울 수 있지만 따라가지는 않는다 (144-158). `is_root`는 root 자체의 삭제/이동 방지용 (160).
- denied: root 밖과 같은 오류(`Outside`)로 거절해 존재 여부를 숨긴다 (8-12). 상대 경로 denied는 무시된다 (`with_denied`, 53-71). 경로 기준이라 bind mount나 hard link는 못 잡는다 (주석 `with_denied` 위).
- 한계: 명령(`/exec`, `/jobs`, `/terms`)의 샌드박스가 아니다. cwd만 제한한다 (14-15).
- 테스트 3개 (`policy.rs:187` 이하).

### `ember/node/src/egress.rs` (715줄) [보안]
- 목적: 원격 브라우저용 SOCKS5 출구 (FR-R1). `/egress` WebSocket 하나가 SOCKS5 바이트 스트림 하나다. 서버 쪽 loopback 리스너가 바이트를 복사하고 Chrome이 직접 핸드셰이크한다 (머리 주석 1-20).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `EgressPolicy` | struct | 131 | `enabled` + `deny: Vec<Cidr>`. 기본은 켜짐, 전부 허용 (137-141) |
| `EgressPolicy::from_env` | fn | 158 | `EMBER_NODE_EGRESS_DENY`(키워드 `private`, `link-local`, `loopback`, CIDR), `EMBER_NODE_EGRESS=off/0/false/no`로 끔 |
| `connect` | fn | 332 | 도메인은 노드에서 해석, 해석된 주소를 모두 정책으로 거르고, 남은 주소에 15초 타임아웃(60)으로 연결. 막히면 응답 코드 `0x02` |
| `serve_socks5` | fn | 366 | CONNECT만 지원 (`0x07` 응답), 핸드셰이크 30초 제한 (62) |
| `serve_listener` | fn | 392 | 선택적 평문 SOCKS5 리스너 |
| `auth_for_peer` | fn | 413 | loopback 피어는 인증 없음, 그 외는 RFC 1929 비밀번호 = 노드 토큰 |
| `ws` | fn | 425 | `/egress` 핸들러. 비활성이면 403 JSON. 활성이면 duplex 파이프로 `serve_socks5`와 연결 (`SocksAuth::None`, 토큰은 업그레이드에서 이미 확인) |
| `NodeClient::egress`, `bridge`, `client_connect` | fn | 497, 505, 550 | 서버 쪽 클라이언트 구현 |
- 반쪽 닫기: 빈 Binary 프레임이 TCP FIN이다 (20-22). 상수 시간 비교 `secret_eq` (225).
- 테스트 있음 (`egress.rs:602` 이하).

### `ember/node/src/exec.rs` (275줄)
- 목적: 명령 실행 (FR-X1). 모든 명령은 자기 프로세스 그룹의 리더로 돈다 (3-4). 종료 이벤트가 항상 마지막이고, 종료 후 출력은 `DRAIN_GRACE` 2초까지 비운다 (22).
- 심볼: `spawn_pipes` 141, `spawn_pty` 192, `argv` 100(`Program`을 argv로), `Control::{write_stdin,close_stdin,resize}` 43-69, `kill_group` 82(유닉스 `killpg`) / 91(Windows는 신호 무시하고 `taskkill /T /F`).
- 사용처: `api.rs` `/exec`, `jobs.rs`, 서버 shim (`SIGINT`).

### `ember/node/src/exec_server.rs` (159줄)
- 목적: Codex `exec-server --listen stdio`를 노드에서 띄우고 WebSocket 바이트를 그대로 중계 (`/exec-server`). 첫 허용 root에서 시작 (`bridge`, 79 이하).
- 심볼: `codex_bin` 43(`EMBER_NODE_CODEX_BIN`, 기본 `codex`), `run_stdio` 57(`ember-node exec-server`), `ws` 75, `NodeClient::exec_server` 156.
- 주의점: 이 실행기는 경로 정책의 제한을 받지 않는다 (codex 자체 샌드박스에 의존, 머리 주석 "Known limits"). 소켓이 닫히면 stdin을 닫고 3초 뒤 kill (`EXIT_GRACE`, 41).

### `ember/node/src/fs.rs` (586줄)
- 목적: 파일 조작 14종 (블로킹, API 계층이 blocking pool에서 실행).

| 이름 | 줄 | 설명 |
|---|---|---|
| `write` | 393 | 같은 디렉터리의 임시 파일(`.<name>.ember-<uuid>.tmp`)에 쓰고 `sync_all` 후 `rename`. `expect`(`Absent` 또는 `Sha256`) 불일치면 `Precondition` 오류. 기존 권한 비트 유지 |
| `read` | 362 | 오프셋/길이 읽기, 최대 `MAX_READ` 16 MiB (`proto.rs:307`), 선택적 전체 해시 |
| `list` | 453 | 디렉터리 항목과 mode/ino |
| `walk` | 497 | `ignore::WalkBuilder`, `follow_links(false)`, denied 항목은 걸러낸다 |
| `glob`, `grep` | 509, 527 | 기본 limit 1000 |
| `stat/lstat/readlink/symlink/mkdir/remove/rename/setattr/pwrite` | 187-340 | 마운트용 네임스페이스 연산 |
| `errno_name`, `io_errno` | 123, 154 | OS 오류를 이식 가능한 errno 이름으로 |
- 주의점: 정책 확인과 실제 연산 사이에 경쟁이 있다 (`write`의 "no race-free guarantee" 주석, 399-401). 사전조건 확인과 rename은 데몬 안 쓰기 락으로만 원자적이고 다른 프로세스에는 해당 없다 (`write` 위 문서 주석).

### `ember/node/src/jobs.rs` (204줄)
- 목적: 백그라운드 잡 (FR-X4)과 노드 이벤트 로그. 잡은 연결이 아니라 데몬이 소유한다. 출력은 잡당 `TAIL_BYTES` 256 KiB 링 버퍼 (23), 이벤트는 `EVENT_HISTORY` 1024개 (25).
- 심볼: `Jobs::start` 100, `list` 155, `get` 162, `kill` 179, `remove` 193(실행 중이면 `StillRunning`), `subscribe` 93(`after` 이후 백로그 + broadcast), `emit` 80, `boot_id` 76.
- 주의점: 데몬이 재시작하면 잡은 사라진다 (`jobs.rs:9`, `lib.rs:19`).

### `ember/node/src/transport.rs` (197줄) [보안]
- 목적: 같은 라우터를 transport 서비스 `ember-node`로 서빙 (FR-N1, FR-N3, FR-N5). 한 스트림이 HTTP/1.1 연결 하나라 WebSocket이 그대로 동작한다.
- 허용 피어: `EMBER_NODE_ALLOWED_PEERS` + `<state>/allowed-peers` 파일을 합친 목록 (`allowed_peers`, 117-135)만 accept 단계에서 통과, 나머지는 요청을 읽기 전에 닫는다 (`PeerGate`, `serve` 145-155). 베어러 토큰도 추가로 필요하다 (6-12).
- `TransportMode::parse/from_env_or_state` 51-68(`0`/`1`/`only`), `bind` 138(키는 `<state>/transport.key`, `hub::discovered_transport_config`). 테스트 있음 (157 이하).

### `ember/node/src/hub.rs` (466줄)
- 목적: darkpyonix.dev hub와의 연동 (FR-N2). 장치 링크로 등록, 앱 레코드 게시, 주소 디렉터리와 relay 발견, 철회 감시, 선택적으로 계정의 main server를 허용 목록에 추가.
- 심볼: `register` 126, `leave` 256, `spawn_watch` 325(장기 폴링, 없으면 60초 `WATCH_PERIOD`, 43), `apply_registration` 245, `discovered_transport_config` 234, `allow_servers_from_env` 45(`EMBER_NODE_HUB_ALLOW_SERVERS`), `cli` 388.
- 파일: `<state>/hub.json`(0600, 장치 토큰과 resolve 토큰 `***`), `<state>/hub-link.json`(승인 대기 링크, 50).
- CLI 문구(사용자에게 보임): `usage: ember-node hub <register [--name NAME] | status | forget [--local]>` (454), `the hub is off (EMBER_HUB_URL=off)` (402).

### `ember/node/src/client.rs` (766줄)
- 목적: 서버가 쓰는 `NodeClient`. HTTP(`new`, 175) 또는 transport(`over_transport`, 222) 위에서 같은 API를 호출한다. 요청마다 `bearer_auth(token)`을 붙인다 (257).
- 메서드: `health` 383, `env` 388, `metrics` 393, `ports` 401, fs 계열 405-476, `exec` 481, `run` 500, `start_job`/`jobs`/`job`/`kill_job`/`remove_job` 520-540, `events` 545, `term_*` 553-601, `post_raw` 322(git 등 임의 POST 중계용). 스트림 타입 `TermAttachment`, `ExecSession`, `EventStream`과 헬퍼 `shell` (759).
- `NODE_SERVICE = "ember-node"` (45). `with_deadline` 198로 요청 마감 시간을 둔다.

### `ember/node/src/proto.rs` (947줄)
- 목적: 와이어 타입. `ErrorBody`/`ErrorCode` (33, 48: `unauthorized`, `forbidden_path`, `not_found`, `precondition_failed`, `bad_request`, `internal`, `not_a_repo`, `conflict`, `timeout`, `too_large`), 환경/메트릭(71-200), 포트(203-250), 파일(253-520), 실행(522-600), 잡/이벤트(600-675), 터미널(678-940).
- 주의점: [client](client.md) 모듈은 같은 DTO를 자체 정의한다. 한쪽을 바꾸면 양쪽을 고친다.

### 작은 파일

| 파일 | 줄 | 설명 |
|---|---|---|
| `ember/node/src/lib.rs` | 44 | 모듈 선언 (`pub mod api` ... `transport`, 25-44)과 크레이트 설명. `git_conflict`만 최상위로 선언 (36) |
| `ember/node/src/envinfo.rs` | 163 | `describe` 141: OS, 커널, 호스트명, 사용자, HOME, 셸, roots, PATH에서 찾은 도구 버전. 데몬의 `PATH` 기준 (3-5). `which` 41 |
| `ember/node/src/metrics.rs` | 176 | `sample(top)` 60: CPU, 메모리, 디스크, 네트워크, 온도, 상위 프로세스 (`sysinfo`). `DEFAULT_TOP` 20, `MAX_TOP` 200. GPU는 사유와 함께 빈 값 (`GPU_UNAVAILABLE`, 23). 테스트 있음 (130) |
| `ember/node/src/ports.rs` | 518 | `listening(roots)` 258: 노드가 시작한 터미널/잡의 자손 프로세스가 listen 중인 TCP 포트 (FR-P7). 실행 파일 이름만 노출하고 명령줄, 환경, cwd, 사용자는 노출하지 않는다 (3-6). `/proc/net/tcp` 파싱 (88), `lsof` 경로 (139, 357) |
| `ember/node/Cargo.toml` | 49 | 크레이트 `ember-node`. feature `letify`는 transport 백엔드 (43-45). dev 의존에 `ember-hub`(fake) |
| `ember/node/service/ember-node.service` | 22 | systemd 사용자 유닛. `EnvironmentFile=%h/.config/ember-node.env`에서 토큰을 읽고 `KillMode=process`로 PTY keeper를 살린다 (주석 6-8, 15, 17) |
| `ember/node/service/ember.node.plist` | 31 | launchd 설정. `EMBER_NODE_TOKEN` 값은 자리표시자 `CHANGE_ME` (22) |

## 동작 지도

git 라우트(`/git/*` 전부)는 [node-git](node-git.md)에 있다. 아래는 비 git 라우트 전체다. 라우트 등록은 `ember/node/src/api.rs:156-228`, 인증은 `/health` 제외 전부 `auth` (`api.rs:240`).

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `GET /health` | `health` `api.rs:348` | 없음 | `Health{ok,version}` |
| `GET /env` | `env` `api.rs:352` | `envinfo::describe` `envinfo.rs:141` | 호스트 정보, 도구 버전 |
| `GET /metrics?top=` | `metrics` `api.rs:356` | `metrics::sample` `metrics.rs:60` | `MetricsSample` |
| `POST /fs/stat` | `stat` `api.rs:364` | `fs::stat` `fs.rs:187` | 파일 메타데이터 |
| `POST /fs/read` | `read` `api.rs:368` | `fs::read` `fs.rs:362` | 파일 내용 (16 MiB 이하) |
| `POST /fs/write` | `write` `api.rs:372` | `fs::write` `fs.rs:393` | 파일 (원자적 교체, 쓰기 락) |
| `POST /fs/list` | `list` `api.rs:378` | `fs::list` `fs.rs:453` | 디렉터리 항목 |
| `POST /fs/lstat` | `lstat` `api.rs:382` | `fs::lstat` `fs.rs:194` | 링크 자체의 메타데이터 |
| `POST /fs/readlink` | `readlink` `api.rs:386` | `fs::readlink` `fs.rs:200` | 링크 대상 |
| `POST /fs/symlink` | `symlink` `api.rs:393` | `fs::symlink` `fs.rs:206` | 심볼릭 링크 생성 (쓰기 락) |
| `POST /fs/mkdir` | `mkdir` `api.rs:399` | `fs::mkdir` `fs.rs:224` | 디렉터리 생성 (쓰기 락) |
| `POST /fs/remove` | `remove` `api.rs:405` | `fs::remove` `fs.rs:242` | 삭제, 204 (root 자체는 `is_root`로 거부) |
| `POST /fs/rename` | `rename` `api.rs:411` | `fs::rename` `fs.rs:261` | 이동, 204 |
| `POST /fs/setattr` | `setattr` `api.rs:564` | `fs::setattr` `fs.rs:288` | chmod, truncate, utimes |
| `POST /fs/pwrite` | `pwrite` `api.rs:570` | `fs::pwrite` `fs.rs:340` | 제자리 위치 쓰기 |
| `POST /fs/glob` | `glob` `api.rs:576` | `fs::glob` `fs.rs:509` | 경로 목록 (limit 1000) |
| `POST /fs/grep` | `grep` `api.rs:580` | `fs::grep` `fs.rs:527` | 일치 목록 (limit 1000) |
| `GET /exec` (WS) | `exec_ws` `api.rs:639` -> `exec_session` `api.rs:643` | `exec::spawn_pty`/`spawn_pipes` `exec.rs:192`/`141` | 자식 프로세스 (연결 종료 시 그룹 kill) |
| `GET /exec-server` (WS) | `exec_server::ws` `exec_server.rs:75` | 같은 파일 `bridge` `:79` | `codex exec-server` 자식 |
| `GET /egress` (WS) | `egress::ws` `egress.rs:425` | `serve_socks5` `egress.rs:366`, `connect` `egress.rs:332` | 외부 TCP 연결 |
| `POST /jobs` | `start_job` `api.rs:584` | `Jobs::start` `jobs.rs:100` | 인메모리 잡 (201) |
| `GET /jobs` | `list_jobs` `api.rs:594` | `Jobs::list` `jobs.rs:155` | `[JobInfo]` |
| `GET /jobs/{id}?tail=` | `get_job` `api.rs:603` | `Jobs::get` `jobs.rs:162` | `JobDetail` (404 `no job <id>`) |
| `POST /jobs/{id}/kill` | `kill_job` `api.rs:610` | `Jobs::kill` `jobs.rs:179` | 204 |
| `DELETE /jobs/{id}` | `remove_job` `api.rs:623` | `Jobs::remove` `jobs.rs:193` | 204, 실행 중이면 409 |
| `GET /events?after=` (WS) | `events_ws` `api.rs:740` -> `events_session` `api.rs:744` | `Jobs::subscribe` `jobs.rs:93` | 이벤트 로그 |
| `GET /ports` | `list_ports` `api.rs:796` | `ports::listening` `ports.rs:258` | `PortsResponse` |
| `POST /terms` | `create_term` `api.rs:780` | `Terms::create` ([node-term](node-term.md)) | 201 생성, 200 키 일치 |
| `GET /terms` | `list_terms` `api.rs:812` | `Terms::list` | `[TermInfo]` |
| `GET /terms/{id}` | `get_term` `api.rs:816` | `Terms::get` | `TermInfo` |
| `DELETE /terms/{id}` | `remove_term` `api.rs:851` | `Terms::remove` | 204, 실행 중이면 409 |
| `GET /terms/{id}/snapshot` | `term_snapshot` `api.rs:820` | `Session::snapshot` `term/session.rs:263` | `TermSnapshot` |
| `GET /terms/{id}/attach` (WS) | `term_attach_ws` `api.rs:859` -> `term_attach_session` `api.rs:863` | `Session::attach/input/resize/control/kill/detach` | 터미널 세션 |
| `POST /terms/{id}/control` | `term_control` `api.rs:827` | `Session::control` `term/session.rs:454` | 204 |
| `POST /terms/{id}/kill` | `kill_term` `api.rs:838` | `Terms::kill` | 204 (기본 SIGHUP 후 SIGKILL) |

### 사용자에게 보이는 에러 메시지

| 원문 | 위치 | 조건 |
|---|---|---|
| `missing or invalid bearer token` | `api.rs:250` | 토큰 없음/불일치 (401) |
| `path is outside the allowed roots: <path>` | `policy.rs:23` | root 밖이거나 denied (403 `forbidden_path`) |
| `path must be absolute: <path>` | `policy.rs:21` | 상대 경로 (400) |
| `no job <id>` | `api.rs:607`, `:619`, `:626` | 잡 없음 (404) |
| `job is still running` | `api.rs:627` | 실행 중 잡 삭제 (409) |
| `no terminal session <id>` | `api.rs:777`, `:878` | 터미널 없음 (404, WS는 에러 이벤트) |
| `session is still running` | `api.rs:855` | 실행 중 세션 삭제 (409) |
| `this session has no screen (lost, or finished before the node restarted)` | `api.rs:823` | 화면 스냅샷 없음 (409) |
| `bad exec request: <e>`, `bad hello: <e>` | `api.rs:649`, `:869` | 첫 WS 프레임 파싱 실패 |
| `dropped: this client fell behind; re-attach for a fresh snapshot` | `api.rs:933` | 느린 터미널 클라이언트 |
| `egress is disabled on this node (EMBER_NODE_EGRESS)` | `egress.rs:430` | 출구 꺼짐 (403) |
| `EMBER_NODE_TOKEN must be set to a non-empty secret or this node enrolled (ember-node enrol)` | `config.rs:113` | 토큰 없이 기동 |
| `token must not be empty` | `api.rs:116` | `Node::new` |

### 보안 코드 요약
- 토큰 인증: `api.rs:236-253`. `/health` 외 전 라우트에 `route_layer`로 적용 (227), WebSocket 업그레이드도 같은 미들웨어를 지난다. 상수 시간 비교(`token_eq`).
- 경로 정책: `policy.rs` (위 절). 모든 fs 함수와 git, `/exec`, `/jobs`, `/terms`의 cwd가 거친다 (`api.rs:585`, `:781`, `exec_session`의 `resolve_existing`).
- egress: `egress.rs` (위 절). 토큰 + 선택적 deny 목록. 기본은 전부 허용.
- transport: 허용 피어 + 토큰 이중 확인 (`transport.rs:6-12`).

## 데이터와 설정

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_NODE_TOKEN` | `config.rs:55`, `:104` | 베어러 토큰 (`***`) | 없음 (없으면 `enrol.json`) |
| `EMBER_NODE_LISTEN` | `config.rs:137` | 리슨 주소 | `127.0.0.1:8741` (`config.rs:9`) |
| `EMBER_NODE_ROOTS` | `config.rs:69` | 허용 root (`:` 구분) | `$HOME` / `USERPROFILE` |
| `EMBER_NODE_DENY` | `config.rs:118` | 거부 경로 | 없음 |
| `EMBER_NODE_STATE_DIR` | `config.rs:126` | 상태 디렉터리 | `$HOME/.ember/node` |
| `EMBER_NODE_KEEP_PTY` | `config.rs:77` | `0/false/no`면 PTY keeper 끔 | 켜짐 |
| `EMBER_NODE_EGRESS`, `EMBER_NODE_EGRESS_DENY` | `egress.rs:158` | 출구 정책 | 켜짐, 거부 없음 |
| `EMBER_NODE_SOCKS_LISTEN` | `main.rs` `serve` | 평문 SOCKS5 주소 | 꺼짐 |
| `EMBER_NODE_CODEX_BIN` | `exec_server.rs:39` | codex 실행 파일 | `codex` |
| `EMBER_NODE_TRANSPORT` | `transport.rs:33` | `1`/`only` | TCP만 |
| `EMBER_NODE_ALLOWED_PEERS` | `transport.rs:34` | 허용 피어 id | 없음 |
| `EMBER_NODE_HUB_ALLOW_SERVERS` | `hub.rs:41` | hub 계정의 main server 허용 | 꺼짐 |
| `EMBER_RELAY_URL`, `EMBER_HUB_URL` | `transport.rs:18`, `main.rs` 머리 주석 | relay, hub (`off`로 끔) | hub는 `https://api.darkpyonix.dev` |
| `RUST_LOG` | `main.rs` `serve` | tracing 필터 | `info` |

- 저장 파일(`<state>` 아래): `local.json`, `transport.key`(0600), `allowed-peers`, `hub.json`(0600), `hub-link.json`, `enrol.json`([node-enrol](node-enrol.md)), 터미널 메타데이터([node-term](node-term.md)). DB는 없다. 잡과 이벤트는 메모리에만 있다.
- 외부 연동: 서버(HTTP 또는 transport), darkpyonix.dev hub와 relay, `codex`, `git`/`gh`([node-git](node-git.md)), `lsof`(`ports.rs:357`).

## 이 모듈을 수정할 때 주의할 점

- 라우트를 추가하면 `api.rs`의 `router`, 머리 주석 표, `client.rs`의 메서드, `proto.rs`의 타입, `ember/client/src/api.rs`의 자체 DTO를 함께 고친다. 새 라우트는 `authed` 라우터 안에 넣어야 인증이 걸린다 (`api.rs:227`).
- `proto.rs` 타입을 바꾸면 `ember/server/src/computers/*`(28곳 import)와 [client](client.md)가 영향을 받는다. AGENTS.md 규칙상 의존 크레이트의 `Cargo.lock`을 같은 PR에서 갱신한다.
- 파일 변경 핸들러는 `write_lock`을 잡아야 사전조건 확인과 rename이 원자적이다. 오래 걸리는 작업(네트워크 git)에서는 잡지 않는다.
- `EMBER_NODE_TRANSPORT=only`이면 `local.json`이 안 써져 `ember-term`이 데몬을 못 찾는다 (`transport.rs:21-23`).
- 서비스 파일의 `KillMode=process`를 바꾸면 PTY keeper와 영속 터미널이 같이 죽는다.
- `egress`와 `exec_server`는 `Node`의 접근자(`egress_policy`, `policy`)를 쓴다. 이름을 바꾸면 두 파일도 고친다.

## 이슈 후보

TODO/FIXME는 이 모듈 파일에서 0개 (grep 확인). 쓰이지 않는 pub 심볼은 점검하지 않았다 [확인 필요].

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 중간 | `egress.rs:35-38`, `:137-141` | 기본 egress 정책이 전부 허용이라 클라우드 메타데이터(169.254.169.254)와 노드의 loopback/LAN에 토큰 소지자가 닿는다. 의도된 기본(FR-R1)이지만 공용 서버에서는 위험 | 배포 문서에 `EMBER_NODE_EGRESS_DENY=link-local` 권장 추가 검토 |
| 보안 | 중간 | `egress.rs:413-420` | `EMBER_NODE_SOCKS_LISTEN`의 loopback 피어는 인증이 없다. 같은 컴퓨터의 모든 프로세스가 출구로 쓸 수 있다 | 문서화, 필요하면 인증 강제 옵션 |
| 보안 | 중간 | `config.rs:137`, `api.rs:236-253` | 토큰은 평문 HTTP로 전달된다. `EMBER_NODE_LISTEN`을 loopback 밖으로 두면 도청과 무차별 대입에 노출되고 시도 횟수 제한도 없다 | loopback 밖 바인딩 시 경고, 또는 transport 사용 안내 |
| 보안 | 낮음 | `api.rs:236` | `token_eq`는 길이가 다르면 즉시 반환해 토큰 길이가 새는 이론적 경로가 있다 | 수용 가능, 해시 후 비교로 대체 가능 |
| 보안 | 중간 | `policy.rs:14-15`, `exec_server.rs` 머리 주석 | 경로 정책은 명령을 제한하지 않는다. `/exec`, `/jobs`, `/terms`, `/exec-server`를 호출할 수 있으면 토큰 소지자는 사용자 권한으로 무엇이든 한다 | 설계상 의도. 토큰 보관(서비스 env 파일 0600)이 사실상 경계 |
| 보안 | 낮음 | `fs.rs:399-401`, `policy.rs` `with_denied` 주석 | 정책 확인과 연산 사이 TOCTOU, denied는 inode가 아니라 경로 기준 | 문서화된 한계 |
| 정확성 | 낮음 | `api.rs:1-72`, `:158` | 머리 주석 라우트 표에 `GET /metrics`가 빠졌다 | 표에 추가 |
| 구조 | 중간 | `api.rs` (971줄), `proto.rs` (947줄) | `api.rs`에 git, 잡, 터미널, WS 핸들러가 섞여 있다 | 라우트군별 파일 분리 |
| 중복 | 낮음 | `api.rs:236`, `egress.rs:225` | 상수 시간 비교 함수가 두 군데에 같은 구현 | 공용 헬퍼로 합치기 |
| 이식성 | 낮음 | `exec.rs:91-98` | Windows `kill_group`은 신호 종류를 무시하고 항상 강제 종료 | 문서화 |
| 하드코딩 | 낮음 | `api.rs:231`, `egress.rs:60-62`, `jobs.rs:23-25` | 본문 64 MiB, 타임아웃 15/30초, 버퍼 256 KiB, 이벤트 1024 | 필요 시 설정화 |
