from datacube import Datacube
from datacube.api.query import Query
from datacube.index.hl import Doc2Dataset
import validators
import requests
from yaml import safe_load_all, safe_load

import boto3
from urllib.parse import urlparse

def load_data(progress_cbk=None, **kwargs):
    with Datacube() as dc:
        data = dc.load(progress_cbk=progress_cbk, **kwargs)
        return data


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


def get_dataset_locations(ds_id):
    with Datacube() as dc:
        return dc.index.datasets.get_locations(ds_id)

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


def get_products(**kwargs):
    with Datacube() as dc:
        # Name is a special case
        if "name" in kwargs:
            yield dc.index.products.get_by_name(kwargs["name"])
        else:
            yield from dc.index.products.search(**kwargs)


def add_products(product_definition_url):
    with Datacube() as dc:
        doc_request = requests.get(product_definition_url)
        doc_request.raise_for_status()
        docs = safe_load_all(doc_request.text)

        for doc in docs:
            product = dc.index.products.from_doc(doc)
            product = dc.index.products.add(product)
            yield product

