# 모듈: server-agents

- 경로: `ember/server/src/agents/` (`mod.rs`, `proc.rs`, `claude_code.rs`, `codex.rs`, `antigravity.rs`, `acp.rs`, `scripted.rs`)와 `ember/server/src/history/` (`mod.rs`, `claude_code.rs`, `codex.rs`). 테스트 코드인 `agents/acp/tests.rs`(1,074줄)와 `agents/acp/fake_agent.rs`(422줄)는 `acp.rs:2215-2218`에서 `mod fake_agent; mod tests;`로 붙는 것만 확인했고 읽지 않았다.
- 규모: 파일 10개(+테스트 2개) / 약 9,100줄 (modules.md 기준 10개 합계)
- 레이어: 비즈니스 로직 (에이전트 CLI 어댑터, 프로세스 shim 런타임, 과거 기록 가져오기)
- 한 줄 책임: 수정하지 않은 에이전트 CLI(Claude Code, Codex, Antigravity, ACP 에이전트)를 각자의 비대화형 프로토콜로 띄우고, 출력을 정규화된 `AgentEvent`로 바꾸며, 승인과 질문 답을 CLI로 돌려보낸다.
- 의존하는 모듈: [server-core](server-core.md) (`AgentEvent`, `ApprovalDecision`, `approval_policy`, `Question`, `Store::shim_offset`, `session_shim::*`), [node-git](node-git.md) 쪽 `ember_node::client::NodeClient` (ACP의 원격 `fs/*`, `terminal/*`), `crate::browser::agent::toml_str` (`codex.rs:375`)
- 이 모듈을 쓰는 모듈: [server-core](server-core.md) (`session.rs`가 `AgentAdapter`를 호출, `main.rs:123-136`이 어댑터 조립), `accounts`, `members`, `a2a`, `computers`, `fork`, `usage`, `mcp`, `projects`, `schedules`, `api` 등 (`AgentKind`를 `grep`으로 확인한 파일 24개)

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `AgentAdapter` | trait | `ember/server/src/agents/mod.rs:320` | 에이전트 종류 하나. `start`가 프로세스를 띄우고 `Box<dyn AgentRun>`을 돌려준다 |
| `AgentRun` | trait | `ember/server/src/agents/mod.rs:372` | 실행 중인 에이전트. `send`, `answer`, `answer_question`, `decline_question`, `interrupt`, `shutdown`, `restore_pending_*` |
| `AgentKind` | enum | `ember/server/src/agents/mod.rs:33` | `ClaudeCode`, `Codex`, `Antigravity`, `Scripted`, `Acp(AcpName)`. 문자열(`"claude-code"` 등)로 직렬화 (`mod.rs:144-155`) |
| `AcpName` | struct | `ember/server/src/agents/mod.rs:50` | 설정으로 정해지는 ACP 이름. 프로세스 전역 레지스트리에 `Box::leak`으로 들여온다 (`mod.rs:87`) |
| `StartRequest`, `ForkFrom`, `NativeFork`, `McpServer`, `RemoteExec` | struct/enum | `mod.rs:159`, `:202`, `:212`, `:223`, `:251` | 시작 요청과 부속 타입 |
| `Detected`, `Probe`, `resolve_executable` | struct/함수 | `mod.rs:261`, `:269`, `:289` | CLI 설치 탐지 (FR-A6) |
| `proc::spawn_agent`, `reattach_agent`, `AgentCommand`, `AgentProc`, `ProcHandle` | 함수/struct/enum | `agents/proc.rs:275`, `:262`, `:198`, `:224`, `:235` | 에이전트를 띄우는 유일한 곳 (직접 자식 또는 shim) |
| `proc::{ShimRuntime, install_runtime, clear_runtime, shim_enabled, require_commit, release_commit, release_commit_of, CommitGate, live_shim_sessions, drain_surviving_lines, shim_died, find_shim_bin, mem_limit_bytes, SESSION_ENV}` | 혼합 | `proc.rs:46`, `:56`, `:60`, `:65`, `:145`, `:152`, `:160`, `:74`, `:577`, `:596`, `:180`, `:189`, `:217`, `:39` | shim 런타임 |
| `ClaudeCodeAdapter` (+`mcp_config`, `cleanup_stale_mcp_files`) | struct/함수 | `agents/claude_code.rs:84`, `:282`, `:227` | Claude Code |
| `CodexAdapter` (+`PROXY_BASE_ENV`, `PROXY_KEY_ENV`, `proxy_config_args`) | struct/상수/함수 | `agents/codex.rs:82`, `:304`, `:306`, `:310` | Codex |
| `AntigravityAdapter`, `HookBroker`, `router`, `HOOK_ROUTE` 등 | struct/함수 | `agents/antigravity.rs:211`, `:600`, `:641`, `:139` | Antigravity와 훅 수신 라우트 |
| `AcpAdapter`, `AcpConfig`, `configs_from_env`, `parse_configs`, `GEMINI_ENV_ALLOW` | struct/함수 | `agents/acp.rs:397`, `:210`, `:380`, `:320`, `:190` | ACP |
| `ScriptedAdapter`, `ScriptedForkAdapter` | struct | `agents/scripted.rs:16`, `:46` | 테스트용 가짜 에이전트 |
| `history::import_file`, `to_events`, `Transcript`, `Message`, `Role` | 함수/struct | `history/mod.rs:106`, `:185`, `:22`, `:42`, `:33` | 에이전트 자체 기록 파일을 이벤트로 |

## AgentAdapter와 AgentRun 계약

`ember/server/src/agents/mod.rs:320-368`, `:372-411`.

| 메서드 | 기본값 | 뜻 |
|---|---|---|
| `kind()` | 필수 | 종류 |
| `binary()` | `None` (`mod.rs:324`) | 탐지에 쓰는 실행 파일 |
| `detect()` | 필수 | 설치 여부와 버전. 없는 것은 에러가 아니다 (`mod.rs:329`) |
| `native_fork()` | `NativeFork::None` (`mod.rs:333`) | 에이전트 자체 포크. Claude `Latest`, Codex `AtTurn`, ACP `Latest`, Antigravity 없음 |
| `rejoins_shim()` | `false` (`mod.rs:339`) | 서버가 죽어도 산 에이전트에 그대로 다시 붙을 수 있나. Claude, Antigravity만 `true` |
| `drains_shim()`, `drain_turn_end()`, `translate_drained()` | `false`/`false`/빈 목록 (`mod.rs:347-359`) | 재접속 불가 에이전트의 마지막 출력을 읽어 이벤트로 바꾼 뒤 멈춘다. Codex, ACP만 `true` |
| `start(req, events)` | 필수 | 이벤트는 `mpsc::Sender<AgentEvent>`로 프로세스가 끝날 때까지 보낸다 |
| `AgentRun::send` | 필수 | 사용자 메시지 전달. 어댑터는 `UserMessage`를 직접 내지 않는다 (세션이 기록, `mod.rs:373-375`) |
| `AgentRun::answer(approval_id, decision)` | 필수 | 승인 응답 (`ApprovalDecision::{AllowOnce, AllowAlways, Deny}`) |
| `answer_question`, `decline_question` | `bail!("this agent does not support questions")` (`mod.rs:392-404`) | 질문은 Claude Code만 구현 |
| `restore_pending_approvals/questions` | 무동작 (`mod.rs:384`, `:388`) | 이전 서버가 남긴 대기 항목 복원. Claude Code만 구현 |
| `interrupt`, `shutdown` | 필수 | 중단은 어댑터가 `TurnEnded{Interrupted}`를 낸다 |

