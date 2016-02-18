'''
Drawille and curses xkcd reader
'''
import sys
import curses
import logging
from bs4 import BeautifulSoup
#from drawille import Canvas, getTerminalSize
import requests
from io import BytesIO
from PIL import Image

PAD_MOVE_X = 5
PAD_MOVE_Y = 5

def text_to_lines(hover_text, line_width):
    '''
    splits a string of words into individual lines
    '''
    hover_words = hover_text.split(' ')
    hover_lines = []
    line = ''
    for word in hover_words:
        if len(line) == 0:      #if the word is longer than the width it will do weird things
            line += word
        elif len(line) + len(word) + 1 <= line_width:
            line += ' '
            line += word
        else:
            hover_lines.append(line)
            line = ''
    return hover_lines

def calculate_screen_dims(screen_size, messages, lines):
    '''
    calculates and returns a tuple of the pad and the image width
    '''
    pad = [0, 0, 0, 0]          #top bottom left right
    img_dims = [0, 0]
    pad[2] = 5
    pad[3] = 5
    img_dims[1] = screen_size[1] - pad[2] - pad[3]
    pad[0] = 3 + len(messages)
    pad[1] = 2 + len(lines)
    img_dims[0] = screen_size[0] - pad[0] - pad[1]
    return pad, img_dims

def get_comic_data(comic_id, testing=False):
    '''
    gets the image, name, and hover text from xkcd.com for the number
    if testing is true it uses a saved comic (#1626)
    '''
    if testing:
        data = None
        with open('comicdata', 'r') as comicdata:
            data = comicdata.read().split('\n')
        title = 'Judgement Day'
        hover_text = ('It took a lot of booster rockets, but luckily Amazon had recently built '
                      'thousands of them to bring Amazon Prime '
                      'same-day delivery to the Moon colony.')
        return title, hover_text, data
    else:
        url = 'http://xkcd.com/{}/'.format(comic_id)
        soup = BeautifulSoup(requests.get(url).text, 'html.parser')

def parse_input(cmd, pad_offset, img_dims, data):
    '''
    handles all input
    '''

    message = None

    if cmd == 'KEY_DOWN':
        pad_offset[0] += PAD_MOVE_Y
        if pad_offset[0] + img_dims[0] >= len(data):
            message = 'Edge of image'
            pad_offset[0] = len(data) - img_dims[0]
            if pad_offset[0] < 0:
                pad_offset[0] = 0
    elif cmd == 'KEY_UP':
        pad_offset[0] -= PAD_MOVE_Y
        if pad_offset[0] <= 0:
            message = 'Edge of image'
            pad_offset[0] = 0
    elif cmd == 'KEY_RIGHT':
        pad_offset[1] += PAD_MOVE_X
        if pad_offset[1] + img_dims[1] >= len(data[0]):
            message = 'Edge of image'
            pad_offset[1] = len(data[0]) - img_dims[1]
            if pad_offset[1] < 0:
                pad_offset[1] = 0
    elif cmd == 'KEY_LEFT':
        pad_offset[1] -= PAD_MOVE_X
        if pad_offset[1] <= 0:
            message = 'Edge of image'
            pad_offset[1] = 0
    elif cmd == 'q':
        sys.exit(0)

    return pad_offset, message


def main(stdscr):
    '''
    Curses fuction
    '''

    logging.basicConfig(filename='v3xkcd.log', level=logging.DEBUG)
    logging.debug('starting program')

    title, hover_text, data = get_comic_data(1626, testing=True)

    pad_offset = [0, 0]
    messages = ['']

    pad, img_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, [''])
    lines = text_to_lines(hover_text, img_dims[1])
    while True:
        pad, img_dims = calculate_screen_dims(stdscr.getmaxyx(), messages, lines)
        #if message is longer than screen width it will probably do weird things, not tested yet
        stdscr.erase()
        for i in range(img_dims[0]):
            if i + pad_offset[0] < len(data):
                j = img_dims[1] if img_dims[1] < len(data[0]) else len(data[0])
                stdscr.addstr(i + pad[0], pad[2],
                              data[i+pad_offset[0]][pad_offset[1] : pad_offset[1]+j])
        stdscr.addstr(1, pad[2], 'Title: {}'.format(title))
        for i, message in iter(messages):
            stdscr.addstr(2 + i, pad[2], message)
        cmd = stdscr.getkey()
        messages = ['']

        pad_offset, message = parse_input(cmd, pad_offset, img_dims, data)
        if messages[0] == '':
            messages[0] = message
        else:
            messages.append(message)

if __name__ == '__main__':
    curses.wrapper(main)
