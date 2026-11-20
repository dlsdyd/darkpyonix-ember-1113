# 모듈: tests

- 경로: `ember/*/tests/`, `ember/server/src/agents/acp/tests.rs`, `ember/server/src/agents/acp/fake_agent.rs`
- 규모: 파일 227개 / 약 51579줄, 테스트 함수 1461개, `#[ignore]` 17개
- 레이어: 테스트
- 한 줄 책임: 크레이트별 통합 테스트. 테스트 이름은 대개 SPEC ID로 시작한다 (예: `fr_l31_1_...`는 FR-L31).
- 생성 방법: `.scratch/analysis/tests.py`가 파일 머리 주석(`//!`), `#[test]`/`#[tokio::test]` 함수 이름, `#[ignore]`, `cfg(feature)`, `EMBER_*` 문자열을 기계적으로 뽑았다. 테스트 본문은 읽지 않았다. "무엇을 검증하는가"는 머리 주석 첫 줄이며, 비어 있으면 머리 주석이 없다는 뜻이다.

## 테스트 실행 명령

명령은 적기만 했고 분석 중에 실행하지 않았다. 저장소 규칙상 빌드는 한 번에 하나, `CARGO_BUILD_JOBS=2`로 돌린다 (`AGENTS.md` "Sub-agents and builds").

| 대상 | 명령 |
|---|---|
| app 전체 | `cd ember/app && cargo test --locked` |
| client 전체 | `cd ember/client && cargo test --locked` |
| editor 전체 | `cd ember/editor && cargo test --locked` |
| editor-conn 전체 | `cd ember/editor-conn && cargo test --locked` |
| hub 전체 | `cd ember/hub && cargo test --locked` |
| node 전체 | `cd ember/node && cargo test --locked` |
| proxy | `cd ember/proxy && python3 -m unittest` |
| server 전체 | `cd ember/server && cargo test --locked` |
| transfer 전체 | `cd ember/transfer && cargo test --locked` |
| transport 전체 | `cd ember/transport && cargo test --locked` |
| 파일 하나 | `cd ember/<crate> && cargo test --locked --test <파일 이름(확장자 없이)>` |
| SPEC ID 하나 | `cd ember/<crate> && cargo test --locked fr_l31` (테스트 이름 접두사로 거른다) |

