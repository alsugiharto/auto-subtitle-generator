import whisper
import os
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
import ssl
import json
import yaml

class VideoTranscriber:
    def __init__(self, model_path, video_path):
        self.model = whisper.load_model(model_path)
        self.video_path = video_path
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self):
        print('Transcribing video')
        result = self.model.transcribe(self.audio_path)
        text = result["segments"][0]["text"]
        textsize = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, config['FONT_SIZE_SPLIT'], 2)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16/9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)].shape[1]
        width = width - (width * 0.1)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textsize[0] / len(text))

        for j in tqdm(result["segments"]):
            lines = []
            text = j["text"]
            end = j["end"]
            start = j["start"]
            total_frames = int((end - start) * self.fps)
            start = start * self.fps
            total_chars = len(text)
            words = text.split(" ")
            i = 0
            
            while i < len(words):
                words[i] = words[i].strip()
                if words[i] == "":
                    i += 1
                    continue
                length_in_pixels = len(words[i]) * self.char_width
                remaining_pixels = width - length_in_pixels
                line = words[i] 
                
                while remaining_pixels > 0:
                    i += 1 
                    if i >= len(words):
                        break
                    length_in_pixels = len(words[i]) * self.char_width
                    remaining_pixels -= length_in_pixels
                    if remaining_pixels < 0:
                        continue
                    else:
                        line += " " + words[i]
                
                line_array = [line, int(start) + 15, int(len(line) / total_chars * total_frames) + int(start) + 15]
                start = int(len(line) / total_chars * total_frames) + int(start)
                print(line_array)
                lines.append(line_array)
                self.text_array.append(line_array)
        
        if config['NEW_TRANSCRIBE']:
            with open(f"{config['FOLDER_PATH']}transcription.json", "w") as f:
                json.dump(self.text_array, f)

        cap.release()
        print('Transcription complete')
    
    def extract_audio(self, output_audio_path):
        print('Extracting audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio 
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')
    
    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = width / height
        N_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)]

            with open(f"{config['FOLDER_PATH']}transcription.json") as handle:
                text_array = json.loads(handle.read())
            print(text_array)

            for i in text_array:
                if N_frames >= i[1] and N_frames <= i[2]:
                    text = i[0]
                    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, config['FONT_SIZE_PRINT'], 2)
                    # position of text
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    # position of text is in middle vertically
                    text_y = int(height*config['TEXT_POSITION_Y'])
                    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, config['FONT_SIZE_PRINT'], TEXT_COLOR, 2)
                    break
            
            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1
        
        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        self.extract_frames(image_folder)
        
        print("Video saved at:", output_video_path)
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))
        
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        
        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.set_audio(audio)
        clip.write_videofile(output_video_path)

# load yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
print('CONFIG')
print(config)

# setup variables and constants
ssl._create_default_https_context = ssl._create_unverified_context #disable SSL
TEXT_COLOR = (config['TEXT_COLOR_R'],config['TEXT_COLOR_G'],config['TEXT_COLOR_B'])
model_path = "base"
video_path = f"{config['FOLDER_PATH']}source.mp4"
output_video_path = f"{config['FOLDER_PATH']}result_transcribe_and_caption.mp4"
output_audio_path = f"{config['FOLDER_PATH']}audio.mp3"

# run the script
transcriber = VideoTranscriber(model_path, video_path)
transcriber.extract_audio(output_audio_path)
transcriber.transcribe_video()
if config['VIDEO_CREATION']:
    transcriber.create_video(output_video_path)