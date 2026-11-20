# 모듈: node-term

- 경로: `ember/node/src/term/` (`mod.rs`, `pty.rs`, `screen.rs`, `session.rs`, `store.rs`), `ember/node/src/bin/ember-term.rs`
- 규모: 파일 6개 / 약 2,708줄
- 레이어: 비즈니스 로직 (영속 터미널 세션 엔진 + 로컬 attach CLI)
- 한 줄 책임: 노드 데몬이 소유하는 영속 터미널 세션(SPEC §P, FR-P1-P6)을 만들고, 여러 클라이언트가 붙고 떨어지게 하며, 화면을 터미널 모델로 유지해 재접속 시 그대로 복원한다. `ember-term`은 VS Code 터미널 같은 로컬 터미널을 그 세션에 이어 주는 바이너리다.
- 의존하는 모듈: [node](node.md) (`crate::jobs::{Jobs, Removal, now_ms}`, `crate::proto::*`, `crate::exec::{argv, SIGHUP, SIGKILL}`: `ember/node/src/term/mod.rs:29-30`, `session.rs:127` 이하). `ember-term`은 `ember_node::client::NodeClient`와 `config::LocalEndpoint`를 쓴다. 외부 크레이트는 `portable-pty`, `alacritty_terminal` (`term/pty.rs`, `term/screen.rs`).
- 이 모듈을 쓰는 모듈: [node](node.md)의 `api.rs`가 `Terms`/`Session`을 호출한다 (`ember/node/src/api.rs:42`, `:780-939`). `main.rs`는 `term::pty::KEEPER_SUBCOMMAND`/`keeper_main`을 부른다 (`ember/node/src/main.rs:44-48`). 서버는 `/terms` 라우트를 `NodeClient::term_*`으로 쓴다 ([server-computers](server-computers.md)의 `computers/terms.rs`). `ember_node::term::` 경로를 직접 import하는 파일은 `main.rs`뿐이다 (grep).

## 공개 인터페이스

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `Terms` | struct | `ember/node/src/term/mod.rs:66` | 세션 테이블. `new`(93), `create`(197), `get`(251), `list`(256), `kill`(270), `remove`(281), `shutdown`(298) |
| `Session` | struct | `ember/node/src/term/session.rs:121` | 세션 하나. `attach`(359), `input`(409), `resize`(441), `control`(454), `detach`(480), `kill`(491), `snapshot`(263) |
| `TermRecord` | struct | `ember/node/src/term/session.rs:43` | 디스크에 저장되는 세션 메타데이터 |
| `Screen` | struct | `ember/node/src/term/screen.rs:90` | 터미널 상태 모델 (`feed`, `snapshot`, `resize`, `compact`) |
| `Pty`, `spawn`, `spawn_keeper`, `keeper_main` | struct/fn | `ember/node/src/term/pty.rs:43`/`:88`, `:131`, `:229`, `:316` | PTY 생성과 keeper 프로세스 |
| `Store` | struct | `ember/node/src/term/store.rs:10` | `<state>/terms/` 디스크 저장 |
| `default_argv` | fn | `ember/node/src/term/mod.rs:74` | 기본 프로그램: 사용자 셸 (macOS는 `-l`, Windows는 `COMSPEC`) |
| `ember-term` | bin | `ember/node/src/bin/ember-term.rs:248` | 로컬 터미널을 노드 세션에 attach하는 CLI |

## 파일별 요약

