# 진입점과 초기화 순서 (Phase 2)

기준 커밋 `ffe9825`. 라우트 표는 [routes.md](routes.md).

## 진입점 목록

| 프로그램 | 진입점 | 하는 일 |
|---|---|---|
| `ember-server` | `ember/server/src/main.rs:79` `main` | 메인 서버. 환경 변수 목록은 `main.rs:24-77` 주석 |
| `ember-shim` | `ember/server/src/bin/ember-shim.rs:4` | 세션 하나의 에이전트 프로세스를 붙잡아 서버보다 오래 살게 한다 (FR-S8), 본체는 `session_shim` |
| `ember-exec` | `ember/server/src/bin/ember-exec.rs:18` | Claude Code의 Bash 도구를 세션의 노드에서 실행 (`CLAUDE_CODE_SHELL_PREFIX`), 본체는 `computers::shim` |
| `ember-a2a` | `ember/server/src/bin/ember-a2a.rs:3` | 에이전트 쪽 A2A 도구 CLI (FR-T2), 본체는 `a2a::client` |
| `ember-node` | `ember/node/src/main.rs:44` `main` | 노드 데몬. 하위 명령: `__keep-pty`(PTY 유지 프로세스), `exec-server`, `hub`, `enrol` (`main.rs:46-70`) |
| `ember-term` | `ember/node/src/bin/ember-term.rs:248` | 노드 터미널에 붙는 CLI |
| `ember-app` | `ember/app/src/main.rs:7` → `ember/app/src/lib.rs:39` `launch` | 네이티브 클라이언트 |
| `bench` | `ember/transport/src/bin/bench.rs:93` | transport 성능 측정 (feature `bench`) |
| `probe` | `ember/editor-conn/examples/probe.rs:42` | Code-OSS 서버 연결 확인용 예제 |
| proxy | `ember/proxy/main.py:53` `app = FastAPI()` (uvicorn `main:app`) | VS Code Web 프록시와 오버레이 |
| proxy serve | `ember/proxy/dpx/serve.py:197` `main` | `python -m dpx.serve`: 런타임 서버와 프록시를 한 번에 |
| proxy hub | `ember/proxy/dpx/hub/server.py` | 여러 머신을 모으는 별도 hub 앱 [확인 필요: 실행 방법은 Phase 4] |
| VS Code 확장 | `extensions/vscode-darkpyonix/src/extension.ts:26` `activate` | 노트북 확장 |
| VS Code 동반 확장 | `ember/proxy/companion/extension.js` | proxy가 VS Code Web에 넣는 동반 확장 |
| IntelliJ 플러그인 | `extensions/intellij-darkpyonix/src/main/resources/META-INF/plugin.xml` | 플러그인 등록 |
| CI | `.github/workflows/*.yml` | [stack.md](stack.md) "CI 워크플로" |

## ember-server 초기화 순서 (`ember/server/src/main.rs`)

1. 로깅(`RUST_LOG`, 기본 `info`) 설정, 지난 실행이 남긴 MCP 설정 파일 정리 `cleanup_stale_mcp_files` (`main.rs:81-88`).
2. 데이터 폴더 `EMBER_DATA_DIR`(기본 `~/.ember`) 생성, `Store::open(ember.db)` (`main.rs:90-94`).
3. 세션 shim 런타임 설치 (`EMBER_SESSION_SHIM=off`면 끔) (`main.rs:97-109`).
4. 데모 시드 `chatgpt::demo::seed` (`EMBER_DEMO_DATA=1`일 때만), 턴 도중 멈춘 세션 상태 리셋 `reset_live_statuses` (`main.rs:111-115`).
5. 채널 JSONL 파일 복구 `JsonlLog::recover` (라우터보다 먼저, 동기) (`main.rs:119`).
6. 에이전트 어댑터 등록: Claude Code, Codex, Antigravity, 선택 Scripted, ACP 에이전트 (`main.rs:123-136`).
7. `Accounts::open`, `Devices::open`, hub 설정과 `ServerHub` (transport가 켜졌을 때만) (`main.rs:137-151`).
8. transport(`EMBER_TRANSPORT=1`) 바인드, hub 연결·감시·대기 중 링크 재개, peer id 출력 (`main.rs:153-196`).
9. 컴퓨터 레지스트리, `Enrol`, `Sessions::new`, 설정 로드, accounts·members 훅 설치 (`main.rs:198-210`).
10. `Computers::with_transport`, 프로젝트 마운트(`EMBER_MOUNT`), 컴퓨터 훅 설치 (`main.rs:211-230`).
11. 에이전트 egress 프록시 훅 (`EMBER_AGENT_EGRESS=off`면 생략) (`main.rs:233-250`).
12. 리슨 주소 `EMBER_LISTEN`(기본 `127.0.0.1:8740`), guest door와 enrol door 설정 (`main.rs:252-262`).
13. Antigravity 훅 URL, A2A 설정과 `A2a::new`, 팀원 컴퓨터 설정 콜백 (`main.rs:264-299`).
14. 유휴 에이전트 정리 루프 (30초마다, `EMBER_IDLE_SECS` 기본 300) (`main.rs:301-315`).
15. 원격 브라우저 `BrowserManager`, 브라우저 MCP 훅, 중앙 MCP 레지스트리 (`main.rs:320-342`).
16. ChatGPT 로그인 `ChatGpt::new` (`EMBER_HOSTED`면 끔) (`main.rs:345-357`).
17. owner TCP 리스너, guest·enrol door 리스너 바인드 (실패하면 시작 중단) (`main.rs:359-396`).
18. `a2a.install()`, 스케줄러 시작 (`main.rs:398-417`).
19. IDE 설정, `OseManager`, `TransferManager` (`main.rs:420-426`).
20. 라우터 조립: 공용 `app` (`main.rs:443-463`), transport로 `app` 제공 (`main.rs:465-481`), 로컬 전용 라우트를 더한 `local_app` (`main.rs:483-498`), 토큰과 Origin/Host 검사 `auth::protect` (`main.rs:501-518`).
21. 이전 서버의 shim 재접속 `rejoin_shims` (`main.rs:519-524`).
22. guest·enrol door 태스크, owner 서버 `axum::serve` (Ctrl+C로 종료) (`main.rs:526-560`).
23. 종료: door 태스크 5초 대기, transport 닫기, 브라우저 종료(프로필 저장), 마운트 해제 (`main.rs:561-583`).

