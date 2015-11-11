#!/bin/python

import youtube_dl

import json
import os
import subprocess
from time import sleep
from multiprocessing import Process, Queue
from glob import glob


DOWNLOAD_FOLDER = os.path.expanduser('~/Downloads/Youtube/')



def start_thread(function, *args):
    process = Process(target=function, args=args)
    process.start()
    return process


class Video():

    def return_json(self, dump):
        return json.dumps(dump)

    def return_formats(self):
        return self.results['formats']

    def find_best_audio(self, max_abr=None):
        format_abr = []
        for each in self.formats:
            if (
                'abr' in each.keys() and
                (max_abr == None or each['abr'] <= max_abr)
            ):
                format_abr.append((each['format_id'], each['abr']))
        format_abr.sort(key=lambda tup: tup[1], reverse=True)
        return format_abr[0][0]

    def find_best_video(self, max_height=None):
        format_filesize = []
        for each in self.formats:
            if (
                ('height' in each.keys() and each['filesize'] != None) and
                (max_height == None or
                    (each['height'] != None and each['height'] <= max_height)
                )
            ):
                format_filesize.append((each['format_id'], each['height'], each['filesize']))
        format_filesize.sort(key=lambda tup: tup[2], reverse=True)
        return format_filesize[0][0]

    def find_best_av(self, max_height=None):
        format_filesize = []
        for each in self.formats:
            if (
                'DASH' not in each['format_note'] and
                'height' in each.keys() and
                ( max_height == None or each['height'] <= max_height )
            ):
                format_filesize.append((each['format_id'], each['height'] ))
        format_filesize.sort(key=lambda tup: tup[1], reverse=True)
        return format_filesize[0][0]

    def download(self, avformat, q):
        options = {
            'noplaylist': True,
            'format': avformat,
            'outtmpl': DOWNLOAD_FOLDER + '%(uploader)s - %(title)s - %(id)s - %(format)s.%(ext)s',
            'nopart': True,
            'progress_hooks': [self.status_hook],
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            results = ydl.extract_info(self.url, download = True)

    def status_hook(self, ytdl_ob):
        if ytdl_ob['status'] == 'finished':
            self.q.put(1.0)
            print('Youtube Download: Finished downloading')
        if ytdl_ob['status'] == 'downloading':
            percent = ytdl_ob['downloaded_bytes']/ytdl_ob['total_bytes']
            self.q.put(percent)

    def play_with_mpv(self, timeout=10):
        # Wait for the file to appear
        count = timeout
        while count >= 0:
            if [n for n in glob(DOWNLOAD_FOLDER + '*' + self.id + '*') if os.path.isfile(n)] != []:
                break
            else:
                sleep(1)
                count -= 1
            if count == 0:
                print('Youtube Download: Download Timeout')
                exit()
        # Use glob to select the full correct filename to use
        video_file_path = [n for n in glob(DOWNLOAD_FOLDER + '*' + self.id + '*') if os.path.isfile(n)][0]
        # Wait for the file to be large enough to play (~4MB)
        count = timeout
        while count >= 0:
            if os.path.getsize(video_file_path) > 4000000:
                break
            else:
                sleep(1)
                count -= 1
            if count == 0:
                print('Youtube Download: File did not reach 4MB, attempting to play')
                break
        # Play the file with mpv, --keep-open is used to not close the file if it reaches EOF due to slow download
        subprocess.call(['mpv', video_file_path, '--really-quiet' , '--keep-open'])
        self.q.put(0.0)
        self.download_process.terminate()


    def download_and_play_av(self):
        self.q = Queue()
        self.download_process = start_thread(self.download, self.find_best_av(), self.q)
        self.mpv_process = start_thread(self.play_with_mpv, )
        return self.q


    def download_and_mux_best_av(self, max_height=1080):
        try:
            self.download(self.find_best_video(max_height) + '+' + self.find_best_audio())
            self.play_with_mpv()
        except:
            self.download_and_play_av()


    def __init__(self, url):
        with youtube_dl.YoutubeDL() as ydl:
            self.results = ydl.extract_info(url, download = False)
        self.url = url
        self.formats = self.return_formats()
        self.id = self.results['id']
        self.video_file_path = ''
