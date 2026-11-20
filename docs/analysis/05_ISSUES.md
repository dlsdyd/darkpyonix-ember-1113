# 문제점

- 기준 커밋: `ffe9825` / 작성: 2026-11-13
- 출처 열: "분석 세션"은 분석 중 직접 확인한 것, "모듈 문서"는 각 모듈 문서의 "이슈 후보" 표, "주의점 발췌"는 이슈 표가 없는 모듈 문서의 "주의할 점" 중 보안·중복·미구현 등의 낱말로 골라낸 것(분류와 심각도는 자동으로 붙였다).
- 심각도: **높음** 보안 문제나 데이터 손상 가능성, **중간** 버그 유발 가능성이나 수정 시 혼란, **낮음** 정리하면 좋은 것.
- 비밀값은 위치만 적었다. 이 문서 어디에도 실제 값은 없다.

## 요약

| 심각도 | 개수 |
|---|---|
| 높음 | 5 |
| 중간 | 76 |
| 낮음 | 137 |

| 분류 | 개수 |
|---|---|
| 보안 | 42 |
| 죽은 코드 | 21 |
| 거대 파일 | 19 |
| 하드코딩 | 16 |
| 중복 | 10 |
| TODO/FIXME | 8 |
| 중복 구현 | 7 |
| 구조 | 6 |
| 기능 미구현 | 4 |
| 문서 불일치 | 4 |
| 정확성 | 4 |
| 이식성 | 4 |
| TODO | 4 |
| 견고성 | 3 |
| 성능 | 3 |
| 죽은 경로 | 2 |
| 순환 의존 | 2 |
| 오류 은닉 | 2 |
| 기능 공백 | 2 |
| 안정성 | 2 |
| 일관성 | 2 |
| 테스트 | 2 |
| 메모리 | 2 |
| 중복 로직 | 2 |
| 중복 정의 | 2 |
| 기능 누락 | 2 |
| 사용하지 않는 pub | 2 |
| 확인 불가 | 2 |
| 미완 기능 | 1 |
| 종료 | 1 |
| 접근성 | 1 |
| 중복 상수 | 1 |
| 중복 데이터 | 1 |
| 모순 문구 | 1 |
| 모의 동작 | 1 |
| 가짜 설정 | 1 |
| 미구현 기능 | 1 |
| 의존자 없음 | 1 |
| 죽은 코드 후보 | 1 |
| 동시성 | 1 |
| 사용되지 않는 심볼 | 1 |
| 미사용 코드 | 1 |
| 한계 | 1 |
| 시그니처 | 1 |
| 기능 갭 | 1 |
| 문구 분산 | 1 |
| 검토 훅 | 1 |
| 사용량 | 1 |
| 데모 상수 | 1 |
| 결합 | 1 |
| 중복 문구 | 1 |
| 쓰이지 않는 심볼 | 1 |
| 비용 | 1 |
| 검증 | 1 |
| 직렬화 일관성 | 1 |
| 타입 | 1 |
| 언어 혼용 | 1 |
| 테스트 위치 | 1 |
| 패닉 | 1 |
| 문서 | 1 |
| 시험 | 1 |
| 버그 | 1 |
| 정리 | 1 |
| 미사용 pub | 1 |
| 경쟁 조건 | 1 |

## 이슈 목록

