import urllib.request
import urllib.error
import sys
import ssl


def req(url):
    """
    aliyun API
    :param url:
    :param appcode:
    :return:
    """
    try:
        request = urllib.request.Request(url)
        # print(url)
        # request.add_header('Authorization', 'APPCODE ' + appcode)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        # print('request.headers: ')
        # print(request.headers)
        # response = urllib.request.urlopen(request, context=ctx)
        # print(response)
        try:
            response = urllib.request.urlopen(request, context=ctx)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            response = None
        # print(response)
        try:
            content = response.read().decode("gb2312")
            response.close()
        except AttributeError:
            content = ''
        if content:
            return content
        else:
            return ''
    except ValueError:
        return None
