# [YT-DLP Server](#ytdlp-server)

## Introduction
YT-DLP Server is an server side for [yt-dlp](https://github.com/yt-dlp/yt-dlp/) that can allow you run it in your server.

## Features
1. Depend on Flask.
2. Easy use API, RESTful-API style respond.
3. Multi-threaded download task.
4. Download with aria2, each tasks RPC host support.
5. User-friendly interactive and interface.

## Use
### Install Aria2
You need to install aria2 first because this script depends on aria2 for more quickly download speed.
- https://github.com/aria2/aria2
### Init Envirment
    $ python -m venv ytdlp-server
    $ cd ytdlp-server

* For Windows
`
    $ .\Scripts\Activate.ps1
`
* For other platform
`
    $ source bin/activate
`
### Download
    $ git clone https://github.com/shadlc/ytdlp-server.git
    $ cd ytdlp-server
### Install Requirements
    $ pip install -r requirements.txt
### Run
    $ python3 ytdlp-server.py

#### Usage Notes
When started this script, you can download videos to server via yt-dlp. You can modify the configuration file "config.json". 

## Web Page
- http://127.0.0.1:8848/

## API

### /download
Directly download the video via yt-dlp.
#### params
- url: The url that input for yt-dlp.
#### example
* ##### request
` GET http://127.0.0.1:8848/download?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ `
* ##### responed
```
{
  "code": 200,
  "status": "Added",
  "data": {
    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
    "thumbnail": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp",
    "site": "youtube",
    "uploader": "Rick Astley",
    "id": "dQw4w9WgXcQ",
    "duration": 212,
    "resolution": "1920x1080",
    "ext": "webm",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  }
}
```
### /info
Get video information via yt-dlp.
#### params
- url: The url that input for yt-dlp.
- type: Default is "brief" and optional in "brief" or "raw".
#### example
* ##### request
` GET http://127.0.0.1:8848/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ `
* ##### responed
```
{
  "code": 200,
  "status": "Success",
  "data": {
    "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
    "thumbnail": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/maxresdefault.webp",
    "site": "youtube",
    "uploader": "Rick Astley",
    "id": "dQw4w9WgXcQ",
    "duration": 212,
    "resolution": "1920x1080",
    "ext": "webm",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "size": 59080956
  }
}
```

### /status
Get the status about download task.
#### params
- None
#### example
* ##### request
` GET http://127.0.0.1:8848/status `
* ##### responed
```
{
  "code": 200,
  "status": "Init",
  "data": {
    "tasks": {}
  }
}
```

### /history
Get the history you downloaded.
#### params
- None
#### example
* ##### request
` GET http://127.0.0.1:8848/history `
* ##### responed
```
{
  "code": 400,
  "status": "No history yet",
  "data": ""
}
```

### /clear_download
Clear the downloading list.
#### params
- None
#### example
* ##### request
` GET http://127.0.0.1:8848/clear_download `
* ##### responed
```
{
  "code": 400,
  "status": "cleared",
  "data": ""
}
```

### /clear_history
Clear the download history.
#### params
- None
#### example
* ##### request
` GET http://127.0.0.1:8848/clear_history `
* ##### responed
```
{
  "code": 400,
  "status": "cleared",
  "data": ""
}
```


## License
[![License](https://img.shields.io/github/license/shadlc/ytdlp-server.svg?style=flat)](https://github.com/shadlc/ytdlp-server/blob/main/LICENSE)