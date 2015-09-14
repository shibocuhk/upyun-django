# upyun_django
This package provides django storage for upyun cdn, API services are provided by official upyun [python-sdk](https://github.com/upyun/python-sdk)
## Important Notice
Still under development, not fully tested. 
## Classes

### UpYunStorage
Implement the `open(), save(), delete(), exists(), listdir(), modified_time(), size()` and ` url()` abstract methods of the base Storage class with [python-sdk](https://github.com/upyun/python-sdk)

### UpYunStorageFile
This file class will create a temp file with `TemporaryFile()`, `write()` will only write content to the temp file, to upload the content to server, remember to call `close()`

### UpYunStaticStorage
By setting `STATICFILES_STORAGE=upyun_django.UpYunStaticStorage`, you can collect you static file to upyun cdn.
`collectstatic` use modified_time to decide whether copy the file or not. To reduce the number of request, this class will preload
all the entry on the cloud and save to the local cache.


## Installation
Download the package and install manually or `pip install git+git://github.com/shibocuhk/upyun-django.git`

## Usage
```
UPYUN_BUCKET = '<YOUR BUCKET>'
UPYUN_USERNAME = '<OPERATOR_NAME>'
UPYUN_PASSWORD = '<OPERATOR_PASSWORD>'
UPYUN_STATIC_ROOT = '<STATIC_ROOT>'
STATICFILES_STORAGE = 'upyun_django.storage.UpYunStaticStorage'
```
Run
`python manage.py collectstatic`

## TODO
### Add upyun form api support
UpYunFileField
signature generation method
### support medial file management

