import threading
import time
import sys
import platform
import urllib.parse
import re
from thirdparty.colorama import *
from .TerminalSize import get_terminal_size

import os
if platform.system() == 'Windows':
    from thirdparty.colorama.win32 import *


class CLIOutput(object):
    def __init__(self):
        init()
        self.lastLength = 0
        self.lastOutput = ''
        self.lastInLine = False
        self.mutex = threading.Lock()
        self.blacklists = {}
        self.mutexCheckedPaths = threading.Lock()
        self.basePath = None
        self.errors = 0

    def inLine(self, string):
        self.erase()
        sys.stdout.write(string)
        sys.stdout.flush()
        self.lastInLine = True

    def erase(self):
        '''
        将一行缓冲区清除，并将光标回到行首
        '''
        if platform.system() == 'Windows':
            '''
             GetConsoleScreenBufferInfo()
             获取屏幕缓冲区字符属性，缓冲区大小，窗口大小 
             typedef struct _CONSOLE_SCREEN_BUFFER_INFO {
               COORD      dwSize; // 以字符为单位的屏幕缓冲宽x高
               COORD      dwCursorPosition; // 光标默认位置
               WORD       wAttributes; // 屏幕缓冲字符属性
               SMALL_RECT srWindow; // 屏幕缓冲窗口RECT
               COORD      dwMaximumWindowSize; // 最大屏幕缓冲窗口大小
             } CONSOLE_SCREEN_BUFFER_INFO;

            '''
            csbi = GetConsoleScreenBufferInfo()
            line = "\b" * int(csbi.dwCursorPosition.X)
            sys.stdout.write(line)
            width = csbi.dwCursorPosition.X
            csbi.dwCursorPosition.X = 0
            FillConsoleOutputCharacter(
                STDOUT, ' ', width, csbi.dwCursorPosition)
            '''
            BOOL FillConsoleOutputCharacter( // 填充指定数据的字符

            HANDLE hConsoleOutput, // 句柄

            TCHAR cCharacter, // 字符

            DWORD nLength, // 字符个数

            COORD dwWriteCoord, // 起始位置

            LPDWORD lpNumberOfCharsWritten);// 已写个数

            '''
            sys.stdout.write(line)
            sys.stdout.flush()
        else:
            '''
            参考https://zh.wikipedia.org/wiki/ANSI%E8%BD%AC%E4%B9%89%E5%BA%8F%E5%88%97
            [1k 表示删除光标到行首的内容，但光标的位置不变
            [0G 表示将光标移动到行首
            '''
            sys.stdout.write('\033[1K')
            sys.stdout.write('\033[0G')

    def newLine(self, string):
        if self.lastInLine == True:
            self.erase()
        if platform.system() == 'Windows':
            sys.stdout.write(string)
            sys.stdout.flush()
            sys.stdout.write('\n')
            sys.stdout.flush()
        else:
            sys.stdout.write(string + '\n')
        sys.stdout.flush()
        self.lastInLine = False
        sys.stdout.flush()

    def sizeHuman(self, num):
        base = 1024
        for x in ['B ', 'KB', 'MB', 'GB']:
            if num < base and num > -base:
                return "%3.0f%s" % (num, x)
            num /= base
        return "%3.0f %s" % (num, 'TB')

    def statusReport(self, path, response, url):
        with self.mutex:
            contentLength = None
            status = response.status_code
            temp = re.findall('\d+', str(response.history))
            history = int(temp[0]) if len(temp) >= 1 else 0
            if history != 0:
                status = history

            # Format message
            try:
                size = int(response.headers['content-length'])
            except (KeyError, ValueError):
                size = len(response.content)
            finally:
                contentLength = self.sizeHuman(size)

            message = '[{0}] {1} - {2} - {3}'.format(
                time.strftime('%H:%M:%S'),
                status,
                contentLength.rjust(6, ' '),
                path
            )

            try:
                file_path = os.path.dirname(os.path.realpath(
                    __file__)) + '/../../report/{}'.format(url.split('//')[1].rstrip('/'))
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                with open(file_path + '/1.txt', 'a') as f:
                    f.write(message + '\r\n')
            except IOError as e:
                raise e
                exit(0)

            if status == 200:
                message = Fore.GREEN + message + Style.RESET_ALL
            elif status == 403:
                message = Fore.BLUE + message + Style.RESET_ALL
            elif status == 401:
                message = Fore.YELLOW + message + Style.RESET_ALL
            # Check if redirect
            elif status in [301, 302, 303, 307]:
                message = Fore.CYAN + message + Style.RESET_ALL
                message += '  ->  {0}'.format(response.url)

            self.newLine(message)

    def lastPath(self, path, index, length):
        with self.mutex:
            def percentage(x, y): return float(x) / float(y) * 100
            x, y = get_terminal_size()
            message = '{0:.2f}% - '.format(percentage(index, length))
            if self.errors > 0:
                message += Style.BRIGHT + Fore.RED
                message += 'Errors: {0}'.format(self.errors)
                message += Style.RESET_ALL
                message += ' - '
            message += 'Last request to: {0}'.format(path)
            if len(message) > x:
                message = message[:x]
            self.inLine(message)

    def error(self, reason):
        with self.mutex:
            stripped = reason.strip()
            start = reason.find(stripped[0])
            end = reason.find(stripped[-1]) + 1
            message = reason[0:start]
            message += Style.BRIGHT + Fore.WHITE + Back.RED
            message += reason[start:end]
            message += Style.RESET_ALL
            message += reason[end:]
            self.newLine(message)

    def warning(self, reason):
        message = Style.BRIGHT + Fore.YELLOW + reason + Style.RESET_ALL
        self.newLine(message)

    def header(self, text):
        message = Style.BRIGHT + Fore.MAGENTA + text + Style.RESET_ALL
        self.newLine(message)

    def configReport(self, extension, threads_count, wordlistSize, recursive, delay, timeout):
        separator = Fore.MAGENTA + ' | ' + Fore.YELLOW

        config = Style.BRIGHT + Fore.YELLOW
        config += 'Extension: {0}'.format(Fore.CYAN +
                                          extension + Fore.YELLOW)

        config += separator
        config += 'Threads: {0}'.format(Fore.CYAN +
                                        threads_count + Fore.YELLOW)

        config += separator
        config += 'Wordlist size: {0}'.format(
            Fore.CYAN + wordlistSize + Fore.YELLOW)

        config += separator
        config += 'Recursive: {0}'.format(Fore.CYAN + recursive + Fore.YELLOW)

        config += separator
        config += 'Delay: {0}'.format(Fore.CYAN + delay + Fore.YELLOW)

        config += separator
        config += 'Timeout: {0}'.format(Fore.CYAN + timeout + Fore.YELLOW)

        config += Style.RESET_ALL
        self.newLine(config)

    def targetReport(self, target):
        config = Style.BRIGHT + Fore.YELLOW
        config += '\nTarget: {0}\n'.format(Fore.CYAN + target + Fore.YELLOW)
        config += Style.RESET_ALL
        self.newLine(config)


if __name__ == '__main__':
    url = 'https://www.youncyb.cn'

    print(os.path.dirname(os.path.realpath(__file__)) +
          '/../../report/{}'.format(url.split('//')[1].rstrip('/')))