### 환경 변수와 설정을 읽는 곳 (요약)

| 이름 | 위치 | 용도 | 기본값 |
|---|---|---|---|
| `EMBER_CLAUDE_BIN` | `claude_code.rs:95` | Claude 실행 파일 | `claude` (PATH) |
| `MCP_TIMEOUT` | `claude_code.rs:273` | 이미 설정돼 있으면 어댑터가 덮어쓰지 않는다. 없으면 MCP 시작 대기(ms)를 어댑터가 넣는다 | 없음 |
| `EMBER_CODEX_BIN` | `codex.rs:95` | Codex 실행 파일 | `codex` |
| `EMBER_CODEX_PROXY_BASE_URL`, `EMBER_CODEX_PROXY_KEY` | `codex.rs:304`, `:306` | 모델 프록시. 요청 env에 있으면 `-c` 재정의로 바뀐다 (키 값은 인자에 안 들어감) | 없음 |
| `EMBER_AGY_BIN`, `EMBER_AGY_SANDBOX` | `antigravity.rs:235`, `:239` | agy 실행 파일, `=1`이면 `--sandbox` | `agy`, 꺼짐 |
| `GOOGLE_GEMINI_BASE_URL`, `GEMINI_API_KEY`, `GOOGLE_API_KEY` | `antigravity.rs:144`, `:146`, `:149` | 프록시 모드 (요청 env에 있을 때 `--settings`가 붙는다) | 없음 |
| `EMBER_ACP_AGENTS`, `EMBER_ACP_AGENTS_FILE` | `acp.rs:381` | ACP 에이전트 목록 (JSON) | 없음 |
| `EMBER_OMP_BIN`, `EMBER_GEMINI_BIN` | `acp.rs:388-389` | 프리셋 바이너리 | `omp`, `gemini` |
| `EMBER_SESSION_SHIM` | `proc.rs:66` | `off`면 shim 없이 직접 자식 | 켜짐 |
| `EMBER_SHIM_BIN` | `proc.rs:190` | `ember-shim` 경로 | 서버 실행 파일 옆 `ember-shim` |
| `EMBER_SESSION_MEM_LIMIT_MB`, `EMBER_SESSION_MEM_POLL_MS` | `proc.rs:341-345` | 세션 메모리 한도(MiB), 폴링 간격 | 한도 없음 |
| `EMBER_SESSION_ID` | `proc.rs:39` | `Sessions::ensure_live`가 요청 env에 넣는 세션 id. `spawn_agent`가 읽고 지운다 (`proc.rs:277`) | |
| `EMBER_SCRIPTED_AGENT` | `ember/server/src/main.rs:129` | `=1`이면 Scripted 어댑터 등록 | 꺼짐 |

## 어댑터별 실행 방식

### 한눈에 비교

| | Claude Code | Codex | Antigravity | ACP | Scripted |
|---|---|---|---|---|---|
| 프로세스 | 세션당 장수 프로세스 1개 | 세션당 장수 `app-server` 1개 | 턴마다 프로세스 1개 | 세션당 장수 1개 | 없음 |
| 프로토콜 | stream-json (한 줄 JSON) | JSON-RPC (`jsonrpc` 필드 없음) | `--output-format stream-json` | JSON-RPC, ACP 버전 1 | 인-프로세스 |
| 승인 | stdout `control_request`/`can_use_tool`, stdin `control_response` | 서버 요청 `*/requestApproval` | 에이전트의 PreToolUse 훅이 로컬 HTTP로 호출 | `session/request_permission` | `ApprovalRequested` 한 번 |
| 질문 | `AskUserQuestion`을 지원 | 없음 | 없음 | 없음 | 없음 |
| shim 재접속 | `reattachable: true` (`claude_code.rs:371`) | `false` + drain (`codex.rs:213`) | 턴 프로세스에 한해 `true` (`antigravity.rs:1082`) | `false` + drain (`acp.rs:593`) | 해당 없음 |

### Claude Code (`ember/server/src/agents/claude_code.rs`)

**실행 인자** (`args_with`, `claude_code.rs:106-160`, 순서 그대로):

| 줄 | 인자 | 조건 |
|---|---|---|
| `107-116` | `--print --input-format stream-json --output-format stream-json --verbose --include-partial-messages --permission-prompt-tool stdio` | 항상 |
| `120-121` | `--model <M>` | `req.model` |
| `124-125` | `--append-system-prompt=<text>` (등호 형태, `-`로 시작해도 플래그로 읽히지 않게) | `req.instructions` |
| `129-130` | `--resume=<id>` | `req.resume_native_id` |
| `132-135` | `--resume=<부모 id> --fork-session` | `req.fork_from` (resume이 없을 때) |
| `142-145` | `--allowedTools <이름...>` (가변 인자라 반드시 다른 플래그 앞이나 끝) | `allowed_tool_ok`를 통과한 정확한 `mcp__...` 이름만 (`claude_code.rs:162-172`). 와일드카드, 공백, 비 MCP 규칙은 경고 후 버린다 |
| `150-155` | `--mcp-config=<파일 경로>` 또는 `--mcp-config=<JSON>` | MCP 서버가 있을 때. env가 있는 서버가 하나라도 있으면(`mcp_needs_file`, `:174`) 개인 파일(`PrivateConfigFile`, `:179-210`, `std::env::temp_dir()`에 만든다, `:359-360`) |

**환경 변수**: 요청 `req.env`를 그대로 얹고 (`:362-363`), MCP 시작 시간이 있으면 `MCP_TIMEOUT`(ms)을 추가 (`:271-277`). `cwd`는 `req.cwd`이고 디렉터리가 아니면 시작을 거부한다 (`:349-354`). 에이전트 자체가 읽는 `CLAUDE_CONFIG_DIR` 등은 계정 모듈이 `req.env`로 넣는다 (`ember/server/src/accounts/mod.rs:16`, 본 모듈은 읽지 않는다).

**출력 해석** (`LineParser::parse`, `claude_code.rs:910-1062`): 한 줄 JSON을 `type`으로 분기한다.

