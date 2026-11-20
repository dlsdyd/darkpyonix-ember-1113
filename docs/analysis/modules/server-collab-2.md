# 모듈: server-collab (2) 채널, 게스트, 멤버

- 경로: `ember/server/src/channels/` (8개 파일), `ember/server/src/guest_door.rs`, `ember/server/src/guest_door/` (`join.html`, `join.js`, `.gitattributes`), `ember/server/src/members.rs`
- 규모: 파일 13개 / 약 4,240줄 (`channels/` 3,264 + `guest_door.rs` 303 + `join.html` 49 + `join.js` 274 + `members.rs` 313 + `.gitattributes` 2, 테스트 포함)
- 레이어: 비즈니스 로직 (HTTP 라우트 포함). 게스트 문은 별도 리스너용 라우터
- 한 줄 책임: 채널(그룹 대화, 피드, 읽음 커서, 멘션), 초대와 게스트와 허용, 사람 메시지의 채널별 JSONL 기록과 시작 시 복구, 게스트 문(`/join` 페이지와 게스트 라우트만 서비스하는 둘째 리스너), 팀원 정의(하네스, 계정, 모델 프록시)를 담당한다.
- 의존하는 모듈: [server-core](server-core.md) (`Store`, `now_ms`, `Sessions`, `Push`, `QuestionAnswerBody`, `events.rs`), [server-collab](server-collab.md) (`a2a::A2a`, `a2a::channel::sanitize_label`, `a2a::api::caller`), [server-enrol](server-enrol.md) (`door/` 공용 문 부품), [server-agents](server-agents.md) (`AgentKind`, 프록시 환경 변수 상수)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`main.rs`, `store.rs` 마이그레이션), [server-collab](server-collab.md) (`a2a/team.rs`가 `members::create_member_session`을 사용), [server-enrol](server-enrol.md) (`door/limits.rs`가 `guest_door::ACCEPT_PATH`를, `computers/enrol.rs`가 `channels::invites::new_secret`을 사용), [client](client.md)

개요, 공개 인터페이스 표, 인증 경계 세 가지, `a2a/` 전체는 [server-collab.md](server-collab.md)에 있다. 이 문서는 그 표를 반복하지 않는다.

## 한눈에 보기

- 채널은 프로젝트 하나에 속한다. 프로젝트마다 기본 채널 `default-<project>`가 있고, 그 멤버는 읽을 때 계산한 프로젝트의 모든 세션이다 (`ember/server/src/channels/mod.rs:199-207`, `:219-240`). 나머지 채널의 멤버는 `channel_agents`에 고정된 세션이다.
- 로그인한 사람은 모든 채널의 멤버 `user`(표시 이름 `나`)다 (`channels/mod.rs:71-73`, `:231`).
- 사람 메시지(`user`, `guest:<id>`)만 JSONL 파일에도 쓴다. 에이전트와 `system` 메시지는 SQLite에만 있다 (`channels/jsonl.rs:59-61`).
- 게스트는 초대 토큰 `dpi_...`를 한 번 써서 자격 `dpg_...`을 받는다. 둘 다 SHA-256 해시만 저장한다 (`channels/invites.rs:67-76`, `:249-310`).
- 게스트 문은 `EMBER_GUEST_LISTEN`이 있을 때만 열리는 둘째 TCP 리스너로, 게스트 라우트 4개와 `GET /join`만 서비스한다.

## 게스트 문 보안 경계

### 서비스하는 라우트 (전부)

| 메서드 | 경로 | 인증 | 핸들러 | 근거 |
|---|---|---|---|---|
| GET | `/join` | 없음 | `guest_door.rs:293` `join` (HTML, CSP, no-store) | `guest_door.rs:81`, `:206` |
| POST | `/api/guest/accept` | 없음 (본문의 초대 토큰이 비밀, 1회용) | `channels/guest.rs:329` `accept` | `channels/guest.rs:264` |
| GET | `/api/guest/channels/{id}` | `Bearer dpg_...` | `guest.rs:345` `summary` | `guest.rs:259` |
| GET | `/api/guest/channels/{id}/messages?after=` | `Bearer dpg_...` | `guest.rs:360` `messages` | `guest.rs:260` |
| POST | `/api/guest/channels/{id}/messages` | `Bearer dpg_...` | `guest.rs:381` `post_message` | `guest.rs:260` |
| 그 밖의 전부 | 임의 | 없음 | `door::harden::not_found` (404) | `guest_door.rs:206` `.fallback(not_found)` |

- 라우트 표는 상수 `GUEST_ROUTES` (`channels/guest.rs:74-79`)와 `JOIN_ROUTE` (`guest_door.rs:81`)에 있다. 테스트 `fr_t14_guest_door_serves_exactly_the_route_table`이 실제 라우터를 이 표와 대조한다고 주석이 적는다 (`guest.rs:72-73`). 테스트는 실행하지 않았다.
- 게스트 라우터에는 피드, 승인, 세션, 소유자 채널 라우트, `/api/guest-door`, `/api/push`가 없다. 소유자 API는 문 리스너에 연결되지 않는다 (`ember/server/src/main.rs:427-441`: `guest_app`은 `guest_router_with_a2a` 결과만 감싸고 `app`에 merge하지 않는다).
- 인증 `require_guest`는 `route_layer`라서 `protected` 라우트 둘에만 걸린다 (`guest.rs:261`, `:292-300`). `/join`, `accept`, 404 폴백에는 자격이 필요 없다.
- 서버 토큰과 런타임 토큰은 게스트 자격이 아니다. `guest_from_headers`는 `Bearer dpg_` 접두사만 받고 (`guest.rs:273-280`) 매 요청마다 DB에서 조회한다 (`invites.rs:314-345`). 그래서 해지가 즉시 반영된다.
- 자격은 한 채널에 묶인다. 다른 채널 id는 403이 아니라 404다 (`guest.rs:315-321` `own_channel`).