### `ember/node/src/term/mod.rs` (310줄)
- 목적: `Terms` 세션 테이블, 생성, 재시작 후 재입양(re-adopt), 정리.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `MAX_FINISHED`, `MAX_FINISHED_SCREENS` | const | 41, 43 | 끝난 세션 100개까지 목록에 남기고, 화면은 20개까지만 유지 (태스크 출력 재접속, FR-P5) |
| `DEFAULT_SIZE` | const | 44 | 24x80 |
| `Shared` | struct | 47 | 저장소와 이벤트 로그 핸들. `save`(53), `emit`(61) |
| `Terms::create` | fn | 197 | `key`가 같은 실행 중 세션이 있으면 새로 만들지 않고 그것을 돌려준다(`created:false`). 아니면 `pty::spawn` -> keeper 기동 -> `Session::start` -> `TermStarted` 이벤트 |
| `Terms::readopt` | fn | 133 | 저장된 `pid`가 살아 있고 keeper 소켓에서 fd를 받으면 재입양, 아니면 `Lost`로 표시하고 keeper를 종료 |
| `Terms::prune` | fn | 175 | 오래된 끝난 세션을 잊고 화면을 버린다 |
| `Terms::shutdown` | fn | 298 | 정상 종료 시 모든 세션의 스크롤백 스냅샷을 `.snap`으로 저장 |
- 부수효과: 세션 시작/종료 시 `Jobs`의 이벤트 로그에 `TermStarted`/`TermFinished`를 낸다. keeper가 없으면 `no PTY keeper; the session will not survive a node restart` 경고 (`mod.rs:213` 주변).
- 주의점: `create`는 `sessions` 뮤텍스를 잡은 채 PTY와 keeper를 띄운다 (keeper 준비 대기 최대 20초, `pty.rs:219`). 그동안 다른 `Terms` 호출이 막힌다 [추정: 호출 경로 기준, 동시 실행 측정은 하지 않음].

### `ember/node/src/term/session.rs` (764줄)
- 목적: 세션 하나. PTY 읽기 스레드, 쓰기 스레드, 종료 대기 스레드와 `Mutex<Inner>` 하나로 구성 (머리 주석 1-14). 화면에 반영되는 모든 것(출력, attach의 스냅샷, 입력, 리사이즈)이 같은 락 아래서 일어나므로 스냅샷과 이후 라이브 스트림 사이에 겹침도 틈도 없고, 여러 클라이언트의 입력은 락을 잡은 순서대로 PTY에 간다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `CLIENT_QUEUE` | const | 33 | 클라이언트당 이벤트 큐 512. 넘으면 그 클라이언트만 끊고 `error` 이벤트를 준다 (느린 클라이언트가 프로그램을 막지 않는다) |
| `KILL_GRACE` | const | 35 | 3초. `kill`에서 신호 미지정이면 SIGHUP 후 3초 뒤 SIGKILL (491-511) |
| `TermRecord` | struct | 43 | id, key, title, origin, project, argv, cwd, tags, pid, state, exit, size, 시각, `keeper_socket`, `adopted` |
| `Child` | enum | 74 | `Ours`(waitpid로 종료 상태 확인) / `Adopted`(재입양, 종료 상태 알 수 없음) |
| `Session::start` | fn | 134 | `Screen` 생성, 복원 바이트 주입, 스레드 3개 시작 |
| `Session::inert` | fn | 221 | 화면 없는 `Lost`/끝난 세션 |
| `Session::attach` | fn | 359 | `Lost`면 에러 반환. `hello.active`이면 활성 클라이언트가 되고 `apply_size`로 PTY를 그 크기에 맞춘 뒤 스냅샷을 보낸다. 끝난 세션은 `Exit`를 바로 보낸다 |
| `Session::input` | fn | 409 | 읽기 전용 클라이언트 또는 다른 클라이언트가 제어권을 가진 경우 `Refused{ReadOnly/Controlled/NotRunning}`. 크기 소유자 아닌 클라이언트가 보낸 터미널 보고(커서 위치 응답 등)는 버린다 (`is_terminal_report`, 679) |
| `Session::control` | fn | 454 | 제어권 가져오기/놓기 (읽기 전용은 가져올 수 없다: `a read-only client cannot take control`) |
| `Inner::apply_size` | fn | 603 | 크기 소유자(제어자 또는 활성 클라이언트)의 크기에 PTY와 화면 모델을 맞추고 `Resized` 방송 |
| `Session::tick` | fn | 288 | 입력 없이 10초(`IDLE_COMPACT_MS`, 37) 지나면 `Screen::compact`로 메모리 반환 |
| `signal_session`, `wait_status` | fn | 513, 524 | 신호 전달, 종료 상태 수집 |
- 주의점: 위 락은 거대한 임계 영역이라 `Session` 메서드를 호출하는 쪽(`api.rs` `term_attach_session`)에서 오래 걸리는 일을 하면 안 된다.
- 테스트 있음 (`session.rs:744` 이하, 터미널 보고와 키 구분).

