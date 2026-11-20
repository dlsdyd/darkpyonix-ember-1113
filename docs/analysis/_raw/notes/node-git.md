# 노트: node-git

## A. 이슈 후보 (Phase 8 재료)

| 분류 | 심각도 제안 | 위치 | 내용 | 권장 조치 |
|---|---|---|---|---|
| 보안 | 중간 | `ember/node/src/git_prs.rs:621-653`, `ember/node/src/api.rs:451-453` | `/git/pr/merge`에 `delete_branch: true`면 gh가 로컬 브랜치를 지우고 체크아웃을 바꿀 수 있는데 노드 `write_lock`을 잡지 않는다. 동시에 도는 stage/commit과 경합 가능 | `delete_branch`일 때 핸들러에서 락을 잡거나 로컬 변경을 막는 옵션 검토 |
| 보안 | 낮음 | `ember/node/src/git_conflict.rs:29-39`, `:107` | 심볼릭 링크 검사 후 `tokio::fs::write`까지 시간 차 (TOCTOU). 저장소에 쓸 수 있는 다른 프로세스가 링크로 바꾸면 루트 밖 파일에 쓸 수 있다 [추정] | `O_NOFOLLOW` 열기 또는 쓰기 직전 재검사 |
| 보안 | 낮음 | `ember/node/src/git_commit.rs:190` | `core.hooksPath=/dev/null`은 Windows 노드에서 의도대로 훅을 끄는지 확인되지 않았다 [확인 필요] | Windows 통합 테스트 추가 또는 `NUL`/빈 디렉터리 사용 |
| 패턴 불일치 | 중간 | `ember/node/src/git.rs:443-451` 대 `ember/node/src/git_commit.rs:192-237` | 에러 응답에 git 원문을 붙이는 정책(FR-G1~G13)과 붙이지 않는 정책(FR-G14 이후)이 공존 | SPEC에서 하나로 정하고 통일 |
| 중복 구현 | 중간 | `ember/node/src/git_prs.rs:286-311`, `ember/node/src/git_github.rs:98-128` | `gh` 실행기(환경 변수 7개 포함)가 두 벌 | 공용 `gh_command()` 헬퍼로 합치기 |
| 중복 구현 | 낮음 | `ember/node/src/git_prs.rs:242-258`, `ember/node/src/git_github.rs:72-90` | gh 실패 → 한국어 표가 두 벌 (404 문구가 서로 다름) | 하나로 합치기 |
| 중복 구현 | 낮음 | `ember/node/src/git_merge.rs:51`, `ember/node/src/git_github.rs:57` | 같은 이름 `clean_name`, 반환형(`Option<String>` 대 `String`)과 동작이 다름 | 이름 구분 또는 공용화 |
| 중복 구현 | 중간 | `ember/node/src/git_prs.rs:176`, `ember/app/src/ui/vcs.rs:292`, `ember/app/src/ui/cr/vcs.rs:28` | 병합 조건 `merge_gate`가 노드와 앱에 따로 구현되어 있다. 규칙이 어긋날 수 있다 | 앱은 노드의 `merge.can_merge`/`reason`만 쓰도록 검토 |
| 중복 구현 | 낮음 | `ember/client/src/api.rs:325`, `:624`, `:632` | `GitMergeState`, `GitStashEntry`, `GitConflict` 등 DTO를 클라이언트가 다시 정의 | 공용 타입 크레이트 검토 (크레이트 의존 방향 확인 필요) |
| 죽은 코드 | 낮음 | `ember/node/src/git.rs:814` | `pub async fn pull`은 저장소 어디서도 호출하지 않는다 (`grep -rnE "git::pull\(" ember` 결과 없음). 핸들러는 두 단계를 따로 부른다 (`api.rs:506-513`) | 삭제하거나 테스트 전용으로 표시 |
| 죽은 코드 | 낮음 | `ember/node/src/git_branches.rs:32`, `:47`, `:75`, `:80`, `ember/node/src/git_merge.rs:44`, `:51`, `ember/node/src/git_github.rs:131`, `:145`, `ember/node/src/git_commit.rs:87`, `:114`, `:140`, `:156`, `:211` | `pub`인데 파일 밖 사용처가 없다 (같은 파일 테스트만 사용) | `pub(crate)` 또는 비공개로 |
| 잔해 파일 | 낮음 | `ember/node/src/git_github.rs:5` | 주석은 "Five calls", 실제 호출은 4회 (`:176`, `:192`, `:202`, `:217`) | 주석 수정 |
| 패턴 불일치 | 낮음 | `ember/node/src/git_commit.rs:187`, `:337-341` | cherry-pick abort 실패에도 "되돌리기를 취소하지 못했습니다" 문구 | 동작별 문구 |
| 패턴 불일치 | 낮음 | `ember/node/src/git_merge.rs:102-104`, `ember/node/src/git_prs.rs:516-518`, `ember/node/src/git_commit.rs:303-305` | `need_confirm`이 세 번 구현 | 공용 함수 |
| 하드코딩 | 낮음 | `ember/node/src/git_prs.rs:195-199` | 승인이 없으면 항상 병합 불가. 리뷰가 필수가 아닌 저장소도 막힘 | 브랜치 보호 규칙(`mergeStateStatus`) 반영 검토 |
| 패턴 불일치 | 낮음 | `ember/node/src/git.rs:574-582` | async 함수 안에서 `std::fs::metadata` 동기 호출 | `tokio::fs::metadata` |
| 패턴 불일치 | 낮음 | `ember/node/src/git.rs:304-305` | 비 unix에서 네트워크 시간 초과 시 자식 프로세스 트리를 죽이지 않는다 (git만 kill) | Windows job object 또는 `taskkill /T` |
| 거대 파일 | 낮음 | `ember/node/src/git.rs` (841줄), `ember/node/src/git_prs.rs` (794줄) | 500줄 초과. 함수 100줄 초과는 없음 (`status` 88줄, `git.rs:497-584`) | `git.rs`의 실행기와 작업을 분리 검토 |