### 라우트를 감싸는 계층 (바깥부터)

`GuestDoor::build` (`guest_door.rs:203-208`)가 `door::harden::stack`에 넘긴다. `stack`의 설명은 [server-enrol.md](server-enrol.md) 99행, 109행에 있다.

| 순서 | 계층 | 동작 | 근거 |
|---|---|---|---|
| 1 | `response_headers` | 모든 응답에 nosniff, no-store | `door/harden.rs:43` |
| 2 | `limit_layer` (`wrap_limited`일 때만) | 주소별 한도 429(`Retry-After`), 전역 토큰 버킷 50/s(버스트 100), 동시 요청 64(503). `ConnectInfo`가 없으면 500 | `door/harden.rs:40-42`, `door/limits.rs:301`, `guest_door.rs:59-78` |
| 3 | `with_timeout` | 요청 전체 10초, 408 | `guest_door.rs:89`, `door/harden.rs:39`, `:51-57` |
| 4 | `guard_layer` | Host 필수이고 허용 목록에 있어야 함(403), Origin 규칙(403), HEAD/TRACE/CONNECT 405, `Content-Length` 16 KiB 초과 413, `Upgrade` 헤더 400 | `door/harden.rs:122-149`, `guest_door.rs:85` |
| 5 | `DefaultBodyLimit` 16 KiB | `Content-Length` 없는 본문도 막음 | `door/harden.rs:37`, `guest.rs:84`, `:267` |
| 6 | 라우터 | `/join`, 게스트 라우트(자격 검사), `not_found` | `guest_door.rs:206` |

- 연결 수준: 헤더 읽기 10초(`HEADER_READ_TIMEOUT`), 열린 연결 256개(`MAX_CONNECTIONS`), HTTP/1만 (`guest_door.rs:73-76`, `:216-244`).
- `auth::protect`는 이 라우터에 걸리지 않는다 (`guest_door.rs:19-21`, `main.rs:427-428`). 서버 토큰이 게스트 문에서 통하는 경로가 없다.
- 한도 키는 TCP 피어 주소이고, `EMBER_GUEST_TRUSTED_PROXIES`에 든 피어일 때만 `X-Forwarded-For`를 오른쪽부터 읽는다 (`guest_door.rs:11`, `door/limits.rs:92`). IPv6은 /64로 줄인다 (`guest_door.rs:35`).
- strict 클래스는 `POST /api/guest/accept`: 분당 5, 시간당 20, 실패도 센다 (`guest_door.rs:55-69`, `door/limits.rs:283-285`). 나머지 요청은 주소당 분당 120.
- 부팅 조건: 비 loopback 바인드는 `EMBER_GUEST_LISTEN_ALLOW_REMOTE=1`이 있어야 하고, 소유자 주소와 같으면 시작 오류다 (`guest_door.rs:8`, `main.rs:362-377`). 문은 평문 HTTP다. TLS는 소유자가 앞단에 둔다 (`guest_door.rs:9`).
- 문이 죽어도 소유자 서버는 멈추지 않는다 (`main.rs:525-536`).

### `/join` 페이지의 CSP

- `build_join_page_from` (`guest_door.rs:125-140`)이 `join.html`의 `__JOIN_JS__`를 `join.js`로 치환하고, 치환 후 `<style>` 내용과 스크립트의 SHA-256을 CSP에 넣는다: `default-src 'none'; script-src 'sha256-..'; style-src 'sha256-..'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`. `unsafe-inline`, `unsafe-eval`은 없다.
- 해시 입력은 `normalize_eol`로 CRLF를 LF로 바꾼 텍스트다 (`guest_door.rs:118-120`). 브라우저가 인라인 스크립트의 줄바꿈을 정규화하므로 필요하다. `guest_door/.gitattributes`가 `join.html`, `join.js`를 `text eol=lf`로 고정해 체크아웃 줄바꿈이 바뀌어도 같은 텍스트가 나오게 한다 (`ember/server/src/guest_door/.gitattributes:1-2`). 저장소 루트와 `ember/server/`에는 `.gitattributes`가 없다.
- 응답 헤더: `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `Cache-Control: no-store` (`guest_door.rs:293-302`).

## 공개 인터페이스

다른 모듈이 쓰는 심볼은 [server-collab.md](server-collab.md)의 표에 있다. 여기에는 그 표에 없는 내부 진입점만 적는다.

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Store::{create_invite, accept_invite, guest_by_credential, revoke_invite}` | 메서드(pub) | `channels/invites.rs:160`, `:249`, `:314`, `:205` | 초대 생성, 수락(1회용 게이트), 자격 조회, 해지 |
| `Store::{set_guest_allowance, clear_guest_allowance, revoke_guest, guest_allowance_at}` | 메서드(pub) | `channels/allowance.rs:72`, `:107`, `:121`, `:160` | 게스트 멘션 허용 |
| `channels::guest::deliver_guest_mentions(_at, _hooked)` | 함수(pub) | `channels/guest.rs:427`, `:448`, `:464` | 게스트 멘션의 에이전트 전달 |
| `channels::api::persist_and_publish` | 함수(pub(super)) | `channels/api.rs:250` | 행 삽입, JSONL 추가, 실패 시 행 삭제, 푸시. 소유자와 게스트 라우트가 공유 |
| `channels::feed::feed_questions`, `INPUT_BYTES_MAX` | 함수/상수(pub) | `channels/feed.rs:89`, `:59` | `AskUserQuestion` 입력을 읽기 쉬운 질문으로 |
| `guest_door::{join_page, invite_link, door_status, status_body, normalize_eol}` | 함수(pub) | `guest_door.rs:142`, `:267`, `:282`, `:287`, `:118` | 페이지, 초대 링크, 문 상태 |
| `members::{MemberDef, ProxySpec, proxy_env, parse_harness}` | 타입/함수(pub) | `members.rs:63`, `:45`, `:122`, `:86` | 팀원 정의와 프록시 환경 |

