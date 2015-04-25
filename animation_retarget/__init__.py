#!/usr/bin/python

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Author:**            Jonas Hauquier, Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3

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


Abstract
--------

Transfer an animation or pose from one skeleton to another by copying each
bone's relative poses, and compensating for differences in bind pose.

Allows transferring the animation from a BVH file imported in Blender to a MH
(or other) skeleton.
Bone names between the two skeletons are matched using fuzzy string matching,
allowing it to automatically find combinations if bone names are similar.

Usage: First select the source armature (with the animation), then select the target armature (where the animation will be transferred to) as active object.
"""

import bpy

bl_info = {
    'name': 'Animation retarget (MH)',
    'author': 'Jonas Hauquier (MakeHuman.org)',
    'version': (0,9,1),
    "blender": (2,6,0),
    'location': "Toolbar > Animation tab > Retarget (MH), Object mode > spacebar operators menu > Retarget (MH)",
    'description': 'Transfer a pose or animation from one armature (eg a BVH file) to another armature, mapping between bones based on name similarity.',
    'warning': '',
    'wiki_url': '',
    'category': 'MakeHuman'}

import sys
import os
sys.path.append( os.path.dirname(__file__) )

import animation_retarget_mh


# Operator
class ANIM_OT_retarget_animation_mh(bpy.types.Operator):
    bl_label = 'Retarget (MH)'
    bl_idname = 'anim.retarget_animation_mh'
    bl_description = 'Retarget animation from source to target armature'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    src_rig = bpy.props.StringProperty(name="Source rig", description="Armature object to copy the active animation from", default="")
    trg_rig = bpy.props.StringProperty(name="Target rig", description="Armature object to transfer the animation to", default="")

    def execute(self, context):
        """Transfer current animation from source armature (selected) to the
        target armature (active).
        """
        if not self.src_rig:
            self.report({'ERROR'}, "No valid source armature selected." % self.src_rig)
            return {'FINISHED'}
        if not self.trg_rig:
            self.report({'ERROR'}, "No valid target armature selected." % self.trg_rig)
            return {'FINISHED'}

        self.report({'INFO'}, "Retarget animation from %s to %s" % (self.src_rig, self.trg_rig))
        animation_retarget_mh.retarget_animation(bpy.data.objects[self.src_rig], bpy.data.objects[self.trg_rig])
        return {'FINISHED'}

    def invoke(self, context, event):
        src_rig, trg_rig = animation_retarget_mh.get_armatures(context)
        self.src_rig = src_rig.name
        self.trg_rig = trg_rig.name
        return self.execute(context)

    @classmethod
    def poll(cls, context):
        """Test whether this operator can be called
        """
        # Two armatures must be selected
        if not context.active_object:
            return False
        if context.active_object.type != "ARMATURE":
            return False
        if len(context.selected_objects) != 2:
            return False
        if context.selected_objects[0].type != "ARMATURE" or \
           context.selected_objects[1].type != "ARMATURE":
            return False
        return True


# GUI (Panel)
class VIEW3D_PT_retarget_animation_mh(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Animation"
    bl_label = 'Retarget (MH)'

    # TODO add bone mapping feature to GUI

    @classmethod
    def poll(self, context):
        return ANIM_OT_retarget_animation_mh.poll()

    # draw the gui
    def draw(self, context):
        Obj = context.active_object
        
        layout = self.layout
        col = layout.column(align=True)
        row = col.row()
        row.operator('anim.retarget_animation_mh', icon='ARMATURE_DATA')

        try:
            src_rig, trg_rig = animation_retarget_mh.get_armatures(context)

            col = layout.column(align=True)
            row = col.row()
            row.label(src_rig.name, icon='POSE_DATA')

            col = layout.column(align=True)
            row = col.row()
            row.label(trg_rig.name, icon='NEXT_KEYFRAME')
        except:
            pass


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

