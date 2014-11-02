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

import bpy
import json
from bpy_extras.io_utils import ExportHelper
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty
from . shared_mh_rigging import *
import os


def boneToVertex(basemesh, point):
    """
    This function gets the coordinates of a bone head, or bone tail,
    and look for the closer vertex in tha basemesh.

    Parameters
    ----------

    basemesh: The makehuman base mesh
    point: The coordinates of the point in as float list [x,y,z]

    Return
    ----------
    The function return a list with only one element, the point, that's list of three float.
    """
    vertPlacings = []
    for vert in basemesh.data.vertices:
        vertPlacings.append([vdist(point,vert.co),vert.index])
    closerVert = min(vertPlacings)

    if closerVert[0] > DELTAMIN:
        return None
    else:
        return [closerVert[1]]

def getVertsFromGroup(basemesh, groupName):

    """
    In Blender the vertgroups are stored in a odd way.
    So to retrieve the vertices that are in a group of vertices, it's
    needed to do a series of loops.
    This function return all the vertices (and their weights) for the specified
    group.
    
    Parameters
    ----------

    basemesh: The makehuman base mesh.
    groupname: the name of group were extract the vertices.

    Return
    ----------
    A list of lists [[vert_index, vert_weight],..., [vert_index, vert_weight]]
    """
    vertsInGroup = []
    if groupName in basemesh.vertex_groups:
        objGroup = basemesh.vertex_groups[groupName]
        for vert in basemesh.data.vertices:
            for vertGroup in vert.groups:
                if vertGroup.group == objGroup.index:
                    vertsInGroup.append([vert.index,round(vertGroup.weight,4)])

    return vertsInGroup

def getWeightsData(basemesh, armature):

    """
    This function extract the weight information.
    In Blender each bone is linked to a group with the same name.
    So for each bone we get the related group and extract the weight
    of each vert of this group.
    
    Parameters
    ----------

    basemesh: The makehuman base mesh.
    armature: The armature modelled for the MakeHuman mesh
    
    Return
    ----------
    A dictionary with weight data. The key is the bone name and the value is a
    list oc couples [vert_index, vert_weight]
    """

    objectMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')
    groupData = {}

    for bone in armature.data.edit_bones:
        groupName = bone.name #Because groups have the same name of bones
        verts = getVertsFromGroup(basemesh, groupName)
        groupData[bone.name] = verts

    bpy.ops.object.mode_set(mode=objectMode)
    return groupData

def getBonesData(basemesh, armature):
    """
    This function extract the main informations of each bone,
    (bone name, head name, tail name, roll angle, parent name)
    and return them as dictinary, ready to be written
    in json format.
    
    Parameters
    ----------

    basemesh: The makehuman base mesh.
    armature: The armature modelled for the MakeHuman mesh

    Return
    ----------
    A dictionary with bones data. The key is the bone name, and the
    value is a sub dictionary with the bone info.
    """

    # Store the status of the object mode that will be restored at
    # the end of the function, then enter in edit mode.
    # We need to stay in edit mode in order to access to the rest position.
    # Note: bone.roll property is available only in the edit_bones object.

    objectMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Create and populate the dictionary.

    bones = {}
    for bone in armature.data.edit_bones:
        boneData = {}
        boneData["head"] = '{0}_head'.format(bone.name)
        boneData["tail"] = '{0}_tail'.format(bone.name)
        boneData["roll"] = bone.roll
        boneData["reference"] = None
        if bone.parent:
            boneData["parent"] = '{0}'.format(bone.parent.name)
        else:
            boneData["parent"] = None
        bones[bone.name] = boneData

    # Restore the initial mode
    bpy.ops.object.mode_set(mode=objectMode)
    return bones


