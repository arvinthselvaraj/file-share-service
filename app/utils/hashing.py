import hashlib


def compute_sha256_and_size(file_obj, max_bytes: int):
    """
    Function to compute sha256 while streaming for integrity/dedupe and size of file.

    :param file_obj:
    :param max_bytes:
    :return:
    """
    h = hashlib.sha256()
    size = 0
    while True:
        chunk = file_obj.read(1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
        size += len(chunk)
        if size > max_bytes:
            raise ValueError()
    file_obj.seek(0)
    return size, h.hexdigest()
