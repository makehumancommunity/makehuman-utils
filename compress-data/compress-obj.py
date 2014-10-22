#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Convert ASCII .obj files to use minimal space.

Usage: compress-obj.py <obj_filename>
"""

import sys
from codecs import open

def main():
    if len(sys.argv) < 2:
        print "No filename specified"
        sys.exit(-1)

    obj_path = sys.argv[1]
    compress_obj(obj_path)


def compress_obj(obj_path):
    f = open(obj_path, 'rU', encoding="utf-8")

    out_buffer = []

    for line in f:
        line_data = line.split()

        # Format vertex coordinate
        if line_data[0] == 'v':
            out_buffer.append( 'v %.4f %.4f %.4f' % (float(line_data[1]), float(line_data[2]), float(line_data[3])) )

        # Format vertex texture (UV) coordinate
        elif line_data[0] == 'vt':
            out_buffer.append( 'vt %.6f %.6f' % (float(line_data[1]), float(line_data[2])) )

        # Format vertex normal
        elif line_data[0] == 'vn':
            out_buffer.append( 'vt %.4f %.4f %.4f' % (float(line_data[1]), float(line_data[2]), float(line_data[3])) )

        # Copy line without change
        else:
            out_buffer.append( line.rstrip('\n') )

    f.close()

    f = open(obj_path, 'w', encoding="utf-8")
    f.write( '\n'.join(out_buffer) )
    f.close()


if __name__ == '__main__':
    main()
