"""
Automation: Recover the full story

Walks the Timelines root page, collects every era database and its
year-sorted entries, then writes:

  - storia.html  — human-readable timeline in the browser
  - storia.md    — compact Markdown for AI context / prompts
"""

import html
import os
import sys
from pathlib import Path

sys.path.insert(0, ".")

from notion_lib.client.auth import NotionApiClient
from notion_lib.nModels.pages import PageFactory, DatabasePage
from notion_lib.nModels.databases import DatabaseFactory
from notion_lib.nTypes.ds_filters import S

OUTPUT_DIR = Path(__file__).resolve().parent
HTML_PATH = OUTPUT_DIR / "storia.html"
MD_PATH = OUTPUT_DIR / "storia.md"

# Block types mapped to Markdown / HTML render hints
HEADING_LEVELS = {
    "heading_1": 1,
    "heading_2": 2,
    "heading_3": 3,
}
LIST_TYPES = {
    "bulleted_list_item": "ul",
    "numbered_list_item": "ol",
    "to_do": "todo",
}


class RitrovaTuttaLaStoria:
    """Custom automation: recover the full story from Notion timelines."""

    ROOT_PAGE = "https://app.notion.com/p/Timelines-2df9b4f7b3cd80da88efc8a3c2923ebb"

    def __init__(self, api_key: str):
        self.api = NotionApiClient(key=api_key)

    # ── extraction ──────────────────────────────────────────────

    def run(self):
        print(f"Starting: {self.__class__.__name__}")
        story = self.collect_story()
        self.write_html(story)
        self.write_markdown(story)
        print(f"Wrote {HTML_PATH}")
        print(f"Wrote {MD_PATH}")
        print("Automation complete.")

    def collect_story(self) -> list[dict]:
        page = PageFactory.find(self.api.headers, self.ROOT_PAGE)
        eras: list[dict] = []

        for child in page.get_children():
            if child.type != "callout":
                continue
            for ch in child.get_children():
                if ch.type != "child_database":
                    continue
                db = DatabaseFactory.find(self.api.headers, ch.block_id)
                ds = db.datasources[0]
                era_title = ds.title.strip()
                print(f"Processing: {era_title}")

                events = []
                for pg in ds.sort(S().get(("Anno", True))):
                    page_obj = PageFactory.find(self.api.headers, pg["url"])
                    year = self._page_year(page_obj)
                    title = page_obj.title() if isinstance(page_obj, DatabasePage) else ""
                    blocks = self._extract_blocks(page_obj.get_children())
                    events.append({
                        "year": year,
                        "title": title.strip(),
                        "blocks": blocks,
                        "url": getattr(page_obj, "url", None) or pg.get("url", ""),
                    })
                    print(f"  - {year}: {title}")

                eras.append({"title": era_title, "events": events})

        return eras

    @staticmethod
    def _page_year(page_obj) -> str:
        if not isinstance(page_obj, DatabasePage):
            return ""
        try:
            val = page_obj.prop("Anno").value
        except KeyError:
            return ""
        if val is None:
            return ""
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

    def _extract_blocks(self, blocks, depth: int = 0) -> list[dict]:
        items: list[dict] = []
        for blk in blocks:
            text = self._block_text(blk)
            entry = {
                "type": blk.type,
                "text": text,
                "depth": depth,
                "children": [],
            }
            if getattr(blk, "supports_children", False):
                try:
                    kids = blk.get_children()
                except Exception:
                    kids = []
                if kids:
                    entry["children"] = self._extract_blocks(kids, depth + 1)
            if text or entry["children"]:
                items.append(entry)
        return items

    @staticmethod
    def _block_text(blk) -> str:
        if hasattr(blk, "rich_text"):
            try:
                return (blk.rich_text.text or "").strip()
            except Exception:
                return ""
        return ""

    # ── Markdown (AI-oriented) ──────────────────────────────────

    def write_markdown(self, story: list[dict]) -> None:
        lines: list[str] = [
            "# Full Story — Timeline",
            "",
            "Canonical chronology recovered from Notion. Use this document as "
            "the single source of truth for the world's history: eras, years, "
            "and narrative events in chronological order.",
            "",
            "---",
            "",
        ]

        for era in story:
            lines.append(f"# Era: {era['title']}")
            lines.append("")
            if not era["events"]:
                lines.append("_(no events)_")
                lines.append("")
                continue

            for event in era["events"]:
                year = event["year"] or "?"
                title = event["title"] or "Untitled"
                lines.append(f"## {year} — {title}")
                lines.append("")
                body = self._blocks_to_markdown(event["blocks"])
                if body:
                    lines.extend(body)
                    lines.append("")
                else:
                    lines.append("_(no content)_")
                    lines.append("")

        MD_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    def _blocks_to_markdown(self, blocks: list[dict]) -> list[str]:
        lines: list[str] = []
        for blk in blocks:
            text = blk["text"]
            btype = blk["type"]
            indent = "  " * blk["depth"]

            if btype in HEADING_LEVELS:
                level = min(HEADING_LEVELS[btype] + 2, 6)  # nest under ## year
                lines.append(f"{'#' * level} {text}")
                lines.append("")
            elif btype == "bulleted_list_item":
                lines.append(f"{indent}- {text}")
            elif btype == "numbered_list_item":
                lines.append(f"{indent}1. {text}")
            elif btype == "to_do":
                lines.append(f"{indent}- [ ] {text}")
            elif btype == "quote":
                for part in text.splitlines() or [text]:
                    lines.append(f"{indent}> {part}")
                lines.append("")
            elif btype == "code":
                lines.append(f"{indent}```")
                lines.append(f"{indent}{text}")
                lines.append(f"{indent}```")
                lines.append("")
            elif btype == "divider":
                lines.append("")
                lines.append("---")
                lines.append("")
            elif btype in ("callout", "toggle"):
                if text:
                    lines.append(f"{indent}**{text}**")
                    lines.append("")
            elif text:
                lines.append(f"{indent}{text}")
                lines.append("")

            if blk["children"]:
                lines.extend(self._blocks_to_markdown(blk["children"]))

        return lines

    # ── HTML (human-oriented) ───────────────────────────────────

    def write_html(self, story: list[dict]) -> None:
        sections = []
        nav_items = []

        for i, era in enumerate(story):
            era_id = f"era-{i}"
            nav_items.append(
                f'<a href="#{era_id}">{html.escape(era["title"])}</a>'
            )
            events_html = []
            for event in era["events"]:
                year = html.escape(str(event["year"] or "?"))
                title = html.escape(event["title"] or "Untitled")
                body = self._blocks_to_html(event["blocks"])
                events_html.append(
                    f"""
                    <article class="event">
                      <div class="year">{year}</div>
                      <div class="event-body">
                        <h3>{title}</h3>
                        <div class="content">{body or "<p class='empty'>No content</p>"}</div>
                      </div>
                    </article>
                    """
                )
            empty = '<p class="empty">No events in this era.</p>'
            sections.append(
                f"""
                <section class="era" id="{era_id}">
                  <h2>{html.escape(era["title"])}</h2>
                  <div class="timeline">
                    {"".join(events_html) if events_html else empty}
                  </div>
                </section>
                """
            )

        doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Full Story — Timeline</title>
  <style>
    :root {{
      --bg: #0f1419;
      --surface: #1a222c;
      --border: #2a3542;
      --text: #e8eef4;
      --muted: #8b9aab;
      --accent: #c9a227;
      --accent-dim: #8a7020;
      --year: #6eb5ff;
      --quote: #3d4f63;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "Iowan Old Style", Georgia, serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
    }}
    header.hero {{
      padding: 3rem 1.5rem 2rem;
      border-bottom: 1px solid var(--border);
      background:
        radial-gradient(ellipse at 20% 0%, #1e2a3a 0%, transparent 55%),
        var(--bg);
    }}
    header.hero h1 {{
      margin: 0 0 0.4rem;
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--accent);
    }}
    header.hero p {{
      margin: 0;
      color: var(--muted);
      max-width: 40rem;
    }}
    nav.toc {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1rem;
      padding: 1rem 1.5rem;
      border-bottom: 1px solid var(--border);
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    nav.toc a {{
      color: var(--year);
      text-decoration: none;
      font-size: 0.9rem;
      font-family: system-ui, sans-serif;
    }}
    nav.toc a:hover {{ text-decoration: underline; color: var(--accent); }}
    main {{
      max-width: 52rem;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    .era {{
      margin-bottom: 3.5rem;
    }}
    .era > h2 {{
      margin: 0 0 1.5rem;
      padding-bottom: 0.5rem;
      font-size: 1.55rem;
      border-bottom: 2px solid var(--accent-dim);
      color: var(--accent);
    }}
    .timeline {{
      position: relative;
      padding-left: 1.25rem;
      border-left: 2px solid var(--border);
    }}
    .event {{
      display: grid;
      grid-template-columns: 5.5rem 1fr;
      gap: 1rem;
      margin-bottom: 1.75rem;
      position: relative;
    }}
    .event::before {{
      content: "";
      position: absolute;
      left: -1.25rem;
      top: 0.55rem;
      width: 0.65rem;
      height: 0.65rem;
      border-radius: 50%;
      background: var(--accent);
      transform: translateX(-55%);
      box-shadow: 0 0 0 3px var(--bg);
    }}
    .year {{
      font-family: system-ui, sans-serif;
      font-weight: 700;
      font-size: 1.05rem;
      color: var(--year);
      padding-top: 0.15rem;
    }}
    .event-body {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.15rem;
    }}
    .event-body h3 {{
      margin: 0 0 0.65rem;
      font-size: 1.15rem;
      font-weight: 600;
    }}
    .content p {{ margin: 0 0 0.75rem; }}
    .content p:last-child {{ margin-bottom: 0; }}
    .content h4, .content h5, .content h6 {{
      margin: 1rem 0 0.4rem;
      color: var(--accent);
    }}
    .content ul, .content ol {{
      margin: 0.4rem 0 0.75rem;
      padding-left: 1.25rem;
    }}
    .content blockquote {{
      margin: 0.5rem 0 0.75rem;
      padding: 0.5rem 0.9rem;
      border-left: 3px solid var(--quote);
      color: var(--muted);
      background: rgba(0,0,0,0.2);
    }}
    .content pre {{
      background: #0a0e12;
      padding: 0.75rem 1rem;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 0.88rem;
    }}
    .content .callout {{
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.65rem 0.9rem;
      margin: 0.5rem 0;
      background: #141c26;
    }}
    .empty {{ color: var(--muted); font-style: italic; }}
    footer {{
      text-align: center;
      padding: 1.5rem;
      color: var(--muted);
      font-size: 0.85rem;
      font-family: system-ui, sans-serif;
      border-top: 1px solid var(--border);
    }}
    @media (max-width: 560px) {{
      .event {{ grid-template-columns: 1fr; gap: 0.35rem; }}
      .year {{ padding-left: 0.25rem; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <h1>Full Story</h1>
    <p>Complete chronology recovered from Notion timelines — eras, years, and narrative events.</p>
  </header>
  <nav class="toc">{"".join(nav_items)}</nav>
  <main>
    {"".join(sections) if sections else "<p class='empty'>No eras found.</p>"}
  </main>
  <footer>Generated by RitrovaTuttaLaStoria</footer>
</body>
</html>
"""
        HTML_PATH.write_text(doc, encoding="utf-8")

    def _blocks_to_html(self, blocks: list[dict]) -> str:
        parts: list[str] = []
        for blk in blocks:
            text = html.escape(blk["text"])
            btype = blk["type"]
            kids = self._blocks_to_html(blk["children"]) if blk["children"] else ""

            if btype == "heading_1":
                parts.append(f"<h4>{text}</h4>{kids}")
            elif btype == "heading_2":
                parts.append(f"<h5>{text}</h5>{kids}")
            elif btype == "heading_3":
                parts.append(f"<h6>{text}</h6>{kids}")
            elif btype == "bulleted_list_item":
                parts.append(f"<ul><li>{text}{kids}</li></ul>")
            elif btype == "numbered_list_item":
                parts.append(f"<ol><li>{text}{kids}</li></ol>")
            elif btype == "to_do":
                parts.append(f"<ul><li>☐ {text}{kids}</li></ul>")
            elif btype == "quote":
                parts.append(f"<blockquote>{text}{kids}</blockquote>")
            elif btype == "code":
                parts.append(f"<pre><code>{text}</code></pre>{kids}")
            elif btype == "divider":
                parts.append("<hr />")
            elif btype in ("callout", "toggle"):
                label = f"<strong>{text}</strong>" if text else ""
                parts.append(f'<div class="callout">{label}{kids}</div>')
            elif text or kids:
                parts.append(f"<p>{text}</p>{kids}" if text else kids)

        return "".join(parts)


if __name__ == "__main__":
    key = os.environ.get("NOTION_KEY") or input("API Key: ")
    if not key:
        print("Error: no API key provided.")
        sys.exit(1)
    RitrovaTuttaLaStoria(key).run()
