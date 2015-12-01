music_rename_id3
================

This repository contains some quick and dirty code to rename and fiddle with
the ID3 tags of a set of music files.

The music files can be .MP3, .OGG, .FLAC or .MP4 files.  All files that aren't
.MP3 files are converted to .MP3 (losing the video if any) and the file is
copied into an output directory structure similar to the input directory
structure.  The ID3 tags are then set.  There are dependencies such as ffmpeg
and the python eyed3 module.

This code grew out of dissatisfaction with the way iTunes handled my music
files.  They always seemed disjoint, with the 3 or 4 files consisting of a
classical symphony sorted in some bizarre way.  The code here goes a little
way to helping me with my problem.  Maybe it can help you too, but I'm sure
you'll have to hack on the code a bit.  Enjoy!

If you have a better approach, please let me know.

Usage
-----

The program is used so:

::

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

The **-i** option is useful once you have the file renaming part working
satisfactorily and you are fiddling with the ID3 tags.
