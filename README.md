# Cutlist

A static site about AI tools and workflows for video editors. No framework, no database. Plain HTML and CSS built by one Python script.

## Edit before you publish

Open `build.py` and change the `SITE` block at the top:

- `url`: your real domain, no trailing slash
- `email`: a real inbox on your domain (shown on the Contact and Privacy pages)
- `adsense_client`: leave empty until AdSense approves you

## Build and preview

```
python3 build.py
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000

The finished site is in `dist/`. Upload that folder to any static host (Cloudflare Pages, Netlify, Vercel, GitHub Pages). Set the build command to `python3 build.py` and the output folder to `dist` if the host builds for you.

## Add an article

Create a new file in `content/articles/`, for example `my-new-guide.html`. Start it with this header, then a line with only `---`, then the article HTML:

```
title: Your article title
slug: your-article-slug
date: 2026-10-20
category: Audio cleanup
read: 6
description: One sentence, around 140 characters.
---
<p class="short"><strong>Short version.</strong> Two sentences.</p>
<h2>First heading</h2>
<p>Text.</p>
```

Use the same `category` text to group articles together. Each category gets its own page automatically.

If you update an article later, add a line `updated: 2026-11-02` to the header. The page shows it as "Last checked".

## Before you apply for AdSense

1. Publish at least 25 to 30 original articles, with your own screenshots and results. Replace the three starter guides' general advice with what you tested yourself.
2. Use your own domain, not a free subdomain.
3. Keep the About, Contact, Privacy and Disclosure pages live and linked in the footer.
4. Apply, then put your publisher ID in `adsense_client` and rebuild. This adds the AdSense script and `ads.txt`.
5. If you expect visitors from the EEA, UK or Switzerland, you need a Google-certified consent banner (CMP) before showing ads to them. AdSense explains this in its Privacy and messaging section.

The privacy policy is a general starting point, not legal advice. Update it if you add analytics or other services.
