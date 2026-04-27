# Modelito PR Patch Plan: Normalized model discovery + metadata contracts

## Goal
Move model listing and model metadata normalization into Modelito so downstream apps (like LLM-r) can consume provider-agnostic, stable response contracts without local fallbacks.

## Scope
1. Add `normalize_models(raw, provider, default_model)` helper in Modelito core.
2. Add `normalize_metadata(raw, provider, model)` helper in Modelito core.
3. Update `Client.list_models()` to always return normalized list entries.
4. Update `Client.model_metadata(model)` (or `get_model_metadata`) to always return normalized metadata object.
5. Add conformance tests across at least one local provider and one hosted provider mock.
6. Document strict response schema in Modelito README and API docs.

## Proposed response contracts

### list_models()
Returns `list[dict]` where each dict includes:
- `id: str` (required)
- `provider: str` (required)
- `name: str | None`
- `default: bool | None`
- `context_window: int | None`
- `input_modalities: list[str] | None`
- `output_modalities: list[str] | None`
- `raw: dict | None` (original provider payload)

### model_metadata(model)
Returns `dict` with:
- `id: str` (required)
- `provider: str` (required)
- `name: str | None`
- `context_window: int | None`
- `pricing: dict | None`
- `modalities: dict | None`
- `capabilities: dict | None`
- `raw: dict | None`

## Validation behavior
- If provider payload is malformed, normalization should raise a typed Modelito exception (e.g., `ModelitoContractError`) with provider + operation context.
- No silent fallback to inferred defaults in downstream clients.

## Test plan (Modelito)
- Unit tests for normalization helpers with representative payload variants:
  - list of strings
  - list of dicts with `model`
  - list of dicts with `id`
  - missing/invalid fields
- Integration tests for `Client.list_models()` and `Client.model_metadata()` using provider stubs.
- Contract tests verifying required keys and types.

## Migration notes for downstream clients
- Downstream wrappers should remove local normalization and fallback behavior.
- Downstream apps can treat non-conforming responses as integration errors and surface diagnostics.
