# pyytdl

A simple drag and drop interface for watching youtube videos (and other streaming media) using a native player such as mpv.

To use a media player other than mpv (or to set your own options), change media_player_subprocess_args in the watch_now method in youtube.py

You may need to install and/or symlink GObject for GTK to work properly.

Use your package manager:

```
sudo pacman -Syu python-gobject
```

symlink to your virtualenv:
```
ln -s /usr/lib/python3.*/site-packages/gobject* /path_to_your_virtualenv/venv/lib/python3.*/site-packages/
```