| `type` / 조건 | 줄 | 결과 |
|---|---|---|
| `system` + `init` | `926-935` | `NativeSession{native_id}` (id가 바뀔 때만 한 번) |
| `stream_event` / `text_delta` | `937-948` | `AssistantDelta` |
| `assistant` 블록 `text` / `tool_use` | `950-969` | `AssistantMessage` / `ToolCall` |
| `user` 블록 `tool_result` | `971-981` | `ToolResult` (`content`는 문자열이거나 블록 목록, `tool_result_text` `:1065`) |
| `result` | `983-1021` | `Usage`(입력 = input + cache 생성 + cache 읽기 토큰), `TurnEnd{error}`. `is_error` 이거나 `subtype`이 `error`로 시작하면 실패. 메시지 우선순위 `result` > `errors` > `claude turn failed (<subtype>)` |
| `control_request` / `can_use_tool` | `1023-1047` | `AskUserQuestion`이고 `parse_questions`가 성공하면 `QuestionRequest`, 아니면 `PermissionRequest` (`needs_person` = 프레임의 `requires_user_interaction == true`) |
| `control_request` 그 밖 | `1048-1051` | `UnsupportedRequest` (아래 오류 응답) |
| `rate_limit_event` | `1058-1067` | `status == "rejected"`일 때만 `RateLimited{resets_at(ms), "Claude <type> limit reached"}` |
| `control_cancel_request` | `1073-1076` | `CancelRequest` |
| 비 JSON, 빈 줄, 모르는 type | `912-918`, `1078` | 무시 |

`read_stdout`(`:579-690`)가 `Parsed`를 이벤트로 바꾼다. `TurnEnd`는 보류 중이던 승인과 질문을 모두 비운다 (`:642-651`). 인터럽트 중이면 `Interrupted`, 오류면 `Error` 뒤 `Failed` (`:654-664`). stdout이 닫혔는데 턴이 진행 중이고 종료 요청이 없었으면 `Error{"claude exited during a turn"}` 뒤 `TurnEnded` (`:680-690`).

**입력 (stdin)**: 사용자 메시지는 `{"type":"user","message":{"role":"user","content":text},"parent_tool_use_id":null,"session_id":""}` (`:712-717`).

**승인 흐름**:
1. `PermissionRequest`가 오면 `approval_policy(tool, needs_person).remember_always`이고 이미 `AllowAlways`로 기억한 도구면 어댑터가 이벤트 없이 바로 `allow`를 stdin에 쓴다 (`:611-624`). 아니면 `st.pending`에 넣고 `ApprovalRequested{approval_id = request_id}` (`:611-628`).
2. `AgentRun::answer` (`:722-750`)가 대기 항목을 꺼내 `AllowOnce/AllowAlways`는 `allow_response`(`{"type":"control_response","response":{"subtype":"success","request_id":..,"response":{"behavior":"allow","updatedInput":<원 input>}}}`, `:450-459`), `Deny`는 `deny_response`(`behavior:"deny"`, 메시지 `The user denied <tool> in Ember.`, `:560-569`, `:745`)를 쓴다.
3. `AllowAlways`는 `remember_always`가 참인 도구만 `always_allowed`에 넣는다 (`:735-737`). 사람이 필요한 도구(질문, 계획)는 매번 다시 묻는다.
4. CLI가 `control_cancel_request`로 철회하면 `PromptWithdrawn{prompt_id}` (`:636`, `withdraw_prompt` `:406`). 가지고 있지 않은 id면 아무것도 내지 않는다.

**질문 흐름**: `AskUserQuestion`의 `input.questions[]`를 `parse_questions`(`:513`)로 `Question`으로 바꿔 `QuestionAsked{question_id = request_id}`를 낸다 (`:590-598`). `answer_question`(`:751`)은 `question_reply`(`:488`)로 원 입력에 `answers`(질문 문장이 키, 다중 선택은 `", "`로 합침)를 더한 `allow`를 쓴다. `decline_question`(`:765`)은 `answers` 없는 `allow`, 그러면 CLI가 모델에게 답이 없었다고 알린다. 질문에는 시간 제한이 없다 (모듈 주석 `:57-58`).

**중단과 종료**: `interrupt`(`:807-842`)는 `{"type":"control_request","request_id":"ember_<n>_<uuid>","request":{"subtype":"interrupt"}}`를 쓰고, `INTERRUPT_GRACE` 10초(`:80`) 안에 `result`가 없으면 `SIGINT` (`:859`, Windows에서는 무동작 `:867`). `shutdown`(`:844-856`)은 stdin을 닫고 `SHUTDOWN_GRACE` 5초(`:82`) 뒤 강제 종료.

**shim 재접속 복원**: `restore_pending_approvals/questions` (`:777-805`)는 `reattached`일 때만 저장소의 대기 항목으로 상태를 다시 채우고 `turn_active = true`로 둔다.

**기타**: `detect`는 `<bin> --version`, 15초 제한 (`:321-340`). `cleanup_stale_mcp_files` (`:227`)는 1시간 넘은 `0600` 개인 MCP 파일을 지운다 (`MIN_AGE`, `:231`).

### Codex (`ember/server/src/agents/codex.rs`)

**실행 인자** (`app_server_args`, `codex.rs:322-349`): 첫 인자 `app-server`. 이어서 `-c <key=value>` 재정의만 쓴다.

| 줄 | 인자 | 조건 |
|---|---|---|
| `324-326` | `-c model_providers.ember_proxy={name="ember-proxy", base_url=<TOML>, env_key="EMBER_CODEX_PROXY_KEY", wire_api="responses"}`, `-c model_provider="ember_proxy"` (`proxy_config_args` `:310-316`) | 요청 env에 `EMBER_CODEX_PROXY_BASE_URL`이 있을 때 |
| `330-333` | `-c mcp_servers.<name>.command="…"`, `-c mcp_servers.<name>.args=[…]` | MCP 서버마다 |
| `334-337` | `-c mcp_servers.<name>.startup_timeout_sec=<n>` | 시작 제한이 있을 때 |
| `338-342` | `-c mcp_servers.<name>.env_vars=[이름들]` | env가 있을 때. 값은 인자에 쓰지 않고 이름만 쓴다 |

MCP 서버 env의 값은 앱 서버 프로세스 환경으로 전달된다 (`mcp_process_env`, `:351-372`). 두 서버가 같은 변수를 서로 다른 값으로 쓰면 뒤의 서버를 빼고 경고한다 (`:357-364`).

**스레드 파라미터** (`thread_params`, `:112-129`): `cwd`, `model`, `approvalPolicy`(`with_approval_policy`로 준 것), `sandbox`(`with_sandbox`), `developerInstructions`(`req.instructions`). 기본으로는 Codex 사용자 설정이 그대로 적용된다 (FR-A4).

**시작 순서** (`start`, `:191-301`): 프로세스를 `reattachable: false`로 띄운다 (`:208-216`) → `initialize` (원격이면 `experimentalApi: true`, `:383-395`) → 알림 `initialized` → 원격이면 `environment/add` → 세 갈래: `thread/fork`(+선택적 `thread/turns/list`로 `lastTurnId`, `excludeTurns: true`; 원격에서는 거부, `:244-266`), `thread/resume`(`threadId`, `excludeTurns`, `:267-273`), `thread/start` (`:274-276`). 응답의 `thread.id`로 `NativeSession`을 낸다 (`:278-280`). 요청 시간 제한은 120초 (`:78`).

