## Summary
Brief description of the change and its purpose.

## Type of Change
- [ ] Feature
- [ ] Bug Fix
- [ ] Refactor
- [ ] Architectural Change

## Affected Layer
- [ ] UI (Streamlit pages, rendering functions)
- [ ] Service Client (`AzureBaseClient` or a subclass)
- [ ] Governance (`GovernanceLayer`, `_GOVERNANCE_PRICING`, `AzureCallMeta`)
- [ ] Telemetry (`AzureCallMeta` contract)
- [ ] Configuration (secrets, API versions)
- [ ] CI / workflows

## Checklist

### General
- [ ] Code follows the existing service-abstraction pattern (`AzureBaseClient` → subclass)
- [ ] No secrets, keys, or credentials committed (check `.streamlit/secrets.toml` is in `.gitignore`)
- [ ] `AzureCallMeta` contract unchanged, or all call sites updated

### Service Clients
- [ ] New client methods return `(result, AzureCallMeta)` tuples
- [ ] Retry/timeout behaviour preserved or intentionally changed
- [ ] Azure API version pinned and documented in code comment

### Governance
- [ ] New operations added to `_GOVERNANCE_PRICING` with source comment
- [ ] `GovernanceLayer.enrich()` and `GovernanceLayer.record()` called at every new call site
- [ ] Billing unit semantics documented (record / image / minute / character / page)

### Documentation
- [ ] `README.md` updated (Services table, Architecture diagram if changed, Changelog entry)
- [ ] Module docstring version bumped if this is a release commit

## Manual Testing
List which services were tested end-to-end:
- [ ] Language Intelligence
- [ ] Vision Intelligence
- [ ] Speech Services
- [ ] Document Intelligence
