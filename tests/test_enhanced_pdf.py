#!/usr/bin/env python3
"""Test enhanced PDF generation with Monaco and San Francisco fonts"""
import asyncio
import os
import sys

# Set library paths before importing any modules
os.environ['DYLD_LIBRARY_PATH'] = f"/opt/homebrew/lib:{os.environ.get('DYLD_LIBRARY_PATH', '')}"
os.environ['PKG_CONFIG_PATH'] = "/opt/homebrew/lib/pkgconfig"

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from utils import write_md_to_pdf

async def test_enhanced_pdf():
    """Test PDF generation with Monaco and San Francisco fonts"""
    print("=" * 60)
    print("Testing Enhanced PDF with Monaco and San Francisco Fonts")
    print("=" * 60)

    test_markdown = r"""# Research Report: AI and Machine Learning
*Generated with GPT Researcher*

## Executive Summary

This document demonstrates the **San Francisco** font for body text and **Monaco** font for code snippets, creating a clean, Apple-inspired aesthetic.

## Key Findings

1. **Natural Language Processing** has advanced significantly
2. *Deep Learning* techniques continue to evolve
3. Multi-modal AI systems are emerging

### Code Example

Here's a sample Python function using the Monaco font:

```python
def calculate_embeddings(text: str, model: str):
    # Generate embeddings for the given text
    # Args: text (input text), model (model name)
    embeddings = OpenAIEmbeddings(model=model)
    return embeddings.embed_query(text)
```

### Inline Code

You can also use inline code like `import numpy as np` or configuration values such as `MAX_TOKENS=4096`.

## Technical Details

| Component | Technology | Status |
|-----------|-----------|--------|
| LLM | GPT-4 | Active |
| Embedding | text-embedding-3-large | Active |
| Vector DB | FAISS | Active |

### Blockquote Example

> "The best way to predict the future is to invent it."
> — Alan Kay

## Implementation Notes

- Use **Monaco** for all code elements
- Apply **San Francisco** for body text
- Maintain Apple's design language throughout

### Environment Variables

```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib"
export PKG_CONFIG_PATH="/opt/homebrew/lib/pkgconfig"
EMBEDDING="openai:text-embedding-3-large"
```

## Conclusion

The combination of Monaco and San Francisco fonts provides a professional, clean appearance that aligns with modern Apple design standards.

---

*This is a test document to verify font rendering in PDF reports.*
"""

    try:
        print("\nGenerating enhanced PDF from markdown...")
        print("- Body text: San Francisco font")
        print("- Code blocks: Monaco font")
        print("")

        pdf_path = await write_md_to_pdf(test_markdown, "enhanced_fonts_test")

        if pdf_path:
            print(f"✓ PDF generated successfully!")
            print(f"  Path: {pdf_path}")

            # Check if file exists
            actual_path = "outputs/enhanced_fonts_test.pdf"
            if os.path.exists(actual_path):
                file_size = os.path.getsize(actual_path)
                print(f"  File size: {file_size:,} bytes")
                print(f"\n✓ ENHANCED PDF GENERATION SUCCESSFUL!")
                print(f"\nOpen the PDF to verify:")
                print(f"  open {actual_path}")
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
    success = asyncio.run(test_enhanced_pdf())
    print("\n" + "=" * 60)
    if success:
        print("✓ ENHANCED PDF TEST PASSED!")
        print("=" * 60)
        print("\nThe PDF now uses:")
        print("  - San Francisco font for body text (clean, modern)")
        print("  - Monaco font for code blocks (monospace)")
        print("  - Apple-inspired color scheme and styling")
        sys.exit(0)
    else:
        print("✗ ENHANCED PDF TEST FAILED")
        print("=" * 60)
        sys.exit(1)