TODO/FIXME/XXX/HACK: 9개 파일 모두 0개 (`grep -nE 'TODO|FIXME|XXX|HACK'` 결과 없음).

## B. 이름 사전 후보 (Phase 6 재료)

| 이름 | 종류 | 정의 위치 | 의미 | 값/형태 | 사용처 수 | 주의 |
|---|---|---|---|---|---|---|
| `GitError` | enum | `ember/node/src/git.rs:156` | git/gh 작업 실패 분류 | `Policy`, `NotARepo`, `Bad`, `Conflict`, `NotFound`, `Internal`, `Timeout`, `TooLarge` | 9개 파일 + `api.rs:321` | HTTP 상태와 1:1 (`api.rs:321-328`) |
| `GitRepoRequest` | struct | `ember/node/src/git.rs:43` | 저장소만 지정하는 요청 | `{ repo }` | 7곳 이상 | `GitStatusRequest`는 별칭 (`:47`) |
| `NETWORK_TIMEOUT_SECS` | const | `ember/node/src/git.rs:179` | fetch/pull/push/gh 시간 제한 | 60 | 2 (+테스트) | 환경 변수로 덮음 |
| `MAX_OUTPUT_BYTES` | const | `ember/node/src/git.rs:181` | git stdout 상한 | 8 MiB | 3 | 충돌 파일 읽기 상한도 같은 값 (`git_conflict.rs:57`) |
| `MAX_STDERR_BYTES` | const | `ember/node/src/git.rs:182` | stderr 상한 | 1 MiB | 1 | |
| `NO_HOOKS` | const | `ember/node/src/git_commit.rs:190` | 사용자 훅 끄기 | `["-c", "core.hooksPath=/dev/null"]` | 4 | Windows 동작 [확인 필요] |
| `MAX_FILES`, `MAX_BODY_CHARS` | const | `ember/node/src/git_commit.rs:12`, `:14` | 커밋 상세 상한 | 500, 20000 | 각 1 | |
| `MAX_NAME_CHARS` | const | `ember/node/src/git_merge.rs:12`, `ember/node/src/git_github.rs:21` | 이름 자르기 | 둘 다 100 | 2 정의 | 같은 이름 두 정의 |
| `DEFAULT_LIMIT`, `MAX_LIMIT` | const | `ember/node/src/git_prs.rs:14-15` | PR 목록 | 30, 200 | 1 | |
| `MAX_PR_NUMBER`, `MAX_INPUT_BODY_CHARS`, `MAX_TITLE_CHARS`, `MAX_COMMENTS`, `MAX_ITEM_CHARS`, `MAX_PR_BODY_CHARS`, `MAX_DETAIL_CHARS` | const | `ember/node/src/git_prs.rs:331-339`, `:262` | PR 입력/출력 상한 | 999999, 60000, 256, 50, 2000, 20000, 500 | 각 1~2 | |
| `PR_LIMIT`, `RUN_LIMIT` | const | `ember/node/src/git_github.rs:17`, `:19` | 카드 요약 | 100, 14 | 1 | |
| git_log 기본 limit | 매직 넘버 | `ember/node/src/git_log.rs:6`, `:41` | 로그 기본/최대 | 50 / 500 | 1 | 상수 이름 없음 |
| `GitPrsState` | enum(상태 문자열) | `ember/node/src/git_prs.rs:22` | 목록 필터 | `open`(기본), `closed`, `merged`, `all` | 1 | |
| `GitPrState` | enum | `ember/node/src/git_prs.rs:56` | PR 상태 | `open`, `closed`, `merged` | 2 | 알 수 없는 값은 `Open` (`:203-207`) |
| `GitPrReview` | enum | `ember/node/src/git_prs.rs:60` | 리뷰 결정 | `approved`, `changes_requested`, `review_required`, `none` | 2 | |
| `GitPrReviewState` | enum | `ember/node/src/git_prs.rs:361` | 개별 리뷰 상태 | `approved`, `changes_requested`, `commented`, `dismissed`, `pending` | 1 | |
| `GitPrCheckState`/`CheckClass` | enum | `ember/node/src/git_prs.rs:349`, `:134` | 체크 결과 | passed/failed/pending | 2 | 같은 뜻 enum 두 개 |
| `CiRun` | enum | `ember/node/src/git_github.rs:33` | 워크플로 결과 | `success`, `failure`, `cancelled`, `pending` | 1 | `skipped`는 `cancelled`로 (`:138`) |
| `GitCommitFileStatus` | enum | `ember/node/src/git_commit.rs:35` | 파일 변경 종류 | `added`, `modified`, `deleted`, `renamed`, `copied`, `type_changed` | 1 | `U`는 `modified`로 (`:94`) |
| `GitLogRefKind` | enum | `ember/node/src/git_log.rs:38` | ref 종류 | `branch`, `remote`, `tag`, `head` | 2 | |
| `ConflictBlock` | enum | `ember/node/src/git_conflict.rs:17` | 충돌 파일 블록 | `kind: common/conflict` | 1 | |
| `GitStashOperation` | enum | `ember/node/src/git_stash.rs:22` | stash 변경 종류 | `Apply`, `Pop`, `Drop` | 4 (`api.rs`) | |
| `Out` | struct | `ember/node/src/git.rs:212` | 프로세스 결과 | `code`, `stdout`, `stderr`, `truncated` | 4 파일 | 이름이 의미를 드러내지 못함 (이름 정리 후보: `ProcOutput`) |
| `run_k` | fn | `ember/node/src/git_commit.rs:227` | 원문 없는 실패 실행기 | | 2 파일 | 이름 정리 후보 (`k`가 Korean인지 불분명) |
| `act` | fn | `ember/node/src/git_commit.rs:301` | revert/cherry-pick 공통 | | 2 | 이름 정리 후보 |

