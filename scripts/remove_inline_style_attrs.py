#!/usr/bin/env python3
"""
Phase 3: Remove inline style="" attributes and replace with CSS classes.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'

# Mappings of inline styles to CSS classes
STYLE_REPLACEMENTS = {
    r'style="display:\s*none;?"': 'class="d-none"',
    r'style="display:\s*none;"': 'class="d-none"',
    r'style="width:\s*100%;?"': 'class="w-100"',
    r'style="width:\s*auto;?"': 'class="w-auto"',
    r'style="cursor:\s*pointer;?"': 'class="cursor-pointer"',
}

# Files to skip (emails must keep inline styles)
SKIP_PATTERNS = ['emails/', 'email_']

def should_skip(filepath):
    """Check if file should be skipped."""
    filepath_str = str(filepath)
    return any(pattern in filepath_str for pattern in SKIP_PATTERNS)

def replace_styles_in_file(filepath):
    """Replace inline styles with CSS classes in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    replacements_made = 0
    
    # Apply each replacement
    for pattern, replacement in STYLE_REPLACEMENTS.items():
        matches = len(re.findall(pattern, content))
        if matches > 0:
            content = re.sub(pattern, replacement, content)
            replacements_made += matches
    
    # Write back if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return replacements_made
    
    return 0

def main():
    print("=" * 80)
    print("PHASE 3: REMOVING INLINE style=\"\" ATTRIBUTES")
    print("=" * 80)
    
    total_files = 0
    total_replacements = 0
    
    # Process all HTML templates
    for template_file in TEMPLATES_DIR.rglob('*.html'):
        if should_skip(template_file):
            continue
        
        replacements = replace_styles_in_file(template_file)
        if replacements > 0:
            relative_path = template_file.relative_to(TEMPLATES_DIR)
            print(f"✓ {relative_path}: {replacements} replacement(s)")
            total_files += 1
            total_replacements += replacements
    
    print("=" * 80)
    print(f"✅ Phase 3 Step 1 Complete!")
    print(f"📊 Modified {total_files} files")
    print(f"📊 Made {total_replacements} replacements")
    print("\nNote: CSS variable styles (--item-index) require separate handling")
    print("=" * 80)

if __name__ == '__main__':
    main()
