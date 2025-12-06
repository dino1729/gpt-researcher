# PDF Generation Setup - Complete Guide

## Overview
GPT Researcher's Docker container is fully configured for seamless PDF generation with custom fonts. Everything is automated - no manual setup required!

## What's Included

### 1. System Libraries (WeasyPrint Dependencies)
The Dockerfile installs all necessary libraries:
- `libcairo2` - Cairo graphics library
- `libpango-1.0-0` - Pango text layout
- `libpangocairo-1.0-0` - Pango Cairo integration
- `libgdk-pixbuf-2.0-0` - Image loading library
- `libffi-dev` - Foreign function interface
- `shared-mime-info` - MIME type detection

### 2. Custom Fonts (Automatic Download)
During Docker build, the container automatically downloads:
- **Monaco** (65KB) - Monospace font for code blocks
- **San Francisco Pro Text Regular** (2.2MB) - Primary body font
- **San Francisco Pro Text Italic** (2.1MB) - Italic variant for emphasis

**Total fonts size**: ~4.4MB

### 3. Font Sources
Fonts are downloaded from trusted GitHub repositories:
- Monaco: https://github.com/todylu/monaco.ttf
- San Francisco Pro: https://github.com/sahibjotsaggu/San-Francisco-Pro-Fonts

## How It Works

### Automatic Font Download in Dockerfile
```dockerfile
# Download fonts for PDF generation (Monaco, San Francisco Pro)
RUN python3 scripts/download_fonts.py --fonts-dir /app/fonts
```

The `scripts/download_fonts.py` script:
1. Creates `/app/fonts/` directory in the container
2. Downloads each font from the configured URLs
3. Skips download if fonts already exist (from COPY . .)
4. Verifies successful download

### Build Process
```bash
$ docker compose up -d --build

# During build you'll see:
#12 [7/9] RUN python3 scripts/download_fonts.py --fonts-dir /app/fonts
#12 0.123 ✔ Monaco.ttf already present, skipping
#12 0.156 ✔ SF-Pro-Text-Regular.otf already present, skipping
#12 0.189 ✔ SF-Pro-Text-RegularItalic.otf already present, skipping
```

## Verification

### Check Fonts in Container
```bash
$ docker compose exec gpt-researcher ls -lh /app/fonts/

total 4.3M
-rw-r--r-- 1 root root  65K Monaco.ttf
-rw-r--r-- 1 root root 2.2M SF-Pro-Text-Regular.otf
-rw-r--r-- 1 root root 2.1M SF-Pro-Text-RegularItalic.otf
```

### Test PDF Generation
```bash
$ docker compose exec gpt-researcher python3 -c "
from weasyprint import HTML
HTML(string='<h1>Test PDF</h1>').write_pdf('/tmp/test.pdf')
print('✓ PDF generation working!')
"

✓ PDF generation working!
```

### Test with Custom Fonts
```bash
$ docker compose exec gpt-researcher python3 -c "
from weasyprint import HTML

html = '''
<html>
<head>
<style>
@font-face {
    font-family: 'Monaco';
    src: url('/app/fonts/Monaco.ttf');
}
@font-face {
    font-family: 'San Francisco';
    src: url('/app/fonts/SF-Pro-Text-Regular.otf');
}
body { font-family: 'San Francisco', sans-serif; }
code { font-family: 'Monaco', monospace; }
</style>
</head>
<body>
<h1>Custom Fonts Test</h1>
<p>Body text with San Francisco Pro</p>
<code>Code block with Monaco</code>
</body>
</html>
'''

HTML(string=html).write_pdf('/tmp/fonts_test.pdf')
print('✓ PDF with custom fonts created!')
"

✓ PDF with custom fonts created!
```

## Using Fonts in Your PDFs

### In Python Code
```python
from weasyprint import HTML, CSS

# Define fonts in CSS
css = CSS(string='''
@font-face {
    font-family: 'Monaco';
    src: url('/app/fonts/Monaco.ttf');
}
@font-face {
    font-family: 'San Francisco';
    src: url('/app/fonts/SF-Pro-Text-Regular.otf');
}
@font-face {
    font-family: 'San Francisco';
    src: url('/app/fonts/SF-Pro-Text-RegularItalic.otf');
    font-style: italic;
}

body {
    font-family: 'San Francisco', -apple-system, sans-serif;
}

code, pre {
    font-family: 'Monaco', 'Courier New', monospace;
}

em, i {
    font-family: 'San Francisco';
    font-style: italic;
}
''')

# Generate PDF with fonts
HTML(string=html_content).write_pdf('output.pdf', stylesheets=[css])
```

### In HTML Templates
```html
<!DOCTYPE html>
<html>
<head>
<style>
@font-face {
    font-family: 'Monaco';
    src: url('/app/fonts/Monaco.ttf');
}
@font-face {
    font-family: 'San Francisco';
    src: url('/app/fonts/SF-Pro-Text-Regular.otf');
}

body {
    font-family: 'San Francisco', sans-serif;
    font-size: 12pt;
}

code {
    font-family: 'Monaco', monospace;
}
</style>
</head>
<body>
<h1>Research Report</h1>
<p>This is body text in San Francisco Pro.</p>
<code>def example(): pass</code>
</body>
</html>
```

