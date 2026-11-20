# 모듈: transfer

- 경로: `ember/transfer/` (크레이트 `ember-transfer`, `ember/transfer/Cargo.toml:2`)
- 규모: 파일 9개 / 약 2,200줄 (`Cargo.toml` 22, `src/*.rs` 8개 약 2,170)
- 레이어: 비즈니스 로직 (장치 쪽 라이브러리. 네트워크 입출력은 `ember-transport` 스트림 위에서만 한다)
- 한 줄 책임: 사용자 장치 사이 파일 전송의 제안(offer), 수락, 거절, 취소 핸드셰이크, 이름 정리, 크기 제한, 수신 모드, 청크 저장과 SHA-256 검증을 맡는다 (`ember/transfer/src/lib.rs:1`, SPEC `FR-F1`..`FR-F10`).
- 의존하는 모듈: `transport` (`ember/transfer/Cargo.toml:11`, `PeerId`, `BiStream`, `Connection`). 외부 크레이트는 `async-trait`, `getrandom`, `hex`, `serde`, `serde_json`, `sha2`, `thiserror`, `tokio` (`ember/transfer/Cargo.toml:12-19`).
- 이 모듈을 쓰는 모듈: `server-core`의 `ember/server/src/transfers.rs` 하나뿐이다 (`ember/server/Cargo.toml:17`). 거기서 쓰는 것은 `limits`, `mode`, `names`, `store`, `wire::DeclineCode`다 (`ember/server/src/transfers.rs:22-29`, `:302`). `session`, `state`는 크레이트 밖에서 쓰이지 않는다 (grep 확인, 이슈 후보 참조).

## 공개 인터페이스

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

## 파일별 요약

### `ember/transfer/src/lib.rs` (29줄)
- 목적: 모듈 선언(`limits`, `mode`, `names`, `session`, `state`, `store`, `wire`, `ember/transfer/src/lib.rs:18-24`), `SERVICE` 상수, `PeerId` 재노출.
- 주의점: 머리 주석이 현재 코드와 어긋난다. "First unit (status: written, not compiled)", "No file bytes move in this unit. Chunk streaming, resume, hashing and progress are the next unit"이라고 쓰지만 (`ember/transfer/src/lib.rs:6`, `:14-15`), 같은 크레이트에 청크 전송(`ember/transfer/src/session.rs:538`)과 `store` 모듈이 이미 있다.

### `ember/transfer/Cargo.toml` (22줄)
- 의존은 위와 같다. dev 의존은 `tempfile`, `tokio`(rt-multi-thread) (`ember/transfer/Cargo.toml:21-22`).

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/transfer/src/limits.rs` | 84 | `Limits { max_bytes }` (`:17`), `check_total` (`:29`, 한도와 같은 값은 통과), `check_offer` (`:38`, `checked_add`로 합산해 오버플로는 `LimitError::Overflow`). 테스트 5개 |
| `ember/transfer/src/mode.rs` | 65 | `ReceiveMode` 기본값 `Ask` (`:12`), `decide(peer, mode)` (`:29`). Off는 `Refuse`, AutoAcceptFrom은 선택한 장치에서만 `Accept`. 등록 장치, 크기, 이름 검사를 건너뛰지 않는 일은 호출자 책임이다 (`:3-4`). 테스트 3개 |

### `ember/transfer/src/names.rs` (400줄)
- 목적: 네트워크에서 온 이름을 신뢰하지 않고 정리한다 (`FR-F9`, `FR-F8`, #527).
- 규칙 (`ember/transfer/src/names.rs:3-12`, `clean_component` `:98-131`): `/`와 `\`로 쪼개 마지막 비어 있지 않은 성분만 취함, 첫 `:` 뒤(NTFS ADS) 제거, 제어 문자와 bidi 오버라이드와 zero-width와 줄/문단 구분자 제거, 앞뒤 점과 공백 제거, Windows 예약 장치명에 `_` 접두, 200바이트 상한(문자 경계).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `is_banned` | fn(비공개) | 31 | 금지 문자 판정 |
| `is_windows_reserved` | fn(비공개) | 44 | CON, PRN, AUX, NUL, COM1-9, LPT1-9 |
| `generated_name` | fn | 75 | `received-<8 hex>`. `getrandom` 실패 시 정적 카운터와 시각으로 대체 (`:29`, `:76-84`) |
| `clean_file_name` | fn | 133 | 한 파일명 정리, 비면 `generated_name` (`:133-138`) |
| `clean_relative_path` | fn | 144 | 폴더 상대 경로를 성분 벡터로. `.`, `..`, 빈 성분은 버리고 깊이 32, 길이 1024로 자른다 (`:141-143`) |
| `clean_offer_paths` | fn | 171 | 제안 전체를 정리하고 정리 후 중복 경로를 구별한다 (#527) |
| `resolve_destination` | fn | 222 | 기존 항목이 있으면 `name (1).ext` 식으로 번호를 붙인다. 부모 디렉터리가 파일과 충돌하면 `dir (n)` |
- 부수효과: 파일 시스템 조회(`symlink_metadata`, `entry_exists_in_dir` `:201`). 쓰기는 하지 않는다.
- 주의점: `clean_component`는 `:`가 있으면 그 앞만 남긴다 (`:100`). `C:` 같은 이름이면 빈 문자열이 되어 `generated_name`으로 대체된다. 테스트 15개.

### `ember/transfer/src/state.rs` (276줄)
- 목적: 상태 기계 (`FR-F3`, `FR-F4`). 상태는 Offered, Accepted, Receiving{bytes}, Done, Declined, Expired, Cancelled, Failed(String) (`ember/transfer/src/state.rs:59-68`). 이벤트는 Accept, Decline, Start, Progress(u64), Finish, Expire, Cancel, Fail (`:80-92`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Clock` | trait | 10 | 단조 시계. `SystemClock`(`:15`)과 시험용 `ManualClock`(`:39`) |
| `next` | fn | 105 | 순수 전이표. 허용되지 않으면 `TransitionError::Illegal` |
| `Transfer` | struct | 129 | `new(now, ttl)`, `apply(event, now)` (`:146`), `expire_if_due` (`:157`) |
| `TransitionError` | enum | 95 | `Illegal`, `Expired`, `ProgressWentBack` |
- 주의점: 응답 전에 기한이 지나면 `apply`가 `Expired`를 돌려준다 (`:96-97`). 수락된 전송은 만료되지 않는다 (테스트 `fr_f3_accepted_transfers_do_not_expire`, `:268`). 테스트 10개.

