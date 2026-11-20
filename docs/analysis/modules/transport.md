# 모듈: transport

- 경로: `ember/transport/` (크레이트 `ember-transport`)
- 규모: 파일 16개 / 약 5,516줄 (`Cargo.toml` 포함, `tests/`는 [tests](tests.md) 모듈)
- 레이어: 인프라
- 한 줄 책임: Ember의 모든 네트워크 접근을 하나의 P2P 인터페이스(`Transport`, `Connection`, `BiStream`)로 감싸고, 백엔드(letify-link, 선택 iroh, 인메모리 가짜)와 기기 입장 제어(`PeerGate`), HTTP-over-transport를 제공한다 (`ember/transport/src/lib.rs:1-17`).
- 의존하는 모듈: 없음 (저장소 안 크레이트에 의존하지 않는다. 외부 `letify-link`(git), `iroh`, `ed25519-dalek`, `reqwest`, `axum`, `hyper`: `ember/transport/Cargo.toml:22-45`)
- 이 모듈을 쓰는 모듈: [hub](hub.md), [transfer](transfer.md), [client](client.md), [node](node.md), [node-enrol](node-enrol.md), [server-core](server-core.md), [server-computers](server-computers.md), [server-enrol](server-enrol.md), [server-accounts](server-accounts.md)

## 기능 플래그 (`ember/transport/Cargo.toml:8-20`)

| feature | 기본 | 켜는 의존성 | 켜지는 코드 |
|---|---|---|---|
| `letify` | 예 | `letify-link`, `reqwest` | `mod letify` (`lib.rs:31-32`), `pub use letify::{direct_addresses_from_txt, is_record_label, HttpPkarrStore, LETIFY_TRANSPORT_ID}` (`lib.rs:59-60`), `Transport::bind`의 `BackendKind::Letify` 분기 (`lib.rs:349-353`) |
| `http` | 예 | `axum`, `hyper`, `hyper-util` | `pub mod http` (`lib.rs:27-28`) |
| `iroh` | 아니오 (레거시) | `iroh`, `url` | `mod iroh_backend` (`lib.rs:29-30`), `ServiceTable::names` (`lib.rs:304-307`), `BackendKind::Iroh` 분기 (`lib.rs:344-348`) |
| `bench` | 아니오 | `serde_json` | 바이너리 `ember-transport-bench` (`Cargo.toml:53-56`, `required-features`) |

- `Transport::bind`는 `iroh`나 `letify` 중 하나라도 켜져야 존재한다 (`lib.rs:341`). 둘 다 없으면 `mem::MemNetwork`만 쓸 수 있다.
- 선택된 백엔드가 컴파일되지 않았으면 `TransportError::Config("the {other} backend is not compiled into this build")`를 돌려준다 (`lib.rs:354-357`).
- 의존 크레이트별 feature 선택: `client`는 `default-features = false, features = ["http"]` (`ember/client/Cargo.toml:14`, 백엔드는 바인드하는 쪽이 켠다), `hub`와 `transfer`는 `default-features = false` (`ember/hub/Cargo.toml:15`, `ember/transfer/Cargo.toml:10`), `hub`의 `fake` feature는 `ember-transport/letify`를 켠다 (`ember/hub/Cargo.toml:10`), `node`와 `server`는 기본 feature를 쓴다 (`ember/node/Cargo.toml:15`, `ember/server/Cargo.toml:13`).
- `.github/scripts/checks/check-transport-isolation.sh:2-5`가 `ember/transport/` 밖의 `.rs`·`Cargo.toml`에서 `iroh`, `letify-link` 언급을 막는다 (FR-N5).

## 공개 인터페이스 (다른 모듈이 쓰는 것)

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

## 파일별 요약

### `ember/transport/src/lib.rs` (약 555줄)
- **목적:** 크레이트 진입점. 공개 핸들(`Transport`, `Listener`, `Connection`, `BiStream`)과 내부 백엔드 경계(`TransportBackend`, `ConnectionBackend`), 서비스 표(`ServiceTable`)를 정의한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `TransportError` | enum(pub) | 64 | `InvalidKey`, `Config`, `Bind`, `Connect{peer,reason}`, `AlreadyListening`, `Closed`, `Stream`, `Io` |
  | `PathState::same_route` | fn(pub) | 120 | RTT를 무시하고 경로 종류·주소만 비교. 경로 변경 알림은 이것이 바뀔 때만 발생 |
  | `TransportBackend` | trait(crate) | 226 | 백엔드가 구현하는 경계. `allow_peer`, `revoke_peer`, `set_power_state`, `resume_now`, `enable_hub`, `set_relays`는 기본 no-op (`lib.rs:237-256`) |
  | `ConnectionBackend` | trait(crate) | 261 | `open_bi_bulk`의 기본 구현은 `open_bi` (`lib.rs:265-267`) |
  | `ServiceTable::register` | fn | 283 | 같은 서비스에 살아 있는 송신자가 있으면 `AlreadyListening`. 채널 용량 64 (`lib.rs:291`) |
  | `Transport::bind` | async fn(pub) | 342 | 백엔드 선택 |
  | `Transport::close` | async fn(pub) | 442 | 서비스 표를 비운 뒤 백엔드 종료 |
  | `Listener::accept` | async fn(pub) | 458 | 다음 연결, 트랜스포트가 닫히면 `None` |
  | `Connection::open_bi_bulk` | async fn(pub) | 524 | letify에서는 대화형 스트림보다 뒤로 밀리는 대량 스트림 |
