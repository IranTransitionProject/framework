#!/usr/bin/env python3
"""
migrate_content.py — Parse ITB/ISA markdown source files into content YAML.

Phase 2 migration: reads hand-authored .md files, produces structured YAML
matching content.schema.json. Handles mojibake cleanup, section/subsection
hierarchy, metadata extraction.

Usage:
    python scripts/migrate_content.py /path/to/SOURCE.md ITB-X [--pillar X]
    python scripts/migrate_content.py --batch /path/to/source_dir/
"""

import re
import sys
import yaml
from pathlib import Path

# ─── Mojibake cleanup ────────────────────────────────────────────────────────

MOJIBAKE_MAP = {
    'â\x80\x94': '—',      # em-dash
    'â\x80\x93': '–',      # en-dash
    'â\x80\x99': '\u2019',  # right single quote
    'â\x80\x98': '\u2018',  # left single quote
    'â\x80\x9c': '\u201c',  # left double quote
    'â\x80\x9d': '\u201d',  # right double quote
    'â\x80¦': '…',          # ellipsis
    'Â§': '§',              # section sign
    'Â ': ' ',              # nbsp artifact
    'â€"': '—',             # common mojibake em-dash
    'â€"': '–',             # common mojibake en-dash
    'â€™': '\u2019',
    'â€˜': '\u2018',
    'â€œ': '\u201c',
    'â€\x9d': '\u201d',
    'â€¦': '…',
}

def clean_mojibake(text: str) -> str:
    """Fix common UTF-8 double-encoding artifacts."""
    for bad, good in MOJIBAKE_MAP.items():
        text = text.replace(bad, good)
    # Catch remaining â€ patterns
    text = re.sub(r'â€[\x80-\xbf]', lambda m: m.group(0), text)
    return text


# ─── Metadata extraction ─────────────────────────────────────────────────────

def extract_metadata(lines: list[str]) -> tuple[dict, int]:
    """Extract header metadata block. Returns (metadata_dict, line_index_after_header)."""
    meta = {}
    i = 0
    
    # Skip the # title line
    while i < len(lines) and not lines[i].startswith('# '):
        i += 1
    if i < len(lines):
        # Extract title from first # line
        title_line = lines[i].lstrip('# ').strip()
        # Remove module code prefix like "ITB-E: "
        if ':' in title_line:
            meta['_raw_title'] = title_line.split(':', 1)[1].strip()
        else:
            meta['_raw_title'] = title_line
        i += 1
    
    # Parse **Key:** Value lines
    while i < len(lines):
        line = lines[i].strip()
        if line == '---':
            i += 1
            continue
        if not line:
            i += 1
            continue
            
        m = re.match(r'\*\*(.+?):\*\*\s*(.*)', line)
        if m:
            key = m.group(1).strip().lower().replace(' ', '_')
            val = m.group(2).strip()
            meta[key] = val
            i += 1
            continue
        
        # Check for pillar header
        if line.startswith('# PILLAR'):
            i += 1
            continue
        
        # Check for Last verified / Confidence line
        m2 = re.match(r'\*\*Last verified:\*\*\s*(.+?)\s*\|\s*\*\*Confidence:\*\*\s*\[(.+?)\]', line)
        if m2:
            meta['last_verified'] = m2.group(1).strip()
            meta['confidence'] = m2.group(2).strip()
            i += 1
            continue
        
        # If we hit a ## heading, we're past the header
        if line.startswith('## '):
            break
        
        # If we hit content that isn't metadata, break
        if line and not line.startswith('#') and not line.startswith('*') and '**' not in line:
            # Check if it's a preamble paragraph
            if line and not line.startswith('|'):
                meta.setdefault('_preamble_lines', [])
                meta['_preamble_lines'].append(lines[i])
            i += 1
            continue
        
        i += 1
    
    return meta, i


# ─── Section parsing ─────────────────────────────────────────────────────────

