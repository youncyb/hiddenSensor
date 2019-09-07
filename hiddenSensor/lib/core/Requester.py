import sys
sys.path.append('../../')

import requests
import urllib
import socket
import random
import time
from requests.packages import urllib3


class RequesterException(Exception):
    pass


class Requester(object):
    def __init__(self, url, header=None, useragent=None, verify=None, cookies=None, proxy=None, delay=0, timeout=30, random_agent=False, random_agents=None, max_retries=5):
        self.url = self.parse_url(url)
        self.cookies = self.setCookies(cookies)
        self.headers = self.setHeaders(header, useragent)
        self.proxy = self.setProxy(proxy)
        self.delay = delay
        self.random_agent = random_agent
        self.random_agents = random_agents
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        if verify == None:
            self.verify = True
        else:
            self.verify = verify

    def parse_url(self, url):
        if not url.endswith('/'):
            url += '/'
        url_p = urllib.parse.urlparse(url)
        if url_p.scheme != 'http' and url_p.scheme != 'https':
            url_p = urllib.parse.urlparse('http://' + url)

        domain = url_p.netloc.split(':')
        if len(domain) == 2:
            port = domain[1]
            domain = domain[0]
        else:
            domain = domain[0]
            port = ''
        try:
            host = socket.gethostbyname(domain)
        except socket.gaierror:
            raise RequesterException({'message': 'could not resovle DNS'})
        return url_p.scheme + '://' + url_p.netloc + url_p.path.rstrip('/') + '/'

    def setCookies(self, cookies):
        if cookies is not None:
            lines = cookies.split(';')
            real_cookie = {}
            for line in lines:
                line = line.split('=')
                real_cookie[line[0].strip()] = line[1].strip()
            return real_cookie
        return

    def setHeaders(self, header, useragent):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0"
        }
        if header is not None:
            header = header.split(';')
            for line in header:
                line = line.split(':')
                headers[line[0].strip()] = line[1].strip()

        if useragent is not None:
            headers['User-Agent'] = useragent
        return headers

    def setProxy(self, proxy):
        if proxy is not None:
            proxies = {}
            parse = urllib.parse.urlparse(proxy)
            if parse.scheme == 'https':
                proxies['https'] = proxy
                proxies['http'] = proxy.replace('https', 'http')
            else:
                proxies['https'] = proxy.replace('http', 'https')
                proxies['http'] = proxy
            return proxies
        return

    def request(self, path, real_redirect=True):
        i = 1
        while i <= self.max_retries:
            try:
                if self.random_agent == True:
                    self.headers['User-Agent'] = random.choice(
                        self.random_agents)
                urllib3.disable_warnings()
                respone = self.session.get(
                    self.url + path, proxies=self.proxy, allow_redirects=real_redirect, verify=self.verify, headers=self.headers, cookies=self.cookies, timeout=self.timeout)
                time.sleep(self.delay)
                break
            except requests.exceptions.TooManyRedirects as e:
                raise RequesterException(
                    {'message': 'Too many redirects: {}'.format(e)})
            except requests.exceptions.ConnectionError as e:
                if self.proxy is not None:
                    raise RequesterException(
                        {'message': 'Error proxy: {}'.format(e)})
                continue
            except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
                continue
            finally:
                i += 1
        if i > self.max_retries:
            raise RequesterException(
                {'message': 'Connection timeout: There was a problem in the request to: {0}'.format(path)})
        return respone
