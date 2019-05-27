# hiddenSensor
webdir scan，it works for ctf and actual combat

**更新到0.2版本，提高了--ctf的识别率**

#### 1. 支持平台      
**macOS|Linux|Windows**  
**python3**

#### 2. 用法    
**python3 -m pip install requests**
```
usage: hiddenSensor.py [-h] [-u URL] [-L URLLIST] [-e EXTENSION] [-H HEADERS]
                       [--user-agent USER_AGENT] [--random-agent] [-c COOKIES]
                       [-r RECURSIVE] [--proxy PROXY] [-s DELAY]
                       [--timeout TIMEOUT] [-m MAX_RETRIES] [-t THREADS_COUNT]
                       [-404 PATH_404] [--lowercase] [--uppercase]
                       [--dicts-path WORDLIST] [--ctf]

optional arguments:
  -h, --help            show this help message and exit

madatory settings:
  -u URL, --url URL     target
  -L URLLIST, --urlList URLLIST
                        url file path
  -e EXTENSION, --extension EXTENSION
                        the extension of website type (default : "php")

connection settings:
  -H HEADERS, --headers HEADERS
                        set headers
  --user-agent USER_AGENT
                        user-agent you want to specify
  --random-agent        random-agent (default: False)
  -c COOKIES, --cookie COOKIES
                        cookie you want to specify (example: -c
                        "domain=xxx;path=xxx")
  -r RECURSIVE, --recursive RECURSIVE
                        Recursive blasting subdir (default: 0 layers)
  --proxy PROXY         set proxy (http proxy,example:--proxy
                        http://127.0.0.1:1090)
  -s DELAY, --delay DELAY
                        time.sleep(delay) every request (default: 0)
  --timeout TIMEOUT     max time every request is waiting (default: 30 s)
  -m MAX_RETRIES, --max-retries MAX_RETRIES
                        max retries when meeting network problem (default: 5)

other settings:
  -t THREADS_COUNT, --thread THREADS_COUNT
                        max thread count you want to specify (default: 10)
  -404 PATH_404, --404-page PATH_404
                        the 404 page you want to specify (example: if
                        error.php -404 "error")
  --lowercase           force to be lowercase
  --uppercase           force to be uppercase
  --dicts-path WORDLIST
                        other dictionary you want to specify
  --ctf                 if it's specified, process will find sensor file
                        (xxx.php.bak, .xxx.php.swp ...)
```   
example:`python3 hiddenSensor.py -u http://www.xxx.com/ -e php --ctf`

#### 3. 特点    
1. **支持多线程**   
2. **支持http头部定制**   
3. **支持多个url扫描**
4. **支持暂停(ctrl+c)、继续**
5. **支持自定义字典，不过db里面的应该够了**
6. **支持自定义延时、最大重试次数**
7. **支持http代理**
8. **支持定义404路径**
9. **支持自定义几层递归扫描**
10. **支持`.bak|.swp`等文件扫描**      

#### 4. 感谢`dirsearch`