def getJointsData(basemesh, armature):
    """
    An helper joint is a little cube included in the base mesh,
    that is always morphed accordingly the base mesh.
    Helper joints are used to recalculate the skeleton afte the morphing.
    Each helper joint is represented by a list of eight vert indices,
    stored in JOINTS_VERT_INDICES.

    This function, for each bone, extract the coordinates of his head
    and then compare it with all the centroids of the helper joints.
    If the head is very close to a centroid, it's mapped to the centroid's
    vertices.

    When all the centroids are too far from the head, the function try to
    map it to a single vertices of the mesh, looking for it in the whole
    vertices list (not only the centroids)

    If this fails too, but the head is positioned between his bone child
    and his parent head, already mapped to an helper or a vert,
    the function try to compare the head coords with the average point
    between them.

    If this fail too, the head mapping must be done by hand, writing his
    vertices in the global MISSEDJOINT dictionary.

    The same happens for the tail of the bone.
    
    Parameters
    ----------

    basemesh: The makehuman base mesh.
    armature: The armature modelled for the MakeHuman mesh

    Return
    ----------

    The function getJointsData get the bones head and tails, and return
    a mapping with the correspondent helper joints.
    """

    global JOINTS_VERT_INDICES
    jointCentroids = []
    joints = {}

    # Store the status of the object mode that will be restored at
    # the end of the function, then enter in edit mode.
    # We need to stay in edit mode in order to access to the rest position.
    # ALso armature.data.edit_bones is empty if the armature is not in edit mode!

    objectMode = bpy.context.object.mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Retrieving the vert coordinates from the vert indices stored in
    # JOINTS_VERT_INDICES, calculate their centroid, and put them in
    # jointCentroids

    for jointIndices in JOINTS_VERT_INDICES:
        vertices = []
        for index in jointIndices:
            try:
                vertices.append(basemesh.data.vertices[index])
            except:
                print("Vert n. {0} not found for centroid calculation. Probably you are exporting a mesh that's not the base human".format(index))
        jointCentroids.append(centroid(vertices))

    for bone in armature.data.edit_bones:
        headPlacings = []
        tailPlacings = []

        # headPlacings contains all the distances between the bone head
        # and the helpers centroid. It also contains, with each distance,
        # the list of the correspondent indices of the helper verts.
        # Using the function "min", it will return the closer helper,
        # and his vert indices. The same for tailPlacing.

        for i in range(len(JOINTS_VERT_INDICES)):
                headPlacings.append([vdist(bone.head,jointCentroids[i]),JOINTS_VERT_INDICES[i]])
                tailPlacings.append([vdist(bone.tail,jointCentroids[i]),JOINTS_VERT_INDICES[i]])

        # If the distance between the bone head and the closer helper
        # is less of DELTAMIN, the helper is valid. Otherwise the head
        # has not a correspodent helper. In the second case, we look for
        # a closer vertices that can be used as helper.
        # The same for tail.

        closerHead = min(headPlacings)
        closerTail = min(tailPlacings)

        # Looking for the closer helper centroid. If fails, look for the closer vert.

        if closerHead[0] > DELTAMIN:
            joints['{0}_head'.format(bone.name)] = boneToVertex(basemesh, bone.head)
        else:
            joints['{0}_head'.format(bone.name)] = closerHead[1]

        if closerTail[0] > DELTAMIN:
            joints['{0}_tail'.format(bone.name)] = boneToVertex(basemesh, bone.tail)
        else:
            joints['{0}_tail'.format(bone.name)] = closerTail[1]

    # If after the loops above, the status is still None, the function
    # look for the interpolation of the connected head and tails.
    for k, v in joints.items():
        if v == None:

            # Retrieve the info about missed joint from the key

            boneName = k.split("_")[0]
            jointType = k.split("_")[1]
            bone = bpy.context.object.data.edit_bones[boneName]

            # Retrieve the info of the connected bones and their centroids

            if jointType == "head":
                jointToRecalculate = bone.head
                if bone.parent:
                    centroid1Key = '{0}_tail'.format(bone.name)
                    centroid2Key = '{0}_head'.format(bone.parent.name)

            elif jointType == "tail":
                jointToRecalculate = bone.tail
                if len(bone.children) != 0:
                    centroid1Key = '{0}_head'.format(bone.name)
                    centroid2Key = '{0}_tail'.format(bone.children[0].name)

            # Check if the connected joints are already mapped and then
            # interpolates them

            if joints[centroid1Key] != None and joints[centroid2Key] != None:
                centroid1= joints[centroid1Key]
                centroid2= joints[centroid2Key]
                vertices = []
                for index in centroid1:
                    vertices.append(basemesh.data.vertices[index])
                for index in centroid2:
                    vertices.append(basemesh.data.vertices[index])

                # If the interpolated centroid is close enough to the joint,
                # it's mapped to the vertices of both the connected elements.

                if vdist(centroid(vertices),jointToRecalculate) < DELTAMIN :
                    joints[k] = centroid1 + centroid2

        # If, after the checks above, the value is still missed, print
        # a warning and try to get it from the dictionary written by hand.

        if joints[k] == None:
            if k in MISSEDJOINTS:
                joints[k] =  MISSEDJOINTS[k]
            else:
                print("{0}: MISSED".format(k))

    # Restore the initial mode
    bpy.ops.object.mode_set(mode=objectMode)
    print("Examined {0} joints".format(len(joints)))

    return joints


