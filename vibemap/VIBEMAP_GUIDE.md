# vibemap 가이드 (에이전트 실행용)

> 이 문서는 AI 에이전트(Claude Code 등)가 읽고 그대로 수행하는 작업 지시서입니다.
> 사람용 설명은 `vibemap/README.md`에 있습니다.

## 목표

바이브 코딩으로 만든 코드베이스를 사람이 **"문제가 생기면 어디를 볼지 알고, 안전하게 고칠 수 있게"** 만드는 것이 목표다. 코드를 전부 설명하는 것이 목표가 아니다.

그래서 세 층만 만든다.

| 층 | 내용 | 누가 만드나 |
|---|---|---|
| 지도 | 모듈 구분, 층, 모듈 간 연결 | 연결은 스크립트, 구분·설명은 에이전트 |
| 명함 | 모듈마다 하는 일, 시작점, 약속, 자주 나는 문제, 주의 | 에이전트 (짧게) |
| 상세 | 함수 하나하나의 설명 | **미리 만들지 않는다.** 필요할 때 사람이 뷰어에서 프롬프트를 복사해 묻는다 |

결과는 사람이 읽을 글이 아니라 **데이터(`vibemap/data/map.json`)** 로 쓴다. 사람은 `build.py`가 만든 HTML 뷰어로 본다.

---

## 1. 절대 규칙

1. **소스 코드를 수정하지 않는다.** 쓰기는 `vibemap/data/` 안에서만 한다.
2. **추측하지 않는다.** 위치는 항상 `path:line` 형식으로 적고, `verify.py`로 확인한다. 확인 못 한 내용은 쓰지 않는다.
3. **코드의 이름은 그대로**, 설명은 한국어로 짧게 쓴다.
4. **비밀값을 기록하지 않는다.** 위치만 적는다.
5. **글자 수 상한을 지킨다.** 사람의 눈이 아프지 않게 하는 핵심 규칙이다.

| 필드 | 상한 | 필드 | 상한 |
|---|---|---|---|
| `one_line` | 60자 | `symptom` | 60자 |
| `what`, `why`, `desc` | 80자 | `breaks_if`, `check`, `fix`, `caution` | 90자 |
| `entry_points`, `contracts`, `problems` | 각 6개 이하 (권장 3~4개) | `cautions`, `look` | 4개 이하 |

---

## 2. 토큰 절약 규칙 (Claude Pro 기준)

사용량이 넉넉하지 않은 환경을 전제로 한다. 아래 규칙은 예외 없이 지킨다.

1. **서브 에이전트, 병렬 에이전트, Task 도구를 쓰지 않는다.** 혼자 순서대로 한다.
2. **한 세션에 한 단계만 한다.** 3단계(명함)는 한 세션에 모듈 2~4개까지만 한다. 단계가 끝나면 `vibemap/data/progress.md`를 갱신하고 멈춘다. 사람은 `/clear` 후 다음 단계를 지시한다.
3. **기계적인 일은 스크립트에 맡긴다.** 파일 목록, import 관계, 공개 함수, 라우트, 환경 변수, 중복 이름, 위치 검증은 모두 스크립트가 한다. 에이전트가 직접 세거나 찾지 않는다.
4. **`raw.json`을 직접 읽지 않는다.** 크다. 대신 아래 명령의 출력만 본다.
   - 전체 요약: `vibemap/data/raw_summary.md`
   - 모듈 하나: `uv run vibemap/scripts/extract.py --module <raw 모듈 id>`
   - 이슈 후보: `uv run vibemap/scripts/extract.py --signals`
   - 문자열 위치: `uv run vibemap/scripts/extract.py --find "<문구>"`
5. **파일을 통째로 읽지 않는다.** `--module` 출력에 나온 줄 번호 주변만 읽는다(앞뒤 20~40줄). 모듈 하나당 읽는 양은 **합계 400줄 이내**를 목표로 한다.
6. **`map.json`을 통째로 다시 쓰지 않는다.** 처음 만들 때만 전체를 쓰고, 이후에는 해당 모듈 객체만 Edit로 바꾼다.
7. **대화로 길게 설명하지 않는다.** 결과는 `map.json`에 쓰고, 사람에게는 마지막에 3줄 이내로 보고한다.
8. **완벽하게 하려고 하지 않는다.** 모든 모듈에 명함이 없어도 뷰어는 동작한다. 사람이 자주 고치는 모듈부터 한다.

