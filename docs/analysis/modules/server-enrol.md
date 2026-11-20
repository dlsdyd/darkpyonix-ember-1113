# 모듈: server-enrol

- 경로: `ember/server/src/computers/enrol.rs`, `ember/server/src/enrol_door.rs`, `ember/server/src/door/`
- 규모: 파일 7개 / 약 4,704줄 (`enrol.rs` 3,281 중 테스트가 1,545줄 이후 약 1,700줄)
- 레이어: API (보안 경계) + 인프라 (door 공용 가드)
- 한 줄 책임: 다른 컴퓨터를 등록하는 일회용 enrol 코드의 발급(mint), 교환(redeem), 소유자 확인(confirm/deny), 자격 증명 1회 전달과, 그 요청을 받는 별도 리스너(enrol door)의 방어 계층을 제공한다.
- 의존하는 모듈: [server-computers](server-computers.md) (`Computers`, 레지스트리 등록), [server-core](server-core.md) (`Store`, 마이그레이션, `auth`), [server-api](server-api.md) (`api::origin::host_of`), [server-collab](server-collab.md) (`channels::invites::new_secret`, `is_forbidden_name_char`), [transport](transport.md) (`PeerId`, `fingerprint_hex`)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs` 조립, 마이그레이션 상수), [server-collab](server-collab.md) (`guest_door.rs`가 `door/`를 공유), `ember/node` (`enrol_cli.rs`가 door 두 라우트 호출), [client](client.md) (`api.rs`가 owner 라우트 호출)

## 보안 경계 요약

두 개의 서로 다른 신뢰 영역이 있고, 같은 `Arc<Enrol>` 하나를 공유한다 (`ember/server/src/main.rs:205`).

| 영역 | 라우트 | 인증 | 리스너 |
|---|---|---|---|
| owner 로컬 라우터 | mint, status, cancel, confirm, deny | 서버 토큰 + Origin/Host (`auth::protect`가 `local_app` 전체에 적용, `ember/server/src/main.rs:517`) | `EMBER_LISTEN` (TCP, 로컬 전용) |
| enrol door | `POST /enrol/redeem`, `GET /enrol/status/{enrol_id}` | 토큰 없음. 코드(redeem) 또는 poll secret(poll)이 인증 수단 | `EMBER_ENROL_LISTEN` (별도 리스너, 기본 꺼짐) |

- redeem 라우트는 owner 라우터에 없다. `ember/server/src/main.rs:487-490` 주석이 명시한다. door에는 mint, confirm, deny가 없다. door는 `auth::protect`로 감싸지 않고 owner 라우터에 merge하지 않는다 (`ember/server/src/enrol_door.rs:34-36`, 테스트 `ember/server/src/auth.rs:355-376`).
- confirm과 deny와 registrar는 owner 라우터에만 있다 (`ember/server/src/main.rs:491-497`). 따라서 도어에 접근하는 외부 기계는 컴퓨터를 직접 등록할 수 없다. 소유자의 confirm만이 등록으로 이어진다.
- transport는 `app`(enrol 라우트를 merge하기 전)을 서비스하고, enrol owner 라우트는 `local_app`에만 합쳐진다 (`ember/server/src/main.rs:467`, `:483-497`). 즉 transport로는 노출되지 않는다.
- 평문 HTTP: door는 TLS를 직접 하지 않는다. 비루프백 바인드는 `EMBER_ENROL_LISTEN_ALLOW_REMOTE=1`이 없으면 시작 오류이고 (`ember/server/src/door/config.rs` `DoorEnv::parse`), 켜면 경고를 로그한다 (`ember/server/src/main.rs:385-390`).

## 코드 흐름: mint, redeem, confirm 또는 deny, registrar

상태기계 (`ember/server/src/computers/enrol.rs:7-9`, 표 `State::TRANSITIONS` `:427`).

```text
waiting --redeem--> awaiting_confirmation --confirm--> confirmed --delivery--> joined
   |                    |    \--deny--> denied              \--lost or late--> expired
   \--code ttl--> expired \--deadline--> expired