환경 변수:

| 이름 | 사용 위치 | 용도 | 기본값 | 필수 여부 |
|---|---|---|---|---|
| `EMBER_GIT_NETWORK_TIMEOUT_SECS` | `ember/node/src/git.rs:187` | 네트워크 git/gh 시간 제한 (테스트용) | 60 | 아니오 |
| `EMBER_GIT_MAX_OUTPUT_BYTES` | `ember/node/src/git.rs:198` | stdout 상한 (테스트용) | 8388608 | 아니오 |
| `EMBER_GH_BIN` | `ember/node/src/git_prs.rs:288`, `ember/node/src/git_github.rs:99` | 실행할 gh 프로그램 (테스트는 가짜 스크립트) | `gh` | 아니오 |
| `GIT_SSH_COMMAND` (읽기) | `ember/node/src/git.rs:287` | 설정돼 있으면 BatchMode를 덧붙이지 않음 | 없음 | 아니오 |
| 자식에 설정: `LC_ALL`, `GIT_TERMINAL_PROMPT`, `GCM_INTERACTIVE`, `GIT_EDITOR`, `GIT_SEQUENCE_EDITOR`, `SSH_ASKPASS_REQUIRE`, `GIT_LITERAL_PATHSPECS`, `GIT_SSH_COMMAND` | `ember/node/src/git.rs:265-288` | 프롬프트 차단 | | |
| 자식에 설정: `GH_PROMPT_DISABLED`, `NO_COLOR`, `GH_NO_UPDATE_NOTIFIER`, `GH_SPINNER_DISABLED`, `GIT_TERMINAL_PROMPT`, `LC_ALL`, `GH_FORCE_TTY` 제거 | `ember/node/src/git_prs.rs:292-298`, `ember/node/src/git_github.rs:103-109` | gh 비대화 | | |

