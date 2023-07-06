import scrapy


class QuotesSpider(scrapy.Spider):
    name = "scribe"
    start_urls = [
        'https://directory.doabooks.org/discover?filtertype=classification_text&filter_relational_operator=equals&filter=Sociology&locale-attribute=en'
    ]

    def parse(self, response):
        for link in response.css('div.row.ds-artifact-item div.col-sm-8.artifact-description a::attr(href)'):
            yield response.follow(f'https://directory.doabooks.org/{link.get()}', callback=self.parse_book)
        next_page = response.xpath("//a[@class='next-page-link']/@href").get()
        if next_page:
            yield response.follow(f'https://directory.doabooks.org/{next_page}', callback=self.parse)

    def parse_book(self, response):
        # name
        name = response.xpath('//*[@id="aspect_versioning_VersionNoticeTransformer_div_item-view"]/div/div[1]/h2/text()').extract_first()

        # authors
        authors = response.xpath("//div[@class='ds-dc_contributor_author-authority']/text()").extract_first()
        if not authors:
            authors = str()
            for contributor in response.xpath("//div[@class='simple-item-view-contributors item-page-field-wrapper table']/div/text()").getall():
                authors += contributor

        # language
        language = response.xpath("//h5[text()='Language']/parent::div/text()").getall()[1]

        # keywords
        keywords = response.xpath('//*[@id="aspect_versioning_VersionNoticeTransformer_div_item-view"]/div/div[2]/div[2]/div[3]/text()').getall()[1],

        # uri
        uri = response.xpath("//h5[text()='URI']/following-sibling::span/a/text()").get()

        # date_and_place
        date_and_place = response.xpath("//h5[text()='Publication date and place']/parent::div/text()").getall()[1]

        # pages
        pages = response.xpath("//h5[text()='Pages']/parent::*/text()").getall()
        if not pages:
            pages = "I don't know"
        else:
            pages = pages[1]

        # конечная информация о книге (словарь)
        book = {
            'name': name,
            'authors': authors,
            'language': language,
            'Keywords': keywords[0],
            'URI': uri,
            'Publication date and place': date_and_place,
            'Pages': pages
        }
        yield book