- **입력 → 출력:** `TransportConfig` → `Transport`; `(PeerAddr, service)` → `Connection` → `BiStream`.
- **의존:** `addr.rs`, `config.rs`, `dialer.rs`, `gate.rs`, `key.rs`, `mem.rs`, `signal.rs`, feature에 따라 `http.rs`, `iroh_backend.rs`, `letify/`.
- **사용처:** `ember/server/src/main.rs:170`(`Transport::bind`), `ember/server/src/transport.rs:85`, `ember/node/src/transport.rs:140`, `ember/client/src/api.rs:13`, `ember/transfer/src/session.rs:23`.
- **부수효과:** 없음 (백엔드에 위임).
- **주의점:** 모듈 문서가 "Backends: `iroh` (feature `iroh`, default ...)"라고 쓰지만 (`lib.rs:13-15`), 실제 기본 feature는 `letify`이다 (`Cargo.toml:9`, `config.rs:24-33`). `Transport::bind` 문서도 "iroh by default"라고 쓴다 (`lib.rs:339-340`). 문서가 낡았다.
- 테스트: 없음.

### `ember/transport/src/config.rs` (약 392줄)
- **목적:** 바인드 설정. 백엔드 타입을 담지 않는 순수 데이터.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `BACKEND_ENV` | const(pub) | 12 | `"EMBER_TRANSPORT_BACKEND"` |
  | `BackendKind` | enum(pub) | 16 | `Iroh`, `Letify`. `Default`는 `letify` feature가 있거나 `iroh`가 없으면 `Letify` (`config.rs:27-33`) |
  | `BackendKind::parse/from_env` | fn(pub) | 38, 48 | `iroh`, `letify`, `letify-link` (대소문자 무시). 모르는 값은 경고 후 기본값 |
  | `ObserverAddr::parse` | fn(pub) | 79 | `host:port` 또는 `host:port#<peer id hex>` |
  | `LetifyConfig` | struct(pub) | 94 | letify 전용 설정. 기본값: `resume_window` 300초, `poll_interval` 1.5초, `dial_timeout` 8초, `connect_timeout` 20초 (`config.rs:126-142`) |
  | `LetifyConfig::from_env` | fn(pub) | 149 | `EMBER_LETIFY_RELAY_LISTEN`, `EMBER_LETIFY_QAD_LISTEN`, `EMBER_LETIFY_OBSERVER`, `EMBER_LETIFY_ADVERTISE` 읽기 |
  | `RELAY_URL_ENV` | const(pub) | 177 | `"EMBER_RELAY_URL"` |
  | `RelayConfig` | enum(pub) | 181 | `Default`, `Disabled`, `Custom(Vec<String>)`. `parse`는 `none/off/disabled`를 `Disabled`로 (`config.rs:193-206`) |
  | `HubDirectory` | struct(pub) | 231 | `pkarr_url`, `token`, `publish_direct`(기본 true). `Debug`는 토큰을 `<redacted>`로 가린다 (`config.rs:258-266`) |
  | `TransportConfig` | struct(pub) | 270 | `secret_key`, `relay`, `directory`, `hub`, `public_lookup`, `bind_addr`, `backend`, `letify` |
  | `TransportConfig::from_env` | fn(pub) | 306 | 릴레이, 백엔드, letify 설정을 환경 변수에서 |
- **입력 → 출력:** 환경 변수·빌더 호출 → `TransportConfig`.
- **의존:** `addr.rs`, `key.rs`, `signal.rs`.
- **사용처:** `ember/hub/src/config.rs:174`, `ember/node/src/hub.rs:227`, `ember/server/src/transport.rs:85`, `ember/server/src/transport.rs:107`, `ember/transport/src/bin/bench.rs:82`.
- **부수효과:** 환경 변수 읽기, 잘못된 값 `tracing::warn`.
- **주의점:** `EMBER_LETIFY_ADVERTISE`의 파싱 실패 항목은 경고 없이 버린다 (`config.rs:169`). 같은 함수의 다른 값은 경고한다 (`config.rs:155`, `165`). `LetifyConfig::relay_open`은 주석상 테스트 전용이다 (`config.rs:99-100`).
- 테스트: 4개, 릴레이 env 파싱, 백엔드 이름 파싱, 관찰자 주소 파싱, `HubDirectory` Debug 토큰 가림.

