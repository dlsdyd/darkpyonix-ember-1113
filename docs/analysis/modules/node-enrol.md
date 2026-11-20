# 모듈: node-enrol

- 경로: `ember/node/src/enrol.rs`, `ember/node/src/enrol_cli.rs`
- 규모: 파일 2개 / 약 2,966줄 (각각 테스트가 큰 비중: `enrol.rs` 약 670줄까지가 본문, 나머지 테스트 47개 / `enrol_cli.rs` 약 1,055줄까지가 본문, 테스트 25개)
- 레이어: 인프라 (노드를 ember 서버에 등록하는 일회성 CLI와 그 결과물 저장)
- 한 줄 책임: `ember-node enrol <code> --server <url>`로 서버의 enrol 문에서 일회용 코드를 교환하고, 소유자 승인을 기다려 서버가 발급한 노드 토큰을 `<state dir>/enrol.json`에 안전하게(원자적, 0600, 잠금) 저장하며, 서버를 신뢰하기로 한 경우에만 서버의 peer id를 `allowed-peers`에 추가한다 (SPEC FR-C2h).
- 의존하는 모듈: [node](node.md) (`crate::transport::{parse_peer_list, allowed_peers_file, TransportMode, ALLOWED_PEERS_FILE}`: `ember/node/src/enrol.rs:283-290`, `ember/node/src/enrol.rs:580-`, `ember/node/src/enrol_cli.rs:692-698`; `crate::config::default_state_dir`: `enrol_cli.rs:693`), 외부 `ember_transport::PeerId`, `reqwest`
- 이 모듈을 쓰는 모듈: [node](node.md)의 `config.rs`가 `enrol::read_enrolment`와 `ENROL_FILE`로 토큰을 읽는다 (`ember/node/src/config.rs:63`, `:108`). `main.rs`가 `enrol` 하위 명령을 `enrol_cli::cli`로 보낸다 (`ember/node/src/main.rs`, 하위 명령 분기). 서버 쪽 통합 테스트가 `ember/server/tests/fr_c2_enrol_node.rs`에서 CLI를 검증한다. 서버의 enrol 문은 `ember/server/src/enrol_door.rs`, `ember/server/src/computers/enrol.rs` ([server-computers](server-computers.md), [server-core](server-core.md)).

## 공개 인터페이스

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

## 파일별 요약

