# Ember 코드 안내서

에이전트가 만든 약 24만 줄을 사람이 처음부터 차례로 읽을 수 있게 정리한 문서다. 코드를 다 읽지 않고도
"어느 폴더가 무엇을 하고, 사용자의 행동 하나가 어느 코드를 지나가는지"를 알게 하는 것이 목적이다.
내용은 `vibemap/data/map.json`(commit 876186d7)에서 왔고, 적힌 위치는 모두 `verify.py`로 실제 코드와
대조했다.

읽는 순서: 1장(전체 그림) → 2장(폴더 투어) → 3장(동작 따라가기). 4~5장은 코드 상태 평가다.

---

## 1. 전체 그림

### 무엇을 하는 프로그램인가

Claude Code, Codex 같은 코딩 에이전트를 **메인 서버 한 대에서** 돌리고, 에이전트가 쓰는 도구(파일 읽기,
명령 실행, 빌드)는 **사용자의 여러 컴퓨터 중 하나에서** 실행하게 하는 개발 환경이다. 대화는 메인 서버에
남으므로 어느 컴퓨터에서 앱을 열어도 같은 대화가 이어진다.

### 프로그램 세 개

| 프로그램 | 폴더 | 어디서 도나 | 하는 일 |
|---|---|---|---|
| `ember-server` | `ember/server` | 메인 서버 (Mac mini 등) | 에이전트 CLI 실행, 대화 저장, 앱에 실시간 알림 |
| `ember-node` | `ember/node` | 작업할 각 컴퓨터 | 서버 대신 파일·명령·터미널을 실제로 실행 |
| `ember-app` | `ember/app` | 사용자 앞 | 프로젝트·세션·대화를 보여 주는 네이티브 앱 |

여기에 별도 Python 서버 `ember/proxy`(브라우저용 VS Code를 감싸는 웹 IDE)가 따로 있다.

### 어떻게 이어지나

```
 [사용자]
    │
 ember-app ──(HTTP 8740 + 실시간 push)──▶ ember-server ──(HTTP 8741 또는 P2P)──▶ ember-node
 (ember/app)                             (ember/server)                       (ember/node)
    │ 내부 라이브러리                        │ 내부 라이브러리                       │
    ├ ember/client  서버 연결·상태            ├ ember/transport  P2P 연결            ├ ember/transport
    ├ ember/editor  편집기 세션               ├ ember/transfer   파일 전송            └ ember/hub
    └ ember/editor-conn  Code-OSS 연결        └ ember/hub        기기 등록
                                                 │
                                                 └─ 에이전트 CLI (claude, codex, agy ...) 를 자식 프로세스로 실행
```

크레이트끼리는 Cargo의 path 의존으로 묶인다: app → client, editor, editor-conn / server → node, transport,
hub, transfer / node → transport, hub / hub·transfer → transport. 그래서 `ember/node`나
`ember/transport`를 바꾸면 위쪽 크레이트도 다시 빌드해야 한다.

### 규모 (빈 줄 제외, 테스트 포함)

| 폴더 | 줄 수 | 그중 테스트 | 메모 |
|---|---:|---:|---|
| `ember/app` | 82,660 | 1,962 | 화면 코드가 대부분 (`ui/` 6.9만 줄) |
| `ember/server` | 76,389 | 27,007 | 테스트 비중이 가장 높음 |
| `ember/node` | 19,414 | 5,099 | |
| `ember/editor` | 14,474 | 4,662 | |
| `ember/proxy` | 8,464 | 1,429 | Python |
| `ember/client` | 7,191 | 933 | |
| `ember/transport` | 6,443 | 1,503 | |
| `ember/editor-conn` | 5,837 | 638 | |
| `extensions/` | 8,008 | 1,967 | VS Code(TS), IntelliJ(Kotlin) |
| `ember/hub`, `transfer`, `bridge`, `ose` | 6,980 | 998 | |

앱과 서버 두 폴더가 전체의 약 3분의 2다. 처음에는 이 둘과 `ember/node`만 알면 된다.

