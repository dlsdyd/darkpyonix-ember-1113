# 모듈: hub

- 경로: `ember/hub/` (크레이트 `ember-hub`, `ember/hub/Cargo.toml:2`)
- 규모: 파일 11개 / 약 2,875줄 (`src/*.rs` 10개 2,843줄, `Cargo.toml` 32줄). 이 중 `src/fake.rs`가 1,028줄이다
- 레이어: 인프라 (darkpyonix.dev 허브 HTTP 클라이언트) + 시험용 가짜 허브(`fake`)
- 한 줄 책임: 허브 계정에 장치를 등록(device link)하고, 장치 목록, 주소, `/me`를 호출하고, 등록 파일을 보관하며, 허브가 장치를 제거했는지 감시한다 (`ember/hub/src/lib.rs:1-26`, SPEC `FR-N2`).
- 의존하는 모듈: `transport` (`ember/hub/Cargo.toml:11`, `PeerId`, `SecretKey`, `TransportConfig`, `HubDirectory`, `RelayConfig`. 백엔드 이름은 쓰지 않는다, FR-N5). 외부 크레이트는 `reqwest`(rustls), `serde`, `tokio`, `tracing`, `base64`, `hex`, `thiserror`, 선택 `axum`(`fake`).
- 이 모듈을 쓰는 모듈: `node` (`ember/node/Cargo.toml:17`, `ember/node/src/hub.rs:32`), `server-core`와 `server-api` (`ember/server/Cargo.toml:15`, `ember/server/src/hub/mod.rs:34`, `ember/server/src/hub/api.rs:35`, `ember/server/src/main.rs:141`, `ember/server/src/transport.rs:101`). 두 크레이트 모두 dev 의존으로 `features = ["fake"]`를 켠다 (`ember/server/Cargo.toml:70`, `ember/node/Cargo.toml:48`).

## 공개 인터페이스

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

## 파일별 요약

