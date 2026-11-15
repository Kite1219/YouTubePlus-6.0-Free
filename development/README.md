# Development archive

Our local helper sources, tests, package scripts and investigation records are browsable under `ytplus-analysis/`. This is not the original complete YouTube or YouTubePlus source project.

The release asset `YouTubePlus-development-backup.zip` preserves every local file from the work folder, including original input, extracted libraries, intermediate analysis, and final IPA. It also includes the supplied 5.2b4 reference IPA when available. `MANIFEST.json` records every file hash. Restore the archive into a workspace before running historical scripts. Some scripts contain original absolute Windows paths and require path adjustment, installed Rust/LLVM tools, Python dependencies or Ghidra. Host tests use mocked iOS APIs; on-device PiP remains unverified.

Latest helper: `ytplus-analysis/free-player-audit/PersonalPlayback.rs`. See `manual-pip-test4-notes.md` and `manual-pip-test4-build.json` in the same directory.

Backup SHA-256: `87bcd3fc3a3582d8c39da41d73e247ea20a5afe2758d87060ca137ee373c568c`
