

from .models import Data as DataModel
from prom.config import CREATE_DATA_PREFIX
from prom.decorator import register_with_prom
from rmxweb.celery import celery


@celery.task
@register_with_prom(CREATE_DATA_PREFIX)
def create_from_webpage(containerid: str = None,
                        endpoint: str = None,
                        seed: bool = False,
                        title: str = None,
                        data: str = None,
                        links: list = None):
    """ Task called within DataModel.create."""
    doc = DataModel.create(
        data=data,
        containerid=containerid,
        links=links,
        title=title,
        endpoint=endpoint,
        seed=seed
    )
    if isinstance(doc, DataModel):
        return doc.pk, doc.file_id
    return None, None


@celery.task
def delete_many(containerid: str = None, data_ids: list = None):
    """
    Delete many data objects that match a containerid and a lit of data ids.
    :param containerid:
    :param data_ids:
    :return:
    """
    DataModel.delete_many(data_ids=data_ids, containerid=containerid)


# todo(): delete
# @celery.task
# def create(corpusid: str = None,
#            fileid: str = None,
#            path: str = None,
#            encoding: str = None,
#            file_name: str = None,
#            success: bool = False,
#            hashtxt: str = None,
#            ):
#     """ Creating a data object for a file that exists. This is used when
#         uploading files.
#
#     :param corpusid:
#     :param fileid:
#     :param path:
#     :param encoding:
#     :param file_name:
#     :param success:
#     :param hashtxt:
#     :return:
#     """
#     # todo(): delete!
#     doc, fileid = DataModel.create_empty(
#         containerid=corpusid,
#         title=file_name,
#         fileid=fileid
#     )
#     if not hashtxt:
#         hasher = hashlib.md5()
#         with open(path, 'r') as _file:
#             for line in _file.readlines():
#                 hasher.update(bytes(line, encoding=encoding))
#
#         hashtxt = hasher.hexdigest()
#     out = {
#         'corpusid': corpusid,
#         'data_id': str(doc.get_id()),
#         'file_id': fileid,
#         'file_name': file_name,
#         'success': success,
#     }
#     try:
#         doc.set_hashtxt(value=hashtxt)
#         out['texthash'] = hashtxt
#     except ValueError:
#         doc.rm_doc()
#         if os.path.exists(path):
#             os.remove(path)
#         out['success'] = False
#
#     return out
