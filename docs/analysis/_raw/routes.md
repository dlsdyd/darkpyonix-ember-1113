# 라우트 목록 (Phase 2)

> 원자료 생성: `.scratch/analysis/routes.py` (axum `.route(` 추출). 테스트 파일 제외.
> 기준 커밋 `ffe9825`. 서버 라우터 조립은 `ember/server/src/main.rs:443-518`.

## 화면 라우트 (네이티브 앱 `ember-app`)

네이티브 앱은 URL 라우터가 없다. 화면 전환은 `Route` enum과 `NavMenu` 신호로 한다.

| 이름 | 정의 위치 | 의미 |
|---|---|---|
| `Route::Projects` | `ember/app/src/ui/mod.rs:56` | 메인 화면: 프로젝트, 세션, 컴퓨터 (FR-L1-L4) |
| `Route::Search` | `ember/app/src/ui/mod.rs:58` | 세션 검색 (FR-L9) |
| `Route::Conversation(id)` | `ember/app/src/ui/mod.rs:60` | 대화 하나 (FR-L5-L7) |
| `Ui.menu: NavMenu` | `ember/app/src/ui/mod.rs:75` | 셸의 메뉴 선택 (FR-L10), 정의는 `ember/app/src/ui/shell.rs:17` (`Home`, `Projects`, `Sessions`, `Channels`, `Routines`, `VersionControl`, `Agents`, `Files`) |
| `Ui.editor` | `ember/app/src/ui/mod.rs:77` | Ember 에디터 화면 (FR-L31), 셸을 대체 |

메뉴별 화면 목록은 [../modules/app-ui.md](../modules/app-ui.md)와 [../01_FEATURE_MAP.md](../01_FEATURE_MAP.md)에 있다.


## ember-server HTTP API (`ember/server`)

리스너: 기본은 owner 리스너(`EMBER_LISTEN`, 기본 `127.0.0.1:8740`, `auth::protect`로 토큰과 Origin/Host 검사). 같은 `app`이 transport(`EMBER_TRANSPORT=1`)로도 제공되며, "로컬 TCP 전용"은 transport에 없다.

### `ember/server/src/a2a/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/a2a/targets` | `targets` | `ember/server/src/a2a/api.rs:61` |
| POST | `/api/a2a/messages` | `send` | `ember/server/src/a2a/api.rs:62` |
| GET | `/api/a2a/messages/{id}` | `message` | `ember/server/src/a2a/api.rs:63` |
| GET | `/api/a2a/settings` | `get_settings` | `ember/server/src/a2a/api.rs:64` |
| PUT | `/api/a2a/settings` | `put_settings` | `ember/server/src/a2a/api.rs:64` |
| GET | `/api/sessions/{id}/a2a` | `get_session_switch` | `ember/server/src/a2a/api.rs:65` |
| PUT | `/api/sessions/{id}/a2a` | `put_session_switch` | `ember/server/src/a2a/api.rs:65` |
| GET | `/api/a2a/team` | `my_team` | `ember/server/src/a2a/api.rs:69` |
| POST | `/api/a2a/team/members` | `spawn` | `ember/server/src/a2a/api.rs:70` |
| DELETE | `/api/a2a/team/members/{member}` | `end_member` | `ember/server/src/a2a/api.rs:71` |
| GET | `/api/a2a/team/tasks` | `list_tasks` | `ember/server/src/a2a/api.rs:72` |
| POST | `/api/a2a/team/tasks` | `add_task` | `ember/server/src/a2a/api.rs:72` |
| PATCH | `/api/a2a/team/tasks/{number}` | `update_task` | `ember/server/src/a2a/api.rs:73` |
| GET | `/api/a2a/team/mail` | `read_mail` | `ember/server/src/a2a/api.rs:74` |
| POST | `/api/a2a/team/mail` | `send_mail` | `ember/server/src/a2a/api.rs:74` |
| GET | `/api/a2a/terminal/{target}` | `terminal_read` | `ember/server/src/a2a/api.rs:75` |
| POST | `/api/a2a/terminal/{target}/text` | `terminal_text` | `ember/server/src/a2a/api.rs:76` |
| POST | `/api/a2a/terminal/{target}/interrupt` | `terminal_interrupt` | `ember/server/src/a2a/api.rs:77` |
| GET | `/api/sessions/{id}/terminal-grants` | `list_terminal_grants` | `ember/server/src/a2a/api.rs:78` |
| PUT | `/api/sessions/{id}/terminal-grants` | `put_terminal_grant` | `ember/server/src/a2a/api.rs:78` |
| GET | `/api/sessions/{id}/mentions` | `mentions` | `ember/server/src/a2a/api.rs:82` |
| GET | `/api/sessions/{id}/team` | `session_team` | `ember/server/src/a2a/api.rs:83` |
| GET | `/api/teams/{team_id}` | `team` | `ember/server/src/a2a/api.rs:84` |
| GET | `/api/teams/{team_id}/mail` | `team_mail` | `ember/server/src/a2a/api.rs:85` |
| POST | `/api/teams/{team_id}/members/{session_id}/end` | `user_end_member` | `ember/server/src/a2a/api.rs:86` |

