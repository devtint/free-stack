# Free Stack

Plain, up-to-date guides to building and deploying real apps on free tiers. Written for solo builders, checked against each product's official documentation.

**Live site:** https://devtint.github.io/free-stack

## Guides

| Guide | Covers |
|-------|--------|
| [Vercel](vercel-guide.html) | Git deploys, CLI, preview and production, env vars, functions, cron jobs, domains, Hobby limits |
| [Supabase](supabase-guide.html) | Publishable and secret keys, tables and RLS, queries, auth, storage, realtime, Edge Functions, pausing |
| [Render](render-guide.html) | Web services, start commands, ports, env vars, health checks, spin-down, render.yaml, deploy hooks |
| [Cloudflare](cloudflare-guide.html) | DNS, proxy and SSL modes, using it with Vercel and Render, Workers, R2 storage |
| [Git](git-guide.html) | Setup, SSH keys, daily cycle, branches, merge and rebase, undo, history, .gitignore |
| [GitHub](github-guide.html) | Pull requests, Actions CI, secrets, scheduled workflows, Pages, rulesets, Dependabot |
| [Keep-alive](keepalive-guide.html) | Health endpoints, UptimeRobot, cron-job.org, GitHub Actions, stopping Supabase pauses |
| [Telegram bots](telegram-bot-guide.html) | python-telegram-bot v22, polling vs webhooks, FastAPI webhook on Render, security, Supabase, rate limits |

Every guide lists the free plan limits, links to the official sources, and ends with a troubleshooting section.

## Editing the site

The published pages are static HTML generated from the files in `_src/`.

```
_src/<page>.html      article content for each page (edit these)
assets/site.css       design system: colors, type, components, light and dark themes
assets/site.js        theme toggle, search, copy buttons, highlighting, mobile menu
build.py              wraps content in the shared layout and writes the root .html files
```

After editing anything in `_src/` or the navigation in `build.py`, rebuild:

```
python3 build.py
```

Then commit both the source and the generated files. No dependencies are needed beyond Python 3.

### Content shorthand

Inside `_src` files you can use these building blocks:

- `<ol class="steps"><li><b>Title</b>Text</li></ol>` for numbered step cards
- `<div class="callout">`, `callout warn` or `callout tip` for notes
- `<pre data-file="name" data-lang="py">raw code</pre>` for code blocks (write code unescaped; languages: js, ts, py, sql, sh, yaml, json)
- `<details><summary>Question</summary><div>Answer</div></details>` for troubleshooting entries
- Plain `<table>` elements, which become cards on phones automatically

## Design

Light by default with an optional dark mode. Warm ivory surfaces, Source Serif 4 for reading, Inter for interface text, JetBrains Mono for code, and a single terracotta accent. Nothing smaller than 14px, generous spacing, and layouts that work down to phone width.

## Built with this stack

| Project | Hosting | Source |
|---------|---------|--------|
| WarpConfGen ([@warpgen_robot](https://t.me/warpgen_robot)) | Vercel | [GitHub](https://github.com/devtint/WarpConfGen) |
| TikTok Downloader ([@tiktokvideodownload_robot](https://t.me/tiktokvideodownload_robot)) | Render | [GitHub](https://github.com/devtint/TelegramtiktokDownloader) |

---

Made by [devtint](https://github.com/devtint) ([Telegram](https://t.me/BadCodeWriter)). An independent educational reference, not affiliated with any service mentioned.

## License

MIT
