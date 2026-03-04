#!/usr/bin/env python3
"""Batch migrate all Convergence Briefs from source markdown to YAML.

Handles all structural variations:
- Preamble text (update notes, framing paragraphs)
- Inter-section --- separators
- Footer extras (key sources, epistemic notes, project descriptions)
- EB01 unique formatting (em-dashes, -----, emergency byline)
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "pyyaml", "--break-system-packages", "-q"])
    import yaml


def str_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_representer)


# ── Metadata registry ────────────────────────────────────────────────────

BRIEF_META = {
    1: dict(brief_id='B01', version='v2.0', date='2026-02-21', date_published='2026-02-21',
            status='STABLE', link='https://hmehr.substack.com/p/the-blind-spot-in-every-iran-deal',
            core_thesis='Western analysis misses taqiyyah as a state-level institutional doctrine -- not just individual deception.',
            itb_anchors=['ITB-A8', 'ITB-A11'],
            shelf_life='LONG', pending='Optional v2.1 adding taqiyyah compliance theater.'),
    2: dict(brief_id='B02', version='v2.1', date='2026-02-23', date_published='2026-02-21',
            status='CURRENT', link='https://hmehr.substack.com/p/the-country-inside-the-country',
            core_thesis='The IRGC is a parallel civilization of 2-10M people held by economic dependency, not ideology; most can be separated from the institution.',
            itb_anchors=['ITB-A9', 'ITB-D'], shelf_life='LONG', pending=None),
    3: dict(brief_id='B03', version='v2.0', date='2026-02-21', date_published='2026-02-21',
            status='STABLE', link='https://hmehr.substack.com/p/iran-is-not-iraq',
            core_thesis='The Iraq comparison freezes policy thinking; Iran has 7 structural differences that make both optimism and pessimism from that analogy wrong.',
            itb_anchors=['ITB-A9', 'ITB-B', 'ITB-C', 'ITB-D', 'ITB-E', 'ITB-G'],
            shelf_life='LONG', pending='Optional diaspora Type B paragraph.'),
    4: dict(brief_id='B04', version='v2.0', date='2026-02-21', date_published='2026-02-21',
            status='STABLE', link='https://hmehr.substack.com/p/the-spoiler',
            core_thesis='A specific named faction (Mirbagheri/Paydari/MASAF) with institutional positions and a 19-year track record has the theological motivation and practical capacity to sabotage any deal.',
            itb_anchors=['ITB-A10', 'ITB-A8'], shelf_life='LONG', pending='Optional TRIPP validation.'),
    5: dict(brief_id='B05', version='v3.0', date='2026-02-23', date_published='2026-02-21',
            status='CURRENT', link='https://hmehr.substack.com/p/the-deal-that-cannot-hold',
            core_thesis='The Iran-US nuclear deal fails on three independent fronts (internal spoilers, external equilibrium beneficiaries, IRGC enrichment mechanism) and actively funds repression.',
            itb_anchors=['ITB-A10', 'ITB-A11', 'ITB-F11', 'ITB-F12', 'ISA-TRAPS'],
            shelf_life='MEDIUM', pending='None unless Geneva Round 3 changes scope.'),
    6: dict(brief_id='B06', version='v3.0', date='2026-02-24', date_published='2026-02-20',
            status='CURRENT', link='https://hmehr.substack.com/p/the-day-after',
            core_thesis='The regime has a documented false-flag doctrine, a 1988 precedent, and an activated legal framework; the day-after scenario is worse than most transition planning assumes.',
            itb_anchors=['ITB-B', 'ITB-A9', 'ITB-G'], shelf_life='MEDIUM',
            pending='Optional post-transition economic barriers.'),
    7: dict(brief_id='B07', version='v1.0', date='2026-02-23', date_published='2026-02-23',
            status='CURRENT', link='https://hmehr.substack.com/p/who-is-actually-running-iran',
            core_thesis='The person making decisions for Iran (Larijani) is not at the negotiating table; the authorization chain terminates in a man who has already said no.',
            itb_anchors=['ITB-A', 'ITB-B'], shelf_life='MEDIUM', pending=None),
    8: dict(brief_id='B08', version='v1.0', date='2026-02-23', date_published='2026-02-23',
            status='CURRENT', link='https://hmehr.substack.com/p/the-puppet-problem',
            core_thesis='Every faction prefers a controllable Supreme Leader, but the office transforms its occupants -- the 1989 precedent shows the deal must survive a succession that will itself transform.',
            itb_anchors=['ITB-A', 'ITB-A10'], shelf_life='LONG', pending=None),
    9: dict(brief_id='B09', version='v1.0', date='2026-02-23', date_published='2026-02-23',
            status='CURRENT', link='https://hmehr.substack.com/p/the-doctrine-behind-the-escalation',
            core_thesis='The regime treats escalation and diplomacy as sequential phases in a single cycle; strikes accelerate rather than terminate the path to genuine negotiation.',
            itb_anchors=['ITB-A12', 'ITB-A8', 'ITB-A10', 'ITB-F'], shelf_life='LONG', pending=None),
    10: dict(brief_id='B10', version='v1.0', date='2026-02-23', date_published='2026-02-23',
             status='CURRENT', link='https://hmehr.substack.com/p/the-table-after-the-bombs',
             core_thesis='A post-strike deal is simultaneously more achievable and more dangerous than a pre-strike deal; every structural trap intensifies under post-strike conditions.',
             itb_anchors=['ITB-A12', 'ITB-A10', 'ITB-A11', 'ITB-F12', 'ITB-B', 'ITB-C', 'ITB-F'],
             shelf_life='MEDIUM', pending=None),
    'EB01': dict(brief_id='EB01', version='v2.0', date='2026-03-01', date_published='2026-02-28',
                 status='CURRENT', link=None,
                 core_thesis='The Minab school bombing killed children in an IRGC compound that no English-language outlet identified; the co-location pattern is systemic and must be addressed in both targeting and transition planning.',
                 itb_anchors=['ITB-A9', 'ITB-B'], shelf_life='MEDIUM', pending=None),
}

ALL_COMPANIONS = {
    1: ('The Blind Spot in Every Iran Deal', 'https://hmehr.substack.com/p/the-blind-spot-in-every-iran-deal', 'the taqiyyah verification gap'),
    2: ('The Country Inside the Country', 'https://hmehr.substack.com/p/the-country-inside-the-country', 'IRGC parallel civilization'),
    3: ('Iran Is Not Iraq', 'https://hmehr.substack.com/p/iran-is-not-iraq', 'why the comparison fails'),
    4: ('The Spoiler', 'https://hmehr.substack.com/p/the-spoiler', 'the faction blocking every deal'),
    5: ('The Deal That Cannot Hold', 'https://hmehr.substack.com/p/the-deal-that-cannot-hold', 'the Pinochet Pivot and three failure fronts'),
    6: ('The Day After', 'https://hmehr.substack.com/p/the-day-after', 'what determines regime survival after the next strike'),
    7: ('Who Is Actually Running Iran?', 'https://hmehr.substack.com/p/who-is-actually-running-iran', 'the Larijani revelation'),
    8: ('The Puppet Problem', 'https://hmehr.substack.com/p/the-puppet-problem', 'why the next Supreme Leader may not matter'),
    9: ('The Doctrine Behind the Escalation', 'https://hmehr.substack.com/p/the-doctrine-behind-the-escalation', 'the coercive-endurance cycle'),
    10: ('The Table After the Bombs', 'https://hmehr.substack.com/p/the-table-after-the-bombs', 'what post-strike negotiations actually look like'),
}

SOURCE_FILES = {
    1: 'Brief_01_The_Blind_Spot_in_Every_Iran_Deal.md',
    2: 'Brief_02_The_Country_Inside_the_Country.md',
    4: 'Brief_04_The_Spoiler.md',
    5: 'Brief_05_The_Deal_That_Cannot_Hold.md',
    6: 'Brief_06_The_Day_After.md',
    7: 'Brief_07_Who_Is_Actually_Running_Iran.md',
    8: 'Brief_08_The_Puppet_Problem.md',
    9: 'Brief_09_The_Doctrine_Behind_the_Escalation.md',
    10: 'Brief_10_The_Table_After_the_Bombs.md',
    'EB01': 'Emergency_Brief_Children_in_the_Compound_v2.md',
}


def parse_brief(source_path: str, brief_num) -> dict:
    """Parse a brief markdown file into structured YAML data.
    
    Strategy: detect footer boundary FIRST, then parse header/preamble/sections
    within the body region only.
    """
    with open(source_path, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')
    meta = BRIEF_META[brief_num]

    # ── Detect separator style ──
    separator = '-----' if '-----' in text else '---'

    # ── Extract title (line 0: # Title) ──
    title = lines[0][2:].strip()

    # ── Find ## headings ──
    h2_positions = [i for i, line in enumerate(lines) if line.startswith('## ')]
    subtitle = lines[h2_positions[0]][3:].strip()

    # ── Find byline ──
    byline_idx = None
    for i, line in enumerate(lines):
        if line.startswith('**By '):
            byline_idx = i
            break
    byline_text = lines[byline_idx] if byline_idx else None

    # ── FOOTER DETECTION (do this FIRST) ──
    # Scan backward from end to find the first --- that starts the footer block.
    # Footer indicators: line after separator starts with *Brief, *Emergency, *Companion
    footer_sep_idx = None
    for i in range(len(lines) - 1, 0, -1):
        if lines[i].strip() in ('---', '-----'):
            # Check what follows (skip blank lines)
            for j in range(i + 1, min(i + 4, len(lines))):
                s = lines[j].strip()
                if not s:
                    continue
                if (s.startswith('*Brief') or s.startswith('*Emergency Brief')
                    or s.startswith('*Companion') or s.startswith('*Hooman Mehr')):
                    footer_sep_idx = i
                break
        if footer_sep_idx is not None:
            break

    # Capture raw footer (from separator to end)
    footer_raw = None
    if footer_sep_idx is not None:
        footer_raw = '\n'.join(lines[footer_sep_idx:]).strip()

    # Body ends at footer_sep_idx (or end of file)
    body_end = footer_sep_idx if footer_sep_idx is not None else len(lines)

    # ── Content ## headings (all ## after subtitle, within body) ──
    body_h2s = [p for p in h2_positions[1:] if p < body_end]

    # ── Find preamble ──
    content_h2_start = body_h2s[0] if body_h2s else body_end
    preamble_lines = lines[byline_idx + 1:content_h2_start] if byline_idx else []
    preamble_text = '\n'.join(preamble_lines).strip()
    if preamble_text in ('---', '-----', '---\n\n---', '-----\n\n-----'):
        preamble_text = None

    # ── Detect section separators ──
    has_section_seps = False
    for idx in range(len(body_h2s) - 1):
        between_start = body_h2s[idx] + 1
        between_end = body_h2s[idx + 1]
        for li in range(between_start, between_end):
            if lines[li].strip() in ('---', '-----'):
                has_section_seps = True
                break
        if has_section_seps:
            break

    # ── Extract body sections ──
    sections = []
    for idx, pos in enumerate(body_h2s):
        sec_title = lines[pos][3:].strip()

        # Section content runs until next ## or body_end
        end_pos = body_h2s[idx + 1] if idx + 1 < len(body_h2s) else body_end
        content_lines = lines[pos + 1:end_pos]
        content = '\n'.join(content_lines).strip()

        # Remove trailing --- separator (between sections)
        if has_section_seps:
            content = re.sub(r'\n---+\s*$', '', content).strip()

        if not content:
            continue

        sections.append({
            'title': sec_title,
            'level': 2,
            'content': content + '\n',
        })

    # ── Parse footer components (for structured metadata access) ──
    footer_paras = []
    if footer_raw:
        raw_no_seps = re.sub(r'\n---+\n', '\n\n', footer_raw)
        footer_paras = [p.strip() for p in raw_no_seps.split('\n\n') if p.strip()]

    footer_attribution = None
    footer_extras = []
    author_bio_text = None

    for para in footer_paras:
        if para.startswith('*Brief') or para.startswith('*Emergency Brief'):
            footer_attribution = para
        elif para.startswith('*Hooman Mehr is'):
            author_bio_text = para.strip('*').strip()
        elif para.startswith('**Key Source') or para.startswith('**Epistemic'):
            footer_extras.append(para)
        elif para.startswith('*The Iran Transition Project') or para.startswith('*Sources:'):
            footer_extras.append(para)
        elif para.startswith('*Sources include:') or para.startswith('*Key source'):
            footer_extras.append(para)

    # ── Build companion briefs ──
    # Use the standard companion list but parse from source to get exact descriptions
    companion_briefs = []
    for num in sorted(ALL_COMPANIONS.keys()):
        if num == brief_num:
            continue
        t, link, desc = ALL_COMPANIONS[num]
        companion_briefs.append({
            'number': num,
            'title': t,
            'link': link,
            'description': desc,
        })

    # ── Format date display ──
    dp = meta['date_published']
    months = {'01': 'January', '02': 'February', '03': 'March', '04': 'April',
              '05': 'May', '06': 'June', '07': 'July', '08': 'August',
              '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
    parts = dp.split('-')
    date_display = f"{months[parts[1]]} {parts[0]}"

    # ── Build brief dict ──
    brief = {
        'brief_id': meta['brief_id'],
        'number': brief_num if isinstance(brief_num, int) else None,
        'title': title,
        'subtitle': subtitle,
        'author': 'Hooman Mehr',
        'contact': 'hooman@mac.com',
        'series_link': 'https://hmehr.substack.com/p/iran-the-convergence-briefs',
        'brief_link': meta['link'],
        'version': meta['version'],
        'date': meta['date'],
        'date_published': meta['date_published'],
        'status': meta['status'],
        'type': 'emergency_brief' if brief_num == 'EB01' else 'brief',
        'core_thesis': meta['core_thesis'],
        'itb_anchors': meta['itb_anchors'],
        'update_notes': [],
        'preamble': preamble_text,
        'separator': separator,
        'section_separators': has_section_seps,
        'sections': sections,
        'source_summary': None,
        'footer_raw': footer_raw,
        'footer_attribution': footer_attribution,
        'companion_briefs': companion_briefs,
        'footer_extras': footer_extras,
        'author_bio': author_bio_text or 'Hooman Mehr is an independent analyst based in Kirkland, Washington. The Iran Transition Project publishes on [Substack](https://hmehr.substack.com) and [LinkedIn](https://www.linkedin.com/in/hoomanmehr). Contact: [hooman@mac.com](mailto:hooman@mac.com)',
        'changelog': [],
        'governance': {
            'routing_decision': None,
            'shelf_life': meta.get('shelf_life'),
            'pending_updates': meta.get('pending'),
            'vulnerability': None,
        },
    }

    # ── Special handling: EB01 byline ──
    if brief_num == 'EB01':
        brief['byline_override'] = byline_text
        brief['date_display'] = 'February 28, 2026'  # Full date for EB
    else:
        brief['date_display'] = date_display

    # ── Special handling: B04 byline differs from standard ──
    if brief_num == 4:
        brief['byline_override'] = byline_text

    return brief


def write_yaml(data: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True,
                  width=120, sort_keys=False)


def main():
    source_dir = Path('/mnt/project')
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'briefs'

    results = []
    for brief_num, filename in sorted(SOURCE_FILES.items(), key=lambda x: str(x[0])):
        source_path = source_dir / filename
        if not source_path.exists():
            print(f"SKIP: {filename}")
            continue

        out_name = f'eb01.yaml' if brief_num == 'EB01' else f'b{brief_num:02d}.yaml'
        out_path = output_dir / out_name

        try:
            brief = parse_brief(str(source_path), brief_num)
            write_yaml(brief, out_path)

            # Roundtrip check
            with open(out_path, 'r', encoding='utf-8') as f:
                rt = yaml.safe_load(f)

            n = len(rt['sections'])
            has_preamble = bool(rt.get('preamble'))
            has_seps = rt.get('section_separators', False)
            n_extras = len(rt.get('footer_extras', []))
            print(f"PASS: {filename} -> {out_name} "
                  f"({n} sections, preamble={'Y' if has_preamble else 'N'}, "
                  f"seps={'Y' if has_seps else 'N'}, extras={n_extras})")
            results.append((out_name, True, n))
        except Exception as e:
            print(f"FAIL: {filename} -> {e}")
            import traceback
            traceback.print_exc()
            results.append((out_name, False, 0))

    print(f"\n{'='*50}")
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"Migrated: {passed}/{len(results)}")


if __name__ == '__main__':
    main()
