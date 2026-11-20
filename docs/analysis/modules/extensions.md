# 모듈: extensions

- 경로: `extensions/` (`vscode-darkpyonix/`, `vscode-darkpyonix-theme/`, `intellij-darkpyonix/`, `README.md`)
- 규모: 파일 81개 / 약 11,617줄 (`docs/analysis/_raw/modules.md` 기준. 테마 JSON 2개 783줄, Gradle wrapper 3개 517줄, LICENSE 3개 612줄 포함)
- 레이어: UI (편집기 확장)
- 한 줄 책임: DarkPyonix 노트북 파일(`.pynb`, `# %%` 셀이 있는 `.py`)을 VS Code와 IntelliJ/PyCharm에서 열고, darkpyonix-core의 커널 매니저 HTTP API로 셀 실행과 다중 클라이언트 공동 편집을 하며, Ember VS Code 런타임의 기본 테마를 제공한다 (`extensions/README.md:3-7`).
- 의존하는 모듈: 저장소 안의 Rust/Python 모듈에는 의존하지 않는다. 외부 계약은 darkpyonix-core의 `docs/api/manager.openapi.yaml` 1.0.0-draft.3, `docs/FORMAT.md`, `docs/PROTOCOL.md`이다 (`extensions/vscode-darkpyonix/README.md:9-10`, `extensions/vscode-darkpyonix/src/manager/types.ts:1-2`).
- 이 모듈을 쓰는 모듈: [tooling](tooling.md) (`ember/ose/stage-extensions.sh:16,26`가 두 VS Code 확장을 OSE 빌드에 넣는다, `.github/workflows/test-vscode-extension.yml`, `.github/workflows/test-intellij-plugin.yml`), [proxy](proxy.md) (`ember/proxy/dpx/vscode/runtime.py:51` `DEFAULT_EXTENSIONS`가 두 확장 ID를 기본 설치한다).

> 주의: 확장 코드 주석의 `FR-C1`, `FR-S1..S8`, `FR-R4`, `FR-M*`, `FR-F1`, `FR-X4`는 **darkpyonix-core의 SPEC** ID다 (`extensions/vscode-darkpyonix/README.md:9-10`). 이 저장소 `docs/SPEC.md`의 같은 이름 ID(예: Ember `FR-C1` 등록 코드, `docs/SPEC.md:555`; Ember `FR-R4` 브라우저 데이터, `docs/SPEC.md:473`)와 뜻이 다르다. Ember SPEC에서 이 모듈에 해당하는 ID는 `FR-W6`(두 VS Code 확장 기본 설치, `docs/SPEC.md:592`)이다.

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `darkpyonix.vscode-darkpyonix` | VS Code 확장 ID | `extensions/vscode-darkpyonix/package.json:2,6` | `publisher` `darkpyonix` + `name`. `ember/proxy/dpx/vscode/runtime.py:51`가 기본 설치 목록에 넣는다 |
| `darkpyonix.vscode-darkpyonix-theme` | VS Code 확장 ID | `extensions/vscode-darkpyonix-theme/package.json:2,6` | `publisher`가 `DarkPyonix`(대문자). VS Code ID는 대소문자를 가리지 않는다 [추정] |
| `dev.darkpyonix.intellij` | IntelliJ 플러그인 ID | `extensions/intellij-darkpyonix/src/main/resources/META-INF/plugin.xml:3`, `build.gradle.kts:29` | |
| `extensions/vscode-darkpyonix/dist/extension.js` | 빌드 산출물 | `extensions/vscode-darkpyonix/esbuild.mjs:18`, `package.json:26` | `ember/ose/check-extensions.sh:16-18`가 이 파일이 있는지 본다 |
| `DarkPyonixApi` | TS 인터페이스 (확장 export) | `extensions/vscode-darkpyonix/src/extension.ts:20` | e2e 테스트용 `connectionFor`, `cellIdOf` |

### VS Code 확장 명령 (`package.json:63-107`, 등록 `src/extension.ts:175-234`)

| 명령 | 제목 | 메뉴 | 동작 |
|---|---|---|---|
| `darkpyonix.openAsNotebook` | Open as DarkPyonix Notebook | explorer, editor title 우클릭, 명령 팔레트 (`.py`/`.pynb`일 때) (`package.json:126-144`) | `vscode.openWith`로 `.pynb`는 `darkpyonix-notebook`, 그 밖은 `darkpyonix-notebook-py`로 연다 (`src/extension.ts:176-181`) |
| `darkpyonix.interruptKernel` | Interrupt Kernel | 노트북 툴바 (`package.json:110-114`) | `POST /api/kernels/{id}/interrupt`. 아무것도 안 돌면 상태 표시줄 문구 (`src/extension.ts:145-154`) |
| `darkpyonix.restartKernel` | Restart Kernel | 노트북 툴바 (`package.json:115-119`) | 소프트 재시작 `restart(false)` (`src/extension.ts:186-189`) |
| `darkpyonix.hardRestartKernel` | Restart Kernel Process (hard) | 팔레트만 | `restart(true)` 뒤 `resync()` (`src/extension.ts:190-193`) |
| `darkpyonix.shutdownKernel` | Shut Down Kernel | 팔레트만 | 모달 확인 뒤 `DELETE /api/kernels/{id}` (graceful) (`src/extension.ts:194-199`) |
| `darkpyonix.connect` | Connect to Manager / Join Collaboration | 노트북 툴바 `status@1` | Quick Pick 3가지: attach, local, remote(URL+토큰, 토큰은 `ctx.secrets`) (`src/extension.ts:204-233`) |
| `darkpyonix.reloadDocument` | Reload Document from Kernel | 팔레트만 | `session.resync()` (`src/extension.ts:200-202`) |
| `darkpyonix.showOutputLog` | Show Log | 팔레트만 | 출력 채널 "DarkPyonix" (`src/extension.ts:203`) |

노트북 타입 2개: `darkpyonix-notebook` (`*.pynb`, priority `default`), `darkpyonix-notebook-py` (`*.py`, priority `option`) (`package.json:33-54`). 활성화 이벤트는 `package.json:27-31`.

### VS Code 확장 설정 (`package.json:146-210`)

