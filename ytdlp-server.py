import os
import time
import json
import flask
import base64
import socket
import hashlib
import threading
from http.cookiejar import LoadError
from flask_cors import CORS

from yt_dlp import YoutubeDL, DownloadError

RED = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE = '\033[0;94m'
YELLOW = '\033[0;33m'
END = '\033[0m'
app = flask.Flask(__name__)
CORS(app, resources=r'/*')
my_yt_dlp = None

CONFIG_FILE = 'config.json'
LOG_FILE = 'latest.log'

@app.route('/')
def index():
  return flask.render_template('index.html')

@app.route('/status')
def status():
  global my_yt_dlp
  result = my_yt_dlp.task_status()
  return restful(200, result['status'], result['data'])

@app.route('/download', methods=['GET','POST'])
def download():
  global my_yt_dlp
  if flask.request.method == 'POST':
    data = json.loads(flask.request.get_data().decode("utf-8"))
    url = data.get('url')
    cookie = data.get('cookie')
    format = data.get('format')
  else:
    result = flask.request.args
    url = result.get('url')
    cookie = ''
    format = ''
  if url == '':
    return restful(400, 'No URL input')
  else:
    result = my_yt_dlp.add(url, cookie, format)
    if 'Added' == result['status']:
      return restful(202, result['status'], result['data'])
    else:
      return restful(200, result['status'], result['data'])

@app.route('/info', methods=['GET','POST'])
def info():
  global my_yt_dlp
  if flask.request.method == 'POST':
    data = json.loads(flask.request.get_data().decode("utf-8"))
    url = data.get('url')
    mode = data.get('mode')
    cookie = data.get('cookie')
    format = data.get('format')
  else:
    data = flask.request.args
    url = data.get('url')
    mode = data.get('mode')
    cookie = ''
    format = ''
  if url == '':
    return restful(400, 'No URL input')
  else:
    if mode == 'raw':
      result = my_yt_dlp.info(url,'raw', cookie, format)
      return restful(200, result['status'], result['data'])
    else:
      result = my_yt_dlp.info(url,'brief', cookie, format)
      return restful(200, result['status'], result['data'])

@app.route('/history')
def history():
  global my_yt_dlp
  if task_list := my_yt_dlp.task_history():
    return restful(200, 'Success', task_list)
  else:
    return restful(200, 'No history yet')

@app.route('/clear_download')
def clear_download():
  global my_yt_dlp
  my_yt_dlp.download_list = []
  my_yt_dlp.error_code = 0
  my_yt_dlp.status = 'Cleared'
  return restful(200, my_yt_dlp.status)

@app.route('/clear_history')
def clear_history():
  global my_yt_dlp
  my_yt_dlp.download_history = []
  return restful(200, my_yt_dlp.status)

def restful(code=200, status='', data=''):
  response = {
    'code': code,
    'status': status,
    'data': data
  }
  return json.dumps(response, indent=2, ensure_ascii=False), code



