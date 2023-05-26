# [YT-DLP Server](#ytdlp-server)

## Introduction
YT-DLP Server is an server side for [yt-dlp](https://github.com/yt-dlp/yt-dlp/) that can allow you run it in your server.

## Notice
- Server side is English but the webpage is in all chinese, you can translate it.
- No download speed or duration for display.

## Features
- Depend on Flask.
- Easy use API, RESTful-API style respond.
- Multi-threaded download task.
- User-friendly interactive and interface.
- Server with single python file, webpage with single HTML file, easy for learning.

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

### Usage Notes
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
  
  ` POST http://127.0.0.1:8848/download `
* #### post params
  ` cookies: Base64 encode Netscape format cookies file. `
  
  ` url: The url that input for yt-dlp. `
  
  ` mode: Default is "brief" and optional in "brief" or "raw". `
  
* ##### response
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
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "cookies": 'youtube'
  }
}
```
### /info
Get video information via yt-dlp.
#### params
- url: The url that input for yt-dlp.
- mode: Default is "brief" and optional in "brief" or "raw".
#### example
* ##### request
  ` GET http://127.0.0.1:8848/info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ `
  
  ` POST http://127.0.0.1:8848/info `
* #### post params
  ` cookies: Base64 encode Netscape format cookies file. `
  
  ` url: The url that input for yt-dlp. `
  
  ` mode: Default is "brief" and optional in "brief" or "raw". `
  
* ##### response
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
    "size": 59080956,
    "cookies": 'youtube'
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
* ##### response
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
* ##### response
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
* ##### response
```
{
  "code": 400,
  "status": "Cleared",
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
* ##### response
```
{
  "code": 400,
  "status": "Cleared",
  "data": ""
}
```


## License
[![License](https://img.shields.io/github/license/shadlc/ytdlp-server.svg?style=flat)](https://github.com/shadlc/ytdlp-server/blob/main/LICENSE)