```

1. **mint** (owner, `POST /api/computers/enrol-codes`): `mint` 핸들러 `enrol.rs:1468`. door가 `Off`면 409 `door_off`, `Unknown`이면 409 `door_url_unknown` (`:1470-1473`). `Enrol::mint` `:911`이 이름 검증(`check_name`), 기반 URL 검증(`check_base_url`), TTL(기본 10분, 상한 10분, 0은 거부)을 거쳐 `dpe_` + 244비트 코드를 만들고 SHA-256만 `enrol_codes`에 INSERT한다 (`:921-929`). 코드는 응답 한 번만 나가며 `Cache-Control: no-store`다 (`:1503`). 응답의 `command`는 `ember-node enrol <code> --server <door URL> [--server-fingerprint <64hex>]` 형식이다 (`:931-935`). mint 때 만료 후 `SWEEP_GRACE_MS`(1시간) 지난 행을 삭제한다 (`:922`).
2. **redeem** (door, `POST /enrol/redeem`): `enrol_door.rs` `redeem` 핸들러(`:355` 부근 `async fn redeem`). 순서: Content-Type 정확히 `application/json` 확인, `ConnectInfo` 없으면 500, `client_ip`로 실제 주소 결정, 본문 4,096바이트 상한, `deny_unknown_fields` 파싱(실패는 고정 문구 400), `Enrol::redeem` `enrol.rs:944`. `redeem`은 (a) 두 실패 한도기(출처별 + 전역) 검사, (b) `NodeInfo::validated`, (c) 코드 형태 검사(형태가 틀리면 SQLite를 조회하지 않고 같은 실패로 기록), (d) 단일 `UPDATE ... WHERE code_hash=? AND used_ms IS NULL AND state='waiting' AND expires_ms>? RETURNING id`로 승자 한 명만 `awaiting_confirmation`으로 보낸다 (`:960-977`). 응답은 `enrol_id`, `poll_secret`(1회), `expires_ms`. 이 시점에는 자격 증명이 없다.
3. **owner 확인**: 소유자는 `GET .../{id}`(`status_detail` `:1164`)로 노드가 보고한 `node_info`, `observed_addr`, `proposed_url`, `fingerprint`, `registered_by`를 본다. 이 값은 신뢰할 수 없는 표시 데이터이고 앱은 평문으로만 렌더해야 한다 (`enrol.rs:36-43`). `POST .../{id}/confirm` (`confirm` 핸들러 `:1527`, `Enrol::confirm` `:1213`) 또는 `POST .../{id}/deny` (`deny` `:1538`, `Enrol::deny` `:1287`).
4. **confirm 내부** (`Enrol::confirm`): gate 잠금 + `settle` -> 상태가 `awaiting_confirmation`이고 마감 전인지 확인 -> `expect_fingerprint` 정규화(16 hex) -> 이름 중복(`registrar.name_taken`) -> 노드 정보 복원 -> 지문 비교(`FingerprintMismatch`), 또는 peer 방식으로 등록될 때 지문 필수(`FingerprintRequired`) -> 토큰 `dpn_` 366비트 생성 -> `registrar.register` -> 토큰을 메모리 `pending`에 넣고 -> `transition(AwaitingConfirmation -> Confirmed)`. 기록 실패 시 `pending` 제거와 `registrar.remove`로 되돌린다 (`:1213-1280`).
5. **registrar** (`ComputersRegistrar` `enrol.rs:656`): `register_target` `:628`의 주소 규칙(1 `info.url`, 2 peer id + transport 켜짐, 3 peer id + transport 꺼짐은 관측 URL, 4 관측 URL 또는 오류), 서버 자신의 peer id를 주장하는 노드는 거부. `register`는 `Computers::register` 또는 `register_peer`를 호출하고 성공하면 상태를 한 번 비차단으로 조회한다 (`:684-706`). `name_taken`은 레지스트리를 못 읽으면 true(fail closed) (`:675-681`).
6. **전달** (door, `GET /enrol/status/{id}`, `poll` 핸들러): 순서는 verify -> limit -> deliver. `bearer`(Authorization 헤더만, 쿼리와 경로 불가) -> `Enrol::verify_poll` `:1324`(부수효과 없음) -> `PollLimiter::check_at`(id당 2초) -> `Enrol::take_delivery` `:1334`. `Confirmed`이면 `pending`에서 토큰을 꺼내 `Joined`로 전이하고 1회 반환, 토큰이 없으면 `Expired`로 전이한다. 이후 poll은 `delivered`.
7. **정리** (`settle` `:1061`): 모든 코어 호출 앞에서 시간 기반 만료를 처리한다. 확인됐지만 `DELIVERY_GRACE_MS`(10분) 안에 안 가져간 행, 또는 재시작으로 메모리 토큰이 사라진 `confirmed` 행은 `expired`가 되고 `reap`이 해당 컴퓨터를 레지스트리에서 제거한다 (`:1113`). `router()`가 시작 때 한 번 sweep한다 (`:1407-1413`).

## 공개 인터페이스

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

## 파일별 요약

### `ember/server/src/computers/enrol.rs` (3,281줄, 본체 약 1,543줄 + 테스트)
- 목적: enrol 코어, 상태기계, owner 라우트. 테스트 블록은 `:1545` 이후이고 `#[test]`/`#[tokio::test]` 81개.
- 주요 심볼

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `State::TRANSITIONS` | const | 427 | 허용 전이 표 전체. 그 밖의 이동은 `IllegalTransition` |
| `Enrol::redeem` | fn | 944 | 단일 UPDATE 승자 결정, 한도기와 형태 검사 포함 |
| `Enrol::settle` | fn | 1061 | 시간 만료, 재시작 손실 처리, `pending` 정리 |
| `Enrol::confirm` | fn | 1213 | 지문 검사, 토큰 생성, 등록, 전이, 롤백 |
| `Enrol::take_delivery` | fn | 1334 | 토큰 1회 전달 (상수 노력 비교) |
| `register_target` | fn | 628 | 노드 주소 결정 규칙 |
| `rate_limited`, `record_failure` | fn | 987, 1009 | 출처별(10회/60초) + 전역(60회/10분) 실패 한도 |
| `NodeInfo::validated` | fn | 317 | 길이 제한, 제어문자와 서식문자 제거 |
| `mint`, `status`, `cancel`, `confirm`, `deny` | async fn | 1468, 1507, 1511, 1527, 1538 | axum 핸들러 |
| `ApiError` | struct | 1422 | `EnrolError`를 HTTP 상태와 JSON으로 변환 |

