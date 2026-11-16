# Development guide

Start with [the current helper](../src/PersonalPlayback.rs) and [test.4 notes](manual-pip-test4.md). Regression tests are under [tests](../tests/); their DLLs must be restored or rebuilt before execution. Historical scripts and previous findings are preserved without changing their behavior.

## Working with the organized layout

Edit the current helper in `src/PersonalPlayback.rs` and tests in `tests/`. Historical packaging scripts expect the old `ytplus-analysis/` layout. The preparation tool creates an isolated workspace with those paths and overlays the organized source files:

```powershell
python tools/prepare_workspace.py --backup C:/path/YouTubePlus-development-backup.zip --output .work
cd .work
```

Download the backup ZIP from the private release first. Its SHA-256 is verified before extraction. Without `--backup`, only text sources are prepared; binary packaging inputs will be absent. The output folder must be empty. Never run archived publication or cleanup scripts merely to build.

The reference 5.2b4 IPA is restored under `inputs/`. Some historical scripts refer to its old Desktop path: update that path to the restored file before running them. Tools can also require installed Rust/LLVM, Python dependencies and Ghidra. This reorganization does not establish a fully portable, one-command build.

After preparation, old scripts work against copies inside `.work/ytplus-analysis/`. Copy intentional changes back to the corresponding organized file before committing. [workspace-map.json](../tools/workspace-map.json) records every source-to-workspace mapping.

## Validation and preserved evidence

- [Manual PiP tests](../tests/test_manual_pip.py)
- [Latest build report](../analysis/free-player-audit/manual-pip-test4-build.json)
- [Original test results](../analysis/free-player-audit/native-host-tests-test4.json)
- [Complete backup manifest](../releases/backup-manifest.json)

This change moves existing file blobs unchanged. No IPA was rebuilt or changed. The full backup and its checksums remain attached to the release; actual iOS PiP behavior still requires device testing.

## Native Duo watch-page helper (test.5)

The independent [DuoWatchLayout helper](../src/DuoWatchLayout.m) is built with Apple's UIKit SDK by the **Build Duo watch layout** GitHub Actions workflow. It uses the pinned test.4 IPA as its base. See [the implementation notes](duo-watch-test5.md), [UIKit fixture](../tests/DuoWatchFixture.m), and [release validation](../analysis/releases/test5-validation.json). This workflow avoids the historical workspace layout and produces a ready-to-sign IPA artifact. It does not execute the full YouTube IPA in the simulator.