| 키 | 타입 | 기본값 | 읽는 곳 | 뜻 |
|---|---|---|---|---|
| `darkpyonix.cliPath` | string | `darkpyonix` | `src/vscode/managerService.ts:69` | 임시 매니저를 띄울 CLI |
| `darkpyonix.managerArgs` | string[] | `["manager","--ephemeral"]` | `managerService.ts:70` | CLI 인자 |
| `darkpyonix.home` | string | `""` | `managerService.ts:61`, `src/manager/discovery.ts:26-30` | 비면 `$DARKPYONIX_HOME`, 그다음 `~/.darkpyonix` |
| `darkpyonix.manager.url` | string | `""` | `managerService.ts:33,62` | 전용 매니저 URL. 비면 로컬 탐색 |
| `darkpyonix.manager.token` | string | `""` | `managerService.ts:63` | 평문 설정 토큰. secret store(`TOKEN_SECRET`)가 먼저다 |
| `darkpyonix.manager.pathMap` | object | `{}` | `managerService.ts:38`, `discovery.ts:164-170` | 로컬 경로 접두사를 매니저 쪽 접두사로 바꾼다 (가장 긴 접두사) |
| `darkpyonix.autoStartKernel` | boolean | `false` | `src/extension.ts:122` | 열 때 커널 시작 또는 attach |
| `darkpyonix.python` | string | `""` | `src/extension.ts:101` | 새 커널 인터프리터 |
| `darkpyonix.nickname` | string | `""` | `managerService.ts:28` | 비면 호스트 이름, 64자 자름 |
| `darkpyonix.lockIdleSeconds` | number | `20` (최소 3) | `src/extension.ts:102` | 입력이 멈춘 뒤 잠금 해제까지 초 |

`darkpyonix.manager`, `darkpyonix.home`, `darkpyonix.cliPath`가 바뀌면 열린 노트북을 모두 다시 연결한다 (`src/extension.ts:296-300`).

### IntelliJ 플러그인 액션과 설정

액션 (`plugin.xml:32-52`, 구현 `actions/NotebookActions.kt`). 그룹 `DarkPyonix.Group`이 편집기 우클릭 메뉴와 Tools 메뉴 끝에 붙는다 (`plugin.xml:49-50`).

| 액션 ID | 클래스 | 문구 | 동작 |
|---|---|---|---|
| `DarkPyonix.RunCell` | `RunCellAction` | Run Cell (단축키 `control alt shift ENTER`, `plugin.xml:36`) | 캐럿 위치 셀 실행 (`NotebookActions.kt:28-36`) |
| `DarkPyonix.RunAll` | `RunAllAction` | Run All Cells | `session.run(null)` (`NotebookActions.kt:38-42`) |
| `DarkPyonix.Interrupt` | `InterruptAction` | Interrupt Kernel | (`NotebookActions.kt:44-48`) |
| `DarkPyonix.Connect` | `ConnectAction` | Start or Attach Kernel | `connectAsync(startKernel = true)` (`NotebookActions.kt:50-54`) |
| `DarkPyonix.Restart` | `RestartKernelAction` | Restart Kernel… | Soft/Hard/Cancel 대화상자 (`NotebookActions.kt:56-73`) |

설정 (`settings/DarkPyonixSettings.kt:17-44`, 저장 파일 `darkpyonix.xml`, `:15`; 화면 Settings | Tools | DarkPyonix, `settings/DarkPyonixConfigurable.kt:15-54`):

| 필드 | 기본값 | 대응하는 VS Code 설정 |
|---|---|---|
| `command` | `darkpyonix` | `darkpyonix.cliPath` |
| `spawnArgs` | `manager --ephemeral` (공백 분리 문자열, `:64`) | `darkpyonix.managerArgs` (배열) |
| `managerUrl` | `""` | `darkpyonix.manager.url` |
| `managerToken` | `""` (설정 XML에 평문) | `darkpyonix.manager.token` + secret store |
| `python` | `""` | `darkpyonix.python` |
| `nickname` | `""` (기본 `IntelliJ@<host>`, `:68-72`) | `darkpyonix.nickname` |
| `clientId` | 자동 `ij-` + UUID 20자 (`:51-60`) | VS Code는 globalState `vsc-` + 16 hex (`managerService.ts:22-30`) |
| `queueWhenBusy` | `true` | 없음 (VS Code는 항상 `on_busy: "queue"`, `src/connection.ts:124`) |
| `attachOnOpen` | `true` | `darkpyonix.autoStartKernel` (뜻이 다르다, 아래) |
| 없음 | | `darkpyonix.home`, `darkpyonix.manager.pathMap`, `darkpyonix.lockIdleSeconds` |

### VS Code 확장과 IntelliJ 플러그인의 차이

IntelliJ 플러그인은 VS Code 확장과 같은 매니저 API를 쓰는 미러다 (`plugin.xml:6-17`). 같은 점: 포맷 파서는 둘 다 커널의 `_parser.py`를 줄 단위로 옮긴 것이다 (`src/format/parser.ts:1-5`, `format/NotebookFormat.kt:44-47`). `KNOWN_TYPES`와 `concorrunt` 별칭도 같다 (`parser.ts:30-35`, `NotebookFormat.kt:53-58`). 편집 전송 디바운스는 둘 다 300 ms다 (`session.ts:96`, `NotebookSession.kt:395`). 다른 점:

