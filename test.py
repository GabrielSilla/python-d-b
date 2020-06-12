import scrapy
import json
import re
import os
import logging
from urllib.parse import urlparse

class TestSpider(scrapy.Spider):
    name = 'd&b_test'
    logger = None

    def start_requests(self):
        self.set_configs()
        f = open("input.txt", "r")
        for x in f:
           yield scrapy.Request(url=x, callback=self.parse)

    def set_configs(self):
        open('results.json', 'w').close()

        logger = logging.getLogger()
        fhandler = logging.FileHandler(filename='test.log', mode='a')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)
        self.logger = logger

    def parse(self, response):
        try:
            self.logger.info('STARTED - ' + response.url)
            response_body = str(response.xpath('.//body').extract())
            
            phones = self.get_phones(response_body)
            logo = self.get_logo(response)
            
            obj = {
                'logo': logo,
                'phones': phones,
                'website': response.url
            }

            self.logger.info('WRITING RESULT')
            with open("results.json", "a") as f:
                f.write(json.dumps(obj) + '\n')
            self.logger.info('FINISHED')
        except Exception as ex:
            self.logger.error(ex)

    def text_containing_logo(self, text):
        return "logo" in text

    def get_phones(self, body):
        regex = r'\+?\d*\s?\(?\d{1,}\)?[\d\s\-]{8,}'

        self.logger.info('GETTING PHONE NUMBERS')
        result = re.findall(regex, body)
        formatted_phones = []
        for phone in result:
            phone = phone.strip()
            phone = phone.replace('/','').replace('-', '')
            if len(phone) > 6:
                formatted_phones.append(phone)

        return formatted_phones

    def get_logo(self, response):
        self.logger.info('GETTING LOGO URL')
        images = response.xpath('.//header//img/@src').extract()
        filtered_images = filter(self.text_containing_logo, images)
        logos = list(filtered_images)

        if len(logos) > 0:
            if self.is_absolute(logos[0]):
                return logos[0]
            else:
                parsedUrl = urlparse(response.url)
                return '{uri.scheme}://{uri.netloc}{logo}'.format(uri=parsedUrl, logo=logos[0])


    def is_absolute(self, url):
        return bool(urlparse(url).netloc)