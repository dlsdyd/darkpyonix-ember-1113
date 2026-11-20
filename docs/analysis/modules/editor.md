# 모듈: editor

- 경로: `ember/editor/` (크레이트 `ember-editor`, 라이브러리 `ember_editor`, `ember/editor/Cargo.toml:2`, `:12`)
- 규모: 소스 파일 30개 / 약 11,900줄 (`Cargo.toml` 32줄 제외, `tests/` 16개 파일과 `tests/fixtures/textmate`는 제외). 소스 안 `#[test]` 68개 (`bridge.rs`, `engine.rs`, `session.rs`, `highlight.rs`, `paths.rs`, `textmate/*`는 0개, 그쪽 검증은 `tests/`에 있음)
- 레이어: 도메인 (세션 계층). 소켓과 프로토콜은 아래, 화면은 위에 둔다.
- 한 줄 책임: [editor-conn](editor-conn.md)이 제공하는 Code-OSS 연결 위에서 열린 문서, 확장 호스트 RPC, 진단, CodeLens, hover, 인라인 완성, 검색과 바꾸기, 구문 강조를 하나의 순수 상태 기계로 돌리고, dioxus-compose `CodeEditor` 위젯의 계약(FR-38)을 일반 Rust 데이터로 모델링한다 (`ember/editor/src/lib.rs:1-7`).
- 의존하는 모듈: [editor-conn](editor-conn.md) (`ember/editor/Cargo.toml:15`), 외부 `onig`(Oniguruma, `:24`), `serde`, `serde_json`, `thiserror`, `tokio`, `tracing`, `uuid`. dioxus-compose에는 의존하지 않는다 (`lib.rs:5-7`).
- 이 모듈을 쓰는 모듈: `ember/app` (`ember/app/src/editor_host.rs:4`, `ember/app/src/ui/editor.rs:86`, `:109`, `ember/app/src/ui/editor_search.rs:10`, `ember/app/src/ui/editor_workbench.rs:4`, `ember/app/src/ui/palette.rs`, `ember/app/src/terminal_stream.rs`). `[확인 필요]` `palette.rs`와 `terminal_stream.rs`에서 어떤 심볼을 쓰는지는 `use` 줄만 확인했다.

## 전체 구조

```
UI(app) ──Input──▶ EditorSession (session.rs, tokio 태스크 Driver)
                       │  Input / Effect 실행(RPC, 파일 I/O, 하이라이트 스레드)
                       ▼
                  SessionCore (engine.rs, I/O 없는 순수 상태 기계)
                       │  Effect::Ui(SessionUpdate)
                       ▼
                  WidgetBridge (bridge.rs) ──▶ CodeEditor 위젯 props, 44바이트 Decorations
```

- `SessionCore::handle(now, input) -> Vec<Effect>`가 유일한 입구다. 시간도 입력이라 디바운스가 결정적이다 (`ember/editor/src/engine.rs:7-10`, `:321`). 끝에서 `run_timers`, `flush_decorations`를 호출한다 (`:343-345`).
- `session.rs`의 `Driver`가 소켓, 타이머, 하이라이트 전용 스레드 `ember-highlight`를 소유하고 effect를 순서대로 실행한다 (`session.rs:2-5` 머리 주석, 하이라이트 스레드는 `spawn_highlighter`, 이름 `ember-highlight`). UI 스레드는 채널 송신만 한다.
- 문서 버전: 위젯은 텍스트를 받을 때마다 0부터, 확장 호스트는 URI마다 엄격히 증가하는 `versionId`가 필요하다. 문서마다 `ext_base`를 두고 위젯 버전 `v`를 `ext_base + v`로 보낸다 (`ember/editor/src/document.rs:1-8`).
- 좌표: 위젯은 0 기반, 확장 호스트는 1 기반이고 열은 둘 다 UTF-16 단위다 (`ember/editor/src/coords.rs:1-8`).
- 구문 강조: 확장이 `contributes.grammars`로 제공한 TextMate 문법만 쓴다. 번들 문법은 없다 (`ember/editor/src/textmate/mod.rs:3-4`).

## 공개 인터페이스

`lib.rs`가 재수출하는 것 (`ember/editor/src/lib.rs:56-67`):

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

## 파일별 요약

### `ember/editor/src/engine.rs` (1,707줄)

