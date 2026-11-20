# 모듈: app-ui-cr-session

- 경로: `ember/app/src/ui/cr/project.rs` (1,894줄), `ember/app/src/ui/cr/conversation.rs` (2,208줄), `ember/app/src/ui/cr/session.rs` (5,180줄). 합계 9,282줄. 세 파일 모두 이 문서에 나온다 (3/3).
- 레이어: 앱 UI (compose-rust). 기본 실행 경로의 실사용 화면이다 (`ui::cr::shell::launch`, `ember/app/src/lib.rs:143-145`).
- 한 줄 책임: 프로젝트 화면(컴퓨터 띠, 프로젝트 상자, 프로젝트 상세, 설정 시트), 대화 화면(대화 기록, 입력창, 승인과 질문 카드, 팀 패널), 세션 화면(좌측 목록, 멀티/싱글/상태 3개 뷰, 새 팀원 시트, IDE와 웹 페이지 메뉴).
- 의존: `crate::services`(`services()`, `run_shared`), `crate::server::ServerApi`, `ember_client::Client`와 `wire`, `crate::ide`, `crate::model`, `crate::demo`, `crate::bridge`, `crate::terminal_stream`, 같은 폴더의 `shell`, `home`, `components`, `compat`, `launcher`, `notice`, `ko`, `theme`, `characters`, `a11y`, `add_computer`, `monitor`, `vcs`.
- 이 모듈을 쓰는 모듈: `ember/app/src/ui/cr/shell.rs:649` (`ProjectScreen`), `shell.rs:661`, `shell.rs:663` (`SessionScreen`), `ember/app/src/ui/cr/home.rs:1242` (`session::SendCircleButton`). `ConversationView`는 `session.rs:2467`의 `SingleView`에서만 `embedded = true`로 부른다.
- 서비스 호출 의미는 `docs/analysis/modules/client.md`, `server-api.md`, `server-core.md`를 따른다. `app-core.md`는 없어서 `ember/app/src/services.rs`, `ember/app/src/server.rs`는 필요한 줄만 읽었다.

## 가장 중요한 사실 (먼저 읽을 것)

1. **라이브 UI에서 대화 화면은 항상 `embedded = true`로만 뜬다** (`session.rs:2467`). `Screen::Conversation(id)`도 `SessionScreen(Some(id))`로 간다 (`shell.rs:660-661`). `embedded = false`인 `ConversationView("demo-s1", false)`는 테스트에서만 부른다 (`conversation.rs:2175`). 따라서 `conversation.rs`의 독립 헤더(제목, "더보기" 메뉴: 고정, 내보내기, 마지막 턴에서 포크, 자동 승인), "컴퓨터" 전환 줄, 대화 화면의 "IDE 열기" 줄은 현재 라이브에서 도달할 수 없다 (`conversation.rs:567-692`, `1073-1199`).
2. 세션 단위 **컴퓨터 전환**(`PUT /api/sessions/{id}/computer`)은 `session.rs`에 호출이 없다. 다른 화면(`ember/app/src/ui/cr/home.rs:666`, `ember/app/src/ui/cr/new_session.rs:238`)에만 있다. 이 3개 파일 안에서 도달 가능한 전환 UI는 없다 (`conversation.rs:1155`는 위 1번의 도달 불가 경로).
3. **모델 선택은 구현되지 않았다.** 칩을 누르면 `"실행 중인 세션의 모델은 바꿀 수 없습니다 (준비 중입니다)"` 한 줄짜리 시트만 열린다 (`session.rs:91`, `326-333`).
4. **보관(archive)과 세션 이름 바꾸기는 이 3개 파일에 없다.** `launcher.rs:159-164`의 메뉴가 `patch_session`을 쓴다. 대화 화면의 `SessionPatch`는 `pinned`뿐이고(`conversation.rs:1095-1101`) 이것도 위 1번 때문에 도달 불가이다.
5. **사용량(usage)은** 상태 뷰의 "오늘 토큰" 타일 하나뿐이다 (`session.rs:3680-3683`). 세션별 `GET /api/sessions/{id}/usage`를 부르는 곳은 없다 (`client.md`도 호출 없음으로 기록).

## 공개 인터페이스

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

## 파일별 요약

### `ember/app/src/ui/cr/project.rs` (1,894줄, 테스트 약 17개 `project.rs:1656` 이후)

