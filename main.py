#!/usr/bin/env python
# coding=utf-8
import os
import sys
import json
import requests
import argparse
from datetime import datetime
from collections import Counter

HISTORY_FILE = '/var/tmp/t/history.json'


file_dir = os.path.split(HISTORY_FILE)[0]
if not os.path.isdir(file_dir):
    os.makedirs(file_dir)

if not os.path.isfile(HISTORY_FILE):
    os.system('echo "{}" > %s' % HISTORY_FILE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='一个命令行的翻译工具')
    parser.add_argument('words', nargs='*', type=str, help='一个英文单词或语句')
    parser.add_argument('-t', nargs='?', type=int, default=0, help='top, 按词频查看单词')
    parser.add_argument('-l', nargs='?', type=int, default=0, help='list, 查看翻译过的单词')

    args = parser.parse_args()
    words = ' '.join(args.words)
    history = json.load(open(HISTORY_FILE, 'r'))
    if words:
        dictionary = history.get('dictionary', {})
        history_list = history.get('history', [])
        json.dump(history, open(HISTORY_FILE, 'w'))
        data = dictionary.get(words)
        if not data:
            response = requests.get(f'http://fanyi.youdao.com/openapi.do?keyfrom=HTransPlugin&key=260187501&type=data&doctype=json&version=1.1&q={words}')
            data = response.json()
            dictionary[words] = data
            history['dictionary'] = dictionary
        history_list.append({
            'words': words,
            'datetime': str(datetime.now())
        })
        history['history'] = history_list
        json.dump(history, open(HISTORY_FILE, 'w'))
        if 'translation' in data:
            print('翻译：')
            print('\n'.join(map(lambda s: '\t' + s, data['translation'])))
        if 'basic' in data:
            print('\n说明：')
            print('\n'.join(map(lambda s: '\t' + s, data['basic']['explains'])))
    elif args.t != 0:
        top_num = args.t or 20
        history_list = history.get('history', [])
        counter = Counter([i.get('words') for i in history_list])
        for i, item in enumerate(counter.most_common(top_num)):
            print(f'\ttop{i + 1}:{item[0]}\t{item[1]}次')
    elif args.l != 0:
        list_len = args.l or 20
        history_list = history.get('history', [])[::-1][:list_len]
        for item in history_list:
            print('\t', item.get("words"))

    else:
        print('请输入一个单词，或者一个短语')
