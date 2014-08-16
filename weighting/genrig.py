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

Rig

"""

import bpy
from mathutils import *
from bpy_extras.io_utils import ExportHelper
from bpy.props import *
import os
from collections import OrderedDict
from . import io_json


#------------------------------------------------------------------------
#    Buttons
#------------------------------------------------------------------------

class VIEW3D_OT_SaveRigButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhw.save_rig"
    bl_label = "Save rig"
    bl_description = "Save rig file"

    filename_ext = ".py"
    filter_glob = StringProperty(default="*.py", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        saveRig(context, self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SaveVertexGroupsButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhw.save_vertex_groups"
    bl_label = "Save vertex groups"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        from .export import exportVertexGroups

        rig = context.object
        human = None
        nverts = 0
        for ob in rig.children:
            if ob.type == 'MESH' and len(ob.data.vertices) > nverts:
                human = ob
                nverts = len(ob.data.vertices)

        exportVertexGroups(context.scene, human, self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SaveActionButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhw.save_action"
    bl_label = "Save Action"
    bl_description = "Save action file"

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        saveAction(context, self.filepath)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_FixJsonListButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhw.fix_json_list"
    bl_label = "Fix JSON List"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", maxlen=1024, default="")

    def execute(self, context):
        jlist = io_json.loadJson(self.filepath)
        string = "".join([('  ["%s", %s],\n' % tuple(elt)) for elt in jlist])
        fp = open(self.filepath, "w")
        fp.write(
            "[\n" +
            string[:-2] +
            "\n]\n")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------------
#    Actions
#------------------------------------------------------------------------

FaceShiftNames = {
    "Neutral" : "00_neutral",
    "LeftBrowDown" : "01_BrowsD_L",
    "RightBrowDown" : "02_BrowsD_R",
    "BrowsUp" : "03_BrowsU_C",
    "LeftBrowUp" : "04_BrowsU_L",
    "RightBrowUp" : "05_BrowsU_R",
    "LeftCheekUp" : "06_CheekSquint_L",
    "RightCheekUp" : "07_CheekSquint_R",
    "ChinUp" : "08_ChinLowerRaise",
    "UpperLipUp3" : "09_ChinUpperRaise",
    "LeftEyeClose" : "10_EyeBlink_L",
    "RightEyeClose" : "11_EyeBlink_R",
    "LeftEyeDown" : "12_EyeDown_L",
    "RightEyeDown" : "13_EyeDown_R",
    "LeftEyeIn" : "14_EyeIn_L",
    "RightEyeIn" : "15_EyeIn_R",
    "LeftEyeOpen" : "16_EyeOpen_L",
    "RightEyeOpen" : "17_EyeOpen_R",
    "LeftEyeOut" : "18_EyeOout_L",
    "RightEyeOut" : "19_EyeOut_R",
    "LeftEyeLowerUp" : "20_EyeSquint_L",
    "RightEyeLowerUp" : "21_EyeSquint_R",
    "LeftEyeUp" : "22_EyeUp_L",
    "RightEyeUp" : "23_EyeUp_R",
    "JawClosedOffset" : "24_JawChew",
    "JawMoveForward" : "25_JawFwd",
    "JawMoveLeft" : "26_JawLeft",
    "JawMoveRight" : "28_JawRight",
    "JawOpen" : "27_JawOpen",
    "LipsOpenKiss" : "29_LipsFunnel",
    "LowerLipsUp" : "30_LipsLowerClose",
    "LowerLipsDown" : "31_LipsLowerDown",
    "LowerLipsDown2" : "32_LipsLowerOpen",
    "LipsKiss" : "33_LipsPucker",
    "MouthLeftSmile" : "34_LipsStretch_L",
    "MouthRightSmile" : "35_LipsStretch_R",
    "UpperLipDown" : "36_LipsUpperClose",
    "UpperLipUp" : "37_LipsUpperOpen",
    "UpperLipUp2" : "38_LipsUpperUp",
    "MouthLeftSmile2" : "39_MouthDimple_L",
    "MouthRightSmile2" : "40_MouthDimple_R",
    "MouthLeftFrown" : "41_MouthFrown_L",
    "MouthRightFrown" : "42_MouthFrown_R",
    "MouthMoveLeft" : "43_MouthLeft",
    "MouthMoveRight" : "44_MouthRight",
    "MouthLeftSmile3" : "45_MouthSmile_L",
    "MouthRightSmile3" : "46_MouthSmile_R",
    "CheeksPump" : "47_Puff",
    "FaceTension" : "48_Sneer",
}

FacePoses = [
    "LeftBrowDown",
    "RightBrowDown",
    "BrowsUp",
    "LeftBrowUp",
    "RightBrowUp",
    "LeftCheekUp",
    "RightCheekUp",
    "ChinUp",
    "UpperLipUp3",
    "LeftEyeClose",
    "RightEyeClose",
    "LeftEyeDown",
    "RightEyeDown",
    "LeftEyeIn",
    "RightEyeIn",
    "LeftEyeOpen",
    "RightEyeOpen",
    "LeftEyeOut",
    "RightEyeOut",
    "LeftEyeLowerUp",
    "RightEyeLowerUp",
    "LeftEyeUp",
    "RightEyeUp",
    "JawClosedOffset",
    "JawMoveForward",
    "JawMoveLeft",
    "JawOpen",
    "JawMoveRight",
    "LipsOpenKiss",
    "LowerLipsUp",
    "LowerLipsDown",
    "LowerLipsDown2",
    "LipsKiss",
    "MouthLeftSmile",
    "MouthRightSmile",
    "UpperLipDown",
    "UpperLipUp",
    "UpperLipUp2",
    "MouthLeftSmile2",
    "MouthRightSmile2",
    "MouthLeftFrown",
    "MouthRightFrown",
    "MouthMoveLeft",
    "MouthMoveRight",
    "MouthLeftSmile3",
    "MouthRightSmile3",
    "CheeksPump",
    "FaceTension",
]

BodyPoses = [
    "UpperArmUpLeft1",
    "UpperArmUpLeft2",
    "UpperArmForwardLeft",
    "UpperArmBackwardLeft",
    "UpperArmDownLeft",
    "UpperArmRollOutLeft",
    "UpperArmRollInLeft",
    "LowerArmBend1Left1",
    "LowerArmBend1Left2",
    "HandRollBackwardLeft",
    "HandRollForwardLeft",
    "HandBendInLeft",
    "HandBendOutLeft",
    "HandBendUpLeft",
    "HandDownLeft",
    "HeadTurnRight",
    "HeadTurnLeft",
    "HeadUp",
    "HeadDown",
    "HeadLeft",
    "HeadRight",
    "TorsoDown",
    "TorsoUp",
    "TorsoLeft",
    "TorsoRight",
    "UpperLegDownLeft",
    "UpperLegUpLeft",
    "UpperLegForwardLeft",
    "UpperLegBackwardLeft",
    "UpperLegRollOutLeft",
    "UpperLegRollInLeft",
    "LowerLegBendLeft1",
    "LowerLegBendLeft2",
    "FootTurnOutLeft",
    "FootTurnInLeft",
    "FootRollInLeft",
    "FootRollOutLeft",
    "FootDownLeft",
    "FootUpLeft",
    "Finger1CloseLeft",
    "Finger2CloseLeft",
    "Finger3CloseLeft",
    "Finger4CloseLeft",
    "Finger5CloseLeft",
    "Finger1OpenLeft",
    "Finger2OpenLeft",
    "Finger3OpenLeft",
    "Finger4OpenLeft",
    "Finger5OpenLeft",
    "Figer1RollInLeft",
    "Figer1RollOutLeft",
    "Toe1CloseLeft",
    "Toe2CloseLeft",
    "Toe3CloseLeft",
    "Toe4CloseLeft",
    "Toe5CloseLeft",
    "Toe6OpenLeft",
    "Toe7OpenLeft",
    "Toe8OpenLeft",
    "Toe9OpenLeft",
    "Toe1OpenLeft",
]

def saveAction(context, filepath):
    rig = context.object

    name = "Face"
    if name == "Face":
        poses = ["Neutral"] + FacePoses
        begin = 0
        end = 48
    elif name == "All":
        poses = ["Neutral"] + FacePoses + BodyPoses
        begin = 1
        end = 199

    fcurves = {}
    affected = {}
    times = {begin:True}

    act = rig.animation_data.action
    afcurves = []
    for fcu in act.fcurves:
        try:
            bname = fcu.data_path.split('"')[1]
        except IndexError:
            print ("Datapath '%s'" % fcu.data_path)
            continue
        if bname in ["neck", "neck2"]:
            continue
        try:
            rig.data.bones[bname]
        except KeyError:
            print("Bone %s not found" % bname)
            continue
        fcurves[bname] = {}
        affected[bname] = {}
        afcurves.append(fcu)

    print("Range", begin, end)

    for fcu in afcurves:
        bname = fcu.data_path.split('"')[1]
        values = fcurves[bname][fcu.array_index] = []
        for t in range(begin,end+1):
            y = fcu.evaluate(t)
            if fcu.array_index > 0 and abs(y) > 1e-7:
                affected[bname][t] = True
                times[t] = True
            values.append(y)

    times = list(times.keys())
    times.sort()

    struct = OrderedDict()
    struct["name"] = name
    poseTable = struct["poses"] = OrderedDict()

    for n,pname in enumerate(poses):
        t = times[n]
        quats = poseTable[pname] = {}
        for bname,aff in affected.items():
            if aff:
                fcus = fcurves[bname]
                if t in aff.keys():
                    try:
                        quat = [fcus[idx][t] for idx in range(4)]
                        quats[bname] = quat
                    except IndexError:
                        print(bname, aff, t)
                        halt

    io_json.saveJson(struct, filepath, maxDepth=0)


#------------------------------------------------------------------------
#    Rig
#------------------------------------------------------------------------

def saveRig(context, filepath):
    rig = context.object
    ob = rig.children[0]
    scn = context.scene
    fp = open(filepath, "w")

    fp.write(
'''#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni, Thomas Larsson

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

The official MakeHuman rig
"""

