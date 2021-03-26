from requests_html import HTMLSession
from svcinfo import ServiceInfoSummary, ServiceInfo
import re
import csv


class AwsProdScraper:
    """Crawls the AWS Products page to discover and document all the products AWS offers.

    Uses requests_html, an open-source library for issues HTTP requests and processing results.
    """

    def __init__(self):
        self.session = HTMLSession()
        self.response = None
        self.content_items = None
        self.service_catalog = []   # Gets filled up with ServiceInfo objects

    def init_response(self, url, render=False):
        """Initializes the HTTP response. Call before doing any processing.

        If render == True, this instructs requests_html to interpret and execute any JavaScript
        it encounters on the downloaded HTML page. Empirical testing demonstrated that none of the
        AWS product pages used JavaScript to render what we need, so I defaulted this to False.
        """
        response = self.session.get(url)
        self.response = response
        if render:
            self.response.html.render()

    def build_service_catalog_summary(self):
        """Builds a summary of AWS services as scraped from the /products page."""
        self._init_products_page()
        for ci in self.content_items:
            raw_html = ci.raw_html.decode("utf-8")
            regex = r"((?<=>) .*(?=<span>))<span>(.*)(?=</span>)"   # felt good figuring this regex out!
            pattern = re.compile(regex)
            result = pattern.findall(raw_html)
            if result:
                service, brief_desc = result[0]
                info_url = next(iter(ci.absolute_links))    # get info URL from the link _set_
                summary = ServiceInfoSummary(service, brief_desc, info_url)
                service_info = ServiceInfo(summary)
                self.service_catalog.append(service_info)

    def display_service_catalog_summary(self):
        """Displays the service catalog summary.

        Consists of a list of ServiceSummaryInfo objects."""
        nservices = 0
        for s in self.service_catalog:
            nservices += 1
            print(f'{nservices}: {s.summary}')

    def build_service_catalog(self):
        """Scrape each product-specific page.

        Consists of a list of ServiceInfo objects.

        Note that AWS is *not* consistent at all with the HTML classes, etc., making scraping a bit of
        a challenge and (like most scraping) rather brittle. The current set of css_patterns seems to cover
        all 240 services accurately and well.
        """
        if self.service_catalog is None:
            self.build_service_catalog_summary()

        # These patterns are used on the various product pages. As of this writing they accurately parse and extract
        # the correct info from the various AWS product pages.
        css_patterns = [
            'div.lb-tiny-align-left.lb-small-align-left.lb-mid-align-left.lb-large-align-left.lb-xlarge-align-left.lb-txt-16.lb-rtxt',
            'div.lb-tiny-align-left.lb-small-align-left.lb-mid-align-left.lb-large-align-left.lb-xlarge-align-left.lb-none-v-margin.lb-rtxt',
            '#aws-page-content > div > div > main > product_desc_div > div.columnbuilder.parbase > div > div.eight.columns > div > div.lead-copy.product_desc_div > div',
            'div.lb-col.lb-tiny-24.lb-mid-16 > div',
            'div.lead-copy.product_desc_div > div',
            'div.lb-tiny-align-left.lb-small-align-left.lb-mid-align-left.lb-large-align-left.lb-xlarge-align-left.lb-rtxt',
            'div.lb-rtxt'
        ]

        # Let's scrape each product page, collect full descriptions, and build up the final catalog by
        # updating the ServiceInfo objects.
        detail_scraper = AwsProdScraper()
        for service in self.service_catalog:
            detail_url = service.summary.info_url
            detail_scraper.init_response(detail_url)

            # Now that we have the page, try finding the full description of the product by applying
            # the each CSS selector in turn, until we find what we're looking for
            for css_selector in css_patterns:
                product_desc_div = detail_scraper._css_find(css_selector)
                if len(product_desc_div) > 0:
                    product_desc_text = (product_desc_div[0]).full_text
                    service.add_to_full_desc(product_desc_text)
                    break

    def display_service_catalog(self):
        """Displays the service catalog to the console."""
        nservices = 0
        for s in self.service_catalog:
            nservices += 1
            print(f'{nservices}: {s}')

    def save_service_catalog(self):
        """Saves the entire service catalog to a CSV file."""
        assert self.service_catalog is not None
        with open('aws-product-catalog.csv', mode='w') as f:
            product_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            product_writer.writerow(['Service Name', 'Brief Desc', 'Summary URL', 'Full Description']);
            for svc in self.service_catalog:
                product_writer.writerow([svc.summary.service_name, svc.summary.brief_desc,
                                         svc.summary.info_url, svc.full_desc])

    def _css_find(self, css_selector):
        """Finds the given HTML elements based on the given CSS selector."""
        return self.response.html.find(css_selector)

    def _init_products_page(self):
        """Finds the list of products from the aws.amazon.com/products/ page."""
        assert self.response.html is not None
        self.content_items = self._css_find('div.lb-content-item')