## C. 동작 지도 재료 (Phase 5 재료)

| HTTP 라우트 | 핸들러 | 호출하는 서비스 함수 | 읽거나 쓰는 데이터 |
|---|---|---|---|
| POST `/git/status` | `ember/node/src/api.rs:459` | `ember/node/src/git.rs:497` | git `status`, `for-each-ref`, `FETCH_HEAD` mtime |
| POST `/git/diff` | `ember/node/src/api.rs:463` | `ember/node/src/git.rs:605` | git `diff`, `ls-files`, `diff --no-index` |
| POST `/git/stage` | `ember/node/src/api.rs:467` | `ember/node/src/git.rs:641` | git `add -A` (index 쓰기) |
| POST `/git/unstage` | `ember/node/src/api.rs:473` | `ember/node/src/git.rs:649` | git `reset` 또는 `rm --cached` |
| POST `/git/apply` | `ember/node/src/api.rs:479` | `ember/node/src/git.rs:662` | git `apply --cached --recount` (stdin 패치) |
| POST `/git/commit` | `ember/node/src/api.rs:485` | `ember/node/src/git.rs:675` | git `commit -F -`, `rev-parse HEAD` |
| POST `/git/checkout` | `ember/node/src/api.rs:490` | `ember/node/src/git.rs:702` | git `switch` |
| POST `/git/branch` | `ember/node/src/api.rs:496` | `ember/node/src/git.rs:708` | git `switch -c` |
| POST `/git/fetch` | `ember/node/src/api.rs:502` | `ember/node/src/git.rs:770` | git `fetch` (네트워크) |
| POST `/git/pull` | `ember/node/src/api.rs:506` | `ember/node/src/git.rs:779`, `:805` | git `fetch`, `merge --ff-only @{u}` |
| POST `/git/push` | `ember/node/src/api.rs:515` | `ember/node/src/git.rs:822` | git `push` (네트워크) |
| POST `/git/conflicts` | `ember/node/src/api.rs:519` | `ember/node/src/git.rs:837` | git `diff --diff-filter=U` |
| POST `/git/log` | `ember/node/src/api.rs:422` | `ember/node/src/git_log.rs:40` | git `log` |
| POST `/git/commit/show` | `ember/node/src/api.rs:942` | `ember/node/src/git_commit.rs:249` | git `show`, `diff-tree` |
| POST `/git/revert` | `ember/node/src/api.rs:946` | `ember/node/src/git_commit.rs:293` | git `revert`, 실패 시 `revert --abort`/`reset --hard` |
| POST `/git/cherry-pick` | `ember/node/src/api.rs:951` | `ember/node/src/git_commit.rs:297` | git `cherry-pick`, 실패 시 abort/reset |
| POST `/git/merge` | `ember/node/src/api.rs:958` | `ember/node/src/git_merge.rs:94` | `MERGE_HEAD`, `MERGE_MSG` 파일, git `name-rev` |
| POST `/git/merge/abort` | `ember/node/src/api.rs:962` | `ember/node/src/git_merge.rs:107` | git `merge --abort` |
| POST `/git/merge/commit` | `ember/node/src/api.rs:967` | `ember/node/src/git_merge.rs:122` | git `commit --no-edit` |
| POST `/git/branches` | `ember/node/src/api.rs:428` | `ember/node/src/git_branches.rs:106` | git `for-each-ref`, `remote`, `symbolic-ref` |
| POST `/git/stash/list` | `ember/node/src/api.rs:524` | `ember/node/src/git_stash.rs:36` | git `stash list` |
| POST `/git/stash/push` | `ember/node/src/api.rs:528` | `ember/node/src/git_stash.rs:52` | git `stash push` |
| POST `/git/stash/apply`, `/pop`, `/drop` | `ember/node/src/api.rs:534`, `:540`, `:546` | `ember/node/src/git_stash.rs:64` | git `stash apply/pop/drop` |
| POST `/git/conflict` | `ember/node/src/api.rs:554` | `ember/node/src/git_conflict.rs:47` | 작업 트리 파일 읽기 |
| POST `/git/resolve` | `ember/node/src/api.rs:558` | `ember/node/src/git_conflict.rs:105` | 작업 트리 파일 쓰기, git `add` |
| POST `/git/prs` | `ember/node/src/api.rs:434` | `ember/node/src/git_prs.rs:317` | `gh pr list` |
| POST `/git/pr` | `ember/node/src/api.rs:445` | `ember/node/src/git_prs.rs:534` | `gh pr view` |
| POST `/git/pr/review` | `ember/node/src/api.rs:448` | `ember/node/src/git_prs.rs:568` | `gh pr review` (GitHub 쓰기) |
| POST `/git/pr/merge` | `ember/node/src/api.rs:451` | `ember/node/src/git_prs.rs:624` | `gh pr view`, `gh pr merge` (GitHub 쓰기) |
| POST `/git/pr/create` | `ember/node/src/api.rs:454` | `ember/node/src/git_prs.rs:726` | `gh pr list`, `gh pr create` (GitHub 쓰기) |
| POST `/git/github` | `ember/node/src/api.rs:440` | `ember/node/src/git_github.rs:155` | `gh repo view`, `gh api user`, `gh pr list`, `gh run list` |

