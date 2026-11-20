# 모듈: app-ui-collab

- 경로: `ember/app/src/ui/agents.rs`, `channels.rs`, `channel_owner.rs`, `characters.rs`, `routines.rs`
- 규모: 파일 5개 / 약 7467줄, pub 항목 384개 중 Dioxus 바깥에서 쓰이는 것 316개
- 레이어: UI (Dioxus, 전환 중)
- 한 줄 책임: 에이전트·채널·캐릭터·루틴 화면의 Dioxus 원본. 대응하는 `cr/` 화면이 로직 대부분을 여기서 가져다 쓴다.
- 의존하는 모듈: [app-core](app-core.md), [client](client.md)
- 이 모듈을 쓰는 모듈: [app-ui-cr-work.md](app-ui-cr-work.md) (agents, routines), [app-ui-cr.md](app-ui-cr.md) (channels, characters, channel_owner)

## 이 문서를 읽기 전에

- 앱의 기본 실행은 compose-rust 셸 `ui::cr::shell::launch`다 (`ember/app/src/lib.rs:143-145`). Dioxus 루트 `crate::ui::app`(`ember/app/src/ui/mod.rs:208`)은 어디서도 호출되지 않는다. `cr/` 모듈은 같은 이름의 `ui/` 모듈을 옮겨 오는 중이며, 다 옮기면 원본을 지운다 (`ember/app/src/ui/cr/mod.rs:1-3`, #220, #226).
- 그래서 이 파일들은 "화면"으로서는 대부분 죽었지만, 안의 상태 모델, 문구 상수, 순수 함수는 `cr/` 화면이 그대로 쓴다. **여기 있는 함수를 고치면 살아 있는 `cr/` 화면이 바뀐다.**
- 예외: `editor*.rs`는 별도 IDE 창(`--editor <project> <folder>`, FR-L31)이 지금도 Dioxus HTML 모드로 띄운다 (`ember/app/src/lib.rs:117-136`). 이 창에 관해서는 살아 있는 화면이다.
- 화면별 동작과 문구는 살아 있는 쪽 문서에 있다: [app-ui-cr-work.md](app-ui-cr-work.md) (agents, routines), [app-ui-cr.md](app-ui-cr.md) (channels, characters, channel_owner).

## 생성 방법과 한계

`.scratch/analysis/legacy.py`가 파일마다 `#[cfg(test)]` 앞의 `pub` 항목(fn, struct, enum, const, static, type, trait)을 뽑고, Dioxus 주 창 트리 바깥 파일(`ui/cr/`, `ember/app/src/*.rs`, `ember/app/tests/`, IDE 창용 `ui/editor*.rs`)에서 "항목 이름"과 "모듈 이름(`ui::<파일>` 또는 `<파일>::`)"이 같은 파일에 함께 나오면 "쓰임"으로 셌다. 이름만 맞춰 보므로 같은 이름이 다른 뜻으로 쓰인 경우 실제로는 죽었는데 쓰임으로 잡힐 수 있다 (과대 집계). 반대로 `use ... ::*` 같은 와일드카드 import는 이름이 나오면 잡힌다. "Dioxus 전용" 목록은 지우기 전에 `cargo check`로 확인해야 한다 [확인 필요].

## 파일별 요약

| 파일 | 줄 | 목적 (머리 주석) | pub 항목 | 바깥에서 쓰임 | Dioxus 전용 (죽은 코드 후보) |
|---|---|---|---|---|---|
| `ember/app/src/ui/agents.rs` | 2307 | The 에이전트 screen (FR-L20, FR-L17, `docs/DESIGN.md` section 6.7): harnesses, models, | 144 | 114 | 30 |
| `ember/app/src/ui/channel_owner.rs` | 581 | The channel owner's side of invites, guests and allowances (FR-T14, FR-T15, FR-T17; the sheet is | 40 | 29 | 11 |
| `ember/app/src/ui/channels.rs` | 1260 | The Channels screen (FR-L12; `docs/DESIGN.md` section 6.4). | 68 | 55 | 13 |
| `ember/app/src/ui/characters.rs` | 1274 | Team character styles (FR-L22, FR-L24; `docs/DESIGN.md` section 7, INTENT D29). | 38 | 28 | 10 |
| `ember/app/src/ui/routines.rs` | 2045 | The 루틴 (Routines) screen (FR-L25, `docs/DESIGN.md` section 6.5): a dashboard on top (KPIs, | 94 | 90 | 4 |

## 파일별 상세

### `ember/app/src/ui/agents.rs` (약 2307줄)
- **목적:** The 에이전트 screen (FR-L20, FR-L17, `docs/DESIGN.md` section 6.7): harnesses, models,
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/agents.rs` 114, `ember/app/src/ui/cr/shell.rs` 9
- **바깥에서 쓰이는 항목:** `LOCAL_STORE_NOTE`:21, `Section`:30, `ALL`:39, `label`:46, `resolve_section`:71, `NavShape`:83, `nav_shape`:92, `AgentHarness`:107, `ALL`:116, `label`:123, `kind`:137, `of_kind`:148, `run_mode`:159, `shim_supported`:175, `picker_harness`:180, `HarnessSettings`:193, `default_settings`:206, `MEM_STEPS_MB`:224, `next_mem_limit`:227, `mem_limit_label`:234, `cycle`:244, `AccountMode`:258, `Routing`:266, `label`:274, `OnFail`:284, `label`:291, `Profile`:301, `AccountInfo`:320, `move_account`:330, `add_account`:341, `remove_account`:350, `THRESHOLD_MIN`:357, `THRESHOLD_MAX`:359, `THRESHOLD_STEP`:360, `step_threshold`:363, `threshold_label`:369, `SkipReason`:375, `Pick`:382, `pick_account`:393, `preview_text`:424 외 74개
- **Dioxus 전용(죽은 코드 후보):** `key`:58, `sandbox_default`:170, `version_pill`:651, `Rescan`:665, `RescanFailure`:675, `RESCAN_NOT_IMPLEMENTED`:680, `RESCAN_FAILED`:682, `NO_VERSION`:685, `rescan_failure`:688, `detect_to_agents`:697, `merge_detected`:711, `latest_detected_at`:719, `rescan_sentence`:725, `ComputerFacts`:952, `NOT_CHOSEN`:1017, `NO_ACCOUNTS`:1019, `ADD_ACCOUNT_FIRST`:1021, `NOT_INSTALLED_REASON`:1026, `HARNESS_SOON_REASON`:1028, `DefaultChips`:1068, `AccountOption`:1116, `HarnessOption`:1147, `PickRow`:1175, `AddKind`:1222, `ANTIGRAVITY_NOTE`:1233, `ACP_NOTE`:1235, `CreatedLogin`:1265, `parse_sheet_hook`:1350, `SAMPLE_LOGIN_COMMAND`:1369, `CHIPS_STACK_BELOW_DP`:1392

### `ember/app/src/ui/channel_owner.rs` (약 581줄)
- **목적:** The channel owner's side of invites, guests and allowances (FR-T14, FR-T15, FR-T17; the sheet is
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/channel_owner.rs` 29, `ember/app/src/ui/cr/channels.rs` 2
- **바깥에서 쓰이는 항목:** `TTL_CHOICES`:12, `DEFAULT_TTL_HOURS`:14, `ALLOW_PRESETS`:16, `MIN_HOURS`:17, `MAX_HOURS`:18, `clamp_hours`:38, `CLAMPED_NOTE`:49, `InviteState`:53, `label`:61, `DoorStatus`:112, `door_status`:123, `text`:132, `warning`:141, `can_copy`:146, `error_message`:162, `capped_note`:172, `Confirm`:187, `tap_remove`:197, `tap_revoke`:209, `is_remove`:219, `is_revoke`:223, `clears_sheet_state`:231, `known_door`:245, `DOOR_READ_FAILED_NOTE`:254, `merge_door`:259, `create_label`:264, `create_runs`:273, `invite_rows`:290, `guest_rows`:317
- **Dioxus 전용(죽은 코드 후보):** `hours_valid`:21, `parse_hours`:27, `invite_state`:72, `remaining_text`:86, `allowance_badge`:105, `guest_author_label`:153, `CONFIRM_DELAY_MS`:178, `confirm_tap`:181, `listen_unreachable`:236, `InviteRow`:279, `GuestRow`:309

### `ember/app/src/ui/channels.rs` (약 1260줄)
- **목적:** The Channels screen (FR-L12; `docs/DESIGN.md` section 6.4).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/channels.rs` 39, `ember/app/src/ui/cr/new_channel.rs` 21, `ember/app/src/ui/cr/vcs.rs` 9, `ember/app/src/ui/cr/shell.rs` 4, `ember/app/src/ui/cr/channel_owner.rs` 3
- **바깥에서 쓰이는 항목:** `Member`:18, `Message`:28, `Room`:42, `last_at`:58, `member`:61, `rooms_snapshot`:69, `SendState`:85, `can_send`:93, `draft_after_send`:100, `Load`:106, `empty_text`:116, `last_seq`:131, `merge_messages`:137, `message_from`:158, `room_from`:174, `rooms_from`:192, `me_id`:209, `ListFilter`:219, `RoomRow`:227, `Section`:238, `unread`:244, `matches`:251, `group_rooms`:268, `badge_text`:303, `filter_chips`:312, `Side`:326, `bubble_side`:332, `FeedItem`:339, `BubbleView`:345, `time_label`:386, `feed`:399, `split_view`:436, `should_mark_read`:442, `initial_room`:449, `RoomMotif`:458, `room_motif`:470, `AvatarKind`:479, `avatar_kind`:483, `compact_shows_room`:493, `AgentChoice`:503 외 15개
- **Dioxus 전용(죽은 코드 후보):** `last_message`:53, `USER_ID`:78, `USER_NAME`:80, `seq_of`:126, `member_from`:146, `day_of`:362, `date_label`:367, `DraftError`:513, `TAKEN_TEXT`:534, `NO_MEMBERS_HINT`:538, `is_forbidden_name_char`:551, `is_valid`:625, `members_in`:630

### `ember/app/src/ui/characters.rs` (약 1274줄)
- **목적:** Team character styles (FR-L22, FR-L24; `docs/DESIGN.md` section 7, INTENT D29).
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/characters_screen.rs` 21, `ember/app/src/ui/cr/characters.rs` 14, `ember/app/src/ui/cr/project.rs` 11, `ember/app/src/ui/cr/home.rs` 8, `ember/app/src/ui/cr/session.rs` 8
- **바깥에서 쓰이는 항목:** `CharStyle`:28, `ALL`:39, `id`:49, `from_id`:61, `label`:64, `blurb`:75, `CharState`:90, `ALL`:100, `from_status`:107, `Family`:121, `family_of`:126, `CharSpec`:174, `crown_shown`:189, `seed_hash`:201, `svg`:574, `SILHOUETTES`:756, `supports_pin`:759, `EDITOR_ROLES`:764, `EDITOR_HARNESSES`:767, `name`:783, `crown`:788, `harness_label`:820, `state_label`:829, `team_cols`:840, `characters_project`:852, `team_preview`:888, `with_topic`:918, `style_apply_needed`:928
- **Dioxus 전용(죽은 코드 후보):** `hue_range`:147, `CROWN_ID`:194, `body_hue`:285, `Prop`:400, `role_prop`:423, `PreviewMember`:772, `preview_team`:794, `TEAM_PREVIEW_CAP`:863, `TeamCell`:867, `TeamPreview`:880

### `ember/app/src/ui/routines.rs` (약 2045줄)
- **목적:** The 루틴 (Routines) screen (FR-L25, `docs/DESIGN.md` section 6.5): a dashboard on top (KPIs,
- **바깥 사용처(파일, 쓰는 항목 수):** `ember/app/src/ui/cr/routines.rs` 90, `ember/app/src/ui/cr/vcs.rs` 6, `ember/app/src/ui/cr/shell.rs` 5, `ember/app/src/services.rs` 3
- **바깥에서 쓰이는 항목:** `Minutes`:26, `LOCAL_OFFSET_MIN`:29, `days_from_civil`:36, `civil_from_days`:47, `weekday`:61, `minutes_at`:66, `cron_valid`:137, `describe_cron`:162, `big_time`:209, `next_run`:236, `format_next`:256, `ago`:271, `Trigger`:289, `ALL`:297, `label`:298, `Routine`:310, `RunStatus`:323, `weekday_chart_size`:335, `weekday_card_height`:345, `weekday_bar_radius`:351, `label`:356, `Run`:369, `Entry`:377, `schedule_line`:385, `last_run_text`:395, `Group`:407, `title`:414, `group_by_project`:429, `filter_projects`:451, `PaneMode`:460, `pane_mode`:468, `FormLayout`:478, `form_layout`:487, `Leave`:496, `LeaveDecision`:509, `routine_form_dirty`:520, `leave_decision`:526, `ROUTINE_DISCARD_QUESTION`:539, `FormField`:543, `FORM_FIELDS`:556 외 50개
- **Dioxus 전용(죽은 코드 후보):** `changes_frozen_fields`:1029, `FROZEN_NOTICE`:1044, `RunRowText`:1098, `DEMO_RUN_BUSY`:1140

## 이 모듈을 수정할 때 주의할 점

- 바깥에서 쓰이는 항목을 고치면 `cr/` 화면(살아 있는 UI)이 바뀐다. 줄 번호 뒤 사용처 파일을 먼저 확인한다.
- 같은 이름의 `cr/` 파일에 비슷한 로직이 다시 있을 수 있다. 한쪽만 고치지 않았는지 [app-ui-cr-work.md](app-ui-cr-work.md)의 이슈 후보를 확인한다.
- Dioxus 전용 항목을 지울 때는 한 파일씩 지우고 `cd ember/app && cargo check --locked`로 확인한다 (분석 중에는 실행하지 않았다).

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 죽은 코드 | 낮음 | `ember/app/src/ui/agents.rs` | Dioxus 전용 pub 항목 30개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/agents.rs` | 2307줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/channel_owner.rs` | Dioxus 전용 pub 항목 11개 | 컴포넌트 단위로 정리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/channels.rs` | Dioxus 전용 pub 항목 13개 | 컴포넌트 단위로 정리 |
| 죽은 코드 | 낮음 | `ember/app/src/ui/characters.rs` | Dioxus 전용 pub 항목 10개 | 컴포넌트 단위로 정리 |
| 거대 파일 | 낮음 | `ember/app/src/ui/routines.rs` | 2045줄 | 살아 있는 로직을 `cr/` 쪽이나 별도 모델 파일로 옮긴 뒤 분리 |
