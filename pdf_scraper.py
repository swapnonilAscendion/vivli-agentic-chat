"""
PDF Processor with Recursive Web Scraper
Extracts content from PDFs and recursively scrapes linked websites
"""

import re
import json
import time
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import asyncio

import pdfplumber
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser
import validators

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PDFContentExtractor:
    """Extract text and links from PDF files"""

    def __init__(self):
        self.url_pattern = r'https?://[^\s\)\]"\']+'

    def extract_pdf_content(self, pdf_path: str) -> Dict:
        """
        Extract text, links, and metadata from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dict with pdf_text, pdf_links, pdf_metadata
        """
        logger.info(f"Extracting content from PDF: {pdf_path}")

        try:
            pdf_file = Path(pdf_path)

            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                full_text = ""
                page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text() or ""
                    full_text += f"\n--- Page {page_num} ---\n{page_text}\n"

                # Extract links from text
                links = self._extract_links_from_text(full_text)

                result = {
                    'pdf_text': full_text,
                    'pdf_links': links,
                    'pdf_metadata': {
                        'file_path': str(pdf_file.absolute()),
                        'file_name': pdf_file.name,
                        'page_count': page_count,
                        'file_size_bytes': pdf_file.stat().st_size,
                        'extraction_timestamp': datetime.now().isoformat(),
                        'total_links_found': len(links)
                    }
                }

                logger.info(f"Successfully extracted {page_count} pages, found {len(links)} links")
                return result

        except FileNotFoundError:
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                'pdf_text': '',
                'pdf_links': [],
                'pdf_metadata': {'error': f"File not found: {pdf_path}"}
            }
        except Exception as e:
            logger.error(f"Error extracting PDF {pdf_path}: {str(e)}")
            return {
                'pdf_text': '',
                'pdf_links': [],
                'pdf_metadata': {'error': str(e)}
            }

    def _extract_links_from_text(self, text: str) -> List[str]:
        """Extract unique URLs from text using regex"""
        urls = re.findall(self.url_pattern, text)

        # Validate and deduplicate
        unique_valid_urls = []
        seen = set()

        for url in urls:
            # Remove trailing punctuation that might be caught by regex
            url = url.rstrip('.,;:)')

            if url not in seen and validators.url(url):
                unique_valid_urls.append(url)
                seen.add(url)

        logger.info(f"Found {len(unique_valid_urls)} valid unique URLs")
        return unique_valid_urls