### `ember/node/src/term/pty.rs` (460줄)
- 목적: PTY 생성과, 노드가 재시작해도 세션이 살도록 PTY master를 쥐고 있는 keeper 프로세스(FR-P6, 최선 노력). 머리 주석(1-30)에 설계 이유가 있다: 마지막 master fd가 닫히면 커널이 hangup을 보내 셸이 SIGHUP을 받으므로, 노드가 master 복제본을 `ember-node __keep-pty`에 넘긴다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `spawn` | fn | 131 | `portable-pty`로 시작. `TERM=xterm-256color`, `COLORTERM=truecolor`를 기본 주입, `EMBER_TERM_ID`를 설정하고 `EMBER_NODE_TOKEN`을 환경에서 제거해 세션으로 자격 증명이 새지 않게 한다 (155-163 부근) |
| `Pty` | struct | 43 (unix), 88 (비 unix) | unix는 master fd 복제본, 그 외는 portable-pty 핸들 |
| `KEEPER_SUBCOMMAND` | const | 209 | `__keep-pty` |
| `spawn_keeper` | fn | 229 | 소켓 경로가 100바이트를 넘으면 거부 (`MAX_SOCKET_PATH`, 213), 준비 대기 20초 |
| `keeper_main` | fn | 316 | `--socket --pid --fd`. 소켓을 0600으로 만들고 2초마다 대상 pid 생존 확인, `F`를 받으면 `SCM_RIGHTS`로 fd 전달, `Q`면 종료 |
| `fetch_from_keeper`, `stop_keeper` | fn | 295, 304 | 재입양 시 fd 회수, keeper 종료 |
| `send_fd`, `recv_fd` | fn | 382, 411 | unsafe fd 전달 (cmsg) |
- 한계: 노드가 없는 동안 아무도 PTY를 읽지 않아 커널 버퍼가 차면 프로그램이 출력에서 멈춘다 (머리 주석). 비 unix(Windows)에서는 keeper가 없다 (`spawn_keeper` 289, `keeper_main` 372는 빈 구현).
- 테스트 1개 (`fds_cross_a_unix_socket`, 448).

### `ember/node/src/term/screen.rs` (628줄)
- 목적: `alacritty_terminal` 에뮬레이터로 PTY 출력을 모두 먹여, 나중에 붙는 클라이언트가 같은 화면을 보게 하는 스냅샷(`Screen::snapshot`, 205)을 만든다 (FR-P2, NFR-P1). 스크롤백은 줄 단위 SGR 텍스트로 압축 보관한다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `SCROLLBACK_LINES`, `SCROLLBACK_BYTES` | const | 39, 42 | 10,000줄, 3 MiB |
| `Screen::feed` | fn | 121 | 바이트 주입, 스크롤 아웃된 줄 수확(`harvest`, 171) |
| `Screen::snapshot` | fn | 205 | 스크롤백 + 주 화면 + (TUI면) 대체 화면 + 커서, 펜, 입력 모드, 제목을 재현하는 바이트열 |
| `Screen::resize`, `compact` | fn | 135, 162 | 크기 변경(줄을 스크롤백으로), 유휴 시 캐시 해제 |
| `take_replies`, `title`, `text`, `cursor`, `alt_screen`, `mode_bits` | fn | 148, 142, 320, 344, 349, 353 | 에뮬레이터가 만든 응답, 제목, 텍스트 덤프 등 |
- 스냅샷 한계: 스크롤 영역(DECSTBM), 원점 모드, 저장 커서, 문자셋, 탭 스톱, OSC 8 하이퍼링크, 밑줄 색은 재현하지 않는다 (머리 주석). TUI는 다음 전체 다시 그리기에서 스스로 복구한다.
- 테스트 8개 (`screen.rs:514` 이하).

