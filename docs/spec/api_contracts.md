# API contracts

*One section per external API the app talks to. Each API
sits behind a **port** (the interface the app calls) and is reached through an
**adapter** (the code that calls the real service). Claude builds from this
file, so name the exact operations and data it needs.*

## <API name>

- **Purpose in the app:** <why we call it>
- **Access today:** available | **not yet available → build a fake adapter**
- **Docs:** <link>
- **Auth:** <API key / OAuth / none>. The key is read from the environment
  variable `<NAME>` in `.env`. It never appears in code, logs, or commits.
- **Port (what the app needs, in domain terms):**
  - `<operation>(<inputs>) → <result>`: <one line>
- **Calls behind it:** <HTTP method + endpoint, or SDK method>
- **Failure behaviour:** <what the app shows or does on timeout, rate limit, bad response>
- **Fake adapter (while unavailable):** <sample data it returns, and how it is switched off>
- **Limits & cost:** <rate limits, pricing, quotas worth knowing>
