# 기술 스택 (Phase 1)

- 기준 커밋: `ffe98256a35046158c3baae2065611168b70d97f` (develop)
- 분석 대상: `git ls-files`에서 락 파일(`Cargo.lock` 등), 바이너리(이미지, 폰트, `.zip`), 빌드 산출물을 뺀 파일 844개, 281,783줄. 목록은 [inventory.tsv](inventory.tsv).
- 작업 트리에만 있고 추적되지 않는 파일(`ember/proxy/darkpyonix.db`, `ember/proxy/_xmo_recent.json`, `ember/*/target/`, `ember/proxy/__pycache__/`)은 제외했다.

## 언어별 규모

| 언어 | 파일 | 라인 | 비율 |
|---|---|---|---|
| Rust | 473 | 232,080 | 82.4% |
| Markdown | 45 | 10,083 | 3.6% |
| HTML | 26 | 6,575 | 2.3% |
| Python | 40 | 5,067 | 1.8% |
| TypeScript | 27 | 4,859 | 1.7% |
| CSS | 11 | 4,528 | 1.6% |
| JavaScript | 13 | 3,984 | 1.4% |
| Kotlin | 24 | 3,825 | 1.4% |
| 기타(`.pptx` 포함 무확장자 등) | 32 | 3,499 | 1.2% |
| Shell | 42 | 2,262 | 0.8% |
| YAML / JSON / TOML / JSONL / 기타 | 91 | 5,021 | 1.8% |

Rust 중 `tests/` 디렉터리가 약 4만 6천 줄이다. 크레이트별 Rust 라인(소스 / `tests/`): app 83,313 / 2,233, server 51,213 / 30,248, node 15,610 / 5,626, editor 10,590 / 4,924, client 6,928 / 1,035, editor-conn 5,528 / 697, transport 5,460 / 1,677, hub 2,873 / 762, transfer 2,174 / 358, bridge 831 / 0.

## 크레이트와 구성 요소

워크스페이스가 없다. `ember/` 아래 크레이트마다 자기 `Cargo.toml`과 `Cargo.lock`을 가지며, 다른 크레이트는 경로(`path = "../x"`)로 참조한다 (`README.md:93-94`).

| 구성 요소 | 경로 | 언어·프레임워크 | 역할 (`Cargo.toml` `description`) |
|---|---|---|---|
| `ember-app` | `ember/app/` | Rust 2024, `dioxus-compose`(git rev 877ef59), `compose-rust`(v0.0.6), `alacritty_terminal` | 네이티브 클라이언트: 런처와 대화 UI, 웹뷰 없음 |
| `ember-client` | `ember/client/` | Rust, `reqwest`, `tokio-tungstenite`, `hyper` | 클라이언트 코어: 연결, 동기화, UI 아래 상태 모델 |
| `ember-server` | `ember/server/` | Rust, `axum` 0.8, `rusqlite`(bundled), `chacha20poly1305`, `croner`, 선택 `nfsserve`/`fuser` | 메인 서버: 에이전트 CLI 래핑, 세션 저장, 클라이언트 푸시 |
| `ember-node` | `ember/node/` | Rust, `axum`, `portable-pty`, `alacritty_terminal`, `ignore`, `grep-*`, `sysinfo` | 각 컴퓨터에서 도구 동작(파일, git, 터미널, exec)을 수행하는 데몬 |
| `ember-transport` | `ember/transport/` | Rust, `letify-link`(git), 선택 `iroh`, `ed25519-dalek` | P2P 연결을 한 인터페이스로 (FR-N5), 인메모리 가짜 포함 |
| `ember-hub` | `ember/hub/` | Rust, `reqwest`, feature `fake`에서 `axum` | darkpyonix.dev 허브 클라이언트: 기기 등록, 목록, 주소 디렉터리 (FR-N2) |
| `ember-transfer` | `ember/transfer/` | Rust, `sha2` | 기기 간 파일 전송 (FR-F1-F10) |
| `ember-bridge` | `ember/bridge/` | Rust, `serde` | IDE 창 브리지: 웹뷰와 네이티브 간 버전 붙은 메시지 (FR-B1-B4) |
| `ember-editor-conn` | `ember/editor-conn/` | Rust, `tokio` | Code-OSS 서버의 Rust 클라이언트 (관리·확장 호스트 연결, 원격 파일 시스템, RPC) |
| `ember-editor` | `ember/editor/` | Rust, `onig`(Oniguruma) | editor-conn과 dioxus-compose 코드 에디터 위젯 사이의 세션 계층 (M8, FR-E1-E4) |
| proxy | `ember/proxy/` | Python 3.10+, FastAPI 0.115, uvicorn 0.30, httpx 0.27, websockets 12.0 고정 | VS Code Web 래퍼와 오버레이, 동반 확장(`companion/`, JS) |
| OSE 파이프라인 | `ember/ose/` | Bash, Python | Code-OSS 빌드·회귀 검사 |
| `vscode-darkpyonix` | `extensions/vscode-darkpyonix/` | TypeScript, esbuild, vitest | DarkPyonix 노트북 VS Code 확장 |
| `vscode-darkpyonix-theme` | `extensions/vscode-darkpyonix-theme/` | JSON 테마 | VS Code 테마 |
| `intellij-darkpyonix` | `extensions/intellij-darkpyonix/` | Kotlin, Gradle | IntelliJ/PyCharm 노트북 플러그인 |