### `ember/transport/src/key.rs` (약 228줄)
- **목적:** Ed25519 신원(`PeerId`)과 비밀키(`SecretKey`), 키 파일 저장.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PeerId::from_bytes` | fn(pub) | 28 | 비정규 인코딩(`y >= p`, `x = 0`에 부호 비트)과 small-order 키를 거부 (FR-N6) |
  | `PeerId::verify` | fn(pub) | 46 | 서명 검증 |
  | `PeerId::fmt_short` | fn(pub) | 54 | 앞 10 hex, 로그용 |
  | `fingerprint_hex(id)` | fn(pub) | 63 | 64자 소문자 hex의 앞 16자를 4자씩 공백으로 (`abab abab abab abab`). 앱과 노드가 같이 쓴다 (FR-C2) |
  | `is_canonical` | fn | 74 | 정규 압축 인코딩 검사 |
  | `PeerId` `FromStr`/`Serialize`/`Deserialize` | impl | 100, 113, 119 | 64 hex 문자열 |
  | `SecretKey::generate` | fn(pub) | 132 | OS 난수. 실패 시 panic (`key.rs:134`) |
  | `SecretKey::sign` | fn(pub) | 148 | 허브에 키 소유 증명용 서명 |
  | `SecretKey::load_or_generate(path)` | fn(pub) | 161 | 파일에서 읽거나 새로 만들어 0600으로 저장 |
  | `tighten_permissions` | fn | 211, 226 | Unix에서 0600으로 조임, 비 Unix는 no-op |
- **입력 → 출력:** 키 파일 경로 → `SecretKey`; hex 문자열 → `PeerId`.
- **의존:** `ed25519-dalek`, `getrandom`, `hex`.
- **사용처:** `ember/node/src/enrol_cli.rs:815`(`load_or_generate`), `ember/server/src/computers/enrol.rs:357`(`fingerprint_hex`), `ember/node/src/enrol_cli.rs:413`.
- **부수효과:** 파일 읽기·쓰기(`create_new`, `sync_all`), 권한 변경.
- **주의점:** Windows에서는 키 파일 권한을 제한하지 않는다 (`key.rs:192-196`은 `cfg(unix)`만, `key.rs:225-228`은 no-op). `SecretKey`는 `Clone`이고 메모리 소거(zeroize)를 하지 않는다 (`key.rs:127-128`). `SecretKey::peer_id`는 `from_bytes` 검사 없이 `PeerId`를 만든다 (`key.rs:153-155`).
- 테스트: 없음 (`ember/transport/tests/key.rs`에 있다).

### `ember/transport/src/gate.rs` (약 252줄)
- **목적:** 기기별 입장 허용과 취소 (FR-N3). 저장소와 무관하다: server는 devices 표에서, node는 설정에서 채운다 (`gate.rs:10-11`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CLOSE_NOT_ALLOWED` | const(pub) | 24 | `403`, 수락 시 거부 |
  | `CLOSE_REVOKED` | const(pub) | 26 | `401`, 취소로 종료 |
  | `PeerGate` | struct(pub) | 31 | 허용 목록과 살아 있는 연결 |
  | `Class::of` | fn | 63 | 마지막 바이트의 부호 비트를 지운 키. A와 -A를 같은 기기로 본다 (FR-N6) |
  | `PeerGate::allow_list/open` | fn(pub) | 89, 98 | 목록 게이트(빈 목록은 아무도 허용 안 함), 열린 게이트 |
  | `PeerGate::attach(transport)` | fn(pub) | 106 | 현재 허용 목록을 `allow_peer`로 전달하고 이후 변경도 전달 |
  | `PeerGate::allow/revoke/set_allowed` | fn(pub) | 134, 145, 173 | 허용 추가, 취소(연결 즉시 닫음, 닫은 수 반환), 목록 교체 |
  | `PeerGate::admit(conn)` | fn(pub) | 210 | 허용 안 되면 `CLOSE_NOT_ALLOWED`로 닫고 `None` |
  | `PeerGate::live_connections` | fn(pub) | 249 | 피어의 살아 있는 연결 수 |
