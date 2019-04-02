from flask_restful import reqparse, abort, Resource

from datacube import Datacube
from datacube.index.hl import Doc2Dataset
from yaml import safe_load


getargparser = reqparse.RequestParser()
getargparser.add_argument('product', type=str, help="Name of the Datacube product")

postargparser = getargparser.copy()
postargparser.add_argument('dataset_definition_urls', action="append", help="List of urls containing dataset definitions")

class Dataset(Resource):

    def get(self, ds_id):
        with Datacube() as dc:
            if not dc.index.datasets.has(ds_id):
                abort(400, message="Datacube does not contain dataset with id {}".format(ds_id))

            dataset = dc.index.datasets.get(ds_id)
            return {"metadata": dataset.metadata_doc}, 200


class Datasets(Resource):

    def get(self):
        args = getargparser.parse_args()
        product = args['product']
        datasets = []
        with Datacube() as dc:
            if dc.index.products.get_by_name(product) is None:
                abort(400, message="product {} does not exist".format(product))
            ds = dc.index.datasets.search(product=product)
            datasets = [ d.metadata.id for d in ds ]

        return {"ids": datasets}, 200

    def post(self):
        import urllib.request

        args = postargparser.parse_args()
        product = args['product']
        urls = args['dataset_definition_urls']

        added = []
        already_indexed = []
        errors = []
        with Datacube() as dc:
            resolver = Doc2Dataset(dc.index, products=[product])
            for url in urls:
                doc_request = urllib.request.urlopen(url)
                doc = safe_load(doc_request.read())

                dataset, err = resolver(doc, url)

                if err:
                    errors.append({"error": err, "url": url})
                    continue
                elif dc.index.datasets.has(dataset.id):
                    already_indexed.append(url)
                    continue
                added.append({"id": dc.index.datasets.add(dataset).metadata.id, "url": url})

        obj = {
            "added": added,
            "already_indexed": already_indexed,
            "errors": errors
        }

        return obj, 200