- 의존: `Computers`, `Store`, `sha2`, `zeroize`, `crate::channels::invites::new_secret`.
- 부수효과: `enrol_codes` 테이블 쓰기, `pending` 토큰 메모리 맵, `Registrar` 통한 레지스트리 등록과 제거, 등록 직후 `tokio::spawn`으로 컴퓨터 상태 1회 조회 (`:696-704`).
- 비밀 취급: 코드와 poll secret은 SHA-256만 저장 (`:30-32`). `EnrolCode`, `Secret`, `Minted`, `Redeemed`, `Delivery`의 `Debug`는 가려져 있다 (`:216`, `:250`, `:266`). 노드 토큰은 SQLite에 열 자체가 없고 메모리에만 있다 (`:108-111` 주석). 레지스트리에는 평문으로 저장된다 (`:46-49`, bearer로 쓰이므로).
- 주의점: 재시작이 `confirmed`와 전달 사이에 일어나면 재시도 경로가 없다 (SPEC FR-C2d). 소유자는 컴퓨터를 지우고 새 코드를 발급해야 한다 (`:50-55`).

### `ember/server/src/enrol_door.rs` (740줄, 본체 약 572줄 + 테스트 `:573` 이후)
- 목적: enrol door 설정, 두 라우트, poll 한도기.
- 주요 심볼

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `EnrolDoor::from_env` / `from_lookup` | fn | 120, 127 | `EMBER_ENROL_*` 읽기. 오류는 시작 오류 |
| `EnrolDoor::routes_for`, `app` | fn | 164, 200 | 라우터와 방어 계층 조립 |
| `EnrolDoor::limits` | fn | 207 | enrol 전용 수치로 `DoorLimits::with_strict_path(.., ENROL_REDEEM_PATH)` |
| `EnrolDoor::door_url` | fn | 266 | mint이 인쇄할 URL (public URL, 아니면 특정 주소의 `http://listen`, 둘 다 아니면 `Unknown`) |
| `redeem` / `poll` | async fn | 450, 518 | 두 핸들러 |
| `PollLimiter::check_at` | fn | 318 | id당 2초, 최대 1,024개, 가득 차면 fail closed |
| `log_id` | fn | 356 | 로그에 찍는 id를 64자 영숫자로 정화 (FR-C2g) |
| `WarnOnce` | struct | 363 | 주소당 분당 1회만 warn 로그 |
| `bearer`, `is_json`, `is_length_limit` | fn | redeem 앞뒤 | 헤더 파싱, 타입 기반 길이 초과 판별 |

