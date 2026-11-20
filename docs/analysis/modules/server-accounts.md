# 모듈: server-accounts

- 경로: `ember/server/src/accounts/`, `ember/server/src/chatgpt/`, `ember/server/src/schedules/`, `ember/server/src/transfers.rs`, `ember/server/src/usage.rs`
- 규모: 파일 17개 / 약 6,665줄 (테스트 블록 포함)
- 레이어: 비즈니스 로직 (+ 각 하위 영역의 HTTP 라우터)
- 한 줄 책임: 에이전트별 다중 계정과 라우팅, API 키와 ChatGPT 토큰의 암호화 저장, Sign in with ChatGPT(OAuth), 예약 작업(스케줄러), 파일 전송 서버 매니저, 토큰 사용량 집계를 맡는다.
- 의존하는 모듈: [server-core](server-core.md) (`Store`, `Sessions`, `events`, 마이그레이션 번호), [server-collab](server-collab.md) (`a2a::A2a` 런타임 토큰 인증), [server-computers](server-computers.md) (`Computers`, `transfers.rs`와 스케줄러의 컴퓨터 배치), [transfer](transfer.md) (`ember_transfer`: 이름 정리, 크기 제한, 수신 모드), [transport](transport.md) (`PeerId`), [server-api](server-api.md) (`api/mod.rs`가 `usage.rs`를 호출)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs`가 조립, `store.rs:137` 등 마이그레이션 상수, `session.rs`의 계정 라우터 훅), [server-api](server-api.md) (`api/mod.rs:91-92`, `:358-367`), [client](client.md) (`/api/accounts`, `/api/chatgpt`, `/api/schedules`, `/api/transfers` 호출)

## 하위 영역과 보안 요약

| 영역 | 파일 | 한 줄 |
|---|---|---|
| 계정/키 | `accounts/*` | 에이전트 CLI 설정 디렉터리를 계정별로 격리, 라우팅, API 키 암호화 |
| ChatGPT | `chatgpt/*` | Sign in with ChatGPT. `EMBER_HOSTED=1`이면 전부 꺼짐 |
| 스케줄 | `schedules/*` | cron, 간격, 1회 예약 프롬프트 실행 |
| 전송 | `transfers.rs` | 서버 측 파일 전송 상태와 `/api/transfers*` |
| 사용량 | `usage.rs` | `events` 테이블 위의 토큰 집계 질의 |

- 인증: 이 모듈의 라우터는 모두 `main.rs`에서 `app`에 merge되어 (`ember/server/src/main.rs:454-463`) 로컬 토큰 보호(`auth::protect`)를 받고, transport 쪽 `app`에도 실린다. 예외는 `GET /auth/callback`(토큰 면제, `ember/server/src/auth.rs:199-203`)과 `/api/a2a/*`(`/api/a2a/settings` 제외, 런타임 토큰을 핸들러가 직접 검사, `auth.rs:212`)이다. 스케줄 에이전트 라우트가 후자다 (`ember/server/src/schedules/api.rs:148-157`).

## 자격 증명과 키 처리 (accounts/secrets.rs)

- 암호: XChaCha20-Poly1305 (`chacha20poly1305`), 암호화마다 OS RNG로 새 24바이트 nonce (`ember/server/src/accounts/secrets.rs:89-101`). 키 값은 문서와 로그에 적지 않는다.
- 키 파일: `<data dir>/secret.key`, 32바이트. `SecretBox::open_or_create` (`secrets.rs:48`)는 `create_new` + 모드 `0600`으로 만들고 (경쟁 시 한 서버만 만듦), 이미 있으면 `check_private`로 그룹/기타 읽기 권한이 있으면 시작을 거부하고 (`:146-157`) 길이가 정확히 32바이트가 아니면 오류 (`:70`의 `ensure!`).
- AAD 바인딩: API 키는 `ember/api-provider-key/v1:<provider id>` (`secrets.rs:39`, `:189`), ChatGPT 토큰은 `ember/chatgpt-tokens/v1:<account id>` (`ember/server/src/chatgpt/store.rs:15`). 다른 행에 복사한 암호문은 복호화에 실패한다.
- 평문 보호: `ApiKey`는 `Zeroizing`, 가려진 `Debug`, `Serialize` 없음 (`secrets.rs:164-175`). `ApiProvider`(목록과 생성 응답)에는 키 조각조차 없다 (`:180`). ChatGPT `Tokens`도 같다 (`chatgpt/store.rs:49-60`).
- 경계: DB만으로는 키를 알 수 없고 DB + `secret.key`가 필요하다. `ember.db` 복사본(백업, 내보내기)을 보호하는 것이 목적이고, 서버 계정이 침해된 경우는 막지 않는다 (`secrets.rs:15-18`).
- 에이전트 로그인 자격은 Ember가 저장하지 않는다. 계정은 디렉터리 `<data dir>/accounts/<id>`(unix에서 0700)를 만들고, 에이전트 CLI가 자기 환경 변수(`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `ember/server/src/accounts/mod.rs:70`)로 거기에 로그인 정보를 둔다. 로그인은 자동화하지 않고 `login_instructions`(`mod.rs:359`)가 사용자가 서버에서 실행할 명령을 돌려준다.

## 계정 라우팅 (accounts/mod.rs)

- 세션 시작 훅 `install` (`mod.rs:208`)이 세션 기록에 계정이 있으면 `config_env_var(agent)=<계정 디렉터리>`를 에이전트 프로세스 환경에 추가한다. 행이 사라졌어도 id에서 디렉터리를 유도해 다른 로그인으로 조용히 돌아가지 않게 한다 (`dir_of` `:236`).
- `route` (`mod.rs:508`): 요청된 계정이 있으면 그대로 사용(에이전트 불일치는 오류, 한도 걸림은 경고를 이유에 추가). 없으면 해당 에이전트 계정 중 한도 안 걸리고 `logged_out`이 아닌 것에서 `(오늘 토큰 수, 기본 계정 우선, 생성 순)`으로 정렬해 첫 번째 선택 (`:545-548`). 계정이 아예 없으면 `None`(서버 자신의 로그인), 있는데 가용 계정이 없으면 폴백 없이 오류 (`:549-555`).
- 한도 감지 `on_event` (`mod.rs:572`): `RateLimited`(구조화 신호)는 `resets_at` 또는 1시간(`DEFAULT_COOLDOWN_MS` `:66`) 후까지 한도 설정, `Error` 메시지는 `limit_in_message`(`:629`) 패턴으로 판별(구조화 신호가 이미 있으면 덮어쓰지 않음), 한도 중인 계정의 `TurnEnded{Completed}`는 한도 해제.
- `check_login` (`mod.rs:411`): `claude auth status --json` 또는 `codex login status`를 20초 제한으로 실행해 `logged_in`/`logged_out` 갱신. Scripted는 항상 `logged_in`, Antigravity와 ACP는 `unknown`. Antigravity 계정 생성은 거부 (`create` `:243-248`).
- `install`은 `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CODEX_API_KEY`가 서버 환경에 있으면 계정 격리를 무력화할 수 있다고 경고한다 (`mod.rs:209-217`).

## 공개 인터페이스

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
| 마이그레이션 | const | `accounts/schema.rs:4` (2번), `chatgpt/schema.rs` (4번), `schedules/schema.rs:13` (12번) | 스키마 |

## 파일별 요약

### `ember/server/src/accounts/mod.rs` (996줄, 테스트 `:718` 이후, 8개)
- 목적: 계정 CRUD, 라우팅, 한도 추적, 로그인 점검, 사용량 병합.
- 주요 심볼: `Account` `:86`, `AccountError` `:129`, `Accounts::route` `:508`, `on_event` `:572`, `limit_in_message` `:629`, `format_utc` `:667`, `usage_since` `:461` (ChatGPT 계정의 일별 사용량을 `chatgpt::store::usage_since`로 합침 `:486`), `tokens_today` `:492`, `delete` `:283` (세션이 쓰는 계정은 409 `Conflict`, 디렉터리는 루트 아래일 때만 삭제 `:305-308`).
- 부수효과: `accounts` 테이블, 계정 디렉터리 생성과 삭제, 로그인 점검 때 자식 프로세스 실행, 세션 훅 등록.
- 주의점: `make_private_dir`는 `#[cfg(unix)]`에서만 0700을 설정한다 (`:705-716`). Windows에서는 권한 보호가 없다 (이슈 참조).

### `ember/server/src/accounts/api.rs` (252줄)
- 목적: 계정, 사용량, API 키 provider HTTP. 오류는 `ApiError(StatusCode, String)`. 응답에 키를 넣지 않는다.
- 라우트는 아래 동작 지도 참조.

### `ember/server/src/accounts/secrets.rs` (359줄), `accounts/schema.rs` (40줄)
- 위 "자격 증명" 절 참조. `random_32` (`secrets.rs`)는 PKCE verifier, OAuth `state`, `nonce`용으로 `chatgpt`가 재사용한다. `schema.rs`는 `accounts`, `api_providers` 테이블과 `sessions.account_id`, `account_reason` 열, 에이전트당 기본 계정 하나를 보장하는 부분 유니크 인덱스, `events` usage 부분 인덱스를 만든다.

### `ember/server/src/chatgpt/mod.rs` (898줄, 테스트 없음)
- 목적: Sign in with ChatGPT. 흐름: `start_signin` (`:301`, PKCE S256 + `state` + `nonce`, 메모리 `pending` 10분 `PENDING_TTL_MS` `:68`) -> 브라우저가 `GET /auth/callback`으로 복귀하거나 다른 기계라면 사용자가 URL을 `POST /api/chatgpt/signin/complete`에 붙여넣기 -> `complete_signin` `:390` -> `finish` `:428` (state 확인, 코드 교환, ID 토큰 iss, aud, exp, nonce 확인, 암호화 저장).
- `access_token` `:555`는 만료 5분 전(`REFRESH_MARGIN_MS` `:70`)에 `refresh` `:576`을 호출한다. 갱신은 `refresh_lock`으로 한 번에 하나이고, 종료성 오류(`invalid_grant` 등)나 401이면 토큰을 지우고 `signed_out`.
- `responses` `:663`: `shape_request`로 요청을 검증(`store:false`, `stream:true` 강제), 플랜 사용 권한과 한도와 `not_eligible` 확인 후 `POST {api_base}/responses` 스트리밍. 사용량은 `ResponseStream`이 `response.completed`에서 기록.
- 리다이렉트는 `http://127.0.0.1:<port>/auth/callback` 고정 (`redirect_uri` `:120`).
- 호스티드 차단: `guard` `:276`이 `config.enabled`가 false이면 `ChatGptError::Disabled`. `enabled = !hosted_from_env()` (`:110-118`), `EMBER_HOSTED`가 `1/true/yes/on`이면 꺼짐 (`:124-129`).
- 주의점: ID 토큰은 서명(JWKS) 검증 없이 클레임만 확인한다 (문서가 열린 항목으로 명시, `chatgpt/mod.rs` 머리 주석). `ChatGpt::responses`의 production 호출자는 없다 (이슈 참조).

### `ember/server/src/chatgpt/oauth.rs` (369줄), `responses.rs` (320줄), `store.rs` (502줄), `api.rs` (267줄), `schema.rs` (50줄), `demo.rs` (104줄)
| 파일 | 설명 |
|---|---|
| `oauth.rs` | 순수 함수: `Pkce` `:29`, `s256` `:52`, `authorize_url` `:76`, `callback_params` `:100`, `TokenResponse` `:113`, `refresh_error_is_terminal` `:185`, `check_id_token` `:204`. 상수 `DYNAMIC_CLIENT`(`dynamic_agent_client`), `SCOPES`, `CALLBACK_PATH` |
| `responses.rs` | 요청 정리와 SSE. `UNSUPPORTED_FIELDS` `:21`와 `UNSUPPORTED_TOOLS` `:41`에 걸리면 조용히 자르지 않고 필드 이름과 함께 거부. `SseParser`, `completed_usage` |
| `store.rs` | `chatgpt_accounts` 행, 암호화 토큰 blob (`seal` `:89`, `tokens` `:270`), `host_id` `:351` (안정적인 `ext_agent_host_id`), `record_usage` `:363`, `usage_since` `:377` |
| `api.rs` | 라우트, `callback` `:163`(성공/실패 HTML 페이지, 코드와 토큰을 에코하지 않음, `escape` `:198`로 이스케이프) |
| `schema.rs` | 마이그레이션 4번: `chatgpt_accounts`(토큰 nonce와 암호문 열, `(client_id, subject)` 유니크), `chatgpt_host`, `chatgpt_usage` |
| `demo.rs` | `EMBER_DEMO_DATA=1`일 때만 `main.rs:111`이 `seed` 호출. 계정 `demo-chatgpt-plan`(`ACCOUNT_ID` `:14`)과 14일 사용량을 `INSERT OR IGNORE/REPLACE`. 토큰 열이 비어 있어 OpenAI에 닿을 수 없다. 테스트 3개 |

### `ember/server/src/schedules/mod.rs` (901줄), `timing.rs` (247줄), `api.rs` (228줄), `schema.rs` (48줄)
- `Scheduler` (`mod.rs:329`): `start` `:372`가 `recover` `:397`(재시작 전 `running` 런을 `failed`로 표시) 후 루프로 `tick` `:670`을 돌리고 다음 예정까지(최대 30초 `MAX_SLEEP`) 잔다. `tick`은 스케줄당 최대 한 번 실행, 지연된 트리거는 `GRACE_MS`(60초) 초과 시 `missed`로 기록하고 `catch_up: true`면 가장 최근 하나만 실행 (`plan` `:715`). 실행 대상은 `continue`(기존 세션이 진행 중이면 `skipped`) 또는 `new`(`create_with_account`로 새 세션, 컴퓨터 지정 시 `ComputerPlacer`로 배치 `:801-855`). 프롬프트는 `[ember schedule]` 머리줄(`HEADER_TAG` `:48`)과 함께 `Sessions::send`로 전달.
- 한도: 프로젝트당 100개 (`MAX_SCHEDULES_PER_PROJECT` `:44`), 누락 기록 20개 (`MAX_MISSED_ROWS` `:42`), 최소 간격 60초 (`timing::MIN_INTERVAL_SECS` `:22`).
- `timing.rs`: `croner` 5필드 cron을 `chrono-tz` IANA 시간대에서 평가, DST 중복 시각은 한 번만 발화. `next_after` `:63`, `occurrences_between` `:112`, 최대 순회 `MAX_WALK` 200,000.
- 부수효과: `schedules`, `schedule_runs` 테이블, 푸시 이벤트(`schedule_created|updated|deleted|run`), 에이전트가 만든 스케줄은 호출 세션의 프로젝트에 한정.
- 사용처: `main.rs:400-417`, 라우트 `main.rs:454-455`. 테스트 `schedules/mod.rs`에는 인라인 테스트가 없고 timing 7개, 통합 테스트는 `ember/server/tests/` [확인 필요].

### `ember/server/src/transfers.rs` (833줄, 인라인 테스트 0개)
- 목적: `ember_transfer` ([transfer](transfer.md))의 정책을 HTTP로 노출하는 서버 매니저. 수신 폴더 `<data_dir>/received/`, 이력 `<data_dir>/transfers-history.json` (`transfers.rs:161-190`), 기본 수신 모드 `Ask`, 크기 상한 `DEFAULT_MAX_BYTES`(4 GiB).
- 주요 심볼: `TransferManager` `:154` (`Mutex<Inner>`), `receive_offer` `:285`, `accept_offer` `:368`, `write_chunk` `:463` (일시중지면 409), `complete_transfer` `:516`, `pause/resume/cancel_transfer`, `update_settings` `:638`, `TransferApiError` `:103` (`NotFound`, `BadRequest`, `Forbidden`, `PayloadTooLarge`, `Conflict`, `Internal` -> `{error}` JSON).
- 라우트: `ember/server/src/transfers.rs:715-730` (아래 표). 장치 등록 여부는 `is_peer_registered` `:191`가 `Devices`와 `Computers`로 확인.
- 주의점: 상태는 메모리 + JSON 이력 파일이라 재시작 시 진행 중 전송은 사라진다 [확인 필요].

### `ember/server/src/usage.rs` (251줄)
- `impl Store`의 `day_start_ms` `:103`, `session_usage` `:118`, `usage_summary` `:143` (일수는 1..366으로 clamp). `events` 테이블의 `usage` 이벤트 위 질의이고 별도 기록은 없다. 비용은 항상 `null`, `COST_NOTE` `:23`가 이유를 설명한다. 사용처 `ember/server/src/api/mod.rs:91-92`.

## 동작 지도

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `GET/POST /api/accounts` | `list`, `create` `accounts/api.rs:110`, `:129` | `Accounts::list`, `create` | `accounts`, 디렉터리 |
| `GET/DELETE /api/accounts/{id}` | `get_one`, `delete` `:138`, `:146` | `get`, `delete` (사용 중이면 409) | `accounts`, `sessions` |
| `POST /api/accounts/{id}/default`, `/check`, `/clear-limit` | `:154`, `:162`, `:170` | `set_default`, `check_login`, `clear_limit` | `accounts` |
| `GET /api/accounts/route?agent=` | `preview_route` `:181` | `route` | 읽기 |
| `GET /api/usage` | `usage` `:198` | `usage_since` | `events`, `chatgpt_usage` |
| `GET/POST /api/providers`, `DELETE /api/providers/{id}` | `:208`, `:221`, `:240` | `secrets::*_provider` | `api_providers` (암호화) |
| `GET /api/chatgpt`, `POST /api/chatgpt/signin`, `GET /api/chatgpt/signin/{state}`, `POST /api/chatgpt/signin/complete` | `chatgpt/api.rs:116`, `:134`, `:148`, `:210` | `start_signin`, `signin_status`, `complete_signin` | 메모리 `pending`, `chatgpt_accounts` |
| `GET /auth/callback` (토큰 면제) | `callback` `:163` | `complete_signin` | 위와 같음 |
| `GET /api/chatgpt/accounts[/{id}]`, `DELETE`, `POST .../refresh`, `.../clear-limit`, `GET .../models` | `:220`-`:262` | `list`, `get`, `sign_out`, `refresh`, `clear_limit`, `models` | `chatgpt_accounts` |
| `/api/schedules` 계열 9개 | `schedules/api.rs:88`-`:130` | `Scheduler::create/update/pause/resume/delete/run_now/runs` | `schedules`, `schedule_runs` |
| `/api/a2a/schedules` (GET/POST), `DELETE /api/a2a/schedules/{id}` | `:160`, `:179`, `:215` | 런타임 토큰 -> 세션 -> 프로젝트 한정 | 같음 |
| `/api/transfers`, `/offers`, `/offers/{id}/accept|decline`, `/{id}/chunks|resume-offset/{file}|complete|pause|resume|cancel`, `/history`, `/settings` | `transfers.rs:732`-`:822` | `TransferManager::*` | 메모리, `received/`, 이력 JSON |

### 사용자에게 보이는 에러 메시지 (주요)
| 원문 | 위치 | 조건 |
|---|---|---|
| `account {id} is used by {n} session(s); its sessions cannot change account` | `accounts/mod.rs:296-299` | 사용 중인 계정 삭제 (409) |
| `no {agent} account is available: ...` | `accounts/mod.rs:549-555` | 계정은 있으나 모두 한도 또는 로그아웃 |
| `Antigravity accounts are not supported yet: ...` | `accounts/mod.rs:245-247` | Antigravity 계정 생성 |
| `... must not be readable by group or others (mode ..); run chmod 600 on it` | `accounts/secrets.rs:151` | 키 파일 권한 불량, 서버 시작 거부 |
| `API key failed to decrypt (wrong secret.key or tampered row)` | `accounts/secrets.rs:117` | 키 불일치나 변조 |
| `sign in to ChatGPT again: {0}` | `chatgpt/mod.rs` `SignInRequired` | 토큰 없음, 갱신 거부 |
| `ChatGPT plan usage limit reached for Ember (until {until_utc}): ... Manage it at https://chatgpt.com/settings/usage` | `chatgpt/mod.rs` `UsageLimited` | 주간 상한 도달 |
| `the sign-in expired; start it again` | `chatgpt/mod.rs:408` | pending 만료 |
| `project must not be empty`, `prompt must not be empty` | `schedules/mod.rs:453`, `:456` | 스케줄 생성 검증 |
| `computer {computer} requested but computers are not enabled` | `schedules/mod.rs:847` | 컴퓨터 배치기 미설정 |

## 데이터와 설정

- DB 테이블: `accounts`, `api_providers`, `chatgpt_accounts`, `chatgpt_host`, `chatgpt_usage`, `schedules`, `schedule_runs`, `sessions.account_id|account_reason`, `events`(usage 부분 인덱스).
- 파일: `<data dir>/secret.key`(32바이트, 0600), `<data dir>/accounts/<id>/`(0700), `<data dir>/received/`, `<data dir>/transfers-history.json`.

| 환경 변수 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_HOSTED` | `chatgpt/mod.rs:124` | `1/true/yes/on`이면 Sign in with ChatGPT 전체 끔 | 꺼짐(기능 켜짐) |
| `EMBER_CHATGPT_REDIRECT_PORT` | `chatgpt/mod.rs:110` | OAuth 콜백 포트 | 서버 listen 포트 |
| `EMBER_DEMO_DATA` | `chatgpt/demo.rs:12` | `1`이면 데모 ChatGPT 계정과 사용량 시드 | 꺼짐 |
| `EMBER_CLAUDE_BIN`, `EMBER_CODEX_BIN` | `accounts/mod.rs:699` | 로그인 점검과 안내에 쓸 CLI | `claude`, `codex` |
| `CLAUDE_CONFIG_DIR`, `CODEX_HOME` | `accounts/mod.rs:70` | 계정 디렉터리를 가리키도록 에이전트 프로세스에 주입 | 계정 없으면 미주입 |

- 외부 연동: `https://auth.openai.com` (authorize, token, discovery), `https://api.openai.com/v1` (`/responses`, `/models`), 에이전트 CLI 프로세스(`claude`, `codex`).

## 이 모듈을 수정할 때 주의할 점

- 마이그레이션 번호가 고정이다 (accounts 2, chatgpt 4, schedules 12). 순서를 바꾸지 않는다 (`ember/server/src/store.rs`의 `MIGRATIONS`).
- 새 암호화 데이터는 `SecretBox::seal/open`에 고유 AAD 접두사를 붙여 쓴다 (기존 두 접두사 변경 금지, 기존 행이 복호화 불가).
- `route`의 정렬 키나 이유 문구를 바꾸면 클라이언트 표시와 `account_reason`이 바뀐다. 세션의 계정은 생성 시 고정이므로 (FR-U2) 이후에 바꾸는 경로를 만들지 않는다.
- `/auth/callback` 면제 (`auth.rs:202`)와 `CALLBACK_PATH`가 연결되어 있다. 경로를 바꾸면 면제도 함께 바꾼다. 콜백 응답에 코드나 토큰을 에코하지 않는다.
- 스케줄러는 시계를 `Clock`으로 주입받는다. 시간 의존 로직에 `SystemTime`을 직접 쓰지 않는다 (테스트가 `ManualClock`과 `tick`을 쓴다).
- 전송 정책 변경은 [transfer](transfer.md) 크레이트와 `transfers.rs`를 함께 본다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 높음 | `ember/server/src/accounts/secrets.rs:158-161`, `accounts/mod.rs:705-716` | 비 unix(Windows)에서는 `secret.key` 권한 검사(`check_private`)가 아무것도 하지 않고 계정 디렉터리 0700도 설정되지 않는다. 이 저장소의 개발 환경이 Windows이므로 암호화 키 파일이 다른 사용자에게 읽힐 수 있다 | Windows ACL 설정과 검사 추가 |
| 보안 | 중간 | `chatgpt/mod.rs` 머리 주석 | ID 토큰 서명(JWKS) 미검증. TLS로 토큰 엔드포인트에서 직접 받으므로 OIDC가 허용하나 문서가 열린 항목으로 인정 | JOSE 의존성 추가 후 검증 |
| 보안 | 중간 | `ember/server/src/auth.rs:202` | `GET /auth/callback`은 토큰 없이 접근 가능하고 `state` 일치만 검증한다. `state`는 OS RNG 32바이트이고 pending에 있어야 하므로 위험은 낮으나 원격 노출 시 임의 호출을 받는 경로 | 현 설계 유지, 원격 노출 시 문서화 [확인 필요] |
| 보안 | 낮음 | `accounts/secrets.rs:15-18` | 키는 파일 하나이고 KMS 미지원. 서버 계정 침해는 방어 대상이 아님 | 문서화된 경계, 키체인 이전은 향후 |
| 사용되지 않는 심볼 | 중간 | `chatgpt/mod.rs:663` `ChatGpt::responses` | production 호출자가 없고 테스트 (`ember/server/tests/chatgpt.rs:482` 등)에서만 쓰인다 (grep 확인) | 사용처가 생길 때까지 [확인 필요]로 두거나 정리 |
| 구조 | 중간 | `schedules/mod.rs` (901줄), `chatgpt/mod.rs` (898줄), `accounts/mod.rs` (996줄), `transfers.rs` (833줄) | 큰 파일. `schedules/mod.rs`와 `chatgpt/mod.rs`에는 인라인 테스트가 없고 별도 통합 테스트에 의존 | 분리 검토 |
| 하드코딩 | 낮음 | `accounts/mod.rs:66`, `schedules/mod.rs:40-46`, `chatgpt/mod.rs:68-70`, `accounts/api.rs:82-90` 부근 | 쿨다운 1시간, 유예 60초, 한도 100개와 20개, 상수 `CAP` 안내문, 에이전트 이름 `DarkPyonix Ember` (`chatgpt/mod.rs:104`) | 필요 시 설정화 |
| 견고성 | 낮음 | `transfers.rs:154-190` | 전송 상태 메모리 보관, 이력 파일 읽기 실패는 조용히 빈 이력 (`unwrap_or_default`), 디렉터리 생성 실패 무시 (`let _ =`) | 오류 로그 추가 |
| 견고성 | 낮음 | `chatgpt/mod.rs:339`, `:400` | `self.pending.lock().unwrap()` (포이즌 시 패닉). 다른 곳은 `unwrap_or_else(into_inner)` 사용 | 일관화 |
| TODO/FIXME | | 17개 파일 | 0개 | |
