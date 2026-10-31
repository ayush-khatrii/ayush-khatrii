# ORBITAL / GitHub Profile — Setup

This package is designed for the **`ayush-khatrii/ayush-khatrii`** special GitHub profile repository.

## Install

1. Create (or open) the public repository named exactly `ayush-khatrii` on the `ayush-khatrii` account.
2. Copy `README.md`, `assets/`, `scripts/`, and `.github/workflows/update-telemetry.yml` into the **root of that repo**. Do **not** upload the ZIP itself as the only file.
3. Commit the files to the repository's default branch (usually `main`). The artwork appears immediately; GitHub caches remote images, so updates may not appear instantly.
4. Under **Settings → Actions → General → Workflow permissions**, enable **Read and write permissions** for GitHub Actions if your repository does not already allow writing. This is needed for the job to commit its generated SVG.
5. In **Actions → Refresh mission telemetry**, select **Run workflow** once. The action calls the public GitHub REST API and replaces the initial placeholder in `assets/telemetry.svg` with actual data. It also runs daily. If Actions are disabled, enable them first.
6. Reload `https://github.com/ayush-khatrii` after the workflow finishes. The activity dropdown and third-party stats cards load from their own endpoints.

## What is original / automated?

- `assets/stellar-hero.gif`: hand-built animated cosmic hero (no third-party hosted banner)
- `assets/signal-bus.gif`: hand-built looping signal visualizer
- `assets/telemetry.svg`: generated from **real public GitHub API data** by `scripts/update_telemetry.py`
- `scripts/render_assets.py`: source code to customize/rebuild both GIFs (requires `Pillow` and `numpy` locally; it isn't run in GitHub Actions)
- `.github/workflows/update-telemetry.yml`: workflow to refresh telemetry and commit the result daily
- GitHub stats, heatmap and activity graph use public third-party image providers and may be rate-limited or temporarily unavailable.

## Visual & GitHub limitations

GitHub sanitizes README HTML: **no inline JavaScript, `<style>`, CSS animations on ordinary markup, external CSS, iframes, or CSS grid**. The motion is baked into standalone GIF images instead. The statistics dropdown uses supported native `<details>` / `<summary>` HTML.

The README avoids huge fixed-width spacers, so it shouldn't create the forced horizontal scrollbar seen with 900px image-width hacks. Nested HTML tables are written without blank lines inside their parent rows to avoid GitHub's Markdown parser corrupting tags. On small screens, any four-column table may still wrap or scroll based on GitHub's renderer.

This isn't a claim that all externally generated statistics always render; verify the final preview on your GitHub page, and replace any unavailable third-party provider if needed.

## Change your username / brand

Search and replace `ayush-khatrii`, `ayushkhatri.in`, and social URLs in `README.md`. Update `USER` in `scripts/update_telemetry.py` as well. To change the GIF text and colors, edit and re-run `python scripts/render_assets.py`.

## Local checks

```bash
python scripts/update_telemetry.py --offline   # placeholder preview; requires no internet
python scripts/render_assets.py              # regenerates GIFs; needs pillow & numpy
```

_Do not publish local font files with the repo. The renderer uses system fonts from the machine on which you run it._
