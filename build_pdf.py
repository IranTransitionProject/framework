#!/usr/bin/env python3
"""
build_pdf.py - Generate ITP release PDFs from built markdown output.

USAGE:
    python build_pdf.py                    # build both tiers
    python build_pdf.py --briefs-only      # Tier 1 (public briefs) only
    python build_pdf.py --full-only        # Tier 2 (full reference) only
    python build_pdf.py --date 2026-03-04  # override release date

OUTPUT:
    releases/ITP-Briefs-v{date}.pdf        # Tier 1: public briefs bundle
    releases/ITP-Reference-v{date}.pdf     # Tier 2: full analytical reference

REQUIREMENTS:
    pip install weasyprint markdown pyyaml
    (pandoc is used for markdown conversion but python-markdown is the fallback)

WORKFLOW:
    1. Run build.py first to ensure output/ is fresh
    2. Run build_pdf.py
    3. Attach PDFs to GitHub Release as assets
"""

import sys
import re
import yaml
import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE     = Path(__file__).parent
OUTPUT   = BASE / "output"
DATA     = BASE / "data"
RELEASES = BASE / "releases"

RELEASES.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Release metadata
# ---------------------------------------------------------------------------

def get_release_date(args):
    for i, a in enumerate(args):
        if a == "--date" and i + 1 < len(args):
            return args[i + 1]
    return datetime.date.today().isoformat()


