from pytube import YouTube
import os
import moviepy.editor as mp
from mhyt import yt_download

import re
import spacy

import urllib.request
import pytube
import urllib

import time

import azure.cognitiveservices.speech as speechsdk

import os.path
import json

import requests
import pafy
from flask import Flask, request
import jsons as jsons
from flask_restful import Api, Resource

# input1 = pd.read_json('/home/ckpl/Downloads/YouTube_content_analysis/sampleonerequest.json')
# input1.head()


class YoutubeAnalysisOutput:
    def __init__(self):
        # self.claims = ''
        self.videoStatus = ''
        self.views = ''
        self.date = ''
        self.likes = ''
        self.disLikes = ''
        self.comment = ''
        self.audioStatus = ''
        self.text = ''
        self.processedText = ''
        self.ingredients = ''
        self.duration = ''
        self.ratings = ''
        self.subscriber = ''
        self.author = ''
        self.key = ''
        self.title = ''


app = Flask(__name__)
api = Api(app)
app.config["DEBUG"] = False


@app.route('/api/youtube/extract', methods=['POST'])
def youtube_analysis_api():

    data = request.get_json()
    print(data)
    url = data['url']
    print(url)
    # div = data['div']
    # dept = data['dept']
    # claims = data['claims']

    # keep it in property file
    APIKEY = "AIzaSyC4b6O0miZBp4dkFOBQKPLInZdOObfJR_4"
    VideoID = url[url.find("https://youtu.be/") + 17:]

    params = {'id': VideoID, 'key': APIKEY,
              'fields': 'items(id,snippet(channelId,title,categoryId),statistics)',
              'part': 'snippet,statistics'}

    ######## google api call to youtube chennel starts ########

    start = 'https://www.googleapis.com/youtube/v3/videos'

    query_string = urllib.parse.urlencode(params)
    start = start + "?" + query_string

    with urllib.request.urlopen(start) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())

    ######## google api call to youtube chennel ends ########

    title = data['items'][0]['snippet']['title']
    comment = data['items'][0]['statistics']['commentCount']
    dislikes = data['items'][0]['statistics']['dislikeCount']
    likes = data['items'][0]['statistics']['likeCount']
    views = data['items'][0]['statistics']['viewCount']

    page = requests.get(url)
    paffy = pafy.new(url)
    youtube = YouTube(url)

    finalTitle = get_title(title, url, page)
    # final_comment = get_comment(url)
    finalDislikes = get_dislikes(dislikes, page)
    finalLikes = get_likes(likes, page)
    finalViews = get_views(views, url, page)
    finalDate = get_date(page)
    finalDuration = get_duration(url)
    finalKey = get_key(VideoID, paffy);
    finalAuthor = get_author(paffy, page, youtube)
    finalRatings = get_rating(paffy, page, youtube)
    finalSubscriber = get_subscriber(page, APIKEY)

    print(title)
    print(finalTitle)

    youtube_analysis_output_list = []

    youtube_analysis_output = YoutubeAnalysisOutput()

    youtube_analysis_output.title = finalTitle
    youtube_analysis_output.comment = comment
    youtube_analysis_output.dislikes = finalDislikes
    youtube_analysis_output.likes = finalLikes
    youtube_analysis_output.views = finalViews
    youtube_analysis_output.date = finalDate
    youtube_analysis_output.duration = finalDuration
    youtube_analysis_output.key = finalKey
    youtube_analysis_output.author = finalAuthor
    youtube_analysis_output.ratings = finalRatings
    youtube_analysis_output.subscriber = finalSubscriber

    title_extracted_from_video, videoStatus = video_extraction(finalTitle, youtube, url, youtube_analysis_output, paffy);
    print("Printing video status")
    print(title_extracted_from_video)
    print(videoStatus)

    audio_to_text_conversion(title_extracted_from_video, youtube_analysis_output, videoStatus)

    os.remove(VidDir + '/' + title_extracted_from_video + '.wav')
    os.remove(VidDir + '/' + title_extracted_from_video + '.mp4')

    youtube_analysis_output_list.append(youtube_analysis_output)

    print(youtube_analysis_output)

    jsonStr = jsons.dumps(youtube_analysis_output.__dict__)

    print(jsonStr)
    return jsonStr