**메시지**: 진행 중인 턴이 있으면 `turn/steer{threadId, input, expectedTurnId}`, 실패하거나 턴이 없으면 `turn/start` (`:560-598`). `turn/start` 실패는 `Error` 뒤 `TurnEnded{Failed}`를 낸다 (`:590-595`).

**출력 해석** (`Mapper`, `:662-910`):

| 알림 | 줄 | 결과 |
|---|---|---|
| `turn/started` | `691-697` | 활성 턴 기록 |
| `item/agentMessage/delta` | `700-705` | `AssistantDelta` |
| `item/started`, `item/completed` | `706-707`, `:803-836` | 도구성 항목(`commandExecution`, `fileChange`, `mcpToolCall`, `dynamicToolCall`)은 `ToolCall`/`ToolResult`, `agentMessage`는 `AssistantMessage` |
| `thread/tokenUsage/updated` | `708-716` | 턴 합계를 쌓았다가 `turn/completed`에서 `Usage` 한 번 |
| `error` (`willRetry != true`) | `717-737` | `codexErrorInfo`가 `usageLimitExceeded`나 `rateLimitExceeded`면 `RateLimited` 후 `Error` |
| `account/rateLimits/updated` | `738-742`, `:749-777` | 창이 100% 이상이거나 `rateLimitReachedType`이 있으면 `RateLimited` (한 번만) |
| `serverRequest/resolved` | `743-747` | 해당 승인 잊기 |
| `turn/completed` | `779-801` | `status`가 `interrupted`/`failed`/그 밖. 실패인데 `Error`가 아직 없으면 `Error` 추가 후 `Usage`, `TurnEnded` |
| 기타 | `748` | 무시 |

**승인 흐름**: 서버가 요청(메서드와 `id`가 있는 줄)을 보내면 `on_server_request` (`:838-898`)가 `ApprovalRequested{needs_person: false}`로 바꾼다.

| 요청 메서드 | 줄 | `tool` |
|---|---|---|
| `item/commandExecution/requestApproval` | `844-849` | `command` |
| `item/fileChange/requestApproval` | `850-862` | 앞서 본 항목의 이름, 없으면 `file_change` |
| `item/permissions/requestApproval` | `863-868` | `permissions` |
| `execCommandApproval` (옛 방식) | `869-880` | `command` |
| `applyPatchApproval` (옛 방식) | `881-886` | `file_change` |
| 그 밖 | `887` | JSON-RPC 에러 `-32601` `ember does not handle <method>` 를 돌려준다 (`read_loop` `:495-505`) |

`AgentRun::answer`(`:600-616`)가 `approval_response`(`:911-943`)로 결과를 만든다. `Command`/`FileChange`: `AllowOnce` → `accept`, `AllowAlways` → `acceptForSession`(서버가 `availableDecisions`에서 허용할 때만, 아니면 `accept`), `Deny` → `decline`(허용 목록에 없으면 `cancel`). `Permissions`: 거부는 `{permissions:{}, scope:"turn"}`, 허용은 요청한 권한 그대로, 범위는 `AllowAlways`면 `session`, 아니면 `turn`. 옛 방식: `approved`, `approved_for_session`, `{denied:{rejection:"Denied by the user in Ember."}}`.

**질문**: 없다. `answer_question`은 기본 구현이라 `bail!`한다.

**중단과 종료**: `turn/interrupt{threadId, turnId}` (`:618-626`). 종료는 stdin을 닫고 `EXIT_GRACE` 5초 (`:628-640`, `:80`). `start`는 exec-server 원격(`req.remote`)을 지원하는 유일한 어댑터다 (`:200-206`).

**재시작 복구(drain)**: `drains_shim() == true` (`:143`). `drain_turn_end`는 `turn/completed` 알림이나 클라이언트에게 온 요청을 만나면 `true` (`:147-155`). `translate_drained`는 알림만 `Mapper`로 바꾼다 (`:157-170`).

### Antigravity (`ember/server/src/agents/antigravity.rs`)

**한 턴의 실행 인자** (`turn_args`, `antigravity.rs:247-283`, 턴마다 새 프로세스):

| 줄 | 인자 | 조건 |
|---|---|---|
| `257-262` | `-p <prompt> --output-format stream-json --add-dir <세션 루트>` (프롬프트가 `-`로 시작하면 앞에 공백) | 항상 |
| `265-267` | `--sandbox` | `EMBER_AGY_SANDBOX=1` |
| `269-271` | `--dangerously-skip-permissions` | `Policy::Gated` (고정된 버전일 때) |
| `273-275` | `--conversation=<id>` | 대화가 있을 때 (`send`가 `native_id` 또는 `resume_native_id`를 쓴다, `:1060-1064`) |
| `276-278` | `--model <M>` | `req.model` |
| `:1074` | `proxy_args`: `--settings {"modelProvider":"gemini"}` (`:154-160`) | 요청 env에 `GOOGLE_GEMINI_BASE_URL`이 비어 있지 않을 때 |

환경 변수는 `req.env`만 얹는다 (`:1075-1076`, 에이전트 자체의 `~/.gemini` 고정, 계정 분리 미지원 `:123-125`). 프로세스는 `reattachable: true`로 띄운다 (`:1078`).

**턴 전 점검**: ① 실행당 한 번 `agy --version`을 `PINNED_VERSION = "1.2.16"`(`:163`)과 비교한다. 다르면 `Policy::ReadOnly`, `--dangerously-skip-permissions` 없음, 훅도 읽기 전용, `Notice` 한 건 (`check_version` `:969-1001`, `policy_for_version` `:285`). ② 매 턴 `agy -p /hooks --output-format json --add-dir <루트>`가 `HOOK_NAME = "ember-approvals"`(`:141`)를 `PreToolUse`, 매처 `*`, 활성으로 나열해야 한다. 아니면 턴을 거부하고 `Antigravity did not load Ember's approval hook (...), so its tools cannot be gated; refusing to run.` (`check_hook` `:1003-1027`, `hook_listing` `:295`). 건너뛰는 스위치는 없다. 보고된 `timeout_seconds`가 `HOOK_TIMEOUT_SECS = 3600`(`:166`)과 다르면 승인 제한이 20초로 줄어든다 (`:1049-1056`, `CAPPED_APPROVAL_TIMEOUT` `:174`).

**세션 루트** (`write_session_root`, `:568-598`): `<data dir>/agy/sessions/<uuid>/` 아래 `.agents/hooks.json`, `.agents/ember-hook.sh`(0700), `.agents/rules/ember.md`(`instructions` 포함), `.agents/mcp_config.json`(0600, MCP 서버가 있을 때만, 없으면 삭제). 대화 id와 루트의 대응은 `<data dir>/agy/conversations/<id>`에 저장한다 (`session_root` `:419-430`, `remember_root` `:432`). 사용자의 `~/.gemini`나 프로젝트에는 쓰지 않는다.

