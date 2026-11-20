# 이름 사전 (2): 상태값과 환경 변수

[02_GLOSSARY.md](02_GLOSSARY.md)의 뒤쪽이다.

## 상태값 (enum)

이름이 `Status`, `State`, `Kind`, `Mode`, `Phase`로 끝나는 pub enum. 변형(variant)은 정의 바로 아래 줄들에서 뽑았다. 새 변형을 넣으면 `match`하는 곳을 모두 고쳐야 한다 (Rust 컴파일러가 빠진 곳을 알려 준다. 단 `_ =>`로 받는 곳은 알려 주지 않는다).

| 이름 | 위치 | 변형 |
|---|---|---|
| `IdeKind` | `ember/app/src/ide.rs:20` | `Ember`, `VsCode`, `Gateway` |
| `TerminalStatus` | `ember/app/src/terminal_stream.rs:384` | `Disconnected`, `Connecting`, `Connected` |
| `DevicesState` | `ember/app/src/ui/add_computer.rs:12` | `Loading`, `Ready`, `HubOff`, `Failed` |
| `ReviewMode` | `ember/app/src/ui/add_computer.rs:170` | `Off`, `List` |
| `AccountMode` | `ember/app/src/ui/agents.rs:258` | `Fixed`, `Auto` |
| `AddPhase` | `ember/app/src/ui/agents.rs:1281` | `Form`, `Busy`, `Created`, `Failed` |
| `InviteState` | `ember/app/src/ui/channel_owner.rs:53` | `Pending`, `Used`, `Expired`, `Revoked` |
| `DoorStatus` | `ember/app/src/ui/channel_owner.rs:112` | `Unknown`, `Off`, `Open` |
| `SendState` | `ember/app/src/ui/channels.rs:85` | `Idle`, `Sending` |
| `AvatarKind` | `ember/app/src/ui/channels.rs:479` | `Character`, `Letter` |
| `CharState` | `ember/app/src/ui/characters.rs:90` | `Run`, `Wait`, `Fail`, `Done`, `Idle` |
| `ButtonKind` | `ember/app/src/ui/components.rs:154` | `Default`, `Primary`, `Destructive` |
| `ButtonKind` | `ember/app/src/ui/cr/components.rs:488` | `Default`, `Primary`, `Destructive` |
| `FileKind` | `ember/app/src/ui/cr/files.rs:145` | `Image`, `Video`, `Audio`, `Zip`, `Doc` |
| `ClipboardKind` | `ember/app/src/ui/editor.rs:368` | `Copy`, `Cut` |
| `DiffLineKind` | `ember/app/src/ui/editor.rs:1128` | `Added`, `Modified`, `Deleted` |
| `DeviceKind` | `ember/app/src/ui/files.rs:58` | `Phone`, `Tablet`, `Laptop`, `Desktop`, `Server`, `Computer` |
| `PathKind` | `ember/app/src/ui/files.rs:113` | `Nearby`, `Direct`, `Relay` |
| `TransferState` | `ember/app/src/ui/files.rs:265` | `Queued`, `Sending`, `Paused`, `Done`, `Failed`, `Cancelled` |
| `GithubSampleKind` | `ember/app/src/ui/home.rs:153` | `Ok`, `Warn`, `Off` |
| `PermMode` | `ember/app/src/ui/home.rs:558` | `Ask`, `Edits`, `Bypass`, `Plan` |
| `FeedStatus` | `ember/app/src/ui/monitor.rs:330` | `Waiting`, `Live`, `Failed` |
| `FanMode` | `ember/app/src/ui/monitor.rs:722` | `Auto`, `Cool`, `Max` |
| `Mode` | `ember/app/src/ui/palette.rs:213` | `Commands`, `Files`, `Everything`, `GotoLine`, `Recent` |
| `AccountsState` | `ember/app/src/ui/project.rs:575` | `Loading`, `Ready` |
| `RunStatus` | `ember/app/src/ui/routines.rs:323` | `Done`, `Failed`, `Running`, `Skipped`, `Missed` |
| `PaneMode` | `ember/app/src/ui/routines.rs:460` | `Both`, `ListOnly`, `DetailOnly` |
| `SideListMode` | `ember/app/src/ui/session.rs:417` | `Column`, `Drawer` |
| `CiState` | `ember/app/src/ui/session.rs:1024` | `Pass`, `Fail`, `Run` |
| `NodeStatus` | `ember/app/src/ui/session.rs:1117` | `Run`, `Wait`, `Done`, `Fail`, `Unknown` |
| `ShellMode` | `ember/app/src/ui/shell.rs:188` | `Sidebar`, `Rail`, `BottomTabs` |
| `CiState` | `ember/app/src/ui/vcs.rs:275` | `Passed`, `Running`, `Waiting`, `Failed` |
| `ReviewState` | `ember/app/src/ui/vcs.rs:283` | `Approved`, `ChangesRequested`, `Pending`, `NoReviewer` |
| `LineKind` | `ember/app/src/ui/vcs.rs:311` | `Context`, `Add`, `Del` |
| `FileStatus` | `ember/app/src/ui/vcs.rs:348` | `Modified`, `Added`, `Deleted`, `Renamed` |
| `ReviewerState` | `ember/app/src/ui/vcs.rs:2013` | `Approved`, `ChangesRequested`, `Waiting`, `Commented` |
| `GitLogRefKind` | `ember/client/src/api.rs:263` | `Branch`, `Remote`, `Tag`, `Head` |
| `GitCommitFileStatus` | `ember/client/src/api.rs:308` | `Added`, `Modified`, `Deleted`, `Renamed`, `Copied`, `TypeChanged` |
| `GithubState` | `ember/client/src/api.rs:401` | `On`, `Warn`, `Off` |
| `GitPrState` | `ember/client/src/api.rs:479` | `Open`, `Closed`, `Merged` |
| `GitPrCheckState` | `ember/client/src/api.rs:550` | `Passed`, `Failed`, `Pending` |
| `GitPrReviewState` | `ember/client/src/api.rs:558` | `Approved`, `ChangesRequested`, `Commented`, `Dismissed`, `Pending` |
| `EnrolState` | `ember/client/src/api.rs:2391` | `Waiting`, `AwaitingConfirmation`, `Joined`, `Denied`, `Expired`, `Unknown` |
| `LauncherStatus` | `ember/client/src/state.rs:18` | `Idle`, `Running`, `WaitingForApproval`, `FinishedUnread`, `Finished`, `Failed`, `Unknown` |
| `ConnectionState` | `ember/client/src/state.rs:55` | `Offline`, `Connecting`, `Connected`, `Reconnecting` |
| `ApprovalState` | `ember/client/src/transcript.rs:43` | `Pending`, `Resolved`, `Abandoned`, `Withdrawn` |
| `QuestionState` | `ember/client/src/transcript.rs:54` | `Pending`, `Answered`, `Skipped`, `Abandoned`, `Withdrawn` |
| `SessionStatus` | `ember/client/src/wire.rs:157` | `Idle`, `Running`, `WaitingForApproval`, `Finished`, `Failed`, `Unknown` |
| `TaskStatus` | `ember/client/src/wire.rs:466` | `Open`, `InProgress`, `Blocked`, `Done`, `Cancelled`, `Unknown` |
| `ScheduleKind` | `ember/client/src/wire.rs:597` | `Cron`, `Interval`, `Once` |
| `RunStatus` | `ember/client/src/wire.rs:652` | `Running`, `Completed`, `Failed`, `Interrupted`, `Skipped`, `Missed`, `Unknown` |
| `ProviderKind` | `ember/editor/src/registry.rs:54` | `Hover`, `CodeLens`, `InlineCompletions` |
| `DecorationKind` | `ember/editor/src/widget.rs:72` | `Underline`, `CodeLens`, `HoverAnchor`, `GhostText` |
| `HoverPhase` | `ember/editor/src/widget.rs:239` | `Rest`, `Leave` |
| `RegistrationState` | `ember/hub/src/registration.rs:170` | `Unknown`, `Active`, `Revoked`, `Rejected`, `Unreachable` |
| `LinkStatus` | `ember/hub/src/types.rs:234` | `Pending`, `Approved`, `Denied`, `Claimed`, `Expired` |
| `GitCommitFileStatus` | `ember/node/src/git_commit.rs:35` |  |
| `GitLogRefKind` | `ember/node/src/git_log.rs:38` |  |
| `GitPrsState` | `ember/node/src/git_prs.rs:22` | `Open`, `Closed`, `Merged`, `All` |
| `GitPrState` | `ember/node/src/git_prs.rs:56` |  |
| `GitPrCheckState` | `ember/node/src/git_prs.rs:349` |  |
| `GitPrReviewState` | `ember/node/src/git_prs.rs:361` |  |
| `PortOwnerKind` | `ember/node/src/proto.rs:214` | `Term`, `Job` |
| `FileKind` | `ember/node/src/proto.rs:259` | `File`, `Dir`, `Symlink`, `Other` |
| `JobState` | `ember/node/src/proto.rs:610` | `Running`, `Exited`, `Signaled` |
| `NodeEventKind` | `ember/node/src/proto.rs:659` | `JobStarted`, `JobFinished` |
| `TermState` | `ember/node/src/proto.rs:756` | `Running`, `Exited`, `Lost` |
| `TransportMode` | `ember/node/src/transport.rs:41` | `Off`, `Also`, `Only` |
| `TaskStatus` | `ember/server/src/a2a/team.rs:117` | `Open`, `InProgress`, `Blocked`, `Done`, `Cancelled` |
| `AgentKind` | `ember/server/src/agents/mod.rs:33` | `ClaudeCode`, `Codex`, `Antigravity`, `Scripted`, `Acp` |
| `SignInStatus` | `ember/server/src/chatgpt/mod.rs:227` | `Pending`, `SignedIn`, `Failed` |
| `State` | `ember/server/src/computers/enrol.rs:415` | `Waiting`, `AwaitingConfirmation`, `Confirmed`, `Joined`, `Denied`, `Expired` |
| `EnrolStatus` | `ember/server/src/computers/enrol.rs:469` | `Waiting`, `AwaitingConfirmation`, `Joined`, `Denied`, `Expired` |
| `FileState` | `ember/server/src/computers/observations.rs:24` | `Hash`, `Missing` |
| `Kind` | `ember/server/src/computers/shim.rs:89` | `BashTool`, `Other` |
| `LimitKind` | `ember/server/src/door/limits.rs:159` | `Accept`, `Other` |
| `SessionStatus` | `ember/server/src/events.rs:244` | `Idle`, `Running`, `WaitingForApproval`, `Finished`, `Failed` |
| `ScheduleKind` | `ember/server/src/schedules/mod.rs:89` | `Cron` |
| `RunStatus` | `ember/server/src/schedules/mod.rs:164` | `Running`, `Completed`, `Failed`, `Interrupted`, `Skipped`, `Missed` |
| `ActiveStatus` | `ember/server/src/transfers.rs:40` | `Queued`, `Sending`, `Paused`, `Done`, `Failed`, `Cancelled` |
| `ReceiveMode` | `ember/transfer/src/mode.rs:12` | `Ask`, `AutoAcceptFrom`, `Off` |
| `State` | `ember/transfer/src/state.rs:59` | `Offered`, `Accepted`, `Receiving`, `Done`, `Declined`, `Expired`, `Cancelled`, `Failed` |
| `BackendKind` | `ember/transport/src/config.rs:16` | `Iroh`, `Letify` |
| `PowerState` | `ember/transport/src/lib.rs:89` | `Foreground`, `Background`, `PowerSave` |
| `PathState` | `ember/transport/src/lib.rs:100` | `Direct`, `Relayed`, `Unknown` |

