import gc

import cv2
import firebase_admin
import numpy as np
import requests
from PIL import Image
from firebase_admin import credentials
from googletrans import Translator
from moviepy.editor import *
from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.video.fx.all import fadein, fadeout

from Models.DescriptiveContent import DescriptiveContent
from consts import STORAGE_BUCKET
from text_to_voice import convert_to_speech_in_multiple_languages
from utils import upload_video_to_firebase, upload_audio_to_firebase


# Define a VideoClip subclass for gradual scaling effect


class GradualScaleClip(VideoClip):
    def __init__(self, img_clip, zoom_factor, duration, target_fps):
        self.img_clip = img_clip
        self.zoom_factor = zoom_factor
        VideoClip.__init__(self, duration=duration)
        self.target_fps = target_fps

    def make_frame(self, t):
        frame_time = t * self.img_clip.fps
        frame = self.img_clip.get_frame(frame_time)

        scale = 1 + (self.zoom_factor - 1) * t / self.duration
        new_width = int(self.img_clip.w * scale)
        new_height = int(self.img_clip.h * scale)
        frame = np.array(Image.fromarray(
            frame).resize((new_width, new_height)))
        return frame

    def size(self):
        return self.img_clip.size

    def close(self):
        self.img_clip.close()


def resize_image_with_aspect_ratio(image_path, target_width):
    # Open the image
    img = Image.open(image_path)

    # Calculate the new height to maintain aspect ratio
    original_width, original_height = img.size
    aspect_ratio = original_width / original_height
    target_height = int(target_width / aspect_ratio)

    # Resize the image while maintaining aspect ratio
    resized_img = img.resize((target_width, target_height))

    return resized_img


# Download and open images from URLs


def download_and_open_images(image_urls):
    image_files = []

    for url in image_urls:
        response = requests.get(url)
        if response.status_code == 200:
            # Save the image locally with .jpg extension
            image_filename = url.split('/')[-1]
            image_filename = os.path.splitext(image_filename)[0] + '.jpg'
            with open(image_filename, 'wb') as f:
                f.write(response.content)
            image_files.append(image_filename)

    return image_files


def download_and_open_image(image_url):
    image_filename = image_url.split('/')[-1]
    image_filename = os.path.splitext(image_filename)[0] + '.jpg'
    response = requests.get(image_url)
    if response.status_code == 200:
        # Save the image locally with .jpg extension
        with open(image_filename, 'wb') as f:
            f.write(response.content)
    return image_filename


# Create a function to apply blur effect to an image clip
def apply_blur(image_clip, blur_radius):
    def blur_frame(t):
        frame = image_clip.get_frame(t)
        blurred_frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
        return blurred_frame

    return VideoClip(make_frame=blur_frame, duration=image_clip.duration)


def createImageWithBlurBackground(image_path, video_width, video_height, duration_per_image, blur_radius=81):
    # Load the image using opencv-python
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize the image to fit the video resolution
    resized_image = cv2.resize(image, (video_width, video_height))

    # Convert the resized image to a MoviePy clip
    image_clip = ImageClip(resized_image, ismask=False,
                           duration=duration_per_image)

    # Apply blur effect to the image clip
    blurred_image_clip = apply_blur(image_clip, blur_radius)

    return blurred_image_clip


# Create a video using images urls, specifications, and car id


