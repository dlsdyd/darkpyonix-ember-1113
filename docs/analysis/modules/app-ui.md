# 모듈: app-ui

- 경로: `ember/app/src/ui/` 중 아래 파일 (셸, 테마, 홈, 프로젝트, 세션, 질문, 팔레트, 키맵, 찾기, 모니터, 컴퓨터 추가, enrol 흐름 등)
- 규모: 파일 20개 / 약 14726줄, pub 항목 846개 중 Dioxus 바깥에서 쓰이는 것 657개
- 레이어: UI (Dioxus, 전환 중)
- 한 줄 책임: Dioxus 시절 기본 화면들. 지금은 화면 컴포넌트보다 `cr/` 화면이 가져다 쓰는 상태 모델, 문구 상수, 순수 함수의 저장소 역할이 크다.
- 의존하는 모듈: [app-core](app-core.md), [client](client.md)
- 이 모듈을 쓰는 모듈: [app-ui-cr.md](app-ui-cr.md), [app-ui-cr-session.md](app-ui-cr-session.md)

## 이 문서를 읽기 전에

- 앱의 기본 실행은 compose-rust 셸 `ui::cr::shell::launch`다 (`ember/app/src/lib.rs:143-145`). Dioxus 루트 `crate::ui::app`(`ember/app/src/ui/mod.rs:208`)은 어디서도 호출되지 않는다. `cr/` 모듈은 같은 이름의 `ui/` 모듈을 옮겨 오는 중이며, 다 옮기면 원본을 지운다 (`ember/app/src/ui/cr/mod.rs:1-3`, #220, #226).
- 그래서 이 파일들은 "화면"으로서는 대부분 죽었지만, 안의 상태 모델, 문구 상수, 순수 함수는 `cr/` 화면이 그대로 쓴다. **여기 있는 함수를 고치면 살아 있는 `cr/` 화면이 바뀐다.**
- 예외: `editor*.rs`는 별도 IDE 창(`--editor <project> <folder>`, FR-L31)이 지금도 Dioxus HTML 모드로 띄운다 (`ember/app/src/lib.rs:117-136`). 이 창에 관해서는 살아 있는 화면이다.
- 화면별 동작과 문구는 살아 있는 쪽 문서에 있다: [app-ui-cr.md](app-ui-cr.md), [app-ui-cr-session.md](app-ui-cr-session.md).

## 생성 방법과 한계

`.scratch/analysis/legacy.py`가 파일마다 `#[cfg(test)]` 앞의 `pub` 항목(fn, struct, enum, const, static, type, trait)을 뽑고, Dioxus 주 창 트리 바깥 파일(`ui/cr/`, `ember/app/src/*.rs`, `ember/app/tests/`, IDE 창용 `ui/editor*.rs`)에서 "항목 이름"과 "모듈 이름(`ui::<파일>` 또는 `<파일>::`)"이 같은 파일에 함께 나오면 "쓰임"으로 셌다. 이름만 맞춰 보므로 같은 이름이 다른 뜻으로 쓰인 경우 실제로는 죽었는데 쓰임으로 잡힐 수 있다 (과대 집계). 반대로 `use ... ::*` 같은 와일드카드 import는 이름이 나오면 잡힌다. "Dioxus 전용" 목록은 지우기 전에 `cargo check`로 확인해야 한다 [확인 필요].

## 파일별 요약

| 파일 | 줄 | 목적 (머리 주석) | pub 항목 | 바깥에서 쓰임 | Dioxus 전용 (죽은 코드 후보) |
|---|---|---|---|---|---|
| `ember/app/src/ui/add_computer.rs` | 293 | The pure model of the add-computer sheet (FR-C1 / FR-C2, D39, #490): the account's hub devices | 17 | 10 | 7 |
| `ember/app/src/ui/coexist.rs` | 571 | Shared UI and live state for the `compose-rust` UI migration (#220, INTENT D9). | 18 | 14 | 4 |
| `ember/app/src/ui/compat.rs` | 17 | Tone colour mapping helper. | 1 | 1 | 0 |
| `ember/app/src/ui/components.rs` | 337 | Shared component tokens (`docs/DESIGN.md` section 4) and `Label` for the separate editor window (`FR | 14 | 13 | 1 |
| `ember/app/src/ui/conversation.rs` | 18 | Transcript item key helper (FR-L5–FR-L7). | 1 | 1 | 0 |
| `ember/app/src/ui/enrol_flow.rs` | 1408 | The pure model of adding a computer with a one-time code (FR-C1, FR-C2, FR-C2c, FR-C2g, D39): | 109 | 83 | 26 |
| `ember/app/src/ui/find.rs` | 362 | Find and replace in the open file (D38, #440, #628): the pure model. The matching is a literal | 20 | 17 | 3 |
| `ember/app/src/ui/fonts.rs` | 89 | The bundled app font: Inter for Latin, then Pretendard for Hangul, then the system fonts. | 6 | 4 | 2 |
| `ember/app/src/ui/home.rs` | 2780 | The Home screen (FR-L11, FR-L15, FR-L16, FR-L23, `docs/DESIGN.md` section 6.1): a chat-first | 147 | 104 | 43 |
| `ember/app/src/ui/keymap.rs` | 368 | The editor keymap (FR-L30, `docs/INTENT.md` D32): VS Code or JetBrains. | 16 | 16 | 0 |
| `ember/app/src/ui/mod.rs` | 247 | The screens. Root component: [`app`]. | 14 | 0 | 14 |
| `ember/app/src/ui/monitor.rs` | 1215 | The computer monitor sheet (FR-L21; `docs/DESIGN.md` section 6.9). | 56 | 44 | 12 |
| `ember/app/src/ui/palette.rs` | 485 | The command palette's model (D38, #447): fuzzy ranking of commands and files. Pure; the sheet | 24 | 24 | 0 |
| `ember/app/src/ui/project.rs` | 1578 | The Project screen (FR-L1 to FR-L4, FR-L24, FR-L26; `docs/DESIGN.md` section 6.2). | 83 | 69 | 14 |
| `ember/app/src/ui/question.rs` | 562 | The question card's pure view-model (FR-T11, FR-A5): the draft, its gating, the reply, the | 45 | 34 | 11 |
| `ember/app/src/ui/safe_area.rs` | 159 | Title-bar safe area (FR-L33, #213): how far the top strip of the window is covered by the | 11 | 3 | 8 |
| `ember/app/src/ui/session.rs` | 2320 | The Session screen (FR-L5 to FR-L7, FR-L15, FR-L16, FR-L18, FR-L24; | 116 | 110 | 6 |
| `ember/app/src/ui/shell.rs` | 590 | The app shell (FR-L10, FR-L28, `docs/DESIGN.md` section 4.7): the eight menus, a sidebar | 41 | 33 | 8 |
| `ember/app/src/ui/theme.rs` | 567 | Design tokens (NFR-L3, `docs/DESIGN.md` section 2) and the System / Light / Dark choice | 62 | 57 | 5 |
| `ember/app/src/ui/usage.rs` | 760 | Token usage as the screens show it (FR-U7, FR-L11, FR-L20, FR-L18, #332): the pure model | 45 | 20 | 25 |

## 파일별 상세

### `ember/app/src/ui/add_computer.rs` (약 293줄)
- **목적:** The pure model of the add-computer sheet (FR-C1 / FR-C2, D39, #490): the account's hub devices
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/add_computer.rs` 10
- **바깥에서 쓰이는 항목:** `DevicesState`:12, `HUB_OFF`:19, `NO_DEVICES`:21, `ENROL_NOTE`:23, `DeviceRow`:60, `device_rows`:123, `devices_state`:152, `demo_devices`:161, `ReviewMode`:170, `review_mode`:178
- **Dioxus 전용(죽은 코드 후보):** `MAX_NAME_CHARS`:24, `MAX_ADDRESS_CHARS`:26, `sanitize_device_text`:32, `device_state_pill`:73, `online_label`:86, `device_kind`:104, `list_error_text`:144

### `ember/app/src/ui/coexist.rs` (약 571줄)
- **목적:** Shared UI and live state for the `compose-rust` UI migration (#220, INTENT D9).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/project.rs` 9, `ember/app/src/services.rs` 7, `ember/app/src/ui/cr/home.rs` 7, `ember/app/src/ui/cr/shell.rs` 7, `ember/app/src/ui/cr/session.rs` 6
- **바깥에서 쓰이는 항목:** `SharedLive`:39, `new`:77, `bump`:96, `bump_all`:100, `SharedUi`:127, `new`:158, `go`:190, `open_conversation`:219, `set_menu`:223, `set_selected_project`:234, `set_show_archived`:241, `set_theme_pref`:248, `update_prefs`:258, `open_editor_connection`:278
- **Dioxus 전용(죽은 코드 후보):** `DioxusMirrors`:113, `register_mirrors`:180, `mirrors`:183, `open_editor`:273

### `ember/app/src/ui/compat.rs` (약 17줄)
- **목적:** Tone colour mapping helper.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/compat.rs` 1, `ember/app/src/ui/cr/launcher.rs` 1
- **바깥에서 쓰이는 항목:** `tone_colors`:9

### `ember/app/src/ui/components.rs` (약 337줄)
- **목적:** Shared component tokens (`docs/DESIGN.md` section 4) and `Label` for the separate editor window (`FR-L31`).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/components.rs` 13, `ember/app/src/ui/cr/vcs.rs` 5, `ember/app/src/ui/cr/routines.rs` 5, `ember/app/src/ui/cr/channels.rs` 4, `ember/app/src/ui/cr/files.rs` 4
- **바깥에서 쓰이는 항목:** `font_refs`:18, `role_color`:38, `resolve_paint`:62, `type_role_style`:70, `Label`:89, `PillTone`:118, `pill_colors`:128, `pill_metrics`:141, `ButtonKind`:154, `ButtonStyle`:165, `button_style`:172, `pickchip_style`:219, `card_colors`:225
- **Dioxus 전용(죽은 코드 후보):** `label_min_width`:203

### `ember/app/src/ui/conversation.rs` (약 18줄)
- **목적:** Transcript item key helper (FR-L5–FR-L7).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/conversation.rs` 1
- **바깥에서 쓰이는 항목:** `item_key`:6

### `ember/app/src/ui/enrol_flow.rs` (약 1408줄)
- **목적:** The pure model of adding a computer with a one-time code (FR-C1, FR-C2, FR-C2c, FR-C2g, D39):
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/add_computer.rs` 83
- **바깥에서 쓰이는 항목:** `POLL_EVERY_MS`:20, `NEW_COMPUTER`:21, `NAME_LABEL`:23, `NAME_HELP`:24, `MAKE_CODE`:27, `WAITING_LINE`:28, `CODE_ONCE`:29, `NO_COMMAND`:32, `HTTP_WARNING`:33, `STDIN_NOTE`:36, `SERVER_FINGERPRINT_LABEL`:37, `CONFIRM_QUESTION`:38, `CONFIRM_CHECK`:39, `REPORTED_NAME`:40, `OBSERVED_ADDR`:41, `REPORTED_ADDR`:42, `PROPOSED_ADDR`:43, `NODE_FINGERPRINT`:44, `CONFIRMED_WAIT`:45, `JOINED_LINE`:46, `JOINED_NEXT`:47, `NODE_CMD_NOTE`:48, `ZSH_QUOTE_NOTE`:49, `DENY_LABEL`:50, `DENIED_LINE`:51, `EXPIRED_LINE`:52, `DEMO_LINE`:54, `NOTE_PROPOSED`:58, `PEER_ID_UNUSED`:59, `PEER_ONLY_NOTE`:60, `TYPED_FINGERPRINT_LABEL`:61, `TYPED_FINGERPRINT_HELP`:62, `NODE_FINGERPRINT_PEER`:63, `STDIN_FORM_NOTE`:67, `ARG_LABEL`:69, `CANCEL_FAILED`:71, `ARG_WARNING`:73, `CONFIRM_UNKNOWN`:79, `WARN_INFORMS`:81, `ConfirmRows`:94 외 43개
- **Dioxus 전용(죽은 코드 후보):** `NAME_EMPTY`:25, `NAME_TOO_LONG`:26, `DOOR_OFF`:30, `DOOR_URL_UNKNOWN`:31, `GONE_LINE`:53, `WARN_ADDR_DIFFERS`:55, `WARN_NAME_DIFFERS`:56, `WARN_PUBLIC_ADDR`:57, `FINGERPRINT_MISMATCH`:64, `FINGERPRINT_REQUIRED`:65, `ADDED_NOTICE`:75, `CONFIRM_FAILED_LATE`:77, `FINGERPRINT_PENDING_HINT`:80, `FLOW_STRINGS`:84, `fingerprint_matches`:147, `UNKNOWN_STATE`:208, `confirm_rows`:212, `Warning`:290, `accept_mint`:514, `is_end_state`:544, `view_after_tick`:566, `should_cancel_on_leave`:576, `MAX_DETACHED_CONFIRMS`:611, `push_detached_confirm`:630, `take_detached_confirm`:639, `info_is_empty`:781

### `ember/app/src/ui/find.rs` (약 362줄)
- **목적:** Find and replace in the open file (D38, #440, #628): the pure model. The matching is a literal
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/tests/find.rs` 17, `ember/app/src/ui/editor_workbench.rs` 12, `ember/app/src/ui/editor_search.rs` 4
- **바깥에서 쓰이는 항목:** `FindOptions`:7, `fn`:14, `Match`:25, `MAX_MATCHES`:46, `MAX_FIND_MATCHES`:47, `find_matches`:91, `find_matches_capped`:96, `cached_doc_matches`:126, `cached_matches`:158, `find_nav_match`:260, `replace_edits`:293, `next_match`:313, `count_text`:326, `FindBarState`:339, `new`:349, `open_find_bar`:354, `close`:358
- **Dioxus 전용(죽은 코드 후보):** `matches_in_line`:50, `DocCacheKey`:116, `scan_match`:182

### `ember/app/src/ui/fonts.rs` (약 89줄)
- **목적:** The bundled app font: Inter for Latin, then Pretendard for Hangul, then the system fonts.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/tests/fonts.rs` 4, `ember/app/src/lib.rs` 1, `ember/app/src/ui/cr/gallery.rs` 1, `ember/app/src/ui/cr/shell.rs` 1
- **바깥에서 쓰이는 항목:** `INTER`:25, `PRETENDARD`:29, `LICENSES`:36, `app_theme`:66
- **Dioxus 전용(죽은 코드 후보):** `Face`:13, `app_font`:47

### `ember/app/src/ui/home.rs` (약 2780줄)
- **목적:** The Home screen (FR-L11, FR-L15, FR-L16, FR-L23, `docs/DESIGN.md` section 6.1): a chat-first
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/home.rs` 92, `ember/app/src/ui/cr/routines.rs` 28, `ember/app/src/ui/cr/agents.rs` 16, `ember/app/src/demo.rs` 15, `ember/app/src/ui/cr/files.rs` 12
- **바깥에서 쓰이는 항목:** `UNAVAILABLE`:20, `DEFAULT_PROJECT`:23, `INTEGRATIONS_TITLE`:28, `GITHUB_NAME`:29, `GITHUB_MIN_GAP`:42, `LATER_PILL`:49, `LATER_LINE`:50, `LATER_INTEGRATIONS`:52, `CiResult`:70, `GithubRepo`:81, `GithubTotals`:95, `GithubState`:106, `state`:129, `settle`:137, `sample_header`:147, `GithubSampleKind`:153, `sample_github_state`:173, `github_sample_from_env`:233, `should_fetch_github`:247, `should_poll_github`:264, `GithubPill`:335, `GithubCard`:366, `from_state`:391, `ComposerAttachment`:478, `ATTACH_HINT`:485, `stage_attachment`:486, `attachment_message`:500, `GREETING`:506, `COMPOSER_PLACEHOLDER`:508, `Harness`:517, `ALL`:524, `kind`:530, `label`:537, `from_kind`:545, `PermMode`:558, `key`:570, `from_key`:578, `label`:588, `description`:599, `is_bypass`:609 외 64개
- **Dioxus 전용(죽은 코드 후보):** `GITHUB_NO_INFO`:30, `GITHUB_UNKNOWN`:32, `GITHUB_SAMPLE_MARK`:34, `GITHUB_NO_ACTIVITY`:35, `GITHUB_LOGIN_HINT`:36, `GITHUB_INSTALL_HINT`:37, `GITHUB_UNAVAILABLE_HINT`:38, `GITHUB_HOW`:40, `GITHUB_SAMPLE_WARN_REASON`:43, `GITHUB_SAMPLE_OFF_REASON`:44, `GITHUB_MAX_REPOS`:46, `GITHUB_MAX_CI`:48, `GithubConn`:57, `GithubFetch`:120, `parse_github_sample_hook`:160, `github_sample_hook_with`:228, `clean_text`:270, `github_state_from`:291, `GithubRepoRow`:348, `GithubAction`:359, `more_repos_text`:385, `ATTACH_EMPTY`:482, `ATTACH_INVALID`:484, `has_effort`:551, `BYPASS_CONFIRM_TITLE`:647, `BYPASS_CONFIRM_TEXT`:649, `mode_picker_rows`:652, `mode_hover`:699, `nav_width_for`:704, `CHIP_COUNT`:721, `CHIP_TEXT_CAPS`:724, `CHIP_TEXT_MINS`:727, `composer_text_px`:735, `composer_chips_avail`:758, `EFFORTS`:849, `effort_name`:854, `CHIP_WRAP_WIDTH`:1149, `suggestion_lines`:1157, `status_counts`:1243, `computers_online`:1264 외 3개

### `ember/app/src/ui/keymap.rs` (약 368줄)
- **목적:** The editor keymap (FR-L30, `docs/INTENT.md` D32): VS Code or JetBrains.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/tests/editor.rs` 16, `ember/app/src/ui/editor_workbench.rs` 14, `ember/app/src/ui/cr/settings.rs` 13, `ember/app/src/ui/editor.rs` 13, `ember/app/tests/palette.rs` 4
- **바깥에서 쓰이는 항목:** `Keymap`:18, `Os`:26, `current`:32, `Action`:43, `ALL`:72, `label`:96, `Chord`:127, `parse`:144, `display`:197, `ALL`:300, `label`:301, `find_label`:310, `palette_label`:316, `chord`:332, `hint`:338, `action_for`:345

### `ember/app/src/ui/mod.rs` (약 247줄)
- **목적:** The screens. Root component: [`app`].
- **Dioxus 전용(죽은 코드 후보):** `Route`:54, `Ui`:65, `go`:83, `open_conversation`:118, `update_prefs`:124, `open_editor`:136, `open_editor_connection`:142, `close_editor`:163, `open_new_session`:169, `with_rows`:179, `with_rows_no_previews`:186, `initial_menu`:200, `use_ui`:203, `app`:207

### `ember/app/src/ui/monitor.rs` (약 1215줄)
- **목적:** The computer monitor sheet (FR-L21; `docs/DESIGN.md` section 6.9).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/monitor.rs` 43, `ember/app/src/demo.rs` 7, `ember/app/src/ui/cr/project.rs` 6, `ember/app/src/ui/cr/shell.rs` 4
- **바깥에서 쓰이는 항목:** `Metric`:18, `ALL`:29, `title`:38, `ComputerMetrics`:54, `NoMetrics`:62, `fold_samples`:77, `ProcessRow`:92, `SortKey`:106, `SortState`:115, `toggle_sort`:131, `sort_rows`:147, `computer_members`:188, `agent_rows`:201, `offline_notice`:218, `cpu_text`:236, `mem_text`:241, `POLL_SECS`:254, `TOP_PROCESSES`:256, `FeedStatus`:330, `MonitorFeed`:341, `push`:353, `fail`:374, `status`:377, `error`:387, `latest`:391, `rates`:397, `CardView`:445, `card_view`:469, `empty_text`:581, `status_line`:594, `process_footer`:604, `bar_fraction`:617, `meter_fraction`:627, `bar_max`:643, `health_score`:667, `score_word`:688, `score_tone`:698, `storage_line`:708, `ram_badge`:716, `FanMode`:722 외 4개
- **Dioxus 전용(죽은 코드 후보):** `SERIES_CAP`:74, `card_columns`:227, `FEED_CAP`:258, `rate_per_sec`:262, `net_rates`:271, `percent_text`:287, `bytes_text`:295, `rate_text`:310, `ratio_percent`:315, `disk_used_percent`:324, `process_rows`:428, `main_disk`:656

### `ember/app/src/ui/palette.rs` (약 485줄)
- **목적:** The command palette's model (D38, #447): fuzzy ranking of commands and files. Pure; the sheet
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/tests/palette.rs` 24, `ember/app/src/ui/editor_workbench.rs` 17, `ember/app/src/editor_host.rs` 3
- **바깥에서 쓰이는 항목:** `Payload`:13, `Item`:28, `Ranked`:41, `rank`:131, `action_items`:159, `extension_command_items`:174, `highlight_segments`:188, `move_selection`:201, `Mode`:213, `mode_for`:222, `placeholder`:234, `skipped_directory`:246, `file_items`:256, `record_recent_path`:270, `prioritize_recent_files`:283, `items_for_workbench`:321, `items_for`:349, `effective_mode`:356, `parse_goto_line`:371, `goto_line_item`:402, `parse_path_line_suffix`:434, `apply_line_suffix`:460, `search_label`:468, `empty_text`:479

### `ember/app/src/ui/project.rs` (약 1578줄)
- **목적:** The Project screen (FR-L1 to FR-L4, FR-L24, FR-L26; `docs/DESIGN.md` section 6.2).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/project.rs` 68, `ember/app/src/ui/cr/session.rs` 15, `ember/app/src/ui/cr/vcs.rs` 15, `ember/app/src/ui/cr/monitor.rs` 13, `ember/app/src/ui/editor_workbench.rs` 11
- **바깥에서 쓰이는 항목:** `SOON`:41, `is_default_project`:42, `display_name`:48, `MAX_TILES`:72, `deck_count`:75, `visible_tiles`:84, `deck_label`:89, `DECK_NAMES`:94, `DECK_AVATARS`:96, `deck_names`:99, `deck_avatars`:117, `strip_arrows_visible`:122, `strip_scroll_target`:128, `Member`:147, `accessible_name`:161, `status_pill`:188, `harness_tone`:201, `MemberFilter`:216, `ALL`:226, `label`:234, `matches`:245, `filter_members`:259, `ProjectBox`:280, `repo_line`:298, `leader`:305, `project_boxes`:362, `project_boxes_with_archived`:367, `ComputerChip`:409, `reach_pill`:419, `chip_line`:430, `computer_chips`:438, `SettingsPart`:463, `part_supported`:480, `NOT_YET`:493, `leader_choice_visible`:496, `danger_allowed`:501, `SETTINGS_SAVE_AVAILABLE`:506, `SettingsDraft`:511, `from_project`:528, `override_harnesses`:561 외 29개
- **Dioxus 전용(죽은 코드 후보):** `DEFAULT_PROJECT_ID`:37, `DEFAULT_PROJECT_NAME`:39, `grid_columns`:63, `deck_names_fit`:105, `row_padding`:133, `order_members`:172, `leader_badge`:183, `member_name`:313, `loaded_overrides`:550, `overrides_map`:555, `SettingsError`:749, `NAME_MAX_CHARS`:770, `NewProjectError`:817, `effective_branch`:891

### `ember/app/src/ui/question.rs` (약 562줄)
- **목적:** The question card's pure view-model (FR-T11, FR-A5): the draft, its gating, the reply, the
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/conversation.rs` 34
- **바깥에서 쓰이는 항목:** `SECRET_ON_TERMINAL`:18, `SECRET_ONLY_SKIP`:21, `SAMPLE_NOTE`:22, `OTHER_PLACEHOLDER`:23, `SENT_WAITING`:24, `SKIPPED_LINE`:25, `ABANDONED_LINE`:26, `WITHDRAWN_LINE`:28, `CARD_TITLE`:29, `NEEDS_ANSWER`:30, `SEND_LABEL`:31, `SKIP_CONFIRM_NOTE`:34, `SKIP_CONFIRM_SECS`:36, `SkipStep`:58, `tap`:66, `reset`:74, `label`:77, `shown`:88, `shown_header`:94, `QuestionDraft`:100, `picked`:112, `clear`:121, `toggle`:130, `set_other`:154, `can_submit`:197, `reply`:203, `has_secret`:216, `answered_lines`:228, `needs_you_count`:259, `needs_you_label`:264, `estimate_height`:274, `DEBUG_SAMPLE_ID`:287, `debug_first`:292, `debug_sample`:295
- **Dioxus 전용(죽은 코드 후보):** `VALUES_MAX`:16, `VALUE_CHARS_MAX`:17, `SECRET_STARS`:27, `SKIP_LABEL`:32, `SKIP_CONFIRM_LABEL`:33, `SHOWN_CHARS_MAX`:39, `SHOWN_HEADER_MAX`:41, `STRINGS`:44, `other_text`:115, `values_of`:171, `mask`:221

### `ember/app/src/ui/safe_area.rs` (약 159줄)
- **목적:** Title-bar safe area (FR-L33, #213): how far the top strip of the window is covered by the
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/shell.rs` 3, `ember/app/src/ui/editor_workbench.rs` 1
- **바깥에서 쓰이는 항목:** `safe_area`:71, `sidebar_top_inset`:87, `top_reservation`:102
- **Dioxus 전용(죽은 코드 후보):** `SafeArea`:17, `Platform`:24, `current_platform`:29, `MACOS_FALLBACK`:41, `safe_area_for`:47, `toolkit_safe_area`:65, `title_strip_height`:81, `TopReservation`:93

### `ember/app/src/ui/session.rs` (약 2320줄)
- **목적:** The Session screen (FR-L5 to FR-L7, FR-L15, FR-L16, FR-L18, FR-L24;
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/session.rs` 109, `ember/app/src/ui/cr/conversation.rs` 17, `ember/app/src/ui/cr/home.rs` 16, `ember/app/src/ui/cr/project.rs` 16, `ember/app/src/ui/cr/shell.rs` 12
- **바깥에서 쓰이는 항목:** `timeline_summary`:71, `UI_STRINGS`:78, `ComputerHost`:187, `WebPagesLoad`:203, `computer_host`:233, `web_pages_from`:253, `web_menu_lines`:290, `WebTap`:302, `web_tap`:307, `SessionView`:326, `ALL`:333, `label`:335, `key`:345, `from_key`:352, `view_from_saved`:359, `PaneLayout`:371, `pane_layout`:380, `pane_rows`:394, `page_step`:404, `SideListMode`:417, `side_list_mode`:423, `toolbar_width`:435, `toolbar_fold_level`:444, `drawer_width`:458, `drawer_open_effective`:477, `view_chips_below`:483, `view_seg_icon_only`:489, `SIDE_LIST_W`:494, `PANE_H`:496, `INFO_PANEL_W`:498, `Section`:506, `side_sections`:516, `resolve_project`:545, `single_target`:559, `KanbanColumn`:572, `ALL`:581, `label`:588, `kanban_column`:602, `kanban`:613, `IdeChoice`:634 외 70개
- **Dioxus 전용(죽은 코드 후보):** `WebPage`:195, `drawer_is_overlay`:471, `ready`:965, `CiState`:1024, `depth`:1184, `vendor_of`:1238

### `ember/app/src/ui/shell.rs` (약 590줄)
- **목적:** The app shell (FR-L10, FR-L28, `docs/DESIGN.md` section 4.7): the eight menus, a sidebar
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/shell.rs` 33, `ember/app/src/ui/cr/project.rs` 9, `ember/app/src/ui/cr/session.rs` 9, `ember/app/src/ui/cr/home.rs` 8, `ember/app/src/ui/cr/agents.rs` 7
- **바깥에서 쓰이는 항목:** `NavMenu`:17, `ALL`:29, `label`:39, `svg`:56, `ICON_MORE_SVG`:69, `ICON_SUN_SVG`:71, `ICON_MOON_SVG`:72, `ICON_GEAR_SVG`:73, `tinted_svg`:76, `active_menu`:83, `Screen`:92, `screen_for`:114, `PLACEHOLDER_TEXT`:128, `BottomTab`:137, `BOTTOM_TABS`:141, `MORE_MENUS`:151, `label`:159, `svg`:165, `tab_for_menu`:175, `ShellMode`:188, `nav_mode`:205, `toggled_collapse`:218, `NavCounts`:224, `NavBadge`:239, `nav_badge`:246, `tab_badge`:261, `badge_text`:278, `DEMO_USER`:284, `ORG_NAME`:286, `avatar_initial`:289, `WINDOWS_CAPTION_HEIGHT_DP`:299, `caption_reserved_width`:302, `mark_svg_for`:316
- **Dioxus 전용(죽은 코드 후보):** `RAIL_MAX_DP`:199, `BAR_MAX_DP`:201, `WINDOWS_CAPTION_BUTTONS_DP`:297, `MARK_SVG`:307, `MARK_SM_SVG`:308, `APP_ICON_SVG`:309, `FAVICON_SVG`:310, `MARK_SM_MAX`:313

### `ember/app/src/ui/theme.rs` (약 567줄)
- **목적:** Design tokens (NFR-L3, `docs/DESIGN.md` section 2) and the System / Light / Dark choice
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/theme.rs` 55, `ember/app/src/ui/cr/shell.rs` 25, `ember/app/src/ui/cr/components.rs` 25, `ember/app/src/ui/cr/session.rs` 24, `ember/app/src/ui/cr/conversation.rs` 22
- **바깥에서 쓰이는 항목:** `Scheme`:17, `ThemePref`:25, `ALL`:33, `next`:36, `label`:43, `resolve`:53, `system_scheme`:77, `Accent`:83, `Palette`:90, `LIGHT`:117, `DARK`:138, `EmberTheme`:162, `new`:168, `select`:177, `press_tint`:182, `paint`:189, `Fs`:200, `ALL`:213, `fn`:226, `fn`:239, `letter_spacing`:256, `Weight`:267, `ALL`:274, `fn`:275, `SP`:291, `GAP_CARD`:292, `GAP_BLOCK`:294, `PAD_CARD_V`:296, `PAD_CARD_H`:297, `PAD_ROW_V`:298, `PAD_ROW_H`:299, `H_BTN`:300, `H_CTL`:302, `H_PILL`:303, `H_PILL_SM`:304, `H_NAV_ITEM`:305, `SIDE_W`:306, `RAIL_W`:307, `TABBAR_H`:308, `TABBAR_BOTTOM_GAP`:309 외 17개
- **Dioxus 전용(죽은 코드 후보):** `color_scheme`:62, `ELEVATION_CARD`:340, `ELEVATION_LARGE`:342, `ThemeCtx`:350, `use_ember_theme`:355

### `ember/app/src/ui/usage.rs` (약 760줄)
- **목적:** Token usage as the screens show it (FR-U7, FR-L11, FR-L20, FR-L18, #332): the pure model
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/home.rs` 14, `ember/app/src/ui/cr/agents.rs` 8, `ember/app/src/bridge.rs` 2
- **바깥에서 쓰이는 항목:** `UNKNOWN`:14, `COST_UNKNOWN`:17, `Load`:24, `agent_label`:57, `DayBar`:110, `total`:118, `SectionModel`:131, `section_model`:153, `window_total`:217, `DEFAULT_WINDOW`:227, `period_cost`:237, `cost_stats`:262, `legend_hatch_style`:287, `cost_legend`:293, `trend_days`:309, `trend_line`:316, `Vendor`:330, `of`:338, `RETRY`:402, `home_stack`:428
- **Dioxus 전용(죽은 코드 후보):** `UTC_NOTE`:16, `LOADING`:18, `FAILED`:19, `NO_REPORT`:20, `format_compact`:32, `day_label`:46, `token_value`:67, `session_usage_text`:76, `today_tokens`:84, `TokenTile`:90, `today_tile`:96, `NO_DATA`:225, `window_sessions`:243, `cost_per_job`:249, `format_usd`:255, `LEGEND_COST`:273, `LEGEND_TOKENS`:275, `CostLegendEntry`:279, `StackSeg`:354, `StackDay`:364, `LegendEntry`:374, `HomeStack`:382, `UTC_CAPTION`:399, `AVERAGE_LEGEND`:401, `weekday_name`:405

## 이 모듈을 수정할 때 주의할 점

- 바깥에서 쓰이는 항목을 고치면 `cr/` 화면(살아 있는 UI)이 바뀐다. 줄 번호 뒤 사용처 파일을 먼저 확인한다.
- `ui/theme.rs`의 토큰은 `ui/cr/theme.rs`에 다시 정의되어 있다. 색이나 크기를 바꿀 때 둘 다 바꾼다 ([app-ui-cr.md](app-ui-cr.md) "토큰과 컴포넌트").
- Dioxus 전용 항목을 지울 때는 한 파일씩 지우고 `cd ember/app && cargo check --locked`로 확인한다 (분석 중에는 실행하지 않았다).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 죽은 코드 | 낮음 | `ember/app/src/ui/enrol_flow.rs` | Dioxus 전용 pub 항목 26개 | 컴포넌트 단위로 정리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/home.rs` | Dioxus 전용 pub 항목 43개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/home.rs` | 2780줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 중간 | `ember/app/src/ui/mod.rs` | pub 항목 14개 모두 Dioxus 트리 안에서만 쓰인다 | #226 정리 때 파일째 삭제 검토 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/monitor.rs` | Dioxus 전용 pub 항목 12개 | 컴포넌트 단위로 정리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/project.rs` | Dioxus 전용 pub 항목 14개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/project.rs` | 1578줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/question.rs` | Dioxus 전용 pub 항목 11개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/session.rs` | 2320줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/usage.rs` | Dioxus 전용 pub 항목 25개 | 컴포넌트 단위로 정리 |