def load_project_meta():
    """Pull version/title from modules.yaml or fall back to defaults."""
    modules_path = DATA / "modules.yaml"
    if modules_path.exists():
        with open(modules_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        meta = data if isinstance(data, dict) else {}
        return meta.get("metadata", {})
    return {}


# ---------------------------------------------------------------------------
# Brief ordering
# ---------------------------------------------------------------------------

# Ordered sequence: exec summary → intro → briefs 01-13 → emergency → supplemental
BRIEF_ORDER_PATTERNS = [
    r"^00_Convergence_Briefs_-_Executive_Summary",
    r"^01_Convergence_Briefs_-_Introduction",
    r"^Brief_(\d+)_",
    r"^Emergency_Brief_",
    r"^PSC_Flash",
    r"^Children_",
    r".*_supplemental",
]

# Content module ordering for Tier 2 (after briefs)
CONTENT_ORDER_PATTERNS = [
    r"^00_MASTER_INDEX",
    r"^ITB_A_CORE",
    r"^ITB_A",
    r"^ITB_B",
    r"^ITB_C",
    r"^ITB_D",
    r"^ITB_E",
    r"^ITB_F",
    r"^ITB_G",
    r"^ITB_H",
    r"^ISA_CORE",
    r"^ISA_CASES",
    r"^ISA_TRAPS",
    r"^ISA_SCENARIOS",
    r"^APPENDIX",
]


def order_key(filename, patterns):
    stem = filename.stem
    for i, pat in enumerate(patterns):
        if re.match(pat, stem, re.IGNORECASE):
            # Secondary sort: numeric within briefs
            m = re.search(r"_(\d+)_", stem)
            secondary = int(m.group(1)) if m else 0
            return (i, secondary, stem)
    return (len(patterns), 0, stem)


def collect_briefs():
    files = [f for f in OUTPUT.glob("*.md") if not f.stem.startswith("APPENDIX_VARIABLES")
             and not f.stem.startswith("APPENDIX_GAPS")]
    brief_files = [f for f in files if any(
        re.match(pat, f.stem, re.IGNORECASE) for pat in BRIEF_ORDER_PATTERNS
    )]
    return sorted(brief_files, key=lambda f: order_key(f, BRIEF_ORDER_PATTERNS))


def collect_content_modules():
    files = list(OUTPUT.glob("*.md"))
    content_files = [f for f in files if any(
        re.match(pat, f.stem, re.IGNORECASE) for pat in CONTENT_ORDER_PATTERNS
    )]
    return sorted(content_files, key=lambda f: order_key(f, CONTENT_ORDER_PATTERNS))


# ---------------------------------------------------------------------------
# Appendix data from YAML
# ---------------------------------------------------------------------------

def load_entries(path):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    if isinstance(data, list):
        return data
    return []


def build_appendix_html():
    """Render compact reference appendix tables from YAML data."""
    sections = []

    # --- Key Variables ---
    variables = load_entries(DATA / "variables.yaml")
    if variables:
        rows = ""
        for v in variables:
            vid   = v.get("id", "")
            name  = v.get("name", "")
            state = v.get("current_state", "—")
            conf  = v.get("confidence", "")
            rows += f"<tr><td>{vid}</td><td>{name}</td><td>{state}</td><td>{conf}</td></tr>\n"
        sections.append(f"""
<h2 class="appendix-heading">Appendix A — Key Analytical Variables</h2>
<table class="ref-table">
  <thead><tr><th>ID</th><th>Variable</th><th>Current State</th><th>Confidence</th></tr></thead>
  <tbody>{rows}</tbody>
</table>""")

    # --- Analytical Gaps ---
    gaps = load_entries(DATA / "gaps.yaml")
    if gaps:
        rows = ""
        for g in gaps:
            gid      = g.get("id", "")
            name     = g.get("name", "")
            priority = g.get("priority", "")
            impact   = g.get("decision_impact", "—")
            rows += f"<tr><td>{gid}</td><td>{name}</td><td>{priority}</td><td>{impact}</td></tr>\n"
        sections.append(f"""
<h2 class="appendix-heading">Appendix B — Analytical Gaps</h2>
<table class="ref-table">
  <thead><tr><th>ID</th><th>Gap</th><th>Priority</th><th>Decision Impact</th></tr></thead>
  <tbody>{rows}</tbody>
</table>""")

    # --- Traps ---
    traps = load_entries(DATA / "traps.yaml")
    if traps:
        rows = ""
        for t in traps:
            tid   = t.get("id", "")
            name  = t.get("name", "")
            desc  = t.get("description", "—")
            # Truncate long descriptions
            if len(desc) > 120:
                desc = desc[:117] + "..."
            rows += f"<tr><td>{tid}</td><td>{name}</td><td>{desc}</td></tr>\n"
        sections.append(f"""
<h2 class="appendix-heading">Appendix C — Analytical Traps</h2>
<table class="ref-table">
  <thead><tr><th>ID</th><th>Trap</th><th>Description</th></tr></thead>
  <tbody>{rows}</tbody>
</table>""")

    # --- Observations ---
    observations = load_entries(DATA / "observations.yaml")
    if observations:
        rows = ""
        for o in observations:
            oid    = o.get("id", "")
            name   = o.get("name", "")
            status = o.get("status", "—")
            rows += f"<tr><td>{oid}</td><td>{name}</td><td>{status}</td></tr>\n"
        sections.append(f"""
<h2 class="appendix-heading">Appendix D — Analytical Observations</h2>
<table class="ref-table">
  <thead><tr><th>ID</th><th>Observation</th><th>Status</th></tr></thead>
  <tbody>{rows}</tbody>
</table>""")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Markdown → HTML conversion
# ---------------------------------------------------------------------------

def md_to_html(md_text):
    """Convert markdown to HTML using python-markdown with tables support."""
    import markdown
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "attr_list"],
    )


def read_md_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# TOC extraction
# ---------------------------------------------------------------------------

def extract_toc_entries(files):
    """
    Extract (anchor_id, display_title, level) from the first H1 of each file.
    Returns list of dicts.
    """
    entries = []
    for f in files:
        text = read_md_file(f)
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                # Generate anchor matching python-markdown toc extension
                anchor = re.sub(r"[^\w\s-]", "", title.lower())
                anchor = re.sub(r"\s+", "-", anchor).strip("-")
                entries.append({"anchor": anchor, "title": title, "file": f.stem})
                break
    return entries


def build_toc_html(entries):
    items = ""
    for e in entries:
        items += f'  <li><a href="#{e["anchor"]}">{e["title"]}</a></li>\n'
    return f"""
<div class="toc-container">
  <h2 class="toc-heading">Contents</h2>
  <ol class="toc-list">
{items}  </ol>
</div>
"""


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------

def build_cover_html(title, subtitle, release_date, version_tag, tier_label):
    return f"""
<div class="cover-page">
  <div class="cover-top-rule"></div>
  <div class="cover-body">
    <p class="cover-series">Iran Transition Project</p>
    <h1 class="cover-title">{title}</h1>
    <p class="cover-subtitle">{subtitle}</p>
    <div class="cover-meta">
      <p>{tier_label}</p>
      <p>Release: {version_tag}</p>
      <p>Date: {release_date}</p>
    </div>
    <div class="cover-footer">
      <p>irantransitionproject.org</p>
      <p>Published under CC BY-SA 4.0</p>
      <p>hmehr.substack.com</p>
    </div>
  </div>
  <div class="cover-bottom-rule"></div>
</div>
"""


