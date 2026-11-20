# 모듈: app-ui-cr-work

- 경로: `ember/app/src/ui/cr/files.rs`, `routines.rs`, `agents.rs`, `vcs.rs` (기본 실행 경로 `ui::cr::shell::launch`의 화면 네 개)
- 규모: 파일 4개 / 약 15,191줄 (files 1,978, routines 3,532, agents 3,471, vcs 6,210). 각 파일의 `#[cfg(test)]` 블록이 절반 가까이 차지한다 (테스트 `#[test]` 수: files 17, routines 59, agents 48, vcs 74).
- 레이어: UI (compose-rust 그리기와 오케스트레이션). 결정 로직과 API 호출은 Dioxus 쪽 `ui/<이름>.rs`에 있다.
- 한 줄 책임: 파일, 루틴(서버 `schedules`), 에이전트(CLI 감지, 계정, 하네스 설정), 버전 관리(노드 `/git/*`) 화면을 그리고 사용자 동작을 서버와 노드 호출로 잇는다.
- 의존하는 모듈: [app-ui-cr](app-ui-cr.md) (`components`, `theme`, `notice`, `home`, `project`, `shell`), [app-core](app-core.md) (`services`, `bridge`, `demo`, `server`), [client](client.md) (`Api`), `crate::ui::{files,routines,agents,vcs,home,usage,coexist}` (Dioxus 쪽 순수 로직 모듈)
- 이 모듈을 쓰는 모듈: `ember/app/src/ui/cr/shell.rs:651,655,657,659` (`FilesScreen`, `VcsScreen`, `AgentsScreen`, `RoutinesScreen`), `ember/app/src/ui/cr/session.rs:4902` (`VcsSheet`)

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `FilesScreen` / `FilesScreenWith` | fn | `ember/app/src/ui/cr/files.rs:379,393` | 파일 화면. 전송 서비스가 없어 장비 목록만 실제 값이다 |
| `RoutinesScreen` / `RoutinesScreenWith` | fn | `ember/app/src/ui/cr/routines.rs:419,489` | 루틴 화면 |
| `load_remote`, `apply_load`, `is_remote`, `with_store`, `with_remote` | fn | `ember/app/src/ui/cr/routines.rs:203,217,198,70,188` | 서버 스케줄 읽기와 기기 보관소 |
| `AgentsScreen` / `AgentsScreenWith` | fn | `ember/app/src/ui/cr/agents.rs:249,306` | 에이전트 화면 (섹션 5개) |
| `sync_from_server` | fn | `ember/app/src/ui/cr/agents.rs:76` | 서버 기본값과 설정을 로컬 저장소에 반영. 호출처 `ember/app/src/bridge.rs:528` |
| `VcsScreen` / `VcsScreenWith` / `VcsSheet` | fn | `ember/app/src/ui/cr/vcs.rs:4197,4236,4436` | 버전 관리 화면과, 대화 화면에 뜨는 시트 |
| `open_for_project_cr` | fn | `ember/app/src/ui/cr/vcs.rs:48` | 프로젝트를 고르고 버전 관리 메뉴로 이동 |
| `sample_*`, `preview` | fn | 각 파일 | 검토 캡처용 표본 (`EMBER_CR_ROUTE`, `EMBER_CR_*_SAMPLE`) |

## 파일별 요약