**출력 해석** (`LineParser`, `:1299-1470`): 한 줄 JSON을 `event`로 분기한다.

| `event` | 줄 | 결과 |
|---|---|---|
| `init` | `1331-1337` | `NativeSession{conversation_id}` |
| `step_update` | `1338`, `:1385-1440` | `text_delta` → `AssistantDelta`. `step_type == "tool"`이면 처음 보일 때 `ToolCall`(id = `call_id(conv, step_index)`, `:687`), `ACTIVE` 아닌 상태가 되면 `ToolResult` (`error.message`가 있으면 그것이 출력, `state != "DONE"`이거나 오류가 있으면 `is_error`). 단계별 `usage`는 마지막 값이 이긴다 |
| `result` | `1339-1375` | `Usage`(단계 합), `response`가 있으면 `AssistantMessage`, `denied_actions`가 있으면 `Notice "Antigravity refused: ..."`, `status != "SUCCESS"`이면 실패(`error` > `error_message` > `Antigravity turn ended with status <s>`) |

stderr는 `StderrErrors`(`:1451-1500` 부근)가 `AGY_ERROR: {...}`와 `error:` 줄을 모으고, `result` 없이 끝났을 때만 쓴다 (`Turn::run` `:1213-1225`). 비율 제한 감지는 `rate_limit()` (`:1473`). 결과가 오면 프로세스가 아직 살아도 바로 턴을 끝낸다 (`:1205-1209`). 프로세스가 `result` 없이 끝나면 `agy exited without a result` 등의 `Error` (`:1218-1224`).

**승인 흐름 (핵심 차이)**: 출력 스트림이 아니라 agy의 `PreToolUse` 훅을 통해 흐른다.
1. agy가 도구를 쓰기 전 `ember-hook.sh`를 실행한다 (`hook_script` `:503-527`). 스크립트는 `curl --max-time 3540 -X POST -H "Authorization: Bearer <세션 토큰>" --data-binary @- <훅 URL>`로 페이로드를 보내고, 응답이 정확히 `{"decision":"allow"}`이거나 `{"decision":"deny"...`로 시작할 때만 그대로 출력하며, 그 밖에는 고정된 `deny`를 출력한다. 항상 `exit 0`. 토큰은 환경 변수가 아니라 이 파일 안에 있다.
2. 서버 쪽 `router` (`:641`)가 `POST /api/agents/antigravity/hook`(`HOOK_ROUTE`, `:139`)를 받아 `Authorization: Bearer`로 `HookBroker::handle`을 부르고, 모르는 토큰이면 401 `{"error":"unknown session","code":"unauthorized"}` (`:645-661`). 로컬 리스너에만 붙여야 한다 (`:638-640`).
3. `RunApprovals::decide` (`:791-880`)가 순서대로 판단한다: 턴이 열려 있지 않으면 deny → 인자에 세션 루트 경로가 나오면 deny → 읽기 전용 도구(`READ_ONLY_TOOLS`, `:186-199`)이고 경로가 작업공간 또는 agy의 `brain/` 안이면 allow → `ReadOnly` 정책이면 deny → 이 실행에서 `AllowAlways`한 도구면 allow → 사용자에게 `ApprovalRequested` 전송 후 대기 (`APPROVAL_TIMEOUT = 3600-120`초, `:171`). 시간 초과 시 `ApprovalResolved{Deny}`와 `Notice "Approval for <tool> timed out; retry."`.
4. `AgentRun::answer` (`:1091`, `RunApprovals::answer` `:882`)가 대기 중인 oneshot으로 결정을 보낸다. 훅은 `{"decision":"allow"|"deny","reason"?}`를 돌려준다 (`allow_reply`, `deny_reply` `:691-700`). 턴 종료, 인터럽트, 실행 종료는 대기 중인 모든 승인을 deny로 처리한다 (`cancel_all` `:898`, `close` `:786`).

**질문**: 없다 (기본 구현이 `bail!`).

**중단과 종료**: `interrupt`는 훅을 닫고(대기 중인 승인은 deny) `SIGINT`, 5초 뒤 `SIGKILL` (`:1099-1115`, `:1280`). 새 턴은 이전 프로세스가 끝나기를 30초 기다린 뒤 죽인다 (`PREVIOUS_EXIT_GRACE`, `:179`, `:1031-1041`). 지원하지 않는 것: 원격 컴퓨터(`:366-369`), 계정, 진행 중 턴 조향 (`:123-126`).

### ACP (`ember/server/src/agents/acp.rs`)

**실행 인자**: 설정(`AcpConfig`, `:210-227`)에서 온다. `process_args_with` (`:286-297`): `config.args` + (모델이 있으면 `model_args`의 `{model}` 치환) + (지시문이 있고 `instructions_args`가 비어 있지 않으면 `{instructions}` 치환).

| 프리셋 | 줄 | 명령 | 인자 |
|---|---|---|---|
| `omp` | `233-243` | `omp` (`EMBER_OMP_BIN`) | `acp`, 모델 `--model {model}`, 지시문 `--append-system-prompt {instructions}` |
| `gemini` | `247-257` | `gemini` (`EMBER_GEMINI_BIN`) | `--acp` (`:128`), 모델 `-m {model}`, 지시문 인자 없음(첫 프롬프트 앞에 붙인다, `:2162-2167`) |

사용자 정의 에이전트는 `EMBER_ACP_AGENTS`(JSON 목록, 문자열은 프리셋 이름, 객체는 프리셋을 덮어쓰거나 새 정의)나 `EMBER_ACP_AGENTS_FILE`로 준다 (`configs_from_env` `:380-392`, `parse_configs` `:320-376`). 이름 규칙 `AcpName::valid` (`mod.rs:65-72`), 중복 이름은 에러. 프리셋은 목록에 이름을 적어야만 제공된다 (opt-in).

**환경 변수**: `child_env` (`:261-273`). `omp`와 사용자 정의는 서버 환경 전체를 상속한다 (`EnvPolicy::Inherit`). `gemini`는 `EnvPolicy::Allowlist(GEMINI_ENV_ALLOW)`(`:190-199`)라서 `ENV_CLEAR` 표시를 넣고 허용 목록(HOME, PATH, XDG_*, GEMINI_API_KEY, GOOGLE_*, 프록시 변수 등)에 있는 값만 서버 환경에서 복사한다. 그 뒤 config의 `env`와 요청의 `req.env`가 얹힌다 (`:584-585`). `--acp` 플래그를 모르는 옛 gemini는 시작 후 2초 안에 실패하고 단독 실행이 "알 수 없는 옵션"을 내면 `--experimental-acp`로 한 번 재시도한다 (`:468-514`, `rejects_acp_flag` `:684`). 프리셋 자체 인자일 때만.