# ---------------------------------------------------------------------------
# CSS stylesheet
# ---------------------------------------------------------------------------

STYLESHEET = """
/* ============================================================
   Iran Transition Project — Release PDF Stylesheet
   Clean professional document style
   ============================================================ */

@page {
  size: A4;
  margin: 2.5cm 2.8cm 2.5cm 2.8cm;
  @bottom-center {
    content: counter(page);
    font-family: 'Georgia', serif;
    font-size: 9pt;
    color: #666;
  }
  @top-right {
    content: "Iran Transition Project";
    font-family: 'Georgia', serif;
    font-size: 8pt;
    color: #999;
  }
}

@page :first {
  @bottom-center { content: none; }
  @top-right { content: none; }
}

/* --- Reset --- */
* { box-sizing: border-box; margin: 0; padding: 0; }

/* --- Body --- */
body {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 10.5pt;
  line-height: 1.65;
  color: #1a1a1a;
  background: white;
}

/* --- Cover page --- */
.cover-page {
  page: cover;
  page-break-after: always;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1cm 0;
}

.cover-top-rule {
  height: 4px;
  background: #1a1a1a;
  margin-bottom: 3cm;
}

.cover-bottom-rule {
  height: 2px;
  background: #1a1a1a;
  margin-top: 2cm;
}

.cover-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.cover-series {
  font-family: 'Georgia', serif;
  font-size: 11pt;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #555;
  margin-bottom: 1.2cm;
}

.cover-title {
  font-family: 'Georgia', serif;
  font-size: 28pt;
  font-weight: bold;
  line-height: 1.2;
  color: #0d0d0d;
  margin-bottom: 0.6cm;
}

.cover-subtitle {
  font-size: 13pt;
  font-style: italic;
  color: #444;
  margin-bottom: 1.5cm;
}

.cover-meta {
  border-top: 1px solid #ccc;
  padding-top: 0.5cm;
  margin-top: 0.5cm;
  color: #444;
  font-size: 10pt;
  line-height: 2;
}

.cover-footer {
  margin-top: 2cm;
  color: #888;
  font-size: 9pt;
  line-height: 1.8;
}

/* --- TOC --- */
.toc-container {
  page-break-after: always;
  padding-top: 1.5cm;
}

.toc-heading {
  font-family: 'Georgia', serif;
  font-size: 16pt;
  font-weight: bold;
  border-bottom: 2px solid #1a1a1a;
  padding-bottom: 0.3cm;
  margin-bottom: 0.8cm;
  color: #0d0d0d;
}

.toc-list {
  list-style: none;
  padding: 0;
  counter-reset: none;
}

.toc-list li {
  padding: 0.25cm 0;
  border-bottom: 1px dotted #ccc;
  font-size: 10.5pt;
}

.toc-list a {
  color: #1a1a1a;
  text-decoration: none;
}

.toc-list a:hover {
  text-decoration: underline;
}

/* --- Section breaks --- */
.section-break {
  page-break-before: always;
}

/* --- Headings --- */
h1 {
  font-family: 'Georgia', serif;
  font-size: 18pt;
  font-weight: bold;
  color: #0d0d0d;
  margin: 0 0 0.6cm 0;
  padding-bottom: 0.3cm;
  border-bottom: 2px solid #1a1a1a;
  page-break-after: avoid;
}

h2 {
  font-family: 'Georgia', serif;
  font-size: 13pt;
  font-weight: bold;
  color: #1a1a1a;
  margin: 0.9cm 0 0.4cm 0;
  page-break-after: avoid;
}

h3 {
  font-family: 'Georgia', serif;
  font-size: 11pt;
  font-weight: bold;
  color: #222;
  margin: 0.7cm 0 0.3cm 0;
  page-break-after: avoid;
}

h4 {
  font-family: 'Georgia', serif;
  font-size: 10.5pt;
  font-weight: bold;
  font-style: italic;
  color: #333;
  margin: 0.5cm 0 0.2cm 0;
  page-break-after: avoid;
}

/* --- Paragraphs --- */
p {
  margin-bottom: 0.5cm;
  orphans: 3;
  widows: 3;
}

/* --- Lists --- */
ul, ol {
  margin: 0.3cm 0 0.5cm 1.4cm;
}

li {
  margin-bottom: 0.2cm;
  line-height: 1.6;
}

/* --- Tables --- */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.5cm 0 0.8cm 0;
  font-size: 9.5pt;
}

th {
  background: #1a1a1a;
  color: white;
  padding: 0.25cm 0.35cm;
  text-align: left;
  font-weight: bold;
  font-family: 'Georgia', serif;
}

td {
  padding: 0.2cm 0.35cm;
  border-bottom: 1px solid #ddd;
  vertical-align: top;
}

tr:nth-child(even) td {
  background: #f8f8f8;
}

/* --- Reference tables (appendix) --- */
.ref-table {
  font-size: 9pt;
}

.ref-table th {
  background: #333;
  font-size: 8.5pt;
}

.appendix-heading {
  margin-top: 1.2cm;
  font-size: 14pt;
  border-bottom: 1.5px solid #555;
  padding-bottom: 0.2cm;
  color: #1a1a1a;
}

/* --- Code / pre --- */
code {
  font-family: 'Courier New', monospace;
  font-size: 9pt;
  background: #f4f4f4;
  padding: 0.05cm 0.15cm;
  border-radius: 2px;
}

pre {
  background: #f4f4f4;
  border-left: 3px solid #999;
  padding: 0.4cm;
  margin: 0.5cm 0;
  font-size: 8.5pt;
  overflow-x: auto;
  white-space: pre-wrap;
}

/* --- Blockquote --- */
blockquote {
  border-left: 3px solid #999;
  margin: 0.5cm 0 0.5cm 0.5cm;
  padding: 0.2cm 0.5cm;
  color: #444;
  font-style: italic;
}

/* --- Horizontal rule --- */
hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 0.8cm 0;
}

/* --- Links --- */
a {
  color: #1a1a1a;
  text-decoration: underline;
}

/* --- Appendix section --- */
.appendix-section {
  page-break-before: always;
}

.appendix-section h1 {
  font-size: 20pt;
  border-bottom: 3px solid #1a1a1a;
}
"""


