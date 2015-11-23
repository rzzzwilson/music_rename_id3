#!/usr/bin/env python
# -*- coding= utf-8 -*-

"""
Modify all music file filenames.

Usage: music_rename_id3.py [-i|-h] <input_dir> <output_dir>

where the
    -h  print help and stop
    -i  assume files already converted and just edit ID3 tags
        (useful for fiddling with ID3 tags without converting/copying)

All files under <input_dir> are copied to the <output_dir> with the
filenames changed according to builtin rules.  The directory structure
under <input_dir> is assumed to be:
    GENRE/COMPOSER/TYPE/TYPE2/FILENAME
After renaming the ID3 tags are changed to something derived from the
directory structure.

All non-MP3 files are converted to MP3 format, ie:
    m4a, ogg, flac

This was in response to the Apple iTunes handling of my disparate music
collection which resulted in absolutely useless arranging of files.  Fiddle
with ID3 tags to try to get some sense out of iTunes which is probably the
WORST system for handling media I have seen (including the Windows and Linux
worlds, too!).
"""

import sys
import os
import re
import getopt
import shutil

import eyed3


# file extensions that can be handled and converted
ConvertExtensions = ['.mp4', '.m4a', '.ogg', '.flac']
HandledExtensions = ConvertExtensions + '.mp3'

# substutitions to be performed within directory/file names
SubstituteList = [
                  ('[^\x00-\x7F]+', ''),# remove non-ASCII chars
                  ('\([^\.]*\)', ''),   # delete '(...)'
                  ('\(.*\.', '.'),      # delete '(...' to next '.'
                  ('[\!\?\@\$]', ''),   # delete some punctuation
                  (';', ''),            # remove ';', os.system() doesn't like!
                  ('\&', 'And'),        # etc
                  (' - ', '-'),         # shorten/remove various strings
                  (' _ ', '_'),
                  ('- ', '-'),
                  ('_ ', '_'),
                  (' -', '-'),
                  (' _', '_'),
                  ("'", ''),
                  ('"', ''),
                  (',', ''),
                  (' ', ''),
                 ]


def usage(msg=None):
    """Print a helpful (?) usage with optional message.

    msg  the optional message
    """

    if msg:
        print('-'*80)
        print(msg)
        print('-'*80)
    print(__doc__)
    sys.exit(10)


def error(msg):
    """Handle an error situation."""

    print('')
    print(msg)
    print('')
    sys.exit(20)


def fix_name(name):
    """Remove spaces, etc, from a directory or file name."""

    for (pat, rep) in SubstituteList:
        name = re.sub(pat, rep, name)
    return name


def split_path(path):
    """Split a given path into a list of names."""

    result = []
    head = path
    while True:
        (head, tail) = os.path.split(head)
        if tail != "":
            result.append(tail)
        else:
            if head != "":
                result.append(head)

            break

    result.reverse()
    return result


def canonical_name(name):
    """Convert dir name to canonical form.

    This mostly means checking if the name is 'misc' which we ignore.

    Returns a unicode string.
    """

    return unicode(name if name != 'misc' else '')


