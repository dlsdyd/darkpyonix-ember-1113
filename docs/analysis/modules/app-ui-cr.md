# 모듈: app-ui-cr

- 경로: `ember/app/src/ui/cr/` 중 `project.rs`, `conversation.rs`, `session.rs`, `files.rs`, `routines.rs`, `agents.rs`, `vcs.rs`를 뺀 21개 파일 (`docs/analysis/_raw/modules.md` "app-ui-cr")
- 규모: 파일 21개 / 약 11,400줄 (`home.rs` 2503, `components.rs` 1471, `shell.rs` 1063, `channels.rs` 899, `monitor.rs` 756, `theme.rs` 710, `channel_owner.rs` 715, `add_computer.rs` 697, `characters_screen.rs` 558, `settings.rs` 502, 나머지 각 460 이하). 줄 수의 상당 부분은 `#[cfg(test)]` 블록이다.
- 레이어: UI (compose-rust 기반 라이브 UI)
- 한 줄 책임: 기본 실행 때 뜨는 compose-rust 셸(사이드바, 레일, 하단 탭)과 그 안의 홈, 채널, 검색, 새 세션, 설정 화면, 시트(컴퓨터 추가, 모니터, 멤버/게스트, 새 채널), 공용 컴포넌트와 디자인 토큰을 그린다.
- 의존하는 모듈: `ember/app/src/ui/*`의 Dioxus 모듈(순수 결정 함수만 재사용, 5절 참고), `ember/app/src/services.rs`(`services()`, `run_shared`), `ember_client`([client](client.md): `services().client.api()`), `compose_rust`(외부 크레이트)
- 이 모듈을 쓰는 모듈: `ember/app/src/lib.rs:137-145`(기본 실행은 `ui::cr::shell::launch`, `EMBER_CR_GALLERY`는 `gallery::launch`), `ember/app/src/ui/fonts.rs:55`(`cr::theme::{LIGHT, DARK}`로 앱 팔레트 생성), 같은 `cr/`의 제외된 7개 화면 파일(`components`, `theme`, `shell`, `notice`, `launcher`, `characters`, `channels::Avatar` 등을 가져다 씀)

