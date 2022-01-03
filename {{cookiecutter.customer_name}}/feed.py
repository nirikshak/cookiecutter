'''
File: feed.py
Copyright: Unbxd, 2022
Owner: Niriksha

Description:
Feed script template for any new onboarding customer accounts.
Usage:
ENV  - $ python3 feed.py --unbxd_api_key=API_KEY --unbxd_site_key=SITE_KEY
'''

import re
import sys
import csv
import os
import json
import xml
import argparse
import codecs
from pyconversion import UnbxdFeedGenerator, UnbxdMain, UnbxdFeedUploader, log
from utils import Helper

FEED_CONFIG_PATH = "utils/sftp_config.json"
TRANSFORMER_CONFIG_PATH = "utils/transformer.json"
SCHEMA_PATH = './utils/schema.json'

#Add raw feed file path and customer name
FILE_PATH = "{{cookiecutter.feed_file_path}}"
CUSTOMER_NAME = "{{cookiecutter.customer_name}}"
SITE_KEY = "{{cookiecutter.site_key}}"
SECRET_KEY = "{{cookiecutter.secret_key}}"

with open(TRANSFORMER_CONFIG_PATH, 'r') as fp:
    transformer = json.load(fp)

class FeedGenerator(UnbxdFeedGenerator):
    @staticmethod
    def read_raw_feed(file_path):
        if file_path.lower().endswith('.csv'):
            data = csv.DictReader(open(file_path), delimiter = ",")
        elif file_path.lower().endswith('.json'):
            with codecs.open(file_path, encoding='utf-8', errors='ignore') as json_obj:
                data = json.load(json_obj)
        elif file_path.lower().endswith('.xml'):
            with open(file_path,'rb') as xml_obj:
                data = xmltodict.parse(xml_obj.read())
        else:
            cv.log.error('Invalid feed file format. Exiting!!')
            sys.exit(9)
        return data

    @staticmethod
    def conversion_attribute_name(pFieldName):
        if pFieldName[0] == '_':
            pFieldName = pFieldName[1:]
        if pFieldName[-1:] == '_':
            pFieldName = pFieldName[:-1]
        formatted_name = re.sub(r'[^\sa-zA-Z0-9\_]', '', pFieldName).strip()
        formatted_name = formatted_name.strip().replace(' ', '_')
        return(formatted_name)

    def to_unbxd_product(self, product: dict) -> dict:
        transformed_product = {}
        for key, value in product.items():
            if key in transformer.keys():
                transformed_product[transformer[key]['name']] = getattr(Helper, transformer[key]['type'])(value)
            else:
                transformed_product[self.conversion_attribute_name(key)] = value
        return transformed_product


    def __parse__(self):
        processed_products = []
        final_products =[]

        data = self.read_raw_feed(FILE_PATH)
        for product in data:
            transformed_product = self.to_unbxd_product(product)
            processed_products.append(transformed_product)

        #Grouping of products and variant logic - only for catalog with variants
        final_products = getattr(Helper, 'merging_products')(processed_products)
        return final_products

class Main(UnbxdMain):
    def __init__(self):
        UnbxdMain.__init__(self)
        self.UNBXD_UNIQUE_ID_FIELD = "uniqueId"
        self.FIELD_SCHEMA_MAPPING = self.getSchema()
        self.GLOBAL_CONFIG = {
            'verbosity': 'debug',
            'log': f'/mnt/{CUSTOMER_NAME}/{SITE_KEY}/full/feedconverter.log',
            'api_version': 'API_VERSION_1',
            'folder': f'/mnt/{CUSTOMER_NAME}/{SITE_KEY}/full/',
            'default_data_type': 'text'
        }

    def getSchema(self):
        schema = {}
        try:
            fp = open(SCHEMA_PATH, 'rb')
        except IOError:
            cv.log.error('Schema was not found!! File Path: '+SCHEMA_PATH)
        else:
            data = json.load(fp)['feed']['catalog']['schema']
            for obj in data:
                schema[obj['fieldName']] = obj
        finally:
            fp.close()
        return schema

    def Start(self):
        self.__main__()
        FeedGenerator(self.path).Run()
        UnbxdFeedUploader(self.path, self.API, self.API_VERSION).Run()

if __name__ == '__main__':
    if not os.path.exists(f'/mnt/{CUSTOMER_NAME}/{SITE_KEY}/full'):
        os.makedirs(f'/mnt/{CUSTOMER_NAME}/{SITE_KEY}/full')

    Main().Start()
