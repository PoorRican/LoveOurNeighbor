from os import listdir as ls
from os.path import join
from django_assets import Bundle, register
from frontend.settings import BASE_DIR

fn = ['app.module.js', 'app.config.js', 'filters.js']

# JS
_path = join(BASE_DIR, "static/js/")
js = Bundle(*[join('js', i) for i in ls(_path)], filters='jsmin', output='assets/packed.js')

# Angular JS
_path = join(BASE_DIR, "static/app/")
_dirs = ('campaign', 'donations', 'layout', 'ministry', 'news', 'people', 'search', 'services', 'static')

# iterate through `static/app` directory and crawl for relevant .js files
for _ in _dirs:
    _dir = join(_path, _)
    files = ls(_dir)
    fn.extend([join(_dir, i) for i in files])  # join the filepath with `_`

fn = [join(_path, i) for i in fn]  # join the filepath with `_path`

app = Bundle(*fn, filters='jsmin', output='assets/app.js')

# CSS
_path = join(BASE_DIR, "static/css")
css = Bundle(*[join('css', i) for i in ls(_path)], filters='cssmin', output='assets/packed.css')

register('js', js)
register('css', css)
register('app', app)
