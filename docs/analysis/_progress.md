# 분석 진행 기록
- 기준 커밋: ffe98256a35046158c3baae2065611168b70d97f (develop)
- 시작일: 2026-11-12
- 현재 단계: 완료 (2026-11-13). 갱신은 가이드 5장 절차대로

## 단계 체크
- [x] Phase 0 준비
- [x] Phase 1 인벤토리: `_raw/inventory.tsv`, `_raw/stack.md` (파일 844개, 281,783줄)
- [x] Phase 2 진입점: `_raw/entrypoints.md`, `_raw/routes.md`
- [x] Phase 3 의존성 그래프: `_raw/imports.tsv`(간선 1,583), `_raw/fan.tsv`, `_raw/orphans.md`(후보 9), `_raw/cycles.md`(SCC 17), `_raw/modules.md`(모듈 30)
- [x] Phase 4 모듈 분석 (모듈별 체크는 아래)
- [x] Phase 5 기능 지도: `01_FEATURE_MAP.md` (`.scratch/analysis/featuremap.py`)
- [x] Phase 6 이름 사전: `02_GLOSSARY.md`, `02_GLOSSARY-2.md`
- [x] Phase 7 흐름·데이터 모델: `03_FLOWS.md`, `04_DATA_MODEL.md`
- [x] Phase 8 문제점: `05_ISSUES.md` (207건)
- [x] Phase 9 수정 가이드: `06_FIX_GUIDE.md`
- [x] Phase 10 검증: 참조 1,974개 중 표본 2회 393개, 확인 가능 296개 중 오류 1개(고침, 약 0.3%). 이름 사전 254개 모두 존재, 링크 깨짐 0, 비밀값 0, em-dash 0. `[확인 필요]` 72, `[추정]` 20 (`.scratch/analysis/verify.py`)
- [x] Phase 11 개요 문서 완성: `00_OVERVIEW.md`

## 모듈 분석 체크
규모가 5만 줄을 넘어 가이드 6장에 따라 모듈 분석을 서브 에이전트에게 나눴다. 1차 시도(18개 동시, `.scratch/analysis/brief.md`)는 사용량 한도에 걸려 모두 중단됐고, 그 전에 완성된 10개 문서는 그대로 쓴다. 나머지는 간소판 지시서(`.scratch/analysis/brief-lean.md`, Sonnet, 동시 3개 이하, 노트 파일 없이 문서 끝 "이슈 후보" 절)와 스크립트로 만들었다.

| 모듈 | 방법 | 상태 |
|---|---|---|
| transport, client, editor-conn, node-git, server-core, server-computers, server-collab, server-api, proxy, extensions | 1차 에이전트 (상세판) | [x] |
| transfer, bridge, hub, editor, node, node-term, node-enrol, server-agents, server-enrol, server-accounts, app-core, app-ui-cr, app-ui-cr-session | 간소판 에이전트 | [x] |
| app-ui-cr-work | 간소판 에이전트 | [x] |
| tests (+ tests-2 역색인) | 스크립트 `.scratch/analysis/tests.py` | [x] |
| docs, tooling | 스크립트 `.scratch/analysis/docs_tooling.py` | [x] |
| app-ui, app-ui-collab, app-ui-dev | 스크립트 `.scratch/analysis/legacy.py`, `legacy_docs.py` (pub 항목의 생사 분류) | [x] |

노트 파일 `_raw/notes/`는 node-git 하나만 있다. Phase 5~8 재료는 각 모듈 문서의 "동작 지도", "데이터와 설정", "이슈 후보" 절에서 가져온다.

## 메모 / 다음에 할 일
- 가이드와 다른 점: 임시 스크립트는 저장소 규칙(AGENTS.md "Where files go")에 따라 `/tmp`가 아니라 `.scratch/analysis/`에 둔다. 모듈 크기 기준은 3,000줄 대신 하위 시스템 단위(`_raw/modules.md` 머리말).
- 앱의 기본 실행 경로는 `ember/app/src/ui/cr/`(compose-rust)다. Dioxus 루트 `crate::ui::app`은 호출되지 않는다 (`_raw/entrypoints.md`). 기능 지도는 `cr/` 화면 기준으로 만든다.
- 정정: `ui/`의 Dioxus 파일은 대부분 죽은 코드가 아니다. pub 항목 약 75%를 `cr/`가 쓴다 (`modules/app-ui*.md`). 통째로 죽은 후보는 `ui/mod.rs`, `ui/workbench.rs`뿐이다.
- 다음: app-ui-cr-work 완료 후 Phase 5(기능 지도)부터 메인 세션이 문서에서 모아 쓴다. 토큰 절약을 위해 원본 코드는 다시 읽지 않고 모듈 문서를 근거로 한다. Phase 10에서 참조를 표본 검증한다.
