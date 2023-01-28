import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .common import *

argparser = buildargs()
args = argparser.parse_args()

bbsengine.initscreen()

try:
    main(args)
except KeyboardInterrupt:
    ttyio.echo("{/all}{bold}INTR{bold}")
except EOFError:
    ttyio.echo("{/all}{bold}EOF{/bold}")
finally:
    ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
