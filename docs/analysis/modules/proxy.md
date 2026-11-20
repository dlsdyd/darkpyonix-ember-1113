# 모듈: proxy

- 경로: `ember/proxy/` (modules.md 정규식 `^ember/proxy/`, 단 `ember/proxy/tests/`는 [tests](tests.md) 모듈)
- 규모: 파일 51개 / 약 10,151줄 (Python 약 3,000줄, 정적 HTML/JS/CSS 약 3,260줄, companion 확장 약 1,670줄, 문서 약 1,640줄)
- 레이어: API (VS Code Web 앞단 리버스 프록시 + 자체 화면 + 로그인)
- 한 줄 책임: 순정 VS Code Web(`code serve-web` 또는 OSE 서버)을 감싸서 로그인 게이트, 모바일 오버레이 주입, 홈 런처(에이전트 대화 열람), ember node 영속 터미널 중계(`/__terms/*`), 탭 분리(detach) 웹뷰 측을 제공한다.
- 의존하는 모듈: [node](node.md) (`/terms` HTTP/WS API와 `~/.ember/node/local.json`, `ember/node/src/api.rs:221-226`), [bridge](bridge.md) (`detach.js` 메시지 형식, `ember/bridge/src/messages.rs:14`). 그 외 외부: VS Code Web 런타임, `~/.claude`, `~/.codex`.
- 이 모듈을 쓰는 모듈: [server-api](server-api.md) (`python -m dpx.serve`가 알린 URL을 `ide_url`로 사용, `ember/server/src/api/ide.rs:66`, `:412`), [bridge](bridge.md) (`detach.js`가 보내는 `tab_detach`를 받음, `ember/bridge/src/lib.rs:3`). 코드 import로 이 모듈을 부르는 다른 모듈은 없다 (`docs/analysis/_raw/imports.tsv`에서 `ember/proxy` 밖 → 안 간선 0개).

프로세스는 두 개다. 브라우저는 프록시(기본 :8888)에 붙고, 프록시가 루프백의 VS Code 웹 서버(기본 :9092)로 중계한다 (`ember/proxy/README.md:19-23`, `ember/proxy/dpx/config.py:15-18`). 별도로 선택 사항인 허브 앱(`uvicorn dpx.hub.server:app`)이 있다 (`ember/proxy/dpx/hub/server.py:26`).

## 요청 한 건이 지나는 길 (`main.py`)

| 순서 | 조건 | 처리 | 위치 |
|---|---|---|---|
| 0 | 모든 요청 | `>> METHOD path` 로그 | `ember/proxy/main.py:196` |
| 1 | `/healthz` 또는 `/__ext/` 로 시작 | 게이트 없이 다음 핸들러로 | `main.py:199-200` |
| 2 | `is_public_path()`가 거짓 | 세션 쿠키 `dpx_session` 검증. 실패 시 HTML GET은 303 `/login?next=...`, 그 외 401 JSON | `main.py:204-209` |
| 2b | `?folder=`/`?workspace=`가 `DPX_FOLDER_ROOTS` 밖 | 403 JSON | `main.py:213-217` |
| 3 | HTML GET `/login`, `/` | `workspace_login.html`, `home.html`(folder 없음), `frame.html`(folder 있고 `xmo!=embed`) | `main.py:151-177` |
| 4 | 워크벤치 메인 CSS 경로 | 업스트림 CSS 뒤에 `overlay.css` 덧붙임 | `main.py:227-228` |
| 5 | HTML GET 웹뷰 호스트 `/webview/browser/pre/index.html` | `<script src="/__kb.js">` 삽입 | `main.py:240-241` |
| 6 | HTML GET `/` (embed) | viewport, overlay.css/js, detach.js, `configurationDefaults` 삽입 | `main.py:247-249` |
| 7 | 나머지 | catch-all이 업스트림으로 스트리밍 중계 | `main.py:258-261` |
| WS | 모든 WebSocket 경로 (`/__terms/*/attach` 제외) | 세션 검증 후 `relay_websocket` | `main.py:264-277` |

미들웨어는 HTTP만 본다. WebSocket은 `websocket_proxy`(`main.py:270`)와 `attach_term`(`ember/proxy/dpx/terms/api.py:162`)이 각자 세션을 확인한다.

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `python -m dpx.serve` | CLI | `ember/proxy/dpx/serve.py:197` | 런타임 서버 + 프록시를 띄우고 stdout에 `{"event":"ready","url":...}` 한 줄을 낸다. ember server의 `ide_url` 출처 (`ember/server/src/api/ide.rs:66`) |
| `uvicorn main:app` | ASGI 앱 | `ember/proxy/main.py:53` | 프록시 본체 |
| `uvicorn dpx.hub.server:app` | ASGI 앱 | `ember/proxy/dpx/hub/server.py:135` | 다중 머신 허브 |
| `python -m dpx.hub.connector` | CLI | `ember/proxy/dpx/hub/connector.py:185` | 허브로 나가는 커넥터 |
| HTTP 라우트 전체 | HTTP | `docs/analysis/_raw/routes.md` "ember/proxy" 절 | `/auth/*`, `/__agents/*`, `/__workspaces`, `/__terms/*`, `/__ext/*`, `/__runtime`, 정적 자산 |
| `tab_detach` 메시지 | webview → 네이티브 | `ember/proxy/static/detach.js:248` | `buildDetachMessage`. 형식은 `ember/bridge/src/messages.rs`와 맞춘다 |
| `window.__emberBridge.receive(json)` | 네이티브 → webview | `ember/proxy/static/detach.js:578-582` | `ember-bridge` DOM 이벤트로 전달 |
| `window.__xmo` | iframe JS API | `ember/proxy/static/overlay.js:854` | `frame.html`(부모)이 VS Code iframe을 조종하는 API |
| `ember-terminals` 확장 | VS Code 웹 확장 | `ember/proxy/companion/package.json:2` | 통합 터미널을 ember node 세션으로 바꾼다 |
| `ember/vectors/bridge/detach_vectors.json` | 공유 테스트 벡터 | `ember/proxy/README.md:386` | `buildWorkspaceQuery`와 `ember-bridge`가 함께 검증 |

## 파일별 요약

