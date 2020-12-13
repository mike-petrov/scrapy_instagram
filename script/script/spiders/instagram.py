import scrapy

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/{0}/'.format('underwaterstuffs')]

    def parse(self, response):
        data={}
        posts=response.css('article div div')
        for group_posts in posts:
            for post in group_posts:
                data['image'] = post.css('img::attr(src)')
                data['text'] = post.css('img::attr(alt)')
                yield data
