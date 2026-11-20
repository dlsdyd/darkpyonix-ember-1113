# 모듈: editor-conn

- 경로: `ember/editor-conn/` (크레이트 `ember-editor-conn`, 라이브러리 이름 `ember_editor_conn`, `ember/editor-conn/Cargo.toml:2`, `:9`)
- 규모: 파일 18개 / 약 5,686줄 (`Cargo.lock` 478줄과 `tests/`는 제외)
- 레이어: 인프라
- 한 줄 책임: 수정하지 않은 Code-OSS(VS Code) 서버와 공식 Node 확장 호스트에 Rust로 붙는 연결 계층. HTTP 업그레이드와 핸드셰이크, 13바이트 프레이밍, `PersistentProtocol`(ack, replay), 관리 연결 IPC, 원격 파일시스템, 확장 호스트 RPC, 문서 동기화, 텍스트 검색 DTO를 담당한다 (`ember/editor-conn/src/lib.rs:1-27`).
- 의존하는 모듈: 없음 (저장소 내부 크레이트 의존 없음. 외부 크레이트는 `serde`, `serde_json`, `thiserror`, `tokio`, `tracing`, `uuid`, `ember/editor-conn/Cargo.toml:12-18`)
- 이 모듈을 쓰는 모듈: [editor](editor.md) (거의 전부), [app-core](app-core.md) (`ember/app/src/editor_host.rs:5`, `:138`), [app-ui-dev](app-ui-dev.md) (`ember/app/src/ui/editor.rs:311`, `ember/app/src/ui/editor_search.rs:12`, `ember/app/src/ui/editor_workbench.rs:75`, `:178`)

## 전체 구조

계층은 아래에서 위로 쌓인다 (`ember/editor-conn/src/lib.rs:10-24`).

| 계층 | 파일 | 하는 일 |
|---|---|---|
| 1 | `frame.rs` | 13바이트 헤더 프레임 인코딩, 디코딩 |
| 2 | `protocol.rs` | `PersistentProtocol` 상태 기계 (IO 없음): id, ack, replay, pause, 타이머 판단 |
| 3 | `connection.rs` | tokio 소켓 드라이버: reader, writer, ticker 태스크, 전송 교체 |
| 4 | `handshake.rs` | `GET /version` 버전 게이트, HTTP 업그레이드, auth → sign → connectionType, 재연결 |
| 5a | `ipc.rs` → `remote_fs.rs`, `management.rs` | 관리 연결의 IPC 채널 클라이언트와 그 위의 채널 |
| 5b | `exthost.rs` → `rpc.rs`, `rpc_ids.rs` | 확장 호스트 초기화와 RPC 피어, 프록시 번호 표 |
| 6 | `document.rs`, `search.rs`, `uri.rs` | 문서 미러, 텍스트 검색 쿼리와 결과, `UriComponents` |

연결 순서 (실제 호출은 `ember/editor/src/session.rs:192-270`):
1. 새 스트림으로 `handshake::verify_server` → 서버 커밋이 `PINNED_COMMIT`인지 확인 (`ember/editor-conn/src/handshake.rs:271-278`).
2. `handshake::connect(.., ConnectionType::Management, None)` → `IpcClient::start` → `management::get_environment_data`, `scan_extensions` → `RemoteFs::new`.
3. `handshake::connect(.., ConnectionType::ExtensionHost, Some(start_params))` → `exthost::initialize(conn, &init_json)` → `RpcPeer`.
4. `exthost::bootstrap_calls`를 먼저 보낸 뒤에야 확장이 활성화된다 (`ember/editor-conn/src/exthost.rs:10-14`, `:356-365`).

## 버전 고정 (`rpc_ids.rs`와 함께 바꿔야 하는 것)

확장 호스트 RPC는 대상 액터를 이름이 아니라 1바이트 번호로 부른다. 번호는 upstream `extHost.protocol.ts`에서 `createProxyIdentifier(...)`가 선언된 순서대로 매겨진다. 그래서 upstream이 중간에 하나를 끼우면 뒤의 번호가 전부 밀린다 (`ember/editor-conn/src/rpc_ids.rs:3-10`).

생성 방법 (`ember/editor-conn/scripts/gen_rpc_ids.sh:1-39`):
- 인자로 `microsoft/vscode` 체크아웃 경로를 받는다. 체크아웃은 `ember/ose/VERSION`의 태그여야 한다 (`gen_rpc_ids.sh:4-6`).
- `src/vs` 안에서 `extHost.protocol.ts`와 `proxyIdentifier.ts` 말고 `createProxyIdentifier`를 부르는 `.ts` 파일이 있으면 종료 코드 2로 실패한다. 모듈 로드 순서가 번호에 영향을 주게 되기 때문이다 (`gen_rpc_ids.sh:24-33`).
- `extHost.protocol.ts`에서 `createProxyIdentifier<`가 있는 줄을 순서대로 뽑아 `    "Name", // N` 줄을 stdout에 쓴다 (`gen_rpc_ids.sh:35-37`). 커밋 해시는 stderr에 쓴다 (`:39`).
- 출력은 `pub const PROXY_IDS: &[&str] = &[`와 `];` 사이에 붙여 넣는다 (`gen_rpc_ids.sh:8-10`). 현재 표는 168개다 (`ember/editor-conn/src/rpc_ids.rs:21-190`, 마지막 `ExtHostBrowsers`는 168, `:234`).

CI 검사 (`.github/workflows/test.yml:120-164`, job `editor-conn-pin`, 이름 "Editor-conn pin matches OSE"):
- `ember/ose/VERSION`(현재 `1.139.1`)의 태그를 sparse로 clone하고 커밋을 읽는다 (`test.yml:133-141`).
- 스크립트 출력과 `rpc_ids.rs`의 표 본문을 `diff -u`로 비교한다 (`test.yml:143-155`).
- `lib.rs`에 `pub const PINNED_VERSION: &str = "<tag>";`와 `pub const PINNED_COMMIT: &str = "<commit>";`가 **그 모양 그대로 한 줄**로 있는지 `grep -qx`로 확인한다 (`test.yml:156-163`).