다른 모듈이 부르는 경로: 서버 `POST /api/projects/{name}/git/<op>` → 노드 `/git/<op>` 중계 (`ember/server/src/api/git.rs:126`). 클라이언트 `Api::git_merge_state`, `git_stash_list`, `git_conflict` 등 (`ember/client/src/api.rs:1111`, `:1161`, `:1185`).

사용자에게 보이는 에러 메시지 (HTTP 본문, 대표만):

| 메시지 원문 | 위치 | 발생 조건 |
|---|---|---|
| `git 출력이 너무 커서 중단했습니다 (최대 {} KiB). 파일 하나씩 확인하세요.` | `ember/node/src/git.rs:207` | stdout 상한 초과 (413) |
| `{what} 명령을 찾을 수 없습니다. 설치되어 있는지 확인하세요.` | `ember/node/src/git.rs:319` | gh 미설치 (409) |
| `원격 저장소가 {}초 안에 응답하지 않아 중단했습니다 (네트워크 연결이나 인증 대기를 확인하세요).` | `ember/node/src/git.rs:358` | 네트워크 시간 초과 (504) |
| `korean_message` 표의 11개 문장 (예: `저장소 소유자가 현재 사용자와 달라 git이 접근을 거부했습니다 (safe.directory 설정이 필요합니다).`) | `ember/node/src/git.rs:396-437` | git 원문 키워드 매칭 (409) |
| `git 작업이 실패했습니다.` | `ember/node/src/git.rs:448-449` | 모르는 git 실패 |
| `작업 트리가 없는 저장소(bare)이거나 .git 안쪽입니다: {repo}` | `ember/node/src/git.rs:464` | bare 저장소 |
| `git 저장소가 아닙니다: {repo}` | `ember/node/src/git.rs:468` | 저장소 아님 (404) |
| `잘못된 {what} 값입니다: {v:?}` | `ember/node/src/git.rs:485` | `-` 시작 이름 등 (400) |
| `paths는 비어 있을 수 없습니다.` / `patch가 비어 있습니다.` / `커밋 요약이 비어 있습니다.` | `ember/node/src/git.rs:636`, `:664`, `:677` | 입력 누락 (400) |
| `커밋할 스테이지된 변경이 없습니다.` | `ember/node/src/git.rs:684` | 빈 커밋 (409) |
| `알 수 없는 원격 저장소입니다: {name} (설정된 원격: {})` | `ember/node/src/git.rs:746` | 설정 안 된 원격 (400) |
| `현재 브랜치의 업스트림은 {up}입니다. 그 원격으로 풀 하세요.` | `ember/node/src/git.rs:794` | 다른 원격에서 pull |
| `확인이 필요합니다.` | `ember/node/src/git_commit.rs:304`, `ember/node/src/git_merge.rs:103`, `ember/node/src/git_prs.rs:517` | `confirm` 누락 (400) |
| `진행 중인 git 작업이 있습니다. 먼저 끝내거나 중단하세요.` | `ember/node/src/git_commit.rs:186` | 진행 중 작업 (409) |
| `작업 중인 변경이 있어 되돌릴 수 없습니다. 먼저 커밋하거나 스태시하세요.` | `ember/node/src/git_commit.rs:314` | 더러운 작업 트리 (409) |
| `병합 커밋은 지원하지 않습니다.` | `ember/node/src/git_commit.rs:322` | 병합 커밋 cherry-pick (400) |
| `그런 커밋을 찾을 수 없습니다.` | `ember/node/src/git_commit.rs:180` | 없는 sha (404) |
| `커밋 SHA는 7자에서 40자의 16진수여야 합니다.` | `ember/node/src/git_commit.rs:160` | sha 형식 (400) |
| `failure_message` 표 5개 문장 | `ember/node/src/git_commit.rs:196-205` | FR-G15/G17 실패 |
| `진행 중인 병합이 없습니다.` / `충돌이 남아 있어 병합 커밋을 만들 수 없습니다.` / `병합을 취소하지 못했습니다. ...` | `ember/node/src/git_merge.rs:16-18` | 병합 작업 (409) |
| `그런 stash가 없습니다.` | `ember/node/src/git_stash.rs:68`, `:71` | 없는 stash 인덱스 (409) |
| `올바른 저장소 상대 경로가 아닙니다.` / `심볼릭 링크는 사용할 수 없습니다.` / `병합 충돌이 없는 경로입니다.` | `ember/node/src/git_conflict.rs:25`, `:33`, `:42` | 충돌 경로 검사 |
| `merge_gate` 사유 문장 8개 (예: `승인이 필요합니다. 리뷰어의 승인을 받아야 합니다.`) | `ember/node/src/git_prs.rs:179-198` | PR 병합 불가 (409 또는 목록의 `merge.reason`) |
| `gh_korean` 표 5개 문장 | `ember/node/src/git_prs.rs:246-254` | gh 실패 (409) |
| `풀 리퀘스트가 바뀌었습니다. 다시 불러온 뒤 병합하세요.` | `ember/node/src/git_prs.rs:639` | head sha 불일치 (409) |
| `이미 열린 풀 리퀘스트가 있습니다: #{}` | `ember/node/src/git_prs.rs:747` | 중복 PR (409) |
| `제목을 입력하세요.` / `내용을 입력하세요. 변경 요청과 댓글에는 본문이 필요합니다.` | `ember/node/src/git_prs.rs:730`, `:584` | 입력 누락 (400) |
| `GitHub에 로그인되어 있지 않습니다. 이 컴퓨터에서 gh auth login을 실행하세요.` | `ember/node/src/git_github.rs:77` | 카드 요약의 `error` 필드 |