# ---------------------------------------------------------------------------
# Full HTML document assembly
# ---------------------------------------------------------------------------

def assemble_html(cover_html, toc_html, body_sections, appendix_html, doc_title):
    body_html = ""
    for i, (content_html, stem) in enumerate(body_sections):
        page_class = "section-break" if i > 0 else ""
        body_html += f'<div class="{page_class}" id="section-{stem}">\n{content_html}\n</div>\n'

    appendix_block = ""
    if appendix_html:
        appendix_block = f'<div class="appendix-section section-break">\n<h1>Appendix</h1>\n{appendix_html}\n</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{doc_title}</title>
  <style>{STYLESHEET}</style>
</head>
<body>
{cover_html}
{toc_html}
{body_html}
{appendix_block}
</body>
</html>"""


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------

def render_pdf(html_content, output_path):
    from weasyprint import HTML, CSS
    print(f"  Rendering PDF... this may take 30-60 seconds for large documents.")
    doc = HTML(string=html_content, base_url=str(BASE))
    doc.write_pdf(str(output_path))
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✅ Written: {output_path.name} ({size_mb:.1f} MB)")


# ---------------------------------------------------------------------------
# Build tiers
# ---------------------------------------------------------------------------

def build_tier1(release_date, version_tag):
    """Tier 1: Public briefs bundle."""
    print("\n--- Building Tier 1: Public Briefs Bundle ---")

    brief_files = collect_briefs()
    if not brief_files:
        print("  ⚠️  No brief files found in output/. Run build.py first.")
        return

    print(f"  Found {len(brief_files)} brief files:")
    for f in brief_files:
        print(f"    {f.name}")

    # TOC
    toc_entries = extract_toc_entries(brief_files)
    toc_html = build_toc_html(toc_entries)

    # Body
    body_sections = []
    for f in brief_files:
        md = read_md_file(f)
        body_sections.append((md_to_html(md), f.stem))

    # Appendix
    appendix_html = build_appendix_html()

    # Cover
    cover_html = build_cover_html(
        title="Convergence Briefs",
        subtitle="Analytical assessments of Iranian regime architecture,\ninternal dynamics, and transition scenarios.",
        release_date=release_date,
        version_tag=version_tag,
        tier_label="Public Briefs Edition",
    )

    html = assemble_html(
        cover_html=cover_html,
        toc_html=toc_html,
        body_sections=body_sections,
        appendix_html=appendix_html,
        doc_title=f"ITP Convergence Briefs {version_tag}",
    )

    out_path = RELEASES / f"ITP-Briefs-{version_tag}.pdf"
    render_pdf(html, out_path)
    return out_path


def build_tier2(release_date, version_tag):
    """Tier 2: Full analytical reference bundle."""
    print("\n--- Building Tier 2: Full Reference Bundle ---")

    brief_files  = collect_briefs()
    module_files = collect_content_modules()

    all_files = brief_files + module_files
    if not all_files:
        print("  ⚠️  No output files found. Run build.py first.")
        return

    print(f"  Briefs:  {len(brief_files)} files")
    print(f"  Modules: {len(module_files)} files")
    print(f"  Total:   {len(all_files)} files")

    # TOC — two sections
    brief_toc  = extract_toc_entries(brief_files)
    module_toc = extract_toc_entries(module_files)

    toc_items = ""
    if brief_toc:
        toc_items += '<li class="toc-section-header"><strong>Part I — Convergence Briefs</strong></li>\n'
        for e in brief_toc:
            toc_items += f'  <li><a href="#{e["anchor"]}">{e["title"]}</a></li>\n'
    if module_toc:
        toc_items += '<li class="toc-section-header" style="margin-top:0.5cm"><strong>Part II — Analytical Reference</strong></li>\n'
        for e in module_toc:
            toc_items += f'  <li><a href="#{e["anchor"]}">{e["title"]}</a></li>\n'

    toc_html = f"""