### `ember/node/src/enrol.rs` (1,436줄, 본문 약 670줄 + 테스트 47개)
- 목적: 노드가 등록 후 보관하는 것의 저장소 (N1). 읽기, 검증, 쓰기만 담당하고 자격 증명을 가져오는 일은 `enrol_cli`가 한다. 유닉스 전용이다 (자격 증명 파일 보호가 0600과 소유자 검사에 의존, Windows ACL 처리 없음, 머리 주석).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `MAX_FILE_BYTES`, `MAX_TOKEN_CHARS` | const | 27, 28 | 파일 64 KiB, 토큰 512자 상한 |
| `open_regular_owned` | fn | 62 (unix) / 76 | 심볼릭 링크, 일반 파일 아님, 다른 사용자 소유 파일을 거부하고 연다 |
| `read_capped` | fn | 92 | 상한 안에서만 읽는다 |
| `lock_state_dir` | fn | 133 (unix) / 168 | 잠금 파일은 `O_NOFOLLOW`, 0600, 일반 파일, 소유자 확인. NFS에서는 `flock`이 권고 수준일 수 있다 (문서 주석). 읽는 쪽(`read_enrolment`)은 잠금을 잡지 않는다: 교체가 `rename` 한 번이라 완전한 옛 파일이나 새 파일만 보인다 |
| `Enrolment`, `validate` | struct/fn | 207, 239 | 토큰은 비어 있지 않고 512자 이하, 인쇄 가능 ASCII(공백 제외). `server_peer_id`는 소문자 hex 64자 |
| `read_enrolment` | fn | 257 | 오류 문구는 파일 이름만 말하고 내용을 인용하지 않는다 (serde 오류는 일부러 버림, 273 부근). 그룹/기타가 읽을 수 있으면 경고만 (`chmod 600` 권고) |
| `append_allowed_peer` | fn | 283 | 이미 있으면 `Ok(None)`. 기존 텍스트가 파싱 안 되면 덮어쓰지 않고 오류 |
| `stage_file`, `stage_retry`, `commit`, `put_back` | fn | 373, 399, 463, 424 | 임시 파일에 먼저 쓰고 rename으로 커밋, 실패 시 롤백 (`put_back`). 순서: `enrol.json`이 먼저. 토큰 없는 peer는 해롭고 peer 없는 토큰은 무해하기 때문 (`write_enrolment` 문서 주석) |
| `write_enrolment` | fn | 501 | `write_with`(510)로 `prepare`(625)와 `commit`을 호출 |
| `preflight` | fn | 580 | `--replace`면 기존 `enrol.json`을 읽을 수 있는지, `allowed-peers`가 파싱되는지, 상태 디렉터리에 쓸 수 있는지(임시 파일 생성 시도)를 코드 교환 전에 확인 |
- 부수효과: 상태 디렉터리에 `enrol.json`(0600), `allowed-peers`(기존 모드 유지), `.enrol.lock`, 임시 파일을 만든다. 상태 디렉터리가 내 소유가 아니거나 그룹/기타가 쓸 수 있으면 경고만 한다 (`warn_state_dir`, 47).
- 사용처: `config.rs`(토큰 읽기), `enrol_cli.rs`.

### `ember/node/src/enrol_cli.rs` (1,530줄, 본문 약 1,055줄 + 테스트 25개)
- 목적: `ember-node enrol <code|-> --server <url> ...` (FR-C2h, N2, 머리 주석에 [provisional]). 서버 enrol 문에서 코드를 교환하고, 소유자 승인을 기다리고, 신뢰 결정(INTENT D39 R1-R4)을 한 뒤 쓴다.
- 머리 주석의 규칙(모든 경로에 적용): 신뢰 결정 전에는 아무것도 쓰지 않고 중단하면 아무것도 남기지 않는다. 코드, poll secret, 노드 토큰은 `EnrolIo::say`, `tracing`, 오류 문구에 넣지 않고 응답 본문은 인용하지 않는다. `reqwest` 클라이언트는 리다이렉트 없음, 프록시 없음, 요청 타임아웃, 본문 상한 `MAX_BODY_BYTES` 64 KiB. 상태 디렉터리는 첫 요청 전에 잠근다. 서버 이름은 이 프로그램이 해석하지 않는다.
- 주의: 머리 주석은 N2b(preflight, 폴링 루프의 Ctrl-C 처리, NotSynced 출력, 도움말, `ember/server/tests/fr_c2_enrol_node.rs`의 새 테스트)가 "작성됐으나 아직 컴파일되지 않았다"고 적고 있다 (`enrol_cli.rs:10-12`). 이 분석 시점의 상태는 확인하지 않았다 [확인 필요].

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Options` | struct | 103 | `code`(비밀, 출력 금지), `server`, `pin`, `trust_unverified`, `url`, `transport`, `state_dir`, `yes`, `allow_http`, `replace`, 폴링 간격 2초, 마감, HTTP 타임아웃 15초 (`Debug`는 비밀을 가림, 130) |
| `parse_args` | fn | 172 | 옵션: `--server`, `--server-fingerprint`, `--trust-unverified-server`, `--url`, `--transport`, `--state-dir`, `--yes`, `--allow-http`, `--replace`. 코드가 `-`면 stdin 한 줄 |
| `classify_server_url` | fn | 338 | URL 형식을 엄격히 검사: `http(s)://`만, 사용자 정보/쿼리/프래그먼트/경로/역슬래시/공백/제어 문자 금지, 최대 256자. 사설 주소와 loopback을 판별 |
| `check_transport_policy` | fn | 379 | 공개 주소에 대한 평문 HTTP는 `--allow-http` 없이는 거부 (코드 교환 전) |
| `parse_pin`, `check_pin` | fn | 395, 428 | `--server-fingerprint`: 64 hex 전체 또는 16 hex 짧은 형 |
| `decide_trust` | fn | 461 | R1-R4. pin 일치면 신뢰, 불일치/서버가 id를 안 줌이면 중단. pin이 없으면 대화형이고 `--yes`가 아닐 때만 묻고, 비대화형이거나 `--yes`면 `--trust-unverified-server`일 때만 신뢰. `--yes`는 "Continue?"에만 답하고 신뢰를 주지 않는다 |
| `strip_display` | fn | 501 | 서버가 준 이름의 제어/비가시 문자를 제거해 출력 |
| `poll_once`, `read_capped` | fn | 628, 583 | 폴링 한 번, 응답 크기 상한 읽기 |
| `run` | fn | 753 | 전체 흐름, 아래 단계 |
| `Signals` | struct | 709 | SIGINT/SIGTERM/SIGHUP을 코드 소비 전에 등록 |

