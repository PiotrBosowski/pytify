import os
import pytube
import queue
import pytify.settings as settings
import threading
from pytify.database.database import Database
# from moviepy.editor import *

DL_ENGINE = 'yt-dlp'


class DownloadWorker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get the work from the queue and expand the tuple
            url = self.queue.get()
            try:
                download_video_if_not_exist(url)
            finally:
                self.queue.task_done()


def urls_in_folder(folder, url_list):
    """
    Generates the list of urls in folder.
    :param folder: Single folder of chrome_bookmarks.folders.
    :param url_list: List of urls.
    """
    for url in folder.urls:
        url_list.append(url['url'])

    for child in folder.folders:
        urls_in_folder(child, url_list)


def download_video(url):
    """
    Downloads a video from youtube.
    :param url: Url of the youtube video.
    """
    youtube = pytube.YouTube(url)
    print(youtube.streams.filter(progressive=True).all())

    name = youtube.streams[0].default_filename
    cwd = os.getcwd()

    file_path_name = cwd + '/' + name
    mp3_file = file_path_name.strip('.mp4') + '.mp3'

    video = youtube.streams.filter(res='720p').first()

    try:
        video.download()
        print('[+] Downloaded!')
    except:
        print('[-] Something went wrong...')


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


class PPHook:
    def __init__(self):
        self.output_filename = None

    def __call__(self, pp):
        if pp['postprocessor'] == 'MoveFiles' and pp['status'] == 'started':
            self.output_filename = pp['info_dict']['filepath']


def download_video_as_mp3(url):
    """
    Downloads a video and converts it to the .mp3 format.
    :params url: Url of the youtube video.
    """
    os.makedirs(settings.save_audio_path, exist_ok=True)
    if DL_ENGINE == 'pytube':
        youtube = pytube.YouTube(url)
        video = youtube.streams.filter(only_audio=True).first()
        video.download(output_path=settings.save_audio_path)

        default_filename = video.default_filename
        video_path = os.path.join(settings.save_audio_path, default_filename)
        clip = AudioFileClip(video_path)

        file_path = os.path.splitext(video_path)[0] + '.mp3'
        clip.write_audiofile(file_path)
        clip.close()
        os.remove(video_path)
        print('[+] Downloaded!')
        filename = os.path.splitext(default_filename)[0]
    if DL_ENGINE == 'youtube-dl':
        import youtube_dl
        ydl_opts = {
            'extract_audio': True,
            'audio_format': 'wav',
            'format': 'bestaudio/best',
            'restrict_filenames': True,
            'outtmpl': f'{settings.save_audio_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            file_path = ydl.prepare_filename(info)
            filename = os.path.basename(file_path)
            ydl.process_info(info)  # starts the download
    if DL_ENGINE == 'yt-dlp':
        from yt_dlp import YoutubeDL
        ydl_opts = {
            'format': 'bestaudio/best',
            # 'quiet': True,
            'lazy_playlist': True,
            'noplaylist': True,
            'restrictfilenames': True,
            'outtmpl': f'{settings.save_audio_path}/%(title)s.%(ext)s',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }]
        }
        with YoutubeDL(ydl_opts) as ydl:
            output_filepath_hook = PPHook()
            result = ydl.add_postprocessor_hook(output_filepath_hook)
            info = ydl.extract_info(url, download=False)
            print(f'Downloading {info["title"]}...')
            error_code = ydl.download(url)
            filepath = output_filepath_hook.output_filename
            filename = os.path.basename(filepath)
    database = Database.get_database()
    database.add_record(url, filepath, filename)


def download_with_threads(video_links, use_threads=False):
    """
    Uses threads to download videos
    :params video_links: List of videos.
    :params use_threads: If run with threads.
    """
    tuple_list = []
    if use_threads:
        que = queue.Queue()
        threads = []
        for video in video_links:
            t = threading.Thread(target=download_video_if_not_exist,
                                 args=(video,))
            threads.append(t)
            t.start()
    else:
        for video in video_links:
            tuple_list.append(download_video_if_not_exist(video))


def download_video_if_not_exist(url):
    """
    Checks if following url already exists in the database. If so, it
    is not being downloaded.
    :param url: Url that is being checked.
    """
    database = Database.get_database()
    if not database.check_if_exist(url):
        try:
            download_video_as_mp3(url)
        except Exception as ex:
            print(f'[X] Failed to download the file from {url}. Details:\n{ex}')
    else:
        print('[*] Url already exists in database.')
