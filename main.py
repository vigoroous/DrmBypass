import argparse
import os
from dotenv import load_dotenv
from catch_content import catch_content
from decrypt import decrypt
from download import download
from merge import merge

load_dotenv()


def cleanup(*paths):
    for path in paths:
        if os.path.isfile(path):
            os.remove(path)
            print(f"File {path} has been deleted")
        else:
            print(f"File {path} does not exist")


def pipeline(url: str, name: str):
    skip_decrypt = False
    (mpd_url, content_key_dict) = catch_content(url)

    if not content_key_dict:
        skip_decrypt = True

    content_path = download(mpd_url, name)

    if content_path is None:
        return (False, "Failed to get content path")

    video_file = [
        f"{content_path}.mp4",
        f"{content_path}_dec.mp4"
    ]
    audio_file = [
        f"{content_path}(Audio).aac",
        f"{content_path}(Audio)_dec.aac"
    ]

    if not skip_decrypt:
        if not decrypt(video_file[0], video_file[1], content_key_dict):
            return (False, "Content was not decrypted")
        cleanup(video_file[0])

        if not decrypt(audio_file[0], audio_file[1], content_key_dict):
            return (False, "Content was not decrypted")
        cleanup(audio_file[0])
    else:
        video_file[1] = f"{content_path}.mp4"
        audio_file[1] = f"{content_path}(Audio).aac"
        video_file[0] = f"{content_path}_merged.mp4"

    if not merge(video_file[1], audio_file[1], video_file[0]):
        return (False, "Failed to combine file fragments")
    cleanup(video_file[1], audio_file[1])
    return (True, "Pipeline finished")


def main():
    parser = argparse.ArgumentParser(
        description='Download and decrypt DRM protected mpeg-dash content')
    parser.add_argument('--url', type=str, help='url goes here')
    parser.add_argument('--name', type=str, help='filename')
    args = parser.parse_args()
    if args.url is not None:
        if args.name is not None:
            pipeline(args.url, args.name)
        else:
            pipeline(args.url, "default_name")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()