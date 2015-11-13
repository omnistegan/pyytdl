#!/bin/python

from gi.repository import Gtk, Gdk, GObject
from youtube import *


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Drag and Drop")

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
        Update value on the progress bar
        """
        try:
            if self.q.empty() == False:
                percent = self.q.get()
            self.progressbar.set_fraction(percent)
        except:
            pass

        # As this is a timeout function, return True so that it
        # continues to get called
        return True

    def create_video_instance(self, url):
        self.video = Video(url)
        self.q = self.video.download_and_play_av()


class DropArea(Gtk.Label):

    def __init__(self):
        Gtk.Label.__init__(self)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

        self.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(
        self, widget, drag_context, x, y, data, info, time
            ):
        win.create_video_instance(data.get_text())


if __name__ == '__main__':
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
