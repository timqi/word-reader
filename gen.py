import os
import argparse
from gtts import gTTS


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

def filter_word(line):
    line = line.strip()
    if not line:
        return None
    else:
        word = line.strip()
        for i, c in enumerate(word):
            if c == '#':
                return word[:i].strip() if i > 0 else None
        return word

def convert(word_list_file, voice_file):
    with open(os.path.join(word_list_path, word_list_file), 'r') as f:
        words = []
        for line in f:
            word = filter_word(line)
            if word:
                words.append(word)
        f.close()
        print_info("{} -> {}".format(os.path.basename(word_list_file), 
            os.path.basename(voice_file)))
        tts = gTTS(text='.   .   '.join(words), lang='en')
        tts.save(voice_file)
        print("Saved the words: {}".format(words))


def main():
    parser = argparse.ArgumentParser(description="Gen mp3 file from word_list")
    parser.add_argument('--update', nargs='+', dest='update',
            help='the number prefix like 001 002 .. of a force updated list')
    args = parser.parse_args()

    if args.update:
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