한 번에 같이 바꿔야 하는 것:

| 항목 | 위치 | 이유 |
|---|---|---|
| OSE 빌드 태그 | `ember/ose/VERSION` | 핀의 원본. `pin_matches_ose_version` 테스트가 읽는다 (`ember/editor-conn/src/lib.rs:162-171`) |
| `PINNED_VERSION` | `ember/editor-conn/src/lib.rs:57` | VERSION과 같아야 한다 |
| `PINNED_COMMIT` | `ember/editor-conn/src/lib.rs:60` | 태그의 커밋. 소문자 40자 hex여야 한다 (`lib.rs:174-177`) |
| `PROXY_IDS` 표 | `ember/editor-conn/src/rpc_ids.rs:21-190` | 스크립트 출력 그대로 |
| 손으로 계산한 번호 점검 | `ember/editor-conn/src/rpc_ids.rs:216-237` | 새 표에서 번호가 바뀌면 같이 고친다 |
| upstream 줄 번호 주석 | `exthost.rs`, `rpc.rs`, `protocol.rs`, `handshake.rs` 등 (`extHost.protocol.ts L...`) | 시그니처가 바뀌었는지 다시 읽어야 한다. `MainThreadCall::parse`의 인자 위치(`exthost.rs:674-753`)는 upstream 시그니처에 묶여 있다 |
| 런타임 게이트 | `ember/editor-conn/src/lib.rs:66-79`, `handshake.rs:271-278` | 다른 커밋의 서버는 `Error::UnsupportedServerVersion`으로 거절된다. 핀을 올리면 이전 OSE 서버에 못 붙는다 |

런타임에는 세 겹으로 막는다: `check_server_commit`(`lib.rs:66`), `connect`가 `opts.commit`을 미리 검사(`handshake.rs:335-337`), 서버가 "Client refused: version mismatch"로 거절하면 `UnsupportedServerVersion { server: None }`로 바꾼다 (`handshake.rs:183`, `:189-191`). 확장 호스트 초기화 데이터에도 같은 커밋을 넣는다 (`exthost.rs:70-73`, `:137-139`).

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `PINNED_VERSION`, `PINNED_COMMIT` | 상수 | `ember/editor-conn/src/lib.rs:57`, `:60` | 고정한 Code-OSS 태그와 커밋. `ember/editor/src/fallback.rs:31-36`, `ember/editor/src/session.rs:35`에서 쓴다 |
| `Error` | enum | `ember/editor-conn/src/lib.rs:83-114` | 모든 계층의 에러. `ember/editor/src/lib.rs:72`가 `Error::Conn`으로 감싼다 |
| `RemoteError` | struct | `ember/editor-conn/src/lib.rs:118-151` | 상대편 IPC, RPC 에러. `fs_code()`로 `EntryNotFound` 등을 얻는다 |
| `handshake::{verify_server, connect, ConnectOptions, ConnectionType, ExtensionHostStartParams}` | 함수, 타입 | `handshake.rs:271`, `:326`, `:55`, `:33`, `:41` | 세션 열기 (`ember/editor/src/session.rs:192-226`) |
| `ipc::{IpcClient, IpcLifecycle}` | 타입 | `ipc.rs:258`, `:243` | 관리 연결 IPC (`ember/editor/src/session.rs:30`, `:210`) |
| `management::{get_environment_data, scan_extensions, RemoteAgentConnectionContext}` | 함수, 타입 | `management.rs:60`, `:77`, `:28` | 환경 데이터, 확장 목록 (`ember/editor/src/session.rs:211-212`) |
| `remote_fs::{RemoteFs, Stat, file_type, WriteOptions, DeleteOptions, WatchOptions, WatchEvent, FileChange, FileChangeType}` | 타입, 상수 | `remote_fs.rs:123`, `:34`, `:25`, `:56`, `:72`, `:81`, `:117`, `:100`, `:92` | 원격 파일 읽기, 쓰기, 감시 (`ember/editor/src/session.rs:32`, `ember/app/src/editor_host.rs:138`, `ember/app/src/ui/editor.rs:311`) |
| `rpc::{RpcPeer, Reply, Arg, IncomingRequest, RpcEvent, js_error}` | 타입, 함수 | `rpc.rs:375`, `:90`, `:64`, `:347`, `:358`, `:480` | 확장 호스트 RPC (`ember/editor/src/engine.rs:20`, `ember/editor/src/session.rs:33`) |
| `exthost::*` | 함수, DTO | `exthost.rs` 전역 | 초기화, 나가는 호출 생성기(`Call`), 들어오는 호출 해석(`MainThreadCall`), `default_reply` |
| `document::{DocumentMirror, EditorChange, TextEdit, EditReason, split_lines}` | 타입, 함수 | `document.rs:113`, `:44`, `:28`, `:34`, `:83` | 문서 미러 (`ember/editor/src/document.rs:20`, `ember/editor/src/coords.rs:174`) |
| `search::{TextQuery, FileMatch, expand_patterns, provide_text_search_results, SearchComplete, DEFAULT_EXCLUDES, ...}` | 타입, 함수 | `search.rs:46`, `:237`, `:187`, `:200`, `:277`, `:33` | FR-E7 텍스트 검색 (`ember/editor/src/search.rs:15`, `ember/editor/src/engine.rs:1340`) |
| `uri::{UriComponents, SCHEME_REMOTE}` | 타입, 상수 | `uri.rs:19`, `:16` | URI 마샬링. editor와 app 양쪽이 쓴다 |

## 파일별 요약

