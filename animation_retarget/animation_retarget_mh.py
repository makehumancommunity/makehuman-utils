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
"""

import bpy
from difflib import SequenceMatcher

BONE_NAME_SIMILARITY_THRESHOLD = 0.7


# Credit goes to Thomas Larsson for these derivations
#
#   M_b = global bone matrix, relative world (PoseBone.matrix)
#   L_b = local bone matrix, relative parent and rest (PoseBone.matrix_local)
#   R_b = bone rest matrix, relative armature (Bone.matrix_local)
#   T_b = global T-pose marix, relative world
#
#
#   M_p = parent global bone matrix
#   R_p = parent rest matrix
#
#   A_b = A bone matrix, A-pose rest matrix, converts M'_b in A pose to M_b in T pose
#   M'_b= bone matrix for the mesh in A pose
#
#   T_b = T bone matrix, converts bone matrix from T pose into A pose
#
#
#   M_b = M_p R_p^-1 R_b L_b
#   M_b = A_b M'_b
#   T_b = A_b T'_b
#   A_b = T_b T'^-1_b
#   B_b = R^-1_b R_p
#
#   L_b = R^-1_b R_p M^-1_p A_b M'_b
#   L_b = B_b M^-1_p A_b M'_b
#

def _get_bone_matrix(bone):
    """bone should be a Bone

    B_b
    """
    if bone.parent:
        b_mat = bone.matrix_local.inverted() * bone.parent.matrix_local
    else:
        b_mat = bone.matrix_local.inverted()
    return b_mat

def _get_rest_pose_compensation_matrix(src_pbone, trg_pbone):
    """Bind pose compensation matrix
    bones are expected to be of type PoseBone and be in rest pose

    A_b
    """
    a_mat = src_pbone.matrix.inverted() * trg_pbone.matrix
    return a_mat

def set_rotation(pose_bone, rot, frame_idx, group=None):
    """Apply rotation to PoseBone and insert a keyframe.
    Rotation can be a matrix, a quaternion or a tuple of euler angles
    """
    if not group:
        group = pose_bone.name

    if pose_bone.rotation_mode == 'QUATERNION':
        try:
            quat = rot.to_quaternion()
        except:
            quat = rot
        pose_bone.rotation_quaternion = quat
        pose_bone.keyframe_insert('rotation_quaternion', frame=frame_idx, group=group)
    else:
        try:
            euler = rot.to_euler(pose_bone.rotation_mode)
        except:
            euler = rot
        pose_bone.rotation_euler = euler
        pose_bone.keyframe_insert('rotation_euler', frame=frame_idx, group=group)

def set_translation(pose_bone, trans, frame_idx, group=None):
    """Insert a translation keyframe for a pose bone
    """
    if not group:
        group = pose_bone.name

    try:
        trans = trans.to_translation()
    except:
        pass
    pose_bone.location = trans
    pose_bone.keyframe_insert("location", frame=frame_idx, group=group)

def fuzzy_stringmatch_ratio(str1, str2):
    """Compare two strings using a fuzzy matching algorithm. Returns the
    similarity of both strings as a float, with 1 meaning identical match,
    and 0 meaning no similarity at all.
    """
    m = SequenceMatcher(None, str1, str2)
    return m.ratio()

def select_and_set_rest_pose(rig, scn):
    """Select the rig, go into pose mode and clear all rotations (sets to rest
    pose)
    """
    scn.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.scale_clear()

def sort_by_depth(bonemaplist):
    """Sort bone mapping list by depth of target bone.
    Creating a breadth-first list through the target skeleton.
    This order is needed for correct retargeting, so that we build up the
    _trg_mat and _src_mat top to bottom.
    """
    def _depth(bonemap):
        """Depth of target bone in the skeleton, is 0 for root bone.
        Depth also is the number of parents this bone has.
        """
        return len(bonemap.trg_bone.parent_recursive)

    sort_tuples = [(_depth(bm), bm) for bm in bonemaplist]
    return [x[1] for x in sorted(sort_tuples, key=lambda b: b[0])]

class AnimationRetarget(object):
    """Manages the retargetting operation between two armatures.
    """
    def __init__(self, src_amt, trg_amt):
        self.src_amt = src_amt
        self.trg_amt = trg_amt

        self.bone_mappings = []
        self.trg_bone_lookup = {}  # Lookup a mapping by target bone name
        self.src_bone_lookup = {}  # Lookup a mapping by source bone name

        # Automatically map source bones to target bones using fuzzy matching
        self.find_bone_mapping()

        self.bone_mappings = sort_by_depth(self.bone_mappings)
        self._init_lookup_structures()

    def _init_lookup_structures(self):
        """Create lookup dicts that allow quick access to the mappings by
        source or target bone name. 
        """
        for bm in self.bone_mappings:
            self.trg_bone_lookup[bm.trg_bone.name] = bm
            self.src_bone_lookup[bm.src_bone.name] = bm

    def find_bone_mapping(self):
        """Find combination of source and target bones by comparing the bones
        from both armatures with a fuzzy string matching algorithm.
        """
        # TODO allow more complicated remappings by allowing to specify a mapping file
        not_mapped_trg = {}
        mapped_src = {}
        for trg_bone in self.trg_amt.pose.bones:
            if trg_bone.name in self.src_amt.pose.bones:
                src_bone = self.src_amt.pose.bones[trg_bone.name]
                self.bone_mappings.append(BoneMapping(src_bone, trg_bone, self))
                print ("Bone mapped: %s -> %s" % (src_bone.name, trg_bone.name))
                mapped_src[src_bone.name] = True
            else:
                not_mapped_trg[trg_bone.name] = trg_bone

        for trg_bone in not_mapped_trg.values():
            src_candidates = [b for b in self.src_amt.pose.bones if b.name not in mapped_src]
            best_candidate = None
            score = -1
            for b_idx, src_bone in enumerate(src_candidates):
                ratio = fuzzy_stringmatch_ratio(src_bone.name, trg_bone.name)
                if ratio > score:
                    score = ratio
                    best_candidate = b_idx
            if best_candidate is not None and score > BONE_NAME_SIMILARITY_THRESHOLD:
                src_bone = src_candidates[best_candidate]
                self.bone_mappings.append(BoneMapping(src_bone, trg_bone, self))
                print ("Bone mapped: %s -> %s" % (src_bone.name, trg_bone.name))
                del src_candidates[best_candidate]
            else:
                print ("Could not find an approriate source bone for %s" % trg_bone.name)

    def retarget(self, scn, frames):
        """Start the retarget operation for specified frames.
        """
        scn.frame_set(0)
        select_and_set_rest_pose(self.src_amt, scn)
        select_and_set_rest_pose(self.trg_amt, scn)

        for bm in self.bone_mappings:
            bm.update_matrices()

        for frame_idx in frames:
            scn.frame_set(frame_idx)
            for b_map in self.bone_mappings:
                b_map.retarget(frame_idx)


class BoneMapping(object):
    def __init__(self, src_pbone, trg_pbone, container):
        """A mapping of a source bone to a target bone. Retargetting will 
        transfer the pose from the source bone, compensate it for the difference
        in bind pose between source and target bone, and apply a corresponding
        pose matrix on the target bone.
        src_pbone and trg_pbone are expected to be PoseBones
        """
        self.container = container
        self.src_bone = src_pbone.bone
        self.trg_bone = trg_pbone.bone

        self.src_pbone = src_pbone
        self.trg_pbone = trg_pbone

        self.src_mat = None
        self.trg_mat = None
        self.a_mat = None
        self.b_mat = None

    @property
    def src_parent(self):
        """Return the bone mapping for the parent of the source bone.
        """
        if not self.src_bone.parent:
            return None
        return self.container.src_bone_lookup[self.src_bone.parent.name]

    @property
    def trg_parent(self):
        """Return the bone mapping for the parent of the target bone.
        """
        if not self.trg_bone.parent:
            return None
        # TODO guard against unmapped bones
        return self.container.trg_bone_lookup[self.trg_bone.parent.name]

    def update_matrices(self):
        """Update static matrices. These change only if the rest poses or structure
        of one of the two rigs changes.
        Should be called when both rigs are in rest pose.
        """
        self.a_mat = _get_rest_pose_compensation_matrix(self.src_pbone, self.trg_pbone)
        self.b_mat = _get_bone_matrix(self.trg_bone)

        #self.src_mat = _get_bone_matrix(self.src_pbone)
        #self.b_mat = 

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return '<BoneMapping %s -> %s>' % (self.src_bone.name, self.trg_bone.name)

    def insert_keyframe(self, frame_idx, pose_mat):
        """Insert the specified matrix as a keyframe for the target bone.
        """
        set_rotation(self.trg_pbone, pose_mat, frame_idx)
        if not self.trg_bone.parent:
            set_translation(self.trg_pbone, pose_mat, frame_idx)

    def retarget(self, frame_idx):
        """Retarget the current pose of the source bone to the target bone, and
        apply it as keyframe with specified index.
        """
        frame_mat = self.src_pbone.matrix.to_4x4()
        pose_mat = self.retarget_frame(frame_mat)
        self.insert_keyframe(frame_idx, pose_mat)

    def retarget_frame(self, frame_mat):
        """Calculate a pose matrix for the target bone by retargeting the
        specified frame_mat, which is a pose on the source bone.
        """
        # Store these for reuse in child bones, should be recalculated for every frame
        self._src_mat = frame_mat
        self._trg_mat = self._src_mat * self.a_mat.to_4x4()
        self._trg_mat.col[3] = frame_mat.col[3]
        trg_parent = self.trg_parent
        if trg_parent:
            mat = trg_parent._trg_mat.inverted() * self._trg_mat
        else:
            mat = self._trg_mat
        mat = self.b_mat * mat

        # TODO apply rotation locks and corrections
        #mat = correctMatrixForLocks(mat, self.order, self.locks, self.trgBone, self.useLimits)

        # Don't know why, but apparently we need to modify _trg_mat another time
        mat_ = self.b_mat.inverted() * mat
        if trg_parent:
            self._trg_mat = trg_parent._trg_mat * mat_
        else:
            self._trg_mat = mat_

        return mat



#create a copy of mesh1 (active), but with vertex order of mesh2 (selected)
trg_rig = bpy.context.active_object
selected_objs = bpy.context.selected_objects[:]

if not trg_rig or len(selected_objs) != 2 or trg_rig.type != "ARMATURE":
    raise Exception("Exactly two armatures must be selected. This Addon copies the current animation/pose the selected armature to the active armature.")

selected_objs.remove(trg_rig)
src_rig = selected_objs[0]

if src_rig.type != "ARMATURE":
    raise Exception("Exactly two armatures must be selected. This Addon copies the current animation/pose the selected armature to the active armature.")


print ("Retarget animation from %s to %s" % (src_rig.name, trg_rig.name))

r = AnimationRetarget(src_rig, trg_rig)
r.retarget(bpy.context.scene, range(10))  # TODO determine how many frames to copy

