import threading
import urllib.parse


class Dictionary(object):
    def __init__(self, file_path, lowercase=False, uppercase=False, extension='php'):
        self.file_path = file_path
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.extension = extension
        self.lock = threading.Lock()
        self.dicts = self.getDict()
        self.index = 0
        self.sensor = []

    def getDict(self):
        dicts = []
        try:
            with open(self.file_path, 'r', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if '%EXT%' in line:
                        line = line.replace('%EXT%', self.extension)
                    dicts.append(urllib.parse.quote(line))
            if self.lowercase:
                result = list(set(map(lambda l: l.lower(), dicts)))
                result.sort()
            elif self.uppercase:
                result = list(set(map(lambda l: l.upper(), dicts)))
                result.sort()
            else:
                result = list(set(dicts))
                result.sort()
            return result
        except IOError as e:
            raise e

    def getNext(self):
        self.lock.acquire()
        try:
            path = self.dicts[self.index]

        except IndexError as e:
            self.lock.release()
            raise StopIteration
        self.index += 1
        self.lock.release()
        return path

    def addSensor(self, path):
        if path.endswith('/') or path.endswith('xml') or path.endswith('html'):
            return
        path = path.lstrip('/')
        if path not in self.sensor:
            sensor_file = []
            ext1 = ['{full}~', '.{full}.un~', '{full}~1', '{full}~2', '{full}~3', '.{full}.swp', '.{full}.swo', '.{full}.swn', '.{full}.swm', '.{full}.swl',
                    '{full}.bak', '{full}.bak~', '{full}.back', '{full}.swp', '{full}.swo', '{full}.zip', '{full}.rar', '{full}.7z', '{full}.tar.gz', '{full}.tar.xz']
            ext2 = ['{name}.txt', '{name}.bak', '{name}.zip',
                    '{name}.rar', '{name}.7z', '{name}.tar.gz', '{name}.tar.xz']
            name = path.split('.')[0]
            for ext in ext1:
                ext = ext.format(full=path)
                if ext not in self.dicts:
                    sensor_file.append(ext)
            for ext in ext2:
                ext = ext.format(name=name)
                if ext not in self.dicts:
                    sensor_file.append(ext)
            self.sensor.extend(sensor_file)
            self.dicts.extend(sensor_file)

    def reset(self):
        self.index = 0

    def __next__(self):
        return self.getNext()

    def __len__(self):
        return len(self.dicts)
