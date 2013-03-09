from tw2.core import CSSLink, DirLink, JSLink
from tw2.jquery import jquery_js

ddmenu_js = JSLink(location='head', filename='static/js/ddmenu.js',
                   resources=[jquery_js])

ddmenu_css = CSSLink(location='head', filename='static/css/style.css')