### `ember/server/src/accounts/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/accounts` | `list` | `ember/server/src/accounts/api.rs:36` |
| POST | `/api/accounts` | `create` | `ember/server/src/accounts/api.rs:36` |
| GET | `/api/accounts/route` | `preview_route` | `ember/server/src/accounts/api.rs:37` |
| GET | `/api/accounts/{id}` | `get_one` | `ember/server/src/accounts/api.rs:38` |
| DELETE | `/api/accounts/{id}` | `delete` | `ember/server/src/accounts/api.rs:38` |
| POST | `/api/accounts/{id}/default` | `set_default` | `ember/server/src/accounts/api.rs:39` |
| POST | `/api/accounts/{id}/check` | `check` | `ember/server/src/accounts/api.rs:40` |
| POST | `/api/accounts/{id}/clear-limit` | `clear_limit` | `ember/server/src/accounts/api.rs:41` |
| GET | `/api/usage` | `usage` | `ember/server/src/accounts/api.rs:42` |
| GET | `/api/providers` | `list_providers` | `ember/server/src/accounts/api.rs:43` |
| POST | `/api/providers` | `create_provider` | `ember/server/src/accounts/api.rs:43` |
| DELETE | `/api/providers/{id}` | `delete_provider` | `ember/server/src/accounts/api.rs:47` |

### `ember/server/src/agents/antigravity.rs` (로컬 TCP 전용)
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `HOOK_ROUTE` | `hook_call` | `ember/server/src/agents/antigravity.rs:642` |

### `ember/server/src/api/git.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `/api/projects/{name}/git/{*op}` | `relay` | `ember/server/src/api/git.rs:67` |

### `ember/server/src/api/harnesses.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `/api/computers/{id}/harnesses/detect` | `detect` | `ember/server/src/api/harnesses.rs:32` |

### `ember/server/src/api/ide.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/sessions/{id}/ide` | `ide_targets` | `ember/server/src/api/ide.rs:483` |
| GET | `/api/computers/{computer}/ide/relay/{launch_id}` | `ide_relay` | `ember/server/src/api/ide.rs:484` |

### `ember/server/src/api/ide_extensions.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `/api/computers/{id}/ide/extensions` | `install` | `ember/server/src/api/ide_extensions.rs:40` |

### `ember/server/src/api/integrations.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/integrations/github` | `github` | `ember/server/src/api/integrations.rs:86` |

### `ember/server/src/api/mod.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/health` | `(closure)` | `ember/server/src/api/mod.rs:80` |
| GET | `/api/agents` | `agents` | `ember/server/src/api/mod.rs:81` |
| GET | `/api/agents/settings` | `get_agent_settings` | `ember/server/src/api/mod.rs:83` |
| GET | `/api/agents/defaults` | `get_agent_defaults` | `ember/server/src/api/mod.rs:84` |
| PUT | `/api/agents/defaults` | `put_agent_defaults` | `ember/server/src/api/mod.rs:84` |
| PUT | `/api/agents/{agent}/settings` | `put_agent_settings` | `ember/server/src/api/mod.rs:85` |
| GET | `/api/sessions` | `list_sessions` | `ember/server/src/api/mod.rs:86` |
| POST | `/api/sessions` | `create_session` | `ember/server/src/api/mod.rs:86` |
| GET | `/api/sessions/{id}` | `get_session` | `ember/server/src/api/mod.rs:87` |
| PATCH | `/api/sessions/{id}` | `patch_session` | `ember/server/src/api/mod.rs:87` |
| GET | `/api/sessions/{id}/export` | `export_session` | `ember/server/src/api/mod.rs:88` |
| POST | `/api/sessions/{id}/fork` | `fork_session` | `ember/server/src/api/mod.rs:89` |
| GET | `/api/search` | `search` | `ember/server/src/api/mod.rs:90` |
| GET | `/api/usage/summary` | `usage_summary` | `ember/server/src/api/mod.rs:91` |
| GET | `/api/sessions/{id}/usage` | `session_usage` | `ember/server/src/api/mod.rs:92` |
| GET | `/api/projects` | `list_projects` | `ember/server/src/api/mod.rs:93` |
| POST | `/api/projects` | `create_project` | `ember/server/src/api/mod.rs:93` |
| GET | `/api/projects/{name}` | `get_project` | `ember/server/src/api/mod.rs:94` |
| PATCH | `/api/projects/{name}` | `patch_project` | `ember/server/src/api/mod.rs:94` |
| PUT | `/api/projects/{name}/computers/{computer_id}` | `assign` | `ember/server/src/api/mod.rs:95` |
| DELETE | `/api/projects/{name}/computers/{computer_id}` | `unassign` | `ember/server/src/api/mod.rs:95` |
| GET | `/api/sessions/{id}/events` | `events` | `ember/server/src/api/mod.rs:96` |
| POST | `/api/sessions/{id}/messages` | `send_message` | `ember/server/src/api/mod.rs:97` |
| POST | `/api/sessions/{id}/approvals/{approval_id}` | `answer` | `ember/server/src/api/mod.rs:98` |
| POST | `/api/sessions/{id}/questions/{question_id}/answer` | `answer_question` | `ember/server/src/api/mod.rs:99` |
| PUT | `/api/sessions/{id}/approve-all` | `set_approve_all` | `ember/server/src/api/mod.rs:100` |
| POST | `/api/sessions/{id}/interrupt` | `interrupt` | `ember/server/src/api/mod.rs:101` |
| POST | `/api/sessions/{id}/lease` | `lease` | `ember/server/src/api/mod.rs:102` |
| GET | `/api/push` | `push` | `ember/server/src/api/mod.rs:103` |

