# 모듈: tests (2) SPEC ID 역색인

[tests.md](tests.md)의 뒤쪽이다. 기능을 고친 뒤 어떤 테스트 파일을 돌려야 하는지 찾을 때 쓴다. 테스트 함수 이름의 접두사에서 뽑았다. 파일 안 `#[cfg(test)]` 단위 테스트는 들어 있지 않다.

| SPEC ID | 테스트 파일 |
|---|---|
| FR-A5 | `ember/server/tests/claude_code.rs`, `ember/server/tests/fr_s9_token_auth.rs`, `ember/server/tests/fr_t11_feed.rs`, `ember/server/tests/session_flow.rs` |
| FR-A6 | `ember/server/tests/fr_a6_1_harness_detect.rs` |
| FR-A9 | `ember/server/tests/members.rs` |
| FR-A10 | `ember/server/src/agents/acp/tests.rs`, `ember/server/tests/fr_a10_gemini.rs` |
| FR-A10A | `ember/server/tests/fr_a10_gemini.rs` |
| FR-A10B | `ember/server/src/agents/acp/tests.rs`, `ember/server/tests/fr_a10_gemini.rs` |
| FR-A10C | `ember/server/src/agents/acp/tests.rs`, `ember/server/tests/fr_a10_gemini.rs` |
| FR-A10D | `ember/server/src/agents/acp/tests.rs` |
| FR-A10F | `ember/server/src/agents/acp/tests.rs` |
| FR-C1 | `ember/server/tests/fr_c1_enrol.rs` |
| FR-C2 | `ember/server/tests/fr_c2_enrol_capture.rs`, `ember/server/tests/fr_c2_enrol_confirm.rs`, `ember/server/tests/fr_c2_enrol_door.rs`, `ember/server/tests/fr_c2_enrol_door_secrets_in_no_log.rs`, `ember/server/tests/fr_c2_enrol_node.rs`, `ember/server/tests/fr_c2_enrol_redeem.rs` |
| FR-E2 | `ember/app/tests/editor.rs` |
| FR-E6 | `ember/editor/tests/fr_e6_fixtures_stay_out_of_the_product.rs`, `ember/editor/tests/fr_e6_textmate_golden.rs`, `ember/editor/tests/fr_e6_textmate_interpreter.rs`, `ember/editor/tests/fr_e6_textmate_loader.rs`, `ember/editor/tests/fr_e6_textmate_perf.rs`, `ember/editor/tests/fr_e6_textmate_selector.rs`, `ember/editor/tests/fr_e6_textmate_session.rs`, `ember/editor/tests/fr_e6_textmate_tokens.rs`, `ember/editor/tests/textmate_real_grammars.rs` |
| FR-E7 | `ember/editor/tests/fr_e7_search_flow.rs` |
| FR-F3 | `ember/server/tests/fr_f_transfer.rs`, `ember/transfer/tests/session.rs` |
| FR-F4 | `ember/server/tests/fr_f_transfer.rs`, `ember/transfer/tests/session.rs` |
| FR-F5 | `ember/transfer/tests/session.rs` |
| FR-F9 | `ember/transfer/tests/session.rs` |
| FR-F10 | `ember/transfer/tests/session.rs` |
| FR-G1 | `ember/node/tests/git_api.rs` |
| FR-G2 | `ember/node/tests/git_api.rs` |
| FR-G3 | `ember/node/tests/git_api.rs` |
| FR-G4 | `ember/client/tests/git_flow.rs`, `ember/server/tests/git_relay.rs` |
| FR-G5 | `ember/node/tests/git_log.rs` |
| FR-G6 | `ember/node/tests/git_stash.rs` |
| FR-G7 | `ember/node/tests/git_conflict.rs` |
| FR-G8 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_prs.rs`, `ember/node/tests/git_prs_missing.rs`, `ember/server/tests/git_relay.rs` |
| FR-G9 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_branches.rs`, `ember/server/tests/git_relay.rs` |
| FR-G10 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_pr_ops.rs`, `ember/node/tests/git_prs_missing.rs` |
| FR-G11 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_pr_ops.rs`, `ember/server/tests/git_relay.rs` |
| FR-G12 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_pr_ops.rs` |
| FR-G13 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_github.rs`, `ember/node/tests/git_github_missing.rs`, `ember/server/tests/fr_g13_github_integration.rs` |
| FR-G14 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_commit.rs` |
| FR-G15 | `ember/node/tests/git_commit.rs`, `ember/node/tests/git_commit_identity.rs` |
| FR-G16 | `ember/client/tests/git_flow.rs`, `ember/node/tests/git_merge.rs` |
| FR-G17 | `ember/node/tests/git_merge.rs`, `ember/node/tests/git_merge_identity.rs` |
| FR-L4 | `ember/server/tests/projects_search.rs` |
| FR-L7 | `ember/server/tests/fr_w4_ide_computers.rs` |
| FR-L9 | `ember/server/tests/projects_search.rs` |
| FR-L20 | `ember/server/tests/fr_l20_agent_settings.rs` |
| FR-L26 | `ember/server/tests/fr_l26_project_patch.rs`, `ember/server/tests/fr_l26_project_profile.rs` |
| FR-L30 | `ember/app/tests/editor.rs` |
| FR-L31 | `ember/app/tests/editor.rs`, `ember/app/tests/find.rs`, `ember/app/tests/palette.rs` |
| FR-N1 | `ember/client/tests/letify_e2e_client.rs`, `ember/server/tests/letify_e2e_node.rs` |
| FR-N2 | `ember/hub/tests/letify_hub_config.rs`, `ember/server/tests/letify_e2e_relay.rs`, `ember/server/tests/letify_server_relay.rs`, `ember/transport/tests/letify_local.rs`, `ember/transport/tests/letify_relay.rs` |
| FR-N3 | `ember/server/tests/fr_n3_revocation_bound.rs`, `ember/server/tests/fr_n3_revocation_streams.rs`, `ember/server/tests/fr_w4_ose_relay.rs`, `ember/transport/tests/letify_gate.rs`, `ember/transport/tests/letify_relay.rs` |
| FR-N5 | `ember/transport/tests/default_backend.rs`, `ember/transport/tests/letify_local.rs` |
| FR-N6 | `ember/hub/tests/directory.rs`, `ember/transport/tests/gate.rs`, `ember/transport/tests/key.rs`, `ember/transport/tests/letify_gate.rs` |
| FR-N7 | `ember/server/tests/fr_n3_revocation_streams.rs`, `ember/server/tests/fr_n7_remote_device.rs` |
| FR-P3 | `ember/server/tests/fr_p3_ws_origin.rs`, `ember/server/tests/terms_relay.rs` |
| FR-P6 | `ember/server/tests/terms_relay.rs` |
| FR-P7 | `ember/node/tests/ports.rs`, `ember/server/tests/fr_p7_ports_relay.rs` |
| FR-S4 | `ember/server/tests/projects_search.rs` |
| FR-S5 | `ember/server/tests/projects_search.rs` |
| FR-S7 | `ember/server/tests/computers.rs` |
| FR-S8 | `ember/server/src/agents/acp/tests.rs`, `ember/server/tests/fr_l20_agent_settings.rs`, `ember/server/tests/fr_s8_wiring.rs`, `ember/server/tests/session_shim.rs` |
| FR-S9 | `ember/server/tests/fr_s9_token_auth.rs`, `ember/server/tests/fr_t12_channel_post.rs` |
| FR-S10 | `ember/server/tests/fr_s9_token_auth.rs` |
| FR-S11 | `ember/client/tests/channels_auth.rs` |
| FR-T9 | `ember/server/tests/a2a_terminal.rs` |
| FR-T10 | `ember/server/tests/fr_t10_channels.rs` |
| FR-T11 | `ember/server/tests/fr_s9_token_auth.rs`, `ember/server/tests/fr_t11_feed.rs`, `ember/server/tests/fr_t14_guest_door.rs` |
| FR-T12 | `ember/server/tests/fr_t12_channel_post.rs`, `ember/server/tests/fr_t12_delivery.rs`, `ember/server/tests/fr_t12_mcp_channel_post.rs`, `ember/server/tests/fr_t12_mentions.rs` |
| FR-T13 | `ember/server/tests/fr_t12_delivery.rs`, `ember/server/tests/fr_t12_mentions.rs` |
| FR-T14 | `ember/server/tests/fr_t14_guest_access.rs`, `ember/server/tests/fr_t14_guest_door.rs`, `ember/server/tests/fr_t14_guest_door_characterization.rs`, `ember/server/tests/fr_t14_guest_door_guard_matrix.rs`, `ember/server/tests/fr_t14_guest_door_logs.rs`, `ember/server/tests/fr_t14_guest_door_order.rs`, `ember/server/tests/fr_t14_guest_door_status.rs`, `ember/server/tests/fr_t14_guest_hardening.rs`, `ember/server/tests/fr_t14_guest_join_page.rs`, `ember/server/tests/fr_t14_guest_limits.rs`, `ember/server/tests/fr_t14_invites.rs`, `ember/server/tests/fr_w4_ose_relay.rs` |
| FR-T15 | `ember/server/tests/fr_t14_guest_access.rs`, `ember/server/tests/fr_t15_attribution.rs`, `ember/server/tests/fr_t17_allowance.rs` |
| FR-T16 | `ember/server/tests/fr_t10_channels.rs`, `ember/server/tests/fr_t15_attribution.rs`, `ember/server/tests/fr_t16_jsonl.rs` |
| FR-T17 | `ember/server/tests/fr_t17_allowance.rs`, `ember/server/tests/fr_t17_allowance_hardening.rs` |
| FR-U6 | `ember/server/tests/fr_u6_agy_proxy.rs`, `ember/server/tests/fr_u6_codex_proxy.rs`, `ember/server/tests/members.rs` |
| FR-U7 | `ember/server/tests/fr_u7_usage.rs` |
| FR-W4 | `ember/server/tests/fr_w4_fs_relay.rs`, `ember/server/tests/fr_w4_local_node_denied.rs`, `ember/server/tests/fr_w4_local_terms.rs`, `ember/server/tests/fr_w4_ose_data_dir.rs`, `ember/server/tests/fr_w4_ose_relay.rs`, `ember/server/tests/fr_w4_ose_token_dir.rs` |
| FR-X1 | `ember/node/tests/policy_denied.rs` |
| FR-X3 | `ember/server/tests/computers.rs` |
| FR-X6 | `ember/server/tests/fr_x6_egress.rs` |
| FR-X7 | `ember/node/tests/node_api.rs`, `ember/server/tests/fr_x7_metrics_relay.rs` |
| NFR-L2 | `ember/app/tests/no_webview.rs` |
| NFR-N1 | `ember/transport/tests/bench_harness_test.rs`, `ember/transport/tests/letify_perf.rs` |
| NFR-V1 | `ember/server/tests/no_api_version.rs` |
