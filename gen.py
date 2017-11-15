import os
import math
import eyed3
import argparse
from gtts import gTTS
from functools import reduce


basepath = os.path.abspath(os.path.dirname(__file__))
word_list_path = os.path.join(basepath, 'word_list')
outputs_path = os.path.join(basepath, 'outputs')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_info(text):
    print(bcolors.OKGREEN + text + bcolors.ENDC)

def print_warning(text):
    print(bcolors.WARNING + text + bcolors.ENDC)

class Entry:
    def __init__(self, word, lyric):
        self.word = word
        self.lyric = lyric

def filter_line(line):
    word = lyric = None
    striped_line = line.strip()
    if striped_line:
        lyric = striped_line.replace('#', '')
        for i, c in enumerate(striped_line):
            if c == '#':
                word = striped_line[:i].strip() if i > 0 else None
                break
        if i == len(striped_line)-1 and not word:
            word = striped_line
        return Entry(word, lyric)
    else:
        return None


def convert(word_list_file, voice_file):
    with open(os.path.join(word_list_path, word_list_file), 'r') as f:
        entries = []
        for line in f:
            entry = filter_line(line)
            if entry:
                entries.append(entry)
        f.close()
        words = list(map(lambda e:e.word, filter(lambda e:e.word, entries)))

        print_info("{} -> {}".format(os.path.basename(word_list_file), 
            os.path.basename(voice_file)))
        tts = gTTS(text='.   '.join(words), lang='en')
        tts.save(voice_file)
        print("Saved the words: {}".format(words))

        audiofile = eyed3.load(voice_file)
        audiofile.initTag()
        audiofile.tag.artist = "Tim"
        audiofile.tag.album = "Vocabulary"
        audiofile.tag.album_artist = "Tim"
        audiofile.tag.title = os.path.splitext(os.path.basename(word_list_file))[0]
        audiofile.tag.save()
        print("Assign tag to:{}".format(voice_file))

        audio_time_secs = audiofile.info.time_secs
        char_count = reduce(lambda x,y: x+y, map(lambda word:len(word), filter(lambda w:w, words)))
        time_secs_per_chat = audio_time_secs / char_count
        with open(os.path.splitext(voice_file)[0]+".lrc", 'w+') as flrc:
            flrc.write("[ti:{}]\n".format(os.path.splitext(os.path.basename(word_list_file))[0]))
            flrc.write("[ar:Tim]\n")
            flrc.write("[au:Tim]\n")
            flrc.write("[al:Vocabulary]\n")
            flrc.write("[by:Tim]\n\n")

            char_computed = 0
            for entry in entries:
                time = char_computed * time_secs_per_chat
                minute = sec = persec = 0
                if time > 60:
                    minute = int(time // 60)
                sec = int(time % 60)
                persec = int(math.modf(time)[0] * 100)
                flrc.write("[{:02d}:{:02d}.{:02d}]{}\n"
                        .format(minute, sec, persec, entry.lyric))
                if entry.word:
                    char_computed = char_computed + len(entry.word)
            flrc.close()
            print("Write lyrics")



def main():
    parser = argparse.ArgumentParser(description="Gen mp3 file from word_list")
    parser.add_argument('--update', nargs='+', dest='update',
            help='the number prefix like 001 002 .. of a force updated list')
    args = parser.parse_args()

    if args.update:
        if args.update[0] == 'all':
            for word_list_file in os.listdir(word_list_path):
                voice_file = os.path.join(outputs_path, os.path.splitext(word_list_file)[0]+'.mp3')
                convert(word_list_file, voice_file)
        else:
            for word_list_file in os.listdir(word_list_path):
                number = word_list_file.split('-')[0]
                if number in args.update:
                    voice_file = os.path.join(outputs_path,
                            os.path.splitext(word_list_file)[0]+'.mp3')
                    convert(word_list_file, voice_file)
        return

    for word_list_file in os.listdir(word_list_path):
        voice_file = os.path.join(outputs_path, os.path.splitext(word_list_file)[0]+'.mp3')
        if os.path.isfile(voice_file):
            print_warning("Ignored, already exists: {}".format(voice_file))
        else:
            convert(word_list_file, voice_file)


if __name__ == '__main__':
    main()