| ID | 분류 | 심각도 | 모듈 | 위치 | 내용 | 권장 조치 | 출처 |
|---|---|---|---|---|---|---|---|
| I-001 | 죽은 경로 | 높음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `conversation.rs:567-692`, `1073-1199`, `session.rs:2467` | 라이브에서 대화 화면은 `embedded = true`뿐이라 고정, 내보내기, 마지막 턴에서 포크, 컴퓨터 전환, 대화 화면의 IDE 줄이 도달 불가 | 싱글 뷰 헤더에 같은 메뉴를 연결하거나 코드를 제거 | 모듈 문서 |
| I-002 | 기능 미구현 | 높음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:3952-4034` | 새 팀원 시트의 "첫 지시", "컴퓨터" 선택, 하네스/모델/모드 칩이 요청에 반영되지 않는다. `agent`는 `"claude-code"` 고정, 컴퓨터 목록은 `["mac-mini","mac-studio","이 컴퓨터"]` 하드코딩 (`:3975`) | 서버의 에이전트와 컴퓨터 목록으로 채우고 필드를 `CreateSession`에 전달 | 모듈 문서 |
| I-003 | 보안 | 높음 | [server-accounts](modules/server-accounts.md) | `ember/server/src/accounts/secrets.rs:158-161`, `accounts/mod.rs:705-716` | 비 unix(Windows)에서는 `secret.key` 권한 검사(`check_private`)가 아무것도 하지 않고 계정 디렉터리 0700도 설정되지 않는다. 이 저장소의 개발 환경이 Windows이므로 암호화 키 파일이 다른 사용자에게 읽힐 수 있다 | Windows ACL 설정과 검사 추가 | 모듈 문서 |
| I-004 | 보안 | 높음 | [server-collab](modules/server-collab.md) | `ember/server/src/members.rs:209`, `ember/server/src/members.rs:122-170`, `ember/server/src/a2a/team.rs:252-254`, `:844` | 팀원 생성 요청(A2A `team spawn`, 에이전트가 보낼 수 있다)의 `proxy.key_env`가 가리키는 서버 환경 변수를 `std::env::var`로 읽어, 임의의 `http(s)` `endpoint`와 함께 새 에이전트의 API 키 변수로 넣는다. 허용 목록이 없다. 에이전트 프로세스가 원래 서버 환경을 물려받는지에 따라 영향이 달라진다 [확인 필요] | `key_env`를 정해진 접두사(예: 사용자가 등록한 키 이름)로 제한하고, endpoint 허용 목록을 둔다 | 분석 세션 |
| I-005 | 보안 | 높음 | [server-collab-2](modules/server-collab-2.md) | `members.rs:122-170`, `:204-211`, `a2a/team.rs:840-845` | 에이전트가 `spawn_teammate`로 보내는 `proxy.endpoint`와 `proxy.key_env`가 이 파일에서 검증 없이 `session_proxy`에 저장되고, 세션 시작 시 `std::env::var(key_env)`의 값(서버 프로세스의 임의 환경 변수, 값은 `***`로 가림)이 `ANTHROPIC_AUTH_TOKEN` 등으로 해당 endpoint를 향한 하네스에 주입된다. endpoint는 어떤 `http(s)` URL이든 된다. 허용 목록은 이 파일에 없다. `team.rs` 쪽 검사는 읽지 않았다 `[확인 필요]` | `key_env`를 접두사 허용 목록(예: `EMBER_PROXY_KEY_*`)으로 제한하고, 에이전트발 `proxy`는 소유자 승인이나 설정된 endpoint 목록으로 제한 | 모듈 문서 |
| I-006 | 문서 불일치 | 중간 | [app-core](modules/app-core.md) | `ember/app/README.md:36-37` | README는 dioxus-compose를 `branch = "develop"`로 쓴다고 하나 `Cargo.toml`은 `tag v0.0.6`과 `rev`로 고정한다 | README 갱신 | 모듈 문서 |
| I-007 | 거대 파일 | 중간 | [app-core](modules/app-core.md) | `ember/app/src/demo.rs` (3,025줄) | 데이터, 상태 기계, 가짜 git, 테스트 59개가 한 파일. 프로덕션 코드가 데모 분기를 가진다 | `demo/` 하위 모듈로 분리 | 모듈 문서 |
| I-008 | 순환 의존 | 중간 | [app-core](modules/app-core.md) | `prefs.rs`, `model.rs`, `ide.rs`, `editor_host.rs` | 하위 계층이 UI 타입 (`ThemePref`, `ProjectPanes`, `CharStyle`, `Keymap`, `EditorTarget`, `FileDiff`)에 의존 | 공용 타입을 UI 밖으로 이동 | 모듈 문서 |
| I-009 | 죽은 경로 | 중간 | [app-core](modules/app-core.md) | `bridge.rs:42-87`, `use_bridge`(`:104`), `services.rs:236` `run`, `Services.live` | Dioxus 루트 `ui::app`이 호출되지 않아 `Live`, `use_bridge`, `live` 분기가 기본 실행에서 동작하지 않는다. `run`의 이 모듈 밖 호출은 확인하지 못했다 | 옛 UI 정리 때 함께 제거 [확인 필요] | 모듈 문서 |
| I-010 | 오류 은닉 | 중간 | [app-core](modules/app-core.md) | `bridge.rs:468-537` | 계정, 사용량, 에이전트, 컴퓨터 새로고침 실패가 `tracing::debug!`로만 남고 UI는 모른다. `chatgpt_accounts`는 실패를 빈 목록으로 삼킨다 (`:484`). 기본 로그 수준 `warn`에서는 보이지 않는다 | 연결 배너 등으로 표면화 | 모듈 문서 |
| I-011 | 미완 기능 | 중간 | [app-core](modules/app-core.md) | `terminal_stream.rs:724` (TODO #334), `:827` (TODO #336) | PTY 크기가 80x24로 고정, 재연결과 프로토콜 오류 표시 없음 (파싱 못한 프레임은 로그만) | 이슈대로 구현 | 모듈 문서 |
| I-012 | 종료 | 중간 | [app-core](modules/app-core.md) | `lib.rs:64-68`, `:101-102` | 콘솔 없는 Windows 빌드에서 `eprintln!` 후 종료하면 사용자는 아무것도 보지 못한다 [추정] | 대화 상자나 로그 파일 | 모듈 문서 |
| I-013 | 죽은 코드 | 중간 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/mod.rs` | pub 항목 14개 모두 Dioxus 트리 안에서만 쓰인다 | #226 정리 때 파일째 삭제 검토 | 모듈 문서 |
| I-014 | 하드코딩 | 중간 | [app-ui-cr](modules/app-ui-cr.md) | `ember/app/src/ui/cr/shell.rs:285`, `home.rs:1073-1074`, `ember/app/src/ui/shell.rs` (`DEMO_USER = ("BREW","ncmnd")`) | 실제 서버에 연결해도 사이드바 사용자 행과 홈 인사말이 데모 사용자 이름 "BREW"를 그린다. 주석은 "mockup greets the signed-in user by name" (`home.rs:1072`) | 로그인한 사용자 이름이 있는 곳에서 읽거나, 데모가 아니면 이름 없는 인사로 | 모듈 문서 |
| I-015 | 중복 | 중간 | [app-ui-cr](modules/app-ui-cr.md) | `cr/theme.rs`와 `ember/app/src/ui/theme.rs` | 팔레트, 타입, 간격 토큰이 두 벌 (3.2절), 테스트가 각각 고정 | phase 8까지 같이 수정하는 체크리스트 유지, 삭제 후 한 벌로 | 모듈 문서 |
| I-016 | 접근성 | 중간 | [app-ui-cr](modules/app-ui-cr.md) | `cr/a11y.rs:1-8`, 사용처 `project.rs`뿐 | 아이콘 전용 버튼(테마, 설정, 메뉴, 멤버, 첨부, 이모지 등)에 접근성 이름이 없다 (compose-rust#460). 상수는 12개이나 쓰이는 것은 2개, `rail_labels()`는 테스트에서만 호출 | 툴킷이 라벨 modifier를 지원하면 일괄 적용 | 모듈 문서 |
| I-017 | 하드코딩 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:4009-4013` | 새 팀원의 `cwd` 기본값 `"/work"` | 프로젝트 설정의 작업 경로 사용 | 모듈 문서 |
| I-018 | 하드코딩 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:284`, `:2093` | 모델 칩에 " · 높음" 고정 접미사, 정보 패널 컴퓨터 이름이 모르면 `"mac-mini"` | 실제 값 사용, 없으면 빈 표시 | 모듈 문서 |
| I-019 | 기능 미구현 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:324-333` | 모델 선택 불가 ("준비 중입니다") | SPEC FR-L15 상태 확인 [확인 필요] | 모듈 문서 |
| I-020 | 기능 미구현 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `project.rs:374-378` | 비데모에서 "새 프로젝트" 비활성 (`can_create = demo`), 서버 생성 코드(`:1340`)는 데모가 아닐 때 도달 불가 | 활성 조건 재검토 | 모듈 문서 |
| I-021 | 기능 미구현 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `project.rs:1627-1628`, `1592` | 보관/삭제/리더가 빈 핸들러 (TODO #384) | 서버 지원 후 연결 | 모듈 문서 |
| I-022 | 중복 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `conversation.rs:316`, `session.rs:1235` | 전송, 중단 로직 복제 | 공용 함수로 추출 | 모듈 문서 |
| I-023 | 거대 파일 | 중간 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs` 5,180줄 | 3개 뷰, 시트, 타임라인, 상태 카드가 한 파일. `ConversationView`도 1,000줄짜리 함수 하나 (`conversation.rs:155-1200`) | 뷰별 파일 분리 | 모듈 문서 |
| I-024 | 중복 상수 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `routines.rs:59,60,62` vs `ember/app/src/ui/routines.rs:1041,1042,913` | `RUN_NOTICE`, `NO_CWD_NOTICE`, `RUNS_SHOWN`이 두 모듈에 같은 값으로 정의된다. `ui/routines.rs`는 `pub`, cr 쪽은 `const`. 테스트가 두 문자열을 모두 점검한다 (`routines.rs:3218-3219`) | cr 쪽을 `pub use crate::ui::routines::{RUN_NOTICE, NO_CWD_NOTICE}`로 바꾼다 | 모듈 문서 |
| I-025 | 중복 데이터 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:1249-1310` vs `ember/app/src/ui/home.rs:834-844` (`model_catalog`) | 모델 카탈로그(id, 이름)가 두 군데 있다 (`opus`/"Opus 5.5", `gpt-5-codex`, `gemini-2.5-pro` 등). 에이전트 화면 쪽은 노트와 플랜 정보를 더 가진다. 홈과 화면이 어긋날 수 있다 | `home::model_catalog`를 단일 출처로 하고 플랜 정보만 따로 둔다 | 모듈 문서 |
| I-026 | 모순 문구 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `ember/app/src/ui/agents.rs:21-22` (`LOCAL_STORE_NOTE`: 서버 저장은 준비 중입니다 (#670)) vs `:1023` (`DEFAULTS_STORAGE_NOTE`: 서버에 저장되어 새 팀원에 적용됩니다) | 기본값은 서버에 저장되고 나머지는 로컬뿐인데, 화면에 로컬 안내를 그리는 `LocalNote`(`agents.rs:829`)는 호출처가 없다 (grep 확인). 사용자는 어떤 설정이 서버에 저장되는지 알 수 없다 | `LocalNote`를 프로필, 샌드박스, shim 행 옆에 다시 붙이거나 삭제한다 | 모듈 문서 |
| I-027 | 모의 동작 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:1980,2141,2177,2277` | 프로필 하네스, 고정 계정, 기본 프로필, 실패 시 동작 고르기는 "…을 선택합니다" 알림만 띄우고 아무것도 고르지 못한다. `MockSwitch`(`agents.rs:514`)라는 이름도 목업 흔적이다 | 선택 시트를 구현하거나 버튼을 비활성화하고 "준비 중입니다"로 표시 | 모듈 문서 |
| I-028 | 가짜 설정 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:2353`, `agents.rs:2291-2296` | "작업 중인 컴퓨터로 내보내기" 스위치는 항상 켜진 채 알림만 띄우고, 모델 프록시는 켜면 `http://127.0.0.1:4000`을 저장하지만 서버에 보내지 않고 프록시 서버도 없다 (문구에 명시) | 검증 전까지 비활성 표시 | 모듈 문서 |
| I-029 | 미구현 기능 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `files.rs` 전체, `ember/app/src/ui/files.rs:613` | 전송 서비스가 없어 장비 목록 외에는 데모 전용이다. `send`는 `Err(UNAVAILABLE)` | FR-F 구현 시 `TransferService` 실제 구현 | 모듈 문서 |
| I-030 | 거대 파일 | 중간 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `vcs.rs` 6,210줄 (본문 4,487), `routines.rs`, `agents.rs` | 한 파일에 화면 섹션 7개와 표본 데이터. `PullRequestsPane` 약 440줄, `HistoryPane` 약 350줄, `BranchesPane` 약 170줄 | 섹션별 파일로 분리 (`vcs/changes.rs`, `vcs/prs.rs` 등) | 모듈 문서 |
| I-031 | 죽은 코드 | 중간 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/workbench.rs` | pub 항목 11개 모두 Dioxus 트리 안에서만 쓰인다 | #226 정리 때 파일째 삭제 검토 | 모듈 문서 |
| I-032 | 의존자 없음 | 중간 | [bridge](modules/bridge.md) | `ember/bridge/Cargo.toml` | `ember-bridge`를 쓰는 크레이트가 저장소에 없다. 진입점이 없는 죽은 크레이트이거나 셸이 아직 붙지 않은 상태다 (`ember/bridge/src/lib.rs:11`, "No platform webview implementation lives here yet") | 의존할 셸을 정하거나 상태를 문서에 적는다 | 모듈 문서 |
| I-033 | 중복 구현 | 중간 | [client](modules/client.md) | `wire.rs:1-5`, `channels.rs:1-2` | **서버 DTO와 두 번 정의된 곳.** `wire.rs`, `channels.rs`, `api.rs`의 DTO는 서버 타입의 손 복사본이다 (`wire.rs:1-5`, `channels.rs:1-2`). 서버 필드를 바꾸면 여기도 고치고, 새 필드는 `#[serde(default)]`로 받아야 구버전 서버와 맞는다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-034 | 보안 | 중간 | [client](modules/client.md) | `api.rs:717-720`, `api.rs:722-724`, `api.rs:890-892` | **토큰 전송 범위.** `Api::with_token`은 토큰이 있어도 허용 호스트가 아니면 버린다 (`api.rs:717-720`). 새 요청 경로를 만들면 `auth` 헤더 처리(`api.rs:722-724`, `api.rs:890-892`)를 똑같이 따라야 한다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-035 | 거대 파일 | 중간 | [editor](modules/editor.md) | `ember/editor/src/engine.rs` (1,707줄) | 검색/바꾸기, 인라인, CodeLens, 확장 호스트 요청 분기가 한 `impl`에 모여 있다. `on_exthost_request`만 약 120줄 (`:1017-1139`) | 기능별 파일로 `impl SessionCore`를 나눈다 | 모듈 문서 |
| I-036 | 중복 | 중간 | [editor](modules/editor.md) | `search.rs:490` `glob_match`, `selector.rs:93` `glob_match` | 같은 이름, 다른 구현(정규식 기반 대 직접 매칭). 문법(`{a,b}` 중첩, `[!a]`, `**`)이 서로 다를 수 있다 | 한 구현으로 합치거나 차이를 문서화 | 모듈 문서 |
| I-037 | 죽은 코드 후보 | 중간 | [editor](modules/editor.md) | `fallback.rs` 전체, `session.rs:142`, `:158` | 앱은 `EditorSession::connect_tcp`만 부르고 (`ember/app/src/editor_host.rs:220`) `connect_or_fallback`, `FallbackTarget`, `vscode_fallback_url`은 `ember/app/src`에서 찾지 못했다 (grep). 버전 불일치 시 VS Code 대체 동작이 앱에서 연결되지 않았을 수 있다 | `[확인 필요]` 앱이 다른 경로로 대체를 처리하는지 확인 | 모듈 문서 |
| I-038 | 기능 공백 | 중간 | [editor](modules/editor.md) | `session.rs:14-17` | 재연결 없음, 작업 폴더 1개, 런타임 설정 변경 없음 (문서가 직접 밝힘). 연결이 끊기면 `ConnectionLost`로 종료 | 별도 이슈로 추적 | 모듈 문서 |
| I-039 | 중복 구현 | 중간 | [extensions](modules/extensions.md) | `session.ts:113-115`, `DocumentState.kt:100-111` | **스냅샷 `seq` 해석이 두 클라이언트에서 다르다** (`session.ts:113-115` 대 `DocumentState.kt:100-111`). 어느 한쪽은 이벤트 하나를 놓치거나 중복 처리한다. 매니저 문서로 확인 후 한쪽에 맞춘다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-040 | 중복 구현 | 중간 | [extensions](modules/extensions.md) | `CellDecorator.kt:31-37` | **팔레트 값이 두 번 정의돼 있다:** 테마 JSON과 `CellDecorator.kt:31-37`. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-041 | 보안 | 중간 | [hub](modules/hub.md) | `ember/hub/src/registration.rs:112-122`, `:134-137` | `hub.json`(장치 토큰 포함)의 0600 보장이 `cfg(unix)`에서만 있다. Windows 노드는 기본 ACL에 의존한다 (노드는 Windows를 지원한다, 최근 커밋 `#200`) | Windows ACL 제한 또는 DPAPI 보관, 아니면 한계를 문서화 | 모듈 문서 |
| I-042 | 보안 | 중간 | [node](modules/node.md) | `egress.rs:35-38`, `:137-141` | 기본 egress 정책이 전부 허용이라 클라우드 메타데이터(169.254.169.254)와 노드의 loopback/LAN에 토큰 소지자가 닿는다. 의도된 기본(FR-R1)이지만 공용 서버에서는 위험 | 배포 문서에 `EMBER_NODE_EGRESS_DENY=link-local` 권장 추가 검토 | 모듈 문서 |
| I-043 | 보안 | 중간 | [node](modules/node.md) | `egress.rs:413-420` | `EMBER_NODE_SOCKS_LISTEN`의 loopback 피어는 인증이 없다. 같은 컴퓨터의 모든 프로세스가 출구로 쓸 수 있다 | 문서화, 필요하면 인증 강제 옵션 | 모듈 문서 |
| I-044 | 보안 | 중간 | [node](modules/node.md) | `config.rs:137`, `api.rs:236-253` | 토큰은 평문 HTTP로 전달된다. `EMBER_NODE_LISTEN`을 loopback 밖으로 두면 도청과 무차별 대입에 노출되고 시도 횟수 제한도 없다 | loopback 밖 바인딩 시 경고, 또는 transport 사용 안내 | 모듈 문서 |
| I-045 | 보안 | 중간 | [node](modules/node.md) | `policy.rs:14-15`, `exec_server.rs` 머리 주석 | 경로 정책은 명령을 제한하지 않는다. `/exec`, `/jobs`, `/terms`, `/exec-server`를 호출할 수 있으면 토큰 소지자는 사용자 권한으로 무엇이든 한다 | 설계상 의도. 토큰 보관(서비스 env 파일 0600)이 사실상 경계 | 모듈 문서 |
| I-046 | 구조 | 중간 | [node](modules/node.md) | `api.rs` (971줄), `proto.rs` (947줄) | `api.rs`에 git, 잡, 터미널, WS 핸들러가 섞여 있다 | 라우트군별 파일 분리 | 모듈 문서 |
| I-047 | 정확성 | 중간 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol_cli.rs:10-12` | 머리 주석이 N2b가 "작성됐으나 컴파일되지 않았다"고 적고 있다. 현재 상태와 어긋나는 낡은 주석일 수 있다 [확인 필요] | CI 결과를 확인하고 주석 갱신 | 모듈 문서 |
| I-048 | 보안 | 중간 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol_cli.rs:75`, `:379-383` | `--allow-http`나 사설/`.local` 주소에서는 평문 HTTP로 코드, poll secret, 자격 증명이 오간다. 경고는 출력하지만 막지는 않는다 | 의도된 동작. 문서에서 https 권장 유지 | 모듈 문서 |
| I-049 | 중복 | 중간 | [node-term](modules/node-term.md) | `ember/node/src/bin/ember-term.rs:358-459` | `attach`의 이벤트 루프가 `#[cfg(unix)]`와 `#[cfg(not(unix))]`로 거의 똑같이 두 벌 (Refused 처리 등) | 공통 핸들러 함수로 추출 | 모듈 문서 |
| I-050 | 동시성 | 중간 | [node-term](modules/node-term.md) | `ember/node/src/term/mod.rs:197-250` | `create`가 `sessions` 락을 잡은 채 PTY와 keeper 기동(최대 20초 대기)을 한다 | 락 밖에서 spawn 후 삽입 시 키 중복만 재확인 | 모듈 문서 |
| I-051 | 중복 구현 | 중간 | [proxy](modules/proxy.md) | `dpx/vscode/proxy.py:116`, `dpx/terms/api.py:173` | **websockets 고정.** `extra_headers` 인자가 두 곳에 있다 (`dpx/vscode/proxy.py:116`, `dpx/terms/api.py:173`). websockets를 올리면 둘 다 `additional_headers`로 바꿔야 한다 (`requirements.txt:7-10`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-052 | 보안 | 중간 | [proxy](modules/proxy.md) | [modules/proxy.md](modules/proxy.md) | **런타임 파일은 커밋하지 않는다.** `darkpyonix.db`에 비밀번호 해시와 살아 있는 세션 토큰이 있다 (`ember/proxy/README.md:309-311`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-053 | 보안 | 중간 | [proxy](modules/proxy.md) | `dpx/auth/api.py:18-20`, `dpx/vscode/roots.py:8-10` | **보안 전제.** 계정은 "출입증"이지 신원이 아니다. 로그인하면 서버를 띄운 OS 사용자의 모든 파일에 닿는다 (`dpx/auth/api.py:18-20`). `DPX_FOLDER_ROOTS`는 URL로 여는 폴더만 제한한다 (`dpx/vscode/roots.py:8-10`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-054 | 보안 | 중간 | [server-accounts](modules/server-accounts.md) | `chatgpt/mod.rs` 머리 주석 | ID 토큰 서명(JWKS) 미검증. TLS로 토큰 엔드포인트에서 직접 받으므로 OIDC가 허용하나 문서가 열린 항목으로 인정 | JOSE 의존성 추가 후 검증 | 모듈 문서 |
| I-055 | 보안 | 중간 | [server-accounts](modules/server-accounts.md) | `ember/server/src/auth.rs:202` | `GET /auth/callback`은 토큰 없이 접근 가능하고 `state` 일치만 검증한다. `state`는 OS RNG 32바이트이고 pending에 있어야 하므로 위험은 낮으나 원격 노출 시 임의 호출을 받는 경로 | 현 설계 유지, 원격 노출 시 문서화 [확인 필요] | 모듈 문서 |
| I-056 | 사용되지 않는 심볼 | 중간 | [server-accounts](modules/server-accounts.md) | `chatgpt/mod.rs:663` `ChatGpt::responses` | production 호출자가 없고 테스트 (`ember/server/tests/chatgpt.rs:482` 등)에서만 쓰인다 (grep 확인) | 사용처가 생길 때까지 [확인 필요]로 두거나 정리 | 모듈 문서 |
| I-057 | 구조 | 중간 | [server-accounts](modules/server-accounts.md) | `schedules/mod.rs` (901줄), `chatgpt/mod.rs` (898줄), `accounts/mod.rs` (996줄), `transfers.rs` (833줄) | 큰 파일. `schedules/mod.rs`와 `chatgpt/mod.rs`에는 인라인 테스트가 없고 별도 통합 테스트에 의존 | 분리 검토 | 모듈 문서 |
| I-058 | 죽은 코드 | 중간 | [server-agents](modules/server-agents.md) | `ember/server/src/history/mod.rs:106`, `:185` | `import_file`과 `to_events`는 `ember/server`의 `history` 밖 소스와 `server/tests`에서 호출을 찾지 못했다 (`grep`). 가져오기 기능이 서버에 아직 연결되지 않았을 수 있다 [확인 필요] | 연결 여부를 확인하고, 없으면 이슈로 남기거나 표시 | 모듈 문서 |
| I-059 | 보안 | 중간 | [server-agents](modules/server-agents.md) | `ember/server/src/agents/antigravity.rs:503-527`, `:568-598` | 훅 토큰이 `ember-hook.sh` 파일에 평문으로 있다 (0700, 같은 사용자만 읽음). 세션 루트 경로를 인자에 넣은 도구 호출은 deny하지만 우회 여지가 있는지는 확인하지 않았다 [확인 필요] | 설계상 의도 (D14), 변경 시 위협 모델 재검토 | 모듈 문서 |
| I-060 | 안정성 | 중간 | [server-agents](modules/server-agents.md) | `ember/server/src/agents/mod.rs:87` | ACP 이름을 `Box::leak`으로 들여온다. 설정과 DB 이름으로 개수가 제한된다고 주석에 적혀 있다 (`mod.rs:46-48`) | 현재는 허용, DB에서 읽는 이름이 늘면 재검토 | 모듈 문서 |
| I-061 | 안정성 | 중간 | [server-agents](modules/server-agents.md) | `ember/server/src/agents/claude_code.rs:884-890` | `shutdown` 외에 `sigint`가 Windows에서는 무동작이다. 인터럽트 응답이 없을 때 최후 수단이 Windows에서는 없다 | Windows용 대체 수단 검토 | 모듈 문서 |
| I-062 | 중복 구현 | 중간 | [server-api](modules/server-api.md) | `computers/mod.rs:71`, `ose.rs:119`, `ember/app/src/ui/cr/new_session.rs:31` | `"local"` 문자열이 `computers::LOCAL`(`computers/mod.rs:71`)과 `ose::LOCAL_COMPUTER`(`ose.rs:119`)에 두 번 정의돼 있다. 앱도 따로 정의한다 (`ember/app/src/ui/cr/new_session.rs:31`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-063 | 보안 | 중간 | [server-api](modules/server-api.md) | `ose.rs:694-698`, `ose.rs:707`, `api/ide.rs:652` | OSE 토큰 흐름: `connection_for`가 실제 토큰은 파일로만 OSE에 주고 (`ose.rs:694-698`), 클라이언트에는 placeholder만 준다 (`ose.rs:707`). 릴레이가 앞 8 KiB에서 교체한다 (`api/ide.rs:652`). 토큰 길이가 같아야 교체가 켜진다 (`api/ide.rs:520-524`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-064 | 보안 | 중간 | [server-api](modules/server-api.md) | `git.rs:155`, `ose.rs:242`, `ose.rs:739` | Windows 지원: `HOME` 의존 (`git.rs:155`, `ose.rs:242`, `ose.rs:739`, `chrome.rs:19`)과 unix 전용 권한 처리(`ose.rs:98-102`)가 있다. Windows 노드 서버 작업(#200, 최근 커밋 `71d356e`)과 겹치는 부분이다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-065 | 보안 | 중간 | [server-collab](modules/server-collab.md) | `auth.rs:212`, `auth.rs:191` | **라우트 인증은 경로 모양이 정한다.** `/api/a2a/` 아래 새 라우트는 자동으로 서버 토큰 면제다 (`auth.rs:212`). 사용자 전용이면 `/api/a2a/` 밖에 두거나 `auth.rs`의 예외 목록을 고친다. `/api/channels/` 아래는 `<id>/post` 하나만 면제다 (`auth.rs:191`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-066 | 중복 구현 | 중간 | [server-collab](modules/server-collab.md) | `a2a/mcp.rs:35`, `channels/guest.rs:82`, `guest_door/join.js:10` | **같은 값이 두 번 정의된 곳.** 메시지 최대 8192바이트 (`a2a/mcp.rs:35`, `channels/guest.rs:82`, `guest_door/join.js:10`). 채널 id 최대 128 (`a2a/mcp.rs:37`, `channels/jsonl.rs:148`). 30분·분당 6회는 상수(`a2a/mod.rs:53`, `:56`)와 별개로 `a2a/mcp.rs:84`, `:321`, `a2a/client.rs:62`의 문장 안에 숫자로 다시 적혀 있다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-067 | 일관성 | 중간 | [server-collab-2](modules/server-collab-2.md) | `channels/api.rs:123-138`, `channels/guest.rs:236-248` | 소유자 라우터와 게스트 라우터가 각자 `JsonlLog`(각자의 잠금)를 만든다. 소유자 글과 게스트 글이 동시에 오면 파일의 `seq` 순서가 어긋날 수 있다. 복구는 마지막 줄의 `seq`만 보므로, 순서가 뒤바뀐 파일에서는 이미 있는 행을 다시 추가할 수 있다 `[확인 필요]` | 하나의 `Arc<JsonlLog>`를 `main.rs`에서 공유하거나, 복구가 파일의 `seq` 집합을 보게 한다 | 모듈 문서 |
| I-068 | 보안 | 중간 | [server-computers](modules/server-computers.md) | `ember/server/src/computers/schema.rs:9-15` | `computers.token`(노드 API 베어러 토큰)을 DB에 평문으로 저장한다. 주석상 클라이언트에는 돌려주지 않는다 | `secret.key`로 암호화하거나 DB 파일 권한을 확인 | 분석 세션 |
| I-069 | 보안 | 중간 | [server-computers](modules/server-computers.md) | `main.rs:482-487` | **라우터 위치가 보안 경계다.** 새 라우트를 `computers::api` 같은 공용 라우터에 넣으면 transport 허용 기기에게도 열린다. 기기나 서버 등록 자체를 바꾸는 라우트는 `devices::api::router`나 `hub::api::admin_router`처럼 `local_app`에만 합친다 (`main.rs:482-487`). | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-070 | 보안 | 중간 | [server-computers](modules/server-computers.md) | `mod.rs:1275` | **노드 토큰이 에이전트 프로세스 환경에 들어간다.** Claude Code 세션은 `EMBER_EXEC_NODE_TOKEN`을 받는다 (`mod.rs:1275`). 에이전트와 그 자식 프로세스는 이 토큰으로 노드 API 전체를 쓸 수 있다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-071 | 보안 | 중간 | [server-computers](modules/server-computers.md) | `mod.rs:946-948` | **loopback 리스너는 컴퓨터 삭제 때만 정리된다.** relay, bridge, egress는 `Computers::remove`(`mod.rs:946-948`)에서 맵을 비울 때 `Drop`으로 닫힌다. 컴퓨터의 URL이나 토큰을 바꾸는 경로는 없으므로 바뀐 노드에는 옛 클라이언트가 남는다 [추정]. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-072 | 보안 | 중간 | [server-computers](modules/server-computers.md) | `hub/mod.rs:56-57` | **봉인 AAD는 바꾸지 않는다.** `hub/mod.rs:56-57`의 접두사를 바꾸면 저장된 hub 토큰을 열 수 없다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-073 | 중복 구현 | 중간 | [server-core](modules/server-core.md) | `projects/mod.rs:21-23`, `api/mod.rs:274`, `session.rs:368` | **같은 값이 두 곳에.** `DEFAULT_PROJECT_NAME`은 클라이언트 `ember/app/src/ui/project.rs`, `ember/app/src/ui/home.rs`에도 있다 (`projects/mod.rs:21-23`). `PERMISSION_MODES`는 `api/mod.rs:274`와 `session.rs:368`에서 재사용된다. | 모듈 문서 "주의할 점" 참고 | 주의점 발췌 |
| I-074 | 보안 | 중간 | [server-enrol](modules/server-enrol.md) | `door/config.rs` `DoorEnv::parse`, `main.rs:385-390` | door가 평문 HTTP이고, 원격 허용 시 코드와 자격 증명이 평문으로 지나간다. 경고만 있고 TLS 종단은 소유자 몫 | 문서화 유지. TLS 앞단 권장을 mint 경고에 이미 있음 (`enrol.rs:1481-1486`) | 모듈 문서 |
| I-075 | 보안 | 중간 | [server-enrol](modules/server-enrol.md) | `enrol.rs:46-49` | 노드 토큰이 레지스트리에 평문 저장 (bearer로 쓰기 위함) | 레지스트리 암호화 여부는 [server-computers](modules/server-computers.md) 참조 [확인 필요] | 모듈 문서 |
| I-076 | 구조 | 중간 | [server-enrol](modules/server-enrol.md) | `door/limits.rs:15-18` | "공용" 모듈이 `crate::guest_door` 상수에 의존, 순환 구조 | 상수를 `door/`로 이동 (`docs/analysis/_raw/cycles.md` 참고) | 모듈 문서 |
| I-077 | 구조 | 중간 | [server-enrol](modules/server-enrol.md) | `computers/enrol.rs` (3,281줄) | 코어, 라우트, 레지스트리 어댑터, 테스트 약 1,700줄이 한 파일 | 테스트를 `tests/`나 하위 모듈로 분리 | 모듈 문서 |
| I-078 | 미사용 코드 | 중간 | [transfer](modules/transfer.md) | `ember/transfer/src/session.rs`, `ember/transfer/src/state.rs` | `Service`, `Outgoing`, `Handled`, `Prompter`, `Transfer`, `State`가 크레이트 밖에서 쓰이지 않는다 (`ember/server`의 import는 `limits`, `mode`, `names`, `store`, `wire::DeclineCode`뿐). 서버는 같은 일을 `ember/server/src/transfers.rs`에서 따로 구현한다 | 서버가 `session`을 쓰게 합치거나 미사용임을 문서에 남긴다 | 모듈 문서 |
| I-079 | 중복 | 중간 | [transfer](modules/transfer.md) | `ember/server/src/transfers.rs:302`, `ember/transfer/src/session.rs:296` | 파일 수 검사가 양쪽에 있다 | 한쪽으로 통일 | 모듈 문서 |
| I-080 | 이식성 | 중간 | [transfer](modules/transfer.md) | `ember/transfer/src/store.rs:322-335` | 비 unix에서 파일 권한 처리가 없다. Windows 노드가 받은 파일은 `FR-F9`의 0644 문구와 다르다 | 요구 문구에 OS별 범위를 적는다 | 모듈 문서 |
| I-081 | 한계 | 중간 | [transfer](modules/transfer.md) | `ember/transfer/src/wire.rs:13`, `:42` | `Chunk.data: Vec<u8>`이 JSON 숫자 배열이면 32 KiB 청크가 `MAX_FRAME` 64 KiB를 넘을 수 있다 [추정, 확인 필요] | 청크 크기와 프레임 크기 관계를 테스트로 고정하거나 base64로 | 모듈 문서 |
| I-082 | 보안 | 낮음 | [app-core](modules/app-core.md) | `terminal_stream.rs:774`, `:812` (TODO #333) | WebSocket이 평문 `ws`이고 토큰도 평문이다 (루프백이 아닌 호스트는 `EMBER_TOKEN_HOSTS`로 허용 가능) | TLS 지원 (#333) | 모듈 문서 |
| I-083 | 중복 | 낮음 | [app-core](modules/app-core.md) | `terminal_stream.rs:34`, `server.rs:523` | `encode_segment`와 `seg`가 같은 퍼센트 인코딩을 따로 가진다. `start`와 `start_view`의 `Shared` 생성도 같은 코드 | 공용 함수로 합침 | 모듈 문서 |
| I-084 | 하드코딩 | 낮음 | [app-core](modules/app-core.md) | `editor_host.rs:219`, `lib.rs:121-129` | `app_language = "ko"` 고정, 에디터 창 크기 1280x820 고정, 창 제목 `Box::leak` | 설정화 또는 주석으로 의도 명시 | 모듈 문서 |
| I-085 | TODO | 낮음 | [app-core](modules/app-core.md) | `ide.rs:109`, `:151`, `lib.rs:132`, `prefs.rs:54`, `server.rs:9`, `terminal_stream.rs` 4개 | Rust 소스 TODO 9개 (`dioxus-compose#152`, `#161`, `ember-client` 이관, 서버 캐릭터 스타일, `#333`, `#334`, `#336`) | 추적 | 모듈 문서 |
| I-086 | 시그니처 | 낮음 | [app-core](modules/app-core.md) | `services.rs:264` `save_prefs(_prefs)` | 인자를 무시하고 `ui.prefs`를 다시 읽는다. 인자 있는 시그니처가 오해를 부른다 | 인자 제거 | 모듈 문서 |
| I-087 | 테스트 | 낮음 | [app-core](modules/app-core.md) | `services.rs`, `main.rs` | 직접 단위 테스트 없음 (`services.rs`는 테스트 보조만). 나머지는 `ember/app/tests/`와 UI 테스트가 다룬다 |  | 모듈 문서 |
| I-088 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/enrol_flow.rs` | Dioxus 전용 pub 항목 26개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-089 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/home.rs` | Dioxus 전용 pub 항목 43개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-090 | 거대 파일 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/home.rs` | 2780줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-091 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/monitor.rs` | Dioxus 전용 pub 항목 12개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-092 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/project.rs` | Dioxus 전용 pub 항목 14개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-093 | 거대 파일 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/project.rs` | 1578줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-094 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/question.rs` | Dioxus 전용 pub 항목 11개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-095 | 거대 파일 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/session.rs` | 2320줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-096 | 죽은 코드 | 낮음 | [app-ui](modules/app-ui.md) | `ember/app/src/ui/usage.rs` | Dioxus 전용 pub 항목 25개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-097 | 죽은 코드 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/agents.rs` | Dioxus 전용 pub 항목 30개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-098 | 거대 파일 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/agents.rs` | 2307줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-099 | 죽은 코드 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/channel_owner.rs` | Dioxus 전용 pub 항목 11개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-100 | 죽은 코드 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/channels.rs` | Dioxus 전용 pub 항목 13개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-101 | 죽은 코드 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/characters.rs` | Dioxus 전용 pub 항목 10개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-102 | 거대 파일 | 낮음 | [app-ui-collab](modules/app-ui-collab.md) | `ember/app/src/ui/routines.rs` | 2045줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-103 | 기능 갭 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `cr/theme.rs:29-31` | `system_scheme()`이 항상 라이트: "시스템" 선택이 OS 다크를 따르지 않음 (compose-rust#97) | 툴킷 훅 대기 | 모듈 문서 |
| I-104 | 죽은 코드 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `cr/a11y.rs:11-22` 중 `THEME`, `SETTINGS`, `PLATFORM`, `MENU`, `NEW_CHANNEL`, `MEMBERS`, `MORE`, `ATTACH`, `EMOJI`, `OPEN_SESSION` | `grep a11y::`로 `cr/` 안 사용처가 `VERSION_CONTROL`, `PROJECT_SETTINGS` 외에 없다 | 적용 전까지 유지 또는 삭제 `[확인 필요: 테스트 외 사용]` | 모듈 문서 |
| I-105 | 문구 분산 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `ko.rs`가 소비자 13곳(`compat`, `conversation`, `launcher`)뿐 | 문구가 파일 인라인, `ui::*` 상수, `ko.rs`에 흩어져 번역, 교정 시 누락 위험. `model`의 영어 원문이 남아 있다 (`ko.rs:1-3`) | phase 8에서 `model`을 한국어로 바꾸고 `ko.rs` 흡수 | 모듈 문서 |
| I-106 | 거대 파일 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `home.rs` 2503줄, `components.rs` 1471줄, `shell.rs` 1063줄 (테스트 포함) | `home.rs`는 작성기, 모델 선택기, 대시보드 8개 타일, 연동 영역이 한 파일 | 작성기와 대시보드로 분리 | 모듈 문서 |
| I-107 | 검토 훅 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `home.rs:429-466,573`, `channels.rs:210,~240`, `channel_owner.rs:138-150`, `monitor.rs`, `new_channel.rs:80-90`, `search.rs:66`, `shell.rs:785-837` | 프로덕션 코드가 `EMBER_CR_*` 환경 변수로 동작을 바꾼다 (`channel_owner`는 "리뷰 변수 없으면 샘플 안 샌다" 테스트 있음 `:709`) | 문서화 완료(데이터 절). 릴리스 빌드에서 `cfg`로 제거 검토 | 모듈 문서 |
| I-108 | TODO | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `grep -c "TODO"`: `components.rs` 18, `home.rs` 19, `channels.rs` 11, `compat.rs` 6, `theme.rs` 4, `shell.rs` 3, `monitor.rs` 3, `characters_screen.rs` 3, `channel_owner.rs` 3, `new_channel.rs` 2, 그 외 파일 각 1 (`a11y`, `notice`, `launcher`, `add_computer`, `new_session`) | 대부분 compose-rust 이슈(#374, #384, #428-429, #443-446, #460)에 묶인 툴킷 갭. 합계 약 76 | 툴킷 업그레이드 때 재검토 | 모듈 문서 |
| I-109 | 보안 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `add_computer.rs:5-6`, `channel_owner.rs:6-8` | 코드와 초대 링크를 시트 상태에만 보관하고 로그, 저장하지 않는 설계 (좋은 점). 비밀값을 이 문서에 기록하지 않았다 | 변경 시 `tracing`에 값이 새지 않도록 유지 | 모듈 문서 |
| I-110 | 정확성 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `cr/shell.rs:69-89`와 `Route::Search` | 검색 중 다른 메뉴를 고르면 `Route::Search`가 남아 `screen_for`가 그 메뉴 화면을 그리지만 라우트는 `Search`인 채다. 이후 프로젝트로 돌아오면 검색이 다시 보임 | 의도 확인 `[확인 필요]` | 모듈 문서 |
| I-111 | 메모리 | 낮음 | [app-ui-cr](modules/app-ui-cr.md) | `shell.rs:98-125`, `characters.rs:27-38` | SVG 문서를 `'static`으로 leak해 캐시: 색, 크기 조합이 늘수록 영구 증가 (테마 전환, 아이콘 크기 수 만큼으로 유한) | 현재 규모에서는 허용 | 모듈 문서 |
| I-112 | 일관성 | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:1297` | `PaneComposer` interrupt는 데모 차단 검사 없음, 전송 실패 배너 없음 | `conversation.rs`와 맞춤 | 모듈 문서 |
| I-113 | 사용량 | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:3680-3683` | 세션 사용량(`GET /api/sessions/{id}/usage`) 호출 없음, 정보 패널의 "컨텍스트" 등은 데모 전용 (`:2117-2123`) | 실데이터 연결 시 추가 | 모듈 문서 |
| I-114 | 데모 상수 | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `session.rs:2671-2737` | 타임라인 레인이 데모 상수 (`DEMO_TL_LANES`) | 비데모 데이터 확인 [확인 필요] | 모듈 문서 |
| I-115 | TODO | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `project.rs` (29줄), `session.rs` (10줄), `conversation.rs` (0줄) | 대부분 `TODO(compose-rust#NNN)` 접근성 이름, 토글, 점선 테두리 | 툴킷 지원 시 처리 | 모듈 문서 |
| I-116 | 순환 의존 | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `conversation.rs:671`, `session.rs:57` | 두 파일이 서로 import | 공용 부품(칩, 버튼)을 `components`로 이동 | 모듈 문서 |
| I-117 | 보안 | 낮음 | [app-ui-cr-session](modules/app-ui-cr-session.md) | `conversation.rs:1342`, `session.rs:4478` | 비밀값 노출 없음. 질문 비밀 입력은 앱에서 받지 않도록 막혀 있다 (`question.rs:20`) | 해당 없음 | 모듈 문서 |
| I-118 | 중복 로직 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `files.rs:539-588` `kpi_cells` vs `ember/app/src/ui/files.rs:958-1000` `kpis` | 같은 KPI 4개를 다시 만든다. 라벨이 다르다 ("지금 전송 중" vs "전송 중"). `kpis`는 `pub use`로 가져오지만 이 화면은 쓰지 않는 것으로 보인다 [확인 필요: 호출 여부 grep 필요] | `kpi_cells`가 `kpis`를 감싸도록 정리 | 모듈 문서 |
| I-119 | 중복 로직 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `files.rs:485` `page_pad`, `agents.rs:326`, `routines.rs:571`, `vcs.rs:4262` | 화면 패딩을 화면마다 `if compact {SP[3]} else {SP[6]}`로 따로 계산한다 (파일 화면만 24 중간 단계 있음) | `super::home::content_width`와 함께 공용 함수로 | 모듈 문서 |
| I-120 | 중복 정의 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:570`, `routines.rs:1087`, `vcs.rs:293` | `FocusOverlay`가 세 파일에 각각 있다 (같은 이름, 시그니처 거의 같음) | `components`로 옮긴다 | 모듈 문서 |
| I-121 | 중복 정의 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `routines.rs:313` `status_tone`, `vcs.rs:2241` `status_tone` | 같은 이름의 색 매핑 함수 두 개. 입력 타입은 다르다 | 필요 시 정리 | 모듈 문서 |
| I-122 | 결합 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `vcs.rs:2805` | `pr_checks_tone`가 문구 "체크 없음" 문자열 비교로 분기한다. `pr_checks_text`(`ui/vcs.rs:1934`)가 바뀌면 조용히 깨진다 | 상태 열거형으로 분기 | 모듈 문서 |
| I-123 | 중복 문구 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `vcs.rs:405` vs `ember/app/src/ui/vcs.rs:214-216,3028` | 원격 버튼은 "가져오기/내려받기/올리기", 알림과 레이블은 "Fetch/Pull/Push"를 섞어 쓴다 | 한 곳에서 정의 | 모듈 문서 |
| I-124 | 쓰이지 않는 심볼 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:829` `LocalNote` | 호출 0건 (`grep LocalNote`에서 정의만) | 삭제 또는 연결 | 모듈 문서 |
| I-125 | 하드코딩 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:1256-1310`, `ui/agents.rs:791` | 모델 이름, 플랜 가용성, `PINNED_ANTIGRAVITY_VERSION = "1.2.16"`이 코드에 박혀 있다 | 서버 카탈로그 연동 시 제거 | 모듈 문서 |
| I-126 | 하드코딩 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `files.rs:924` | `DEFAULT_INBOX = "~/Downloads/Ember"` (TODO FR-F8) | 전송 설정에서 읽기 | 모듈 문서 |
| I-127 | 기능 누락 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `routines.rs` | 서버 스케줄 삭제 UI가 없다. client에는 `delete_schedule`(`api.rs:1317`)이 있으나 app이 부르지 않는다 (client 문서 153줄과 일치) | 삭제 버튼 또는 `delete_schedule` 정리 | 모듈 문서 |
| I-128 | 기능 누락 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs` 전체 | 요청 범위에 있던 MCP 설정 화면은 이 모듈에 없다 | 다른 모듈 확인 [확인 필요] | 모듈 문서 |
| I-129 | 오류 은닉 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `routines.rs:219-226` | 상태 코드가 있는 서버 오류의 `load_remote` 실패는 `tracing::warn!`만 하고 화면에는 이전 목록이 그대로 남는다 | 알림 한 줄 | 모듈 문서 |
| I-130 | 비용 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `routines.rs:203-209` | 스케줄마다 실행 기록을 따로 요청한다 (N+1). 조작 한 번마다 전체를 다시 읽는다 | 서버에 묶음 조회 | 모듈 문서 |
| I-131 | 검증 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:299`, `ui/bridge.rs:402` | 에이전트 화면은 사용량을 14일로만 요청하지만 선택 UI는 7일/14일이다 (`agents.rs:2490`) [확인 필요: 7일은 클라이언트 합산인지] | 확인 후 정리 | 모듈 문서 |
| I-132 | 보안 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | `agents.rs:2294` | 로컬 주소 `http://127.0.0.1:4000` 기본 프록시 값 하드코딩. 비밀값 아님 | 설정값으로 | 모듈 문서 |
| I-133 | TODO | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | 개수: files 12, routines 8, agents 8, vcs 15 (`TODO\ | FIXME` grep) | 대부분 compose-rust 이슈 번호(#372, #385, #428, #460 등)와 FR-F8 | 모듈 문서 |
| I-134 | 거대 파일 | 낮음 | [app-ui-cr-work](modules/app-ui-cr-work.md) | 테스트 | 각 파일의 테스트가 파일 크기의 30-50%를 차지한다. 일부 테스트가 소스를 문자열로 읽어 점검한다 (`routines.rs:2825` `handler.find("notice::post(RUN_NOTICE)")`) | 테스트 파일 분리 | 모듈 문서 |
| I-135 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor.rs` | Dioxus 전용 pub 항목 10개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-136 | 거대 파일 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor.rs` | 1579줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-137 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor_scm.rs` | Dioxus 전용 pub 항목 44개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-138 | 거대 파일 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor_scm.rs` | 2030줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-139 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor_search.rs` | Dioxus 전용 pub 항목 18개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-140 | 거대 파일 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/editor_workbench.rs` | 2187줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-141 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/files.rs` | Dioxus 전용 pub 항목 32개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-142 | 거대 파일 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/files.rs` | 2140줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-143 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/term_pane.rs` | Dioxus 전용 pub 항목 14개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-144 | 죽은 코드 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/vcs.rs` | Dioxus 전용 pub 항목 43개 | 컴포넌트 단위로 정리 | 모듈 문서 |
| I-145 | 거대 파일 | 낮음 | [app-ui-dev](modules/app-ui-dev.md) | `ember/app/src/ui/vcs.rs` | 5901줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 | 모듈 문서 |
| I-146 | 문서 불일치 | 낮음 | [bridge](modules/bridge.md) | `ember/bridge/Cargo.toml:5` | "versioned"라고 적었지만 코드는 버전 없음 (D15) | 설명 수정 | 모듈 문서 |
| I-147 | 하드코딩 | 낮음 | [bridge](modules/bridge.md) | `ember/bridge/src/messages.rs:165-169` | VS Code Web 내부 동작(`openFile`, `gotoLineMode`)에 묶여 있다 | VS Code 갱신 때 벡터로 회귀 확인 | 모듈 문서 |
| I-148 | 직렬화 일관성 | 낮음 | [bridge](modules/bridge.md) | `ember/bridge/src/messages.rs:75-82` | `TabDetach`/`OpenWindow`의 일부 선택 필드가 `null`로 직렬화된다 [추정] | `skip_serializing_if` 통일 여부 결정 | 모듈 문서 |
| I-149 | 타입 | 낮음 | [bridge](modules/bridge.md) | `ember/bridge/src/messages.rs:84-97` | `sent_at_ms`가 `f64`다 (밀리초 에포크는 `f64`로 정확하지만 비교, 직렬화 때 정수 표현이 아님) | 현재는 JS `Date.now()`와 맞춘 것으로 보임 [추정] | 모듈 문서 |
| I-150 | TODO/FIXME | 낮음 | [bridge](modules/bridge.md) | `ember/bridge/src/` | 0개 (grep) | 없음 | 모듈 문서 |
| I-151 | 거대 파일 | 낮음 | [editor](modules/editor.md) | `textmate/interpreter.rs` (1,267줄) | 컴파일러와 토크나이저가 한 파일 | 컴파일(`Builder`)과 토큰화를 분리 | 모듈 문서 |
| I-152 | 문서 불일치 | 낮음 | [editor](modules/editor.md) | `lib.rs:30-31` | "written without compiling" 상태 문구가 남아 있다. 테스트가 16개 파일 있다 | 현재 상태에 맞게 갱신 | 모듈 문서 |
| I-153 | 보안 | 낮음 | [editor](modules/editor.md) | `paths.rs:3-8` | 파일이 스스로 보안 경계가 아니라고 밝힌다. OSE 파일 채널은 서버 사용자 권한으로 쓰고 폴더 경계가 없다. 심볼릭 링크는 부모에서 `refuse_symlink_parent`로만 막는다 | 설계 의도 확인. 서버 쪽 경계가 필요하면 별도 이슈 | 모듈 문서 |
| I-154 | 보안 | 낮음 | [editor](modules/editor.md) | `grammar.rs`, `plist.rs`, `selector.rs`, `interpreter.rs` | 확장이 주는 문법은 외부 입력이다. 크기, 깊이, 노드, 정규식 시간 상한이 이미 있다 (`MAX_*`, `REGEX_RETRY_LIMIT`). 문서 쪽 방어는 충분해 보이나 Oniguruma 자체의 C 코드 취약점은 범위 밖 | 해당 없음 (정보) | 모듈 문서 |
| I-155 | 하드코딩 | 낮음 | [editor](modules/editor.md) | `session.rs:240-246`, `engine.rs:56-63` | 에디터 기본 설정(탭 4칸, 코드렌즈 켬 등)과 디바운스가 코드에 고정 | 사용자 설정과 연결할 때 `user_settings` 경로를 쓴다 | 모듈 문서 |
| I-156 | 언어 혼용 | 낮음 | [editor](modules/editor.md) | `paths.rs:27-32` 대 `fallback.rs:30`, `lib.rs:75` | 사용자 문구가 한국어와 영어로 섞여 있다 | 문구 정책 통일 | 모듈 문서 |
| I-157 | 기능 공백 | 낮음 | [editor](modules/editor.md) | `engine.rs:1030-1034` | `setContext`는 아무것도 하지 않는다 (주석: "no-op for Ember for now") | 필요해지면 구현 | 모듈 문서 |
| I-158 | TODO/FIXME | 낮음 | [editor](modules/editor.md) | `ember/editor/src` 전체 | 0개 (grep) | - | 모듈 문서 |
| I-159 | 테스트 위치 | 낮음 | [editor](modules/editor.md) | `bridge.rs`, `engine.rs`, `session.rs`, `highlight.rs`, `paths.rs`, `textmate/*` | 소스 내 단위 테스트가 0개. `tests/`(`widget_bridge.rs`, `engine_flow.rs`, `explorer_paths.rs`, `fr_e6_textmate_*.rs`)가 대신 검증한다 | 정보 | 모듈 문서 |
| I-160 | 하드코딩 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/config.rs:13` | 기본 허브 URL `https://api.darkpyonix.dev` | 의도된 기본값. 변경은 `EMBER_HUB_URL` | 모듈 문서 |
| I-161 | 하드코딩 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/fake.rs:46-47` | 가짜 허브의 `ACCOUNT_ID`, `GITHUB_LOGIN = "octocat"` | 시험 전용(feature `fake`), 조치 불필요 | 모듈 문서 |
| I-162 | 패닉 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/client.rs:145` | `HubClient::new`가 `expect`로 패닉 가능 (TLS 초기화 실패) | `Result` 반환 | 모듈 문서 |
| I-163 | 사용하지 않는 pub | 낮음 | [hub](modules/hub.md) | `ember/hub/src/registration.rs:247`, `:272` | `watch_registration`, `watch_registration_with`는 `server/src`, `node/src`, `app/src`, `client/src`, `editor/src`, `transport/src`에서 호출 0회 (grep). 서버는 `DeviceWatcher`를 직접 쓰는 것으로 보인다 (`ember/server/src/hub/mod.rs` 안 `DeviceWatcher` 언급) [추정] | 쓰이지 않으면 제거 또는 서버 쪽 중복을 이 함수로 통합 | 모듈 문서 |
| I-164 | 사용하지 않는 pub | 낮음 | [hub](modules/hub.md) | `ember/hub/src/client.rs:343`, `:357`, `ember/hub/src/config.rs:180`, `ember/hub/src/link.rs:29`, `ember/hub/src/types.rs:218` | `rename_device`, `readmit`, `relay_config_for`, `link_message`, `service_label`은 크레이트 밖 호출이 없다 (grep). 일부는 `hub/tests`나 `fake`가 쓸 수 있다 [확인 필요] | 시험 전용인지 확인 후 `#[cfg(test)]`나 `pub(crate)`로 | 모듈 문서 |
| I-165 | 하드코딩 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/types.rs:177-179` | `supports_devices_wait`가 항상 `true` (주석상 의도, 허브가 `wait`를 무시하면 감시자가 폴링으로 전환) | 현 상태 유지, 이름이 오해를 부를 수 있다 | 모듈 문서 |
| I-166 | 거대 파일 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/fake.rs` (1,028줄) | 가짜 허브가 한 파일에 있다 | 필요 시 분리. 시험 전용이라 우선순위 낮음 | 모듈 문서 |
| I-167 | 문서 | 낮음 | [hub](modules/hub.md) | `ember/hub/src/lib.rs:2-3` | 허브 계약이 외부 저장소(`darkpyonix-core`)의 특정 브랜치 `feat/m4-hub-ember-gaps`를 가리킨다. 브랜치가 병합 후 지워지면 참조가 끊긴다 | 병합된 커밋이나 버전으로 교체 | 모듈 문서 |
| I-168 | TODO/FIXME | 낮음 | [hub](modules/hub.md) | `ember/hub/src/` | 0개 (grep, `fake.rs` 포함) | 없음 | 모듈 문서 |
| I-169 | 보안 | 낮음 | [node](modules/node.md) | `api.rs:236` | `token_eq`는 길이가 다르면 즉시 반환해 토큰 길이가 새는 이론적 경로가 있다 | 수용 가능, 해시 후 비교로 대체 가능 | 모듈 문서 |
| I-170 | 보안 | 낮음 | [node](modules/node.md) | `fs.rs:399-401`, `policy.rs` `with_denied` 주석 | 정책 확인과 연산 사이 TOCTOU, denied는 inode가 아니라 경로 기준 | 문서화된 한계 | 모듈 문서 |
| I-171 | 정확성 | 낮음 | [node](modules/node.md) | `api.rs:1-72`, `:158` | 머리 주석 라우트 표에 `GET /metrics`가 빠졌다 | 표에 추가 | 모듈 문서 |
| I-172 | 중복 | 낮음 | [node](modules/node.md) | `api.rs:236`, `egress.rs:225` | 상수 시간 비교 함수가 두 군데에 같은 구현 | 공용 헬퍼로 합치기 | 모듈 문서 |
| I-173 | 이식성 | 낮음 | [node](modules/node.md) | `exec.rs:91-98` | Windows `kill_group`은 신호 종류를 무시하고 항상 강제 종료 | 문서화 | 모듈 문서 |
| I-174 | 하드코딩 | 낮음 | [node](modules/node.md) | `api.rs:231`, `egress.rs:60-62`, `jobs.rs:23-25` | 본문 64 MiB, 타임아웃 15/30초, 버퍼 256 KiB, 이벤트 1024 | 필요 시 설정화 | 모듈 문서 |
| I-175 | 보안 | 낮음 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol_cli.rs:59-66` | 코드를 인자로 주면 `ps`와 셸 기록에 남는다 (일회용, 10분 만료). `-`(stdin)을 쓰도록 `USAGE`가 안내한다 | 이미 완화됨 | 모듈 문서 |
| I-176 | 보안 | 낮음 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol_cli.rs:97` | `--trust-unverified-server`는 서버 id를 확인 없이 `allowed-peers`에 넣는다. NAT를 넘는 transport라 가짜 서버가 어디서든 접근할 수 있다 | 경고가 이미 있음 | 모듈 문서 |
| I-177 | 이식성 | 낮음 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol.rs:7-8`, `:51-53`, `:168` | 유닉스 전용 보호 모델. Windows 노드의 enrol 보호 수준이 낮다 | 한계로 문서화 [확인 필요: Windows 지원 범위] | 모듈 문서 |
| I-178 | 구조 | 낮음 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol_cli.rs` `run` (753-1054, 약 300줄) | 한 함수에 8단계가 모여 있다 | 단계별 함수로 분리 고려 | 모듈 문서 |
| I-179 | 견고성 | 낮음 | [node-enrol](modules/node-enrol.md) | `ember/node/src/enrol.rs:133-190` | `flock`은 NFS에서 권고 수준일 수 있다 (문서 주석에 명시) | 한계로 문서화 | 모듈 문서 |
| I-180 | 보안 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/bin/ember-term.rs:262-266` | `--node <url>`을 주면 URL만 바꾸고 `local.json`의 토큰을 그 URL로 보낸다. 잘못된 URL에 노드 토큰이 전송될 수 있다 | `--node` 사용 시 `EMBER_NODE_TOKEN` 명시를 요구하거나 경고 | 모듈 문서 |
| I-181 | 보안 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/bin/ember-term.rs:301-305` | 호출 환경 전체를 세션에 넘긴다 (토큰/URL/ID만 제외). 다른 비밀 환경 변수는 그대로 전달된다. 의도된 동작(task 환경 반영)이다 | 문서화 | 모듈 문서 |
| I-182 | 보안 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/term/pty.rs:316-372` | keeper 소켓은 0600이지만 같은 사용자의 어떤 프로세스든 `F`를 보내 PTY master를 받을 수 있다 | 같은 사용자 신뢰 모델이므로 수용 가능, 문서화 | 모듈 문서 |
| I-183 | 구조 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/term/session.rs` (764줄) | 파일이 크고 `Inner`와 `Session`, 크기/제어 정책, 터미널 보고 판별이 한 곳에 있다 | 정책 부분 분리 고려 | 모듈 문서 |
| I-184 | 이식성 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/term/pty.rs:289`, `:372` | 비 unix에서 keeper가 빈 구현이라 Windows 노드는 재시작 시 세션을 잃는다 | 한계로 문서화 [확인 필요: Windows 지원 범위] | 모듈 문서 |
| I-185 | 정확성 | 낮음 | [node-term](modules/node-term.md) | `ember/node/src/term/mod.rs:133-170` | 재입양된 세션의 종료 상태는 알 수 없어 `ember-term`은 0을 돌려준다 (`bin/ember-term.rs:238-245`) | 의도된 동작 (코드 주석에 명시) | 모듈 문서 |
| I-186 | 보안 | 낮음 | [server-accounts](modules/server-accounts.md) | `accounts/secrets.rs:15-18` | 키는 파일 하나이고 KMS 미지원. 서버 계정 침해는 방어 대상이 아님 | 문서화된 경계, 키체인 이전은 향후 | 모듈 문서 |
| I-187 | 하드코딩 | 낮음 | [server-accounts](modules/server-accounts.md) | `accounts/mod.rs:66`, `schedules/mod.rs:40-46`, `chatgpt/mod.rs:68-70`, `accounts/api.rs:82-90` 부근 | 쿨다운 1시간, 유예 60초, 한도 100개와 20개, 상수 `CAP` 안내문, 에이전트 이름 `DarkPyonix Ember` (`chatgpt/mod.rs:104`) | 필요 시 설정화 | 모듈 문서 |
| I-188 | 견고성 | 낮음 | [server-accounts](modules/server-accounts.md) | `transfers.rs:154-190` | 전송 상태 메모리 보관, 이력 파일 읽기 실패는 조용히 빈 이력 (`unwrap_or_default`), 디렉터리 생성 실패 무시 (`let _ =`) | 오류 로그 추가 | 모듈 문서 |
| I-189 | 견고성 | 낮음 | [server-accounts](modules/server-accounts.md) | `chatgpt/mod.rs:339`, `:400` | `self.pending.lock().unwrap()` (포이즌 시 패닉). 다른 곳은 `unwrap_or_else(into_inner)` 사용 | 일관화 | 모듈 문서 |
| I-190 | TODO/FIXME | 낮음 | [server-accounts](modules/server-accounts.md) | 17개 파일 | 0개 |  | 모듈 문서 |
| I-191 | 확인 불가 | 낮음 | [server-agents](modules/server-agents.md) | `ember/server/src/agents/acp.rs:863-873` | Gemini 인증 방식 id `gemini-api-key`는 주석에서 UNVERIFIED라고 한다 | 실제 CLI로 확인 | 모듈 문서 |
| I-192 | 확인 불가 | 낮음 | [server-agents](modules/server-agents.md) | `ember/server/src/agents/acp.rs:974-995` | 오류 분류가 메시지 부분 문자열 추정이다 (`:6-8` 주석: 실제 문구는 미확인) | 실제 에이전트 응답 기록으로 고정 | 모듈 문서 |
| I-193 | 하드코딩 | 낮음 | [server-agents](modules/server-agents.md) | `claude_code.rs:80-82`, `codex.rs:78-80`, `antigravity.rs:166-181`, `acp.rs:159-167` | 제한 시간 상수(10초, 5초, 120초, 3600초, 600초 등) | 설정으로 뺄지 검토 | 모듈 문서 |
| I-194 | 중복 | 낮음 | [server-agents](modules/server-agents.md) | `claude_code.rs:282-300`와 `antigravity.rs:530`, `codex.rs:322-349`, `acp.rs:888-901` | MCP 서버 설정을 만드는 코드가 어댑터마다 있다 (각 CLI 형식이 다르므로 의도된 중복일 수 있다) | 유지 가능 | 모듈 문서 |
| I-195 | 거대 파일 | 낮음 | [server-agents](modules/server-agents.md) | `acp.rs` 2,218줄, `antigravity.rs` 1,977줄, `claude_code.rs` 1,711줄 | 테스트가 큰 몫이다 (`claude_code.rs`는 `:1077` 이후가 테스트). `acp.rs`는 프로토콜, 설정, 마스킹, 호스트(fs/terminal)가 한 파일 | 필요하면 `acp/` 하위로 분리 | 모듈 문서 |
| I-196 | TODO/FIXME | 낮음 | [server-agents](modules/server-agents.md) | 이 모듈 전체 | 0개 (`grep`) | 없음 | 모듈 문서 |
| I-197 | 시험 | 낮음 | [server-agents](modules/server-agents.md) | `claude_code.rs:1077-`, `codex.rs:1056-`, `antigravity.rs` (1,500줄 이후), `mod.rs:415-`, `history/mod.rs:222-` | 인라인 테스트 모듈이 있다. `acp/tests.rs`(1,074줄)와 `acp/fake_agent.rs`(422줄)는 읽지 않았다 |  | 모듈 문서 |
| I-198 | 죽은 코드 | 낮음 | [server-api](modules/server-api.md) | [01_FEATURE_MAP.md](01_FEATURE_MAP.md) "화면과 연결되지 않은 API" | 서버 `/api/*` 라우트 101개가 앱 문서 어디에도 나오지 않는다. 대부분 A2A CLI, guest·enrol door, 관리용이지만 browser·MCP·transfers·chatgpt는 앱 화면이 없다 | 화면이 없는 기능을 SPEC 진행 상태와 대조 | 분석 세션 |
| I-199 | 버그 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `join.js:123` | `new Date(m.at)`는 밀리초를 기대하나 서버의 `GuestMessage.at`은 초 단위다 (`channels/mod.rs:187`, `guest.rs:135-159`). 게스트 화면의 시각이 1970년 1월 기준으로 표시된다. 테스트 `fr_t14_guest_join_page.rs`가 시각을 보는지 `[확인 필요]` | `m.at * 1000`으로 변환 | 모듈 문서 |
| I-200 | 보안 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `guest_door.rs:9` | 문은 평문 HTTP다. 비 loopback으로 열 때 TLS는 전적으로 소유자 몫이고, 서버는 자격(`dpg_`)이 도청되는지 알 수 없다 | `ALLOW_REMOTE` 경고(`main.rs:367`)에 TLS 필요를 명시 | 모듈 문서 |
| I-201 | 보안 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `guest.rs:212-228`, `:551-568` | 게스트 글 한도(분당 10)와 전달 한도(시간당 20)는 메모리에만 있어 서버 재시작 때 초기화된다. 주소별 한도도 메모리다 | 허용된 위험으로 문서화 (주석에 이미 있음) | 모듈 문서 |
| I-202 | 성능 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `guest.rs:135-159` | 메시지마다 `channel_guests`를 조회한다(게스트 작성자 이름). 최대 500개 읽기에서 N+1 | `annotate`처럼 한 번에 읽기 | 모듈 문서 |
| I-203 | 성능 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `feed.rs:197` | `channel_feed`가 호출마다 멤버 세션의 모든 이벤트를 `events_after(id, 0)`으로 재생 | 보고 시점 이후 이벤트만 읽거나 캐시 | 모듈 문서 |
| I-204 | 중복 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `join.js:10-12`, `guest.rs:82` | 8192바이트, 폴링 상수 등이 JS와 Rust에 따로 있다 | 변경 시 함께 수정 (위 주의점) | 모듈 문서 |
| I-205 | 정리 | 낮음 | [server-collab-2](modules/server-collab-2.md) | `channels/api.rs:101-146` | 생성자 5종이 겹친다. 프로덕션은 `router_with_a2a_door` 하나를 쓴다 (`main.rs:457`). 나머지가 테스트 전용인지 `[확인 필요]` | 빌더로 합치기 | 모듈 문서 |
| I-206 | TODO/FIXME | 낮음 | [server-collab-2](modules/server-collab-2.md) | 이 모듈 전체 | 대상 파일에 `TODO`, `FIXME`가 0개 (grep) | 해당 없음 | 모듈 문서 |
| I-207 | 보안 | 낮음 | [server-enrol](modules/server-enrol.md) | `enrol_door.rs` `PollLimiter` 문서 | 잘못된 secret의 poll은 id별 한도가 없고 주소별과 전역 한도에만 묶인다 (문서가 인정한 잔여 위험) | 현 상태 유지 가능 | 모듈 문서 |
| I-208 | 하드코딩 | 낮음 | [server-enrol](modules/server-enrol.md) | `enrol.rs:162` | `PROPOSED_NODE_PORT = 8741` | 설정화 검토 | 모듈 문서 |
| I-209 | 하드코딩 | 낮음 | [server-enrol](modules/server-enrol.md) | `enrol_door.rs:83-99` | 한도 수치 전부 상수, 주석상 "adjustable" | 운영 설정이 필요하면 환경 변수화 | 모듈 문서 |
| I-210 | 중복 | 낮음 | [server-enrol](modules/server-enrol.md) | `enrol.rs:60-75`과 `door/limits.rs` | 실패 한도기와 주소 한도기가 비슷한 개념을 두 곳에서 따로 구현 (목적은 다름: redeem 실패 대 요청 수) | 의도된 이중 방어로 보이나 [확인 필요] | 모듈 문서 |
| I-211 | TODO/FIXME | 낮음 | [server-enrol](modules/server-enrol.md) | 7개 파일 | 0개 |  | 모듈 문서 |
| I-212 | 테스트 | 낮음 | [server-enrol](modules/server-enrol.md) | `enrol.rs` 81개, `enrol_door.rs` 8개 (`#[test]` 계열) | 통합 테스트는 `ember/server/tests/fr_c1_enrol.rs`, `fr_c2_enrol_*.rs` |  | 모듈 문서 |
| I-213 | 문서 불일치 | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/lib.rs:6`, `:14`, `ember/transfer/src/wire.rs:3` | "written, not compiled", "No file bytes move", "Only Offer, Accept, Decline and Cancel" 주석이 현재 코드와 다르다 | 주석 갱신 | 모듈 문서 |
| I-214 | 미사용 pub | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/wire.rs:42` | `ResumeFrom`, `Pause`, `Resume` 메시지는 크레이트 밖 사용 0 (grep) | 쓸 때까지 보류 표시 | 모듈 문서 |
| I-215 | 메모리 | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/session.rs:538` | `send_bytes`가 파일 전체를 메모리 슬라이스로 받는다 | 스트리밍 API | 모듈 문서 |
| I-216 | 경쟁 조건 | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/names.rs:222`, `ember/transfer/src/store.rs:287` | 존재 확인 후 `rename`까지 사이에 같은 이름이 생길 수 있다 | `create_new` 기반으로 | 모듈 문서 |
| I-217 | 성능 | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/store.rs:240-247` | 청크마다 파일을 다시 열고 `flush` | 핸들 유지 | 모듈 문서 |
| I-218 | TODO/FIXME | 낮음 | [transfer](modules/transfer.md) | `ember/transfer/src/` | 0개 (grep) | 없음 | 모듈 문서 |

## 측정값

### 거대 파일 (Rust, 테스트 제외, 2,000줄 이상)

| 파일 | 줄 |
|---|---|
| `ember/app/src/ui/cr/vcs.rs` | 6210 |
| `ember/app/src/ui/vcs.rs` | 5901 |
| `ember/app/src/ui/cr/session.rs` | 5180 |
| `ember/app/src/ui/cr/routines.rs` | 3532 |
| `ember/app/src/ui/cr/agents.rs` | 3471 |
| `ember/server/src/computers/enrol.rs` | 3281 |
| `ember/app/src/demo.rs` | 3025 |
| `ember/app/src/ui/home.rs` | 2780 |
| `ember/client/src/api.rs` | 2653 |
| `ember/app/src/ui/cr/home.rs` | 2503 |
| `ember/app/src/ui/session.rs` | 2320 |
| `ember/app/src/ui/agents.rs` | 2307 |
| `ember/server/src/agents/acp.rs` | 2218 |
| `ember/app/src/ui/cr/conversation.rs` | 2208 |
| `ember/app/src/ui/editor_workbench.rs` | 2187 |
| `ember/app/src/ui/files.rs` | 2140 |
| `ember/app/src/ui/routines.rs` | 2045 |
| `ember/app/src/ui/editor_scm.rs` | 2030 |

500줄 이상인 파일 전체는 [_raw/inventory.tsv](_raw/inventory.tsv)를 줄 수로 정렬해 본다.

### TODO / FIXME / XXX / HACK (테스트·Markdown 제외)

모두 239개.

| 구성 요소 | 개수 |
|---|---|
| app | 222 |
| vectors | 12 |
| ose | 2 |
| client | 1 |
| server | 1 |
| transport | 1 |

목록: `git grep -nE "\b(TODO|FIXME|XXX|HACK)\b" -- ember extensions ":!ember/*/tests/*" ":!*.md"`

### 순환 의존

파일 단위 SCC 17개 ([_raw/cycles.md](_raw/cycles.md)). 가장 큰 것은 앱 UI(`ui/`와 `ui/cr/`이 서로 참조)다. Rust에서는 같은 크레이트 안 모듈 순환이 컴파일 오류가 아니지만, 한 파일을 고칠 때 영향 범위가 넓다.

### 안 쓰는 의존성

확인하지 않았다 [확인 필요]. Rust는 `cargo machete` 또는 `cargo udeps`, VS Code 확장은 `npx depcheck`로 본다 (분석 중에는 실행하지 않았다). 알려진 것: `ember-bridge` 크레이트에 의존하는 크레이트가 없다.