| 항목 | VS Code (`extensions/vscode-darkpyonix/`) | IntelliJ (`extensions/intellij-darkpyonix/`) |
|---|---|---|
| 편집기 모델 | 노트북 UI. 셀을 `NotebookCellData`로 보여 준다 (`src/vscode/serializer.ts:28-38`) | 텍스트 편집기 그대로. 거터 아이콘, 잠긴 셀 색, 줄 끝 메모로 꾸민다 (`editor/CellDecorator.kt:39-43`) |
| 출력 표시 | 셀 출력 (`src/vscode/notebookHost.ts:132-167`) | 별도 툴 윈도 "DarkPyonix" (`plugin.xml:25-26`, `toolwindow/OutputsToolWindow.kt:50-54`) |
| `.py` 판정 | 어떤 `.py`든 "Open as" 로 연다 (`package.json:45-53`) | `# %%` 마커가 있는 `.py`만 노트북 (`notebook/NotebookService.kt:21-29`) |
| 커널 찾기 | `GET /api/kernels` 목록에서 `path`가 같은 것 (`src/connection.ts:56-59`) | 경로 SHA-256으로 `k_` + 20자 ID를 로컬 계산 후 `GET /kernels/{id}` (`format/NotebookFormat.kt:176`, `notebook/NotebookSession.kt:214-219`) |
| 열 때 동작 | `autoStartKernel` 기본 false. 돌고 있는 커널이면 항상 attach, 없으면 `GET /api/documents?path=`로 저장된 출력 표시 (`src/connection.ts:41-54`) | `attachOnOpen` 기본 true. 돌고 있는 커널에만 attach, 시작은 안 함 (`NotebookSession.kt:133`). 커널 없는 문서 조회 API는 쓰지 않는다 |
| 매니저 선택 순서 | 등록 파일을 `started_at` 최신순 (`discovery.ts:80`) | `dedicated` 모드를 먼저, 그다음 최신순 (`manager/ManagerDiscovery.kt:65`) |
| 매니저 spawn | `detached`, stderr 8 KB 버퍼, 15초 대기, 150 ms 폴링. `DARKPYONIX_HOME`은 설정했을 때만 넘긴다 (`discovery.ts:111-143`) | stderr를 `managers/spawn.log`에, 10초 대기, 50 ms 폴링, `DARKPYONIX_HOME` 항상 넘긴다 (`ManagerDiscovery.kt:48,76-115`) |
| 전용 매니저 토큰 저장 | OS secret store 우선, 평문 설정은 대체 (`managerService.ts:63`, `src/extension.ts:218`) | 앱 설정 XML에 평문 (`DarkPyonixSettings.kt:28`) |
| 스냅샷 `seq` 해석 | "스냅샷 다음 이벤트 번호"로 보고 `since = seq - 1` (`src/collab/session.ts:113-115`) | "스냅샷에 포함된 마지막 이벤트"로 보고 `since = seq`, `seq <= lastSeq`는 버린다 (`protocol/DocumentState.kt:100-111,129-130`). README가 미확인으로 적어 둔다 (`intellij-darkpyonix/README.md:78-80`) |
| 잠금 해제 | 입력 멈춤 `lockIdleSeconds`(기본 20초) 뒤 (`session.ts:610-613`) | 30초마다 검사, 60초 넘게 입력 없으면 (`NotebookSession.kt:124-125,554-556`) |
| 잠금 갱신 | 60초마다 `PUT .../lock` (`session.ts:96,119,648`) | 주기 갱신 없음 (`ManagerClient.kt:158` 주석만 "renews") |
| presence 전송 간격 | 최소 200 ms (`session.ts:96`) | 100 ms (`NotebookSession.kt:111,582-592`) |
| 닉네임 헤더 | 비ASCII는 퍼센트 인코딩 (`src/manager/client.ts:158-160`) | 그대로 보낸다 (`manager/ManagerClient.kt:202`). 비ASCII 닉네임에서 Java `HttpClient`가 거부할 수 있다 [확인 필요] |
| 이벤트 재연결 | 250, 500, 1000, 2000, 5000 ms (`src/manager/sse.ts:108`) | 500 ms부터 두 배, 최대 10초 (`manager/EventStream.kt:46,82`) |
| HTTP 기본 timeout | 30초, 커널 시작/재시작 60초 (`client.ts:52,94,107`) | 15초, 시작/재시작 30초 (`ManagerClient.kt:81,87,196`) |
| 셀 동기화 방식 | 편집기와 모델의 차이를 직접 계산, 구조 변경은 1초 안정 대기 (`session.ts:315-420`) | 버퍼를 다시 파싱해 `CellMatcher` + `CellReconciler`로 `SyncOp` 목록 생성 (`protocol/CellSync.kt:11-144`, `NotebookSession.kt:437-460`) |
| 권한 처리 | 없음 | `GET /api/manager`의 `permission`으로 실행/편집 가능 여부 판단, 편집 권한이 없으면 버퍼 전체를 `source`로 보내 실행 (`NotebookSession.kt:221-225,654-679`) |
| 바쁜 커널 | 항상 큐 | 409 `busy`면 Queue/Interrupt 알림 (`NotebookSession.kt:681-688`) |
| 없는 기능 | Run All 명령 없음 (`connection.ts:129` `runAll`은 호출처 없음) | Shut Down, Reload Document, Show Log, pathMap, home 설정 없음 |

## 파일별 요약

### `extensions/vscode-darkpyonix/src/extension.ts` (약 316줄)
- **목적:** VS Code 진입점. serializer, 노트북 컨트롤러, 셀 상태 표시, 명령, 편집기 이벤트를 편집기 독립 모듈에 연결한다 (`:1-3`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `activate(ctx)` | 함수(export) | 26 | 노트북 타입마다 serializer, 상태 제공자, 컨트롤러 `darkpyonix-kernel-<type>` 등록 (`:50-68`) |
  | `connect(nb, autoStart)` | 내부 함수 | 90 | `Entry.opening` 프로미스로 동시 연결을 하나로 묶는다 |
  | `execute(cells, nb)` | 내부 함수 | 133 | 세션이 없고 dirty면 먼저 저장한다 (새 커널은 디스크 파일을 파싱한다, `:136`) |
  | `reconnectAll()` | 내부 함수 | 236 | 엔드포인트를 지우고 모든 노트북을 다시 연결 |
  | `deactivate()` | 함수(export) | 309 | 비어 있다. 정리는 `ctx.subscriptions`가 한다 |
  | `describe(err)` | 내부 함수 | 313 | `ApiError`면 `code: message` |
- **입력 → 출력:** VS Code 이벤트 → `NotebookConnection`, `CollabSession` 호출.
- **의존:** `src/connection.ts`, `src/manager/client.ts`, `src/vscode/*.ts`.
- **사용처:** `esbuild.mjs:18` 진입점, `test/e2e/suite.ts`.
- **부수효과:** 저장(`nb.save()`), 전역 설정 쓰기(`cfg.update("manager.url", ...)`, `:217,221`), secret 저장(`:218`).
- **주의점:** UI 갱신은 50 ms 디바운스 하나로 모은다 (`:39-47`). 스킴이 `file`이 아닌 노트북은 연결하지 않는다 (`:121`).

### `extensions/vscode-darkpyonix/src/connection.ts` (약 171줄)
- **목적:** 노트북 하나와 그 파일의 커널 연결. 편집기 독립 (`:1-2`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `OutputsHost` | 인터페이스 | 10 | `showOutputs`, `kernelChanged` |
  | `NotebookConnection` | 클래스 | 20 | `kernel`, `session`, `tracker` 보유 |
  | `open(autoStart)` | 메서드 | 41 | 커널이 있으면 attach, 없으면 경로로 문서 조회해 저장 출력 표시. 404/403은 무시 (`:51`) |
  | `ensureAttached(existing?)` | 메서드 | 62 | 커널 시작(멱등) 후 `CollabSession.start()` |
  | `showSnapshotOutputs(doc, bound)` | 메서드 | 94 | 커널 없을 때는 위치로 맞추고, 편집기 텍스트 SHA가 다르면 stale 표시 (`:111-112`) |
  | `run(positions)` | 메서드 | 117 | `flushNow()` 뒤 `cell_ids`로 `startRun`, `on_busy: "queue"` |
  | `runAll()` | 메서드 | 129 | 호출처 없음 (죽은 코드) |
  | `interrupt()`, `restart(hard)`, `shutdown()`, `detach()`, `dispose()` | 메서드 | 137-168 | shutdown은 `force`를 쓰지 않는다 (`:148`) |
- **의존:** `format/cells.ts`, `format/parser.ts`, `collab/session.ts`, `manager/client.ts`, `run/tracker.ts`.
- **사용처:** `src/extension.ts:100`, `test/integration/collab.test.ts`.
- **부수효과:** 매니저 HTTP 호출.
- **주의점:** `run`은 셀에 `cellId`가 없으면 "These cells are not in the kernel's document yet." 예외 (`:123`).

### `extensions/vscode-darkpyonix/src/collab/session.ts` (약 701줄, 거대 파일)
- **목적:** 커널 문서 하나에 대한 공동 편집. 편집기 독립 (`:1-2`). 에코 루프 규칙: 원격 변경은 모델에 먼저 쓰고 편집기에 쓰므로 뒤따르는 변경 콜백은 보낼 것이 없다 (`:4-7`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `HostCell`, `NotebookHost` | 인터페이스 | 16, 24 | 편집기 추상화 (VS Code는 `VsNotebookHost`, 테스트는 `FakeHost`) |
  | `SessionOptions` | 인터페이스 | 39 | 기본값 `editDebounceMs` 300, `lockIdleMs` 20000, `lockRenewMs` 60000, `presenceThrottleMs` 200, `structureSettleMs` 1000 (`:96`) |
  | `CollabSession` | 클래스 | 68 | |
  | `start(doc?)` | 메서드 | 108 | 스냅샷 로드, 편집기 정렬, `since = seq - 1`로 SSE 구독, 잠금 갱신 타이머 |
  | `resync()` | 메서드 | 124 | 스냅샷 다시 읽기. `replay_truncated`에서도 부른다 (`:164-167`) |
  | `dispose()` | 메서드 | 134 | 보류 편집 flush, 잠금 해제, presence 떠나기 |
  | `onEvent(ev)` | private | 162 | `doc.*`/`presence.*`는 모델로, 나머지는 `onRunEvent`로 |
  | `applyOps(ops)` | private | 212 | 모델 op를 편집기에 반영 |
  | `syncFromHost()` | 메서드 | 315 | 0) 미바인딩 셀 입양, 1) 삭제, 2) 생성, 3) 이동, 그다음 텍스트 |
  | `localEdit`, `ensureLock`, `flush` | private | 477, 494, 532 | 잠금 받고 `base_version`으로 `PATCH` |
  | `askConflict`, `onConflict` | private | 563, 580 | 충돌 선택 대화 ("Keep mine"/"Use theirs", "Keep editor version"/"Use disk version") |
  | `release(cellId)` | 메서드 | 620 | 최종 소스와 함께 잠금 해제 |
  | `focusChanged`, `reportPresence` | 메서드 | 662, 672 | presence 스로틀 |
  | `flushNow()` | 메서드 | 687 | 실행 전에 보류 편집을 보낸다 |
  | `isLockedByMe` | 메서드 | 103 | 저장소에서 호출처 없음 |
