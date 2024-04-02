import cv2
import random
import re

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

def seed_db(episodes_path, cursor):
    cursor.execute("CREATE TABLE episode(number INTEGER PRIMARY KEY, title, season, url, episode_number)")
    cursor.execute("CREATE TABLE frame(id INTEGER PRIMARY KEY, number, episode_id, view_count)")
    seasons = load_all_from_file(episodes_path)
    season_index = 1
    episode_index = 0
    episode_index2 = 0
    for season in seasons:
        for episode in season.episodes: 
            episode_name = re.search(r'^\d+\.\s*(.*)', episode.title)
            episode_number = re.search(r'^(\d+)', episode.title)
            if episode_name is None or episode_number is None:
                print("Episode name or episode number found to be None, skipping")
                continue
            cursor.execute("INSERT into episode VALUES (?, ?, ?, ?, ?)", (episode_index, episode_name.group(1), season_index, episode.url, episode_number.group(1)))
            episode_index +=1
        for episode in season.episodes:
            vidcap = cv2.VideoCapture(episode.url) 
            total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
            for i in range(0,total_frames):
                cursor.execute("INSERT into frame (number, episode_id, view_count) VALUES (?, ?, ?)", (i, episode_index2, 0))
            episode_index2 +=1
        season_index +=1 

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

def get_random_frame(cursor):
    cursor.execute("SELECT * FROM episode ORDER BY RANDOM() LIMIT 1") 
    episode = cursor.fetchone()
    cursor.execute("SELECT * FROM frame WHERE episode_id = ?", (episode[0],))
    episode_frames = cursor.fetchall()
    random_frame, frame_index = get_episode_random_frame(episode[3], len(episode_frames)-1)
    episode_views = episode_frames[frame_index][3] + 1
    cursor.execute("UPDATE frame SET view_count=? WHERE id=?", (episode_views, episode_frames[frame_index][0])) 
    return (random_frame, episode, frame_index)

def get_episode_random_frame(url,frame_count ):
    vidcap = cv2.VideoCapture(url)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    start = 95*fps # capture from second 95
    stop = 50*fps # capture to before last n seconds
    random_frame_index = calculate_random_frame(frame_count, start, stop)
    return (get_frame(vidcap, random_frame_index),random_frame_index)

def calculate_random_frame(frame_count, start, stop):
    first_frame = int(start)
    last_frame = int(frame_count-stop)
    return random.randint(first_frame, last_frame)

def get_frame(episode_vidcap, frame_number):
    episode_vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    _, frame = episode_vidcap.read()
    _, frame_bytes = cv2.imencode('.jpg', frame)
    return frame_bytes