### `ember/server/src/browser/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/browsers` | `list` | `ember/server/src/browser/api.rs:38` |
| GET | `/api/browsers/{project}` | `info` | `ember/server/src/browser/api.rs:39` |
| POST | `/api/browsers/{project}` | `open` | `ember/server/src/browser/api.rs:39` |
| DELETE | `/api/browsers/{project}` | `stop` | `ember/server/src/browser/api.rs:39` |
| GET | `/api/browsers/{project}/egress` | `get_egress` | `ember/server/src/browser/api.rs:40` |
| PUT | `/api/browsers/{project}/egress` | `egress` | `ember/server/src/browser/api.rs:40` |
| DELETE | `/api/browsers/{project}/data` | `clear` | `ember/server/src/browser/api.rs:41` |
| POST | `/api/browsers/{project}/input` | `input` | `ember/server/src/browser/api.rs:42` |
| GET | `/api/browsers/{project}/view` | `view` | `ember/server/src/browser/api.rs:43` |
| GET | `/api/browsers/{project}/cdp` | `cdp` | `ember/server/src/browser/api.rs:44` |
| GET | `/api/browsers/{project}/cdp/json/version` | `cdp_version` | `ember/server/src/browser/api.rs:45` |
| GET | `/api/browsers/{project}/cdp/{nonce}` | `cdp_agent` | `ember/server/src/browser/api.rs:47` |
| GET | `/api/browsers/{project}/cdp/{nonce}/json/version` | `cdp_version_agent` | `ember/server/src/browser/api.rs:48` |
| GET | `/api/browsers/{project}/agent-config` | `agent_config` | `ember/server/src/browser/api.rs:49` |

### `ember/server/src/channels/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/channels` | `list` | `ember/server/src/channels/api.rs:150` |
| POST | `/api/channels` | `create` | `ember/server/src/channels/api.rs:150` |
| GET | `/api/channels/{id}` | `one` | `ember/server/src/channels/api.rs:151` |
| GET | `/api/channels/{id}/messages` | `messages` | `ember/server/src/channels/api.rs:152` |
| POST | `/api/channels/{id}/messages` | `post_message` | `ember/server/src/channels/api.rs:152` |
| POST | `/api/channels/{id}/post` | `agent_post` | `ember/server/src/channels/api.rs:153` |
| POST | `/api/channels/{id}/read` | `mark_read` | `ember/server/src/channels/api.rs:154` |
| POST | `/api/channels/{id}/mentions/preview` | `preview` | `ember/server/src/channels/api.rs:155` |
| GET | `/api/channels/{id}/feed` | `feed` | `ember/server/src/channels/api.rs:156` |
| POST | `/api/channels/{id}/feed/{approval_id}/answer` | `answer_feed` | `ember/server/src/channels/api.rs:157` |
| POST | `/api/channels/{id}/questions/{question_id}/answer` | `answer_feed_question` | `ember/server/src/channels/api.rs:158` |
| GET | `/api/guest-door` | `guest_door_status` | `ember/server/src/channels/api.rs:159` |
| GET | `/api/channels/{id}/invites` | `list_invites` | `ember/server/src/channels/api.rs:160` |
| POST | `/api/channels/{id}/invites` | `create_invite` | `ember/server/src/channels/api.rs:160` |
| DELETE | `/api/channels/{id}/invites/{invite_id}` | `revoke_invite` | `ember/server/src/channels/api.rs:161` |
| GET | `/api/channels/{id}/guests` | `list_guests` | `ember/server/src/channels/api.rs:162` |
| DELETE | `/api/channels/{id}/guests/{guest_id}` | `revoke_guest` | `ember/server/src/channels/api.rs:163` |
| PUT | `/api/channels/{id}/guests/{guest_id}/allow` | `set_allowance` | `ember/server/src/channels/api.rs:164` |
| DELETE | `/api/channels/{id}/guests/{guest_id}/allow` | `clear_allowance` | `ember/server/src/channels/api.rs:164` |

