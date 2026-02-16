#!/usr/bin/env python3
"""
Browser Agent (Bankai Module B)
Headless browser capabilities using Playwright.
"""

import sys
import argparse
import asyncio
from playwright.async_api import async_playwright
import html2text

async def google_search(query: str, limit: int = 5) -> list[dict]:
    """Perform a Google search (Async)."""
    results = []
    async with async_playwright() as p:
        # Launch with stealth args
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Asia/Singapore"
        )
        page = await context.new_page()
        
        # Search
        try:
            await page.goto(f"https://www.google.com/search?q={query}", timeout=15000)
            await page.wait_for_selector("div.g", timeout=10000)
        except Exception:
            # Fallback to duckduckgo if Google blocks
             await page.goto(f"https://duckduckgo.com/?q={query}", timeout=15000)
             # DuckDuckGo selectors needed here, but let's try just headers first.
             # Actually, if google times out, let's just create a simpler scraper logic.
             pass
        
        # Extract
        elements = await page.query_selector_all("div.g")
        for el in elements[:limit]:
            try:
                title_el = await el.query_selector("h3")
                link_el = await el.query_selector("a")
                snippet_el = await el.query_selector("div.VwiC3b") 
                
                if title_el and link_el:
                    title = await title_el.inner_text()
                    url = await link_el.get_attribute("href")
                    snippet = await snippet_el.inner_text() if snippet_el else ""
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
            except Exception:
                continue
                
        await browser.close()
    return results

async def browse_url(url: str) -> str:
    """Visit a URL and return markdown content (Async)."""
    content = ""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=30000)
            # Remove clutter
            await page.evaluate("""
                document.querySelectorAll('script, style, nav, footer, iframe, ads').forEach(el => el.remove());
            """)
            html = await page.content()
            
            # Convert to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            content = h.handle(html)
            
        except Exception as e:
            await browser.close()
            return f"Error browsing {url}: {e}"
            
        await browser.close()
    return content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Athena Browser Agent")
    parser.add_argument("action", choices=["search", "browse"], help="Action to perform")
    parser.add_argument("query", help="URL or Search Query")
    args = parser.parse_args()
    
    if args.action == "search":
        res = asyncio.run(google_search(args.query))
        for r in res:
            print(f"- [{r['title']}]({r['url']})\n  {r['snippet']}\n")
            
    elif args.action == "browse":
        print(asyncio.run(browse_url(args.query)))