## 파일별 요약

### `ember/server/src/channels/mod.rs` (약 548줄, 테스트 없음)

- 목적: 채널 테이블 마이그레이션, 채널과 메시지 저장 함수, 읽음 커서, 멘션 미리보기. 하위 모듈 7개를 선언한다 (`:13-19`).
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MIGRATION`, `READS_MIGRATION`, `MENTIONS_MIGRATION` | 상수 | 29, 55, 66 | `channels`, `channel_agents`, `channel_messages`(+인덱스), `channel_reads`, `mentions` 열 |
  | `USER`, `USER_LABEL`, `SYSTEM`, `DEFAULT_NAME` | 상수 | 71-78 | `user`, `나`, `system`, `전체` |
  | `ChannelError` | enum | 83 | `NotFound`, `BadRequest`, `Forbidden`, `NotAMember`, `Coded(코드, 문장)`, `Other` |
  | `Message`, `Channel`, `NewChannel`, `Member` | 구조체 | 121, 142, 157, 109 | `Message.at`은 초 단위 (`:187`, `at_ms / 1000`) |
  | `ensure_default_channels` | 함수 | 199 | 기본 채널이 없는 프로젝트마다 `default-<name>`을 INSERT. `channel_row`가 매번 호출한다 (`:209-210`) |
  | `members_of` | 함수 | 219 | 기본 채널은 프로젝트의 세션 전체, 그 외는 `channel_agents` 조인. 이름은 세션 `title`, 비면 하네스 이름 |
  | `create_channel` | 함수 | 392 | 이름 금지 문자 검사, 프로젝트 존재 검사, 세션이 같은 프로젝트인지 검사, 트랜잭션 삽입 |
  | `post_channel_message` | 함수 | 443 | 멤버 검사. `user`의 `@이름`만 해석해 `mentions` 저장, 모르는 이름은 `NotAMember` |
  | `post_channel_system_message` | 함수 | 481 | 멤버 검사와 멘션 해석 없이 `system` 행 삽입 |
  | `mark_channel_read` | 함수 | 267 | 커서는 앞으로만, 최신 `seq`를 넘지 않음 (`MAX(last_seq, ...)`) |
  | `annotate` | 함수 | 304 | 에이전트, 게스트 메시지의 `author_name`을 읽을 때 채움 |
  | `channel_messages_after` | 함수 | 511 | `seq > after`, 오름차순 또는 최신 N개 |

- 부수효과: `channel_row`를 부르는 모든 읽기와 쓰기가 기본 채널 INSERT를 일으킬 수 있다.
- 주의점: 상세 응답의 메시지는 최근 `DETAIL_LIMIT`=200개 (`:80`). `delete_channel_message` (`:505`)는 JSONL 추가 실패 시 롤백용이다.

### `ember/server/src/channels/api.rs` (약 495줄, 테스트 없음)

- 목적: 소유자 채널 라우트. 문서 머리에 라우트 표가 있다 (`:1-72`).
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ChannelsCtx` | 구조체 | 90 | `store`, `sessions`, `jsonl`, `a2a`, `door` |
  | `router`, `router_with_dir`, `router_with_a2a`, `router_with_a2a_door`, `router_with_door` | 함수(pub) | 101, 106, 112, 123, 140 | 부품을 하나씩 더 붙인 생성자. `main.rs:457`은 `router_with_a2a_door` |
  | `build` | 함수 | 148 | 라우트 등록 (`:150-164`) |
  | `impl IntoResponse for ChannelError` | 구현 | 168 | `Coded`의 `rate_limited`, `quota_exceeded`는 429, 나머지 코드는 400 |
  | `persist_and_publish` | 함수 | 250 | JSONL 잠금 아래에서 삽입, 추가, 푸시 |
  | `agent_post` | 함수 | 283 | 런타임 토큰(`a2a::api::caller`), 멤버+30분 안 멘션+분당 6회(`check_channel_post`), 본문은 `{text}` |
  | `deliver_mentions` | 함수 | 313 | 사람 메시지의 멘션마다 `tokio::spawn`으로 `send_from_person`. 실패는 `@이름 not reached: ...` `system` 메시지 |
  | `answer_feed_question` | 함수 | 397 | 피드의 멤버 확인 후 `Sessions::resolve_question_body`에 넘기고 오류를 404/400/409/500으로 매핑 |
  | `create_invite` | 함수 | 426 | 토큰은 이 응답에만 나옴. `invite_link`로 링크 생성 |

- 주의점: 소유자 `post_message` (`:231`)는 `from`에 멤버 에이전트 id를 받아 그 에이전트 이름으로 기록할 수 있다 (소유자 전용 라우트). `agent_post`에는 본문 길이 상한이 없다 ([server-collab.md](server-collab.md)의 `mcp.rs` 항목 참고).

### `ember/server/src/channels/guest.rs` (약 592줄, 테스트 없음)

