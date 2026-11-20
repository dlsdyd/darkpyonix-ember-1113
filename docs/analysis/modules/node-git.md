# 모듈: node-git

- 경로: `ember/node/src/git.rs`, `ember/node/src/git_*.rs` (modules.md 정규식 `^ember/node/src/git`)
- 규모: 파일 9개 / 약 2,958줄
- 레이어: 비즈니스 로직
- 한 줄 책임: 노드 HTTP API의 `/git/*` 요청을 받아 그 컴퓨터의 `git`, `gh` CLI를 안전하게(프롬프트 없음, 시간 제한, 출력 상한) 실행하고 결과를 JSON DTO로 바꾼다.
- 의존하는 모듈: [node](node.md) (`crate::policy::PathPolicy`, `ember/node/src/git.rs:36`)
- 이 모듈을 쓰는 모듈: [node](node.md) (`ember/node/src/api.rs`, `ember/node/src/lib.rs:35-36`). 서버는 `/api/projects/{name}/git/<op>`를 본문 그대로 노드 `/git/<op>`로 중계만 한다 (`ember/server/src/api/git.rs:1-29`, `:126`), 즉 [server-api](server-api.md)가 HTTP로 간접 사용한다. [client](client.md)는 같은 DTO를 자체 정의해 쓴다 (`ember/client/src/api.rs:325`, `:624`, `:632`).

## 모듈 구조: `#[path]`로 묶은 하위 모듈

`git.rs`가 부모 모듈이고, 나머지 일곱 파일은 `#[path = "..."]` 속성으로 `git`의 하위 모듈로 선언된다 (`ember/node/src/git.rs:14-27`). 파일은 `src/` 바로 아래에 평평하게 놓여 있지만 Rust 경로로는 `crate::git::git_branches`, `crate::git::git_commit` 같은 형태가 된다. 그래서 하위 파일은 `use super::{finish, open, run, ...}`으로 `git.rs`의 비공개(`fn`, `struct Out`) 헬퍼를 직접 쓴다 (`ember/node/src/git_branches.rs:3`, `ember/node/src/git_commit.rs:8`, `ember/node/src/git_github.rs:14`, `ember/node/src/git_prs.rs:12`).

| 파일 | Rust 경로 | 선언 위치 |
|---|---|---|
| `git_branches.rs` | `crate::git::git_branches` | `ember/node/src/git.rs:14-15` |
| `git_commit.rs` | `crate::git::git_commit` | `ember/node/src/git.rs:16-17` |
| `git_github.rs` | `crate::git::git_github` | `ember/node/src/git.rs:18-19` |
| `git_log.rs` | `crate::git::git_log` | `ember/node/src/git.rs:20-21` |
| `git_merge.rs` | `crate::git::git_merge` | `ember/node/src/git.rs:22-23` |
| `git_prs.rs` | `crate::git::git_prs` | `ember/node/src/git.rs:24-25` |
| `git_stash.rs` | `crate::git::git_stash` | `ember/node/src/git.rs:26-27` |
| `git_conflict.rs` | `crate::git_conflict` (예외: 크레이트 최상위 모듈) | `ember/node/src/lib.rs:36` |

`git_conflict.rs`만 `lib.rs`에서 별도 최상위 모듈로 선언되어 `crate::git::{self, ...}`의 공개 함수만 쓴다 (`ember/node/src/git_conflict.rs:6`). 같은 디렉터리의 같은 접두사 파일인데 선언 방식이 둘이라 혼동하기 쉽다.

## 공통 실행기와 안전 장치

모든 git 호출은 `run`/`run_net` → `run_with` → `exec_cmd`를 거친다 (`ember/node/src/git.rs:228-291`, `:309-364`).

