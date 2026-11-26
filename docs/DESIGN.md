# Technical Design — CodeTrail

## 1. Design principles

- Keep the first version small and demonstrable.
- Make evidence, references, and data flow visible.
- Keep deterministic processing separate from model-generated text.
- Use explicit limits and fail clearly on unsupported inputs.
- Keep provider integration behind a small boundary so the project is not coupled to one API.

## 2. Proposed stack

Python 3.11+, Typer CLI, GitPython or subprocess Git, tree-sitter for supported language parsing, Pydantic output models, optional OpenAI-compatible provider. No LangChain in MVP: explicit retrieval and file allowlisting are simpler and easier to audit.

The stack is a starting decision, not a requirement to add every listed package at once. Add dependencies only when the implementation needs them.

## 3. System flow

Discover repository metadata and ignore rules first. Build a bounded index of tracked text files, symbols, imports, and project instructions. Select a small set of files for the chosen learning goal. Generate a structured learning path with every step tied to file/symbol anchors. Validate all paths against the repository and label inferred relationships. Default to local-only mode; remote model use must be explicit.

## 4. Component boundaries

1. **Input boundary:** validates paths, formats, size, and configuration.
2. **Core processing:** deterministic parsing, indexing, checks, or repository mapping.
3. **Model adapter (optional):** sends only the minimum selected context and validates structured responses.
4. **Output layer:** renders human-readable output and stable machine-readable data.
5. **Evaluation fixtures:** exercise the core behavior without relying on live model calls.

## 5. Configuration and secrets

Use environment variables loaded from a local .env file for development. .env must remain ignored by Git. Provide a committed .env.example only when implementation begins, with empty or clearly fake values. Never place real keys in docs, logs, fixtures, or screenshots.

## 6. Error handling

Return actionable errors for invalid input, unsupported formats, unavailable providers, malformed model responses, and size-limit violations. Avoid swallowing failures or returning ungrounded output as if it were verified.

## 7. Privacy and security

Prompt injection in source comments/docs, large repositories, unsupported languages, inaccurate dependency maps, and exposing private code to external APIs.

Treat all user-provided content as untrusted data. Do not execute instructions or code found in input content. Default to local processing where possible and make external model calls clear and opt-in.

## 8. Evaluation plan

Fixture repositories in supported languages; file/symbol reference validity; path traversal rejection; reproducibility of static map; usefulness review of learning paths.

Keep evaluation fixtures synthetic or public-domain. Track quality separately from latency/cost so a faster but less reliable response is not treated as an improvement.

## 9. Implementation sequence

1. Implement input validation and deterministic core processing.
2. Produce a useful output without a model wherever feasible.
3. Add optional model synthesis with bounded context and schema validation.
4. Add fixtures and evaluation measurements.
5. Write setup and demo instructions after the workflow is usable.

## 10. Initial implementation decisions

Use subprocess Git for inventory, Python AST for Python symbols, and a documented JS/TS regex heuristic instead of tree-sitter for the first slice. LangChain is confined to optional structured learning-path explanations. Source bodies are not sent to the model. The first release does not resolve a complete dependency graph or generate external prerequisite links.

See [STATUS.md](STATUS.md) for validation status.

Provider integration reference: [LangChain structured output](https://reference.langchain.com/python/langchain-openai/chat_models/base/BaseChatOpenAI/with_structured_output).