def get_title(input_title, url, page):
    try:
        # title = apipart(url)[0]
        title = re.sub(r'[^\w\s]', '', input_title)
    except:
        try:
            # page = requests.get(url)
            title = re.search('title":"(.+?)"', page.text)
            title = title.group(1)
            title = re.sub(r'[^\w\s]', '', title)
        except:
            try:
                yt_obj = YouTube(url)
                title = yt_obj.title
                title = re.sub(r'[^\w\s]', '', title)
            except:
                try:
                    yt_obj = YouTube(url)
                    title = yt_obj.title
                    title = re.sub(r'[^\w\s]', '', title)
                except:
                    try:
                        response = requests.get(url).text
                        title = re.findall(r'"title":"[^>]*",', response)[0].split(',')[0][9:-1]
                        title = re.sub(r'[^\w\s]', '', title)
                    except:
                        title = 'empty'
    return title


def get_rating(paffy, page, youtube):
    try:
        rating = re.search('averageRating":(.+?),', page.text)
        rating = rating.group(1)
    except:
        try:
            rating = paffy.rating
        except:
            try:
                rating = youtube.rating
            except Exception as e:
                rating = e
    return rating


def get_views(input_views, url, page):
    try:
        views = input_views
    except:
        try:
            yt_obj = pafy.new(url)
            views = yt_obj.viewcount
        except:
            try:
                views = re.search('viewCount":"(.+?)"', page.text)
                views = views.group(1)
            except:
                try:
                    yt_obj = YouTube(url)
                    views = yt_obj.views
                except Exception as e:
                    views = e
    return views


def get_author(paffy, page, youtube):
    try:
        author = paffy.author
    except:
        try:
            author = re.search('author":"(.+?)"', page.text)
            author = author.group(1)
        except:
            try:
                author = youtube.author
            except Exception as e:
                author = e
    return author


def get_key(input_videoid, yt_obj):
    try:
        key = yt_obj.videoid
    except:
        try:
            key = input_videoid
        except Exception as e:
            key = e
    return key


def get_duration(url):
    try:
        yt_obj = pafy.new(url)
        duration = yt_obj.duration
    except Exception as e:
        duration = e
    return duration


def get_comment(url):
    try:
        comment = youtube_analysis_api(url)[1]
    except Exception as e:
        comment = e
    return comment


def get_dislikes(dislikes, page):
    try:
        # page = requests.get(url)
        dislikes = re.search('dislike this video along with (.+?) other people', page.text)
        dislikes = dislikes.group(1)
    except:
        try:
            dislikes = dislikes
        except Exception as e:
            dislikes = e
    return dislikes


def get_likes(likes, page):
    try:
        # page = requests.get(url)
        likes = re.search('like this video along with (.+?) other people', page.text)
        likes = likes.group(1)
    except:
        try:
            likes = likes
        except Exception as e:
            likes = e
    return likes


def get_date(page):
    try:
        # page = requests.get(url)
        date = re.search('datePublished" content="(.+?)">', page.text)
        date = date.group(1)
    except Exception as e:
        date = e
    return date


def get_subscriber(page, key):
    try:
        channelid = re.search('channelId":"(.+?)"', page.text)
        chanid = channelid.group(1)
        data = urllib.request.urlopen(
            "https://www.googleapis.com/youtube/v3/channels?part=statistics&id=" + chanid + "&key=" + key).read()
        subs = json.loads(data)
        subscriber = subs["items"][0]["statistics"]["subscriberCount"]
    except Exception as e:
        subscriber = e
    return subscriber


# input1['comment'] = input1['url'].apply(lambda x: comment(x))
# input1['date'] = input1['url'].apply(lambda x: date(x))
# input1['likes'] = input1['url'].apply(lambda x: likes(x))
# input1['dislikes'] = input1['url'].apply(lambda x: dislikes(x))
# input1['duration'] = input1['url'].apply(lambda x: duration(x))
# input1['key'] = input1['url'].apply(lambda x: key(x))
# input1['author'] = input1['url'].apply(lambda x: author(x))
# input1['views'] = input1['url'].apply(lambda x: views(x))
# input1['title'] = input1['url'].apply(lambda x: title(x))
# input1['rating'] = input1['url'].apply(lambda x: rating(x))
# input1['subscriber'] = input1['url'].apply(lambda x: subscriber(x))

