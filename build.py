#!/usr/bin/env python3
"""Builds the Cutlist static site into ./dist

Usage:  python3 build.py
Preview: python3 -m http.server 8000 --directory dist

To add an article, drop a new .html file in content/articles/ using the same
header format as the existing ones, then run the build again.
"""
import html
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"

# ---- Edit these before you publish ----------------------------------------
SITE = {
    "name": "Cutlist",
    "url": "https://example.com",          # your real domain, no trailing slash
    "tagline": "Practical AI workflows for video editors",
    "author": "Muhammad Ammaz Khan",
    "email": "hello@example.com",          # a real inbox on your domain
    "adsense_client": "",                  # example: "ca-pub-1234567890123456"
}
# ----------------------------------------------------------------------------

FONTS = (
    "https://fonts.googleapis.com/css2?"
    "family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700"
    "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400"
    "&display=swap"
)

NAV = [("Articles", "/articles/"), ("How we test", "/how-we-test/"), ("About", "/about/")]
FOOTER_LINKS = [
    ("Contact", "/contact/"),
    ("Privacy", "/privacy/"),
    ("Disclosure", "/disclosure/"),
    ("Sitemap", "/sitemap.xml"),
]


def esc(s):
    return html.escape(s, quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fmt_date(d):
    dt = datetime.strptime(d, "%Y-%m-%d")
    return f"{dt:%B} {dt.day}, {dt.year}"


def fill(text):
    return (
        text.replace("{{name}}", SITE["name"])
        .replace("{{email}}", SITE["email"])
        .replace("{{author}}", SITE["author"])
        .replace("{{url}}", SITE["url"])
    )


def read_doc(path):
    raw = path.read_text(encoding="utf-8")
    head, sep, body = raw.partition("\n---\n")
    if not sep:
        raise SystemExit(f"{path}: add a line with only --- after the header")
    meta = {}
    for line in head.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = fill(value.strip())
    meta["body"] = fill(body.strip())
    return meta


def load_articles():
    items = []
    for f in sorted((ROOT / "content" / "articles").glob("*.html")):
        a = read_doc(f)
        for key in ("title", "slug", "date", "category", "read", "description"):
            if key not in a:
                raise SystemExit(f"{f}: missing '{key}' in header")
        a["path"] = f"/articles/{a['slug']}/"
        a["topic_slug"] = slugify(a["category"])
        items.append(a)
    items.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    return items


def load_pages():
    pages = []
    for f in sorted((ROOT / "content" / "pages").glob("*.html")):
        p = read_doc(f)
        for key in ("title", "slug", "description"):
            if key not in p:
                raise SystemExit(f"{f}: missing '{key}' in header")
        p["path"] = f"/{p['slug']}/"
        pages.append(p)
    return pages


def nav_html(path):
    links = []
    for label, href in NAV:
        current = ' aria-current="page"' if path.startswith(href) else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return "\n".join(links)


def layout(path, title, description, body, *, full_title=None, article=None,
           ruler=False, noindex=False):
    page_title = full_title or f"{title} | {SITE['name']}"
    canonical = SITE["url"] + path
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""

    ads = ""
    if SITE["adsense_client"]:
        ads = (
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/'
            f'adsbygoogle.js?client={esc(SITE["adsense_client"])}" '
            'crossorigin="anonymous"></script>\n'
        )

    ld = ""
    if article:
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["title"],
            "description": article["description"],
            "datePublished": article["date"],
            "dateModified": article.get("updated", article["date"]),
            "author": {"@type": "Person", "name": SITE["author"]},
            "publisher": {"@type": "Organization", "name": SITE["name"]},
            "mainEntityOfPage": canonical,
        }
        ld = f'<script type="application/ld+json">{json.dumps(data)}</script>\n'

    og_type = "article" if article else "website"
    ruler_html = (
        '<div class="ruler" aria-hidden="true"><span class="ticks"></span>'
        '<span class="head"></span></div>\n'
        if ruler else ""
    )

    footer_links = "\n".join(
        f'<li><a href="{href}">{label}</a></li>' for label, href in FOOTER_LINKS
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(page_title)}</title>
<meta name="description" content="{esc(description)}">
{robots}<link rel="canonical" href="{esc(canonical)}">
<meta name="theme-color" content="#F4F5F7">
<meta property="og:site_name" content="{esc(SITE['name'])}">
<meta property="og:title" content="{esc(page_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{esc(canonical)}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/site.css">
{ads}{ld}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
<div class="wrap">
<a class="logo" href="/">{esc(SITE['name'])}</a>
<nav class="nav" aria-label="Main">
{nav_html(path)}
</nav>
</div>
</header>
{ruler_html}<main id="main">
{body}
</main>
<footer class="footer">
<div class="wrap">
<div>
<p>{esc(SITE['name'])} is written by {esc(SITE['author'])}. Guides are checked against the current version of each tool and dated.</p>
<p>&copy; {date.today().year} {esc(SITE['name'])}</p>
</div>
<ul>
{footer_links}
</ul>
</div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""


def entry(a, tag="h3"):
    return (
        '<article class="entry">'
        f'<p class="meta"><a href="/topics/{a["topic_slug"]}/">{esc(a["category"])}</a>, '
        f'{esc(a["read"])} min read</p>'
        f'<{tag}><a href="{a["path"]}">{esc(a["title"])}</a></{tag}>'
        f'<p class="desc">{esc(a["description"])}</p>'
        "</article>"
    )


def topics_of(articles):
    seen = {}
    for a in articles:
        seen.setdefault(a["topic_slug"], a["category"])
    return seen


