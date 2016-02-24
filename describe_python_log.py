#!/usr/bin/env python

# Copyright 2015, 2016 Jeff Trawick, http://emptyhammock.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# WHAT SHOULD BE DONE?
# 1. for nested exceptions, save multiple exceptions with some clear relationship

from __future__ import print_function

import argparse
import io
import json
import sys

from stacktraces.python.shortcuts import read_log

args = None
need_delim = False
seen = dict()


def print_process(process, traceback_lines):
    global args, need_delim

    if not args.include_duplicates:
        thread = process.threads[0]
        frame_functions = [frame.fn for frame in thread.frames]
        key = ','.join(frame_functions)
        if key in seen:
            return
        seen[key] = True

    if args.format == 'text':
        print(process)
        if args.include_raw:
            print(''.join(traceback_lines))
    else:
        if need_delim:
            print(',')
        if args.include_raw:
            to_serialize = {
                'wrapped': process.description(wrapped=True),
                'raw': ''.join(traceback_lines)
            }
        else:
            to_serialize = process.description(wrapped=True)
        print(json.dumps(to_serialize))
        need_delim = True


def main():
    global args

    parser = argparse.ArgumentParser()
    parser.add_argument('log_file_name',
                        help='name of log file to parse')
    parser.add_argument('--format', action='store', default='text',
                        help='output format ("json" or "text")')
    parser.add_argument('--include-duplicates', action='store_true',
                        help='whether to include duplicate stacktraces in output')
    parser.add_argument('--include-raw', action='store_true',
                        help='whether to include raw stacktraces in output')
    args = parser.parse_args()

    if args.format != 'text' and args.format != 'json':
        print('Wrong value for --format', file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        print('[')
    read_log(tracelvl=1, logfile=io.open(sys.argv[1], encoding='utf8'), handler=print_process)
    if args.format == 'json':
        print(']')

if __name__ == '__main__':
    main()