- 목적: 게스트 라우터, 게스트가 보는 메시지 변환, 허용 아래의 멘션 전달. 머리 주석이 라우트, 한도, 정책을 설명한다 (`:1-52`).
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `GUEST_ROUTES` | 상수 | 74 | 서비스하는 (메서드, 경로) 표 |
  | `MAX_TEXT_BYTES`=8192, `MAX_BODY_BYTES`=16 KiB, `READ_LIMIT`=500, `POSTS_PER_MINUTE`=10, `MESSAGE_CAP`=500 | 상수 | 82-93 | 한도 |
  | `GuestMessage` | 구조체 | 100 | `author`는 `user`/`system`/`agent`/`guest`만, id 없음. `you`는 본인 메시지 |
  | `guest_view` | 함수 | 135 | 세션 id, 하네스, 작업 디렉터리를 숨기고 이름만 노출 |
  | `post_guest_message` | 함수 | 171 | 빈 글, 8192바이트, 모르는 멘션(`NotAMember`) 검사. 작성자는 서버가 `guest:<id>`로 고정 |
  | `Ctx::rate_check` | 함수 | 212 | 게스트별 최근 1분 `VecDeque<Instant>` (메모리) |
  | `build`, `guest_router`, `guest_router_with_dir`, `guest_router_with_a2a` | 함수 | 251, 230, 236, 242 | `main.rs:431`은 `_with_a2a` |
  | `require_guest`, `guest_from_headers` | 함수 | 292, 273 | 자격 검사. 실패는 401 + `WWW-Authenticate: Bearer` |
  | `deliver_guest_mentions_hooked` | 함수 | 464 | 전달 로직 (아래) |
  | `DELIVERIES` | static | 551 | 게스트별 시간당 전달 기록 (전역 Mutex, 메모리) |

- 게스트 메시지 전달 규칙 (`:464-541`)
  1. 멘션이 없거나 작성자가 해당 게스트가 아니면 반환한다.
  2. 대상은 멤버 에이전트만, 중복 제거.
  3. 허용이 없으면 `guest @x's mention to @a was not delivered (no active allowance)` `system` 메시지만 남기고 `a2a_messages` 행은 만들지 않는다.
  4. 대상이 3개를 넘으면 앞 3개만 (`MAX_MENTION_TARGETS`, 안내 메시지 1개).
  5. 전송 직전마다 허용을 DB에서 다시 읽고(`now`에 경과 시간을 더함), 끝났으면 나머지를 중단한다.
  6. 시간당 20회 한도(`DELIVERIES_PER_HOUR`)를 넘으면 중단한다.
  7. `A2a::send_from_guest`가 UNTRUSTED 블록으로 감싸 전달하고, 거부는 `@이름 not reached: <이유>`로 남긴다.
- 의존: `invites.rs`, `a2a/channel.rs` (`sanitize_label`), `channels/api.rs::persist_and_publish`.

### `ember/server/src/channels/invites.rs` (약 354줄, 테스트 없음)

- 목적: 초대와 게스트 테이블(`channel_invites`, `channel_guests`), 이름 규칙, 비밀 생성과 해시.
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MIGRATION` | 상수 | 16 | `channel_invites`(`token_hash UNIQUE`, `used_at`, `revoked_at`), `channel_guests`(`credential_hash UNIQUE`, `allow_until`) |
  | `INVITE_PREFIX`=`dpi_`, `CREDENTIAL_PREFIX`=`dpg_`, `DEFAULT_TTL_HOURS`=24, `MAX_TTL_HOURS`=168 | 상수 | 43-49 | |
  | `hash_secret`, `new_secret` | 함수 | 67, 73 | SHA-256 hex, 접두사+난수 |
  | `is_forbidden_name_char` | 함수 | 87 | 제어, 서식(Cf), 줄 구분 문자 금지. Cf는 손으로 적은 목록 (`:99-108`) |
  | `check_guest_name` | 함수 | 112 | 1~64자, 예약어(`user`, `나`, `system`, `agent`)와 멤버 이름 불가 |
  | `create_invite` | 함수 | 160 | TTL 1~168시간, 토큰 평문은 반환값에만 존재 |
  | `accept_invite_at` | 함수 | 254 | 이름 검사 후 `UPDATE ... SET used_at WHERE used_at IS NULL AND revoked_at IS NULL AND expires_at > now`로 1회용 게이트, 같은 트랜잭션에서 게스트 삽입. 자격 만료는 초대 만료와 같다 |
  | `guest_by_credential_at` | 함수 | 319 | 접두사, 해시 조회, 게스트와 초대 모두 미해지, 만료 전. DB 오류는 `None` (fail closed) |

- 주의점: 이름의 모양 검사를 토큰 조회보다 먼저 하고, 토큰이 살아 있으면 멤버 이름 충돌도 소각 전에 검사한다 (`:256-270`). 그래서 유효한 토큰만 이름 충돌 오류를 받는다. 주석은 비밀이 244비트라 실용적 영향이 없다고 적는다.

### `ember/server/src/channels/allowance.rs` (약 195줄, 테스트 없음)

- 목적: 소유자가 게스트 하나의 멘션 전달을 N시간 허용한다 (FR-T15, FR-T17).
- 심볼: `check_hours` (`:48`, 정수 1~168이 아니면 `invalid_hours`), `USABLE` (`:65`, 해지 안 됨, 초대 해지 안 됨, 만료 전 조건), `set_guest_allowance_at` (`:77`, `allow_until = min(now+N시간, 자격 만료)`, `capped` 반환), `clear_guest_allowance` (`:107`), `revoke_guest` (`:121`, `allow_until`도 비움), `list_guests` (`:135`), `guest_allowance_at` (`:160`, 매번 DB 조회), `channel_guests_at` (`:181`).
- 부수효과: 만료는 비교로만 처리한다. 지우는 작업이 없다.

### `ember/server/src/channels/jsonl.rs` (약 351줄, 그중 테스트 약 27줄, 테스트 1개)

- 목적: 사람 메시지의 채널별 추가 전용 파일 `<data dir>/channels/<channel id>.jsonl` (FR-T16). 줄 모양은 `{"seq","channel_id","from","text","at"}`이고 게스트 줄에만 `name`이 더해진다 (`:64-82`). `at`은 초.
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MAX_FILE_BYTES` | 상수 | 41 | 1 GiB. 넘으면 새 줄을 쓰지 않고 `Ok(false)`. 행은 남고 경고는 채널당 한 번 |
  | `RECOVER_WINDOW` | 상수 | 44 | 복구 때 파일 끝에서 읽는 1 MiB |
  | `path_of` | 함수 | 189 | 채널 id가 영숫자, `-`, `_`이고 128자 이하일 때만 경로 허용 |
  | `open_log`, `handle_ok` | 함수 | 84, 99 | `O_NOFOLLOW`와 `O_NONBLOCK`, 신규 0600, 열린 핸들이 일반 파일이고 현재 사용자 소유인지 확인 (Windows에서의 동작은 읽지 않았다 `[확인 필요]`) |
  | `append` | 함수 | 202 | `write_all` 한 번 + `sync_data`. 실패는 호출자가 행을 롤백 |
  | `recover`, `recover_channel` | 함수 | 236, 264 | 시작 시 복구 |