`cr/mod.rs:1-3`: "각 모듈은 `ui/`의 같은 이름 Dioxus 모듈을 그대로 본뜨고, 마지막 화면이 옮겨지면 대체한다(phase 8에서 원본 삭제). 이 안은 `dioxus_compose`를 import하지 않는다." (#220). 그래서 이 모듈은 "그리는 코드"이고, 판단 로직(메뉴 순서, 화면 선택, 정렬, 문구 상수)은 `crate::ui::<module>`에 남아 있다.

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `shell::launch(pref)` | fn | `ember/app/src/ui/cr/shell.rs:779` | 기본 실행. 테마 설정 후 `LaunchBuilder`로 창("Ember", 기본 1440x900) 열기 |
| `shell::shell()` | composable | `shell.rs:599` | 루트 레이아웃. 메뉴->화면 분기(아래 1절)와 시트 호스팅 |
| `shell::choose(ui, menu)` | fn | `shell.rs:69` | 메뉴 이동. 프로젝트=`Route::Projects`, 세션=가장 최근 대화 열기 |
| `shell::Sidebar/RailItem/NavRow/BottomBar/PhoneMenu/Placeholder` | composable | `shell.rs:330/196/161/412/481/575` | 내비게이션 조각 |
| `shell::requested()`, `window_chrome()` | fn | `shell.rs:748`, `:769` | `EMBER_CR_SHELL` 읽기, macOS 풀사이즈 크롬 |
| `home::HomeScreen` | composable | `home.rs:504` | 홈 화면 (작성기 + 대시보드) |
| `channels::ChannelsScreen`, `ChannelsScreenWith`, `Avatar`, `sample_rooms`, `preview` | composable/fn | `channels.rs:209/227/60/713/783` | 채널 화면 |
| `search::SearchScreen` | composable | `search.rs:64` | 검색 화면 |
| `new_session::NewSessionDialog`, `can_start`, `build_request` | composable/fn | `new_session.rs:41/50/55` | 새 세션 다이얼로그 |
| `settings::SettingsSheet`, `SettingsContent`, `shortcut_rows`, `ide_choice_label`, `IDE_CHOICES` | 혼합 | `settings.rs:69/82/31/51/61` | 설정 시트 |
| `add_computer::AddComputerSheet`, `AddUi` | composable/struct | `add_computer.rs:378/42` | 컴퓨터 추가 시트 (`project.rs:1216`에서 호출) |
| `monitor::MonitorSheet`, `mon_columns`, `card_height`, `sort_mark` | 혼합 | `monitor.rs:89/58/254/47` | 컴퓨터 모니터 시트 (`project.rs:1220`) |
| `channel_owner::MembersSheet`, `OwnerState`, `hour_chip_rows` | 혼합 | `channel_owner.rs:335/41/408` | 채널 멤버/게스트 시트 |
| `new_channel::NewChannelButton/NewChannelSheet/NewChannelState` | 혼합 | `new_channel.rs:130/205/27` | 새 채널 시트 |
| `characters_screen::CharactersScreen` | composable | `characters_screen.rs:140` | 팀 캐릭터 화면 (메뉴 아님, `ui.characters`가 `Some`일 때) |
| `characters::Character`, `StylePicker`, `draw` | composable | `characters.rs:41/79/68` | 그려진 팀 캐릭터 |
| `launcher::ConnectionBanner`, `SessionRowView/With`, `patch_session`, `rename`, `export` | 혼합 | `launcher.rs:31/91/96/229/238/246` | 세션 행과 서버 호출 |
| `notice::post`, `NoticeHost` | fn/composable | `notice.rs:19/25` | 어느 스레드에서든 토스트 |
| `components::*`, `compat::*`, `theme::*`, `ko::*`, `a11y::*`, `gallery::*` | 모음 | 3-4절 | 토큰, 컴포넌트, 문구 표 |

## 1. 셸 매핑: 메뉴와 창 크기가 화면 함수가 되는 경로

### 1.1 메뉴 -> 화면 함수

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

### 1.2 창 크기 -> 레이아웃

`current_mode(collapsed)` (`cr/shell.rs:593`)가 `nav_mode(width_dp, collapsed)` (`ember/app/src/ui/shell.rs:205-213`)를 부른다. 창 폭은 `compose_rust::runtime::current_window_size()`로 읽어 recomposition에 걸린다 (`:593`의 주석).

| 폭 (dp) | `ShellMode` | 그리는 곳 | 비고 |
|---|---|---|---|
| `<= 560` (`BAR_MAX_DP`, `ui/shell.rs:201`) | `BottomTabs` | `shell.rs:677-693`: 내용 열 + `BottomBar` (`:412`) + 폰 메뉴 `PhoneMenu` (`:481`) | 탭 5개: 홈, 프로젝트, 세션, 채널, 더보기 (`BOTTOM_TABS`, `ui/shell.rs:142`). 더보기 시트(`:710`)는 `MORE_MENUS`: 루틴, 버전 관리, 에이전트, 파일 (`ui/shell.rs:151`). 대화방이 열려 있으면(`ui.detail_open`) 폰 메뉴를 숨긴다 (`shell.rs:691`) |
| `561..=1279` (`RAIL_MAX_DP`, `ui/shell.rs:199`) | `Rail` | `shell.rs:694-709`: `Sidebar(rail=true)` 72dp (`RAIL_W`, `theme.rs:300`) + 내용 | 접기 토글은 이 구간에서 무효 (`toggled_collapse`, `ui/shell.rs:218`) |
| `> 1279` | `Sidebar` (접으면 `Rail`) | 같은 분기, `Sidebar(rail=false)` 234dp (`SIDE_W`, `theme.rs:299`) | 브랜드 줄의 접기 버튼이 `collapsed`를 토글 |
- 화면 안쪽 크기 분기는 각 화면이 `current_window_size()`로 따로 한다: 채널 분할(`split_view(window.class)`, `channels.rs:236`), 홈 `layout(width_dp)` (`home.rs:156`), 시트 표현(<560 바텀시트, 그 외 다이얼로그, 모니터는 <=560 전체 화면; `components.rs:760-770`).
- Windows는 내용 열 위에 32dp 캡션 띠 + 138dp 오른쪽 예약을 그린다 (`shell.rs:629-637`, `WINDOWS_CAPTION_HEIGHT_DP`). macOS 하단탭 모드는 신호등 아래 띠(`strip`, `:612`, `:638-640`). 둘 다 `TODO(#213, #204)` (`shell.rs:11-14`).

### 1.3 검토용 실행 경로

`launch`는 `EMBER_CR_ROUTE` 값으로 화면 하나를 바로 연다 (`shell.rs:785-837`): `search`, `new-session`, `launcher-row`(`launcher::rows_preview`), `monitor`(`monitor::preview`), `channels`, `project`/`project-detail`, `files`, `vcs`, `agents`, `routines`, `home`, `session(s)`, `characters`, `conversation`(대화 `demo-s1`). `EMBER_CR_SIZE=WxH` (기본 1440x900, `:756-766`), `EMBER_CR_SHELL=light|dark|1` (`:747-754`).

## 2. 파일별 요약

### `ember/app/src/ui/cr/shell.rs` (1063줄, 테스트 8개)
- 목적: 사이드바, 레일, 하단 탭, 폰 메뉴, 루트 레이아웃, 런처.
- 주요 심볼: `choose` `:69`, `NavIcon` `:127`(SVG를 색, 크기별로 tint하고 `'static`으로 leak해 캐시 `:98-125`), `RedBadge` `:133`, `NavRow` `:161`, `RailItem` `:196`, `ToolRow` `:224`, `Brand` `:252`, `UserRow` `:283`, `Sidebar` `:330`, `BottomBar` `:412`, `PhoneMenu` `:481`, `shell` `:599`, `launch` `:779`.
- 의존: `ui::shell`(re-export 목록 `:30-35`), `ui::coexist::{shared_ui, SharedUi}`, `ui::Route`, `ui::safe_area`, `ui::fonts::app_theme`, `crate::model`, `crate::demo::active_from_env`, `crate::services::try_services`.
- 사용처: 이 모듈 전체와 제외된 화면(`NavIcon`, `ICON_*`).
- 부수효과: `ICONS`/`DOCS` thread_local에 SVG 바이트를 영구 leak (`:98-112`). 데모 초기화는 `services.reset_demo()` 호출 (`:389-395`).
- 주의점: `UserRow`가 `DEMO_USER`("BREW", "ncmnd", `ui/shell.rs`)를 데모와 무관하게 그린다 (`:285`). 5.2절 이슈 참고.

### `ember/app/src/ui/cr/home.rs` (2503줄, 테스트 22개)
- 목적: 홈. 위쪽은 인사말 + 큰 작성기 + 제안 칩, 아래는 "오늘의 팀" 대시보드.
- 주요 심볼: `HomeScreen` `:504`, `Composer` `:538`(상태) / `send` `:617` / `lists` `:704`, `Hero` `:1055`, `ComposerCard` `:1213`, `Dashboard` `:1401`, `IntegrationsArea` `:1459`, `KpiStrip` `:1562`, `TokenTrendTile` `:1623`, `StatusTile` `:1707`, `HarnessTile` `:1839`, `CrewTile` `:1928`, `SuccessTile` `:1967`, `ProjectsTile` `:2017`, `layout` `:156`.
- 의존: `ui::home`(결정 함수 대량 re-export `:17-24`, `read_dash`, `stage_attachment`, `GithubCard` 등), `ui::usage`, `ui::shell::{NavMenu, DEMO_USER}`, `ui::coexist`, `crate::server::CreateSession`, `crate::prefs::LastUsed`, `crate::bridge::request_github_summary`.
- 사용처: `shell.rs:653`. `home::text_px`는 `channel_owner.rs:21`에서도 사용.
- 부수효과: 마운트 때 GitHub 요약 요청 (`:511-514`). 보내기는 세션을 만들고 outbox에 첫 메시지를 넣은 뒤 대화로 이동 (동작 지도 참고).
- 주의점: `EMBER_CR_SCROLL`, `HOME_PICK/MODE/SUGGEST` 검토 훅이 프로덕션 코드에 섞여 있다 (`Skip::from_env` `:466`, `initial_pick` `:429`, `initial_suggestion` `:456`).

### `ember/app/src/ui/cr/components.rs` (1471줄, 테스트 28개)
- 목적: 공용 컴포넌트 (3절).
### `ember/app/src/ui/cr/theme.rs` (710줄, 테스트 17개)
- 목적: 디자인 토큰 (3절).
### `ember/app/src/ui/cr/channels.rs` (899줄, 테스트 9개)
- 목적: 채널 화면 (카카오톡식 방 목록과 방 보기).
- 주요 심볼: `Feed` `:79`(`refresh` `:101`, `follow` `:131`, `mark_read` `:163`, `send` `:181`), `ChannelsScreen` `:209`, `ChannelsView` `:231`, `RoomList` `:321`, `RoomItem` `:417`, `RoomView` `:463`, `InputBar` `:553`, `BubbleRow` `:642`, `Avatar` `:60`, `POLL_EVERY` `:75`(2초), `list_width` `:43`.
- 의존: `ui::channels`(re-export `:24-29`: `rooms_from`, `merge_messages`, `split_view` 등 판단 로직 전부), `ui::project::{display_name, harness_tone}`, `ui::characters::seed_hash`, `super::{new_channel, channel_owner, notice}`.
- 부수효과: 방을 열면 `follow` 효과가 2초마다 `?after=seq`로 폴링 (`:131-160`); 방 열기 때 읽음 처리.
- 주의점: `ChannelsScreen`은 데모, `EMBER_CR_ROUTE=channels`일 때 `Feed` 없이 샘플 방(`sample_rooms` `:713`: "배포 논의", "디자인 리뷰", "자유 채널")을 그리고 보내기를 막는다 (`:209-215`). 입력창의 첨부, 이모지 버튼은 `a11y` 상수만 있고 동작 연결은 `[확인 필요]`.

### `ember/app/src/ui/cr/monitor.rs` (756줄, 테스트 11개)
- 목적: 컴퓨터 모니터 시트(FR-L21). 열려 있는 동안 `POLL_SECS`마다 지표를 읽어 카드, 막대, 프로세스 표로 그림.
- 주요 심볼: `MonitorSheet` `:89`, `fetch_metrics` `:76`, `Grid` `:214`, `StatusCard` `:286`, `FanCard` `:336`, `MetricCard` `:354`, `Meter` `:372`, `ProcessTable` `:404`, `ProcessRowView` `:467`, `mon_columns` `:58`, `preview` `:513`.
- 의존: `ui::monitor`(피드, 정렬, 서식 `:18-27`), `ui::project::{ComputerChip, ProjectBox, reach_pill, display_name, SOON}`, `ui::Route`, `super::characters`.
- 부수효과: 시트가 열려 있는 동안 `launched_effect`가 루프로 폴링 (`:107-115`), 오프라인 컴퓨터는 폴링 안 함.
- 주의점: 데모는 `demo::metrics_sample`/`metrics_previous` (`:77-79`, `:108`). 팬 제어 버튼은 비활성이고 이유 문구만 보인다 (`FAN_MODE_AVAILABLE`, `FAN_MODE_REASON`).

### `ember/app/src/ui/cr/channel_owner.rs` (715줄, 테스트 4개)
- 목적: 채널 소유자 시트 "멤버/게스트" (FR-T14 초대, FR-T15 게스트, FR-T17 허용 시간).
- 주요 심볼: `OwnerState` `:41`(`refresh` `:205`, `read_door` `:233`, `act` `:257`, `create_invite` `:286`, `revoke` `:300`, `remove` `:307`, `allow` `:314`, `clear` `:325`), `MembersSheet` `:335`, `HourChips` `:420`, `InviteSection` `:435`, `InviteList` `:486`, `GuestList` `:541`, `review_sample_data` `:83`.
- 의존: `ui::channel_owner`(문구, 판단 `:25-27`), `super::home::text_px`, `super::project::wrap_lines`, `super::notice`.
- 주의점: 새 초대 링크는 시트 상태에만 있고 시트를 닫으면 사라진다 (서버가 한 번만 보여줌, `:6-8`). 리뷰 샘플은 `EMBER_CR_OWNER_SHEET`, `EMBER_CR_OWNER_DOOR` 환경 변수일 때만 (`:138-150`).

### `ember/app/src/ui/cr/add_computer.rs` (697줄, 테스트 0개)
- 목적: "컴퓨터 추가" 시트(FR-C1, FR-C2, D39, #490): 허브 기기 목록, 이름 입력, 일회용 코드 발급, 폴링, 확인 카드, 결과.
- 주요 심볼: `AddUi` `:42`, `mint` `:242`, `fetch_status` `:278`, `apply_poll` `:289`, `confirm` `:315`, `deny` `:355`, `cancel_on_server` `:223`, `load_devices` `:232`, `AddComputerSheet` `:378`, `ListBody` `:444`, `NamingBody` `:466`, `WaitingBody` `:508`, `ConfirmBody` `:560`, `Outcome` `:651`.
- 의존: `ui::add_computer::*`, `ui::enrol_flow`(상태기계 `Stage`, `RunGuard`, 문구 상수), `crate::model::now_ms`.
- 부수효과: 코드는 시트 상태에만 보관하고 닫을 때 서버 취소 (`cancel_on_server`); 로그, 저장 금지 (`:5-6`).

### `ember/app/src/ui/cr/characters_screen.rs` (558줄, 테스트 6개)
- 목적: 팀 캐릭터 화면(FR-L22, D29, #489): 여섯 스타일 x 9칸 카탈로그, 팀 미리보기, 한 팀원 편집기. 메뉴가 아니라 프로젝트 설정 시트에서 열리고 "뒤로" 버튼이 있다.
- 주요 심볼: `CharactersScreen` `:140`, `apply_style` `:31`, `Section` `:70`, `FieldRow` `:84`, `Cell` `:106`, `StyleSection` `:120`, `LEAD` `:398`.
- 의존: `ui::characters`(`team_preview`, `style_apply_needed` 등), `ui::project::{project_boxes, effective_style, patch_error_message}`, `ui::coexist`.
- 주의점: 편집기 변경은 저장되지 않는 미리보기다 ("팀원별 수정은 아직 저장되지 않고" `:271`).

### `ember/app/src/ui/cr/settings.rs` (502줄, 테스트 4개)
- 목적: 설정 시트: 테마, 에디터 단축키, 기본 IDE, 보관 세션 표시, 서버/데이터 경로.
- 주요 심볼: `SettingsSheet` `:69`, `SettingsContent` `:82`, `SectionBlock` `:232`, `InfoRow` `:242`, `ShortcutTableView` `:254`, `shortcut_rows` `:31`, `IDE_CHOICES` `:61`.
- 의존: `ui::keymap::{Action, Keymap, Os}`, `crate::ide::IdeKind`, `ui::coexist`, `crate::services::try_services`.

### 작은 파일과 중간 파일

| 파일 (줄) | 요약 |
|---|---|
| `new_session.rs` (457) | 새 세션 다이얼로그(FR-L8). `NewSessionDialog` `:41`, `NewSessionForm` `:82`, `can_start` `:50`, `build_request` `:55`, `FALLBACK_AGENTS` `["claude-code","codex"]` `:28`. `TODO(compose-rust#374)`: TextField 초기값이 없어 기억한 값을 placeholder로 보임 (`:5-6`) |
| `new_channel.rs` (332) | "새 채널" 시트(FR-T10). `NewChannelState` `:27`, `NewChannelButton` `:130`, `create` `:163`, `NewChannelSheet` `:205`. 데모, 리뷰에서는 만들기 대신 이유를 알림 (`:5-7`, `DEMO_NO_CREATE`) |
| `search.rs` (259) | 전체 검색(FR-L9, FR-S4). `SearchScreen` `:64`, `DEBOUNCE` 250ms `:30`, `HIT_LIMIT` 100 `:32`, `superseded` `:56` |
| `launcher.rs` (323) | Dioxus `Launcher` 화면 중 다른 화면이 쓰는 조각만 이식(`:1-7`): `ConnectionBanner` `:31`, `SessionRowWith` `:96`(고정, 이름 변경, 보관, 내보내기 메뉴), `patch_session` `:229`, `rename` `:238`, `export` `:246` |
| `characters.rs` (138) | `Character` `:41`, `StylePicker` `:79`. 그림 로직은 `ui::characters`(`svg`, `family_of` 등 re-export `:16`) |
| `compat.rs` (237) | 공용 위젯: `Badge` `:57`, `Dot` `:71`, `Spinner` `:86`, `StatusIndicator/Dot/Pill` `:94/122/127`, `MessageText` `:136`, `CodeText` `:144`, `SplitPane` `:174`, `Banner` `:190`, `tone_colors` `:23`, `mix` `:36` |
| `gallery.rs` (157) | `EMBER_CR_GALLERY=light|dark|1`일 때 컴포넌트 갤러리 창 (`lib.rs:137`). "마지막 phase와 함께 사라진다" (`:5`) |
| `notice.rs` (55) | `post(text)` `:19`(전역 `NEXT` 카운터, `shared_ui().notice`에 저장), `NoticeHost` `:25`가 `Message::new(text).with_duration(Long).show()`. 워커 스레드의 호출을 UI 스레드에서 보여주려는 우회 (`:1-5`) |
| `a11y.rs` (58) | 아이콘 전용 버튼의 한국어 접근성 이름 상수 12개 (`THEME` "테마 전환" ... `OPEN_SESSION` "세션 열기"). 툴킷에 라벨 modifier가 없어(compose-rust#460) 대부분 아직 적용 못 함 (`:1-8`). 실제 사용은 `project.rs:578,584,780,782`의 `VERSION_CONTROL`, `PROJECT_SETTINGS`뿐 |
| `ko.rs` (192) | 한국어 문구 표 (4절) |
| `mod.rs` (31) | 모듈 선언 27개. `dioxus_compose` import 금지 (`:1-3`) |

## 3. 토큰과 컴포넌트

### 3.1 `theme.rs` 토큰 (NFR-L3, DESIGN.md 2절, mockup `style.css`)

- 팔레트: `LIGHT` `:70`, `DARK` `:91` (`Palette` 필드 `bg, surface, surface_2, line, text, text_2, muted, hover, sel, ink, ink_text, track` + 액센트 `blue, orange, sky, grey, red, green`: 각각 `strong`/`soft`). 예: 라이트 `bg 0xf3f2ee`, `surface 0xffffff`, `text 0x1c1b19`, `blue 0x3f74d4/0xe6eefb`; 다크 `bg 0x151514`, `surface 0x1f1f1d`, `text 0xf0eee9`, `blue 0x6b95e0/0x1e2a3f`.
- 타입: `Fs` 9단계 `Xs2 11, Xs 12, Sm 13, Md 14, Lg 15, Xl 18, Xl2 28, Xl3 32, Xl4 40` (`:219-231`), `Weight` Regular/Medium/Semibold 3종 (`:260-282`).
- 간격: `SP = [4,8,12,16,20,24,32]` `:284`; `GAP_CARD 16`, `GAP_BLOCK 12`, `PAD_CARD_V/H 16/20`, `PAD_ROW_V/H 12/16` (`:286-292`).
- 크기: `H_BTN 40`, `H_CTL 32`, `H_PILL 24`, `H_PILL_SM 20`, `H_NAV_ITEM 38`, `SIDE_W 234`, `RAIL_W 72`, `TABBAR_H 64`, `TABBAR_RADIUS 26`, `SHEET_HEADER_H 60` (`:294-305`).
- 반경: `CORNER_2XS 5, XS 6, SM 8, MD 12, LG 14, XL 24, BUBBLE 18, TAIL 6`, `PILL 999` (`:307-316`), `SQUIRCLE_SMOOTHING 0.6` `:321`.
- 눌림: `PRESS_SCALE 0.975`, `PRESS_IN_MS 180`, `HOLD 120`, `OUT 200` (`:326-329`), 틴트는 라이트 `0x12000000`, 다크 `0x1a000000` (`ember/app/src/ui/theme.rs:182-185`).
- 그림자: `SHADOW_SM/MD/LG_LIGHT/DARK` `:337-369`, `with_shadows(modifier, layers)` `:378`.
- 테마 해석: `ember_theme()` `:388`은 `services().ui.theme_pref`를 읽는 컴포저블 상태이고 서비스가 없으면 기본값(System). `system_scheme()` `:29`는 항상 `Scheme::Light` (compose-rust#97: OS 값을 읽는 훅 없음, 따라서 "시스템"은 라이트로 그림).
- `Scheme`, `ThemePref`는 새로 정의하지 않고 `crate::ui::theme`에서 re-export (`:22`): "라이트/다크/시스템" 라벨 (`ui/theme.rs:44-50`).

### 3.2 `ember/app/src/ui/theme.rs`와의 이중 정의 (같이 고쳐야 함)

`ember/app/src/ui/theme.rs`(567줄)에 `Accent` `:83`, `Palette` `:90`, `LIGHT` `:118`, `DARK` `:139`, `EmberTheme` `:162`, `Fs` `:~200`, `Weight`, `SP` `:291`, `GAP_*`, `PAD_*`, `H_*` 같은 값이 한 번 더 정의돼 있다 (`cr/theme.rs:6-7`: "값은 Dioxus 원본과 같아야 하고 아래 테스트가 둘 다 고정한다"). 어느 쪽 팔레트가 어디서 쓰이나:

| 소비자 | 쓰는 팔레트 | 근거 |
|---|---|---|
| `cr/` 전체 화면과 컴포넌트 | `cr::theme::{LIGHT, DARK}` (`use super::theme::*`) | 각 파일 `use super::theme::*` |
| 툴킷 앱 팔레트 `APP_PALETTE` (Cupertino unified 테마, `ColorRole`별 라이트/다크 매핑) | `cr::theme::{DARK, LIGHT}` | `ember/app/src/ui/fonts.rs:55-63` |
| Dioxus 쪽 화면(`ember/app/src/ui/*.rs`) | `ui::theme` 자체 | - |

토큰 하나를 바꾸면 `cr/theme.rs`, `ui/theme.rs`, 그리고 모크업 `style.css`(NFR-L3) 세 곳을 함께 보아야 하고, 폰트 스택(`components.rs:35-51`: Inter -> Apple SD Gothic Neo -> Noto Sans KR -> SystemUi, 모노 JetBrains Mono -> SF Mono -> Menlo)은 `fonts.rs`의 번들 폰트와 함께 본다. `cr/theme.rs`의 테스트(`nfr_l3_*`)가 DESIGN.md 표와 일치를 고정한다 (`:405-441`).

### 3.3 `components.rs` 컴포넌트

| 이름 | 줄 | 설명 |
|---|---|---|
| `Clickable(modifier, align, on_click, content)` | `:121` | 눌림 효과가 있는 클릭 컨테이너. 행(`NavRow` 등)은 모두 이것으로 구현 |
| `Label(text, fs, weight, color, max_lines)` | `:252` | 한 줄/줄 수 제한 텍스트 (cr 화면은 이것을 쓰도록 테스트가 강제 `:1369`) |
| `MonoLabel`, `Txt` | `:271`, `:286` | 모노, 일반 텍스트 |
| `EmberField(FieldOptions)` | `:358` | 토큰으로 그린 텍스트 필드 (`FieldOptions` `:332`: `placeholder`, `on_value_change`, `on_submit`, `multiline`, `bare` 등) |
| `AppButton(text, icon, kind, small, enabled, fill, on_click)` | `:552` | `ButtonKind::{Default, Primary, Destructive}` `:488` |
| `IconButton(IconRole, small, on_click)` | `:583` | 아이콘 단추 |
| `Pill(text, PillTone, small)` | `:452` | 톤 `Blue/Orange/Red/Green/Sky/Grey` `:404`. 24dp, 작은 것 20dp (`pill_metrics` `:443`) |
| `PickChip`, `FilterChip` | `:613`, `:908` | 선택 칩 |
| `EmberCard`, `EmberCardSized`, `InsetPanel` | `:656`, `:670`, `:707` | 카드, 안쪽 패널 |
| `Select`, `OptionSheet`, `MenuRow` | `:191`, `:154`, `:134` | 선택, 목록 시트 |
| `EmberSheet(title, open, on_dismiss, actions, content)`, `EmberSheetSized`, `SheetHeader`, `SheetFooter`, `CloseButton` | `:847`, `:860`, `:823`, `:229`, `:807` | 모달. 폭 `SHEET_WIDTH_DEFAULT 760`, `SHEET_WIDTH_MONITOR 1360` (`:739-742`). <560dp는 바텀시트(높이 85%), 그 외 다이얼로그(창 높이-32) (`:760-790`) |
| `SearchField(placeholder, height, on_change)` | `:966` | 돋보기가 붙은 검색 필드 (높이 36 컴팩트 `:930`) |
| `TrackBar` | `:470` | 진행 막대 |

`PillTone`은 `crate::ui::components::PillTone`에서 `From`으로 변환된다 (`:415-416`). `ember/app/src/ui/components.rs`의 `button_style`, `pill_colors` 같은 스타일 함수와 이름이 같다 (`:1-2` 주석). 컴포넌트 안에서 `compose_rust` 호출을 한 파일에 모으려는 의도다 (`:5-6`). 알려진 갭 주석 18개: #372, #443, #444 등 (`TODO` 18).

## 4. `ko.rs` 문구 표 (192줄)

`model`은 영어를 돌려주고 Dioxus 화면과 그 테스트가 그것에 의존하므로, cr 화면은 같은 값에서 한국어로 매핑하는 표를 따로 둔다 (`ko.rs:1-3`). 소비자는 `compat.rs`(3곳), `conversation.rs`(8곳), `launcher.rs`(2곳)뿐이다 (`grep "ko::"`). 즉 화면 문구 대부분은 `ko.rs`가 아니라 각 파일 안에 하드코딩이다 (아래 "동작 지도"가 그 위치를 적는다). 주요 항목:

| 항목 | 줄 | 값 |
|---|---|---|
| `status_label(LauncherStatus)` | `:11-20` | 대기 중, 실행 중, 승인 대기, 읽지 않음, 완료, 실패, 알 수 없음 |
| `reachability_label` | `:22-28` | 온라인, 오프라인, 확인 중... |
| `approve_all_banner(on)` | `:32-34` | "모든 요청 자동 승인이 켜져 있습니다: 이 세션의 도구 요청을 묻지 않고 허용합니다." |
| `approve_all_menu_label` | `:37-39` | "도구 실행 전 다시 묻기" / "모두 자동 승인" |
| `FORK_MENU_LABEL`, `FORK_TURN_LABEL` | `:42`, `:45` | "마지막 턴에서 포크", "여기서 포크" |
| `fork_origin_label` | `:49-52` | "{부모}에서 포크됨" |
| `task_status_label`, `task_line` | `:56-75` | 열림, 진행 중, 차단됨, 완료, 취소됨, 알 수 없음; `#3 [진행 중] 제목 · 담당` (미배정, 팀원) |
| `team_member_rows` | `:80-120` | 팀 패널 행 (리더 우선, 종료 팀원 뒤) |
| `relative_time` | `:122-133` | 방금, N분, N시간, N일, N주 |
| `connection_banner(&ConnectionState)` | `:136-148` | "오프라인: 저장된 데이터를 보여주는 중입니다", "메인 서버에 연결하는 중입니다...", "연결이 끊어졌습니다({error}). N초 후 다시 시도합니다" |

## 동작 지도

공통: 서버 호출은 `run_shared(async, then)` (`ember/app/src/services.rs:253`)이 tokio 워커에서 돌리고 `then`이 `MutableState`를 쓴다. `services().client.api()`는 [client](client.md)의 `Api`(경로는 그 문서 표)이고, `services().server`는 `ember/app/src/server.rs`의 직접 reqwest 래퍼, 데모(`services().demo`)는 서버를 부르지 않고 `demo.rs`를 쓴다. 사용자에게 보이는 토스트는 `notice::post` (`notice.rs:19`).

### 셸 (`shell.rs`)

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

### 홈 (`home.rs`)

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

### 채널 (`channels.rs`, `new_channel.rs`, `channel_owner.rs`)

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

### 검색 (`search.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 검색창 입력 | 제목 "전체 검색", placeholder "세션 검색", 안내 "모든 대화의 메시지와 제목, 프로젝트, 에이전트, 계정, 폴더를 검색합니다.", "검색 중...", "결과 {N}건", "일치하는 항목이 없습니다.", 구역 "프로젝트" | `on_change` `search.rs:73-122` (250ms 디바운스, 낡은 응답 폐기 `superseded`) | `client.search(q, Some(100))` (`GET /search?q=&limit=100`); 데모는 호출 대신 한 번 "사용 불가" 안내 (`demo_blocked`) |
| 결과 행 클릭 | 세션 행 | `SessionRowView` `launcher.rs:91` -> `open_conversation` `:25` | 없음 |
| 검색 실패 | "메시지 검색에 실패했습니다: {e}. 제목 일치만 보여줍니다." `:165` | - | - |

### 세션 행과 새 세션 (`launcher.rs`, `new_session.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 행 메뉴 | "고정"/"고정 해제", "이름 변경", "보관"/"보관 해제", "내보내기"; 뱃지 "고정됨"; 계정 없으면 "서버 로그인" | `SessionRowWith` `launcher.rs:96-` (`:149`, `:64-72`) | `patch_session` -> `services.patch_session` (`PATCH /sessions/{id}`) |
| 이름 변경 | 시트 "세션 이름 변경", 버튼 "취소"/"변경" | `rename` `:238` (빈 제목이면 아무 일 없음) | 같음 |
| 내보내기 | 토스트 "내보냈습니다: {경로}" | `export` `:246` | `crate::export::export_session` (로컬 파일 쓰기; 데모는 막힘) |
| 연결 배너 재시도 | "다시 시도" | `ConnectionBannerView` `:41-` | `ember_client` 재연결 `[확인 필요: 호출 대상은 launcher.rs:58 본문]` |
| 새 세션 열기 | 시트 "새 세션"; 필드 "프로젝트"(옵션 "새 프로젝트..." + 이름 입력 "프로젝트 이름"), "컴퓨터의 폴더", "모델 (선택)"(placeholder "에이전트 기본값"), "제목 (선택)"(placeholder "새 대화"), "에이전트", "계정"(옵션 "자동 (서버 라우터가 고름)", "(기본)", "한도 도달"), "컴퓨터"(옵션 "메인 서버 (기본)") | `NewSessionDialog` `:41`, `NewSessionForm` `:82`, 옵션은 `GET /agents`, `/accounts`, `/computers`(헤더 주석 `:1-3`) | `[확인 필요]` 옵션 로딩 호출 위치: 같은 파일 `:125-200` |
| "만들기" | 버튼 "취소"/"만들기" | `start` `new_session.rs:215-262` | `create_session`(`POST /sessions`) -> 필요 시 `server.switch_computer`(`PUT /sessions/{id}/computer`) -> `open_conversation`; `prefs.last_used[project]` 갱신 |

### 설정 (`settings.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 테마 칩 | 구역 "화면 테마" / "앱 전체의 색상 모드를 선택합니다."; 칩 "시스템", "라이트", "다크" | `settings.rs:110-121` -> `set_theme_pref` | `prefs` 저장 |
| 단축키 체계, 표 | "에디터 단축키" / "Ember 에디터의 기본 단축키 체계를 선택합니다."; 토글 "단축키 표 보기"/"단축키 표 접기" | `update_prefs(|pr| pr.keymap = km)` `:131` | `prefs` 저장 |
| 기본 IDE | "기본 IDE" / "프로젝트나 세션에서 IDE 열기를 눌렀을 때 기본으로 실행할 대상입니다."; 칩 "매번 선택", "Ember 에디터" + 설치된 IDE | `update_prefs(|pr| pr.ide_target = v)` `:167-169` | `prefs` 저장 |
| 보관 표시 | "세션 목록" / "보관 처리된 이전 세션을 목록에 함께 표시합니다."; "보관된 세션 표시" + pill "켜짐"/"꺼짐" | `u.set_show_archived(!show_archived)` `:192` | 없음 |
| 서버, 경로 표시 | "연결 및 저장소": "메인 서버"({server_url}), "데이터 경로"(경로 또는 "메모리 전용"); 닫기 "닫기" | `settings.rs:221-228` | 없음 |

### 프로젝트 화면의 시트들 (호출은 제외된 `project.rs`)

| 사용자 동작 | 화면 문구(원문) | 핸들러 | 호출 API |
|---|---|---|---|
| 컴퓨터 추가 | 시트 "컴퓨터 추가"; "새 컴퓨터 추가", "컴퓨터 이름", "예: 연구실 컴퓨터", "코드 만들기"/"만드는 중", "기기를 불러오는 중입니다", "예시"; 대기 "다른 컴퓨터에서 아래 명령을 실행하면 이 화면에 요청이 표시됩니다", "코드는 한 번만 표시되며 한 번 쓰면 무효가 됩니다" (전체 문구는 `ember/app/src/ui/enrol_flow.rs:22-81`) | `mint` `add_computer.rs:242`, `fetch_status` `:278`, `apply_poll` `:289` | `hub_devices()`, `enrol_mint(name)` (`POST /computers/enrol-codes`), `enrol_status(id)` (`GET /computers/enrol-codes/{id}`) 폴링 |
| 확인 카드 | "이 기기를 컴퓨터로 추가합니다. 추가한 컴퓨터는 서버 사용자와 같은 권한으로 쓰입니다", "기기가 보고한 이름", "관측 주소", "시스템", 버튼 "확인하고 추가"/"추가하는 중", "거부" | `confirm` `:315`, `deny` `:355` | `enrol_confirm(id, name, fingerprint)` (`POST .../confirm`), `enrol_deny` (`POST .../deny`); 시트 닫을 때 `enrol_cancel` (`DELETE`) `:223` |
| 결과 | "컴퓨터가 추가되었습니다" + "이제 프로젝트의 컴퓨터 목록에서 고를 수 있습니다", "새 코드 만들기", 토스트 "컴퓨터를 추가했습니다" | `Outcome` `:651` | `refresh_computers` `:303` |
| 컴퓨터 모니터 | 제목 컴퓨터 이름 또는 "컴퓨터"; 카드 "상태", 프로세스 표 "이름 (N)"/"메모리"/"전력", 오프라인 "마지막 연결 시각은 아직 알 수 없습니다. 아래는 마지막으로 받은 값입니다.", 실패 "지표를 읽지 못했습니다", "컴퓨터를 찾을 수 없습니다", "할당된 프로젝트가 없습니다", "이 컴퓨터에서 실행 중인 팀원이 없습니다", "(리더)" | `MonitorSheet` `monitor.rs:89`, 정렬 헤더 클릭 `ProcessTable` `:404` | `client.api().metrics(id, TOP_PROCESSES)` (`GET /computers/{id}/metrics?top=`) 를 `POLL_SECS`마다 |
| 팀 캐릭터 화면 | "팀 캐릭터", "뒤로", "팀 미리보기", "미리보기" 뱃지, "이 프로젝트에 적용"/"저장 중", "편집기", 필드 "이름", "하네스", "역할", "스타일", "실루엣 고정", "상태" | `CharactersScreen` `characters_screen.rs:140`, `apply_style` `:31` | `client.patch_project(project, {character_style})` (`PATCH /projects/{name}`), 성공 후 `prefs.set_character_style` |

### 사용자에게 보이는 에러 메시지 (주요)

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

## 5. 파일별 `crate::ui::<module>` import

(`use` 줄 기준. `ui::coexist::shared_ui`는 `ui.route/menu/prefs/live` 같은 공유 상태에 접근한다. `use super::...`는 cr 내부이므로 표에서 뺐다.)

| 파일 | 가져오는 `crate::ui::*` 항목 | 비고 |
|---|---|---|
| `a11y.rs` | 없음 | 상수만 |
| `add_computer.rs` | `ui::add_computer::*`, `ui::enrol_flow::{self as flow, CommandView, ConfirmRows, EnrolView, RunGuard, Stage}` | 이름이 같은 Dioxus 모듈의 판단 로직 |
| `channel_owner.rs` | `ui::channel_owner::{capped_note, clears_sheet_state, create_label, create_runs, door_status, error_message, guest_rows, invite_rows}` | |
| `channels.rs` | `ui::channels::{...}`(`pub use` 20여 개 `:24-29`), `ui::project::{display_name, harness_tone}`, `ui::characters::seed_hash` | 방, 말풍선 로직은 전부 원본에 있음 |
| `characters.rs` | `ui::characters::{CharSpec, CharState, CharStyle, Family, crown_shown, family_of, svg}`(`pub use`), `ui::coexist::shared_ui`, `ui::project::effective_style` | |
| `characters_screen.rs` | `ui::characters::{characters_project, harness_label, state_label, style_apply_needed, supports_pin, team_cols, team_preview, with_topic, EDITOR_HARNESSES, EDITOR_ROLES, SILHOUETTES}`, `ui::coexist::shared_ui`, `ui::project::{project_boxes, effective_style, patch_error_message}` | |
| `compat.rs` | `ui::cr::ko::status_label` (`:229`, 테스트), `crate::model::Tone` | |
| `components.rs` | `ui::components::PillTone`(`:416`), `ui::shell::{NavBadge, NavMenu}` (테스트 `:1436`) | 본체는 `crate::ui`를 거의 안 씀 |
| `gallery.rs` | `ui::coexist::shared_ui`, `ui::fonts::app_theme` | |
| `home.rs` | `ui::home::{...}`(`pub use` 80여 개 `:17-24`, `model_*` `:25`), `ui::coexist::{shared_ui, SharedUi}`, `ui::usage`, `ui::shell::{NavMenu, ShellMode, DEMO_USER}` | `crate::model`, `crate::prefs`, `crate::server`도 사용 |
| `ko.rs` | 없음 (`crate::model::{TeamMemberRow, Tone}`, `ember_client`) | |
| `launcher.rs` | `ui::coexist::shared_ui` | |
| `monitor.rs` | `ui::monitor::{...}`(`pub use` `:18`, `use` `:23-27`), `ui::coexist::shared_ui`, `ui::components::PillTone`(테스트), `ui::project::{display_name, reach_pill, ComputerChip, ProjectBox, computer_chips, project_boxes, SOON}`, `ui::Route` | |
| `new_channel.rs` | `ui::channels::{agent_choices, create_error_text, default_new_project, AgentChoice, NewChannelDraft, Room, DEMO_NO_CREATE, new_channel_review_hook, room_from, rooms_from}`, `ui::project::{display_name, CloseAction, SettingsGuard, DISCARD_QUESTION}` | |
| `new_session.rs` | `ui::coexist::shared_ui` | |
| `notice.rs` | `ui::coexist::shared_ui` | |
| `search.rs` | `ui::coexist::shared_ui` | |
| `settings.rs` | `ui::coexist::shared_ui`, `ui::keymap::{Action, Keymap, Os}` | `crate::ide::IdeKind` |
| `shell.rs` | `ui::shell::{...}`(`pub use` `:30-35`), `ui::coexist::{shared_ui, SharedUi}`, `ui::Route`, `ui::shell::mark_svg_for`(`:255`), `ui::safe_area::{sidebar_top_inset, safe_area, top_reservation}`, `ui::fonts::app_theme`(`:840`) | |
| `theme.rs` | `ui::theme::{Scheme, ThemePref}`(`pub use` `:22`), `ui::cr::{components, session}`(테스트 `:675`, `:690`) | `fonts.rs`가 거꾸로 이 파일에서 `LIGHT`, `DARK`를 가져옴 |

`cr/` 안의 의존 방향: `theme`는 최하층, `components`/`compat`/`notice`가 그 위, 화면과 시트가 그 위. 주의할 역참조는 `channel_owner -> home::text_px`, `channel_owner -> project::wrap_lines`, `channels -> project`(제외된 파일이 이 모듈을 쓰는데 이 모듈이 다시 `ui::project`를 씀, Dioxus `ui::project`와 cr `project.rs`는 다른 파일), `monitor -> characters`, `new_channel -> channels::Feed`, `home -> shell::{self, NavIcon}`.

## 데이터와 설정

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_CR_SHELL` | `shell.rs:747` | 초기 테마(`light`, `dark`, `1`; `0`, 빈 값은 끔). `lib.rs:143`이 `unwrap_or(저장된 설정)`로 사용 | 저장된 `initial_prefs.theme` |
| `EMBER_CR_SIZE` | `shell.rs:756` | 창 크기 `WxH` (검토용) | `1440x900` |
| `EMBER_CR_ROUTE` | `shell.rs:785` | 시작 화면 직접 열기 (1.3절), 채널, 모니터, 채널 소유자, 새 채널도 읽음 (`channels.rs:210`, `launcher.rs`, `monitor.rs`, `new_channel.rs`, `channel_owner.rs`) | 없음 |
| `EMBER_CR_GALLERY` | `gallery.rs:19` | 컴포넌트 갤러리 창 | 없음 |
| `EMBER_CR_HOME_PICK/MODE/SUGGEST`, `EMBER_CR_SCROLL` | `home.rs:429-466, 573` | 홈 검토 캡처 훅 | 없음 |
| `EMBER_CR_QUERY` | `search.rs:66` | 검색창 초기 값 | 빈 값 |
| `EMBER_CR_ROOM`, `EMBER_CR_NEWCHANNEL`, `EMBER_CR_OWNER_SHEET/DOOR`, `EMBER_CR_COMPUTER`, `EMBER_CR_PROJECT_SHEET` | `channels.rs`, `new_channel.rs`, `channel_owner.rs`, `monitor.rs`, `add_computer.rs` | 시트 검토용 | 없음 |
| `EMBER_DEMO_DATA` 등 데모 | `crate::demo::active_from_env` (`shell.rs:325-327`) | 사이드바 데모 도구 표시, 모니터 샘플 | 꺼짐 |

- 저장 파일: 이 모듈이 직접 쓰는 파일은 없다. 환경설정은 `ui.update_prefs`/`set_theme_pref`/`set_show_archived` -> `save_prefs`(`ember/app/src/services.rs:~262`)가 `config.prefs_path()`에 쓴다. 내보내기는 `config.export_dir()` (`launcher.rs:250`).
- DB: 없음. 서버/노드 API만 사용 (라우트는 동작 지도).
- 정적 자산: `ember/app/assets/nav/*.svg`(메뉴, 채널방 모티브 6종 `channels.rs:387-392`, 모니터 아이콘), `assets/brand/*.svg`(`ui/shell.rs:~303`).
- 외부 연동: GitHub 요약(서버 `gh` 경유, 토큰 미저장), 메인 서버 REST, 허브 기기 목록.

## 이 모듈을 수정할 때 주의할 점

- 메뉴 추가나 이름 변경은 `ember/app/src/ui/shell.rs`(`NavMenu`, `screen_for`, `BOTTOM_TABS`, `MORE_MENUS`)와 `cr/shell.rs:638-672` 사슬, `choose`를 함께 고친다. `ui/shell.rs`의 테스트가 라벨 순서를 고정한다.
- 토큰(색, 간격, 반경)은 `cr/theme.rs`와 `ui/theme.rs`를 같이 (3.2절). `cr::theme::{LIGHT, DARK}`는 `fonts.rs` 툴킷 팔레트의 원천이라 한 곳만 바꿔도 툴킷 기본 위젯 색이 변한다.
- 화면 문구는 대부분 파일 안 하드코딩이거나 `ui::home`, `ui::enrol_flow`, `ui::channels` 같은 원본 상수다. 원본 상수를 고치면 Dioxus 쪽 테스트가 같이 깨질 수 있다. 문구를 한 곳에서 바꾸려면 `ko.rs`는 일부(상태, 포크, 연결 배너)만 덮는다는 점을 감안한다.
- phase 8 삭제 계획: 원본 `ui/*.rs`를 지우면 이 모듈이 `pub use crate::ui::<module>::{...}`로 가져오는 판단 함수와 `Scheme`/`ThemePref`를 `cr/`로 옮겨야 한다 (`shell.rs:5-7`, `theme.rs:19-21` 주석).
- 순서 의존: `notice::NoticeHost`는 `shell()` 첫 줄에서 한 번만 마운트돼야 한다 (`shell.rs:601`). `SettingsSheet`와 `NewSessionDialog`는 셸 끝에 항상 마운트된다 (`:738-739`): 다른 곳에서 중복 마운트하지 않는다.
- `services()`가 없는 테스트는 `ember_theme()`이 기본(System=라이트)로 그린다 (`theme.rs:388-396`). 테스트에서 `shared_ui()`를 쓰려면 `services::test_guard()`가 필요하다 (`notice.rs:44`).
- 폴링 효과(`channels::follow`, `monitor::MonitorSheet`)는 `launched_effect` 키가 바뀌거나 컴포지션에서 빠지면 취소된다. 키를 바꾸지 않는 리팩터링이 안전하다.
- 빌드 금지 규칙에 따라 이 문서는 코드를 컴파일하거나 실행하지 않고 작성했다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 하드코딩 | 중간 | `ember/app/src/ui/cr/shell.rs:285`, `home.rs:1073-1074`, `ember/app/src/ui/shell.rs` (`DEMO_USER = ("BREW","ncmnd")`) | 실제 서버에 연결해도 사이드바 사용자 행과 홈 인사말이 데모 사용자 이름 "BREW"를 그린다. 주석은 "mockup greets the signed-in user by name" (`home.rs:1072`) | 로그인한 사용자 이름이 있는 곳에서 읽거나, 데모가 아니면 이름 없는 인사로 |
| 중복 | 중간 | `cr/theme.rs`와 `ember/app/src/ui/theme.rs` | 팔레트, 타입, 간격 토큰이 두 벌 (3.2절), 테스트가 각각 고정 | phase 8까지 같이 수정하는 체크리스트 유지, 삭제 후 한 벌로 |
| 기능 갭 | 낮음 | `cr/theme.rs:29-31` | `system_scheme()`이 항상 라이트: "시스템" 선택이 OS 다크를 따르지 않음 (compose-rust#97) | 툴킷 훅 대기 |
| 접근성 | 중간 | `cr/a11y.rs:1-8`, 사용처 `project.rs`뿐 | 아이콘 전용 버튼(테마, 설정, 메뉴, 멤버, 첨부, 이모지 등)에 접근성 이름이 없다 (compose-rust#460). 상수는 12개이나 쓰이는 것은 2개, `rail_labels()`는 테스트에서만 호출 | 툴킷이 라벨 modifier를 지원하면 일괄 적용 |
| 죽은 코드 | 낮음 | `cr/a11y.rs:11-22` 중 `THEME`, `SETTINGS`, `PLATFORM`, `MENU`, `NEW_CHANNEL`, `MEMBERS`, `MORE`, `ATTACH`, `EMOJI`, `OPEN_SESSION` | `grep a11y::`로 `cr/` 안 사용처가 `VERSION_CONTROL`, `PROJECT_SETTINGS` 외에 없다 | 적용 전까지 유지 또는 삭제 `[확인 필요: 테스트 외 사용]` |
| 문구 분산 | 낮음 | `ko.rs`가 소비자 13곳(`compat`, `conversation`, `launcher`)뿐 | 문구가 파일 인라인, `ui::*` 상수, `ko.rs`에 흩어져 번역, 교정 시 누락 위험. `model`의 영어 원문이 남아 있다 (`ko.rs:1-3`) | phase 8에서 `model`을 한국어로 바꾸고 `ko.rs` 흡수 |
| 거대 파일 | 낮음 | `home.rs` 2503줄, `components.rs` 1471줄, `shell.rs` 1063줄 (테스트 포함) | `home.rs`는 작성기, 모델 선택기, 대시보드 8개 타일, 연동 영역이 한 파일 | 작성기와 대시보드로 분리 |
| 검토 훅 | 낮음 | `home.rs:429-466,573`, `channels.rs:210,~240`, `channel_owner.rs:138-150`, `monitor.rs`, `new_channel.rs:80-90`, `search.rs:66`, `shell.rs:785-837` | 프로덕션 코드가 `EMBER_CR_*` 환경 변수로 동작을 바꾼다 (`channel_owner`는 "리뷰 변수 없으면 샘플 안 샌다" 테스트 있음 `:709`) | 문서화 완료(데이터 절). 릴리스 빌드에서 `cfg`로 제거 검토 |
| TODO | 낮음 | `grep -c "TODO"`: `components.rs` 18, `home.rs` 19, `channels.rs` 11, `compat.rs` 6, `theme.rs` 4, `shell.rs` 3, `monitor.rs` 3, `characters_screen.rs` 3, `channel_owner.rs` 3, `new_channel.rs` 2, 그 외 파일 각 1 (`a11y`, `notice`, `launcher`, `add_computer`, `new_session`) | 대부분 compose-rust 이슈(#374, #384, #428-429, #443-446, #460)에 묶인 툴킷 갭. 합계 약 76 | 툴킷 업그레이드 때 재검토 |
| 보안 | 낮음 | `add_computer.rs:5-6`, `channel_owner.rs:6-8` | 코드와 초대 링크를 시트 상태에만 보관하고 로그, 저장하지 않는 설계 (좋은 점). 비밀값을 이 문서에 기록하지 않았다 | 변경 시 `tracing`에 값이 새지 않도록 유지 |
| 정확성 | 낮음 | `cr/shell.rs:69-89`와 `Route::Search` | 검색 중 다른 메뉴를 고르면 `Route::Search`가 남아 `screen_for`가 그 메뉴 화면을 그리지만 라우트는 `Search`인 채다. 이후 프로젝트로 돌아오면 검색이 다시 보임 | 의도 확인 `[확인 필요]` |
| 메모리 | 낮음 | `shell.rs:98-125`, `characters.rs:27-38` | SVG 문서를 `'static`으로 leak해 캐시: 색, 크기 조합이 늘수록 영구 증가 (테마 전환, 아이콘 크기 수 만큼으로 유한) | 현재 규모에서는 허용 |