def GeneratePRVideo(pr: DescriptiveContent):
    # Define video parameters
    video_fps = 30
    # car_id = carDat["id"]
    image_files = download_and_open_images(pr.imageUrls)
    languages = ["en", "hi", "bn", "te", "mr", "ta", "ur", "gu", "ml", "kn"]
    convert_to_speech_in_multiple_languages(pr.prId, ". ".join(pr.descriptive_text), languages)
    translator = Translator()

    maxDuration = 0
    audio_urls = []
    for lan in languages:
        audio_path = f"{pr.prId}_output_{lan}.mp3"
        audio_urls.append({
            "language": lan,
            "url": upload_audio_to_firebase(audio_path)
        })
        audio_clip = AudioFileClip(audio_path)
        maxDuration = max(maxDuration, audio_clip.duration)
        audio_clip.close()
    ans = ""
    # for lan in languages:
    try:
        # audio_path = f"{pr.prId}_output_{lan}.mp3"
        # try:
        # Open the first image to get dimensions
        # image = Image.open(image_files[0])
        image_width, image_height = 1920, 1080
        # image.close()

        # Load background music
        # background_music = AudioFileClip(audio_path)
        # background_music = background_music.fx(vfx.speedx, 1.25)

        # Initialize lists for clips and settings
        clips = []

        duration_per_image = maxDuration / len(image_files)

        for i, image_file in enumerate(image_files):
            # create a clip from the image black.jpg with duration 2s

            background_clip = createImageWithBlurBackground(
                image_file, image_width, image_height, duration_per_image)

            fade_in_background_clip = fadein(background_clip, duration=1)
            fade_out_background_clip = fadeout(background_clip, duration=1)

            # background_clip = GradualScaleClip(
            #     background_clip, 1.1, duration_per_image, target_fps=video_fps)

            image_clip = VideoFileClip(image_file, audio=False)

            # Fitting the image to the video resolution
            image_clip_width = image_clip.size[0]
            image_clip_height = image_clip.size[1]

            scaling_factor = min(image_width / image_clip_width,
                                 image_height / image_clip_height)

            image_clip = image_clip.resize(
                (int(image_clip_width * scaling_factor), int(image_clip_height * scaling_factor)))

            # Apply zoom effect
            zoom_factor = 1.2
            scaled_clip = GradualScaleClip(
                image_clip, zoom_factor, duration_per_image, target_fps=video_fps).set_position(
                ("center", "center"))

            # Apply fade in and fade out effects
            fade_in_clip = fadein(scaled_clip, duration=1)
            fade_out_clip = fadeout(scaled_clip, duration=1)

            logo_clip = None
            # Placing logo on the top right corner
            #
            # if (carDat['dealerInfo']['dealerLogo'] is None or carDat['dealerInfo']['dealerLogo'] == "" or
            #         carDat['dealerInfo']['dealerLogo'] == defaultLogo):
            #     logo_clip = ImageClip(logo_path, ismask=False,
            #                           duration=duration_per_image)
            #     logo_clip = logo_clip.resize((220, 220))
            #     logo_clip = logo_clip.set_position(
            #         (image_width - logo_clip.size[0] + 10, -20))
            #
            # else:
            #     logo_path = download_and_open_image(
            #         carDat['dealerInfo']['dealerLogo'])
            #     logo_clip = ImageClip(np.array(resize_image_with_aspect_ratio(logo_path, 180)), ismask=False,
            #                           duration=duration_per_image)
            #     logo_clip = logo_clip.set_position(
            #         (image_width - logo_clip.size[0], 0))
            #
            # fade_in_logo_clip = fadein(logo_clip, duration=1)
            # fade_out_logo_clip = fadeout(logo_clip, duration=1)

            # Create text and color clips for each line in specification
            text_line = TextClip(translator.translate(pr.title, dest=lan).text.encode('utf-8'), font="Segoe-UI",
                                 fontsize=40,
                                 color='white',
                                 interline=10).set_duration(duration_per_image)

            im_width, im_height = text_line.size

            color_clip = ColorClip(size=(int(im_width * 1.05), int(im_height * 1.05)),
                                   color=(0, 0, 0)).set_duration(duration_per_image)
            color_clip = color_clip.set_opacity(0.25)
            text_line = text_line.set_position(
                ("center", 0.05), relative=True)
            color_clip = color_clip.set_position(
                ("center", 0.05), relative=True)
            # for j, line in enumerate(spec.split('\n')):
            #     if j == 0 or j == 1:
            #         text_line = TextClip(line, font='Segoe-UI', fontsize=40,
            #                              color='white',
            #                              interline=10).set_duration(duration_per_image)
            #     else:
            #         text_line = TextClip(line, font='Segoe-UI', fontsize=35,
            #                              color='white',
            #                              interline=10).set_duration(duration_per_image)
            #
            #     im_width, im_height = text_line.size
            #     title_width = im_width
            #
            #     color_clip = ColorClip(size=(int(im_width * 1.05), int(im_height * 1.05)),
            #                            color=(0, 0, 0)).set_duration(duration_per_image)
            #     color_clip = color_clip.set_opacity(0.25)
            #
            #     if len(spec.split('\n')) == 2:
            #         if j == 0:
            #             text_line = text_line.set_position(
            #                 ("center", 0.05), relative=True)
            #             color_clip = color_clip.set_position(
            #                 ("center", 0.05), relative=True)
            #         else:
            #             text_line = text_line.set_position(
            #                 ("center", 0.85), relative=True)
            #             color_clip = color_clip.set_position(
            #                 ("center", 0.85), relative=True)
            #     else:
            #         if j == 0:
            #             text_line = text_line.set_position(
            #                 ("center", 0.05), relative=True)
            #             color_clip = color_clip.set_position(
            #                 ("center", 0.05), relative=True)
            #         elif j == len(spec.split('\n')) - 1:
            #             text_line = text_line.set_position(
            #                 ("center", 0.2), relative=True)
            #             color_clip = color_clip.set_position(
            #                 ("center", 0.2), relative=True)
            #         else:
            #             text_line = text_line.set_position(
            #                 ("center", 0.85), relative=True)
            #             color_clip = color_clip.set_position(
            #                 ("center", 0.85), relative=True)
            #

            #
            #     prev_text_clip_height += (im_height + 20)

            # Create a composite clip with all effects
            combined_clip = CompositeVideoClip(
                [fade_in_background_clip, fade_out_background_clip, fade_in_clip, fade_out_clip,
                 # text_line, color_clip
                 ],
                use_bgclip=True)
            clips.append(combined_clip)

        video_width = image_width
        video_height = image_height
        #
        # # Load the image using opencv-python
        # image_path = brand_details_path
        #
        # background_image_clip = createImageWithBlurBackground(
        #     image_path, video_width, video_height, duration_per_image, 161)
        #
        # image_clip = ImageClip(image_path, ismask=False,
        #                        duration=duration_per_image).set_position(("center", "center"))
        #
        # # Making image_clip size fixed using scaling_factor
        # image_clip_width = image_clip.size[0]
        # image_clip_height = image_clip.size[1]
        #
        # scaling_factor = min(video_width / image_clip_width,
        #                      video_height / image_clip_height)
        #
        # image_clip = image_clip.resize(
        #     (int(image_clip_width * scaling_factor), int(image_clip_height * scaling_factor)))
        #
        # clips.append(CompositeVideoClip(
        #     [background_image_clip, image_clip], use_bgclip=True))

        # Concatenate all clips to create the final video
        final_clip = concatenate_videoclips(clips)

        # Trim background music to match final clip duration
        # background_music_duration = final_clip.duration
        # background_music = background_music.subclip(
        #     0, background_music_duration)

        # Set background music and resize the final video
        # final_clip = final_clip.set_audio(background_music)
        final_clip = final_clip.resize((video_width, video_height))

        video_path = f"{pr.prId}.mp4"

        # Write the final video file
        final_clip.write_videofile(
            video_path, codec="libx264", fps=video_fps)

        ans = upload_video_to_firebase(video_path)

        # Close video clips
        for combined_clip in clips:
            combined_clip.close()

        # Close final clip
        final_clip.close()

        # Close audio clips
        # background_music.close()

        # Explicitly trigger garbage collection
        gc.collect()

        # Upload video to Instagram and Youtube

        # Remove image files

        # except Exception as e:
        #     print("An error occurred:", e)
        #     # Handle exceptions appropriately
    except Exception as e:
        print(e)
        # continue

    for image_file in image_files:
        os.remove(image_file)
    for lang in languages:
        os.remove(f"{pr.prId}_output_{lang}.mp3")

    os.remove(f"{pr.prId}.mp4")
    return ans, audio_urls


