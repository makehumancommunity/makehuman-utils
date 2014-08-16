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

Bone weighting utility

"""

bl_info = {
    "name": "Weighting Tools",
    "author": "Thomas Larsson",
    "version": (1,4),
    "blender": (2, 7,0 ),
    "location": "View3D > Properties > MH Weighting Tools",
    "description": "MakeHuman Utilities",
    "warning": "",
    'wiki_url': "http://www.makehuman.org",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading MH weighting tools v %d.%03d" % bl_info["version"])
    import imp
    imp.reload(numbers)
    imp.reload(genrig)
    imp.reload(vgroup)
    imp.reload(symmetry)
    imp.reload(helpers)
    imp.reload(export)
    imp.reload(varia)
    imp.reload(io_json)
    imp.reload(gen_faceshapes)
else:
    print("Loading MH weighting tools v %d.%03d" % bl_info["version"])
    import bpy
    import os
    from bpy.props import *
    from . import numbers
    from . import genrig
    from . import vgroup
    from . import symmetry
    from . import helpers
    from . import export
    from . import varia
    from . import io_json
    from . import gen_faceshapes

#
#    class MhxWeightToolsPanel(bpy.types.Panel):
#

class MhxNumbersPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Numbers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.operator("mhw.print_vnums")
        layout.operator("mhw.print_first_vnum")
        layout.operator("mhw.print_enums")
        layout.operator("mhw.print_fnums")
        layout.operator("mhw.select_quads")
        layout.prop(scn, 'MhxVertNum')
        layout.operator("mhw.select_vnum")
        layout.operator("mhw.list_vert_pairs")


class MhxRiggingPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Rigging"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        rig = context.object
        scn = context.scene
        layout.operator("mhw.save_rig")
        layout.operator("mhw.save_action")
        layout.operator("mhw.save_vertex_groups")
        layout.prop(scn, 'MhxExportSelectedOnly', text="Selected VGroups Only")
        layout.prop(rig, "MhxExportZeroRoll")
        layout.operator("mhw.fix_json_list")


class MhxVGroupsPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Vertex groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.operator("mhw.show_only_group")
        layout.operator("mhw.remove_unlinked_from_group")

        layout.separator()
        layout.operator("mhw.unvertex_selected")
        layout.operator("mhw.unvertex_diamonds")
        layout.operator("mhw.delete_diamonds")
        layout.operator("mhw.integer_vertex_groups")
        layout.operator("mhw.copy_vertex_groups")
        layout.operator("mhw.remove_vertex_groups")
        layout.separator()
        layout.prop(scn, "MhxBlurFactor")
        layout.operator("mhw.blur_vertex_groups")
        layout.operator("mhw.prune_four")
        layout.prop(scn, "MhxVG0")
        layout.prop(scn, "MhxFactor")
        layout.operator("mhw.factor_vertex_group")
        layout.separator()

        layout.prop(scn, "MhxVG0")
        layout.prop(scn, "MhxVG1")
        layout.prop(scn, "MhxVG2")
        layout.prop(scn, "MhxVG3")
        layout.prop(scn, "MhxVG4")
        layout.operator("mhw.merge_vertex_groups")

        layout.label('Weight pair')
        layout.prop(context.scene, 'MhxWeight')
        layout.operator("mhw.multiply_weights")
        layout.prop(context.scene, 'MhxBone1')
        layout.prop(context.scene, 'MhxBone2')
        layout.operator("mhw.pair_weight")
        layout.operator("mhw.ramp_weight")
        layout.operator("mhw.create_left_right")

        layout.separator()
        layout.operator("mhw.weight_lid", text="Weight Upper Left Lid").lidname = "uplid.L"
        layout.operator("mhw.weight_lid", text="Weight Lower Left Lid").lidname = "lolid.L"


class MhxSymmetryPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Symmetry"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.prop(scn, "MhxEpsilon")
        row = layout.row()
        row.label("Weights")
        row.operator("mhw.symmetrize_weights", text="L=>R").left2right = True
        row.operator("mhw.symmetrize_weights", text="R=>L").left2right = False

        row = layout.row()
        row.label("Clean")
        row.operator("mhw.clean_right", text="Right side of left vgroups").doRight = True
        row.operator("mhw.clean_right", text="Left side of right vgroups").doRight = False

        row = layout.row()
        row.label("Shapes")
        row.operator("mhw.symmetrize_shapes", text="L=>R").left2right = True
        row.operator("mhw.symmetrize_shapes", text="R=>L").left2right = False

            #row = layout.row()
            #row.label("Verts")
            #row.operator("mhw.symmetrize_verts", text="L=>R").left2right = True
            #row.operator("mhw.symmetrize_verts", text="R=>L").left2right = False

        row = layout.row()
        row.label("Selection")
        row.operator("mhw.symmetrize_selection", text="L=>R").left2right = True
        row.operator("mhw.symmetrize_selection", text="R=>L").left2right = False


class MhxExportPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.prop(scn, 'MhxVertexGroupFile', text="File")
        row = layout.row()
        row.prop(scn, 'MhxExportAsWeightFile', text="As Weight File")
        row.prop(scn, 'MhxExportSelectedOnly', text="Selected Only")
        row.prop(scn, 'MhxVertexOffset', text="Offset")
        layout.operator("mhw.export_vertex_groups")
        layout.operator("mhw.export_left_right")
        layout.operator("mhw.export_sum_groups")
        layout.operator("mhw.export_custom_shapes")
        layout.operator("mhw.print_vnums_to_file")
        layout.operator("mhw.read_vnums_from_file")
        layout.operator("mhw.print_fnums_to_file")
        layout.separator()
        layout.operator("mhw.shapekeys_from_objects")
        layout.operator("mhw.export_shapekeys")


class MhxVariaPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Varia"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.operator("mhw.localize_files")
        layout.operator("mhw.transfer_vgroups")
        layout.operator("mhw.check_vgroups_sanity")
        layout.separator()
        layout.operator("mhw.create_hair_rig")
        layout.operator("mhw.generate_lr_files")
        layout.separator()
        layout.operator("mhw.statistics")


class MhxHelpersPanel(bpy.types.Panel):
    bl_category = "MH Weighting"
    bl_label = "Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.operator("mhw.join_meshes")
        layout.operator("mhw.fix_base_file")
        layout.operator("mhw.project_weights")
        layout.operator("mhw.smoothen_skirt")
        layout.operator("mhw.project_materials")
        layout.operator("mhw.export_base_obj")


#
#    initInterface(context):
#    class VIEW3D_OT_InitInterfaceButton(bpy.types.Operator):
#

def initInterface(context):
    bpy.types.Scene.MhxEpsilon = FloatProperty(
        name="Epsilon",
        description="Maximal distance for identification",
        default=1.0e-3,
        min=0, max=1)

    bpy.types.Scene.MhxFactor = FloatProperty(
        name="Factor",
        default=1.0,
        min=0, max=2)

    bpy.types.Scene.MhxVertNum = IntProperty(
        name="Vert number",
        description="Vertex number to select")

    bpy.types.Scene.MhxBlurFactor = FloatProperty(
        name="Blur Factor",
        default=0,
        min=0, max=1)

    bpy.types.Scene.MhxWeight = FloatProperty(
        name="Weight",
        description="Weight of bone1, 1-weight of bone2",
        default=1.0,
        min=0, max=1)

    bpy.types.Scene.MhxBone1 = StringProperty(
        name="Bone 1",
        maxlen=40,
        default='Bone1')

    bpy.types.Scene.MhxBone2 = StringProperty(
        name="Bone 2",
        maxlen=40,
        default='Bone2')

    bpy.types.Scene.MhxExportAsWeightFile = BoolProperty(
        name="Export as weight file",
        default=False)

    bpy.types.Scene.MhxExportSelectedOnly = BoolProperty(
        name="Export selected verts only",
        default=False)

    bpy.types.Scene.MhxVertexOffset = IntProperty(
        name="Offset",
        default=0,
        description="Export vertex numbers with offset")

    bpy.types.Scene.MhxVertexGroupFile = StringProperty(
        name="Vertex group file",
        maxlen=100,
        default="/home/vgroups.txt")

    bpy.types.Object.MhxExportZeroRoll = BoolProperty(
        name="Zero roll angles",
        description="Export all roll angles as 0",
        default=False)


    bpy.types.Scene.MhxVG0 = StringProperty(name="MhxVG0", maxlen=40, default='')
    bpy.types.Scene.MhxVG1 = StringProperty(name="MhxVG1", maxlen=40, default='')
    bpy.types.Scene.MhxVG2 = StringProperty(name="MhxVG2", maxlen=40, default='')
    bpy.types.Scene.MhxVG3 = StringProperty(name="MhxVG3", maxlen=40, default='')
    bpy.types.Scene.MhxVG4 = StringProperty(name="MhxVG4", maxlen=40, default='')

    bpy.types.Scene.MhxShowNumbers = BoolProperty(name="Show numbers", default=False)
    bpy.types.Scene.MhxShowVGroups = BoolProperty(name="Show vertex groups", default=False)
    bpy.types.Scene.MhxShowSymmetry = BoolProperty(name="Show symmetry", default=False)
    bpy.types.Scene.MhxShowHelpers = BoolProperty(name="Show helpers", default=False)
    bpy.types.Scene.MhxShowExport = BoolProperty(name="Show export", default=False)
    bpy.types.Scene.MhxShowVaria = BoolProperty(name="Show varia", default=False)
    return

#
#    Init and register
#

initInterface(bpy.context)

def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()