- 요청 계층 순서 (바깥부터, `door/harden.rs` `stack`): 응답 헤더, 한도(429/503), 타임아웃(408, 10초), guard(Host, Origin, 메서드, Content-Length), 본문 한도(4,096), 라우트, 404 폴백.
- 응답 매핑: redeem 성공 200 + `no-store`; `Refused::Generic` 403 `forbidden`; `RateLimited` 429 + `Retry-After: 60`; `BadNodeInfo` 400; 형식 불량 400 `bad_request`; 타입 불일치 415. poll은 잘못된 secret, 헤더 없음, 모르는 id, 내부 오류가 모두 같은 404 `not_found`다.
- 수치: redeem 분당 10, 시간당 30 (주소별, strict), 기타 분당 60, 전역 초당 5 버스트 10, 동시 8, 추적 주소 10,000, 연결 32, 헤더 읽기 10초 (`enrol_door.rs:83-99`).
- 사용처: `main.rs:259`, `:442`, `:549`. 테스트 `ember/server/tests/fr_c2_enrol_door.rs` 등.

### `ember/server/src/door/` (공용 가드, 5개 파일 683줄)
| 파일 | 줄 | 설명 |
|---|---|---|
| `door/mod.rs` (25) | | 모듈 선언, `DoorError`, `err`. 주석에 guest door에서 이동했다고 적힘 |
| `door/config.rs` (118) | | `parse_public_url`, `listen_clash`, `Spec`, `DoorEnv::parse`. 검사 순서: 주소 문법, 다른 리스너와 충돌, 원격 허용 변수, 신뢰 프록시, public URL. `Host` 허용 목록은 listen IP, `localhost`(루프백일 때), `*_ALLOWED_HOSTS`, public URL host |
| `door/harden.rs` (149) | | `stack`(계층 순서를 한 함수에 고정), `with_timeout`, `guard_layer`(Host 필수, Origin 규칙, HEAD/TRACE/CONNECT 405, Content-Length 413, Upgrade 400), `response_headers`(nosniff, no-store), `not_found` |
| `door/limits.rs` (324) | | `client_ip`(신뢰 프록시일 때만 `X-Forwarded-For`를 오른쪽에서부터 해석), `TokenBucket`, `AddrLimiter`, `LimitConfig`, `DoorLimits::new`(guest 전용)와 `with_strict_path`, `limit_layer` |
| `door/serve.rs` (67) | | `serve_capped`: 연결 수 세마포어, 헤더 읽기 타임아웃, `ConnectInfo` 삽입, graceful shutdown, accept 오류 시 100ms 대기 후 계속 |

- 사용처: `guest_door.rs:44-49`와 `enrol_door.rs`. `LimitConfig`는 두 번째 공개 경로가 `enrol_door`와 `guest_door`에서 재내보내기된다.
- 주의점: `door/limits.rs:15-18`이 `crate::guest_door` 상수(`ACCEPT_PATH`, 수치들)를 import한다. 즉 "공용"이지만 guest door에 의존하며, `LimitConfig::default`와 `DoorLimits::new`는 guest 전용이다. enrol door는 반드시 `with_strict_path`와 필드별 `LimitConfig`를 써야 한다 (`door/mod.rs:5-8`).

## 동작 지도