if __name__ == "__main__":
    cred = credentials.Certificate('credentials.json')
    firebase_admin.initialize_app(cred, {'storageBucket': STORAGE_BUCKET})
    print(GeneratePRVideo(DescriptiveContent(1954753,
                                             "On the eve of Teachers’ Day, PM interacts with winners of National Teachers’ "
                                             "Award 2023",
                                             [
                                                 "The President addressed the officers of the Indian Corporate Law Service, "
                                                 "emphasizing the importance of their role in ensuring good corporate "
                                                 "governance and encouraging the development of industry and "
                                                 "entrepreneurship.",
                                                 "The President highlighted that their decisions have a significant impact "
                                                 "on the industrial and governance ecosystem of the country, and Corporate "
                                                 "Law Service officers should ensure that companies are managed in the best "
                                                 "interests of shareholders and other stakeholders.",
                                                 "The President urged the officers to uphold the principles of "
                                                 "transparency, fairness, and accountability, and to remember their "
                                                 "commitment to the well-being of the citizens of the country.",
                                                 "The President stressed the importance of efficient governance models and "
                                                 "an ethical culture for long-term sustainable growth and inclusive "
                                                 "development of the country."
                                             ]
                                             , [
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/JASOCX3p7J.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/8rleUMde04.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/f09y4YkYjX.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/UhOa215jIq.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/qlHdCZ91eC.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/SCpdEEocde.jpg",
                                                 "https://storage.googleapis.com/synth-ai-envoys.appspot.com/images"
                                                 "/VQ4Q9NWpH1.jpg"
                                             ], [
                                                 "corporate law service officers",
                                                 "corporate governance",
                                                 "industry development",
                                                 "entrepreneurship",
                                                 "stakeholders",
                                                 "transparency",
                                                 "fairness",
                                                 "accountability",
                                                 "sustainable growth",
                                                 "inclusive development"
                                             ], 1693765800000, "english", "")))