`run`의 단계 (`enrol_cli.rs:753-1054`의 주석 번호):
1. 인자 검증 (파일, 네트워크 접근 전). 2. 서버, TLS 여부, "This node will accept commands from this server." 출력, 평문 HTTP 경고, "Continue?" 확인. 3. 상태 디렉터리 잠금, 기존 `enrol.json`이 있으면 `--replace` 없이는 거부, `preflight`. 4. 노드 정보 구성. 5. `POST <server>/enrol/redeem` (본문 `code`, `node_public_info`; 403은 `REFUSED_TEXT`, 429는 `too many attempts, wait and try again`). 6. `GET <server>/enrol/status/<enrol_id>`를 폴링 (`enrol_cli.rs:875`), 상태 `denied`/`expired`/`delivered` 처리, 연속 네트워크 오류 5회면 포기 (`MAX_NET_ERRORS`, 45). 7. 신뢰 결정, 자격 증명 형식 검증. 8. `write_enrolment`, 결과 안내.
- 신호 처리: 코드를 소비하기 전에 신호 리스너를 등록하므로 교환 요청과 폴링 중 신호는 아무것도 쓰지 않는 깨끗한 종료가 된다. 자격 증명이 도착한 뒤에는 쓰는 도중에 프로세스가 죽어 토큰을 잃지 않도록 신호를 읽지 않는다. 그래서 지문 질문에는 Ctrl-C 대신 `n`, Enter, Ctrl-D로 답한다 (`FINGERPRINT_PROMPT`).
- 부수효과: 네트워크 요청(서버 enrol 문), 상태 디렉터리 쓰기. `--transport`이면 노드의 transport 키도 만들 수 있다 (`run` 위 문서 주석).
- 사용처: `main.rs`(`enrol` 하위 명령), 서버 통합 테스트.

## 동작 지도

HTTP 라우트는 없다 (노드 API에 등록되지 않는다). 대신 CLI 동작과 호출하는 서버 엔드포인트를 적는다.

| 동작 | 핸들러 `경로:줄` | 서비스 함수 `경로:줄` | 데이터 |
|---|---|---|---|
| `ember-node enrol ...` | `ember/node/src/main.rs` (`enrol` 분기) -> `enrol_cli::cli` `enrol_cli.rs:692` | `run` `enrol_cli.rs:753`, `write_enrolment` `enrol.rs:501` | `<state>/enrol.json`, `<state>/allowed-peers`, `.enrol.lock` |
| 코드 교환 | `run` 5단계 | `POST /enrol/redeem` (서버 `ember/server/src/enrol_door.rs`) | 코드(비밀), `poll_secret` |
| 승인 대기 | `run` 6단계 `enrol_cli.rs:875` | `GET /enrol/status/{id}` + `poll_once` `enrol_cli.rs:628` | 상태, 자격 증명(전달 시 1회) |
| 데몬 기동 시 토큰 읽기 | `config.rs:104` `token_with_source` | `read_enrolment` `enrol.rs:257` | `enrol.json`의 `node_token` |