VidDir = "/Users/smitasahu/Downloads/YT"


def file_base_name(file_name):
    if '.' in file_name:
        separator_index = file_name.index('.')
        base_name = file_name[:separator_index]
        return base_name
    else:
        return file_name


def path_base_name(VidDir):
    file_name = os.path.basename(VidDir)
    return file_base_name(file_name)


def video_extraction(input_title, youtube, input_url, youtube_api_json, paffy):

    print(input_title)
    print(youtube)
    print(input_url)
    print(paffy)

    title = input_title
    videoStatus = ""

    print(os.path.exists(VidDir + '/' + input_title + '.mp4'))

    if os.path.exists(VidDir + '/' + input_title + '.mp4') is False:
        try:
            def download_youtube(path):
                yt = youtube.streams.filter(progressive=True, file_extension='mp4').order_by(
                    'resolution').desc().first()
                if not os.path.exists(path):
                    os.makedirs(path)
                filename = yt.download(path)
                title = path_base_name(filename)
                return title

            final_title = download_youtube(input_url, VidDir)
            title = final_title
            youtube_api_json.videoStatus = 'success'
            videoStatus = 'success'
            # if input_title is 'empty':
            youtube_api_json.title = final_title

        except:
            try:
                def download_youtube(VidDir):
                    filename = youtube.streams.first().download(VidDir)
                    title = path_base_name(filename)
                    return title

                final_title = download_youtube(input_url, VidDir)
                title = final_title
                youtube_api_json.videoStatus = 'success'
                videoStatus = 'success'
                youtube_api_json.title = final_title
            except:
                try:
                    filename = pytube.YouTube(input_url).streams.get_highest_resolution().download(VidDir)
                    final_title = path_base_name(filename)
                    title = final_title
                    youtube_api_json.videoStatus = 'success'
                    videoStatus = 'success'
                    # if input_title is 'empty':
                    youtube_api_json.title = final_title
                except:
                    try:
                        def paffy_video(paffy, VidDir):
                            # video = pafy.new(url)
                            streams = paffy.streams
                            best = paffy.getbest(preftype="mp4")
                            best.download(VidDir)
                            title = paffy.title
                            return title

                        final_title = paffy_video(paffy, VidDir)
                        youtube_api_json.videoStatus = 'success'
                        videoStatus = 'success'
                        title = final_title
                        # if input_title is 'empty':
                        youtube_api_json.title = final_title
                    except:
                        try:
                            def mhyt_ydl(url, VidDir, title):
                                title = title + '.mp4'
                                ydl_opts = {
                                    'outtmpl': os.path.join(VidDir, title)
                                }

                                yt_download(url, video_format='mp4', ismucic=True, **ydl_opts)

                            mhyt_ydl(input_url, VidDir, input_title)

                            youtube_api_json.videoStatus = 'success'
                            videoStatus = 'success'

                        except Exception as e:
                            youtube_api_json.videoStatus = e
                            videoStatus = e

    else:
        youtube_api_json.videoStatus = 'video already exist'
        videoStatus = 'video already exist'

    return title, videoStatus


# for i in input1['title']:

