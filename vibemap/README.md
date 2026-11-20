# vibemap: 바이브 코딩 코드베이스 지도

AI가 만든 큰 코드를 사람이 **"문제가 생기면 어디를 볼지 알고, 안전하게 고칠 수 있게"** 정리하는 도구입니다.

- **스크립트**가 코드에서 사실(파일, 연결, 함수, 위치)을 뽑습니다. 토큰이 들지 않습니다.
- **에이전트**는 짧은 설명(명함, 증상 지도)만 데이터로 씁니다.
- **사람**은 브라우저에서 뷰어로 봅니다. 검색창에 증상이나 화면 문구를 치면 볼 곳이 나옵니다.
- 함수 하나하나의 상세 설명은 미리 만들지 않습니다. 뷰어에서 **"에이전트에게 물어보기"** 버튼으로 프롬프트를 복사해 필요할 때 묻습니다.

필요한 것: uv (Python 3.8 이상, 추가 패키지 없음)

---

## 설치

`vibemap/` 폴더를 프로젝트 루트에 그대로 넣습니다.

`.gitignore`에 아래를 추가하는 것을 권장합니다. `map.json`과 `progress.md`는 커밋해서 팀이 함께 씁니다.

```
vibemap/data/raw.json
vibemap/data/raw_summary.md
vibemap/out/
```

## 사용 순서

모든 명령은 프로젝트 루트에서 실행합니다. 단계 사이에는 Claude Code에서 `/clear`로 대화를 비우면 토큰이 절약됩니다.

| 단계 | 누가 | 입력할 것 | 걸리는 세션 |
|---|---|---|---|
| 0. 추출 | 사람 | `uv run vibemap/scripts/extract.py` | 없음 (스크립트) |
| 1. 지도 | 에이전트 | `vibemap/VIBEMAP_GUIDE.md를 읽고 1단계만 수행해` | 1 |
| 2. 명함 | 에이전트 | `vibemap/VIBEMAP_GUIDE.md를 읽고 2단계를 progress.md 순서대로 모듈 3개만 수행해` | 모듈 수 ÷ 3 |
| 3. 증상 지도 | 에이전트 | `vibemap/VIBEMAP_GUIDE.md를 읽고 3단계만 수행해` | 1 |
| 4. 흐름·이름 | 에이전트 | `vibemap/VIBEMAP_GUIDE.md를 읽고 4단계만 수행해` | 1 |
| 5. 문제점 | 에이전트 | `vibemap/VIBEMAP_GUIDE.md를 읽고 5단계만 수행해` | 1 |
| 보기 | 사람 | `uv run vibemap/scripts/build.py` → `vibemap/out/vibemap.html`을 브라우저로 열기 | 없음 |

- 1단계까지만 해도 뷰어에서 전체 구조와 함수·파일 검색을 쓸 수 있습니다. 나머지는 필요한 만큼만 하세요.
- 명함은 자주 고치는 모듈부터 만들면 됩니다. 전부 만들 필요는 없습니다.
- 사용자 테스트 피드백이 있으면 `vibemap/data/feedback.md`에 한 줄씩 적은 뒤(형식은 `feedback.example.md` 참고) 3단계를 하세요. 피드백마다 증상 카드가 생깁니다.

## 코드가 바뀐 뒤

```
uv run vibemap/scripts/extract.py
uv run vibemap/scripts/verify.py
```

`verify.py`가 줄이 밀리거나 이름이 바뀐 위치를 알려 줍니다. 오류가 있으면 에이전트에게 `vibemap/VIBEMAP_GUIDE.md의 4장 갱신 절차를 수행해`라고 지시하세요.

## 혼자 쓸 수 있는 명령

| 명령 | 용도 |
|---|---|
| `uv run vibemap/scripts/extract.py --find "결제하기"` | 화면 문구나 에러 메시지가 코드 어디에 있는지 |
| `uv run vibemap/scripts/extract.py --module <id>` | 모듈의 파일, 공개 함수, 다른 모듈과의 연결 |
| `uv run vibemap/scripts/extract.py --signals` | 중복 이름, 안 쓰는 파일, 큰 파일 등 정리 후보 |
| `uv run vibemap/scripts/build.py --card <id>` | 모듈 명함을 텍스트로 (에이전트에게 붙여 넣기 좋음) |
| `uv run vibemap/scripts/build.py --symptom S1` | 증상 하나와 관련 모듈 명함 |

## 파일 구성

```
vibemap/
├── README.md            사람용 (이 파일)
├── VIBEMAP_GUIDE.md     에이전트용 작업 지시서
├── config.json          (선택) 제외 경로, 모듈 경로 직접 지정
├── scripts/
│   ├── extract.py       코드에서 사실 추출
│   ├── verify.py        map.json의 위치가 실제 코드와 맞는지 검사
│   └── build.py         뷰어 HTML 생성, 명함 출력
├── viewer/template.html 뷰어 원본
├── data/
│   ├── raw.json         추출 결과 (자동)
│   ├── raw_summary.md   추출 요약 (자동, 에이전트가 읽음)
│   ├── map.json         지도·명함·증상·흐름·이슈·이름 (에이전트가 씀)
│   ├── progress.md      진행 기록
│   └── feedback.md      (선택) 사용자 테스트 피드백
└── out/vibemap.html     뷰어 (이것만 열면 됨, 다른 사람에게 보내도 됨)
```

## 지원 언어

import 관계와 공개 함수 추출: Python, JavaScript/TypeScript(Vue·Svelte 포함), Go, Rust, Java, Kotlin.
그 밖의 언어는 파일 목록과 줄 수, 검색만 됩니다.
