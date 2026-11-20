# 이름 사전

- 기준 커밋: `ffe9825` / 작성: 2026-11-13
- 도메인(모듈)별로 묶었다. 찾을 때는 Ctrl+F로 이름을 검색한다.
- 출처: 각 모듈 문서의 "공개 인터페이스" 표(다른 모듈이 쓰는 이름), 코드에서 grep한 환경 변수, 상태 enum. 열은 모듈 문서의 것을 그대로 옮겼다. 사용처 수는 파일 단위 import 그래프 [_raw/fan.tsv](_raw/fan.tsv)의 팬인으로 본다.
- 기능 지도의 핸들러는 이름보다 화면 문구로 찾는 편이 빠르다 ([01_FEATURE_MAP.md](01_FEATURE_MAP.md)). 서버 핸들러는 [_raw/routes.md](_raw/routes.md)에 모두 있다.

## 목차

- [전송 (transport)](#전송-transport)
- [파일 전송 (transfer)](#파일-전송-transfer)
- [IDE 브리지 (bridge)](#ide-브리지-bridge)
- [허브 (hub)](#허브-hub)
- [Code-OSS 연결 (editor-conn)](#code-oss-연결-editor-conn)
- [에디터 세션 (editor)](#에디터-세션-editor)
- [클라이언트 코어 (client)](#클라이언트-코어-client)
- [노드 데몬 (node)](#노드-데몬-node)
- [노드 git (node-git)](#노드-git-node-git)
- [노드 터미널 (node-term)](#노드-터미널-node-term)
- [노드 등록 (node-enrol)](#노드-등록-node-enrol)
- [서버 코어: 세션, 저장소, 인증 (server-core)](#서버-코어-세션-저장소-인증-server-core)
- [에이전트 어댑터 (server-agents)](#에이전트-어댑터-server-agents)
- [컴퓨터, 기기, 허브 연결 (server-computers)](#컴퓨터-기기-허브-연결-server-computers)
- [컴퓨터 등록 코드 (server-enrol)](#컴퓨터-등록-코드-server-enrol)
- [A2A, 채널, 게스트 (server-collab)](#a2a-채널-게스트-server-collab)
- [HTTP API, IDE, 브라우저, MCP (server-api)](#http-api-ide-브라우저-mcp-server-api)
- [계정, ChatGPT, 일정, 전송 (server-accounts)](#계정-chatgpt-일정-전송-server-accounts)
- [앱 코어 (app-core)](#앱-코어-app-core)
- [앱 셸과 기본 화면 (app-ui-cr)](#앱-셸과-기본-화면-app-ui-cr)
- [앱 프로젝트·세션 화면 (app-ui-cr-session)](#앱-프로젝트세션-화면-app-ui-cr-session)
- [앱 파일·루틴·에이전트·버전 관리 화면 (app-ui-cr-work)](#앱-파일루틴에이전트버전-관리-화면-app-ui-cr-work)
- [VS Code Web proxy (proxy)](#vs-code-web-proxy-proxy)
- [확장 (extensions)](#확장-extensions)
- [상태값 (enum)](02_GLOSSARY-2.md#상태값-enum)
- [환경 변수](02_GLOSSARY-2.md#환경-변수)
- [이름 정리 후보](#이름-정리-후보)

## 전송 (transport)

자세히: [modules/transport.md](modules/transport.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Transport` | struct | `ember/transport/src/lib.rs:324` | 바인드된 엔드포인트. 복제 가능, 모든 복제본이 한 백엔드를 공유 |
| `Transport::bind(config)` | async fn | `lib.rs:342` | `config.backend`에 따라 letify 또는 iroh 백엔드 생성 |
| `Transport::connect/listen/local_addr/add_peer_addr` | fn | `lib.rs:368`, `373`, `380`, `385` | 다이얼, 서비스별 수신 등록, 자기 주소, 주소 힌트 |
| `Transport::enable_hub/set_relays/set_directory_token` | fn | `lib.rs:398`, `404`, `391` | 허브 디렉터리 사용 시작, 릴레이 교체, 해석 토큰 교체 |
| `Transport::allow_peer/revoke_peer` | fn | `lib.rs:411`, `418` | 게이트 아래(letify 릴레이·acceptor)에 입장 허용/취소 전달 |
| `Transport::set_power_state/resume_now/wait_online/close` | fn | `lib.rs:424`, `431`, `437`, `442` | 전원 상태, 경로 재수립, 온라인 대기, 종료 |
| `Listener` | struct | `lib.rs:449` | 한 서비스의 수신기. drop 시 서비스 등록 해제 (`lib.rs:471-476`) |
| `Connection` | struct | `lib.rs:487` | 인증된 피어 연결. `open_bi`, `open_bi_bulk`, `accept_bi`, `path_state`, `watch_path`, `close`, `closed` (`lib.rs:516-554`) |
| `BiStream`, `SendHalf`, `RecvHalf` | struct/type | `lib.rs:169`, `163`, `165` | tokio `AsyncRead + AsyncWrite` 양방향 스트림 |
| `TransportError`, `Result` | enum/type | `lib.rs:64`, `83` | 백엔드 오류는 문자열로만 담는다 |
| `PowerState` | enum | `lib.rs:89` | `Foreground`, `Background`, `PowerSave` |
| `PathState` | enum | `lib.rs:100` | `Direct{rtt,remote}`, `Relayed{relay,rtt}`, `Unknown` |
| `CloseReason` | enum | `lib.rs:143` | `Local`, `Remote{code,reason}`, `Lost(String)` |
| `PeerId`, `SecretKey`, `fingerprint_hex` | struct/fn | `key.rs:19`, `key.rs:128`, `key.rs:63` | Ed25519 신원, 키 파일, 사람이 비교하는 지문 |
| `PeerAddr`, `AddressDirectory`, `MemoryDirectory` | struct/trait | `addr.rs:23`, `addr.rs:53`, `addr.rs:61` | 피어 주소와 주소 디렉터리 |
| `TransportConfig`, `RelayConfig`, `HubDirectory`, `BackendKind`, `LetifyConfig`, `ObserverAddr` | struct/enum | `config.rs:270`, `181`, `231`, `16`, `94`, `71` | 바인드 설정 (순수 데이터) |
| `BACKEND_ENV`, `RELAY_URL_ENV` | const | `config.rs:12`, `config.rs:177` | 환경 변수 이름 |
| `Dialer` | struct | `dialer.rs:19` | (피어, 서비스)마다 연결 하나를 캐시 |
| `PeerGate`, `gate::CLOSE_NOT_ALLOWED`, `gate::CLOSE_REVOKED` | struct/const | `gate.rs:31`, `24`, `26` | 허용 목록, 취소 시 즉시 종료 |
| `http::HttpListener`, `http::http1_client`, `http::http1_handshake` | struct/fn | `http.rs:30`, `107`, `119` | axum 서빙, hyper 클라이언트 (feature `http`) |
| `mem::MemNetwork` | struct | `mem.rs:38` | 테스트용 인메모리 네트워크 |
| `SignalChannel`, `PkarrStore`, `MemorySignalHub`, `MemorySignal`, `MemoryPkarrStore`, `verify_pkarr_payload`, `pkarr_signable`, `SIGNAL_MAX` | trait/struct/fn | `signal.rs:30`, `46`, `86`, `104`, `141`, `57`, `72`, `25` | letify 백엔드의 랑데부·pkarr 배관 |
| `HttpPkarrStore`, `direct_addresses_from_txt`, `is_record_label`, `LETIFY_TRANSPORT_ID` | struct/fn/const | `letify/pkarr.rs:174`, `295`, `306`, `letify/mod.rs:68` | feature `letify` |

## 파일 전송 (transfer)

자세히: [modules/transfer.md](modules/transfer.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `SERVICE` | const | `ember/transfer/src/lib.rs:27` | 서비스 식별자 `"ember-transfer/1"` |
| `PeerId` | re-export | `ember/transfer/src/lib.rs:29` | `ember_transport::PeerId` |
| `Limits`, `DEFAULT_MAX_BYTES`, `LimitError` | struct/const/enum | `ember/transfer/src/limits.rs:17`, `:4`, `:8` | 제안 합계 크기 제한 (기본 4 GiB) |
| `ReceiveMode`, `Decision`, `decide` | enum/enum/fn | `ember/transfer/src/mode.rs:12`, `:23`, `:29` | 수신 모드(Ask, AutoAcceptFrom, Off)와 그 결정 |
| `clean_file_name`, `clean_relative_path`, `clean_offer_paths`, `resolve_destination`, `generated_name`, `split_stem_ext` | fn | `ember/transfer/src/names.rs:133`, `:144`, `:171`, `:222`, `:75`, `:90` | 네트워크에서 온 이름 정리, 덮어쓰기 없는 목적지 결정 |
| `MAX_NAME_BYTES`(200), `MAX_PATH_DEPTH`(32), `MAX_PATH_BYTES`(1024), `MAX_OFFER_FILES`(1024) | const | `ember/transfer/src/names.rs:21-27` | 이름, 경로, 파일 수 상한 |
| `Clock`, `SystemClock`, `ManualClock`, `State`, `Event`, `TransitionError`, `next`, `Transfer` | trait/struct/enum/fn | `ember/transfer/src/state.rs:10`, `:15`, `:39`, `:59`, `:80`, `:95`, `:105`, `:129` | 전송 상태 기계. 시계를 주입한다 |
| `Message`, `FileEntry`, `DeclineCode`, `WireError`, `encode`, `decode`, `read_message`, `write_message`, `WIRE_VERSION`, `MAX_FRAME` | enum/struct/fn/const | `ember/transfer/src/wire.rs:42`, `:16`, `:25`, `:99`, `:113`, `:137`, `:158`, `:183`, `:11`, `:13` | 4바이트 길이 + JSON 프레임 |
| `Service`, `Handled`, `Outgoing`, `Reply`, `PeerPolicy`, `Prompter`, `IncomingOffer`, `PromptAnswer`, `Halves`, `Error`, `DEFAULT_OFFER_TTL` | struct/trait/enum | `ember/transfer/src/session.rs:230`, `:94`, `:444`, `:436`, `:56`, `:83`, `:68`, `:76`, `:88`, `:37`, `:34` | 스트림 한 개 위의 핸드셰이크와 청크 송수신 |
| `ReceiveWriter`, `StoreError`, `DeclaredFile`, `StoredFile`, `HistoryRecord`, `TransferDirection`, `TransferResult`, `sha256_file`, `DEFAULT_CHUNK_BYTES` | struct/enum/fn/const | `ember/transfer/src/store.rs:111`, `:34`, `:53`, `:64`, `:92`, `:76`, `:83`, `:337`, `:31` | 수신 파일 저장, 재개, 검증, 이력 |

## IDE 브리지 (bridge)

자세히: [modules/bridge.md](modules/bridge.md)

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

## 허브 (hub)

자세히: [modules/hub.md](modules/hub.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `HubConfig`, `RelaySource`, `DEFAULT_HUB_URL`, `HUB_URL_ENV`, `HUB_RELAY_URL_ENV` | struct/enum/const | `ember/hub/src/config.rs:28`, `:17`, `:13`, `:10`, `:12` | 어느 허브를 쓰는지, 릴레이, 주소 디렉터리, 전송 설정으로의 변환 |
| `HubClient`, `HubError`, `DevicesPoll`, `CODE_DEVICE_REMOVED`, `CODE_INVALID_CREDENTIALS`, `MAX_WAIT` | struct/enum/const | `ember/hub/src/client.rs:89`, `:33`, `:113`, `:20`, `:22`, `:29` | 허브 REST 호출 |
| `DeviceLink`, `LinkPoll`, `LinkError`, `link_message` | struct/enum/fn | `ember/hub/src/link.rs:63`, `:56`, `:35`, `:29` | 장치 연결 흐름 (RFC 8628 형태 + 키 소유 증명) |
| `Registration`, `RegistrationFile`, `RegistrationState`, `REGISTRATION_FILE`, `now_secs` | struct/enum/const/fn | `ember/hub/src/registration.rs:27`, `:89`, `:170`, `:18`, `:21` | 등록 결과와 저장 |
| `check_registration`, `ensure_resolve_token`, `watch_registration`, `watch_registration_with` | fn | `ember/hub/src/registration.rs:215`, `:206`, `:247`, `:272` | 등록 상태 확인과 감시 |
| `DeviceWatcher`, `DEFAULT_WAIT` | struct/const | `ember/hub/src/watch.rs:35`, `:13` | 장치 목록 추적(롱폴 또는 조건부 폴링) |
| `Role`, `Device`, `LinkRequest`, `PendingLink`, `ClaimOutcome`, `LinkCodeInfo`, `Me`, `AddressRecord`, `HubInfo`, `DeviceApp`, `LinkStatus`, `LinkInfo`, `Readmission`, `service_label` | 타입 | `ember/hub/src/types.rs:11`, `:41`, `:61`, `:69`, `:85`, `:110`, `:120`, `:132`, `:158`, `:185`, `:234`, `:245`, `:277`, `:218` | 허브 API 와이어 타입 |
| `paths` | 모듈 | `ember/hub/src/paths.rs` | 호출 경로 상수와 `TEMPLATES` |
| `z32` | 모듈 | `ember/hub/src/z32.rs` | z-base-32 (`encode`, `decode_key`) |
| `fake::FakeHub` | struct (feature `fake`) | `ember/hub/src/fake.rs:209` | 프로세스 안 가짜 허브 |

## Code-OSS 연결 (editor-conn)

자세히: [modules/editor-conn.md](modules/editor-conn.md)

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

## 에디터 세션 (editor)

자세히: [modules/editor.md](modules/editor.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `EditorSession` | struct | `session.rs:117` | 한 서버, 한 작업 폴더, 한 창. `connect`, `open`, `close`, `widget_event`, 탐색기 파일 조작, `search` 등 모두 비차단 송신 |
| `SessionConfig` | struct | `session.rs:51`, `new` `:72` | `host`, `remote_authority`, `connection_token`, `workspace_path`, `user_settings`, `core`, `vscode_url` |
| `DirLister` | struct | `session.rs:104` | 복제 가능한 디렉터리 목록 조회 핸들 (`read_dir` `:111`) |
| `SessionCore`, `Input`, `Effect`, `SessionUpdate`, `CoreOptions`, `ExternalChange` | 타입 | `engine.rs:231`, `:86`, `:117`, `:144`, `:45`, `:135` | 순수 상태 기계와 그 입출력 |
| `WidgetBridge`, `BridgeAction`, `DocumentWidgetState`, `SyntaxRuns`, `apply_text_change` | 타입, 함수 | `bridge.rs:116`, `:50`, `:18`, `:43`, `:82` | `SessionUpdate`를 위젯 props로 바꾸고 위젯 콜백을 `(uri, generation, WidgetEvent)`로 되돌린다 |
| `WidgetEvent`, `WidgetCommand`, `Decoration`, `DecorationId`, `DecorationKind`, `Severity`, `HoverPhase`, `DECORATION_RECORD_LEN` | 타입 | `widget.rs:246`, `:270`, `:108`, `:98`, `:72`, `:36`, `:239`, `:31` | FR-38 계약. 레코드 1개는 44바이트 |
| `WidgetPos`, `WidgetRange` | struct | `coords.rs:21`, `:44` | 0 기반, UTF-16 |
| `Fallback`, `ConnectOutcome`, `FallbackTarget`, `fallback_for`, `vscode_fallback_url` | 타입, 함수 | `fallback.rs:20`, `:90`, `:72`, `:110`, `:61` | 서버 버전이 맞지 않을 때 "VS Code로 열기"를 제안 |
| `ContributedCommand`, `parse_contributed_commands` | 타입, 함수 | `commands.rs:7`, `:43` | 확장 `contributes.commands` |
| `OutputChannel`, `ExtensionMessage`, `MessageSeverity`, `MAX_OUTPUT_CHANNEL_BYTES` | 타입, 상수 | `output.rs:14`, `:76`, `:50`, `:10` | 출력 채널 (채널당 64 KiB) |
| `Error` | enum | `lib.rs:70` | `Conn`, `Io`, `Json`, `Refused`, `Closed`, `Path` |
| `textmate::*` | 모듈 | `textmate/mod.rs:10-23` | `Grammar`, `GrammarSet`, `DocumentTokens`, `SyntaxRole`, `GrammarCatalog`, `parse_grammar` 등 |
| `search::*` | 모듈 | `search.rs` | `SearchRequest`, `ReplaceRequest`, `Matcher`, `FileHits`, `relative_to` 등. 앱이 직접 가져다 쓴다 (`ember/app/src/ui/editor_search.rs:10`) |

## 클라이언트 코어 (client)

자세히: [modules/client.md](modules/client.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Client` | struct | `ember/client/src/client.rs:96` | 동기화 엔진 핸들. `Arc<Inner>` 공유, clone 저렴 |
| `ClientConfig` | struct | `ember/client/src/client.rs:35` | base URL, 캐시 경로, lease 주기(30s), backoff(250ms..30s), resync 지연(250ms), 캐시 debounce(500ms) (`client.rs:53-63`) |
| `Api` | struct | `ember/client/src/api.rs:685` | 메인 서버 `/api` HTTP 클라이언트. HTTP 또는 P2P 전송 두 경로 |
| `ApiError`, `ApiResult` | enum, type | `ember/client/src/api.rs:37`, `api.rs:179` | 에러 분류. `code()`, `status()` (`api.rs:157`, `api.rs:165`) |
| `QuestionReply`, `QuestionCallError`, `question_error_ko` | enum, fn | `ember/client/src/api.rs:64`, `api.rs:93`, `api.rs:143` | 질문 답변 본문과 고정 한국어 에러 문구 |
| `ProjectPatchError`, `HubCallError`, `EnrolCallError` | enum | `ember/client/src/api.rs:1994`, `api.rs:2271`, `api.rs:2464` | 호출별 타입화된 에러 |
| `State`, `Input`, `Changes`, `LauncherStatus`, `ConnectionState` | struct/enum | `ember/client/src/state.rs:169`, `state.rs:66`, `state.rs:96`, `state.rs:18`, `state.rs:55` | 순수 리듀서와 입력, 변경 알림 (`lib.rs:27`에서 재수출) |
| `Computer`, `Reachability`, `ProjectView`, `SessionView`, `CacheSnapshot`, `CACHE_FORMAT` | struct/enum/const | `ember/client/src/state.rs:44`, `state.rs:33`, `state.rs:138`, `state.rs:145`, `state.rs:153`, `state.rs:166` | 런처 화면용 읽기 뷰와 캐시 구조 |
| `Transcript`, `TranscriptItem`, `ApprovalState`, `QuestionState`, `Applied` | struct/enum | `ember/client/src/transcript.rs:83`, `transcript.rs:17`, `transcript.rs:43`, `transcript.rs:54`, `transcript.rs:73` | 한 세션 대화의 리듀서 |
| `wire::*` | struct/enum | `ember/client/src/wire.rs` | 서버 JSON 타입 (`SessionRecord`, `AgentEvent`, `Push`, `Project`, `TeamView`, `Schedule` 등). 팬인 28 |
| `channels::*` | struct/fn | `ember/client/src/channels.rs` | 채널 API 타입과 경로 함수 |
| `push::decode`, `push::Backoff`, `push::SKIPPED_TYPES` | fn/struct/const | `ember/client/src/push.rs:74`, `push.rs:118`, `push.rs:70` | push 프레임 해석과 재연결 backoff |
| `token::{server_token, server_token_from_env, token_allowed_for, token_allowed_for_hosts, auth_headers, bearer_header}` | fn | `ember/client/src/token.rs:15`, `token.rs:177`, `token.rs:132`, `token.rs:138`, `token.rs:168`, `token.rs:186` | 서버 토큰 탐색과 전송 허용 판정. app의 `ServerApi`, `terminal_stream`도 쓴다 (`ember/app/src/server.rs:362-375`, `ember/app/src/terminal_stream.rs:776-815`) |
| `cache::{load, save}` | fn | `ember/client/src/cache.rs:21`, `cache.rs:36` | 스냅샷 파일 읽기/원자적 쓰기 |

## 노드 데몬 (node)

자세히: [modules/node.md](modules/node.md)

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

## 노드 git (node-git)

자세히: [modules/node-git.md](modules/node-git.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `GitError` | enum | `ember/node/src/git.rs:156` | 8가지 에러. `api.rs:321-328`이 HTTP로 변환 |
| `GitRepoRequest` 외 요청/응답 DTO | struct | `ember/node/src/git.rs:43-150` | `api.rs` 핸들러의 `Json<..>` 타입 |
| `status`, `diff`, `stage`, `unstage`, `apply`, `commit`, `checkout`, `branch`, `fetch`, `pull_fetch`, `pull_merge`, `push`, `conflicts` | async fn | `ember/node/src/git.rs:497-841` | `api.rs` 핸들러가 호출 |
| `network_timeout`, `max_output`, `NETWORK_TIMEOUT_SECS`, `MAX_OUTPUT_BYTES` | fn/const | `ember/node/src/git.rs:179-203` | `git_conflict.rs:57-59`와 테스트가 사용 |
| `korean_message` | fn | `ember/node/src/git.rs:393` | 테스트(`ember/node/tests/git_api.rs`)만 사용 |
| `worktree_root` | `pub(crate)` fn | `ember/node/src/git.rs:475` | `git_conflict.rs:27`, `:108` |
| `git_log::log`, `git_branches::list`, `git_commit::{show, revert, cherry_pick}`, `git_merge::{state, abort, commit}`, `git_stash::{list, push, change}`, `git_prs::{list, detail, review, merge, create}`, `git_github::summarize`, `git_conflict::{conflict, resolve}` | async fn | 각 파일 | `api.rs` 핸들러 |
| `git_prs::{check_class, parse_prs, parse_detail, merge_gate}` | fn | `ember/node/src/git_prs.rs:160`, `:235`, `:503`, `:176` | 통합 테스트(`ember/node/tests/git_prs.rs`)가 사용 |

## 노드 터미널 (node-term)

자세히: [modules/node-term.md](modules/node-term.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Terms` | struct | `ember/node/src/term/mod.rs:66` | 세션 테이블. `new`(93), `create`(197), `get`(251), `list`(256), `kill`(270), `remove`(281), `shutdown`(298) |
| `Session` | struct | `ember/node/src/term/session.rs:121` | 세션 하나. `attach`(359), `input`(409), `resize`(441), `control`(454), `detach`(480), `kill`(491), `snapshot`(263) |
| `TermRecord` | struct | `ember/node/src/term/session.rs:43` | 디스크에 저장되는 세션 메타데이터 |
| `Screen` | struct | `ember/node/src/term/screen.rs:90` | 터미널 상태 모델 (`feed`, `snapshot`, `resize`, `compact`) |
| `Pty`, `spawn`, `spawn_keeper`, `keeper_main` | struct/fn | `ember/node/src/term/pty.rs:43`/`:88`, `:131`, `:229`, `:316` | PTY 생성과 keeper 프로세스 |
| `Store` | struct | `ember/node/src/term/store.rs:10` | `<state>/terms/` 디스크 저장 |
| `default_argv` | fn | `ember/node/src/term/mod.rs:74` | 기본 프로그램: 사용자 셸 (macOS는 `-l`, Windows는 `COMSPEC`) |
| `ember-term` | bin | `ember/node/src/bin/ember-term.rs:248` | 로컬 터미널을 노드 세션에 attach하는 CLI |

## 노드 등록 (node-enrol)

자세히: [modules/node-enrol.md](modules/node-enrol.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `ENROL_FILE` | const | `ember/node/src/enrol.rs:24` | `enrol.json` |
| `Enrolment` | struct | `ember/node/src/enrol.rs:207` | `server`, `node_token`(비밀, `Debug`는 `[redacted]`), `server_peer_id`, `name`, `computer_id`, `enrolled_ms` |
| `read_enrolment` | fn | `ember/node/src/enrol.rs:257` | 파일 읽기와 검증. 없으면 `Ok(None)` |
| `lock_state_dir`, `EnrolLock` | fn/struct | `ember/node/src/enrol.rs:133`, `:111` | 상태 디렉터리의 `flock`(`.enrol.lock`) |
| `preflight` | fn | `ember/node/src/enrol.rs:580` | 코드를 쓰기 전에 나중 쓰기가 실패할 조건을 미리 검사 |
| `write_enrolment` | fn | `ember/node/src/enrol.rs:501` | `enrol.json`과 `allowed-peers`를 함께 (둘 다 바뀌거나 둘 다 안 바뀌게) 쓴다 |
| `append_allowed_peer` | fn | `ember/node/src/enrol.rs:283` | `allowed-peers` 새 텍스트 계산 (기존 바이트 유지) |
| `WriteError`, `WriteReport` | enum/struct | `ember/node/src/enrol.rs:305`, `:336` | 쓰기 실패 종류와 결과 |
| `cli` | fn | `ember/node/src/enrol_cli.rs:692` | `ember-node enrol` 진입 |
| `run`, `Options`, `EnrolIo` | fn/struct/trait | `ember/node/src/enrol_cli.rs:753`, `:103`, `:532` | 전체 흐름, 옵션, 입출력 추상화 (테스트에서 `Script`로 대체) |
| `parse_args` | fn | `ember/node/src/enrol_cli.rs:172` | 인자 해석. 코드가 `-`이면 stdin 한 줄 |
| `USAGE`, `PLAIN_HTTP_WARNING`, `LOOPBACK_HTTP_NOTE`, `REFUSED_TEXT` | const | `ember/node/src/enrol_cli.rs:59`, `:75`, `:78`, `:91` | 사용자에게 보이는 문구 |

## 서버 코어: 세션, 저장소, 인증 (server-core)

자세히: [modules/server-core.md](modules/server-core.md)

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

## 에이전트 어댑터 (server-agents)

자세히: [modules/server-agents.md](modules/server-agents.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `AgentAdapter` | trait | `ember/server/src/agents/mod.rs:320` | 에이전트 종류 하나. `start`가 프로세스를 띄우고 `Box<dyn AgentRun>`을 돌려준다 |
| `AgentRun` | trait | `ember/server/src/agents/mod.rs:372` | 실행 중인 에이전트. `send`, `answer`, `answer_question`, `decline_question`, `interrupt`, `shutdown`, `restore_pending_*` |
| `AgentKind` | enum | `ember/server/src/agents/mod.rs:33` | `ClaudeCode`, `Codex`, `Antigravity`, `Scripted`, `Acp(AcpName)`. 문자열(`"claude-code"` 등)로 직렬화 (`mod.rs:144-155`) |
| `AcpName` | struct | `ember/server/src/agents/mod.rs:50` | 설정으로 정해지는 ACP 이름. 프로세스 전역 레지스트리에 `Box::leak`으로 들여온다 (`mod.rs:87`) |
| `StartRequest`, `ForkFrom`, `NativeFork`, `McpServer`, `RemoteExec` | struct/enum | `mod.rs:159`, `:202`, `:212`, `:223`, `:251` | 시작 요청과 부속 타입 |
| `Detected`, `Probe`, `resolve_executable` | struct/함수 | `mod.rs:261`, `:269`, `:289` | CLI 설치 탐지 (FR-A6) |
| `proc::spawn_agent`, `reattach_agent`, `AgentCommand`, `AgentProc`, `ProcHandle` | 함수/struct/enum | `agents/proc.rs:275`, `:262`, `:198`, `:224`, `:235` | 에이전트를 띄우는 유일한 곳 (직접 자식 또는 shim) |
| `proc::{ShimRuntime, install_runtime, clear_runtime, shim_enabled, require_commit, release_commit, release_commit_of, CommitGate, live_shim_sessions, drain_surviving_lines, shim_died, find_shim_bin, mem_limit_bytes, SESSION_ENV}` | 혼합 | `proc.rs:46`, `:56`, `:60`, `:65`, `:145`, `:152`, `:160`, `:74`, `:577`, `:596`, `:180`, `:189`, `:217`, `:39` | shim 런타임 |
| `ClaudeCodeAdapter` (+`mcp_config`, `cleanup_stale_mcp_files`) | struct/함수 | `agents/claude_code.rs:84`, `:282`, `:227` | Claude Code |
| `CodexAdapter` (+`PROXY_BASE_ENV`, `PROXY_KEY_ENV`, `proxy_config_args`) | struct/상수/함수 | `agents/codex.rs:82`, `:304`, `:306`, `:310` | Codex |
| `AntigravityAdapter`, `HookBroker`, `router`, `HOOK_ROUTE` 등 | struct/함수 | `agents/antigravity.rs:211`, `:600`, `:641`, `:139` | Antigravity와 훅 수신 라우트 |
| `AcpAdapter`, `AcpConfig`, `configs_from_env`, `parse_configs`, `GEMINI_ENV_ALLOW` | struct/함수 | `agents/acp.rs:397`, `:210`, `:380`, `:320`, `:190` | ACP |
| `ScriptedAdapter`, `ScriptedForkAdapter` | struct | `agents/scripted.rs:16`, `:46` | 테스트용 가짜 에이전트 |
| `history::import_file`, `to_events`, `Transcript`, `Message`, `Role` | 함수/struct | `history/mod.rs:106`, `:185`, `:22`, `:42`, `:33` | 에이전트 자체 기록 파일을 이벤트로 |

## 컴퓨터, 기기, 허브 연결 (server-computers)

자세히: [modules/server-computers.md](modules/server-computers.md)

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

## 컴퓨터 등록 코드 (server-enrol)

자세히: [modules/server-enrol.md](modules/server-enrol.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Enrol` | struct | `ember/server/src/computers/enrol.rs:826` | 코어 서비스. `mint/redeem/confirm/deny/cancel/status/status_detail/verify_poll/take_delivery/sweep` |
| `computers::enrol::router` | fn | `enrol.rs:1407` | owner 라우터 5개 라우트. 로컬 토큰 보호 라우터에만 merge |
| `Registrar` | trait | `enrol.rs:595` | `name_taken`, `register`, `remove`, `registers_by` |
| `ComputersRegistrar` | struct | `enrol.rs:656` | 레지스트리 구현, `with_server_peer_id` |
| `DoorUrl` | enum | `enrol.rs:1386` | `Off`, `Unknown`, `Url` (mint이 인쇄할 주소) |
| `MIGRATION`, `CONFIRM_MIGRATION` | const | `enrol.rs:89`, `:108` | `enrol_codes` 테이블 (`store::MIGRATIONS` 25, 26번) |
| `NodeInfo` | struct | `enrol.rs:285` | 노드가 보고하는 공개 정보. `validated`, `fingerprint`, `minimal` |
| `Delivery`, `Refused`, `EnrolError`, `State`, `EnrolStatus` | enum | `enrol.rs:523`, `:389`, `:545`, `:415`, `:469` | 결과와 오류 유형 |
| `EnrolDoor` | struct | `ember/server/src/enrol_door.rs:107` | door 설정, `from_env`, `app`, `door_url`, `bind`, `serve` |
| `PollLimiter` | struct | `enrol_door.rs:301` | id당 poll 한도 |
| `door::{config, harden, limits, serve}` | mod | `ember/server/src/door/mod.rs:10-13` | 두 door 공용 부품 |
| `DoorError` | struct | `door/mod.rs:21` | 시작 오류 |

## A2A, 채널, 게스트 (server-collab)

자세히: [modules/server-collab.md](modules/server-collab.md)

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

## HTTP API, IDE, 브라우저, MCP (server-api)

자세히: [modules/server-api.md](modules/server-api.md)

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

## 계정, ChatGPT, 일정, 전송 (server-accounts)

자세히: [modules/server-accounts.md](modules/server-accounts.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Accounts` | struct | `ember/server/src/accounts/mod.rs:138` | `open`, `create`, `list`, `delete`, `set_default`, `route`, `on_event`, `check_login`, `usage_since`, `install` |
| `accounts::api::router` | fn | `accounts/api.rs:34` | `/api/accounts*`, `/api/usage`, `/api/providers*` |
| `SecretBox`, `create_provider`, `provider_key` | struct/fn | `accounts/secrets.rs:42`, `:193`, `:244` | 암호화 저장소와 API 키 CRUD |
| `chatgpt::ChatGpt` | struct | `chatgpt/mod.rs:243` | `start_signin`, `complete_signin`, `access_token`, `refresh`, `responses`, `models`, `sign_out` |
| `chatgpt::api::router` | fn | `chatgpt/api.rs:32` | `/api/chatgpt*`, `/auth/callback` |
| `ChatGptConfig::from_env`, `hosted_from_env` | fn | `chatgpt/mod.rs:110`, `:124` | `EMBER_HOSTED`, 콜백 포트 |
| `chatgpt::demo::seed` | fn | `chatgpt/demo.rs:39` | 데모 계정 시드 |
| `Scheduler`, `Clock`, `SystemClock`, `ManualClock` | struct/trait | `schedules/mod.rs:329`, `:51`, `:56`, `:66` | 스케줄 엔진과 주입 시계 |
| `schedules::api::router`, `agent_router` | fn | `schedules/api.rs:50`, `:62` | 사용자 라우트, 에이전트 라우트 |
| `TransferManager`, `transfers::router` | struct/fn | `ember/server/src/transfers.rs:154`, `:715` | 서버 측 전송 |
| `usage` 질의 | `impl Store` | `ember/server/src/usage.rs:103`, `:118`, `:143` | `day_start_ms`, `session_usage`, `usage_summary` |

## 앱 코어 (app-core)

자세히: [modules/app-core.md](modules/app-core.md)

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

## 앱 셸과 기본 화면 (app-ui-cr)

자세히: [modules/app-ui-cr.md](modules/app-ui-cr.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `shell::launch(pref)` | fn | `ember/app/src/ui/cr/shell.rs:779` | 기본 실행. 테마 설정 후 `LaunchBuilder`로 창("Ember", 기본 1440x900) 열기 |
| `shell::shell()` | composable | `shell.rs:599` | 루트 레이아웃. 메뉴->화면 분기(아래 1절)와 시트 호스팅 |
| `shell::choose(ui, menu)` | fn | `shell.rs:69` | 메뉴 이동. 프로젝트=`Route::Projects`, 세션=가장 최근 대화 열기 |
| `shell::Sidebar/RailItem/NavRow/BottomBar/PhoneMenu/Placeholder` | composable | `shell.rs:330/196/161/412/481/575` | 내비게이션 조각 |
| `shell::requested()`, `window_chrome()` | fn | `shell.rs:748`, `:769` | `EMBER_CR_SHELL` 읽기, macOS 풀사이즈 크롬 |
| `home::HomeScreen` | composable | `home.rs:504` | 홈 화면 (작성기 + 대시보드) |
| `channels::ChannelsScreen`, `ChannelsScreenWith`, `Avatar`, `sample_rooms`, `preview` | composable/fn | `channels.rs:209/227/60/713/783` | 채널 화면 |
| `search::SearchScreen` | composable | `search.rs:64` | 검색 화면 |
| `new_session::NewSessionDialog`, `can_start`, `build_request` | composable/fn | `new_session.rs:41/50/55` | 새 세션 다이얼로그 |
| `settings::SettingsSheet`, `SettingsContent`, `shortcut_rows`, `ide_choice_label`, `IDE_CHOICES` | 혼합 | `settings.rs:69/82/31/51/61` | 설정 시트 |
| `add_computer::AddComputerSheet`, `AddUi` | composable/struct | `add_computer.rs:378/42` | 컴퓨터 추가 시트 (`project.rs:1216`에서 호출) |
| `monitor::MonitorSheet`, `mon_columns`, `card_height`, `sort_mark` | 혼합 | `monitor.rs:89/58/254/47` | 컴퓨터 모니터 시트 (`project.rs:1220`) |
| `channel_owner::MembersSheet`, `OwnerState`, `hour_chip_rows` | 혼합 | `channel_owner.rs:335/41/408` | 채널 멤버/게스트 시트 |
| `new_channel::NewChannelButton/NewChannelSheet/NewChannelState` | 혼합 | `new_channel.rs:130/205/27` | 새 채널 시트 |
| `characters_screen::CharactersScreen` | composable | `characters_screen.rs:140` | 팀 캐릭터 화면 (메뉴 아님, `ui.characters`가 `Some`일 때) |
| `characters::Character`, `StylePicker`, `draw` | composable | `characters.rs:41/79/68` | 그려진 팀 캐릭터 |
| `launcher::ConnectionBanner`, `SessionRowView/With`, `patch_session`, `rename`, `export` | 혼합 | `launcher.rs:31/91/96/229/238/246` | 세션 행과 서버 호출 |
| `notice::post`, `NoticeHost` | fn/composable | `notice.rs:19/25` | 어느 스레드에서든 토스트 |
| `components::*`, `compat::*`, `theme::*`, `ko::*`, `a11y::*`, `gallery::*` | 모음 | 3-4절 | 토큰, 컴포넌트, 문구 표 |

## 앱 프로젝트·세션 화면 (app-ui-cr-session)

자세히: [modules/app-ui-cr-session.md](modules/app-ui-cr-session.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `ProjectScreen` | composable | `project.rs:238` | 프로젝트 메뉴 화면. 그리드, 상세, 시트를 모두 그린다 |
| `Header`, `HeaderGap`, `ThemeButton`, `PHONE_MENU_ROOM` | fn/const | `project.rs:273`, `280`, `316`, `312` | 다른 화면이 쓰는 페이지 머리 |
| `toggle_search`, `search_field_visible`, `search_icon_visible`, `grid_cols`, `team_cols`, `full_two_columns`, `team_segments`, `grouped`, `box_matches`, `wrap_lines`, `stat_width`, `chip_sub`, `sheet_scroll_dp` | 순수 fn | `project.rs:332-346`, `50-146`, `1248` | 레이아웃과 필터 결정 (단위 테스트 대상) |
| `ConversationView(id, embedded)` | composable | `conversation.rs:155` | 한 세션의 대화. 입력, 큐, 멘션, 팝업 포함 |
| `TranscriptRow`, `QuestionCard`, `TeamPanel` | composable | `conversation.rs:1486`, `1279`, `1933` | 항목 한 줄, 질문 카드, 팀 패널 |
| `fork_from(ui, id, seq)` | fn | `conversation.rs:130` | 포크 후 새 세션 열기 |
| `item_key`, `estimate_item_height`, `tail_start_index`, `empty_transcript_text` | fn | `conversation.rs:36`, `67`, `92`, `2122` | LazyColumn 키와 높이 추정 |
| `SessionScreen(focus)` | composable | `session.rs:4353` | 세션 메뉴 화면 전체 |
| `MultiView`, `SingleView`, `StatusView`, `SideList`, `SideListRail`, `Pane`, `InfoPanel` | composable | `session.rs:1602`, `2371`, `3622`, `703`, `935`, `1392`, `2035` | 3개 뷰와 부품 |
| `ModelChip`, `ModeChip`, `ComposerChips`, `StopCircleButton`, `SendCircleButton` | composable | `session.rs:259`, `337`, `442`, `216`, `237` | 입력창 칩과 원형 버튼. `conversation.rs`와 `home.rs:1242`가 쓴다 |
| `IdeMenu`, `IdeChevron`, `ide_main_click`, `ide_click`, `launch_ide_shared` | fn | `session.rs:524`, `501`, `470`, `462`, `171` | IDE 열기 분할 버튼과 실행 |
| `PaneTranscript`, `PaneComposer`, `PaneTerminal` | composable | `session.rs:1033`, `1223`, `1105` | 멀티 뷰 칸 내용 |

## 앱 파일·루틴·에이전트·버전 관리 화면 (app-ui-cr-work)

자세히: [modules/app-ui-cr-work.md](modules/app-ui-cr-work.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `FilesScreen` / `FilesScreenWith` | fn | `ember/app/src/ui/cr/files.rs:379,393` | 파일 화면. 전송 서비스가 없어 장비 목록만 실제 값이다 |
| `RoutinesScreen` / `RoutinesScreenWith` | fn | `ember/app/src/ui/cr/routines.rs:419,489` | 루틴 화면 |
| `load_remote`, `apply_load`, `is_remote`, `with_store`, `with_remote` | fn | `ember/app/src/ui/cr/routines.rs:203,217,198,70,188` | 서버 스케줄 읽기와 기기 보관소 |
| `AgentsScreen` / `AgentsScreenWith` | fn | `ember/app/src/ui/cr/agents.rs:249,306` | 에이전트 화면 (섹션 5개) |
| `sync_from_server` | fn | `ember/app/src/ui/cr/agents.rs:76` | 서버 기본값과 설정을 로컬 저장소에 반영. 호출처 `ember/app/src/bridge.rs:528` |
| `VcsScreen` / `VcsScreenWith` / `VcsSheet` | fn | `ember/app/src/ui/cr/vcs.rs:4197,4236,4436` | 버전 관리 화면과, 대화 화면에 뜨는 시트 |
| `open_for_project_cr` | fn | `ember/app/src/ui/cr/vcs.rs:48` | 프로젝트를 고르고 버전 관리 메뉴로 이동 |
| `sample_*`, `preview` | fn | 각 파일 | 검토 캡처용 표본 (`EMBER_CR_ROUTE`, `EMBER_CR_*_SAMPLE`) |

## VS Code Web proxy (proxy)

자세히: [modules/proxy.md](modules/proxy.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `python -m dpx.serve` | CLI | `ember/proxy/dpx/serve.py:197` | 런타임 서버 + 프록시를 띄우고 stdout에 `{"event":"ready","url":...}` 한 줄을 낸다. ember server의 `ide_url` 출처 (`ember/server/src/api/ide.rs:66`) |
| `uvicorn main:app` | ASGI 앱 | `ember/proxy/main.py:53` | 프록시 본체 |
| `uvicorn dpx.hub.server:app` | ASGI 앱 | `ember/proxy/dpx/hub/server.py:135` | 다중 머신 허브 |
| `python -m dpx.hub.connector` | CLI | `ember/proxy/dpx/hub/connector.py:185` | 허브로 나가는 커넥터 |
| `tab_detach` 메시지 | webview → 네이티브 | `ember/proxy/static/detach.js:248` | `buildDetachMessage`. 형식은 `ember/bridge/src/messages.rs`와 맞춘다 |
| `window.__emberBridge.receive(json)` | 네이티브 → webview | `ember/proxy/static/detach.js:578-582` | `ember-bridge` DOM 이벤트로 전달 |
| `window.__xmo` | iframe JS API | `ember/proxy/static/overlay.js:854` | `frame.html`(부모)이 VS Code iframe을 조종하는 API |
| `ember-terminals` 확장 | VS Code 웹 확장 | `ember/proxy/companion/package.json:2` | 통합 터미널을 ember node 세션으로 바꾼다 |
| `ember/vectors/bridge/detach_vectors.json` | 공유 테스트 벡터 | `ember/proxy/README.md:386` | `buildWorkspaceQuery`와 `ember-bridge`가 함께 검증 |

## 확장 (extensions)

자세히: [modules/extensions.md](modules/extensions.md)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `darkpyonix.vscode-darkpyonix` | VS Code 확장 ID | `extensions/vscode-darkpyonix/package.json:2,6` | `publisher` `darkpyonix` + `name`. `ember/proxy/dpx/vscode/runtime.py:51`가 기본 설치 목록에 넣는다 |
| `darkpyonix.vscode-darkpyonix-theme` | VS Code 확장 ID | `extensions/vscode-darkpyonix-theme/package.json:2,6` | `publisher`가 `DarkPyonix`(대문자). VS Code ID는 대소문자를 가리지 않는다 [추정] |
| `dev.darkpyonix.intellij` | IntelliJ 플러그인 ID | `extensions/intellij-darkpyonix/src/main/resources/META-INF/plugin.xml:3`, `build.gradle.kts:29` | |
| `extensions/vscode-darkpyonix/dist/extension.js` | 빌드 산출물 | `extensions/vscode-darkpyonix/esbuild.mjs:18`, `package.json:26` | `ember/ose/check-extensions.sh:16-18`가 이 파일이 있는지 본다 |
| `DarkPyonixApi` | TS 인터페이스 (확장 export) | `extensions/vscode-darkpyonix/src/extension.ts:20` | e2e 테스트용 `connectionFor`, `cellIdOf` |
| `darkpyonix.openAsNotebook` | Open as DarkPyonix Notebook | explorer, editor title 우클릭, 명령 팔레트 (`.py`/`.pynb`일 때) (`package.json:126-144`) | `vscode.openWith`로 `.pynb`는 `darkpyonix-notebook`, 그 밖은 `darkpyonix-notebook-py`로 연다 (`src/extension.ts:176-181`) |
| `darkpyonix.interruptKernel` | Interrupt Kernel | 노트북 툴바 (`package.json:110-114`) | `POST /api/kernels/{id}/interrupt`. 아무것도 안 돌면 상태 표시줄 문구 (`src/extension.ts:145-154`) |
| `darkpyonix.restartKernel` | Restart Kernel | 노트북 툴바 (`package.json:115-119`) | 소프트 재시작 `restart(false)` (`src/extension.ts:186-189`) |
| `darkpyonix.hardRestartKernel` | Restart Kernel Process (hard) | 팔레트만 | `restart(true)` 뒤 `resync()` (`src/extension.ts:190-193`) |
| `darkpyonix.shutdownKernel` | Shut Down Kernel | 팔레트만 | 모달 확인 뒤 `DELETE /api/kernels/{id}` (graceful) (`src/extension.ts:194-199`) |
| `darkpyonix.connect` | Connect to Manager / Join Collaboration | 노트북 툴바 `status@1` | Quick Pick 3가지: attach, local, remote(URL+토큰, 토큰은 `ctx.secrets`) (`src/extension.ts:204-233`) |
| `darkpyonix.reloadDocument` | Reload Document from Kernel | 팔레트만 | `session.resync()` (`src/extension.ts:200-202`) |
| `darkpyonix.showOutputLog` | Show Log | 팔레트만 | 출력 채널 "DarkPyonix" (`src/extension.ts:203`) |
| `darkpyonix.cliPath` | string | `darkpyonix` | `src/vscode/managerService.ts:69` | 임시 매니저를 띄울 CLI |
| `darkpyonix.managerArgs` | string[] | `["manager","--ephemeral"]` | `managerService.ts:70` | CLI 인자 |
| `darkpyonix.home` | string | `""` | `managerService.ts:61`, `src/manager/discovery.ts:26-30` | 비면 `$DARKPYONIX_HOME`, 그다음 `~/.darkpyonix` |
| `darkpyonix.manager.url` | string | `""` | `managerService.ts:33,62` | 전용 매니저 URL. 비면 로컬 탐색 |
| `darkpyonix.manager.token` | string | `""` | `managerService.ts:63` | 평문 설정 토큰. secret store(`TOKEN_SECRET`)가 먼저다 |
| `darkpyonix.manager.pathMap` | object | `{}` | `managerService.ts:38`, `discovery.ts:164-170` | 로컬 경로 접두사를 매니저 쪽 접두사로 바꾼다 (가장 긴 접두사) |
| `darkpyonix.autoStartKernel` | boolean | `false` | `src/extension.ts:122` | 열 때 커널 시작 또는 attach |
| `darkpyonix.python` | string | `""` | `src/extension.ts:101` | 새 커널 인터프리터 |
| `darkpyonix.nickname` | string | `""` | `managerService.ts:28` | 비면 호스트 이름, 64자 자름 |
| `darkpyonix.lockIdleSeconds` | number | `20` (최소 3) | `src/extension.ts:102` | 입력이 멈춘 뒤 잠금 해제까지 초 |
| `DarkPyonix.RunCell` | `RunCellAction` | Run Cell (단축키 `control alt shift ENTER`, `plugin.xml:36`) | 캐럿 위치 셀 실행 (`NotebookActions.kt:28-36`) |
| `DarkPyonix.RunAll` | `RunAllAction` | Run All Cells | `session.run(null)` (`NotebookActions.kt:38-42`) |
| `DarkPyonix.Interrupt` | `InterruptAction` | Interrupt Kernel | (`NotebookActions.kt:44-48`) |
| `DarkPyonix.Connect` | `ConnectAction` | Start or Attach Kernel | `connectAsync(startKernel = true)` (`NotebookActions.kt:50-54`) |
| `DarkPyonix.Restart` | `RestartKernelAction` | Restart Kernel… | Soft/Hard/Cancel 대화상자 (`NotebookActions.kt:56-73`) |
| `command` | `darkpyonix` | `darkpyonix.cliPath` |
| `spawnArgs` | `manager --ephemeral` (공백 분리 문자열, `:64`) | `darkpyonix.managerArgs` (배열) |
| `managerUrl` | `""` | `darkpyonix.manager.url` |
| `managerToken` | `""` (설정 XML에 평문) | `darkpyonix.manager.token` + secret store |
| `python` | `""` | `darkpyonix.python` |
| `nickname` | `""` (기본 `IntelliJ@<host>`, `:68-72`) | `darkpyonix.nickname` |
| `clientId` | 자동 `ij-` + UUID 20자 (`:51-60`) | VS Code는 globalState `vsc-` + 16 hex (`managerService.ts:22-30`) |
| `queueWhenBusy` | `true` | 없음 (VS Code는 항상 `on_busy: "queue"`, `src/connection.ts:124`) |
| `attachOnOpen` | `true` | `darkpyonix.autoStartKernel` (뜻이 다르다, 아래) |
| `.py` 판정 | 어떤 `.py`든 "Open as" 로 연다 (`package.json:45-53`) | `# %%` 마커가 있는 `.py`만 노트북 (`notebook/NotebookService.kt:21-29`) |

## 이름 정리 후보

모듈 문서와 분석 중 눈에 띈 것. 바꿀 때는 사용처를 모두 고쳐야 한다.

| 현재 이름 | 위치 | 실제 의미 | 제안 |
|---|---|---|---|
| `cr` (모듈 이름) | `ember/app/src/ui/cr/mod.rs:1` | compose-rust 화면. 이름만으로는 뜻을 알 수 없다 | Dioxus 원본을 지운 뒤(#226) `ui`로 올린다 |
| `ui::<파일>` 과 `ui::cr::<파일>` 같은 이름 쌍 | `ember/app/src/ui/`, `ember/app/src/ui/cr/` | 앞쪽은 Dioxus 원본(로직은 살아 있음), 뒤쪽은 실제 화면 | 로직을 `model` 류 모듈로 옮겨 이름 충돌을 없앤다 |
| `bridge` (세 곳) | `ember/bridge/` (크레이트), `ember/app/src/bridge.rs`, `ember/editor/src/bridge.rs` | 각각 IDE 창 메시지, 클라이언트 상태를 UI 신호로, 에디터 위젯 연결. 서로 관계없다 | 크레이트는 쓰이지 않으므로 정리하거나 `ember-ide-bridge` 등으로 |
| `XMO_*` 환경 변수 | `ember/proxy/` | 이전 이름(proxy 쪽 접두사). 다른 프로그램은 `EMBER_*`를 쓴다 | 문서화된 이름으로 통일 검토 |

