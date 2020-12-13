import scrapy
from urllib.parse import urlencode
API = '95413e818c49686b5d90a4bd8834bb54'

def get_url(url):
    payload = {'api_key': API, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['api.scraperapi.com']
    custom_settings = {'CONCURRENT_REQUESTS_PER_DOMAIN': 5}

    def start_requests(self):
        url = f'https://www.instagram.com/{0}/'.format('underwaterstuffs')
        yield scrapy.Request(get_url(url), callback=self.parse)

    def parse(self, response):
        data={}
        posts=response.css('article div div')
        for group_posts in posts:
            for post in group_posts:
                data['image'] = post.css('img::attr(src)')
                data['text'] = post.css('img::attr(alt)')
                yield data
