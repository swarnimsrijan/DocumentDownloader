import os
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from PyPDF2 import PdfMerger


async def download_all_pages(
    start_url: str,
    base_url: str,
    next_selector: str,
    output_filename: str = "merged.pdf",
    dark_mode: bool = False,
) -> str:
    """
    Crawl documentation pages using a "next" link selector,
    print each page to PDF, merge them, and return the merged file path.
    """

    os.makedirs("output", exist_ok=True)
    merged_path = os.path.join("output", output_filename)

    merger = PdfMerger()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            color_scheme="dark" if dark_mode else "light"
        )

        current_url = start_url
        index = 1

        while current_url:
            print(f"[Downloader] Visiting: {current_url}")
            await page.goto(current_url, wait_until="networkidle")

            # Force dark mode via CSS class, if requested
            if dark_mode:
                await page.evaluate(
                    """() => { document.documentElement.classList.add('dark'); }"""
                )

            pdf_path = os.path.join("output", f"page_{index}.pdf")
            await page.pdf(path=pdf_path, format="A4", print_background=True)
            merger.append(pdf_path)

            # Find next button
            next_btn = page.locator(next_selector)
            if await next_btn.count() == 0:
                print("[Downloader] No more next pages. Stopping.")
                break

            next_href = await next_btn.get_attribute("href")
            if not next_href:
                break

            # Resolve relative URLs against base_url
            current_url = urljoin(base_url, next_href)
            index += 1

        merger.write(merged_path)
        merger.close()
        await browser.close()

    print(f"[Downloader] Merged PDF created at: {merged_path}")
    return merged_path
