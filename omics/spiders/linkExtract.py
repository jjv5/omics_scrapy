#!/usr/bin/env python3

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from Bio import Entrez
import urllib
import dpath.util
from extruct.jsonld import JsonLdExtractor

DOMAIN = 'omictools.com'
URL = 'https://%s' % DOMAIN
#URL='https://omictools.com/samtools-tool'
#URL='https://omictools.com/whole-genome-resequencing-category'
URL='https://omictools.com/'

class MySpider(CrawlSpider):
    name = 'linkExtract'
    allowed_domains = [DOMAIN]
    start_urls = [
    URL
    ]
    
    rules = (
        Rule(LinkExtractor(allow=('-tool$')), callback="parse_item"),
        Rule(LinkExtractor(allow=('-category$')) ),
        )

    def removeNonAscii(self,s): return "".join(filter(lambda x: ord(x)<128, s))

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        
        # Fields to output for each tool
        my_keys=['@id','@type','applicationCategory','name','alternateName','description','url','sameAs','image','genre','softwareVersion','softwareRequirements','operatingSystem','downloadUrl','installUrl']

        #oururl= urlopen(url).read()
        #print(oururl)
        extractor = JsonLdExtractor()
        #with urllib.request.urlopen(url) as response:
        #html_text = response.read().decode('utf-8')
        
        my_items = extractor.extract(response.body_as_unicode(), response.url)

        # If this is a -tool page only:
        #my_items = extractor.extract(html_text)
        this_item=my_items['items'][0]['@graph'][0]
        my_item = {}

        # output all basic items
        for this_key in my_keys:
         #      print(this_key,'\t',this_item[this_key])
         my_item[this_key]=this_item[this_key]

        # get license
        license_type=this_item['license']['@type']
        license_text=self.removeNonAscii(this_item['license']['text'])
        #   print('license_type','\t',license_type)
        #   print('license_text','\t',license_text)
        my_item['license_type']=license_type
        my_item['license_text']=license_text


        # Get pmcrefcount of first only  
        Entrez.email = "vincent@hkl.hms.harvard.edu"
        first_pub = this_item['publication'][0]
        pmcrefcount=0
        if 'pubmed' in first_pub['url']:
            this_pmid = first_pub['url'].split('/')[-1:]
            pmcrefcount=Entrez.read(Entrez.efetch(db="pubmed", id=this_pmid, rettype="docsum"))[0]['PmcRefCount']
        #   print('primary_pub','\t',first_pub['name'])
        #   print('primary_pub_url','\t',first_pub['url'])
        #   print('primary_pub_pmcrefcount','\t',pmcrefcount)
        my_item['primary_pub']=first_pub['name']
        my_item['primary_pub_url']=first_pub['url']
        my_item['primary_pub_pmcrefcount']=pmcrefcount

        #return my_item
  
        yield my_item
        return my_item
