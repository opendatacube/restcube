# -*- coding: utf-8 -*-

# Contains Datacube API wrapper 
# Functions which require a datacube to be created should be placed in this file
import os
import sys
import subprocess
import json
from pathlib import Path
from datacube import Datacube
from datacube.index import index_connect

from datacube.api.query import Query
from datacube.index.hl import Doc2Dataset
from datacube.config import LocalConfig


import validators
import requests
import yaml
import psycopg2
from psycopg2 import sql
import configparser

import boto3
from urllib.parse import urlparse
import base64

# Create a database
# init the database
def create_database(new_db_name, new_db_user, new_db_password, db_host, db_port, admin_username='test', admin_password='test'):

    # in EKS, not required to save a configfile
    CONFIG_FILE_PATHS = [str( Path(__file__).parent/ 'datacube.conf'),
                         os.path.expanduser('~/.datacube.conf')]

    # create new section in datacube config - local testing
    config = configparser.RawConfigParser()
    config.read(CONFIG_FILE_PATHS[1])

    config.add_section(new_db_name)
    config.set(new_db_name, 'DB_USERNAME', new_db_user)
    config.set(new_db_name, 'DB_HOSTNAME', db_host)
    config.set(new_db_name, 'DB_PORT', db_port)
    config.set(new_db_name, 'DB_DATABASE', new_db_name)
    config.set(new_db_name, 'DB_PASSWORD', new_db_password)

    with open(CONFIG_FILE_PATHS[1], 'w') as configfile:
        config.write(configfile)


    proc = subprocess.Popen(['bash', str( Path(__file__).parent.parent/'scripts/create-db.sh')], stdout=subprocess.PIPE,
                            env={'DB_USERNAME': new_db_user,
                                 'DB_HOSTNAME': db_host,
                                 'DB_PORT': db_port,
                                 'ADMIN_USERNAME': admin_username,
                                 'ADMIN_PASSWORD': admin_password,
                                 'DB_DATABASE': new_db_name,
                                 'DB_PASSWORD': new_db_password})

    child = proc.communicate()[0]
    # init db
    
    index = index_connect(LocalConfig.find(CONFIG_FILE_PATHS, env=new_db_name), # to be replace with kubenetes config
                                           validate_connection=False)
    status = index.init_db(with_default_types=True)

    # Create kubenetes secrets for the new database owner 
    
    secret_template = {'apiVersion':'v1', 'kind':'Secret', 'metadata':{'name':'','namespace':''},'type':'Opaque','data':{'postgres-username':'','postgres-password':''}} 
    # add new postgres user to secret
    secret_template['metadata']['name'] = new_db_name
    secret_template['data']['postgres-username'] = base64.b64encode(new_db_user.encode()).decode()
    secret_template['data']['postgres-password'] = base64.b64encode(new_db_password.encode()).decode()
    secret_template['metadata']['namespace'] = 'webtools'
    output_file_name = '/tmp/' + new_db_name

    with open(output_file_name, 'w') as fp:
        yaml.dump(secret_template, fp, default_flow_style=False)

    kube = subprocess.call(['kubectl', 'apply', '-f', output_file_name ]) 
    
    return new_db_name 



# Perform a DC load based on kwargs passed to this function
# and returns an xarray based on this load
def load_data(progress_cbk=None, **kwargs):
    with Datacube() as dc:
        data = dc.load(progress_cbk=progress_cbk, **kwargs)
        return data


# Retrieves DC dataset metadata for datasets based on query
# passed in by kwargs.
# If kwargs contains 'id' or 'url', performs different search
# based on id or url.
# Function should yield results
def get_datasets(**kwargs):
    with Datacube() as dc:
        # Special case for id specified
        if 'id' in kwargs and kwargs['id'] is not None:
            d_id = kwargs['id']
            # validate as a UUID
            if validators.uuid(d_id) != True:
                raise ValueError("{} is an invalid UUID".format(d_id))
            if not dc.index.datasets.has(d_id):
                yield None
            else:
                yield dc.index.datasets.get(d_id)
        elif 'url' in kwargs and kwargs['url'] is not None:
            d_url = kwargs['url']
            yield from dc.index.datasets.get_datasets_for_location(d_url, mode="exact")
        else:
            query = Query(**kwargs)
            yield from dc.index.datasets.search(**query.search_terms)


# Retrieves DC dataset locations (i.e. URL to dataset YAML or filepath)
# for a dataset given a dataset id
def get_dataset_locations(ds_id):
    with Datacube() as dc:
        return dc.index.datasets.get_locations(ds_id)

# Adds datasets based on dataset metadata URLs and a product
# Supports S3 URLs and HTTP
def add_datasets(urls, product):

    def get_protocol(url):
        parsed = urlparse(url)
        return parsed.scheme

    def get_bucket_and_key(s3url):
        parsed = urlparse(s3url)
        return parsed.netloc, parsed.path.lstrip("/")


    if urls is None or len(urls) <= 0:
        raise ValueError

    with Datacube() as dc:
        resolver_args = dict()
        if product is not None:
            resolver_args['products'] = [product]

        resolver = Doc2Dataset(dc.index, **resolver_args)
        for url in urls:
            if get_protocol(url) == "s3":
                bucket, key = get_bucket_and_key(url)
                s3 = boto3.resource("s3")
                s3_obj = s3.Object(bucket, key).get(ResponseCacheControl='no-cache')
                doc = safe_load(s3_obj['Body'].read())
            else:
                doc_request = requests.get(url)
                doc_request.raise_for_status()
                doc = safe_load(doc_request.text)

            dataset, err = resolver(doc, url)

            if err:
                yield { "status": "error", "error": err, "url": url }
            elif dc.index.datasets.has(dataset.id):
                yield { "status": "already indexed", "url": url, "id": dataset.metadata.id }
            else:
                d = dc.index.datasets.add(dataset)
                yield {"status": "indexed", "id": d.metadata.id, "url": url}

# Retrieves DC product metadata based on a query specified in kwargs
def get_products(**kwargs):
    with Datacube() as dc:
        # Name is a special case
        if "name" in kwargs:
            yield dc.index.products.get_by_name(kwargs["name"])
        else:
            yield from dc.index.products.search(**kwargs)

# Given a datacube product definition URL, add the product or products in the URL
def add_products(product_definition_url):
    with Datacube() as dc:
        doc_request = requests.get(product_definition_url)
        doc_request.raise_for_status()
        docs = safe_load_all(doc_request.text)

        for doc in docs:
            product = dc.index.products.from_doc(doc)
            product = dc.index.products.add(product)
            yield product

