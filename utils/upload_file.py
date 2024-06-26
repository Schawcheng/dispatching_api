import os

import tools


def save_django_upload_file(file, path):
    with open(path, 'wb+') as f:
        if file.multiple_chunks():
            for chunk in file.chunks():
                f.write(chunk)
        else:
            f.write(file.read())


def handle_upload_file_save_path(root_dir, file_name_suffix, prefix='', suffix=''):
    file_name = tools.generate_unique_string(prefix=prefix)
    file_fullname = file_name + file_name_suffix
    file_path = os.path.join(root_dir, file_fullname)

    return file_path, file_fullname


def generate_file_url(root_url, file_fullname):
    return os.path.join(root_url, file_fullname)
