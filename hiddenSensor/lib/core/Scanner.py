from .Fuzzer import Fuzzer
import threading
from .Requester import Requester, RequesterException
#from dictionary.Dictionary import Dictionary
import urllib.parse


class Scanner(object):
    def __init__(self, requester, dictionary, path_404=None, threads=1, match_call_back=None, fail_call_back=None, error_call_back=None, sensor=False):
        self.pause_semaphore = threading.Semaphore(0)
        self.event = threading.Event()
        self.requester = requester
        self.dictionary = dictionary
        self.thread_counts = threads if len(
            self.dictionary) > threads else len(self.dictionary)
        self.threads = []
        self.fuzzer = Fuzzer(requester, path_404)
        self.match_call_back = match_call_back
        self.fail_call_back = fail_call_back
        self.error_call_back = error_call_back
        self.sensor = sensor

    def scan(self, path):
        response = self.requester.request(path)
        if self.fuzzer.fuzz(response):
            status = response.status_code
        else:
            status = None
        return status, response

    def threadSuspend(self):
        self.event.clear()
        for thread in self.threads:
            if thread.is_alive():
                self.pause_semaphore.acquire()

    def threadResume(self):
        self.event.set()

    def threadProc(self):
        self.event.wait()
        try:
            path = next(self.dictionary)
            path = path.lstrip('/')
            while path is not None:
                try:
                    status, response = self.scan(path)
                    if status is not None:
                        if response.status_code in [200, 301, 302, 303, 307] and self.sensor:
                            self.dictionary.addSensor(path)
                        full_path = urllib.parse.urlparse(
                            self.requester.url).path + path
                        self.match_call_back(full_path, response)
                    else:
                        self.fail_call_back(path, len(self.dictionary))
                except RequesterException as e:
                    self.error_call_back(e.args[0]['message'])
                    continue
                finally:
                    if not self.event.isSet():
                        self.pause_semaphore.release()
                        self.event.wait()
                    path = next(self.dictionary)
                    path = path.lstrip('/')
                    if not self.running:
                        break
        except StopIteration as e:
            return

    def threadStop(self):
        self.running = False
        self.event.set()

    def over(self):
        for thread in self.threads:
            thread.join(0.3)
            if thread.is_alive():
                return False
        return True

    def start(self):
        self.running = True
        if self.threads != []:
            self.threads = []
        for i in range(self.thread_counts):
            thread = threading.Thread(target=self.threadProc)
            thread.daemon = True
            self.threads.append(thread)
        self.event.clear()
        self.dictionary.reset()
        for t in self.threads:
            t.start()
        self.threadResume()

