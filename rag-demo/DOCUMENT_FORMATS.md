# Supported Document Formats

The ingestion pipeline now supports a wide range of file formats for your RAG system.

## Supported Formats

| Format | Extension | Status | Requirement |
|--------|-----------|--------|-------------|
| Markdown | `.md` | ✓ Built-in | None |
| Text | `.txt` | ✓ Built-in | None |
| PDF | `.pdf` | ✓ Built-in | `pypdf>=4.0.0` |
| Word Document | `.docx` | ✓ Built-in | `python-docx>=0.8.11` |
| JSON | `.json` | ✓ Built-in | None |
| CSV | `.csv` | ✓ Built-in | None |
| Excel | `.xlsx` | ✓ Built-in | `openpyxl>=3.1.0` |

## Installation

All required dependencies are listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs:
- `pypdf` — PDF text extraction
- `python-docx` — Word document parsing
- `openpyxl` — Excel file reading

## How It Works

### Document Loading Process

1. **Recursively scans** `../resources/organized-data/` and all subdirectories
2. **Detects file types** by extension
3. **Extracts text** from each format:
   - PDFs: Page-by-page text extraction
   - DOCX: Paragraph extraction
   - Excel: Sheet-by-sheet with cell values
   - CSV: Row-by-row formatted as records
   - JSON: Pretty-printed with indentation
   - Text/Markdown: Direct file reading

4. **Preserves metadata** per file:
   - Original filename
   - Full file path
   - Format-specific info (page count, sheet count, row count, etc.)

### Format-Specific Behavior

#### PDF Files
- Extracts text from all pages
- Skips pages that fail extraction (logs warning)
- Tracks total page count in metadata
- Handles corrupted PDFs gracefully

#### Word Documents (DOCX)
- Extracts all paragraph text
- Maintains text order and structure
- Records paragraph count

#### Excel Files (XLSX)
- Reads all sheets
- Formats data as pipe-separated values
- Includes sheet name headers
- Tracks sheet count

#### CSV Files
- Parses as records with headers
- Formats as "Record N: key: value" for readability
- Counts total rows

#### JSON Files
- Supports objects and arrays
- Pretty-prints for readability
- Handles nested structures

## Using in Ingestion Pipeline

Simply run the pipeline as normal — it will automatically detect and load all supported formats:

```powershell
python ingestion_pipeline.py
```

The pipeline will:
1. Scan the `organized-data` directory
2. Load all supported formats
3. Create chunks and embeddings
4. Index everything in Azure AI Search

### Example Directory Structure

```
resources/
├── organized-data/
│   ├── guides/
│   │   ├── getting-started.md
│   │   └── faq.md
│   ├── pdfs/
│   │   ├── policy.pdf
│   │   └── guide.pdf
│   ├── data/
│   │   ├── metadata.json
│   │   └── records.csv
│   ├── docs/
│   │   ├── manual.docx
│   │   └── pricing.xlsx
│   └── README.txt
```

The pipeline will load all files from all these directories automatically.

## Error Handling

- **Missing dependencies**: Warns and skips that format
- **Corrupt files**: Logs error and continues with next file
- **Encoding issues**: Defaults to UTF-8, handles gracefully
- **Empty files**: Silently skips (no documents extracted)

## Performance Notes

- **PDF extraction** is the slowest operation
- **CSV/JSON parsing** is fastest
- **Excel files** with many sheets may take time
- All operations log progress (check console for details)

## Troubleshooting

### "pypdf not installed" warning
```bash
pip install pypdf
```

### "python-docx not installed" warning
```bash
pip install python-docx
```

### "openpyxl not installed" warning
```bash
pip install openpyxl
```

### Files not being loaded
1. Check file extension matches (case-sensitive on some systems)
2. Verify files are in `organized-data` or subdirectories
3. Check logs for specific errors
4. Try `python ingestion_pipeline.py --sample` to verify pipeline works

### Slow ingestion
- PDF extraction is inherently slow for large files
- Consider splitting large PDFs before ingestion
- CSV/JSON files should process quickly
