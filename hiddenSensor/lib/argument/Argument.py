import argparse
import os


class Argument(object):
    def __init__(self):
        self.base_path = os.path.dirname(
            os.path.realpath(__file__)) + '/../../db/dicc.txt'
        args = self.parseArguments()
        self.recursive = args.recursive
        self.urlList = []
        if args.url is not None:
            self.urlList.append(args.url)

        if args.urlList is not None:
            try:
                with open(args.urlList, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        self.urlList.append(line)
            except IOError as e:
                raise e
        if len(self.urlList) == 0:
            print('url target is necessary')
            exit(0)
        self.extension = args.extension
        self.headers = args.headers
        self.user_agent = args.user_agent
        self.random_agent = args.random_agent
        self.cookies = args.cookies
        self.proxy = args.proxy
        self.delay = args.delay
        self.timeout = args.timeout
        self.max_retries = args.max_retries
        self.threads_count = args.threads_count
        self.path_404 = args.path_404
        self.lowercase = args.lowercase
        self.uppercase = args.uppercase
        self.wordList = args.wordList
        self.sensor = args.ctf
        self.crt = args.verify

    def parseArguments(self):
        parser = argparse.ArgumentParser()
        group1 = parser.add_argument_group('madatory settings')
        group1.add_argument('-u', '--url', help='target',
                            action='store', dest='url', default=None)
        group1.add_argument('-L', '--urlList', help='url file path',
                            action='store', dest='urlList', default=None)
        group1.add_argument('-e', '--extension', help='the extension of website type (default : "php")',
                            action='store', dest='extension', default='php')

        group2 = parser.add_argument_group('connection settings')
        group2.add_argument(
            '-H', '--headers', help='set headers', action='store', dest='headers', default=None)
        group2.add_argument('--user-agent', help='user-agent you want to specify',
                            action='store', dest='user_agent', default=None)
        group2.add_argument('--random-agent', help='random-agent (default: False)',
                            action='store_true', dest='random_agent')
        group2.add_argument('-c', '--cookie', help='cookie you want to specify (example: -c "domain=xxx;path=xxx")',
                            action='store', dest='cookies', default=None)
        group2.add_argument('-r', '--recursive', type=int, help='Recursive blasting subdir (default: 0 layers)',
                            action='store', dest='recursive', default=0)
        group2.add_argument('--proxy', help='set proxy (http proxy,example:--proxy http://127.0.0.1:1090)',
                            action='store', dest='proxy', default=None)
        group2.add_argument('-s', '--delay', type=float, help='time.sleep(delay) every request (default: 0)',
                            action='store', dest='delay', default=0)
        group2.add_argument('--timeout', type=int, help='max time every request is waiting (default: 30 s)',
                            action='store', dest='timeout', default=30)
        group2.add_argument('-m', '--max-retries', type=int, help='max retries when meeting network problem (default: 5)',
                            action='store', dest='max_retries', default=5)
        group2.add_argument('--verify', help='if ssl error occured, process will disable ssl verify',
                            action='store_false', dest='verify')

        group3 = parser.add_argument_group('other settings')
        group3.add_argument('-t', '--thread', type=int, help='max thread count you want to specify (default: 10)',
                            action='store', dest='threads_count', default=10)
        group3.add_argument('-404', '--404-page', help='the 404 page you want to specify (example: if error.php  -404 "error")',
                            action='store', dest='path_404', default=None)
        group3.add_argument('--lowercase', help='force to be lowercase',
                            action='store_true', dest='lowercase')
        group3.add_argument('--uppercase', help='force to be uppercase',
                            action='store_true', dest='uppercase')
        group3.add_argument('--dicts-path', help='other dictionary you want to specify',
                            action='store', dest='wordList', default=self.base_path)
        group3.add_argument(
            '--ctf', help='if it\'s specified, process will find sensor file (xxx.php.bak, .xxx.php.swp ...)', action='store_true', dest='ctf')

        args = parser.parse_args()
        return args