### `ember/editor-conn/src/lib.rs` (약 191줄)
- **목적:** 크레이트 루트. 모듈 선언, 버전 핀, 공통 에러 타입.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PINNED_VERSION` | 상수(pub) | 57 | `"1.139.1"`. `ember/ose/VERSION`과 같아야 한다 |
  | `PINNED_COMMIT` | 상수(pub) | 60 | `"04c0d99f..."` 40자 커밋 |
  | `check_server_commit(server_commit)` | 함수(pub) | 66 | 공백을 자른 값이 `PINNED_COMMIT`이면 Ok. 아니면 `UnsupportedServerVersion`. 64자 이하 영숫자와 `-_.`만 있으면 `server: Some`, HTML 등은 `None` (`:71-76`) |
  | `Error` | enum(pub) | 83 | `Io`, `Json`, `Malformed`, `Handshake`, `Refused`, `Closed`, `Timeout`, `Remote`, `UnknownProxy`, `UnsupportedServerVersion` |
  | `RemoteError` | struct(pub) | 118 | `name`, `message`, `raw`. `from_json`(`:136`), `fs_code`(`:148`) |
  | `Result<T>` | 타입 | 153 | 크레이트 공통 결과 |
- **입력 → 출력:** 서버 커밋 문자열 → Ok 또는 거절 에러.
- **의존:** 모든 하위 모듈을 선언한다 (`:41-53`).
- **사용처:** `ember/editor/src/fallback.rs:31`, `:112`, `ember/editor/src/lib.rs:72`, `ember/editor/src/session.rs:35`.
- **부수효과:** 없음.
- **주의점:** CI가 `PINNED_VERSION`, `PINNED_COMMIT` 줄을 `grep -qx`로 정확히 찾으므로 줄 모양(공백, 타입 표기)을 바꾸면 CI가 실패한다 (`.github/workflows/test.yml:156-160`).
- **테스트:** 3개. VERSION 파일 일치, 커밋 형식, `check_server_commit` 동작.

### `ember/editor-conn/src/frame.rs` (약 187줄)
- **목적:** `PersistentProtocol`의 13바이트 헤더 프레임 (`TYPE u8 | ID u32be | ACK u32be | LEN u32be | DATA`, `frame.rs:8-10`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `HEADER_LEN` | 상수(pub) | 15 | 13 |
  | `MAX_FRAME_LEN` | 상수(pub) | 18 | 256 MiB. upstream에는 없는 방어용 상한 |
  | `MessageType` | enum(pub) | 23 | `None 0`, `Regular 1`, `Control 2`, `Ack 3`, `Disconnect 5`, `ReplayRequest 6`, `Pause 7`, `Resume 8`, `KeepAlive 9` |
  | `Frame` | struct(pub) | 55 | `ty`, `id`, `ack`, `data`. `encode`, `encode_into` (`:73`, `:79`) |
  | `FrameDecoder::next_frame` | 함수(pub) | 114 | 버퍼에서 완전한 프레임 하나를 꺼낸다. 모자라면 `Ok(None)` |
- **입력 → 출력:** 바이트 조각 → `Frame`.
- **의존:** `lib.rs`의 `Error`.
- **사용처:** `connection.rs:19`, `protocol.rs:22`.
- **부수효과:** 없음.
- **주의점:** 모르는 타입 바이트는 `MessageType::None`으로 바꿔 무시한다 (`frame.rs:130-132`). 길이 초과는 `Malformed` 에러이고 connection이 소켓을 끊는다 (`connection.rs:201-206`).
- **테스트:** 4개. 헤더 바이트, keep-alive, 쪼개진 청크 디코딩, 모르는 타입.

### `ember/editor-conn/src/protocol.rs` (약 363줄)
- **목적:** upstream `PersistentProtocol`을 IO 없는 상태 기계로 옮긴 것. 어떤 프레임을 쓸지만 정한다 (`protocol.rs:1-17`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ACKNOWLEDGE_TIME` | 상수(pub) | 25 | 2초 안에 ack |
  | `TIMEOUT_TIME` | 상수(pub) | 27 | 20초간 수신 없으면 끊김 |
  | `KEEP_ALIVE_SEND_TIME` | 상수(pub) | 29 | 5초마다 keep-alive |
  | `REPLAY_REQUEST_INTERVAL` | 상수(pub) | 31 | replay 요청은 10초에 한 번 |
  | `RECONNECTION_GRACE_TIME` | 상수(pub) | 34 | 3시간. 저장소에서 쓰는 곳 없음 |
  | `RECONNECT_BACKOFF_SECS` | 상수(pub) | 37 | `[0,5,5,10,10,10,10,10,30]` |
  | `Inbound` | enum(pub) | 41 | `Regular`, `Control`, `Disconnect` |
  | `PersistentProtocol::send` | 함수(pub) | 117 | id를 1씩 올리고 ack를 실어 보낸다. 재연결 중이면 큐에만 넣는다 |
  | `receive` | 함수(pub) | 149 | ack로 큐를 줄이고, 순서 맞는 regular만 올린다. 틈이 있으면 `ReplayRequest` |
  | `tick` | 함수(pub) | 213 | 2초 지난 ack 보내기, 20초 타임아웃 판정 |
  | `begin_reconnect`, `end_reconnect` | 함수(pub) | 242, 252 | 재연결 시작, 끝나면 Ack와 미확인 큐 전체 재전송 |
- **입력 → 출력:** 프레임과 현재 시각 → 올릴 메시지와 쓸 프레임 목록.
- **의존:** `frame.rs`.
- **사용처:** `connection.rs:20`, `handshake.rs:27`.
- **부수효과:** 없음 (순수 상태).
- **주의점:** `Unacked::written_at`은 쓰기만 하고 읽지 않는다 (`protocol.rs:53`, `:123-125`, `:190-191`). Pause 중에는 frame이 `held`에 쌓이지만, `send_disconnect`는 pause를 무시한다 (`:144-145`).
- **테스트:** 7개. 번호와 ack, 큐 정리, 틈과 중복, replay, pause, 재연결, 타이머.