### `ember/node/src/term/store.rs` (87줄)
- 목적: `<state>/terms/<id>.json`(레코드), `<id>.snap`(정상 종료 스냅샷), keeper 소켓 `<id 앞 12자>.sock` (`store.rs:1-4`, `socket_path` 36).
- `Store::open` 15가 디렉터리를 0700으로 만든다 (상위 state 디렉터리도 0700으로 바꾼다). `save`(48)는 임시 파일 후 rename으로 원자적 저장, `load_all`(54)은 읽지 못하는 파일을 경고하고 건너뜀, `take_snapshot`(81)은 읽고 지운다.

### `ember/node/src/bin/ember-term.rs` (459줄)
- 목적: VS Code 터미널 프로파일의 셸. VS Code가 자기 PTY에서 이 프로그램을 띄우면, 이 프로그램이 그 PTY를 노드의 영속 세션에 연결한다 (머리 주석 1-30). 창이 닫혀 HUP를 받으면 detach만 하고 세션은 계속된다.

| 이름 | 종류 | 줄 | 설명 |
|---|---|---|---|
| `Cmd`, `Opts`, `parse` | enum/struct/fn | 55, 40, 79 | 하위 명령: (없음) 새 셸, `-c <command>`, `attach <id> [--passive]`, `attach-or-create --key <k> [-- argv]`, `list [--project] [--all] [--json]`, `kill <id> [--signal n]` |
| `run` | fn | 262 | `LocalEndpoint::discover()`로 노드를 찾고, `--node`가 있으면 URL만 덮어쓴다 (토큰은 그대로) |
| `create` | fn | 295 | 현재 환경 전체를 `env`로 넘기고 `env_clear: true`로 요청. `EMBER_NODE_TOKEN`, `EMBER_NODE_URL`, `EMBER_TERM_ID`는 제외. 태그 `ember-term.pid`, `ember-term.mode`, `vscode.window`. 프로젝트 기본값은 `EMBER_PROJECT` 또는 cwd |
| `attach` | fn | 358 | `TermHello{active: !passive, snapshot: true}`, raw 모드(`RawMode`, 192), 출력/스냅샷을 stdout에 쓰고 stdin을 입력으로 보낸다. 유닉스는 SIGWINCH로 리사이즈, SIGHUP이면 129, SIGTERM이면 143으로 나가고 detach (비 unix 분기는 Ctrl-C로 130) |
| `status_code` | fn | 238 | 종료 코드 (신호면 128+신호, 모르면 0) |
| `usage` | fn | 64 | 사용법 출력 후 exit 2 |
- 부수효과: stdout에 터미널 제어 바이트 출력. 제어권 거절 시 `\x07` 벨과 창 제목(OSC 0)으로 알림.
- 주의점: `attach`의 `select!` 본문이 unix/비 unix 두 벌로 복제되어 있다 (아래 이슈).

## 동작 지도

HTTP 라우트(`/terms*`)의 핸들러는 [node](node.md)의 동작 지도에 있다 (`api.rs:780-939`). 이 모듈은 그 뒤의 서비스 함수다.

