# 순환 의존 (Phase 3)

> 파일 단위 `use` 간선의 강한 연결 요소(SCC) 중 크기 2 이상. `mod x;` 선언 간선은 뺐다 (Rust에서 부모가 자식을 선언하고 자식이 `super::`를 쓰는 것은 정상 구조라서).
> Rust는 같은 크레이트 안의 모듈 순환을 허용하므로 컴파일 오류가 아니다. 다만 순환이 크면 한 파일을 고칠 때 영향 범위가 넓어진다.

## C-01 (파일 56개)

- `ember/app/src/bridge.rs`
- `ember/app/src/demo.rs`
- `ember/app/src/editor_host.rs`
- `ember/app/src/ide.rs`
- `ember/app/src/model.rs`
- `ember/app/src/prefs.rs`
- `ember/app/src/server.rs`
- `ember/app/src/services.rs`
- `ember/app/src/terminal_stream.rs`
- `ember/app/src/ui/agents.rs`
- `ember/app/src/ui/characters.rs`
- `ember/app/src/ui/coexist.rs`
- `ember/app/src/ui/cr/add_computer.rs`
- `ember/app/src/ui/cr/agents.rs`
- `ember/app/src/ui/cr/channel_owner.rs`
- `ember/app/src/ui/cr/channels.rs`
- `ember/app/src/ui/cr/characters.rs`
- `ember/app/src/ui/cr/characters_screen.rs`
- `ember/app/src/ui/cr/compat.rs`
- `ember/app/src/ui/cr/components.rs`
- `ember/app/src/ui/cr/conversation.rs`
- `ember/app/src/ui/cr/files.rs`
- `ember/app/src/ui/cr/home.rs`
- `ember/app/src/ui/cr/ko.rs`
- `ember/app/src/ui/cr/launcher.rs`
- `ember/app/src/ui/cr/monitor.rs`
- `ember/app/src/ui/cr/new_channel.rs`
- `ember/app/src/ui/cr/new_session.rs`
- `ember/app/src/ui/cr/notice.rs`
- `ember/app/src/ui/cr/project.rs`
- `ember/app/src/ui/cr/routines.rs`
- `ember/app/src/ui/cr/search.rs`
- `ember/app/src/ui/cr/session.rs`
- `ember/app/src/ui/cr/settings.rs`
- `ember/app/src/ui/cr/shell.rs`
- `ember/app/src/ui/cr/theme.rs`
- `ember/app/src/ui/cr/vcs.rs`
- `ember/app/src/ui/editor.rs`
- `ember/app/src/ui/editor_scm.rs`
- `ember/app/src/ui/editor_search.rs`
- `ember/app/src/ui/editor_workbench.rs`
- `ember/app/src/ui/enrol_flow.rs`
- `ember/app/src/ui/files.rs`
- `ember/app/src/ui/fonts.rs`
- `ember/app/src/ui/home.rs`
- `ember/app/src/ui/mod.rs`
- `ember/app/src/ui/monitor.rs`
- `ember/app/src/ui/palette.rs`
- `ember/app/src/ui/project.rs`
- `ember/app/src/ui/question.rs`
- `ember/app/src/ui/routines.rs`
- `ember/app/src/ui/safe_area.rs`
- `ember/app/src/ui/session.rs`
- `ember/app/src/ui/shell.rs`
- `ember/app/src/ui/term_pane.rs`
- `ember/app/src/ui/vcs.rs`

## C-02 (파일 40개)