def process_file(file_num, input_dir, output_dir, rel_path_list, dirpath, fname):
    """Handle one file.

    file_nmum      number of this file
    input_dir      base path of input directories
    output_dir     base path of output directories
    rel_path_list  list of directory names BELOW 'input_dir'
    dirpath        path down to the current dir
    fname          name of the file to process
    """

    output_rel_path_list = [fix_name(dir_name) for dir_name in rel_path_list]
    output_fname = fix_name(fname)

    # get full path to input file
    full_input_path = os.path.join(dirpath, fname)

    # get path tail starting at top-level dir
    (top_dir, base_dir) = os.path.split(input_dir)
    tail_path = full_input_path[len(top_dir)+1:]

    # compose output file path
    full_output_path = os.path.join(output_dir, tail_path)
    tmp = split_path(full_output_path)
    result = []
    for t in tmp:
        result.append(fix_name(t))
    full_output_path = result
    full_output_path = os.path.join(*full_output_path)

    # create output directories
    (full_output_dir, _) = os.path.split(full_output_path)
    cmd = 'mkdir -p %s' % full_output_dir
    if os.system(cmd) != 0:
        # error or maybe ^C
        sys.exit(10)

    # decide how to handle this file
    cmd = None
    (head, tail) = os.path.splitext(full_output_path)
    if tail in ConvertExtensions:
        # convert to MP3 in output directory
        full_output_path = head + '.mp3'

        if not os.path.isfile(full_output_path):
            # convert file to MP3
            cmd = ('ffmpeg -loglevel 8 -i "%s" -ab 128k %s'
                   % (full_input_path, full_output_path))

    elif tail == '.mp3':
        if not os.path.isfile(full_output_path):
            # MP#, copy file to output directory
            cmd = 'cp "%s" %s' % (full_input_path, full_output_path)
    else:
        # something else, abort
        error("Can't process unknown filetype: %s" % fname)

    # copy or convert the file IF REQUIRED.
    # if ID3OnlyFlag is True we only want to fiddle with ID3 tags and
    # we assume files have already been converted/copied.
    if not ID3OnlyFlag:
        if cmd:
            # print command so we see some progress
            print('%04d: %s' % (file_num, cmd))
            if os.system(cmd) != 0:
                # error or maybe ^C
                sys.exit(10)

    # create an ID3 title for the file
    paths = split_path(tail_path)
    while len(paths) < 5:
        paths.insert(0, paths[0])
    title = ''
    for x in range(4, 0, -1):
        if paths[-x] != 'misc':
            title = title + '-' + paths[-x]
    title = title[1:]       # remove leading '-'

    # now edit ID3 tags on output file
    try:
        audiofile = eyed3.load(full_output_path)
        if audiofile.tag:       # can a file NOT HAVE a tag?
            audiofile.tag.title = unicode(title)

            audiofile.tag.genre = canonical_name(paths[1])

            audiofile.tag.artist = canonical_name(paths[2])

            album = paths[3]
            if paths[4] != 'misc':
                album = paths[3] + '_' + paths[4]
            audiofile.tag.album = canonical_name(album)

            audiofile.tag.save()
    except Exception as e:
        print('full_output_path=%s' % full_output_path)
        raise


def main(argv):
    """Perform program operations.

    argv  the program arguments vector
    """

    global LenAbsInputDir, ID3OnlyFlag

    try:
        (opts, args) = getopt.getopt(argv, 'hi', ['help', 'id3'])
    except getopt.error:
        usage()

    ID3OnlyFlag = False
    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
        elif opt in ('-i', '--id3'):
            ID3OnlyFlag = True

    # get input and output directories
    if len(args) != 2:
        usage()
    input_dir = args[0]
    if not os.path.isdir(input_dir):
        error("Can't find input dir: %s" % input_dir)
    abs_input_dir = os.path.abspath(input_dir)
    LenAbsInputDir = len(split_path(abs_input_dir))

    output_dir = args[1]

    files = []
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        # if there are real files in 'filenames'
        for fname in filenames:
            if fname[0] != '.':
                (head, tail) = os.path.splitext(fname)
                if tail in HandledExtensions:
                    files.append((dirpath, fname))

    # process found files
    file_num = 0
    for (dirpath, fname) in files:
        rel_path_list = split_path(dirpath)[LenAbsInputDir:]
        rel_path = os.path.join(rel_path_list)
        if len(rel_path_list) != 4:
            error('dirpath %s is WRONG!  len(rel_path_list)=%d, expected 4'
                  % (dirpath, len(rel_path_list)))
        file_num += 1
        process_file(file_num,
                     input_dir, output_dir, rel_path_list, dirpath, fname)

    print('%d files processed.' % len(files))


if __name__ == '__main__':
    main(sys.argv[1:])
