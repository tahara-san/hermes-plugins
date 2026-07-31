# Hermes web search backend is not configured

**Issue**

The Hermes `web_search` tool cannot run because no Firecrawl backend is configured.

**Location**

Active Hermes profile web-tool configuration under `/home/hermes/.hermes`

**Severity**

low

**Context**

A documentation lookup through `web_search` failed with a configuration error requesting `FIRECRAWL_API_KEY`, `FIRECRAWL_API_URL`, or managed Nous Portal access. Direct browser access to the authoritative Hermes documentation succeeded, so this did not block the workflow deployment. Web-search provider configuration is unrelated to the approved planning-workflow files and was not changed inline.

**Suggested Fix**

In a separate configuration task, choose a supported web-search provider or configure Firecrawl through the documented Hermes model/plugin setup. Verify with a bounded `web_search` request without exposing credentials.
