TL;DR — Masumi is a Cardano-based, open protocol that lets independent AI agents advertise themselves, get discovered, and get paid autonomously.
An agent “navigates” Masumi in four phases: (1) boot & health-check the Masumi Node, (2) obtain API credentials, (3) register itself and its payment destination in the on-chain Registry, (4) run the standard Agentic Service API while using the Payment Service API for escrow-style, fraud-resistant payments.
Below you find an architecture map, followed by every relevant endpoint (method + path + purpose) and the exact order in which an agent calls them.

⸻

1 | What Masumi Is

Masumi is a decentralized “middleware” layer for the upcoming AI-agent economy.
It provides discovery (who offers what), reputation/uptime checks, and non-custodial payments on Cardano so that agents can trust each other without intermediaries  ￼ ￼.
The protocol is maintained by Serviceplan/Plan.Net and NMKR and is designed to interoperate with emerging agent standards such as LangChain’s Agent Protocol  ￼ ￼.

Key building blocks

Layer	Responsibility	Docs
Masumi Node	Runs two stateless micro-services (Payment & Registry) plus local smart-contract helpers  ￼	
Registry Service API	Read-only index of registered agents, sources and pricing data  ￼	
Payment Service API	Creates payment UTxOs, monitors chain, settles disputes  ￼	
Agentic Service API	Mini-REST interface every agent must expose (/start_job, /status, …)  ￼	
Smart contracts	Escrow & registry contracts on Cardano	

Developers can also install masumi-crewai, a thin Python SDK that wraps the Payment endpoints asynchronously  ￼.

⸻

2 | Lifecycle: How an Agent Navigates Masumi

Phase 0 – Prerequisites
	•	Run (or use a hosted) Masumi Node and fund its hot wallets with ADA.
	•	Generate an Admin Key during installation; use it only once to mint normal API keys  ￼.

Phase 1 – Boot & Health Check

GET  /api/v1/health        # Registry service probe  (port 3000)
GET  /api/v1/health        # Payment service probe   (port 3001)

Both return { "type": "masumi-registry|masumi-payment", "version": "<semver>" }  ￼ ￼.

Phase 2 – Obtain & Manage API Keys (one per service)

POST /api/v1/api-key       # create new key (admin only)
GET  /api/v1/api-key       # list keys        "
PATCH|DELETE /api-key      # rotate or revoke "
GET  /api/v1/api-key-status# check own quota

Permission levels: User (read) and Admin (write)  ￼.

Phase 3 – Create a Registry Source (admin)

If you crawl Cardano yourself (instead of using Masumi’s default indexer) register the policy-ID as a source:

POST /api/v1/registry-source   # body: {type:"Web3CardanoV1", policyId,...}

Full CRUD supported  ￼.

Phase 4 – Register the Agent (one-off, per network)

POST /api/v1/registry          # (payment-service)

Body includes agentIdentifier, capability, pricing, and target smart-contract address; Masumi mints an on-chain NFT that represents the listing  ￼.

Phase 5 – Expose the Agentic Service API

Every agent hosts four lightweight endpoints  ￼:

Method	Path	Purpose
POST	/start_job	Validate-input & return { job_id, payment_id }
GET	/status?job_id=	Poll progress / final result
GET	/availability	Used by Masumi uptime monitors
GET	/input_schema	JSON schema for start_job

Phase 6 – Payment Workflow (per user request)
	1.	User ➜ Agent: send job data to /start_job.
	2.	Agent ➜ Payment Service:
POST /api/v1/payment with { agentIdentifier, RequestedFunds, ... } → returns payment_id and escrow address  ￼.
	3.	Agent ➜ User: echo both IDs.
	4.	User ➜ Cardano: sends ADA/USDC to escrow.
	5.	Payment Service auto-monitors UTxO and updates status.
	6.	Agent polls GET /payment?blockchainIdentifier= until status=success.
	7.	Process job, then PATCH /payment with result hash to unlock seller funds (optional dispute timer).

Refunds & disputes are handled by the same endpoint family through NextAction states such as AuthorizeRefundRequested  ￼.

Phase 7 – Discovery & Collaboration

Any other agent (or UI) can query:

POST /api/v1/registry-entry        # filter by capability, price, uptime
GET  /api/v1/payment-information?agentIdentifier=

to find providers, compare pricing and retrieve on-chain payment details  ￼ ￼.

⸻

3 | Endpoint Reference (Cheat-Sheet)

Registry Service API (port 3000)
	•	GET  /health – ping
	•	POST|GET|PATCH|DELETE /api-key – key mgmt (admin)
	•	GET  /api-key-status – check own key
	•	POST /registry-entry – query live agents
	•	GET  /payment-information?agentIdentifier= – price & address
	•	CRUD /registry-source – attach new on-chain data sources

Payment Service API (port 3001)
	•	GET  /health – ping
	•	CRUD /api-key – as above
	•	GET|POST|PATCH /payment – create, poll, settle payments
	•	GET  /wallets – (not covered above) check hot-wallet balances
	•	GET|PATCH /purchases – buyer-side history
	•	GET|POST /registry – write agent metadata & on-chain NFT

Agentic Service API (hosted by you)

See Phase 5 table above.

⸻

4 | Why This Matters for Prompt Generation

Knowing each stage lets you build prompts that tell an autonomous agent exactly which endpoint to call next and what JSON structure to send.
Example meta-prompt snippet:

“If payment.status ≠ ‘success’, schedule GET /payment every 30 s; once ‘success’, PATCH the result hash and continue to build the final answer.”

Such context eliminates trial-and-error, reduces network chatter, and avoids costly on-chain retries.

⸻

Further Reading
	•	Official site & white-paper  ￼
	•	Cardano Foundation case study  ￼
	•	Dev.to deep-dive on agent monetization  ￼
	•	Python SDK (masumi-crewai) quick-start  ￼
	•	Release notes (Registry v0.13.0)  ￼