### `ember/app/src/ui/cr/files.rs` (약 1,978줄, 본문 1,615줄 + 테스트)
- 목적: 장비 사이 파일 전송 화면 (FR-L27). 전송 기능은 서버와 노드 API가 아직 없다(FR-F Draft). 그래서 장비는 `services().client`의 컴퓨터 목록으로 실제 값을 그리고, 나머지는 "준비 중입니다"(`ember/app/src/ui/files.rs:28` `UNAVAILABLE`)를 보여 준다 (`ember/app/src/ui/cr/files.rs:5-8`).
- 가져오는 것 (`crate::ui::files`, `ui/cr/files.rs:28-33`): `pub use` 61개(모델 `FilesModel` `Device` `Offer` `Transfer`, 서비스 `TransferService` `transfer_service`, 결정 함수 `build_model` `answer_offer` `send_blocker` `user_actions`, 상수 `UNAVAILABLE` `FILE_PICK_UNAVAILABLE` `SHARE_NOTE` 등)와 `choose_target` `files_line` 등 8개. `crate::ui::home::{crew, CrewMember}`, `crate::ui::coexist::shared_ui`도 쓴다. 이 파일이 가장 얇은 래퍼다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `State` | struct | 357 | 화면 상태: 보내기 시트 `SendDraft`, 응답한 제안 id, 기록 필터, 장비 필터, 갱신 카운터 |
| `FilesScreen` | fn | 379 | `build_model(&computers, svc)`와 `svc.pending_offers()`로 모델을 만들고 `FilesScreenWith` 호출 |
| `FilesScreenWith` | fn | 393 | 헤더, KPI 4칸, `Stage`, 전송 중과 받은 파일 카드, 기록 카드, 제안 카드, 시트 둘을 조립 |
| `Stage` | fn | 674 | 장비 타일(`DeviceTile` 815), 에이전트 타일(`AgentTile` 877), "보낼 파일" 트레이 |
| `OfferCard` | fn | 928 | 들어온 제안을 오른쪽 위에 띄우는 카드 (거절, 받기) |
| `TransferRow` | fn | 1061 | 전송 한 줄과 일시정지, 재개, 취소 버튼 |
| `SendSheet` | fn | 1327 | "파일 보내기" 시트 (받는 곳 고르기, 파일, 보내기) |
| `ShareSheet` | fn | 1499 | "공유 시트" (장비, 에이전트, 준비 중 동작 3개) |
| `kpi_cells`, `KpiCell` | fn | 551, 539 | KPI 네 칸. `ui::files::kpis`와 따로 만든다 (이슈 후보 참고) |
| `sample_model`, `sample_extras` | fn | 309, 338 | `EMBER_CR_FILES_SAMPLE=1` 표본 |

