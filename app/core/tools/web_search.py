import re
from typing import List
from googlesearch import search
import httpx
from bs4 import BeautifulSoup
import markdownify
import asyncio
from pydantic import BaseModel

class WebPage(BaseModel):
    url: str
    content: str

async def get_relevant_web_pages(query: str) -> List[str]:
    """
    Searches for relevant web pages based on a query, extracts their content,
    and converts it to Markdown format.

    Args:
        query: The search query or a specific URL.

    Returns:
        A list of Markdown-formatted strings representing the content of the
        relevant web pages.
    """

    url_pattern = re.compile(
        r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!$&'()*+,;=.]+$",
        re.IGNORECASE,
    )

    if bool(url_pattern.match(query)):
        urls = [query]
    else:
        urls = list(search(query, num_results=10, region="my"))

    markdown_contents = await asyncio.gather(*[extract_content_as_markdown(url) for url in urls])
    return [content for content in markdown_contents if content is not None]


async def extract_content_as_markdown(url: str) -> str | None:
    """
    Extracts the main content from a web page, converts it to Markdown,
    and returns the Markdown string.

    Args:
        url: The URL of the web page to process.

    Returns:
        A string containing the Markdown-formatted content of the page, or None if an error occurred.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()  

            soup = BeautifulSoup(response.text, "html.parser")
            content_text = str(soup.body)

            markdown_content = markdownify.markdownify(content_text, heading_style="ATX")
            return WebPage(url=url, content=markdown_content)

        except httpx.RequestError as e:
            print(f"Error fetching URL {url}: {e}")
            return None
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return None
