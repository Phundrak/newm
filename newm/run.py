import logging

from .layout import Layout

from pywm import (
    PYWM_MOD_LOGO,
    # PYWM_MOD_ALT
)

def run():
    logging.basicConfig(format='[%(levelname)s] %(filename)s:%(lineno)s %(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    wm = Layout(
        PYWM_MOD_LOGO,
        xkb_model="macintosh",
        xkb_layout="de,de",
        xkb_options="caps:escape",
        output_scale=2.0,
        encourage_csd=False,

        # See comments in view.py
        xwayland_handle_scale_clientside=True,
        enable_output_manager=False,

        # TODO: Find these
        wallpaper="/etc/wallpaper.jpg",
        panel_dir="/usr/lib/node_modules/newm-panel"
    )

    try:
        wm.run()
    except Exception:
        logging.exception("Unexpected")
    finally:
        wm.terminate()
