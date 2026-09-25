# Shadow Files — Cloudflare Integration

This directory contains the Cloudflare integration layer for Shadow Files.

## Architecture

Telegram
→ Cloudflare
→ Shadow Files
→ Production
→ Final video
→ Cloudflare storage/delivery
→ Telegram

Cloudflare is responsible for:

- Telegram webhook/edge entry
- conversational request routing
- lightweight request interpretation
- secure communication with Shadow Files
- delivery coordination
- Cloudflare-side secrets and bindings

Shadow Files remains responsible for:

- investigation
- evidence management
- case memory
- story planning
- script production
- media production
- rendering
- quality control
- human approval
- publication workflow

## Current operating mode

The system is initially HUMAN-CONTROLLED.

Cloudflare must not:

- automatically publish videos
- automatically approve productions
- bypass human approval
- silently execute irreversible actions

Automation can be enabled later after the complete system has been tested,
stabilized, and explicitly trusted.

## Storage

Large production assets must not be treated as Worker source files.

Cloudflare R2 may be used as the object-storage layer for:

- completed videos
- thumbnails
- production assets
- delivery artifacts

## Repository integration

Cloudflare Workers Builds may be connected to the Shadow Files GitHub
repository so deployment can follow repository changes.

Cloudflare-specific code should remain isolated from the main Shadow Files
application until the integration has been tested.

## Security

Secrets must never be committed to GitHub.

Expected Cloudflare secrets include:

- Telegram bot token
- Shadow service authentication secret
- AI/provider credentials where applicable

Secrets must be configured through Cloudflare's secret/environment system.