---

## 3. 단계

각 단계 끝에는 항상 아래를 실행하고, 오류가 0이 될 때까지 고친다.

```
uv run vibemap/scripts/verify.py
uv run vibemap/scripts/build.py
```

### 0단계: 추출 (스크립트만, 에이전트 불필요)

```
uv run vibemap/scripts/extract.py
```

`raw.json`과 `raw_summary.md`가 생긴다. 사람이 직접 실행해도 된다.

모듈 후보가 너무 잘게 나뉘었거나 생성 코드가 섞였다면 `vibemap/config.json`을 만들어 조정한 뒤 다시 실행할 수 있다.

```json
{ "exclude": ["frontend/src/client/generated"], "modules": { "web": "frontend/src", "api": "backend/app" } }
```

### 1단계: 지도 (1세션)

**읽을 것:** `raw_summary.md`, `README`의 앞부분(80줄 이내), 스택을 알려 주는 설정 파일(`package.json`의 scripts, `pyproject.toml` 등)

**할 일**
1. 프로젝트 한 줄 요약, 구조 유형(`raw_summary.md`의 구조 추정 참고), 실행 명령을 정한다.
2. **raw 모듈 후보를 사람이 이해할 단위(보통 6~15개)로 묶는다.**
   - 기술 종류별 구조(`tech`): 기능이 보이도록 묶는다. 예) `components/Items`, `components/Admin` → "기능 화면 조각"
   - 기능별 구조(`feature`): 폴더를 거의 그대로 쓴다.
   - 역할·계층별 구조(`layer`): 폴더를 그대로 쓰고 층 순서를 정하는 데 집중한다.
   - `path`에는 폴더(또는 폴더 목록)를 적는다. **상위 폴더를 적으면 더 구체적인 path를 가진 모듈이 없는 하위 폴더를 모두 맡는다.** 이 성질을 이용해 남는 파일이 없게 한다.
3. **층(layers)을 정한다.** 위에서 아래로: 사용자 접점 → 기능 → 공통·기반 → 테스트·도구. 층 이름과 설명은 사람이 이해하는 말로 쓴다.
4. 모든 모듈을 `status: "draft"`, `one_line`만 채운 상태로 `map.json`을 만든다.
5. `progress.md`를 만든다. 모듈 목록을 명함 작성 우선순위 순으로 적는다. 우선순위는 (1) 사람이 자주 고친다고 말한 곳 (2) `used_by`가 많은 곳 (3) 사용자 접점 순이다.

**완료 조건:** `verify.py`에 오류가 없고 `[미배정]` 파일이 없다.

### 2단계: 명함 (모듈 2~4개씩, 여러 세션)

`progress.md`에서 아직 안 한 모듈을 위에서부터 고른다.

**모듈마다**
1. 해당 모듈에 속한 raw 모듈 id마다 `extract.py --module <id>`를 실행한다.
2. 출력의 **"다른 모듈이 쓰는 파일"** 이 약속(contracts) 후보이고, **팬인이 높은 파일의 공개 심볼**과 라우트가 시작점(entry_points) 후보다.
3. 후보의 줄 번호 주변만 읽고 명함을 채운다.
   - `entry_points` (3~4개): "이 모듈을 이해하려면 여기서부터 읽어라"
   - `contracts` (3~5개): 다른 모듈이 쓰는 것. **`breaks_if`에는 바꾸면 무엇이 깨지는지를 꼭 적는다.** 사용처 수는 `--module` 출력의 숫자를 쓴다.
   - `problems` (2~3개): 이 모듈에서 날 법한 증상과 볼 곳. 에러 메시지, 검증 조건, 권한 체크, 외부 호출 지점이 좋은 후보다.
   - `cautions` (1~3개): 자동 생성 파일, 프론트·백엔드 중복 정의, 순서 의존성처럼 모르고 고치면 사고가 나는 것만 적는다.
