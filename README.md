# Jav.land-videos
[Jav.land](https://jav.land/en/) videos detailer and edit PMV video

# Installation
```bash
git clone https://github.com/DARKDEV22/Jav.land-videos
cd Jav.land-videos
python -m pip install -r requirements.txt
```

# Using
- get video detail from Jav.land website : copy url from any page 

![pic2](https://user-images.githubusercontent.com/121659506/210045491-ca042353-ebbe-4259-b08a-2a5d52e7984f.png)

```python
from main import JavLandSoup

URL = "https://jav.land/en/genre/pl8e7l.html?page=3"
J = JavLandSoup(URL)
pageVideosDetail = J.videoListsFromMainPage()
```

```
# return
[ { name: name of video,
    code : video code,
    link : link to a single video page,
    coverImage : link of cover image},
...
]
```

- download video from any page
```
from main import VideoStuff

D = VideoStuff()
L = J.videoListsFromMainPage()
dir = "videos"
os.makedirs(dir, exist_ok=True)
for video in L :
    detail = J.getVideoDetail(video)
    if detail['sampleVideo'] != "---" and len(detail['cast']) == 1:
        D.downloadVideo(detail['sampleVideo'], dest=f"{dir}/{detail['code']}.mp4")
        with open(f"{dir}/desc.txt", "a+") as f :
            f.write(f"{detail['code']}\n")
```

- split all videos
```
filePath = [os.path.join(dir, name) for name in os.listdir(dir) if name.endswith("mp4")]
for path in filePath :
    D.splitVideoClip(path, start_at=5, duration_split=10)
```
- combine videos
```
folderPath = [os.path.join(dir, name) for name in os.listdir(dir) if not name.endswith("mp4") and not name.endswith("txt")]
combined_dir = "combined"
os.makedirs(combined_dir, exist_ok=True)
D.combineClip(folderPath, dest=f"{combined_dir}/combined.mp4")
```

- or combine with split screen with one long video
```
from moviepy.editor import VideoFileClip, clips_array

clip = VideoFileClip(f'{combined_dir}/combined.mp4')
timePerWindow = int(clip.end / 4)

w1 = clip.subclip(0, timePerWindow)
w2 = clip.subclip(timePerWindow, timePerWindow*2)
w3 = clip.subclip(timePerWindow*2, timePerWindow*3)
w4 = clip.subclip(timePerWindow*3, timePerWindow*4)

final = clips_array([
    [w1, w2],
    [w3, w4]
]).write_videofile(f'{combined_dir}/final.mp4')
```

- or 4 videos

![pic3](https://user-images.githubusercontent.com/121659506/210046002-06ea928f-6eb6-4e47-b2df-80eaaee8b576.png)

```
v = VideoStuff()
v.stackVID(["v1.mp4", "v2.mp4", "v3.mp4", "v4.mp4"])
```

and more
- add audio
- add clip speed

example videos : 
- [ena koume x mei washio](https://spankbang.com/7myy6/video/ena+koume+x+mei+washio)
- [split screen JAV](https://spankbang.com/7myv3/video/split+screen+jav)
