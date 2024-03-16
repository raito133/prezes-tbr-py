import os
import cv2
import random

class Episode:
    def __init__(self, title, url):
        self.title = title
        self.url = url
    def __str__(self):
        return self.title + " " + self.url + "\n"

class Season:
    def __init__(self, name):
        self.name = name
        self.episodes = []
    def add_episode(self,title,url):
        episode = Episode(title, url)
        self.episodes.append(episode)
    def __str__(self):
        returnstr = ""
        for episode in self.episodes:
            returnstr += episode.__str__()
        return returnstr
def load_all_from_file(file_name):
    f = open(file_name, "r")
    lines = f.readlines()
    structure = []
    currentSeason = ''
    num_lines = len(lines)
    current_line_index = 0
    while current_line_index < num_lines:
        currentLine = lines[current_line_index].strip()
        if currentLine == "":
            current_line_index += 1
            continue 
        if "SEZON" in currentLine:
            currentSeason = Season(currentLine)
            structure.append(currentSeason)
            current_line_index +=1
            continue
        if currentSeason != '':
            structure[structure.index(currentSeason)].add_episode(lines[current_line_index].strip(), lines[current_line_index+1].strip())
            current_line_index +=2
            continue
    return structure

def kiepski_random_frame(file_name):
    structure = load_all_from_file(file_name)
    random_season = structure[random.randint(0,len(structure)-1)]
    episode = random_season.episodes[random.randint(0, len(random_season.episodes)-1)]
    file_name = episode.title
    
    vidcap = cv2.VideoCapture(episode.url)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    video_length_seconds = total_frames/fps

    start = 95 # capture from second 95
    stop = 50 # capture to before last n seconds

    first_frame = int(start*fps)
    last_frame = int((video_length_seconds-stop)*fps)

    random_frame = random.randint(first_frame, last_frame)
    time_of_frame = random_frame/fps
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
    _, frame = vidcap.read()
    _, frame_bytes = cv2.imencode('.jpg', frame)
    return (frame_bytes, file_name)