### 시작 시 JSONL 복구 (FR-T16)

- 호출: `ember/server/src/main.rs:119` `JsonlLog::new(&data_dir).recover(&store)`. `reset_live_statuses` (`main.rs:112`) 이후, 어떤 라우터가 만들어지기 전에 동기로 실행한다. 복구용 `JsonlLog`는 라우터의 인스턴스와 잠금을 공유하지 않으므로 이 순서가 필수다 (`jsonl.rs:224-232`).
- 채널마다 (`recover_channel`, `:264-324`)
  1. 파일이 일반 파일이 아니거나(심볼릭 링크 포함), 소유자가 다르거나, 1 GiB를 넘으면 건드리지 않고 `skipped`로 센다.
  2. `scan_tail`이 끝 1 MiB만 읽는다 (`:117-146`). 마지막 `\n` 뒤의 조각은 충돌 흔적이라 보고 그 위치까지 자른다 (`set_len`, 조각은 보관하지 않음). 마지막 완전한 줄을 JSON으로 읽어 `seq`를 얻는다. 파싱 불가, `seq` 없음, 마지막 줄이 1 MiB 초과면 해당 채널을 건너뛴다.
  3. SQLite에서 `seq > 마지막 줄의 seq`인 사람 행을 읽어 파일 끝에 순서대로 추가하고 `sync_data`한다.
- 결과 `RecoverReport` (`channels_checked`, `truncated_bytes`, `repaired_lines`, `skipped`)는 비어 있지 않을 때만 `tracing::info!`로 기록한다. 어떤 문제도 시작을 막지 않는다 (`:236-262`).
- 한계: 복구는 추가 전용이라 파일 중간에서 빠진 행은 복구되지 않는다 (`:20-22`).
- 쓰기 경로의 일관성: `persist_and_publish`가 삽입과 추가를 JSONL 잠금 아래에서 하고, 추가 실패 시 `delete_channel_message`로 행을 지운다 (`api.rs:250-271`).

### `ember/server/src/channels/feed.rs` (약 357줄, 그중 테스트 약 93줄, 테스트 5개)

- 목적: 채널 멤버 에이전트의 대기 승인, 대기 질문, 마지막 턴 보고를 세션 이벤트에서 파생한다. 저장소가 없다 (`:1-20`).
- 심볼: `FeedItem` (`:129`, `id`는 `approval:<id>`, `question:<id>`, `report:<session>:<seq>`), `feed_questions` (`:89`), `capped_input` (`:63`, 입력 8 KiB 상한), `Store::channel_feed` (`:164`, 세션별로 `events_after(id, 0)` 전체를 재생), `channel_feed_approval` (`:246`), `channel_feed_question` (`:256`).
- 규칙: `TurnEnded`는 대기 항목을 모두 지운다. 보고는 세션 상태가 `Finished`나 `Failed`일 때만 낸다. 요약은 500자 (`:27`), 질문 4개, 선택지 8개 (`:30-31`).
- 주의점: `channel_feed`는 호출마다 멤버 세션의 이벤트 전체를 읽는다. `[추정]` 이벤트가 많은 세션에서는 느려진다.

### `ember/server/src/channels/mention.rs` (68줄)

- `parse_mentions` (`:28`): `@이름`은 단어 시작에서만 유효하다. 앞이 영숫자, `_`, `-`, `.`, `@`이면 무시해 이메일과 `@@`(세션 작성기 멘션)를 피한다. 이름 문자는 영숫자, `_`, `-`와 뒤에 이름 문자가 오는 `.`. 에이전트 이름과 대소문자 무시로 정확히 일치해야 하고 접두사는 불일치다. 같은 이름의 에이전트가 여럿이면 모두 멘션된다 (`:49-56`). 공백이 든 이름은 멘션할 수 없다.

### `ember/server/src/guest_door.rs` (약 303줄, 테스트 없음)

- 목적: 둘째 리스너 설정, 보호 계층 조립, `/join` 페이지, 초대 링크 계산. 환경 변수 표가 머리 주석에 있다 (`:6-13`).
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `GuestDoor` | 구조체 | 149 | `listen`, `public_url`, 허용 호스트, 신뢰 프록시 |
  | `from_env`, `from_lookup` | 함수 | 161, 166 | `DoorEnv::parse`에 소유자 주소(`EMBER_LISTEN`)를 충돌 검사용으로 넘김 |
  | `wrap`, `wrap_limited`, `limits`, `build` | 함수 | 187, 194, 199, 203 | `wrap`은 한도 없음(테스트용). 서비스하는 쪽은 `wrap_limited` |
  | `build_join_page_from`, `join_page` | 함수 | 125, 142 | 페이지와 CSP 해시. `OnceLock`에 한 번 |
  | `invite_link` | 함수 | 267 | 문이 꺼져 있으면 `/join#<token>`, 켜져 있고 공개 URL이 있으면 `<url>/join#<token>`, 공개 URL이 없으면 `http://<listen>/join#<token>`과 `link_warning` |
  | `status_body` | 함수 | 287 | `GET /api/guest-door` 본문 |
  | 상수 | | 59-89 | 한도 숫자, `MAX_BODY_BYTES`=16 KiB, `REQUEST_TIMEOUT`=10초 |

