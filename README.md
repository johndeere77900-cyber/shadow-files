# Shadow Files

Shadow Files is a Python-based true-crime documentary production agent.

The system is designed around:

- evidence-first investigation
- source and claim tracking
- factual verification
- controlled story and script production
- media production
- quality control
- human approval
- Telegram-based control and notifications
- scheduled YouTube publication

## Phase 6 — Python Foundation

Phase 6 establishes the core software foundation before higher-level
features are added.

Current foundation components:

- configuration
- controlled case state machine
- immutable audit events
- unique job IDs
- authorization
- retry policy
- provider interfaces
- automated tests

## Publication Architecture

The initial production publication path is:

Shadow Files
→ completed video
→ complete YouTube metadata package
→ Telegram dashboard
→ human review
→ manual YouTube upload

This keeps final publication under human control.

Automated YouTube API publishing remains a future optional capability
and must be separately qualified before being enabled.

## Provider Architecture

External services are accessed through provider interfaces rather than
being embedded directly into the core system.

Planned provider categories include:

- research
- language model
- image
- voice
- video
- storage

This allows providers to be replaced without redesigning Shadow Files'
core architecture.

## Case Lifecycle

The planned primary lifecycle is:

IDEA
→ CASE_SELECTED
→ RESEARCHING
→ EVIDENCE_REVIEW
→ RESEARCH_VERIFIED
→ STORY_PLANNING
→ SCRIPT_DRAFT
→ SCRIPT_REVIEW
→ SCRIPT_APPROVED
→ SCENE_PLANNING
→ PRODUCTION
→ QC
→ HUMAN_APPROVAL
→ UPLOAD
→ SCHEDULED
→ PUBLISHED

Failure and intervention states are also supported.

## Testing

Foundation tests are located in:

`tests/test_foundation.py`

Run them with:

```bash
python -m unittest discover -s tests -v