| 라우트/동작 | 핸들러 `경로:줄` | 서비스 함수 `경로:줄` | 데이터 |
|---|---|---|---|
| `POST /terms` | `ember/node/src/api.rs:780` | `Terms::create` `term/mod.rs:197` -> `pty::spawn` `pty.rs:131`, `spawn_keeper` `pty.rs:229`, `Session::start` `session.rs:134` | `<state>/terms/<id>.json`, keeper 소켓 |
| `GET /terms`, `GET /terms/{id}` | `api.rs:812`, `:816` | `Terms::list` `mod.rs:256`, `get` `mod.rs:251` | 메모리 |
| `GET /terms/{id}/snapshot` | `api.rs:820` | `Session::snapshot` `session.rs:263` | `Screen` |
| `GET /terms/{id}/attach` (WS) | `api.rs:863` | `Session::attach/input/resize/control/detach` `session.rs:359-490` | 클라이언트 큐 |
| `POST /terms/{id}/control` | `api.rs:827` | `Session::control` `session.rs:454` | 제어권 |
| `POST /terms/{id}/kill` | `api.rs:838` | `Terms::kill` `mod.rs:270` -> `Session::kill` `session.rs:491` | 신호 |
| `DELETE /terms/{id}` | `api.rs:851` | `Terms::remove` `mod.rs:281` | 레코드 삭제 |
| 노드 종료 | `main.rs` `serve` | `Terms::shutdown` `mod.rs:298` | `<id>.snap` |
| 노드 시작 | `Terms::new` `mod.rs:93` | `load` 120, `readopt` 133 | 레코드, keeper 소켓 |

### 사용자에게 보이는 에러 메시지

| 원문 | 위치 | 조건 |
|---|---|---|
| `terminal session <id> was lost when ember node restarted` | `session.rs:361` | `Lost` 세션에 attach |
| `the session is not running` | `session.rs:457` | 끝난 세션의 제어권 변경 |
| `client <n> is not attached` | `session.rs:460` | 붙지 않은 클라이언트가 제어 |
| `a read-only client cannot take control` | `session.rs:465` | 읽기 전용이 제어권 요청 |
| `read-only: controlled by <device>`, `read-only`, `session ended` | `bin/ember-term.rs` `attach`의 `Refused` 처리 | 입력 거절 알림 (창 제목) |
| `ember node closed the connection` | `bin/ember-term.rs` `attach` | WS가 닫힘 |
| `ember-term: <e>` | `bin/ember-term.rs:252` | 실행 실패, 종료 코드 1 |
| `usage: ember-term [-c <command>] | attach <id> ...` | `bin/ember-term.rs:64-67` | 인자 오류, 종료 코드 2 |
| `usage: ember-node __keep-pty --socket <path> --pid <pid> --fd <fd>` | `pty.rs` `keeper_main` | keeper 인자 오류 |
| `socket path too long: <path>` | `pty.rs` `spawn_keeper` | 소켓 경로 100바이트 초과 |

## 데이터와 설정

- 저장 파일 (`<state dir>/terms/`, 0700): `<id>.json`(`TermRecord`), `<id>.snap`(정상 종료 때만, 재입양 후 읽고 지움), `<id 앞 12자>.sock`(keeper, 0600). DB 없음.
- 환경 변수: `EMBER_NODE_KEEP_PTY=0`이면 keeper 없음 (`ember/node/src/config.rs:77`, [node](node.md)). `ember-term`은 `EMBER_NODE_URL`, `EMBER_NODE_TOKEN`(또는 `local.json`), `EMBER_PROJECT`, `EMBER_VSCODE_WINDOW`, `SHELL`을 읽는다 (`bin/ember-term.rs:137`, `:295-333`). 세션 프로세스에는 `EMBER_TERM_ID`가 설정된다 (`pty.rs` `spawn`).
- 상수: 스크롤백 10,000줄 / 3 MiB, 클라이언트 큐 512, 끝난 세션 100개 / 화면 20개, kill 유예 3초, 유휴 압축 10초.
- 외부 연동: OS PTY, unix 소켓 + `SCM_RIGHTS`, 노드 HTTP/WS API (`ember-term`).

## 이 모듈을 수정할 때 주의할 점

