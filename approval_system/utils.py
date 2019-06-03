import time
import hashlib

from flask import flash, request, current_app
from flask_login import current_user

from approval_system.extensions import archives


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash("%s - %s" % (getattr(form, field).label.text, error), 'warning')


def file_path(inner_path):
    return current_app.config['UPLOADED_ARCHIVES_DEST']+inner_path


def path(number='', id=0, filename=''):
    return number + '/' + str(id) + '/' + filename


def upload_file(last_time, id=None, name='file'):
    for file in request.files.getlist(name):
        hash_name = hashlib.md5((str(time.time()) + file.filename).encode('UTF-8')).hexdigest()[:5]
        file_name = last_time.replace(':', '-') + '_' + hash_name + '.'
        archives.save(file, folder=path(number=current_user.number, id=id), name=file_name)

# def upload_img(id=None, name='upload'):
#     for file in request.files.getlist(name):
#         hash_name = hashlib.md5((str(time.time()) + file.filename).encode('UTF-8')).hexdigest()[:5]
#         file_name = hash_name + '.'
#         archives.save(file, folder=path(number=current_user.number, id=id), name=file_name)
