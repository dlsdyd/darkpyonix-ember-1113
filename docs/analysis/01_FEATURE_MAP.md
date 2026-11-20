# 기능 지도

- 기준 커밋: `ffe9825` / 작성: 2026-11-13
- 근거: 각 화면 모듈 문서의 "동작 지도" 절을 화면 순서로 모았다. 원문과 상세는 [modules/app-ui-cr.md](modules/app-ui-cr.md), [modules/app-ui-cr-session.md](modules/app-ui-cr-session.md), [modules/app-ui-cr-work.md](modules/app-ui-cr-work.md).

## 사용법

1. 사용자 피드백에 나온 화면 이름, 버튼 문구, 에러 메시지를 이 문서에서 Ctrl+F로 찾는다. 화면 문구는 코드의 원문 그대로다.
2. 찾은 행의 "핸들러"에서 시작해 오른쪽(호출 API, 서버 라우트)으로 따라간다.
3. 서버 쪽은 라우트 이름으로 [_raw/routes.md](_raw/routes.md)에서 핸들러 위치를 찾고, 그 모듈 문서([modules/server-api.md](modules/server-api.md) 등)로 간다. 클라이언트 함수와 라우트의 대응은 [modules/client.md](modules/client.md)의 "`Api` 메서드 → HTTP 라우트 표".
4. 고칠 때 주의할 점은 [06_FIX_GUIDE.md](06_FIX_GUIDE.md).

**경로 표기:** 이 문서의 표에서 디렉터리 없이 쓴 `shell.rs:642` 같은 경로는 `ember/app/src/ui/cr/` 기준이다. `ui/shell.rs`처럼 `ui/`로 시작하는 것은 `ember/app/src/ui/`(Dioxus 원본, 로직은 지금도 쓰인다) 기준이다. 그 밖의 경로는 저장소 루트 기준이다.

**먼저 알아야 할 것:** 앱의 기본 화면은 compose-rust로 그린 `ember/app/src/ui/cr/`다 (`ember/app/src/lib.rs:143-145`). `ember/app/src/ui/`의 같은 이름 파일은 옮겨 오기 전 Dioxus 원본이지만, 거기 있는 상태 모델과 함수 대부분을 `cr/` 화면이 그대로 쓴다 ([modules/app-ui.md](modules/app-ui.md)). 화면은 `cr/`에서, 로직은 `ui/`에서 찾는 경우가 많다.

## 화면 목록