## ember-node 초기화 순서 (`ember/node/src/main.rs`)

1. 하위 명령 분기: `__keep-pty`, `exec-server`, `hub`, `enrol` (`main.rs:46-70`).
2. `serve()`: 로깅, `NodeConfig::from_env` (`EMBER_NODE_TOKEN` 필수), transport 모드, `Node::new` (`main.rs:73-84`).
3. 선택 SOCKS5 리스너 `EMBER_NODE_SOCKS_LISTEN` (`main.rs:85-89`).
4. TCP 리스너 `EMBER_NODE_LISTEN`(기본 `127.0.0.1:8741`), `local.json` 기록 (ember-term과 VS Code 동반 확장이 이것으로 노드를 찾는다) (`main.rs:94-105`).
5. transport 모드: 키, 허용 peer 목록, hub 등록 확인, peer id 출력, hub 감시, SIGHUP으로 허용 목록 다시 읽기, transport 서버 추가 (`main.rs:109-175`).
6. 라우터: `/health`만 인증 없이, 나머지는 베어러 토큰 미들웨어 뒤 (`ember/node/src/api.rs:154-234`).

## ember-app 초기화 순서 (`ember/app/src/lib.rs:39`)

1. 로깅 `EMBER_LOG` (기본 `warn,ember_app=info,ember_client=info`) (`lib.rs:40-46`).
2. `AppConfig::from_env` (`EMBER_SERVER_URL` 등) (`lib.rs:48`).
3. tokio 런타임 (워커 2개, `ember-io`) (`lib.rs:51-56`).
4. `Client::new`: 캐시된 스냅샷을 읽어 첫 화면에 바로 보여준다 (FR-L1). URL이 잘못되면 종료 코드 2 (`lib.rs:60-70`).
5. 데모 모드(`EMBER_DEMO_DATA=1`, 서버 URL 없음)면 `DemoSource`가 데이터를 넣고 서버에 연결하지 않는다. 아니면 `client.start()` (푸시 연결, 재동기화, 캐시 쓰기) (`lib.rs:73-91`).
6. 설정 `prefs::load`, `SharedUi`, `ServerApi::new`, `install(Services)` (`lib.rs:93-115`).
7. 창 열기, 세 갈래 (`lib.rs:117-146`):
   - `--editor <project> <folder>`: 별도 IDE 창, Dioxus HTML 모드 `ui::editor_workbench::page::app` (FR-L31).
   - 갤러리 요청: `ui::cr::gallery::launch` (#220 검토 창).
   - 기본: `bridge::start_shared()` 후 compose-rust 셸 `ui::cr::shell::launch`.
8. 창이 닫히면 `shutdown`: 설정 저장, 캐시 기록, 클라이언트 정지 (`lib.rs:148-167`).

중요: 기본 실행 경로는 `ember/app/src/ui/cr/`(compose-rust)다. Dioxus 루트 `crate::ui::app`(`ember/app/src/ui/mod.rs:208`)은 어디서도 호출되지 않고 `coexist.rs` 주석에만 나온다. `ui/`의 Dioxus 모듈 중 상당수는 `cr/` 화면이 함수와 모델을 가져다 쓰기 때문에 남아 있다 (예: `ember/app/src/ui/cr/agents.rs`에서 `crate::ui::agents` 참조 86회).

## proxy 초기화 (`ember/proxy/main.py`)

`FastAPI()` 생성(`main.py:53`), `/auth` 하위 앱 마운트(`main.py:68`), `home_api`·`extension`·`terms_api` 라우터 포함(`main.py:82-86`), 정적 자원 라우트(`main.py:107-146`), 나머지는 VS Code Web으로 가는 catch-all HTTP·WebSocket 프록시(`main.py:258`, `main.py:264`). 상세는 [../modules/proxy.md](../modules/proxy.md).
