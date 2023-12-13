from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx #for transition
import yaml

# load yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
print('CONFIG')
print(config)

# constants
video_path = f"{config['FOLDER_PATH']}source.mp4"
output_video_path = f"{config['FOLDER_PATH']}result_combine_video.mp4"

# get 3 clips with effects
clip_1 = VideoFileClip(video_path).subclip(0, 2).fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
clip_2 = VideoFileClip(video_path).subclip(2, 4).fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
clip_3 = VideoFileClip(video_path).subclip(4, 6).fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
# combine
combined = concatenate_videoclips([clip_1, clip_2, clip_3])
# generate video
combined.write_videofile(output_video_path)