from flask import Flask, json, request, abort
import datacube
from datacube import Datacube
from datacube.index.hl import Doc2Dataset
from yaml import safe_load, safe_load_all

app = Flask(__name__)

@app.route("/products", methods=["GET"])
def get_products():
    products = []
    with Datacube() as dc:
        products = [ p.to_dict() for p in dc.index.products.get_all() ]

    response = app.response_class(
        response=json.dumps(products),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route("/product/<name>")
@app.route("/products/<name>")
def get_product(name):
    with Datacube() as dc:
        product = dc.index.products.get_by_name(name)

        response = app.response_class(
            response=json.dumps(product.to_dict()),
            status=200,
            mimetype='application/json'
        )

        return response

@app.route("/products", methods=["POST"])
def create_product():
    import urllib.request
    data = json.loads(request.data)
    if not data or not 'url' in data:
        abort(400)

    products = []
    with Datacube() as dc:
        doc_request = urllib.request.urlopen(data['url'])
        docs = safe_load_all(doc_request.read())
        
        for doc in docs:
            product = dc.index.products.from_doc(doc)
            product = dc.index.products.add(product)
            products.append(product.to_dict())

    response = app.response_class(
        response=json.dumps(products),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route("/product/<name>/datasets", methods=["GET"])
@app.route("/products/<name>/datasets", methods=["GET"])
def get_datasets_by_product(name):
    datasets = []
    with Datacube() as dc:
        ds = dc.index.datasets.search(product=name)
        datasets = [ d.metadata.id for d in ds ]

    response = app.response_class(
        response=json.dumps(datasets),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route("/product/<name>/datasets", methods=["POST"])
@app.route("/products/<name>/datasets", methods=["POST"])
def add_datasets_by_product(name):
    import urllib.request
    data = json.loads(request.data)
    if not data or not 'urls' in data:
        abort(400)
    added = []
    already_indexed = []
    errors = []
    with Datacube() as dc:
        resolver = Doc2Dataset(dc.index, products=[name])
        urls = data['urls']

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

    response = app.response_class(
        response=json.dumps(obj),
        status=200,
        mimetype='application/json'
    )

    return response