def audio_to_text_conversion(input_title, youtube_api_json, video_status):

    input_video_status = youtube_api_json.__getattribute__("videoStatus")

    audio_status = ''
    print("we are inside audio ")
    print(video_status)
    print(input_video_status)

    if video_status is 'success':
        print(video_status)
        file = VidDir + '/' + input_title + '.mp4'
        if os.path.exists(VidDir + '/' + input_title + '.wav') is False:
            try:
                def aud(file):
                    video = mp.VideoFileClip(file)
                    newfile = file[:-4]
                    audio = video.audio.write_audiofile(newfile + ".wav")
                    title = path_base_name(file)
                    return title

                title = aud(file)
                youtube_api_json.audioStatus = 'success'
                audio_status = 'success'

                def concatenate_list_data(list):
                    result = ''
                    for element in list:
                        result += str(element)
                    return result

                def processed_text(list):
                    result = ''
                    for element in list:
                        result = re.sub(r'[^\w\s]', ' ', element)
                        result = re.sub(r'\d+', '', result)
                        result = result.lower().strip()
                        result = re.sub('\s+', ' ', result)
                    return result

                def ing(text, prdnlp):
                    result = ''
                    for model in prdnlp:
                        for element in text:
                            doc = model(str(element))
                            op = {ent.text for ent in doc.ents}
                            op = ', '.join(op)
                            temp = ","
                            result += op + temp
                            # print(result)
                    result = result[:-1]
                    each = result.split(",")
                    result = [x.strip(' ') for x in each]
                    result = set(result)
                    result = ', '.join(result)  # optional convert to str
                    return result

                def speech_recognize_continuous_from_file(file):
                    """performs continuous speech recognition with input from an audio file"""
                    # <SpeechContinuousRecognitionWithFile>
                    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
                    speech_config.endpoint_id = EndpointId
                    audio_config = speechsdk.audio.AudioConfig(filename=file)

                    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                                   audio_config=audio_config)

                    done = False

                    def stop_cb(evt):
                        """callback that stops continuous recognition upon receiving an event `evt`"""
                        # print('CLOSING on {}'.format(evt))
                        speech_recognizer.stop_continuous_recognition()
                        nonlocal done
                        done = True

                    all_results = []

                    def handle_final_result(evt):
                        all_results.append(evt.result.text)

                    speech_recognizer.recognized.connect(handle_final_result)
                    # Connect callbacks to the events fired by the speech recognizer
                    speech_recognizer.recognizing.connect(lambda evt: 'RECOGNIZING: {}'.format(evt))
                    speech_recognizer.recognized.connect(lambda evt: 'RECOGNIZED: {}'.format(evt))
                    speech_recognizer.session_started.connect(lambda evt: 'SESSION STARTED: {}'.format(evt))
                    speech_recognizer.session_stopped.connect(lambda evt: 'SESSION STOPPED {}'.format(evt))
                    speech_recognizer.canceled.connect(lambda evt: 'CANCELED {}'.format(evt))
                    # stop continuous recognition on either session stopped or canceled events
                    speech_recognizer.session_stopped.connect(stop_cb)
                    speech_recognizer.canceled.connect(stop_cb)

                    # Start continuous speech recognition
                    speech_recognizer.start_continuous_recognition()
                    while not done:
                        time.sleep(.5)
                    return all_results

                speech_key, service_region = "0f95674905f94c32abfe87a2679aa37d", "eastus"
                EndpointId = "a1679626-4779-43ba-8c6a-876722f5601f"

                prdnlp = [spacy.load('/Users/smitasahu/Downloads/YT/prdnlpNov06'),
                          spacy.load('/Users/smitasahu/Downloads/YT/prdnlpNov25'),
                          spacy.load('/Users/smitasahu/Downloads/YT/prdnlpNov29'),
                          spacy.load('/Users/smitasahu/Downloads/YT/prdnlpNov18')]

                if audio_status is 'success':
                    text_list = []
                    # i = input_title
                    temp = [speech_recognize_continuous_from_file(VidDir + '/' + input_title + '.wav') if (os.path.exists(
                        VidDir + '/' + input_title + '.wav')) is True else 'notexist']

                    for i in range(0, len(temp)):
                        text_list.append(concatenate_list_data(temp[i]))
                    youtube_api_json.text = text_list
                    processedText = processed_text(text_list)
                    youtube_api_json.processedText = processedText
                    youtube_api_json.ingredients = ing(processedText, prdnlp)

            except OSError as e:
                youtube_api_json.audioStatus = e
    else:
        youtube_api_json.audioStatus = 'aud already exist'


# end dataframe can b dumped into json
# input1.to_json(VidDir+'/'+'output.json', orient='records', lines=True)

if __name__ == '__main__':
    # reading url from properties file
    app.run(host="0.0.0.0", port=5000, debug=False)