크레이트 의존 방향: `app → client, editor, editor-conn` / `client → transport` / `editor → editor-conn` / `server → node, transport, hub, transfer` / `node → transport, hub` / `hub → transport` / `transfer → transport`. `bridge`는 다른 어느 크레이트도 의존하지 않는다 (`grep -rn ember-bridge --include=Cargo.toml`에서 자기 자신만 나온다).

## 실행·빌드·테스트 명령

| 목적 | 명령 | 근거 |
|---|---|---|
| 메인 서버 실행 | `cd ember/server && cargo build --release --locked && ./target/release/ember-server` | `README.md:99-103` |
| 클라이언트 실행 | `cd ember/app && EMBER_SERVER_URL=http://127.0.0.1:8740 cargo run --release --locked` | `README.md:105-108` |
| 데모 모드 클라이언트 | `EMBER_DEMO_DATA=1` (서버 URL 없이) | `ember/app/src/lib.rs:72-86` |
| 노드 실행 | `ember-node` (`EMBER_NODE_TOKEN` 필수) | `ember/node/src/main.rs:13-44` |
| proxy 실행 | `uv run --with-requirements requirements.txt uvicorn main:app --host 0.0.0.0 --port 8888` | `ember/proxy/README.md:68` |
| proxy를 노드 옆에서 | `uv run --with-requirements requirements.txt python -m dpx.serve --runtime vsc --root ~/work` | `ember/proxy/README.md:109` |
| Rust 테스트 | 크레이트마다 `cargo test --locked` | `.github/workflows/test.yml:13` |
| proxy 테스트 | `cd ember/proxy && python3 -m unittest` | `ember/proxy/README.md:393` |
| VS Code 확장 | `npm ci && npm run typecheck && npm test` | `.github/workflows/test-vscode-extension.yml` |
| IntelliJ 플러그인 | `./gradlew --no-daemon test` / `buildPlugin` | `.github/workflows/test-intellij-plugin.yml` |
| 저장소 규칙 검사 | `bash .github/scripts/checks/check-no-em-dash.sh`, `check-no-webview.sh`, `check-transport-isolation.sh`, `check-vendored-css.sh`, `check-no-has-selector.sh`, `check-release-workflow.sh`, `check-node-units.sh` | `.github/workflows/test.yml:35-121` |

AGENTS.md 규칙: 빌드와 테스트는 한 번에 하나, `CARGO_BUILD_JOBS=2`, worktree마다 별도 `target/` (`AGENTS.md`, "Sub-agents and builds").

## CI 워크플로

| 파일 | 이름 | 내용 |
|---|---|---|
| `.github/workflows/test.yml` | Test | 저장소 검사 스크립트, 크레이트별 `cargo test`, Oniguruma 빌드, Windows 노드·서버 |
| `.github/workflows/test-ose.yml` | OSE build | `ember/ose/build.sh`, 회귀 검사 |
| `.github/workflows/test-vscode-extension.yml` | VS Code extension | typecheck, test, package |
| `.github/workflows/test-intellij-plugin.yml` | IntelliJ plugin | Gradle test, buildPlugin |
| `.github/workflows/test-windows-preview.yml` | Windows preview | Windows용 앱 미리보기 패키지 |
| `.github/workflows/publish-ose.yml`, `publish-release.yml` | Publish OSE / Publish to GitHub release | 태그 릴리스 |
| `.github/workflows/release-sync.yml` | Release sync | develop에서 main으로 동기화 |
| `.github/workflows/pages.yml` | Pages | `docs/guide` 게시 |
