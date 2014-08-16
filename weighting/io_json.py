"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman-utils

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

JSON parser
"""

import json
import gzip

def loadJson(filepath):
    try:
        with gzip.open(filepath, 'rb') as fp:
            bytes = fp.read()
    except IOError:
        bytes = None

    if bytes:
        string = bytes.decode("utf-8")
        struct = json.loads(string)
    else:
        with open(filepath, "rU") as fp:
            struct = json.load(fp)

    return struct


def saveJson(struct, filepath, binary=False, maxDepth=1):
    global _maxDepth
    _maxDepth = maxDepth
    if binary:
        bytes = json.dumps(struct)
        with gzip.open(realpath, 'wb') as fp:
            fp.write(bytes)
    else:
        string = encodeJsonData(struct, 0, "")
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)
            fp.write("\n")


def encodeJsonData(data, depth, pad=""):
    global _maxDepth
    if data == None:
        return "none"
    elif isinstance(data, bool):
        if data == True:
            return "true"
        else:
            return "false"
    elif isinstance(data, float):
        if abs(data) < 1e-7:
            return "0"
        else:
            return "%g" % data
    elif isinstance(data, int):
        return str(data)
    elif isinstance(data, str):
        return "\"%s\"" % data
    elif isinstance(data, (list, tuple)):
        if data == []:
            return "[]"
        elif leafList(data) and depth >= _maxDepth:
            string = "["
            for elt in data:
                string += encodeJsonData(elt, depth+1) + ", "
            return string[:-2] + "]"
        else:
            string = "["
            for elt in data:
                string += "\n    " + pad + encodeJsonData(elt, depth+1, pad+"    ") + ","
            return string[:-1] + "\n%s]" % pad
    elif isinstance(data, dict):
        if data == {}:
            return "{}"
        string = "{"
        for key,value in data.items():
            if isinstance(key, int):
                pass
            else:
                key = '"%s"' % key
            string += "\n    %s%s : " % (pad, key) + encodeJsonData(value, 0, pad+"    ") + ","
        return string[:-1] + "\n%s}" % pad


def leafList(data):
    for elt in data:
        if isinstance(elt, (list,tuple)):
            leaf = leafList(elt)
            if not leaf:
                return False
        elif isinstance(elt, dict):
            return False
    return True
