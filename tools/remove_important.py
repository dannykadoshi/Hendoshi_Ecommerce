#!/usr/bin/env python3
"""
REMOVE_IMPORTANT SCRIPT (DISABLED)

This script was used to remove `!important` tokens from CSS files during
testing. It has been intentionally disabled (commented out) so it remains in
the repository for future use but will not run accidentally.

To re-enable, restore the original implementation below (remove the triple
quoted block and uncomment the code), or use the backup `tools/remove_important.py.bak`
if present.
"""

# The script has been disabled as requested. Original implementation is kept
# below inside a comment block for reference.

"""
#!/usr/bin/env python3
"""Strip all occurrences of '!important' from CSS files under static/css.
Creates a .bak backup for each file before editing.

Usage: python tools/remove_important.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_GLOB = ROOT / 'static' / 'css'

def process_file(path: Path):
    text = path.read_text(encoding='utf-8')
    if '!important' not in text:
        return False
    # Create backup
    bak = path.with_suffix(path.suffix + '.bak')
    bak.write_text(text, encoding='utf-8')
    # Remove !important and tidy spaces
    new = text.replace('!important', '')
    # Also collapse instances like '  ;' that might appear if spacing left
    new = new.replace('  ;', ' ;')
    new = new.replace(' ;', ';')
    path.write_text(new, encoding='utf-8')
    return True

def main():
    changed = []
    for p in sorted(CSS_GLOB.rglob('*.css')):
        try:
            if process_file(p):
                changed.append(p.relative_to(ROOT))
        except Exception as e:
            print('ERROR', p, e)
    print('Processed', len(changed), 'files:')
    for c in changed:
        print('-', c)

if __name__ == '__main__':
    main()
"""
