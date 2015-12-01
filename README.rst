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