- 목적: FR-L1~L4, L24, L26. 컴퓨터 띠, 프로젝트 상자 그리드, 한 프로젝트 전체 보기, 새 프로젝트 시트, 설정 시트. 상자, 멤버, 정렬, 필터 결정은 `crate::ui::project`의 순수 함수를 그대로 쓴다 (`project.rs:1-9`).
- 주요 심볼

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Ui` | struct | 162 | 화면 상태: `full`, `settings`, `computer`, `new_project`, `new_draft`, `query`, `expanded`, `filter`, `search_open` |
| `set_assignment` | fn | 219 | 컴퓨터 할당/해제 (`assign_computer`/`unassign_computer`) |
| `ProjectScreen` | composable | 238 | `ui.live.launcher` 신호를 읽고 `project_boxes_with_archived`로 상자 계산 |
| `Grid`, `ComputerStrip`, `ProjectBoxView` | composable | 407, 438, 553 | 목록 화면 |
| `FullProject`, `KpiStrip`, `MembersCard` | composable | 760, 939, 1011 | 상세 화면 |
| `IdeMenu`, `launch_ide` | composable/fn | 886, 845 | 첫 세션 기준 IDE 대상 조회와 실행 |
| `Sheets`, `SettingsSheet`, `SkipSection`, `SheetSkip` | composable/struct | 1076, 1417, 1279, 1256 | 새 프로젝트, 컴퓨터 모니터, 설정 시트. `SheetSkip`은 캡처용 스크롤 환경변수 처리 |
| `create_project`, `save_settings` | fn | 1313, 1376 | 프로젝트 생성(POST 후 PATCH)과 설정 저장(PATCH) |

- 의존 (`crate::ui::*`): `crate::ui::characters::CharStyle` (`project.rs:29`), `crate::ui::coexist::{shared_ui, SharedUi}` (`:42`), `crate::ui::shell::NavMenu` (`:43`), `crate::ui::project` (`ProjectBox`, `NewProjectDraft`, `SettingsDraft`, `SOON`, `NOT_YET`, `SETTINGS_SAVE_AVAILABLE`, `create_error_message`, `patch_error_message` 등, `:21-27`), `crate::ui::session::ide_choices` (`:909`). 비-ui: `crate::model::status_rank`, `crate::ide`, `crate::server::IdeLaunch`, `crate::services`.
- 부수효과: 프로젝트 PATCH/POST/PUT/DELETE, 이름 변경 시 `ui.update_prefs`로 기기별 설정 키 이동 (`project.rs:1399-1405`), `notice::post`로 토스트.
- 주의: `EMBER_CR_PROJECT`, `EMBER_CR_ROUTE`, `EMBER_CR_PROJECT_SHEET`, `EMBER_CR_PROJECT_EXPAND`, `EMBER_CR_PROJECT_SEARCH`(디버그 빌드만), `EMBER_CR_IDE_MENU`, 시트 스크롤 환경변수는 캡처용 훅이다 (`project.rs:186-205`, `:891`).

### `ember/app/src/ui/cr/conversation.rs` (2,208줄, 테스트 약 3개 `conversation.rs:2132` 이후)

- 목적: FR-L5~L7, T6, T7, A5, S5. 헤더, `LazyColumn` 대화 기록(이벤트 seq 키), 입력창(Enter 전송, 에이전트가 일하는 동안은 큐에 쌓음), `@@` 멘션, 도구 호출 카드, 승인 카드, 질문 카드, 팀 패널.
- 주요 심볼

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `ConversationView` | composable | 155 | 본체. `load`(팀, 포크 정보, approve-all, 컴퓨터, IDE 대상 조회)는 시작 시 한 번 (`:225-228`) |
| `send` 클로저 | closure | 316 | 멘션 치환 후 `outbox.push` -> `bump_outbox` -> `drive_outbox` |
| `TranscriptRow` | composable | 1486 | `User`, `Assistant`(스트리밍이면 `▉`와 Spinner, `:1523-1531`), `ToolCall`, `Approval`, `Question`, `TurnEnded`, `Error`, `Notice` 8종 |
| `QuestionCard` | composable | 1279 | 질문 답/건너뛰기 (2단계 확인, 비밀 입력 차단) |
| `TeamPanel` | composable | 1933 | 팀원 상태, 열기, 종료, 작업 목록 |
| `fork_from` | fn | 130 | `Client::fork_session` 후 `open_conversation` |
| `demo_blocked_cr` | fn | 118 | 데모에서 막힌 동작이면 안내 토스트 |

- 의존 (`crate::ui::*`): `crate::ui::coexist::{SharedUi, shared_ui}` (`:44`), `crate::ui::question as qv` (`:45`, 질문 초안과 고정 문구), `crate::ui::Route` (`:46`, `Route::Projects`), `crate::ui::session`의 `SIDE_W`/`RAIL_W`/`SIDE_LIST_W`/`INFO_PANEL_W` 등 (`:894-909`에서 경로로 직접 참조). 같은 폴더: `compat`, `components`, `ko`, `launcher::{ConnectionBanner, export, patch_session}` (`:54`), `notice`, `shell::{ICON_PLUS_SVG, NavIcon}`, `session::{launch_ide_shared, ModeChip, ModelChip, StopCircleButton, SendCircleButton, ide_main_click, IdeChevron}`.
- 부수효과: 전송은 outbox를 거쳐 `Client::send_message`. 에이전트가 바쁜 동안 보낸 글은 큐에 남고 턴 경계에 나간다 (FR-L6, `services.rs:99-125`).
- 주의: 순환 import. `conversation.rs`가 `session.rs`를 쓰고 `session.rs:57`이 `conversation.rs`를 쓴다 (`docs/analysis/_raw/cycles.md:28`, `:40`에 두 파일이 등재됨).

### `ember/app/src/ui/cr/session.rs` (5,180줄, 테스트 약 10개 `session.rs:4978` 이후)

- 목적: FR-L5~L7, L15, L16, L18, L24. 좌측 세션 목록, 상단 바(프로젝트, 뷰 전환, 새 팀원, 버전 관리, 웹 페이지, IDE), **멀티**(칸 여러 개, 칸 탭), **싱글**(대화 + 우측 정보 패널), **상태**(칸반, KPI, 카드).
- 순수 결정(`SessionView`, `PaneLayout`, `ProjectPanes`, `side_sections`, `kanban`, `lease_plan`, `model_chip_label`, `mode_rows`, `environment_rows` 등)은 `crate::ui::session`에 있고 여기서 `pub use`로 재수출한다 (`session.rs:29-40`).
- 주요 심볼

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `SessionScreen` | composable | 4353 | 프로젝트 해석, 뷰 선택, 목록/레일/서랍, 시트와 메뉴 5종 |
| `use_leases_cr` | fn | 149 | 화면에 보이는 세션만 `services().open_session`/`close_session` (lease와 이벤트 로드) |
| `edit_panes`, `panes_of`, `default_panes_for` | fn | 124, 138, 108 | 칸 배치를 `ui.update_prefs`(기기별 설정 파일)에 저장 |
| `launch_ide_shared` | fn | 171 | IDE 대상 계획(`plan`) 후 OS 열기 또는 Ember 에디터 화면 |
| `ModelChip`, `ModeChip` | composable | 259, 337 | 모델 칩(잠김), 권한 모드 칩(`approve_all`) |
| `IdeMenu` | composable | 524 | 세션별 IDE 대상 조회 (`ide_targets`) + 분할 버튼 + 선택 시트 |
| `PaneTerminal` | composable | 1105 | 세션 컴퓨터를 조회하고 `terminal_stream::start_view`로 읽기 전용 터미널을 붙임 |
| `NewMemberSheet` | composable | 3952 | 새 팀원 시트 -> `create_session` |
| `StatusView`, `StatusCardsGrid` | composable | 3622, 3583 | KPI 6개, 칸반, PR/서브에이전트/부하 카드 |
| `TimelineCard` | composable | 2882 | "에이전트 간 통신" 타임라인. 데모 레인 상수(`DEMO_TL_LANES`, `:2671`)를 쓴다 |

- 의존 (`crate::ui::*`): `crate::ui::coexist::{SharedUi, shared_ui}` (`:46`), `crate::ui::project::{Member, display_name, project_boxes, project_boxes_with_archived, status_pill}` (`:47`), `crate::ui::session::{...}` (`:29`, `:94`), `crate::ui::shell::{nav_mode, ShellMode}` (`:1409`), `crate::ui::term_pane` (`:1107`), `crate::ui::home::today_utc` (`:3682`), `crate::ui::session::{view_seg_icon_only, drawer_open_effective, drawer_width}` (`:4453`, `4850`, `4861`). 비-ui: `crate::bridge::request_project_day` (`:3681`), `crate::terminal_stream`, `crate::ide`, `crate::server`.
- 부수효과: 세션 lease (서버에 `POST /sessions/{id}/lease` 주기 호출은 `Client::open_session`), `terminal_stream` 연결(백그라운드 스레드, 화면에서 나가면 detach `:1137-1146`), prefs 쓰기(`last_project`, `session_view`, `panes`).

## 동작 지도

표기: 서버 라우트는 `docs/analysis/_raw/routes.md` 기준 (핸들러 위치 포함). `Client`/`Api` 메서드 의미는 `client.md`. "라이브" 열이 `도달 불가`이면 위 "가장 중요한 사실 1"에 해당한다.

### A. 프로젝트 화면 (`project.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 `경로:줄` | 호출 API `경로:줄` | 서버 라우트 |
|---|---|---|---|---|
| 화면 열기 | "프로젝트", "프로젝트를 누르면 세션으로 들어가 팀원들의 대화를 함께 봅니다." (`project.rs:411`) | `ProjectScreen` `project.rs:238` | `services().client.read(...)` (캐시 읽기만, `:242`) | 없음 (push로 갱신) |
| 프로젝트 없음/검색 결과 없음 | "아직 프로젝트가 없습니다" / "일치하는 프로젝트가 없습니다" (`:421`), "프로젝트를 찾을 수 없습니다" (`:261`) | `Grid` `:407` | 없음 | 없음 |
| 팀원 검색 | "팀원 검색" (`:358`, `:416`) | `toggle_search` `:332`, `box_matches` `:112` | 없음 (로컬 필터) | 없음 |
| 컴퓨터 칩 누름 | "등록된 컴퓨터가 없습니다" (`:441`) | `ComputerStrip` `:438` -> `st.computer.set` `:459` | `MonitorSheet` (`monitor.rs`, 이 문서 범위 밖) | 없음 [확인 필요: monitor 내부 호출] |
| 컴퓨터 추가 | "컴퓨터 추가" (`:467`) | `AddUi::show` `:464` | `add_computer.rs` (범위 밖) | 없음 [확인 필요] |
| 새 프로젝트 버튼 | "새 프로젝트" (`:383`), 비활성이면 토스트 "준비 중입니다" (`ember/app/src/ui/project.rs:41`) | `open_new` `:372-378` | **데모에서만 활성** (`can_create = services().demo.is_some()` `:374`) | 없음 (비데모에서는 도달 불가) |
| 새 프로젝트 "만들기" | "새 프로젝트", "이름", "프로젝트 이름", "저장소", "기본 브랜치", "비워 두면 {main}을 씁니다", "팀 캐릭터", "취소", "만들기"/"만드는 중" (`:1110-1192`) | `create_project` `:1313` | 데모: `d.create_project` `:1329`. 서버: `client.api().create_project` `:1340-1343`, `load_projects` `:1344`, 이어서 `client.patch_project` `:1348` | `POST /api/projects` (`ember/server/src/api/mod.rs:93`), `PATCH /api/projects/{name}` (`mod.rs:94`) |
| 새 프로젝트 닫기 확인 | "변경 사항", "계속 편집", "닫기" (`:1202-1209`) | `SettingsGuard` `:1096-` | 없음 | 없음 |
| 상자 이름 누름 | 프로젝트 이름, 저장소 줄 (`:563-565`) | `st.full.set` `:561` | 없음 | 없음 |
| 상자의 버전 관리 아이콘 | (아이콘, 접근성 이름 `a11y::VERSION_CONTROL`) | `shell::choose(NavMenu::VersionControl)` `:577-580` | 없음 | 없음 |
| 상자의 설정 아이콘 | `a11y::PROJECT_SETTINGS` | `st.settings.set` `:583` | 없음 | 없음 |
| "세션 열기"(원형 버튼/상세 상단) | "세션 열기" (`:790`) | `OpenSessionButton` `:661`, `FullProject` `:790-793` | 첫 팀원 있으면 `ui.open_conversation`, 없으면 `ui.open_new_session` (`ember/app/src/ui/coexist.rs:220`, `:367`) | 없음 |
| 팀원 타일 누름 | 팀원 이름, 작업, 상태 알약(`status_pill`) | `MemberTile` `:732`, `:742` -> `open_conversation` | 없음 | 없음 |
| 팀원 덱 펼치기/접기 | "외 N명", "접기" (`:617`) | `DeckCard` `:631`, `:609-621` | 없음 | 없음 |
| "새 팀원" | "새 팀원" (`:396`) | `NewMemberButton` `:392` -> `open_new_session` | `new_session.rs` (범위 밖) | 없음 (여기서는) |
| 상세 "IDE 열기" | "IDE 열기"/"IDE", "세션이 없어 IDE를 열 수 없습니다" (`:916-918`) | `IdeMenu` `:886`, `ide_main_click` `session.rs:470` | `services().server.ide_targets(&sid, None)` `project.rs:904` (`server.rs:452`) | `GET /api/sessions/{id}/ide` (`ember/server/src/api/ide.rs:483`) |
| IDE 항목 선택 | "Ember 에디터", "VS Code", "JetBrains Gateway"(`session.rs:100-106`); 토스트 "{IDE}: 여는 중입니다", "...열지 못했습니다: {e}", "...사용할 수 없습니다: {why}", "IDE 목록을 받아오는 중입니다", "IDE 목록을 받지 못했습니다: {e}", "Ember 에디터: 서버가 OSE 런타임을 시작하지 못했습니다" (`project.rs:845-879`) | `launch_ide` `:845` | `open_external(&url)` (`ember/app/src/ide.rs`) 또는 `ui.open_editor_connection` `:876` | 없음 (대상 조회는 위 행) |
| 설정 시트 열기 | "{이름} 설정", 구역 "기본", "컴퓨터", "새 팀원 기본값", "팀 캐릭터", "리더 (오케스트레이터)", "프로필 덮어쓰기", "연결", "위험 영역" (`:1468-1625`) | `SettingsSheet` `:1417` | 없음 (시트 열 때) | 없음 |
| 컴퓨터 "할당"/"할당됨" | "컴퓨터", "이 프로젝트의 팀원이 일할 수 있는 컴퓨터입니다", "할당", "할당됨" (`:1515-1528`) | `set_assignment` `:219` | `client.assign_computer` / `unassign_computer` `:222-223` | `PUT`/`DELETE /api/projects/{name}/computers/{computer_id}` (`mod.rs:95`) |
| 설정 "저장" | "저장"/"저장 중", "취소" (`:1462`) | `save_settings` `:1376` | `services().client.patch_project(&project, &patch)` `:1394` | `PATCH /api/projects/{name}` (`mod.rs:94`) |
| 리더, 보관, 삭제 | "프로젝트 보관", "프로젝트 삭제" (`:1627-1628`), 힌트 "리더 지정은 서버가 아직 지원하지 않습니다" (`:1592`) | 빈 핸들러 `|| {}` `:1627` (TODO #384) | 없음 | 없음 (서버 `not_yet`) |
| 캐릭터 전체 보기 | "캐릭터 전체 보기" (`:1583`) | `SettingsSheet` 내부 | `characters_screen` (범위 밖) | 없음 |
| 알림 | "컴퓨터 할당을 바꾸지 못했습니다: {e}" (`:228`) | `set_assignment` | | |

### B. 대화 화면 (`conversation.rs`, 라이브는 `embedded = true`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 `경로:줄` | 호출 API `경로:줄` | 서버 라우트 |
|---|---|---|---|---|
| 대화 열림 (세션 선택) | "아직 대화가 없습니다" (`:2128`), "대화를 불러오는 중입니다..." (`:2126`), 세션 없음: "이 세션을 찾을 수 없습니다.", "삭제되었거나 아직 목록을 불러오는 중입니다.", "프로젝트로 돌아가기" (`:354-373`) | `ConversationView` `:155`, `load` `:206-299` | 팀 `client.load_team` `:218`; 포크 정보 `load_fork_info` `:233`; `load_approve_all` `:250` (둘 다 `GET /sessions/{id}`); `server.session_computer` `:276`; `server.ide_targets` `:291`; 멘션 후보는 `@@` 입력 시 `client.mention_candidates` `:190` | `GET /api/sessions/{id}/team` (`a2a/api.rs:83`), `GET /api/sessions/{id}` (`api/mod.rs:87`), `GET /api/sessions/{id}/computer` (`computers/api.rs:41`), `GET /api/sessions/{id}/ide` (`api/ide.rs:483`), `GET /api/sessions/{id}/mentions` (`a2a/api.rs:82`) |
| lease와 이벤트 로드 | (화면 없음) | `use_leases_cr` `session.rs:149-168` -> `services().open_session` `:161` (`services.rs:81`) | `Client::open_session` (`client.md`: 주기 lease, 이벤트 gap 복구) | `POST /api/sessions/{id}/lease` (`mod.rs:102`), `GET /api/sessions/{id}/events` (`mod.rs:96`), `GET /api/push` (`mod.rs:103`) |
| 메시지 전송 (Enter 또는 보내기) | 입력창 힌트: 바쁠 때 "다음 턴에 보낼 메시지를 입력하세요", 평소(임베디드) "무엇이든 물어보세요" (폰) / "무엇이든 물어보세요. @로 파일, /로 명령", 비임베디드 "메시지를 입력하세요 (@@로 세션 멘션)" (`:928-938`, `:1020-1026`) | `send` `:316-337`, 제출 `:949-951`, 보내기 `SendCircleButton` `:1060` | `outbox.push` `:333`, `bump_outbox` `:334`, `drive_outbox` `:335` (`services.rs:99`) -> `s.client.send_message(&sid, &text)` `services.rs:115` | `POST /api/sessions/{id}/messages` (`api/mod.rs:97`) |
| 큐에 쌓임 (에이전트가 바쁜 동안) | 배지 "{n}개 대기 중", "이번 턴이 끝나면 순서대로 전송합니다. 다음: {첫 줄}" (`:765-769`) | `drive_outbox`가 `is_busy`면 보내지 않음 (`services.rs:99-105`) | 턴 경계에 `next(id, busy, last_seq)` | 위와 같음 |
| 큐 비우기 | "비우기" (`:780`) | `:787-788` | `outbox.clear`, `bump_outbox` (로컬) | 없음 |
| 전송 실패 | 배너 "전송하지 못했습니다: {오류}", 버튼 "다시 시도" (`:801-807`) | `:813` -> `drive_outbox` | `services.rs:114-119`에서 `outbox.failed` | `POST .../messages` 재시도 |
| 스트리밍 응답 | 마지막 텍스트에 `▉`와 스피너 (`:1523-1531`) | `TranscriptRow` `Assistant{streaming}` | 없음. push로 `ui.live.transcripts` 갱신 (`:414`) | `GET /api/push` |
| 중단 | "중단" (비임베디드 `:1033`), 임베디드는 빨간 원형 정지 버튼 `StopCircleButton` (`:966`); 실패 토스트 "중단하지 못했습니다: {e}" (`:984`, `:1055`, 칸 입력창 `session.rs:1312`) | `:966-989`, `:1040-1061`, `PaneComposer` `session.rs:1297-1315` | `services().client.interrupt(&id)` `conversation.rs:977`, `session.rs:1306` (`client.rs:304`) | `POST /api/sessions/{id}/interrupt` (`api/mod.rs:101`) |
| 도구 호출 카드 펼침 | 상태 "실행 중"/"오류"/"완료", 제목 "도구", "자세히"/"접기", "입력", "오류"/"결과" (`:1550-1630`) | `expanded` 토글 `:1600-1606` | 없음 | 없음 |
| 승인 응답 | "{tool} 실행을 허용할까요?", "대기 중", 버튼 "한 번 허용", "항상 허용", "거부"; 결과 "허용함", "항상 허용", "거부함"; "에이전트가 이 요청을 거두었습니다", "턴이 끝나기 전에 응답하지 않았습니다" (`:1695-1829`) | `answer` 클로저 `:1654-1675` | `services().answer(&s_id, &a_id, decision)` `:1665` -> `client.answer` (`services.rs:128`) | `POST /api/sessions/{id}/approvals/{approval_id}` (`api/mod.rs:98`) |
| 응답 실패 | "응답하지 못했습니다: {e}" (`:1671`) | 위 | | |
| 질문에 답함 / 건너뜀 | 카드 "에이전트의 질문", "답 필요", "보내기", "건너뛰기", "정말 건너뛰기", "이 질문을 거절하고 건너뜁니다. 다시 누르면 보내게 됩니다", "직접 입력", "답을 보냈습니다. 에이전트의 응답을 기다리고 있습니다", "건너뜀", "답하지 않고 끝났습니다", "에이전트가 이 질문을 거두었습니다", 비밀 질문 "비밀 입력은 이 앱에서 받지 않습니다. 컴퓨터의 터미널에서 답해야 합니다" / "여기서는 건너뛸 수만 있습니다" (`ember/app/src/ui/question.rs:20-34`) | `send` 클로저 `:1318-1349`, 건너뛰기 `tap_skip` `:1360` | `services().answer_question(&s_id, &q_id, &reply)` `:1343` -> `client.answer_question` (`services.rs:144`) | `POST /api/sessions/{id}/questions/{question_id}/answer` (`api/mod.rs:99`) |
| 질문 실패 | "이 질문은 이미 답했거나 끝난 질문입니다.", "답이 질문과 맞지 않습니다. 선택을 확인해 주세요.", "에이전트가 실행 중이 아니어서 답을 보낼 수 없습니다.", "이 질문에는 소유자만 답할 수 있습니다.", "답을 보낼 수 없습니다. 앱을 업데이트해 주세요.", "답을 보내지 못했습니다. 연결을 확인하고 다시 시도해 주세요." (`ember/client/src/api.rs:132-137`) | `failed.set` `:1356` | | 서버 응답 본문은 UI에 나오지 않는다 (`services.rs:140-143` 주석) |
| 턴 끝 줄과 "여기서 포크" | "턴 완료"/"중단됨"/"턴 실패", "여기서 포크" (`:1852-1854`, `ko.rs:46`) | `:1881-1883` | `fork_from(&ui, sid, Some(seq))` `:130` -> `client.fork_session(&id, seq)` `:138` | `POST /api/sessions/{id}/fork` (`api/mod.rs:89`) |
| 포크 후 | 토스트 "포크하지 못했습니다: {e}" (`:145`), 성공이면 새 세션 `open_conversation` `:144` | `fork_from` | | |
| 포크된 세션의 "원본 열기" | "{부모}에서 포크됨", "원본 열기" (`ko.rs:49-51`, `:619`) | `:625` | 없음 | 없음 |
| `@@` 멘션 선택 | "세션 멘션", "멘션 대상: {목록}", "지우기" (`:826`, `:863`, `:872`) | `on_draft` `:539-550` | `mention_candidates` (위) | `GET /api/sessions/{id}/mentions` |
| 모드 칩 (권한/자동 승인) | 칩 문구 `mode_chip_label` (`ui/session.rs:881`), 잠김 항목은 "{모드} (준비 중입니다)", 배너 "모든 요청 자동 승인이 켜져 있습니다: 이 세션의 도구 요청을 묻지 않고 허용합니다." (`ko.rs:33`) | `ModeChip` `session.rs:337`, 선택 `:419-437` | `services().set_approve_all(&s_id, enable)` `session.rs:429` (`services.rs:180`) -> `client.set_approve_all` | `PUT /api/sessions/{id}/approve-all` (`api/mod.rs:100`) |
| 모드 변경 실패 | "모드를 바꾸지 못했습니다: {e}" (`session.rs:432`) | | | |
| 모델 칩 | 칩 `model_chip_label` + " · 높음"(고정 문자열, `session.rs:284`), 시트 "실행 중인 세션의 모델은 바꿀 수 없습니다 (준비 중입니다)" (`:91`, `:324`) | `ModelChip` `:259` | 없음. 선택해도 닫힐 뿐 (`:331`) | 없음 |
| 파일 첨부 "+" | 토스트 "파일 첨부는 준비 중입니다" (`:954`) | | 없음 | 없음 |
| 팀 패널 | "팀 · 팀원 {n}명 · 열린 작업 {n}개", "접기"/"펼치기", "{이름} (리더)", "{에이전트} · 종료됨", "작업 {n}", "열기", "종료", "등록된 작업이 없습니다" (`:1977-2096`) | `TeamPanel` `:1933` | 종료: `client.end_teammate(&t_id, &s_id)` `:2074` | `POST /api/teams/{team_id}/members/{session_id}/end` (`a2a/api.rs:86`) |
| 팀원 종료 토스트 | "{이름} 팀원을 종료했습니다" / "{이름} 팀원을 종료하지 못했습니다: {e}" (`:2082-2085`) | | | |
| **(도달 불가) 더보기: 고정/해제** | "고정"/"고정 해제" (`:1074-1078`) | `:1095` -> `launcher::patch_session` (`launcher.rs:229`) | `services().patch_session` -> `client.patch_session` | `PATCH /api/sessions/{id}` (`api/mod.rs:87`) |
| **(도달 불가) 내보내기** | "내보내기"; 토스트 "내보냈습니다: {경로}" / "내보내지 못했습니다: {e}" (`launcher.rs:246-256`) | `:1102` | `crate::export::export_session` -> `Api::export_session` | `GET /api/sessions/{id}/export` (`api/mod.rs:88`) |
| **(도달 불가) 마지막 턴에서 포크 / 자동 승인 토글** | "마지막 턴에서 포크", "모두 자동 승인"/"도구 실행 전 다시 묻기" (`ko.rs:38-43`) | `:1103`, `:1104-1114` | `fork_from`, `set_approve_all` | 위와 같음 |
| **(도달 불가) 컴퓨터 전환** | "컴퓨터", 항목 "{이름} (온라인/오프라인/확인 중...)", "등록된 컴퓨터가 없습니다", 토스트 "{이름} 컴퓨터로 전환했습니다" / "컴퓨터를 전환하지 못했습니다: {e}" (`:638`, `:1117-1172`) | `:1146-1175` | `services().server.switch_computer(&s_id, &cid)` `:1157` (`server.rs:444`) | `PUT /api/sessions/{id}/computer` (`computers/api.rs:41`) |
| 데모에서 막힘 | `crate::demo::unavailable` 문구 (`:118-126`) | `demo_blocked_cr` | | |

### C. 세션 화면 (`session.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 `경로:줄` | 호출 API `경로:줄` | 서버 라우트 |
|---|---|---|---|---|
| 세션 메뉴 열기 | 프로젝트 없음: "프로젝트가 없습니다", 버튼 "새 세션" (`:4423`, `:86`) | `SessionScreen` `:4353`, `shell.rs:660-663` | `services().client.read(project_boxes_with_archived)` `:4408` | 없음 |
| 좌측 목록에서 팀원 선택 | "세션", "세션 검색" (`:737`, `:761`), 드래그 안내 "팀원을 끌어 칸에 놓을 수 있습니다" (`:765`) | `open_member` `:4510-4535` | 멀티: `edit_panes` -> `add_pane` (prefs). 그 외: `ui.open_conversation` | 없음 |
| 보기 전환 | "멀티", "싱글", "상태" (`ui/session.rs:338-340`) | `set_view` `:4499-4505`, `ViewSeg` `:3833`, `:4724` | `ui.update_prefs(session_view)` (로컬 파일) | 없음 |
| 프로젝트 고르기 | 시트 항목 = 프로젝트 이름 (`:4930-4950`) | `:4942-4945` | `ui.update_prefs(last_project)` | 없음 |
| 새 팀원 시트 열기 | "새 팀원" (`:4730`) | `new_member_open.set` `:4734` | 없음 | 없음 |
| 새 팀원 "만들기" | "새 팀원"(제목), "역할 이름", "예: 구현, 리뷰, 문서", "첫 지시 (선택)", "이 팀원이 할 일을 적으세요", "하네스, 모델, 권한 모드", "프로필 Claude 개인", "컴퓨터", "취소", "만들기" (`:4051-4325`) | `create_cb` `:3984-4034` | `services().create_session(&body)` `:4020` -> `server.create_session` (`services.rs:161-167`) 후 `Input::SessionLoaded`. `agent`는 `"claude-code"` 고정, `cwd`는 `latest_cwd` 또는 `"/work"` (`:4005-4013`) | `POST /api/sessions` (`api/mod.rs:86`) |
| 새 팀원 결과 | 토스트 "{역할} 팀원을 만들지 못했습니다..." 가 아닌 "팀원을 만들지 못했습니다: {e}" (`:4028`), 성공 시 `open_conversation(&rec.id)` `:4026` | | | |
| 칸(멀티) 확대/닫기/이동 | "왼쪽으로 이동", "오른쪽으로 이동", "이동할 수 있는 위치가 없습니다", "대화"/"터미널" (`:1568-1576`, `ui/session.rs:915`) | `Pane` `:1392`, 닫기 `:1547`, 이동 `:1590-1594`, 확대 `:1529` | `edit_panes` (prefs) | 없음 |
| 칸 탭 추가/칸 추가 | "팀원 추가", "이전", "다음", "칸 머리를 끌어 옮길 수 있습니다. 가운데에 놓으면 바꾸고, 가장자리에 놓으면 나눕니다" (`:1807-1871`) | `:1799`, `:2015` | `edit_panes` | 없음 |
| 칸의 대화 입력/전송/중단 | 힌트 "메시지"/"대기열에 넣기", 알약 "{n}개 대기 중입니다" (`:1266-1292`) | `PaneComposer` `:1223`, `send` `:1235-1250` | outbox (B의 전송 행과 동일), `interrupt` `:1306` | `POST .../messages`, `POST .../interrupt` |
| 칸의 터미널 | `tp::CONNECTING` 등 (`ui/term_pane.rs`) | `PaneTerminal` `:1105`, 컴퓨터 조회 `:1119-1120`, 연결 `:1134` | `services().server.session_computer` -> `start_view(&server, id, project, None)` (`terminal_stream.rs:862`) | `GET /api/sessions/{id}/computer` + 터미널 스트림 [확인 필요: `terminal_stream.rs`의 소켓 경로, 범위 밖] |
| 싱글 뷰: 대화 + 정보 패널 | "세션 정보", 카드 "환경", "컨텍스트", "결과물", "변경 사항" (`:2488`, `ui/session.rs:956-959`) | `SingleView` `:2371`, `InfoPanel` `:2035` | `server.session_computer` `:2053-2056` (컴퓨터 이름 표시) | `GET /api/sessions/{id}/computer` |
| 상단 IDE 열기 (분할 버튼) | "IDE 열기" (`:630`, 대상 없으면 비활성 `:4768`), 선택 시트 `IdeChoice` 라벨 | `IdeMenu` `:524`, 조회 `:541-562`, 기본 클릭 `:597`, `:619`, 선택 `:673` | `services().server.ide_targets(&sid, None)` `:556-558`, 선택 후 `launch_ide_shared` `:171` | `GET /api/sessions/{id}/ide` (`api/ide.rs:483`) |
| 버전 관리 | "버전 관리" (`:4738`) | `vcs_open.set` `:4742`, `vcs::VcsSheet` `:4902` | `vcs.rs` (범위 밖) | `POST /api/projects/{name}/git/{*op}` 등 [확인 필요: vcs.rs] |
| 웹 페이지 | "웹 페이지" (`:4746`), 오류 "세션이 없습니다" (`:92`, `:4468`), "포트 목록을 불러오지 못했습니다: {e}" (`ui/session.rs:260`) | `open_web_menu` `:4460-4487`, 선택 `:4915-4921` | `server.session_computer` `:4477`, `client.api().computer_ports(&id)` `:4479` | `GET /api/sessions/{id}/computer`, `GET /api/computers/{id}/ports` (`computers/ports.rs:25`) |
| 웹 페이지 열기 실패 | "브라우저를 열지 못했습니다" (`:4919`) | `open_external` | | |
| 상태 뷰 | KPI "팀원", "실행 중", "승인 대기", "실패", "오늘 토큰", "성공률"; 칸반 열 "대기", "실행", "승인 대기", "검토", "완료"; "칸반" (`:3648-3752`, `ui/session.rs:591-595`) | `StatusView` `:3622` | 오늘 토큰: `bridge::request_project_day` `:3681` -> `Api::usage_summary(Day(today), Some(project))` (`bridge.rs:421-422`) | `GET /api/usage/summary?day=&project=` (`api/mod.rs:91`) |
| 상태 카드 | 카드 "PR과 CI", "서브 에이전트 스레드", "부하", 컴퓨터 부하 | `StatusCardsGrid` `:3583`, `computer_rows` | `services().client.read(computers)` `:3805` (캐시) | 없음 |
| 타임라인 | "에이전트 간 통신", 알약 "생각", "도구 호출", "대기", "핸드오프", "실패"; 토스트 "타임라인 재생 데모입니다", "처음으로 되돌렸습니다" (`:93`, `:3145`, `:3155`, `:3232-3301`) | `TimelineCard` `:2882` | `timeline_summary(demo)` `:2956`. 비데모 데이터 [확인 필요] | 없음 |

### 사용자에게 보이는 에러 메시지 (주요)

| 원문 | 위치 | 조건 |
|---|---|---|
| "이미 있는 이름입니다" | `ember/app/src/ui/project.rs:738`, `:835` | 프로젝트 이름 충돌 (409 `name_taken`) |
| "기본 프로젝트의 이름은 바꿀 수 없습니다" | `ui/project.rs:739` | 403 `protected_project` |
| "입력한 값을 서버가 받아들이지 않았습니다. 내용을 확인하십시오." / "선택한 계정을 쓸 수 없습니다. 다시 고르십시오." / "입력한 값이 올바르지 않습니다" / "프로젝트를 찾지 못했습니다" / "설정을 저장하지 못했습니다. 잠시 뒤에 다시 시도해 주세요" | `ui/project.rs:740-744` | 설정 저장 실패 (`save_settings` `project.rs:1409`) |
| "프로젝트를 만들지 못했습니다. 잠시 뒤에 다시 시도해 주세요" | `ui/project.rs:837` | 생성 실패 |
| "전송하지 못했습니다: {e}" | `conversation.rs:801` | outbox 전송 실패 |
| "응답하지 못했습니다: {e}" | `conversation.rs:1671` | 승인 응답 실패 |
| "중단하지 못했습니다: {e}" | `conversation.rs:984`, `1055`, `session.rs:1312` | interrupt 실패 |
| "팀원을 만들지 못했습니다: {e}" | `session.rs:4028` | 새 팀원 생성 실패 |
| "세션을 업데이트하지 못했습니다: {e}" | `launcher.rs:232` | 고정 등 (도달 불가 경로) |

## 데이터와 설정

- DB 테이블: 없음. 기기별 설정 파일(`ui.prefs`: `session_view`, `last_project`, `panes`, `ide_target`, 프로젝트별 캐릭터 스타일)은 `SharedUi::update_prefs`로 쓴다 (`ember/app/src/ui/coexist.rs`; 저장 위치는 [확인 필요: coexist.rs/prefs 구현]).
- 환경 변수 (디버그/캡처 훅, 운영에 영향 없음 [추정]):

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_CR_PROJECT`, `EMBER_CR_ROUTE=project-detail` | `project.rs:187-191` | 상세 화면으로 시작 | 없음 |
| `EMBER_CR_PROJECT_SHEET` (`settings`/`computer`/`new`/`add-computer`) | `:193` | 시트를 열고 시작 | 없음 |
| `EMBER_CR_PROJECT_EXPAND=1`, `EMBER_CR_PROJECT_SEARCH=open` | `:194-199`, `:181` | 덱 펼침, 검색 열림 (검색은 디버그 빌드만) | 꺼짐 |
| `EMBER_CR_IDE_MENU=1` | `project.rs:889`, 기타 | IDE 시트 열고 시작 | 꺼짐 |
| `EMBER_CR_QUESTION`, `EMBER_CR_QUESTION_FIRST` | `conversation.rs:424-443` | 샘플 질문 주입 (디버그만) | 없음 |
| `EMBER_CR_SESSION_VIEW`, `_PROJECT`, `_DRAWER`, `_NEW_MEMBER`, `_VCS`, `_WEB`, `_INFO` | `session.rs:4360-4400`, `2376` | 세션 화면 캡처 훅 | 없음 |

- 외부 연동: 서버 REST와 push는 위 표 참조. OS 열기 (`open_external`), 터미널 스트림 (`terminal_stream`).

## 이 모듈을 수정할 때 주의할 점

- `ConversationView`는 `embedded` 플래그로 두 갈래이다. 대화 화면의 기능(고정, 내보내기, 포크 메뉴, 컴퓨터 전환)을 라이브에 살리려면 `session.rs`의 `SingleView`에 같은 진입점을 만들어야 한다. 지금 `embedded = false`는 테스트 전용이다.
- 전송 경로는 세 곳에 복제되어 있다: `conversation.rs:316-337`, `session.rs:1235-1250` (`PaneComposer`), `home.rs:1242`(범위 밖). 큐/실패 표시는 `conversation.rs`에만 있고 `PaneComposer`는 개수 알약만 있다 (실패 배너 없음).
- 중단(interrupt) 핸들러도 3곳에 복제: `conversation.rs:966`, `:1040`, `session.rs:1297`. `PaneComposer`만 `demo_blocked_cr()` 검사를 하지 않는다 (`session.rs:1297-1315` 대비 `conversation.rs:967-969`).
- `conversation.rs`와 `session.rs`가 서로 import한다 (`conversation.rs:671`, `session.rs:57`). 이동 시 함께 고쳐야 한다.
- `crate::ui::session`의 순수 함수 이름과 `session.rs`의 `pub use` 목록(`:29-40`)을 함께 바꿔야 한다. `crate::ui::project`의 `SOON`, `NOT_YET`, 오류 문구도 마찬가지다.
- 응답 문구에 서버 본문을 쓰지 않는 규칙(`services.rs:140-143`)이 질문 답변에 있다. 다른 호출은 `e.to_string()`을 그대로 토스트에 넣는다.
- 테스트는 소스 문자열을 `contains`로 검사하는 것이 있다 (`session.rs:4983-4984`). 코드 형태를 바꾸면 깨진다.
- 빌드, 테스트는 실행하지 않았다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 죽은 경로 | 높음 | `conversation.rs:567-692`, `1073-1199`, `session.rs:2467` | 라이브에서 대화 화면은 `embedded = true`뿐이라 고정, 내보내기, 마지막 턴에서 포크, 컴퓨터 전환, 대화 화면의 IDE 줄이 도달 불가 | 싱글 뷰 헤더에 같은 메뉴를 연결하거나 코드를 제거 |
| 기능 미구현 | 높음 | `session.rs:3952-4034` | 새 팀원 시트의 "첫 지시", "컴퓨터" 선택, 하네스/모델/모드 칩이 요청에 반영되지 않는다. `agent`는 `"claude-code"` 고정, 컴퓨터 목록은 `["mac-mini","mac-studio","이 컴퓨터"]` 하드코딩 (`:3975`) | 서버의 에이전트와 컴퓨터 목록으로 채우고 필드를 `CreateSession`에 전달 |
| 하드코딩 | 중간 | `session.rs:4009-4013` | 새 팀원의 `cwd` 기본값 `"/work"` | 프로젝트 설정의 작업 경로 사용 |
| 하드코딩 | 중간 | `session.rs:284`, `:2093` | 모델 칩에 " · 높음" 고정 접미사, 정보 패널 컴퓨터 이름이 모르면 `"mac-mini"` | 실제 값 사용, 없으면 빈 표시 |
| 기능 미구현 | 중간 | `session.rs:324-333` | 모델 선택 불가 ("준비 중입니다") | SPEC FR-L15 상태 확인 [확인 필요] |
| 기능 미구현 | 중간 | `project.rs:374-378` | 비데모에서 "새 프로젝트" 비활성 (`can_create = demo`), 서버 생성 코드(`:1340`)는 데모가 아닐 때 도달 불가 | 활성 조건 재검토 |
| 기능 미구현 | 중간 | `project.rs:1627-1628`, `1592` | 보관/삭제/리더가 빈 핸들러 (TODO #384) | 서버 지원 후 연결 |
| 중복 | 중간 | `conversation.rs:316`, `session.rs:1235` | 전송, 중단 로직 복제 | 공용 함수로 추출 |
| 일관성 | 낮음 | `session.rs:1297` | `PaneComposer` interrupt는 데모 차단 검사 없음, 전송 실패 배너 없음 | `conversation.rs`와 맞춤 |
| 사용량 | 낮음 | `session.rs:3680-3683` | 세션 사용량(`GET /api/sessions/{id}/usage`) 호출 없음, 정보 패널의 "컨텍스트" 등은 데모 전용 (`:2117-2123`) | 실데이터 연결 시 추가 |
| 데모 상수 | 낮음 | `session.rs:2671-2737` | 타임라인 레인이 데모 상수 (`DEMO_TL_LANES`) | 비데모 데이터 확인 [확인 필요] |
| TODO | 낮음 | `project.rs` (29줄), `session.rs` (10줄), `conversation.rs` (0줄) | 대부분 `TODO(compose-rust#NNN)` 접근성 이름, 토글, 점선 테두리 | 툴킷 지원 시 처리 |
| 거대 파일 | 중간 | `session.rs` 5,180줄 | 3개 뷰, 시트, 타임라인, 상태 카드가 한 파일. `ConversationView`도 1,000줄짜리 함수 하나 (`conversation.rs:155-1200`) | 뷰별 파일 분리 |
| 순환 의존 | 낮음 | `conversation.rs:671`, `session.rs:57` | 두 파일이 서로 import | 공용 부품(칩, 버튼)을 `components`로 이동 |
| 보안 | 낮음 | `conversation.rs:1342`, `session.rs:4478` | 비밀값 노출 없음. 질문 비밀 입력은 앱에서 받지 않도록 막혀 있다 (`question.rs:20`) | 해당 없음 |
