from __future__ import unicode_literals
import json

import argparse
import os
import re
from itertools import starmap
import multiprocessing

import pysrt
import imageio
# import youtube_dl
import chardet
import nltk
import os
proxy = 'http://edcguest:edcguest@172.31.100.29:3128'

os.environ['http_proxy'] = proxy 
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy
# imageio.plugins.ffmpeg.download()
# nltk.download('punkt')

import subprocess
import sys
from moviepy.editor import VideoFileClip, concatenate_videoclips
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.lsa import LsaSummarizer
import moviepy.editor as mpe

# imageio.plugins.ffmpeg.download()


def timeStamp(list_time):

    format_time = dict()
    i = 0
    for time in list_time:
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        format_time[str(i)] = {"%dh%02dm%02ds" % (h, m, s): time}
        i += 1
    return format_time


def summarize(srt_file, n_sentences, language="english"):
    parser = PlaintextParser.from_string(
        srt_to_txt(srt_file), Tokenizer(language))
    stemmer = Stemmer(language)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    segment = []
    for sentence in summarizer(parser.document, n_sentences):
        index = int(re.findall("\(([0-9]+)\)", str(sentence))[0])
        item = srt_file[index]
        segment.append(srt_segment_to_range(item))
    return segment


def srt_to_txt(srt_file):

    text = ''
    for index, item in enumerate(srt_file):
        if item.text.startswith("["):
            continue
        text += "(%d) " % index
        text += item.text.replace("\n", "").strip("...").replace(
                                     ".", "").replace("?", "").replace("!", "")
        text += ". "
    return text


def srt_segment_to_range(item):
    start_segment = item.start.hours * 60 * 60 + item.start.minutes * \
        60 + item.start.seconds + item.start.milliseconds / 1000.0
    end_segment = item.end.hours * 60 * 60 + item.end.minutes * \
        60 + item.end.seconds + item.end.milliseconds / 1000.0
    return start_segment, end_segment


def time_regions(regions):
    return sum(starmap(lambda start, end: end - start, regions))


def find_summary_regions(srt_filename, duration=30, language="english"):

    srt_file = pysrt.open(srt_filename)

    enc = chardet.detect(open(srt_filename, "rb").read())['encoding']
    srt_file = pysrt.open(srt_filename, encoding=enc)

    # generate average subtitle duration
    subtitle_duration = time_regions(
        map(srt_segment_to_range, srt_file)) / len(srt_file)
    # compute number of sentences in the summary file
    n_sentences = duration / subtitle_duration
    print(subtitle_duration)
    print(n_sentences)
    summary = summarize(srt_file, n_sentences, language)
    total_time = time_regions(summary)
    too_short = total_time < duration
    if too_short:
        while total_time < duration:
            n_sentences += 1
            summary = summarize(srt_file, n_sentences, language)
            total_time = time_regions(summary)
    else:
        while total_time > duration:
            n_sentences -= 1
            summary = summarize(srt_file, n_sentences, language)
            total_time = time_regions(summary)
    return summary


def create_summary(filename, regions):
    subclips = []
    input_video = VideoFileClip(filename)
    last_end = 0
    for (start, end) in regions:
        subclip = input_video.subclip(start, end)
        subclips.append(subclip)
        last_end = end
    return concatenate_videoclips(subclips)


def get_summary(filename, subtitles):
    clip = VideoFileClip(filename)
    regions = find_summary_regions(subtitles, clip.duration/10, "english")
    summary = create_summary(filename, regions)
    base, ext = os.path.splitext(filename)
    output = "{0}_.mp4".format(base)
    summary.write_videofile(
                output,
                codec="libx264",
                audio=True,
                temp_audiofile="temp.m4a", remove_temp=False, audio_codec="aac")
    # summary.write_videofile(output, temp_audiofile="/home/ankitb/Downloads/GTube-master/temp.m4a")
    # summary = summary.set_audio("temp.m4a")

    cmd = "ffmpeg -i " + output + " -i temp.m4a -c:v copy -c:a copy " + output[0:len(output)-4] + "1.mp4";
    subprocess.call(cmd, shell=True)
    os.remove(output)
    os.remove("temp.m4a")
    return True


def download_video_srt(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': '1.%(ext)s',
        'subtitlesformat': 'srt',
        'writeautomaticsub': True,
    }

    movie_filename = ""
    subtitle_filename = ""
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # ydl.download([subs])
        result = ydl.extract_info("{}".format(url), download=True)
        movie_filename = ydl.prepare_filename(result)
        subtitle_info = result.get("requested_subtitles")
        # subtitle_language = subtitle_info.keys()[0]
        subtitle_language = "en"
        # subtitle_ext = subtitle_info.get(subtitle_language).get("ext")
        subtitle_ext = "vtt"
        subtitle_filename = movie_filename.replace(".mp4", ".%s.%s" %
                                                   (subtitle_language,
                                                    subtitle_ext))
    return movie_filename, subtitle_filename


def fun(movie_filename, subtitle_filename):
    # movie_filename, subtitle_filename = download_video_srt(url)
    summary_retrieval_process = multiprocessing.Process(target=get_summary, args=(movie_filename, subtitle_filename))
    summary_retrieval_process.start()
    summary_retrieval_process.join()
    # os.remove(movie_filename)
    # os.remove(subtitle_filename)
    print("[sum.py] Remove the original files")

# if __name__ == '__main__':
    # app.run()

# fun("https://youtu.be/D5VN56jQMWM")
# fun("stranger_things.mp4", "stranger_things_sub.srt")
if __name__ == '__main__':
    # url = "https://www.youtube.com/watch?v=-6OFqkemd4c"
    url = sys.argv[1]
    srt = sys.argv[2]
    fun(sys.argv[1], sys.argv[2])