| 장치 | 위치 | 내용 |
|---|---|---|
| 환경 | `ember/node/src/git.rs:262-278` | `-c core.quotepath=false`, `LC_ALL=C`, `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`, `GIT_EDITOR=true`, `GIT_SEQUENCE_EDITOR=true`, `SSH_ASKPASS_REQUIRE=never`, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_INDEX_FILE` 제거, `kill_on_drop` |
| 리터럴 pathspec | `ember/node/src/git.rs:281-283` | `GIT_LITERAL_PATHSPECS=1`, 단 `stash push`는 제외 (git 2.43 버그 회피) |
| ssh 배치 모드 | `ember/node/src/git.rs:287-289` | 네트워크 작업이고 `GIT_SSH_COMMAND`가 없으면 `core.sshCommand`(또는 `ssh`)에 `-o BatchMode=yes`를 붙인다 |
| 시간 제한 | `ember/node/src/git.rs:186-193`, `:350-363` | 네트워크 작업만 `network_timeout()`(기본 60초). 넘으면 프로세스 그룹 전체 SIGKILL 후 `GitError::Timeout` |
| 출력 상한 | `ember/node/src/git.rs:197-203`, `:220-226`, `:338-341` | stdout `max_output()`(기본 8 MiB), stderr 1 MiB. 넘으면 kill, `truncated` |
| 프로세스 그룹 | `ember/node/src/git.rs:312-315`, `:294-305` | unix에서 네트워크 작업은 `process_group(0)`, kill은 `libc::kill(-pid)`. 비 unix는 그룹 kill이 빈 함수 |
| 저장소 확인 | `ember/node/src/git.rs:454-472` | `PathPolicy::resolve_existing` 후 `rev-parse --is-inside-work-tree`. 저장소 아님은 `NotARepo`, bare나 dubious ownership은 `Conflict` |
| 이름 인자 검사 | `ember/node/src/git.rs:483-488` | 빈 값, `-`로 시작, NUL 포함 거부 (옵션 주입 방지) |
| 원격 이름 제한 | `ember/node/src/git.rs:732-750` | `remote`는 `git remote`에 설정된 이름만 허용. URL을 넘겨 임의 주소로 접속시키는 것을 막는다 |

에러 변환: `finish`가 종료 코드 0이 아니면 `korean_message` 표를 거쳐 "한국어 문장\ngit 원문" 형태의 `GitError::Conflict`를 만든다 (`ember/node/src/git.rs:376-451`). FR-G14 이후 파일(`git_commit.rs`, `git_merge.rs`)은 반대로 git 원문을 응답에 넣지 않고 debug 로그로만 보낸다 (`run_k`, `ember/node/src/git_commit.rs:226-237`). 두 정책이 공존한다.

`GitError` → HTTP 상태 변환은 `ember/node/src/api.rs:321-328`: `Policy`→정책 에러, `NotARepo` 404, `Bad` 400, `Conflict` 409, `NotFound` 404, `Internal` 500, `Timeout` 504, `TooLarge` 413.

## HTTP 라우트 → 핸들러 → 이 모듈 함수

라우트 등록은 `ember/node/src/api.rs:172-212`. 모두 POST, JSON 본문에 `repo`(절대 경로)가 들어간다. "외부" 열은 실제로 실행하는 프로그램, "락"은 노드 `write_lock`을 잡는지, "confirm"은 본문에 `confirm: true`가 없으면 400 "확인이 필요합니다."인지를 뜻한다.

| 라우트 | 핸들러 (`api.rs`) | 호출 함수 | 외부 | 락 | confirm |
|---|---|---|---|---|---|
| `/git/log` | `git_log_handler` `:422` | `git_log::log` `ember/node/src/git_log.rs:40` | git | 아니오 | 아니오 |
| `/git/commit/show` | `git_commit_show_handler` `:942` | `git_commit::show` `ember/node/src/git_commit.rs:249` | git | 아니오 | 아니오 |
| `/git/revert` | `git_revert_handler` `:946` | `git_commit::revert` `ember/node/src/git_commit.rs:293` | git | 예 | 예 (`:303`) |
| `/git/cherry-pick` | `git_cherry_pick_handler` `:951` | `git_commit::cherry_pick` `ember/node/src/git_commit.rs:297` | git | 예 | 예 (`:303`) |
| `/git/merge` | `git_merge_state_handler` `:958` | `git_merge::state` `ember/node/src/git_merge.rs:94` | git | 아니오 | 아니오 |
| `/git/merge/abort` | `git_merge_abort_handler` `:962` | `git_merge::abort` `ember/node/src/git_merge.rs:107` | git | 예 | 예 (`:108`) |
| `/git/merge/commit` | `git_merge_commit_handler` `:967` | `git_merge::commit` `ember/node/src/git_merge.rs:122` | git | 예 | 예 (`:123`) |
| `/git/branches` | `git_branches_handler` `:428` | `git_branches::list` `ember/node/src/git_branches.rs:106` | git | 아니오 | 아니오 |
| `/git/prs` | `git_prs_handler` `:434` | `git_prs::list` `ember/node/src/git_prs.rs:317` | gh | 아니오 | 아니오 |
| `/git/github` | `git_github_handler` `:440` | `git_github::summarize` `ember/node/src/git_github.rs:155` | gh | 아니오 | 아니오 |
| `/git/pr` | `git_pr_handler` `:445` | `git_prs::detail` `ember/node/src/git_prs.rs:534` | gh | 아니오 | 아니오 |
| `/git/pr/review` | `git_pr_review_handler` `:448` | `git_prs::review` `ember/node/src/git_prs.rs:568` | gh | 아니오 | 예 (`:569`) |
| `/git/pr/merge` | `git_pr_merge_handler` `:451` | `git_prs::merge` `ember/node/src/git_prs.rs:624` | gh | 아니오 | 예 (`:625`) |
| `/git/pr/create` | `git_pr_create_handler` `:454` | `git_prs::create` `ember/node/src/git_prs.rs:726` | gh | 아니오 | 예 (`:727`) |
| `/git/status` | `git_status` `:459` | `git::status` `ember/node/src/git.rs:497` | git | 아니오 | 아니오 |
| `/git/diff` | `git_diff` `:463` | `git::diff` `ember/node/src/git.rs:605` | git | 아니오 | 아니오 |
| `/git/stage` | `git_stage` `:467` | `git::stage` `ember/node/src/git.rs:641` | git | 예 | 아니오 |
| `/git/unstage` | `git_unstage` `:473` | `git::unstage` `ember/node/src/git.rs:649` | git | 예 | 아니오 |
| `/git/apply` | `git_apply` `:479` | `git::apply` `ember/node/src/git.rs:662` | git | 예 | 아니오 |
| `/git/commit` | `git_commit` `:485` | `git::commit` `ember/node/src/git.rs:675` | git | 예 | 아니오 |
| `/git/checkout` | `git_checkout` `:490` | `git::checkout` `ember/node/src/git.rs:702` | git | 예 | 아니오 |
| `/git/branch` | `git_branch` `:496` | `git::branch` `ember/node/src/git.rs:708` | git | 예 | 아니오 |
| `/git/fetch` | `git_fetch` `:502` | `git::fetch` `ember/node/src/git.rs:770` | git (네트워크) | 아니오 | 아니오 |
| `/git/pull` | `git_pull` `:506` | `git::pull_fetch` `ember/node/src/git.rs:779` (락 없이), `git::pull_merge` `:805` (락 안에서) | git (네트워크) | 병합 단계만 | 아니오 |
| `/git/push` | `git_push` `:515` | `git::push` `ember/node/src/git.rs:822` | git (네트워크) | 아니오 | 아니오 |
| `/git/conflicts` | `git_conflicts` `:519` | `git::conflicts` `ember/node/src/git.rs:837` | git | 아니오 | 아니오 |
| `/git/stash/list` | `git_stash_list` `:524` | `git_stash::list` `ember/node/src/git_stash.rs:36` | git | 아니오 | 아니오 |
| `/git/stash/push` | `git_stash_push` `:528` | `git_stash::push` `ember/node/src/git_stash.rs:52` | git | 예 | 아니오 |
| `/git/stash/apply` | `git_stash_apply` `:534` | `git_stash::change(.., Apply)` `ember/node/src/git_stash.rs:64` | git | 예 | 아니오 |
| `/git/stash/pop` | `git_stash_pop` `:540` | `git_stash::change(.., Pop)` `ember/node/src/git_stash.rs:64` | git | 예 | 아니오 |
| `/git/stash/drop` | `git_stash_drop` `:546` | `git_stash::change(.., Drop)` `ember/node/src/git_stash.rs:64` | git | 예 | 아니오 |
| `/git/conflict` | `git_conflict` `:554` | `git_conflict::conflict` `ember/node/src/git_conflict.rs:47` | git + 파일 읽기 | 아니오 | 아니오 |
| `/git/resolve` | `git_resolve` `:558` | `git_conflict::resolve` `ember/node/src/git_conflict.rs:105` | 파일 쓰기 + git add | 예 | 아니오 |

`gh`를 쓰는 라우트는 여섯 개(`/git/prs`, `/git/github`, `/git/pr`, `/git/pr/review`, `/git/pr/merge`, `/git/pr/create`)이고 모두 락을 잡지 않는다 (`ember/node/src/api.rs:433-457` 주석 "holds no lock").

`confirm: true`가 필요한 작업: revert, cherry-pick, merge abort, merge commit, PR review, PR merge, PR create (7개). stash drop, checkout, commit amend 같은 다른 파괴적 작업은 confirm 없이 실행된다.

## 공개 인터페이스 (다른 모듈이 쓰는 것)

| 이름 | 종류 | 위치 | 설명 |
|---|---|---|---|
| `GitError` | enum | `ember/node/src/git.rs:156` | 8가지 에러. `api.rs:321-328`이 HTTP로 변환 |
| `GitRepoRequest` 외 요청/응답 DTO | struct | `ember/node/src/git.rs:43-150` | `api.rs` 핸들러의 `Json<..>` 타입 |
| `status`, `diff`, `stage`, `unstage`, `apply`, `commit`, `checkout`, `branch`, `fetch`, `pull_fetch`, `pull_merge`, `push`, `conflicts` | async fn | `ember/node/src/git.rs:497-841` | `api.rs` 핸들러가 호출 |
| `network_timeout`, `max_output`, `NETWORK_TIMEOUT_SECS`, `MAX_OUTPUT_BYTES` | fn/const | `ember/node/src/git.rs:179-203` | `git_conflict.rs:57-59`와 테스트가 사용 |
| `korean_message` | fn | `ember/node/src/git.rs:393` | 테스트(`ember/node/tests/git_api.rs`)만 사용 |
| `worktree_root` | `pub(crate)` fn | `ember/node/src/git.rs:475` | `git_conflict.rs:27`, `:108` |
| `git_log::log`, `git_branches::list`, `git_commit::{show, revert, cherry_pick}`, `git_merge::{state, abort, commit}`, `git_stash::{list, push, change}`, `git_prs::{list, detail, review, merge, create}`, `git_github::summarize`, `git_conflict::{conflict, resolve}` | async fn | 각 파일 | `api.rs` 핸들러 |
| `git_prs::{check_class, parse_prs, parse_detail, merge_gate}` | fn | `ember/node/src/git_prs.rs:160`, `:235`, `:503`, `:176` | 통합 테스트(`ember/node/tests/git_prs.rs`)가 사용 |

## 파일별 요약

### `ember/node/src/git.rs` (약 841줄)
- **목적:** FR-G1~G3. 상태, 스테이징, 커밋, 브랜치, 원격 작업과 공통 실행기. 하위 모듈 선언.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `GitStatus`, `GitFile` | struct | 52, 61 | porcelain v2 상태. `index`/`worktree`는 한 글자, 추적 안 된 파일은 `?`,`?` |
  | `GitError` | enum | 156 | 에러 분류 |
  | `run_with` | fn | 256 | git 명령 조립 (환경 변수, pathspec, ssh) |
  | `exec_cmd` | fn | 309 | git과 gh가 같이 쓰는 실행기 (상한, 시간 제한, 그룹 kill) |
  | `korean_message`, `describe` | fn | 393, 444 | git 원문 → 한국어 문장 표 |
  | `open` | fn | 454 | 정책 확인 + 작업 트리 확인 |
  | `status` | fn(pub) | 497 | `status --porcelain=v2 --branch -z --untracked-files=all` 파싱 + 브랜치 목록 + `FETCH_HEAD` mtime |
  | `diff` | fn(pub) | 605 | 단일 파일, staged, 또는 `include_untracked`로 추적 안 된 파일까지 `--no-index` 패치 |
  | `unstage` | fn(pub) | 649 | HEAD 없으면 `rm --cached`, 있으면 `reset -q` |
  | `commit` | fn(pub) | 675 | 메시지를 stdin(`-F -`)으로. amend 아니면 `diff --cached --quiet`로 빈 커밋 거부 |
  | `pull_fetch`/`pull_merge` | fn(pub) | 779, 805 | 풀을 네트워크 단계와 `merge --ff-only @{u}` 단계로 분리 |
  | `pull` | fn(pub) | 814 | 두 단계를 합친 함수. 저장소에서 호출처 없음 (아래 주의점) |
  | `push` | fn(pub) | 822 | upstream 없으면 `push -u <remote 또는 origin> HEAD` |
- **입력 → 출력:** `&PathPolicy`, 요청 DTO → `Result<응답 DTO, GitError>`.
- **의존:** `ember/node/src/policy.rs` (`PathPolicy`, `PolicyError`).
- **사용처:** `ember/node/src/api.rs:459-521`, `ember/node/src/git_conflict.rs`, 하위 모듈 전부.
- **부수효과:** `git` 프로세스 실행, 저장소 index/작업 트리/refs 변경, 네트워크(fetch/pull/push).
- **주의점:** `status`가 `FETCH_HEAD` mtime을 `std::fs::metadata`로 async 함수 안에서 동기 호출한다 (`:577`). 비 unix에서는 시간 초과 시 그룹 kill이 없어 git만 죽고 ssh, credential helper는 남을 수 있다 (`:304-305`). 파일 안에 테스트 없음.

### `ember/node/src/git_commit.rs` (약 452줄)
- **목적:** FR-G14 커밋 상세, FR-G15 revert와 cherry-pick. 다른 하위 모듈이 쓰는 헬퍼(`run_k`, `failure_message`, `NO_HOOKS`, `strip_controls`, `cut_chars`)도 여기 있다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MAX_FILES`, `MAX_BODY_CHARS` | const | 12, 14 | 파일 목록 500개, 본문 20,000자 |
  | `parse_name_status`, `parse_numstat`, `merge_files` | fn(pub) | 87, 114, 140 | `diff-tree -z` 출력 파서 |
  | `check_sha` | fn(pub) | 156 | 7~40자 16진수 |
  | `NO_HOOKS` | const | 190 | `-c core.hooksPath=/dev/null`, 사용자 훅을 끈다 |
  | `failure_message` | fn(pub) | 193 | git 원문 → 고정 한국어 문장 (원문은 응답에 안 넣음) |
  | `abort_outcome` | fn(pub) | 211 | abort 종료 코드로 "취소함"과 "취소 못 함" 구분 |
  | `run_k` | `pub(super)` fn | 227 | 실패 시 원문을 debug 로그로만 남기는 실행기 |
  | `in_progress` | fn | 240 | `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `MERGE_HEAD`, `sequencer`, `rebase-*` 존재 확인 |
  | `show` | fn(pub) | 249 | 메타 + name-status + numstat 결합 |
  | `act` | fn | 301 | revert/cherry-pick 공통: confirm → 진행 중 작업 거부 → 작업 트리 깨끗한지 → 실행 → 실패 시 abort 또는 `reset --hard` |
- **입력 → 출력:** `GitCommitShowRequest` → `GitCommitShowResponse`, `GitCommitActionRequest` → `GitCommitActionResponse { new_sha }`.
- **의존:** `git.rs`(`super`), `git_log.rs`(`ref_of`, `GitLogRef`).
- **사용처:** `ember/node/src/api.rs:942-955`, `ember/node/src/git_merge.rs:7`.
- **부수효과:** 커밋 생성, 실패 경로에서 `git reset --hard -q <before>` (`:347`).
- **주의점:** 실패 후 아무 작업도 멈춰 있지 않고 HEAD가 그대로면 `reset --hard`로 되돌린다 (`:345-351`). 사전에 추적 파일이 깨끗한지 확인하므로(`:312-315`) 사용자 변경을 지우지는 않지만, 이 순서를 바꾸면 데이터 손실이 난다. `ABORT_FAILED` 문구가 "되돌리기를 취소하지 못했습니다"로 고정되어 cherry-pick 실패에도 같은 말이 나간다 (`:187`, `:215`). `NO_HOOKS`의 `/dev/null`이 Windows에서 훅을 끄는지는 [확인 필요]. 테스트: 9개, 파서, sha 형식, 본문 자르기, 실패 문구 표, abort 결과, 제어 문자 제거를 검증한다.

### `ember/node/src/git_prs.rs` (약 794줄)
- **목적:** FR-G8 PR 목록, FR-G10 상세, FR-G11 리뷰와 병합, FR-G12 생성. 모두 `gh` CLI로 실행한다. 자격 증명은 그 컴퓨터의 `gh` 것이고 Ember는 비밀을 저장하지 않는다 (`:1-2`).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `DEFAULT_LIMIT`, `MAX_LIMIT`, `JSON_FIELDS` | const | 14-16 | 기본 30, 최대 200 |
  | `GitPr`, `GitPrMerge`, `GitPrChecks` | struct | 73, 66, 63 | 목록 항목 |
  | `classify` / `check_class` | fn | 140 / 160 | check run의 `conclusion`, status context의 `state`를 통과/실패/대기로 |
  | `merge_gate` | fn(pub) | 176 | FR-L19 병합 조건: 열림, 초안 아님, 충돌 없음, 실패/대기 체크 없음, 승인 있음 |
  | `run_gh` | fn | 286 | `EMBER_GH_BIN` 또는 `gh`, 프롬프트/색/업데이트 알림 끔, 네트워크 시간 제한 |
  | `gh_korean`, `gh_failure` | fn | 242, 272 | gh 원문 → 한국어 + 500자로 자른 원문 |
  | `detail` | fn(pub) | 534 | `gh pr view <n> --json DETAIL_FIELDS` |
  | `review` | fn(pub) | 568 | approve, request-changes, comment. 본문은 `--body=<값>` 한 인자로 |
  | `merge` | fn(pub) | 624 | 다시 읽어 `merge_gate` 확인, `head_sha` 일치 확인, `--match-head-commit=<sha>`로 병합 |
  | `valid_ref`, `branch_arg` | fn | 681, 698 | `check-ref-format` 규칙 흉내, `owner:branch` 허용 |
  | `create` | fn(pub) | 726 | 명시 head면 중복 PR 확인 후 `gh pr create --title= --body= ...` |
- **입력 → 출력:** 요청 DTO → `GitPrsResponse`, `GitPrDetail`, `GitPrReviewResponse`, `GitPrMergeResponse`, `GitPrCreateResponse`.
- **의존:** `git.rs`(`exec_cmd`, `network_timeout`, `open`, `too_large`).
- **사용처:** `ember/node/src/api.rs:434-456`.
- **부수효과:** `gh` 실행, GitHub에 리뷰 게시, PR 병합, PR 생성, `--delete-branch`면 원격 브랜치 삭제와 로컬 체크아웃 전환 가능 (`:621-623`).
- **주의점:** `--flag=value` 한 인자로 넘겨 `-`로 시작하는 값이 옵션으로 읽히지 않게 한다 (`:520-523`). `merge`는 `--admin`, `--auto`를 쓰지 않는다 (`:617-619`). `merge_gate`는 승인을 항상 요구해 리뷰가 필수가 아닌 저장소에서도 병합을 막는다 (`:195-199`). 앱에도 같은 이름의 별도 `merge_gate`가 있다 (`ember/app/src/ui/vcs.rs:292`). 테스트: 3개, 생성 URL 파싱, PR 번호 범위, 원문 자르기를 검증한다.

### `ember/node/src/git_github.rs` (약 246줄)
- **목적:** FR-G13 홈 GitHub 카드 요약. `gh`를 순서대로 호출해 저장소 이름, 기본 브랜치, 로그인 계정, 열린 PR 수, 리뷰 요청 수, 최근 CI 결과를 모은다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `PR_LIMIT`, `RUN_LIMIT` | const | 17, 19 | 100, 14 |
  | `GitGithubResponse` | struct | 36 | 필드마다 `Option`, `signed_out`, `error` |
  | `run_gh` | fn | 98 | `git_prs::run_gh`와 거의 같은 복사본. 시간 초과는 그 호출만의 실패로 처리 |
  | `map_run` | fn(pub) | 131 | `gh run list` 항목 → `CiRun` |
  | `count_review_requested` | fn(pub) | 145 | 계정 로그인이 리뷰 요청에 있는 PR 수 |
  | `summarize` | fn(pub) | 155 | `repo view` → `api user` → `pr list` → `run list` 순 실행 |
- **입력 → 출력:** `GitGithubRequest { repo }` → `GitGithubResponse`.
- **의존:** `git.rs`(`exec_cmd`, `network_timeout`, `open`).
- **사용처:** `ember/node/src/api.rs:440-442`.
- **부수효과:** `gh` 실행 최대 4회 (네트워크).
- **주의점:** 모듈 주석은 "Five calls"라 하지만 실제 호출은 4회다 (`:5` 대 `:176`, `:192`, `:202`, `:217`). 로그아웃이 감지되면 뒤 호출을 건너뛴다 (`:187-189`, `:196-198`). 테스트: 2개, 이름 정리와 CI 결과 매핑.

### `ember/node/src/git_branches.rs` (약 181줄)
- **목적:** FR-G9 로컬 브랜치 목록 (upstream 추적, 마지막 커밋, worktree 경로, 기본 브랜치 표시).
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `GitBranchInfo` | struct | 10 | 브랜치 한 개 |
  | `parse_track` | fn(pub) | 32 | `[ahead 2, behind 1]` 등 → (ahead, behind) |
  | `FORMAT` | const | 43 | `for-each-ref` 형식, 필드 구분자 U+001F, 제목은 마지막 |
  | `parse_lines` | fn(pub) | 47 | 줄마다 9필드 |
  | `fallback_default` | fn(pub) | 75 | `main`, 없으면 `master` |
  | `sort_branches` | fn(pub) | 80 | 현재 → 기본 → 최신 커밋 → 이름 |
  | `remote_default` | fn | 90 | `refs/remotes/<remote>/HEAD`, `origin` 우선 |
  | `list` | fn(pub) | 106 | 위를 합쳐 응답 |
- **입력 → 출력:** `GitRepoRequest` → `GitBranchesResponse`.
- **의존:** `git.rs`, `policy.rs`.
- **사용처:** `ember/node/src/api.rs:428-430`.
- **부수효과:** git 읽기만.
- **주의점:** 제목에 줄바꿈이 없다는 가정에 기대어 줄 단위로 나눈다 (`:45-46`). 테스트: 4개, track 파서, 줄 분할, 기본 브랜치 대체, 정렬 순서.

### `ember/node/src/git_merge.rs` (약 160줄)
- **목적:** FR-G16 병합 상태, FR-G17 병합 취소와 병합 커밋.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `MAX_NAME_CHARS` | const | 12 | 브랜치 이름 100자 |
  | `GitMergeState` | struct | 28 | `in_progress`, `from`, `into`, `conflict_files`, `can_commit` |
  | `merge_from` | fn(pub) | 44 | `MERGE_MSG` 첫 줄의 따옴표 안 이름 |
  | `clean_name` | fn(pub) | 51 | 제어 문자 제거, 100자 |
  | `merging` | fn | 62 | `MERGE_HEAD` 존재 |
  | `merge_source` | fn | 66 | `MERGE_MSG`(8 KiB까지) 실패 시 `name-rev MERGE_HEAD` |
  | `state`, `abort`, `commit` | fn(pub) | 94, 107, 122 | 상태, `merge --abort`, `commit --no-edit` |
- **입력 → 출력:** `GitRepoRequest`/`GitMergeActionRequest` → `GitMergeState`, `GitMergeAborted { ok }`, `GitCommitActionResponse`.
- **의존:** `git.rs`, `git_commit.rs`(`run_k`, `failure_message`, `NO_HOOKS` 등).
- **사용처:** `ember/node/src/api.rs:958-970`.
- **부수효과:** 병합 취소, 병합 커밋 생성.
- **주의점:** `git_github.rs:57`에도 `clean_name`이 있는데 동작이 다르다 (이쪽은 `None` 반환, 저쪽은 빈 문자열). 테스트: 2개, `merge_from`와 이름 정리.

### `ember/node/src/git_conflict.rs` (약 110줄)
- **목적:** FR-G7 충돌 파일을 블록(공통/충돌)으로 파싱하고, 해결된 내용을 써서 stage한다.
- **주요 심볼:**
  | 이름 | 종류 | 줄 | 설명 |
  |---|---|---|---|
  | `ConflictBlock` | enum | 17 | `Common { text }`, `Conflict { ours, theirs, ours_label, theirs_label }`, `kind` 태그 |
  | `target` | fn | 22 | 저장소 상대 경로 검사(정상 컴포넌트만), 경로 중간 심볼릭 링크 거부, 충돌 목록에 있는지 확인 |
  | `conflict` | fn(pub) | 47 | 파일을 `max_output()`까지 읽고 UTF-8 확인 후 `parse` |
  | `parse` | fn | 69 | `<<<<<<<`, diff3 base 마커(7개의 세로줄, 내용은 버림), `=======`, `>>>>>>>` 마커 해석. 닫히지 않은 마커는 공통 텍스트로 |
  | `resolve` | fn(pub) | 105 | 파일 쓰기 후 `git::stage` |
- **입력 → 출력:** `GitConflictRequest` → `GitConflict { blocks }`, `GitResolveRequest` → `()`.
- **의존:** `git.rs`(공개 함수만), `policy.rs`.
- **사용처:** `ember/node/src/api.rs:554-561`.
- **부수효과:** 작업 트리 파일 쓰기 (`tokio::fs::write`, `:107`), index 변경.
- **주의점:** 심볼릭 링크 검사(`:30-39`)와 실제 쓰기(`:107`) 사이에 시간 차가 있다 (TOCTOU). `resolve`는 `worktree_root`를 두 번 계산한다 (`target` 안 `:27`, `:108`). 파일 안에 테스트 없음 (통합 테스트 `ember/node/tests/git_conflict.rs`).

### 작은 파일

| 파일 | 줄 | 요약 |
|---|---|---|
| `ember/node/src/git_log.rs` | 89 | FR-G5 히스토리. `log --topo-order --decorate=full`을 U+001E/NUL/U+001F 구분 형식으로 읽어 `GitLogCommit` 목록으로 (`:40-78`). `limit` 최대 500, 기본 50 (`:6`, `:41-43`). HEAD 없는 빈 저장소는 빈 목록 (`:46-54`). `ref_of`는 `git_commit.rs`와 공유 (`:82`). 테스트 없음 |
| `ember/node/src/git_stash.rs` | 85 | FR-G6 stash. `list`는 `%gd%x00%gs%x00%cI` 형식 파싱 (`:36-50`), `push`는 `--include-untracked`, `-m` 지원 (`:52-62`), `change`는 인덱스가 실제 목록에 있는지 확인 후 `stash apply/pop/drop stash@{n}` (`:64-85`). `index`는 `serde_json::Value`로 받아 숫자가 아니면 409 (`ember/node/src/git_stash.rs:18`, `:66-68`). 테스트 없음 |

## 이 모듈을 수정할 때 주의할 점
- 새 git 하위 파일을 만들면 `git.rs`에 `#[path]` 선언을 추가해야 `super::` 헬퍼를 쓸 수 있다 (`ember/node/src/git.rs:14-27`). `git_conflict.rs`처럼 `lib.rs`에 두면 공개 함수만 쓸 수 있다.
- 에러 문구 정책이 두 가지다. FR-G1~G13은 한국어 + git/gh 원문 (`git.rs:443-451`, `git_prs.rs:272-282`), FR-G14 이후는 한국어만 (`git_commit.rs:192-207`). 앱이 원문 유무에 기대는지 [확인 필요] (`ember/app/src/ui/vcs.rs:4370` 테스트 이름이 "korean message from the node is not wrapped again").
- `gh` 실행기는 두 벌이다 (`git_prs.rs:286`, `git_github.rs:98`). 환경 변수를 바꿀 때 둘 다 바꿔야 한다. 한국어 표도 두 벌이다 (`git_prs.rs:242`, `git_github.rs:72`).
- 락 정책: 작업 트리나 index를 바꾸는 라우트만 `write_lock`을 잡는다. 네트워크 작업은 오래 걸려 잡지 않는다 (`ember/node/src/api.rs:417-419`). 그런데 `/git/pr/merge`에 `delete_branch`를 주면 gh가 로컬 체크아웃을 바꿀 수 있는데도 락이 없다 (`git_prs.rs:621-623`, `api.rs:451-453`).
- 응답 DTO는 `ember/client/src/api.rs`에 별도로 다시 정의되어 있다. 필드를 바꾸면 클라이언트도 바꿔야 한다.
- 환경 변수 `EMBER_GIT_NETWORK_TIMEOUT_SECS`, `EMBER_GIT_MAX_OUTPUT_BYTES`, `EMBER_GH_BIN`은 테스트용이지만 운영 노드에서도 그대로 읽힌다.