- 나머지는 `door/`의 재노출이다 (`:48-52`). 상수 일부를 `door/limits.rs`가 거꾸로 import해 순환이 있다 ([server-collab.md](server-collab.md) 공개 인터페이스 표).

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/server/src/guest_door/join.html` | 49 | 이름 입력, 채팅, 종료 화면 3개 섹션. `<style>` 1개, `__JOIN_JS__` 자리에 스크립트 치환 (`:48`). 화면 문구는 한국어 |
| `ember/server/src/guest_door/join.js` | 274 | 게스트 페이지 스크립트. DOM 텍스트는 `textContent`만 (`:121-130`). 토큰은 `location.hash`에서 읽고 즉시 `history.replaceState`로 주소창에서 지운다 (`:253-254`). 자격은 `sessionStorage`에만 저장 (`:55`). `fetch`는 같은 출처, `credentials: "omit"` (`:104`). 3초 폴링 `poll` (`:145`), 429는 `Retry-After`와 지터로 후퇴, 노드 500개 유지 (`:12`, `:132`), 401은 `endInvitation` |
| `ember/server/src/guest_door/.gitattributes` | 2 | `join.html text eol=lf`, `join.js text eol=lf` |

### `ember/server/src/members.rs` (약 313줄, 그중 테스트 약 64줄, 테스트 6개)

- 목적: 팀원 정의(하네스 하나 + 계정 선택 하나 + 선택적 모델 프록시)와 세션 생성 (FR-A9, FR-U1, FR-U6).
- 주요 심볼

  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MIGRATION` | 상수 | 24 | `session_proxy(session_id PK, endpoint, key_env)` |
  | `MemberDef`, `ProxySpec`, `ResolvedMember`, `AccountChoice` | 타입 | 63, 45, 79, 56 | 고정 계정 또는 파이프라인 중 정확히 하나 |
  | `parse_harness` | 함수 | 86 | `claude-code`, `claude`, `agy`, `antigravity`, 그 외는 `AgentKind::parse` |
  | `MemberDef::resolve` | 함수 | 96 | 계정 선택 검사, 프록시가 있으면 하네스 지원 여부를 `proxy_env`로 검사 |
  | `proxy_env` | 함수 | 122 | endpoint는 `http(s)://`만. Claude Code는 `ANTHROPIC_BASE_URL`+`ANTHROPIC_AUTH_TOKEN`, Codex와 Antigravity는 각자 상수 변수. 키는 `key_env`가 가리키는 서버 환경 변수에서 읽고 없으면 `ember-proxy`. 그 외 하네스는 `Unsupported` |
  | `install` | 함수 | 204 | 시작 훅 등록. 세션 시작 때 `session_proxy`를 읽어 `proxy_env`를 실제 환경 변수 조회로 실행한다 (`:209`, `main.rs:210`) |
  | `create_member_session` | 함수 | 224 | 파이프라인이면 프로젝트의 하네스별 계정 재정의(FR-L20)를 요청 계정으로 쓰고, 세션 생성 후 프록시를 저장 |

- 사용처: `a2a/team.rs:840`, `:855` (`spawn_teammate`)가 유일한 호출자다. `session_proxy`, `set_session_proxy`는 `members.rs` 밖에서 호출되지 않는다 (grep).
- 주의점: 키 값은 DB에 저장하지 않고 환경 변수 이름만 저장한다 (`:11-13`).

## 동작 지도

### 소유자 라우트 (서버 토큰, `channels/api.rs:148-165`)

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `GET/POST /api/channels` | `api.rs:199`, `:203` | `mod.rs:367` `channels`, `:392` `create_channel` | `channels`, `channel_agents` |
| `GET /api/channels/{id}` | `api.rs:207` | `mod.rs:386` `channel` | 위 + `channel_messages`(최근 200) |
| `GET/POST /api/channels/{id}/messages` | `api.rs:216`, `:231` | `mod.rs:538`, `:443`, JSONL `jsonl.rs:202` | `channel_messages`, `<id>.jsonl` |
| `POST /api/channels/{id}/post` (런타임 토큰) | `api.rs:283` | `a2a/channel.rs:234` `check_channel_post`, `mod.rs:443` | `channel_messages` |
| `POST /api/channels/{id}/read` | `api.rs:346` | `mod.rs:267` | `channel_reads` |
| `POST /api/channels/{id}/mentions/preview` | `api.rs:360` | `mod.rs:544` | 없음 |
| `GET /api/channels/{id}/feed` | `api.rs:370` | `feed.rs:164` | 세션 이벤트 |
| `POST .../feed/{approval_id}/answer` | `api.rs:381` | `feed.rs:246` + 세션 승인 | 세션 |
| `POST .../questions/{question_id}/answer` | `api.rs:397` | `feed.rs:256` + `resolve_question_body` | 세션 |
| `GET/POST /api/channels/{id}/invites` | `api.rs:452`, `:426` | `invites.rs:193`, `:160` | `channel_invites` |
| `DELETE .../invites/{invite_id}` | `api.rs:456` | `invites.rs:205` | `channel_invites` |
| `GET /api/channels/{id}/guests` | `api.rs:464` | `allowance.rs:135` | `channel_guests` |
| `PUT/DELETE .../guests/{gid}/allow` | `api.rs:470`, `:481` | `allowance.rs:72`, `:107` | `channel_guests.allow_until` |
| `DELETE .../guests/{gid}` | `api.rs:489` | `allowance.rs:121` | `channel_guests.revoked_at` |
| `GET /api/guest-door` | `api.rs:448` | `guest_door.rs:287` | 없음 |

### 게스트 문 라우트