### `ember/hub/src/lib.rs` (51줄)
- 목적: 모듈 선언(`client`, `config`, `link`, `registration`, `types`, `watch`는 비공개, `paths`, `z32`는 공개, `fake`는 feature, `ember/hub/src/lib.rs:27-37`)과 재노출. 머리 주석이 허브 계약(`darkpyonix-core/docs/api/hub.openapi.yaml` v0.3.0, core PR #34)을 가리킨다 (`:1-3`).
- 주의점: 주소 게시와 조회는 이 크레이트의 HTTP 호출이 아니라 `ember_transport::HubDirectory`가 `/pkarr`로 직접 한다 (`:23-26`).

### `ember/hub/Cargo.toml` (32줄)
- feature `fake = ["dep:axum", "ember-transport/letify"]` (`ember/hub/Cargo.toml:9`). dev 의존에 자기 자신을 `fake`와 함께 넣어 통합 시험이 가짜 허브를 쓴다 (`:28`).

### `ember/hub/src/client.rs` (399줄)
- 목적: 허브 REST 호출을 타입으로 감싼다. `reqwest::Client`는 20초 타임아웃, User-Agent `ember/<버전>` (`ember/hub/src/client.rs:141-144`). `/config`는 5초 (`:25`), 롱폴은 `wait + 15초` (`:27`, `:317`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `HubError` | enum | 33 | `Unauthorized`, `DeviceRemoved`, `InvalidCredentials`, `Forbidden`, `NotFound`, `Conflict`, `BadRequest`, `RateLimited`, `Status`, `Unreachable`, `Decode`, `NotRegistered` |
| `error_for` | fn(비공개) | 187 | 응답 본문 `{error, code}`를 읽어 상태 코드와 `code`로 `HubError` 선택. `device_removed` 코드가 우선 (`:193-195`) |
| `config` | fn | 228 | `GET /config`. 404, 405, 501이면 `Ok(None)` |
| `create_link`, `claim`, `link_status`, `link_code`, `decide_link_code` | fn | 239, 246, 265, 272, 280 | 장치 연결과 링크 코드 승인 |
| `me`, `rotate_resolve_token` | fn | 290, 297 | `GET /me`, `POST /me/resolve-token` |
| `devices`, `devices_since`, `device`, `rename_device`, `set_app`, `readmit`, `remove_device`, `addresses` | fn | 303, 313, 337, 343, 350, 357, 363, 368 | 장치 목록(ETag, `?wait=`), 이름 변경, 앱 정보, 재허용, 제거, 주소 |
- `is_revocation` (`:82`)은 `DeviceRemoved` 또는 (이전에 동작하던 토큰의) 코드 없는 401을 제거로 본다 (`:36-38`).
- 부수효과: HTTP 요청. 토큰은 `Authorization: Bearer`로만 보낸다 (`with_token` `:150`, `Debug`는 토큰을 가린다 `:95`).
- 주의점: `HubClient::new`가 `expect("reqwest client builds")`로 패닉할 수 있다 (`:145`). `devices_since`는 `wait`를 1..=25초로 자른다 (`:313-318`). 테스트 1개.

### `ember/hub/src/config.rs` (255줄)
- 목적: 허브 URL과 릴레이, 디렉터리 설정. `HubConfig::from_env` (`ember/hub/src/config.rs:122`)는 `EMBER_HUB_URL`과 `EMBER_HUB_RELAY_URL`을 읽고, `parse` (`:134`)는 `off`, `none`, `disabled`, `0`이면 `None`(허브 끔), 빈 값이나 `default`면 기본 URL을 쓴다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `apply_info` | fn | 71 | `/config`를 적용. 명시된 릴레이(`Explicit`)는 덮지 않는다. `pkarr_url`은 절대 URL 또는 허브 기준 경로로 해석 |
| `discover` | fn | 98 | `GET /config`. 실패해도 오류 없이 파생값으로 대체 |
| `pkarr_url` | fn | 149 | 광고된 값, 없으면 `<hub>/pkarr` |
| `relay_config` | fn | 155 | `EMBER_RELAY_URL`이 있으면 그 환경값 우선, 없으면 허브 릴레이, 없으면 전송 기본값 |
| `directory`, `transport_config` | fn | 166, 172 | `HubDirectory`와 `TransportConfig`(환경 기반 위에 릴레이와 디렉터리 덮어쓰기) |
| `relay_config_for` | fn | 180 | 서버의 장치 기록이 알리는 `letify://` 릴레이를 허브 목록보다 우선 (INTENT D36) |
- 테스트 2개.

### `ember/hub/src/link.rs` (182줄)
- 목적: 장치 연결(허브 `FR-H1`). 흐름 (`ember/hub/src/link.rs:4-12`): `DeviceLink::start`(`POST /device-links`) 후 사용자가 코드를 승인, `poll`/`wait`가 `darkpyonix-hub/v2/link\n<link_id>\n<challenge>`에 엔드포인트 키로 서명해 올린다 (`link_message` `:29`).
- `poll` (`:132`): `Pending`, `Approved`(응답의 `endpoint_id`가 내 키와 다르면 `HubError::Decode`), 403은 `Denied`, 404는 `Expired`, 409는 `AlreadyRegistered`.
- `wait` (`:164`): 429면 간격을 두 배(최대 60초), `Unreachable`과 `Status`는 재시도, 만료까지 반복.
- 부수효과: 승인되면 `tracing::info!`로 장치 이름과 역할을 기록 (`:149`). 토큰은 `Registration`에 담겨 반환된다.
- 사용자에게 보이는 에러: 아래 표.

### `ember/hub/src/registration.rs` (379줄)
- 목적: 등록 결과의 구조와 보관, 제거 감시.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Registration` | struct | 27 | `hub_url`, `device`, `device_token`(`dpd_`), `resolve_token`(`dpr_`), `registered_at`, `revoked_at`. `Debug`는 토큰을 가린다 (`:73`) |
| `active_token`, `directory_token` | fn | 59, 64 | 폐기된 등록이면 `None` |
| `RegistrationFile` | struct | 89 | `hub.json` (`REGISTRATION_FILE` `:18`). `load`는 그룹과 다른 사용자가 읽을 수 있으면 0600으로 조인다(unix, `:112-122`). `save`는 임시 파일에 0600으로 쓰고 `sync_all` 후 `rename` (`:128-145`) |
| `mark_revoked`, `remove` | fn | 148, 159 | 폐기 표시(파일 유지), 로컬 삭제 |
| `RegistrationState` | enum | 170 | `Unknown`, `Active(Me)`, `Revoked`(최종), `Rejected`(최종 아님), `Unreachable` |
| `ensure_resolve_token` | fn | 206 | 없을 때만 `POST /me/resolve-token`. 새로 발급하면 이전 것이 폐기되므로 있으면 건드리지 않는다 (`:200-205`) |
| `watch_registration` | fn | 247 | `GET /me`를 주기적으로 호출. 폐기를 보면 종료 |
| `watch_registration_with` | fn | 272 | 허브가 롱폴을 광고하면 `DeviceWatcher`로 제거를 한 왕복 안에 감지 |
- 부수효과: 파일 쓰기와 권한 변경, `tokio::spawn` 백그라운드 작업, 경고 로그.
- 주의점: 권한 0600은 `cfg(unix)`에서만 적용된다 (`:112`, `:134`). 테스트 1개.

### `ember/hub/src/watch.rs` (152줄)
- 목적: `DeviceWatcher::next` (`ember/hub/src/watch.rs:90`)는 처음에는 현재 목록을 바로 돌려주고 이후 바뀔 때마다 돌려준다. 롱폴이면 `GET /devices?wait=25` + `If-None-Match`, 허브가 `wait`를 무시하면(0.5초 안에 3번 응답) 또는 400이면 `period`마다 조건부 폴링으로 바꾼다 (`:16-18`, `:145-151`).
- `expecting(id)`로 자기 id를 알려 주면, 목록에서 자기가 사라졌을 때 `HubError::DeviceRemoved("this device is no longer in the account's device list")`를 낸다 (`:113-117`). 오류 후에는 백오프(최대 30초) 뒤에 다시 묻는다 (`:20`).

### `ember/hub/src/types.rs` (310줄)
- 허브 OpenAPI의 와이어 타입. `Role`은 `MainServer`, `Computer`, `Client`(snake_case, `Client`는 허브 계약상 provisional, `ember/hub/src/types.rs:11-21`). `ClaimOutcome::Approved`의 `Debug`는 토큰을 `<redacted>`로 가린다 (`:93-107`). `HubInfo::supports_devices_wait`는 항상 `true`를 돌려준다 (`:177-179`). `AddressRecord::to_peer_addr` (`:146`)가 전송 계층의 `PeerAddr`로 바꾼다. 테스트 2개.

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/hub/src/paths.rs` | 52 | 호출 경로 상수(`CONFIG`, `DEVICE_LINKS`, `DEVICES`, `ME`, `ME_RESOLVE_TOKEN`)와 경로 함수(`device_link` `:12`, `device_link_token`, `link_code`, `device`, `device_readmit`, `device_addresses`), 시험용 `TEMPLATES` (`:38`). 버전 접두사 없음 (core NFR-V1, `/v1/*`은 404) |
| `ember/hub/src/z32.rs` | 65 | `encode` (`:6`), `decode_key` (`:26`, 52자만 허용, 마지막 4비트 패딩은 0이어야 함). 테스트 1개 |

### `ember/hub/src/fake.rs` (1,028줄, feature `fake`)
- 목적: 허브 OpenAPI 하위 집합을 구현한 프로세스 내 가짜 허브 (axum). 계정은 하나, "로그인한 브라우저"는 `FakeHub::session_token`을 Bearer로 보내는 것으로 표현한다 (`ember/hub/src/fake.rs:3-4`). 모든 401은 `device_removed` 또는 `invalid_credentials` 코드를 단다 (`:13`). GitHub 로그인, 릴레이, 공유, 이름은 구현하지 않는다 (`:14`).
- 데이터: 메모리의 `Inner`(`:93`)와 `Arc<Mutex<Inner>>`. 고정값 `ACCOUNT_ID`, `GITHUB_LOGIN = "octocat"` (`:46-47`), 재허용 유효 시간 `READMIT_SECS = 900` (`:53`), `?wait`는 0..=25 (`:51`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `FakeHub::start` | fn | 217 | 임의 포트에 서버 기동, `Drop`으로 정지 (`:371`) |
| `session_token`, `browser` | fn | 253, 258 | 계정 소유자 세션과 그 클라이언트 |
| `set_interval`, `set_link_ttl`, `set_config_enabled`, `set_config_relays`, `set_honour_wait` | fn | 263-283 | 오동작 허브와 옛 허브 흉내 |
| `approve`, `decide`, `register`, `remove`, `readmit`, `set_online` | fn | 318, 305, 323, 333, 338, 350 | 시험에서 허브 상태를 직접 조작 |
| `router` | fn | 386 | 라우트 표 (아래 동작 지도) |
| `pkarr_put`, `pkarr_get` | fn | 887, 924 | pkarr 릴레이 프로토콜. 서명 검사, 해석은 `dpr_` 토큰으로만 (`:12-13`) |
| `parse_txt_answers` | fn | 978 | DNS 패킷의 TXT 응답 파싱 (`MAX_DNS_PACKET = 1000`, `:49`) |
- 주의점: 긴 폴 대기는 변경 즉시 깨어나지만 허브가 약 2초마다 확인한다는 점이 실제와 다르다 (`:17-19`). `#![allow(clippy::result_large_err)]` (`:22`). 테스트 모듈은 `:1008`부터 약 20줄.

## 동작 지도

서버·노드 모듈 대응으로 허브 REST 호출과 가짜 허브 라우트를 적는다. 이 크레이트가 허브를 호출하는 쪽이고, 라우트는 `fake.rs` 라우터(`ember/hub/src/fake.rs:386-400`)다.

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `GET /health` | 인라인 `ember/hub/src/fake.rs:388` | 없음 | 상수 JSON |
| `GET /config` | `hub_config` `ember/hub/src/fake.rs:528` | `HubClient::config` `ember/hub/src/client.rs:228` | `Inner` |
| `POST /device-links` | `create_link` `:545` | `HubClient::create_link` `ember/hub/src/client.rs:239` | `Link` |
| `GET /device-links/{link_id}` | `get_link` `:592` | `link_status` `:265` | `Link` |
| `POST /device-links/{link_id}/token` | `claim_link` `:618` | `claim` `:246` | `Link`, `FakeDevice` |
| `GET`, `POST /link-codes/{code}` | `get_link_code` `:664`, `decide_link_code` `:678` | `link_code` `:272`, `decide_link_code` `:280` | `Link` |
| `GET /me` | `me` `:696` | `me` `:290` | 계정 |
| `POST /me/resolve-token` | `rotate_resolve_token` `:705` | `rotate_resolve_token` `:297` | 토큰 |
| `GET /devices` | `list_devices` `:735` | `devices`, `devices_since` `:303`, `:313` | ETag, 롱폴 |
| `GET`, `PATCH`, `DELETE /devices/{id}` | `get_device` `:772`, `update_device` `:780`, `remove_device` `:818` | `device`, `set_app`, `rename_device`, `remove_device` | `FakeDevice` |
| `POST /devices/{id}/readmit` | `readmit_device` `:830` | `readmit` `:357` | 15분 창 |
| `GET /devices/{id}/addresses` | `device_addresses` `:849` | `addresses` `:368` | `Record` |
| `PUT`, `GET /pkarr/{key}` | `pkarr_put` `:887`, `pkarr_get` `:924` | `ember_transport::HubDirectory` (이 크레이트가 아님) | `Record` |

위 표에서 핸들러 줄 번호는 `ember/hub/src/fake.rs` 기준이다.

사용자에게 보이는 에러 메시지 (주요한 것만, 원문):

| 원문 | 위치 | 조건 |
|---|---|---|
| `the hub did not accept this device's credentials (401): {0}` | `ember/hub/src/client.rs:36` | 코드 없는 401 |
| `the hub removed this device from the account: {0}` | `ember/hub/src/client.rs:41` | 401 `device_removed` |
| `rate limited by the hub (429)` | `ember/hub/src/client.rs:55` | 429 |
| `cannot reach the hub: {0}` | `ember/hub/src/client.rs:61` | 연결 실패 |
| `no device token: this device is not registered with the hub` | `ember/hub/src/client.rs:65` | 토큰 없이 인증 호출 |
| `the link was denied` | `ember/hub/src/link.rs:37` | 403 |
| `the link expired before it was approved (user code {0})` | `ember/hub/src/link.rs:39` | 404 또는 만료 |
| `this endpoint is already registered with the hub, or was removed from its account ({0}). A removed device can rejoin after ...` | `ember/hub/src/link.rs:41-44` | 409 |
| `the link was already claimed but this device did not keep its tokens: remove the device on the hub, re-admit it, and link again` | `ember/hub/src/link.rs:48` | 토큰 유실 |
| `this device is no longer in the account's device list` | `ember/hub/src/watch.rs:117` | 목록에서 자기 id 사라짐 |

## 데이터와 설정

- DB 없음. 저장 파일: `hub.json` (`REGISTRATION_FILE`), 디렉터리는 호출자가 정한다 (`RegistrationFile::in_dir` `ember/hub/src/registration.rs:99`). 안에 `device_token`, `resolve_token`이 평문으로 있다 (값은 `***`). 서버는 DB에 봉인해서 보관하고 노드는 0600 파일로 둔다 (`ember/hub/src/lib.rs:11-12`).

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_HUB_URL` | `ember/hub/src/config.rs:10` | 허브 URL. `off`, `none`, `disabled`, `0`은 끔 | `https://api.darkpyonix.dev` (`:13`) |
| `EMBER_HUB_RELAY_URL` | `ember/hub/src/config.rs:12` | 릴레이 명시 | 없음 (허브 `/config` 또는 파생) |
| `EMBER_RELAY_URL` | `ember_transport`의 `RELAY_URL_ENV`, 읽는 곳 `ember/hub/src/config.rs:156`, `:181` | 있으면 허브 릴레이보다 우선 | 없음 |
| `EMBER_LETIFY_*` | `ember/hub/src/config.rs:173` (주석) | 전송 백엔드 선택. 허브가 덮지 않는다 | 전송 쪽 기본 |

- 외부 연동: darkpyonix.dev 허브 REST(`/config`, `/device-links`, `/me`, `/devices`, `/pkarr`). 계약 문서는 `darkpyonix-core/docs/api/hub.openapi.yaml` v0.3.0이며 이 저장소에는 없다 (`hub/tests/openapi_paths.rs`가 대조한다고 적혀 있음, `ember/hub/src/paths.rs:2-3`) [확인 필요: tests는 읽지 않았다].

## 이 모듈을 수정할 때 주의할 점

- 경로나 와이어 타입을 바꾸면 `ember/hub/src/paths.rs`의 `TEMPLATES`, `ember/hub/src/fake.rs`의 라우터와 핸들러, 그리고 `hub/tests/openapi_paths.rs`를 같이 맞춘다.
- `HubError`의 변형을 바꾸면 서버의 `ember/server/src/hub/api.rs`가 `HubError`, `LinkError`, `RegistrationState`를 매핑하므로 같이 고친다 (`ember/server/src/hub/api.rs:35`).
- `Registration`의 필드를 바꾸면 노드의 `hub.json` 호환과 서버의 DB 봉인 형식을 확인한다 (`#[serde(default)]` 필드만 안전하게 추가할 수 있다).
- 이 크레이트가 바뀌면 `ember/server`, `ember/node`와 그 의존자의 `Cargo.lock`을 같은 PR에서 갱신한다 (AGENTS.md).
- `fake`는 서버와 노드의 시험이 쓰므로 가짜 허브 동작을 바꾸면 두 크레이트의 시험이 영향을 받는다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 중간 | `ember/hub/src/registration.rs:112-122`, `:134-137` | `hub.json`(장치 토큰 포함)의 0600 보장이 `cfg(unix)`에서만 있다. Windows 노드는 기본 ACL에 의존한다 (노드는 Windows를 지원한다, 최근 커밋 `#200`) | Windows ACL 제한 또는 DPAPI 보관, 아니면 한계를 문서화 |
| 하드코딩 | 낮음 | `ember/hub/src/config.rs:13` | 기본 허브 URL `https://api.darkpyonix.dev` | 의도된 기본값. 변경은 `EMBER_HUB_URL` |
| 하드코딩 | 낮음 | `ember/hub/src/fake.rs:46-47` | 가짜 허브의 `ACCOUNT_ID`, `GITHUB_LOGIN = "octocat"` | 시험 전용(feature `fake`), 조치 불필요 |
| 패닉 | 낮음 | `ember/hub/src/client.rs:145` | `HubClient::new`가 `expect`로 패닉 가능 (TLS 초기화 실패) | `Result` 반환 |
| 사용하지 않는 pub | 낮음 | `ember/hub/src/registration.rs:247`, `:272` | `watch_registration`, `watch_registration_with`는 `server/src`, `node/src`, `app/src`, `client/src`, `editor/src`, `transport/src`에서 호출 0회 (grep). 서버는 `DeviceWatcher`를 직접 쓰는 것으로 보인다 (`ember/server/src/hub/mod.rs` 안 `DeviceWatcher` 언급) [추정] | 쓰이지 않으면 제거 또는 서버 쪽 중복을 이 함수로 통합 |
| 사용하지 않는 pub | 낮음 | `ember/hub/src/client.rs:343`, `:357`, `ember/hub/src/config.rs:180`, `ember/hub/src/link.rs:29`, `ember/hub/src/types.rs:218` | `rename_device`, `readmit`, `relay_config_for`, `link_message`, `service_label`은 크레이트 밖 호출이 없다 (grep). 일부는 `hub/tests`나 `fake`가 쓸 수 있다 [확인 필요] | 시험 전용인지 확인 후 `#[cfg(test)]`나 `pub(crate)`로 |
| 하드코딩 | 낮음 | `ember/hub/src/types.rs:177-179` | `supports_devices_wait`가 항상 `true` (주석상 의도, 허브가 `wait`를 무시하면 감시자가 폴링으로 전환) | 현 상태 유지, 이름이 오해를 부를 수 있다 |
| 거대 파일 | 낮음 | `ember/hub/src/fake.rs` (1,028줄) | 가짜 허브가 한 파일에 있다 | 필요 시 분리. 시험 전용이라 우선순위 낮음 |
| 문서 | 낮음 | `ember/hub/src/lib.rs:2-3` | 허브 계약이 외부 저장소(`darkpyonix-core`)의 특정 브랜치 `feat/m4-hub-ember-gaps`를 가리킨다. 브랜치가 병합 후 지워지면 참조가 끊긴다 | 병합된 커밋이나 버전으로 교체 |
| TODO/FIXME | 낮음 | `ember/hub/src/` | 0개 (grep, `fake.rs` 포함) | 없음 |