## File Structure

```
gpt-researcher/
├── Dockerfile                      # Includes font download step
├── docker-compose.yml              # Container configuration
├── scripts/
│   └── download_fonts.py           # Font download utility
├── fonts/                          # Font directory (gitignored)
│   ├── Monaco.ttf                  # Downloaded at build time
│   ├── SF-Pro-Text-Regular.otf     # Downloaded at build time
│   └── SF-Pro-Text-RegularItalic.otf  # Downloaded at build time
└── backend/styles/pdf_styles.css   # PDF styling with fonts
```

## Font Management

### Adding New Fonts
To add additional fonts, edit `scripts/download_fonts.py`:

```python
FONTS: tuple[FontSpec, ...] = (
    {
        "family": "Monaco",
        "filename": "Monaco.ttf",
        "url": "https://github.com/todylu/monaco.ttf/raw/master/monaco.ttf",
        "description": "Monaco monospace font used for code blocks.",
    },
    # Add your font here:
    {
        "family": "Your Font",
        "filename": "YourFont.ttf",
        "url": "https://example.com/path/to/font.ttf",
        "description": "Description of your font.",
    },
)
```

Then rebuild the container:
```bash
docker compose up -d --build
```

### Manual Font Download (Local Development)
If developing locally (not in Docker), download fonts manually:
```bash
python3 scripts/download_fonts.py --fonts-dir ./fonts
```

### Font Cache
Fonts are downloaded once during Docker build and cached in the image. To force re-download:
```bash
# Clean build (no cache)
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### Fonts Not Loading in PDF
**Check fonts exist:**
```bash
docker compose exec gpt-researcher ls /app/fonts/
```

**Verify font paths in CSS:**
```css
@font-face {
    font-family: 'Monaco';
    src: url('/app/fonts/Monaco.ttf');  /* Absolute path */
}
```

### Font Download Failed During Build
**Error**: `Failed to download Monaco.ttf`

**Solution**: Check network connectivity or use cached fonts:
```bash
# If you have fonts locally, they'll be copied with COPY . .
# The download script will skip them
ls fonts/  # Check if fonts exist locally
```

### PDF Generation Fails
**Test WeasyPrint:**
```bash
docker compose exec gpt-researcher python3 -c "import weasyprint; print('OK')"
```

**Check system libraries:**
```bash
docker compose exec gpt-researcher dpkg -l | grep -E "cairo|pango|pixbuf"
```

All libraries should be installed (see "What's Included" section above).

## Performance

### Build Time Impact
Font download adds ~1-2 seconds to Docker build time:
- Network download: 0.5-1 second (4.4MB total)
- File operations: 0.1-0.5 second

### Runtime Impact
**Zero** - Fonts are loaded once during PDF generation. No performance impact.

### Image Size Impact
Adds ~4.4MB to the final Docker image:
- Monaco: 65KB
- SF Pro Regular: 2.2MB
- SF Pro Italic: 2.1MB

## Best Practices

### 1. Use Font Fallbacks
Always specify fallback fonts in CSS:
```css
body {
    font-family: 'San Francisco', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

### 2. Preload Fonts
Define all @font-face rules in a separate CSS file for reuse:
```python
css = CSS(filename='backend/styles/pdf_styles.css')
HTML(string=html).write_pdf('output.pdf', stylesheets=[css])
```

### 3. Test Font Rendering
Always test PDF output to verify fonts render correctly:
```bash
# Generate test PDF
docker compose exec gpt-researcher python3 -c "..."

# Copy to host for inspection
docker compose cp gpt-researcher:/tmp/test.pdf ./test.pdf
open test.pdf  # macOS
```

### 4. Keep Fonts in gitignore
Fonts are automatically downloaded - no need to commit them:
```gitignore
# .gitignore
fonts/*.ttf
fonts/*.otf
```

## Summary

✅ **System Libraries**: All WeasyPrint dependencies installed
✅ **Custom Fonts**: Monaco & San Francisco Pro automatically downloaded
✅ **Automatic Setup**: No manual configuration needed
✅ **Docker Native**: Works out of the box in container
✅ **Local Development**: Use `python3 scripts/download_fonts.py` for local setup

### Quick Verification
```bash
# Start container
docker compose up -d

# Check everything
docker compose exec gpt-researcher python3 -c "
import weasyprint
from pathlib import Path

print('✓ WeasyPrint installed')
print('✓ Fonts:', list(Path('/app/fonts/').glob('*')))
print('✓ PDF generation ready!')
"
```

**Result**: Seamless PDF generation with custom fonts in Docker! 🎉

---

**Last Updated**: 2025-12-05
**Status**: ✅ Fully Automated and Working