## D. 데이터 모델·외부 연동 재료 (Phase 7 재료)

- DB 테이블: 없음. 파일 저장: 없음 (저장소 파일만 읽고 쓴다: `MERGE_MSG` 읽기 `ember/node/src/git_merge.rs:66-77`, 충돌 파일 읽기/쓰기 `ember/node/src/git_conflict.rs:47-61`, `:105-110`).
- 주요 DTO: `GitStatus`(`ember/node/src/git.rs:61`), `GitDiff`(`:88`), `GitLogResponse`(`ember/node/src/git_log.rs:20`), `GitCommitShowResponse`(`ember/node/src/git_commit.rs:49`), `GitBranchesResponse`(`ember/node/src/git_branches.rs:7`), `GitMergeState`(`ember/node/src/git_merge.rs:28`), `GitStashEntry`(`ember/node/src/git_stash.rs:29`), `GitConflict`(`ember/node/src/git_conflict.rs:14`), `GitPr`/`GitPrDetail`(`ember/node/src/git_prs.rs:73`, `:381`), `GitGithubResponse`(`ember/node/src/git_github.rs:36`). 직렬화 형태: serde 기본(snake_case 필드), enum은 `rename_all` 지정.
- 외부 연동:

| 대상 | 호출 위치 | 필요한 환경 변수 | 실패 처리 |
|---|---|---|---|
| `git` CLI | `ember/node/src/git.rs:257` (모든 git 작업), `:239` (`core.sshCommand` 조회) | 없음 (PATH의 git) | 종료 코드 → `GitError::Conflict` 한국어 문장, 미설치 → `Internal` "cannot run git" (`:321`) |
| `gh` CLI | `ember/node/src/git_prs.rs:289`, `ember/node/src/git_github.rs:100` | `EMBER_GH_BIN` (선택) | 미설치 409, 시간 초과 504 (목록) 또는 필드 null (카드), 로그아웃 감지 |
| 원격 git 서버 (ssh/https) | fetch/pull/push (`ember/node/src/git.rs:770-835`) | 사용자 credential helper, ssh 키 | 60초 시간 제한, 프롬프트 차단, 연결 실패 한국어 문장 |
| GitHub API (gh 경유) | `git_prs.rs`, `git_github.rs` | gh 자체 로그인 | 위와 같음 |
