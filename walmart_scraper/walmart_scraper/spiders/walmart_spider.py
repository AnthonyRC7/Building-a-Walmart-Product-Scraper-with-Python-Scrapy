import json
# import math
import scrapy
from urllib.parse import urlencode
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest


# To get a specific number of pages*************************************************
class WalmartSpider(ScrapingBeeSpider):
    name = "walmart_spider"

    def start_requests(self):
        keyword_list = ['ipad']
        for keyword in keyword_list:
            for page_num in range(4, 5):
                payload = {'q': keyword, 'sort': 'best_seller', 'page': page_num, 'affinityOverride': 'default'}
                walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)

                yield ScrapingBeeRequest(url=walmart_search_url,
                                         params={
                                             'render_js': False,
                                             'premium_proxy': False,
                                         },
                                         callback=self.parse_search_results
                                         )

    def parse_search_results(self, response):
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)

            # Request Product Page
            product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
            for product in product_list:
                walmart_product_url = 'https://www.walmart.com' + product.get('canonicalUrl', '').split('?')[0]
                yield ScrapingBeeRequest(url=walmart_product_url,
                                         params={
                                             'render_js': False,
                                             'premium_proxy': False,
                                         },
                                         callback=self.parse_product_data,
                                         )

    def parse_product_data(self, response):
        script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        if script_tag is not None:
            json_blob = json.loads(script_tag)
            raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
            yield {
                'id': raw_product_data.get('id'),
                'type': raw_product_data.get('type'),
                'name': raw_product_data.get('name'),
                'brand': raw_product_data.get('brand'),
                'averageRating': raw_product_data.get('averageRating'),
                'manufacturerName': raw_product_data.get('manufacturerName'),
                'shortDescription': raw_product_data.get('shortDescription'),
                'thumbnailUrl': raw_product_data['imageInfo'].get('thumbnailUrl'),
                'price': raw_product_data['priceInfo']['currentPrice'].get('price'),
                'currencyUnit': raw_product_data['priceInfo']['currentPrice'].get('currencyUnit'),
            }


# To get all products from all the pages*******************************************************
# class WalmartSpider(ScrapingBeeSpider):
#     name = "walmart_spider"
#
#     def start_requests(self):
#         keyword_list = ['ipad']
#         for keyword in keyword_list:
#             payload = {'q': keyword, 'sort': 'best_seller', 'page': 1, 'affinityOverride': 'default'}
#             walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
#             yield ScrapingBeeRequest(url=walmart_search_url,
#                                      params={
#                                          'render_js': False,
#                                          'premium_proxy': False,
#                                      },
#                                      callback=self.parse_search_results,
#                                      meta={'keyword': keyword, 'page': 1})
#
#     def parse_search_results(self, response):
#         page = response.meta['page']
#         keyword = response.meta['keyword']
#         script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
#         if script_tag is not None:
#             json_blob = json.loads(script_tag)
#
#             # Request Product Page
#             product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
#             for product in product_list:
#                 walmart_product_url = 'https://www.walmart.com' + product.get('canonicalUrl', '').split('?')[0]
#                 yield ScrapingBeeRequest(url=walmart_product_url,
#                                          params={
#                                              'render_js': False,
#                                              'premium_proxy': False,
#                                          },
#                                          callback=self.parse_product_data,
#                                          meta={'keyword': keyword, 'page': page})
#
#             # Request Next Page
#             if page == 1:
#                 total_product_count = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0][
#                     "count"]
#                 max_pages = math.ceil(total_product_count / 40)
#                 if max_pages > 25:
#                     max_pages = 25
#                 for p in range(2, max_pages):
#                     payload = {'q': keyword, 'sort': 'best_seller', 'page': p, 'affinityOverride': 'default'}
#                     walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
#                     yield ScrapingBeeRequest(url=walmart_search_url,
#                                              params={
#                                                  'render_js': False,
#                                                  'premium_proxy': False,
#                                              },
#                                              callback=self.parse_search_results,
#                                              meta={'keyword': keyword, 'page': p})
#
#     def parse_product_data(self, response):
#         script_tag = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
#         if script_tag is not None:
#             json_blob = json.loads(script_tag)
#             raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
#             yield {
#                 'keyword': response.meta['keyword'],
#                 'page': response.meta['page'],
#                 'id': raw_product_data.get('id'),
#                 'type': raw_product_data.get('type'),
#                 'name': raw_product_data.get('name'),
#                 'brand': raw_product_data.get('brand'),
#                 'averageRating': raw_product_data.get('averageRating'),
#                 'manufacturerName': raw_product_data.get('manufacturerName'),
#                 'shortDescription': raw_product_data.get('shortDescription'),
#                 'thumbnailUrl': raw_product_data['imageInfo'].get('thumbnailUrl'),
#                 'price': raw_product_data['priceInfo']['currentPrice'].get('price'),
#                 'currencyUnit': raw_product_data['priceInfo']['currentPrice'].get('currencyUnit'),
#             }
