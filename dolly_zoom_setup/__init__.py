"""Dolly Zoom Setup Add-on for Blender

Adds a simple dolly zoom camera setup using a path, base circle, and focus target.
Author: dura.xyz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import bpy
from bpy.types import Operator

bl_info = {
    "name": "Dolly Zoom Setup",
    "author": "dura.xyz",
    "version": (1, 0, 0),
    "blender": (3, 3, 0),
    "location": "Add > Camera > Dolly Camera Setup",
    "description": "Adds simple dolly zoom camera setup with automatic driver configuration",
    "category": "Camera",
    "doc_url": "https://github.com/duraxyz/dolly-zoom-setup",
    "tracker_url": "https://github.com/duraxyz/dolly-zoom-setup/issues",
}

def create_dolly_zoom_setup(context):
    """Creates a simple dolly zoom setup with camera, path, and focus objects."""
    coll_name = "Dolly Zoom Setup"
    if coll_name in bpy.data.collections:
        coll_name = f"{coll_name}.{len([c for c in bpy.data.collections if c.name.startswith('DollyZoom')]):03d}"

    collection = bpy.data.collections.new(coll_name)
    context.scene.collection.children.link(collection)

    prev_active = context.view_layer.active_layer_collection
    for col in context.view_layer.layer_collection.children:
        if col.name == collection.name:
            context.view_layer.active_layer_collection = col
            break

    try:
        bpy.ops.curve.primitive_bezier_circle_add(radius=1, location=(6, -6, 3))
        base = context.active_object
        base.name = f"{coll_name}.Base"

        bpy.ops.curve.primitive_bezier_curve_add()
        path = context.active_object
        path.name = f"{coll_name}.Path"
        path.data.splines.clear()
        spline = path.data.splines.new('BEZIER')
        spline.bezier_points.add(1)
        spline.bezier_points[0].co = (0, 0, 0)
        spline.bezier_points[1].co = (0, 0, 1)

        bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
        focus = context.active_object
        focus.name = f"{coll_name}.Focus"

        bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(0, 0, 0))
        camera = context.active_object
        camera.name = f"{coll_name}.Camera"
        camera.data.lens = 50

        follow_path = camera.constraints.new('FOLLOW_PATH')
        follow_path.target = path

        copy_loc = path.constraints.new('COPY_LOCATION')
        copy_loc.target = base

        track_to = path.constraints.new('TRACK_TO')
        track_to.target = focus
        track_to.track_axis = 'TRACK_NEGATIVE_Z'
        track_to.up_axis = 'UP_Y'

        driver = follow_path.driver_add('offset').driver
        driver.type = 'SCRIPTED'

        var_dist = driver.variables.new()
        var_dist.name = "dist"
        var_dist.type = 'LOC_DIFF'
        var_dist.targets[0].id = base
        var_dist.targets[1].id = focus

        var_lens = driver.variables.new()
        var_lens.name = "lens"
        var_lens.type = 'SINGLE_PROP'
        var_lens.targets[0].id = camera
        var_lens.targets[0].data_path = "data.lens"

        driver.expression = "dist*100 - dist*100*lens/50"

        context.scene.camera = camera
    finally:
        context.view_layer.active_layer_collection = prev_active

    return {'FINISHED'}

class CAMERA_OT_add_dolly_zoom_setup(Operator):
    """Add simple dolly zoom camera setup"""
    bl_idname = "camera.add_dolly_zoom_setup"
    bl_label = "Dolly Zoom Setup"
    bl_description = "Add simple dolly zoom camera setup with automatic driver configuration"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return create_dolly_zoom_setup(context)

def menu_func(self, context):
    """Add operator to the Camera Add menu"""
    self.layout.operator(CAMERA_OT_add_dolly_zoom_setup.bl_idname, text="Dolly Zoom Setup", icon='CAMERA_DATA')

classes = (CAMERA_OT_add_dolly_zoom_setup,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_camera_add.append(menu_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_camera_add.remove(menu_func)

if __name__ == "__main__":
    register()
