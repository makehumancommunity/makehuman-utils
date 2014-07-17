"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         GPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
Project to proxy

"""

import bpy
import os
from collections import OrderedDict
from . import io_json
from maketarget.utils import round


SplitInfo = {
    "brow_mid_up"           : "LR",
    "brow_mid_down"         : "LR",
    "brow_outer_up"         : "LR",
    "brow_outer_down"       : "LR",
    "brow_squeeze"          : "Sym",

    "cheek_narrow"          : "LR",
    "cheek_balloon"         : "LR",
    "cheek_up"              : "LR",
    "cheek_squint"          : "LR",

    "lips_mid_upper_up"     : "LR",
    "lips_mid_lower_up"     : "LR",
    "lips_mid_upper_down"   : "LR",
    "lips_mid_lower_down"   : "LR",
    "lips_upper_in"         : "Sym",
    "lips_lower_in"         : "Sym",
    "lips_upper_out"        : "Sym",
    "lips_lower_out"        : "Sym",
    "lips_part"             : "Sym",

    "mouth_corner_in"       : "LR",
    "mouth_corner_out"      : "LR",
    "mouth_corner_up"       : "LR",
    "mouth_corner_down"     : "LR",
    "mouth_up"              : "LR",
    "mouth_down"            : "LR",
    "mouth_narrow"          : "LR",
    "mouth_open"            : "Sym",
    "mouth_wide"            : "LR",

    "nose_wrinkle"          : "Sym",

    "tongue_back_up"        : "Sym",
    "tongue_out"            : "Sym",
    "tongue_up"             : "Sym",
    "tongue_wide"           : "Sym",
}

Scales = {
    "base" : {
        "x" : (5399, 11998, 1.4800),
        "y" : (791, 881, 2.3298),
        "z" : (962, 5320, 1.9221),
    },
}

def generateLRFiles(folder):
    lrFile = os.path.join(os.path.dirname(__file__), "data/vgrp_leftright.json")
    lrVgroups = io_json.loadJson(lrFile)
    left = {}
    right = {}
    for n in range(19000):
        left[n] = 0.0
        right[n] = 0.0
    for n,w in lrVgroups["Left"]:
        left[n] = w
    for n,w in lrVgroups["Right"]:
        right[n] = w

    raw = os.path.join(folder, "plugins/9_export_xmhx/data/faceshapes/raw/")
    struct = OrderedDict()
    struct["scale"] = Scales["base"]
    targets = struct["targets"] = OrderedDict()

    for file in os.listdir(raw):
        fname,ext = os.path.splitext(file)
        if ext == ".target":
            filepath = os.path.join(raw, file)
            if SplitInfo[fname] == "Sym":
                targets[fname] = readCoords(filepath)
            else:
                targets[fname+"_left"] = readCoords(filepath, left)
                targets[fname+"_right"] = readCoords(filepath, right)

    filepath = os.path.join(folder, "plugins/9_export_xmhx/data/faceshapes/faceshapes.json")
    io_json.saveJson(struct, filepath, maxDepth=0)


def readCoords(filepath, vgroup=None):
    coord = []
    fp = open(filepath, "rU")
    eps = 1e-5
    for line in fp:
        words = line.split()
        if len(words) == 0 or words[0][0] == "#":
            pass
        else:
            n,x,y,z = int(words[0]), float(words[1]), float(words[2]), float(words[3])
            if vgroup:
                k = vgroup[n]
            else:
                k = 1.0
            x,y,z = k*x,k*y,k*z
            if not (abs(x) < eps and abs(y) < eps and abs(z) < eps):
                coord.append((n, (x,y,z)))
    fp.close()
    return coord


class VIEW3D_OT_GenereateLRFilesButton(bpy.types.Operator):
    bl_idname = "mhw.generate_lr_files"
    bl_label = "Generate LR Files"

    def execute(self, context):
        generateLRFiles("/home/hg/mhx_system/")
        return{'FINISHED'}