### `ember/server/src/channels/guest.rs` (guest door (`EMBER_GUEST_LISTEN`))
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/guest/channels/{id}` | `summary` | `ember/server/src/channels/guest.rs:259` |
| GET | `/api/guest/channels/{id}/messages` | `messages` | `ember/server/src/channels/guest.rs:260` |
| POST | `/api/guest/channels/{id}/messages` | `post_message` | `ember/server/src/channels/guest.rs:260` |
| POST | `/api/guest/accept` | `accept` | `ember/server/src/channels/guest.rs:264` |

### `ember/server/src/chatgpt/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/chatgpt` | `status` | `ember/server/src/chatgpt/api.rs:34` |
| POST | `/api/chatgpt/signin` | `start` | `ember/server/src/chatgpt/api.rs:35` |
| POST | `/api/chatgpt/signin/complete` | `complete_pasted` | `ember/server/src/chatgpt/api.rs:36` |
| GET | `/api/chatgpt/signin/{state}` | `signin_status` | `ember/server/src/chatgpt/api.rs:37` |
| GET | `/api/chatgpt/accounts` | `list` | `ember/server/src/chatgpt/api.rs:38` |
| GET | `/api/chatgpt/accounts` | `list` | `ember/server/src/chatgpt/api.rs:39` |
| GET | `/api/chatgpt/accounts/{id}` | `get_one` | `ember/server/src/chatgpt/api.rs:40` |
| DELETE | `/api/chatgpt/accounts/{id}` | `sign_out` | `ember/server/src/chatgpt/api.rs:40` |
| POST | `/api/chatgpt/accounts/{id}/refresh` | `refresh` | `ember/server/src/chatgpt/api.rs:44` |
| POST | `/api/chatgpt/accounts/{id}/clear-limit` | `clear_limit` | `ember/server/src/chatgpt/api.rs:45` |
| GET | `/api/chatgpt/accounts/{id}/models` | `models` | `ember/server/src/chatgpt/api.rs:46` |

### `ember/server/src/computers/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/computers` | `list` | `ember/server/src/computers/api.rs:39` |
| POST | `/api/computers` | `register` | `ember/server/src/computers/api.rs:39` |
| GET | `/api/computers/{id}` | `status` | `ember/server/src/computers/api.rs:40` |
| DELETE | `/api/computers/{id}` | `remove` | `ember/server/src/computers/api.rs:40` |
| GET | `/api/sessions/{id}/computer` | `current` | `ember/server/src/computers/api.rs:41` |
| PUT | `/api/sessions/{id}/computer` | `switch` | `ember/server/src/computers/api.rs:41` |
| PUT | `/api/sessions/{id}/designated-computer` | `designate` | `ember/server/src/computers/api.rs:42` |

### `ember/server/src/computers/enrol.rs` (로컬 TCP 전용 (owner) / enrol door)
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `/api/computers/enrol-codes` | `mint` | `ember/server/src/computers/enrol.rs:1415` |
| GET | `/api/computers/enrol-codes/{id}` | `status` | `ember/server/src/computers/enrol.rs:1416` |
| DELETE | `/api/computers/enrol-codes/{id}` | `cancel` | `ember/server/src/computers/enrol.rs:1416` |
| POST | `/api/computers/enrol-codes/{id}/confirm` | `confirm` | `ember/server/src/computers/enrol.rs:1417` |
| POST | `/api/computers/enrol-codes/{id}/deny` | `deny` | `ember/server/src/computers/enrol.rs:1418` |

### `ember/server/src/computers/fs.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| POST | `/api/computers/{id}/fs/{op}` | `relay` | `ember/server/src/computers/fs.rs:49` |

### `ember/server/src/computers/metrics.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/computers/{id}/metrics` | `metrics` | `ember/server/src/computers/metrics.rs:26` |

### `ember/server/src/computers/ports.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/computers/{id}/ports` | `ports` | `ember/server/src/computers/ports.rs:25` |

### `ember/server/src/computers/terms.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/computers/{id}/terms` | `list` | `ember/server/src/computers/terms.rs:49` |
| POST | `/api/computers/{id}/terms` | `create` | `ember/server/src/computers/terms.rs:49` |
| GET | `/api/computers/{id}/terms/{tid}` | `one` | `ember/server/src/computers/terms.rs:50` |
| DELETE | `/api/computers/{id}/terms/{tid}` | `remove` | `ember/server/src/computers/terms.rs:50` |
| GET | `/api/computers/{id}/terms/{tid}/snapshot` | `snapshot` | `ember/server/src/computers/terms.rs:51` |
| POST | `/api/computers/{id}/terms/{tid}/control` | `control` | `ember/server/src/computers/terms.rs:52` |
| POST | `/api/computers/{id}/terms/{tid}/kill` | `kill` | `ember/server/src/computers/terms.rs:53` |
| GET | `/api/computers/{id}/terms/{tid}/attach` | `attach` | `ember/server/src/computers/terms.rs:54` |

