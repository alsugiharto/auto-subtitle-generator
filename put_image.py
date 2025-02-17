import numpy as np
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
import yaml
import math

def motion_crossing_leftup_rightdown(t):
    size_x = video_clip.size[0]
    size_y = video_clip.size[1]
    percentage = t/video_clip.duration
    return percentage * size_x, percentage * size_y

def motion_circleing_in_middle(t):
    center_x = video_clip.size[0] / 2 - image_clip.size[0]/2
    center_y = video_clip.size[1] / 2 - image_clip.size[1]/2
    radius = video_clip.size[1] * 0.2
    return center_x + radius * np.cos((t/video_clip.duration) * 2 * math.pi), center_y + radius * np.sin((t/video_clip.duration) * 2 * math.pi)


# load yaml
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
print('CONFIG')
print(config)

# constants
video_path = f"{config['FOLDER_PATH']}source.mp4"
image_path = f"{config['FOLDER_PATH']}download.jpeg"
output_video_path = f"{config['FOLDER_PATH']}result_put_image.mp4"

# get video
video_clip = VideoFileClip(video_path)
# get the image
image_clip = ImageClip(image_path).set_duration(video_clip.duration)
# set position of the image
image_clip = image_clip.set_position(motion_circleing_in_middle)
# combine the image and video
final_clip = CompositeVideoClip([video_clip, image_clip])
# generate video
final_clip.write_videofile(output_video_path, fps=video_clip.fps)