def writeRiggingFile(context, filepath):

    """
    This function write the data in json format.
    
    Parameters
    ----------

    context: Blender context.
    filepath: The path of file to save.
    
    """
    basemesh = getObject() 
     
    
    #if basemesh == None: 
        #bpy.ops.box1.message('INVOKE_DEFAULT')
        #return {'FINISHED'}
        
    armature = basemesh.parent  
    if armature == None:
        print("The selected mesh is not parented with an armature")
        bpy.ops.box1.message('INVOKE_DEFAULT')
        return {'FINISHED'}
    
    # This is very important, because the armature
    # must be active in order to turn in edit mode.
    
    bpy.context.scene.objects.active = armature

    numVertices = len(basemesh.data.vertices)
    numFaces = len(basemesh.data.polygons)
    bones = getBonesData(basemesh, armature)
    joints = getJointsData(basemesh, armature)
    weights = getWeightsData(basemesh, armature)    

    weightsFilePath = os.path.splitext(filepath)[0]+"_weights.jsonw"
    weightsFile = os.path.basename(weightsFilePath)

    dataArmature = {}
    dataArmature["name"] = "MakeHuman skeleton"
    dataArmature["version"] = VERSION #102 means 1.0.2
    dataArmature["copyright"] = "(c) Makehuman.org 2014"
    dataArmature["license"] = "GNU Affero General Public License 3"
    dataArmature["description"] = "Very cool general-purpose skeleton"
    dataArmature["joints"] =  joints
    dataArmature["bones"] =  bones
    dataArmature["num_of_faces"] =  numFaces
    dataArmature["num_of_vertices"] =  numVertices
    dataArmature["weights_file"] = weightsFile
    
    dataWeights = {}
    dataWeights["name"] = "MakeHuman weights"
    dataWeights["version"] = VERSION #102 means 1.0.2
    dataWeights["copyright"] = "(c) Makehuman.org 2014"
    dataWeights["description"] = "Very cool general-purpose skeleton"
    dataWeights["license"] = "GNU Affero General Public License 3"
    dataWeights["weights"] =  weights
    
    
    outfile = open(filepath, 'w')
    json.dump(dataArmature, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    outfile.close()
        
    outfile = open(weightsFilePath, 'w')
    json.dump(dataWeights, outfile, sort_keys=True, indent=4, separators=(',', ': '))
    outfile.close()

    #Restore the initial active object
    bpy.context.scene.objects.active = basemesh
    return {'FINISHED'}

"""
BLENDER GUI
The following functions and classes are used to create the interface in Blender.
The script will create a new category tab in the Blender tools column
"""

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportMHRigging(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_rigging.data"  # important since its how bpy.ops.import_rigging.data is constructed
    bl_label = "Export MakeHuman Rigging"

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):        
        return writeRiggingFile(context, self.filepath)       


