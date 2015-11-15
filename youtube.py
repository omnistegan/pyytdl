#!/bin/python

from glob import glob
from multiprocessing import Process, Queue
import os
import subprocess
from time import sleep
import youtube_dl

DOWNLOAD_FOLDER = os.path.expanduser('~/Downloads/Youtube/')


def start_thread(function, *args):
    # Start and return a process with *args
    process = Process(target=function, args=args)
    process.start()
    return process


def cleanup(path, size=100000000):
    # Remove file if it is less than ~100MB
    if os.path.getsize(path) < size:
        os.remove(path)


class Video():

    """
    This class sets the necessary options and provides two functions:
     - starting the download
     - playing the file.
    """

    def __init__(self, url, avformat='best', watch=True):
        if '+' in avformat:
            watch = False
        self.q = Queue()
        self.resultsq = Queue()
        self.url = url
        self.options = {
            'noplaylist': True,
            'format': avformat,
            'outtmpl': (
                DOWNLOAD_FOLDER +
                '%(uploader)s - %(title)s - %(id)s - %(format)s.%(ext)s'),
            'nopart': True,
            'progress_hooks': [self.status_hook],
        }
        self.ydl = youtube_dl.YoutubeDL(self.options)
        self.download_thread = start_thread(self.download_video, watch)
        while True:
            # Take the first result to enter Queue, which will be the info_dict
            if self.resultsq.empty() == False:
                self.results = self.resultsq.get()
                self.id = self.results['id']
                break
        if watch:
            self.media_player_thread = start_thread(self.watch_now, )

    def status_hook(self, hook_dict):
        # Places the status hook dict into the Queue
        self.q.put(hook_dict)

    def download_video(self, watch=True):
        # extract_info returns a dict of info regarding the url submitted
        results = self.ydl.extract_info(self.url, process=True, download=False)
        self.resultsq.put(results)
        self.id = results['id']
        results = self.ydl.process_ie_result(results, download=True)
        if watch is False:
            self.watch_now()

    def watch_now(self, timeout=10):
        """
        This function controls ensuring the file exists and
        is large enough to begin playing.
        Calls at the end of this function terminate
        the download process and reset the progress bars.
        """
        # Set the media player arguments
        media_player_subprocess_args = ['mpv', '--really-quiet', '--keep-open']
        # Wait for the file to appear
        count = timeout*100
        while count >= 0:
            if ([n for n in glob(
                    DOWNLOAD_FOLDER + '*' + self.id + '*'
                    ) if os.path.isfile(n)] != []):
                break
            else:
                sleep(.01)
                count -= 1
            if count == 0:
                exit()
        # Use glob to select the full correct filename to use
        video_file_path = [n for n in glob(
            DOWNLOAD_FOLDER + '*' + self.id + '*'
            ) if os.path.isfile(n)][0]
        media_player_subprocess_args.append(video_file_path)
        # Wait for the file to be large enough to play (~4MB)
        count = timeout*100
        while count >= 0:
            if os.path.getsize(video_file_path) > 4000000:
                break
            else:
                sleep(.01)
                count -= 1
            if count == 0:
                # If we timeout, the media player will still be called
                break
        # Play the file with mpv
        subprocess.call(media_player_subprocess_args)
        # Cleanup download_thread, progress bar, and file on disk
        if hasattr(self, 'download_thread'):
            self.download_thread.terminate()
        self.q.put({'status': 'media_player_terminate', 'fraction': 0.0})
        cleanup(video_file_path)
