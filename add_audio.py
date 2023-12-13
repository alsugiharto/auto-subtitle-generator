from moviepy.editor import AudioFileClip, VideoFileClip, CompositeAudioClip, afx
import yaml

# load yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
print('CONFIG')
print(config)

# constants
video_path = f"{config['FOLDER_PATH']}source.mp4"
audio_path = f"{config['FOLDER_PATH']}song.mp4"
output_video_path = f"{config['FOLDER_PATH']}result_audio_not_full.mp4"

# get video
clip_1 = VideoFileClip(video_path)
# get audio, lower volume
audio_source = AudioFileClip(audio_path).fx(afx.volumex, 0.1)
# combine audio song and audio original
clip_1.audio = CompositeAudioClip([audio_source, clip_1.audio])
# generate video
clip_1.write_videofile(output_video_path)