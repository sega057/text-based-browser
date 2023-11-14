from collections import deque
from bs4 import BeautifulSoup
from colorama import Fore
import argparse
import requests
import os
import re

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
URL_PREFIX = 'https://'
EXIT_COMMAND = 'exit'
BACK_COMMAND = 'back'
INVALID_URL_MESSAGE = 'Invalid URL'


def get_file_name(url: str):
    return re.sub(r'https?://', '', url).split('.')[0]


def has_page(file_name: str):
    return os.access(file_name, os.F_OK)


def show_visited_page(file_name: str):
    with open(file_name, 'r') as file:
        print(file.read())


def get_page_text(soup: BeautifulSoup):
    text = ''
    tags = soup.find_all(["p", "h1", "h2", "a", "ul", "ol", "li"])

    for tag in tags:
        if tag.name == 'a':
            tag_text = Fore.BLUE + tag.text.strip() + Fore.RESET + '\n'
        else:
            tag_text = tag.text.strip() + '\n'
        if tag_text:
            text += tag_text

    return text


def process_url(prompt: str, history: deque):
    url = prompt if prompt.startswith(URL_PREFIX) else URL_PREFIX + prompt

    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        print(INVALID_URL_MESSAGE)
        return

    if response.status_code != 200:
        print(INVALID_URL_MESSAGE)
        return

    soup = BeautifulSoup(response.content, "html.parser")
    page_text = get_page_text(soup)
    print(page_text)

    file_name = get_file_name(prompt)
    history.append(file_name)

    if not has_page(file_name):
        with open(file_name, 'w') as file:
            file.write(page_text)


def go_back(history: deque):
    if len(history) > 1:
        history.pop()  # Remove the current page from the history
        previous_page = history.pop()  # Get the previous page
        show_visited_page(previous_page)


def process_file_name(file_name: str, history: deque):
    if has_page(file_name):
        history.append(file_name)
        show_visited_page(file_name)
    else:
        print(INVALID_URL_MESSAGE)


def process_browser_commands(history: deque):
    prompt = input()

    if prompt == EXIT_COMMAND:
        exit()
    elif prompt == BACK_COMMAND:
        go_back(history)
    elif '.' in prompt:
        # If the input contains a dot, treat it as a URL
        process_url(prompt, history)
    else:
        # If the input doesn't contain a dot, treat it as a file name
        process_file_name(prompt, history)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_name')
    args = parser.parse_args()
    dir_name = args.dir_name

    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    os.chdir(dir_name)
    history = deque()

    while True:
        process_browser_commands(history)


if __name__ == '__main__':
    main()