### `ember/editor-conn/src/connection.rs` (약 267줄)
- **목적:** `PersistentProtocol`을 실제 소켓에 붙이는 비동기 드라이버. 소켓을 바꿔도 프로토콜 상태는 유지된다 (`connection.rs:1-9`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `LostReason` | enum(pub) | 25 | `SocketClosed`, `Timeout` |
  | `ConnEvent` | enum(pub) | 34 | `Message`, `Disconnected`, `Lost` |
  | `ConnectionHandle` | struct(pub, Clone) | 55 | 보내는 쪽. `send`, `send_control`, `recv_control`, `close`, `replace_transport`, `finish_reconnect` (`:90-143`) |
  | `Connection::new(stream, initial)` | 함수(pub) | 67 | 핸들과 이벤트 수신기를 만든다 |
  | `attach` | 함수(내부) | 154 | writer, reader, ticker 태스크 3개를 띄운다 |
- **입력 → 출력:** `AsyncRead + AsyncWrite` 스트림 → `ConnEvent` 스트림과 control 메시지 큐.
- **의존:** `frame.rs`, `protocol.rs`.
- **사용처:** `handshake.rs:26`, `ipc.rs:26`, `rpc.rs:36`, `exthost.rs:26`.
- **부수효과:** tokio 태스크 생성, 소켓 읽기 쓰기, 500ms 주기 ticker (`connection.rs:240`).
- **주의점:**
  - `generation` 카운터로 이전 소켓의 태스크가 `Lost`를 보내지 못하게 막는다 (`:158`, `:179`, `:226`, `:245`). 새 태스크를 추가할 때도 이 검사를 넣어야 한다.
  - reader 태스크는 `Inner`의 강한 참조(`:190-191`)를 들고 있어 `Connection`을 버려도 소켓이 닫히거나 `close()`가 불릴 때까지 살아 있다 [추정].
  - `std::sync::Mutex`를 태스크 안에서 짧게 잡는다. `tick` 결과를 받은 뒤 같은 lock을 다시 잡는다 (`:250`, `:253`).
  - 테스트 없음.

### `ember/editor-conn/src/handshake.rs` (약 612줄)
- **목적:** 버전 게이트(`GET /version`), raw WebSocket 업그레이드(`skipWebSocketFrames=true`), auth → sign → connectionType 핸드셰이크, 재연결 (`handshake.rs:1-17`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ConnectionType` | enum(pub) | 33 | `Management 1`, `ExtensionHost 2`, `Tunnel 3` |
  | `ExtensionHostStartParams` | struct(pub) | 41 | 확장 호스트 연결의 `args` |
  | `ConnectOptions` | struct(pub) | 55 | host, path, connection token, reconnection token(UUID), commit, timeout 30초 (`:75-84`) |
  | `HandshakeMessage` | enum(pub) | 98 | `Auth`, `Sign`, `ConnectionType`, `Error`, `Ok` JSON |
  | `NO_CONNECTION_TOKEN` | 상수(pub) | 125 | 토큰이 없을 때 보내는 20자 `0` |
  | `upgrade` | 함수(pub) | 141 | 업그레이드 요청을 쓰고 `101`인지 확인. 헤더 뒤 남은 바이트를 돌려준다 |
  | `VERSION_MISMATCH_REASON` | 상수(pub) | 183 | `"Client refused: version mismatch"` |
  | `server_commit` | 함수(pub) | 206 | HTTP/1.0 `GET /version`, 본문을 문자열로. chunked도 푼다 (`:249-266`) |
  | `verify_server` | 함수(pub) | 271 | `server_commit` + `check_server_commit` |
  | `handshake` | 함수(pub) | 289 | auth 전송 → sign 10초 대기 → connectionType 전송 → 첫 응답 |
  | `connect` | 함수(pub) | 326 | 커밋 검사 → 업그레이드 → `Connection::new` → `handshake` |
  | `reconnect` | 함수(pub) | 346 | 같은 reconnection token으로 새 소켓 붙이기 |
  | `is_permanent` | 함수(pub) | 367 | `Refused`, `UnsupportedServerVersion`이면 재시도하지 않는다 |
  | `reconnect_loop` | 함수(pub) | 373 | 백오프 재시도 루프 |
- **입력 → 출력:** 스트림, `ConnectOptions` → `(Connection, 첫 응답 JSON)`.
- **의존:** `connection.rs`, `protocol.rs`.
- **사용처:** `ember/editor/src/session.rs:192`, `:201`, `:226`, `ember/editor-conn/examples/probe.rs:46`, `:57`.
- **부수효과:** 네트워크 쓰기와 읽기.
- **주의점:**
  - 서버 서명을 검증하지 않는다. 서버 진위는 전송 계층(TLS, ember-transport) 몫이라고 적혀 있다 (`:283-288`). connection token이 있으면 `auth`와 `signedData` 둘 다에 평문으로 실린다 (`:297`, `:313`).
  - `reconnect_loop`, `reconnect`, `is_permanent`는 제품 코드에서 부르지 않는다. editor 세션은 끊기면 `ConnectionLost`를 알리고 재연결은 하지 않는다 (`ember/editor/src/session.rs:20`) [확인 필요: 재연결을 의도적으로 뺀 것인지].
  - 업그레이드 응답 헤더 16 KiB, `/version` 응답 16 KiB 상한 (`:155`, `:221`).
- **테스트:** 9개. 메시지 JSON 모양, 키 길이, 비 101 거절, 가짜 서버와 관리 핸드셰이크, `/version` 파싱, 다른 커밋 거절, IO 없이 거절, 버전 불일치 타입, error 메시지.

### `ember/editor-conn/src/ipc.rs` (약 512줄)
- **목적:** Code-OSS `ipc.ts` 채널 프로토콜. 관리 연결이 쓴다 (`ipc.rs:1-16`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `data_type` | mod(내부) | 30 | 값 태그 0..6 |
  | `request_type`, `response_type` | mod(pub) | 40, 47 | 100..103, 200..204 |
  | `IpcValue` | enum(pub) | 57 | `Undefined`, `String`, `Buffer`, `VsBuffer`, `Array`, `Object(JSON)`, `Int(i32)` |
  | `write_vql`, `read_vql` | 함수(pub) | 110, 127 | 7비트 가변 길이 정수 |
  | `serialize`, `deserialize`, `encode_message`, `decode_message` | 함수(pub) | 146, 192, 226, 234 | 헤더+본문 인코딩 |
  | `IpcClient::start(conn, ctx)` | 함수(pub) | 274 | context와 `[200]`을 먼저 보내고 디스패치 태스크를 띄운다 |
  | `IpcClient::call` | 함수(pub) | 334 | 서버 `[200]`을 기다린 뒤 Promise 요청 |
  | `IpcClient::listen`, `unlisten`, `cancel` | 함수(pub) | 364, 379, 354 | 이벤트 구독, 해제, 취소 |
  | `dispatch` | 함수(내부) | 393 | 응답, 이벤트, 서버 측 요청 처리 |
- **입력 → 출력:** 채널 이름, 명령, 인자 → `IpcValue`.
- **의존:** `connection.rs`.
- **사용처:** `remote_fs.rs:18`, `management.rs:17`, `ember/editor/src/session.rs:30`, `:210`.
- **부수효과:** tokio 태스크 하나, 소켓 쓰기.
- **주의점:**
  - 서버가 우리 쪽 채널을 부르면 `"Unknown channel"` 에러로 답한다 (`:426-440`).
  - `call`은 요청 id를 밖으로 내주지 않아 `cancel(id)`를 쓸 방법이 없다 (`:334-351`, `:354`). `unlisten`도 저장소에서 쓰지 않는다.
  - 연결이 끝나면 대기 중 요청을 `Canceled` 에러로 끝낸다 (`:313-317`).
  - `IpcSubscription`을 버려도 구독이 풀리지 않는다 (`:264-265`).
- **테스트:** 4개. VQL 벡터, Promise 요청 바이트, Initialize 응답, readdir 중첩 배열.

### `ember/editor-conn/src/remote_fs.rs` (약 310줄)
- **목적:** `'remoteFilesystem'` IPC 채널 클라이언트 (`remote_fs.rs:1-13`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CHANNEL` | 상수(pub) | 22 | `"remoteFilesystem"` |
  | `file_type` | mod(pub) | 25 | `FILE 1`, `DIRECTORY 2`, `SYMBOLIC_LINK 64` 비트 |
  | `Stat` | struct(pub) | 34 | type, mtime, ctime, size, permissions |
  | `WriteOptions` | struct(pub) | 56 | 기본값 create, overwrite true (`:63-67`) |
  | `RemoteFs` | struct(pub) | 123 | IPC 클라이언트와 세션 UUID |
  | `stat`, `read_file`, `write_file`, `readdir`, `mkdir`, `delete`, `rename` | 함수(pub) | 141-197 | 위치 인자 배열로 IPC 호출 |
  | `subscribe_changes` | 함수(pub) | 200 | `fileChange` 이벤트를 `WatchEvent`로 바꿔 넘기는 태스크 |
  | `watch`, `unwatch` | 함수(pub) | 224, 234 | 요청 UUID로 감시 시작, 중지 |
  | `parse_watch_event` | 함수(pub) | 242 | 배열이면 변경, 문자열이면 감시 에러 |
- **입력 → 출력:** `UriComponents` → 파일 내용, 디렉터리 목록, 변경 이벤트.
- **의존:** `ipc.rs`, `uri.rs`.
- **사용처:** `ember/editor/src/session.rs:32`, `:213-214`, `:707`, `:720`.
- **부수효과:** 원격 서버의 파일 읽기, 쓰기, 삭제, 이름 바꾸기.
- **주의점:** URI는 `vscode-remote://` 형식이어야 서버의 URI 변환기가 `file:`로 바꾼다 (`:12-13`). 변경 타입 1, 2 외의 값은 모두 `Updated`로 본다 (`:250-254`). `subscribe_changes`는 `watch`보다 먼저 한 번만 불러야 한다 (`:199`).
- **테스트:** 3개. stat 파싱, fileChange 배열과 에러, writeFile 인자 모양.

### `ember/editor-conn/src/rpc.rs` (약 604줄)
- **목적:** renderer와 확장 호스트 사이 `rpcProtocol.ts` 메시지 인코더, 디코더, 요청과 응답 피어 (`rpc.rs:1-27`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `msg_type`, `arg_type` | mod(내부) | 40, 55 | 메시지 타입 1..12, 인자 타입 1..4 |
  | `Arg` | enum(pub) | 64 | `Json`, `Undefined`, `Buffer`, `JsonWithBuffers` |
  | `Reply` | enum(pub) | 90 | `Empty`, `Json`, `Buffer`, `JsonWithBuffers` |
  | `RpcMessage::encode`, `decode` | 함수(pub) | 144, 238 | 인자가 전부 `Json`이면 JSON 요청, 아니면 mixed 요청 (`:148-154`) |
  | `IncomingRequest` | struct(pub) | 347 | 확장 호스트가 부른 `MainThread*` 요청. `proxy`는 `rpc_ids::name_of`로 푼 이름 |
  | `RpcEvent` | enum(pub) | 358 | `Request`, `Cancel`, `Lost`, `Disconnected` |
  | `RpcPeer::start` | 함수(pub) | 397 | 디스패치 태스크를 띄운다 |
  | `start_call`, `call`, `fire`, `cancel`, `respond` | 함수(pub) | 436, 446, 451, 458, 467 | 이름으로 호출 (`rpc_ids::id_of`), 취소, 응답 |
  | `js_error(name, message)` | 함수(pub) | 480 | `{ $isError: true, ... }` 에러 JSON |
- **입력 → 출력:** 프록시 이름, 메서드, 인자 → `PendingCall`, 들어오는 요청 → `RpcEvent`.
- **의존:** `connection.rs`, `rpc_ids.rs`.
- **사용처:** `exthost.rs:28`, `ember/editor/src/engine.rs:20`, `ember/editor/src/session.rs:33`.
- **부수효과:** tokio 태스크, 소켓 쓰기.
- **주의점:** 들어오는 요청은 처리 전에 바로 `Acknowledged`로 답한다 (`:487-490`). 응답은 받는 쪽(editor)이 반드시 `respond`해야 확장 호스트가 기다리지 않는다. 메서드 이름 255바이트, mixed 인자 255개 상한 (`:125`, `:163`). `fire`는 쓰는 곳이 없다.
- **테스트:** 5개. JSON 요청 바이트, undefined가 mixed로 바꾸는 것, 응답 왕복, ack 5바이트, 진단 요청 디코딩.

### `ember/editor-conn/src/rpc_ids.rs` (약 238줄)
- **목적:** 확장 호스트 RPC 프록시 번호 표. 생성된 파일이다 (위 "버전 고정" 절).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PINNED_COMMIT` | 재수출(pub use) | 18 | 크레이트 핀 |
  | `PROXY_IDS` | 상수(pub) | 21 | `PROXY_IDS[nid - 1]` = 이름. 168개 |
  | `id_of(name)` | 함수(pub) | 193 | 이름 → 번호 |
  | `name_of(id)` | 함수(pub) | 198 | 번호 → 이름 |
- **사용처:** `rpc.rs:437`, `:494`.
- **주의점:** 표를 손으로 고치지 않는다. CI가 스크립트 출력과 비교한다 (`.github/workflows/test.yml:152-155`).
- **테스트:** 2개. 255 이하와 중복 없음, 손 계산 번호 점검.

### `ember/editor-conn/src/exthost.rs` (약 981줄)
- **목적:** 확장 호스트 초기화(Ready → initData → Initialized)와 `extHost.protocol.ts`의 최소 부분집합을 타입으로 옮긴 것 (`exthost.rs:1-18`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MSG_INITIALIZED`, `MSG_READY`, `MSG_TERMINATE` | 상수(pub) | 33-35 | 1바이트 제어 메시지 1, 2, 3 |
  | `proxy` | mod(pub) | 38 | 쓰는 프록시 이름 상수 20개 |
  | `InitDataParams::to_json` | 함수(pub) | 87 | `IExtensionHostInitData` JSON. `appName "Ember"`, `appUriScheme "ember"`, `uiKind 1` 고정 (`:100`, `:105`, `:135`) |
  | `activation_events_map` | 함수(pub) | 148 | commands, languages, views에서 암묵 활성화 이벤트 생성 |
  | `initialize(conn, init)` | 함수(pub) | 204 | Ready를 받으면 init 전송, Initialized까지 60초 대기 → `RpcPeer::start` |
  | `terminate(conn)` | 함수(pub) | 226 | Terminate 바이트 전송 후 `close` |
  | `Range`, `Position`, `Selection` | struct(pub) | 236, 246, 254 | 1부터 시작하는 줄, UTF-16 열 |
  | `WorkspaceData`, `WorkspaceFolder` | struct(pub) | 263, 270 | 워크스페이스 |
  | `MarkerData`, `DocumentFilter` | struct(pub) | 286, 309 | 진단, 문서 선택자 DTO |
  | `Call` | struct(pub) | 328 | 나가는 호출 하나 (proxy, method, args, cancellable). `start(peer)` (`:344`) |
  | `bootstrap_calls` | 함수(pub) | 356 | `$initializeConfiguration`, `$initializeWorkspace` |
  | `configuration_init_data` | 함수(pub) | 369 | 점으로 나뉜 키를 중첩 객체로 |
  | `contributed_configuration_defaults` | 함수(pub) | 414 | 확장의 `contributes.configuration` 기본값과 scope |
  | `activate_by_event` | 함수(pub) | 443 | `$activateByEvent(event, 0)` |
  | `ModelAddedData`, `TextEditorAddData`, `DocumentsAndEditorsDelta` | struct(pub) | 450, 465, 478 | 문서, 편집기 추가 delta |
  | `accept_*`, `provide_*`, `release_*`, `resolve_code_lens`, `handle_inline_completion_*`, `free_inline_completions_list`, `execute_contributed_command` | 함수(pub) | 493-615 | 나가는 `Call` 생성기 |
  | `InlineCompletionContext` | struct(pub) | 557 | 인라인 완성 요청 문맥 |
  | `MainThreadCall` | enum(pub) | 626 | 들어오는 호출 중 editor가 처리하는 것 22종 + `Other` |
  | `MainThreadCall::parse` | 함수(pub) | 674 | `IncomingRequest` → `MainThreadCall`. 위치 인자 번호에 묶여 있다 |
  | `default_reply(proxy, method)` | 함수(pub) | 768 | 구현하지 않은 호출에 줄 기본 응답 |
- **입력 → 출력:** 환경 데이터, 확장 목록 → init JSON. 편집기 상태 → `Call`. 들어오는 요청 → `MainThreadCall`.
- **의존:** `connection.rs`, `management.rs`, `rpc.rs`, `uri.rs`, `document.rs`(타입), `search.rs`.
- **사용처:** `ember/editor/src/session.rs:28`, `:227`, `:241`, `:270`, `:618`, `ember/editor/src/engine.rs:18`, `ember/editor/src/inline.rs:40`, `ember/editor/src/registry.rs:14`, `ember/editor/src/replies.rs:16`, `ember/editor/src/selector.rs:14`, `ember/editor/src/coords.rs:17`, `ember/editor/src/diagnostics.rs:19`, `ember/editor/src/document.rs:21`.
- **부수효과:** `initialize`, `terminate`는 소켓 쓰기. 나머지는 값 생성만.
- **주의점:**
  - `default_reply`는 `$isResourceTrusted`, `$requestWorkspaceTrust`에 항상 `true`(`:772`), `$checkExists`에 항상 `false`(`:771`), `$getCommands`에 빈 배열(`:773`)을 준다. 신뢰 확인을 사실상 건너뛴다.
  - `j()`는 직렬화 실패를 `null`로 삼킨다 (`:349-351`).
  - `RegisterInlineCompletionsSupport`는 upstream 17개 인자 중 앞부분만 해석한다 (`:632-634`, `:695-702`).
  - `proxy::MAIN_THREAD_STORAGE`, `EXT_HOST_EDITORS`, `EXT_HOST_FILE_SYSTEM_INFO`는 크레이트 안에서도 쓰지 않는다.
  - 파일이 981줄이다 (테스트 포함). 
- **테스트:** 8개. changeMany, hover 등록, 검색 등록과 결과, hover 취소 가능성, 활성화 이벤트, 설정 중첩, storage 기본 응답, 출력과 메시지 서비스 해석.

### `ember/editor-conn/src/document.rs` (약 582줄)
- **목적:** 편집기 변경을 `ExtHostDocuments.$acceptModelChanged` 이벤트로 바꾸는 문서 미러. 좌표는 1부터 시작하는 줄과 UTF-16 열이다 (`document.rs:1-17`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `TextEdit`, `EditReason`, `EditorChange` | 타입(pub) | 28, 34, 44 | 편집 한 번의 입력 |
  | `ModelContentChange`, `ModelContentChangedEvent` | struct(pub) | 55, 65 | upstream 직렬화 모양 |
  | `split_lines`, `detect_eol` | 함수(pub) | 83, 104 | Monaco식 줄 나누기, EOL 판정 |
  | `DocumentMirror` | struct(pub) | 113 | 줄 목록, EOL, version, dirty |
  | `with_version` | 함수(pub) | 140 | 재등록 때 버전이 뒤로 가지 않게 시작 버전 지정 |
  | `apply(change)` | 함수(pub) | 259 | 범위 검증 → 끝에서 앞으로 정렬 → 겹침 거부 → 버전 증가 검사 → 적용 |
  | `replace_all`, `set_eol`, `mark_saved` | 함수(pub) | 301, 318, 333 | 전체 교체(`isFlush`), EOL 변경, 저장 |
  | `DocumentBridge` | struct(pub) | 341 | URI 키 → 미러. `open`, `open_in_editor`, `close`, `change`, `saved`, `set_language` |
- **입력 → 출력:** `EditorChange` → `ModelContentChangedEvent` (또는 `Call`).
- **의존:** `exthost.rs`, `uri.rs`.
- **사용처:** `ember/editor/src/document.rs:20` (`DocumentMirror` 등), `ember/editor/src/engine.rs:17`, `ember/editor/src/coords.rs:174`.
- **부수효과:** 없음.
- **주의점:** `rangeOffset`, `rangeLength`는 확장에 그대로 보이므로 정확해야 한다 (`:8-10`). 확장 호스트는 알리지 않은 문서의 변경에 `unknown document`를 던지므로 open delta를 먼저 보내야 한다 (`:16-17`). `DocumentBridge`, `set_eol`, `position_from_byte`는 제품 코드에서 쓰지 않는다 (editor는 `DocumentMirror`를 직접 쓴다).
- **테스트:** 10개. 삽입, 다중 커서 정렬, UTF-16, CRLF, 겹침과 오래된 버전, JSON 모양, bridge 순서, open_in_editor, with_version, replace_all.

### `ember/editor-conn/src/search.rs` (약 407줄)
- **목적:** 확장 호스트의 ripgrep 검색 제공자를 통한 텍스트 검색 (FR-E7, `search.rs:1-14`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `QUERY_TYPE_TEXT` | 상수(pub) | 25 | 2 |
  | `PREVIEW_CHARS_PER_LINE` | 상수(pub) | 29 | 1000 |
  | `DEFAULT_EXCLUDES` | 상수(pub) | 33 | `**/.git` 등 8개 |
  | `TextQuery` | struct(pub) | 46 | 패턴, 옵션, 폴더, include, exclude, 최대 결과 |
  | `TextQuery::to_raw` | 함수(pub) | 85 | `IRawTextQuery` JSON |
  | `split_patterns`, `expand_pattern`, `expand_patterns` | 함수(pub) | 127, 169, 187 | QueryBuilder식 glob 확장 |
  | `provide_text_search_results` | 함수(pub) | 200 | 취소 가능한 `ExtHostSearch.$provideTextSearchResults` 호출 |
  | `SearchRange`, `RangeLocation`, `TextMatch`, `FileMatch` | 타입(pub) | 214-240 | 0부터 시작하는 결과 좌표 |
  | `parse_file_matches` | 함수(pub) | 257 | `$handleTextMatch` 인자 해석. context 줄은 버린다 |
  | `SearchComplete::from_json` | 함수(pub) | 283 | `limitHit`, 메시지 |
  | `is_workspace_scheme` | 함수(pub) | 300 | 쓰는 곳 없음 |
- **사용처:** `exthost.rs:749`, `ember/editor/src/search.rs:15`, `ember/editor/src/engine.rs:1340`, `:1356`, `:1371`.
- **부수효과:** 없음.
- **주의점:** 검색 결과 좌표는 0부터 시작하고, `exthost::Range`는 1부터 시작한다 (`search.rs:211`, `exthost.rs:233`). 섞지 않는다.
- **테스트:** 7개. raw 쿼리 모양, ignore 끔, multiline, 패턴 확장, 취소 가능성, 결과 해석, 완료 통계.

### `ember/editor-conn/src/management.rs` (약 99줄)
- **목적:** 관리 연결에서 확장 호스트 부팅에 필요한 호출 (`management.rs:1-12`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ENV_CHANNEL`, `SCANNER_CHANNEL` | 상수(pub) | 21, 22 | 채널 이름 |
  | `RemoteAgentConnectionContext` | struct(pub) | 28 | IPC 시작 context (`remoteAuthority`, `clientId`) |
  | `RemoteAgentEnvironment` | struct(pub) | 43 | pid, `connection_token`, 경로들, os, arch, grace time. 원본은 `raw` |
  | `get_environment_data` | 함수(pub) | 60 | `getEnvironmentData` |
  | `scan_extensions(ipc, language)` | 함수(pub) | 77 | 확장 설명 JSON 배열. 배열이 아니면 빈 목록 |
  | `when_extensions_ready` | 함수(pub) | 92 | 쓰는 곳 없음 |
  | `extension_id(desc)` | 함수(pub) | 97 | `identifier.value` |
- **사용처:** `ember/editor/src/session.rs:211-212`, `exthost.rs:27`, `examples/probe.rs:69-72`.
- **부수효과:** IPC 호출 (서버가 확장 폴더를 읽는다).
- **주의점:** `RemoteAgentEnvironment.connection_token`은 서버 비밀값을 담는다 (`:45`). `Debug`가 derive돼 있어 로그에 찍히면 노출된다 (`:41`) [추정: 실제로 찍는 곳은 확인하지 않음].
- **테스트:** 없음.

### `ember/editor-conn/src/uri.rs` (약 96줄)
- **목적:** Code-OSS가 마샬링하는 `UriComponents` (`$mid: 1`, `uri.rs:1-11`).
- **주요 심볼:** `SCHEME_REMOTE`(상수, `:16`, `"vscode-remote"`), `UriComponents`(struct, `:19`), `new`(`:38`), `remote(authority, path)`(`:50`), `file(path)`(`:55`), `key()`(`:61`, Ember 안에서만 쓰는 맵 키, 퍼센트 인코딩 없음).
- **사용처:** editor 거의 전 파일, `ember/app/src/editor_host.rs:5`, `ember/app/src/ui/editor_search.rs:12`, `ember/app/src/ui/editor_workbench.rs:75`.
- **주의점:** `$mid`는 역직렬화하지 않고 항상 1이다 (`:20`). `key()`는 RFC 3986 문자열이 아니다 (`:59-60`).
- **테스트:** 2개. `$mid` 직렬화, 서버 모양 역직렬화.

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/editor-conn/Cargo.toml` | 21 | 패키지 정의. 런타임 의존 6개, dev는 tokio full (`:12-21`) |
| `ember/editor-conn/examples/probe.rs` | 79 | 실제 OSE 서버에 버전 게이트, 관리 핸드셰이크, 환경 데이터, 확장 스캔까지 해 보고 `PROBE OK` 또는 `PROBE FAIL at <step>`을 출력한다 (`probe.rs:27`, `:78`). 기본 주소 `127.0.0.1:18765`, 스캔 언어 `"ko"` 고정 (`:43`, `:72`) |
| `ember/editor-conn/scripts/gen_rpc_ids.sh` | 39 | `PROXY_IDS` 표 생성기 (위 "버전 고정" 절) |
| `ember/editor-conn/scripts/fetch-ose-artifact.sh` | 98 | `test-ose.yml` 최근 성공 실행에서 `dpx-ose-<target>` 아티팩트를 `gh`로 내려받아 sha256 확인 후 `.scratch/ose/`에 풀고 `bin/dpx-ose-server` 경로를 출력한다 (`:50-57`, `:64`, `:79-87`, `:98`). `live_ose` 테스트용 |

테스트 파일 (다른 에이전트 담당): `ember/editor-conn/tests/live_ose.rs` (697줄, `#[ignore]`, `EMBER_OSE_SERVER` 필요, `live_ose.rs:361`).

## 이 모듈을 수정할 때 주의할 점

- **Code-OSS 버전을 올릴 때**는 `ember/ose/VERSION`, `PINNED_VERSION`, `PINNED_COMMIT`, `PROXY_IDS`를 한 커밋에서 바꾼다. 하나라도 어긋나면 단위 테스트(`lib.rs:162`)나 CI(`test.yml:120-164`)가 실패하고, 런타임에는 서버가 거절된다. upstream 시그니처가 바뀌었으면 `MainThreadCall::parse`의 인자 위치와 `Call` 생성기의 인자 순서도 다시 맞춘다.
- `lib.rs`의 두 핀 상수 줄 모양은 CI의 `grep -qx`에 묶여 있다 (`test.yml:156-160`).
- 프레이밍, IPC, RPC 바이트 형식은 upstream 줄 번호 주석을 근거로 한다. 단위 테스트가 바이트 벡터를 고정하므로(`ipc.rs:473`, `rpc.rs:524`) 형식을 바꾸면 테스트도 바뀐다. 테스트만 고쳐 통과시키지 말고 upstream을 다시 확인한다.
- `connection.rs`의 태스크는 `generation`으로 세대를 구분한다. 재연결 경로를 손볼 때 이 검사를 빠뜨리면 이전 소켓의 `Lost`가 새 연결에 섞인다.
- 좌표계가 세 가지다: `exthost::Range`(1부터, UTF-16), `search::SearchRange`(0부터, UTF-16), editor 위젯의 바이트 또는 char 오프셋. 변환은 editor의 `coords.rs`가 맡는다.
- `exthost::default_reply`를 바꾸면 확장 활성화가 멈추거나 신뢰 동작이 바뀐다 (`exthost.rs:756-776`).
- 이 크레이트를 바꾸면 의존하는 `ember/editor`, `ember/app`의 `Cargo.lock`이 함께 갱신될 수 있다 (AGENTS.md 규칙: 의존 크레이트를 다시 빌드해 lock을 같은 PR에 커밋).
