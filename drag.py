#!/bin/python

from youtube import *

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject


class MainWindow(Gtk.Window):

    def __init__(self):
        """
        Initialize the gtk window
        """
        Gtk.Window.__init__(self, title="Youtube Drag and Drop")

        self.set_default_size(250, 250)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        self.drop_area = DropArea()

        box.pack_start(self.drop_area, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_homogeneous(True)
        box.add(hbox)

        button1 = Gtk.RadioButton.new_with_label_from_widget(
            None, 'Watch')
        button1.connect('toggled', self.on_button_toggled, 'watch')
        hbox.pack_start(button1, False, False, 0)

        button2 = Gtk.RadioButton.new_from_widget(button1)
        button2.set_label('Download')
        button2.connect('toggled', self.on_button_toggled, 'download')
        hbox.pack_start(button2, False, False, 0)

        self.drop_area.drag_dest_set_target_list(None)
        self.drop_area.drag_dest_add_text_targets()

        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, False, False, 0)

        self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)

    def on_button_toggled(self, button, mode):
        if button.get_active():
            if mode == 'download':
                self.drop_area.avformat = 'bestvideo[height<=1080]+bestaudio'
            elif mode == 'watch':
                self.drop_area.avformat = 'best'

    def on_timeout(self, user_data):
        """
        Set parameters for updating the progress bar
        """
        # Check if the Video object exists
        if hasattr(self.drop_area, 'v'):
            update_progress_bar(self.drop_area.v, self.progressbar)
        return True


class DropArea(Gtk.Label):

    def __init__(self):
        Gtk.Label.__init__(self)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)

        self.connect('drag-data-received', self.on_drag_data_received)

        self.avformat = 'best'

    def on_drag_data_received(
        self, widget, drag_context, x, y, data, info, time
            ):
        self.v = Video(data.get_text(), avformat=self.avformat)


if __name__ == '__main__':
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
