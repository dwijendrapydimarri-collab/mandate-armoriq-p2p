# Antigravity — Final Critical Submission Fix

The current `SUBMISSION-READINESS.md` is not yet accurate. Do not claim `SUBMISSION PACKAGE FULLY CLOSED & VERIFIED` until the two blockers below are closed with evidence.

## Blocker 1: No public GitHub or deployed link

`git remote -v` returns no remote. The hackathon requires a GitHub repository link or deployed link. A local Git repository is not sufficient.

Do one of the following:

1. Add the real GitHub remote and push the final feature-frozen repository, then record the public URL; or
2. Deploy the unified server and record a publicly accessible URL that a judge can open.

Never invent a URL. If credentials or deployment access are unavailable, mark the submission as blocked rather than claiming readiness.

Update `README.md`, `SUBMISSION-READINESS.md`, `ROUND2-SUBMISSION-DRAFT.md`, and Slide 7 of the PDF with the actual URL.

## Blocker 2: The MP4 has no audio stream

The current MP4 contains only an H.264 video stream. The portal requirement says the video must explain the project and how ArmorIQ is used. A silent screen recording is not sufficient evidence of explanation.

Create a new MP4 with:

- the browser workflow;
- a clear voiceover or subtitles explaining Mandate;
- an explicit ArmorIQ explanation: sealed authority, delegated agent scope, gateway authorization, and BLOCK before the payment tool;
- the local-adapter disclosure if cloud ArmorIQ is not connected;
- a total size below 100 MB;
- a final media check proving both `codec_type=video` and `codec_type=audio`, or a clearly readable subtitle track if the portal accepts subtitles instead of narration.

Use this concise narration:

> “Mandate is an autonomous procure-to-pay system governed by a sealed Authority Envelope. The CFO fixes approved payees and spending limits before the invoice is read. ArmorIQ authorizes delegated agent actions through the gateway. When an invoice proposes an unauthorized payee, the request is blocked before the payment tool runs, and the ledger remains unchanged. This prototype uses the local ArmorIQ contract adapter, clearly disclosed in the interface.”

Keep the video length appropriate for the portal and verify it actually contains the narration.

## Final verification

Run and record:

```text
git remote -v
ffprobe -v error -show_entries stream=codec_type,codec_name:format=duration,size -of default=noprint_wrappers=1 recordings/mandate_demo_recording.mp4
```

Confirm that the PDF exists, has exactly seven pages, and is under 10 MB. Preserve the 28 passing tests and the feature freeze. Then rewrite `SUBMISSION-READINESS.md` with one of these statuses:

- `SUBMISSION READY` only if a public URL and explanatory video are verified;
- `SUBMISSION BLOCKED` if either remains unavailable.

Do not add product features. This is artifact and access hardening only.