### `ember/server/src/devices/api.rs` (로컬 TCP 전용)
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/devices` | `list` | `ember/server/src/devices/api.rs:25` |
| POST | `/api/devices` | `add` | `ember/server/src/devices/api.rs:25` |
| DELETE | `/api/devices/{peer}` | `remove` | `ember/server/src/devices/api.rs:26` |

### `ember/server/src/enrol_door.rs` (enrol door (`EMBER_ENROL_LISTEN`))
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/enrol/status/{enrol_id}` | `poll` | `ember/server/src/enrol_door.rs:176` |
| GET | `/enrol/status/{enrol_id}` | `poll` | `ember/server/src/enrol_door.rs:177` |

### `ember/server/src/guest_door.rs` (guest door)
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `JOIN_ROUTE.1 (/join)` | `join` | `ember/server/src/guest_door.rs:206` |

### `ember/server/src/hub/api.rs` (`router`: 공용 / `admin_router`: 로컬 TCP 전용)
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/hub` | `status` | `ember/server/src/hub/api.rs:53` |
| GET | `/api/hub/devices` | `devices` | `ember/server/src/hub/api.rs:54` |
| POST | `/api/hub/devices/{id}/computer` | `add_computer` | `ember/server/src/hub/api.rs:55` |
| POST | `/api/hub/link` | `start_link` | `ember/server/src/hub/api.rs:62` |
| DELETE | `/api/hub/link` | `cancel_link` | `ember/server/src/hub/api.rs:62` |
| POST | `/api/hub/check` | `check` | `ember/server/src/hub/api.rs:63` |
| DELETE | `/api/hub/registration` | `forget` | `ember/server/src/hub/api.rs:64` |
| DELETE | `/api/hub/devices/{id}` | `remove_device` | `ember/server/src/hub/api.rs:65` |
| GET | `/api/hub/link-codes/{code}` | `lookup_code` | `ember/server/src/hub/api.rs:66` |
| POST | `/api/hub/link-codes/{code}` | `decide_code` | `ember/server/src/hub/api.rs:66` |
| POST | `/api/hub/sync-devices` | `sync_now` | `ember/server/src/hub/api.rs:67` |
| PUT | `/api/hub/sync-devices` | `set_sync` | `ember/server/src/hub/api.rs:67` |

### `ember/server/src/mcp/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/mcp` | `list` | `ember/server/src/mcp/api.rs:29` |
| POST | `/api/mcp` | `add` | `ember/server/src/mcp/api.rs:29` |
| GET | `/api/mcp/{id}` | `one` | `ember/server/src/mcp/api.rs:30` |
| PATCH | `/api/mcp/{id}` | `update` | `ember/server/src/mcp/api.rs:30` |
| DELETE | `/api/mcp/{id}` | `remove` | `ember/server/src/mcp/api.rs:30` |

### `ember/server/src/schedules/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/schedules` | `list` | `ember/server/src/schedules/api.rs:52` |
| POST | `/api/schedules` | `create` | `ember/server/src/schedules/api.rs:52` |
| GET | `/api/schedules/{id}` | `one` | `ember/server/src/schedules/api.rs:53` |
| PATCH | `/api/schedules/{id}` | `update` | `ember/server/src/schedules/api.rs:53` |
| DELETE | `/api/schedules/{id}` | `remove` | `ember/server/src/schedules/api.rs:53` |
| POST | `/api/schedules/{id}/pause` | `pause` | `ember/server/src/schedules/api.rs:54` |
| POST | `/api/schedules/{id}/resume` | `resume` | `ember/server/src/schedules/api.rs:55` |
| POST | `/api/schedules/{id}/run` | `run_now` | `ember/server/src/schedules/api.rs:56` |
| GET | `/api/schedules/{id}/runs` | `runs` | `ember/server/src/schedules/api.rs:57` |
| GET | `/api/a2a/schedules` | `agent_list` | `ember/server/src/schedules/api.rs:64` |
| POST | `/api/a2a/schedules` | `agent_create` | `ember/server/src/schedules/api.rs:64` |
| DELETE | `/api/a2a/schedules/{id}` | `agent_remove` | `ember/server/src/schedules/api.rs:65` |

### `ember/server/src/transfers.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/api/transfers` | `get_snapshot` | `ember/server/src/transfers.rs:717` |
| POST | `/api/transfers/offers` | `post_offer` | `ember/server/src/transfers.rs:718` |
| POST | `/api/transfers/offers/{id}/accept` | `post_accept` | `ember/server/src/transfers.rs:719` |
| POST | `/api/transfers/offers/{id}/decline` | `post_decline` | `ember/server/src/transfers.rs:720` |
| POST | `/api/transfers/{id}/chunks` | `post_chunk` | `ember/server/src/transfers.rs:721` |
| GET | `/api/transfers/{id}/resume-offset/{file}` | `get_resume_offset` | `ember/server/src/transfers.rs:722` |
| POST | `/api/transfers/{id}/complete` | `post_complete` | `ember/server/src/transfers.rs:723` |
| POST | `/api/transfers/{id}/pause` | `post_pause` | `ember/server/src/transfers.rs:724` |
| POST | `/api/transfers/{id}/resume` | `post_resume` | `ember/server/src/transfers.rs:725` |
| POST | `/api/transfers/{id}/cancel` | `post_cancel` | `ember/server/src/transfers.rs:726` |
| GET | `/api/transfers/history` | `get_history` | `ember/server/src/transfers.rs:727` |
| DELETE | `/api/transfers/history` | `delete_history` | `ember/server/src/transfers.rs:727` |
| PUT | `/api/transfers/settings` | `put_settings` | `ember/server/src/transfers.rs:728` |


## ember-node HTTP API (`ember/node`)

`/health`만 인증 없이, 나머지는 `auth` 미들웨어(베어러 토큰 `EMBER_NODE_TOKEN`) 뒤에 있다 (`ember/node/src/api.rs:155-234`).

### `ember/node/src/api.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/env` | `env` | `ember/node/src/api.rs:157` |
| GET | `/metrics` | `metrics` | `ember/node/src/api.rs:158` |
| POST | `/fs/stat` | `stat` | `ember/node/src/api.rs:159` |
| POST | `/fs/read` | `read` | `ember/node/src/api.rs:160` |
| POST | `/fs/write` | `write` | `ember/node/src/api.rs:161` |
| POST | `/fs/list` | `list` | `ember/node/src/api.rs:162` |
| POST | `/fs/lstat` | `lstat` | `ember/node/src/api.rs:163` |
| POST | `/fs/readlink` | `readlink` | `ember/node/src/api.rs:164` |
| POST | `/fs/symlink` | `symlink` | `ember/node/src/api.rs:165` |
| POST | `/fs/mkdir` | `mkdir` | `ember/node/src/api.rs:166` |
| POST | `/fs/remove` | `remove` | `ember/node/src/api.rs:167` |
| POST | `/fs/rename` | `rename` | `ember/node/src/api.rs:168` |
| POST | `/fs/setattr` | `setattr` | `ember/node/src/api.rs:169` |
| POST | `/fs/pwrite` | `pwrite` | `ember/node/src/api.rs:170` |
| POST | `/fs/glob` | `glob` | `ember/node/src/api.rs:171` |
| POST | `/fs/grep` | `grep` | `ember/node/src/api.rs:172` |
| POST | `/git/log` | `git_log_handler` | `ember/node/src/api.rs:174` |
| POST | `/git/commit/show` | `git_commit_show_handler` | `ember/node/src/api.rs:175` |
| POST | `/git/revert` | `git_revert_handler` | `ember/node/src/api.rs:176` |
| POST | `/git/cherry-pick` | `git_cherry_pick_handler` | `ember/node/src/api.rs:177` |
| POST | `/git/merge` | `git_merge_state_handler` | `ember/node/src/api.rs:178` |
| POST | `/git/merge/abort` | `git_merge_abort_handler` | `ember/node/src/api.rs:179` |
| POST | `/git/merge/commit` | `git_merge_commit_handler` | `ember/node/src/api.rs:180` |
| POST | `/git/branches` | `git_branches_handler` | `ember/node/src/api.rs:181` |
| POST | `/git/prs` | `git_prs_handler` | `ember/node/src/api.rs:182` |
| POST | `/git/github` | `git_github_handler` | `ember/node/src/api.rs:183` |
| POST | `/git/pr` | `git_pr_handler` | `ember/node/src/api.rs:184` |
| POST | `/git/pr/review` | `git_pr_review_handler` | `ember/node/src/api.rs:185` |
| POST | `/git/pr/merge` | `git_pr_merge_handler` | `ember/node/src/api.rs:186` |
| POST | `/git/pr/create` | `git_pr_create_handler` | `ember/node/src/api.rs:187` |
| POST | `/git/status` | `git_status` | `ember/node/src/api.rs:190` |
| POST | `/git/diff` | `git_diff` | `ember/node/src/api.rs:191` |
| POST | `/git/stage` | `git_stage` | `ember/node/src/api.rs:192` |
| POST | `/git/unstage` | `git_unstage` | `ember/node/src/api.rs:193` |
| POST | `/git/apply` | `git_apply` | `ember/node/src/api.rs:194` |
| POST | `/git/commit` | `git_commit` | `ember/node/src/api.rs:195` |
| POST | `/git/checkout` | `git_checkout` | `ember/node/src/api.rs:196` |
| POST | `/git/branch` | `git_branch` | `ember/node/src/api.rs:197` |
| POST | `/git/fetch` | `git_fetch` | `ember/node/src/api.rs:198` |
| POST | `/git/pull` | `git_pull` | `ember/node/src/api.rs:199` |
| POST | `/git/push` | `git_push` | `ember/node/src/api.rs:200` |
| POST | `/git/conflicts` | `git_conflicts` | `ember/node/src/api.rs:201` |
| POST | `/git/stash/list` | `git_stash_list` | `ember/node/src/api.rs:203` |
| POST | `/git/stash/push` | `git_stash_push` | `ember/node/src/api.rs:204` |
| POST | `/git/stash/apply` | `git_stash_apply` | `ember/node/src/api.rs:205` |
| POST | `/git/stash/pop` | `git_stash_pop` | `ember/node/src/api.rs:206` |
| POST | `/git/stash/drop` | `git_stash_drop` | `ember/node/src/api.rs:207` |
| POST | `/git/conflict` | `git_conflict` | `ember/node/src/api.rs:210` |
| POST | `/git/resolve` | `git_resolve` | `ember/node/src/api.rs:211` |
| GET | `/exec` | `exec_ws` | `ember/node/src/api.rs:213` |
| GET | `/exec-server` | `crate::exec_server::ws` | `ember/node/src/api.rs:214` |
| GET | `/egress` | `crate::egress::ws` | `ember/node/src/api.rs:215` |
| GET | `/jobs` | `list_jobs` | `ember/node/src/api.rs:216` |
| POST | `/jobs` | `start_job` | `ember/node/src/api.rs:216` |
| GET | `/jobs/{id}` | `get_job` | `ember/node/src/api.rs:217` |
| DELETE | `/jobs/{id}` | `remove_job` | `ember/node/src/api.rs:217` |
| POST | `/jobs/{id}/kill` | `kill_job` | `ember/node/src/api.rs:218` |
| GET | `/events` | `events_ws` | `ember/node/src/api.rs:219` |
| GET | `/ports` | `list_ports` | `ember/node/src/api.rs:220` |
| GET | `/terms` | `list_terms` | `ember/node/src/api.rs:221` |
| POST | `/terms` | `create_term` | `ember/node/src/api.rs:221` |
| GET | `/terms/{id}` | `get_term` | `ember/node/src/api.rs:222` |
| DELETE | `/terms/{id}` | `remove_term` | `ember/node/src/api.rs:222` |
| GET | `/terms/{id}/snapshot` | `term_snapshot` | `ember/node/src/api.rs:223` |
| GET | `/terms/{id}/attach` | `term_attach_ws` | `ember/node/src/api.rs:224` |
| POST | `/terms/{id}/control` | `term_control` | `ember/node/src/api.rs:225` |
| POST | `/terms/{id}/kill` | `kill_term` | `ember/node/src/api.rs:226` |
| GET | `/health` | `health` | `ember/node/src/api.rs:229` |


## 가짜 hub (`ember/hub/src/fake.rs`, feature `fake`, 테스트용)

### `ember/hub/src/fake.rs`
| 메서드 | 경로 | 핸들러 | 위치 |
|---|---|---|---|
| GET | `/health` | `(closure)` | `ember/hub/src/fake.rs:388` |
| GET | `/config` | `hub_config` | `ember/hub/src/fake.rs:389` |
| POST | `/device-links` | `create_link` | `ember/hub/src/fake.rs:390` |
| GET | `/device-links/{link_id}` | `get_link` | `ember/hub/src/fake.rs:391` |
| POST | `/device-links/{link_id}/token` | `claim_link` | `ember/hub/src/fake.rs:392` |
| GET | `/link-codes/{code}` | `get_link_code` | `ember/hub/src/fake.rs:393` |
| POST | `/link-codes/{code}` | `decide_link_code` | `ember/hub/src/fake.rs:393` |
| GET | `/me` | `me` | `ember/hub/src/fake.rs:394` |
| POST | `/me/resolve-token` | `rotate_resolve_token` | `ember/hub/src/fake.rs:395` |
| GET | `/devices` | `list_devices` | `ember/hub/src/fake.rs:396` |
| GET | `/devices/{id}` | `get_device` | `ember/hub/src/fake.rs:397` |
| PATCH | `/devices/{id}` | `update_device` | `ember/hub/src/fake.rs:397` |
| DELETE | `/devices/{id}` | `remove_device` | `ember/hub/src/fake.rs:397` |
| POST | `/devices/{id}/readmit` | `readmit_device` | `ember/hub/src/fake.rs:398` |
| GET | `/devices/{id}/addresses` | `device_addresses` | `ember/hub/src/fake.rs:399` |
| PUT | `/pkarr/{key}` | `pkarr_put` | `ember/hub/src/fake.rs:400` |
| GET | `/pkarr/{key}` | `pkarr_get` | `ember/hub/src/fake.rs:400` |


## ember/proxy (Python FastAPI, VS Code Web 래퍼)

앱 조립: `ember/proxy/main.py:53` (`FastAPI()`), `/auth` 마운트 `main.py:68`, 라우터 포함 `main.py:82-86`. 그 외 모든 경로는 `main.py:258`, `main.py:264`의 catch-all이 VS Code Web으로 프록시한다.

| 메서드 | 경로 | 위치 |
|---|---|---|
| POST | `/auth/login` | `ember/proxy/dpx/auth/api.py:181` |
| POST | `/auth/logout` | `ember/proxy/dpx/auth/api.py:203` |
| GET | `/auth/me` | `ember/proxy/dpx/auth/api.py:211` |
| GET | `/auth/users` | `ember/proxy/dpx/auth/api.py:225` |
| POST | `/auth/users` | `ember/proxy/dpx/auth/api.py:232` |
| DELETE | `/auth/users/{username}` | `ember/proxy/dpx/auth/api.py:249` |
| POST | `/auth/change-password` | `ember/proxy/dpx/auth/api.py:262` |
| GET | `/__workspaces` | `ember/proxy/dpx/home/api.py:43` |
| GET | `/__agents/workspaces` | `ember/proxy/dpx/home/api.py:49` |
| GET | `/__agents/conversations` | `ember/proxy/dpx/home/api.py:77` |
| GET | `/__agents/transcript` | `ember/proxy/dpx/home/api.py:91` |
| GET | `/__agents/resume` | `ember/proxy/dpx/home/api.py:104` |
| WS | `/hub/connect` | `ember/proxy/dpx/hub/server.py:163` |
| GET | `/api/machines` | `ember/proxy/dpx/hub/server.py:219` |
| GET | `/api/tree` | `ember/proxy/dpx/hub/server.py:228` |
| GET | `/api/machines/{mid}/conversations` | `ember/proxy/dpx/hub/server.py:250` |
| GET | `/api/machines/{mid}/transcript` | `ember/proxy/dpx/hub/server.py:273` |
| GET | `/api/machines/{mid}/open` | `ember/proxy/dpx/hub/server.py:290` |
| GET | `/api/machines/{mid}/refresh` | `ember/proxy/dpx/hub/server.py:315` |
| GET | `/healthz` | `ember/proxy/dpx/hub/server.py:331` |
| GET | `/favicon.ico` | `ember/proxy/dpx/hub/server.py:337` |
| GET | `/login` | `ember/proxy/dpx/hub/server.py:352` |
| GET | `/` | `ember/proxy/dpx/hub/server.py:357` |
| GET | `/__terms/_status` | `ember/proxy/dpx/terms/api.py:75` |
| GET | `/__terms` | `ember/proxy/dpx/terms/api.py:87` |
| POST | `/__terms` | `ember/proxy/dpx/terms/api.py:96` |
| GET | `/__terms/{term_id}` | `ember/proxy/dpx/terms/api.py:105` |
| DELETE | `/__terms/{term_id}` | `ember/proxy/dpx/terms/api.py:112` |
| GET | `/__terms/{term_id}/snapshot` | `ember/proxy/dpx/terms/api.py:119` |
| POST | `/__terms/{term_id}/control` | `ember/proxy/dpx/terms/api.py:126` |
| POST | `/__terms/{term_id}/kill` | `ember/proxy/dpx/terms/api.py:137` |
| WS | `/__terms/{term_id}/attach` | `ember/proxy/dpx/terms/api.py:156` |
| POST | `/__ext/ping` | `ember/proxy/dpx/vscode/extension.py:44` |
| GET | `/__ext/state` | `ember/proxy/dpx/vscode/extension.py:55` |
| GET | `/__overlay.css` | `ember/proxy/main.py:107` |
| GET | `/__overlay.js` | `ember/proxy/main.py:112` |
| GET | `/__detach.js` | `ember/proxy/main.py:117` |
| GET | `/__kb.js` | `ember/proxy/main.py:123` |
| GET | `/favicon.ico` | `ember/proxy/main.py:130` |
| GET | `/__runtime` | `ember/proxy/main.py:137` |
| GET | `/healthz` | `ember/proxy/main.py:146` |
| ANY | `/{full_path:path}` | `ember/proxy/main.py:258` |
| WS | `/{full_path:path}` | `ember/proxy/main.py:264` |

`ember/proxy/dpx/hub/server.py`의 라우트는 별도 hub 서버 앱(`dpx.hub`)이다.
