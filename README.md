# codexTest

Design Token MVP for a Figma + Token Studio + Git workflow.

## MVP scope

- Token categories: `color`, `space`, `radius`, `typography`
- Component tokens: `button.primary`, `input.default`
- Two visual versions:
  - V1: `tokens/tokens.json` (current MVP)
  - V2: `tokens/tokens-v2.json` (selected direction)
- Output formats:
  - `dist/*.css` (CSS custom properties)
  - `dist/*.resolved.json` (alias-resolved flat map)

## File structure

- `tokens/tokens.json`: source of truth token file synced from Token Studio
- `tokens/tokens-v2.json`: selected B version token source
- `scripts/build_tokens.py`: validation + build script
- `examples/token-preview.html`: V1 vs V2 visual comparison page
- `index.html`: B version(V2) single-page preview for deployment
- `vercel.json`: Vercel routing config
- `.github/workflows/tokens-ci.yml`: CI trigger and checks
- `dist/*`: generated artifacts

## Local usage

Validate only:

```bash
python3 scripts/build_tokens.py --check --input tokens/tokens.json
python3 scripts/build_tokens.py --check --input tokens/tokens-v2.json
```

Validate + build:

```bash
python3 scripts/build_tokens.py --build --input tokens/tokens.json
python3 scripts/build_tokens.py --build --input tokens/tokens-v2.json
```

Open visual comparison:

```bash
# 브라우저에서 examples/token-preview.html 열기
```

Open deployment target(B version):

```bash
# 브라우저에서 index.html 열기
```

## Vercel deploy (B version)

1. Build V2 tokens

```bash
python3 scripts/build_tokens.py --build --input tokens/tokens-v2.json
```

2. Deploy to Vercel (CLI)

```bash
vercel --prod
```

Vercel serves `index.html` at `/` and uses `dist/tokens-v2.css` for styling.

## CI behavior

CI is triggered on pull requests and pushes to `main` when token pipeline files change.

Checks run:

1. JSON token structure validation
2. Required top-level categories check
3. Alias resolution check (`{color.bg.primary}` style references)
4. Build artifacts for V1 and V2
5. Upload generated outputs and preview HTML

## Token Studio integration plan

1. Connect Token Studio Remote Storage to this Git repo.
2. Set source token path to `tokens/tokens.json`.
3. Use branch workflow (`token/*`) and open PRs.
4. Merge only after `tokens-ci` passes.