from .flags import *

''')

    bpy.ops.object.mode_set(mode='OBJECT')
    hjoints,tjoints,ignores,connects = writeJoints(fp, rig, ob, scn)
    writeHeadsTails(fp, rig, hjoints, tjoints, connects)
    hier = makeHierarchy(rig)
    writeArmature(fp, hier, rig, [])
    bpy.ops.object.mode_set(mode='POSE')

    fp.write(
'''
Planes = {}
Constraints = {}
LocationLimits = {}
RotationLimits = {}
CustomShapes = {}
''')

    fp.close()
    print('Rig saved to "%s"' % filepath)

    if ignores:
        print("Check the following bones manually")
        for bname in ignores:
            print("  %s" % bname)


def makeHierarchy(rig):
    roots = []
    for b in rig.data.bones:
        if b.parent is None:
            roots.append(b)

    hier = []
    for root in roots:
       hier.append((root, makeChildren(root)))
    return (None, hier)


def makeChildren(parent):
    hier = []
    for bone in parent.children:
        hier.append((bone, makeChildren(bone)))
    return hier


ManualHeads = {
    'root' : ('o', ('pelvis', (0,0,-1))),
    'special02' : ('vl', ((0.5, 5577), (0.5,12174))),
}

ManualTails = {
    'foot.L' : ('vl', ((0.5, 16839), (0.5,16851))),
    'foot.R' : ('vl', ((0.5, 15535), (0.5,15547))),
    'special01' : ('vl', ((0.5, 317), (0.5,343))),
    #'special04' : ('vl', ((0.5, 5213), (0.5,11823))),
    #'oris05' : ('vl', ((0.75, 466), (0.25,467))),
}

def writeJoints(fp, rig, ob, scn):
    fp.write("\nJoints = [\n")

    #verts = []
    #for v in ob.data.vertices:
    #    if findJoint(v, rig):
    #        verts.append(v)

    scn.objects.active = ob
    joints = defineJoints(ob)

    for j in joints:
        fp.write("  ('%s', 'j', '%s'),\n" % (j,j))
    fp.write('\n')

    scn.objects.active = rig
    bpy.ops.object.mode_set(mode='EDIT')
    ignores = []
    dolast = []
    connects = {}
    hjoints = {}
    tjoints = {}
    for eb in rig.data.edit_bones:
        bname = getBoneName(eb)
        if (eb.parent and
            (eb.use_connect or distance(eb.head, eb.parent.tail) < 1e-3)):
            pname = getBoneName(eb.parent)
            hjoints[bname] = getTailLoc(pname, tjoints)
            connects[bname] = pname
        else:
            jname1,jname2 = findJoints(eb.name, eb.head, joints)
            if jname2 is None:
                hjoints[bname] = jname1
            else:
                hv = findVertex(eb.head, ob.data.vertices)
                if hv:
                    hjoints[bname] = ('%s_hd' % bname)
                    fp.write("  ('%s_hd', 'v', %d),\n" % (bname, hv.index))
                elif bname in ManualHeads.keys():
                    hjoints[bname] = ('%s_hd' % bname)
                    type,value = ManualHeads[bname]
                    if isinstance(value,str):
                        value = ("'%s'" % value)
                    fp.write("  ('%s_hd', '%s', %s),\n" % (bname, type, value))
                else:
                    print("Head:", bname)
                    ignores.append(bname)

        jname1,jname2 = findJoints(eb.name, eb.tail, joints)
        if jname2 is None:
            tjoints[bname] = jname1
        else:
            tv = findVertex(eb.tail, ob.data.vertices)
            if tv:
                fp.write("  ('%s_tl', 'v', %d),\n" % (bname, tv.index))
                tjoints[bname] = ('%s_tl' % bname)
            elif bname in ManualTails.keys():
                tjoints[bname] = ('%s_tl' % bname)
                type,value = ManualTails[bname]
                if isinstance(value,str):
                    value = ("'%s'" % value)
                fp.write("  ('%s_tl', '%s', %s),\n" % (bname, type, value))
                tjoints[bname] = ('%s_tl' % bname)
            elif len(eb.children) == 1:
                child = eb.children[0]
                dolast.append((bname, child.name, eb.head, eb.tail, child.tail))
            else:
                print("Tail:", bname)
                ignores.append(bname)

    print("On line:")
    fp.write("\n")
    for bname,cname,bhead,btail,ctail in dolast:
        hj = hjoints[bname]
        try:
            tj = tjoints[cname]
        except KeyError:
            tj = None
            print("No tail:", bname, cname)
        vec1 = btail - bhead
        vec2 = ctail - bhead
        frac = vec1.length / vec2.length
        offset = (vec1 - frac*vec2) / vec2.length

        if bname == 'clavicle.L':
            print(bname)
            print(bhead)
            print(btail)
            print(cname)
            print(ctail)
            print(vec1)
            print(vec2)
            print(frac)
            print(offset)

        if offset.length > 1e-3:
            #print("Unaligned:", bname, cname,vec1, vec2, norm)
            x,y,z = offset
            fp.write(
            "  ('%s_tl0', 'l', ((%.4f, '%s'), (%.4f, '%s'))),\n" %
                (bname, 1-frac, hj, frac, tj) +
            "  ('%s_tl', 'so', ('%s_tl0', '%s', '%s', (%.4f, %.4f, %.4f))),\n" %
                (bname, bname, hj, tj, x, z, -y)
            )
        else:
            print("H %s, T %s, %f" % (bname, cname, frac))
            fp.write(
            "  ('%s_tl', 'l', ((%.4f, '%s'), (%.4f, '%s'))),\n" %
                (bname, 1-frac, hjoints[bname], frac, tjoints[cname])
            )
        tjoints[bname] = ('%s_tl' % bname)

    fp.write("\n]\n")
    return hjoints, tjoints, ignores, connects


def getHeadLoc(bname, hjoints, connects):
    try:
        return hjoints[bname]
    except KeyError:
        pass
    try:
        return ('%s_tl' % connects[bname])
    except KeyError:
        return ('%s_hd' % bname)


def getTailLoc(bname, tjoints):
    try:
        return tjoints[bname]
    except KeyError:
        return ('%s_tl' % bname)


def findJoints(bname, co, joints, minDist=0.05):
    dists = []
    for jname,jco in joints.items():
        dists.append((distance(co, jco), jname))
    dists.sort()
    if abs(dists[0][0]) < minDist:
        return (dists[0][1], None)
    else:
        return (dists[0][1], dists[1][1])


def distance(co1, co2):
    vec = co1-co2
    return vec.length


def findVertex(co, verts):
    for v in verts:
        if distance(v.co, co) < 1e-4:
            return v

    return None


def getBoneName(bone):
    bname = bone.name[0].lower() + bone.name[1:]
    return bname


def writeHeadsTails(fp, rig, hjoints, tjoints, connects):
    fp.write("\nHeadsTails = {\n")
    for bone in rig.data.bones:
        bname = getBoneName(bone)
        hloc = getHeadLoc(bname, hjoints, connects)
        tloc = getTailLoc(bname, tjoints)
        fp.write("  '%s' : ('%s', '%s'),\n" % (bname, hloc, tloc))
    fp.write("\n}\n")


def writeArmature(fp, hier, rig, ignores):
    fp.write("\nArmature = {\n")
    writeHierarchy(fp, hier, None, rig, ignores, False)
    fp.write("\n}\n")


def writeHierarchy(fp, hier, parent, rig, ignores, inface):
    bone,children = hier
    if parent:
        pstring = "'%s'" % getBoneName(parent)
    else:
        pstring = "None"
        fp.write("\n")
    if bone:
        bname = getBoneName(bone)
        if bone.use_connect:
            conn = "|F_CON"
        else:
            conn = ""
        if rig.MhxExportZeroRoll:
            roll = 0
        else:
            roll = rig.data.edit_bones[bone.name].roll
        if bname not in ignores:
            if bname in ["head", "neck", "neck2", "eye.L", "eye.R"]:
                layer = "L_HEAD"
                inface = True
            elif inface:
                layer = "L_FACE"
            else:
                layer = "L_MAIN"
            fp.write("  '%s' : (%.3f, %s, F_DEF%s, %s),\n" % (bname, roll, pstring, conn, layer))
    for child in children:
        writeHierarchy(fp, child, bone, rig, ignores, inface)


def defineJoints(ob):
    jointNames = [
    "l-eye",
    "r-eye",
    "pelvis",
    "spine-4",
    "spine-3",
    "spine-2",
    "spine-1",
    "l-foot-2",
    "l-foot-1",
    "l-toe-5-3",
    "l-toe-5-4",
    "l-toe-4-3",
    "l-toe-4-4",
    "l-toe-3-3",
    "l-toe-3-4",
    "l-toe-2-4",
    "l-toe-2-3",
    "l-toe-2-2",
    "l-toe-3-2",
    "l-toe-4-2",
    "l-toe-5-2",
    "l-toe-5-1",
    "l-toe-4-1",
    "l-toe-3-1",
    "l-toe-2-1",
    "l-toe-1-3",
    "l-toe-1-2",
    "l-toe-1-1",
    "l-ankle",
    "l-knee",
    "l-upper-leg",
    "l-finger-2-4",
    "l-finger-3-4",
    "l-finger-4-4",
    "l-finger-5-4",
    "l-finger-5-3",
    "l-finger-4-3",
    "l-finger-3-3",
    "l-finger-2-3",
    "l-finger-2-2",
    "l-finger-3-2",
    "l-finger-4-2",
    "l-finger-5-2",
    "l-finger-5-1",
    "l-finger-4-1",
    "l-finger-3-1",
    "l-finger-2-1",
    "l-finger-1-4",
    "l-finger-1-3",
    "l-finger-1-2",
    "l-finger-1-1",
    "l-hand-3",
    "l-hand-2",
    "l-hand",
    "l-elbow",
    "l-shoulder",
    "l-clavicle",
    "l-scapula",
    "head",
    "l-lowerlid",
    "l-eye-target",
    "l-upperlid",
    "r-foot-2",
    "r-foot-1",
    "r-toe-5-3",
    "r-toe-5-4",
    "r-toe-4-3",
    "r-toe-4-4",
    "r-toe-3-3",
    "r-toe-3-4",
    "r-toe-2-4",
    "r-toe-2-3",
    "r-toe-2-2",
    "r-toe-3-2",
    "r-toe-4-2",
    "r-toe-5-2",
    "r-toe-5-1",
    "r-toe-4-1",
    "r-toe-3-1",
    "r-toe-2-1",
    "r-toe-1-3",
    "r-toe-1-2",
    "r-toe-1-1",
    "r-ankle",
    "r-knee",
    "r-upper-leg",
    "r-finger-2-4",
    "r-finger-3-4",
    "r-finger-4-4",
    "r-finger-5-4",
    "r-finger-5-3",
    "r-finger-4-3",
    "r-finger-3-3",
    "r-finger-2-3",
    "r-finger-2-2",
    "r-finger-3-2",
    "r-finger-4-2",
    "r-finger-5-2",
    "r-finger-5-1",
    "r-finger-4-1",
    "r-finger-3-1",
    "r-finger-2-1",
    "r-finger-1-4",
    "r-finger-1-3",
    "r-finger-1-2",
    "r-finger-1-1",
    "r-hand-3",
    "r-hand-2",
    "r-hand",
    "r-elbow",
    "r-shoulder",
    "r-clavicle",
    "r-scapula",
    "r-lowerlid",
    "r-eye-target",
    "r-upperlid",
    "neck",
    "jaw",
    "tongue-4",
    "tongue-3",
    "head-2",
    "tongue-2",
    "tongue-1",
    "mouth",
    ]

    joints = {}
    vn0 = 13606
    for name in jointNames:
        vsum = Vector((0,0,0))
        for n in range(8):
            vsum += ob.data.vertices[vn0+n].co
        joints[name] = vsum/8
        print(name, vn0, vn0+7, joints[name])
        vn0 += 8
    return joints
