# 모듈: app-ui-dev

- 경로: `ember/app/src/ui/files.rs`, `vcs.rs`, `editor*.rs`, `term_pane.rs`, `workbench.rs`
- 규모: 파일 9개 / 약 15564줄, pub 항목 554개 중 Dioxus 바깥에서 쓰이는 것 380개
- 레이어: UI (Dioxus, 전환 중)
- 한 줄 책임: 파일·버전 관리 화면의 Dioxus 원본, 그리고 지금도 Dioxus로 도는 별도 IDE 창(`--editor`, `ember/app/src/lib.rs:117-136`)의 화면.
- 의존하는 모듈: [app-core](app-core.md), [client](client.md)
- 이 모듈을 쓰는 모듈: [app-ui-cr-work.md](app-ui-cr-work.md) (files, vcs), [editor.md](editor.md), [app-core.md](app-core.md) (`editor_host.rs`)

## 이 문서를 읽기 전에

- 앱의 기본 실행은 compose-rust 셸 `ui::cr::shell::launch`다 (`ember/app/src/lib.rs:143-145`). Dioxus 루트 `crate::ui::app`(`ember/app/src/ui/mod.rs:208`)은 어디서도 호출되지 않는다. `cr/` 모듈은 같은 이름의 `ui/` 모듈을 옮겨 오는 중이며, 다 옮기면 원본을 지운다 (`ember/app/src/ui/cr/mod.rs:1-3`, #220, #226).
- 그래서 이 파일들은 "화면"으로서는 대부분 죽었지만, 안의 상태 모델, 문구 상수, 순수 함수는 `cr/` 화면이 그대로 쓴다. **여기 있는 함수를 고치면 살아 있는 `cr/` 화면이 바뀐다.**
- 예외: `editor*.rs`는 별도 IDE 창(`--editor <project> <folder>`, FR-L31)이 지금도 Dioxus HTML 모드로 띄운다 (`ember/app/src/lib.rs:117-136`). 이 창에 관해서는 살아 있는 화면이다.
- 화면별 동작과 문구는 살아 있는 쪽 문서에 있다: [app-ui-cr-work.md](app-ui-cr-work.md) (files, vcs), [editor.md](editor.md), [app-core.md](app-core.md) (`editor_host.rs`).

## 생성 방법과 한계

`.scratch/analysis/legacy.py`가 파일마다 `#[cfg(test)]` 앞의 `pub` 항목(fn, struct, enum, const, static, type, trait)을 뽑고, Dioxus 주 창 트리 바깥 파일(`ui/cr/`, `ember/app/src/*.rs`, `ember/app/tests/`, IDE 창용 `ui/editor*.rs`)에서 "항목 이름"과 "모듈 이름(`ui::<파일>` 또는 `<파일>::`)"이 같은 파일에 함께 나오면 "쓰임"으로 셌다. 이름만 맞춰 보므로 같은 이름이 다른 뜻으로 쓰인 경우 실제로는 죽었는데 쓰임으로 잡힐 수 있다 (과대 집계). 반대로 `use ... ::*` 같은 와일드카드 import는 이름이 나오면 잡힌다. "Dioxus 전용" 목록은 지우기 전에 `cargo check`로 확인해야 한다 [확인 필요].

## 파일별 요약

| 파일 | 줄 | 목적 (머리 주석) | pub 항목 | 바깥에서 쓰임 | Dioxus 전용 (죽은 코드 후보) |
|---|---|---|---|---|---|
| `ember/app/src/ui/editor.rs` | 1579 | Editor target and tab state. | 100 | 90 | 10 |
| `ember/app/src/ui/editor_icons.rs` | 88 | Icons from the mockup (icons.js): 24x24 stroke icons, drawn as images because the HTML path | 1 | 1 | 0 |
| `ember/app/src/ui/editor_scm.rs` | 2030 | Source control in the Ember editor window (FR-L31.2, #444). | 87 | 43 | 44 |
| `ember/app/src/ui/editor_search.rs` | 948 | The editor window's search tool window (SPEC FR-E7, #443): search across the project's files and rep | 30 | 12 | 18 |
| `ember/app/src/ui/editor_workbench.rs` | 2187 | Remote editor workbench. | 10 | 8 | 2 |
| `ember/app/src/ui/files.rs` | 2140 | The Files screen (FR-L27, FR-L27.1 to FR-L27.6, `docs/DESIGN.md` section 6.8): file transfer | 100 | 68 | 32 |
| `ember/app/src/ui/term_pane.rs` | 396 | The Terminal side of a Session pane (FR-L18, FR-P2): a read-only view of a member's terminal. | 24 | 10 | 14 |
| `ember/app/src/ui/vcs.rs` | 5901 | Data and action logic for 버전 관리 (FR-L19, INTENT D34, `docs/DESIGN.md` section 6.6). | 191 | 148 | 43 |
| `ember/app/src/ui/workbench.rs` | 295 | State classes for the workbench chrome (FR-L14, INTENT D23, #143). | 11 | 0 | 11 |

## 파일별 상세

### `ember/app/src/ui/editor.rs` (약 1579줄)
- **목적:** Editor target and tab state.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/editor_workbench.rs` 79, `ember/app/tests/editor.rs` 73, `ember/app/src/ui/editor_scm.rs` 19, `ember/app/src/ui/editor_search.rs` 12, `ember/app/src/editor_host.rs` 7
- **바깥에서 쓰이는 항목:** `EditorTarget`:9, `position_text`:36, `base_name`:41, `file_failure_reason`:47, `display_name`:66, `row_click_closes_prompt`:78, `syntax_spans`:109, `EditorTabs`:118, `open`:129, `activate`:139, `close`:148, `rename_prefix`:161, `set_dirty`:173, `is_dirty`:179, `has_unsaved`:183, `paths`:187, `current_path`:191, `close_others`:197, `ancestor_dirs_to_expand`:215, `empty_state_hints`:236, `tree_row_class`:247, `tab_class`:257, `tab_width_text`:267, `breadcrumb_segments`:274, `TreeRow`:288, `tree_rows`:298, `editor_grid_style`:332, `editor_page_height`:345, `editor_strip_padding`:351, `editor_grid_style_maximized`:357, `ClipboardKind`:368, `TreeClipboard`:375, `TreePrompt`:382, `update_tree_selection`:391, `prune_redundant_selection`:427, `select_all_tree_rows`:440, `cut_selection`:448, `clipboard_badge_text`:471, `new_item_parent`:482, `delete_confirmation`:495 외 50개
- **Dioxus 전용(죽은 코드 후보):** `colour_role`:86, `breadcrumb_text`:362, `DELETE_GUARD_MS`:545, `chord_from_key`:871, `DOUBLE_SHIFT_MS`:891, `from_action`:1009, `is_implemented`:1086, `EditorScreen`:1119, `MAX_DIFF_MATRIX_CELLS`:1143, `first_diff_line`:1348

### `ember/app/src/ui/editor_icons.rs` (약 88줄)
- **목적:** Icons from the mockup (icons.js): 24x24 stroke icons, drawn as images because the HTML path
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/editor_workbench.rs` 1
- **바깥에서 쓰이는 항목:** `IconResolver`:58

### `ember/app/src/ui/editor_scm.rs` (약 2030줄)
- **목적:** Source control in the Ember editor window (FR-L31.2, #444).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/tests/editor.rs` 25, `ember/app/src/ui/editor_workbench.rs` 24, `ember/app/src/editor_host.rs` 6
- **바깥에서 쓰이는 항목:** `reconstruct_base_text`:21, `reconstruct_base_from_read`:64, `markers_from_file_diff`:73, `side_by_side_rows`:128, `discard_patch`:166, `discard_tap`:171, `Group`:192, `title`:202, `staged`:211, `is_empty`:237, `get`:240, `modified_paths_set`:295, `groups`:317, `op_paths`:339, `branch_line`:362, `NEED_MESSAGE`:398, `commit_gate_with_amend`:406, `commit_gate`:423, `ScmLoad`:429, `status`:443, `visible`:524, `title`:529, `new`:557, `close_diff`:624, `Scm`:633, `new`:640, `snapshot`:644, `branch_line`:659, `modified_paths`:665, `diff_visible`:670, `close_diff`:673, `refresh`:688, `gutter_decorations`:744, `remote`:855, `conflict_visible`:889, `stage`:1105, `unstage`:1113, `commit`:1123, `show_git`:1197, `commit_window`:1225 외 3개
- **Dioxus 전용(죽은 코드 후보):** `DIFF_LINE_CAP`:188, `Entry`:218, `Groups`:230, `is_conflict`:251, `letter_of`:256, `letter_label`:265, `letter_color`:280, `branch_name`:353, `upstream_text`:374, `split_message`:388, `NOTHING_STAGED`:400, `CONFLICTS_LEFT`:401, `NOT_READ_YET`:402, `BUSY`:403, `note`:451, `load_from`:464, `DiffView`:475, `note`:485, `diff_from`:497, `DiffState`:511, `ScmState`:537, `begin_load`:577, `finish_load`:587, `begin_diff`:597, `finish_diff`:612, `set_message`:680, `ensure_gutter_diff`:706, `toggle_side_by_side`:774, `toggle_diff_line`:784, `toggle_diff_hunk`:795, `stage_diff_selection`:806, `apply_patch`:823, `toggle_amend`:828, `set_new_branch`:833, `checkout`:838, `create_branch`:846, `open_conflict`:893, `set_conflict_choice`:920, `pick_all_conflicts`:930, `set_conflict_step`:940 외 4개

### `ember/app/src/ui/editor_search.rs` (약 948줄)
- **목적:** The editor window's search tool window (SPEC FR-E7, #443): search across the project's files and replace.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/editor_workbench.rs` 9, `ember/app/src/editor_host.rs` 8
- **바깥에서 쓰이는 항목:** `next_id`:17, `SEARCH_DEBOUNCE_MS`:22, `SearchResults`:27, `start`:51, `clear`:60, `apply`:83, `take_refresh`:123, `files`:134, `open`:454, `apply_pending_reveal`:471, `schedule_reveal`:495, `panel`:526
- **Dioxus 전용(죽은 코드 후보):** `ReplaceScope`:43, `cancel_local`:70, `begin_replace`:76, `match_count`:143, `file_count`:147, `limit_hit`:151, `replace_request`:157, `status_text`:170, `LIMIT_NOTE`:190, `failure_text`:193, `confirm_text`:206, `report_text`:220, `relative_path`:243, `dir_part`:248, `preview_parts`:270, `replaced_text`:288, `hit_label`:306, `file_label`:312

### `ember/app/src/ui/editor_workbench.rs` (약 2187줄)
- **목적:** Remote editor workbench.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/editor_search.rs` 4, `ember/app/src/ui/editor_scm.rs` 4, `ember/app/tests/editor.rs` 3, `ember/app/src/ui/editor.rs` 3, `ember/app/src/editor_host.rs` 2
- **바깥에서 쓰이는 항목:** `FindCmd`:26, `PendingGoto`:36, `Shared`:44, `join_path`:159, `config`:271, `app`:284, `icon`:936, `icon_px`:941
- **Dioxus 전용(죽은 코드 후보):** `FindState`:12, `open_find_bar`:305

### `ember/app/src/ui/files.rs` (약 2140줄)
- **목적:** The Files screen (FR-L27, FR-L27.1 to FR-L27.6, `docs/DESIGN.md` section 6.8): file transfer
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/files.rs` 67, `ember/app/src/ui/cr/shell.rs` 7
- **바깥에서 쓰이는 항목:** `UNAVAILABLE`:28, `FILE_PICK_UNAVAILABLE`:37, `LOCK_LINE`:40, `FILE_PICK_REASON`:43, `FILE_PICKER_AVAILABLE`:51, `DeviceKind`:58, `label`:69, `Presence`:82, `label`:91, `PathKind`:113, `Device`:120, `path_label`:143, `connected_count`:175, `sendable_devices`:183, `grid`:192, `clean_member_name`:203, `demo_files`:240, `Direction`:250, `label`:256, `TransferState`:265, `TransferAction`:286, `label`:297, `user_actions`:333, `Transfer`:345, `format_bytes`:381, `percent`:438, `progress_line`:449, `ReceivedFile`:472, `HistoryResult`:479, `label`:487, `HistoryEntry`:498, `Offer`:513, `Answer`:521, `offer_line`:527, `visible_offers`:541, `answer_offer`:551, `TransferService`:572, `new`:637, `reset`:730, `is_demo`:881 외 28개
- **Dioxus 전용(죽은 코드 후보):** `EMPTY_DEVICES`:29, `EMPTY_AGENTS`:31, `EMPTY_TRANSFERS`:32, `EMPTY_RECEIVED`:33, `EMPTY_HISTORY`:34, `PICK_RECEIVER`:38, `PICK_FILES`:39, `AGENT_SEND_UNSUPPORTED`:45, `OFFLINE_TAG`:47, `order_devices`:131, `devices_from_computers`:156, `DEMO_FILES`:234, `is_active`:275, `next_state`:313, `apply`:358, `IllegalTransition`:375, `format_speed`:400, `format_duration`:408, `eta_secs`:429, `NoTransferService`:590, `DemoTransferService`:621, `demo_transfer_service`:888, `SHARE_NO_FILE`:1049, `SHARE_OFFLINE`:1066, `SHARE_AGENTS_MAX`:1069, `ShareDevice`:1073, `TARGET_OFFLINE`:1171, `target_selectable`:1183, `SHEET_FRAME_INSET`:1241, `SEND_SHEET_PAD`:1243, `chip_text_px`:1272, `chip_text_max`:1323

### `ember/app/src/ui/term_pane.rs` (약 396줄)
- **목적:** The Terminal side of a Session pane (FR-L18, FR-P2): a read-only view of a member's terminal.
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/session.rs` 10
- **바깥에서 쓰이는 항목:** `CONNECTING`:18, `NO_TERMINAL`:20, `TermRole`:29, `new`:123, `all`:145, `len`:152, `is_empty`:156, `TermView`:164, `view_for_member`:206, `view_for_attached`:228
- **Dioxus 전용(죽은 코드 후보):** `SCROLLBACK_LINES`:14, `RENDER_LINES`:17, `FAILED`:21, `NO_AGENT_TERMINAL`:22, `AMBIGUOUS_TERMINAL`:23, `DROPPED`:24, `EMPTY`:25, `strip_ansi`:43, `classify_line`:77, `ScrollBuffer`:116, `push_text`:126, `render_rows`:176, `view_from_state`:182, `demo_lines`:238

### `ember/app/src/ui/vcs.rs` (약 5901줄)
- **목적:** Data and action logic for 버전 관리 (FR-L19, INTENT D34, `docs/DESIGN.md` section 6.6).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/vcs.rs` 146, `ember/app/src/ui/editor_scm.rs` 35, `ember/app/src/ui/cr/session.rs` 25, `ember/app/tests/editor.rs` 25, `ember/app/src/demo.rs` 24
- **바깥에서 쓰이는 항목:** `SOON`:35, `Section`:43, `ALL`:54, `label`:63, `key`:77, `from_key`:88, `route_section`:95, `SectionNav`:101, `section_nav`:107, `PaneLayout`:117, `pane_layout`:125, `PaneTab`:136, `label`:146, `pane_tabs`:159, `tab_after_select`:169, `effective_tab`:179, `RemoteAction`:195, `remote_action`:200, `label`:212, `ahead_behind_text`:222, `fetched_text`:232, `bar_fractions`:243, `upstream_text`:253, `soon_line`:261, `CiState`:275, `ReviewState`:283, `merge_gate`:292, `LineKind`:311, `DiffLine`:318, `is_change`:331, `Hunk`:337, `FileStatus`:348, `letter`:357, `label`:365, `FileDiff`:377, `added`:389, `removed`:392, `parse_hunk_header`:408, `parse_unified`:514, `Check`:674 외 108개
- **Dioxus 전용(죽은 코드 후보):** `set_all`:773, `hunk_check`:803, `status_of`:1045, `untracked_paths`:1063, `build_snapshot`:1076, `diff_body`:1149, `UNTRACKED_SKIPPED_NOTE`:1163, `merge_untracked_diff`:1169, `AMEND_CONFIRM_DELAY_MS`:1203, `HISTORY_PAGE`:1274, `ref_label`:1302, `history_time_text`:1313, `history_entry`:1327, `annotate_history_sync`:1350, `history_matches_filter`:1370, `history_entries`:1383, `history_may_have_more`:1391, `log_body`:1396, `COMMIT_FILES_SHOWN`:1451, `COMMIT_BODY_LINES`:1453, `CommitFileView`:1457, `file_status_letter`:1501, `COMMIT_TEXT_MAX`:1640, `COMMIT_NODE_FILES_MAX`:1643, `clip_line`:1647, `commit_files_notice`:1659, `commit_failure`:1697, `commit_applied_notice`:1780, `PR_LIMIT`:1875, `pr_entry`:1941, `prs_body`:1979, `MERGE_GATE_DEFAULT`:2034, `PR_COMMENT_CUT`:2036, `PR_BODY_LINES`:2038, `pr_reviewers`:2094, `pr_detail_view`:2124, `korean_failure`:2178, `MERGE_NO_HEAD`:2204, `PR_TITLE_MAX_CHARS`:2275, `STALE_HEAD_TEXT`:2382 외 3개

### `ember/app/src/ui/workbench.rs` (약 295줄)
- **목적:** State classes for the workbench chrome (FR-L14, INTENT D23, #143).
- **Dioxus 전용(죽은 코드 후보):** `VIEWS_CSS`:10, `TITLEBAR_CSS`:11, `ACTION_WIDGET_CSS`:12, `tree_row_classes`:27, `view_filter_classes`:38, `command_center_classes`:46, `action_widget_classes`:54, `stylesheets`:62, `chrome`:94, `config`:134, `WorkbenchChrome`:146

## 이 모듈을 수정할 때 주의할 점

- 바깥에서 쓰이는 항목을 고치면 `cr/` 화면(살아 있는 UI)이 바뀐다. 줄 번호 뒤 사용처 파일을 먼저 확인한다.
- 같은 이름의 `cr/` 파일에 비슷한 로직이 다시 있을 수 있다. 한쪽만 고치지 않았는지 [app-ui-cr-work.md](app-ui-cr-work.md)의 이슈 후보를 확인한다.
- Dioxus 전용 항목을 지울 때는 한 파일씩 지우고 `cd ember/app && cargo check --locked`로 확인한다 (분석 중에는 실행하지 않았다).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 죽은 코드 | 낮음 | `ember/app/src/ui/editor.rs` | Dioxus 전용 pub 항목 10개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/editor.rs` | 1579줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/editor_scm.rs` | Dioxus 전용 pub 항목 44개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/editor_scm.rs` | 2030줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/editor_search.rs` | Dioxus 전용 pub 항목 18개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/editor_workbench.rs` | 2187줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/files.rs` | Dioxus 전용 pub 항목 32개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/files.rs` | 2140줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/term_pane.rs` | Dioxus 전용 pub 항목 14개 | 컴포넌트 단위로 정리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/vcs.rs` | Dioxus 전용 pub 항목 43개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/vcs.rs` | 5901줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 중간 | `ember/app/src/ui/workbench.rs` | pub 항목 11개 모두 Dioxus 트리 안에서만 쓰인다 | #226 정리 때 파일째 삭제 검토 |
