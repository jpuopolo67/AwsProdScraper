import os


class ServiceInfoSummary:
    """Stores AWS service summary info including name, a (very) brief description and a product page URL."""
    def __init__(self, service_name, brief_desc, info_url):
        self.service_name = service_name.strip()
        self.brief_desc = brief_desc.strip()
        self.info_url = info_url

    def __repr__(self):
        return f'("{self.service_name}", "{self.brief_desc}", {self.info_url})'


class ServiceInfo:
    """Stores info about each AWS service.

    Contains a ServiceInfoSummary and a full description scraped from the specific product page.
    """
    def __init__(self, service_info_summary):
        self.summary = service_info_summary
        self.full_desc = ''

    def __repr__(self):
        summary_string = str(self.summary)
        return summary_string + self.full_desc

    def add_to_full_desc(self, text):
        text = text.strip()
        text = text.replace('\n', ' ')
        self.full_desc += text

