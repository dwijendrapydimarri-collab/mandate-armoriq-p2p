# Antigravity Prompt — Final Submission Gap Fix

The product is feature-frozen. Do not add product features. Complete only final submission hardening.

## Known status

- Backend/Judge suite: 28 tests passing.
- Frontend build: passes from `frontend/` with `npm run build`.
- Unified launcher: `python run.py --host 0.0.0.0 --port 8008`.
- Seven-slide PDF exists as `MANDATE-ROUND2-PRESENTATION.pdf`.
- The reported browser recording is a `.webp` in the hidden IDE workspace, not in the repository.
- No public deployed URL is currently recorded.

## Required actions

1. Run the unified launcher from a clean checkout and test:
   - `/`
   - `/docs`
   - `/api/health`
   - New Judge Scenario
   - CFO Setup
   - Mission Seal
   - custom untrusted invoice
   - Security Probe
   - Counterfactual Proof
   - unchanged ledger after BLOCK
2. Record the exact launch command and browser URL.
3. Copy the final browser recording into the repository or a clearly accessible submission location. Prefer MP4/H.264 or another format accepted by the submission portal; do not rely only on a hidden `.webp` path.
4. Confirm the video is under 100 MB and actually explains both the project and how ArmorIQ is used. Keep the local-adapter disclosure if cloud ArmorIQ is not connected.
5. Confirm `MANDATE-ROUND2-PRESENTATION.pdf` has exactly seven pages and is under 10 MB. Do not claim this unless measured.
6. Populate the final team identity everywhere:
   - STELLAR STACK
   - team-E657F05D7F45
   - AMRITA VISHWA VIDYAPEETHAM, NAGERCOIL
7. Add the final GitHub URL or public deployed URL to the README, PDF Slide 7, and submission draft. If there is no public URL, state that clearly and do not invent one.
8. Preserve the feature freeze and do not alter security behavior during artifact preparation.

Return a final `SUBMISSION-READINESS.md` with artifact paths, measured sizes, exact commands, URL(s), browser evidence, and remaining blockers. Do not mark the project fully submission-ready until the video is portable and a repository or deployed link is available.