def parse_section_heading(line: str) -> tuple[int, str, str, list[str]]:
    """Parse a markdown heading into (level, id, title, tags).
    
    Handles patterns like:
      ## E1) Kurdish Regions — UPDATED
      ### B1.2) Sub-Section Title
      ## 1. Section Title
      ## A1) Title
    """
    m = re.match(r'^(#{2,5})\s+(.+)', line)
    if not m:
        return 0, '', '', []
    
    level = len(m.group(1))
    rest = m.group(2).strip()
    
    tags = []
    # Extract trailing tags: — UPDATED, — NEW, — CRITICAL FINDING, etc.
    tag_match = re.search(r'\s*[—–-]+\s+((?:UPDATED|NEW|CRITICAL FINDING|PRIORITY \d+ GAP FILLED|CRITICAL|ADDED|STUB|REVISED)(?:\s*,\s*(?:UPDATED|NEW|CRITICAL FINDING|PRIORITY \d+ GAP FILLED|CRITICAL|ADDED|STUB|REVISED))*)\s*$', rest)
    if tag_match:
        tags = [t.strip() for t in tag_match.group(1).split(',')]
        rest = rest[:tag_match.start()].strip()
    
    # Extract section ID and title
    # Pattern: "E1) Title" or "B1.2) Title" or "1. Title" or "A1) Title"
    id_match = re.match(r'([A-Z]?\d+(?:\.\d+)*[a-z]?)\)\s*(.*)', rest)
    if not id_match:
        # Try "1. Title" pattern
        id_match = re.match(r'(\d+(?:\.\d+)*)\.\s*(.*)', rest)
    if not id_match:
        # Try quoted titles or special patterns
        # Just use the whole thing as title, generate id
        return level, '', rest, tags
    
    sec_id = id_match.group(1)
    title = id_match.group(2).strip()
    
    # Clean title of any remaining tag markers
    title = re.sub(r'\s*[—–-]+\s*$', '', title).strip()
    
    return level, sec_id, title, tags


def parse_sections(lines: list[str], start_idx: int) -> tuple[list[dict], str]:
    """Parse all sections from the markdown body.
    Returns (sections_list, footer_text).
    """
    sections = []
    footer = ''
    i = start_idx
    
    while i < len(lines):
        line = lines[i]
        
        # Check for footer (italic line at end)
        if line.strip().startswith('*') and line.strip().endswith('*') and i >= len(lines) - 3:
            # Check if this is actually the footer (italic note at bottom)
            remaining = [l.strip() for l in lines[i:] if l.strip() and l.strip() != '---']
            if len(remaining) <= 2 and all(r.startswith('*') and r.endswith('*') for r in remaining):
                footer = ' '.join(r.strip('* ') for r in remaining)
                break
        
        # Check for section heading
        if line.startswith('## ') or line.startswith('### ') or line.startswith('#### ') or line.startswith('##### '):
            level, sec_id, title, tags = parse_section_heading(line)
            if not title and not sec_id:
                i += 1
                continue
            
            # Collect content until next heading of same or higher level
            content_lines = []
            subsection_lines = []
            i += 1
            
            # Skip --- after heading
            while i < len(lines) and lines[i].strip() == '---':
                i += 1
            
            while i < len(lines):
                next_line = lines[i]
                
                # Check if next line is a heading
                if re.match(r'^#{2,5}\s+', next_line):
                    next_level = len(re.match(r'^(#{2,5})', next_line).group(1))
                    if next_level <= level:
                        # Same or higher level — end this section
                        break
                    else:
                        # Lower level — this is a subsection, collect it
                        subsection_lines.append(('START', i))
                        i += 1
                        continue
                
                # Skip --- separators
                if next_line.strip() == '---':
                    i += 1
                    continue
                
                # Regular content
                if not subsection_lines:
                    content_lines.append(next_line)
                else:
                    subsection_lines.append(('CONTENT', i))
                i += 1
            
            # Build section dict
            section = {'id': sec_id, 'title': title}
            if tags:
                section['tags'] = tags
            
            # Process content
            content = '\n'.join(content_lines).strip()
            if content:
                section['content'] = content + '\n'
            
            sections.append(section)
        else:
            i += 1
    
    return sections, footer


