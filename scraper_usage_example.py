"""
Example Usage of PDF Scraper with Recursive Web Scraping
Shows different ways to use the module and process results
"""

import asyncio
import json
from pathlib import Path
from pdf_scraper import process_pdf_with_scraping


# ============================================================================
# EXAMPLE 1: Basic Usage - Process a single PDF
# ============================================================================

async def example_1_basic_usage():
    """Most simple usage - just process a PDF and scrape its links"""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 70)

    pdf_path = "sample.pdf"  # Your PDF file

    result = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=2.0,
        timeout=30,
        save_output=True
    )

    print(f"\n✓ Processing complete!")
    print(f"  Found {len(result['combined_data']['all_links'])} unique links")
    print(f"  Combined text: {result['statistics']['total_text_chars']:,} characters")


# ============================================================================
# EXAMPLE 2: Control Recursion Depth
# ============================================================================

async def example_2_control_depth():
    """
    Control how deep to follow links
    Depth 0 = just scrape initial PDF links
    Depth 1 = also scrape links found in those pages
    Depth 2 = go 2 levels deeper, etc.
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Control Recursion Depth")
    print("=" * 70)

    pdf_path = "sample.pdf"

    # Shallow scraping (just 1 level)
    print("\nShallow scraping (depth=1)...")
    result_shallow = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=1,
        rate_limit=2.0
    )

    # Deep scraping (3 levels)
    print("\nDeep scraping (depth=3)...")
    result_deep = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=3,
        rate_limit=2.0
    )

    print(f"\nComparison:")
    print(f"  Depth 1: {result_shallow['scraping_results']['total_urls_processed']} URLs processed")
    print(f"  Depth 3: {result_deep['scraping_results']['total_urls_processed']} URLs processed")


# ============================================================================
# EXAMPLE 3: Fast Scraping vs Respectful Scraping
# ============================================================================

async def example_3_rate_limiting():
    """
    Control how fast you scrape
    Lower rate_limit = faster (but might get blocked)
    Higher rate_limit = slower (more respectful)
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Rate Limiting")
    print("=" * 70)

    pdf_path = "sample.pdf"

    # Fast scraping (1 second between requests)
    print("\nFast scraping (1 second delay)...")
    result_fast = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=1.0  # 1 second between requests
    )

    # Slow scraping (5 seconds between requests)
    print("\nSlow scraping (5 second delay)...")
    result_slow = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=5.0  # 5 seconds between requests
    )

    print(f"\nExecution times:")
    print(f"  Fast (1s delay): {result_fast['execution_time_seconds']:.2f} seconds")
    print(f"  Slow (5s delay): {result_slow['execution_time_seconds']:.2f} seconds")


# ============================================================================
# EXAMPLE 4: Extract and Process Results
# ============================================================================

async def example_4_process_results():
    """Process results after scraping"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Process Results")
    print("=" * 70)

    pdf_path = "sample.pdf"

    result = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=2.0,
        save_output=True
    )

    # Extract combined text
    combined_text = result['combined_data']['all_text']
    print(f"\n1. Combined Text Length: {len(combined_text):,} characters")

    # Get all links found
    all_links = result['combined_data']['all_links']
    print(f"\n2. All Links Found ({len(all_links)}):")
    for i, link in enumerate(all_links[:10], 1):  # Show first 10
        print(f"   {i}. {link}")

    # See link graph (which pages link to which)
    link_graph = result['combined_data']['link_graph']
    print(f"\n3. Link Graph (sample):")
    for url, links in list(link_graph.items())[:3]:  # Show first 3
        print(f"   {url}")
        print(f"     → Links to: {len(links)} pages")
        for linked in links[:3]:  # Show first 3 links from this page
            print(f"        • {linked}")

    # Check success rate
    success_rate = result['scraping_results']['success_rate']
    print(f"\n4. Success Rate: {success_rate}")

    # Failed URLs
    failed = result['errors']['failed_urls']
    if failed:
        print(f"\n5. Failed URLs ({len(failed)}):")
        for error in failed[:5]:  # Show first 5 failures
            print(f"   • {error['url']}")
            print(f"     Error: {error['error']}")


# ============================================================================
# EXAMPLE 5: Batch Processing Multiple PDFs
# ============================================================================

async def example_5_batch_processing():
    """Process multiple PDFs"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Processing Multiple PDFs")
    print("=" * 70)

    pdf_files = [
        "sample1.pdf",
        "sample2.pdf",
        "sample3.pdf"
    ]

    results = []

    for pdf_file in pdf_files:
        print(f"\nProcessing {pdf_file}...")

        try:
            result = await process_pdf_with_scraping(
                pdf_path=pdf_file,
                max_depth=2,
                rate_limit=2.0
            )
            results.append(result)
            print(f"✓ {pdf_file}: {result['scraping_results']['total_urls_processed']} URLs processed")

        except Exception as e:
            print(f"✗ {pdf_file}: Failed - {str(e)}")

    # Summary
    print(f"\n" + "=" * 70)
    print(f"Batch Summary: {len(results)} PDFs processed successfully")
    print("=" * 70)

    total_urls = sum(r['scraping_results']['total_urls_processed'] for r in results)
    total_text = sum(r['statistics']['total_text_chars'] for r in results)

    print(f"Total URLs processed: {total_urls}")
    print(f"Total text extracted: {total_text:,} characters")


