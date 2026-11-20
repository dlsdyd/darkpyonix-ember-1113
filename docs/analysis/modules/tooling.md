# 모듈: tooling

- 경로: `.github/workflows/`, `.github/scripts/`, `ember/ose/`, `.vscode/`
- 규모: 파일 44개 / 약 2683줄
- 레이어: 인프라
- 한 줄 책임: CI 워크플로, 저장소 규칙 검사 스크립트, Code-OSS(OSE) 빌드 파이프라인.
- 생성 방법: `.scratch/analysis/docs_tooling.py`가 워크플로의 `name:`과 job, 스크립트 머리 주석을 뽑았다.

## 워크플로와 job

| 워크플로 | 이름 | 트리거 | job (`name:`) |
|---|---|---|---|
| `.github/workflows/pages.yml` | Pages | push, workflow_dispatch | `deploy` Deploy the guide |
| `.github/workflows/publish-ose.yml` | Publish OSE | workflow_run | `publish` Publish the release |
| `.github/workflows/publish-release.yml` | Publish to GitHub release | push | `build` Build (${{ matrix.target }}); `publish` Publish the release |
| `.github/workflows/release-sync.yml` | Release sync | push, workflow_dispatch | `sync` Sync release |
| `.github/workflows/test-intellij-plugin.yml` | IntelliJ plugin | push, pull_request, workflow_dispatch | `build` Build and test |
| `.github/workflows/test-ose.yml` | OSE build | pull_request, push, workflow_dispatch | `product` Check product.json; `build` Build (${{ matrix.target }}) |
| `.github/workflows/test-vscode-extension.yml` | VS Code extension | push, pull_request, workflow_dispatch | `notebook` Package notebook extension; `theme` Package theme |
| `.github/workflows/test-windows-preview.yml` | Windows preview | workflow_dispatch, pull_request | `preview` Build the preview zip |
| `.github/workflows/test.yml` | Test | pull_request, push, workflow_dispatch | `transport-isolation` Transport isolation (FR-N5); `sync-release` Release sync script; `node-units` Node service units keep PTY keepers (FR-P6); `bench-summary` Bench matrix summarizer (NFR-N1); `no-em-dash` No em-dash; `release-workflow` Release workflow follows the rules (NFR-R1); `vendored-css` Vendored Code-OSS CSS is reproducible; `no-webview` No webview in the launcher (NFR-L2); `editor-conn-pin` Editor-conn pin matches OSE; `oniguruma` Oniguruma builds (${{ matrix.os }}); `windows-node-server` Windows node and server (windows-latest); `rust` Cargo test (${{ matrix.crate }}) |

## 스크립트