class YT_DLP():
  def __init__(self, opts):
    '''init yt_dlp class'''
    super(YT_DLP, self).__init__()
    self.download_dir = opts.get('download_dir')
    self.opts = opts.get('ydl')
    self.opts['paths'] = {'home':self.download_dir}
    self.opts['logger'] = self.Logger(opts.get('log_dir') + LOG_FILE)
    self.cookies = opts.get('cookies')
    self.download_list = []
    self.download_history = []
    self.rpc_list = {}
    self.error_code = 0
    self.status = 'Init'
    threading.Thread(target=self.download_thread, daemon=True).start()

  def download_thread(self):
    '''download thread'''
    while(True):
      if self.download_list != []:
        url = self.download_list[0].get('url')
        info = self.download_list[0]
        self.error_code = self.download(url, info)
        self.download_list.pop(0)
        self.download_history.append(info)
        if self.error_code:
          self.status = f'Error with code: {self.error_code}'
        elif self.download_list == []:
          self.status = 'Listening'
        else:
          self.status = 'Downloading'
      time.sleep(1)

  def download(self, url, info):
    '''yt_dlp download method'''
    try:
      opts = self.opts.copy()
      if info['type'] == 'video':
        opts['paths'] = {'home':self.download_dir.rstrip('/')}
      else:
        opts['paths'] = {'home':self.download_dir.rstrip('/') + '/' + info['title']}
      opts['cookiefile'] = "cookies/" + self.cookies.get(info['cookie'])
      opts['format'] = info['format']
      # port = find_available_port()
      # if port:
      #   md5 = sum_md5(url)
      #   opts['external_downloader_args'].append(f'--gid={md5[:16]}')
      #   opts['external_downloader_args'].append(f'--rpc-secret={md5[:16]}')
      #   opts['external_downloader_args'].append(f'--enable-rpc=true')
      #   opts['external_downloader_args'].append(f'--rpc-listen-all=true')
      #   opts['external_downloader_args'].append(f'--rpc-allow-origin-all=true')
      #   print(f'{YELLOW}Start download for [{url}] with aria2c rpc port at localhost:{port} which GID is {md5[:16]}{END}')
      #   self.rpc_list[url] = {'port': port, 'token': md5[:16]}
      # else:
      #   opts['external_downloader_args'].append('--enable-rpc=false')
      #   print(f'{YELLOW}Start download for [{url}] with aria2c but has No available port！')
      ydl = YoutubeDL(opts)
      ydl.add_progress_hook(self.progress_hook)
      self.status = 'Downloading'
      error_code = ydl.download(url)
      print(f'\n{GREEN}Success download for {url}{END}')
      return error_code
    except Exception as e:
      return f'{e}'.replace(RED, '').replace(GREEN, '').replace(BLUE, '').replace(END, '')

  def check_cookies(self, url, cookie):
    if cookie:
      cookie_file = self.cookies.get('user_custom','cookies/custom.txt')
      open(cookie_file, mode='w').write(base64.b64decode(cookie).decode('utf-8'))
      return 'user_custom'

    for keyword in self.cookies:
      file = self.cookies[keyword]
      if keyword in url and os.path.exists(f"cookies/{file}"):
        return keyword
    
    return 'Null'

  def info(self, url, mode='brief', cookie='', format=''):
    '''get information from url'''
    try:
      cookie = self.check_cookies(url, cookie)
      opts = self.opts.copy()
      opts['cookiefile'] = "cookies/" + self.cookies.get(cookie)
      if format:
        opts['format'] = format
      else:
        opts['format'] = self.opts.get('format')
      extract_info = YoutubeDL(opts).extract_info(url, download=False)
      if mode == 'raw':
        return {'status': 'Success', 'data': extract_info}
      info = {}
      info['title'] = extract_info.get('title', 'unknown')
      info['url'] = extract_info.get('webpage_url', '')
      info['cookie'] = cookie
      info['format'] = opts['format']
      if 'entries' in extract_info:
        info['type'] = 'playlist'
        info['uploader'] = extract_info.get('entries')[0].get('uploader', '')
        info['count'] = len(extract_info.get('entries'))
        info['entires'] = []
        for i in range(info['count']):
          entries = extract_info.get('entries')
          item = {}
          item['title'] = entries[i].get('title', 'unknown')
          item['url'] = entries[i].get('webpage_url', '')
          item['uploader'] = entries[i].get('uploader', '')
          item['site'] = entries[i].get('extractor', 'unknown')
          item['thumbnail'] = entries[i].get('thumbnail', '')
          item['id'] = entries[i].get('display_id', '')
          item['duration'] = entries[i].get('duration', '')
          item['resolution'] = entries[i].get('resolution', '')
          item['ext'] = entries[i].get('ext', 'unknown')
          item['size'] = entries[i].get('filesize_approx', '')
          info['entires'].append(item)
      else:
        info['type'] = 'video'
        info['title'] = extract_info.get('title', 'unknown')
        info['url'] = extract_info.get('webpage_url', '')
        info['uploader'] = extract_info.get('uploader', '')
        info['site'] = extract_info.get('extractor', 'unknown')
        info['thumbnail'] = extract_info.get('thumbnail', '')
        info['id'] = extract_info.get('display_id', '')
        info['duration'] = extract_info.get('duration', '')
        info['resolution'] = extract_info.get('resolution', '')
        info['ext'] = extract_info.get('ext', 'unknown')
        info['size'] = extract_info.get('filesize_approx', '')
      if mode == 'brief':
        return {'status': 'Success', 'data': info}
      else:
        return {'status': 'Success', 'data': info}
    except LoadError:
      return {'status': 'Load cookies failed. See more <a href="http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt">Here</a>', 'data': ''}
    except Exception as e:
      status = f'{e}'.replace(RED, '').replace(GREEN, '').replace(BLUE, '').replace(END, '')
      if 'available formats' in str(e):
        status += '. See more <a href="https://github.com/yt-dlp/yt-dlp#format-selection">Here</a>'
      elif 'Unsupported URL' in str(e):
        status += '. See more <a href="https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md">Here</a>'
      return {'status': status, 'data': ''}

  def add(self, url, cookie='', format=''):
    '''detect url and start download'''
    try:
      query_info = self.info(url, cookies=cookie, format=format)
      info = query_info['data']
      if 'url' not in info:
        return query_info
      info['url'] = info['url'].rstrip('/')
      if info['url'] in [i.get('url') for i in self.download_list]:
        return self.task_status()
      else:
        self.download_list.append(info)
        self.status = 'Added'
        return {'status': self.status, 'data': info}
    except LoadError:
      return {'status': 'Load Cookies failed. See more from <a href="http://fileformats.archiveteam.org/wiki/Netscape_cookies.txt">Here</a>', 'data': ''}
    except Exception as e:
      status = f'{e}'.replace(RED, '').replace(GREEN, '').replace(BLUE, '').replace(END, '')
      if 'available formats' in str(e):
        status += '. See more <a href="https://github.com/yt-dlp/yt-dlp#format-selection">Here</a>'
      elif 'Unsupported URL' in str(e):
        status += '. See more <a href="https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md">Here</a>'
      return {'status': status, 'data': ''}

  def task_status(self):
    '''return running status and downloading list'''
    if self.status == 'Added':
      self.status = 'Downloading'
    if self.status == 'finished' and self.download_list != []:
      self.status = 'Downloading'
    return {'status': self.status, 'data': self.download_list}

  def task_history(self):
    '''downloaded url history'''
    return self.download_history

  def progress_hook(self, d):
    '''yt_dlp hook'''
    self.status = d['status']

  class Logger:
    '''yt_dlp log class'''
    def __init__(self, log_file):
      self.log = open(log_file, mode='a+')

    def __del__(self):
      self.log.close()

    def debug(self, msg):
      # For compatibility with youtube-dl, both debug and info are passed into debug
      # You can distinguish them by the prefix '[debug] '
      if msg.startswith('[debug] '):
        pass
      else:
        self.info(msg)

    def info(self, msg):
      prefix = '\n[' + time.strftime('%H:%M:%S', time.localtime()) + ' INFO] '
      msg = prefix + msg
      self.log.write(msg)

    def warning(self, msg):
      prefix = '\n[' + time.strftime('%H:%M:%S', time.localtime()) + ' WARNING] '
      msg = prefix + msg
      self.log.write(msg)

    def error(self, msg):
      prefix = '\n[' + time.strftime('%H:%M:%S', time.localtime()) + ' ERROR] '
      msg = prefix + msg
      self.log.write(msg)
      print(msg)


def import_json(file):
  '''import json'''
  content = '{}'
  if not os.path.exists(file):
    open(file,'w', encoding='utf-8').write('{}')
  elif temp := open(file, 'r', encoding='utf-8').read():
    content = temp
  return json.loads(content)

def sum_md5(string):
  '''compute the md5'''
  return hashlib.md5(string.encode('utf-8')).hexdigest()

def find_available_port(interface=''):
  '''find available port'''
  try:
    with socket.socket() as sock:
      sock.bind((interface, 0))
      return sock.getsockname()[1]
  except OSError:
    return None

if __name__ == '__main__':
  config = import_json(CONFIG_FILE)
  my_yt_dlp = YT_DLP(config)
  print('yt_dlp server start!')
  app.run(config['host'], config['port'])