- `ember/server/src/a2a/api.rs`
- `ember/server/src/a2a/channel.rs`
- `ember/server/src/a2a/mention.rs`
- `ember/server/src/a2a/mod.rs`
- `ember/server/src/a2a/team.rs`
- `ember/server/src/a2a/terminal.rs`
- `ember/server/src/accounts/mod.rs`
- `ember/server/src/accounts/schema.rs`
- `ember/server/src/accounts/secrets.rs`
- `ember/server/src/agents/antigravity.rs`
- `ember/server/src/agents/codex.rs`
- `ember/server/src/agents/proc.rs`
- `ember/server/src/auth.rs`
- `ember/server/src/browser/agent.rs`
- `ember/server/src/browser/egress.rs`
- `ember/server/src/channels/allowance.rs`
- `ember/server/src/channels/api.rs`
- `ember/server/src/channels/guest.rs`
- `ember/server/src/channels/invites.rs`
- `ember/server/src/channels/jsonl.rs`
- `ember/server/src/channels/mod.rs`
- `ember/server/src/chatgpt/mod.rs`
- `ember/server/src/chatgpt/oauth.rs`
- `ember/server/src/chatgpt/schema.rs`
- `ember/server/src/chatgpt/store.rs`
- `ember/server/src/computers/enrol.rs`
- `ember/server/src/computers/mod.rs`
- `ember/server/src/computers/mount.rs`
- `ember/server/src/computers/schema.rs`
- `ember/server/src/devices/mod.rs`
- `ember/server/src/devices/schema.rs`
- `ember/server/src/fork.rs`
- `ember/server/src/hub/mod.rs`
- `ember/server/src/hub/schema.rs`
- `ember/server/src/members.rs`
- `ember/server/src/projects/mod.rs`
- `ember/server/src/schedules/mod.rs`
- `ember/server/src/session.rs`
- `ember/server/src/store.rs`
- `ember/server/src/transport.rs`

## C-03 (파일 17개)

- `ember/node/src/api.rs`
- `ember/node/src/client.rs`
- `ember/node/src/config.rs`
- `ember/node/src/egress.rs`
- `ember/node/src/enrol.rs`
- `ember/node/src/enrol_cli.rs`
- `ember/node/src/envinfo.rs`
- `ember/node/src/exec.rs`
- `ember/node/src/exec_server.rs`
- `ember/node/src/fs.rs`
- `ember/node/src/hub.rs`
- `ember/node/src/jobs.rs`
- `ember/node/src/metrics.rs`
- `ember/node/src/ports.rs`
- `ember/node/src/proto.rs`
- `ember/node/src/term/mod.rs`
- `ember/node/src/transport.rs`

## C-04 (파일 5개)

- `ember/server/src/door/config.rs`
- `ember/server/src/door/harden.rs`
- `ember/server/src/door/limits.rs`
- `ember/server/src/door/mod.rs`
- `ember/server/src/guest_door.rs`

## C-05 (파일 4개)

- `ember/editor-conn/src/document.rs`
- `ember/editor-conn/src/exthost.rs`
- `ember/editor-conn/src/rpc.rs`
- `ember/editor-conn/src/search.rs`

## C-06 (파일 3개)

- `ember/client/src/cache.rs`
- `ember/client/src/client.rs`
- `ember/client/src/state.rs`

## C-07 (파일 3개)

- `ember/editor/src/engine.rs`
- `ember/editor/src/fallback.rs`
- `ember/editor/src/session.rs`

## C-08 (파일 3개)

- `ember/server/src/computers/mount/fuse.rs`
- `ember/server/src/computers/mount/nfs.rs`
- `ember/server/src/computers/mount/remote_fs.rs`

## C-09 (파일 2개)

- `ember/client/src/api.rs`
- `ember/client/src/channels.rs`

## C-10 (파일 2개)

- `ember/editor-conn/src/connection.rs`
- `ember/editor-conn/src/protocol.rs`

## C-11 (파일 2개)

- `ember/editor/src/ids.rs`
- `ember/editor/src/widget.rs`

## C-12 (파일 2개)

- `ember/server/src/api/ide.rs`
- `ember/server/src/ose.rs`

## C-13 (파일 2개)

- `ember/editor/src/textmate/interpreter.rs`
- `ember/editor/src/textmate/selector.rs`

## C-14 (파일 2개)

- `ember/server/src/a2a/client.rs`
- `ember/server/src/a2a/mcp.rs`

## C-15 (파일 2개)

- `ember/transfer/src/mode.rs`
- `ember/transfer/src/session.rs`

## C-16 (파일 2개)

- `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/manager/EventStream.kt`
- `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/manager/ManagerClient.kt`

## C-17 (파일 2개)

- `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/notebook/NotebookService.kt`
- `extensions/intellij-darkpyonix/src/main/kotlin/dev/darkpyonix/intellij/notebook/NotebookSession.kt`

