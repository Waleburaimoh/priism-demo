# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file HTML/CSS/JS frontend for the PRiiSM Strategy Management Platform. Everything lives in `index.html` (~2200 lines). There is no build tooling, no bundler, no framework, no separate JS or CSS files — edit `index.html` directly.

## Development Workflow

- **Edit**: work directly in `index.html`
- **Deploy**: push to `main` — GitHub Actions deploys automatically to Azure Static Web Apps (no PRs, no build step)
- **Live URL**: https://zealous-field-08eef5c00.7.azurestaticapps.net
- **API base URL**: `https://priism-api-v4.azurewebsites.net/api`

Do not create separate `.js` or `.css` files. Do not introduce a package manager, bundler, or framework.

## index.html Structure

The file is organised in order:
1. `<head>` — Google Fonts, Tabler icons CDN, `<style>` block (all CSS)
2. `<body>` — HTML markup (login screen, app shell, sidebar, modals, detail panel)
3. `<script>` at the bottom — all JavaScript (state, API calls, render functions)

Add new styles in the `<style>` block. Add new HTML in the appropriate section of `<body>`. Add new JS functions before the closing `</script>` tag.

## Design System

CSS custom properties (defined in `:root`):

```
--teal: #2C4A52       (primary background)
--teal-dark: #1e333a  (body background)
--teal-mid: #3a5c66
--teal-light: #4d7280
--gold: #C9A84C       (accent / interactive)
--gold-light: #dfc07a
--gold-dark: #a8872f
--cream: #F5F0E8      (primary text)
--cream-dark: #ede5d5
--border: rgba(201,168,76,0.18)
--border2: rgba(201,168,76,0.32)
--muted: rgba(245,240,232,0.48)
--surface: rgba(255,255,255,0.04)
--surface2: rgba(255,255,255,0.07)
```

Fonts:
- `--font-display: 'Cormorant Garamond', serif` — headings and labels
- `--font-body: 'DM Sans', sans-serif` — body text

Icons: Tabler Icons webfont (`<i class="ti ti-{name}"></i>`). Do not use other icon libraries.

## API Calls

All fetch calls use the base `https://priism-api-v4.azurewebsites.net/api` prefix. The logged-in org UUID is available from the session state. All endpoints require `org_id` from the session — never hardcode UUIDs.