| 화면 | 들어가는 방법 | 화면 함수 | 이 문서의 절 |
|---|---|---|---|
| 셸 (사이드바, 레일, 하단 탭) | 항상 | `shell.rs` `launch` | [셸](#화면-셸-사이드바-레일-하단-탭) |
| 홈 | 메뉴 "홈" | `home::HomeScreen` (`home.rs:504`) | [홈](#화면-홈) |
| 프로젝트 | 메뉴 "프로젝트" | `project::ProjectScreen` (`shell.rs:649`) | [프로젝트](#화면-프로젝트) |
| 검색 | 사이드바 "검색" (`Route::Search`) | `search::SearchScreen` (`search.rs:64`) | [검색](#화면-검색) |
| 세션 (대화 포함) | 메뉴 "세션", 세션 행 클릭 | `session::SessionScreen` (`shell.rs:661`) | [세션](#화면-세션) |
| 채널 | 메뉴 "채널" | `channels::ChannelsScreen` (`channels.rs:209`) | [채널](#화면-채널) |
| 루틴 | 메뉴 "루틴" | `routines::RoutinesScreen` (`shell.rs:659`) | [루틴](#화면-루틴) |
| 버전 관리 | 메뉴 "버전 관리" | `vcs::VcsScreen` (`shell.rs:655`) | [버전 관리](#화면-버전-관리) |
| 에이전트 | 메뉴 "에이전트" | `agents::AgentsScreen` (`shell.rs:657`) | [에이전트](#화면-에이전트) |
| 파일 | 메뉴 "파일" | `files::FilesScreen` (`shell.rs:651`) | [파일](#화면-파일) |
| 캐릭터 | `ui.characters`가 설정되면 어떤 메뉴보다 먼저 | `characters_screen::CharactersScreen` (`characters_screen.rs:140`) | [modules/app-ui-cr.md](modules/app-ui-cr.md) |
| 설정 (시트) | 셸의 설정 | `settings.rs` (`shell.rs:738`) | [설정](#화면-설정-시트) |
| 별도 IDE 창 | `ember-app --editor <project> <folder>` | `ui::editor_workbench::page::app` (Dioxus HTML 모드, `ember/app/src/lib.rs:117-136`) | [IDE 창](#화면-별도-ide-창) |
| VS Code Web (브라우저) | 앱의 "IDE 열기"가 OS 브라우저로 연다 | `ember/proxy/main.py` | [VS Code Web](#화면-vs-code-web-proxy) |

## 셸: 메뉴와 창 크기가 화면이 되는 경로


#### 1.1 메뉴 -> 화면 함수

결정은 `ember/app/src/ui/shell.rs`의 순수 함수이고, 그리는 쪽은 `cr/shell.rs:638-672`의 `if / else if` 사슬이다 (`cr/shell.rs:30-35`가 그 함수들을 re-export).

- 활성 메뉴: `active_menu(&route, 선택한 메뉴)` (`ember/app/src/ui/shell.rs:83`): `Route::Conversation`이면 항상 `Sessions`, 아니면 선택한 메뉴.
- 화면 선택: `screen_for(&route, active)` (`ember/app/src/ui/shell.rs:114-127`).
- 사슬 순서는 `cr/shell.rs:642`부터: `ui.characters`가 `Some`이면 (메뉴와 무관하게) 캐릭터 화면이 이긴다.

| NavMenu (라벨) | `Screen` (`ui/shell.rs`) | `cr/` 화면 함수 (`cr/shell.rs` 줄) | 구현 파일 |
|---|---|---|---|
| (어느 메뉴든 `ui.characters`가 `Some`) | - | `characters_screen::CharactersScreen()` (`:643`) | `characters_screen.rs:140` |
| `Projects` (프로젝트) + `Route::Search` | `Screen::Search` (`ui/shell.rs:120`) | `search::SearchScreen()` (`:645`) | `search.rs:64` |
| `Projects` (프로젝트) 그 외 | `Screen::Launcher` (`:121`) | `project::ProjectScreen()` (`:649`) | 제외 파일 `project.rs` |
| `Home` (홈) | `Screen::Home` | `home::HomeScreen()` (`:653`) | `home.rs:504` |
| `Sessions` (세션) + 열린 대화 | `Screen::Conversation(id)` (`:119`) | `session::SessionScreen(Some(id))` (`:661`) | 제외 파일 `session.rs` |
| `Sessions` (세션) 열린 대화 없음 | `Screen::Placeholder(Sessions)` | `session::SessionScreen(None)` (`:663`) | 제외 파일 `session.rs` |
| `Channels` (채널) | `Screen::Channels` | `channels::ChannelsScreen()` (`:647`) | `channels.rs:209` |
| `Routines` (루틴) | `Screen::Routines` | `routines::RoutinesScreen()` (`:659`) | 제외 파일 |
| `VersionControl` (버전 관리) | `Screen::VersionControl` | `vcs::VcsScreen()` (`:655`) | 제외 파일 |
| `Agents` (에이전트) | `Screen::Agents` | `agents::AgentsScreen()` (`:657`) | 제외 파일 |
| `Files` (파일) | `Screen::Files` | `files::FilesScreen()` (`:651`) | 제외 파일 |
| 위에 없는 `Screen::Placeholder` | - | `shell::Placeholder(menu)` (`:670`, 정의 `:575`): 메뉴 라벨과 "준비 중입니다" | `shell.rs:575-583` |

메뉴 라벨과 순서(`NavMenu::ALL`, `ember/app/src/ui/shell.rs:30-39`): 홈, 프로젝트, 세션, 채널, 루틴, 버전 관리, 에이전트, 파일. 아이콘은 `ember/app/assets/nav/*.svg`(`ui/shell.rs:58-67`).

- `choose()` (`cr/shell.rs:69-89`)의 부수효과: 프로젝트 선택=`ui.go(Route::Projects)`; 세션 선택=열린 대화가 없을 때만 `model::recent_sessions(..., 1)`의 첫 행을 `open_conversation`(최근 세션이 없으면 `Placeholder` 화면); 그 밖의 메뉴는 대화 중이었다면 `Route::Projects`로 돌린 뒤; 항상 `detail_open=false`, `ui.set_menu(menu)`. 홈으로 들어오면 `set_menu`가 `bridge::request_github_summary()`를 호출한다 (`ember/app/src/ui/coexist.rs:224-232`).
- 검색은 메뉴가 아니다: 사이드바, 레일, 더보기, 폰 메뉴의 "검색"이 `ui.go(Route::Search)`를 부르고 `go()`가 메뉴를 `Projects`로 맞춘다 (`coexist.rs:190-217`). 단 `Route::Search`인 채로 다른 메뉴를 고르면 `choose`가 `Route::Projects`로 돌리지 않는다(대화일 때만 돌림). 그래서 `screen_for(Home, Search)`는 홈을 그린다. 이는 의도한 동작으로 보이나 `[확인 필요]`.
- 설정은 화면이 아니라 시트다 (`shell.rs:738`). 새 세션 다이얼로그도 항상 마운트된다 (`:739`).

#### 1.2 창 크기 -> 레이아웃

`current_mode(collapsed)` (`cr/shell.rs:593`)가 `nav_mode(width_dp, collapsed)` (`ember/app/src/ui/shell.rs:205-213`)를 부른다. 창 폭은 `compose_rust::runtime::current_window_size()`로 읽어 recomposition에 걸린다 (`:593`의 주석).

| 폭 (dp) | `ShellMode` | 그리는 곳 | 비고 |
|---|---|---|---|
| `<= 560` (`BAR_MAX_DP`, `ui/shell.rs:201`) | `BottomTabs` | `shell.rs:677-693`: 내용 열 + `BottomBar` (`:412`) + 폰 메뉴 `PhoneMenu` (`:481`) | 탭 5개: 홈, 프로젝트, 세션, 채널, 더보기 (`BOTTOM_TABS`, `ui/shell.rs:142`). 더보기 시트(`:710`)는 `MORE_MENUS`: 루틴, 버전 관리, 에이전트, 파일 (`ui/shell.rs:151`). 대화방이 열려 있으면(`ui.detail_open`) 폰 메뉴를 숨긴다 (`shell.rs:691`) |
| `561..=1279` (`RAIL_MAX_DP`, `ui/shell.rs:199`) | `Rail` | `shell.rs:694-709`: `Sidebar(rail=true)` 72dp (`RAIL_W`, `theme.rs:300`) + 내용 | 접기 토글은 이 구간에서 무효 (`toggled_collapse`, `ui/shell.rs:218`) |
| `> 1279` | `Sidebar` (접으면 `Rail`) | 같은 분기, `Sidebar(rail=false)` 234dp (`SIDE_W`, `theme.rs:299`) | 브랜드 줄의 접기 버튼이 `collapsed`를 토글 |
- 화면 안쪽 크기 분기는 각 화면이 `current_window_size()`로 따로 한다: 채널 분할(`split_view(window.class)`, `channels.rs:236`), 홈 `layout(width_dp)` (`home.rs:156`), 시트 표현(<560 바텀시트, 그 외 다이얼로그, 모니터는 <=560 전체 화면; `components.rs:760-770`).
- Windows는 내용 열 위에 32dp 캡션 띠 + 138dp 오른쪽 예약을 그린다 (`shell.rs:629-637`, `WINDOWS_CAPTION_HEIGHT_DP`). macOS 하단탭 모드는 신호등 아래 띠(`strip`, `:612`, `:638-640`). 둘 다 `TODO(#213, #204)` (`shell.rs:11-14`).

#### 1.3 검토용 실행 경로

`launch`는 `EMBER_CR_ROUTE` 값으로 화면 하나를 바로 연다 (`shell.rs:785-837`): `search`, `new-session`, `launcher-row`(`launcher::rows_preview`), `monitor`(`monitor::preview`), `channels`, `project`/`project-detail`, `files`, `vcs`, `agents`, `routines`, `home`, `session(s)`, `characters`, `conversation`(대화 `demo-s1`). `EMBER_CR_SIZE=WxH` (기본 1440x900, `:756-766`), `EMBER_CR_SHELL=light|dark|1` (`:747-754`).


## 화면: 셸 (사이드바, 레일, 하단 탭)


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 사이드바, 레일 메뉴 클릭 | 홈, 프로젝트, 세션, 채널, 루틴, 버전 관리, 에이전트, 파일 | `choose` `shell.rs:69` (`NavRow` `:161`, `RailItem` `:196`) | 없음(상태). 세션은 `ui.open_conversation` -> `s.open_session` |
| 하단 탭 클릭 | 홈 / 프로젝트 / 세션 / 채널 / 더보기 | `shell.rs:684-688` | 같음. 더보기는 시트 열기 |
| 더보기 시트 | "더보기", 메뉴 4개, "테마: {시스템|라이트|다크}", "검색", "설정" | `shell.rs:710-735` | 없음 |
| 테마 행 클릭 | "테마: 라이트" 등 | `ui.set_theme_pref(pref.next())` `shell.rs:378-380`, `:722` | 환경설정 저장(`prefs`) |
| 검색 행 클릭 | "검색" | `ui.go(Route::Search)` `:382`, `:523`, `:726` | 없음 |
| 설정 행 클릭 | "설정" | `on_settings` -> `settings_open.set(true)` `:383`, `:701` | 없음 |
| 폰 메뉴 단추(우상단 32dp) | "테마 전환", "검색", "설정" | `PhoneMenu` `:481-555` | 없음 |
| 데모일 때만: 사이드바 | "플랫폼: iOS|기타", "데모 초기화" | `shell.rs:384-395` | `services.reset_demo()` -> 토스트 "데모를 초기 상태로 되돌렸습니다" |
| 접기 버튼 | (브랜드 줄) | `toggled_collapse(...)` `shell.rs:702-705` | 없음 |
| 내용 없음 | "준비 중입니다" | `Placeholder` `:575` | 없음 |


## 화면: 홈

- 진입 시: 홈 메뉴로 들어오면 `set_menu`가 `bridge::request_github_summary()`를 부른다 (`ember/app/src/ui/coexist.rs:224-232`).


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 화면 진입 | "{BREW}, 무엇을 도와줄까요?"(`GREETING` + `DEMO_USER.0`, `home.rs:1073-1074`), 입력창 placeholder "무엇이든 물어보세요. 새 대화는 고른 프로젝트의 팀원이 됩니다.", 안내 "오늘의 팀" | `HomeScreen` `:504`, `remember(...)` `:511-514` | `bridge::request_github_summary()` -> `client.api().github_summary()` (`GET /api/integrations/github`, `ember/app/src/bridge.rs:294-319`) |
| 제안 칩 클릭 | "develop CI 실패 요약해줘", "열린 PR 리뷰해줘", "이번 주 사용량 정리해줘" (`ui/home.rs:1137-1141`) | `Suggestions` `home.rs:1382-1390`: 칩 문구를 `suggestion`으로 설정 | 없음 |
| 칩: 프로젝트/모델/권한 모드/컴퓨터 | (선택된 값) 모델 시트 "모델 선택", 검색 "모델 검색", 없음 "일치하는 모델이 없습니다"; 컴퓨터 목록 첫 항목 로컬 이름(없으면 "이 서버") | `Composer::lists` `:704`, `model_sheet` `:816`, `mode_popover` `:779`, `tap_mode` `:767` | 없음 (목록은 `client.read` 상태) |
| "+"로 첨부 | "파일의 절대 경로", 버튼 "첨부", 안내 "파일 경로가 메시지에 포함됩니다. 파일 내용은 전송되지 않습니다", 제안 선택 시 "제안을 고르셨습니다. 입력하지 않으면 이 내용으로 시작합니다", "취소" | `add_attachment` `:605-615` (`stage_attachment`) | 없음 (경로 검사 `is_file`) |
| 보내기 원형 단추 / Enter | (없음) | `Composer::send` `:617-702` | `services().create_session` (`POST /sessions`, `ember/app/src/services.rs:161`); 컴퓨터를 골랐고 데모가 아니면 `server.switch_computer` (`PUT /sessions/{id}/computer`, `ember/app/src/server.rs:444-448`); 권한 모드가 바이패스면 `set_approve_all` (`ember/app/src/services.rs:180`); 성공 시 outbox에 첫 메시지를 넣고 `open_conversation`, `drive_outbox` |
| (보내기 실패, 안내) | 아래 에러 표 | `:634-637`, `:667`, `:672`, `:697` | - |
| 대시보드 | "오늘의 팀" + "{M월 D일 요일} · 서버 기준"; 카드 "비용과 토큰 추이", "팀원 상태"(실행, 승인 대기, 새 결과, 완료, "실패 N"), "하네스별 사용량"(버튼 "자세히"), "지금 일하는 팀원", "작업 성공률"("집계 전", "성공", "실패", "CI 결과는 GitHub 연동에서 옵니다"), "프로젝트"(버튼 "모두 보기"); 데이터 없는 타일 "팀원별 효율", "승인 대기 시간", "컴퓨터 부하" + "준비 중입니다" | `Dashboard` `:1401`, `StatusTile` `:1707`, `HarnessTile` `:1839`, `SuccessTile` `:1967`, `ProjectsTile` `:2017` | `services().client.read(ui::home::read_dash)` (로컬 상태), "자세히" -> `shell::choose(Agents)` `:1879`, "모두 보기" -> `set_selected_project(None)` + `choose(Projects)` `:2024-2027`, 프로젝트 타일 -> `set_selected_project` + `choose(Projects)` |
| 연동 영역 | 제목 "연동"; GitHub 카드(상태 pill, 액션 버튼은 로그인 방법 안내만 표시, "PR {n} · 리뷰 {m}", 활동 없음 "연동이 만든 일이 아직 없습니다", 정보 없음 "아직 정보가 없습니다", 데모 "(예시)"); Slack, Discord, Linear, 캘린더, 메일은 "준비 중입니다" + "12월 이후에 지원합니다" | `IntegrationsArea` `:1459-1545` | `live.github` 상태 (위 GitHub 요청 결과). 버튼은 안내 문구만 토글, 토큰 저장 없음 `:1496-1500` |


## 화면: 프로젝트


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


### 프로젝트 화면의 시트들


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 컴퓨터 추가 | 시트 "컴퓨터 추가"; "새 컴퓨터 추가", "컴퓨터 이름", "예: 연구실 컴퓨터", "코드 만들기"/"만드는 중", "기기를 불러오는 중입니다", "예시"; 대기 "다른 컴퓨터에서 아래 명령을 실행하면 이 화면에 요청이 표시됩니다", "코드는 한 번만 표시되며 한 번 쓰면 무효가 됩니다" (전체 문구는 `ember/app/src/ui/enrol_flow.rs:22-81`) | `mint` `add_computer.rs:242`, `fetch_status` `:278`, `apply_poll` `:289` | `hub_devices()`, `enrol_mint(name)` (`POST /computers/enrol-codes`), `enrol_status(id)` (`GET /computers/enrol-codes/{id}`) 폴링 |
| 확인 카드 | "이 기기를 컴퓨터로 추가합니다. 추가한 컴퓨터는 서버 사용자와 같은 권한으로 쓰입니다", "기기가 보고한 이름", "관측 주소", "시스템", 버튼 "확인하고 추가"/"추가하는 중", "거부" | `confirm` `:315`, `deny` `:355` | `enrol_confirm(id, name, fingerprint)` (`POST .../confirm`), `enrol_deny` (`POST .../deny`); 시트 닫을 때 `enrol_cancel` (`DELETE`) `:223` |
| 결과 | "컴퓨터가 추가되었습니다" + "이제 프로젝트의 컴퓨터 목록에서 고를 수 있습니다", "새 코드 만들기", 토스트 "컴퓨터를 추가했습니다" | `Outcome` `:651` | `refresh_computers` `:303` |
| 컴퓨터 모니터 | 제목 컴퓨터 이름 또는 "컴퓨터"; 카드 "상태", 프로세스 표 "이름 (N)"/"메모리"/"전력", 오프라인 "마지막 연결 시각은 아직 알 수 없습니다. 아래는 마지막으로 받은 값입니다.", 실패 "지표를 읽지 못했습니다", "컴퓨터를 찾을 수 없습니다", "할당된 프로젝트가 없습니다", "이 컴퓨터에서 실행 중인 팀원이 없습니다", "(리더)" | `MonitorSheet` `monitor.rs:89`, 정렬 헤더 클릭 `ProcessTable` `:404` | `client.api().metrics(id, TOP_PROCESSES)` (`GET /computers/{id}/metrics?top=`) 를 `POLL_SECS`마다 |
| 팀 캐릭터 화면 | "팀 캐릭터", "뒤로", "팀 미리보기", "미리보기" 뱃지, "이 프로젝트에 적용"/"저장 중", "편집기", 필드 "이름", "하네스", "역할", "스타일", "실루엣 고정", "상태" | `CharactersScreen` `characters_screen.rs:140`, `apply_style` `:31` | `client.patch_project(project, {character_style})` (`PATCH /projects/{name}`), 성공 후 `prefs.set_character_style` |


## 화면: 검색


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 검색창 입력 | 제목 "전체 검색", placeholder "세션 검색", 안내 "모든 대화의 메시지와 제목, 프로젝트, 에이전트, 계정, 폴더를 검색합니다.", "검색 중...", "결과 {N}건", "일치하는 항목이 없습니다.", 구역 "프로젝트" | `on_change` `search.rs:73-122` (250ms 디바운스, 낡은 응답 폐기 `superseded`) | `client.search(q, Some(100))` (`GET /search?q=&limit=100`); 데모는 호출 대신 한 번 "사용 불가" 안내 (`demo_blocked`) |
| 결과 행 클릭 | 세션 행 | `SessionRowView` `launcher.rs:91` -> `open_conversation` `:25` | 없음 |
| 검색 실패 | "메시지 검색에 실패했습니다: {e}. 제목 일치만 보여줍니다." `:165` | - | - |


## 화면: 세션

세션 화면은 세션 목록과 대화를 한 화면에 그린다. 대화 부분은 `conversation.rs`의 `ConversationView`를 `embedded = true`로만 부른다 (`session.rs:2467`). 그래서 `embedded = false`일 때만 보이는 대화 화면의 동작(고정, 내보내기, "마지막 턴에서 포크", 컴퓨터 전환 줄, "IDE 열기" 줄)은 지금 앱에서 닿을 수 없다 ([05_ISSUES.md](05_ISSUES.md)).

### 세션 목록과 새 세션


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 행 메뉴 | "고정"/"고정 해제", "이름 변경", "보관"/"보관 해제", "내보내기"; 뱃지 "고정됨"; 계정 없으면 "서버 로그인" | `SessionRowWith` `launcher.rs:96-` (`:149`, `:64-72`) | `patch_session` -> `services.patch_session` (`PATCH /sessions/{id}`) |
| 이름 변경 | 시트 "세션 이름 변경", 버튼 "취소"/"변경" | `rename` `:238` (빈 제목이면 아무 일 없음) | 같음 |
| 내보내기 | 토스트 "내보냈습니다: {경로}" | `export` `:246` | `crate::export::export_session` (로컬 파일 쓰기; 데모는 막힘) |
| 연결 배너 재시도 | "다시 시도" | `ConnectionBannerView` `:41-` | `ember_client` 재연결 `[확인 필요: 호출 대상은 launcher.rs:58 본문]` |
| 새 세션 열기 | 시트 "새 세션"; 필드 "프로젝트"(옵션 "새 프로젝트..." + 이름 입력 "프로젝트 이름"), "컴퓨터의 폴더", "모델 (선택)"(placeholder "에이전트 기본값"), "제목 (선택)"(placeholder "새 대화"), "에이전트", "계정"(옵션 "자동 (서버 라우터가 고름)", "(기본)", "한도 도달"), "컴퓨터"(옵션 "메인 서버 (기본)") | `NewSessionDialog` `:41`, `NewSessionForm` `:82`, 옵션은 `GET /agents`, `/accounts`, `/computers`(헤더 주석 `:1-3`) | `[확인 필요]` 옵션 로딩 호출 위치: 같은 파일 `:125-200` |
| "만들기" | 버튼 "취소"/"만들기" | `start` `new_session.rs:215-262` | `create_session`(`POST /sessions`) -> 필요 시 `server.switch_computer`(`PUT /sessions/{id}/computer`) -> `open_conversation`; `prefs.last_used[project]` 갱신 |


### 세션 화면


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


### 대화 영역


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


## 화면: 채널


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 화면 진입 | 로딩, 실패, 비어 있음 문구(`ui::channels::empty_text`), 제목 "채널", 검색 "채널, 메시지 검색", 필터 칩 기본 "전체" | `ChannelsScreen` `:209`, `Feed::refresh` `:101` | `client.api().channels(None)` (`GET /channels`) |
| 방 목록 로드 실패 | "채널을 불러오지 못했습니다. 잠시 뒤 다시 시도합니다." `:368`, "연결이 끊겼습니다" `:113` | `Load::Failed` | - |
| 방 선택 | 마지막 문구 "메시지가 없습니다"; 컴팩트는 "목록" 버튼으로 돌아감 | `RoomItem` `:417`, `follow` `:131` | `client.api().channel(id)` (`GET /channels/{id}`), 이후 2초마다 `channel_messages(id, after=seq)` (`GET /channels/{id}/messages?after=`), 열 때 `mark_channel_read` (`POST /channels/{id}/read`) `:163-178` |
| 메시지 입력 후 전송 | placeholder "메시지 입력", 버튼 "전송"/"전송 중", 말풍선 pill "에이전트", "게스트" | `InputBar` `:553`, `Feed::send` `:181` | `post_channel_message` (`POST /channels/{id}/messages`, 본문 `{text}`) |
| 방 헤더 멤버 단추 | 시트 "{방 이름} 멤버/게스트", 버튼 "닫기" | `MembersSheet` `channel_owner.rs:335` (열기 `channels.rs:467`, `:545`) | `guest_door()` (`GET /guest-door`), `invites`(`GET /channels/{id}/invites`), `guests`(`GET /channels/{id}/guests`) `channel_owner.rs:205-260` |
| 초대 만들기 | "초대 만들기", "링크는 한 번만 보이며, 한 사람이 한 번만 쓸 수 있습니다", 만든 뒤 "이 링크는 지금만 보입니다. 닫으면 다시 볼 수 없습니다", 주소 경고 "127.0.0.1 같은 내 컴퓨터 주소나 0.0.0.0 주소는 밖에서 닿지 않습니다", 시간 칩 "{N}시간" | `create_invite` `:286` | `create_invite(channel, Some(ttl))` (`POST /channels/{id}/invites`) |
| 초대 취소 | "취소" -> 확인 "정말 취소합니다" / "아니요"; 결과 "초대를 취소했습니다" | `revoke` `:300` | `revoke_invite` (`DELETE .../invites/{iid}`) |
| 게스트 허용 | "게스트", "허용 시간 (이 시간 동안 게스트의 멘션이 에이전트에 닿습니다)", "직접 입력 ({MIN_HOURS}~{MAX_HOURS}시간)", "선택한 허용 시간: N시간", 버튼 "{N}시간 허용"; 결과 "허용했습니다" | `allow` `:314` | `set_allowance` (`PUT .../guests/{gid}/allow`) |
| 허용 해제 / 게스트 제거 | "허용 해제" -> "허용을 해제했습니다"; "제거" -> "정말 제거합니다" -> "게스트를 제거했습니다" | `clear` `:325`, `remove` `:307` | `clear_allowance`, `remove_guest` (`DELETE`) |
| 새 채널 "+" | 시트 "새 채널"; 필드 "이름"("채널 이름"), "프로젝트", "멤버 (에이전트)", 빈 상태 "프로젝트가 없습니다", "이 프로젝트에는 에이전트 세션이 없습니다"; 버튼 "취소", "만들기"/"만드는 중"; 변경 확인 시트 "변경 사항" + "계속 편집"/"닫기" | `NewChannelButton` `new_channel.rs:130`, `create` `:163` | `create_channel` (`POST /channels`), 이어서 `channels(None)`로 재조회 |


## 화면: 루틴


| 사용자 동작 | 화면 문구 | 핸들러 | 호출 API (client) | 서버 라우트 |
|---|---|---|---|---|
| 화면 열기, 새로고침 | 제목 "루틴", "팀원이 일정이나 이벤트에 맞춰 스스로 하는 일" `routines.rs:1076-1077` | `refresh` `routines.rs:233` (`launched_effect` 438) | `Api::schedules`, `schedule_runs(id, 20)` `routines.rs:203-209` (`ember/client/src/api.rs:1300,1336`) | `GET /api/schedules`, `GET /api/schedules/{id}/runs` (`ember/server/src/schedules/api.rs:52,57`) |
| 켜기/끄기 스위치 | "{이름} 루틴 켜기/끄기" `routines.rs:1111-1113` | `on_toggle` `routines.rs:574` | `resume_schedule` / `pause_schedule` `routines.rs:586-588` (`api.rs:1326,1322`) | `POST /api/schedules/{id}/resume`, `/pause` (`api.rs:55,54`) |
| "지금 실행" | "지금 실행" `routines.rs:1690,1710` | `on_run_now` `routines.rs:608` | `run_schedule` `routines.rs:616` (`api.rs:1331`) | `POST /api/schedules/{id}/run` (`api.rs:56`) |
| 새 루틴 저장 (시간 트리거, 온라인) | "새 루틴", 저장 "저장" `routines.rs:1891,1910` | `on_save` `routines.rs:649` -> `create_schedule` `routines.rs:689` | `Api::create_schedule` (`api.rs:1307`) | `POST /api/schedules` (`api.rs:52`) |
| 루틴 편집 저장 (서버 스케줄) | "루틴 편집" `routines.rs:1889` | `on_save` `routines.rs:649-672` | `update_schedule(id, patch)` `routines.rs:668` (`api.rs:1312`) | `PATCH /api/schedules/{id}` (`api.rs:53`) |
| 이벤트 루틴, 오프라인 저장 | 알림 `OFFLINE_NOTE`/`LOCAL_NOTE` (`ui/routines.rs:1036-1040`) | `on_save` `routines.rs:699-735` | 없음 (`LocalStore`) | - |
| 로컬 루틴 지금 실행 | 알림 "서버에 연결되지 않아 지금 실행할 수 없습니다" `routines.rs:59,627,631` | `on_run_now` `routines.rs:630` | 없음 | - |
| 실행 기록 "세션 열기" | "세션 열기" `routines.rs:1822` | `svc.ui.open_conversation` `routines.rs:1824` | 없음 | - |
| 폼 떠날 때 | 시트 "변경 사항", "변경 사항을 버릴까요?", "계속 편집", "버리기" `routines.rs:1005-1012` | `leave_decision` | 없음 | - |
| 필터 | "전체", 검색 "루틴 검색" `routines.rs:1363,1374` | `FilterSegButton` 1125 | 없음 | - |


## 화면: 버전 관리


모든 호출은 `ember/app/src/ui/vcs.rs:1138` `git_call` -> `Api::git_raw(project, op, body)` (`ember/client/src/api.rs:1006`) -> `POST /api/projects/{name}/git/{*op}` (`ember/server/src/api/git.rs:67` `relay`) -> 노드 `POST /git/<op>` (`ember/node/src/api.rs:174-211`). 데모는 `demo.git(...)`로 대신한다 (`ui/vcs.rs:1141`). 아래 `ui/vcs.rs` 줄은 호출 함수 위치다.

| 사용자 동작 | 화면 문구 | 핸들러 (`ui/cr/vcs.rs`) | 호출 (`ui/vcs.rs`) | 노드 op |
|---|---|---|---|---|
| 화면 열기, 다시 시도 | 제목 "버전 관리", 섹션 "변경 사항/히스토리/브랜치/풀 리퀘스트/스태시/충돌/팀 작업" (`ui/vcs.rs:66-72`), "다시 시도" `4341`; 프로젝트 없음 "저장소를 둘 수 있는 프로젝트가 없습니다" `4318` | `VcsScreen` `4197`, 로드 `4228` | `fetch_snapshot` `1225` | `status`(1226), `conflicts`(1227), `diff`(1158) 두세 번 |
| 가져오기 / 내려받기 / 올리기 | "가져오기", "내려받기", "올리기" `405-407`; 성공 "Pull 완료: …" / "Push을 마쳤습니다" 등 (`ui/vcs.rs:3028-3040`) | `Actions::remote` `79`, `RemoteControls` `791` | `run_remote` `3015` | `fetch`, `pull`, `push` |
| 브랜치 전환 | 성공 "브랜치를 전환했습니다" `87` | 메뉴 행 `RepoBar` 약 `757`, `Actions::branch` `84` | `git_call("checkout")` | `checkout` |
| 새 브랜치 (메뉴) | "새 브랜치 이름", "새 브랜치", 성공 "새 브랜치를 만들었습니다" `766,775,88` | `Actions::branch(create)` | `git_call("branch")` | `branch` |
| 파일 체크와 diff | "변경 파일 {n}" `1100`, "이 덩어리 전체" `1010` | `Staging` 토글 `FilesHeader` `1082`, `DiffView` `933` | 로컬 상태 (커밋 때 반영) | - |
| 커밋 | 입력 "요약 (필수) 예: Feat: Wire shim", "설명 (선택)", "마지막 커밋 수정 (amend)", 보조 "선택한 변경 사항을 커밋합니다" / "요약과 스테이징한 파일이 필요합니다" `1341,1358,1378,1418-1420`; 성공 "커밋했습니다 (abc1234)" (`ui/vcs.rs:3009-3012`) | `CommitBox` `1305`, 클릭 `1396-1417` | `run_commit` `ui/vcs.rs:2995` | `stage`/`unstage`/`apply` 후 `commit` |
| 스태시 아이콘 | "스태시", 안내 "스태시는 추적하지 않는 파일을 포함하지 않습니다." `STASH_NOW_NOTE`; 성공 "스태시를 만들었습니다" `114` | `FilesHeader` `1106`, `Actions::stash_now` `105` | `run_stash_push` `ui/vcs.rs:2748` | `stash/push` |
| 히스토리 선택 | 행 푸시 알약 "푸시 안 됨", "원격에 있음", "병합" `2137-2143` | `HistoryPane` `2384`, 목록 `2419` | `fetch_history` `ui/vcs.rs:1402` | `log` |
| 커밋 상세 | "여기서 브랜치", "SHA 복사", "만들고 전환" `2329-2370`; "SHA를 클립보드에 복사했습니다." `2596` | 상세 로드 `2463` | `fetch_commit_detail` `ui/vcs.rs:1628` | `commit/show` |
| revert, cherry-pick | 확인 후 실행 (`commit_action_gate`) | `2510-2520` | `run_commit_revert`, `run_commit_cherry_pick` `ui/vcs.rs:1798` | `revert`, `cherry-pick` |
| 커밋에서 브랜치 | 실패 "브랜치 이름을 확인해 주세요. 공백이나 쓸 수 없는 문자가 있습니다" `2566` | `2571` | `run_branch_from` `ui/vcs.rs:1821` | `branch` |
| PR 목록과 상세 | 알약 "초안", "열림 {n}", "새 PR" `2828,3427,3431` | `3129`, `3180` | `fetch_prs` `ui/vcs.rs:1985`, `fetch_pr_detail` `2419` | `prs`, `pr` |
| PR 승인, 변경 요청, 코멘트 | "승인", "변경 요청", "코멘트", 두 번째 클릭 "정말 승인합니다", 성공 "승인했습니다" 등 (`ui/vcs.rs:2370-2392`); 코멘트 입력 "코멘트나 변경 요청의 내용" `3052` | `3259` | `run_pr_review` `ui/vcs.rs:2425` | `pr/review` |
| PR 병합 | "병합", "정말 병합합니다", "병합 후 브랜치 삭제", 성공 "병합했습니다" `3287`; 본인 승인 막힘 "본인이 연 풀 리퀘스트는 직접 승인할 수 없습니다." (`ui/vcs.rs:2241`) | `3292` | `run_pr_merge` `ui/vcs.rs:2436` | `pr/merge` |
| 새 PR | "제목 (필수)", "설명 (선택)", "만들기", "취소" `3382-3413`; 성공 "풀 리퀘스트 #{n}을 만들었습니다" | `3342` | `run_pr_create` `ui/vcs.rs:2445` | `pr/create` |
| 브랜치 목록 | "현재", "기본", "워크트리 {…}", "전환", "브랜치 검색" `3587-3704` | `3637`, 전환 `3739` | `fetch_branches` `ui/vcs.rs:2604` | `branches`, `checkout` |
| 스태시 목록, 적용, 꺼내기, 삭제 | "적용", "꺼내기", "삭제", 확인 "그래도 적용합니다/그래도 꺼냅니다/정말 삭제합니다", "스태시 만들기", "메시지 (선택)" `4060,4073`; 성공 "스태시를 적용했습니다/꺼냈습니다/삭제했습니다" | `3995`, `4014`, `4033` | `fetch_stashes` `ui/vcs.rs:2744`, `run_stash_action` `2758` | `stash/list`, `stash/{apply,pop,drop}`, `stash/push` |
| 충돌 | 병합 배너 "병합 취소", "병합 커밋", "정말 …합니다"; "해결 완료", "해결하고 스테이징", "목록으로", 성공 "충돌을 해결했습니다" `1930,2047-2069` | `1659`, `1694-1695`, `2066` | `fetch_merge_state` `ui/vcs.rs:3489`, `fetch_conflict` `3438`, `run_resolve` `3444`, `run_merge_abort` `3571`, `run_merge_commit` `3576` | `merge`, `conflict`, `resolve`, `merge/abort`, `merge/commit` |
| 팀 작업 | "리더", "현재" `3848,3858` | `TeamPane` `3875`, 멤버 cwd `member_cwds` `3790` | `fetch_branches` + 공유 PR 목록 | `branches`, `prs` |


## 화면: 에이전트


| 사용자 동작 | 화면 문구 | 핸들러 | 호출 API | 서버 라우트 |
|---|---|---|---|---|
| 화면 열기 | 제목 "에이전트", 부제 "하네스와 모델, 프로필, 네트워크, 사용량을 설정합니다" `agents.rs:348,356`; 섹션 "하네스/모델/프로필/네트워크/사용량" | `AgentsScreen` `agents.rs:249` | `bridge::request_usage_summary` `agents.rs:299` (`usage_summary(14일)` `bridge.rs:402`) | `GET /api/usage/summary` [확인 필요: 서버 라우트 표에는 `/api/usage`만 있다] |
| 하네스 "다시 감지" (라벨은 `rescan_label`) | KPI "설치된 하네스", "상주 shim", "세션 메모리 한도 합", "마지막 감지" `agents.rs:966-980` | `agents.rs:1124-1126` -> `bridge::rescan_agents` | `detect_harnesses("local")` `ember/app/src/bridge.rs:345` (`api.rs:2187`) | `POST /api/computers/{id}/harnesses/detect` (`ember/server/src/api/harnesses.rs:32`) |
| 메모리 한도 슬라이더 (1-16 GB) | "세션당 메모리 한도", "{n} GB" `agents.rs:1220,1190` | `agents.rs:1181-1188` -> `save_server_mem_limit` `agents.rs:127` | `server.put_agent_mem_limit` `agents.rs:139` | `PUT /api/agents/{agent}/settings` (`ember/server/src/api/mod.rs:85`) |
| 샌드박스 스위치 (Antigravity) | 알림 "샌드박스를 켰습니다. 셸 쓰기가 실패합니다." / "샌드박스를 껐습니다." `agents.rs:1189-1191` | `agents.rs:1186` `edit(...)` | 없음 (로컬 보관소만) | - |
| 상주 shim 스위치 | "상주 shim을 켰습니다." / "…껐습니다." `agents.rs:1207-1209` | `agents.rs:1204-1206` | 없음 (로컬만) | - |
| 기본 하네스, 모델 고르기 | "새 팀원 기본값", 안내 `DEFAULTS_STORAGE_NOTE` `agents.rs:1385,1451` | `agents.rs:1405-1430` -> `save_server_defaults` `agents.rs:97` | `put_agent_defaults` `agents.rs:107` (`ember/app/src/server.rs`) | `PUT /api/agents/defaults` (`api/mod.rs:84`) |
| 추론 강도, 권한 모드, 기본 모델 라디오 | "기본 추론 강도", "기본 권한 모드", 알림 "기본 모델을 바꿨습니다" `agents.rs:1670,1709,1781` | `agents.rs:1697,1731,1778` -> `save_server_defaults` | `put_agent_defaults` | `PUT /api/agents/defaults` |
| 기본 계정 고르기 | 알림 실패 "기본 계정을 바꾸지 못했습니다. {사유}" `agents.rs:1343` | `agents.rs:1440` -> `set_default_account` `agents.rs:1329` | `server.set_default_account`, 이어 `accounts()` `agents.rs:1333,1351` | `POST /api/accounts/{id}/default`, `GET /api/accounts` (`accounts/api.rs:39,36`) |
| "계정 추가" -> "만들기" | 시트 "계정 추가", "하네스", "이름"(예: "예: 회사 계정"), "만드는 중입니다", "만들기", "닫기" `agents.rs:1508-1574`; 실패 `ADD_FAILED` "계정을 만들지 못했습니다" | `agents.rs:1573` -> `create_account` `agents.rs:1581` | `server.create_account(kind, label)` `agents.rs:1598` | `POST /api/accounts` (`accounts/api.rs:36`) |
| "로그인 확인" | "로그인 확인" `agents.rs:1531`; 실패 "로그인을 확인하지 못했습니다" (`ui/agents.rs:1041`) | `agents.rs:1532` -> `check_login` `agents.rs:1615` | `server.check_account(id)` `agents.rs:1632` | `POST /api/accounts/{id}/check` (`accounts/api.rs:40`) |
| 프로필 편집, 새 프로필, 지우기, 순서, 임계값 | "새 프로필", "지우기", "위로/아래로/빼기", "낮추기/높이기" `agents.rs:1997,2087,2211-2246` | `edit_profiles` `agents.rs:161` | 없음 (앱 안 보관소) | - |
| 프로필 하네스, 고정 계정, 실패 시 동작 고르기 | 알림 "기본 프로필을 선택합니다", "프로필 하네스를 선택합니다", "고정 계정을 선택합니다", "실패 시 동작을 선택합니다" `agents.rs:1980,2141,2177,2277` | 알림만 띄움 | 없음 | - |
| 모델 프록시 켜기 | "모델 프록시", 켜면 `http://127.0.0.1:4000` 저장 `agents.rs:2287-2296` | `ProfileEditor::apply` `agents.rs:181` | 없음 | - |
| 네트워크 "작업 중인 컴퓨터로 내보내기" | 알림 "아직 검증 전이라 켜 둔 채로만 보입니다" `agents.rs:2353` | 알림만 | 없음 | - |
| 컴퓨터 "IP 확인" | "세션이 본 IP: {ip}" `agents.rs:2462-2464` | `agents.rs:2463` | 없음 | - |
| 사용량 기간 | "7일", "14일" `agents.rs:2490-2492` | `SegGroup` | `UsageSummary`는 화면 진입 때 한 번만 요청 | - |


## 화면: 파일


| 사용자 동작 | 화면 문구 | 핸들러 | 호출 API / 라우트 |
|---|---|---|---|
| 화면 열기 | 제목 "파일", 부제 "연결된 모든 장비 사이에서 파일을 주고받습니다. 휴대폰과 태블릿도 포함됩니다." (`files.rs:428`) | `FilesScreen` `files.rs:379` | `services().client.read(computers)`만. 서버 호출 없음 |
| KPI | "지금 전송 중", "직접 연결 비율", "연결된 장비", "이번 주 보낸 용량"(값 없으면 "준비 중입니다") `files.rs:558-582` | `kpi_cells` `files.rs:551` | 없음 |
| 헤더 "보내기" | "보내기" `files.rs:447` | `files.rs:439` `SendDraft::default` | 없음 (시트 열기) |
| 헤더 "공유 시트" | "공유 시트" `files.rs:1470` | `files.rs:430` | 없음 |
| 장비 타일 누름 | 오프라인이면 "{장비}은(는) 지금 연결되어 있지 않습니다." `files.rs:711` | `files.rs:703-724` | 없음 |
| "파일 고르기" | 안내 "파일 선택은 준비 중입니다" (`ui/files.rs:37`) | `files.rs:783-790` | 없음 (비데모는 알림만) |
| 에이전트 타일 "대화 열기" / "보내기" | "대화 열기", "보내기" `files.rs:909,914` | `ui.open_conversation` `files.rs:910`, 보내기 시트 | 없음 |
| 시트 "보내기" | "파일 전송을 시작했습니다." `files.rs:1447` | `files.rs:1440-1452` | `TransferService::send` (기본 구현은 `Err("준비 중입니다")` `ui/files.rs:613`) |
| 제안 "받기" / "거절" | "파일 전송 요청을 수락했습니다." / "…거절했습니다." `files.rs:975-976` | `files.rs:967-979` -> `answer_offer` | `TransferService::answer` (기본 구현은 아무 일 없음) |
| 전송 행 일시정지, 재개, 취소 | 아이콘 버튼 | `files.rs:1100-1106` | `TransferService::control` (기본 구현은 아무 일 없음) |
| 받은 파일 "열기" | 알림 "준비 중입니다" `files.rs:1172` | `files.rs:1172` | 없음 |
| 기록 필터 | "전체", "보냄", "받음", "실패와 거절" `files.rs:254-257`; "모든 장비" `files.rs:1190` | `HistoryCard` `files.rs:1178` | 없음 |


## 화면: 설정 (시트)


| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 테마 칩 | 구역 "화면 테마" / "앱 전체의 색상 모드를 선택합니다."; 칩 "시스템", "라이트", "다크" | `settings.rs:110-121` -> `set_theme_pref` | `prefs` 저장 |
| 단축키 체계, 표 | "에디터 단축키" / "Ember 에디터의 기본 단축키 체계를 선택합니다."; 토글 "단축키 표 보기"/"단축키 표 접기" | `update_prefs(|pr| pr.keymap = km)` `:131` | `prefs` 저장 |
| 기본 IDE | "기본 IDE" / "프로젝트나 세션에서 IDE 열기를 눌렀을 때 기본으로 실행할 대상입니다."; 칩 "매번 선택", "Ember 에디터" + 설치된 IDE | `update_prefs(|pr| pr.ide_target = v)` `:167-169` | `prefs` 저장 |
| 보관 표시 | "세션 목록" / "보관 처리된 이전 세션을 목록에 함께 표시합니다."; "보관된 세션 표시" + pill "켜짐"/"꺼짐" | `u.set_show_archived(!show_archived)` `:192` | 없음 |
| 서버, 경로 표시 | "연결 및 저장소": "메인 서버"({server_url}), "데이터 경로"(경로 또는 "메모리 전용"); 닫기 "닫기" | `settings.rs:221-228` | 없음 |


## 화면: 별도 IDE 창

- 실행: `ember-app --editor <project> <folder>` (FR-L31). 이 창만 아직 Dioxus HTML 모드로 돈다 (`ember/app/src/lib.rs:117-136`, `TODO(dioxus-compose#161)`).
- 화면 코드: `ember/app/src/ui/editor_workbench.rs`, `editor.rs`, `editor_scm.rs`, `editor_search.rs` ([modules/app-ui-dev.md](modules/app-ui-dev.md)).
- 편집기 연결: `ember/app/src/editor_host.rs` ([modules/app-core.md](modules/app-core.md)) → `ember-editor` 세션 ([modules/editor.md](modules/editor.md)) → `ember-editor-conn`으로 Code-OSS 서버에 붙는다 ([modules/editor-conn.md](modules/editor-conn.md)).
- 동작별 표는 아직 없다 [확인 필요]: 이 창의 화면 파일은 스크립트로 생사만 분류했고 동작 지도를 만들지 않았다.

## 화면: VS Code Web (proxy)

- 앱의 "IDE 열기"는 서버가 만든 URL(`ember/server/src/api/ide.rs`, [modules/server-api.md](modules/server-api.md))을 OS 브라우저로 연다. 그 URL 뒤에 `ember/proxy/`가 VS Code Web을 감싸고 오버레이를 넣는다.
- 로그인 화면, 오버레이, 분리 창 등 proxy 화면의 문구와 동작은 [modules/proxy.md](modules/proxy.md).

## 사용자에게 보이는 에러 메시지

화면별로 모았다. 원문으로 검색한다.

### 셸·홈·채널·검색·새 세션·설정


| 원문 | 위치 | 조건 |
|---|---|---|
| "작업 폴더를 알 수 없습니다. 새 세션 창에서 폴더를 정해 주세요" | `home.rs:635` | 홈에서 보내기, 폴더를 기억도 최근 세션 폴더도 못 구함 (이후 새 세션 다이얼로그를 연다) |
| "세션을 시작하지 못했습니다: {e}" | `home.rs:697`, `new_session.rs:258` | `create_session` 실패 |
| "메인 서버에서 시작했습니다. 컴퓨터를 바꾸지 못했습니다({e})" | `home.rs:667`, `new_session.rs:239` | `switch_computer` 실패 |
| "모두 허용을 켜지 못했습니다({e})" | `home.rs:672` | 바이패스 모드 `set_approve_all` 실패 |
| "세션을 업데이트하지 못했습니다: {e}" | `launcher.rs:232` | 고정, 이름 변경, 보관 실패 |
| "내보내지 못했습니다: {e}" | `launcher.rs:255` | 내보내기 실패 |
| "메시지를 불러오지 못했습니다. 잠시 뒤 다시 시도합니다." | `channels.rs:140` | 방 첫 로드 실패 |
| "메시지를 보내지 못했습니다. 입력한 내용은 그대로 남아 있습니다." | `channels.rs:199` | 채널 전송 실패 |
| "초대와 게스트를 불러오지 못했습니다", "서버에 연결되어 있지 않아 초대와 게스트를 관리할 수 없습니다" | `channel_owner.rs:494`, `:383` | 읽기 실패, 데모 |
| 등록 오류: "서버의 등록 기능이 꺼져 있어 코드를 만들 수 없습니다", "같은 이름의 컴퓨터가 이미 있습니다. 다른 이름을 입력하세요", "이 요청은 더 이상 확인을 기다리지 않습니다", "코드가 만료되었습니다. 새 코드를 만드세요" | `ember/app/src/ui/enrol_flow.rs:387-399`, `:52` | `EnrolCallError` 종류별 |
| "메시지 검색에 실패했습니다: {e}. 제목 일치만 보여줍니다." | `search.rs:165` | `GET /search` 실패 |
| "지표를 읽지 못했습니다" | `monitor.rs:206` | 지표 요청 실패 (마지막 값은 흐리게 유지) |


### 프로젝트·세션·대화


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


### 파일·루틴·에이전트·버전 관리


| 원문 | 위치 | 조건 |
|---|---|---|
| "서버에 연결되지 않아 지금 실행할 수 없습니다" | `routines.rs:59` | 로컬 루틴 즉시 실행, 표본 모드 |
| "이 프로젝트의 작업 폴더를 알 수 없습니다. 프로젝트에서 세션을 한 번 시작하셔야 합니다" | `routines.rs:60` | 새 서버 루틴 만들 때 `latest_cwd` 없음 |
| "서버가 요청을 처리하지 못했습니다: {e}" | `routines.rs:262` | `remote_action` 실패 |
| "서버가 루틴을 만들지 못했습니다: {e}" | `routines.rs:704` | 생성이 서버 오류 (연결 실패면 로컬 보관) |
| "기본값을 저장하지 못했습니다. {사유}", "메모리 한도를 저장하지 못했습니다. {사유}" | `agents.rs:114,146` | `PUT` 실패 |
| 사유: "입력을 확인하세요"(400,422), "권한이 없습니다"(401,403), "계정을 찾을 수 없습니다"(404), "이미 있는 이름입니다"(409), "서버가 처리하지 못했습니다"(5xx), "서버에 연결하지 못했습니다" | `ember/app/src/ui/agents.rs:1045-1054` | `account_error_ko(status)` |
| "{무엇}하지 못했습니다: {message}" / "…서버 인증에 실패했습니다. 서버 토큰을 확인해 주세요" / "…서버에 닿지 않습니다: {e}" | `ember/app/src/ui/vcs.rs:3059-3066` | 모든 git 호출 실패 (노드가 한국어 메시지를 주면 그대로) |
| "작업 중인 변경이 있습니다. 먼저 커밋하거나 스태시해야 합니다." 등 5종 | `ember/app/src/ui/vcs.rs:1677-1689` | `history_error_reason`: 메시지 문자열 부분 일치 |
| "준비 중입니다" | `ember/app/src/ui/files.rs:28`, `ui/vcs.rs:35`, `ui/agents.rs:684` | 미구현 기능 |


## 화면과 연결되지 않은 API

서버 `/api/*` 라우트 중 `client.md`, `app-core.md`, 세 `cr/` 화면 문서 어디에도 경로가 나오지 않는 것. 앱이 아닌 호출자(에이전트 CLI `ember-a2a`, 노드, 관리자 명령, guest·enrol door, proxy)가 쓰거나, 아직 화면이 없는 기능이다. 문서 문자열을 대조한 결과라 실제 호출 여부는 [확인 필요].

| 소스 파일 | 라우트 |
|---|---|
| `ember/server/src/a2a/api.rs` | `GET /api/a2a/targets` (`ember/server/src/a2a/api.rs:61`), `POST /api/a2a/messages` (`ember/server/src/a2a/api.rs:62`), `GET /api/a2a/messages/{id}` (`ember/server/src/a2a/api.rs:63`), `GET /api/a2a/settings` (`ember/server/src/a2a/api.rs:64`), `PUT /api/a2a/settings` (`ember/server/src/a2a/api.rs:64`), `GET /api/sessions/{id}/a2a` (`ember/server/src/a2a/api.rs:65`), `PUT /api/sessions/{id}/a2a` (`ember/server/src/a2a/api.rs:65`), `GET /api/a2a/team` (`ember/server/src/a2a/api.rs:69`), `POST /api/a2a/team/members` (`ember/server/src/a2a/api.rs:70`), `DELETE /api/a2a/team/members/{member}` (`ember/server/src/a2a/api.rs:71`), `GET /api/a2a/team/tasks` (`ember/server/src/a2a/api.rs:72`), `POST /api/a2a/team/tasks` (`ember/server/src/a2a/api.rs:72`), `PATCH /api/a2a/team/tasks/{number}` (`ember/server/src/a2a/api.rs:73`), `GET /api/a2a/team/mail` (`ember/server/src/a2a/api.rs:74`), `POST /api/a2a/team/mail` (`ember/server/src/a2a/api.rs:74`), `GET /api/a2a/terminal/{target}` (`ember/server/src/a2a/api.rs:75`), `POST /api/a2a/terminal/{target}/text` (`ember/server/src/a2a/api.rs:76`), `POST /api/a2a/terminal/{target}/interrupt` (`ember/server/src/a2a/api.rs:77`), `GET /api/sessions/{id}/terminal-grants` (`ember/server/src/a2a/api.rs:78`), `PUT /api/sessions/{id}/terminal-grants` (`ember/server/src/a2a/api.rs:78`), `GET /api/teams/{team_id}/mail` (`ember/server/src/a2a/api.rs:85`) |
| `ember/server/src/accounts/api.rs` | `GET /api/accounts/route` (`ember/server/src/accounts/api.rs:37`), `GET /api/accounts/{id}` (`ember/server/src/accounts/api.rs:38`), `DELETE /api/accounts/{id}` (`ember/server/src/accounts/api.rs:38`), `POST /api/accounts/{id}/clear-limit` (`ember/server/src/accounts/api.rs:41`), `GET /api/providers` (`ember/server/src/accounts/api.rs:43`), `POST /api/providers` (`ember/server/src/accounts/api.rs:43`), `DELETE /api/providers/{id}` (`ember/server/src/accounts/api.rs:47`) |
| `ember/server/src/api/ide.rs` | `GET /api/computers/{computer}/ide/relay/{launch_id}` (`ember/server/src/api/ide.rs:484`) |
| `ember/server/src/api/ide_extensions.rs` | `POST /api/computers/{id}/ide/extensions` (`ember/server/src/api/ide_extensions.rs:40`) |
| `ember/server/src/api/mod.rs` | `GET /api/search` (`ember/server/src/api/mod.rs:90`) |
| `ember/server/src/browser/api.rs` | `GET /api/browsers` (`ember/server/src/browser/api.rs:38`), `GET /api/browsers/{project}` (`ember/server/src/browser/api.rs:39`), `POST /api/browsers/{project}` (`ember/server/src/browser/api.rs:39`), `DELETE /api/browsers/{project}` (`ember/server/src/browser/api.rs:39`), `GET /api/browsers/{project}/egress` (`ember/server/src/browser/api.rs:40`), `PUT /api/browsers/{project}/egress` (`ember/server/src/browser/api.rs:40`), `DELETE /api/browsers/{project}/data` (`ember/server/src/browser/api.rs:41`), `POST /api/browsers/{project}/input` (`ember/server/src/browser/api.rs:42`), `GET /api/browsers/{project}/view` (`ember/server/src/browser/api.rs:43`), `GET /api/browsers/{project}/cdp` (`ember/server/src/browser/api.rs:44`), `GET /api/browsers/{project}/cdp/json/version` (`ember/server/src/browser/api.rs:45`), `GET /api/browsers/{project}/cdp/{nonce}` (`ember/server/src/browser/api.rs:47`), `GET /api/browsers/{project}/cdp/{nonce}/json/version` (`ember/server/src/browser/api.rs:48`), `GET /api/browsers/{project}/agent-config` (`ember/server/src/browser/api.rs:49`) |
| `ember/server/src/channels/guest.rs` | `GET /api/guest/channels/{id}` (`ember/server/src/channels/guest.rs:259`), `GET /api/guest/channels/{id}/messages` (`ember/server/src/channels/guest.rs:260`), `POST /api/guest/channels/{id}/messages` (`ember/server/src/channels/guest.rs:260`), `POST /api/guest/accept` (`ember/server/src/channels/guest.rs:264`) |
| `ember/server/src/chatgpt/api.rs` | `GET /api/chatgpt` (`ember/server/src/chatgpt/api.rs:34`), `POST /api/chatgpt/signin` (`ember/server/src/chatgpt/api.rs:35`), `POST /api/chatgpt/signin/complete` (`ember/server/src/chatgpt/api.rs:36`), `GET /api/chatgpt/signin/{state}` (`ember/server/src/chatgpt/api.rs:37`), `GET /api/chatgpt/accounts/{id}` (`ember/server/src/chatgpt/api.rs:40`), `DELETE /api/chatgpt/accounts/{id}` (`ember/server/src/chatgpt/api.rs:40`), `POST /api/chatgpt/accounts/{id}/refresh` (`ember/server/src/chatgpt/api.rs:44`), `POST /api/chatgpt/accounts/{id}/clear-limit` (`ember/server/src/chatgpt/api.rs:45`), `GET /api/chatgpt/accounts/{id}/models` (`ember/server/src/chatgpt/api.rs:46`) |
| `ember/server/src/computers/api.rs` | `PUT /api/sessions/{id}/designated-computer` (`ember/server/src/computers/api.rs:42`) |
| `ember/server/src/computers/fs.rs` | `POST /api/computers/{id}/fs/{op}` (`ember/server/src/computers/fs.rs:49`) |
| `ember/server/src/computers/metrics.rs` | `GET /api/computers/{id}/metrics` (`ember/server/src/computers/metrics.rs:26`) |
| `ember/server/src/computers/terms.rs` | `GET /api/computers/{id}/terms/{tid}` (`ember/server/src/computers/terms.rs:50`), `DELETE /api/computers/{id}/terms/{tid}` (`ember/server/src/computers/terms.rs:50`), `GET /api/computers/{id}/terms/{tid}/snapshot` (`ember/server/src/computers/terms.rs:51`), `POST /api/computers/{id}/terms/{tid}/control` (`ember/server/src/computers/terms.rs:52`), `POST /api/computers/{id}/terms/{tid}/kill` (`ember/server/src/computers/terms.rs:53`) |
| `ember/server/src/devices/api.rs` | `GET /api/devices` (`ember/server/src/devices/api.rs:25`), `POST /api/devices` (`ember/server/src/devices/api.rs:25`), `DELETE /api/devices/{peer}` (`ember/server/src/devices/api.rs:26`) |
| `ember/server/src/hub/api.rs` | `GET /api/hub` (`ember/server/src/hub/api.rs:53`), `POST /api/hub/devices/{id}/computer` (`ember/server/src/hub/api.rs:55`), `POST /api/hub/link` (`ember/server/src/hub/api.rs:62`), `DELETE /api/hub/link` (`ember/server/src/hub/api.rs:62`), `POST /api/hub/check` (`ember/server/src/hub/api.rs:63`), `DELETE /api/hub/registration` (`ember/server/src/hub/api.rs:64`), `DELETE /api/hub/devices/{id}` (`ember/server/src/hub/api.rs:65`), `GET /api/hub/link-codes/{code}` (`ember/server/src/hub/api.rs:66`), `POST /api/hub/link-codes/{code}` (`ember/server/src/hub/api.rs:66`), `POST /api/hub/sync-devices` (`ember/server/src/hub/api.rs:67`), `PUT /api/hub/sync-devices` (`ember/server/src/hub/api.rs:67`) |
| `ember/server/src/mcp/api.rs` | `GET /api/mcp` (`ember/server/src/mcp/api.rs:29`), `POST /api/mcp` (`ember/server/src/mcp/api.rs:29`), `GET /api/mcp/{id}` (`ember/server/src/mcp/api.rs:30`), `PATCH /api/mcp/{id}` (`ember/server/src/mcp/api.rs:30`), `DELETE /api/mcp/{id}` (`ember/server/src/mcp/api.rs:30`) |
| `ember/server/src/schedules/api.rs` | `GET /api/a2a/schedules` (`ember/server/src/schedules/api.rs:64`), `POST /api/a2a/schedules` (`ember/server/src/schedules/api.rs:64`), `DELETE /api/a2a/schedules/{id}` (`ember/server/src/schedules/api.rs:65`) |
| `ember/server/src/transfers.rs` | `GET /api/transfers` (`ember/server/src/transfers.rs:717`), `POST /api/transfers/offers` (`ember/server/src/transfers.rs:718`), `POST /api/transfers/offers/{id}/accept` (`ember/server/src/transfers.rs:719`), `POST /api/transfers/offers/{id}/decline` (`ember/server/src/transfers.rs:720`), `POST /api/transfers/{id}/chunks` (`ember/server/src/transfers.rs:721`), `GET /api/transfers/{id}/resume-offset/{file}` (`ember/server/src/transfers.rs:722`), `POST /api/transfers/{id}/complete` (`ember/server/src/transfers.rs:723`), `POST /api/transfers/{id}/pause` (`ember/server/src/transfers.rs:724`), `POST /api/transfers/{id}/resume` (`ember/server/src/transfers.rs:725`), `POST /api/transfers/{id}/cancel` (`ember/server/src/transfers.rs:726`), `GET /api/transfers/history` (`ember/server/src/transfers.rs:727`), `DELETE /api/transfers/history` (`ember/server/src/transfers.rs:727`), `PUT /api/transfers/settings` (`ember/server/src/transfers.rs:728`) |

