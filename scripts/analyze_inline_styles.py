#!/usr/bin/env python3
"""Analyze inline styles and scripts in templates for Code Institute cleanup"""

import re
from pathlib import Path

def analyze_templates():
    templates_dir = Path('templates')
    
    style_templates = []
    script_templates = []
    inline_style_attrs = []
    
    for html_file in templates_dir.rglob('*.html'):
        content = html_file.read_text(encoding='utf-8')
        rel_path = str(html_file.relative_to(templates_dir))
        
        # Count <style> blocks
        style_blocks = len(re.findall(r'<style>', content))
        if style_blocks > 0:
            style_templates.append((rel_path, style_blocks))
        
        # Count <script> blocks (exclude external scripts)
        script_blocks = len(re.findall(r'<script>[\s\S]*?</script>', content))
        if script_blocks > 0:
            script_templates.append((rel_path, script_blocks))
        
        # Count style="" attributes
        inline_attrs = len(re.findall(r'\sstyle="[^"]*"', content))
        if inline_attrs > 0:
            inline_style_attrs.append((rel_path, inline_attrs))
    
    print("\n" + "="*60)
    print("CODE INSTITUTE COMPLIANCE CHECK")
    print("="*60)
    
    print(f"\n📋 INLINE <style> BLOCKS: {len(style_templates)} templates")
    for tmpl, count in sorted(style_templates):
        print(f"   {tmpl}: {count} block(s)")
    
    print(f"\n📋 INLINE <script> BLOCKS: {len(script_templates)} templates")
    for tmpl, count in sorted(script_templates):
        print(f"   {tmpl}: {count} block(s)")
    
    print(f"\n📋 INLINE style=\"\" ATTRIBUTES: {len(inline_style_attrs)} templates")
    total_attrs = sum(c for _, c in inline_style_attrs)
    print(f"   Total occurrences: {total_attrs}")
    for tmpl, count in sorted(inline_style_attrs, key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {tmpl}: {count} attribute(s)")
    
    print(f"\n{'='*60}")
    print(f"SUMMARY:")
    print(f"  - {len(style_templates)} templates need <style> extraction")
    print(f"  - {len(script_templates)} templates need <script> extraction")
    print(f"  - {len(inline_style_attrs)} templates need style=\"\" cleanup")
    print(f"  - Total issues: {len(style_templates) + len(script_templates) + len(inline_style_attrs)}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    analyze_templates()