def parse_sections_v2(lines: list[str], start_idx: int) -> tuple[list[dict], str]:
    """More robust section parser that handles subsection nesting."""
    # First pass: identify all headings and their line ranges
    headings = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        m = re.match(r'^(#{2,5})\s+(.+)', line)
        if m:
            level = len(m.group(1))
            headings.append((i, level, line))
    
    if not headings:
        return [], ''
    
    # Second pass: collect content for each heading
    raw_sections = []
    for idx, (line_num, level, heading_line) in enumerate(headings):
        # Content ends at next heading or end of file
        if idx + 1 < len(headings):
            end_line = headings[idx + 1][0]
        else:
            end_line = len(lines)
        
        content_lines = []
        for j in range(line_num + 1, end_line):
            if lines[j].strip() != '---':
                content_lines.append(lines[j])
        
        # Trim trailing empty lines
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()
        
        parsed_level, sec_id, title, tags = parse_section_heading(heading_line)
        
        raw_sections.append({
            'level': parsed_level,
            'id': sec_id,
            'title': title,
            'tags': tags,
            'content_lines': content_lines,
            'line_num': line_num,
        })
    
    # Check for footer: last content that's italic
    footer = ''
    if raw_sections:
        last_content = '\n'.join(raw_sections[-1]['content_lines']).strip()
        # Check if last section's last paragraph is a footer-like italic
        last_lines = [l for l in raw_sections[-1]['content_lines'] if l.strip()]
        if last_lines:
            last_line = last_lines[-1].strip()
            if last_line.startswith('*') and last_line.endswith('*') and '**' not in last_line[:3]:
                # This might be a footer — check if it's a standalone italic note
                footer_candidate = last_line.strip('* ')
                if any(kw in footer_candidate.lower() for kw in ['remaining gap', 'module upgraded', 'stub', 'key remaining', 'to be', 'not yet']):
                    footer = footer_candidate
                    # Remove it from content
                    raw_sections[-1]['content_lines'] = [
                        l for l in raw_sections[-1]['content_lines']
                        if l.strip() != last_line
                    ]
    
    # Third pass: build nested structure
    # Level 2 (##) = top-level sections
    # Level 3 (###) = subsections  
    # Level 4 (####) = sub-subsections
    
    top_sections = []
    for rs in raw_sections:
        content = '\n'.join(rs['content_lines']).strip()
        
        section = {}
        if rs['id']:
            section['id'] = rs['id']
        else:
            section['id'] = f"_L{rs['line_num']}"
        section['title'] = rs['title']
        
        if rs['level'] > 2:
            section['level'] = rs['level']
        if rs['tags']:
            section['tags'] = rs['tags']
        if content:
            section['content'] = content + '\n'
        
        if rs['level'] == 2:
            section['_subsections'] = []
            top_sections.append(section)
        elif rs['level'] == 3 and top_sections:
            section['_subsections'] = []
            top_sections[-1]['_subsections'].append(section)
        elif rs['level'] == 4 and top_sections and top_sections[-1]['_subsections']:
            top_sections[-1]['_subsections'][-1].setdefault('_subsections', []).append(section)
        elif rs['level'] == 5 and top_sections and top_sections[-1]['_subsections']:
            last_l3 = top_sections[-1]['_subsections'][-1]
            if last_l3.get('_subsections'):
                last_l3['_subsections'][-1].setdefault('_subsections', []).append(section)
            else:
                last_l3.setdefault('_subsections', []).append(section)
        else:
            # Orphan — attach at top level
            top_sections.append(section)
    
    # Convert _subsections to subsections, removing empty ones
    def finalize(section):
        subs = section.pop('_subsections', [])
        if subs:
            section['subsections'] = [finalize(s) for s in subs]
        return section
    
    result = [finalize(s) for s in top_sections]
    return result, footer


# ─── Full file migration ─────────────────────────────────────────────────────

def migrate_file(source_path: Path, module_code: str, pillar: str = None) -> dict:
    """Migrate a single markdown file to content YAML structure."""
    text = source_path.read_text(encoding='utf-8')
    text = clean_mojibake(text)
    lines = text.split('\n')
    
    # Extract metadata
    meta, body_start = extract_metadata(lines)
    
    # Determine pillar from module code if not given
    if not pillar:
        if module_code.startswith('ITB-'):
            pillar = module_code.replace('ITB-', '').split('-')[0]
            # Handle sub-modules: ITB-A8 -> pillar A
            pillar = re.match(r'([A-Z])', pillar).group(1) if re.match(r'[A-Z]', pillar) else None
        elif module_code.startswith('ISA-'):
            pillar = 'ISA'
    
    # Parse sections
    sections, footer = parse_sections_v2(lines, body_start)
    
    # Build YAML structure
    result = {
        'module_code': module_code,
        'version': meta.get('version', '1.0'),
        'date': meta.get('date', '2026-02-27'),
        'source': meta.get('source', ''),
    }
    
    # Dependencies
    deps = meta.get('dependencies', '')
    if deps:
        result['dependencies'] = [d.strip() for d in deps.split(',') if d.strip()]
    
    # Referenced by
    refs = meta.get('referenced_by', '')
    if refs:
        result['referenced_by'] = [r.strip() for r in refs.split(',') if r.strip()]
    
    # Title
    result['title'] = meta.get('_raw_title', module_code)
    
    if pillar:
        result['pillar'] = pillar
    
    if meta.get('last_verified'):
        result['last_verified'] = meta['last_verified']
    if meta.get('confidence'):
        result['confidence'] = meta['confidence']
    
    # Preamble
    if meta.get('_preamble_lines'):
        result['preamble'] = '\n'.join(meta['_preamble_lines']).strip()
    
    result['sections'] = sections
    
    if footer:
        result['footer'] = footer
    
    return result


# ─── YAML output ──────────────────────────────────────────────────────────────

class BlockScalarDumper(yaml.Dumper):
    """Custom dumper that uses block scalar (|) for multi-line strings."""
    pass

def str_representer(dumper, data):
    if '\n' in data:
        # Use block scalar for multi-line
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    if len(data) > 80 or any(c in data for c in ':{}[]&*?|>!%@`'):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

BlockScalarDumper.add_representer(str, str_representer)