- **입력 → 출력:** 수락된 `Connection` → 허용된 `Connection` 또는 `None`.
- **의존:** `lib.rs`(`Connection`, `Transport`).
- **사용처:** `ember/server/src/transport.rs:135`(`attach`), `ember/node/src/transport.rs:152`, `ember/server/src/devices/mod.rs:19`, `ember/node/src/main.rs:10`.
- **부수효과:** 연결 닫기, 연결마다 감시 태스크 spawn (`gate.rs:226`), 로그.
- **주의점:** `admit`와 `revoke`는 한 락(`GateInner::state`)을 쓰므로 섞이지 않는다 (`gate.rs:37-39`). 열린 게이트에서 `attach`하면 `allowed()`가 `None`이라 백엔드에 아무것도 전달되지 않는다 (`gate.rs:107`). 그러면 letify 백엔드의 `admitted`가 `None`으로 남아 모든 송신자의 릴레이 제안을 믿는다 (`letify/mod.rs:380-383`). `revoke`는 닫기 프레임을 큐에 넣은 뒤 백엔드에 취소를 알린다 (순서 의존, `gate.rs:160-164`). `attach`는 `Transport`를 강한 참조로 보관한다 (`gate.rs:110`).
- 테스트: 없음 (`ember/transport/tests/gate.rs`, `letify_gate.rs`).

### `ember/transport/src/dialer.rs` (약 121줄)
- **목적:** 다이얼하는 쪽의 연결 캐시. (피어, 서비스)마다 `Connection` 하나를 두고 스트림을 여러 개 연다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `Dialer::new` | fn(pub) | 48 | |
  | `Dialer::connection` | async fn(pub) | 60 | 캐시에 없으면 다이얼. 동시 첫 호출은 둘 다 다이얼할 수 있고 나중 것이 캐시를 차지 (`dialer.rs:58-59`) |
  | `Dialer::open_bi` | async fn(pub) | 90 | 스트림 열기 실패 시 캐시를 버리고 한 번 다시 다이얼 |
  | `Dialer::forget/disconnect` | fn(pub) | 103, 111 | 한 서비스 또는 피어의 모든 연결을 닫고 잊음 |
- **입력 → 출력:** `(&PeerAddr, service)` → `BiStream`.
- **의존:** `lib.rs`.
- **사용처:** `ember/client/src/api.rs:790`, `ember/node/src/client.rs:267`, `ember/server/src/computers/bridge.rs:63`, `ember/server/src/computers/mod.rs:942`(`disconnect`).
- **부수효과:** 연결마다 감시 태스크 spawn (`dialer.rs:74`), 마지막 복제본 drop 시 모든 연결 닫음 (`dialer.rs:30-39`).
- **주의점:** `addr`가 비어 있지 않으면 `add_peer_addr`로 힌트를 남긴다 (`dialer.rs:65-67`). 항상 `open_bi`(대화형)만 쓰고 `open_bi_bulk`는 제공하지 않는다.

### `ember/transport/src/http.rs` (약 134줄, feature `http`)
- **목적:** 스트림 하나에 HTTP/1.1 연결 하나를 싣는다. axum 서버와 hyper 클라이언트를 트랜스포트 위에서 쓴다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `HttpListener::new/with_gate` | fn(pub) | 39, 45 | 게이트 없이 또는 `PeerGate`로 거른 리스너 |
  | `HttpListener::build` | fn | 49 | 수락 루프 태스크. 연결마다 `accept_bi` 루프 태스크 |
  | `impl axum::serve::Listener for HttpListener` | impl | 82 | 트랜스포트가 닫히면 영원히 대기 (`http.rs:89-90`) |
  | `impl Connected<..> for PeerId` | impl | 99 | 핸들러가 `ConnectInfo<PeerId>`로 호출자를 안다 |
  | `http1_client(conn)` | async fn(pub) | 107 | 새 스트림 위 hyper 핸드셰이크 |
  | `http1_handshake(stream)` | async fn(pub) | 119 | 이미 연 스트림 위 핸드셰이크, upgrade 허용 |
- **입력 → 출력:** `Listener` → axum 리스너; `BiStream` → `SendRequest<B>`.
- **의존:** `lib.rs`, `gate.rs`, `axum`, `hyper`, `hyper-util`.
- **사용처:** `ember/server/src/transport.rs:136`, `ember/node/src/transport.rs:153`, `ember/client/src/api.rs:792`, `ember/node/src/client.rs:268`.
- **부수효과:** 태스크 spawn. `HttpListener` drop 시 수락 태스크 abort (`http.rs:76-80`).
- **주의점:** 트랜스포트가 닫혀도 `accept`가 끝나지 않으므로 서버를 멈추려면 graceful shutdown이 필요하다 (`http.rs:89-90`). `http1_client`는 저장소 소스에서 쓰이지 않는다 (테스트에서만, 노트 A 참고).