## app (5개 파일, 테스트 114개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/app/tests/editor.rs` | 1431 | The Ember editor screen (FR-L31) and its keymap choice (FR-L30): the pure parts, no renderer. | 67 | FR-E2, FR-L30, FR-L31 |  |
| `ember/app/tests/find.rs` | 295 | Find and replace in the open file (D38, #440, #628): the pure model. Columns are UTF-16 code units, as | 18 | FR-L31 |  |
| `ember/app/tests/fonts.rs` | 40 | The bundled app font: Inter, then Pretendard, then system fonts, for every role but Mono. | 3 |  |  |
| `ember/app/tests/no_webview.rs` | 124 | NFR-L2 (E1 made testable): the launcher and conversation UI never allocate a webview. | 3 | NFR-L2 |  |
| `ember/app/tests/palette.rs` | 343 | The command palette's model (D38, #447): fuzzy ranking of commands and files, and the list of | 23 | FR-L31 |  |

## client (6개 파일, 테스트 24개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/client/tests/channels_auth.rs` | 52 | FR-S11: the channel calls go through the common Bearer path (`Api` default headers). | 1 | FR-S11 |  |
| `ember/client/tests/git_flow.rs` | 335 | The git wrappers (SPEC FR-G4) against a stub of `/api/projects/{id}/git/<op>` that records | 13 | FR-G10, FR-G11, FR-G12, FR-G13, FR-G14, FR-G16 외 |  |
| `ember/client/tests/letify_e2e_client.rs` | 98 | SPEC FR-N1, FR-N3 and FR-N5: client sync, push and revocation over letify. | 1 | FR-N1 |  |
| `ember/client/tests/schedules_flow.rs` | 109 | The schedules wrapper against a real ember-server router in-process (SPEC FR-A8, FR-L25). | 4 |  |  |
| `ember/client/tests/server_flow.rs` | 320 | The client against a real ember-server router in-process, with the scripted agent. | 4 |  |  |
| `ember/client/tests/transport_flow.rs` | 121 | The client against a real ember-server router served over the in-memory fake transport | 1 |  |  |

## editor (47개 파일, 테스트 158개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/editor/tests/connect_and_fallback.rs` | 692 | Scripted end-to-end integration tests for `EditorSession::connect_or_fallback` and | 5 |  |  |
| `ember/editor/tests/engine_flow.rs` | 656 | End-to-end flows through the pure session core (no server): widget events in, RPC calls / file | 11 |  |  |
| `ember/editor/tests/explorer_paths.rs` | 178 | Explorer edits (D38, #438): the paths a create, rename or delete may name. The checks keep | 13 |  |  |
| `ember/editor/tests/fixtures/textmate/demo-lang/syntaxes/demo.tmLanguage.json` | 26 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/demo-lang/syntaxes/typo.tmLanguage.json` | 7 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/generate-golden.cjs` | 92 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/host.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/js.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/json.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/md.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/py.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/rs.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/golden/ts.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/JSON.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/JavaScript.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/MagicPython.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/MagicRegExp.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/NOTICE.md` | 126 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/Regular Expressions (JavaScript).tmLanguage` | 237 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/TypeScript.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/injection-guest.tmLanguage.json` | 8 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/injection-host.tmLanguage.json` | 18 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/jsdoc.js.injection.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/jsdoc.ts.injection.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/markdown.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/grammars/rust.tmLanguage.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/plist-js-regexp.expected.json` | 0 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.host` | 6 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.js` | 33 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.json` | 16 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.md` | 42 |  | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.py` | 47 | usr/bin/env python3 | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.rs` | 45 | A tiny crate with the usual Rust syntax. | 0 |  |  |
| `ember/editor/tests/fixtures/textmate/samples/sample.ts` | 51 |  | 0 |  |  |
| `ember/editor/tests/fr_e6_fixtures_stay_out_of_the_product.rs` | 72 | The grammar copies under `tests/fixtures/textmate/grammars` are test data with their own licences. They | 3 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_golden.rs` | 152 | FR-E6 acceptance (2): the interpreter against the real VS Code tokenizer. The files in | 7 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_interpreter.rs` | 317 | FR-E6: the interpreter's rules on small grammars, one behaviour at a time (the golden tests cover the | 24 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_loader.rs` | 620 | FR-E6 (syntax highlighting), the loader: which grammars the extensions contribute and how a grammar | 33 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_perf.rs` | 78 | FR-E6 acceptance (4): what tokenizing costs on a large file. Ignored by default (it prints numbers and | 1 | FR-E6 | `#[ignore]` 1 |
| `ember/editor/tests/fr_e6_textmate_selector.rs` | 124 | FR-E6: scope selectors (`injectionSelector`, the keys of `injections`), after vscode-textmate's matcher. | 9 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_session.rs` | 373 | FR-E6: syntax highlighting inside the session. The core asks for the grammar files a document needs, | 16 | FR-E6 |  |
| `ember/editor/tests/fr_e6_textmate_tokens.rs` | 249 | FR-E6: colour roles from scopes, and a document whose runs follow its edits. The property that matters | 15 | FR-E6 |  |
| `ember/editor/tests/fr_e7_search_flow.rs` | 298 | FR-E7: search across files and replace, through the pure session core (no server). The test plays the | 10 | FR-E7 |  |
| `ember/editor/tests/live_session.rs` | 319 | `EditorSession` against a real OSE server. Ignored by default and gated on `EMBER_OSE_SERVER` | 2 |  | `#[ignore]` 2; env `EMBER_OSE_KEEP`, `EMBER_OSE_SERVER` |
| `ember/editor/tests/onig_link.rs` | 31 | Oniguruma is linked into the editor core and compiles the patterns TextMate grammars rely on. | 2 |  |  |
| `ember/editor/tests/textmate_real_grammars.rs` | 55 | The loader against the grammars of a real Code-OSS build. Ignored by default and gated on | 1 | FR-E6 | `#[ignore]` 1; env `EMBER_OSE_EXTENSIONS` |
| `ember/editor/tests/widget_bridge.rs` | 665 | End-to-end FR-38 `CodeEditor` widget decoration & event bridge tests (`ember_editor::bridge`, | 6 |  |  |

## editor-conn (1개 파일, 테스트 1개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/editor-conn/tests/live_ose.rs` | 697 | End-to-end test against a real OSE server (Code-OSS [`PINNED_VERSION`], the build CI makes from | 1 |  | `#[ignore]` 1; env `EMBER_OSE_KEEP`, `EMBER_OSE_SERVER`, `EMBER_OSE_VERBOSE` |

## hub (7개 파일, 테스트 29개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/hub/tests/config_longpoll.rs` | 292 | The hub additions of darkpyonix-core PR #34 against the fake hub: `GET /config` discovery | 12 |  |  |
| `ember/hub/tests/directory.rs` | 129 | Address directory through the hub (FR-N2): each endpoint publishes its signed record to the | 3 | FR-N6 |  |
| `ember/hub/tests/fixtures/hub.openapi.yaml` | 1241 |  | 0 |  |  |
| `ember/hub/tests/letify_hub_config.rs` | 37 | SPEC FR-N2, FR-N5, INTENT D36: the hub's transport configuration keeps the backend choice and | 2 | FR-N2 |  |
| `ember/hub/tests/link_flow.rs` | 192 | The device-link flow end to end against the fake hub (FR-N2: a device joins the user's | 6 |  |  |
| `ember/hub/tests/openapi_paths.rs` | 68 | Every hub path the client uses exists in the vendored `hub.openapi.yaml` (darkpyonix-core, | 4 |  |  |
| `ember/hub/tests/revocation.rs` | 44 | Revocation on the hub (device removed) is detected and surfaced. | 2 |  |  |

## node (25개 파일, 테스트 170개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/node/tests/common/mod.rs` | 96 | Shared test helper: write a shell script and make sure it can be executed (#546, #555). | 0 |  |  |
| `ember/node/tests/egress.rs` | 106 | `/egress` (FR-R1): a SOCKS5 handshake and CONNECT carried over the node's WebSocket | 2 |  |  |
| `ember/node/tests/exec_server.rs` | 64 | `/exec-server`: the raw byte relay to `codex exec-server --listen stdio`, exercised with a | 1 |  |  |
| `ember/node/tests/git_api.rs` | 1007 | The git API over HTTP (SPEC FR-G1 to FR-G3): temp repositories under `.scratch/`, a local | 38 | FR-G1, FR-G2, FR-G3 | env `EMBER_GIT_MAX_OUTPUT_BYTES`, `EMBER_GIT_NETWORK_TIMEOUT_SECS` |
| `ember/node/tests/git_branches.rs` | 159 | FR-G9 branch list over HTTP, on repositories under `.scratch/` with a local bare remote. | 4 | FR-G9 |  |
| `ember/node/tests/git_commit.rs` | 426 | FR-G14 commit detail and FR-G15 revert and cherry-pick over HTTP, on repositories under `.scratch/`. | 22 | FR-G14, FR-G15 |  |
| `ember/node/tests/git_commit_identity.rs` | 81 | FR-G15 missing git identity. Own test file (own process): it changes HOME and git env process-wide. | 1 | FR-G15 |  |
| `ember/node/tests/git_conflict.rs` | 285 | The git API over HTTP (SPEC FR-G1 to FR-G3): temp repositories under `.scratch/`, a local | 6 | FR-G7 | env `EMBER_GIT_MAX_OUTPUT_BYTES`, `EMBER_GIT_NETWORK_TIMEOUT_SECS` |
| `ember/node/tests/git_github.rs` | 188 | FR-G13 over HTTP: `POST /git/github` with a fake `gh`. `EMBER_GH_BIN` names the script; per | 7 | FR-G13 | env `EMBER_GH_BIN` |
| `ember/node/tests/git_github_missing.rs` | 25 | FR-G13 when `gh` is not installed: a separate test binary, because `EMBER_GH_BIN` is read | 1 | FR-G13 | env `EMBER_GH_BIN` |
| `ember/node/tests/git_log.rs` | 122 | FR-G5 history over HTTP, using repositories under `.scratch/`. | 5 | FR-G5 |  |
| `ember/node/tests/git_merge.rs` | 224 | FR-G16 merge state and FR-G17 merge abort and commit over HTTP, on repositories under `.scratch/`. | 11 | FR-G16, FR-G17 |  |
| `ember/node/tests/git_merge_identity.rs` | 96 | FR-G17 missing git identity on a merge commit. Own test file (own process): it changes HOME and git env proces | 1 | FR-G17 |  |
| `ember/node/tests/git_pr_ops.rs` | 413 | FR-G10 to FR-G12 over HTTP: pull request detail, review, merge and create, with temp | 20 | FR-G10, FR-G11, FR-G12 | env `EMBER_GH_BIN` |
| `ember/node/tests/git_prs.rs` | 208 | FR-G8 pull requests over HTTP: temp repositories under `.scratch/` and a fake `gh` script. | 7 | FR-G8 | env `EMBER_GH_BIN` |
| `ember/node/tests/git_prs_missing.rs` | 45 | FR-G8 when `gh` is not installed: a separate test binary, because `EMBER_GH_BIN` is read | 2 | FR-G10, FR-G8 | env `EMBER_GH_BIN` |
| `ember/node/tests/git_stash.rs` | 104 | FR-G6 stash routes against repositories under `.scratch/`. | 4 | FR-G6 |  |
| `ember/node/tests/hub.rs` | 208 | ember node and the darkpyonix.dev hub (SPEC FR-N2), against the in-process fake hub: | 4 |  |  |
| `ember/node/tests/memory.rs` | 115 | FR-X5 / NFR-X1: the daemon's memory stays bounded however many sessions use it. | 2 |  | `#[ignore]` 2 |
| `ember/node/tests/node_api.rs` | 594 | In-process integration tests: the daemon on an ephemeral port, driven through the client. | 12 | FR-X7 | env `EMBER_X` |
| `ember/node/tests/policy_denied.rs` | 122 | FR-X1 (#521): denied paths inside a root are refused through the node API exactly like paths | 3 | FR-X1 |  |
| `ember/node/tests/ports.rs` | 107 | FR-P7: `GET /ports` lists the listening TCP ports of processes under node-owned jobs and | 3 | FR-P7 |  |
| `ember/node/tests/term_nfr.rs` | 153 | NFR-P1 measurement (SPEC §P): idle-session memory and attach-to-snapshot latency. | 2 |  | `#[ignore]` 3 |
| `ember/node/tests/terms.rs` | 460 | Persistent terminal sessions (SPEC §P): the daemon on an ephemeral port, driven through the | 8 |  |  |
| `ember/node/tests/transport.rs` | 218 | The node API over the in-memory fake transport (SPEC FR-N1, FR-N3, FR-N5): the same router | 4 |  |  |

## proxy (9개 파일, 테스트 89개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/proxy/tests/__init__.py` | 4 |  | 0 |  |  |
| `ember/proxy/tests/js/detach.test.js` | 291 |  | 22 |  |  |
| `ember/proxy/tests/test_inject.py` | 106 |  | 9 |  |  |
| `ember/proxy/tests/test_main_roots.py` | 65 |  | 3 |  |  |
| `ember/proxy/tests/test_roots.py` | 75 |  | 10 |  |  |
| `ember/proxy/tests/test_runtime.py` | 198 |  | 19 |  |  |
| `ember/proxy/tests/test_serve.py` | 185 |  | 10 |  |  |
| `ember/proxy/tests/test_terms_relay.py` | 170 |  | 13 |  |  |
| `ember/proxy/tests/test_transcript_vectors.py` | 84 |  | 3 |  |  |

## server (114개 파일, 테스트 799개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/server/src/agents/acp/fake_agent.rs` | 422 | An in-process ACP agent for tests: speaks ACP v1 over a byte stream, scripted by the prompt. | 0 |  |  |
| `ember/server/src/agents/acp/tests.rs` | 1074 | ACP adapter tests against the in-process fake agent ([`super::fake_agent`]) and unit tests of | 69 | FR-A10, FR-A10B, FR-A10C, FR-A10D, FR-A10F, FR-S8 |  |
| `ember/server/tests/a2a_flow.rs` | 666 | Agent-to-agent messaging against the scripted agent: FR-T1–FR-T6. | 9 |  | env `EMBER_RUNTIME_TOKEN`, `EMBER_SESSION_ID`, `EMBER_URL` |
| `ember/server/tests/a2a_team.rs` | 629 | Agent teams (FR-T7) and composer mentions (FR-T6) against the scripted agent. | 9 |  | env `EMBER_RUNTIME_TOKEN`, `EMBER_SESSION_ID`, `EMBER_URL` |
| `ember/server/tests/a2a_terminal.rs` | 274 | A2A terminal tools (FR-T9): read, send text and interrupt, gated by a grant. | 5 | FR-T9 | env `EMBER_RUNTIME_TOKEN`, `EMBER_SESSION_ID`, `EMBER_URL` |
| `ember/server/tests/accounts_flow.rs` | 343 | Accounts end to end: isolation env per session (FR-U1), routing with reasons (FR-U2/U3), | 4 |  | env `EMBER_SCRIPTED_HOME` |
| `ember/server/tests/acp_gemini.rs` | 142 | The real Gemini CLI over ACP (SPEC FR-A10g). **UNVERIFIED until run on a machine with the CLI.** | 1 |  | `#[ignore]` 1; env `EMBER_E2E_GEMINI`, `EMBER_E2E_GEMINI_MODEL`, `EMBER_E2E_GEMINI_NOKEY`, `EMBER_GEMINI_BIN` |
| `ember/server/tests/acp_omp.rs` | 113 | Real OMP (oh-my-pi) over ACP end to end (SPEC FR-A2 acceptance): a turn that reads a file, | 1 |  | `#[ignore]` 1; env `EMBER_E2E_OMP`, `EMBER_E2E_OMP_MODEL`, `EMBER_OMP_BIN` |
| `ember/server/tests/antigravity.rs` | 402 | Antigravity adapter: process and approval-hook plumbing against a fake CLI (the hook really | 6 |  | `#[ignore]` 1; env `EMBER_AGY_BIN`, `EMBER_E2E_AGY`, `EMBER_E2E_AGY_MODEL` |
| `ember/server/tests/browser.rs` | 392 | Remote browser end to end against a real Chrome/Chromium (SPEC FR-R1–FR-R4). | 3 |  |  |
| `ember/server/tests/browser_egress.rs` | 120 | Browser egress through a computer (FR-R1), without Chrome: the server's loopback SOCKS5 | 2 |  |  |
| `ember/server/tests/chatgpt.rs` | 654 | Sign in with ChatGPT end to end (FR-U4) against an in-process fake of OpenAI's auth server and | 7 |  |  |
| `ember/server/tests/claude_code.rs` | 451 | Claude Code adapter: process plumbing against a fake CLI, and an opt-in end-to-end run against | 7 | FR-A5 | `#[ignore]` 1; env `EMBER_E2E_CLAUDE` |
| `ember/server/tests/codex.rs` | 156 | Real Codex end to end (SPEC FR-A2 acceptance): a turn that reads a file, edits it and runs a | 2 |  | `#[ignore]` 1; env `EMBER_E2E_CODEX`, `EMBER_E2E_CODEX_MODEL` |
| `ember/server/tests/common/mod.rs` | 98 | Shared test helper: write a shell script and make sure it can be executed (#546, #555). | 0 |  |  |
| `ember/server/tests/computers.rs` | 727 | Computers registry and switching a session between computers (FR-X3, FR-S7 v0), against the | 16 | FR-S7, FR-X3 | env `EMBER_COMPUTER_ID` |
| `ember/server/tests/fixtures/acp/fake-acp-agent.sh` | 18 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/acp/fake-gemini.sh` | 43 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/agy/fake-agy-ticks.sh` | 13 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/agy/fake-agy-without-hooks.sh` | 6 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/agy/fake-agy.sh` | 53 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/agy/hooks_list_1.2.16.json` | 1 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/pre_tool_use.json` | 1 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/step_hook_failed_1.2.16.jsonl` | 1 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/turn1_denied.jsonl` | 6 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/turn1_stderr.txt` | 1 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/turn2_resumed.jsonl` | 7 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/turn_hook_denied_1.2.16.jsonl` | 15 |  | 0 |  |  |
| `ember/server/tests/fixtures/agy/turn_tool_output_1.2.16.jsonl` | 20 |  | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude-approval.sh` | 10 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude-plan.sh` | 12 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude-question-reply.sh` | 11 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude-question.sh` | 18 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude-ticks.sh` | 14 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/fake-claude.sh` | 18 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/claude/question_answered_2.1.319.jsonl` | 7 |  | 0 |  |  |
| `ember/server/tests/fixtures/claude/question_unanswered_2.1.319.jsonl` | 7 |  | 0 |  |  |
| `ember/server/tests/fixtures/claude/write_then_bash.jsonl` | 74 |  | 0 |  |  |
| `ember/server/tests/fixtures/codex/fake-app-server.sh` | 21 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/codex/session.jsonl` | 62 |  | 0 |  |  |
| `ember/server/tests/fixtures/codex/synthetic.jsonl` | 13 |  | 0 |  |  |
| `ember/server/tests/fixtures/shim/fake-agent.sh` | 12 | bin/sh | 0 |  |  |
| `ember/server/tests/fixtures/shim/memhog.sh` | 5 | bin/sh | 0 |  |  |
| `ember/server/tests/fr_a10_gemini.rs` | 297 | FR-A10..FR-A10f: the Gemini CLI as the `gemini` ACP preset, against a fake `gemini` shell | 11 | FR-A10, FR-A10A, FR-A10B, FR-A10C |  |
| `ember/server/tests/fr_a6_1_harness_detect.rs` | 174 | FR-A6.1: per-computer harness detection that never invents a version. The adapters take the | 7 | FR-A6 |  |
| `ember/server/tests/fr_c1_enrol.rs` | 164 | FR-C1: the admin routes for enrol codes (INTENT D39, provisional). The redeem core has no | 5 | FR-C1 |  |
| `ember/server/tests/fr_c2_enrol_capture.rs` | 199 | FR-C2g: the secrets are in no tracing output of confirm and deny. | 1 | FR-C2 |  |
| `ember/server/tests/fr_c2_enrol_confirm.rs` | 635 | FR-C2a to FR-C2d, FR-C2g (step 1 of the enrol work, INTENT D39 "Confirm at join", all | 17 | FR-C2 |  |
| `ember/server/tests/fr_c2_enrol_door.rs` | 947 | FR-C2e, FR-C2f: the enrol door's guards and limits (step C2, all [provisional]), and its route | 24 | FR-C2 | env `EMBER_ENROL_ALLOWED_HOSTS`, `EMBER_ENROL_LISTEN`, `EMBER_ENROL_LISTEN_ALLOW_REMOTE`, `EMBER_ENROL_PUBLIC_URL` |
| `ember/server/tests/fr_c2_enrol_door_secrets_in_no_log.rs` | 206 | FR-C2g: the code, the poll secret and the node token are in no tracing output of a full | 1 | FR-C2 |  |
| `ember/server/tests/fr_c2_enrol_node.rs` | 1175 | FR-C2h (step N2, [provisional]): `ember_node::enrol_cli::run` against the REAL enrol door on a | 27 | FR-C2 |  |
| `ember/server/tests/fr_c2_enrol_redeem.rs` | 1262 | FR-C2b, FR-C2d, FR-C2e, FR-C2f, FR-C2g (step C3a, all [provisional]): the two routes of the | 29 | FR-C2 | env `EMBER_ENROL_TRUSTED_PROXIES` |
| `ember/server/tests/fr_f_transfer.rs` | 313 | Integration tests for server-side file transfer API (`FR-F1`..`FR-F10`, `#487`, `#527`). | 2 | FR-F3, FR-F4 |  |
| `ember/server/tests/fr_g13_github_integration.rs` | 294 | FR-G13: `GET /api/integrations/github` aggregates the nodes' `POST /git/github` answers. | 12 | FR-G13 |  |
| `ember/server/tests/fr_l20_agent_settings.rs` | 462 | FR-L20 and FR-S8 (#311): the per-harness memory limit is stored on the server. | 16 | FR-L20, FR-S8 |  |
| `ember/server/tests/fr_l26_project_patch.rs` | 294 | Project settings over HTTP (SPEC FR-L26, #384 PR 2): `PATCH /api/projects/{name}` with the | 11 | FR-L26 |  |
| `ember/server/tests/fr_l26_project_profile.rs` | 308 | Per-project profile override (SPEC FR-L26 and FR-L20, #384 PR 3): `profile_overrides` on | 8 | FR-L26 |  |
| `ember/server/tests/fr_n3_revocation_bound.rs` | 270 | SPEC FR-N3: revoking a device closes its live connections within one heartbeat, with a | 4 | FR-N3 |  |
| `ember/server/tests/fr_n3_revocation_streams.rs` | 388 | SPEC FR-N3 and FR-N7: revoking a device ends everything it has open over the transport, not | 5 | FR-N3, FR-N7 |  |
| `ember/server/tests/fr_n7_remote_device.rs` | 226 | SPEC FR-N7: a remote device's credential is its device key. A request that arrives through | 5 | FR-N7 |  |
| `ember/server/tests/fr_p3_ws_origin.rs` | 146 | FR-P3: the terminal attach WebSocket refuses a cross-site browser page (cross-site WebSocket | 3 | FR-P3 |  |
| `ember/server/tests/fr_p7_ports_relay.rs` | 87 | FR-P7: the node's listening ports relayed under `/api/computers/{id}/ports`, against a real | 1 | FR-P7 |  |
| `ember/server/tests/fr_s8_wiring.rs` | 767 | FR-S8 wiring: the adapters start their agent under `ember-shim` through the shared spawn | 17 | FR-S8 | env `EMBER_SESSION_MEM_LIMIT_MB`, `EMBER_SESSION_MEM_POLL_MS`, `EMBER_SESSION_SHIM` |
| `ember/server/tests/fr_s9_token_auth.rs` | 553 | FR-S9 and FR-S10: the local token and the Origin/Host check (INTENT D37, #338). | 24 | FR-A5, FR-S10, FR-S9, FR-T11 |  |
| `ember/server/tests/fr_t10_channels.rs` | 266 | Channels server API (SPEC FR-T10, FR-T16, FR-L12): list, create, post, read. | 13 | FR-T10, FR-T16 |  |
| `ember/server/tests/fr_t11_feed.rs` | 611 | Channel feed (SPEC FR-T11): member agents' approval requests and reports, answerable there. | 17 | FR-A5, FR-T11 |  |
| `ember/server/tests/fr_t12_channel_post.rs` | 284 | An agent posts into a channel with `ember-a2a channel post` (SPEC FR-T12, FR-S9). | 9 | FR-S9, FR-T12 |  |
| `ember/server/tests/fr_t12_delivery.rs` | 214 | Delivery of a person's channel mentions to agents (SPEC FR-T12, FR-T13). | 6 | FR-T12, FR-T13 |  |
| `ember/server/tests/fr_t12_mcp_channel_post.rs` | 392 | The real `ember-a2a mcp` binary posts into a channel over stdio (SPEC FR-T12, #380). | 8 | FR-T12 | env `EMBER_RUNTIME_TOKEN`, `EMBER_URL` |
| `ember/server/tests/fr_t12_mentions.rs` | 160 | Channel mentions (SPEC FR-T12, FR-T13): parsing, the member gate and the composer preview. | 10 | FR-T12, FR-T13 |  |
| `ember/server/tests/fr_t14_guest_access.rs` | 409 | FR-T14, FR-T15: accepting an invite and the guest routes. Details are [provisional]. | 15 | FR-T14, FR-T15 |  |
| `ember/server/tests/fr_t14_guest_door.rs` | 550 | FR-T14: the guest door (`EMBER_GUEST_LISTEN`, PR 5a). Details are [provisional]. | 26 | FR-T11, FR-T14 | env `EMBER_GUEST_ALLOWED_HOSTS`, `EMBER_GUEST_LISTEN`, `EMBER_GUEST_LISTEN_ALLOW_REMOTE`, `EMBER_GUEST_PUBLIC_URL` |
| `ember/server/tests/fr_t14_guest_door_characterization.rs` | 772 | FR-T14: characterization tests of the guest door's hardening code. They pin what the code does | 18 | FR-T14 | env `EMBER_GUEST_ALLOWED_HOSTS`, `EMBER_GUEST_LISTEN`, `EMBER_GUEST_LISTEN_ALLOW_REMOTE`, `EMBER_GUEST_PUBLIC_URL` |
| `ember/server/tests/fr_t14_guest_door_guard_matrix.rs` | 174 | FR-T14: measures the Host and Origin guard on the WRONG-METHOD path of the guest door. The guest | 3 | FR-T14 | env `EMBER_GUEST_LISTEN` |
| `ember/server/tests/fr_t14_guest_door_logs.rs` | 198 | FR-T14: the tracing messages of `serve_capped` that say "guest door", pinned before the | 1 | FR-T14 | env `EMBER_GUEST_LISTEN` |
| `ember/server/tests/fr_t14_guest_door_order.rs` | 212 | FR-T14: the ORDER of the guest door's layers, pinned before the mixed items move into | 8 | FR-T14 | env `EMBER_GUEST_LISTEN` |
| `ember/server/tests/fr_t14_guest_door_status.rs` | 133 | FR-T14: `GET /api/guest-door`, the owner's view of the guest door. | 6 | FR-T14 | env `EMBER_GUEST_LISTEN`, `EMBER_GUEST_PUBLIC_URL` |
| `ember/server/tests/fr_t14_guest_hardening.rs` | 210 | FR-T14, FR-T15 hardening of the guest routes (review of #400). Details are [provisional]. | 8 | FR-T14 |  |
| `ember/server/tests/fr_t14_guest_join_page.rs` | 246 | FR-T14: the guest page served at `GET /join` (written test first; compiled by CI; browser behaviour is UNVERIF | 10 | FR-T14 | env `EMBER_GUEST_LISTEN` |
| `ember/server/tests/fr_t14_guest_limits.rs` | 609 | FR-T14: the guest door's limits (invite PR 5b). The numbers are a leader decision, adjustable. | 26 | FR-T14 | env `EMBER_GUEST_LISTEN`, `EMBER_GUEST_TRUSTED_PROXIES` |
| `ember/server/tests/fr_t14_invites.rs` | 173 | FR-T14: channel invites, the store and the owner routes. Details are [provisional]. | 7 | FR-T14 |  |
| `ember/server/tests/fr_t15_attribution.rs` | 177 | FR-T15, FR-T16: a message is attributed to the account that wrote it, in the owner's views | 4 | FR-T15, FR-T16 |  |
| `ember/server/tests/fr_t16_jsonl.rs` | 399 | FR-T16: the per-channel JSONL file of human messages. Layout is [provisional]. | 21 | FR-T16 |  |
| `ember/server/tests/fr_t17_allowance.rs` | 517 | FR-T15, FR-T17: the owner's allowance for a guest's mentions, and what an agent receives for | 13 | FR-T15, FR-T17 |  |
| `ember/server/tests/fr_t17_allowance_hardening.rs` | 506 | FR-T17 hardening [provisional]: marker variants (Unicode, spacing, nesting), sanitised labels, the | 13 | FR-T17 |  |
| `ember/server/tests/fr_u6_agy_proxy.rs` | 190 | SPEC FR-U6 / #146: an Antigravity (`agy`) member's model traffic goes to the member's proxy. | 3 | FR-U6 | env `EMBER_AGY_BIN` |
| `ember/server/tests/fr_u6_codex_proxy.rs` | 214 | SPEC FR-U6 / #145: a Codex member's model traffic goes to the member's proxy endpoint. | 3 | FR-U6 | env `EMBER_CODEX_BIN` |
| `ember/server/tests/fr_u7_usage.rs` | 146 | FR-U7: tokens per session and per day, served by the API. Cost is null with a reason. | 3 | FR-U7 |  |
| `ember/server/tests/fr_w4_fs_relay.rs` | 318 | FR-W4 / FR-L7 (#456): the node's read-only file operations relayed under | 7 | FR-W4 |  |
| `ember/server/tests/fr_w4_ide_computers.rs` | 184 | "Open IDE" computers come from the computers registry and the session's current computer | 8 | FR-L7 |  |
| `ember/server/tests/fr_w4_local_node_denied.rs` | 70 | FR-W4 / FR-X1 (#521): the local node (rooted at `$HOME`) refuses the server's own data dir and | 2 | FR-W4 | env `EMBER_DATA_DIR`, `EMBER_OSE_DATA_DIR` |
| `ember/server/tests/fr_w4_local_terms.rs` | 204 | FR-W4 (#455): the local computer's terminal relay `/api/computers/local/terms` is served by an | 4 | FR-W4 |  |
| `ember/server/tests/fr_w4_ose_data_dir.rs` | 480 | FR-W4 (#459): a data dir per computer for the OSE, and the extension install route. | 19 | FR-W4 |  |
| `ember/server/tests/fr_w4_ose_relay.rs` | 671 | SPEC FR-W4, FR-N3, FR-T14 (#458, #461): authenticated WebSocket relay for the OSE socket | 12 | FR-N3, FR-T14, FR-W4 | env `EMBER_GUEST_LISTEN` |
| `ember/server/tests/fr_w4_ose_token_dir.rs` | 129 | FR-W4 (#521): the tokens dir and its parent computer dir are hardened, not just created. | 7 | FR-W4 |  |
| `ember/server/tests/fr_x6_egress.rs` | 263 | FR-X6 / INTENT D19: the agent CLI's API traffic leaves through the session's current | 9 | FR-X6 |  |
| `ember/server/tests/fr_x7_metrics_relay.rs` | 63 | FR-X7: the node's metrics sample relayed under `/api/computers/{id}/metrics`, against a | 1 | FR-X7 |  |
| `ember/server/tests/git_relay.rs` | 246 | FR-G4: `/api/projects/{name}/git/<op>` relays to the project's computer node, with `repo` | 10 | FR-G11, FR-G4, FR-G8, FR-G9 |  |
| `ember/server/tests/hub.rs` | 465 | ember server and the darkpyonix.dev hub (SPEC FR-N2), against the in-process fake hub and the | 13 |  | env `EMBER_TRANSPORT` |
| `ember/server/tests/ide.rs` | 141 | "Open IDE" launch targets: FR-L7 (`GET /api/sessions/{id}/ide`). | 5 |  |  |
| `ember/server/tests/letify_e2e_node.rs` | 48 | SPEC FR-N1 and FR-N5: the server reaches a real node over letify on loopback. | 1 | FR-N1 |  |
| `ember/server/tests/letify_e2e_relay.rs` | 79 | SPEC FR-N2 and FR-N5: client and node traffic crosses the main server relay. | 1 | FR-N2 |  |
| `ember/server/tests/letify_server_relay.rs` | 86 | SPEC FR-N2, INTENT D36: a main server on the letify backend is the relay and the address | 3 | FR-N2 |  |
| `ember/server/tests/mcp_schedules.rs` | 500 | Central MCP registry (FR-A7) and scheduled tasks (FR-A8) against the scripted agent. | 5 |  | env `EMBER_RUNTIME_TOKEN` |
| `ember/server/tests/members.rs` | 152 | Team member definition (FR-A9, FR-U1, FR-U6): harness + fixed account or switching pipeline, | 6 | FR-A9, FR-U6 |  |
| `ember/server/tests/native_fork.rs` | 175 | FR-S5 (#78): a fork uses the agent's own fork when it has one, and copies the conversation | 6 |  |  |
| `ember/server/tests/no_api_version.rs` | 94 | INTENT D15 [user]: no REST path carries a version segment, and the old `/api/v1` prefix is | 2 | NFR-V1 |  |
| `ember/server/tests/peer_mount.rs` | 303 | The project mount for a computer registered by peer (SPEC FR-N1, FR-N5, FR-X2), on the | 4 |  |  |
| `ember/server/tests/projects_search.rs` | 333 | Projects and computer assignment (FR-L4), session metadata (FR-L9), full-text search | 7 | FR-L4, FR-L9, FR-S4, FR-S5 |  |
| `ember/server/tests/script_ready.rs` | 108 | The shared `common::write_exec_ready` helper (#546, #555): a script it wrote can be executed | 3 |  |  |
| `ember/server/tests/session_flow.rs` | 1097 | End-to-end session flow against the scripted agent: FR-S1–S3, FR-A5, PR-1. | 27 | FR-A5 | env `EMBER_SESSION_ID` |
| `ember/server/tests/session_shim.rs` | 174 | FR-S8: agents outlive the ember server. Uses the real `ember-shim` binary and a fake agent. | 7 | FR-S8 |  |
| `ember/server/tests/terms_relay.rs` | 395 | FR-P3 / FR-P6: the node's persistent terminal routes relayed under | 4 | FR-P3, FR-P6 |  |
| `ember/server/tests/transport.rs` | 300 | ember server on the in-memory fake transport (SPEC FR-N1, FR-N3, FR-N5): a real ember node | 4 |  |  |

## transfer (1개 파일, 테스트 15개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/transfer/tests/session.rs` | 358 | SPEC FR-F3, FR-F4, FR-F9, FR-F10 over the in-memory fake transport. Nothing sleeps: the | 15 | FR-F10, FR-F3, FR-F4, FR-F5, FR-F9 |  |

## transport (12개 파일, 테스트 62개)

| 파일 | 줄 | 무엇을 검증하는가 | 테스트 | SPEC ID | 필요 조건 |
|---|---|---|---|---|---|
| `ember/transport/tests/bench_harness_test.rs` | 43 |  | 1 | NFR-N1 | env `EMBER_TRANSPORT_BACKEND` |
| `ember/transport/tests/common.rs` | 90 | Shared test helpers (included with `mod common;`). | 0 |  | feature `iroh`, `letify` |
| `ember/transport/tests/default_backend.rs` | 22 | SPEC FR-N5, INTENT D36: letify-link is the default backend. | 2 | FR-N5 |  |
| `ember/transport/tests/fake.rs` | 98 |  | 6 |  |  |
| `ember/transport/tests/gate.rs` | 176 | FR-N3 admission and revocation, and the dialer's connection cache, on the fake transport. | 6 | FR-N6 | feature `http`, `iroh` |
| `ember/transport/tests/http.rs` | 101 | An axum router (HTTP + WebSocket) served over transport streams: fake and iroh. | 2 |  | feature `http`, `iroh` |
| `ember/transport/tests/iroh_local.rs` | 85 | iroh backend on localhost: two endpoints in one process, relay disabled, addresses found | 3 |  | feature `iroh` |
| `ember/transport/tests/key.rs` | 206 |  | 14 | FR-N6 |  |
| `ember/transport/tests/letify_gate.rs` | 194 | `FR-N3` admission and revocation, and `FR-N6` canonical identities, on the letify-link | 7 | FR-N3, FR-N6 | feature `letify` |
| `ember/transport/tests/letify_local.rs` | 272 | The transport conformance suite against the letify-link backend on localhost (SPEC `FR-N5`: | 14 | FR-N2, FR-N5 | feature `letify` |
| `ember/transport/tests/letify_perf.rs` | 200 | `NFR-N1` measurement on loopback for the letify-link backend: bulk throughput against a raw | 2 | NFR-N1 | `#[ignore]` 2; feature `iroh`, `letify` |
| `ember/transport/tests/letify_relay.rs` | 190 | `FR-N2`: the main server is the relay. Two devices that cannot reach each other directly | 5 | FR-N2, FR-N3 | feature `letify` |

역색인: [tests-2.md](tests-2.md)