4. `status`를 `"carded"`로 바꾼다. `verify.py`를 통과하고 시작점을 실제로 열어 확인했다면 `"verified"`로 바꾼다.
5. `progress.md`에 체크한다.

**좋은 예 / 나쁜 예**

```
나쁨  "what": "이 함수는 사용자 인증을 처리하며 토큰을 검증하고 데이터베이스에서 사용자를 조회한 뒤 활성 상태를 확인하여 반환합니다"
좋음  "what": "토큰으로 현재 사용자 확인", "breaks_if": "로그인이 필요한 API 전부 영향"
```

### 3단계: 증상 지도 (1세션)

사람은 문제를 항상 **증상**으로 만난다. 이 단계의 결과물이 가장 많이 쓰인다.

**재료 모으기 (스크립트와 grep으로, 파일 전체를 읽지 말 것)**
- `raw_summary.md`의 라우트 목록
- 사용자에게 보이는 에러 메시지: `HTTPException`, `throw new Error`, `toast`, `alert`, `log.error`, `panic`, `return err` 같은 패턴을 grep해서 **개수와 위치만** 본다
- `vibemap/data/feedback.md`가 있으면 그 내용 (사람이 적은 실제 사용자 테스트 피드백)

**할 일**
- 증상 8~20개를 쓴다. `category`로 묶는다(예: 로그인, 결제, 연결, 성능).
- `symptom`은 **사용자나 테스터가 실제로 말할 문장**으로 쓴다. ("get_current_user 403" 말고 "로그인했는데 로그인 화면으로 튕김")
- `keywords`에는 화면 문구, 에러 메시지 원문, 비슷한 표현을 넣는다. 검색에 걸리게 하기 위해서다.
- `look`에는 먼저 볼 곳 2~4개를 원인에 가까운 순서로 적는다.
- `steps`는 사람이 코드를 열기 전에 확인할 수 있는 것 위주로 적는다(브라우저 개발자도구, 로그, 설정값).
- `feedback.md`의 항목은 하나도 빠짐없이 증상으로 만든다.

### 4단계: 흐름과 이름 (1세션)

**흐름 (`flows`, 3~5개):** 핵심 사용자 시나리오가 지나가는 코드를 4~8단계로 적는다. 화면 → API → 로직 → 저장처럼 **모듈 경계를 넘는 지점**이 꼭 들어가야 한다. import로는 보이지 않는 연결(HTTP, 메시지 큐, 이벤트, 소켓)은 흐름으로만 드러나기 때문이다.

**이름 (`names`, 10~30개):** 다음만 고른다.
- 여러 모듈에서 쓰는 상태값, 설정, 상수, 환경 변수
- 이름만 봐서는 뜻을 알 수 없는 것 (`data`, `temp`, `handleClick2` 등)
- 바꾸면 다른 곳이 깨지는 것 (`caution`에 이유를 적는다)

### 5단계: 문제점 (1세션)

```
uv run vibemap/scripts/extract.py --signals
```

출력은 **후보**일 뿐이다. 라이브러리 관례(예: 파일 기반 라우팅의 `Route`), 마이그레이션 파일, 동적 로딩 파일은 걸러낸다. 의심되는 것만 해당 위치를 열어 확인한다.

- 5~20개를 `issues`로 적는다. 심각도: `high`는 보안·데이터 손상, `mid`는 버그 유발·수정 시 혼란, `low`는 정리하면 좋은 것.
- `fix`는 한 문장으로 쓴다. 고치지는 않는다.

### 6단계: 마무리

1. `verify.py` 오류 0, 경고는 가능한 한 줄인다.
2. `build.py`로 `vibemap/out/vibemap.html`을 만든다.
3. 사람에게 3줄로 보고한다: 모듈·증상·이슈 개수, 심각도 높음 이슈, 다음에 할 일.

---

## 4. 갱신 (코드가 바뀐 뒤)