### 사용자에게 보이는 에러 메시지 (주요)

| 원문 | 위치 | 조건 |
|---|---|---|
| `this enrol code cannot be used` | `enrol_cli.rs:91` | 서버가 코드를 거부 (이유를 구분하지 않는 단일 문구) |
| `too many attempts, wait and try again` | `enrol_cli.rs:92` | 429 |
| `timed out waiting for the owner` | `enrol_cli.rs:93` | 마감 초과 |
| `plain HTTP to a public address is refused; use an https address, or pass --allow-http` | `enrol_cli.rs:381` | 공개 주소에 평문 HTTP |
| `interrupted; nothing was written on this node. The code may already have been redeemed: ...` | `enrol_cli.rs:96` | 교환 후 폴링 중 신호 |
| `cancelled; nothing was changed` | `enrol_cli.rs` `run` 2단계 | "Continue?"에 거절 |
| `<path> already exists; pass --replace to replace it` | `enrol_cli.rs` `run` 3단계 | 기존 `enrol.json` |
| `the owner denied this computer`, `the enrolment expired before the owner confirmed it` | `enrol_cli.rs` `run` 6단계 | 폴링 결과 |
| `the server sent an invalid credential (<e>); nothing was written` | `enrol_cli.rs` `run` 7단계 | 형식 검증 실패 |
| `<path> is malformed (not a valid enrolment file; line N, column M)` | `enrol.rs:274` 부근 | `enrol.json` 파싱 실패 (값 인용 없음) |
| `the node token is empty` / `... longer than 512 characters` / `must be printable ASCII without spaces` | `enrol.rs:240-246` | 토큰 검증 실패 |
| `the state directory <dir> is not writable; fix its permissions, then run enrol again (nothing was redeemed)` | `enrol.rs` `preflight` | 쓰기 불가 |
| `Warning: this adds an unverified server to this node's allowed peers; ...` | `enrol_cli.rs:97` | `--trust-unverified-server` |
| `usage: ember-node enrol <code|-> --server <url> [--server-fingerprint <id>] ...` | `enrol_cli.rs:59` | 인자 오류 |

## 데이터와 설정

- 파일 (`<state dir>`, 기본 `$HOME/.ember/node`): `enrol.json`(0600, 비밀 `node_token` = `***`), `allowed-peers`(한 줄에 peer id 하나, 기존 모드 유지), `.enrol.lock`(0600), 쓰는 동안의 임시 파일.
- `enrol.json` 필드: `server`, `node_token`, `server_peer_id`(선택), `name`, `computer_id`, `enrolled_ms` (`enrol.rs:207-220`).
- 상수: 본문 상한 64 KiB (`enrol_cli.rs:35`), URL 최대 256자 (37), 폴링 간격 2초 (39), HTTP 타임아웃 15초 (41), 최대 폴링 지연 30초 (43), 연속 네트워크 오류 5회 (45), 마감 유예 30초 (47), 대기 시간 하한/상한 1분/15분 (50, 51).
- 환경 변수: `EMBER_NODE_STATE_DIR`(기본 상태 디렉터리, `config::default_state_dir`), `EMBER_NODE_TRANSPORT`(켜져 있으면 `--transport` 효과, `enrol_cli.rs:694`). `EMBER_NODE_TOKEN`이 있으면 `enrol.json`보다 우선하며 노드가 그 사실을 로그로 알린다 (`config.rs:62-65`).
- 외부 연동: ember 서버 enrol 문 (`/enrol/redeem`, `/enrol/status/{id}`), 코드는 일회용이며 10분 후 만료 (`USAGE` 문구, 62-63).

