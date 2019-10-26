from os import listdir as ls
from os.path import join
from django_assets import Bundle, register
from frontend.settings import BASE_DIR

fn = ['app.module.js', 'app.config.js', 'filters.js', 'routes.js']

_path = join(BASE_DIR, "static/js/")
js = Bundle(*[join('js', i) for i in ls(_path)], filters='jsmin', output='assets/packed.js')

_path = join(BASE_DIR, "static/css")
css = Bundle(*[join('css', i) for i in ls(_path)], filters='cssmin', output='assets/packed.css')

register('js', js)
register('css', css)
