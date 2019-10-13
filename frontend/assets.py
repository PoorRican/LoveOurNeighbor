from os import listdir as ls
from os.path import join
from django_assets import Bundle, register
from frontend.settings import BASE_DIR

fn = ['app.module.js', 'app.config.js', 'filters.js', 'routes.js']

_path = join(BASE_DIR, "static/app/")
_dirs = ('campaign', 'donations', 'layout', 'ministry', 'news', 'people', 'search', 'services', 'static')

for _ in _dirs:
    _dir = join(_path, _)
    files = ls(_dir)
    fn.extend([join(_dir, i) for i in files])       # join the filepath with `_`

fn = [join(_path, i) for i in fn]                   # join the filepath with `_path`

angular_js = Bundle(*fn, filters='jsmin', output='packed.js')
register('angular_js', angular_js)