#!/usr/bin/env python3
"""
Analyze inline style="" attributes in templates.
Shows what styles are being used and where.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'

def extract_style_attributes(template_path):
    """Extract all style="" attributes from a template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all style="" attributes
    pattern = r'style="([^"]*)"'
    matches = re.findall(pattern, content)
    
    return matches

def main():
    print("=" * 80)
    print("ANALYZING INLINE style=\"\" ATTRIBUTES")
    print("=" * 80)
    
    # Categories to analyze
    style_categories = defaultdict(list)
    template_styles = {}
    
    # Walk through all templates
    for template_file in TEMPLATES_DIR.rglob('*.html'):
        relative_path = template_file.relative_to(TEMPLATES_DIR)
        
        # Skip email templates
        if 'emails' in str(relative_path):
            continue
        
        styles = extract_style_attributes(template_file)
        if styles:
            template_styles[str(relative_path)] = styles
            
            # Categorize by style type
            for style in styles:
                style_lower = style.lower()
                if 'display' in style_lower:
                    style_categories['display'].append((relative_path, style))
                if 'color' in style_lower or 'background' in style_lower:
                    style_categories['colors'].append((relative_path, style))
                if 'margin' in style_lower or 'padding' in style_lower:
                    style_categories['spacing'].append((relative_path, style))
                if 'width' in style_lower or 'height' in style_lower:
                    style_categories['sizing'].append((relative_path, style))
                if 'position' in style_lower or 'top' in style_lower or 'left' in style_lower:
                    style_categories['positioning'].append((relative_path, style))
                if '--item-index' in style_lower or '--' in style_lower:
                    style_categories['css-variables'].append((relative_path, style))
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"Templates with style attributes: {len(template_styles)}")
    total_attrs = sum(len(styles) for styles in template_styles.values())
    print(f"Total style attributes: {total_attrs}\n")
    
    # Print by template
    print("📁 BY TEMPLATE:")
    for template, styles in sorted(template_styles.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {template}: {len(styles)} attribute(s)")
        for style in styles[:3]:  # Show first 3
            print(f"    - {style[:60]}...")
        if len(styles) > 3:
            print(f"    ... and {len(styles) - 3} more\n")
    
    # Print by category
    print("\n🏷️  BY CATEGORY:")
    for category, items in sorted(style_categories.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {category}: {len(items)} occurrence(s)")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