- `TermRecord` 필드를 바꾸면 이미 디스크에 있는 `<id>.json`과 호환되어야 한다 (필드에 `#[serde(default)]`가 붙은 것은 이 때문). 필드를 추가할 때는 `default`를 준다.
- `Session`의 단일 락 불변식(스냅샷과 라이브 스트림 사이에 틈이 없다)을 깨지 않는다. 락 밖에서 `screen`을 건드리거나 락을 잡은 채 블로킹 I/O를 하지 않는다.
- `proto.rs`의 `TermInput`/`TermEvent`/`TermHello`를 바꾸면 `ember-term`, `api.rs`의 attach 루프, 서버의 `computers/terms.rs`, 에디터 쪽 소비자를 함께 고친다.
- keeper 프로토콜(`F`, `Q`, `--socket --pid --fd`)을 바꾸면 이전 버전 keeper가 남은 채 노드를 재시작하는 경우 재입양이 깨진다. 노드와 keeper는 같은 바이너리(`std::env::current_exe`, `config.rs:78`)다.
- `main.rs`가 `__keep-pty`를 런타임과 로깅 없이 먼저 처리한다 (`main.rs:44-48`). 이 분기를 늦추면 keeper가 무거워진다.
- Windows는 keeper와 재입양이 없고 `Pty`가 다른 타입이다. unix 전용 코드를 건드리면 비 unix 빌드도 확인한다.

## 이슈 후보

TODO/FIXME는 이 모듈 파일에서 0개 (grep 확인).

| 분류 | 심각도 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 낮음 | `ember/node/src/bin/ember-term.rs:262-266` | `--node <url>`을 주면 URL만 바꾸고 `local.json`의 토큰을 그 URL로 보낸다. 잘못된 URL에 노드 토큰이 전송될 수 있다 | `--node` 사용 시 `EMBER_NODE_TOKEN` 명시를 요구하거나 경고 |
| 보안 | 낮음 | `ember/node/src/bin/ember-term.rs:301-305` | 호출 환경 전체를 세션에 넘긴다 (토큰/URL/ID만 제외). 다른 비밀 환경 변수는 그대로 전달된다. 의도된 동작(task 환경 반영)이다 | 문서화 |
| 보안 | 낮음 | `ember/node/src/term/pty.rs:316-372` | keeper 소켓은 0600이지만 같은 사용자의 어떤 프로세스든 `F`를 보내 PTY master를 받을 수 있다 | 같은 사용자 신뢰 모델이므로 수용 가능, 문서화 |
| 중복 | 중간 | `ember/node/src/bin/ember-term.rs:358-459` | `attach`의 이벤트 루프가 `#[cfg(unix)]`와 `#[cfg(not(unix))]`로 거의 똑같이 두 벌 (Refused 처리 등) | 공통 핸들러 함수로 추출 |
| 동시성 | 중간 | `ember/node/src/term/mod.rs:197-250` | `create`가 `sessions` 락을 잡은 채 PTY와 keeper 기동(최대 20초 대기)을 한다 | 락 밖에서 spawn 후 삽입 시 키 중복만 재확인 |
| 구조 | 낮음 | `ember/node/src/term/session.rs` (764줄) | 파일이 크고 `Inner`와 `Session`, 크기/제어 정책, 터미널 보고 판별이 한 곳에 있다 | 정책 부분 분리 고려 |
| 이식성 | 낮음 | `ember/node/src/term/pty.rs:289`, `:372` | 비 unix에서 keeper가 빈 구현이라 Windows 노드는 재시작 시 세션을 잃는다 | 한계로 문서화 [확인 필요: Windows 지원 범위] |
| 정확성 | 낮음 | `ember/node/src/term/mod.rs:133-170` | 재입양된 세션의 종료 상태는 알 수 없어 `ember-term`은 0을 돌려준다 (`bin/ember-term.rs:238-245`) | 의도된 동작 (코드 주석에 명시) |
