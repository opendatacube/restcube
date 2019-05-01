import os
import requests

from uuid import uuid4
from json import dumps

import aiobotocore
import asyncio

from odc.ppt.async_thread import AsyncThread
from odc.aws import auto_find_region

from odc.aio import S3Fetcher
from odc.aws._find import parse_query, norm_predicate
from odc.ppt import future_results

from restcube.factory import make_celery
from celery.result import AsyncResult
from celery import current_app
from restcube.datacube.api import add_datasets

celery = make_celery()

class SQSProducer(object):
    def __init__(self,
                 region_name=None):
        from aiobotocore.config import AioConfig

        if region_name is None:
            region_name = auto_find_region()

        self._async = AsyncThread()
        self._session = None
        self._closed = False

        async def setup():
            session = aiobotocore.get_session()
            s3 = session.create_client('sqs',
                                       region_name=region_name)
            return (session, s3)

        session, sqs = self._async.submit(setup).result()
        self._session = session
        self._sqs = sqs

    def close(self):
        async def _close(sqs):
            await sqs.close()

        if not self._closed:
            self._async.submit(_close, self._sqs).result()
            self._async.terminate()
            self._closed = True

    def __del__(self):
        self.close()


    async def push_message(self, message, sqs_url):
        """ push message to sqs queue
        """
        await self._sqs.send_message(
            QueueUrl=sqs_url,
            MessageBody=message)

def s3_find(uri, skip_check):
    """ List files on S3 bucket.

    Example:

       \b
       List files in directory that match `*yaml`
        > s3-find 's3://mybucket/some/path/*yaml'

       \b
       List files in directory and all sub-directories that match `*yaml`
        > s3-find 's3://mybucket/some/path/**/*yaml'

       \b
       List files that match `*yaml` 2 levels deep from known path
        > s3-find 's3://mybucket/some/path/*/*/*yaml'

       \b
       List directories 2 levels deep from known path
        > s3-find 's3://mybucket/some/path/*/*/'

       \b
       List all files named `metadata.yaml` 2 directories deep
        > s3-find 's3://mybucket/some/path/*/*/metadata.yaml'
    """

    def do_file_query(qq, pred):
        for d in s3.dir_dir(qq.base, qq.depth):
            _, _files = s3.list_dir(d).result()
            for f in _files:
                if pred(f):
                    yield f

    def do_file_query2(qq):
        fname = qq.file

        stream = s3.dir_dir(qq.base, qq.depth)

        if skip_check:
            yield from (SimpleNamespace(url=d+fname) for d in stream)
            return

        stream = (s3.head_object(d+fname) for d in stream)

        for (f, _), _ in future_results(stream, 32):
            if f is not None:
                yield f

    def do_dir_query(qq):
        return (SimpleNamespace(url=url) for url in s3.dir_dir(qq.base, qq.depth))

    flush_freq = 100

    try:
        qq = parse_query(uri)
    except ValueError as e:
        click.echo(str(e), err=True)
        sys.exit(1)

    s3 = S3Fetcher()

    glob_or_file = qq.glob or qq.file

    if qq.depth is None and glob_or_file is None:
        stream = s3.find(qq.base)
    elif qq.depth is None or qq.depth < 0:
        if qq.glob:
            stream = s3.find(qq.base, glob=qq.glob)
        elif qq.file:
            postfix = '/'+qq.file
            stream = s3.find(qq.base, pred=lambda o: o.url.endswith(postfix))
    else:
        # fixed depth query
        if qq.glob is not None:
            pred = norm_predicate(glob=qq.glob)
            stream = do_file_query(qq, pred)
        elif qq.file is not None:
            stream = do_file_query2(qq)
        else:
            stream = do_dir_query(qq)

    yield from stream

@celery.task(bind=True, acks_late=True)
def index_in_dc(self, url, product):
    add_datasets([url], product)


@celery.task(bind=True)
def index_from_s3(self, s3_pattern, dc_product):
    s3_urls = s3_find(s3_pattern, False)

    state = {"last_processed": "", "count": 0}
    count = 0
    for s3_url in s3_urls:

        index_in_dc.apply_async(args=[s3_url.url, dc_product])
        count = count + 1
        state = {"type": "index","last_processed": s3_url.url, "count": count}
        print(state)
        self.update_state(state="PROGRESS", meta=state)

    return state


@celery.task(bind=True)
def send_s3_urls_to_sqs(self, s3_pattern, dc_product, sqs_url):

    # Unfortunately Celery does not cope well with
    # Exception classes that use a custom constructor,
    # including botocore exceptions
    producer = SQSProducer()

    message = dict()
    if dc_product is not None:
        message["product"] = dc_product

    s3_urls = s3_find(s3_pattern, False)

    state = {"last_processed": "", "count": 0}
    count = 0
    for s3_url in s3_urls:
        message["url"] = s3_url.url
        body = dumps(message)
        future = producer._async.submit(producer.push_message, body, sqs_url)
        exc = future.exception()
        if exc:
            raise RuntimeError(str(exc))
        else:
            future.result()
        count = count + 1
        state = {"type": "index","last_processed": s3_url.url, "count": count}
        print(state)
        self.update_state(state="PROGRESS", meta=state)

    return state

def get_all_tasks():
    all_tasks = current_app.tasks
    return all_tasks



def get_task(task_id):
    task = AsyncResult(task_id, app=celery)
    if not task:
        return '{"error": "Error finding task"}', 500
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "processed": 0,
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "processed": task.info.get("count"),
            "last_processed": task.info.get("last_processed")
        }
    else:
        response = {
            "state": task.state,
            # "processed": task.info.get("count"),
            # "last_processed": task.info.get("last_processed"),
            "error": str(task.info)
        }
    return response

def delete_task(task_id):
    celery.control.revoke(task_id, terminate=True)