# ============================================================================
# EXAMPLE 6: Save Results in Different Formats
# ============================================================================

async def example_6_save_formats():
    """Save results in different formats for further processing"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Save Results in Different Formats")
    print("=" * 70)

    pdf_path = "sample.pdf"

    result = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=2.0,
        save_output=True,
        output_dir='./scraper_output'
    )

    output_dir = Path('./scraper_output')
    exec_id = result['execution_id']

    # 1. Save full result as JSON
    full_json_path = output_dir / f"full_result_{exec_id}.json"
    with open(full_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"✓ Full result saved: {full_json_path}")

    # 2. Save combined text to a markdown file
    text_path = output_dir / f"combined_text_{exec_id}.md"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(f"# Combined Extracted Text\n\n")
        f.write(f"**Source PDF:** {result['source_pdf']['file_name']}\n\n")
        f.write(f"**Total URLs Processed:** {result['scraping_results']['total_urls_processed']}\n\n")
        f.write(f"---\n\n")
        f.write(result['combined_data']['all_text'])
    print(f"✓ Combined text saved: {text_path}")

    # 3. Save links as a text file
    links_path = output_dir / f"all_links_{exec_id}.txt"
    with open(links_path, 'w', encoding='utf-8') as f:
        f.write("All Links Found During Scraping\n")
        f.write("=" * 50 + "\n\n")
        for i, link in enumerate(result['combined_data']['all_links'], 1):
            f.write(f"{i}. {link}\n")
    print(f"✓ Links saved: {links_path}")

    # 4. Save statistics as JSON
    stats_path = output_dir / f"statistics_{exec_id}.json"
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump({
            'scraping_stats': result['scraping_results'],
            'data_stats': result['statistics'],
            'errors': result['errors']
        }, f, indent=2)
    print(f"✓ Statistics saved: {stats_path}")

    print(f"\nAll files saved to: {output_dir}")


# ============================================================================
# EXAMPLE 7: Real-World Scenario - Process PDF and Analyze Results
# ============================================================================

async def example_7_full_workflow():
    """Full workflow: process, analyze, and extract insights"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Full Workflow - Process and Analyze")
    print("=" * 70)

    pdf_path = "sample.pdf"

    print(f"\n1. Scraping {pdf_path}...")
    result = await process_pdf_with_scraping(
        pdf_path=pdf_path,
        max_depth=2,
        rate_limit=2.0,
        save_output=True
    )

    print(f"\n2. Analyzing Results...")

    # PDF Statistics
    print(f"\n   PDF Statistics:")
    print(f"   • File: {result['source_pdf']['file_name']}")
    print(f"   • Pages: {result['source_pdf']['page_count']}")
    print(f"   • Size: {result['source_pdf']['file_size_bytes']:,} bytes")
    print(f"   • Initial links: {result['source_pdf']['links_extracted']}")

    # Scraping Statistics
    print(f"\n   Web Scraping Statistics:")
    print(f"   • Total URLs: {result['scraping_results']['total_urls_processed']}")
    print(f"   • Successful: {result['scraping_results']['successful_scrapes']}")
    print(f"   • Failed: {result['scraping_results']['failed_scrapes']}")
    print(f"   • Success Rate: {result['scraping_results']['success_rate']}")

    # Combined Data Statistics
    print(f"\n   Combined Data Statistics:")
    print(f"   • Total text: {result['statistics']['total_text_chars']:,} characters")
    print(f"   • Unique URLs: {result['statistics']['unique_urls_found']}")
    print(f"   • Execution time: {result['execution_time_seconds']:.2f} seconds")

    # Content Analysis
    print(f"\n3. Content Analysis...")
    combined_text = result['combined_data']['all_text']

    # Word count
    word_count = len(combined_text.split())
    print(f"   • Total words: {word_count:,}")

    # Find most common topics (simple analysis)
    keywords = ['form', 'data', 'request', 'user', 'process', 'submission', 'validation']
    print(f"   • Keyword frequency:")
    for keyword in keywords:
        count = combined_text.lower().count(keyword)
        if count > 0:
            print(f"     - '{keyword}': {count} occurrences")

    print(f"\n✓ Workflow complete!")
    print(f"  Execution ID: {result['execution_id']}")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

async def run_all_examples():
    """Run all examples"""
    examples = [
        ("Basic Usage", example_1_basic_usage),
        # ("Control Depth", example_2_control_depth),
        # ("Rate Limiting", example_3_rate_limiting),
        ("Process Results", example_4_process_results),
        # ("Batch Processing", example_5_batch_processing),
        # ("Save Formats", example_6_save_formats),
        ("Full Workflow", example_7_full_workflow),
    ]

    for example_name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n✗ {example_name} failed: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        print(f"Running example {example_num}...")
    else:
        print("PDF Scraper Examples")
        print("=" * 70)
        print("Usage: python scraper_usage_example.py [example_number]")
        print("\nAvailable examples:")
        print("  1 - Basic Usage")
        print("  2 - Control Recursion Depth")
        print("  3 - Rate Limiting")
        print("  4 - Process Results")
        print("  5 - Batch Processing")
        print("  6 - Save Different Formats")
        print("  7 - Full Workflow")
        print("\nExample: python scraper_usage_example.py 1")
        sys.exit(1)

    asyncio.run(run_all_examples())