- 목적: 세션의 모든 결정을 내리는 동기 상태 기계. 입력은 `Input`, 출력은 `Effect` (`engine.rs:1-10`).
- 주의: 이 파일에는 `#[cfg(test)]`가 없다. 테스트는 `ember/editor/tests/engine_flow.rs`, `fr_e7_search_flow.rs`에 있다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Input` | enum | 86 | `Open/Close/Reload/Focus`, `Widget{uri,generation,event}`, `TriggerInline`, `ExtHostRequest`, `RpcReply`, `FileRead/FileWritten`, `FilesChanged`, `Highlighted`, `ExecuteCommand`, `Search/CancelSearch/Replace`, `Tick` |
| `Effect` | enum | 117 | `Rpc{token,call}`, `Cancel`, `Respond`, `ReadFile`, `WriteFile`, `Watch/Unwatch`, `Highlight(HighlightJob)`, `Ui(SessionUpdate)` |
| `SessionUpdate` | enum | 144 | UI가 받는 모든 결과: `Opened`, `Decorations`, `Syntax`, `Hover`, `Dirty`, `Saved`, `SaveFailed`, `ExternalChange`, `Desync`, `Problems`, `OutputChannels`, `ExtensionMessage`, `Commands`, `SearchHits/SearchDone`, `ReplaceDone`, `ConnectionLost` 등 |
| `ReadPurpose` | enum | 70 | 파일 읽기 목적: `Open`, `Reload`, `ForceReload`, `ExtHostOpen`, `Grammar{scope}`, `Replace{id}` |
| `Pending` | enum | 189 | 응답을 기다리는 RPC 종류: CodeLens, 해결, Hover, Inline, `ActivateThenRun`, `Command`, `Search` |
| `CoreOptions` | struct | 45 | 기본값: `tab_width` 4, `insert_spaces` true, `codelens_debounce` 250ms, `codelens_resolve_cap` 100, `inline_completions` true (`:56-63`) |
| `SessionCore::handle` | fn | 321 | 입력 처리 후 타이머 실행, 장식 flush, `out` 비우기 |
| `on_exthost_request` | fn | 1017 | 확장 호스트가 보낸 `MainThread*` 호출을 분기: 진단, 명령, 출력 채널, 메시지, 검색 제공자 등록, `$tryOpenDocument`, 그 밖은 `registry.apply` 또는 `session_reply` |
| `on_code_changed` | fn | 612 | 위젯 변경을 `OpenDocument::apply_widget_change`로 반영하고 확장 호스트에 `$acceptModelChanged`를 보낸다 |
| `flush_decorations` | fn | 1662 | 진단, CodeLens, hover 앵커, 고스트 텍스트를 합쳐 정렬 후 `SessionUpdate::Decorations` 하나로 내보낸다 |
| `on_highlighted` | fn | 1563 | 하이라이트 스레드 결과를 받아 `SessionUpdate::Syntax`로 변환 |

- 부수효과 없음(순수). 토큰은 `Token = u64` (`:42`).
- 사용처: `session.rs`의 `Driver`, `bridge.rs`(`SessionUpdate` 소비).
- 주의: 1,700줄 단일 `impl`이라 한 기능(검색/바꾸기 `:1305-1510`, 인라인 `:795-964`, CodeLens `:966-1016`)이 파일 곳곳에 흩어진다.

### `ember/editor/src/session.rs` (730줄)

- 목적: 연결 순서 수행과 `Driver` 태스크 (`session.rs:1-20`). 순서는 `GET /version` 버전 확인, 관리 연결, IPC, `getEnvironmentData`, `scanExtensions`, 원격 파일 `fileChange` 구독, 확장 호스트 연결, `$initializeConfiguration`, `$initializeWorkspace` (`:180-270`). 연결 계층 쪽 설명은 [editor-conn](editor-conn.md) "전체 구조"를 따른다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `EditorSession::connect` | async fn | 180 | 위 순서를 실행하고 `(Self, UnboundedReceiver<SessionUpdate>)` 반환. 설정 기본값으로 `editor.tabSize`, `editor.insertSpaces`, `editor.inlineSuggest.enabled`, `editor.codeLens`(언어별 재정의 값 6)를 넣는다 (`:240-246`) |
| `connect_tcp`, `connect_tcp_or_fallback`, `connect_or_fallback` | async fn | 127, 142, 158 | TCP 다이얼과 버전 불일치 시 `ConnectOutcome::Fallback` |
| `create_file`, `create_dir`, `rename_path`, `delete_path`, `move_path`, `copy_path` | async fn | 319, 345, 354, 363, 372, 406 | 탐색기 편집. 모두 `paths.rs` 검사를 먼저 거치고, 심볼릭 링크 부모는 `refuse_symlink_parent`로 거절한다 (`:374`, `:408`) |
| `copy_entry` | async fn | 약 381 | 스택 기반 재귀 복사. 심볼릭 링크를 만나면 `PathError::Symlink` |
| `open/close/reload/focus/widget_event/trigger_inline_completion/execute_command/search/cancel_search/replace/resync` | fn | 422-475 | 모두 `Command` 채널 송신, 태스크가 끝났으면 `Error::Closed` (`:454-458`) |
| `Driver::run`, `execute`, `spawn_highlighter` | | 약 543, 622, 515 | 이벤트 루프, effect 실행(`ReadFile` 등은 `tokio::spawn`), 하이라이트 스레드 큐. 큐가 가득 차면 작업을 버리고 문서를 다시 빌드한다 |

- 부수효과: 소켓, 원격 파일 읽기/쓰기, 스레드 1개 생성. `Drop`에서 태스크를 정리한다 (`:487-495` 근처).
- 사용처: `ember/app/src/editor_host.rs:220` (`EditorSession::connect_tcp`).
- 주의: 재연결 없음. 연결이 끊기면 `SessionUpdate::ConnectionLost`로 끝난다 (`session.rs:14-17`). 작업 폴더는 하나뿐이다.

### `ember/editor/src/bridge.rs` (401줄)

- 목적: `SessionUpdate`를 문서별 위젯 상태로 바꾸고 위젯 콜백을 `(UriComponents, generation, WidgetEvent)`로 번역 (`bridge.rs:1-4`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `DocumentWidgetState` | struct | 18 | 문서 하나의 위젯 props: 텍스트, generation, 인코딩된 장식 바이트, hover, 대기 중인 `EditCode`, 외부 변경 |
| `BridgeAction` | enum | 50 | `apply` 결과로 UI가 할 일. `resync_uri()` (`:74`) |
| `apply_text_change` | fn | 82 | 범위 치환을 텍스트에 적용 (UTF-16 열) |
| `WidgetBridge::apply` | fn | 161 | `SessionUpdate`별 상태 갱신. `Decorations`는 generation이 같을 때만 반영 (`:207-215`). `SetText`는 상태를 모두 초기화한다 |
| `on_code_changed`, `on_code_hovered`, `on_save_requested`, `on_decoration_activated`, `on_selection_changed`, `on_visible_range_changed`, `on_edit_rejected` | fn | 324-395 | 위젯 이벤트를 `Input::Widget`용 튜플로 |

- 사용처: `ember/app/src/ui/editor_workbench.rs:46`, `:144`, `:249`.

### 문서 모델과 좌표

### `ember/editor/src/document.rs` (382줄)

- 목적: 열린 문서 하나. 버전 변환, 확장 호스트 미러, 저장/재로드 상태 (`document.rs:1-8`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `DocError` | enum | 31 | `NotUtf8`("file is not UTF-8"), `VersionGap`, `BadChange` (`:32-41`) |
| `decode` | fn | 44 | UTF-8 BOM을 떼고 UTF-8이 아니면 거절 |
| `OpenDocument::open` | fn | 79 | 문서 생성 |
| `apply_widget_change` | fn | 193 | 다음 버전이 아니면 `VersionGap`, 범위가 맞지 않으면 `BadChange`. 성공 시 확장 호스트로 보낼 `Call` 반환 |
| `reset`, `saved`, `matches_disk`, `matches_buffer`, `save_bytes` | fn | 212, 240, 228, 233, 182 | 재로드, 저장 후 상태, 디스크와 비교, 저장 바이트(BOM 복원) |

### `ember/editor/src/coords.rs` (308줄)

- `WidgetPos`, `WidgetRange`와 변환 함수. `utf16_len` (`:92`), `utf16_to_byte` (`:98`), `byte_to_utf16`, `char_to_utf16`, `utf16_to_char`, `clamp_col` (`:148`), `clamp_range` (`:161`), `end_of_insert` (`:173`), `transform_range` (`:200`, 편집을 거친 범위 이동, 삭제되면 `None`). `to_exthost/from_exthost`는 0/1 기반 변환 (`:32`, `:37`, `:74`, `:83`).

### 확장 호스트 기능 브리지

| 파일 (줄) | 목적과 주요 심볼 | 비고 |
|---|---|---|
| `diagnostics.rs` (404) | FR-E2 마커를 밑줄 장식으로. `Diagnostics` (`:57`) `change_many` (`:82`), `clear` (`:145`), `problems` (`:119`), `decorations` (`:195`), `on_edit` (`:171`), `at` (`:275`, hover용). `Problem` (`:36`) | 마커는 문서와 owner별로 위젯 좌표에 저장 (`:6-8`) |
| `codelens.rs` (332) | FR-E3 CodeLens를 줄 위 장식으로. `CodeLenses` (`:87`) `set_visible_range` (`:104`, 보이는 줄의 `$provideCodeLenses` 요청 목록), `set_list` (`:133`), `resolved` (`:172`), `command_for` (`:230`), `remove_provider` (`:237`) | 해결되지 않은 렌즈는 목록당 `resolve_cap`(100)개까지만 해결 (`engine.rs:49`) |
| `hover.rs` (277) | `$provideHover`를 모든 일치 제공자에 보내 마크다운 팝업 하나로 합친다. `HoverState::begin` (`:98`), `reply` (`:164`), `end` (`:205`). `MarkdownString` (`:22`), `HoverPopup` (`:57`) | upstream처럼 `$releaseHover`를 부르지 않는다 (`hover.rs:7-9`) |
| `inline.rs` (603) | FR-E4 인라인 완성에서 고스트 텍스트. `Debouncer` (`:58`, 기본 50ms `:49`), `snippet_to_text` (`:104`), `parse_list` (`:173`), `ghost_for` (`:218`), `Ghost::type_through` (`:265`), `InlineDoc` (`:345`), `provide_call` (`:435`), `did_show_call`, `end_calls` | 제공자 응답을 `order`로 고르고 취소 가능 |
| `registry.rs` (273) | 확장 호스트의 `$register*` 호출을 `handle -> Provider`로 기록. `Registry::apply` (`:124`), `matching` (`:179`, 점수 높은 순, 같으면 최신 등록 우선), `has_command` (`:192`). `InlineMeta::from_raw` (`:37`, 위치 인자 17개) | `selector::score`를 사용 |
| `selector.rs` (230) | upstream `languageSelector.ts`의 `score()` 이식. `score` (`:19`), `glob_match` (`:93`, `*`, `**`, `?`, `{a,b}`, `[..]`) | 아래 이슈 후보: `search.rs`에 같은 이름의 다른 구현이 있다 |
| `languages.rs` (132) | 확장 `contributes.languages`로 파일의 언어 id 결정. `LanguageRegistry::language_for` (`:63`), 기본값 `PLAINTEXT` (`:18`) | 확장 호스트는 언어를 정하지 않고 통보만 받는다 (`:1-8`) |
| `replies.rs` (44) | 처리되지 않은 확장 호스트 요청의 응답. `session_reply` (`:21`): `MainThreadLanguages.$getLanguages`와 `MainThreadOutputService.$register`만 직접, 나머지는 `exthost::default_reply` | 라이브 테스트에서 배운 응답 (`:3-6`) |
| `commands.rs` (88) | `ContributedCommand` (`:7`), `display_title` (`:23`), `parse_contributed_commands` (`:43`) | 팔레트가 표시 |
| `output.rs` (115) | `OutputChannel::append` (`:30`)는 채널당 64 KiB로 자른다 (`:10`). `MessageSeverity::from_u8` (`:57`), `label` (`:65`) | 채널 id는 `ember-output-<seq>` (`engine.rs` `OutputRegister` 분기, `:1043` 근처) |
| `ids.rs` (137) | 장식 id 안정화. `IdSpace` (`:23`: `Diagnostic=1`, `CodeLens=2`, `HoverAnchor=3`, `GhostText=4`), id 상위 8비트에 공간을 넣어 활성화를 바로 분기 (`:56` 시프트). `DecorationIds::id` (`:59`), `retain` (`:87`) | 0은 "장식 없음"이라 쓰지 않는다 (`:5`) |
| `fallback.rs` (172) | 서버 커밋 불일치를 `UnsupportedServerVersion`으로 받아 VS Code 대체 URL 제안. `Fallback::message` (`:27`), `vscode_fallback_url` (`:61`: `<base>/?folder=<퍼센트 인코딩 경로>`), `fallback_for` (`:110`) | 앱은 쓰지 않는다 (아래 이슈) |

### `ember/editor/src/widget.rs` (294줄)

- 목적: FR-38 `CodeEditor` 계약을 일반 데이터로 (`widget.rs:1-6`). 장식 레코드는 44바이트 리틀엔디언 (`:31`, `put_u16` `:125` 근처). `Decoration` (`:108`), `Decoration::encode_records` (`:164`), `decode_records` (`:188`), `Severity::from_marker` (`:45`, 마커 8=Error, 4=Warning, 2=Info, 그 밖은 Hint), `WidgetEvent` (`:246`), `WidgetCommand` (`:270`, `SetText`, `EditCode`).
- 주의: 색은 항상 0(디자인 시스템이 정한다) (`:114-116`).

### `ember/editor/src/search.rs` (674줄)

- 목적: 파일 간 검색과 바꾸기(FR-E7)의 순수 부분. 검색 자체는 OSE 확장 호스트(ripgrep)가 하고, Ember는 저장하지 않은 열린 문서와 바꾸기 재확인에서만 `Matcher`(Oniguruma)로 직접 찾는다 (`search.rs:1-9`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `MAX_RESULTS` | const | 21 | 2000. Code-OSS는 20,000, 패널이 가상 목록이 아니라 더 낮춤 |
| `SearchRequest::query` | fn | 49 | `ember_editor_conn::search::TextQuery` 생성 |
| `Matcher::new/find/captures/hits_in_lines` | | 232, 257, 246, 262 | 줄 단위 매칭 (멀티라인 없음) |
| `expand_replacement`, `replacement_for` | fn | 303, 361 | `$1` 형태 치환 템플릿 |
| `replace_in_text` | fn | 397 | 사용자가 본 결과의 위치에서만 치환해 중간에 바뀐 파일을 보호한다 (`:8-9`) |
| `hits_from_matches` | fn | 149 | 확장 호스트 `FileMatch`를 `FileHits`로 |
| `glob_match`, `path_included` | fn | 490, 509 | 정규식 기반 glob, 포함/제외 판단 |
| `relative_to` | fn | 518 | 앱이 사용 (`ember/app/src/ui/editor_search.rs:244`) |

### `ember/editor/src/highlight.rs` (473줄)

- 목적: 구문 강조의 세션 쪽 결정과 백그라운드 작업 (`highlight.rs:1-8`). 두 부분: 순수한 `Highlights`(어느 문법이 필요하고 어느 파일을 읽을지)와 스레드에서 도는 `Worker`.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `WINDOW_MARGIN` | const | 24 | 보이는 범위 위아래 150줄만 색을 보낸다 |
| `MAX_GRAMMARS_PER_LANGUAGE` | const | 26 | 언어당 문법 파일 40개 상한 |
| `HighlightJob` | enum | 30 | `Build`, `Edit`, `Window`, `Drop` (`seq`로 오래된 결과 구분) |
| `Worker::run` | fn | 149 | 작업 목록을 처리해 `HighlightOutput` 반환 |
| `guard` | fn | 216 | `catch_unwind`로 패닉을 잡아 `Problem::Off("the highlighter stopped on an internal error")` 출력을 만들고 워커를 새로 만든다 (`:236-245`) |
| `Highlights::open/grammar_read/edit/visible/accept/rebuild/turn_off/close` | fn | 348-470 | 문서별 `Phase` 관리 |

### `ember/editor/src/paths.rs` (173줄)

- 목적: 탐색기 편집이 가리킬 수 있는 경로 검사 (D38, #438). 보안 경계가 아니라 실수 방지 장치라고 파일이 스스로 밝힌다 (`paths.rs:3-8`).
- `PathError` (`:10`), `normalize` (`:40`), `child_path` (`:74`), `target_path` (`:87`), `renamed_path` (`:100`), `folder_path` (`:113`), `split_stem_ext` (`:125`), `paste_destination` (`:137`).

### TextMate 인터프리터 (`ember/editor/src/textmate/`)

데이터 흐름: `GrammarCatalog`(어느 확장이 어떤 문법을 주는지) -> `parse_grammar`(파일을 `RawGrammar`로) -> `GrammarSet::add` -> `Grammar::new(set, root)`(규칙 컴파일) -> `DocumentTokens`(문서 단위 증분 토큰화) -> `role_for_scopes`(스코프를 색 역할로).

| 파일 (줄) | 목적과 주요 심볼 |
|---|---|
| `mod.rs` (23) | 하위 모듈 선언과 재수출 (`textmate/mod.rs:10-23`). 로더 쪽이라고 머리 주석이 밝힌다 |
| `catalog.rs` (183) | `GrammarEntry` (`:14`), `GrammarCatalog::from_extensions` (`:41`), `by_scope` (`:104`), `for_language` (`:109`), `injections_into` (`:114`), `skipped` (`:126`). 확장 폴더 밖으로 나가는 경로는 `resolve_inside` (`:162`)가 거르고 `skipped`에 기록한다 (`:6-8`) |
| `grammar.rs` (252) | JSON(`*.tmLanguage.json`)과 plist(`*.tmLanguage`)를 같은 `RawGrammar` (`:55`, `RawRule` `:69`)로 읽는다. YAML은 `GrammarError::UnsupportedFormat`로 거절 (`:3-5`). 상한 `MAX_GRAMMAR_BYTES` 4 MiB (`:26`), `MAX_RULES` 100,000 (`:28`), 깊이 제한. 잘못된 타입의 값은 버리고 나머지는 유지한다 (vscode-textmate와 같은 관대함, `:7-11`). `parse_grammar` (`:187`), `read_grammar` (`:229`), `referenced_scopes` (`:158`) |
| `plist.rs` (325) | XML plist 소형 리더. DOCTYPE은 Apple 형태만 허용하고 `[`(내부 서브셋)가 있으면 거절, 엔티티는 5개와 숫자 참조만, 크기 4 MiB, 노드 200,000, 깊이 64 상한 (`:19-23`), 재귀 없이 명시적 스택 (`:15-17`). `parse_plist` (`:199`) |
| `selector.rs` (203) | 스코프 선택자(`injectionSelector`, `injections` 키). `a.b`, 공백 경로, `-x`, `\|`/`,`, 괄호, `L:`/`R:` 우선순위. 길이 1024, 토큰 512, 깊이 16 상한 (`:19-23`). `Selector::parse` (`:183`), `Matcher::matches` (`:42`) |
| `roles.rs` (87) | 스코프 스택에서 가장 안쪽의 역할을 고른다. `SyntaxRole` 15종 (`:13`: Keyword, String, Comment, Number, Constant, Type, Function, Variable, Property, Operator, Punctuation, Tag, Attribute, Escape, Macro). `RULES` 표 (`:33`), `role_for_scopes` (`:85`). 역할이 없는 스코프는 기본 색 |
| `tokens.rs` (215) | `DocumentTokens` (`:75`): 줄과 줄 끝 상태, 줄별 색 구간을 보관. `apply_edit` (`:156`)는 바뀐 줄부터 다시 토큰화하고 줄 끝 상태가 이전과 같아지면 멈춘다 (`:3-8`). 같은 상태는 `Arc`로 공유. 8 MiB 또는 100,000줄 초과 문서는 `TooLarge` (`:22-27`). `runs_between` (`:147`) |
| `interpreter.rs` (1,267) | 아래 상세 |

### `ember/editor/src/textmate/interpreter.rs` (1,267줄)

- 목적: vscode-textmate 규칙을 하나씩 따라 하는 문법 컴파일러 겸 줄 단위 토크나이저 (`interpreter.rs:1-10`). 정규식은 Oniguruma(`onig`)가 실행한다. Cargo 주석에 따르면 순수 Rust 엔진은 Markdown과 YAML 문법의 규칙 26개를 거절하기 때문에 `onig`를 쓴다 (`ember/editor/Cargo.toml:20-23`).
- 지원: `match`, `begin/end`, `begin/while`, `captures`(중첩 `patterns`, 스코프 이름의 `$n`), `include`(`#repo`, `$self`, `$base`, 다른 문법 스코프, `scope#repo`), 시작 매치 캡처를 쓰는 end 패턴(`\1`), `applyEndPatternLast`, `\A`, `\G`, 진전 없는 push/pop 방지 (`:3-8`). 주입: 루트 문법의 `injections`와 `injectTo`+`injectionSelector`를 가진 문법. 루트 문법 자신의 `injections`만 센다 (`:12-15`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| 상한 | const | 29-40, 212, 215, 1083 | `MAX_LINE_BYTES` 20,000, `MAX_STACK_DEPTH` 256, `MAX_COMPILED_RULES` 200,000, `REGEX_RETRY_LIMIT` 500,000, `REGEX_STACK_LIMIT` 1,000,000, `MAX_INJECTIONS` 256, `MAX_ROOT_INJECTIONS` 192, `MAX_SEARCH_BUDGET` 2,000,000 |
| `Pattern::regex` | fn | 72 | `\A`, `\G`를 허용하는 위치에 따라 정규식을 따로 컴파일해 캐시. `disable_anchors` (`:100`)는 허용되지 않는 앵커를 매치 불가로 바꾼다 |
| `GrammarSet` | struct | 175 | `add` (`:186`), `add_injector` (`:191`), `contains` (`:198`) |
| `Grammar::new` | fn | 508 | 루트 스코프의 규칙을 `Builder`로 컴파일 (`include` 해석 `:383`). 실패한 규칙은 `problems()` (`:574`)에 쌓는다 |
| `Grammar::tokenize_line` | fn | 664 | 이전 줄의 `StateStack`을 받아 `LineTokens`와 새 상태를 반환 |
| `tokenize_string` | fn | 698 | 한 줄 안의 주 루프 |
| `match_rule_or_injections`, `match_injections`, `match_rule` | fn | 832, 852, 889 | 후보 중 가장 앞서는 매치 선택 (`Best`, `consider` `:1094`) |
| `check_while` | fn | 931 | `begin/while` 조건 확인 |
| `handle_captures` | fn | 982 | 캡처 그룹별 스코프와 중첩 패턴 |
| `SearchCache` | struct | 1065 | 줄마다 검색 횟수 예산 (`MIN_SEARCH_BUDGET + SEARCHES_PER_BYTE * len`을 `MAX_SEARCH_BUDGET`으로 제한, `:1075`). 초과하면 그 줄의 나머지는 칠하지 않는다 (`skipped`, `:1080-1082`) |
| `expand_name`, `resolve_backrefs` | fn | 1183, 1238 | `$n` 스코프 이름, `\n` 역참조 치환 |

- 주의: 지속 상태 `StateStack`은 `Arc`로 공유되고 (`tokens.rs`), `Builder.locals`는 `*const RawRule` 포인터를 키로 쓴다 (`interpreter.rs:298`). 안전한 코드지만 `RawGrammar`가 컴파일 중 이동하면 안 된다. 파일 안에 `unsafe`는 없다 (grep 확인).

## 동작 지도 (세션 입력과 결과)

이 모듈에는 화면이 없다. 위젯 이벤트가 들어와 무엇이 나가는지만 적는다. 화면 문구는 앱 모듈 문서를 본다.

| 위젯 이벤트 | 핸들러 | 결과 |
|---|---|---|
| `CodeChanged` | `engine.rs:612` `on_code_changed` | 문서 갱신, `$acceptModelChanged`, 장식 이동(`on_edit`), 인라인 재요청(`:819`), CodeLens 디바운스 재예약(`:424`), 하이라이트 `Edit`(`:1543`). 버전 불일치는 `Desync` |
| `CodeHovered` | `engine.rs:683` `on_hover_rest` | 일치 제공자마다 `$provideHover`, `SessionUpdate::Hover` |
| `CodeSaveRequested` | `engine.rs:732` `on_save` | `Effect::WriteFile`, 완료 시 `Saved` 또는 `SaveFailed` (`:741`) |
| `DecorationActivated` | `engine.rs:765` `on_activated` | `IdSpace`로 분기: CodeLens면 명령 실행(`run_command` `:780`), 고스트면 `accept_ghost` (`:937`) |
| `SelectionChanged`, `VisibleRangeChanged` | `engine.rs:648`, `:657` | 커서 기록, CodeLens 요청 범위, 하이라이트 창 이동 |
| `CodeEditRejected` | `bridge.rs:339` `on_edit_rejected` | `[확인 필요]` 엔진에서의 처리는 읽지 않았다 |
| 외부 변경 | `engine.rs:1599` `on_files_changed` | 깨끗한 버퍼는 조용히 다시 읽고, 수정 중이면 `ExternalChange::ChangedWhileDirty`, 삭제면 `Deleted` (`:135-142`) |

사용자에게 보이는 문구 (주요):

| 원문 | 위치 | 조건 |
|---|---|---|
| `이름이 올바르지 않습니다. 비어 있거나 / 가 들어 있으면 안 됩니다` | `paths.rs:27` | `PathError::BadName` |
| `프로젝트 폴더 밖의 경로입니다` | `paths.rs:28` | `OutsideFolder` |
| `프로젝트 폴더 자체는 바꿀 수 없습니다` | `paths.rs:29` | `FolderRoot` |
| `심볼릭 링크 폴더 안에는 만들 수 없습니다` | `paths.rs:30` | `Symlink` |
| `이름이 그대로입니다` | `paths.rs:31` | `SameName` |
| `폴더를 자기 자신이나 하위 폴더 안으로 옮길 수 없습니다` | `paths.rs:32` | `IntoSelf` |
| `This computer's editor server is Code-OSS {c}, but Ember's editor supports {} ({}). Opening in VS Code instead.` | `fallback.rs:30-34` | 서버 커밋 불일치 |
| `This computer's editor server version is unknown; ... Opening in VS Code instead.` | `fallback.rs:35-38` | 커밋을 알 수 없음 |
| `file is not UTF-8` | `document.rs:32` | UTF-8이 아닌 파일 열기 |
| `server refused the management connection: {0}` | `lib.rs:75` | 관리 핸드셰이크 응답이 `{"type":"ok"}`가 아님 |
| `session closed` | `lib.rs:78` | 세션 태스크 종료 후 송신 |

한국어 문구(`paths.rs`)와 영어 문구(`fallback.rs`, `lib.rs`)가 섞여 있다 (이슈 후보).

## 데이터와 설정

- DB, 저장 파일: 없다. 문서는 원격 서버 파일을 `RemoteFs`로 읽고 쓴다. 문법 파일은 확장 폴더에서 읽는다 (`ReadPurpose::Grammar`).
- 환경 변수: 이 크레이트는 읽지 않는다 `[확인 필요]` (`grep`으로 `env::var`를 찾지 않았다).
- 설정 입력: `SessionConfig` (`session.rs:51`), `CoreOptions` (`engine.rs:45`). 에디터 기본 설정 4개는 `session.rs:240-246`에 하드코딩이다.
- 외부 연동: OSE(Code-OSS) 서버 (관리 연결, 확장 호스트 연결), 고정 커밋은 `ember_editor_conn::PINNED_COMMIT`. C 컴파일러가 필요하다: `onig_sys`가 C 라이브러리를 `cc`로 빌드한다 (`Cargo.toml:21-23`).
- 테스트 데이터: `ember/editor/tests/fixtures/textmate` (자체 라이선스의 문법 사본). `Cargo.toml`이 패키징에서 제외 (`:10`). 테스트 `fr_e6_fixtures_stay_out_of_the_product.rs`가 제품 코드로 새지 않는지 검사한다.

## 이 모듈을 수정할 때 주의할 점

- `SessionUpdate`나 `Input`에 변형을 추가하면 `engine.rs`, `bridge.rs`(`apply`의 `match`, `:161`), 앱의 `editor_host.rs`와 `editor_workbench.rs`를 함께 고친다.
- RPC 대상 번호는 `ember_editor_conn`의 `rpc_ids.rs`와 고정 커밋에 묶여 있다. `PINNED_COMMIT`을 올리면 `ember/editor/src/engine.rs`의 `MainThreadCall` 분기와 `registry.rs`의 `InlineMeta`(위치 인자 17개)를 upstream 시그니처와 대조한다.
- 장식 레코드 44바이트 형식(`widget.rs:31`, `encode_records` `:164`)은 compose-rust FR-38 `DECORATION_LEN`과 일치해야 한다. 양쪽을 함께 바꾼다.
- `IdSpace`를 추가하려면 `ids.rs`의 `from_u8`과 `engine.rs` `on_activated`의 분기를 함께 고친다. id 상위 8비트가 공간이다.
- 문서 버전 규칙 `ext_base + v`를 바꾸면 `document.rs`의 `reset`과 `saved`, `engine.rs`의 `reset_doc` (`:1614`)를 함께 본다. 확장 호스트 버전은 감소하면 안 된다.
- effect는 순서대로 실행되어야 한다. `$acceptModelChanged`가 같은 버전의 요청보다 먼저 가야 한다 (`engine.rs:7-9`). `Driver::execute`를 병렬화하면 깨진다.
- 새 문법 규칙 기능을 넣을 때는 상한 상수(`interpreter.rs:29-40`)와 `tests/fr_e6_textmate_*.rs`, `textmate_real_grammars.rs`를 함께 갱신한다. 문법은 외부 입력이라 크기, 깊이, 시간 상한이 방어선이다.
- 빌드에 C 컴파일러가 필요하다. 새 플랫폼 CI는 Oniguruma 작업으로 확인한다 (`Cargo.toml:21-23`).
- `lib.rs:30-31`의 머리 주석은 "Status: written without compiling"이라고 말한다. 현재 사실과 맞는지 확인이 필요하다 (이슈 후보).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 거대 파일 | 중간 | `ember/editor/src/engine.rs` (1,707줄) | 검색/바꾸기, 인라인, CodeLens, 확장 호스트 요청 분기가 한 `impl`에 모여 있다. `on_exthost_request`만 약 120줄 (`:1017-1139`) | 기능별 파일로 `impl SessionCore`를 나눈다 |
| 거대 파일 | 낮음 | `textmate/interpreter.rs` (1,267줄) | 컴파일러와 토크나이저가 한 파일 | 컴파일(`Builder`)과 토큰화를 분리 |
| 중복 | 중간 | `search.rs:490` `glob_match`, `selector.rs:93` `glob_match` | 같은 이름, 다른 구현(정규식 기반 대 직접 매칭). 문법(`{a,b}` 중첩, `[!a]`, `**`)이 서로 다를 수 있다 | 한 구현으로 합치거나 차이를 문서화 |
| 죽은 코드 후보 | 중간 | `fallback.rs` 전체, `session.rs:142`, `:158` | 앱은 `EditorSession::connect_tcp`만 부르고 (`ember/app/src/editor_host.rs:220`) `connect_or_fallback`, `FallbackTarget`, `vscode_fallback_url`은 `ember/app/src`에서 찾지 못했다 (grep). 버전 불일치 시 VS Code 대체 동작이 앱에서 연결되지 않았을 수 있다 | `[확인 필요]` 앱이 다른 경로로 대체를 처리하는지 확인 |
| 문서 불일치 | 낮음 | `lib.rs:30-31` | "written without compiling" 상태 문구가 남아 있다. 테스트가 16개 파일 있다 | 현재 상태에 맞게 갱신 |
| 보안 | 낮음 | `paths.rs:3-8` | 파일이 스스로 보안 경계가 아니라고 밝힌다. OSE 파일 채널은 서버 사용자 권한으로 쓰고 폴더 경계가 없다. 심볼릭 링크는 부모에서 `refuse_symlink_parent`로만 막는다 | 설계 의도 확인. 서버 쪽 경계가 필요하면 별도 이슈 |
| 보안 | 낮음 | `grammar.rs`, `plist.rs`, `selector.rs`, `interpreter.rs` | 확장이 주는 문법은 외부 입력이다. 크기, 깊이, 노드, 정규식 시간 상한이 이미 있다 (`MAX_*`, `REGEX_RETRY_LIMIT`). 문서 쪽 방어는 충분해 보이나 Oniguruma 자체의 C 코드 취약점은 범위 밖 | 해당 없음 (정보) |
| 하드코딩 | 낮음 | `session.rs:240-246`, `engine.rs:56-63` | 에디터 기본 설정(탭 4칸, 코드렌즈 켬 등)과 디바운스가 코드에 고정 | 사용자 설정과 연결할 때 `user_settings` 경로를 쓴다 |
| 언어 혼용 | 낮음 | `paths.rs:27-32` 대 `fallback.rs:30`, `lib.rs:75` | 사용자 문구가 한국어와 영어로 섞여 있다 | 문구 정책 통일 |
| 기능 공백 | 중간 | `session.rs:14-17` | 재연결 없음, 작업 폴더 1개, 런타임 설정 변경 없음 (문서가 직접 밝힘). 연결이 끊기면 `ConnectionLost`로 종료 | 별도 이슈로 추적 |
| 기능 공백 | 낮음 | `engine.rs:1030-1034` | `setContext`는 아무것도 하지 않는다 (주석: "no-op for Ember for now") | 필요해지면 구현 |
| TODO/FIXME | - | `ember/editor/src` 전체 | 0개 (grep) | - |
| 테스트 위치 | 낮음 | `bridge.rs`, `engine.rs`, `session.rs`, `highlight.rs`, `paths.rs`, `textmate/*` | 소스 내 단위 테스트가 0개. `tests/`(`widget_bridge.rs`, `engine_flow.rs`, `explorer_paths.rs`, `fr_e6_textmate_*.rs`)가 대신 검증한다 | 정보 |

모듈 파일 30개와 `Cargo.toml` 모두 이 문서에 이름이 나온다: `bridge`, `codelens`, `commands`, `coords`, `diagnostics`, `document`, `engine`, `fallback`, `highlight`, `hover`, `ids`, `inline`, `languages`, `lib`, `output`, `paths`, `registry`, `replies`, `search`, `selector`, `session`, `widget`, `textmate/{catalog,grammar,interpreter,mod,plist,roles,selector,tokens}`.
