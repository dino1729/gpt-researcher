#!/usr/bin/env python3
"""Test PDF generation with WeasyPrint"""
import asyncio
import os
import sys

# Set library paths before importing any modules
os.environ['DYLD_LIBRARY_PATH'] = f"/opt/homebrew/lib:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
os.environ['PKG_CONFIG_PATH'] = "/opt/homebrew/lib/pkgconfig"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils import write_md_to_pdf

async def test_pdf():
    """Test PDF generation with a simple markdown document"""
    print("=" * 60)
    print("Testing PDF Generation")
    print("=" * 60)

    test_markdown = """# Test Document

This is a **test document** to verify PDF generation is working.

## Section 1
- Item 1
- Item 2
- Item 3

## Section 2
This is some regular text with *italic* and **bold** formatting.
"""

    try:
        print("\nGenerating PDF from markdown...")
        pdf_path = await write_md_to_pdf(test_markdown, "test_pdf")

        if pdf_path:
            print(f"✓ PDF generated successfully!")
            print(f"  Path: {pdf_path}")

            # Check if file exists
            unquoted_path = pdf_path.replace('%2F', '/').replace('outputs/', 'outputs/')
            actual_path = f"outputs/test_pdf.pdf"
            if os.path.exists(actual_path):
                file_size = os.path.getsize(actual_path)
                print(f"  File size: {file_size} bytes")
                print(f"\n✓ PDF GENERATION SUCCESSFUL!")
                return True
            else:
                print(f"  Warning: Path returned but file not found at {actual_path}")
                return False
        else:
            print(f"✗ PDF generation failed - empty path returned")
            return False

    except Exception as e:
        print(f"✗ PDF generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pdf())
    print("\n" + "=" * 60)
    if success:
        print("✓ PDF GENERATION TEST PASSED!")
        print("=" * 60)
        print("\nPDF export should now work in the web interface.")
        sys.exit(0)
    else:
        print("✗ PDF GENERATION TEST FAILED")
        print("=" * 60)
        sys.exit(1)