### `ember/proxy/main.py` (약 277줄)
- **목적:** 앱 조립과 요청 라우팅만 한다 (`main.py:3`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | Python 버전 검사 | 모듈 코드 | 30 | 3.10 미만이면 `SystemExit` |
  | `app` | FastAPI | 53 | CORS `allow_origins=["*"]`, `allow_credentials=True` (55-61) |
  | `init_db(); app.mount("/auth", auth_app)` | 모듈 코드 | 67-68 | 로그인 앱을 같은 오리진에 마운트 |
  | `_NO_USERS_HELP` | 상수 | 70 | 계정이 없을 때 시작 경고 문구 |
  | `_start_hub_connector()` | startup 훅 | 89 | `DPX_HUB_URL`이 있으면 커넥터를 같은 루프에서 시작 |
  | `overlay_css`/`overlay_js`/`detach_js`/`webview_kb_js` | 라우트 | 107-127 | `static/` 자산 응답 |
  | `favicon` | 라우트 | 130 | 204 |
  | `vscode_runtime` | 라우트(sync) | 137 | `runtime.detect()` JSON |
  | `healthz` | 라우트 | 146 | `ok`. catch-all보다 먼저 등록해야 한다 (144) |
  | `_serve_our_page(request, path, xmo)` | 함수 | 151 | 자체 화면 선택. `workspaces.record()` 호출 (175) |
  | `route_request` | HTTP 미들웨어 | 191 | 위 표의 1-7단계 |
  | `catch_all` | 라우트 | 258 | GET/POST/PUT/PATCH/DELETE/OPTIONS/HEAD 중계 |
  | `websocket_proxy` | WS 라우트 | 264 | 세션 없으면 1008로 닫음 |
- **입력 → 출력:** 브라우저 요청 → 자체 화면, 주입된 VS Code 문서, 또는 업스트림 응답.
- **의존:** `dpx/assets.py`, `dpx/auth/api.py`, `dpx/auth/gate.py`, `dpx/home/*`, `dpx/config.py`, `dpx/terms/api.py`, `dpx/vscode/*`.
- **사용처:** `ember/proxy/dpx/serve.py:70` (`uvicorn main:app`으로 자식 실행).
- **부수효과:** import 시점에 SQLite 생성(`init_db`, 67), 최근 폴더 파일 쓰기(`workspaces.record`, 175, 234).
- **주의점:** 라우터 등록 순서가 동작을 정한다. `terms_api.router`가 catch-all WS보다 먼저 포함되어야 `/__terms/{id}/attach`가 VS Code 중계에 가려지지 않는다 (`main.py:84-86`). `/healthz`도 같다 (144).

### `ember/proxy/dpx/config.py` (약 68줄)
- **목적:** 환경 변수, 경로, 상수를 한곳에 둔다 (`config.py:1-6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `UPSTREAM_HOST`/`UPSTREAM_PORT`/`UPSTREAM_BASE` | 상수 | 15-18 | `XMO_UPSTREAM_HOST`(127.0.0.1), `XMO_UPSTREAM_PORT`(9092) |
  | `UPSTREAM_WS_SCHEME` | 상수 | 19 | `UPSTREAM_SCHEME`이 `http`로 고정이라 항상 `ws` |
  | `FOLDER_ROOTS` | 상수 | 25 | `parse_roots(DPX_FOLDER_ROOTS)` |
  | `BASE_DIR`, `STATIC_DIR`, `RECENT_FILE`, `DB_FILE`, `HUB_STATE_FILE`, `MACHINE_ID_FILE` | 경로 | 32-37 | 모두 `ember/proxy/` 바로 아래 |
  | `ASSET_VERSION` | 상수 | 43 | 프로세스 시작 시각. 주입 자산 캐시 무효화용 쿼리 |
  | `TAB_DETACH` | 플래그 | 48 | `DPX_TAB_DETACH`(기본 켜짐) |
  | `EXT_TTL_SECONDS` | 상수 | 53 | 30.0 |
  | `RECENT_LIMIT` | 상수 | 56 | 20 |
  | `EMBER_NODE_URL`/`EMBER_NODE_TOKEN`/`EMBER_NODE_STATE_DIR` | 상수 | 64-68 | ember node 엔드포인트 재정의 |
- **사용처:** `main.py:46`, `dpx/assets.py:15`, `dpx/auth/api.py:32`, `dpx/home/workspaces.py:12`, `dpx/hub/server.py:43`, `dpx/hub/connector.py:39`, `dpx/terms/api.py:33`, `dpx/vscode/inject.py:23`, `dpx/vscode/proxy.py:19`, `dpx/vscode/extension.py:16`.
- **주의점:** 문서는 "모든 설정이 여기 있다"고 하지만 허브(`hub/server.py:48-50`), 커넥터(`hub/connector.py:43-48`), 런타임(`vscode/runtime.py:88-176`), 서버 실행기(`serve.py:169-181`), 인증(`auth/api.py:80-81`)이 `os.environ`을 직접 읽는다.

### `ember/proxy/dpx/assets.py` (약 61줄)
- **목적:** `static/` 파일을 읽어 응답으로 만든다. 프로세스 수명 동안 캐시한다.
- **주요 심볼:** `NO_CACHE`(17), `_CACHE_ENABLED`(20, `DPX_NO_ASSET_CACHE`), `read(name)`(23), `page(name, status_code)`(41), `script(name)`(50), `stylesheet(name)`(57). 파일이 없으면 500 `static/<name> is missing.`(36).
- **사용처:** `main.py:109-127,170-176`, `dpx/vscode/inject.py:56,62,82,101`, `dpx/vscode/proxy.py:42`.
- **주의점:** 허브는 이 모듈을 쓰지 않고 자체 `_page()`로 매 요청 파일을 읽는다 (`hub/server.py:344`). 같은 일을 두 곳에서 한다.

### `ember/proxy/dpx/auth/api.py` (약 279줄)
- **목적:** `/auth`에 마운트되는 독립 FastAPI 앱. 사용자, 세션, SQLite.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `SESSION_COOKIE` | 상수 | 35 | `"dpx_session"` |
  | `SESSION_TTL` | 상수 | 36 | 14일 |
  | `PBKDF_ROUNDS` | 상수 | 37 | 200,000 |
  | `_hash_pw(pw)` | 함수 | 46 | `secrets.token_bytes(16)` 솔트, `pbkdf2_hmac("sha256")`, 저장형 `salt_hex + "$" + dk_hex` |
  | `_verify_pw(pw, stored)` | 함수 | 52 | 같은 솔트로 다시 유도해 `hmac.compare_digest`로 hex 비교. 예외는 모두 False |
  | `init_db()` | 함수(공개) | 61 | `users`, `sessions` 테이블 생성. 사용자가 0명이고 `DPX_USERNAME`+`DPX_PASSWORD`가 둘 다 있으면 첫 계정 생성 |
  | `create_session(username)` | 함수 | 93 | `secrets.token_urlsafe(32)`를 그대로 `sessions.id`에 저장, 만료된 세션 청소 |
  | `validate_session(sid)` | 함수(공개) | 103 | 존재하고 미만료면 True. 예외는 False |
  | `session_user(sid)` | 함수 | 115 | 세션의 사용자 이름 |
  | `delete_session`, `add_user`, `list_users`, `user_count`, `delete_user`, `set_password` | 함수 | 129-170 | 사용자 관리 |
  | `auth_app` | FastAPI | 173 | 라우트: `POST /login`(181), `POST /logout`(203), `GET /me`(211), `GET/POST /users`(225, 232), `DELETE /users/{username}`(249), `POST /change-password`(262) |
  | `_require_user(request)` | 함수 | 221 | 로그인만 확인한다 (역할 없음, 218-220 주석) |
- **입력 → 출력:** JSON `{username, password}` → 쿠키 `dpx_session`(`httponly`, `samesite="lax"`, `path="/"`, `secure` 없음, 198-199).
- **의존:** `dpx/config.py`(`DB_FILE`).
- **사용처:** `main.py:42,67-68,205,270`, `dpx/hub/server.py:42,136-137,151`, `dpx/terms/api.py:150`.
- **부수효과:** SQLite 파일 `ember/proxy/darkpyonix.db` 읽기/쓰기.
- **주의점 (보안):** 비밀번호 저장과 확인 방식은 노트 파일 "A" 표의 보안 항목에 모아 두었다. 요지: 솔트 있는 PBKDF2-SHA256 20만 회, 상수 시간 비교는 맞다. 다만 로그인 시도 제한이 없고(181-200), 없는 사용자는 해시 계산 없이 즉시 401을 내서 응답 시간으로 사용자 존재를 가늠할 수 있고(192-194), 세션 토큰이 DB에 평문으로 남고(97), 비밀번호 변경이 다른 세션을 끊지 않고(167-170), 아무 로그인 사용자나 계정을 만들고 지울 수 있다(232-259). `with _conn() as c`는 커밋만 하고 연결을 닫지 않는다 (40-43) [추정: CPython 참조 카운트로 곧 닫힌다].

### `ember/proxy/dpx/auth/gate.py` (약 19줄)
- **목적:** 세션 없이 열리는 경로를 정한다.
- **주요 심볼:** `_PUBLIC_EXACT = {"/healthz", "/login", "/favicon.ico"}`(13), `_PUBLIC_PREFIX = ("/auth", "/__ext", "/__overlay", "/__kb", "/__detach")`(14), `is_public_path(path)`(17).
- **사용처:** `main.py:43,204`.
- **주의점:** 접두사 비교에 `/` 경계가 없다. `/authX...`, `/__extX...`, `/__overlayX...`처럼 공개 접두사로 시작하지만 실제 라우트가 없는 경로는 세션 없이 catch-all을 거쳐 업스트림으로 간다. `main.py:199`의 `/__ext/` 예외도 같은 구멍이다. 경로에 `..`가 섞여 업스트림에서 정규화되면 게이트 우회가 된다 [확인 필요: uvicorn/httpx의 점 세그먼트 처리]. 노트 A 표 참고.

### `ember/proxy/dpx/vscode/proxy.py` (약 155줄)
- **목적:** 업스트림으로 바이트를 그대로 넘긴다 (HTTP 스트리밍, WebSocket).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CLIENT` | 전역 `httpx.AsyncClient` | 25 | 30초 타임아웃, `follow_redirects=True`, 연결 64개 |
  | `_HOP_HEADERS` | 상수 | 32 | 제거할 응답 헤더 |
  | `upstream_url(path)` | 함수 | 35 | `UPSTREAM_BASE + path` |
  | `upstream_down(request)` | 함수 | 39 | HTML이면 `upstream_down.html` 502, 아니면 `{"error":"upstream unavailable"}` 502 |
  | `fetch(request, url, follow_redirects)` | 함수 | 46 | 본문 전체가 필요한 주입용 GET. 호출마다 새 클라이언트 |
  | `relay(request, url)` | 함수 | 58 | 요청 헤더 전부(Host, Cookie 포함) 전달, 응답 스트리밍 |
  | `relay_websocket(websocket, full_path)` | 함수 | 95 | `cookie`, `authorization`, 서브프로토콜만 전달. `websockets.connect(extra_headers=...)` (114-116) |
- **사용처:** `main.py:248,261,275`, `dpx/vscode/inject.py:51-101`.
- **부수효과:** 네트워크 (업스트림 HTTP/WS).
- **주의점:** `extra_headers`는 websockets 12.x 이름이라 `requirements.txt`의 `websockets==12.0` 고정이 필요하다 (`ember/proxy/requirements.txt:7-11`). 요청 본문은 `await request.body()`로 전부 버퍼링한다 (71). Host 헤더를 일부러 보존한다 (61-65, 태블릿 먹통 원인). 공유 `CLIENT`가 리다이렉트를 서버 쪽에서 따라가므로 업스트림의 3xx가 브라우저에 보이지 않는다 (27) [추정: 의도 여부 불명].

### `ember/proxy/dpx/vscode/inject.py` (약 101줄)
- **목적:** 업스트림 응답에 CSS/JS를 끼워 넣는 세 지점.
- **주요 심볼:** `MAIN_CSS_REGEX`(32), `WEBVIEW_HOST_HTML`(38), `is_main_css`(41), `is_webview_host`(45), `main_css`(49, 200 + `text/css`일 때만 덧붙임), `workbench_html`(68, `html_rewrite.workbench_inserts` 호출), `webview_kb`(85, `</head>` 앞에 `/__kb.js` 삽입).
- **사용처:** `main.py:227-249`.
- **주의점:** 오버레이는 최상위 워크벤치 문서(`/`)에만 넣는다. 확장 호스트 iframe 문서에 넣으면 안드로이드가 멈춘다 (`inject.py:12-15`, `main.py:243-246`).

### `ember/proxy/dpx/vscode/html_rewrite.py` (약 77줄)
- **목적:** FastAPI 없이 테스트할 수 있는 순수 문자열 재작성.
- **주요 심볼:** `_CONFIG_META`(16, `vscode-workbench-web-configuration` 메타의 `data-settings`), `DETACH_CONFIGURATION_DEFAULTS = {"workbench.editor.dragToOpenWindow": False}`(28), `add_configuration_defaults(html, defaults)`(31, 사용자가 이미 둔 키는 유지), `workbench_inserts(html, asset_version, detach)`(58, viewport, overlay.css, overlay.js, detach.js를 `<head>` 바로 뒤에 삽입).
- **사용처:** `dpx/vscode/inject.py:79`.
- **주의점:** 문서 형식이 예상과 다르면 원문 그대로 돌려준다 (35-49).

### `ember/proxy/dpx/vscode/roots.py` (약 81줄)
- **목적:** `?folder=`/`?workspace=`가 열 수 있는 폴더 제한 (파일 시스템 샌드박스가 아님, 8-10).
- **주요 심볼:** `WORKSPACE_PARAMS`(20), `parse_roots(value)`(23, `os.pathsep` 구분), `normalise(path)`(31, `expanduser` + `realpath` + `normcase`), `is_allowed(folder, roots)`(40, 루트 없으면 항상 True, `file://`만 허용, 그 외 URI 거부, `commonpath` 비교), `refused_param(query, roots)`(69), `roots_from_env()`(79).
- **사용처:** `dpx/config.py:11,25`, `main.py:213`, `dpx/serve.py:93`.
- **주의점:** `roots_from_env()`는 저장소 어디서도 부르지 않는다. 쿼리는 `dict(request.query_params)`로 넘어와 같은 이름의 마지막 값만 본다 (`main.py:213`). 업스트림에 넘기는 쿼리도 같은 방식이라 지금은 일관된다 (`proxy.py:73`).

### `ember/proxy/dpx/vscode/runtime.py` (약 268줄)
- **목적:** 두 런타임(`ose` 기본, `vsc`) 감지, 서버 명령 구성, 기본 확장 설치 (`FR-W4`, `FR-W6`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `RUNTIMES`, `DEFAULT_RUNTIME` | 상수 | 43-44 | `("ose","vsc")`, `"ose"` |
  | `DEFAULT_EXTENSIONS` | 상수 | 51 | `darkpyonix.vscode-darkpyonix`, `darkpyonix.vscode-darkpyonix-theme` |
  | `DEFAULT_OSE_ARGS` | 상수 | 54 | `{host}` `{port}` `{data_dir}` 템플릿 |
  | `CHECK_TIMEOUT`/`INSTALL_TIMEOUT` | 상수 | 57-58 | 15초 / 180초 |
  | `VSC_GUIDE`, `OSE_GUIDE` | 상수 | 60, 79 | 설치 안내 문구 |
  | `detect(rt, command)` | 함수 | 105 | `<cmd> --version` 실행, 결과 dict |
  | `server_cmd(...)` | 함수 | 150 | `vsc`는 `serve-web ... --without-connection-token` |
  | `_bundled_vsix(ext_id)` | 함수 | 166 | 저장소 `extensions/dist/<name>-*.vsix` 탐색 (`parents[4]` = 저장소 루트) |
  | `default_extensions()` | 함수 | 174 | |
  | `extension_id(entry)`, `installed_ids(dir)` | 함수 | 182, 192 | |
  | `prepare_data_dir(rt, data_dir)` | 함수 | 208 | OSE에서 `extensions.verifySignature=false`를 Machine/User 설정에 씀 |
  | `ensure_extensions(entries, dir, command)` | 함수 | 235 | 없는 것만 `--install-extension` |
- **사용처:** `main.py:141`, `dpx/serve.py:175,200,218-220,231`.
- **부수효과:** 외부 프로세스 실행, 설정 파일 쓰기, 확장 디렉터리 생성.
- **주의점:** README는 기본 확장을 "DarkPyonix theme" 하나로 적지만 코드는 두 개다 (`ember/proxy/README.md:140`, `runtime.py:51`). `/__runtime`은 요청마다 `--version` 프로세스를 띄운다 (`main.py:141`).

### `ember/proxy/dpx/vscode/extension.py` (약 57줄)
- **목적:** companion 확장 하트비트 게이트와 `/__ext/ping`, `/__ext/state`.
- **주요 심볼:** `EXT_STATE`(22, 전역 dict), `active()`(25), `_record_ping`(30), `_ping_age`(38), `ext_ping`(44), `ext_state`(55).
- **사용처:** `main.py:83` (라우터만).
- **주의점:** `active()`를 읽는 곳이 없고, `/__ext/ping`을 보내는 코드도 저장소에 없다 (grep). README도 "plumbing only, unused"로 적는다 (`ember/proxy/README.md:258`). docstring의 `app/extension` 경로는 존재하지 않는다 (4).

### `ember/proxy/dpx/terms/api.py` (약 211줄)
- **목적:** ember node 영속 터미널을 `/__terms/*`로 중계한다. node 베어러 토큰은 프록시에만 있다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `CLIENT` | 전역 httpx | 40 | 15초/연결 5초 |
  | `endpoint()` | 함수 | 43 | 매 요청 `node.discover()` (node 재시작 반영) |
  | `_forward(method, path, params, body)` | 함수 | 52 | 없으면 503, 연결 실패 502, 그 외 node 응답 그대로 |
  | `_json_body` | 함수 | 65 | |
  | 라우트 | HTTP | 75-145 | `_status`, 목록, 생성, 조회, 삭제, snapshot, control, kill |
  | `_ws_authorized(websocket)` | 함수 | 148 | `same_origin` + 세션 |
  | `attach_term` | WS | 156 | 텍스트 프레임만 node로, node 프레임은 그대로 브라우저로 |
- **사용처:** `main.py:47,86`.
- **부수효과:** 네트워크 (ember node HTTP/WS), `~/.ember/node/local.json` 읽기.
- **주의점:** HTTP 라우트는 미들웨어 세션 게이트 뒤에 있지만 Origin 검사는 없다. CORS 설정(`main.py:55-61`)과 겹쳐 같은 사이트의 다른 오리진 페이지가 자격 증명을 실어 `POST /__terms`로 셸 세션을 만들 수 있다 [확인 필요]. 노트 A 표 참고.

### `ember/proxy/dpx/terms/node.py` (약 175줄)
- **목적:** `/__terms` 중계의 순수 도우미 (FastAPI, 네트워크 없음).
- **주요 심볼:** `LOCAL_ENDPOINT_FILE`(15), `ORIGINS`(19), `BROWSER_ORIGINS = ("ide-vscode","ide-ember")`(20), `_CREATE_KEYS`(22), `_ID`(25, `^[A-Za-z0-9_-]{1,64}$`), `NodeEndpoint`(29, `http()`, `ws()`, `headers()`), `discover(url, token, state_dir)`(48), `valid_id`(66), `sanitize_create(body, home)`(89, 알 수 없는 키 제거, origin은 IDE만, `program`은 키 하나짜리 dict), `sanitize_query`(125), `sanitize_control`(141), `sanitize_kill`(152, signal 1..64), `same_origin(origin, host)`(165, Origin 없으면 통과).
- **사용처:** `dpx/terms/api.py:34,45,90-140,151`.
- **주의점:** `program`의 내용(`argv`/`shell`)은 node가 다시 검증한다고 적혀 있다 (`node.py:5`, `:118-122`). 즉 세션을 가진 브라우저는 임의 명령을 실행할 수 있고 그것이 설계다.

### `ember/proxy/dpx/home/api.py` (약 108줄)
- **목적:** 홈 화면 JSON API.
- **주요 심볼:** `router`(27), `agents_mod` import 실패 허용(32-36), `list_workspaces`(43), `agents_workspaces`(49, 어댑터 작업공간 + 최근 폴더 병합, `to_thread`), `agents_conversations`(77), `agents_transcript`(91, 없으면 404 문구), `agents_resume`(104).
- **사용처:** `main.py:44,82`.
- **주의점:** `DPX_FOLDER_ROOTS`를 적용하지 않는다. 루트 밖 폴더의 대화 목록과 전문도 보인다.

### `ember/proxy/dpx/home/workspaces.py` (약 44줄)
- **목적:** 최근 연 폴더 기록 `_xmo_recent.json`.
- **주요 심볼:** `RECENT_WORKSPACES`(15, 모듈 import 시 파일에서 읽는 전역 리스트), `record(folder)`(22, 앞에 넣고 20개로 자르고 파일에 씀, 실패 무시), `folder_key`(36), `folder_name`(41).
- **사용처:** `main.py:175,234`, `dpx/home/api.py:44-79`.
- **주의점:** `folder_key`/`folder_name`은 `dpx/agents/base.py:80-90`의 `folder_name`/`norm_folder`와 같은 구현이다.

### `ember/proxy/dpx/agents/base.py` (약 258줄)
- **목적:** 에이전트 어댑터 인터페이스와 공용 모델.
- **주요 심볼:** `PREVIEW_MESSAGES=3`(32), `PREVIEW_CHARS=180`(33), `TAIL_BYTES=256KiB`(34), `Message`(39), `Conversation`(50, `source`는 디버깅용 파일 경로), `Workspace`(68), `folder_name`(80), `norm_folder`(86), `clip`(92), `read_tail_lines`(97), `read_head_lines`(117), `iter_json`(130), `count_lines`(143), `flatten_content`(151, 도구 결과는 `"↩ 결과"`, 도구 호출은 `"🔧 "` 접두), `AgentAdapter`(201), `pick_preview`(241), `home_dir()`(252, `DPX_HOME` → `USERPROFILE` → `HOME`).
- **사용처:** `dpx/agents/__init__.py:8`, `dpx/agents/claude_code.py:26`, `dpx/agents/codex.py:235`.

### `ember/proxy/dpx/agents/claude_code.py` (약 220줄)
- **목적:** `~/.claude/projects/*/*.jsonl` 파서.
- **주요 심볼:** `_ts`(35), `_is_noise`(47), `_message_of`(58), `ClaudeCodeAdapter`(70, `id="claude-code"`), `_find_file`(90, `/`, `\`, `..` 거부 후 전체 파일 스캔), `_summarize`(99, 앞 60줄 + 끝 256KiB, `(mtime,size)` 캐시), `_count_messages`(165, 8MB 넘으면 줄 수로 근사), `transcript`(191), `resume`(208, `claude --resume <cid>`).
- **사용처:** `dpx/agents/__init__.py:13`, `dpx/agents/codex.py:240` (`_ts`).
- **주의점:** 제목 우선순위: `custom-title` > 앞부분 `summary` > 끝부분 `summary` > 첫 사용자 발화 > 파일명 8자 (113-147).

### `ember/proxy/dpx/agents/codex.py` (약 143줄)
- **목적:** `~/.codex/sessions/**/*.jsonl` 파서 (실험적).
- **주요 심볼:** `_payload`(23), `_INJECTED`(29, Codex가 넣는 컨텍스트 블록 접두), `_message_of`(37), `CodexAdapter`(54), `_summarize`(81), `resume`(137, `codex resume <cid>`).
- **주의점:** `message_count=len(preview)`라 최대 3이다 (109). `cid`는 파일명(`rollout-<timestamp>-<id>`) 전체라 `codex resume`이 받는 id와 다를 수 있다 [확인 필요] (106-107, 142).

### `ember/proxy/dpx/hub/connector.py` (약 190줄)
- **목적:** 각 머신에서 허브로 WebSocket을 열어 스냅샷을 밀고 RPC에 답한다.
- **주요 심볼:** `HUB_URL`, `HUB_TOKEN`, `PUBLIC_URL`, `MACHINE_NAME`, `SNAPSHOT_INTERVAL`(20초), `SNAPSHOT_CONVERSATIONS`(40) (43-48), `machine_id()`(52, `_dpx_machine.json`), `machine_info`(71), `_snapshot`(82), `RPC_METHODS`(95: ping, workspaces, conversations, transcript, resume, snapshot), `_serve(ws)`(116, 변화 없으면 `beat`), `run_forever`(154, 토큰을 쿼리 `?token=`에 붙임 160, 지수 백오프 최대 60초), `start_background`(178).
- **사용처:** `main.py:97-99`.
- **부수효과:** 네트워크, 머신 id 파일 쓰기, 로컬 대화 파일 읽기.

### `ember/proxy/dpx/hub/server.py` (약 361줄)
- **목적:** 여러 머신의 스냅샷을 모아 홈 화면 하나로 보여주는 별도 앱.
- **주요 심볼:** `HUB_TOKEN`(48), `OFFLINE_AFTER`(49, 75초), `RPC_TIMEOUT`(50, 25초), `Machine`(55, `online`, `to_dict`, `rpc`, `resolve`), `MACHINES`(109, 전역 dict), `save_state`/`load_state`(112, 122, `_dpx_hub_state.json`), `app`(135, `/auth` 마운트, `/static` 공개 마운트 138-139), `hub_connect`(163, `hmac.compare_digest`로 토큰 비교), REST(219-328), `_page`(344), `login_page`(352), `home`(357).
- **사용처:** 없음 (별도 실행).
- **부수효과:** 상태 파일 쓰기(스냅샷 수신마다), 같은 `darkpyonix.db` 사용.
- **주의점:** 토큰만 있으면 어떤 머신 id든 덮어쓸 수 있다 (177-187). 커넥터가 보낸 `public_url`을 검증 없이 `/api/machines/{mid}/open`의 `url`로 돌려주고 `hub_home.html`이 `location.href`로 이동한다 (298-301, `static/hub_home.html:336`).

### `ember/proxy/dpx/serve.py` (약 276줄)
- **목적:** `python -m dpx.serve`. 런타임 확인 → 기본 확장 설치 → 업스트림을 루프백 빈 포트에 시작 → 프록시 시작 → ready 줄 출력 → 감시.
- **주요 심볼:** `PROXY_DIR`(41), `DEFAULT_DATA_DIR`(43, `~/.ember/vscode-web`), `EXIT_NOT_INSTALLED=3`(44), `EXIT_START_FAILED=4`(45), `free_port`(50), `announce_url`(58), `proxy_cmd`(69), `proxy_env`(73, `XMO_UPSTREAM_*`, `DPX_FOLDER_ROOTS`, `DPX_RUNTIME` 주입), `resolve_roots`(88), `ready_line`(100), `wait_port`(107), `wait_http_ok`(120), `spawn`(135, POSIX는 새 세션), `stop`(141), `parse_args`(164), `main`(197).
- **사용처:** ember server 운영 절차 (`ember/server/src/api/ide.rs:412` 오류 문구).
- **부수효과:** 자식 프로세스 2개, 파일(`--announce-file`) 쓰기, SIGTERM 핸들러 설치.
- **주의점:** 업스트림 자식은 `env=` 없이 시작해 부모 환경(첫 계정 `DPX_PASSWORD` 포함)을 그대로 물려받는다 (231-233). VS Code 서버의 확장 호스트와 터미널에서 그 값이 보인다 [추정: VS Code 서버가 환경을 자식에 넘기는 기본 동작]. 업스트림은 `--without-connection-token`으로 루프백에 떠 있어 같은 기계의 다른 로컬 사용자는 프록시 로그인 없이 직접 붙을 수 있다 (`runtime.py:154-156`, `:54-55`). 종료 코드 2는 상수 없이 리터럴이다 (209, 213).

### `ember/proxy/static/overlay.js` (약 1,003줄)
- **목적:** VS Code 워크벤치(iframe 안)에 들어가 모바일 동작을 만든다: 숨긴 액티비티 바의 뷰 목록 읽기, 터치 → 클릭 다리, 키보드 정책, 상태 바 위로 고정, 부모용 `window.__xmo` API.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `XMO_EMBED`, `XMO_CHROME`, `XMO_PORTRAIT` | 상태 | 5, 11, 17 | URL의 `xmo=embed`, `xmochrome`, `xmoorient`로 초기화 |
  | `XMO_VIEW_SOURCES`, `XMO_VIEW_SKIP` | 상수 | 33, 38 | 액티비티 바 셀렉터, 채팅 컨테이너 제외 |
  | `xmoViewCache` + `xmo_views2_<folder>` | localStorage 캐시 | 43-66 | 폴더별 뷰 목록 |
  | `xmoScanViews` | 함수 | 108 | |
  | `xmoSendKey` | 함수 | 184 | 합성 키 이벤트 (`keyCode` 재정의) |
  | `xmoActivateView`, `xmoActivate` | 함수 | 246, 397 | 숨긴 항목 클릭, 오버플로 메뉴 키보드 조작 |
  | `xmoSaveChat` | 함수 | 507 | 채팅 입력을 `localStorage['xmo_chats_<folder>']`에 8개까지 저장 |
  | `xmoInitMenuTapBridge`, `xmoInitTouchClickBridge` | 함수 | 548, 565 | |
  | `XMO_KB_INPUT`, `XMO_KB_SURFACE`, `XMO_KB_HOLD` | 상수 | 594-604 | 키보드 정책 대상 |
  | `xmoInitKeyboardPolicy` | 함수 | 656 | 탭하지 않은 포커스는 `inputmode=none` 또는 blur |
  | `xmoEmbedChromeRestore`, `xmoEmbedStatusTop` | 함수 | 724, 736 | 상태 바를 제목 줄 아래로 고정 |
  | `apply`, `syncThemeColor` | 함수 | 832, 841 | |
  | `window.__xmo` | API | 854-981 | `setChrome`, `filesTap`, `terminal`, `agent`, `view`, `menu`, `views`, `activateView`, `codiconFont`, `dismissKeyboard`, `kbState`, `isFilesActive`, `ready`, `gutter`, `metrics`, `state`, `theme` |
  | 주기 작업 | 타이머 | 990-1001 | `xmoEmbedStatusTop` 250ms, `xmoAutoHideSidebarOnEditor` 400ms, 하위 트리 MutationObserver |
- **사용처:** `frame.html:148` (`frame.contentWindow.__xmo`), `dpx/vscode/html_rewrite.py:70-71`(주입), `main.py:112`.
- **주의점:** VS Code DOM 클래스와 aria 문구(`'Toggle Panel'`, `'Maximize Panel'` 등, 875-887)에 강하게 묶여 있다. VS Code 버전이 바뀌면 조용히 동작하지 않는다. `xmo_chats_*`는 쓰기만 하고 읽는 코드가 없다 (grep). 함수 하나가 파일 전체인 IIFE다.

### `ember/proxy/static/detach.js` (약 604줄)
- **목적:** 탭을 탭 줄 밖으로 끌어 놓으면 같은 작업공간의 새 IDE 창으로 옮긴다 (`FR-B1`, `FR-B2`, `FR-B4`). 네이티브 셸이 있으면 메시지, 없으면 `window.open`.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `KINDS`, `HANDLER_NAME='emberBridge'`, `EDITOR_KIND`, `THRESHOLD_PX=48` | 상수 | 54-58 | `ember/bridge/src/messages.rs`와 맞춘다 |
  | `distanceToRect`, `insideWindowBounds` | 함수 | 68, 77 | |
  | `createTracker` | 함수 | 89 | 드래그 상태 기계. `end()`가 결정과 이유를 낸다 (123-143) |
  | `uriToString`, `fromViewState`, `extractFromTransfer`, `parseStatusSelection` | 함수 | 155, 176, 204, 235 | 드래그 데이터와 DOM에서 파일/커서/스크롤 추출 |
  | `buildDetachMessage` | 함수 | 248 | `kind:'tab_detach'` |
  | `decodeIncoming` | 함수 | 271 | |
  | `buildWorkspaceQuery` | 함수 | 295 | `?folder=&payload=[["openFile",...],["gotoLineMode","true"]]` |
  | `hostWindows`, `pickTransport`, `send` | 함수 | 317, 332, 357 | WKWebView, WebView2, 브라우저 순 |
  | `install(win)` | 함수 | 370 | DOM 연결, `window.__emberBridge` |
- **사용처:** `ember/proxy/tests/js/detach.test.js`, `ember/bridge/src/messages.rs:14`, `dpx/vscode/html_rewrite.py:72-73`.
- **주의점:** 드래그 이벤트를 취소하거나 합성하지 않는다 (8-10). 결정은 `dragend`에서 `dropEffect==='none'`일 때만 한다.

### `ember/proxy/static/frame.html` (약 416줄)
- **목적:** 작업공간 래퍼. 부모 페이지가 바(nav)를 그리고 VS Code를 iframe(`?xmo=embed`)으로 띄운다.
- **주요 심볼:** `chromeMq`(129, `(pointer: coarse), (max-width: 1366px)`), `portraitMq`(134), iframe `src`(143), `api()`(148), `ICONS`(152), `withApi`(206), `syncActive`(215), `renderBar`(276), 딥링크 `?cid=` 처리(301-312), 설정 메뉴(325-332), `syncTheme`(337), `syncLayoutVars`(353), `applyChrome`(375), 1.5초 주기(400), 데스크톱 사이트 경고(407-414).
- **사용처:** `main.py:176`.
- **주의점:** `?agent=&cid=`는 에이전트 패널만 열고 대화를 이어 붙이지는 않는다 (297-300). 모든 쿼리를 iframe에 그대로 넘긴다 (138-143).

### `ember/proxy/static/home.html` (약 431줄)
- **목적:** 홈 런처. 해시 라우팅 `#/`(폴더 카드), `#/w/<b64>`(대화 목록), `#/c/<agent>/<cid>?f=<b64>`(전문).
- **주요 심볼:** `LS='xmo_home_ws'`(111, 북마크), `api(path)`(141, 401이면 로그인으로), `openWorkspace`(149, 다른 서버 북마크면 그 서버 `/login?name=&url=&folder=`로), `mergedWorkspaces`(161), `workspaceCard`(181), `renderHome`(243), `renderConversations`(285), `renderTranscript`(321), `resumeIn`(353), `route`(373), 모달 저장(391), `load`(405), 30초 갱신(414), 테마(417-429).
- **사용처:** `main.py:173`.
- **주의점:** 모든 서버 문자열을 `textContent`로 넣는다 (`el()`, 129). 테마 팔레트가 다른 HTML 세 곳과 복사본이다.

### `ember/proxy/static/hub_home.html` (약 386줄)
- **목적:** 허브 홈. `#/`(컴퓨터), `#/m/<mid>`(작업공간), `#/m/<mid>/w/<b64>`(대화), `#/m/<mid>/c/<agent>/<cid>`(전문).
- **주요 심볼:** `api`(118), `machineCard`(126), `renderMachines`(161), `workspaceCard`(176), `renderWorkspaces`(210), `renderConversations`(259), `renderTranscript`(292), `jump`(325), `route`(340), `loadTree`(359), 20초 갱신(369).
- **사용처:** `dpx/hub/server.py:361`.
- **주의점:** `home.html`과 구조가 거의 같은 복사본이다. 빈 목록 안내가 `python connector.py`라고 적는다 (167, 실제는 `python -m dpx.hub.connector`).

### `ember/proxy/static/workspace_login.html` (약 96줄)
- **목적:** 프록시 로그인 화면 (`GET /login`).
- **주요 심볼:** `qp(k)`(58), 쿼리 `name`/`url`/`folder`(59), 서버 URL 입력칸(51, 60), 제출(66-87, `srv + '/auth/login'`으로 POST, 성공 시 `location.href = nx || ...` 83), 테마(88-95).
- **사용처:** `main.py:170`.
- **주의점 (보안):** `?url=`이 입력칸 기본값이 되고 비밀번호를 그 주소로 보낸다 (60, 70, 75). `?next=` 값을 검사 없이 `location.href`에 넣는다 (80-83). 노트 A 표 참고. 81-82의 주석("서버가 UA를 보고 판단")은 현재 코드(`main.py:154`, 항상 래퍼)와 맞지 않는다.

### `ember/proxy/companion/extension.js` (약 1,052줄)
- **목적:** VS Code 웹 확장 `ember-terminals`. 통합 터미널과 디버기를 ember node 세션으로 돌려 창을 닫아도 살아 있게 한다 (SPEC §P, `FR-P5`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `bytesToBase64`, `base64ToBytes`, `Emitter`, `wsUrl` | 함수/클래스 | 31-75 | |
  | `TermApi` | 클래스 | 77 | `/__terms` 클라이언트. `credentials:'include'` (85) |
  | `RECONNECT_MS`, `MAX_QUEUED_INPUT`, `NOTICE_EVERY_MS` | 상수 | 137-139 | 재연결 간격, 입력 대기열 1MiB, 거부 알림 3초 |
  | `EmberPty` | 클래스 | 145 | `vscode.Pseudoterminal` 구현. `open`(185), `handleInput`(206), `close`(216, detach만), `connect`(243), `handleEvent`(292) |
  | `refusalText` | 함수 | 389 | |
  | `planAutoAttach` | 함수 | 407 | 이 창에 자동으로 띄울 세션 |
  | `deviceLabel`, `randomId` | 함수 | 427, 446 | |
  | `DEBUG_TAG`, `NODE_TYPES`, `PY_TYPES`, `READY_TIMEOUT_MS` | 상수 | 467-476 | |
  | `shQuote`, `loginShellArgv` | 함수 | 479, 488 | `/bin/sh -c 'exec "${SHELL:-/bin/sh}" -l -i -c "$1"'` |
  | `DEBUGPY_BOOT` | 상수 | 511 | debugpy 부트스트랩 Python 코드 |
  | `planDebugLaunch` | 함수 | 532 | launch 구성을 node 세션 + attach 구성으로 바꿈 |
  | `parseDebugEndpoint`, `attachFor`, `reattachConfig`, `planReattach`, `launchDebuggee` | 함수 | 602-686 | |
  | `activate(context)` | 함수 | 695-1023 | 명령 7개, 터미널 프로필, 디버그 구성 제공자, 5초 폴링 |
  | `deactivate` | 함수 | 1025 | `deactivating=true` |
- **사용처:** VS Code 웹 확장 호스트 (`companion/package.json:14`). 이 확장을 어떻게 설치하는지는 이 모듈 코드에 없다 [확인 필요: `DEFAULT_EXTENSIONS`(`runtime.py:51`)에 `ember-terminals`가 없다].
- **주의점:** 디버기는 `127.0.0.1`의 OS 할당 포트에서 디버거를 연다 (550, 516). `activate`가 330줄짜리 함수다.

### `ember/proxy/docs/BACKGROUND.md` (약 689줄), `docs/CONSTRAINTS.md` (약 271줄), `docs/HUB.md` (약 125줄)
- **목적:** 설계 배경과 시도/폐기 기록(BACKGROUND), 코드를 건드리기 전에 읽을 함정(CONSTRAINTS), 허브 사용법(HUB).
- **주의점:** BACKGROUND §7-3(502-516)이 보안 구멍 목록을 이미 적는다 (CORS 반사 측정 결과 포함). 일부 내용은 코드와 어긋난다: `xmoLiftTopCovered`(`CONSTRAINTS.md:43`)는 `overlay.js`에 없고, 홈 카드가 `xmo_chats_*`를 읽는다는 서술(`BACKGROUND.md:326`)은 `home.html`에 없다, "No folder restriction"(`BACKGROUND.md:512`)은 `DPX_FOLDER_ROOTS`가 생긴 뒤에도 그대로다.

### 작은 파일

| 파일 | 줄 | 내용 |
|---|---|---|
| `ember/proxy/.gitattributes` | 3 | `* text=auto eol=lf` |
| `ember/proxy/.gitignore` | 21 | `darkpyonix.db`, `_xmo_recent.json`, `_dpx_*.json`, `*.pem`, `*.key` 등 |
| `ember/proxy/AGENTS.md` | 96 | 홈 화면 흐름과 에이전트 어댑터 추가 방법 (`_CANDIDATES`에 한 줄) |
| `ember/proxy/README.md` | 405 | 실행법, 환경 변수, 엔드포인트, 파일 지도, 탭 분리 |
| `ember/proxy/requirements.txt` | 11 | `fastapi==0.115.0`, `uvicorn[standard]==0.30.6`, `httpx==0.27.2`, `websockets==12.0` (고정 이유 7-10) |
| `ember/proxy/dpx/__init__.py` | 18 | 패키지 지도 docstring |
| `ember/proxy/dpx/auth/__init__.py` | 11 | `from .gate import is_public_path` 재수출 (11). 쓰는 곳 없음 (`main.py:43`은 `dpx.auth.gate`에서 직접 import) |
| `ember/proxy/dpx/home/__init__.py` | 9 | docstring |
| `ember/proxy/dpx/hub/__init__.py` | 9 | docstring |
| `ember/proxy/dpx/terms/__init__.py` | 14 | docstring |
| `ember/proxy/dpx/vscode/__init__.py` | 14 | docstring |
| `ember/proxy/dpx/agents/__init__.py` | 101 | 어댑터 레지스트리. `_CANDIDATES`(10), `all_adapters`(26, 지연 싱글톤 `_ADAPTERS`), `active_adapters`(40), `get_adapter`(45), `workspaces`(52), `conversations`(71), `transcript`(84), `resume`(94). 어댑터 예외는 모두 삼킨다 |
| `ember/proxy/companion/package.json` | 135 | `ember-terminals` 0.1.0, `browser: ./extension.js`, 명령 7개, 설정 9개 (`ember.terminals.*`, `ember.debug.*`), `untrustedWorkspaces.supported=false` |
| `ember/proxy/companion/test/extension.test.js` | 255 | 테스트: 9개. `TermApi`, `EmberPty`(생성, 재연결, 종료, 제어), `planAutoAttach`, `deviceLabel` |
| `ember/proxy/companion/test/debug.test.js` | 226 | 테스트: 10개. 셸 인용, `planDebugLaunch`(node/debugpy), 엔드포인트 파싱, attach/re-attach, `launchDebuggee` |
| `ember/proxy/static/README.md` | 46 | 각 정적 파일이 언제 서빙되는지 |
| `ember/proxy/static/login.html` | 55 | 허브 로그인. `fetch('/auth/login')` 후 `location.href='/'` (45-49) |
| `ember/proxy/static/upstream_down.html` | 16 | 업스트림 다운 안내 (502). 안내 명령에 `--accept-server-license-terms`가 없다 (16) |
| `ember/proxy/static/overlay.css` | 120 | `data-xmo-embed/chrome/orient` 속성 기반 규칙. 액티비티 바를 `opacity:0`으로 숨기되 DOM은 유지 (5) |
| `ember/proxy/static/webview-kb.js` | 84 | 웹뷰 호스트 프레임용 작은 키보드 정책. 부모의 `data-xmo-chrome`을 읽고(9-22), 하위 iframe을 700ms마다 훑어 설치 (72-83) |

## 이 모듈을 수정할 때 주의할 점

- **두 프로세스.** 화면과 주입은 모두 프록시에 있다. serve-web 포트에 직접 붙으면 순정 VS Code만 보인다 (`ember/proxy/README.md:13-25`). 업스트림 포트가 9092가 아니면 `XMO_UPSTREAM_PORT`를 맞춰야 한다 (`dpx/config.py:16`).
- **websockets 고정.** `extra_headers` 인자가 두 곳에 있다 (`dpx/vscode/proxy.py:116`, `dpx/terms/api.py:173`). websockets를 올리면 둘 다 `additional_headers`로 바꿔야 한다 (`requirements.txt:7-10`).
- **라우트 등록 순서.** catch-all(`main.py:258`, `:264`)보다 먼저 등록된 것만 살아남는다. 새 라우트는 `main.py:82-86` 근처나 그 위에 둔다.
- **공개 경로는 접두사 비교다.** `dpx/auth/gate.py:14`에 접두사를 추가하면 그 접두사로 시작하는 모든 경로가 업스트림까지 세션 없이 열린다.
- **주입은 최상위 문서에만.** `overlay.js`를 VS Code 내부 HTML에 넣으면 안드로이드가 멈춘다 (`dpx/vscode/inject.py:12-15`, `static/README.md:41-46`).
- **같은 값이 여러 곳에 있다.**
  - 폴더 키 정규화(`\`→`/`, 끝 `/` 제거, 소문자): `dpx/home/workspaces.py:36`, `dpx/agents/base.py:86`, `dpx/hub/server.py:239,242,266`, `static/home.html` `key()`(118).
  - 테마 팔레트와 `xmo_theme` 키: `static/home.html`, `static/hub_home.html`, `static/workspace_login.html:8-12`, `static/login.html:7-10`.
  - `detach.js`의 `KINDS`/`HANDLER_NAME`과 URL 형식은 `ember/bridge/src/messages.rs`, `ember/bridge/src/url.rs`와 짝이다 (`detach.js:51-53`, `:291-294`). 바꾸면 `ember/vectors/bridge/detach_vectors.json`도 바꾼다.
  - 터미널 attach 프로토콜(`hello`, `attached`, `snapshot`, `output`, `refused`, `exit`)은 ember node와 짝이다 (`companion/extension.js:247-256`, `:292-372`, 설계 `docs/design/TERMINALS.md`).
  - 활동 바 숨김 폭 48px가 `overlay.css:17`, `detach.js:58`(별개 의미의 임계값), `frame.html`의 `--xf-gutter` 기본값에 흩어져 있다 [확인 필요: frame.html CSS 기본값 줄].
- **VS Code DOM 의존.** `overlay.js`, `frame.html`, `webview-kb.js`, `detach.js`는 VS Code의 클래스 이름과 aria 레이블(영어/한국어)을 직접 찾는다. VS Code 버전을 올리면 실제 기기에서 다시 확인해야 한다 (README: 헤드리스 Chromium은 웹뷰를 못 그린다, `ember/proxy/README.md:224-226`).
- **런타임 파일은 커밋하지 않는다.** `darkpyonix.db`에 비밀번호 해시와 살아 있는 세션 토큰이 있다 (`ember/proxy/README.md:309-311`).
- **보안 전제.** 계정은 "출입증"이지 신원이 아니다. 로그인하면 서버를 띄운 OS 사용자의 모든 파일에 닿는다 (`dpx/auth/api.py:18-20`). `DPX_FOLDER_ROOTS`는 URL로 여는 폴더만 제한한다 (`dpx/vscode/roots.py:8-10`).
- **빌드·테스트는 이 문서 작성 중 실행하지 않았다.** 위 동작 서술은 코드 읽기만으로 확인한 것이다.
