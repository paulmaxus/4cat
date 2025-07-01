"""
"""
import asyncio

from backend.lib.search import Search
from common.lib.helpers import UserInput
from datasources.tiktok.search_tiktok import SearchTikTok as SearchTikTokByImport
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
    extension = "ndjson"  # extension of result file, used internally and in UI
    is_local = False  # Whether this datasource is locally scraped
    is_static = False  # Whether this datasource is still updated

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
            "help": "This data source can retrieve video from TikTok posts based on a list of URLs for those "
                    "posts.\n\nEnter a list of TikTok post URLs."
        },
        "amount": {
            "type": UserInput.OPTION_TEXT,
            "help": "No. of videos (max 1000)",
            "default": 100,
            "min": 0,
            "max": 1000,
            "tooltip": "Due to simultaneous downloads, you may end up with a few extra videos."
        },
        "urls": {
            "type": UserInput.OPTION_TEXT_LARGE,
            "help": "Post URLs",
            "tooltip": "Separate by commas or new lines."
        }

    }

    def get_items(self, query):
        """
        Retrieve metadata for TikTok URLs

        :param dict query:  Search query parameters
        """
        # Prepare staging area for downloads
        results_path = self.dataset.get_staging_area()
        
        tiktok_scraper = TikTokScraper(processor=self, config=self.config)
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(tiktok_scraper.download_videos(query["ids"].split(","), results_path, query["amount"]))

    @staticmethod
    def validate_query(query, request, user):
        params = SearchTikTokByID.validate_query(query, request, user)
        # get ids from urls
        params["ids"] = ",".join([url.split("/")[-1] for url in params["urls"].split(",")])
        # add amount
        params["amount"] = query.get("amount", 0)
        return params