[게스트 문 보안 경계](#게스트-문-보안-경계)의 표가 전부다.

### 사용자에게 보이는 에러 메시지

| 원문 | 위치 | 조건 |
|---|---|---|
| `channel name must not be empty` | `channels/mod.rs:395` | 채널 이름이 공백 |
| `channel name must not contain a control, format or line-separator character` (`invalid_name`) | `channels/mod.rs:402` | 이름에 금지 문자 |
| `not a member of this channel: <names>` (400, `not_a_member`) | `channels/mod.rs:91` | 멘션이 멤버 에이전트가 아님 |
| `message text must not be empty` | `channels/mod.rs:445`, `guest.rs:173` | 빈 메시지 |
| `message text must be at most 8192 bytes` | `guest.rs:176` | 게스트 메시지 초과 |
| `at most 10 posts per minute` (429 `rate_limited`) | `guest.rs:221` | 게스트 분당 한도 |
| `a guest may post at most 500 messages in a channel` (429 `quota_exceeded`) | `guest.rs:396` | 게스트 채널당 500개 |
| `missing or invalid guest credential` (401) | `guest.rs:285` | 자격 없음, 만료, 해지 |
| `invite not found` (404) | `invites.rs:273` | 초대가 없음, 사용됨, 해지, 만료 (구분하지 않음) |
| `ttl_hours must be a whole number from 1 to 168` | `invites.rs:168` | 초대 TTL 범위 밖 |
| `name must be 1 to 64 characters ...`, `that name is reserved in this channel` | `invites.rs:113-124` | 게스트 이름 |
| `hours must be a whole number from 1 to 168` (`invalid_hours`) | `allowance.rs:52` | 허용 시간 잘못됨 |
| `host not allowed`, `origin not allowed` (403) | `door/harden.rs:123-128` | 게스트 문 Host, Origin 검사 |
| `body too large` (413), `no upgrade here` (400), `request timed out` (408) | `door/harden.rs:141`, `:145`, `:54` | 문 계층 |
| `guest @x's mention to @a was not delivered (no active allowance)` (`system` 메시지) | `guest.rs:494` | 허용 없이 게스트가 멘션 |
| 화면: `이 초대 링크는 사용할 수 없습니다. 이미 사용했거나 기간이 지났을 수 있습니다.` | `join.js:241` | accept가 400 이외로 실패 |
| 화면: `초대가 종료되었습니다. 채널 소유자에게 새 초대 링크를 요청하세요.` | `join.js:92` | 401 |

## 데이터와 설정

### 테이블 (모두 `ember.db`, 마이그레이션 등록은 `store.rs:151-157`)

| 테이블 | 열 | 정의 |
|---|---|---|
| `channels` | `id`, `project`(FK `projects.name`), `name`, `is_default`, `created_at`. 프로젝트당 기본 채널 1개 부분 유니크 인덱스 | `channels/mod.rs:30-37` |
| `channel_agents` | `(channel_id, session_id)` PK. `session_id`에 FK 없음 | `mod.rs:38-42` |
| `channel_messages` | `seq` AUTOINCREMENT(전 채널 공통), `channel_id`, `author`, `body`, `at`(ms), `mentions`(JSON 배열) | `mod.rs:43-50`, `:66-68` |
| `channel_reads` | `(channel_id, reader)` PK, `last_seq`. `reader`는 `user`뿐 | `mod.rs:55-62` |
| `channel_invites` | `token_hash UNIQUE`, `created_by`, `expires_at`, `used_at`, `revoked_at` | `invites.rs:17-27` |
| `channel_guests` | `invite_id`, `name`, `credential_hash UNIQUE`, `expires_at`, `revoked_at`, `allow_until` | `invites.rs:28-39` |
| `session_proxy` | `session_id` PK, `endpoint`, `key_env` | `members.rs:24-30` |

### 파일

- `<data dir>/channels/<channel id>.jsonl`: 사람 메시지, 디렉터리 0700, 파일 0600, 상한 1 GiB (`jsonl.rs:41`).
- 저장된 비밀은 해시뿐이다. 평문 초대 토큰은 `create_invite` 응답에만, 평문 자격은 `accept` 응답과 게스트 브라우저 `sessionStorage`에만 있다.

### 환경 변수 (게스트 문, `guest_door.rs:6-13`, `:54-58`)

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_GUEST_LISTEN` | `guest_door.rs:54` | 문의 `ip:port`. 비면 문과 게스트 라우터를 만들지 않음 | 없음 (꺼짐) |
| `EMBER_GUEST_LISTEN_ALLOW_REMOTE` | `guest_door.rs:55` | `1`이면 비 loopback 바인드 허용 (경고 로그) | 없음 |
| `EMBER_GUEST_TRUSTED_PROXIES` | `guest_door.rs:58` | `X-Forwarded-For`를 믿을 피어 IP 목록 | 없음 |
| `EMBER_GUEST_ALLOWED_HOSTS` | `guest_door.rs:56` | `Host`로 허용할 호스트 이름 | 없음 |
| `EMBER_GUEST_PUBLIC_URL` | `guest_door.rs:57` | 초대 링크의 기준 URL, 그 호스트도 허용 | 없음 |

`proxy_env`가 읽는 환경 변수는 팀원이 `key_env`로 지정한 이름이다 (`members.rs:209`).

## 이 모듈을 수정할 때 주의할 점

- 게스트 라우트를 추가하면 `GUEST_ROUTES` (`channels/guest.rs:74`)에도 넣는다. 테스트가 어긋남을 잡는다. 인증이 필요한 라우트는 `protected` 라우터(`guest.rs:258-262`)에 넣어야 `require_guest`가 걸린다. `accept`가 있는 바깥 라우터에 넣으면 인증 없이 열린다.
- 문의 보호 계층 순서는 `door::harden::stack` 한 곳에 있다. `GuestDoor::build`에서 계층을 직접 얹지 않는다.
- `join.html`/`join.js`를 고치면 CSP 해시가 시작 시 다시 계산된다. 외부 스크립트, 인라인 이벤트 핸들러, 추가 `<style>` 블록은 CSP가 막는다. `<style>`은 정확히 하나여야 한다 (`guest_door.rs:128-130`의 `expect`).
- `.gitattributes`의 LF 고정을 지우지 않는다. `normalize_eol`이 있어 해시는 맞지만 두 장치가 함께 있다.
- 게스트 메시지의 `author`/`name` 규칙(`guest_view`)이 세션 id 노출 방지를 맡는다. 게스트에게 새 필드를 주면 id, 경로, 하네스가 새지 않는지 본다.
- 한도 숫자는 세 곳에 따로 있다: 서버 상수(`guest.rs:82-93`), 문 상수(`guest_door.rs:59-78`), 페이지 상수(`join.js:10-12`). 메시지 8192바이트는 `a2a/mcp.rs:35`에도 있다.
- 복구 순서: `JsonlLog::recover`는 라우터 생성 전에 동기로 실행해야 한다 (`jsonl.rs:224-232`). `main.rs`에서 비동기로 옮기거나 라우터 뒤로 보내지 않는다.
- 채널 테이블을 바꾸면 `store.rs:151-157`의 마이그레이션 순서(`members::MIGRATION`, `channels::MIGRATION`, `READS_MIGRATION`, `MENTIONS_MIGRATION`, `invites::MIGRATION`)가 이어진다. 기존 마이그레이션을 편집하지 않고 뒤에 붙인다.
- 팀원 프록시 규칙을 바꾸면 `a2a/team.rs:840-845`의 호출 쪽과 어댑터의 `PROXY_*` 상수(`agents/codex`, `agents/antigravity`)를 함께 본다. 새 하네스는 `proxy_env`에서 `Unsupported`로 기본 거부된다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 높음 | `members.rs:122-170`, `:204-211`, `a2a/team.rs:840-845` | 에이전트가 `spawn_teammate`로 보내는 `proxy.endpoint`와 `proxy.key_env`가 이 파일에서 검증 없이 `session_proxy`에 저장되고, 세션 시작 시 `std::env::var(key_env)`의 값(서버 프로세스의 임의 환경 변수, 값은 `***`로 가림)이 `ANTHROPIC_AUTH_TOKEN` 등으로 해당 endpoint를 향한 하네스에 주입된다. endpoint는 어떤 `http(s)` URL이든 된다. 허용 목록은 이 파일에 없다. `team.rs` 쪽 검사는 읽지 않았다 `[확인 필요]` | `key_env`를 접두사 허용 목록(예: `EMBER_PROXY_KEY_*`)으로 제한하고, 에이전트발 `proxy`는 소유자 승인이나 설정된 endpoint 목록으로 제한 |
| 버그 | 낮음 | `join.js:123` | `new Date(m.at)`는 밀리초를 기대하나 서버의 `GuestMessage.at`은 초 단위다 (`channels/mod.rs:187`, `guest.rs:135-159`). 게스트 화면의 시각이 1970년 1월 기준으로 표시된다. 테스트 `fr_t14_guest_join_page.rs`가 시각을 보는지 `[확인 필요]` | `m.at * 1000`으로 변환 |
| 일관성 | 중간 | `channels/api.rs:123-138`, `channels/guest.rs:236-248` | 소유자 라우터와 게스트 라우터가 각자 `JsonlLog`(각자의 잠금)를 만든다. 소유자 글과 게스트 글이 동시에 오면 파일의 `seq` 순서가 어긋날 수 있다. 복구는 마지막 줄의 `seq`만 보므로, 순서가 뒤바뀐 파일에서는 이미 있는 행을 다시 추가할 수 있다 `[확인 필요]` | 하나의 `Arc<JsonlLog>`를 `main.rs`에서 공유하거나, 복구가 파일의 `seq` 집합을 보게 한다 |
| 보안 | 낮음 | `guest_door.rs:9` | 문은 평문 HTTP다. 비 loopback으로 열 때 TLS는 전적으로 소유자 몫이고, 서버는 자격(`dpg_`)이 도청되는지 알 수 없다 | `ALLOW_REMOTE` 경고(`main.rs:367`)에 TLS 필요를 명시 |
| 보안 | 낮음 | `guest.rs:212-228`, `:551-568` | 게스트 글 한도(분당 10)와 전달 한도(시간당 20)는 메모리에만 있어 서버 재시작 때 초기화된다. 주소별 한도도 메모리다 | 허용된 위험으로 문서화 (주석에 이미 있음) |
| 성능 | 낮음 | `guest.rs:135-159` | 메시지마다 `channel_guests`를 조회한다(게스트 작성자 이름). 최대 500개 읽기에서 N+1 | `annotate`처럼 한 번에 읽기 |
| 성능 | 낮음 | `feed.rs:197` | `channel_feed`가 호출마다 멤버 세션의 모든 이벤트를 `events_after(id, 0)`으로 재생 | 보고 시점 이후 이벤트만 읽거나 캐시 |
| 중복 | 낮음 | `join.js:10-12`, `guest.rs:82` | 8192바이트, 폴링 상수 등이 JS와 Rust에 따로 있다 | 변경 시 함께 수정 (위 주의점) |
| 정리 | 낮음 | `channels/api.rs:101-146` | 생성자 5종이 겹친다. 프로덕션은 `router_with_a2a_door` 하나를 쓴다 (`main.rs:457`). 나머지가 테스트 전용인지 `[확인 필요]` | 빌더로 합치기 |
| TODO/FIXME | 없음 | 이 모듈 전체 | 대상 파일에 `TODO`, `FIXME`가 0개 (grep) | 해당 없음 |