**시작 순서** (`connect`, `:718-860`): `initialize{protocolVersion:1, clientCapabilities:{fs:{readTextFile,writeTextFile}, terminal:true}, clientInfo}` (`:875-886`). 다른 `protocolVersion`이면 `the agent speaks ACP protocol version ...; Ember supports 1`로 거부 (`:753`). 이어서 `session/fork`(`fork_from`, 지원 광고가 없으면 실패해서 세션 계층이 대화 복사로 대체, `:762-780`) → `session/resume`(광고했을 때, `:783-794`) → `session/load`(`loadSession` 광고 시. 대화 전체 재생 `session/update`는 버린다, `:795-812`) → 둘 다 없으면 `Notice "This agent cannot resume ACP session ..."` 후 `session/new`. `session/new`가 인증 오류면 세션을 못 얻은 채로 시작하고 첫 프롬프트에서 다시 시도한다 (`:821-836`, `prompt_loop` `:1470-1481`). 요청 시간 제한 120초, `session/load`는 600초 (`:159`, `:161`).

**출력 해석** (`Mapper::on_update`, `:1665-1727`, 알림 `session/update`):

| `sessionUpdate` | 결과 |
|---|---|
| `agent_message_chunk` | `AssistantDelta`, `messageId`가 바뀌거나 도구/계획이 시작되거나 턴이 끝나면 `AssistantMessage` 한 번 |
| `tool_call`, `tool_call_update` | 처음 보면 `ToolCall`, `status`가 `completed`/`failed`면 `ToolResult` |
| `plan` | 이름이 `Plan`인 `ToolCall` + 즉시 `ToolResult` (`[상태] 내용` 줄들) |
| 그 밖 (`user_message_chunk`, `agent_thought_chunk`, `usage_update` 등) | 무시 |

턴 끝은 `session/prompt` 응답의 `stopReason`이다 (`turn_end_events` `:1510-1540`). `cancelled`나 취소 요청이 있었으면 `Interrupted`, `end_turn`이거나 없으면 `Completed`, `max_tokens` 등 그 밖의 값은 `Notice "<이유> (ACP stop reason <x>)"` 후 `Completed`. `usage.{inputTokens,outputTokens}`가 있으면 `Usage`.

**승인 흐름**: 에이전트가 `session/request_permission`을 보내면 `acp-<n>` 형태의 승인 id로 `ApprovalRequested{needs_person:false}`를 내고, 옵션 목록과 JSON-RPC id를 `conn.approvals`에 둔다 (`on_agent_request` `:1404-1412`, `Mapper::on_permission` `:1741`). `AgentRun::answer` (`:2170-2185`)가 `choose_option` (`:1769-1786`)으로 옵션 `kind`를 고른다: `AllowOnce` → `allow_once`(없으면 `allow_always`), `AllowAlways` → `allow_always`(없으면 `allow_once`), `Deny` → `reject_once`(없으면 `reject_always`). 맞는 옵션이 없으면 `{"outcome":"cancelled"}`, 있으면 `{"outcome":"selected","optionId":..}`로 응답한다. 인터럽트하거나 턴이 끝나면 남은 요청은 모두 `cancelled`로 답한다 (`cancel_permissions` `:1336`, `:1488`, `:2187-2198`).

**에이전트가 클라이언트에게 요청하는 것**: `fs/read_text_file`, `fs/write_text_file`, `terminal/create|output|wait_for_exit|kill|release`는 별도 작업으로 `Host::handle`(`:1899`)이 처리한다. `StartRequest::computer`가 있으면 노드의 API로, 없으면 이 서버에서 직접 실행한다 (argv, 셸 없음). 터미널 출력 한도 4 MiB (`DEFAULT_OUTPUT_LIMIT` `:165`). 그 밖의 요청(예: `elicitation/create`)은 `-32601` `Ember does not support <method>` (`:1423-1426`). 따라서 ACP에는 질문이 없다.

**오류 분류**: `session/new`, `session/prompt`의 JSON-RPC 오류를 `classify_rpc_error`(`:974-995`)가 코드와 메시지 부분 문자열로 분류한다. 한도(429, quota, rate limit 등) → `TurnError{code:"quota_exceeded"}`, 인증(코드 `-32000`, 401, `api key` 등) → `TurnError{code:"auth_required"}`, 그 밖 → `Error "ACP session/prompt failed: ..."`. 모두 `TurnEnded{Failed}` 뒤따른다 (`turn_failure_events` `:1220-1238`). 업스트림 메시지는 `redact_upstream`(`:1021`)이 토큰, 이메일, 긴 비밀을 `[redacted]`로 가리고 300자로 자른다 (`:1006-1008`).

**메시지**: `send`는 프롬프트 큐(`mpsc::unbounded`)에 넣고 `prompt_loop`가 하나씩 `session/prompt{sessionId, prompt:[{type:"text",text}]}`로 보낸다 (조향 없음, 중간 메시지는 턴 뒤에 처리, `:2162-2168`, `:1461-1508`). 중단은 알림 `session/cancel{sessionId}`.

**재시작 복구(drain)**: `drains_shim() == true`. 진행 중이던 `session/prompt`의 응답이나 클라이언트 요청을 만나면 읽기를 멈춘다 (`drain_ends_turn` `:629`, `translate_drained_lines` `:642`). 에이전트 자체는 재접속하지 못하고 다음 메시지에서 네이티브 이어하기를 한다 (`:589-590`, `:434-436`).

### Scripted (`ember/server/src/agents/scripted.rs`, 153줄)

프로세스, 네트워크 없는 테스트용 가짜 (`scripted.rs:1-5`). `EMBER_SCRIPTED_AGENT=1`일 때만 `main.rs:129-131`이 등록한다. `send`는 `ToolCall(Bash)` + `ApprovalRequested{approval-<turn>}`를 내고 (`:100-122`), `answer`가 `ToolResult`(거부면 `denied`), `AssistantMessage "echo: <text>"`, `Usage{10,5}`, `TurnEnded{Completed}`를 낸다 (`:124-143`). 메시지에 `slow`가 들어 있으면 `interrupt`가 올 때까지 기다렸다가 `Interrupted` (`:93-99`). `ScriptedForkAdapter`(`:46`)는 포크 시험용으로 네이티브 id를 `fork-of-<id>[@<n>]`로 만든다 (`:65-79`).

## proc.rs: shim 런타임 (`ember/server/src/agents/proc.rs`, 652줄)

목적: 에이전트 프로세스를 띄우는 유일한 곳 (FR-S8, `proc.rs:1`). 런타임이 설치되고 요청에 `EMBER_SESSION_ID`가 있으면 `ember-shim` 아래에서 시작해 서버보다 오래 산다. 그렇지 않으면 `kill_on_drop(true)` 직접 자식 (`spawn_direct` `:288-311`).