- **의존:** `format/parser.ts`, `format/cells.ts`, `manager/client.ts`, `collab/model.ts`.
- **사용처:** `src/connection.ts:71`, `test/integration/collab.test.ts`.
- **부수효과:** 셀 생성/수정/삭제/이동/잠금, presence HTTP 호출. 타이머 다수.
- **주의점:** 모든 편집기 변경은 `enqueue` 체인 하나로 직렬화된다 (`:154-160`). 실패는 로그만 남기고 체인을 끊지 않는다. 구조 변경은 `structureSettleMs` 동안 안정해야 보낸다 (VS Code가 디스크 재로드 시 셀을 새로 만드는 것을 흡수하려고, `:48-54`).

### `extensions/vscode-darkpyonix/src/collab/model.ts` (약 226줄)
- **목적:** 클라이언트가 아는 공유 문서: 스냅샷 + `doc.*`, `presence.*` 이벤트. 순수 함수형 (`:1-3`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ModelOp` | 타입 | 6 | `insert`, `update`, `delete`, `move`, `reset`, `state`, `conflict`, `lockLost` |
  | `DocModel` | 클래스 | 20 | `cells`, `docVersion`, `presence` |
  | `apply(ev)` | 메서드 | 119 | 이벤트 타입별 처리. `doc_version <= docVersion`이면 무시 (`:111-113`) |
  | `upsert(cell)` | 메서드 | 69 | `version`이 낮으면 버린다 |
  | `isVisible(c)` | 메서드 | 55 | 빈 preamble은 숨긴다 |
  | `who(a)` | 함수(export) | 222 | `user@nickname` 표시 문자열 |
- **사용처:** `collab/session.ts:13`, `vscode/status.ts`, `test/unit/model.test.ts`.
- **부수효과:** 없음.

### `extensions/vscode-darkpyonix/src/manager/client.ts` (약 160줄)
- **목적:** 매니저 HTTP 클라이언트 (`:1`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ClientIdentity` | 인터페이스 | 7 | `clientId` (`^[A-Za-z0-9_-]{8,64}$`), `nickname` |
  | `ApiError` | 클래스 | 14 | `status`, `code`, `data`. 연결 실패는 `status 0`, `code "unreachable"` (`:64`) |
  | `ManagerClient` | 클래스 | 34 | 헤더 `X-DarkPyonix-Client`, `X-DarkPyonix-Nickname`, `Authorization: Bearer` (`:41-50`) |
  | `request(method, path, body, timeoutMs=30000)` | 메서드 | 52 | 오류 본문 `{error:{code,message,data}}` 해석 |
  | `health` … `leavePresence` | 메서드 | 84-141 | 아래 API 표 |
  | `events(id, since, onEvent, onState)` | 메서드 | 144 | `EventStream` 생성 |
  | `encodeHeader(v)` | 함수(export) | 158 | 비ASCII 퍼센트 인코딩 |
- **사용처:** `connection.ts`, `collab/session.ts`, `vscode/managerService.ts:56`.
- **부수효과:** 네트워크.
- **주의점:** `manager()`(`:87`)와 `getKernel()`(`:96`)은 저장소에서 호출처가 없다.

### `extensions/vscode-darkpyonix/src/manager/discovery.ts` (약 170줄)
- **목적:** CLI와 같은 방식의 매니저 탐색 (`:1-3`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `RegistryRecord`, `ManagerEndpoint` | 인터페이스 | 9, 18 | `source`: `ephemeral`, `spawned`, `dedicated` |
  | `darkpyonixHome(configured?, env)` | 함수 | 26 | `DARKPYONIX_HOME` 읽음 |
  | `pidAlive(pid)` | 함수 | 36 | `process.kill(pid, 0)`, EPERM도 살아 있음 |
  | `checkHealth(url, timeoutMs=2000)` | 함수 | 46 | `/health`의 `status === "ok"` |
  | `readRegistry(home)` | 함수 | 61 | `<home>/managers/*.json` 최신순 |
  | `findLiveManager`, `spawnManager`, `resolveManager` | 함수 | 90, 111, 155 | |
  | `mapPath(local, pathMap)` | 함수 | 164 | 가장 긴 접두사 치환 |
- **부수효과:** 파일 읽기, 프로세스 spawn(detached, `unref`), 네트워크.
- **주의점:** spawn 실패 메시지 "darkpyonix manager did not start (...)" (`:133`), 시간 초과 "darkpyonix manager did not write .../<pid>.json within 15s" (`:137`).

### `extensions/vscode-darkpyonix/src/manager/sse.ts` (약 152줄)
- **목적:** WHATWG SSE 증분 파서와 `Last-Event-ID`로 재개하는 재연결 리더 (`:1-2`).
- **주요 심볼:** `SseParser` 클래스 `:12` (`push(chunk)` `:19`), `toKernelEvent(msg)` `:63` (숫자 `id`만 `seq`), `EventStream` 클래스 `:86` (`once()`는 `seq <= lastSeq` 이벤트를 버린다).
- **부수효과:** 네트워크 스트림. 핸들러 예외는 `console.error`로 삼킨다.

### `extensions/vscode-darkpyonix/src/manager/types.ts` (약 131줄)
- **목적:** 매니저 API DTO (1.0.0-draft.3). 읽지 않는 필드는 뺐다 (`:1-2`).
- **주요 심볼:** `Permission` `:4` (`admin`, `editor`, `viewer3`, `viewer2`, `viewer1`), `Kernel` `:6` (`status`: `starting`/`idle`/`busy`/`stopping`), `NbOutput` `:20`, `Lock` `:33`, `Cursor` `:43`, `Presence` `:50`, `DocumentCell` `:62`, `Document` `:89`, `RunRequest` `:100`, `RunAccepted` `:109`, `Attribution` `:116`, `ApiErrorBody` `:122`, `KernelEvent` `:127`.

### `extensions/vscode-darkpyonix/src/format/parser.ts` (약 236줄)
- **목적:** DarkPyonix 포맷 파서/직렬화기. 커널 `kernel/darkpyonix/format/_parser.py`의 줄 단위 이식. 바이트 단위 왕복 보장 (`:1-17`).
- **주요 심볼:** `MARKER_RE` `:21`, `METADATA_RE` `:24`, `KNOWN_TYPES` `:30`, `TYPE_ALIASES` `:35`, `Cell` `:39`, `NotebookDocument` `:57`, `sha256` `:90`, `sourceSha256` `:98`, `canonicalType` `:147` (null은 `code`), `parse` `:154`, `pyJsonDumps` `:190`, `formatHeader` `:202`, `serialize` `:219`.
- **주의점:** 줄 기반이라 삼중 따옴표 문자열 안의 마커도 새 셀을 연다 (`:15-16`). IntelliJ `NotebookFormat.kt`와 같은 규칙을 두 번 구현한 것이다.

### `extensions/vscode-darkpyonix/src/format/cells.ts` (약 209줄)
- **목적:** 파싱된 셀과 노트북 편집기 표시 사이의 변환. 정확한 바이트 복원 정보는 `DpxCellMeta`(`header`, `trailer`, `eol`, `md`)에 담는다 (`:1-12`).
- **주요 심볼:** `DpxCellMeta` `:23`, `ViewCell` `:35`, `ViewNotebook` `:44`, `DEFAULT_MD` `:49`, `splitTrailer` `:52`, `unwrapMarkdown`/`wrapMarkdown` `:72`/`:89` (`darkpyonix.markdown("""...""")` 래퍼), `bodyToView` `:96`, `textToView` `:129`, `effectiveType` `:140`, `viewToSource` `:151`, `viewToDocument` `:178`, `viewToText` `:205`.

### `extensions/vscode-darkpyonix/src/run/tracker.ts` (약 183줄)
- **목적:** 실행 이벤트(`run.*`, `cell.*`, `output`, `output.clear`)를 셀별 실행으로 바꾼다. 다른 클라이언트가 시작한 실행도 (`:1-2`).
- **주요 심볼:** `ExecHandle` `:5`, `RunInfo` `:12`, `ExecSink` `:19`, `RunTracker` `:38`, `expect(runId, cellIds, by)` `:61`, `handle(ev)` `:94`, `abandonAll()` `:174`, `isActive(runId)` `:72` (테스트 `test/unit/model.test.ts:148`만 쓴다).
- **주의점:** 시작되지 않고 끝난 셀은 `"cancelled"`로 끝낸다 (`:162`).

### `extensions/vscode-darkpyonix/src/vscode/notebookHost.ts` (약 255줄)
- **목적:** `NotebookHost`, `OutputsHost`, `ExecSink`의 VS Code 구현.
- **주요 심볼:** `toCellOutput` `:12`, `NotebookUiState` `:20` (`kernelState` 기본 `"not connected"`), `VsNotebookHost` `:28` (셀 편집 `:48-114`, `notify` `:120`, `showOutputs` `:132`, `flushPendingOutputs` `:139`), `VsExecSink` `:169`.
- **주의점:** 저장된 출력은 셀 실행(`createNotebookCellExecution`)으로 쓴다. 컨트롤러가 선택되지 않았으면 `pendingOutputs`에 두었다가 선택 시 쓴다 (`src/extension.ts:64`).

### `extensions/vscode-darkpyonix/src/vscode/status.ts` (약 171줄)
- **목적:** 셀 상태 표시줄 항목, 원격 커서 데코레이션, 커널 상태 표시줄 항목.
- **주요 심볼:** `NotebookEntry` `:10`, `CellStatusProvider` `:20` (preamble 안내, stale, 실행 중, 잠금, 포커스, 충돌 표시 `:30-87`), `RemoteDecorations` `:89`, `KernelStatusItem` `:139` (문구 `"<icon> DarkPyonix: <state>"`, `:158`).

### `extensions/vscode-darkpyonix/src/vscode/managerService.ts` (약 76줄)
- **목적:** 설정, 기기 식별자, 매니저 엔드포인트 캐시.
- **주요 심볼:** `CLIENT_ID_KEY` `:9` (`darkpyonix.clientId`), `TOKEN_SECRET` `:10` (`darkpyonix.manager.token`), `ManagerService` `:12` (`identity` `:22`, `managerPath` `:37`, `client` `:50`, `resolve` `:59`).
- **주의점:** 로컬 매니저일 때 `realpathSync.native`로 실제 경로를 보낸다 (`:40`). 커널 ID는 경로로 정해지므로 심볼릭 링크 차이가 다른 커널을 만든다 [추정].

### `extensions/vscode-darkpyonix/src/vscode/serializer.ts` (약 69줄)
- **목적:** `NotebookSerializer`. 편집하지 않은 노트북은 바이트가 같고 출력은 쓰지 않는다 (`:1-2`).
- **주요 심볼:** `NOTEBOOK_TYPES` `:6`, `META_KEY` `:9` (`darkpyonix`), `SERIALIZER_OPTIONS` `:10` (`transientOutputs`), `bindCellId`/`cellIdOf` `:20`/`:24` (WeakMap, 메타데이터에 넣으면 dirty가 되므로, `:14-18`), `DarkPyonixSerializer` `:54`.

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/notebook/NotebookSession.kt` (약 762줄, 거대 파일)
- **목적:** IDE에 열린 노트북 파일 하나와 매니저를 통한 커널 연결. 출력 상태, 공동 편집, presence (`:47-55`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `NotebookSession` | 클래스 | 56 | `state: DocumentState`, `client`, `kernelId`, `permission`, `statusText` |
  | `editorOpened()`/`editorClosed()` | 메서드 | 131, 136 | 첫 편집기면 `attachOnOpen`에 따라 조용히 연결 |
  | `connectAsync(startKernel, quiet, then)` | 메서드 | 170 | 요청을 모아 한 번에 연결 (`drainConnectRequests` `:179`) |
  | `connect(startKernel)` | private | 203 | 커널 ID 로컬 계산, `managerInfo()`로 권한 |
  | `startStream()`, `resync()` | 메서드 | 234, 246 | `state.subscribeSince`로 구독 |
  | `onEvent`, `applyRemote` | private | 261, 286 | 원격 변경을 `WriteCommandAction`으로 버퍼에 반영 (`:356`) |
  | `onBeforeChange`, `onChanged`, `lock`, `flush` | | 372, 386, 399, 429 | 300 ms 뒤 `CellReconciler` 결과 전송 |
  | `onEditRejected(op, e)` | private | 489 | 409 `conflict`/`locked`, 403 처리 |
  | `releaseIdleLocks()` | private | 554 | 60초 무입력이면 해제 |
  | `onCaret(editor)` | 메서드 | 561 | presence |
  | `run`, `runNow`, `interrupt`, `restart` | 메서드 | 647, 651, 696, 708 | |
  | `positionAt`, `serverCellAt` | 메서드 | 722, 728 | |
  | `dispose()` | 메서드 | 736 | 보류 편집 flush, 잠금 해제, presence 떠나기 |
- **의존:** `manager/*`, `protocol/*`, `format/NotebookFormat.kt`, `settings/DarkPyonixSettings.kt`.
- **사용처:** `notebook/NotebookService.kt:52`, `actions/NotebookActions.kt`, `editor/CellDecorator.kt`, `toolwindow/OutputsToolWindow.kt`.
- **부수효과:** 버퍼 쓰기와 파일 저장 (`FileDocumentManager.saveDocument`, `:366,482`), HTTP, 스레드 풀 작업.
- **주의점:** 저장은 커널이 같은 바이트를 쓰게 하려는 의도이며, 커널 watcher가 이를 외부 편집으로 볼지는 미확인이다 (`README.md:84-86`).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/protocol/DocumentState.kt` (약 350줄)
- **목적:** 커널 공유 문서의 클라이언트 쪽 사본. `VS Code`의 `DocModel`에 해당 (`:46-51`).
- **주요 심볼:** `DocChange` `:12` (`Created`, `Updated`, `Deleted`, `Moved`, `Reloaded`), `ApplyResult` `:22` (`Kind` `:30`), `DocumentState` `:53`, `loadSnapshot` `:104`, `apply(seq, type, data)` `:127`, `upsertFromResponse` `:300`, `removeCell` `:314`, `setLock` `:319`.
- **주의점:** `apply`, `loadSnapshot`은 `@Synchronized`, 읽기는 복사본 (`:50-51`).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/protocol/Models.kt` (약 234줄)
- **목적:** 프로토콜 DTO와 출력 도우미. 파일 이름과 다른 클래스들을 담는다.
- **주요 심볼:** `CellLock` `:13`, `CellCursor` `:42`, `Presence` `:61`, `DocCell` `:108` (`withDocumentFieldsOf` `:157`), `Actor` `:176`, `Outputs` 객체 `:191` (`normalize`, `append`, `stripAnsi`, `plainText`).
- **사용처:** `NotebookSession.kt`(38곳), `DocumentState.kt`(34곳), `OutputsToolWindow.kt`(9곳) (`grep -E '\b(CellLock|CellCursor|Presence|DocCell|Actor|Outputs)\b'`). **고아 후보 기각.**

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/protocol/CellSync.kt` (약 144줄)
- **목적:** 버퍼 셀과 서버 셀 매칭, 차이를 `SyncOp`로 계산.
- **주요 심볼:** `CellMatcher.match(local, server)` `:11-13`, `SyncOp` `:49` (`Update` `:51`, `Create` `:63`, `Delete` `:71`, `Move` `:74`), `CellReconciler` `:81` (`newRef` `:82`, `reconcile` `:84`).
- **사용처:** `notebook/NotebookSession.kt:32-33,38,294,380,437-460,666,730`. **고아 후보 기각** (제품 코드가 쓴다).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/actions/NotebookActions.kt` (약 73줄)
- **목적:** 메뉴 액션 5개와 공통 기반 `NotebookAction` (`:13`).
- **사용처:** `plugin.xml:34-48`가 `RunCellAction`, `RunAllAction`, `InterruptAction`, `ConnectAction`, `RestartKernelAction`을 등록한다. **고아 후보 기각** (XML 등록은 import 그래프에 보이지 않는다).
- **주의점:** 노트북 세션이 없으면 액션을 숨긴다 (`:23-25`).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/manager/ManagerClient.kt` (약 229줄)
- **목적:** 매니저 API의 블로킹 클라이언트. EDT 밖에서 부른다 (`:32-35`).
- **주요 심볼:** `ManagerException` `:18` (`isConflict`, `isLocked`, `isBusy` `:24-26`), `ClientIdentity` `:30`, `ManagerClient` `:36`, `health` `:55`, `managerInfo` `:63`, `listKernels` `:67` (호출처 [확인 필요]), `getKernel` `:71`, `startKernel` `:78`, `interrupt` `:84`, `restart` `:86`, `document` `:91`, `startRun` `:99`, 셀 편집 `:121-166`, presence `:168-172`, `eventsRequest` `:179`, `call` `:196`, `openEvents` `:225`.
- **부수효과:** 네트워크.

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/manager/ManagerDiscovery.kt` (약 125줄)
- **목적:** 등록 파일 탐색과 임시 매니저 spawn. CLI `discovery.rs`의 미러 (`:29-33`).
- **주요 심볼:** `ManagerRecord` `:14`, `ManagerDiscovery` `:34`, `defaultHome()` `:40` (`DARKPYONIX_HOME`), `SPAWN_TIMEOUT_MS` `:48` (10,000), `liveRecords` `:54`, `findLive` `:69`, `spawnEphemeral` `:76`.
- **부수효과:** 디렉터리 생성, `spawn.log` 쓰기, 프로세스 실행.

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/notebook/NotebookService.kt` (약 108줄)
- **목적:** 프로젝트 서비스 (`@Service(Service.Level.PROJECT)`, `:33`). 열린 세션 목록과 공유 매니저 연결.
- **주요 심볼:** `NotebookFiles.isNotebook` `:20-30`, `NotebookService` `:34`, `getOrCreate` `:52`, `managerClient(spawn)` `:79` (전용 URL 우선, 아니면 탐색, `spawn`이면 띄운다), `notify` `:98` (알림 그룹 `DarkPyonix`).
- **주의점:** 전용 매니저가 `/health`에 답하지 않으면 "The dedicated manager at $url does not answer /health." 예외 (`:89`).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/format/NotebookFormat.kt` (약 217줄)
- **목적:** 포맷 파서의 Kotlin 이식 (`:44-47`). `NotebookCell` `:14` (오프셋 기반).
- **주요 심볼:** `KNOWN_TYPES` `:53`, `MARKER_RE` `:61`, `parse` `:79`, `sourceSha256` `:164`, `kernelIdFor(canonicalPath)` `:176` (`"k_" + sha256(path)[0:20]`), `formatHeader` `:179`.
- **주의점:** `kernelIdFor`는 매니저의 커널 ID 규칙을 클라이언트에서 다시 구현한 것이다. 매니저 규칙이 바뀌면 attach가 조용히 실패한다 ("No kernel for this file", `NotebookSession.kt:216`).

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/json/Json.kt` (약 262줄)
- **목적:** 의존성 없는 JSON 읽기/쓰기 (IDE 클래스패스 없이 단위 테스트하려고, `:3-9`). `Json.parse` `:14`, `parseOrNull` `:24`, `stringify` `:30`, 확장 함수 `str`/`long`/`int`/`double`/`bool`/`obj`/`list` `:250-262`.

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/editor/CellDecorator.kt` (약 181줄)
- **목적:** 편집기별 꾸밈: 셀 마커 거터 실행/중단 아이콘, 다른 사람이 잠근 셀 색, 줄 끝 메모 (`:39-43`).
- **주요 심볼:** `Palette` `:31` (테마 색을 하드코딩: `0xC65F3C`/`0xE07A55` 등), `CellDecorator` `:43`, `CellGutterRenderer` `:127`, `NoteRenderer` `:167`.
- **주의점:** 색은 `extensions/vscode-darkpyonix-theme/README.md:22-26` 팔레트와 같은 값을 두 번 정의한다.

### `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/toolwindow/OutputsToolWindow.kt` (약 229줄)
- **목적:** 선택된 편집기의 노트북 셀별 최신 출력 툴 윈도 (`:50-54`). `OutputsToolWindowFactory` `:41` (`plugin.xml:26`), `OutputsPanel` `:54`.

### 작은 파일

| 파일 | 줄 | 한 줄 요약 |
|---|---|---|
| `extensions/README.md` | 13 | 세 확장 표와 상태 (`:9-13`). 추적 이슈 #15 |
| `extensions/vscode-darkpyonix/README.md` | 77 | 기능별 요구 ID와 소스 위치 표 (`:12-`) |
| `extensions/vscode-darkpyonix/package.json` | 229 | 매니페스트 (위 명령/설정 표). 스크립트 `build`, `typecheck`, `test`(vitest), `test:e2e`, `package` (`:212-219`) |
| `extensions/vscode-darkpyonix/LICENSE` | 204 | Apache-2.0 |
| `extensions/vscode-darkpyonix/.vscodeignore` | 6 | `dist/extension.js`, `package.json`, `README.md`, `LICENSE`, `media/**`만 패키지 |
| `extensions/vscode-darkpyonix/esbuild.mjs` | 27 | `src/extension.ts`를 `dist/extension.js`(CJS, node18, `vscode` external)로. `--e2e`면 `dist/e2e/suite.js`도 (`:18-21`). 고아 후보 기각 (npm 스크립트 `package.json:213`) |
| `extensions/vscode-darkpyonix/vitest.config.mjs` | 8 | `test/unit`, `test/integration`, timeout 15초. 고아 후보 기각 (vitest 설정) |
| `extensions/vscode-darkpyonix/tsconfig.json` | 17 | ES2022, strict, `src`+`test` |
| `extensions/vscode-darkpyonix/src/run/outputs.ts` | 79 | nbformat 출력을 MIME 항목으로. `STDOUT_MIME`/`STDERR_MIME`/`ERROR_MIME` `:5-7`, `convertOutput` `:55`, 리치 MIME 우선 `mimeRank` `:46`. `decodeText` `:77`은 테스트만 쓴다 |
| `extensions/vscode-darkpyonix/test/corpus/cases.ts` | 20 | 왕복 테스트 케이스 (core `tests/test_fr_f1_format.py`에서) |
| `extensions/vscode-darkpyonix/test/corpus/darkpyonix_format.py` | 202 | 기준 노트북 예제 파일 (파서 테스트 입력) |
| `extensions/vscode-darkpyonix/test/e2e/runTest.mjs` | 43 | 설치된 VS Code로 e2e. `VSCODE_PATH` 기본 macOS 앱 경로 (`:13`), 작업 폴더 `.scratch/vscode-e2e` (`:3`) |
| `extensions/vscode-darkpyonix/test/e2e/suite.ts` | 116 | 실제 확장 + 가짜 매니저 e2e (7개 테스트) |
| `extensions/vscode-darkpyonix/test/fake/fakeHost.ts` | 108 | 배열 기반 `FakeHost`, `FakeSink`, `until` |
| `extensions/vscode-darkpyonix/test/fake/fakeManager.ts` | 385 | 프로세스 안 가짜 매니저 HTTP 서버 (문서, 잠금, presence, 실행, SSE). 참조 구현이 아니다 (`:1-3`) |
| `extensions/vscode-darkpyonix/test/integration/collab.test.ts` | 291 | 테스트 19개: 실제 클라이언트, SSE, 세션, 트래커를 가짜 매니저에 연결 |
| `extensions/vscode-darkpyonix/test/integration/discovery.test.ts` | 85 | 테스트 5개: 등록 파일 탐색과 spawn. `.scratch` 사용 (`:8`) |
| `extensions/vscode-darkpyonix/test/unit/cells.test.ts` | 112 | 테스트 10개: 편집기 뷰와 바이트 정확 저장 |
| `extensions/vscode-darkpyonix/test/unit/model.test.ts` | 170 | 테스트 11개: `DocModel.apply`, `RunTracker` |
| `extensions/vscode-darkpyonix/test/unit/parser.test.ts` | 164 | 테스트 9개: core FR-F1 테스트 이식 |
| `extensions/vscode-darkpyonix/test/unit/sse_outputs.test.ts` | 52 | 테스트 4개: SSE 파서, 출력 변환, `mapPath` |
| `extensions/vscode-darkpyonix-theme/package.json` | 32 | 테마 2개 등록: Light(`vs`), Dark(`vs-dark`) (`:18-30`). `repository`는 upstream 저장소 (`:16`) |
| `extensions/vscode-darkpyonix-theme/themes/DarkPyonix Dark-color-theme.json` | 392 | Dark 색 테마 (`colors` + `tokenColors` scope 40개). 여기서 만든 파생본 |
| `extensions/vscode-darkpyonix-theme/themes/DarkPyonix Light-color-theme.json` | 391 | Light 색 테마 (upstream 그대로) |
| `extensions/vscode-darkpyonix-theme/README.md` | 36 | upstream 커밋 `5c2dbd7...`에서 가져온 내력, 팔레트 표 (`:20-26`) |
| `extensions/vscode-darkpyonix-theme/CHANGELOG.md` | 14 | 0.0.2: 가져옴, Dark 추가 |
| `extensions/vscode-darkpyonix-theme/LICENSE` | 204 | Apache-2.0 (upstream은 MIT, `README.md:9`) |
| `extensions/vscode-darkpyonix-theme/.gitattributes` | 2 | `* text=auto` |
| `extensions/vscode-darkpyonix-theme/.gitignore` | 136 | Node 템플릿 gitignore (테마에는 대부분 무관) |
| `extensions/vscode-darkpyonix-theme/.vscode/launch.json` | 17 | Extension Development Host 실행 설정 |
| `extensions/vscode-darkpyonix-theme/.vscodeignore` | 4 | `.vscode/**`, `.vscode-test/**`, `.gitignore`, quickstart 제외 |
| `extensions/vscode-darkpyonix-theme/vsc-extension-quickstart.md` | 28 | `yo code` 생성 안내문 (잔해) |
| `extensions/intellij-darkpyonix/README.md` | 91 | 빌드 명령 (`:19-23`), 기능, 구조, 미검증 목록 (`:71-88`) |
| `extensions/intellij-darkpyonix/LICENSE` | 204 | Apache-2.0 |
| `extensions/intellij-darkpyonix/.gitignore` | 5 | `.gradle`, `.idea`, `.intellijPlatform`, `.kotlin`, `build` |
| `extensions/intellij-darkpyonix/build.gradle.kts` | 54 | Kotlin JVM 21, IntelliJ Platform, JUnit 4, `runPyCharm` 등록 (`:41-48`) |
| `extensions/intellij-darkpyonix/gradle.properties` | 16 | `pluginVersion 0.1.0`, `platformVersion 2025.3.6.1`, `pluginSinceBuild 253` |
| `extensions/intellij-darkpyonix/settings.gradle.kts` | 25 | Kotlin 2.4.20, platform settings 2.19.0, foojay |
| `extensions/intellij-darkpyonix/gradle/wrapper/gradle-wrapper.jar` | 157 | 바이너리 (Gradle wrapper) |
| `extensions/intellij-darkpyonix/gradle/wrapper/gradle-wrapper.properties` | 9 | Gradle 9.8.0 |
| `extensions/intellij-darkpyonix/gradlew` | 248 | Gradle 표준 셸 래퍼 |
| `extensions/intellij-darkpyonix/gradlew.bat` | 112 | Gradle 표준 Windows 래퍼 |
| `extensions/intellij-darkpyonix/src/main/resources/META-INF/plugin.xml` | 53 | 플러그인 설명자 (위 액션 표). `editorFactoryListener`, `toolWindow`, `notificationGroup`, `applicationConfigurable` (`:23-30`) |
| `extensions/intellij-darkpyonix/src/main/resources/META-INF/darkpyonix-python.xml` | 7 | Python 지원이 있을 때 `.pynb`를 Python 파일 타입에 추가 |
| `.../intellij/editor/NotebookEditorFactoryListener.kt` | 37 | 노트북 편집기마다 `CellDecorator` 부착 (`:12-29`) |
| `.../intellij/manager/EventStream.kt` | 90 | 데몬 스레드에서 이벤트 구독, `Last-Event-ID` 재연결 (`:12-17`) |
| `.../intellij/protocol/SseParser.kt` | 74 | 줄 단위 SSE 파서. `id` 없는 메시지는 이전 `lastEventId` 유지 (`:6-12`) |
| `.../intellij/settings/DarkPyonixSettings.kt` | 73 | 앱 설정 (위 표) |
| `.../intellij/settings/DarkPyonixConfigurable.kt` | 55 | 설정 화면 (Kotlin UI DSL) |
| `.../src/test/.../format/NotebookFormatTest.kt` | 140 | 테스트 10개: 파서 |
| `.../src/test/.../json/JsonTest.kt` | 35 | 테스트 3개: JSON |
| `.../src/test/.../protocol/CellSyncTest.kt` | 91 | 테스트 7개: 매칭과 reconcile |
| `.../src/test/.../protocol/DocumentStateTest.kt` | 187 | 테스트 10개: 이벤트 적용 |
| `.../src/test/.../protocol/SseParserTest.kt` | 50 | 테스트 5개: SSE 파서 |

(`...`은 `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix` 또는 `extensions/intellij-darkpyonix/src/test/kotlin/dev/darkpyonix`.)

## 이 모듈을 수정할 때 주의할 점

- **포맷 규칙이 세 곳에 있다.** 커널 `_parser.py`(darkpyonix-core), `src/format/parser.ts`, `format/NotebookFormat.kt`. 마커 정규식, `KNOWN_TYPES`, 별칭, `source_sha256` 계산을 바꾸면 셋을 함께 바꾸고 `test/unit/parser.test.ts`, `NotebookFormatTest.kt`를 같이 고친다. 어긋나면 stale 판정과 셀 매칭이 틀린다.
- **매니저 API 계약은 외부 저장소다.** `src/manager/types.ts`와 `ManagerClient.kt`는 1.0.0-draft.3에 맞춰 있다. 가짜 매니저(`test/fake/fakeManager.ts`)는 참조 구현이 아니므로 (`:3`), 테스트 통과가 실제 매니저 호환을 뜻하지 않는다. README도 실제 매니저로는 돌려 보지 않았다고 적는다 (`extensions/README.md:11`).
- **스냅샷 `seq` 해석이 두 클라이언트에서 다르다** (`session.ts:113-115` 대 `DocumentState.kt:100-111`). 어느 한쪽은 이벤트 하나를 놓치거나 중복 처리한다. 매니저 문서로 확인 후 한쪽에 맞춘다.
- **IntelliJ는 커널 ID를 직접 계산한다** (`NotebookFormat.kt:176`). VS Code는 목록에서 `path`로 찾는다. 매니저의 커널 ID 규칙이 바뀌면 IntelliJ만 깨진다.
- **팔레트 값이 두 번 정의돼 있다:** 테마 JSON과 `CellDecorator.kt:31-37`.
- **확장 ID 대소문자:** 노트북 확장 publisher는 `darkpyonix`, 테마는 `DarkPyonix`. `ember/proxy/dpx/vscode/runtime.py:51`은 소문자로 쓴다. 대소문자 비교에 의존하는 코드를 추가할 때 주의한다.
- **VS Code 쪽 편집기 → 서버 동기화는 직렬 큐 하나다** (`session.ts:154-160`). 큐 안에서 오래 기다리는 작업을 넣으면 모든 편집과 원격 반영이 멈춘다.
- **빌드 산출물 경로 결합:** `ember/ose/check-extensions.sh:16-18`와 `ember/ose/stage-extensions.sh:16`가 `extensions/vscode-darkpyonix/dist/extension.js`와 폴더 이름에 기대므로, 폴더나 출력 경로를 바꾸면 OSE 빌드도 고친다.
- **Ember SPEC과 ID 이름이 겹친다.** 확장 주석의 FR-* 는 darkpyonix-core SPEC이다. 이 저장소 SPEC 번호로 해석하지 않는다.