class WebScraper:
    """Scrape websites with Playwright automation"""

    def __init__(self, rate_limit: float = 2.0, timeout: int = 30):
        self.rate_limit = rate_limit
        self.timeout = timeout * 1000  # Convert to milliseconds for Playwright
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]

    async def scrape_webpage(self, url: str, browser: Browser) -> Dict:
        """
        Scrape a single webpage using Playwright

        Args:
            url: Website URL
            browser: Playwright Browser instance

        Returns:
            Dict with scraped content
        """
        logger.info(f"Scraping: {url}")

        try:
            page = await browser.new_page(user_agent=self.user_agents[hash(url) % len(self.user_agents)])

            # Navigate to page with timeout
            await page.goto(url, wait_until='networkidle', timeout=self.timeout)

            # Get page title
            title = await page.title()

            # Get page content
            content = await page.content()

            # Extract text
            text_content = await page.evaluate('() => document.body.innerText')

            # Extract links
            links_data = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(a => a.href)
                    .filter(href => href && (href.startsWith('http') || href.startsWith('/')));
            }''')

            # Convert relative URLs to absolute
            base_url = url.rsplit('/', 1)[0] + '/'
            links = [urljoin(base_url, link) for link in links_data]

            await page.close()

            return {
                'url': url,
                'title': title,
                'text_content': text_content[:5000],  # First 5000 chars
                'text_content_length': len(text_content),
                'links_found': links,
                'status': 'success',
                'error': None,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': None,
                'text_content': '',
                'text_content_length': 0,
                'links_found': [],
                'status': 'failed',
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }

    @staticmethod
    def _get_url_hash(url: str) -> str:
        """Generate hash for URL deduplication"""
        return hashlib.sha256(url.encode()).hexdigest()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if URL is valid and scrapeable"""
        try:
            if not url.startswith('http'):
                return False

            # Skip certain file types
            skip_extensions = ['.pdf', '.zip', '.exe', '.jpg', '.png', '.gif', '.mp4', '.mp3']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False

            return validators.url(url)
        except:
            return False

    @staticmethod
    def _should_follow_url(url: str, base_domain: Optional[str] = None, same_domain_only: bool = False) -> bool:
        """Check if URL should be followed"""
        if not WebScraper._is_valid_url(url):
            return False

        if same_domain_only and base_domain:
            try:
                url_domain = urlparse(url).netloc
                return url_domain == base_domain
            except:
                return False

        return True


class RecursiveScraper:
    """Recursively scrape URLs and follow links"""

    def __init__(self, max_depth: int = 3, rate_limit: float = 2.0, timeout: int = 30):
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.visited_urls: Set[str] = set()
        self.visited_hashes: Set[str] = set()
        self.web_scraper = WebScraper(rate_limit=rate_limit, timeout=timeout)

    async def scrape_recursive(self, start_urls: List[str], browser: Browser) -> Dict:
        """
        Recursively scrape URLs and follow links

        Args:
            start_urls: Initial URLs to scrape
            browser: Playwright Browser instance

        Returns:
            Dict with all scraped data organized by depth
        """
        logger.info(f"Starting recursive scraping with {len(start_urls)} URLs, max depth: {self.max_depth}")

        results_by_depth = {f'depth_{i}': [] for i in range(self.max_depth + 1)}

        # Start with depth 0
        queue = [(url, 0) for url in start_urls if self.web_scraper._is_valid_url(url)]

        while queue:
            url, depth = queue.pop(0)

            # Skip if already visited or max depth reached
            if url in self.visited_urls:
                logger.debug(f"Skipping already visited URL: {url}")
                continue

            if depth > self.max_depth:
                logger.debug(f"Max depth reached for {url}")
                continue

            self.visited_urls.add(url)

            # Scrape the URL
            scrape_result = await self.web_scraper.scrape_webpage(url, browser)

            # Calculate content hash for deduplication
            content_hash = hashlib.sha256(scrape_result['text_content'].encode()).hexdigest()

            if content_hash in self.visited_hashes:
                logger.info(f"Duplicate content detected: {url}")
                scrape_result['status'] = 'duplicate'
                results_by_depth[f'depth_{depth}'].append(scrape_result)
                continue

            self.visited_hashes.add(content_hash)

            # Add summary to result
            scrape_result['child_links_count'] = len(scrape_result['links_found'])

            # Store result
            results_by_depth[f'depth_{depth}'].append(scrape_result)
            logger.info(f"[Depth {depth}] Scraped {url}: {scrape_result['status']}")

            # If successful and not at max depth, add found links to queue
            if scrape_result['status'] == 'success' and depth < self.max_depth:
                new_links = scrape_result['links_found'][:5]  # Limit to 5 links per page

                for new_url in new_links:
                    if new_url not in self.visited_urls and self.web_scraper._is_valid_url(new_url):
                        queue.append((new_url, depth + 1))
                        logger.debug(f"Added to queue for depth {depth + 1}: {new_url}")

            # Rate limiting
            await asyncio.sleep(self.rate_limit)

        # Calculate statistics
        stats = self._calculate_stats(results_by_depth)

        return {
            'results_by_depth': results_by_depth,
            'statistics': stats
        }

    @staticmethod
    def _calculate_stats(results_by_depth: Dict) -> Dict:
        """Calculate scraping statistics"""
        total_urls = 0
        successful = 0
        failed = 0
        duplicates = 0

        for depth_data in results_by_depth.values():
            total_urls += len(depth_data)
            for result in depth_data:
                if result['status'] == 'success':
                    successful += 1
                elif result['status'] == 'duplicate':
                    duplicates += 1
                else:
                    failed += 1

        return {
            'total_urls_processed': total_urls,
            'successful_scrapes': successful,
            'failed_scrapes': failed,
            'duplicate_urls_skipped': duplicates,
            'success_rate': f"{(successful / total_urls * 100):.1f}%" if total_urls > 0 else "0%"
        }


class DataCombiner:
    """Combine PDF and scraping data"""

    @staticmethod
    def combine_all_data(pdf_data: Dict, scraping_data: Dict, execution_time: float) -> Dict:
        """
        Combine PDF and scraping data into final output

        Args:
            pdf_data: Extracted PDF data
            scraping_data: Scraped website data
            execution_time: Total execution time in seconds

        Returns:
            Combined structured data
        """
        logger.info("Combining PDF and scraping data")

        # Extract all text from successful scrapes
        all_text_parts = [pdf_data['pdf_text']]
        all_links = set(pdf_data['pdf_links'])
        link_graph = {}

        for depth_key, results in scraping_data['results_by_depth'].items():
            for result in results:
                if result['status'] == 'success':
                    all_text_parts.append(f"\n\n--- Source: {result['url']} ---\n{result['text_content']}")
                    all_links.update(result['links_found'])

                    # Build link graph
                    link_graph[result['url']] = result['links_found'][:5]  # Store first 5 links

        # Combine all text
        combined_text = "".join(all_text_parts)

        # Identify failed URLs
        failed_urls = []
        for depth_key, results in scraping_data['results_by_depth'].items():
            for result in results:
                if result['status'] == 'failed':
                    failed_urls.append({
                        'url': result['url'],
                        'error': result['error']
                    })

        return {
            'execution_id': hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12],
            'started_at': datetime.now().isoformat(),
            'completed_at': datetime.now().isoformat(),
            'execution_time_seconds': execution_time,

            'source_pdf': {
                'file_path': pdf_data['pdf_metadata'].get('file_path', ''),
                'file_name': pdf_data['pdf_metadata'].get('file_name', ''),
                'page_count': pdf_data['pdf_metadata'].get('page_count', 0),
                'file_size_bytes': pdf_data['pdf_metadata'].get('file_size_bytes', 0),
                'text_length': len(pdf_data['pdf_text']),
                'links_extracted': len(pdf_data['pdf_links'])
            },

            'scraping_results': scraping_data['statistics'],

            'combined_data': {
                'all_text': combined_text,
                'all_text_length': len(combined_text),
                'all_links': sorted(list(all_links)),
                'unique_links_count': len(all_links),
                'link_graph': link_graph
            },

            'errors': {
                'failed_urls': failed_urls,
                'total_failed': len(failed_urls)
            },

            'statistics': {
                'total_text_chars': len(combined_text),
                'unique_urls_found': len(all_links),
                'pages_with_errors': len(failed_urls),
                'extraction_success_rate': scraping_data['statistics']['success_rate']
            }
        }


async def process_pdf_with_scraping(
    pdf_path: str,
    max_depth: int = 3,
    rate_limit: float = 2.0,
    timeout: int = 30,
    save_output: bool = True,
    output_dir: str = './scraper_output'
) -> Dict:
    """
    Main function: Process PDF and recursively scrape linked websites

    Args:
        pdf_path: Path to PDF file
        max_depth: Maximum recursion depth (default: 3)
        rate_limit: Seconds between requests (default: 2.0)
        timeout: Request timeout in seconds (default: 30)
        save_output: Save results to JSON (default: True)
        output_dir: Output directory for results (default: './scraper_output')

    Returns:
        Dict with combined PDF and scraping data
    """
    start_time = time.time()

    logger.info("=" * 60)
    logger.info("Starting PDF Processing with Recursive Web Scraping")
    logger.info("=" * 60)
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Max Depth: {max_depth}, Rate Limit: {rate_limit}s, Timeout: {timeout}s")

    # Step 1: Extract PDF content
    logger.info("\n[Step 1/3] Extracting PDF content...")
    pdf_extractor = PDFContentExtractor()
    pdf_data = pdf_extractor.extract_pdf_content(pdf_path)

    if not pdf_data['pdf_links']:
        logger.warning("No links found in PDF!")
        execution_time = time.time() - start_time
        result = {
            'pdf_data': pdf_data,
            'scraping_data': {'results_by_depth': {}, 'statistics': {}},
            'execution_time': execution_time
        }
        logger.info(f"Execution completed in {execution_time:.2f} seconds")
        return result

    logger.info(f"Found {len(pdf_data['pdf_links'])} links in PDF")

    # Step 2: Scrape linked websites recursively
    logger.info(f"\n[Step 2/3] Scraping {len(pdf_data['pdf_links'])} initial links recursively...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        recursive_scraper = RecursiveScraper(max_depth=max_depth, rate_limit=rate_limit, timeout=timeout)
        scraping_data = await recursive_scraper.scrape_recursive(pdf_data['pdf_links'], browser)

        await browser.close()

    # Step 3: Combine all data
    logger.info("\n[Step 3/3] Combining PDF and scraping data...")
    execution_time = time.time() - start_time

    combined_result = DataCombiner.combine_all_data(pdf_data, scraping_data, execution_time)

    # Save output if requested
    if save_output:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / f"scrape_result_{combined_result['execution_id']}.json"

        # Convert for JSON serialization
        json_data = json.dumps(combined_result, indent=2, default=str)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)

        logger.info(f"Results saved to: {output_file}")

    logger.info("=" * 60)
    logger.info(f"✓ Execution completed in {execution_time:.2f} seconds")
    logger.info(f"✓ Processed {combined_result['scraping_results']['total_urls_processed']} URLs")
    logger.info(f"✓ Combined text length: {combined_result['statistics']['total_text_chars']} characters")
    logger.info("=" * 60)

    return combined_result


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    import sys

    # Example: Run with a PDF file
    pdf_file = "sample.pdf"  # Change this to your PDF path

    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]

    # Run the scraper
    result = asyncio.run(
        process_pdf_with_scraping(
            pdf_path=pdf_file,
            max_depth=2,
            rate_limit=2.0,
            timeout=30,
            save_output=True,
            output_dir='./scraper_output'
        )
    )

    # Display summary
    print("\n" + "=" * 60)
    print("SCRAPING RESULTS SUMMARY")
    print("=" * 60)
    print(f"\nPDF File: {result['source_pdf']['file_name']}")
    print(f"Pages: {result['source_pdf']['page_count']}")
    print(f"Initial Links Found: {result['source_pdf']['links_extracted']}")

    print(f"\nWeb Scraping:")
    print(f"  Total URLs Processed: {result['scraping_results']['total_urls_processed']}")
    print(f"  Successful: {result['scraping_results']['successful_scrapes']}")
    print(f"  Failed: {result['scraping_results']['failed_scrapes']}")
    print(f"  Duplicates Skipped: {result['scraping_results']['duplicate_urls_skipped']}")
    print(f"  Success Rate: {result['scraping_results']['success_rate']}")

    print(f"\nCombined Data:")
    print(f"  Total Text Length: {result['statistics']['total_text_chars']:,} characters")
    print(f"  Unique URLs Found: {result['statistics']['unique_urls_found']}")
    print(f"  Failed URLs: {result['errors']['total_failed']}")
    print(f"  Execution Time: {result['execution_time_seconds']:.2f} seconds")

    print("\n" + "=" * 60)

    # Display first 500 chars of combined text
    print("\nFirst 500 characters of combined data:")
    print("-" * 60)
    print(result['combined_data']['all_text'][:500])
    print("...")
    print("-" * 60)
