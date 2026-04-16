# Azure Foundry

The live path in this repo uses Azure OpenAI for one thing only: rewriting fetched documents into denser knowledge records.

Everything else stays local:

- URL frontier construction
- canonicalization
- stable content hashing
- delta classification

That boundary is what keeps the system debuggable.

## Required Deployments

Minimum:

- one chat-capable deployment for extraction, for example `gpt-5-mini`

Useful but optional:

- one heavier reasoning deployment, for example `gpt-5.4`, if you add adjudication or review workflows later
- one embedding deployment, for example `text-embedding-3-small`, if you push exports straight into a vector index

## Environment

```bash
export CRAWL_TO_KNOWLEDGE_PROVIDER=azure
export AZURE_OPENAI_ENDPOINT="https://<resource>.openai.azure.com/"
export AZURE_OPENAI_API_KEY="<key>"
export AZURE_OPENAI_API_VERSION="2025-04-01-preview"
export AZURE_OPENAI_EXTRACT_DEPLOYMENT="gpt-5-mini"
```

Verify the resource has the deployment you expect:

```bash
az cognitiveservices account deployment list \
  --resource-group <resource-group> \
  --name <azure-openai-account>
```

Run the live demo:

```bash
uv run python scripts/run_live_demo.py
```

## Why `gpt-5-mini` Is The Default Here

This extractor is not writing prose for humans. It is writing dense records for downstream retrieval.

The useful model behavior is:

- keep concrete facts
- preserve operational limits and protocol names
- compress navigation chrome and repetitive copy
- return structured fields through a tool call

`gpt-5-mini` is a good fit for that shape. If you care more about throughput than density, swap the deployment. If you care more about second-pass adjudication than extraction, add a heavier model in a separate stage.

## Porting To Other Providers

Do not fork the crawl engine. Swap the extraction backend.

The interface to keep is `ExtractionBackend.extract(payload) -> ExtractionResult`.

### OpenAI API

Add `OpenAIExtractionBackend` that mirrors `azure_extractor.py`:

- same tool schema
- same prompt contract
- same `ExtractionResult`

Do not move canonicalization or hash computation into the provider.

### Google Vertex AI

Add `VertexExtractionBackend` with Gemini structured output or function calling:

- map the fetched page into the same prompt payload
- require JSON fields `title`, `section_path`, and `content`
- return the same `ExtractionResult`

The stable hash path should still use `DeterministicExtractionBackend`.

### Anthropic Or Other APIs

Same rule:

- provider owns the export text
- the app owns the diff boundary

If a provider cannot return stable structured fields, it is the wrong layer for this service.