### `ember/transport/src/mem.rs` (약 310줄)
- **목적:** 항상 컴파일되는 인메모리 가짜 트랜스포트. 다른 크레이트 테스트용 (FR-N5).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PIPE_BUFFER` | const | 34 | 256 KiB duplex 버퍼 |
  | `MemNetwork::new/transport/transport_with_key` | fn(pub) | 61, 66, 71 | 같은 id의 이전 노드를 교체 |
  | `MemNetwork::set_path` | fn(pub) | 85 | 두 피어 사이 모든 연결의 `PathState`를 바꿔 감시자를 깨운다 |
  | `MemNode` | struct | 96 | `TransportBackend` 구현. `wait_online`은 항상 `true` (`mem.rs:157-159`) |
  | `MemConn` | struct | 170 | 한쪽 연결. drop 시 닫힘 (`mem.rs:218-230`) |
  | `MemConn::open_bi` | async fn | 234 | 두 duplex 파이프를 펌프로 잇고, 연결이 닫히면 펌프를 멈춘다 |
- **입력 → 출력:** 프로세스 안 `Transport` 여러 개.
- **의존:** `lib.rs`.
- **사용처:** `ember/server/src/computers/enrol.rs:3224`(테스트 모듈), 크레이트 `tests/` 16개 파일.
- **부수효과:** 스트림마다 펌프 태스크 spawn.
- **주의점:** 지연과 손실이 없다 (`mem.rs:17`). `allow_peer`, `revoke_peer`는 기본 no-op이라 게이트 아래 차단은 시험되지 않는다.

### `ember/transport/src/signal.rs` (약 181줄)
- **목적:** letify 백엔드의 랑데부(`SignalChannel`)와 pkarr 디렉터리(`PkarrStore`) 경계, 그리고 테스트용 인메모리 구현.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SIGNAL_MAX` | const(pub) | 25 | 4096바이트 |
  | `SignalChannel` | trait(pub) | 30 | `send`, `recv`, `watch` |
  | `PkarrStore` | trait(pub) | 46 | `put`, `get`, `set_token` |
  | `verify_pkarr_payload` | fn(pub) | 57 | 64바이트 서명 + 8바이트 타임스탬프(마이크로초 BE) + DNS. 72바이트 미만 거부 |
  | `pkarr_signable` | fn(pub) | 72 | `3:seqi<ts>e1:v<len>:<dns>` |
  | `MemorySignalHub/MemorySignal` | struct(pub) | 86, 104 | 인프로세스 신호망 |
  | `MemoryPkarrStore` | struct(pub) | 141 | 서명이 틀리거나 더 새롭지 않은 패킷 거부 (`signal.rs:168-176`) |
- **입력 → 출력:** 서명된 pkarr 페이로드 ↔ `(timestamp, dns)`.
- **의존:** `key.rs`.
- **사용처:** `ember/transport/src/letify/pkarr.rs:27`, `ember/transport/src/config.rs:7`. 저장소 소스의 다른 크레이트는 쓰지 않는다 (테스트만).
- **부수효과:** 없음.
- **주의점:** pkarr 페이로드 형식은 허브(`hub/src/fake.rs`)와 같아야 한다 (`signal.rs:42-44`).

