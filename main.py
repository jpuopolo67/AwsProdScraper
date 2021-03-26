# AwsProdScraper
# John Puopolo, March 2021

from awsscraper import AwsProdScraper

# Scrapes the aws.amazon.com/products page and extracts summary information for all
# available AWS products. It then crawls each specific product page to get more information.
# At the end of the run, it saves its results to a CSV file.

if __name__ == '__main__':
    scraper = AwsProdScraper()
    scraper.init_response('https://aws.amazon.com/products/')
    scraper.build_service_catalog_summary()
    scraper.build_service_catalog()
    scraper.save_service_catalog()