## 환경 변수

코드(테스트 제외)에서 grep한 201개. "뜻"은 그 이름으로 시작하는 코드 주석(예: `ember/server/src/main.rs:24-77`, `ember/node/src/main.rs:13-43`)이나 모듈 문서에서 가져왔고, 빈칸은 직접 확인해야 한다. 기본값은 대개 주석의 "(default ...)" 부분이다. 서버 실행 옵션 전체는 `ember/server/src/main.rs:24-77`의 주석이 가장 정확하다.

| 이름 | 쓰는 곳 | 읽는 위치 (예) | 파일 수 | 뜻 |
|---|---|---|---|---|
| `DARKPYONIX_HOME` | extensions | `extensions/vscode-darkpyonix/src/manager/discovery.ts` | 2 |  |
| `DPX_BUNDLED_EXTENSIONS_DIR` | proxy | `ember/proxy/dpx/vscode/runtime.py:168` | 1 |  |
| `DPX_CODE_BIN` | proxy | `ember/proxy/dpx/serve.py:81` | 2 |  |
| `DPX_DEFAULT_EXTENSIONS` | proxy | `ember/proxy/dpx/vscode/runtime.py:175` | 2 |  |
| `DPX_E2E_WS` | extensions | `extensions/vscode-darkpyonix/test/e2e/suite.ts` | 1 |  |
| `DPX_EMBER_NODE_TOKEN` | proxy | `ember/proxy/dpx/config.py:65` | 1 | override it (both must be set). The token never reaches the browser. |
| `DPX_EMBER_NODE_URL` | proxy | `ember/proxy/dpx/config.py:64` | 1 |  |
| `DPX_FOLDER_ROOTS` | proxy | `ember/proxy/dpx/config.py:25` | 4 |  |
| `DPX_HOME` | proxy | `ember/proxy/dpx/agents/base.py:254` | 1 |  |
| `DPX_HUB_TOKEN` | proxy | `ember/proxy/dpx/hub/connector.py:44` | 2 |  |
| `DPX_HUB_URL` | proxy | `ember/proxy/dpx/hub/connector.py:43` | 2 |  |
| `DPX_MACHINE_ID` | proxy | `ember/proxy/dpx/hub/connector.py:54` | 1 |  |
| `DPX_MACHINE_NAME` | proxy | `ember/proxy/dpx/hub/connector.py:46` | 1 |  |
| `DPX_NO_ASSET_CACHE` | proxy | `ember/proxy/dpx/assets.py:20` | 1 |  |
| `DPX_OFFLINE_AFTER` | proxy | `ember/proxy/dpx/hub/server.py:49` | 1 |  |
| `DPX_OSE_ARGS` | proxy | `ember/proxy/dpx/vscode/runtime.py:157` | 1 |  |
| `DPX_OSE_SERVER` | proxy | `ember/proxy/dpx/serve.py:81` | 2 |  |
| `DPX_PASSWORD` | proxy | `ember/proxy/dpx/auth/api.py:81` | 2 |  |
| `DPX_PUBLIC_URL` | proxy | `ember/proxy/dpx/hub/connector.py:45` | 3 |  |
| `DPX_RPC_TIMEOUT` | proxy | `ember/proxy/dpx/hub/server.py:50` | 1 |  |
| `DPX_RUNTIME` | proxy | `ember/proxy/dpx/serve.py:79` | 2 |  |
| `DPX_SERVER_DATA_DIR` | proxy | `ember/proxy/dpx/serve.py:181` | 1 |  |
| `DPX_SERVE_HOST` | proxy | `ember/proxy/dpx/serve.py:169` | 1 |  |
| `DPX_SERVE_PORT` | proxy | `ember/proxy/dpx/serve.py:171` | 1 |  |
| `DPX_SNAPSHOT_CONVERSATIONS` | proxy | `ember/proxy/dpx/hub/connector.py:48` | 1 |  |
| `DPX_SNAPSHOT_INTERVAL` | proxy | `ember/proxy/dpx/hub/connector.py:47` | 1 |  |
| `DPX_TAB_DETACH` | proxy | `ember/proxy/dpx/config.py:48` | 2 |  |
| `DPX_USERNAME` | proxy | `ember/proxy/dpx/auth/api.py:80` | 2 |  |
| `EMBER_A2A` | server | `ember/server/src/main.rs:281` | 1 | 0`: agent-to-agent messaging starts off until a user turns it on |
| `EMBER_A2A_BIN` | server | `ember/server/src/a2a/mod.rs:576` | 1 |  |
| `EMBER_ACP_AGENTS` | server | `ember/server/src/agents/acp.rs:381` | 3 | Agent Client Protocol agents to offer, as JSON: a list of preset names |
| `EMBER_ACP_AGENTS_FILE` | server | `ember/server/src/agents/acp.rs:381` | 3 | else none. |
| `EMBER_ACP_HOME` | server | `ember/server/src/accounts/mod.rs:81` | 1 |  |
| `EMBER_AGENT_EGRESS` | server | `ember/server/src/main.rs:233` | 1 |  |
| `EMBER_AGENT_URL` | server | `ember/server/src/main.rs:277` | 1 | the server URL given to agents for A2A (default derived from |
| `EMBER_AGY_ACCOUNT_DIR` | server | `ember/server/src/accounts/mod.rs:76` | 1 |  |
| `EMBER_AGY_BIN` | server | `ember/server/src/agents/antigravity.rs:235` | 2 | the Antigravity CLI (default `agy` on `PATH`). Its sessions keep a private |
| `EMBER_AGY_SANDBOX` | app, server | `ember/server/src/agents/antigravity.rs:239` | 3 | Antigravity 샌드박스 |
| `EMBER_ALLOWED_HOSTS` | server | `ember/server/src/main.rs:507` | 2 | extra host names accepted in `Host` (comma-separated, FR-S10); the |
| `EMBER_APP_BIN` | server | `ember/server/scripts/real-server-smoke.sh` | 1 |  |
| `EMBER_BROWSER_CDP_WS` | server | `ember/server/src/browser/agent.rs:262` | 1 | / `EMBER_BROWSER_MCP_CONFIG`. |
| `EMBER_BROWSER_HEADFUL` | server | `ember/server/src/browser/mod.rs:57` | 1 | 1`: show a window (debugging) |
| `EMBER_BROWSER_MCP` | server | `ember/server/src/browser/agent.rs:140` | 2 | → which server, if any. `None` = off (the default), or an unknown value, |
| `EMBER_BROWSER_MCP_CONFIG` | server | `ember/server/src/browser/agent.rs:263` | 1 | the Claude Code `--mcp-config` JSON. |
| `EMBER_BROWSER_MCP_RUNNER` | server | `ember/server/src/browser/agent.rs:89` | 2 | (a path or name; `bunx`/`bun x` style is told apart by its file |
| `EMBER_CHATGPT_REDIRECT_PORT` | server | `ember/server/src/chatgpt/mod.rs:111` | 2 | port of the `http://127.0.0.1:<port>/auth/callback` sign-in |
| `EMBER_CHROME_BIN` | server | `ember/server/src/browser/chrome.rs:15` | 4 | browser binary |
| `EMBER_CLAUDE_BIN` | server | `ember/server/scripts/real-server-smoke.sh:170` | 4 | the Claude Code CLI (default `claude` on `PATH`) |
| `EMBER_CODEX_BIN` | server | `ember/server/src/accounts/mod.rs:181` | 3 | the Codex CLI (default `codex` on `PATH`) |
| `EMBER_CODEX_PROXY_BASE_URL` | server | `ember/server/src/agents/codex.rs:304` | 2 |  |
| `EMBER_CODEX_PROXY_KEY` | server | `ember/server/src/agents/codex.rs:306` | 2 |  |
| `EMBER_COMPUTER_ID` | server | `ember/server/src/computers/mod.rs:1334` | 1 |  |
| `EMBER_CR_AGENTS_LIVE` | app | `ember/app/src/ui/cr/agents.rs:252` | 1 |  |
| `EMBER_CR_AGENTS_SECTION` | app | `ember/app/src/ui/cr/agents.rs:288` | 1 |  |
| `EMBER_CR_AGENTS_SHEET` | app | `ember/app/src/ui/agents.rs:1365` | 1 |  |
| `EMBER_CR_COMPUTER` | app | `ember/app/src/ui/cr/monitor.rs:516` | 1 | (an index: 0 is the online "이 컴퓨터", 1 the offline "스튜디오 PC"). |
| `EMBER_CR_FILES_SAMPLE` | app | `ember/app/src/ui/files.rs:882` | 2 | 1` fills it with sample data so every section can be reviewed. |
| `EMBER_CR_FILES_SHEET` | app | `ember/app/src/ui/cr/files.rs:369` | 1 | send` opens the send sheet at the start, for review captures. |
| `EMBER_CR_GALLERY` | app | `ember/app/src/ui/cr/gallery.rs:20` | 1 | 컴포넌트 갤러리 창 |
| `EMBER_CR_GITHUB` | app | `ember/app/src/ui/home.rs:235` | 1 |  |
| `EMBER_CR_HOME_MODE` | app | `ember/app/src/ui/cr/home.rs:560` | 1 |  |
| `EMBER_CR_HOME_PICK` | app | `ember/app/src/ui/cr/home.rs:430` | 1 | project/model/mode/computer/mode_armed` opens one list at the start |
| `EMBER_CR_HOME_SUGGEST` | app | `ember/app/src/ui/cr/home.rs:457` | 1 |  |
| `EMBER_CR_IDE_MENU` | app | `ember/app/src/ui/cr/project.rs:890` | 1 |  |
| `EMBER_CR_NEWCHANNEL` | app | `ember/app/src/ui/cr/new_channel.rs:83` | 2 |  |
| `EMBER_CR_OWNER_DOOR` | app | `ember/app/src/ui/cr/channel_owner.rs:153` | 1 |  |
| `EMBER_CR_OWNER_SHEET` | app | `ember/app/src/ui/cr/channel_owner.rs:152` | 1 | 1`. The inputs are passed in so the gate is testable. |
| `EMBER_CR_PROJECT` | app | `ember/app/src/ui/cr/project.rs:188` | 1 |  |
| `EMBER_CR_PROJECT_EXPAND` | app | `ember/app/src/ui/cr/project.rs:194` | 1 |  |
| `EMBER_CR_PROJECT_SEARCH` | app | `ember/app/src/ui/cr/project.rs:197` | 1 | open` starts with the inline search row open. Debug builds only. |
| `EMBER_CR_PROJECT_SHEET` | app | `ember/app/src/ui/cr/add_computer.rs:97` | 4 | add-computer`: the sheet open with sample devices. |
| `EMBER_CR_QUERY` | app | `ember/app/src/ui/cr/search.rs:66` | 1 | 검색창 초기 값 |
| `EMBER_CR_QUESTION` | app | `ember/app/src/ui/cr/conversation.rs:435` | 2 | single/multi/secret/answered`: a sample question item for review |
| `EMBER_CR_QUESTION_FIRST` | app | `ember/app/src/ui/cr/conversation.rs:441` | 2 | 1` puts the sample before the approvals, so a narrow capture shows it. |
| `EMBER_CR_ROOM` | app | `ember/app/src/ui/cr/channels.rs:237` | 1 |  |
| `EMBER_CR_ROUTE` | app | `ember/app/src/ui/cr/agents.rs:253` | 11 | channels`, in debug builds only. |
| `EMBER_CR_ROUTINE` | app | `ember/app/src/ui/cr/routines.rs:500` | 1 |  |
| `EMBER_CR_ROUTINE_EDIT` | app | `ember/app/src/ui/cr/routines.rs:146` | 1 |  |
| `EMBER_CR_ROUTINE_RUN` | app | `ember/app/src/ui/cr/routines.rs:162` | 1 |  |
| `EMBER_CR_ROUTINE_RUN_AT` | app | `ember/app/src/ui/cr/routines.rs` | 1 |  |
| `EMBER_CR_SCROLL` | app | `ember/app/src/ui/cr/files.rs:512` | 4 | <dp/bottom/agents/tray/transfers/history>` for review captures: the toolkit |
| `EMBER_CR_SESSION_DRAWER` | app | `ember/app/src/ui/cr/session.rs:4391` | 1 |  |
| `EMBER_CR_SESSION_INFO` | app | `ember/app/src/ui/cr/session.rs:2376` | 1 |  |
| `EMBER_CR_SESSION_NEW_MEMBER` | app | `ember/app/src/ui/cr/session.rs:4395` | 1 |  |
| `EMBER_CR_SESSION_PROJECT` | app | `ember/app/src/ui/cr/session.rs:4377` | 1 |  |
| `EMBER_CR_SESSION_VCS` | app | `ember/app/src/ui/cr/session.rs:4402` | 1 |  |
| `EMBER_CR_SESSION_VIEW` | app | `ember/app/src/ui/cr/session.rs:4366` | 1 |  |
| `EMBER_CR_SESSION_WEB` | app | `ember/app/src/ui/cr/session.rs:4491` | 1 |  |
| `EMBER_CR_SHEET_SCROLL` | app | `ember/app/src/ui/cr/project.rs:1261` | 1 |  |
| `EMBER_CR_SHELL` | app | `ember/app/src/ui/cr/shell.rs:749` | 2 | 초기 테마(`light`, `dark`, `1`; `0`, 빈 값은 끔). `lib.rs:143`이 `unwrap_or(저장된 설정)`로 사용 |
| `EMBER_CR_SIZE` | app | `ember/app/src/lib.rs:122` | 2 | 1440x900`: the window's opening size, for capturing at 1440, 1024, 768, 390. |
| `EMBER_CR_VCS_COMMIT` | app | `ember/app/src/ui/cr/vcs.rs:2391` | 1 |  |
| `EMBER_CR_VCS_CONFLICT` | app | `ember/app/src/ui/cr/vcs.rs:1796` | 1 |  |
| `EMBER_CR_VCS_PR` | app | `ember/app/src/ui/cr/vcs.rs:3112` | 1 |  |
| `EMBER_CR_VCS_SECTION` | app | `ember/app/src/ui/cr/vcs.rs:4268` | 1 | 섹션 지정 |
| `EMBER_DATA_DIR` | app, client, server | `ember/app/src/config.rs:27` | 6 | overrides that directory (tests, portable installs). |
| `EMBER_DEBUGPY_PATH` | proxy | `ember/proxy/companion/extension.js:513` | 2 |  |
| `EMBER_DEMO_DATA` | app, server | `ember/app/src/demo.rs:32` | 8 | 1`: add a demo ChatGPT plan account with 14 days of usage (screenshots only) |
| `EMBER_DEMO_OSE` | app, server | `ember/app/src/demo.rs:60` | 2 | 데모 IDE 대상 |
| `EMBER_DEVICE` | node | `ember/node/src/bin/ember-term.rs:161` | 1 |  |
| `EMBER_EDITOR_COMPUTER` | app | `ember/app/src/ide.rs:128` | 1 |  |
| `EMBER_EDITOR_SERVER` | app | `ember/app/src/ide.rs:126` | 1 |  |
| `EMBER_EDITOR_TOKEN` | app | `ember/app/src/ide.rs:124` | 1 |  |
| `EMBER_ENROL_ALLOWED_HOSTS` | server | `ember/server/src/enrol_door.rs:57` | 1 | 허용 Host 이름 |
| `EMBER_ENROL_LISTEN` | app, server | `ember/app/src/ui/enrol_flow.rs:853` | 4 | is unset: no door, so no code is minted. |
| `EMBER_ENROL_LISTEN_ALLOW_REMOTE` | server | `ember/server/src/enrol_door.rs:55` | 2 | `1`이면 비루프백 허용 |
| `EMBER_ENROL_PUBLIC_URL` | app, server | `ember/app/src/ui/enrol_flow.rs:853` | 4 | 노드에 알려줄 URL, 호스트는 Host 허용 |
| `EMBER_ENROL_TRUSTED_PROXIES` | server | `ember/server/src/enrol_door.rs:56` | 1 | `X-Forwarded-For` 신뢰 프록시 IP 목록 |
| `EMBER_ENV_CLEAR` | server | `ember/server/src/session_shim.rs:71` | 1 |  |
| `EMBER_EXEC_BIN` | server | `ember/server/src/computers/mod.rs:1269` | 2 | the `ember-exec` shim for Claude Code on other computers (default: next |
| `EMBER_EXEC_FORWARD_ENV` | server | `ember/server/src/computers/shim.rs:48` | 2 |  |
| `EMBER_EXEC_NODE_TOKEN` | server | `ember/server/src/computers/shim.rs:42` | 2 |  |
| `EMBER_EXEC_NODE_URL` | server | `ember/server/src/computers/shim.rs:40` | 3 |  |
| `EMBER_EXEC_NON_TOOL` | server | `ember/server/src/computers/shim.rs:46` | 2 |  |
| `EMBER_EXEC_REMOTE_SHELL` | server | `ember/server/src/computers/shim.rs:44` | 2 |  |
| `EMBER_FALLBACK_INTERVAL_SECS` | server | `ember/server/src/computers/mod.rs:712` | 1 | values; unset or invalid (or zero) values keep the defaults (FR-X3). |
| `EMBER_FALLBACK_PROBES` | server | `ember/server/src/computers/mod.rs:711` | 1 |  |
| `EMBER_GEMINI_BIN` | server | `ember/server/src/agents/acp.rs:389` | 2 |  |
| `EMBER_GH_BIN` | node | `ember/node/src/git_github.rs:99` | 2 | (tests point it at a fake script). |
| `EMBER_GITHUB_CACHE_SECS` | server | `ember/server/src/api/integrations.rs:73` | 1 | changes the lifetime and `EMBER_GITHUB_DEADLINE_MS` the deadline |
| `EMBER_GITHUB_DEADLINE_MS` | server | `ember/server/src/api/integrations.rs:74` | 1 |  |
| `EMBER_GIT_MAX_OUTPUT_BYTES` | node | `ember/node/src/git.rs:198` | 1 |  |
| `EMBER_GIT_NETWORK_TIMEOUT_SECS` | node | `ember/node/src/git.rs:187` | 1 |  |
| `EMBER_GUEST_ALLOWED_HOSTS` | server | `ember/server/src/guest_door.rs:54` | 2 |  |
| `EMBER_GUEST_LISTEN` | server | `ember/server/src/enrol_door.rs:142` | 6 | the guest door (FR-T14), off when unset: a second listener that serves |
| `EMBER_GUEST_LISTEN_ALLOW_REMOTE` | server | `ember/server/src/guest_door.rs:53` | 2 |  |
| `EMBER_GUEST_PUBLIC_URL` | server | `ember/server/src/guest_door.rs:55` | 2 | name the hosts guests use. See `guest_door`. |
| `EMBER_GUEST_TRUSTED_PROXIES` | server | `ember/server/src/guest_door.rs:56` | 1 |  |
| `EMBER_HOSTED` | server | `ember/server/src/chatgpt/mod.rs:128` | 3 | 1` (or `true`) disables the feature; `EMBER_CHATGPT_REDIRECT_PORT` |
| `EMBER_HUB_RELAY_URL` | hub, node, server | `ember/hub/src/config.rs:12` | 3 | / [`HubConfig::with_relay`]: never replaced by discovery. |
| `EMBER_HUB_SYNC_DEVICES` | server | `ember/server/src/hub/mod.rs:52` | 2 |  |
| `EMBER_HUB_URL` | hub, node, server | `ember/hub/src/config.rs:10` | 8 | the darkpyonix.dev hub (default `https://api.darkpyonix.dev`, `off` disables); |
| `EMBER_IDE_COMPUTERS` | server | `ember/server/src/api/ide.rs:111` | 2 | list exists, exactly as before. |
| `EMBER_IDE_URL` | server | `ember/server/src/api/ide.rs:116` | 2 |  |
| `EMBER_IDLE_SECS` | server | `ember/server/src/main.rs:302` | 1 | release an agent process after this long without activity (default 300) |
| `EMBER_LETIFY_ADVERTISE` | transport | `ember/transport/src/config.rs:168` | 1 |  |
| `EMBER_LETIFY_OBSERVER` | transport | `ember/transport/src/config.rs:162` | 1 |  |
| `EMBER_LETIFY_QAD_LISTEN` | server, transport | `ember/transport/src/config.rs:159` | 3 | ), the relay listens on TCP `0.0.0.0:<port>` and the observer on UDP |
| `EMBER_LETIFY_RELAY_LISTEN` | server, transport | `ember/transport/src/config.rs:158` | 3 | `EMBER_LETIFY_QAD_LISTEN`: override role addresses |
| `EMBER_LISTEN` | server | `ember/server/src/enrol_door.rs:140` | 4 | listen address (default `127.0.0.1:8740`) |
| `EMBER_LOG` | app | `ember/app/src/lib.rs:42` | 1 | tracing 필터 |
| `EMBER_MOUNT` | server | `ember/server/src/computers/mount.rs:59` | 4 | ; otherwise they stay local). |
| `EMBER_MOUNT_CTL` | server | `ember/server/src/computers/mount.rs:65` | 2 |  |
| `EMBER_MOUNT_SHADOW` | server | `ember/server/src/computers/mount.rs:61` | 3 |  |
| `EMBER_MOUNT_TTL_MS` | server | `ember/server/src/computers/mount.rs:63` | 2 | sets the attribute cache lifetime (default 1000) |
| `EMBER_NODE_ALLOWED_PEERS` | node | `ember/node/src/transport.rs:34` | 2 | and `<state dir>/allowed-peers`: peer ids (ember servers) allowed |
| `EMBER_NODE_BIN` | server | `ember/server/scripts/real-server-smoke.sh` | 1 |  |
| `EMBER_NODE_CODEX_BIN` | node | `ember/node/src/exec_server.rs:39` | 2 | codex binary for `/exec-server` (default `codex` on `PATH`) |
| `EMBER_NODE_DENY` | node | `ember/node/src/config.rs:82` | 2 | colon-separated paths the file API refuses (default none), see |
| `EMBER_NODE_EGRESS` | node | `ember/node/src/egress.rs:163` | 3 | `EMBER_NODE_EGRESS_DENY`: the browser egress policy |
| `EMBER_NODE_EGRESS_DENY` | node | `ember/node/src/egress.rs:159` | 3 | denied egress destinations (`private`, `link-local`, `loopback`, |
| `EMBER_NODE_HUB_ALLOW_SERVERS` | node | `ember/node/src/hub.rs:41` | 2 | hub 계정의 main server 허용 |
| `EMBER_NODE_KEEP_PTY` | node, server | `ember/node/src/config.rs:77` | 4 | `0` disables PTY keepers (terminal sessions then end with the |
| `EMBER_NODE_LISTEN` | node, server | `ember/node/src/config.rs:137` | 3 | (default `127.0.0.1:8741`). |
| `EMBER_NODE_ROOTS` | node, server | `ember/node/src/config.rs:69` | 3 | colon-separated allowed roots (default `$HOME`). |
| `EMBER_NODE_SOCKS_LISTEN` | node, server | `ember/node/src/main.rs:85` | 3 | <addr>` also serves SOCKS5 on a TCP port, for direct use on a LAN. |
| `EMBER_NODE_STATE_DIR` | node, proxy, server | `ember/node/src/config.rs:127` | 7 | state directory (default `$HOME/.ember/node`). |
| `EMBER_NODE_TOKEN` | node, proxy, server | `ember/node/src/bin/ember-term.rs:301` | 8 | (non-empty): bearer token. When it is unset or empty, the `node_token` |
| `EMBER_NODE_TRANSPORT` | node, server | `ember/node/src/transport.rs:33` | 4 | `1` also serves the API over the peer-to-peer transport (service |
| `EMBER_NODE_URL` | node, proxy | `ember/node/src/bin/ember-term.rs:301` | 4 |  |
| `EMBER_OMP_BIN` | server | `ember/server/src/agents/acp.rs:388` | 2 |  |
| `EMBER_OSE_DATA_DIR` | server | `ember/server/src/computers/local_node.rs:51` | 2 | no `EMBER_DATA_DIR` and no usable HOME it is an error: a relative path |
| `EMBER_OSE_SERVER` | editor-conn, server | `ember/server/src/ose.rs:736` | 2 |  |
| `EMBER_PROJECT` | node, proxy | `ember/node/src/bin/ember-term.rs:312` | 3 |  |
| `EMBER_PUBLIC_URL` | server | `ember/server/src/api/ide.rs:122` | 2 |  |
| `EMBER_RELAY_URL` | hub, node, server, transport | `ember/transport/src/config.rs:177` | 7 | relay server(s) for the transport (overrides the hub's relay) |
| `EMBER_RUNTIME_TOKEN` | server | `ember/server/src/a2a/client.rs:143` | 5 |  |
| `EMBER_SCRIPTED_AGENT` | server | `ember/server/src/main.rs:129` | 2 | 1`: also offer the test agent (development only) |
| `EMBER_SCRIPTED_HOME` | server | `ember/server/src/accounts/mod.rs:77` | 1 |  |
| `EMBER_SERVER_BIN` | server | `ember/server/scripts/real-server-smoke.sh` | 1 |  |
| `EMBER_SERVER_RELAY` | server | `ember/server/src/transport.rs:35` | 3 | off`: disable the automatic letify relay and QAD roles |
| `EMBER_SERVER_RELAY_PORT` | server | `ember/server/src/transport.rs:33` | 2 | letify relay TCP and QAD UDP port (default 7443) |
| `EMBER_SERVER_TOKEN` | client, server | `ember/client/src/token.rs:179` | 2 | variable, else the `server-token` file in the data folder, else the |
| `EMBER_SERVER_UPDATE_BIN` | server | `ember/server/scripts/real-server-smoke.sh` | 1 |  |
| `EMBER_SERVER_URL` | app, server | `ember/app/src/config.rs:26` | 4 | the main server, default `http://127.0.0.1:8740`. |
| `EMBER_SESSION_ID` | server | `ember/server/src/a2a/mod.rs:572` | 2 | `EMBER_RUNTIME_TOKEN`) and instructions for the `ember-a2a` command, which |
| `EMBER_SESSION_MEM_LIMIT_MB` | server | `ember/server/src/agents/proc.rs:343` | 3 | ). Zero and unparsable values mean no limit. |
| `EMBER_SESSION_MEM_POLL_MS` | server | `ember/server/src/agents/proc.rs:345` | 1 |  |
| `EMBER_SESSION_SHIM` | server | `ember/server/src/agents/proc.rs:66` | 2 | off` keeps direct spawning. |
| `EMBER_SHIM_BIN` | server | `ember/server/src/agents/proc.rs:190` | 1 | `ember-shim` 경로 |
| `EMBER_SHIM_DRAIN_SECS` | server | `ember/server/src/session.rs:1092` | 1 |  |
| `EMBER_SHIM_LINGER_SECS` | server | `ember/server/src/session_shim.rs:206` | 1 |  |
| `EMBER_TERM_ID` | node | `ember/node/src/bin/ember-term.rs:301` | 2 |  |
| `EMBER_TERM_ORIGIN` | node | `ember/node/src/bin/ember-term.rs:153` | 1 |  |
| `EMBER_TERM_SHELL` | node | `ember/node/src/bin/ember-term.rs:139` | 1 |  |
| `EMBER_TOKEN_HOSTS` | app, client | `ember/client/src/token.rs:133` | 2 |  |
| `EMBER_TRANSPORT` | server | `ember/server/src/transport.rs:28` | 4 | 1`: bind the peer-to-peer transport (key in `<data dir>/transport.key`; |
| `EMBER_TRANSPORT_BACKEND` | transport | `ember/transport/src/config.rs:12` | 2 |  |
| `EMBER_URL` | server | `ember/server/src/a2a/client.rs:72` | 3 | names. It does not refuse a non-loopback host (an operator may publish a LAN |
| `EMBER_VSCODE_WINDOW` | node | `ember/node/src/bin/ember-term.rs:306` | 1 |  |
| `XMO_CHROME` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_EMBED` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_KB_HOLD` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_KB_INPUT` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_KB_SURFACE` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_PART_OF` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_PORTRAIT` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_UPSTREAM_HOST` | proxy | `ember/proxy/dpx/config.py:15` | 2 |  |
| `XMO_UPSTREAM_PORT` | proxy | `ember/proxy/dpx/config.py:16` | 2 |  |
| `XMO_VIEW_SKIP` | proxy | `ember/proxy/static/overlay.js` | 1 |  |
| `XMO_VIEW_SOURCES` | proxy | `ember/proxy/static/overlay.js` | 1 |  |