1. `uv run vibemap/scripts/extract.py`를 다시 실행한다.
2. `uv run vibemap/scripts/verify.py`를 실행한다. **줄이 밀렸거나 이름이 바뀐 위치가 오류로 나온다.** 이 오류만 고치면 된다.
3. 새로 생긴 폴더가 `[미배정]`으로 나오면 모듈 path에 추가하거나 새 모듈을 만든다.
4. 크게 바뀐 모듈만 `status`를 `"draft"`로 내리고 2단계를 다시 한다. 바뀐 파일은 `git diff --name-only <project.commit> HEAD`로 확인한다.
5. `project.commit`과 `project.updated`를 갱신하고 `build.py`를 실행한다.

---

## 5. `map.json` 형식

```json
{
  "version": 1,
  "project": {
    "name": "프로젝트 이름",
    "summary": "무엇을 하는 프로그램인지 1~2문장 (160자 이내)",
    "structure": "tech | feature | layer",
    "commit": "abc1234",
    "updated": "YYYY-MM-DD",
    "how_to_run": [ { "label": "개발 서버", "cmd": "npm run dev" } ]
  },
  "layers": [
    { "id": "screen", "name": "화면", "desc": "사용자가 보고 누르는 곳", "modules": ["web.pages"] }
  ],
  "modules": [
    {
      "id": "web.pages",
      "name": "페이지",
      "path": "frontend/src/routes",
      "status": "draft | carded | verified",
      "one_line": "URL마다 하나씩 있는 화면",
      "entry_points": [ { "name": "onSubmit", "at": "frontend/src/routes/login.tsx:65", "what": "로그인 버튼" } ],
      "contracts":    [ { "name": "useAuth", "at": "frontend/src/hooks/useAuth.ts:70", "what": "로그인 상태", "breaks_if": "화면 13곳" } ],
      "problems":     [ { "symptom": "로그인 화면으로 튕김", "check": "frontend/src/routes/_layout.tsx:14" } ],
      "cautions":     [ "routeTree.gen.ts는 자동 생성" ]
    }
  ],
  "symptoms": [
    {
      "id": "S1", "category": "로그인", "symptom": "로그인했는데 로그인 화면으로 튕김",
      "keywords": ["redirect", "access_token"],
      "modules": ["web.pages", "web.core"],
      "look": [ { "at": "frontend/src/routes/_layout.tsx:14", "why": "토큰이 없으면 /login으로", "name": "beforeLoad" } ],
      "steps": [ "localStorage에 access_token이 있는지" ]
    }
  ],
  "flows": [
    { "id": "F1", "name": "로그인", "desc": "선택", "steps": [ { "module": "web.pages", "at": "path:line", "what": "버튼 → onSubmit", "name": "onSubmit" } ] }
  ],
  "issues": [
    { "id": "I1", "severity": "high | mid | low", "type": "보안", "at": "path:line", "what": "무엇이 문제인지", "fix": "권장 조치" }
  ],
  "names": [
    { "name": "access_token", "kind": "localStorage 키", "module": "web.core", "at": "path:line", "meaning": "뜻", "caution": "선택" }
  ]
}
```

**`at`과 `name`에 대해:** `at`은 `path:line`이고, 같은 객체에 `name`이 있으면 `verify.py`가 그 이름이 해당 줄 ±3줄 안에 실제로 있는지 확인한다. 위치를 확실하게 하고 싶을 때는 `name`을 함께 적는다. 파일 전체를 가리킬 때는 줄 번호 없이 경로만 적어도 된다.

---

## 6. 하네스·다른 에이전트와 함께 쓰기

명함이 만들어진 뒤에는, 코드를 고치는 에이전트가 수정 전에 명함을 먼저 보게 할 수 있다. 프로젝트의 `CLAUDE.md`(또는 `AGENTS.md`)에 아래를 추가하도록 사람에게 제안한다. 직접 추가하지는 않는다.

```markdown
## 코드 수정 전
- 고칠 파일이 속한 모듈의 명함을 먼저 확인: `uv run vibemap/scripts/build.py --card <모듈 id>` (모듈 id 목록은 vibemap/data/map.json)
- 명함의 contracts에 있는 함수를 바꾸면 breaks_if에 적힌 곳도 확인
- 수정 후 `uv run vibemap/scripts/verify.py`가 오류를 내면 vibemap/data/map.json의 해당 위치도 갱신
```
