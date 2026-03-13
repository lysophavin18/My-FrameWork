# AI Assistant

## Purpose

The AI assistant helps teams interpret and prioritize findings directly inside the dashboard.

## Capabilities

- Explain vulnerability details in plain language
- Propose remediation actions
- Prioritize findings by risk and exploitability
- Generate executive summary text
- Suggest next recon actions in bug hunting mode

## Service Design

- Dedicated ai-assistant microservice
- OpenAI-compatible endpoint support
- Context injection from current scan/session data
- Per-user rate limiting
- Conversation history stored per user/session

## Configuration Fields

- AI_API_URL
- AI_API_KEY
- AI_MODEL
- AI_RATE_LIMIT_PER_MINUTE
- AI_MAX_TOKENS
- AI_TEMPERATURE

## Safe Usage Notes

- AI responses are advisory, not final authority.
- Validate all remediation commands in staging.
- Do not expose sensitive secrets in prompts.
