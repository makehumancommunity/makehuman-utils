"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Author:**            Manuel Bastioni

**Copyright(c):**      Manuel Bastioni 2014

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

Export a json file with a rigging designed upon the makehuman base mesh.

To use this script, you can place it in the .blender/scripts/addons dir
and then activate the script in the "Addons" tab (user preferences).
Access from the File > Import menu.

"""

bl_info = {
    'name': 'Export: MakeHuman Rigging (.json)',
    'author': 'Manuel Bastioni',
    'version': (1,0,2),
    "blender": (2,6,0),
    'location': "File > Export > MakeHuman Rigging (.json) and File > Import > MakeHuman Rigging (.json)",
    'description': 'Export skeleton, groups and weights as json file',
    'warning': '',
    'wiki_url': '',
    'category': 'MakeHuman'}

import bpy 
from . export_mh_rigging import *
from . import_mh_rigging import *

def menu_func_export(self, context):
    self.layout.operator(ExportMHRigging.bl_idname, text="MakeHuman rigging (.json)")    
    
def menu_func_import(self, context):    
    self.layout.operator(ImportMHRigging.bl_idname, text="MakeHuman rigging (.json)")    

            
def register():
    bpy.utils.register_class(ExportMHRigging)
    bpy.utils.register_class(ImportMHRigging)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.utils.register_class(UI_messagebox)


def unregister():
    bpy.utils.unregister_class(ExportMHRigging)
    bpy.utils.unregister_class(ImportMHRigging)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(UI_messagebox) 

if __name__ == "__main__":
    register()