### owner 로컬 라우터 (`auth::protect` 안)
| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `POST /api/computers/enrol-codes` | `mint` `enrol.rs:1468` | `Enrol::mint` `:911` | `enrol_codes` INSERT |
| `GET /api/computers/enrol-codes/{id}` | `status` `:1507` | `Enrol::status_detail` `:1164` | `enrol_codes` 읽기 |
| `DELETE /api/computers/enrol-codes/{id}` | `cancel` `:1511` | `Enrol::cancel` `:1368` (미사용 코드만 삭제) | DELETE |
| `POST .../{id}/confirm` | `confirm` `:1527` | `Enrol::confirm` `:1213` | 상태 전이, 레지스트리 등록, `pending` |
| `POST .../{id}/deny` | `deny` `:1538` | `Enrol::deny` `:1287` | 상태 전이 |

### enrol door (별도 리스너, 토큰 없음)
| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `POST /enrol/redeem` | `redeem` `enrol_door.rs` | `Enrol::redeem` `enrol.rs:944` | `enrol_codes` UPDATE |
| `GET /enrol/status/{enrol_id}` | `poll` `enrol_door.rs` | `verify_poll` `:1324`, `take_delivery` `:1334` | 상태 전이, `pending` 소비 |
| 그 밖의 모든 경로와 메서드 | `not_found` | | 빈 본문 404 |

### 사용자에게 보이는 에러 메시지
| 원문 | 위치 | 조건 |
|---|---|---|
| `this enrol code cannot be used` | `enrol.rs:167` | 알 수 없음, 사용됨, 만료, 취소, 형식 불량 코드 (모두 동일 문구) |
| `too many attempts, try again later` | `enrol.rs:169` | 실패 한도 초과 (429) |
| `invalid node information` | `enrol.rs:171` | `NodeInfo` 검증 실패 (400) |
| `The enrol door is off: set EMBER_ENROL_LISTEN (and EMBER_ENROL_PUBLIC_URL) and restart` | `enrol.rs:570` `DoorOff` | door 꺼짐, mint 409 |
| `Set EMBER_ENROL_PUBLIC_URL to the address the other machine uses` | `DoorUrlUnknown` | 0.0.0.0 바인드에 public URL 없음 |
| `The fingerprint does not match the one the other machine reported; nothing was registered` | `FingerprintMismatch` | confirm 409 |
| `This computer is registered by its peer id; confirm with expect_fingerprint set ...` | `FingerprintRequired` | peer 방식인데 지문 미제공 |
| `a computer named {0:?} already exists; choose another name` | `NameTaken` | 이름 충돌, 상태 유지 |
| `enrolment {id} is {state}, not awaiting confirmation` / `enrolment {0} has expired` | `WrongState`, `Expired` | 409 / 410 |
| `The code is shown once. Check that {door_url} is reachable ...` + HTTP 경고 문구 | `enrol.rs:1480-1487` | mint 응답의 `warning` |

## 데이터와 설정

- DB 테이블: `enrol_codes` (id, code_hash BLOB UNIQUE, name, created_ms, expires_ms, used_ms, computer_id + state, poll_hash, node_info, observed_addr, confirm_deadline_ms, confirmed_ms, delivered_ms, denied_ms, final_name) `enrol.rs:89-121`. 노드 토큰 열은 없다.
- 메모리: `Enrol::pending` (enrol id -> 토큰), 출처별 실패 큐, 전역 실패 큐, door의 `PollLimiter`와 `WarnOnce`.