### `ember/transport/src/iroh_backend.rs` (약 474줄, feature `iroh`)
- **목적:** 레거시 iroh 1.x 백엔드. `iroh`를 이름으로 부르는 유일한 모듈 (`iroh_backend.rs:1`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `IrohBackend::bind` | async fn | 39 | `presets::Minimal`, `public_lookup`이면 `presets::N0`, 릴레이 모드, `MemoryLookup` 힌트, `DirectoryLookup` |
  | `accept_loop` | async fn | 96 | ALPN을 서비스 이름으로 써서 라우팅, 없으면 코드 1로 닫음 |
  | `services_changed` | fn | 134 | 서비스 표가 바뀌면 ALPN 목록 갱신 |
  | `enable_hub` | fn | 169 | iroh `PkarrPublisher`와 `HubResolver` 등록. 재호출은 토큰만 갱신 |
  | `set_directory_token` | fn | 193 | 토큰을 URL 쿼리 `?token=`에 넣은 `PkarrResolver`로 교체 |
  | `set_relays` | async fn | 216 | 릴레이 맵 추가·삭제 |
  | `IrohConnection`, `monitor_paths`, `current_path` | struct/fn | 258, 284, 309 | 경로 이벤트를 `PathState` 감시로 |
  | `close_reason` | fn | 322 | iroh `ConnectionError` → `CloseReason` |
  | `DirectoryLookup` | struct | 407 | Ember `AddressDirectory`를 iroh lookup으로 |
  | `hub_pkarr_url` | fn | 443 | 쿼리 없는 http(s) URL만 허용 |
- **의존:** `iroh`, `url`, `lib.rs`.
- **사용처:** `lib.rs:346` (`BackendKind::Iroh`일 때만).
- **부수효과:** UDP 소켓, 외부 릴레이(n0 기본 릴레이, `config.rs:183`), 허브 pkarr HTTP.
- **주의점:** `allow_peer`, `revoke_peer`, `set_power_state`, `resume_now`를 구현하지 않으므로 기본 no-op이다 (`lib.rs:248-256`). Cargo 주석은 "kept for one release"이다 (`Cargo.toml:10-11`).

### `ember/transport/src/letify/mod.rs` (약 971줄)
- **목적:** 기본 백엔드. letify-link Noise 세션을 TCP 경로와 메인 서버 릴레이 위에서 운용한다 (`letify/mod.rs:1-26`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `LETIFY_TRANSPORT_ID` | const(pub) | 68 | `record::DEFAULT_TRANSPORT` (테스트 기대값 `letify-link/1`, `letify/mod.rs:932`) |
  | `MAX_MEETINGS` | const | 71 | 동시 릴레이 제안 처리 8개 |
  | `MAX_TCP_CANDIDATES` | const | 73 | 피어당 TCP 후보 8개 |
  | `Inner` | struct | 112 | 백엔드 상태 전체 (링크, 힌트, 릴레이, 신호, `admitted`, pkarr, 관찰 주소, 전원) |
  | `LetifyBackend::bind` | async fn | 168 | TCP 리스너, 선택적 릴레이 역할(`relay_listen`), QAD 응답자(`qad_listen`), 관찰 루프, 신호, pkarr, 허브 |
  | `Inner::advertised` | fn | 313 | 공개할 TCP 주소. QAD 되접속 확인 후에만 관찰 IP를 공개 (`letify/mod.rs:322-330`) |
  | `Inner::record_txt` | fn | 351 | 서명된 주소 레코드 |
  | `Inner::trusts` | fn | 378 | 릴레이가 우리 서버이고, 게이트가 붙었으면 송신자가 허용된 기기일 때만 릴레이 만남 수락 |
  | `Inner::register_link` | fn | 444 | 종료 중 추가된 링크를 즉시 닫음 (#411 경합 수정) |
  | `Inner::dial` | async fn | 546 | 힌트, 디렉터리, pkarr 레코드에서 TCP 후보 수집, 릴레이 후보 추가, `PathManager::start` |
  | `Inner::connect` | async fn | 618 | 링크 위 연결을 열고, 세션이 죽었으면 한 번 다시 |
  | `Inner::revoke/allow` | fn | 658, 678 | acceptor·relay에 취소/복원, 시작한 세션 닫기 |
  | `relay_candidate` | fn | 690 | `RelayOffer`를 랑데부로 보내고 릴레이에 다이얼 |
  | `refused_by_all` | async fn | 710 | 모든 주소가 즉시 거부하면 타임아웃을 기다리지 않음 (1.5초 프로브) |
  | `accept_loop`, `manage`, `signal_loop`, `observe_loop` | async fn | 725, 746, 766, 795 | 배경 태스크. 관찰은 300초마다 또는 `resume_now` 시 |
  | `impl TransportBackend for LetifyBackend` | impl | 833 | 경계 구현 |
- **입력 → 출력:** `TransportConfig` → `Arc<LetifyBackend>`.
- **의존:** `link.rs`, `pkarr.rs`, `relay_url.rs`, `letify-link`.
- **사용처:** `lib.rs:351`.
- **부수효과:** TCP 리스너(기본 `0.0.0.0:0`, `letify/mod.rs:177`), 릴레이 TCP, QAD UDP, pkarr HTTP, 다수의 배경 태스크.
- **주의점:** `wait_online`은 타임아웃을 무시하고 닫히지 않았으면 `true`다 (`letify/mod.rs:855-857`). `lib.rs:435-436`의 "home relay에 연결될 때까지 대기" 의미와 다르다. `set_relays`는 첫 번째 파싱되는 `letify://` URL만 쓰고 나머지는 버린다 (`letify/mod.rs:880-891`). `Default`·`Disabled`는 자기 릴레이로 돌아간다 (`letify/mod.rs:893-895`). 정책 `PeerPolicy::from_fn(|_| true)`: 입장은 `PeerGate` 몫이다 (`letify/mod.rs:185-187`). UDP 경로와 홀펀칭은 아직 없다 (`letify/mod.rs:24-26`).
- 테스트: 1개, 레코드에 `letify-link/1`이 없는 피어는 두 목록을 이름으로 대며 거부.

### `ember/transport/src/letify/link.rs` (약 673줄)
- **목적:** 피어 쌍당 letify 세션 하나(`PeerLink`) 위에 Ember 연결 여러 개(`LConn`)를 다중화한다.
- **와이어 형식:** 스트림마다 5바이트 헤더 `kind(u8) + conn id(u32 BE)`. kind 1은 제어 스트림: 여는 쪽이 `service_len:u8, service`, 받는 쪽이 `status:u8, reason_len:u8, reason`(0=수락). 종료 시 `'C', code:u32, reason_len:u16, reason` 한 프레임. kind 2는 데이터 스트림 (`link.rs:7-17`). 연결 id는 세션 시작 쪽이 짝수, 상대가 홀수 (`link.rs:290`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `KIND_CTRL/KIND_DATA/FRAME_CLOSE` | const | 39-41 | 1, 2, `b'C'` |
  | `HEADER_TIMEOUT/OPEN_TIMEOUT` | const | 43, 45 | 10초 |
  | `OpenError` | enum | 48 | `Refused`(재시도 안 함), `Dead`(새 세션으로 재시도) |
  | `PeerLink::compute_state` | fn | 164 | 모든 subflow가 릴레이면 `Relayed`, 아니면 `Direct{remote: None}` |
  | `PeerLink::close_local` | async fn | 218 | 경로 관리자 먼저 멈추고 세션 닫음 |
  | `PeerLink::teardown` | fn | 237 | 세션 종료 사유 `"revoked"`이면 코드 `CLOSE_REVOKED` |
  | `PeerLink::open_conn` | async fn | 283 | 서비스 이름 1-255바이트 |
  | `PeerLink::accept_conn` | async fn | 326 | 거부 사유 `"service not available"`, `"connection id in use"` |
  | `run_demux`, `run_path_watch`, `handle_stream` | async fn | 373, 386, 398 | 스트림 라우팅, 경로 감시 |
  | `ConnShared::close_local` | fn | 456 | 닫기 프레임을 noop waker로 즉시 큐에 넣고, 남으면 태스크로 씀 |
  | `ctrl_reader` | async fn | 499 | 제어 스트림 끝을 `CloseReason`으로 |
  | `LConn` | struct | 536 | `ConnectionBackend` 구현. `open_bi`는 `Priority::Interactive`, `open_bi_bulk`는 `Priority::Bulk` (`link.rs:572-578`) |
  | `Guarded<T>` | struct | 622 | 연결이 닫히면 읽기는 EOF, 쓰기는 `BrokenPipe` |
- **의존:** `letify-link`, `gate.rs`(`CLOSE_REVOKED`), `lib.rs`.
- **사용처:** `letify/mod.rs:54`.
- **부수효과:** 스트림·연결마다 태스크 spawn.
- **주의점:** 거부 응답의 사유 읽기에는 타임아웃이 없다 (`link.rs:305-306`). 등록되지 않았거나 닫힌 연결 id의 데이터 스트림은 조용히 버린다 (`link.rs:407-413`). 와이어 형식을 바꾸면 양쪽 엔드포인트가 함께 바뀌어야 한다.

### `ember/transport/src/letify/pkarr.rs` (약 638줄)
- **목적:** 허브의 pkarr 디렉터리를 letify 백엔드의 랑데부로 쓴다. 한 패킷에 `_letify.<key>` 주소 레코드와 `m<recipient>.<key>` 우편함을 싣는다 (`pkarr.rs:1-13`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MAX_DNS` | const | 31 | 1000바이트 |
  | `MAILBOX_BYTES` | const | 33 | 수신자당 200바이트 |
  | `MESSAGE_TTL_S` | const | 35 | 120초 |
  | `REPUBLISH` | const | 37 | 120초마다 재서명·재공개 |
  | `RECORD_LABEL` | const | 39 | `"_letify"` |
  | `z32` | fn | 52 | z-base-32 (허브 `/pkarr/{key}` 경로) |
  | `mailbox_label` | fn | 71 | `m` + 수신자 키 앞 8바이트 hex |
  | `build_dns/parse_dns/read_name` | fn | 80, 136, 104 | 최소 DNS TXT 패킷 생성·해석, 압축 포인터 32회 제한 |
  | `HttpPkarrStore` | struct(pub) | 174 | `PUT/GET {base}/{z32}`, 10초 타임아웃, GET에 `?token=` |
  | `direct_addresses_from_txt` | fn(pub) | 295 | 레코드 TXT에서 TCP 주소. fake 허브가 쓴다 |
  | `is_record_label` | fn(pub) | 306 | 이름의 첫 라벨이 `_letify`인지 |
  | `PkarrNode::start` | fn | 313 | 공개 루프와 폴링 루프 시작 (약한 참조) |
  | `PkarrNode::build_packet` | fn | 367 | 크기를 넘으면 가장 오래된 메시지부터 버림 |
  | `PkarrNode::lookup` | async fn | 429 | 서명 검증 후 레코드가 같은 노드를 가리키는지 확인 |
  | `PkarrNode::poll_peer` | async fn | 447 | 본 적 없는 시퀀스만 수신함에 넣음 |
  | `publish_loop`, `poll_loop` | async fn | 488, 517 | 실패 시 2초에서 60초까지 지수 백오프 |
  | `impl SignalChannel for PkarrNode` | impl | 531 | 운영용 신호 채널. 메시지 + 6바이트가 200바이트를 넘으면 거부 |
- **의존:** `signal.rs`, `key.rs`, `letify-link::record`, `reqwest`.
- **사용처:** `letify/mod.rs:52-56`, `ember/hub/src/fake.rs:862-863`.
- **부수효과:** HTTP PUT/GET (허브), 배경 태스크 2개.
- **주의점:** 시퀀스 번호는 유닉스 초와 섞인 값이다 (`pkarr.rs:539`). TTL 비교가 이에 의존한다 (`pkarr.rs:373`). `z32`는 `ember/hub/src/z32.rs`에도 따로 있다 (중복). `published()`는 `#[allow(dead_code)]` (`pkarr.rs:346-349`).
- 테스트: 4개, z32 길이·알파벳, DNS 왕복, 서명된 패킷을 통한 메시지 왕복, 레코드 조회와 노드 일치.

### `ember/transport/src/bin/bench.rs` (약 389줄, feature `bench`)
- **목적:** NFR-N1 측정 도구 `ember-transport-bench`. `listen`은 주소 JSON 한 줄을 출력하고, `dial`은 연결 시간, 직접 경로 시간, RTT p50/p95, 처리량, 경로 변화, 원시 TCP 기준선을 JSON으로 출력한다 (`bench.rs:1-20`).
- **주요 심볼:** `SERVICE = "ember/bench/0"` (32), `ListenInfo` (37), `bind` (77, `TransportConfig::from_env`), `main` (93), `listen` (111), `serve_stream` (156, 첫 바이트 `E` 에코 / `S` 싱크), `rtt_summary` (186), `pings` (205), `throughput` (224), `dial` (250), `tcp_baseline` (346).
- **입력 → 출력:** CLI 인자 → stdout JSON.
- **사용처:** `ember/transport/tests/bench_harness_test.rs`, `.github/scripts/bench/summarize-matrix.py` [확인 필요: 스크립트가 출력 형식을 읽는지].
- **부수효과:** TCP 리스너, 키 파일(`--key`), 네트워크.
- **주의점:** `listen`은 게이트 없이 모든 피어를 받는다 (`bench.rs:143-152`). 측정 전용이다.

### 작은 파일

| 파일 | 줄 | 요약 |
|---|---|---|
| `ember/transport/Cargo.toml` | 56 | 기능 플래그(위 표), `letify-link`을 git rev `c66d017a...`로 고정 (`Cargo.toml:35`), bench 바이너리 |
| `ember/transport/src/addr.rs` | 89 | `PeerAddr{peer, relays, direct}` (`addr.rs:23`), `AddressDirectory` trait(`publish`는 fire-and-forget, `addr.rs:53`), `MemoryDirectory` (`addr.rs:61`). 다른 크레이트 소스는 `AddressDirectory`를 구현하지 않는다 |
| `ember/transport/src/letify/relay_url.rs` | 53 | `letify://<64 hex>@host:port` 파싱 → `RelayTarget{addr,node,url}` (`relay_url.rs:13`, `23`). 테스트 1개, URL 파싱 성공·실패 |

## 이 모듈을 수정할 때 주의할 점

- **공개 API에 백엔드 타입을 넣지 않는다.** FR-N5이고 CI 검사가 있다 (`lib.rs:16-17`, `.github/scripts/checks/check-transport-isolation.sh`).
- **기본 백엔드 결정은 세 곳에 있다:** `Cargo.toml:9`의 `default`, `BackendKind::default` (`config.rs:24-33`), `EMBER_TRANSPORT_BACKEND` (`config.rs:48-57`). 플릿의 모든 엔드포인트가 같은 값을 써야 한다 (`config.rs:11`).
- **`PeerGate`의 `Class`(부호 비트 무시)와 letify의 `NodeId::canonical`은 같은 동치를 가정한다** (`gate.rs:54-68`, `letify/mod.rs:6-8`). 한쪽만 바꾸면 취소된 기기가 별칭으로 돌아올 수 있다.
- **연결 종료 코드 `401`/`403`**은 `gate.rs:24-26`에 있고 letify는 세션 종료 사유 문자열 `"revoked"`를 코드 401로 바꾼다 (`link.rs:242`, `link.rs:520`). 사유 문자열을 바꾸면 매핑이 깨진다 (`letify/mod.rs:673`).
- **pkarr 페이로드 형식·z32 인코딩은 허브와 공유한다** (`signal.rs:42-44`, `letify/pkarr.rs:49-68`, `ember/hub/src/z32.rs`). 허브 쪽 구현과 함께 바꾼다.
- **배경 태스크가 많다.** 대부분 약한 참조로 끝나지만 `LetifyBackend` drop은 `bg` 태스크를 abort만 한다 (`letify/mod.rs:152-165`). 정상 종료는 `Transport::close`를 거친다.
- **`open_bi_bulk`는 정의돼 있지만 파일 전송(`ember/transfer/src/session.rs:469`)은 `open_bi`를 쓴다.** 우선순위 분리를 기대하면 그쪽을 고쳐야 한다 [확인 필요: 의도인지].
