"""
Download TikTok videos from URLs
"""
import asyncio

from backend.lib.search import Search
from common.lib.helpers import UserInput
from datasources.tiktok_urls.search_tiktok_urls import SearchTikTokByID, TikTokScraper
from common.config_manager import config

class SearchTikTokVideo(Search):
    """
    Download TikTok videos
    """
    type = "tiktok-videos-search"  # job ID
    category = "Search"  # category
    title = "Search TikTok Videos by post URL"  # title displayed in UI
    description = "Retrieve videos for TikTok post URLs."  # description displayed in UI
    extension = "zip"  # extension of result file, used internally and in UI
    is_local = False  # Whether this datasource is locally scraped
    is_static = False  # Whether this datasource is still updated
    max_workers=4

    # not available as a processor for existing datasets
    accepts = [None]

    config = {
        "tiktok-urls-search.proxies": {
            "type": UserInput.OPTION_TEXT_JSON,
            "default": [],
            "help": "Proxies for TikTok data collection"
        },
        "tiktok-urls-search.proxies.wait": {
            "type": UserInput.OPTION_TEXT,
            "coerce_type": float,
            "default": 0,
            "help": "Request wait",
            "tooltip": "Time to wait before sending a new request from the same IP"
        }
    }

    options = {
        "intro": {
            "type": UserInput.OPTION_INFO,
            "help": "This data source can retrieve videos from TikTok posts based on a list of URLs for those "
                    "posts.\n\nEnter a list of TikTok post URLs."
        },
        "urls": {
            "type": UserInput.OPTION_TEXT_LARGE,
            "help": "Post URLs",
            "tooltip": "Separate by commas or new lines."
        }

    }

    def get_items(self, query):
        """
        Retrieve videos from TikTok URLs

        :param dict query:  Search query parameters
        """
        # Prepare staging area for downloads
        results_path = self.dataset.get_staging_area()
        
        tiktok_scraper = TikTokScraper(processor=self, config=self.config)
        loop = asyncio.new_event_loop()
        results = loop.run_until_complete(
            tiktok_scraper.download_videos(query["ids"].split(","), results_path, query["amount"])
        )
        return results_path

    @staticmethod
    def validate_query(query, request, user):
        params = SearchTikTokByID.validate_query(query, request, user)
        urls = params["urls"].split(",")
        # get ids from urls
        params["ids"] = ",".join([url.split("/")[-1] for url in urls])
        # amount = total amount
        params["amount"] = len(urls)
        return params