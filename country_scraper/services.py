import scrapy
from scrapy.crawler import CrawlerRunner
from crochet import setup, wait_for
import json
import asyncio
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from twisted.web._newclient import ResponseFailed
import logging


# Initialize Crochet
setup()

scraped_data = {}
errors = {}


class CountrySpider(scrapy.Spider):
    name = 'country_spider'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'HTTPERROR_ALLOW_ALL': True,
    }

    def __init__(self, criteria, *args, **kwargs):
        super(CountrySpider, self).__init__(*args, **kwargs)
        self.criteria = criteria
        self.start_urls = [self.build_url()]
        self.country_data = []
        self.error = None

    def build_url(self):
        base_url = 'https://restcountries.com/v3.1'
        if self.criteria.get('name'):
            return f"{base_url}/name/{self.criteria['name']}"
        if self.criteria.get('capital'):
            return f"{base_url}/capital/{self.criteria['capital']}"
        if self.criteria.get('region'):
            return f"{base_url}/region/{self.criteria['region']}"
        if self.criteria.get('subregion'):
            return f"{base_url}/subregion/{self.criteria['subregion']}"
        if self.criteria.get('language'):
            return f"{base_url}/lang/{self.criteria['language']}"
        if self.criteria.get('currency'):
            return f"{base_url}/currency/{self.criteria['currency']}"
        return base_url

    def start_requests(self):
        for url in self.start_urls:
            logging.info(f"Requesting URL: {url}")
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self.errback,
                dont_filter=True,
            )

    def parse(self, response):
        logging.info(f"Received response with status {response.status}")
        if response.status == 200:
            data = json.loads(response.text)
            if data:
                self.country_data.extend(data)
            else:
                self.error = {'status': 404, 'message': 'Country not found.'}
        elif response.status == 404:
            self.error = {'status': 404, 'message': 'Country not found.'}
        else:
            self.error = {
                'status': response.status,
                'message': 'An error occurred while fetching data.'
            }

    def errback(self, failure):
        logging.error(f"Request failed with error: {failure}")
        if failure.check(DNSLookupError):
            self.error = {'status': 503, 'message': 'DNS Lookup Error.'}
        elif failure.check(TimeoutError, TCPTimedOutError, ResponseFailed):
            self.error = {'status': 504, 'message': 'Connection timed out.'}
        else:
            self.error = {'status': 500, 'message': 'An unexpected error occurred.'}


runner = CrawlerRunner()


@wait_for(timeout=10)
def run_spider(criteria_key, criteria_value):
    global scraped_data, errors
    # Create a unique key for storing results
    result_key = f"{criteria_key}:{criteria_value}"
    crawler = runner.create_crawler(CountrySpider)
    deferred = runner.crawl(crawler, criteria={criteria_key: criteria_value})

    def get_data(_):
        if crawler.spider.error:
            logging.error(f"Error from spider: {crawler.spider.error}")
            errors[result_key] = crawler.spider.error
        else:
            logging.info("Spider completed successfully.")
            scraped_data[result_key] = crawler.spider.country_data

    deferred.addCallback(get_data)
    return deferred


async def fetch_country_info(
    name=None,
    capital=None,
    region=None,
    subregion=None,
    language=None,
    currency=None
):
    global scraped_data, errors
    # Determine which criterion is being used
    criteria = {
        'name': name,
        'capital': capital,
        'region': region,
        'subregion': subregion,
        'language': language,
        'currency': currency,
    }

    criteria = {k: v for k, v in criteria.items() if v is not None}

    # Input validation
    if not criteria:
        return {"error": "No search criteria provided.", "status": 400}
    if len(criteria) > 1:
        return {
            "error": "Please provide only one search criterion at a time.",
            "status": 400
        }

    criteria_key, criteria_value = next(iter(criteria.items()))
    result_key = f"{criteria_key}:{criteria_value}"

    # Check if result is already available
    if result_key in scraped_data:
        return scraped_data.pop(result_key)
    if result_key in errors:
        error = errors.pop(result_key)
        return error

    # Run the spider
    try:
        run_spider(criteria_key, criteria_value)
    except Exception as e:
        logging.error(f"Exception occurred while running spider: {e}")
        return {"error": "An error occurred while processing your request.", "status": 500}

    while result_key not in scraped_data and result_key not in errors:
        await asyncio.sleep(0.1)

    if result_key in errors:
        error = errors.pop(result_key)
        return error
    return scraped_data.pop(result_key)
