#!/bin/python

from gi.repository import Gtk, Gdk, GObject
from youtube import *


class MainWindow(Gtk.Window):

    def __init__(self):
        """
        Initialize the gtk window
        """
        Gtk.Window.__init__(self, title="Youtube Drag and Drop")

        self.set_default_size(250, 250)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_homogeneous(False)
        self.add(box)

        self.drop_area = DropArea()

        box.pack_start(self.drop_area, True, True, 0)

        self.drop_area.drag_dest_set_target_list(None)
        self.drop_area.drag_dest_add_text_targets()

        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, False, False, 0)

        self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)

    def on_timeout(self, user_data):
        """
        Set parameters for updating the progress bar
        """
        # Check if the Video object exists and that the Queue is not empty.
        if (
            hasattr(self.drop_area, 'v') and
            self.drop_area.v.q.empty() == False
        ):
            hook = self.drop_area.v.q.get()
            if (
                hook['status'] == 'downloading' and
                hook['downloaded_bytes'] > 4000000
            ):
                percent = (
                    hook['downloaded_bytes'] /
                    hook['total_bytes']
                    )
                self.progressbar.set_fraction(percent)
            elif hook['status'] == 'media_player_terminate':
                self.progressbar.set_fraction(hook['fraction'])
            else:
                self.progressbar.set_fraction(
                    hook['downloaded_bytes'] / 4000000)
        return True


class DropArea(Gtk.Label):

    def __init__(self):
        Gtk.Label.__init__(self)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

        self.connect('drag-data-received', self.on_drag_data_received)

    def on_drag_data_received(
        self, widget, drag_context, x, y, data, info, time
            ):
        self.v = Video(data.get_text())


if __name__ == '__main__':
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