- 부수효과: `svc.control`(1105), `svc.send`(1443)만 서비스를 바꾼다. 기본 구현 `NoTransferService`는 `send`에서 `Err(UNAVAILABLE)`을 돌려 주고 `control`은 아무 일도 하지 않는다 (`ember/app/src/ui/files.rs:608-615`). 네트워크 호출은 없다.
- 환경 변수: `EMBER_CR_FILES_SAMPLE`(표본), `EMBER_CR_FILES_SHEET=send|share`(시트를 열어 둔 채 시작, `files.rs:360,411`).
- 주의점: `FILE_PICKER_AVAILABLE`이 `false`라서 파일 고르기는 데모에서만 동작한다 (`ember/app/src/ui/files.rs:51`, `ember/app/src/ui/cr/files.rs:780-790`). 드래그와 파일 선택기는 없다(#166 우회).

### `ember/app/src/ui/cr/routines.rs` (약 3,532줄, 본문 2,375줄 + 테스트 약 1,150줄)
- 목적: 루틴 대시보드(KPI, 성공률 링, 요일별 막대), 프로젝트별 목록, 상세 패널, 만들기와 편집 폼 (FR-L25).
- 가져오는 것: `crate::ui::routines`의 `pub use` 79개(cron 해석 `cron_valid` `describe_cron`, 달력 `civil_from_days`, 묶기 `group_by_project`, 서버 매핑 `schedule_to_entry` `new_schedule` `schedule_patch` `changed_patch`, 데모 실행 `begin_demo_run` `finish_demo_run`, 저장소 `LocalStore` `RoutineStore`, 폼 `FormDraft` `Leave`, 상수 `OFFLINE_NOTE` `LOCAL_NOTE` `SAMPLE_FLAG`)와 `crate::ui::home`(`harness_block` `model_catalog` `modes_for` 등 8개).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `RoutinesScreen` | fn | 419 | 표본이면 `sample_entries()` 병합, 아니면 `refresh`로 서버를 읽고 `with_remote`와 `with_store`를 합쳐 `RoutinesScreenWith`에 넘김 |
| `RoutinesScreenWith` | fn | 489 | 상태 소유, `on_toggle`(574) `on_run_now`(608) `on_save`(649) 클로저, 레이아웃(목록 폭 `list_pane_width` 344, 상세 폭 `detail_panel_width` 374) |
| `Remote`, `with_remote` | struct, fn | 178, 188 | 서버 스케줄 캐시 `{online, entries}` (전역 `OnceLock<Mutex<_>>`) |
| `load_remote` | async fn | 203 | `api.schedules(None)` 후 스케줄마다 `api.schedule_runs(id, Some(20))` |
| `remote_action` | fn | 246 | 서버 호출 뒤 `load_remote`를 다시 불러 캐시 갱신, 실패는 알림 |
| `demo_run` | fn | 99 | 데모의 가짜 실행 (`begin_demo_run` 후 `launched_effect`성 타이머로 `finish_demo_run`) |
| `ListPane` / `RoutineRow` | fn | 1334 / 1414 | 필터 알약, 검색, 프로젝트 묶음, 켜기/끄기 스위치 `RoutineSwitch`(1102) |
| `DetailPane` | fn | 1519 | 이름, 다음 실행, `편집`, `지금 실행`, 값 타일, 프롬프트, 실행 기록 `RunTile`(1803) |
| `RoutineForm` / `FormFields` | fn | 1865 / 1957 | 만들기와 편집 폼 (이름, 프로젝트, 트리거, cron 또는 이벤트, 하네스, 모델, 권한, 컴퓨터, 프롬프트) |
| `sample_entries` | fn | 2178 | 표본 루틴 7개 (한국어 이름과 프롬프트 포함) |

- 부수효과: 서버 스케줄 생성, 수정, 일시정지, 재개, 즉시 실행(아래 동작 지도). 서버에 닿지 않거나 이벤트 트리거면 `LocalStore`(앱 실행 동안만 메모리, `ember/app/src/ui/routines.rs:853-857`)에 보관한다. 서버 스케줄 삭제 UI는 없다(`delete` 문자열 없음, grep 확인).
- 주의점: 서버가 이름과 일부 필드를 바꾸지 못해 `changed_patch`가 프롬프트와 일정만 보낸다 (`routines.rs:655-670`, `ember/app/src/ui/routines.rs:1066-1067`). 생성은 프로젝트의 마지막 `cwd`가 필요하다(`crate::model::latest_cwd`, `routines.rs:675-681`).

### `ember/app/src/ui/cr/agents.rs` (약 3,471줄, 본문 2,747줄 + 테스트)
- 목적: 에이전트 화면 5섹션 (하네스, 모델, 프로필, 네트워크, 사용량; `Section::label` `ember/app/src/ui/agents.rs:47-55`). 에이전트 CLI 감지 결과, 계정, 하네스별 설정, 사용량을 보여 준다. **MCP 설정 UI는 이 화면에 없다** (`mcp` 대소문자 무관 grep 결과 0건, `ui/agents.rs`도 0건).
- 가져오는 것: `crate::ui::agents`에서 `pub use` 44개(`LocalStore` `Profile` `Section` `AgentHarness` `step_threshold` `resolve_profile` 등)와 본문 인라인 경로 약 60곳(`account_error_ko` 5, `server_error_status` 5, `harness_path_text` 4, `kpi_text` 3, `AddAccount` 5, `SheetHook`, `rescan_*`, `pick_rows`, `apply_pick` 등). `crate::ui::agents` 참조는 모두 78번(단어 경계 기준), `crate::ui::` 전체 102번. 그 밖에 `crate::ui::home`(`HarnessBar`, `harness_usage`, `modes_for`, `default_option`, `UNAVAILABLE`), `crate::ui::usage`(`Load`, `SectionModel`, `DayBar`).

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `LOCAL`, `local_load`, `local_save`, `edit` | static, fn | 58, 60, 68, 153 | 설정과 프로필 보관소 (프로세스 전역 `Mutex<Option<LocalStore>>`) |
| `sync_from_server` | fn | 76 | 서버 `AgentDefaults`와 `AgentSettingsResponse`를 보관소에 합치고 `agent_store_rev`를 올림 |
| `save_server_defaults` | fn | 97 | `PUT /api/agents/defaults` (`s.server.put_agent_defaults`, 107) |
| `save_server_mem_limit` | fn | 127 | `PUT /api/agents/{agent}/settings` (`put_agent_mem_limit`, 139) |
| `AgentsLive` | struct | 203 | 감지된 에이전트, 계정, ChatGPT 계정, 기본 계정 id |
| `AgentsScreen` | fn | 249 | `s.ui.live.{accounts,agents,chatgpt,usage_summary}`를 읽어 `AgentsScreenWith` 호출. `bridge::request_usage_summary()`(299) |
| `AgentsScreenWith` | fn | 306 | 섹션 전환, 섹션 본문 분기 (379-383, 400-404) |
| `HarnessSection` / `HarnessCard` | fn | 935 / 1046 | KPI 4개, 하네스 카드 (설치와 버전, 다시 감지, 고정 버전, 기본 프로필, 실행 방식, 샌드박스, 상주 shim, 메모리 한도) |
| `ModelsSection` / `ModelCard` | fn | 1362 / 1648 | 새 팀원 기본값(하네스 선택, 계정 선택), 추론 강도, 권한 모드, 모델 표 |
| `AddAccountSheet` / `create_account` / `check_login` | fn | 1486 / 1581 / 1615 | 계정 추가 흐름 (FR-U1) |
| `ProfilesSection` / `ProfileCard` | fn | 1875 / 2037 | 계정 목록, 하네스별 기본 프로필, 프로필 편집 (모두 로컬 보관소) |
| `NetworkSection` / `ComputerTile` | fn | 2337 / 2429 | API 트래픽 내보내기 안내, 컴퓨터별 상태 |
| `UsageSection` | fn | 2480 | 7일/14일 전환, 오늘 토큰, 계정별 남은 구독량, 토큰 종류, 하네스별 비용 |
| `CLAUDE_SPECS`, `CODEX_SPECS`, `GEMINI_SPECS` | const | 1256, 1277, 1298 | 모델 카탈로그 (이슈 후보 참고) |

- 부수효과: 서버 호출 `accounts`, `set_default_account`, `create_account`, `check_account`, `put_agent_defaults`, `put_agent_mem_limit`, `bridge::rescan_agents`(`detect_harnesses("local")`, `ember/app/src/bridge.rs:345`). 데모(`s.demo.is_some()`)이면 호출하지 않는다 (`agents.rs:104-106,135-137`).
- 주의점: 프로필, 라우팅, 프록시, 샌드박스, 상주 shim, 모델 활성화 같은 설정은 서버에 저장되지 않는 앱 안 보관소뿐이다 (아래 이슈 후보).

### `ember/app/src/ui/cr/vcs.rs` (약 6,210줄, 본문 4,487줄 + 테스트 약 1,700줄)
- 목적: 버전 관리 화면 (FR-L19, D34). 섹션 7개(변경 사항, 히스토리, 브랜치, 풀 리퀘스트, 스태시, 충돌, 팀 작업; `ember/app/src/ui/vcs.rs:43-74`). 이 파일에는 API 호출이 **하나도 없다**. 모든 호출은 `crate::ui::vcs`의 `fetch_*`와 `run_*`(내부는 `git_call` -> `Api::git_raw`)를 부른다.
- 가져오는 것 (`ui/cr/vcs.rs:14-37`): `crate::ui::vcs`에서 약 149개 이름(`pub use` 40여 개 + 한 줄 `use` 약 110개). 대표: 읽기 `fetch_snapshot` `fetch_history` `fetch_prs` `fetch_pr_detail` `fetch_branches` `fetch_stashes` `fetch_conflict` `fetch_merge_state` `fetch_commit_detail`, 쓰기 `run_commit` `run_remote` `run_stash_push` `run_stash_action` `run_commit_revert` `run_commit_cherry_pick` `run_branch_from` `run_resolve` `run_merge_abort` `run_merge_commit` `run_pr_review` `run_pr_merge` `run_pr_create`, 공통 `git_call` `failure_text` `load_from`, 결정 `merge_gate` `plan_staging` `parse_unified` `build_tree` `valid_branch_name`. `crate::ui::vcs` 참조는 13번, `crate::ui::` 전체 25번이고 나머지는 `crate::ui::{project, home::GithubFetch, shell::NavMenu, coexist, Route}`.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Actions` | struct | 55 | 프로젝트 id와 `reload` 카운터. `finish`(61) `remote`(79) `branch`(84) `create_from`(95) `stash_now`(105) |
| `VcsScreen` | fn | 4197 | 프로젝트 고르기(`pick_project`), `launched_effect`로 `fetch_snapshot` 호출 (4219-4230) |
| `VcsScreenWithLoad` | fn | 4246 | 헤더, `RepoBarWithActions`, 섹션 목록 또는 알약, `SectionContent` |
| `VcsSheet` | fn | 4436 | 대화 화면의 시트 (프로젝트 전환 없음, #495) |
| `SectionContent` | fn | 1573 | `(snap, Section)`으로 패널 분기 |
| `RepoBarWithActions` | fn | 612 | 프로젝트 고르기, 브랜치 메뉴(새 브랜치), 원격 버튼 |
| `ChangesPaneWithActions` | fn | 1454 | 파일 트리 `FilesTree`(1114), diff `DiffView`(933), 커밋 상자 `CommitBox`(1305) |
| `ConflictsPane` / `ConflictsBody` | fn | 1642 / 1793 | 충돌 목록, 병합 배너, 충돌 블록 해결 |
| `HistoryPane` | fn | 2384 | 커밋 목록, 상세, revert, cherry-pick, 여기서 브랜치 |
| `PullRequestsPane` | fn | 3105 | PR 목록, 상세, 리뷰, 병합, 새 PR (가장 큰 함수, 약 440줄) |
| `BranchesPane` / `TeamPane` / `StashPane` | fn | 3617 / 3875 / 3974 | 브랜치, 팀 작업(멤버 cwd와 PR), 스태시 |

- 부수효과: 노드의 작업 트리를 바꾼다 (stage, commit, checkout, push, merge 등). 위험 동작은 두 번 눌러야 실행되는 "정말 …" 확인 패턴을 쓴다 (`amend_tap`, `merge_tap`, `stash_tap`, `review_tap`).
- 주의점: 화면에서 만든 문장 일부(`pr_checks_tone`가 문자열 "체크 없음"으로 분기, `vcs.rs:2805`)가 `ui/vcs.rs` 문구에 묶여 있다.

## 동작 지도

공통: 알림은 `ember/app/src/ui/cr/notice.rs`의 `notice::post`로 토스트를 띄운다. 호출 경로는 클라이언트 `Api`(`docs/analysis/modules/client.md`)가 `/api` 접두를 붙인다.

### 파일 (전부 서비스 없음 상태, 서버 호출 없음)

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

### 루틴 (서버 `schedules`)

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

### 에이전트 (감지, 계정, 서버 기본값)

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

### 버전 관리 (노드 `/git/*`)

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

### 사용자에게 보이는 에러 메시지

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

## 데이터와 설정

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_CR_FILES_SAMPLE` | `ember/app/src/ui/files.rs` (`is_demo`) [확인 필요: 읽는 위치는 `is_demo` 쪽] | 파일 화면 표본 | 꺼짐 |
| `EMBER_CR_FILES_SHEET` | `ui/cr/files.rs:360,411` | `send` 또는 `share` 시트 열고 시작 | 없음 |
| `EMBER_CR_ROUTE` (`agents`, `vcs`) | `agents.rs:252`, `vcs.rs:4198` | 검토 캡처용 표본 | 없음 |
| `EMBER_CR_AGENTS_LIVE`, `EMBER_CR_AGENTS_SECTION` | `agents.rs:251,291` | 실제 경로로 열기(디버그 빌드만), 섹션 지정 | 없음 |
| `EMBER_CR_VCS_SECTION` | `vcs.rs:4272` | 섹션 지정 | `changes` |
| `EMBER_AGY_SANDBOX` | `agents.rs:1177` (문구에서만 언급) | Antigravity 샌드박스 | 꺼짐 |
| 전역 저장소 | `routines.rs:64-68` (`LocalStore`), `routines.rs:183` (`Remote`), `agents.rs:58` (`LocalStore`), `vcs.rs:4399` (`VCS_LAST_WINDOW`) | 프로세스 메모리 | 디스크에 저장하지 않음 |
| DB 테이블 | 없음 | - | - |

서버 쪽 데이터: 스케줄은 서버의 `schedules` 모듈, 계정과 기본값은 [server-accounts](server-accounts.md)와 `api/mod.rs`, git은 노드 [node-git](node-git.md).

## 이 모듈을 수정할 때 주의할 점

- 이 네 파일은 "그리기"만 갖는다. 문구 상수, 수 계산, API 호출은 대응하는 `ember/app/src/ui/{files,routines,agents,vcs}.rs`에 있고 Dioxus 화면과 공유한다. 로직을 고치면 두 화면이 함께 바뀐다. cr 쪽 `pub use`가 이름 하나만 바꿔도 깨지므로 이름을 바꿀 때 `cr/*.rs`의 `use` 목록(특히 `vcs.rs:15-16`의 약 110개)을 같이 고친다.
- `ui/vcs.rs`의 `git_call` 본문 모양은 노드 `/git/*` 요청 타입과 맞아야 한다. 타입 있는 `Api::git_*`을 쓰지 않으므로 컴파일러가 어긋남을 잡아 주지 못한다 (client 문서 383줄 참고).
- 루틴 저장 분기 순서가 중요하다: 서버 스케줄 편집, 새 서버 스케줄(시간 트리거이고 온라인이며 `cwd` 있음), 그 밖(로컬)의 순이다 (`routines.rs:649-735`). 이벤트 트리거는 서버가 지원하지 않아 항상 로컬이다.
- `remote_action`은 호출 뒤 `load_remote`로 전체 스케줄과 실행 기록을 다시 읽는다(스케줄 N개면 요청 N+1개). 호출 빈도를 늘리면 부담이 된다.
- 에이전트 화면에서 서버에 저장되는 것은 기본 하네스, 모델, 추론 강도, 권한 모드, 메모리 한도, 기본 계정뿐이다. 나머지를 서버에 올릴 때는 `sync_from_server`와 `LocalStore::to_server_defaults` 양쪽을 맞춘다.
- 위험 동작은 두 번 누르기와 시간 제한으로 막는다 (`AMEND_CONFIRM_DELAY_MS` 600ms `ui/vcs.rs:1203`, `STASH_ARM_TIMEOUT_MS` 4000ms `ui/vcs.rs:2781`). 문구를 바꾸면 접근성 라벨(`FocusOverlay`)도 같이 바꾼다.
- `FocusOverlay`가 `agents.rs:570`, `routines.rs:1087`, `vcs.rs:293`에 각각 정의되어 있다 (이슈 후보).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 중복 상수 | 중간 | `routines.rs:59,60,62` vs `ember/app/src/ui/routines.rs:1041,1042,913` | `RUN_NOTICE`, `NO_CWD_NOTICE`, `RUNS_SHOWN`이 두 모듈에 같은 값으로 정의된다. `ui/routines.rs`는 `pub`, cr 쪽은 `const`. 테스트가 두 문자열을 모두 점검한다 (`routines.rs:3218-3219`) | cr 쪽을 `pub use crate::ui::routines::{RUN_NOTICE, NO_CWD_NOTICE}`로 바꾼다 |
| 중복 데이터 | 중간 | `agents.rs:1249-1310` vs `ember/app/src/ui/home.rs:834-844` (`model_catalog`) | 모델 카탈로그(id, 이름)가 두 군데 있다 (`opus`/"Opus 5.5", `gpt-5-codex`, `gemini-2.5-pro` 등). 에이전트 화면 쪽은 노트와 플랜 정보를 더 가진다. 홈과 화면이 어긋날 수 있다 | `home::model_catalog`를 단일 출처로 하고 플랜 정보만 따로 둔다 |
| 중복 로직 | 낮음 | `files.rs:539-588` `kpi_cells` vs `ember/app/src/ui/files.rs:958-1000` `kpis` | 같은 KPI 4개를 다시 만든다. 라벨이 다르다 ("지금 전송 중" vs "전송 중"). `kpis`는 `pub use`로 가져오지만 이 화면은 쓰지 않는 것으로 보인다 [확인 필요: 호출 여부 grep 필요] | `kpi_cells`가 `kpis`를 감싸도록 정리 |
| 중복 로직 | 낮음 | `files.rs:485` `page_pad`, `agents.rs:326`, `routines.rs:571`, `vcs.rs:4262` | 화면 패딩을 화면마다 `if compact {SP[3]} else {SP[6]}`로 따로 계산한다 (파일 화면만 24 중간 단계 있음) | `super::home::content_width`와 함께 공용 함수로 |
| 중복 정의 | 낮음 | `agents.rs:570`, `routines.rs:1087`, `vcs.rs:293` | `FocusOverlay`가 세 파일에 각각 있다 (같은 이름, 시그니처 거의 같음) | `components`로 옮긴다 |
| 중복 정의 | 낮음 | `routines.rs:313` `status_tone`, `vcs.rs:2241` `status_tone` | 같은 이름의 색 매핑 함수 두 개. 입력 타입은 다르다 | 필요 시 정리 |
| 결합 | 낮음 | `vcs.rs:2805` | `pr_checks_tone`가 문구 "체크 없음" 문자열 비교로 분기한다. `pr_checks_text`(`ui/vcs.rs:1934`)가 바뀌면 조용히 깨진다 | 상태 열거형으로 분기 |
| 중복 문구 | 낮음 | `vcs.rs:405` vs `ember/app/src/ui/vcs.rs:214-216,3028` | 원격 버튼은 "가져오기/내려받기/올리기", 알림과 레이블은 "Fetch/Pull/Push"를 섞어 쓴다 | 한 곳에서 정의 |
| 모순 문구 | 중간 | `ember/app/src/ui/agents.rs:21-22` (`LOCAL_STORE_NOTE`: 서버 저장은 준비 중입니다 (#670)) vs `:1023` (`DEFAULTS_STORAGE_NOTE`: 서버에 저장되어 새 팀원에 적용됩니다) | 기본값은 서버에 저장되고 나머지는 로컬뿐인데, 화면에 로컬 안내를 그리는 `LocalNote`(`agents.rs:829`)는 호출처가 없다 (grep 확인). 사용자는 어떤 설정이 서버에 저장되는지 알 수 없다 | `LocalNote`를 프로필, 샌드박스, shim 행 옆에 다시 붙이거나 삭제한다 |
| 쓰이지 않는 심볼 | 낮음 | `agents.rs:829` `LocalNote` | 호출 0건 (`grep LocalNote`에서 정의만) | 삭제 또는 연결 |
| 모의 동작 | 중간 | `agents.rs:1980,2141,2177,2277` | 프로필 하네스, 고정 계정, 기본 프로필, 실패 시 동작 고르기는 "…을 선택합니다" 알림만 띄우고 아무것도 고르지 못한다. `MockSwitch`(`agents.rs:514`)라는 이름도 목업 흔적이다 | 선택 시트를 구현하거나 버튼을 비활성화하고 "준비 중입니다"로 표시 |
| 가짜 설정 | 중간 | `agents.rs:2353`, `agents.rs:2291-2296` | "작업 중인 컴퓨터로 내보내기" 스위치는 항상 켜진 채 알림만 띄우고, 모델 프록시는 켜면 `http://127.0.0.1:4000`을 저장하지만 서버에 보내지 않고 프록시 서버도 없다 (문구에 명시) | 검증 전까지 비활성 표시 |
| 하드코딩 | 낮음 | `agents.rs:1256-1310`, `ui/agents.rs:791` | 모델 이름, 플랜 가용성, `PINNED_ANTIGRAVITY_VERSION = "1.2.16"`이 코드에 박혀 있다 | 서버 카탈로그 연동 시 제거 |
| 하드코딩 | 낮음 | `files.rs:924` | `DEFAULT_INBOX = "~/Downloads/Ember"` (TODO FR-F8) | 전송 설정에서 읽기 |
| 미구현 기능 | 중간 | `files.rs` 전체, `ember/app/src/ui/files.rs:613` | 전송 서비스가 없어 장비 목록 외에는 데모 전용이다. `send`는 `Err(UNAVAILABLE)` | FR-F 구현 시 `TransferService` 실제 구현 |
| 기능 누락 | 낮음 | `routines.rs` | 서버 스케줄 삭제 UI가 없다. client에는 `delete_schedule`(`api.rs:1317`)이 있으나 app이 부르지 않는다 (client 문서 153줄과 일치) | 삭제 버튼 또는 `delete_schedule` 정리 |
| 기능 누락 | 낮음 | `agents.rs` 전체 | 요청 범위에 있던 MCP 설정 화면은 이 모듈에 없다 | 다른 모듈 확인 [확인 필요] |
| 오류 은닉 | 낮음 | `routines.rs:219-226` | 상태 코드가 있는 서버 오류의 `load_remote` 실패는 `tracing::warn!`만 하고 화면에는 이전 목록이 그대로 남는다 | 알림 한 줄 |
| 비용 | 낮음 | `routines.rs:203-209` | 스케줄마다 실행 기록을 따로 요청한다 (N+1). 조작 한 번마다 전체를 다시 읽는다 | 서버에 묶음 조회 |
| 검증 | 낮음 | `agents.rs:299`, `ui/bridge.rs:402` | 에이전트 화면은 사용량을 14일로만 요청하지만 선택 UI는 7일/14일이다 (`agents.rs:2490`) [확인 필요: 7일은 클라이언트 합산인지] | 확인 후 정리 |
| 보안 | 낮음 | `agents.rs:2294` | 로컬 주소 `http://127.0.0.1:4000` 기본 프록시 값 하드코딩. 비밀값 아님 | 설정값으로 |
| TODO | 낮음 | 개수: files 12, routines 8, agents 8, vcs 15 (`TODO\|FIXME` grep) | 대부분 compose-rust 이슈 번호(#372, #385, #428, #460 등)와 FR-F8 | 툴킷 개선 시 정리 |
| 거대 파일 | 중간 | `vcs.rs` 6,210줄 (본문 4,487), `routines.rs`, `agents.rs` | 한 파일에 화면 섹션 7개와 표본 데이터. `PullRequestsPane` 약 440줄, `HistoryPane` 약 350줄, `BranchesPane` 약 170줄 | 섹션별 파일로 분리 (`vcs/changes.rs`, `vcs/prs.rs` 등) |
| 거대 파일 | 낮음 | 테스트 | 각 파일의 테스트가 파일 크기의 30-50%를 차지한다. 일부 테스트가 소스를 문자열로 읽어 점검한다 (`routines.rs:2825` `handler.find("notice::post(RUN_NOTICE)")`) | 테스트 파일 분리 |
