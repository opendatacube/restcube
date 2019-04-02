from datacube import Datacube
from datacube.index.hl import Doc2Dataset
import validators
import requests


def get_datasets(**kwargs):
    with Datacube() as dc:
        # Special case for id specified
        if 'id' in kwargs:
            d_id = kwargs['id']
            # validate as a UUID
            if validators.uuid(d_id) != True:
                raise ValueError("{} is an invalid UUID".format(d_id))
            if not dc.index.datasets.has(d_id):
                yield None
            else:
                yield dc.index.datasets.get(d_id)
        yield from dc.index.datasets.search(**kwargs)


def add_datasets(urls, product):
    with Datacube() as dc:
        resolver = Doc2Dataset(dc.index, products=[product])
        for url in urls:
            doc_request = requests.get(url)
            doc_request.raise_for_status()
            docs = safe_load(doc_request.text)

            dataset, err = resolver(doc, url)

            if err:
                yield { "status": "error", "error": err, "url": url }
            elif dc.index.datasets.has(dataset.id):
                yield { "status": "already indexed", "url": url, "id": dataset.id }
            d = dc.index.datasets.add(dataset)
            yield {"status": "indexed", "id": d.metadata.id, "url": url}
