import os
import warnings
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.request
from random import shuffle
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, clips_array
warnings.filterwarnings("ignore")

class JavLandSoup :
    def __init__(self, URL: str = "https://jav.land/en/v_mostwanted.php") :
        """
        scrap video detail from jav.land website
        input : URL from page that have many videos
        return : detail every single video
        """
        self.baseURL = baseURL = "https://jav.land"
        assert URL.startswith(self.baseURL) , f"[ERROR] expect URL from JAV.LAND website but got {URL}" 
        self.baseVideoLink = "https://videos.vpdmm.cc/litevideo/freepv/"
        self.soup = BeautifulSoup(
            requests.get(URL).text, "html.parser"
        ).find_all("div", class_="panel-body no-padding")
        self.videoList: List[str] = str(self.soup).split('<div class="panel-body no-padding">')[1:]

    def videoListsFromMainPage(self) -> List[Dict]  :
        """
        input : URL from page that have many videos
        return : detail every single video
        """
        videoLists: List[Dict] = []
        for video in self.videoList :
            videoName: str = video.split("</a>")[0].split('<img alt="')[1].split("src=")[0].strip()[:-1]
            videoCode: str = video.split("</a>")[0].split('<img alt="')[1].split("src=")[1].split('"/>\n<span class="bsid">')[1][:-7]
            videoLink: str = self.baseURL + video.split("</a>")[0].split("><")[0].split('href="')[1][:-1]
            imageLink: str = video.split("</a>")[0].split('<img alt="')[1].split("src=")[1].split('"/>\n<span class="bsid">')[0].strip()[1:]
    
            videoDict = {
                'name' : videoName,
                'code' : videoCode,
                'link' : videoLink,
                'coverimage' : imageLink
            }
            
            videoLists.append(videoDict)

        return videoLists
    
    def getVideoDetail(self, videoFromMainPage: Dict) -> Dict :
        """
        input Dict from videoListsFromMainPage but just a single one
        return video detail such as videolinks images cast director etc.
        """
        videoLink = videoFromMainPage['link']
        videoDetail = videoFromMainPage.copy()

        response = requests.get(videoLink)
        soup = BeautifulSoup(response.text, 'html.parser')
        detailSoup = str(soup.find_all('table', class_="videotextlist table table-bordered table-hover"))
        detailList =  detailSoup.split("</tr>")[2:]

        releaseDate = detailList[0].split('<td>')[1][:-6]
        d = releaseDate.split('-')[-1]
        m = releaseDate.split('-')[1]
        y = releaseDate.split('-')[0]
        releaseDate = f'{d}/{m}/{y}'

        try :
            length = int(detailList[1].split('<td>')[1][:-9])
        except :
            length = int(detailList[1].split('<td>')[1][:-9][-4:-1])

        hour = length // 60 
        minute = length - (hour*60)
        length = f'{hour}:{minute} hr' if minute >= 10 else f'{hour}:0{minute} hr'

        try :
            director = detailList[2].split("director")[3].split('rel="tag">')[1].split('</a>')[0]
        except :
            director = detailList[2].split("director")[0].split('</td>')[1][5:]

        serieName = detailList[3].split('<td>')[1][:-6]
        if serieName != "---" :
            serieName = serieName.split('rel="tag">')[1][:-11]
            
        maker = detailList[4].split('rel="tag">')[1].split('</a>')[0]

        genreLists: List[str] = []
        for i, genre in enumerate(detailList[6].split("<span ")[1:], start=1) :
            genre = genre.split('rel="category tag">')[1][:-11]
            genreLists.append(genre)
        genreLists[-1] = genreLists[-1][:-6]
        
        cast = [ name.split('</a>')[0] for name in detailList[7].split('rel="tag">')[1:] ]
        
        try :
            imageSoup = str(soup.find_all('span', id="waterfall")[0]).split('<img src="')
            imageLinks: List[str] = []
            for i, imageLink in enumerate(imageSoup, start=1) :
                if i != len(imageSoup) :
                    imageLink = imageLink.split('href="')[1][:-2]
                    imageLinks.append(imageLink)
        except :
            imageLinks = "---"
        
        try :
            videoSoup = str(soup).split('class="img-responsive" src="')[1].split('pl.jpg"/>\n<div class="" id="video_favorite_edit">')[0][36:]
            if "real" in videoSoup :
                temp = str("84" + videoSoup.split("/")[0][3:])
                videoSoup = temp + "/" + temp
            sampleVideo = f'{self.baseVideoLink}{videoSoup[0]}/{videoSoup[:3]}/{videoSoup}_mhb_w.mp4'

            v_available = "200" in str(requests.get(sampleVideo))
            if not v_available :
                sampleVideo = f'{self.baseVideoLink}{videoSoup[0]}/{videoSoup[:3]}/{videoSoup}_dmb_w.mp4'
    
                v_available = "200" in str(requests.get(sampleVideo))
                if not v_available :
                    relink = videoSoup.split("00")
                    relink = "".join(relink)
                    sampleVideo = f'{self.baseVideoLink}{videoSoup[0]}/{videoSoup[:3]}/{relink}_mhb_w.mp4'
        
                    v_available = "200" in str(requests.get(sampleVideo))
                    if not v_available :
                        sampleVideo = f'{self.baseVideoLink}{videoSoup[0]}/{videoSoup[:3]}/{relink}_dmb_w.mp4'
            
                        v_available = "200" in str(requests.get(sampleVideo))
                        if not v_available :
                            sampleVideo = "---"
        except :
            sampleVideo = "---"
        
        videoDetail.update({
            'cast' : cast,
            'sampleVideo' : sampleVideo,
            'maker' : maker,
            'genre' : genreLists,
            'serieName' : serieName,
            'releaseDate' : releaseDate,
            'length' : length,
            'director' : director,
            'imageLinks' : imageLinks 
        })
        return videoDetail

    def getFullVideo(self, code: str) :
        """
        get full video link from code 
        """
        webs = ["hpj", "javguru", "javmost"]
        fullLinks = {}
        for idx, web_ in enumerate([self.hpj, self.guru, self.javmost]) :
            current_url = web_(code)
            if current_url != "---" :
                fullLinks[webs[idx]] = current_url

        return fullLinks
    
    def hpj(self, code: str) :
        hpjSearch = "https://hpav.tv/?s="
        hpjBase = "https://hpav.tv/"
        URL = hpjSearch + code
        r = requests.get(URL)
        s = BeautifulSoup(r.text, "html.parser").find_all('div', class_="featured-content-image")

        links = str(s).split('<a href="')[-1].split("rel")[0].strip()[:-1]
        codeChecking = links.split("/")[-1].upper()
        if codeChecking != code :
            return "---"

        videopageLink = hpjBase + links
        r = requests.get(videopageLink)
        avai = 200 == r.status_code
        if avai :
            return videopageLink

        return '---'
    
    def guru(self, code: str) :
        videopageLink = "https://jav.guru/" + code + '/'
        avai = 200 == requests.get(videopageLink).status_code
        if avai :
            return videopageLink
        return "---"

    def javmost(self, code: str) :
        videopageLink = "https://www5.javmost.com/" + code + '/'
        r = requests.get(videopageLink).text
        avai = "The page you're looking for doesn't exist." not in r
        if avai :
            return videopageLink
        return "---"

    
    def __str__(self) :
        return "jav.land scraping site"

