# Security Rules

- Never commit secrets. Real API keys, passwords, and tokens must never appear in code, config files, or git history.
- Read all configuration from environment variables. Nothing sensitive is hardcoded — see `.env.example` for the full list of variables the app needs.
- Hash API keys before storing them. Never store a raw customer-facing API key at rest; store a hash and compare hashes on lookup.
- Validate all external input. Anything coming from a request body, query param, header, or third-party API response (including Oxylabs and OpenAI) is untrusted until validated against a Pydantic model.