---

## 2. 폴더 투어

폴더마다 "무엇을 하나 / 먼저 열어 볼 파일 / 누구와 대화하나"를 적는다. 링크는 이 문서 기준 상대 경로다.

### 2.1 `ember/server`: 메인 서버 (가장 중요)

에이전트를 실제로 돌리는 곳이다. 안쪽이 커서 네 덩어리로 나눠 본다.

**뼈대와 API** (`src/` 바로 아래, `api/`, `door/`)
- 서버 시작, HTTP API, 저장소, 세션 관리.
- 먼저 열 파일:
  - [main.rs:79](../ember/server/src/main.rs#L79) `main`: 환경 변수를 읽고 모든 부품을 조립한다.
  - [api/mod.rs:78](../ember/server/src/api/mod.rs#L78) `router`: 앱이 부르는 API 경로 목록. 여기서 기능 전체가 한눈에 보인다.
  - [session.rs:225](../ember/server/src/session.rs#L225) `Sessions`: 세션 만들기, 메시지 보내기, 승인, 중단.
  - [store.rs:81](../ember/server/src/store.rs#L81) `Store`: SQLite(`~/.ember/ember.db`)에 세션과 이벤트를 저장한다.
  - [events.rs:12](../ember/server/src/events.rs#L12) `AgentEvent`: 대화에 쌓이는 이벤트 종류(메시지, 도구 사용, 승인 요청 등).
- 보안 입구: [auth.rs:176](../ember/server/src/auth.rs#L176) `protect`가 모든 API를 서버 토큰으로 막는다.

**에이전트와 계정** (`agents/`, `accounts/`, `history/`, `chatgpt/`, `mcp/`)
- 에이전트 CLI마다 "어댑터"가 하나씩 있다. 어댑터는 CLI를 실행하고, CLI 출력 형식을 `AgentEvent`로 바꾼다.
- [agents/mod.rs:320](../ember/server/src/agents/mod.rs#L320) `AgentAdapter`: 모든 어댑터가 지키는 인터페이스.
  `claude_code.rs`, `codex.rs`, `antigravity.rs`, `acp.rs`(ACP 프로토콜 에이전트)가 구현체다.
- [accounts/mod.rs:508](../ember/server/src/accounts/mod.rs#L508) `route`: 새 세션에 쓸 계정 고르기. 한도에 걸린 계정은 건너뛴다.

**에이전트 사이 통신** (`a2a/`, `channels/`, `schedules/`)
- A2A: 세션이 다른 세션에 메시지를 보낸다. 에이전트는 `ember-a2a` CLI를 실행해서 보낸다.
- 채널: 프로젝트별 대화방. 에이전트와 사람(손님 포함)이 함께 글을 쓴다.
- 루틴: 정해진 시각에 세션에 메시지를 넣는 예약 실행.
- [a2a/mod.rs:800](../ember/server/src/a2a/mod.rs#L800) `send`, [schedules/mod.rs:670](../ember/server/src/schedules/mod.rs#L670) `tick`.

**컴퓨터와 프로젝트** (`computers/`, `projects/`, `browser/`)
- 서버에 붙은 컴퓨터(노드) 목록, 상태 확인, 등록, 세션을 다른 컴퓨터로 옮기기.
- [computers/mod.rs:1081](../ember/server/src/computers/mod.rs#L1081) `switch`: 세션의 컴퓨터 바꾸기.
- [computers/enrol.rs:911](../ember/server/src/computers/enrol.rs#L911) `mint`: 새 컴퓨터 등록 코드 발급.
- `browser/`: 다른 컴퓨터의 IP로 나가는 Chrome을 서버에서 띄운다.

누구와 대화하나: 앱(HTTP), 노드(HTTP 또는 P2P), 에이전트 CLI(자식 프로세스의 stdin/stdout), 허브.

### 2.2 `ember/node`: 각 컴퓨터의 실행 데몬

서버의 손발이다. 에이전트 CLI는 서버에서 돌지만, 에이전트가 "이 파일 읽어", "빌드 돌려"라고 하면 그
일은 세션이 연결된 컴퓨터의 노드가 한다. 노드는 에이전트를 실행하지도, 대화를 저장하지도 않는다.

- [main.rs:44](../ember/node/src/main.rs#L44) `main`: 필수 환경 변수 `EMBER_NODE_TOKEN`, 허용 경로 `EMBER_NODE_ROOTS`.
- [api.rs:147](../ember/node/src/api.rs#L147) `serve`: `/fs/*`(파일), `/exec`(명령), `/terms`(터미널) API.
- [policy.rs:31](../ember/node/src/policy.rs#L31) `PathPolicy`: 허용된 경로 밖은 막는다.
- `term/`: 앱을 닫아도 살아 있는 터미널 세션.
- 서버가 노드를 부를 때 쓰는 클라이언트도 여기 있다([client.rs](../ember/node/src/client.rs)). 그래서 서버가 이 크레이트에 의존한다.

### 2.3 `ember/app`: 네이티브 앱

사용자가 보는 화면이다. 웹뷰 없이 `dioxus-compose`로 직접 그린다(CI가 검사한다).

- [lib.rs](../ember/app/src/lib.rs) `launch`: 시작점. [ui/mod.rs:54](../ember/app/src/ui/mod.rs#L54) `Route`가 화면 목록이다.
- [services.rs:28](../ember/app/src/services.rs#L28) `Services`: 화면이 서버에 접근하는 단 하나의 입구.
- [model.rs](../ember/app/src/model.rs): 화면에 보일 문구·상태 계산 (테스트가 있는 순수 함수).
- [demo.rs](../ember/app/src/demo.rs): 서버 없이 화면을 보여 주는 데모 데이터 (`EMBER_DEMO_DATA=1`).

꼭 알아야 할 점: **화면이 두 벌이다.** `ui/`는 dioxus-compose 화면, `ui/cr/`는 새 UI 라이브러리
(compose-rust)로 옮기는 중인 화면이다. 두 UI가 다른 창에서 동시에 돌며 상태만 공유한다
([ui/coexist.rs](../ember/app/src/ui/coexist.rs)). 이전이 끝나면 `ui/` 쪽 원본을 지울 예정이다(#226).
그래서 `vcs.rs`와 `cr/vcs.rs`처럼 같은 이름의 큰 파일이 짝으로 있다.

### 2.4 `ember/client`: 앱 아래의 연결 계층

앱의 화면 코드와 서버 사이에서 연결, 실시간 수신, 상태를 맡는다. 화면이 없는 라이브러리다.

- [client.rs:96](../ember/client/src/client.rs#L96) `Client`: 연결 본체. [api.rs](../ember/client/src/api.rs)가 서버 API 호출을 모아 둔다.
- [push.rs:74](../ember/client/src/push.rs#L74) `decode`: 서버가 밀어 주는 이벤트 해석.
- [transcript.rs:83](../ember/client/src/transcript.rs#L83) `Transcript`: 대화 기록 상태.
- [wire.rs](../ember/client/src/wire.rs): 서버의 이벤트 타입을 **손으로 복사**해 둔 파일. 서버 쪽 `events.rs`를 바꾸면 여기도 맞춰야 한다.

### 2.5 `ember/editor`, `ember/editor-conn`: 앱 안의 코드 편집기

앱 안에 VS Code 수준의 편집 기능을 넣기 위한 계층이다. 원격 컴퓨터의 Code-OSS 서버(VS Code의 오픈소스
서버, 이 프로젝트에서는 OSE라고 부른다)에 Rust로 직접 접속해, 그 서버의 확장 기능(언어 서버 등)을 쓴다.

- `editor-conn`: Code-OSS 서버와의 소켓 연결과 RPC ([connection.rs:60](../ember/editor-conn/src/connection.rs#L60)).
- `editor`: 편집 세션 ([session.rs:117](../ember/editor/src/session.rs#L117) `EditorSession`). 연결에 실패하면 브라우저용 VS Code로 대신 연다([fallback.rs](../ember/editor/src/fallback.rs)).

### 2.6 `ember/transport`, `ember/transfer`, `ember/hub`: 기기 사이 연결

- `transport`: 컴퓨터끼리 직접(P2P) 연결하는 공통 입구 [lib.rs:324](../ember/transport/src/lib.rs#L324) `Transport`. iroh와 letify 두 방식을 같은 인터페이스로 감싼다.
- `transfer`: 내 기기 사이 파일 보내기 (제안, 수락, 취소).
- `hub`: darkpyonix.dev 허브에 이 기기를 등록하고, 내 기기 목록과 주소를 받아 온다. 허브 서버 자체는 이 저장소 밖에 있다.

### 2.7 나머지

| 폴더 | 하는 일 |
|---|---|
| `ember/proxy` | 브라우저용 VS Code 앞에 서는 Python(FastAPI) 서버. 로그인, 터미널, 여러 컴퓨터 목록을 붙인다. 시작점 [main.py](../ember/proxy/main.py) |
| `ember/bridge` | IDE 창(웹뷰)과 네이티브 코드 사이 메시지 형식 (탭 떼어 내기 등). 750줄로 작다 |
| `ember/ose` | Code-OSS를 빌드해 OSE 패키지로 만드는 스크립트. CI 전용(수십 분, 8GB) |
| `ember/vectors` | 여러 구현이 같은 결과를 내는지 확인하는 공유 테스트 데이터 |
| `extensions/` | VS Code·IntelliJ 확장. darkpyonix-core의 노트북 관리자와 연결한다 (Ember 본체와 별개) |
| `docs/` | `SPEC.md`(요구사항 ID), `INTENT.md`(결정과 이유), `ARCHITECTURE.md`, 사용자 안내서 `guide/` |
| `.github/` | CI. webview 금지, em-dash 금지 같은 저장소 규칙을 스크립트로 검사 |

---

## 3. 동작 따라가기

사용자 행동 하나가 어느 폴더의 어느 함수를 지나가는지 따라간다. import만 봐서는 안 보이는 연결(HTTP,
CLI 호출)이 여기서 드러난다.

### 3.1 대화에 메시지를 보내면

1. 앱에서 입력하고 보내기를 누르면 [services.rs:116](../ember/app/src/services.rs#L116)이 클라이언트에 넘긴다.
2. 클라이언트가 `POST /api/sessions/{id}/messages`를 보낸다 ([client/api.rs:929](../ember/client/src/api.rs#L929)).
3. 서버의 [session.rs:807](../ember/server/src/session.rs#L807) `send`가 받는다. 에이전트 프로세스가 없으면 이때 띄운다.
4. 어댑터가 에이전트 CLI의 stdin에 글을 쓴다 ([claude_code.rs:706](../ember/server/src/agents/claude_code.rs#L706)).
5. CLI가 내놓는 출력을 어댑터가 `AgentEvent`로 바꿔 DB에 저장하고, `/api/push`로 모든 앱에 밀어 준다 ([api/mod.rs:676](../ember/server/src/api/mod.rs#L676)).
6. 앱의 클라이언트가 받아 대화 기록에 붙인다 ([transcript.rs:126](../ember/client/src/transcript.rs#L126)).

요점: 앱은 서버에 "보냈다"고만 하고, 화면 갱신은 push로 따로 온다. 화면이 안 바뀌면 3~5보다 6(수신)을 먼저 의심한다.

### 3.2 에이전트가 명령을 실행하면 (다른 컴퓨터에서)

1. 에이전트 CLI는 서버에서 돌지만, Claude Code의 Bash 도구가 부르는 셸은 `ember-exec`라는 대리 실행 파일로 바뀌어 있다 ([bin/ember-exec.rs:18](../ember/server/src/bin/ember-exec.rs#L18)).
2. `ember-exec`가 세션의 현재 컴퓨터를 찾아 명령을 보낸다 ([computers/shim.rs:283](../ember/server/src/computers/shim.rs#L283) `run_remote`).
3. 그 컴퓨터의 노드가 `/exec` 웹소켓으로 받는다 ([node/api.rs:213](../ember/node/src/api.rs#L213)).
4. 노드가 실제 프로세스를 실행하고 출력을 돌려보낸다 ([exec.rs:141](../ember/node/src/exec.rs#L141)).

요점: "에이전트는 서버, 손은 노드"라는 이 프로젝트의 핵심 구조가 여기다.

### 3.3 새 컴퓨터를 등록하면

1. 앱에서 컴퓨터 추가를 누르면 서버가 등록 코드를 만든다 ([enrol.rs:911](../ember/server/src/computers/enrol.rs#L911) `mint`).
2. 새 컴퓨터에서 `ember-node enrol <코드> --server <주소>`를 실행한다 ([node/main.rs:59](../ember/node/src/main.rs#L59)).
3. 서버의 등록용 별도 입구가 받는다 ([enrol_door.rs:176](../ember/server/src/enrol_door.rs#L176)).
4. 코드를 확인하고 컴퓨터 목록에 추가한다 ([enrol.rs:944](../ember/server/src/computers/enrol.rs#L944) `redeem`). 실패 이유는 보안상 모두 같은 응답으로 숨기므로, 원인은 서버 로그에서 본다.

### 3.4 에이전트가 다른 세션에 말을 걸면 (A2A)

1. 에이전트가 `ember-a2a` CLI를 실행한다 ([bin/ember-a2a.rs:3](../ember/server/src/bin/ember-a2a.rs#L3)).
2. CLI가 서버에 HTTP로 보낸다 ([a2a/client.rs:195](../ember/server/src/a2a/client.rs#L195)).
3. 서버가 권한과 속도 제한을 확인하고 큐에 넣는다 ([a2a/mod.rs:800](../ember/server/src/a2a/mod.rs#L800)).
4. 받는 세션이 한가해지면 꺼내 보낸다 ([a2a/mod.rs:950](../ember/server/src/a2a/mod.rs#L950) `flush`). 결국 3.1의 3번과 같은 `send`로 들어간다.

### 3.5 브라우저로 웹 IDE에 들어가면

1. 모든 요청이 Python 프록시의 [main.py:192](../ember/proxy/main.py#L192) `route_request`를 먼저 지난다.
2. 로그인 쿠키를 확인한다 ([auth/api.py:103](../ember/proxy/dpx/auth/api.py#L103)).
3. 화면과 웹소켓을 뒤에 있는 VS Code 서버(기본 포트 9092)로 중계한다 ([main.py:265](../ember/proxy/main.py#L265)).

---

## 4. 코드 상태 평가

### 잘 된 점

- **요구사항과 코드가 이어져 있다.** 주석과 테스트 이름에 `FR-S8`, `NFR-L2` 같은 `docs/SPEC.md`의 ID가 붙어 있어서, 어떤 코드가 왜 있는지 문서로 거슬러 올라갈 수 있다.
- **서버 테스트가 두텁다.** `ember/server`는 7.6만 줄 중 2.7만 줄이 테스트다. 가짜 에이전트(`scripted.rs`, `acp/fake_agent.rs`)와 가짜 허브·네트워크(`fake`, `mem.rs`)로 실제 CLI 없이도 시험한다.
- **경계가 분명하다.** 서버는 에이전트를, 노드는 실행을, 앱은 표시를 맡는다는 역할이 코드 주석과 실제 의존 관계에서 일치한다.
- **저장소 규칙을 CI가 검사한다.** webview 금지, em-dash 금지, transport 격리 같은 규칙이 `.github/scripts/checks/`에 스크립트로 있다.

### 위험한 점 (근거 포함)

| 심각도 | 문제 | 위치 |
|---|---|---|
| 높음 | 에이전트가 팀원 생성 요청에 환경 변수 이름과 주소를 넣으면, 서버가 그 비밀값을 그 주소로 보낸다 | [members.rs:209](../ember/server/src/members.rs#L209) |
| 높음 | Windows에서 암호화 키 파일 권한 검사가 아무것도 하지 않는다 | [secrets.rs:159](../ember/server/src/accounts/secrets.rs#L159) |
| 중간 | 웹 IDE 로그인에 시도 횟수 제한이 없다 | [auth/api.py:182](../ember/proxy/dpx/auth/api.py#L182) |
| 중간 | 새 팀원 화면의 컴퓨터 목록이 `mac-mini` 등으로 하드코딩돼 있다 | [cr/session.rs:3975](../ember/app/src/ui/cr/session.rs#L3975) |
| 중간 | 화면이 `ui/`와 `ui/cr/` 두 벌이다 (이전 중) | [ui/cr/mod.rs](../ember/app/src/ui/cr/mod.rs) |
| 중간 | 서버 이벤트 타입을 클라이언트에 손으로 복사했다 | [client/wire.rs](../ember/client/src/wire.rs) |
| 중간 | 데모 데이터가 서버 API를 따로 흉내 내서, API를 바꾸면 두 곳을 고쳐야 한다 | [demo.rs](../ember/app/src/demo.rs) |
| 낮음 | 5천 줄이 넘는 파일 (`ui/cr/vcs.rs` 5,825줄, `ui/vcs.rs` 5,312줄) | |
| 낮음 | TODO가 `ui/cr/`에 몰려 있다 (`project.rs` 29개) | |

전체 이슈 218건의 상세 목록은 [docs/analysis/05_ISSUES.md](../docs/analysis/05_ISSUES.md)에 있다. 위 표는
그중 코드로 다시 확인한 것이다.

---

## 5. 에이전트가 만든 코드에서 보이는 특징

- **"된 것처럼 보이는" 화면.** 버튼과 선택지는 있는데 요청에 반영되지 않거나(새 팀원 시트), 값이 하드코딩된 곳이 있다. 화면을 눌러 보는 것만으로는 구별이 안 되므로 실행 확인 때 서버 로그를 함께 본다.
- **멈춘 이전 작업.** UI 라이브러리 이전(`ui/` → `ui/cr/`)이 진행 중이라 같은 화면이 두 벌이고, TODO가 새 쪽에 몰려 있다. 화면을 고칠 때는 지금 어느 쪽이 실제로 쓰이는지 먼저 확인해야 한다.
- **복사로 해결한 경계.** 크레이트를 서로 링크하지 않으려고 타입을 복사한 곳(`client/wire.rs`, 확장의 `types.ts`는 darkpyonix-core의 API 명세를 옮겨 적은 것)이 있다. 한쪽만 고치면 조용히 어긋난다.
- **파일이 계속 커진다.** 기능을 한 파일에 덧붙이는 경향이 있어 2천 줄 넘는 파일이 15개다(테스트 제외). 에이전트에게 수정을 맡길 때도 파일이 클수록 실수가 늘어난다.

---

## 6. 더 깊이 보려면

| 하고 싶은 것 | 방법 |
|---|---|
| 증상으로 코드 찾기 | `uv run vibemap/scripts/build.py` 후 `vibemap/out/vibemap.html`을 열고 검색 |
| 모듈 하나 요약 보기 | `uv run vibemap/scripts/build.py --card server.core` (모듈 id는 `map.json`) |
| 화면 문구가 코드 어디 있는지 | `uv run vibemap/scripts/extract.py --find "준비 중입니다"` |
| 요구사항의 이유 | `docs/SPEC.md`에서 ID 검색, 결정 배경은 `docs/INTENT.md` |
| 코드가 바뀐 뒤 이 문서의 위치 확인 | `uv run vibemap/scripts/extract.py` 후 `uv run vibemap/scripts/verify.py` |

이 문서의 링크와 줄 번호는 commit 876186d7 기준이다. 코드가 바뀌면 `verify.py`가 밀린 위치를 알려 준다.