| 환경 변수 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_ENROL_LISTEN` | `enrol_door.rs:54` | door 바인드 `ip:port` | 꺼짐 |
| `EMBER_ENROL_LISTEN_ALLOW_REMOTE` | `enrol_door.rs:55` | `1`이면 비루프백 허용 | 거부 |
| `EMBER_ENROL_TRUSTED_PROXIES` | `enrol_door.rs:56` | `X-Forwarded-For` 신뢰 프록시 IP 목록 | 없음 |
| `EMBER_ENROL_ALLOWED_HOSTS` | `enrol_door.rs:57` | 허용 Host 이름 | 없음 |
| `EMBER_ENROL_PUBLIC_URL` | `enrol_door.rs:58` | 노드에 알려줄 URL, 호스트는 Host 허용 | 없음 |

- 외부 연동: 노드 쪽 클라이언트 `ember/node/src/enrol_cli.rs:843` (redeem), `:875` (poll).

## 이 모듈을 수정할 때 주의할 점

- 보안 불변식: (1) 코드와 poll secret은 해시로만 저장, (2) 토큰은 메모리에만, (3) 코어 호출은 항상 `gate`와 `settle`을 먼저, (4) 거부 이유를 구분해 노출하지 않음 (코드, poll 모두 단일 응답), (5) poll 순서 verify -> limit -> deliver, (6) 로그에는 `log_id`를 거친 id만. 하나라도 깨면 `fr_c2_*` 테스트가 잡도록 되어 있으니 테스트를 먼저 읽는다.
- 상태 추가는 `State::TRANSITIONS`, `settle`, `Delivery`, `EnrolStatus`, door `poll`의 `match`를 모두 고쳐야 한다.
- 수치 변경은 `ENROL_*` 상수와 문서 `docs/design/COMPUTERS.md`, SPEC FR-C2f 동시 수정. 주석은 "leader decision 2026-11-06, adjustable"이라고 적는다.
- `door/` 변경은 guest door 특성화 테스트 (`ember/server/tests/fr_t14_guest_limits.rs`, `fr_t14_guest_door_characterization.rs`)에 영향을 준다 (`door/serve.rs:3-4`).
- 마이그레이션은 `store::MIGRATIONS` 25, 26번 자리에 고정이다. 순서를 바꾸지 않는다.
- 새 owner 라우트는 `computers::enrol::router`에, 새 door 라우트는 `EnrolDoor::routes_with`에만 추가하고, door에 owner 동작(confirm 등)을 두지 않는다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 중간 | `door/config.rs` `DoorEnv::parse`, `main.rs:385-390` | door가 평문 HTTP이고, 원격 허용 시 코드와 자격 증명이 평문으로 지나간다. 경고만 있고 TLS 종단은 소유자 몫 | 문서화 유지. TLS 앞단 권장을 mint 경고에 이미 있음 (`enrol.rs:1481-1486`) |
| 보안 | 중간 | `enrol.rs:46-49` | 노드 토큰이 레지스트리에 평문 저장 (bearer로 쓰기 위함) | 레지스트리 암호화 여부는 [server-computers](server-computers.md) 참조 [확인 필요] |
| 보안 | 낮음 | `enrol_door.rs` `PollLimiter` 문서 | 잘못된 secret의 poll은 id별 한도가 없고 주소별과 전역 한도에만 묶인다 (문서가 인정한 잔여 위험) | 현 상태 유지 가능 |
| 구조 | 중간 | `door/limits.rs:15-18` | "공용" 모듈이 `crate::guest_door` 상수에 의존, 순환 구조 | 상수를 `door/`로 이동 (`docs/analysis/_raw/cycles.md` 참고) |
| 구조 | 중간 | `computers/enrol.rs` (3,281줄) | 코어, 라우트, 레지스트리 어댑터, 테스트 약 1,700줄이 한 파일 | 테스트를 `tests/`나 하위 모듈로 분리 |
| 하드코딩 | 낮음 | `enrol.rs:162` | `PROPOSED_NODE_PORT = 8741` | 설정화 검토 |
| 하드코딩 | 낮음 | `enrol_door.rs:83-99` | 한도 수치 전부 상수, 주석상 "adjustable" | 운영 설정이 필요하면 환경 변수화 |
| 중복 | 낮음 | `enrol.rs:60-75`과 `door/limits.rs` | 실패 한도기와 주소 한도기가 비슷한 개념을 두 곳에서 따로 구현 (목적은 다름: redeem 실패 대 요청 수) | 의도된 이중 방어로 보이나 [확인 필요] |
| TODO/FIXME | | 7개 파일 | 0개 | |
| 테스트 | | `enrol.rs` 81개, `enrol_door.rs` 8개 (`#[test]` 계열) | 통합 테스트는 `ember/server/tests/fr_c1_enrol.rs`, `fr_c2_enrol_*.rs` | |