def write_yaml(data: dict, output_path: Path):
    """Write YAML with block scalars for content fields."""
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=BlockScalarDumper, 
                  default_flow_style=False, allow_unicode=True,
                  sort_keys=False, width=120)


# ─── Batch config ─────────────────────────────────────────────────────────────

# Map: module_code -> (source_files, pillar)
# Source files are relative to the project directory
BATCH_CONFIG = {
    'ITB-A':    (['ITB_A_CORE.md'], 'A'),
    'ITB-A6':   (['A6_PARLIMENT_DRAFT.md', 'A6_10_RACHET_ADDENDUM.md'], 'A'),
    'ITB-A8':   (['ITB_A8_IDEOLOGY.md'], 'A'),
    'ITB-A9':   (['ITB_A9_IRGC_PARALLEL.md'], 'A'),
    'ITB-A10':  (['ITB_A10_ESCHATOLOGICAL.md'], 'A'),
    'ITB-A11':  (['ITB_A11_PINOCHET.md'], 'A'),
    'ITB-A12':  (['ITB_A12_COERCIVE_ENDURANCE.md'], 'A'),
    'ITB-C':    (['ITB_C_ECONOMY.md'], 'C'),
    'ITB-D':    (['ITB_D_SOCIETY_V4_0.md'], 'D'),
    'ITB-D16':  (['D16_THE_JUDICIARY.md'], 'D'),
    'ITB-E':    (['ITB_E_TERRITORY.md'], 'E'),
    'ITB-F':    (['ITB_F_INTERNATIONAL.md'], 'F'),
    'ITB-F12':  (['ITB_F_F12_NORMALIZATION_QUALITY_v1_0.md'], 'F'),
    'ITB-G':    (['ITB_G_DIASPORA.md'], 'G'),
    'ISA-CORE': (['ISA_CORE.md'], 'ISA'),
    'ISA-CASES':(['ISA_CASE_STUDIES.md'], 'ISA'),
}
# Note: ITB-F11 needs special handling (two source files, including an addendum)
# It's not in project files list — may need manual check


def run_batch(source_dir: Path, output_dir: Path):
    """Migrate all configured modules."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    
    for code, (files, pillar) in BATCH_CONFIG.items():
        print(f"\n{'='*60}")
        print(f"Migrating {code}...")
        
        # Read and concatenate source files
        combined_text = ''
        found_files = []
        for fname in files:
            fpath = source_dir / fname
            if fpath.exists():
                combined_text += fpath.read_text(encoding='utf-8')
                if len(files) > 1:
                    combined_text += '\n\n---\n\n'
                found_files.append(fname)
            else:
                print(f"  ⚠️  Source not found: {fpath}")
        
        if not found_files:
            print(f"  ❌ No source files found for {code}")
            results[code] = 'MISSING'
            continue
        
        # Write combined to temp file and migrate
        tmp = output_dir / f'_tmp_{code}.md'
        tmp.write_text(combined_text, encoding='utf-8')
        
        try:
            data = migrate_file(tmp, code, pillar)
            
            # Determine output filename
            yaml_name = code.lower().replace('-', '_') + '.yaml'
            out_path = output_dir / yaml_name
            write_yaml(data, out_path)
            
            n_sections = len(data.get('sections', []))
            total_sub = sum(len(s.get('subsections', [])) for s in data.get('sections', []))
            print(f"  ✅ {code}: {n_sections} sections, {total_sub} subsections -> {yaml_name}")
            results[code] = f'OK ({n_sections}s/{total_sub}ss)'
        except Exception as e:
            print(f"  ❌ Error migrating {code}: {e}")
            import traceback
            traceback.print_exc()
            results[code] = f'ERROR: {e}'
        finally:
            tmp.unlink(missing_ok=True)
    
    print(f"\n{'='*60}")
    print("MIGRATION SUMMARY")
    print(f"{'='*60}")
    for code, status in results.items():
        print(f"  {code:12s} {status}")
    
    return results


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--batch':
        source_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('/mnt/project')
        output_dir = Path(__file__).parent.parent / 'data' / 'content'
        run_batch(source_dir, output_dir)
    elif len(sys.argv) >= 3:
        source = Path(sys.argv[1])
        code = sys.argv[2]
        pillar = sys.argv[3] if len(sys.argv) > 3 else None
        data = migrate_file(source, code, pillar)
        yaml_name = code.lower().replace('-', '_') + '.yaml'
        out = Path(__file__).parent.parent / 'data' / 'content' / yaml_name
        write_yaml(data, out)
        print(f"✅ {out}")
    else:
        print("Usage:")
        print("  python scripts/migrate_content.py SOURCE.md ITB-X [pillar]")
        print("  python scripts/migrate_content.py --batch [/path/to/source_dir]")
