# pindown - Convert bookmarks from a pinboard export file to individual markdown files
# Copyright (C) 2020 Robert van Bregt (https://www.robertvanbregt.nl/)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import json
import os
import string

from dateutil.parser import parse

VALID_FILENAME_CHARS = "-_.() %s%s" % (string.ascii_letters, string.digits)
FILE_EXTENSION = "md"

def get_bookmarks(input_filename):
    with open(input_filename, "r") as input_filename:
        return json.load(input_filename)

def add_tag(tags, extra_tags):
    if len(extra_tags) > 0:
        tags = tags + " " + extra_tags
    return tags

def prepend_tags(tags, prepend):
    if len(prepend) > 0:
        tags = (" " + prepend).join( tags.split() )
        if len(tags) > 0:
            tags = prepend + tags
    return (tags)

def format_bookmark(bookmark):
    trans = "".maketrans('','','[]()')
    time = parse(bookmark["time"])
    return(f"{bookmark['description'].translate(trans).strip()}  \n"
           f"{bookmark['href'].translate(trans)}  \n"
           f"{time.date()}  \n"
           f"{prepend_tags(bookmark['tags'], args.prepend_tags)}  \n\n"
           f"{bookmark['extended']}")

def create_path(output_path):
    try:
        os.makedirs(output_path)
    except FileExistsError:
        pass

def sanitize_filename(text):
    return "".join(c for c in text if c in VALID_FILENAME_CHARS).strip().strip('.')

def write_file(bookmark, output_path):
    date = parse(bookmark["time"]).strftime("%Y-%m-%d")
    output_path = os.path.expanduser(output_path)
    sanitized = sanitize_filename(bookmark["description"])
    if len(f"{date} {sanitized}.{FILE_EXTENSION}") > 255:
        sanitized = sanitized[:255-len(FILE_EXTENSION)-len(""+date)-2]
    output_file = f"{output_path}/{date} {sanitized}.{FILE_EXTENSION}"

    create_path(output_path)
    with open(output_file, "w") as output_file:
        formatted = format_bookmark(bookmark)
        output_file.write(formatted)

def main():
    parser = argparse.ArgumentParser(description='Convert pinboard bookmarks to markdown.')
    parser.add_argument('-i', '--input-file', type=argparse.FileType('r'), required=True, help='input file')
    parser.add_argument('-p', '--output-path', default='./pinboard', help='output path')
    parser.add_argument('--extra-tags', default='', help='space separated list of extra tags')
    parser.add_argument('--prepend-tags', default='', help='character to prepend each tag with')
    global args
    args = parser.parse_args()

    bookmarks = get_bookmarks( args.input_file.name )
    if len(bookmarks) == 0:
        print("No bookmarks in file {args.input_file.name}")
        return
    for bookmark in bookmarks:
        bookmark['tags'] = add_tag(bookmark['tags'], args.extra_tags)
        write_file(bookmark, args.output_path)
