import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from finecobank.items import Article


class FinecoSpider(scrapy.Spider):
    name = 'fineco'
    start_urls = ['https://finecobank.co.uk/public/newsroom/']

    def parse(self, response):
        heading = response.xpath('//div[@class="col-12 col-md-6 offset-md-3 col-lg-6 offset-lg-3"]/a/@href').get()
        yield response.follow(heading, self.parse_article)

        links = response.xpath('//div[@class="col-12 col-md-6 col-lg-4 mb-8"]/a[last()]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="text-grey note"]/span[@class="pl-2"]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d/%m/%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="mt-6"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        category = response.xpath('//p[@class="text-grey note"]/span[1]/text()').get()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()
