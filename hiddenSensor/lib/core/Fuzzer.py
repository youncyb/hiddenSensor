import sys
sys.path.append('../../')


from difflib import SequenceMatcher
from thirdparty.sqlmap import DynamicContentParser
import re
import random
import string
import urllib.parse

#import requests
#from .Requester import Requester


class Fuzzer(object):
    def __init__(self, requester, path=None):
        self.requester = requester
        self.path = path
        self.suffix = ['php', 'jsp', 'asp']
        self.redirection_code = ['301', '302', '303', '307']
        self.base_ratio = 0.98
        self.flag = False
        self.redirection_regexp = []
        self.setup()

    def getRandomPath(self):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(8))

    def generateRedirectRegExp(self, firstLocation, secondLocation):
        if firstLocation is None or secondLocation is None:
            return None
        sm = SequenceMatcher(None, firstLocation, secondLocation)
        marks = []
        for blocks in sm.get_matching_blocks():
            i = blocks[0]
            n = blocks[2]
            # empty block
            if n == 0:
                continue
            mark = firstLocation[i:i + n]
            if mark.startswith('http') or mark.startswith('https'):
                marks.append(mark)
        regexp = "^.*{0}.*$".format(".*".join(map(re.escape, marks))
                                    ).replace('http', '(https|http)')
        return regexp

    def getDmain(self, url):
        url_parser = urllib.parse.urlparse(url)
        return url_parser.scheme + '://' + url_parser.netloc

    def getHistory(self, history):
        history = re.findall('\d+', history)
        history = history[0] if len(history) >= 1 else []
        return str(history)

    def setup(self):
        if self.path is None or self.path is '':
            self.path = self.getRandomPath()

        firstpath_php = self.path + '.' + self.suffix[0]
        res1_php = self.requester.request(firstpath_php, True)
        secondpath_php = self.getRandomPath() + '.' + self.suffix[0]
        res2_php = self.requester.request(secondpath_php, True)

        firstpath_jsp = self.path + '.' + self.suffix[1]
        res1_jsp = self.requester.request(firstpath_jsp, True)
        secondpath_jsp = self.getRandomPath() + '.' + self.suffix[1]
        res2_jsp = self.requester.request(secondpath_jsp, True)

        firstpath_asp = self.path + '.' + self.suffix[2]
        res1_asp = self.requester.request(firstpath_asp, True)
        secondpath_asp = self.getRandomPath() + '.' + self.suffix[2]
        res2_asp = self.requester.request(secondpath_asp, True)

        if res1_asp.status_code == 404 and res1_php.status_code == 404 and res1_jsp.status_code == 404:
            self.flag = True
        else:

            if self.getHistory(str(res1_php.history)) in self.redirection_code and self.getHistory(str(res2_php.history)) in self.redirection_code:
                regExp = self.generateRedirectRegExp(
                    res1_php.url, res2_php.url)
                self.redirection_regexp.append(
                    regExp) if regExp not in self.redirection_regexp else 0

            if self.getHistory(str(res1_jsp.history)) in self.redirection_code and self.getHistory(str(res2_jsp.history)) in self.redirection_code:
                regExp = self.generateRedirectRegExp(
                    res1_jsp.url, res2_jsp.url)
                self.redirection_regexp.append(
                    regExp) if regExp not in self.redirection_regexp else 0

            if self.getHistory(str(res1_asp.history)) in self.redirection_code and self.getHistory(str(res2_asp.history)) in self.redirection_code:
                regExp = self.generateRedirectRegExp(
                    res1_asp.url, res2_asp.url)
                self.redirection_regexp.append(
                    regExp) if regExp not in self.redirection_regexp else 0

            if res1_asp.status_code == 404 and res1_php.status_code == 404 and res1_jsp.status_code == 404:
                self.flag = True

            self.dynamic_php = DynamicContentParser(
                self.requester, firstpath_php, res1_php.text, res2_php.text)
            if self.dynamic_php is not None:
                ratio = float('{0:.2f}'.format(
                    self.dynamic_php.comparisonRatio))
                if self.base_ratio > ratio:
                    self.base_ratio = ratio

            self.dynamic_jsp = DynamicContentParser(
                self.requester, firstpath_jsp, res1_jsp.text, res2_jsp.text)
            if self.dynamic_jsp is not None:
                ratio = float('{0:.2f}'.format(
                    self.dynamic_jsp.comparisonRatio))
                if self.base_ratio > ratio:
                    self.base_ratio = ratio

            self.dynamic_asp = DynamicContentParser(
                self.requester, firstpath_asp, res1_asp.text, res2_asp.text)
            if self.dynamic_asp is not None:
                ratio = float('{0:.2f}'.format(
                    self.dynamic_asp.comparisonRatio))
                if self.base_ratio > ratio:
                    self.base_ratio = ratio

    def fuzz(self, cmp_page):
        if self.flag == True:
            if cmp_page.status_code == 404:
                return False
            else:
                return True
        else:
            if cmp_page.status_code == 404:
                return False
            redirectToInvalid = []
            for express in self.redirection_regexp:
                if express is not None:
                    redirectToInvalid.append(
                        re.match(express, cmp_page.url) is not None)
            if not any(redirectToInvalid):
                return True
            ratio_php = self.dynamic_php.compareTo(cmp_page.text)
            ratio_jsp = self.dynamic_jsp.compareTo(cmp_page.text)
            ratio_asp = self.dynamic_asp.compareTo(cmp_page.text)
            if self.base_ratio <= ratio_php or self.base_ratio <= ratio_jsp or self.base_ratio <= ratio_asp:
                return False
            elif any(redirectToInvalid) and ((self.base_ratio - 0.15) <= ratio_php or (self.base_ratio - 0.15) <= ratio_jsp or (self.base_ratio - 0.15) <= ratio_asp):
                return False
            return True


if __name__ == '__main__':
    req = Requester('https://www.baidu.com/')
    fuzzer = Fuzzer(req)
    print(fuzzer.fuzz(requests.get('https://www.baidu.com/hello.php')))

