from lib.core.Requester import Requester, RequesterException
from lib.core.Scanner import Scanner
from lib.dictionary.Dictionary import Dictionary
import os
import time


class SkipTargetInterrupt(Exception):
    pass


class Controller(object):
    def __init__(self, arguments, output):
        self.output = output
        self.random_agents = []
        if arguments.random_agent:
            try:
                filename = os.path.dirname(os.path.realpath(
                    __file__)) + '/../../db/agent.txt'
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        self.random_agents.append(line)
            except IOError as e:
                raise e
        self.recursive = arguments.recursive
        self.random_agent = arguments.random_agent
        self.dictionary = Dictionary(
            arguments.wordList, arguments.lowercase, arguments.uppercase, arguments.extension)
        self.output.header(open(os.path.dirname(__file__) + '/banner.txt', 'r').read())
        self.output.configReport(arguments.extension, str(arguments.threads_count), str(len(
            self.dictionary)), str(self.recursive), str(arguments.delay), str(arguments.timeout))
        self.urlList = arguments.urlList
        try:
            for url in self.urlList:
                self.url = url
                try:
                    self.output.targetReport(url)
                    try:

                        self.requester = Requester(url, arguments.headers, arguments.user_agent, arguments.cookies, arguments.proxy,
                                                   arguments.delay, arguments.timeout, arguments.random_agent, self.random_agents, arguments.max_retries)
                        self.requester.request('/')
                    except RequesterException as e:
                        self.output.error(e.args[0]['message'])
                        raise SkipTargetInterrupt

                    self.scanner = Scanner(self.requester, self.dictionary, arguments.path_404,
                                           arguments.threads_count, self.matchCallBack, self.failCallBack, self.errorCallBack, arguments.sensor)
                    self.wait(url)
                except SkipTargetInterrupt:
                    continue
                finally:
                    self.recursive -= 1
        except KeyboardInterrupt:
            self.output.error('\nexit by user')
            exit(0)
        finally:
            self.output.warning('Scanning Over!')

    def recursive_path(self, url):
        if self.recursive >= 1:
            if url.endswith('/'):
                if url not in self.urlList:
                    self.urlList.append(url)

    def matchCallBack(self, path, response):
        self.output.statusReport(path, response, self.url)
        self.recursive_path(response.url)
        self.index += 1

    def failCallBack(self, path, length):
        self.index += 1
        self.output.lastPath(path, self.index, length)

    def errorCallBack(self, reason):
        self.output.error(reason)

    def handleInterrupt(self):
        self.output.warning('\ncatch out ctrl+c, process suspend')
        self.scanner.threadSuspend()
        while True:
            msg = '[e]xit | [c]ontinue'
            if len(self.urlList) > 1:
                msg += ' | [s]kipt'
            self.output.inLine(msg + ': ')
            option = input()
            if option.lower() == 'e':
                self.scanner.threadStop()
                raise KeyboardInterrupt
            elif option.lower() == 'c':
                self.scanner.threadResume()
                break
            elif option.lower() == 's':
                raise SkipTargetInterrupt
            else:
                continue

    def wait(self, url):
        self.index = 0
        self.output.warning('\n{0} start at {1}'.format(
            url, time.strftime('%H:%M:%S')))
        self.scanner.start()
        while True:
            try:
                while not self.scanner.over():
                    continue
                break
            except (KeyboardInterrupt, SystemExit):
                self.handleInterrupt()