| 심볼 | 줄 | 설명 |
|---|---|---|
| `ShimRuntime`, `install_runtime`, `clear_runtime` | `46-62` | `bin`, `dir`, `Arc<Store>`. 서버 `main`이 설치 |
| `active_runtime` | `172` | `EMBER_SESSION_SHIM=off`이면 `None` |
| `spawn_agent` | `275-282` | env에서 `EMBER_SESSION_ID`를 꺼내 지운 뒤, 런타임과 안전한 id(`safe_id` `:284`, 영숫자 `-` `_`)가 있으면 `spawn_shimmed`, 아니면 `spawn_direct` |
| `spawn_shimmed` | `313-332` | 저장소의 오프셋으로 `attach_or_resume`. 살아 있고 `reattachable`이면 다시 붙고, 살아 있지만 재접속 불가면 shim을 멈추고(`stop_shim`) 오프셋을 지운 뒤 새로 시작. `Resume`이면 오프셋을 지우고 새로 시작 |
| `start_shim` | `334-350` | `ShimSpec{session, program, args, cwd, env, mem_limit_bytes, mem_poll_ms}`. 한도는 요청 MiB, 없으면 `EMBER_SESSION_MEM_LIMIT_MB`, 0이나 파싱 실패는 한도 없음 (`mem_limit_bytes` `:217`) |
| `bridge` | `476-575` | shim의 `Output/Exited` 이벤트를 `AsyncRead`/`AsyncWrite`로 바꿔 어댑터 코드를 그대로 쓰게 한다 |
| `ShimReader` | `400-474` | 한 번의 읽기에 한 줄만 준다. 다음 줄을 요청하면 앞 줄 처리가 끝난 것이므로 그 오프셋을 승인(ack)하고 저장한다 |
| `CommitGate`, `require_commit` | `74-150` | 세션의 이벤트 펌프가 `require_commit`을 부르면 ack를 "펌프가 지금까지 보낸 이벤트를 모두 저장한 뒤"로 미룬다 (`commit_if_idle` `:108`). 저장 중 크래시가 나도 줄이 다음 서버에서 재생된다. 저장 실패 시 `store_failed`로 이후 ack를 막는다 (`:125`) |
| `live_shim_sessions` | `577-593` | 서버 시작 시 살아 있는 shim의 세션 id 목록. 죽은 것의 오프셋은 지운다 |
| `drain_surviving_lines` | `596-651` | 재접속할 수 없는 에이전트(Codex, ACP)용. 저장된 오프셋 이후의 출력을 `done`이 받아들이는 줄까지(또는 `max`까지) 읽고, 에이전트를 멈추고, 오프셋을 지운다. 세션은 다음 메시지에서 네이티브 이어하기 |
| `ProcHandle::shutdown` | `242-259` | stdin을 닫고 `grace` 안에 끝나지 않으면 kill |
| `shim_died` | `180` | shim 메타데이터는 있는데 shim pid가 죽었는지 |

주의: shim 아래 에이전트의 stderr는 shim이 자기 로그 파일에 두므로 `AgentProc::stderr`는 직접 자식일 때만 `Some`이다 (`proc.rs:229`).

## history/ 모듈 (SPEC FR-S2, INTENT D13)

| 파일 | 줄 | 설명 |
|---|---|---|
| `ember/server/src/history/mod.rs` (361) | `22`, `33`, `42`, `106`, `185` | 중립 `Transcript{native_id, cwd, title, messages}`, `Message{role, text, tool_name, tool_call_id, is_error}`. `import_file(agent, path)`가 파일 전체를 읽어 Claude Code와 Codex는 해당 파서로, Antigravity와 Scripted와 ACP는 `bail!`한다 (`:106-120`). `to_events`는 `NativeSession`, `UserMessage`, `ToolCall`, `AssistantMessage`, `ToolResult`로 바꾸고 사용자 메시지마다 앞 턴을 `TurnEnded{Completed}`로 닫는다 (`:185-219`) |
| `ember/server/src/history/claude_code.rs` (85) | `13` | `~/.claude/projects/<slug>/<session-id>.jsonl` 파서. `user`/`assistant` 줄, `custom-title`, `summary`만 보고 나머지는 건너뛴다 |
| `ember/server/src/history/codex.rs` (113) | `22`, `99` | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` 파서. `session_meta`와 `response_item`만 쓰고 `event_msg`와 `compacted`는 건너뛴다. 알 수 없는 줄은 에러가 아니다 |

형식은 `ember/vectors/transcripts/`의 공유 시험 벡터로 고정한다 (`history/mod.rs:6-8`). 이 파일들 자체는 홈 디렉터리를 찾지 않는다: 경로는 호출자가 준다.

## 동작 지도

서버 모듈이지만 이 모듈은 HTTP 라우트를 직접 갖지 않는다. 하나 예외로 Antigravity 훅 라우트가 있다.

| 라우트 | 핸들러 | 서비스 함수 | 데이터 |
|---|---|---|---|
| `POST /api/agents/antigravity/hook` (Bearer 세션 토큰) | `hook_call` `ember/server/src/agents/antigravity.rs:645` | `HookBroker::handle` `:632` → `RunApprovals::decide` `:791` | 메모리의 대기 승인(`oneshot`)과 `always_allowed` 집합 |

`router(broker)` (`:641`)가 이 라우트를 만든다. 서버 어디에 붙는지는 `main.rs`에서 확인하지 못했다 [확인 필요].

### 사용자에게 보이는 에러 메시지

| 원문 | 위치 | 조건 |
|---|---|---|
| `working directory <p> does not exist on the ember server (on another computer it is mounted here when the project mount is enabled; see EMBER_MOUNT)` | `claude_code.rs:349-354` | Claude 시작 시 `cwd`가 없다 |
| `claude exited during a turn` | `claude_code.rs:684` | 턴 중 stdout이 닫힘 |
| `unknown approval <id>`, `unknown question <id>` | `claude_code.rs:732`, `:757`, `:771`, `codex.rs:612`, `acp.rs:2177` | 대기 항목이 없다 |
| `The user denied <tool> in Ember.` | `claude_code.rs:745` | Claude에서 거부 |
| `codex app-server exited` | `codex.rs:901` | 예기치 않은 종료 |
| `Antigravity sessions cannot run on another computer yet` | `antigravity.rs:368` | 원격 시작 요청 |
| `Antigravity did not load Ember's approval hook (...), so its tools cannot be gated; refusing to run.` | `antigravity.rs:1020-1024` | 훅 점검 실패 |
| `Antigravity <v> is not the tested version 1.2.16: this session runs read-only ...` | `antigravity.rs:988-994` | 버전 불일치 (Notice) |
| `Approval for <tool> timed out; retry.` | `antigravity.rs:871` | 훅 승인 시간 초과 |
| `the agent speaks ACP protocol version ...; Ember supports 1` | `acp.rs:753` | ACP 버전 불일치 |
| `This agent cannot resume ACP session <id>; a new session was started without the earlier conversation.` | `acp.rs:815` | 이어하기 불가 |
| `the ACP agent exited` | `acp.rs:1398` | 턴 밖에서 종료 |
| `this agent does not support questions` | `mod.rs:392-404` | Claude 이외에서 질문 응답 |
| `importing Antigravity history is not supported yet` | `history/mod.rs:112` | Antigravity 기록 가져오기 |

## 데이터와 설정

