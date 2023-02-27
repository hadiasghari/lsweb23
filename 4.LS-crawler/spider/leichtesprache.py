# Scrapy Spider to save LeichteSprache pages found through a list of websites
# Author: Hadi Asghari
# Version: 2023.02

from os import mkdir, path
import logging
from urllib.parse import urlparse
import scrapy
import tldextract
import html2text


class LeichteSpracheSpider(scrapy.Spider):
    name = 'LeichteSprache'
    start_urls = []
    url_files = ['sitelist.txt',]  # input: lists of sites to scan (e.g. one for each state)
    DIR_SAVEPAGE = "savedpages"  # output directory (location of saved pages)

    def __init__(self):
        if not path.exists(self.DIR_SAVEPAGE):
            mkdir(self.DIR_SAVEPAGE)
        for uf in self.url_files:
            for line in open(uf, "rt"):
                if not line.startswith('#'):
                    if not line.lowercase().startswith("http"):
                        assert '://' not in line  # scheme must be http:// or https:// or empty
                        line = "http://" + line
                    self.start_urls.append(line)
        # warn if domain is not .de -- although this can be well valid for regional tlds
        for url in self.start_urls:
            dom = tldextract.extract(url).registered_domain
            if not dom.endswith(".de"):
                logging.info(f' __init__(): non .de domain <{url}>')
        #
        logging.info(f' __init__(): loaded {len(self.start_urls)} urls to crawl')

    def parse(self, response):
        """Find all links matching patterns typically used for LS pages; and save the page text"""

        # ignore non-text pages (eg mp3s or pdfs)
        # (note, errors of 404, 500, DNS will be logged as INFO/ERROR by Scrapy and don't end up here)
        try:
            response.text
        except AttributeError:
            ctype = str(response.headers['Content-Type'])
            logging.debug(f"ignoring `{response.url}` since content is `{ctype}`")
            return

        # find links with the word leicht.+sprach in them.
        # - `de-plein` is used in some states; so also checked
        # - `barrierefrei` often point to a more general declaration, not per se LS, so not checked (many FPs)
        # - we expect LS pages to be linked on the homepage, since this is the law, but we also search on subpages
        # - we ignore non http (e.g. `mailto`, `javascript:`) schemes, and also links outside current domain
        urls_ls = set()
        for anode in response.xpath('//a'):
            ahref = anode.xpath('@href').get()
            atext = str(anode.getall()).lower()
            if not ahref:
                continue
            ahrefsplit = urlparse(ahref.lower())
            if ahrefsplit.scheme and ahrefsplit.scheme not in ['http', 'https']:
                continue
            if ahrefsplit.scheme in ['http', 'https']:
                adom = tldextract.extract(ahrefsplit.netloc).registered_domain
                thisdom = tldextract.extract(response.url).registered_domain
                if adom != thisdom:
                    continue
            if ("leicht" in atext and "sprach" in atext) or "de-plain" in atext:
                urls_ls.add(ahref)

        # check if we are on a subpage crawl -- and save the page if so
        # - for the results/stats file, we keep the home/startpage as an identifier
        if 'home' in response.meta:
            home = response.meta['home']
            self.savepage(response)
            start = False
        else:
            home = response.request.url.replace("http://", "").replace("https://", "")
            start = True

        yield {'start': start,
               'start_url': home,
               'url': response.url,
               'ls_sublinks': len(urls_ls)}

        # Continue crawling subpages (this is where LS pages will be saved)
        # - duplicate URLs are already ignored by Scrapy
        # - don't crawl URLs ending with mp3/pdf (to save speed)
        for url in urls_ls:
            if url.endswith('.mp3') or url.endswith(".pdf"):
                logging.debug(f'ignoring link with bad href `{response.url}` → `{url}`!')
                continue
            yield response.follow(url, callback=self.parse, meta={"home": home})

    def savepage(self, response):
        """Save the HTML & TEXT of the retrieved webpage"""
        logging.debug("savepage() for: " + str(response.url))

        # make the filename
        # (note: this might benefit from truncating if the filename is too long; also making sure it is unique)
        filename = response.url.split("/")[2]
        if filename.startswith("www."):
            filename = filename[4:]
        page = response.url.split("/")[-1]
        if '?' in page:
            page = page.split("?")[0].replace("?", "")
        if page.endswith(".html"):
            page = page[:-5]
        filename += "__" + page

        # save HTML
        with open(self.DIR_SAVEPAGE + "/" + filename + ".html", 'wb') as f:
            f.write(response.body)

        # save text (with HTML2Text) -- which makes it easier for textual analysis
        with open(self.DIR_SAVEPAGE + "/" + filename + ".txt", 'wt') as f:
            f.write(response.url + "\n\n")  # save the URL too
            # select, if possible, only the main content using some tags.
            el = response.xpath('//main|//div[@role="main"]|//section[@role="main"]|//div[@class="main-row"]|//div[@class="main"]|//div[@id="main"]')
            if el:
                src = "\n".join(el.getall())
                if len(el) > 1:
                    logging.info(f'page has {len(el)} main tags {response.url}')
            else:
                logging.info(f'page has no main tag {response.url}')
                src = response.text
            # following conversion works pretty well
            # - more options available at https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_emphasis = True
            h.images_to_alt = True
            h.single_line_break = True
            txt = h.handle(src)
            f.write(txt)
