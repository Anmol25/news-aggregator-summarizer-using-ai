import asyncio
from .feed_parser import FeedParser  # Relative import


class RssFeed:
    def __init__(self):
        self._articles = None

    @classmethod
    def get_articles(self):
        """
        Get Articles
        Returns:
            articles: articles stored in current object
        """
        return self._articles

    @classmethod
    def set_articles(self, articles: dict):
        """
        Update Articles
        Args:
            articles: dict of articles topic wise
        """
        self._articles = articles

    @staticmethod
    async def fetch_articles(feeds: dict, model, device: str) -> dict:
        """
        Fetch and Parse RSS Feeds

        Args:
            feeds: Rss Feeds in form of a dictionary
            model: Embedding creation model to be used remove duplicate headlines
            device: Device to run model on (CPU/GPU)
        Returns:
            data: Articles Topicwise in a dict format
        """
        rss_feeds = feeds
        results = []
        for topic in rss_feeds:
            results.append(FeedParser.fetch_topics_feed(rss_feeds[topic]))

        responses = await asyncio.gather(*results)

        articles = {}
        for topic, xml_data in zip(rss_feeds, responses):
            articles[topic] = FeedParser.parse_feed(xml_data, model, device)
        return articles

    @classmethod
    async def refresh_articles(self, feeds: dict, model, device: str) -> dict:
        """
        Refreshes and Updates Articles

        Args:
            feeds: Rss Feeds in form of a dictionary
            model: Embedding creation model to be used remove duplicate headlines
            device: Device to run model on (CPU/GPU) 
        """
        articles = await RssFeed.fetch_articles(feeds, model, device)
        self._articles = articles
