import os
from pathlib import Path

from moviepy.editor import VideoFileClip

from app.api.dto.reddit_dto import Comment
from app.core.config import settings
from app.utils.comment_audio_generator import generate_comments_with_duration
from app.utils.reddit_comment_overlay import add_comments_to_video, write_videofile
from app.utils.trim_video import trim_video_to_fit_comments


def convert_dict_comments_to_objects(comment_dicts):
    """Convert a list of comment dictionaries to Comment objects"""
    return [Comment(**comment_dict) for comment_dict in comment_dicts]


def get_first_video_in_directory(directory="./assets/video_templates"):
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        return None

    # List all files and filter for common video extensions
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = [f for f in os.listdir(directory)
                   if os.path.isfile(os.path.join(directory, f)) and
                   os.path.splitext(f)[1].lower() in video_extensions]

    if not video_files:
        print(f"No video files found in {directory}")
        return None

    # Return the first video file found
    return os.path.join(directory, video_files[0])


# In the generate_comments function
def generate_comments():
    # Define comments to overlay on the video
    comment_dicts = [
        {
            "username": "i_am_a_toaster",
            "text": "I asked once for craigslist missed connections stories. I still want to know if there ARE any.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "MrP8978",
            "text": "I’m thinking of trying out to be a prison guard, so asked Resddit what a day in the life is really like. Nobody answered.\n\n\nLooked for an ELI5 on hayfever, got thousands of responses. ",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "untilthestarsfall",
            "text": "I wanted to know the answer to \"People who work door-to-door, what weird things have you witnessed in people's homes?\"",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "TheVillainInGlasses",
            "text": "People who have heckled professional comedians, why did you do it and what happened? ",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "Haephestus",
            "text": "I asked once: \"What is something you respect about a religion or ideology that you disagree with?\" \n\nAll I got were passive-aggressive responses like \"I guess I appreciate that kind of moronic innocence...\"",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "[deleted]",
            "text": "I posted one on an old account that was something like\n\n\n\nWhat happened at your job to make you think 'I don't get paid enough for this'?\n\nI have that thought all the time so I was hoping to read about other people's crappy jobs to make myself feel better.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "[deleted]",
            "text": "I asked \"What is the best photo you have, or have taken?\" (something along those lines). I think the very best post on this site was the one where people had pics of things that would sound unbelievable if they didn't have them.\n\nEdit: Don't mean objectively the best, but just your favourite out of all your photos",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "just_redd_it",
            "text": "Asked \"what red flags turned out to be false alarm\". Didn't get any answer and lost an argument",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "Praktykal",
            "text": "I asked “lawyers of reddit, who were some of your clients that you know should have gotten a harsher sentence?”, I thought it was a great question and was gonna hit the front page. Guess not, because only one person responded with the answer “I am not a lawyer”. Thanks for your contribution buddy.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "30NiceGuy03",
            "text": "This is like multiple askreddit tread on an askreddit tread, we must go deeper.\n\nEDIT: forgot the h in thread",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "ThreeSheetzToTheWind",
            "text": "I posted something along the lines of,\n\n>What is one small way your job makes people's lives better?\n\nI was genuinely feeling bad about myself and my job that day and wanted to hear what people had to say.\n\nI had just one response that was really beautiful from a landscaper who said it was \"nice to see how happy all the color makes homes and businesses look.\"  I would have loved to see more because that is some genuinely heartwarming shit, right there.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "QuintaGouldsmith",
            "text": "What was the most romantic thing anyone has ever said to you? I wanted to hear from people with differing opinions about romantic things. My ideas are vastly different than the advertised stuff - except flowers I love flowers. I don’t wear jewelry. So I just wondered what others thought about romancing with words. ",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "SpareAnimalParts",
            "text": "\"What experience or lesson defines your attitude towards death, whether it's your own or someone else's?\"\n\nNo responses.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "tinyahjumma",
            "text": "Parents/Aunt/Uncles: what do you admire about the child(ren) in your life?\n\nEdit: all these answers are warming my heart.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "essentiallycallista",
            "text": "Thank you for asking, a lot of people feel like no one wants to listen. Now people are having the conversations they really wanted.",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "Cw2e",
            "text": "What’s a song you enjoy from a band you usually hate? ",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "noodle-face",
            "text": "I asked about people pooping their pants in public \\- how did it happen? what lead up to the poopcident?",
            "avatar": "/avatar_default_0.png"
        },
        {
            "username": "TimTheGamer555",
            "text": ">If you could replace any fictional character with yourself, what character would you replace and why?\n\nI only got four responses and I was looking forward to hearing lots of funny answers, like Godzilla being replaced by some guy named Dave or something.",
            "avatar": "/avatar_default_0.png"
        }
    ]
    comment_objects = [Comment(**comment) for comment in comment_dicts]

    target_duration = 60.0  # Target duration in seconds
    processed_comments, duration = generate_comments_with_duration(comment_objects, target_duration,
                                                                   allow_exceed_duration=True)

    return processed_comments


if __name__ == '__main__':
    settings.CACHE_DIR = Path("/tmp/post2video")
    OUTPUT_DIR = "generated/output"
    # Path to your input video
    INPUT_VIDEO = 'assets/video_templates/x.mp4'
    OUTPUT_VIDEO = OUTPUT_DIR

    if not INPUT_VIDEO:
        print("No input video found. Please ensure there are videos in the output directory.")
        exit(1)

    # Create the overlay processor
    video = VideoFileClip(INPUT_VIDEO)
    comments = generate_comments()
    video = add_comments_to_video(video, comments)
    video = trim_video_to_fit_comments(video, comments)
    output_path = write_videofile(video, OUTPUT_VIDEO)
    print(f"Video successfully created at: {output_path}")

    # Clean up resources
    video.close()