<div class="toc-container">
  <h2 class="toc-heading">Contents</h2>
  <ol class="toc-list">
{toc_items}  </ol>
</div>"""

    # Body
    body_sections = []
    for f in all_files:
        md = read_md_file(f)
        body_sections.append((md_to_html(md), f.stem))

    # Appendix
    appendix_html = build_appendix_html()

    # Cover
    cover_html = build_cover_html(
        title="Full Analytical Reference",
        subtitle="Convergence Briefs with complete ITB and ISA analytical framework.\nFor policy research use.",
        release_date=release_date,
        version_tag=version_tag,
        tier_label="Full Reference Edition",
    )

    html = assemble_html(
        cover_html=cover_html,
        toc_html=toc_html,
        body_sections=body_sections,
        appendix_html=appendix_html,
        doc_title=f"ITP Full Reference {version_tag}",
    )

    out_path = RELEASES / f"ITP-Reference-{version_tag}.pdf"
    render_pdf(html, out_path)
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    release_date = get_release_date(args)
    version_tag  = f"v{release_date}"

    briefs_only = "--briefs-only" in args
    full_only   = "--full-only"   in args

    print(f"ITP PDF Release Builder")
    print(f"Release: {version_tag}")
    print(f"Output:  {RELEASES}/")

    if not OUTPUT.exists():
        print(f"\n❌  output/ directory not found at {OUTPUT}")
        print("    Run `python build.py` first to generate markdown files.")
        sys.exit(1)

    md_count = len(list(OUTPUT.glob("*.md")))
    if md_count == 0:
        print(f"\n❌  No .md files in output/. Run `python build.py` first.")
        sys.exit(1)

    print(f"Found {md_count} markdown files in output/")

    built = []

    if not full_only:
        p = build_tier1(release_date, version_tag)
        if p:
            built.append(p)

    if not briefs_only:
        p = build_tier2(release_date, version_tag)
        if p:
            built.append(p)

    print(f"\n{'='*50}")
    print(f"PDF release build complete.")
    print(f"Files in releases/:")
    for p in built:
        size_mb = p.stat().st_size / (1024 * 1024)
        print(f"  {p.name}  ({size_mb:.1f} MB)")
    print(f"\nNext step: Create a GitHub Release tagged {version_tag}")
    print(f"and attach the PDF files from releases/ as release assets.")


if __name__ == "__main__":
    main()