def home_body(articles):
    lead = articles[0]
    rest = articles[1:4]
    lead_html = (
        '<article class="lead">'
        f'<p class="meta"><a href="/topics/{lead["topic_slug"]}/">{esc(lead["category"])}</a>, '
        f'{esc(lead["read"])} min read</p>'
        f'<h3><a href="{lead["path"]}">{esc(lead["title"])}</a></h3>'
        f'<p class="desc">{esc(lead["description"])}</p>'
        "</article>"
    )
    stack = "\n".join(entry(a) for a in rest)
    tasks = "\n".join(
        f'<li><a href="/topics/{slug}/">{esc(name)}</a></li>'
        for slug, name in topics_of(articles).items()
    )
    return f"""<section class="intro wrap">
<h1>{esc(SITE['tagline'])}.</h1>
<p class="lede">{esc(SITE['name'])} covers the AI features that change how you cut, clean audio, caption, and mask. Each guide walks through one editing job from start to finish and says where the tool gets it wrong.</p>
</section>
<section class="band" aria-labelledby="newest">
<div class="wrap">
<h2 id="newest">Newest guides</h2>
<div class="latest-grid">
{lead_html}
<div class="stack">
{stack}
</div>
</div>
</div>
</section>
<section class="band" aria-labelledby="jobs">
<div class="wrap">
<h2 id="jobs">Find a guide by job</h2>
<ul class="tasks-list">
{tasks}
</ul>
</div>
</section>
<section class="band method" aria-labelledby="method">
<div class="wrap">
<h2 id="method">How the guides are written</h2>
<p>Every guide is built around one editing job. You get the order of steps, the settings worth changing, and the mistakes that make a result look fake.</p>
<p>Tools change fast, so each article shows when it was last checked. <a href="/how-we-test/">Read how tools are tested</a> before they are recommended.</p>
</div>
</section>"""


def article_body(a, articles):
    same = [x for x in articles if x["slug"] != a["slug"] and x["category"] == a["category"]]
    other = [x for x in articles if x["slug"] != a["slug"] and x["category"] != a["category"]]
    related = (same + other)[:3]
    more = ""
    if related:
        items = "\n".join(entry(x) for x in related)
        more = f'<aside class="more" aria-labelledby="more-h"><h2 id="more-h">More guides</h2><div class="more-list">\n{items}\n</div></aside>'
    checked = fmt_date(a.get("updated", a["date"]))
    return f"""<article class="post wrap">
<header class="head">
<p class="meta"><a href="/topics/{a['topic_slug']}/">{esc(a['category'])}</a>, {esc(a['read'])} min read</p>
<h1 class="title">{esc(a['title'])}</h1>
<p class="dek">{esc(a['description'])}</p>
<p class="byline">By {esc(SITE['author'])}. Last checked {checked}.</p>
</header>
<div class="prose">
{a['body']}
</div>
{more}
</article>"""


def listing_body(heading, intro, items):
    entries = "\n".join(entry(a, "h2") for a in items)
    return f"""<section class="page wrap">
<div class="head">
<h1 class="title">{esc(heading)}</h1>
<p class="dek">{esc(intro)}</p>
</div>
<div class="entry-list">
{entries}
</div>
</section>"""


def page_body(p):
    return f"""<article class="page wrap">
<header class="head">
<h1 class="title">{esc(p['title'])}</h1>
<p class="dek">{esc(p['description'])}</p>
</header>
<div class="prose">
{p['body']}
</div>
</article>"""


def write(path, content):
    if path == "/":
        target = OUT / "index.html"
    else:
        target = OUT / path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main():
    articles = load_articles()
    pages = load_pages()
    if not articles:
        raise SystemExit("No articles found in content/articles/")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")

    urls = ["/"]

    write("/", layout(
        "/", SITE["name"], f"{SITE['tagline']}. Step by step guides for audio cleanup, captions, masking, and more.",
        home_body(articles),
        full_title=f"{SITE['name']}: {SITE['tagline']}",
    ))

    write("/articles/", layout(
        "/articles/", "All guides", "Every guide on the site, newest first.",
        listing_body("All guides", "Every guide on the site, newest first.", articles),
    ))
    urls.append("/articles/")

    for a in articles:
        write(a["path"], layout(
            a["path"], a["title"], a["description"], article_body(a, articles),
            article=a, ruler=True,
        ))
        urls.append(a["path"])

    for slug, name in topics_of(articles).items():
        items = [a for a in articles if a["topic_slug"] == slug]
        path = f"/topics/{slug}/"
        intro = f"Guides about {name.lower()}."
        write(path, layout(path, name, intro, listing_body(name, intro, items)))
        urls.append(path)

    for p in pages:
        write(p["path"], layout(p["path"], p["title"], p["description"], page_body(p)))
        urls.append(p["path"])

    not_found = layout(
        "/404.html", "Page not found", "That page does not exist.",
        """<section class="page wrap">
<div class="head">
<h1 class="title">Page not found</h1>
<p class="dek">The link may be old or mistyped. Try the <a href="/articles/">list of guides</a> or go back to the <a href="/">home page</a>.</p>
</div>
</section>""",
        noindex=True,
    )
    (OUT / "404.html").write_text(not_found, encoding="utf-8")

    today = date.today().isoformat()
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"<url><loc>{esc(SITE['url'] + u)}</loc><lastmod>{today}</lastmod></url>")
    sitemap.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")

    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8"
    )

    if SITE["adsense_client"]:
        pub = SITE["adsense_client"].replace("ca-pub-", "pub-")
        (OUT / "ads.txt").write_text(
            f"google.com, {pub}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8"
        )

    print(f"Built {len(urls)} pages into {OUT}")


if __name__ == "__main__":
    main()