class VideoStuff :
    def __init__(self) :
        """
        video editor for PMV video
        """
        pass 

    def downloadVideo(self, link: str, dest: str = "video.mp4") :
        """
        download video from website
        """
        urllib.request.urlretrieve(link, dest)
        print("[INFO] DOWNLOAD SUCCESS!!")

    def splitVideoClip(self, filename: str, start_at = 4, duration_split = 5, end_at = False, speed = 1.0) :
        """
        split video clip from duration 
        start_at = time(s) that what to start split
        duration_split = every second for splition
        end_at = time(s) before end 
        return .mp4 split file in new folder
        """
        try :
            clip = VideoFileClip(filename).speedx(speed)
            splitList = [f'{start_at}-{start_at+duration_split}']
            if end_at  :
                print(end_at)
                end_at /= speed
            clipDuration = clip.duration - end_at
            timeLeft = int((clipDuration - int(splitList[0].split("-")[1])) // duration_split)
        
            for i in range(timeLeft) :
                start = int(splitList[-1].split("-")[-1])
                endtime = start + duration_split
                splitList.append(f"{start}-{endtime}")
            splitList[-1] = splitList[-1].split("-")[0] + "-" + str(int(clipDuration))
            
            folderName = f"{str(filename[:-4])}_split"
            os.makedirs(folderName, exist_ok=True)
            for i, timeSplit in enumerate(splitList, start=1) :
                start = int(timeSplit.split("-")[0])
                end = int(timeSplit.split("-")[1])
                clip.subclip(start, end).write_videofile(f"{folderName}/{i}.mp4")        
            
            print(f"[INFO] {filename} SPLITING SUCCESS!!")
        except :
            print(f"[ERROR] this file : {filename} cannot be split")
    
    def combineClip(self, folderpath: List[str], dest: str = "final.mp4", random = True) :
        """
        combine short videoclip
        random = random order video
        """
        videoPath = []
        for path in folderpath :
            videoPath += [
                os.path.join(path, name)
                for name in os.listdir(path)
            ]
        
        if random :
            shuffle(videoPath)
        
        clips = [ VideoFileClip(clip) for clip in videoPath ]
        concatenate_videoclips(clips, method="compose").write_videofile(dest)

    def addAudio(self, videoname: str, audioname: str, destname: str = "final_audio_added.mp4",volumn: float = 0.7, audio_start: int = 5) :
        """
        add audio to videofile
        """
        v_clip = VideoFileClip(videoname)
        a_clip = AudioFileClip(audioname).subclip(audio_start, v_clip.end + audio_start).volumex(volumn)
        final_audio = CompositeAudioClip([v_clip.audio, a_clip])
        final_clip = v_clip.set_audio(final_audio)
        final_clip.write_videofile(destname)
        print("[INFO] COMBINE AUDIO SUCCESS!!")

    def stackVID(self, videoPaths : List[str], destname: str = "final_stack.mp4") :
        """
        stack video in one screen 
        """
        assert len(videoPaths) == 4 , "[ERROR] 4 screen stack only"
        clips = [VideoFileClip(path) for path in videoPaths]
        shortest = min(clips[0].end, clips[1].end, clips[2].end, clips[0].end)
        
        for idx in range(4) :
            clips[idx] = clips[idx].subclip(0, shortest)

        final = clips_array([
            [clips[0], clips[1]],
            [clips[2], clips[3]]
        ]).write_videofile(destname)

        print("[INFO] STACKING VIDEOs SUCCESS!!")