- DB 테이블: 이 모듈은 직접 만들지 않는다. `proc.rs`가 `Store::shim_offset`, `clear_shim_offset`, `shim_offsets`를 부른다 (`proc.rs:265`, `:318`, `:578`).
- 저장 파일: Claude의 개인 MCP 설정 파일(`std::env::temp_dir()`, 모드 0600, `claude_code.rs:359`, `:183-200`), Antigravity 세션 루트(`<data dir>/agy/sessions/<uuid>/.agents/...`, `<data dir>/agy/conversations/<id>`).
- 환경 변수: 위 "환경 변수와 설정을 읽는 곳" 표.
- 외부 연동: `claude`, `codex app-server`, `agy`, ACP 에이전트(`omp acp`, `gemini --acp`) 프로세스, `ember-shim` 바이너리, `ember_node::client::NodeClient`(원격 `fs/*`, `terminal/*`), 각 CLI의 로컬 기록 파일(`~/.claude/projects`, `~/.codex/sessions`).

## 이 모듈을 수정할 때 주의할 점

- 어댑터를 추가하면 `main.rs:123-136`(조립), `AgentKind`의 `as_str`/`parse`/`BUILTIN_NAMES`(`mod.rs:53`, `:111`, `:122`), `history::import_file`의 `match`(`history/mod.rs:106`)를 함께 고쳐야 한다. `AgentKind`는 `Serialize`로 DB의 `agent` 열에 저장되므로 기존 문자열을 바꾸면 안 된다 (`mod.rs:15-17`).
- `rejoins_shim`/`drains_shim`/`reattachable`은 한 묶음이다: `reattachable: true`로 띄우는 어댑터는 `rejoins_shim() == true`여야 하고, 핸드셰이크가 있는 프로토콜(Codex, ACP)은 `reattachable: false` + `drains_shim() == true`여야 한다 (`proc.rs:198-210`).
- 승인 id는 어댑터가 정한다 (Claude는 CLI의 `request_id`, Codex는 `approvalId`/`itemId`에 충돌 시 `#<rpc_id>` 접미, Antigravity는 `call_id(conv, step)`, ACP는 `acp-<n>`). 세션이 저장소의 대기 항목을 복원할 때 같은 id를 쓰므로 형식을 바꾸면 복원이 깨진다.
- `approval_policy`(server-core의 `events.rs:132`)는 `remember_always`를 정한다. Claude와 Antigravity가 쓰고 Codex와 ACP는 쓰지 않는다. 승인 기억 규칙을 바꾸면 어댑터별로 따로 확인해야 한다.
- `StartRequest`에 필드를 더하면 `Default`를 파생한 `mod.rs:158`을 지키고, 모든 어댑터가 무시해도 되는지 정해야 한다 (예: `allowed_tools`는 Claude만, `remote`는 Codex만, `computer`는 ACP만).
- Claude의 `--allowedTools`는 가변 인자다: 그 뒤에는 다른 플래그나 끝만 올 수 있다 (`claude_code.rs:137-145`). 인자 순서를 바꾸지 말 것.
- Antigravity 훅 스크립트는 빈 출력이나 `ask`가 도구를 실행시키므로 정확한 `allow`/`deny`만 출력해야 한다 (`antigravity.rs:41-47`, `:503-527`). `PINNED_VERSION`은 SPEC §A 시험이 새 버전에서 통과한 뒤에만 옮긴다 (`:163`).
- 이 모듈의 `//!` 주석과 줄 번호가 문서와 어긋나면 코드가 맞다.

## 이슈 후보

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 죽은 코드 | 중간 | `ember/server/src/history/mod.rs:106`, `:185` | `import_file`과 `to_events`는 `ember/server`의 `history` 밖 소스와 `server/tests`에서 호출을 찾지 못했다 (`grep`). 가져오기 기능이 서버에 아직 연결되지 않았을 수 있다 [확인 필요] | 연결 여부를 확인하고, 없으면 이슈로 남기거나 표시 |
| 보안 | 중간 | `ember/server/src/agents/antigravity.rs:503-527`, `:568-598` | 훅 토큰이 `ember-hook.sh` 파일에 평문으로 있다 (0700, 같은 사용자만 읽음). 세션 루트 경로를 인자에 넣은 도구 호출은 deny하지만 우회 여지가 있는지는 확인하지 않았다 [확인 필요] | 설계상 의도 (D14), 변경 시 위협 모델 재검토 |
| 안정성 | 중간 | `ember/server/src/agents/mod.rs:87` | ACP 이름을 `Box::leak`으로 들여온다. 설정과 DB 이름으로 개수가 제한된다고 주석에 적혀 있다 (`mod.rs:46-48`) | 현재는 허용, DB에서 읽는 이름이 늘면 재검토 |
| 안정성 | 중간 | `ember/server/src/agents/claude_code.rs:884-890` | `shutdown` 외에 `sigint`가 Windows에서는 무동작이다. 인터럽트 응답이 없을 때 최후 수단이 Windows에서는 없다 | Windows용 대체 수단 검토 |
| 확인 불가 | 낮음 | `ember/server/src/agents/acp.rs:863-873` | Gemini 인증 방식 id `gemini-api-key`는 주석에서 UNVERIFIED라고 한다 | 실제 CLI로 확인 |
| 확인 불가 | 낮음 | `ember/server/src/agents/acp.rs:974-995` | 오류 분류가 메시지 부분 문자열 추정이다 (`:6-8` 주석: 실제 문구는 미확인) | 실제 에이전트 응답 기록으로 고정 |
| 하드코딩 | 낮음 | `claude_code.rs:80-82`, `codex.rs:78-80`, `antigravity.rs:166-181`, `acp.rs:159-167` | 제한 시간 상수(10초, 5초, 120초, 3600초, 600초 등) | 설정으로 뺄지 검토 |
| 중복 | 낮음 | `claude_code.rs:282-300`와 `antigravity.rs:530`, `codex.rs:322-349`, `acp.rs:888-901` | MCP 서버 설정을 만드는 코드가 어댑터마다 있다 (각 CLI 형식이 다르므로 의도된 중복일 수 있다) | 유지 가능 |
| 거대 파일 | 낮음 | `acp.rs` 2,218줄, `antigravity.rs` 1,977줄, `claude_code.rs` 1,711줄 | 테스트가 큰 몫이다 (`claude_code.rs`는 `:1077` 이후가 테스트). `acp.rs`는 프로토콜, 설정, 마스킹, 호스트(fs/terminal)가 한 파일 | 필요하면 `acp/` 하위로 분리 |
| TODO/FIXME | 낮음 | 이 모듈 전체 | 0개 (`grep`) | 없음 |
| 시험 | 낮음 | `claude_code.rs:1077-`, `codex.rs:1056-`, `antigravity.rs` (1,500줄 이후), `mod.rs:415-`, `history/mod.rs:222-` | 인라인 테스트 모듈이 있다. `acp/tests.rs`(1,074줄)와 `acp/fake_agent.rs`(422줄)는 읽지 않았다 | |
