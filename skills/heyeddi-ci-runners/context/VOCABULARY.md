# Vocabulary: HeyEddi CI runners

- **Spot (shipped)**: isolated VMs for sealed `pipeline:` and optional GHA overflow/always
- **GHA overflow / always**: workspace `gha_spot_mode`; hook `vars.HEYEDDI_RUNS_ON` → `heyeddi-linux`
- **Sealed pipeline job**: `eddi-ci.yaml` `pipeline:` unit; Check name `HeyEddi Runner: {job_id}`
- **Living contract**: policy feed for valid knobs (`load_policy_contract`)
- **assert_runners_claims**: blocks execution claims without Check/Spot evidence
