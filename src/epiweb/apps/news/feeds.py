from django.contrib.syndication.feeds import Feed
from cmsplugin_news.models import News

class NewsEntryFeed(Feed):
    title = "News"
    link = "http://localhost:8000/new/"
    description = "News"

    def items(self):
        return News.published.all()[:10]
    
    def item_pubdate(self, item):
        return item.pub_date