## 이 모듈을 수정할 때 주의할 점

- `Enrolment` 필드를 바꾸면 `config.rs`의 토큰 읽기, 서버 쪽 enrol 문(`ember/server/src/enrol_door.rs`)이 보내는 `credential`, `ember/server/tests/fr_c2_enrol_node.rs`를 함께 고친다. 파일 형식은 기존 설치와 호환되어야 한다 (선택 필드에 `serde(default)`).
- 서버는 자격 증명을 한 번만 넘기고 지운다. 전달 뒤 쓰기가 실패하면 토큰을 잃는다. 그래서 `preflight`가 쓰기 실패 조건을 코드 교환 전에 거른다. `write_enrolment`가 거부할 조건을 추가하면 `preflight`에도 같은 검사를 넣어 둘이 어긋나지 않게 한다 (`enrol.rs` `read_previous_enrol` 주석).
- 쓰기 순서(`enrol.json` 먼저, `allowed-peers` 나중)와 롤백(`put_back`)을 바꾸지 않는다.
- 비밀(코드, poll secret, 노드 토큰)을 `say`, `tracing`, 오류 문구, `Debug`에 넣지 않는다. 테스트 `fr_c2_node_cli_run_does_not_say_the_code`가 일부를 지킨다 (`enrol_cli.rs:1470`).
- 신뢰 결정(`decide_trust`)은 INTENT D39 R1-R4를 구현한다. `--yes`가 신뢰를 주도록 바꾸면 보안 모델이 깨진다.
- 유닉스 전용 가정(0600, `flock`, 소유자 검사)이 있다. Windows에서는 `euid()`가 0을 돌려주고 (`enrol.rs:51-53`) 비 unix `lock_state_dir`(168)가 따로 있어 보호 수준이 다르다.

## 이슈 후보

TODO/FIXME는 두 파일에서 0개 (grep 확인).

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 정확성 | 중간 | `ember/node/src/enrol_cli.rs:10-12` | 머리 주석이 N2b가 "작성됐으나 컴파일되지 않았다"고 적고 있다. 현재 상태와 어긋나는 낡은 주석일 수 있다 [확인 필요] | CI 결과를 확인하고 주석 갱신 |
| 보안 | 중간 | `ember/node/src/enrol_cli.rs:75`, `:379-383` | `--allow-http`나 사설/`.local` 주소에서는 평문 HTTP로 코드, poll secret, 자격 증명이 오간다. 경고는 출력하지만 막지는 않는다 | 의도된 동작. 문서에서 https 권장 유지 |
| 보안 | 낮음 | `ember/node/src/enrol_cli.rs:59-66` | 코드를 인자로 주면 `ps`와 셸 기록에 남는다 (일회용, 10분 만료). `-`(stdin)을 쓰도록 `USAGE`가 안내한다 | 이미 완화됨 |
| 보안 | 낮음 | `ember/node/src/enrol_cli.rs:97` | `--trust-unverified-server`는 서버 id를 확인 없이 `allowed-peers`에 넣는다. NAT를 넘는 transport라 가짜 서버가 어디서든 접근할 수 있다 | 경고가 이미 있음 |
| 이식성 | 낮음 | `ember/node/src/enrol.rs:7-8`, `:51-53`, `:168` | 유닉스 전용 보호 모델. Windows 노드의 enrol 보호 수준이 낮다 | 한계로 문서화 [확인 필요: Windows 지원 범위] |
| 구조 | 낮음 | `ember/node/src/enrol_cli.rs` `run` (753-1054, 약 300줄) | 한 함수에 8단계가 모여 있다 | 단계별 함수로 분리 고려 |
| 견고성 | 낮음 | `ember/node/src/enrol.rs:133-190` | `flock`은 NFS에서 권고 수준일 수 있다 (문서 주석에 명시) | 한계로 문서화 |