### `ember/transfer/src/wire.rs` (300줄)
- 목적: 프레임 = 4바이트 big-endian 길이 + JSON `{"v":1,"msg":{...}}`. `MAX_FRAME` 64 KiB를 넘으면 할당 전에 오류 (`ember/transfer/src/wire.rs:1-3`, `:13`).
- `Message` (`:42`): `Offer`, `Accept`, `Decline{code,detail}`, `Cancel`, `Chunk{id,file,offset,data,sha256}`, `ResumeFrom`, `Pause`, `Resume`, `Done{sha256}`. 머리 주석은 "Only Offer, Accept, Decline and Cancel exist in this unit (no chunks yet)"라고 하지만 (`:3-4`) 실제로는 Chunk 등이 정의돼 있다.
- `DeclineCode` (`:25`): User, Expired, NotRegistered, ReceiveOff, TooLarge, Invalid. 서버가 응답에 쓴다 (`ember/server/src/transfers.rs:29`).
- `read_message`, `write_message` (`:158`, `:183`)는 비동기 스트림용. 스트림이 깨끗이 끝나면 `Ok(None)`.
- 주의점: `Chunk.data`는 `Vec<u8>`이라 serde_json 기본으로는 숫자 배열로 직렬화된다 [추정]. 그러면 32 KiB 청크(`DEFAULT_CHUNK_BYTES`)가 64 KiB 프레임을 넘을 수 있다 (이슈 후보). 테스트 6개.

