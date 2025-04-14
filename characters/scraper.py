import asyncio
import time
import httpx
from django.conf import settings
from httpx import AsyncClient

from characters.models import Character


GRAPHQL_QUERY = """
query($page: Int!) {
  characters(page: $page) {
    info {
      pages
    }
    results {
      api_id: id
      name
      status
      gender
      image
    }
  }
}
"""

def parse_characters_response(characters_response: dict) -> list[Character]:
    if "data" not in characters_response:
        print("⚠️ Invalid response received:", characters_response)
        raise ValueError("No 'data' in GraphQL response")

    return [
        Character(**character_dict)
        for character_dict in characters_response["data"]["characters"]["results"]
    ]


async def fetch_page(client: AsyncClient, url: str, page: int) -> list[Character]:
    response = await client.post(
        url,
        json={"query": GRAPHQL_QUERY, "variables": {"page": page}}
    )
    return parse_characters_response(response.json())


async def scrape_characters() -> list[Character]:
    start = time.perf_counter()
    url = settings.RICK_AND_MORTY_API_CHARACTERS_URL

    response = httpx.post(
        url,
        json={"query": GRAPHQL_QUERY, "variables": {"page": 1}}
    )
    data = response.json()
    num_pages = data["data"]["characters"]["info"]["pages"]
    characters = parse_characters_response(data)

    async with AsyncClient() as client:
        tasks = [fetch_page(client, url, page) for page in range(2, num_pages + 1)]
        pages_characters = await asyncio.gather(*tasks)
        for page in pages_characters:
            characters.extend(page)

    print("Elapsed for scraping:", time.perf_counter() - start)
    return characters


async def save_characters(characters: list[Character]) -> None:
    start = time.perf_counter()
    await Character.objects.abulk_create(characters, ignore_conflicts=True)
    print("Elapsed for saving:", time.perf_counter() - start)


async def sync_characters_with_api() -> None:
    characters = await scrape_characters()
    await save_characters(characters)
