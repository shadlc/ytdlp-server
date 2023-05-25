import os
import time
import json
import copy
import flask
import socket
import hashlib
import requests
import threading
from flask_cors import CORS
from yt_dlp import YoutubeDL

GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
ENDC = '\033[0m'
app = flask.Flask(__name__)
CORS(app, resources=r'/*')
MyYTDLP = None

OPT_FILE = 'config.json'
LOG_FILE = 'latest.log'

@app.route('/')
def index():
  return flask.render_template('index.html')

@app.route('/download')
def download():
  global MyYTDLP
  if flask.request.method == 'POST':
    url = request.form['url']
  else:
    result = flask.request.args
    url = result['url'] if 'url' in result else ''
  if url == '':
    return restful(400, 'No URL input')
  else:
    result = MyYTDLP.start(url)
    if 'Added' == result['status']:
      return restful(202, result['status'], result['data'])
    else:
      return restful(200, result['status'], result['data'])

@app.route('/status')
def status():
  global MyYTDLP
  result = MyYTDLP.task_status()
  return restful(200, result['status'], result['data'])

@app.route('/info')
def info():
  global MyYTDLP
  if flask.request.method == 'POST':
    url = request.form['url']
  else:
    result = flask.request.args
    url = result['url'] if 'url' in result else ''
    mode = result['mode'] if 'mode' in result else ''
  if url == '':
    return restful(400, 'No URL input')
  else:
    if mode == 'essential':
      result = MyYTDLP.info(url)
      return restful(200, result['status'], result['data'])
    elif mode == 'raw':
      result = MyYTDLP.info(url,'raw')
      return restful(200, result['status'], result['data'])
    else:
      result = MyYTDLP.info(url)
      return restful(200, result['status'], result['data'])

@app.route('/history')
def history():
  global MyYTDLP
  if task_list := MyYTDLP.task_history():
    return restful(200, 'Success', task_list)
  else:
    return restful(400, 'No history yet')

@app.route('/clear_download')
def clear_download():
  global MyYTDLP
  MyYTDLP.download_list = {}
  MyYTDLP.error_code = 0
  MyYTDLP.status = 'Cleared'
  return restful(200, MyYTDLP.status)

@app.route('/clear_history')
def clear_history():
  global MyYTDLP
  MyYTDLP.download_history = {}
  return restful(200, MyYTDLP.status)

def restful(code=200, status='', data=''):
  response = {
    'code': code,
    'status': status,
    'data': data
  }
  return json.dumps(response, indent=2, ensure_ascii=False), code