### `ember/transfer/src/session.rs` (577줄)
- 목적: 스트림 하나 위의 핸드셰이크. 수신 측 `Service::handle_stream` (`ember/transfer/src/session.rs:272`)과 송신 측 `Outgoing` (`:444`).
- 수신 검사 순서 (`:272-340`): 1) `PeerPolicy::is_registered`가 아니면 `NotRegistered` 2) 파일 없음, 파일 수 > `MAX_OFFER_FILES`, 합 오버플로, 합과 `total` 불일치는 `Invalid` 3) `Limits::check_total` 실패는 `TooLarge` 4) `clean_offer_paths`로 이름 정리, 그 결과가 `IncomingOffer`로 프롬프트에 보인다 5) `decide`: Off는 `ReceiveOff`, AutoAccept는 프롬프트 생략, Ask는 `Prompter::prompt`와 송신자 메시지를 `select!`로 경쟁시킨다 (`:347-370`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `PeerPolicy` | trait | 56 | `HashSet<PeerId>`에 구현 (`:60`) |
| `Prompter` | trait | 83 | 사용자에게 물어 `PromptAnswer`를 돌려준다 (async-trait) |
| `Service` | struct | 230 | `new`, `with_ttl`, `set_limits`, `set_mode`, `handle_stream` |
| `Handled` | struct | 94 | 결과. `state()`, `cancel()`, `receive_into(received_dir, limits)` (`:127`) |
| `Outgoing` | struct | 444 | `start(conn, files, clock, ttl)` (`:455`), `wait_answer` (`:486`), `wait_cancel`, `cancel`, `send_bytes` (`:538`) |
- `receive_into`는 수락된 스트림에서 `Chunk`를 받아 `ReceiveWriter`에 쓰고, 예상 밖 메시지면 `writer.abort()` 후 `Error::Protocol` (`:218-224`).
- `send_bytes`는 메모리에 있는 `&[&[u8]]` 전체를 받아 청크로 보낸다 (`:538`). 파일 스트리밍이 아니다.
- 부수효과: 스트림 입출력, OS 난수(`random_id` `:48`, 8바이트 hex).
- 테스트: 파일 안에 `#[test]`, `#[tokio::test]`가 0개다 (grep). 시험은 `ember/transfer/tests/session.rs`에 있다 (규칙상 읽지 않음).

### `ember/transfer/src/store.rs` (443줄)
- 목적: 수신 파일 저장 (`FR-F4`, `FR-F5`, `FR-F8`, `FR-F9`, `FR-F10`, #527). 수락 전에는 아무것도 쓰지 않는다. 청크는 `<received_dir>/.partial/<offer_id>/<idx>.part`로 흘려 쓴다 (`ember/transfer/src/store.rs:6-7`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `ReceiveWriter::open` | fn | 123 | 선언된 합계와 `Limits`를 먼저 확인, 기존 `.part`로 재개 가능 |
| `resume_offset` | fn | 194 | 파일별 검증된 바이트 오프셋 |
| `write_chunk` | fn | 207 | 오프셋 연속성, 파일별 선언 크기, 전체 한도, 청크 SHA-256 검사 후 `seek`와 `write_all` |
| `finalize` | fn | 261 | 크기와 SHA-256 최종 검증, `resolve_destination`으로 `rename`, 권한 0644 |
| `abort` | fn | 315 | `.partial` 삭제 (`FR-F4`) |
| `sha256_file` | fn | 337 | 32 KiB 단위 해시 |
| `HistoryRecord` | struct | 92 | 이력 행 (`id`, `name`, `device`, `direction`, `size`, `result`, `timestamp_ms`) |
- 부수효과: 디스크 쓰기, 디렉터리 생성과 삭제, `rename`.
- 주의점: `set_safe_file_mode`는 unix에서만 0644를 적용하고 그 외 OS는 아무것도 하지 않는다 (`:322-335`). `write_chunk`는 매 청크마다 파일을 열고 `flush`한다 (`:240-247`). `finalize`는 파일마다 전체를 다시 읽어 해시한다 (`:276`). 이력 저장 자체는 이 크레이트가 아니라 서버가 한다 (`ember/server/src/transfers.rs:26`). 테스트 4개.

## 동작 지도

라이브러리라 HTTP 라우트는 없다. 서버가 이 크레이트를 부르는 지점만 적는다.

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `GET /api/transfers/{id}/resume-offset/{file}` | `ember/server/src/transfers.rs:772` (`get_resume_offset`) | `resume_offset` (`ember/server/src/transfers.rs:434`) 안에서 `ReceiveWriter::open` (`:443`)과 `writer.resume_offset` (`:458`) | `.partial/<id>/<idx>.part` |
| 수락 시 쓰기 시작 | `ember/server/src/transfers.rs:376` | `ReceiveWriter::open` | 위와 같음 |

사용자에게 보이는 에러 메시지 (`DeclineCode`와 함께 송신자에게 간다. 원문):

| 원문 | 위치 | 조건 |
|---|---|---|
| `not a registered device` | `ember/transfer/src/session.rs:287` | 송신자가 등록 장치가 아님 |
| `the offer has no files` | `ember/transfer/src/session.rs:291` | 파일 0개 |
| `the offer has too many files` | `ember/transfer/src/session.rs:296` | 1024개 초과 |
| `the total is not the sum of the files` | `ember/transfer/src/session.rs:307` | 합계 불일치 |
| `the offer is {total} bytes, above the limit of {max} bytes` | `ember/transfer/src/limits.rs:9` | 한도 초과 |
| `the device does not receive files` | `ember/transfer/src/session.rs:350` | 수신 모드 Off |
| `SHA-256 mismatch for {name:?}: expected {expected}, got {got}` | `ember/transfer/src/store.rs:44` | 해시 불일치 |

## 데이터와 설정

- DB 없음. 저장 파일: `<received_dir>/.partial/<offer_id>/<idx>.part`(진행 중), 완료 파일은 `received_dir` 아래 (`ember/transfer/src/store.rs:6-12`).
- 환경 변수 없음. 설정은 호출자가 넣는다.

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `Limits.max_bytes` | `ember/transfer/src/limits.rs:4` | 제안 합계 한도 | 4 GiB |
| `ReceiveMode` | `ember/transfer/src/mode.rs:12` | 수신 정책 | `Ask` |
| `DEFAULT_OFFER_TTL` | `ember/transfer/src/session.rs:34` | 응답 대기 시간 | 60초 |
| `DEFAULT_CHUNK_BYTES` | `ember/transfer/src/store.rs:31` | 청크와 해시 버퍼 | 32 KiB |

- 외부 연동: `ember-transport`의 `BiStream`, `Connection`.

## 이 모듈을 수정할 때 주의할 점

- `wire::Message`를 바꾸면 `WIRE_VERSION`(`ember/transfer/src/wire.rs:11`)과 `session.rs`의 송수신 분기를 함께 고친다.
- 수신 검사 순서(등록, 형식, 크기, 이름, 모드)는 프롬프트 전에 거절한다는 보장(`FR-F9`, `FR-F10`)에 묶여 있다 (`ember/transfer/src/session.rs:5-12`). 순서를 바꾸지 않는다.
- 서버가 쓰는 `store`, `names`, `limits`, `mode`, `wire::DeclineCode`의 시그니처를 바꾸면 `ember/server/src/transfers.rs`를 고치고, 서버를 쓰는 `ember/client/`와 서버의 `Cargo.lock`을 같은 PR에서 갱신한다 (AGENTS.md).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 미사용 코드 | 중간 | `ember/transfer/src/session.rs`, `ember/transfer/src/state.rs` | `Service`, `Outgoing`, `Handled`, `Prompter`, `Transfer`, `State`가 크레이트 밖에서 쓰이지 않는다 (`ember/server`의 import는 `limits`, `mode`, `names`, `store`, `wire::DeclineCode`뿐). 서버는 같은 일을 `ember/server/src/transfers.rs`에서 따로 구현한다 | 서버가 `session`을 쓰게 합치거나 미사용임을 문서에 남긴다 |
| 중복 | 중간 | `ember/server/src/transfers.rs:302`, `ember/transfer/src/session.rs:296` | 파일 수 검사가 양쪽에 있다 | 한쪽으로 통일 |
| 문서 불일치 | 낮음 | `ember/transfer/src/lib.rs:6`, `:14`, `ember/transfer/src/wire.rs:3` | "written, not compiled", "No file bytes move", "Only Offer, Accept, Decline and Cancel" 주석이 현재 코드와 다르다 | 주석 갱신 |
| 미사용 pub | 낮음 | `ember/transfer/src/wire.rs:42` | `ResumeFrom`, `Pause`, `Resume` 메시지는 크레이트 밖 사용 0 (grep) | 쓸 때까지 보류 표시 |
| 이식성 | 중간 | `ember/transfer/src/store.rs:322-335` | 비 unix에서 파일 권한 처리가 없다. Windows 노드가 받은 파일은 `FR-F9`의 0644 문구와 다르다 | 요구 문구에 OS별 범위를 적는다 |
| 한계 | 중간 | `ember/transfer/src/wire.rs:13`, `:42` | `Chunk.data: Vec<u8>`이 JSON 숫자 배열이면 32 KiB 청크가 `MAX_FRAME` 64 KiB를 넘을 수 있다 [추정, 확인 필요] | 청크 크기와 프레임 크기 관계를 테스트로 고정하거나 base64로 |
| 메모리 | 낮음 | `ember/transfer/src/session.rs:538` | `send_bytes`가 파일 전체를 메모리 슬라이스로 받는다 | 스트리밍 API |
| 경쟁 조건 | 낮음 | `ember/transfer/src/names.rs:222`, `ember/transfer/src/store.rs:287` | 존재 확인 후 `rename`까지 사이에 같은 이름이 생길 수 있다 | `create_new` 기반으로 |
| 성능 | 낮음 | `ember/transfer/src/store.rs:240-247` | 청크마다 파일을 다시 열고 `flush` | 핸들 유지 |
| TODO/FIXME | 낮음 | `ember/transfer/src/` | 0개 (grep) | 없음 |
