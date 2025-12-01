import os
import uuid
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from PyPDF2 import PdfMerger
from job_manager import job_status


async def download_all_pages(
    job_id: str,
    start_url: str,
    base_url: str,
    next_selector: str,
    output_filename: str,
    dark_mode: bool
):
    os.makedirs("output", exist_ok=True)
    merger = PdfMerger()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(color_scheme="dark" if dark_mode else "light")

        current_url = start_url
        index = 1

        while current_url:
            job_status[job_id] = {
                "status": "running",
                "current_page": index,
                "message": f"Downloading page {index}",
                "done": False,
            }

            await page.goto(current_url, wait_until="networkidle")

            if dark_mode:
                await page.evaluate("() => document.documentElement.classList.add('dark')")

            pdf_path = f"output/page_{index}.pdf"
            await page.pdf(path=pdf_path, format="A4", print_background=True)
            merger.append(pdf_path)

            next_btn = page.locator(next_selector)
            if await next_btn.count() == 0:
                break

            next_href = await next_btn.get_attribute("href")
            if not next_href:
                break

            current_url = urljoin(base_url, next_href)
            index += 1

        merged_path = f"output/{output_filename}"
        merger.write(merged_path)
        merger.close()
        await browser.close()

    job_status[job_id] = {
        "status": "completed",
        "done": True,
        "message": "PDF generated",
        "filename": output_filename
    }

    return merged_path