class YTDLP():
  def __init__(self, opts):
    '''init yt_dlp class'''
    super(YTDLP, self).__init__()
    self.download_dir = opts['download_dir']
    self.opts = opts['ydl']
    self.opts['logger'] = self.Logger()
    self.opts['paths'] = {'home':self.download_dir}
    self.download_list = {}
    self.download_history = {}
    self.rpc_list = {}
    self.error_code = 0
    self.status = 'Init'

  def download_thread(self, url, info):
    '''download thread'''
    self.download_list[url] = info
    self.error_code = self.download(url, info)
    self.download_list.pop(url)
    self.download_history[url] = info
    if self.download_list == {}:
      self.status = 'Listening'
    elif self.error_code:
      self.status = f'Error with code: {self.error_code}'
    else:
      self.status = 'Downloading'

  def download(self, url, info):
    '''yt_dlp download method'''
    if 'bilibili' in url and os.path.exists("cookies/bilibili.txt"):
      self.opts['cookiefile'] = "cookies/bilibili.txt"
    elif 'youtube' in url and os.path.exists("cookies/youtube.txt"):
      self.opts['cookiefile'] = "cookies/youtube.txt"
    elif 'qq' in url and os.path.exists("cookies/qqvideo.txt"):
      self.opts['cookiefile'] = "cookies/qqvideo.txt"
    opts = self.opts.copy()
    if info['type'] == 'video':
      opts['paths'] = {'home':self.download_dir.rstrip('/') + '/' + info['uploader']}
    else:
      opts['paths'] = {'home':self.download_dir.rstrip('/') + '/' + info['uploader'] + '/' + info['title']}
    # port = find_available_port()
    # if port:
    #   md5 = sum_md5(url)
    #   opts['external_downloader_args'].append(f'--gid={md5[:16]}')
    #   opts['external_downloader_args'].append(f'--rpc-secret={md5[:16]}')
    #   opts['external_downloader_args'].append(f'--enable-rpc=true')
    #   opts['external_downloader_args'].append(f'--rpc-listen-all=true')
    #   opts['external_downloader_args'].append(f'--rpc-allow-origin-all=true')
    #   print(f'{YELLOW}Start download for [{url}] with aria2c rpc port at localhost:{port} which GID is {md5[:16]}{ENDC}')
    #   self.rpc_list[url] = {'port': port, 'token': md5[:16]}
    # else:
    #   opts['external_downloader_args'].append('--enable-rpc=false')
    #   print(f'{YELLOW}Start download for [{url}] with aria2c but has No available port！')
    ydl = YoutubeDL(opts)
    ydl.add_progress_hook(self.progress_hook)
    self.status = 'Downloading'
    error_code = ydl.download(url)
    print(f'\n{GREEN}Success download for {url}{ENDC}')
    return error_code

  def info(self, url, mode='essential'):
    '''get informations from url'''
    try:
      if 'bilibili' in url and os.path.exists("cookies/bilibili.txt"):
        self.opts['cookiefile'] = "cookies/bilibili.txt"
      elif 'youtube' in url and os.path.exists("cookies/youtube.txt"):
        self.opts['cookiefile'] = "cookies/youtube.txt"
      elif 'qq' in url and os.path.exists("cookies/qqvideo.txt"):
        self.opts['cookiefile'] = "cookies/qqvideo.txt"
      extract_info = YoutubeDL(self.opts).extract_info(url, download=False)
      if mode == 'raw':
        return {'status': 'Success', 'data': extract_info}
      info = {}
      if 'entries' in extract_info:
        info['type'] = 'playlist'
        info['title'] = extract_info.get('title')
        info['url'] = extract_info.get('webpage_url')
        info['uploader'] = extract_info.get('entries')[0].get('uploader')
        info['count'] = len(extract_info.get('entries'))
        info['entires'] = []
        for i in range(info['count']):
          entries = extract_info.get('entries')
          item = {}
          item['title'] = entries[i].get('title')
          item['site'] = entries[i].get('extractor')
          item['thumbnail'] = entries[i].get('thumbnail')
          item['uploader'] = entries[i].get('uploader')
          item['id'] = entries[i].get('display_id')
          item['duration'] = entries[i].get('duration')
          item['resolution'] = entries[i].get('resolution')
          item['ext'] = entries[i].get('ext')
          item['url'] = entries[i].get('webpage_url')
          item['size'] = entries[i].get('filesize_approx')
          info['entires'].append(item)
      else:
        info['type'] = 'video'
        info['title'] = extract_info.get('title')
        info['url'] = extract_info.get('webpage_url')
        info['uploader'] = extract_info.get('uploader')
        info['site'] = extract_info.get('extractor')
        info['thumbnail'] = extract_info.get('thumbnail')
        info['id'] = extract_info.get('display_id')
        info['duration'] = extract_info.get('duration')
        info['resolution'] = extract_info.get('resolution')
        info['ext'] = extract_info.get('ext')
        info['size'] = extract_info.get('filesize_approx')
      if mode == 'essential':
        return {'status': 'Success', 'data': info}
      else:
        return {'status': 'Success', 'data': info}
    except:
      return {'status': 'Invaid URL', 'data': ''}

  def start(self, url):
    '''detect url and start download'''
    info = self.info(url)['data']
    if 'url' in info:
      url = info['url']
    elif 'webpage_url' in info:
      url = info['webpage_url']
    else:
      return {'status': 'Invaid URL', 'data': ''}
    url = url.rstrip('/')
    info['url'] = url
    if url in self.download_list:
      return self.task_status()
    else:
      threading.Thread(target=self.download_thread, args=(url, info), daemon=True).start()
      self.status = 'Added'
      return {'status': self.status, 'data': info}
    try:
      pass
    except:
      return {'status': 'Invaid URL', 'data': ''}

  # def count_process(self):
  #   for url in self.rpc_list:
  #     port = self.rpc_list[url]['port']
  #     token = self.rpc_list[url]['token']
  #     response = requests.post(f'http://localhost:{port}/jsonrpc', data = '{"jsonrpc":"2.0","method":"aria2.tellActive","id":1,"params": ["token:' + token + '"]}')
  #     result = json.loads(response.text)
  #     if not result['result']:
  #       continue
  #     result = result['result'][0]
  #     self.download_list[url]['size'] = result['totalLength']
  #     self.download_list[url]['download_speed'] = result['downloadSpeed']
  #     self.download_list[url]['processed'] = result['completedLength']

  def task_status(self):
    '''return running status and downloading list'''
    if self.status == 'Added':
      self.status = 'Downloading'
    if self.status == 'finished' and self.download_list != {}:
      self.status = 'Downloading'
    # self.count_process()
    return {'status': self.status, 'data': self.download_list}

  def task_history(self):
    '''downloaded url history'''
    return self.download_history

  def progress_hook(self, d):
    '''yt_dlp hook'''
    self.status = d['status']

  class Logger:
    '''yt_dlp log class'''
    def __init__(self):
      if os.path.exists(LOG_FILE):
        self.log = open(LOG_FILE, mode='a')
      else:
        self.log = open(LOG_FILE, mode='w')

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
  config = import_json(OPT_FILE)
  MyYTDLP = YTDLP(config)
  print('yt_dlp server start!')
  app.run(config['host'], config['port'])