| 파일 | 줄 | 하는 일 (머리 주석) |
|---|---|---|
| `.github/scripts/bench/run-matrix.sh` | 49 | NFR-N1: run one network pair from the dialing machine. Repeat for each pair. |
| `.github/scripts/bench/summarize-matrix.py` | 233 | NFR-N1: summarize the matrix results written by run-matrix.sh. |
| `.github/scripts/bench/tests/fixtures/direct.json` | 15 |  |
| `.github/scripts/bench/tests/fixtures/relayed.json` | 10 |  |
| `.github/scripts/bench/tests/summarize-matrix.test.sh` | 83 | Tests .github/scripts/bench/summarize-matrix.py (NFR-N1) on fixtures. No cargo, no network. |
| `.github/scripts/checks/check-no-em-dash.sh` | 25 | Fails if an em-dash (U+2014) appears in a human-written file. |
| `.github/scripts/checks/check-no-has-selector.sh` | 15 | No `:has(` in Ember-owned CSS (issue #142): the renderer's stylo does not parse :has(), so a |
| `.github/scripts/checks/check-no-webview.sh` | 67 | SPEC NFR-L2 (E1): the launcher and conversation UI never allocate a webview. |
| `.github/scripts/checks/check-node-units.sh` | 23 | SPEC FR-P6: the service units for ember-node must not kill the PTY keepers and shells with the |
| `.github/scripts/checks/check-release-workflow.sh` | 30 | SPEC NFR-R1: the release workflow follows the CI naming rule (AGENTS.md "CI names") and keeps |
| `.github/scripts/checks/check-transport-isolation.sh` | 41 | SPEC FR-N5: no iroh or letify-link type appears outside the transport crate. |
| `.github/scripts/checks/check-vendored-css.sh` | 6 | The vendored Code-OSS CSS equals its pristine copy plus Ember's recorded patch, and the |
| `.github/scripts/checks/test-transcript-vectors.sh` | 11 | Runs the shared transcript vectors (ember/vectors/transcripts/) against both parsers: |
| `.github/scripts/preview/README.txt` | 13 |  |
| `.github/scripts/preview/fetch-renderer.ps1` | 15 | Downloads the compose-rust renderer for Windows and verifies its checksum. |
| `.github/scripts/preview/package-windows.ps1` | 17 | Stages ember-app, the renderer files and the launcher, then zips them. |
| `.github/scripts/preview/run-preview.cmd` | 7 |  |
| `.github/scripts/release/sync-release.sh` | 69 | Publishes develop to the `release` branch, append-only, and opens or retitles the release to main |
| `.github/scripts/tests/check-node-units.test.sh` | 34 | Tests .github/scripts/checks/check-node-units.sh (SPEC FR-P6): it must fail when a unit file or |
| `.github/scripts/tests/sync-release.test.sh` | 81 | Tests .github/scripts/release/sync-release.sh against a throwaway origin. |
| `.vscode/extensions.json` | 3 |  |
| `ember/ose/README.md` | 166 | OSE: DarkPyonix's own build of Code-OSS |
| `ember/ose/VERSION` | 1 |  |
| `ember/ose/build.sh` | 231 | Build DarkPyonix OSE: the Code-OSS (MIT) VS Code web server ("REH web"), renamed and pointed at |
| `ember/ose/check-extensions.sh` | 27 | Cheap check for SPEC FR-W6 on OSE: build.sh stages both extensions, and staging yields |
| `ember/ose/check-product.sh` | 86 | Verify an OSE product.json (SPEC FR-W4): Open VSX gallery, telemetry off, no Microsoft |
| `ember/ose/product.overrides.json` | 37 |  |
| `ember/ose/regress.sh` | 67 | Extension regression test for a packaged OSE build (SPEC NFR-W1, #84). |
| `ember/ose/regression/expected.json` | 15 |  |
| `ember/ose/regression/extensions.json` | 15 |  |
| `ember/ose/regression/fixture-exthost.txt` | 5 |  |
| `ember/ose/regression/regress.py` | 93 | Extension regression helpers for OSE (SPEC NFR-W1, issue #84). |
| `ember/ose/smoke.sh` | 79 | Smoke-test a packaged OSE build (SPEC FR-W4 acceptance, automated part). |
| `ember/ose/stage-extensions.sh` | 29 | Stage the DarkPyonix editor extensions as built-in extensions of a Code-OSS checkout (SPEC FR-W6). |
| `ember/ose/vendor-workbench-css.sh` | 83 | Vendor the Code-OSS workbench CSS Ember needs (INTENT D23, issue #143). |

## 수정할 때 주의할 점
- 워크플로 이름과 파일 이름은 thisisthepy 공통 규칙을 따른다: `test.yml` "Test", `test-<target>.yml`, `publish-<target>.yml`, `release-sync.yml`, `pages.yml` (`AGENTS.md` "CI names"). main의 필수 검사가 job 이름으로 걸려 있으므로 job 이름을 바꾸면 보호 규칙도 같이 고쳐야 한다 [확인 필요: 저장소 설정].
- `check-no-em-dash.sh`는 문서와 코드에서 U+2014를 막는다. `.json`, `.jsonl`, 기록된 픽스처는 예외 (`AGENTS.md` "Writing").
- `check-no-webview.sh`는 런처·대화 UI에 웹뷰가 들어오지 않게 막는다 (`AGENTS.md` 규칙 5, NFR-L2).
- `ember/ose/VERSION`을 바꾸면 `ember/editor-conn/src/rpc_ids.rs`를 다시 만들어야 한다. test.yml의 "Editor-conn pin matches OSE" job이 비교한다 ([editor-conn.md](editor-conn.md)).
- 벤더링한 Code-OSS CSS는 원본 + 패치와 같아야 한다 (`check-vendored-css.sh`, `ember/ose/vendor-workbench-css.sh`).
