
from .models import Data as DataModel
from rmxweb.celery import celery


@celery.task
def create_from_webpage(containerid: str = None,
                        endpoint: str = None,
                        title: str = None,
                        data: str = None,
                        links: list = None):
    """ Task called within DataModel.create."""
    doc = DataModel.create(
        data=data,
        containerid=containerid,
        links=links,
        title=title,
        endpoint=endpoint
    )
    if isinstance(doc, DataModel):
        return doc.pk, doc.file_id
    return None, None


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
