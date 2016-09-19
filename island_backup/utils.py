EMPTY_DATA = object()


def url_page_combine(base_url, num):
    return base_url + '?page=' + str(num)