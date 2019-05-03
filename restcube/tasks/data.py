from restcube.factory import make_celery
from restcube.datacube.api import load_data

from datacube.drivers.netcdf import write_dataset_to_netcdf

celery = make_celery()

import boto3
import botocore
from botocore.client import Config
import os

def _uploadToS3(filename, data, mimetype):
    session = boto3.Session()
    bucket = os.getenv("S3_RESULT_BUCKET")
    s3 = session.client('s3')
    s3.upload_fileobj(
        data,
        bucket,
        filename,
        ExtraArgs={
            'ACL':'public-read',
            'ContentType': mimetype
        }
    )
    # Create unsigned s3 client for determining public s3 url
    s3 = session.client('s3', config=Config(signature_version=botocore.UNSIGNED))
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        ExpiresIn=0,
        Params={
            'Bucket': bucket,
            'Key': filename
        }
    )
    return url

@celery.task(bind=True)
def get_data(self, **kwargs):

    def callback(processed, total):
        self.update_state(state="PROGRESS", meta={
            "processed": processed,
            "total": total    
        })


    print(kwargs)

    data = load_data(progress_cbk=callback, **kwargs)

    print(data)

    filename = f'{self.request.id}.nc'

    write_dataset_to_netcdf(data, filename)

    url = ""
    with open(filename, 'rb') as f:
        url = _uploadToS3(f'{self.request.id}/{filename}', f, 'application/x-netcdf4')

    os.remove(filename)

    return url

