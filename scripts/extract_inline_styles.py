#!/usr/bin/env python3
"""
Automated inline style extractor for Code Institute compliance
Extracts <style> blocks from templates and creates CSS files
"""

import re
from pathlib import Path
from collections import defaultdict

def extract_styles_from_template(template_path):
    """Extract all <style> blocks from a template"""
    content = template_path.read_text(encoding='utf-8')
    
    # Find all <style> blocks with their content
    pattern = r'<style>(.*?)</style>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if not matches:
        return None, content
    
    # Combine all style blocks
    combined_styles = '\n\n'.join(matches)
    
    # Remove <style> blocks from template
    cleaned_content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
    
    return combined_styles, cleaned_content

def process_category(category_name, template_files):
    """Process all templates in a category"""
    all_styles = []
    templates_processed = []
    
    print(f"\nProcessing {category_name.upper()}...")
    
    for template_file in template_files:
        styles, cleaned_content = extract_styles_from_template(template_file)
        
        if styles:
            # Add comment header for this template's styles
            template_name = template_file.stem
            style_block = f"/* ===== {template_name.upper()} ===== */\n{styles}"
            all_styles.append(style_block)
            templates_processed.append((template_file, cleaned_content))
            print(f"  ✓ Extracted from {template_file.name}")
    
    return '\n\n'.join(all_styles), templates_processed

def main():
    templates_dir = Path('templates')
    css_dir = Path('static/css/page-specific')
    css_dir.mkdir(parents=True, exist_ok=True)
    
    # Categorize templates
    categories = {
        'home': [],
        'products': [],
        'checkout': [],
        'account': [],
        'vault': [],
        'profiles': [],
        'themes': [],
        'cookies': [],
        'notifications': []
    }
    
    # Find all templates with <style> blocks
    for html_file in templates_dir.rglob('*.html'):
        content = html_file.read_text(encoding='utf-8')
        if '<style>' in content:
            rel_path = html_file.relative_to(templates_dir)
            category = str(rel_path).split('/')[0]
            
            if category in categories:
                categories[category].append(html_file)
            else:
                # Skip email templates - they need inline styles
                if 'emails' not in str(rel_path):
                    print(f"Warning: Uncategorized template: {rel_path}")
    
    # Process each category
    for category, templates in categories.items():
        if not templates:
            continue
        
        # Skip email templates
        non_email_templates = [t for t in templates if 'emails' not in str(t)]
        if not non_email_templates:
            print(f"\nSkipping {category.upper()} - only email templates")
            continue
        
        combined_styles, processed = process_category(category, non_email_templates)
        
        if combined_styles:
            # Create CSS file header
            css_header = f"""/* ================================================
   {category.upper()} PAGES - Extracted Inline Styles
   ================================================
   
   Extracted from inline <style> blocks for Code Institute compliance.
   These styles were previously embedded in HTML templates.
   
   Templates processed: {len(processed)}
   ================================================ */

"""
            # Write CSS file
            css_file = css_dir / f'{category}-pages.css'
            css_file.write_text(css_header + combined_styles, encoding='utf-8')
            print(f"  → Created {css_file}")
            
            # Update templates (remove inline styles)
            for template_path, cleaned_content in processed:
                template_path.write_text(cleaned_content, encoding='utf-8')
                print(f"  → Updated {template_path.name}")
    
    print(f"\n✅ Extraction complete!")
    print(f"   CSS files created in: {css_dir}")
    print(f"\n⚠️  Next steps:")
    print(f"   1. Add CSS files to base.html")
    print(f"   2. Test all pages")
    print(f"   3. Commit changes")

if __name__ == '__main__':
    main()
