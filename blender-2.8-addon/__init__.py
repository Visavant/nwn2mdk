bl_info = {
    "name": "Neverwinter Nights 2 MDB/GR2 formats (NWN2MDK)",
    "author": "FreshLook",
    "version": (0, 11, 1),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Neverwinter Nights 2 MDB/GR2 Import/Export",
    "wiki_url": "https://github.com/Arbos/nwn2mdk/wiki",
    "category": "Import-Export",
}


import bpy
from bpy.props import (
        StringProperty,
        BoolProperty,
        FloatProperty,
        FloatVectorProperty,
        EnumProperty,
        CollectionProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )


def import_custom_properties(objects):
    for obj in objects:
        for k in obj.keys():
            if k == "TINT_MAP":
                obj.nwn2mdk.object_type = 'MESH'
                obj.nwn2mdk.tint_map = obj[k]
                del obj[k]
            elif k == "DIFFUSE_COLOR":
                obj.nwn2mdk.diffuse_color = obj[k]
                del obj[k]
            elif k == "SPECULAR_COLOR":
                obj.nwn2mdk.specular_color = obj[k]
                del obj[k]
            elif k == "SPECULAR_LEVEL":
                obj.nwn2mdk.specular_level = obj[k]
                del obj[k]
            elif k == "GLOSSINESS":
                obj.nwn2mdk.glossiness = obj[k]
                del obj[k]
            elif k == "TRANSPARENCY_MASK":
                obj.nwn2mdk.use_transparency_mask = obj[k] == 1
                del obj[k]
            elif k == "HEAD":
                obj.nwn2mdk.is_head = obj[k] == 1
                del obj[k]
            elif k == "DONT_CAST_SHADOWS":
                obj.nwn2mdk.cast_no_shadows = obj[k] == 1
                del obj[k]
            elif k == "ENVIRONMENT_MAP":
                obj.nwn2mdk.use_environment_map = obj[k] == 1
                del obj[k]
            elif k == "GLOW":
                obj.nwn2mdk.glow = obj[k] == 1
                del obj[k]
            elif k == "PROJECTED_TEXTURES":
                obj.nwn2mdk.receive_projected_textures = obj[k] == 1
                del obj[k]
            elif k == "HSB_LOW":
                obj.nwn2mdk.object_type = 'HAIR_INFO'
                if obj[k] == 1:
                    obj.nwn2mdk.hair_shortening_behavior = 'LOW'
                del obj[k]
            elif k == "HSB_SHORT":
                if obj[k] == 1:
                    obj.nwn2mdk.hair_shortening_behavior = 'SHORT'
                del obj[k]
            elif k == "HSB_PONYTAIL":
                if obj[k] == 1:
                    obj.nwn2mdk.hair_shortening_behavior = 'PONYTAIL'
                del obj[k]
            elif k == "HHHB_NONE_HIDDEN":
                obj.nwn2mdk.object_type = 'HELM_INFO'
                if obj[k] == 1:
                    obj.nwn2mdk.helm_hair_hiding_behavior = 'NONE_HIDDEN'
                del obj[k]
            elif k == "HHHB_HAIR_HIDDEN":
                if obj[k] == 1:
                    obj.nwn2mdk.helm_hair_hiding_behavior = 'HAIR_HIDDEN'
                del obj[k]
            elif k == "HHHB_PARTIAL_HAIR":
                if obj[k] == 1:
                    obj.nwn2mdk.helm_hair_hiding_behavior = 'PARTIAL_HAIR'
                del obj[k]
            elif k == "HHHB_HEAD_HIDDEN":
                if obj[k] == 1:
                    obj.nwn2mdk.helm_hair_hiding_behavior = 'HEAD_HIDDEN'
                del obj[k]


class ImportMDBGR2(bpy.types.Operator, ImportHelper):
    """Import MDB/GR2"""               # Tooltip for menu items and buttons.
    bl_idname = "import_scene.nwn2mdk" # Unique identifier for buttons and menu items to reference.
    bl_label = "Import MDB/GR2"        # Display name in the interface.
    bl_options = {'UNDO', 'PRESET'}    # Enable undo for the operator.

    filter_glob: StringProperty(default="*.mdb;*.gr2", options={'HIDDEN'})

    files: CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )

    automatic_bone_orientation: BoolProperty(
            name="Automatic Bone Orientation",
            description="Try to align the major bone axis with the bone children",
            default=True,
            )

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        import os

        nw2fbx_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "nw2fbx")
        args = [nw2fbx_path]

        working_dir = os.path.dirname(self.filepath)

        for file in self.files:
            path = os.path.join(working_dir, file.name)
            args.append(path)

        args.append("-o");
        args.append("nwn2mdk-tmp.fbx");

        with open(os.path.join(working_dir, "log.txt"), "w") as log:
            import subprocess
            proc = subprocess.Popen(args, stdout=log, cwd=working_dir)
            proc.wait()

        tmpfbx = os.path.join(working_dir, "nwn2mdk-tmp.fbx")
        bpy.ops.import_scene.fbx(filepath=tmpfbx,
                                 use_image_search=False,
                                 automatic_bone_orientation=self.automatic_bone_orientation)

        import_custom_properties(context.selected_objects)

        if os.path.exists(tmpfbx):
            os.remove(tmpfbx)

        return {'FINISHED'}


def export_mesh_properties(obj):
    obj["NWN2MDK_TINT_MAP"] = obj.nwn2mdk.tint_map
    obj["NWN2MDK_DIFFUSE_COLOR"] = obj.nwn2mdk.diffuse_color
    obj["NWN2MDK_SPECULAR_COLOR"] = obj.nwn2mdk.specular_color
    obj["NWN2MDK_SPECULAR_LEVEL"] = obj.nwn2mdk.specular_level
    obj["NWN2MDK_GLOSSINESS"] = obj.nwn2mdk.glossiness
    obj["NWN2MDK_TRANSPARENCY_MASK"] = float(obj.nwn2mdk.use_transparency_mask)
    obj["NWN2MDK_HEAD"] = float(obj.nwn2mdk.is_head)
    obj["NWN2MDK_DONT_CAST_SHADOWS"] = float(obj.nwn2mdk.cast_no_shadows)
    obj["NWN2MDK_ENVIRONMENT_MAP"] = float(obj.nwn2mdk.use_environment_map)
    obj["NWN2MDK_GLOW"] = float(obj.nwn2mdk.glow)
    obj["NWN2MDK_PROJECTED_TEXTURES"] = float(obj.nwn2mdk.receive_projected_textures)


def export_custom_properties(objects):
    for obj in objects:
        if obj.nwn2mdk.object_type == 'MESH':
            export_mesh_properties(obj)
        elif obj.nwn2mdk.object_type == 'HAIR_INFO':
            obj["NWN2MDK_HSB"] = obj.nwn2mdk.hair_shortening_behavior
        elif obj.nwn2mdk.object_type == 'HELM_INFO':
            obj["NWN2MDK_HHHB"] = obj.nwn2mdk.helm_hair_hiding_behavior


def delete_custom_properties(objects):
    for obj in objects:
        obj.pop("NWN2MDK_TINT_MAP", None)
        obj.pop("NWN2MDK_DIFFUSE_COLOR", None)
        obj.pop("NWN2MDK_SPECULAR_COLOR", None)
        obj.pop("NWN2MDK_SPECULAR_LEVEL", None)
        obj.pop("NWN2MDK_GLOSSINESS", None)
        obj.pop("NWN2MDK_TRANSPARENCY_MASK", None)
        obj.pop("NWN2MDK_HEAD", None)
        obj.pop("NWN2MDK_DONT_CAST_SHADOWS", None)
        obj.pop("NWN2MDK_ENVIRONMENT_MAP", None)
        obj.pop("NWN2MDK_GLOW", None)
        obj.pop("NWN2MDK_PROJECTED_TEXTURES", None)
        obj.pop("NWN2MDK_HSB", None)
        obj.pop("NWN2MDK_HHHB", None)


class ExportMDB(bpy.types.Operator, ExportHelper):
    """Export MDB"""                       # Tooltip for menu items and buttons.
    bl_idname = "export_scene.nwn2mdk_mdb" # Unique identifier for buttons and menu items to reference.
    bl_label = "Export MDB"                # Display name in the interface.
    bl_options = {'UNDO', 'PRESET'}        # Enable undo for the operator.

    filename_ext = ".mdb"
    filter_glob: StringProperty(default="*.mdb", options={'HIDDEN'})

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        export_custom_properties(context.scene.objects)

        import os
        working_dir = os.path.dirname(self.filepath)
        tmpfbx = os.path.join(working_dir, "nwn2mdk-tmp.fbx")

        bpy.ops.export_scene.fbx(filepath=tmpfbx,
                                 axis_forward='-Z',
                                 axis_up='Y',
                                 use_tspace=True,
                                 use_custom_props=True,
                                 add_leaf_bones=False,
                                 bake_anim=False)

        import os

        fbx2nw_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fbx2nw")
        args = [fbx2nw_path, tmpfbx, "-o", os.path.basename(self.filepath)]
        working_dir = os.path.dirname(self.filepath)

        with open(os.path.join(working_dir, "log.txt"), "w") as log:
            import subprocess
            proc = subprocess.Popen(args, stdout=log, cwd=working_dir)
            proc.wait()
            if proc.returncode > 0:
                self.report({'ERROR'}, "Error during export. See log.txt for errors.")

        if os.path.exists(tmpfbx):
            os.remove(tmpfbx)

        delete_custom_properties(context.scene.objects)

        return {'FINISHED'}


class ExportGR2(bpy.types.Operator, ExportHelper):
    """Export GR2"""                       # Tooltip for menu items and buttons.
    bl_idname = "export_scene.nwn2mdk_gr2" # Unique identifier for buttons and menu items to reference.
    bl_label = "Export GR2"                # Display name in the interface.
    bl_options = {'UNDO', 'PRESET'}        # Enable undo for the operator.

    filename_ext = ".gr2"
    filter_glob: StringProperty(default="*.gr2", options={'HIDDEN'})

    bake_anim: BoolProperty(
            name="Baked Animation",
            description="Export baked keyframe animation",
            default=False,
            )

    bake_anim_simplify_factor: FloatProperty(
            name="Simplify",
            description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
            min=0.0, max=100.0,  # No simplification to up to 10% of current magnitude tolerance.
            soft_min=0.0, soft_max=10.0,
            default=1.0,  # default: min slope: 0.005, max frame step: 10.
            )

    def draw(self, context):
        pass

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        import os
        working_dir = os.path.dirname(self.filepath)
        tmpfbx = os.path.join(working_dir, "nwn2mdk-tmp.fbx")

        bpy.ops.export_scene.fbx(filepath=tmpfbx,
                                 axis_forward='-Z',
                                 axis_up='Y',
                                 use_tspace=True,
                                 use_custom_props=True,
                                 add_leaf_bones=False,
                                 bake_anim=self.bake_anim,
                                 bake_anim_use_all_bones=False,
                                 bake_anim_use_nla_strips=False,
                                 bake_anim_use_all_actions=False,
                                 bake_anim_force_startend_keying=False,
                                 bake_anim_simplify_factor=self.bake_anim_simplify_factor)


        fbx2nw_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fbx2nw")
        args = [fbx2nw_path, tmpfbx, "-o", os.path.basename(self.filepath)]

        with open(os.path.join(working_dir, "log.txt"), "w") as log:
            import subprocess
            proc = subprocess.Popen(args, stdout=log, cwd=working_dir)
            proc.wait()

        if os.path.exists(tmpfbx):
            os.remove(tmpfbx)

        return {'FINISHED'}


class NWN2MDK_PT_import_armature(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Armature"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_nwn2mdk"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "automatic_bone_orientation"),


class NWN2MDK_PT_export_bake_animation(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Bake Animation"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_nwn2mdk_gr2"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "bake_anim", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.enabled = operator.bake_anim
        layout.prop(operator, "bake_anim_simplify_factor")


class NWN2ObjectProperties(bpy.types.PropertyGroup):
    object_type: EnumProperty(
            items=(('AUTO', "Auto", "The exporter will try to auto-detect the type"),
                   ('MESH', "Mesh", "Rigid mesh or skin"),
                   ('HAIR_INFO', "Hair Info", "Hair info"),
                   ('HELM_INFO', "Helm Info", "Helm info")),
            name="Type",
            description="Type of NWN2 object")
    tint_map: StringProperty(
            name="Tint Map",
            description="Filename of the tint map without extension",
            maxlen=32)
    diffuse_color: FloatVectorProperty(
            name="Diffuse Color",
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0,
            subtype='COLOR_GAMMA')
    specular_color: FloatVectorProperty(
            name="Specular Color",
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0,
            subtype='COLOR_GAMMA')
    specular_level: FloatProperty(name='Specular Level', default=1.0)
    glossiness: FloatProperty(name='Glossiness', default=20.0)
    use_transparency_mask: BoolProperty(
            name="Transparency Mask",
            description="Indicates whether to use alpha-masked transparency")
    is_head: BoolProperty(
            name="Head (cutscene)",
            description="Indicates whether the model is a head weighted to facial bones")
    cast_no_shadows: BoolProperty(
            name="Don't Cast Shadows",
            description="Indicates whether the model casts shadows")
    use_environment_map: BoolProperty(name="Environment Map")
    glow: BoolProperty(
            name="Glow",
            description="Indicates whether the model uses a glow map")
    receive_projected_textures: BoolProperty(
            name="Projected Textures",
            description="Indicates whether the model receives interface projected textures")
    hair_shortening_behavior: EnumProperty(
            items=(('LOW', "Low", ""),
                   ('SHORT', "Short", ""),
                   ('PONYTAIL', "Ponytail", "")),
            name="Hair Shortening",
            description="Hair shortening behavior")
    helm_hair_hiding_behavior: EnumProperty(
            items=(('NONE_HIDDEN', "None Hidden", "Nothing is hidden"),
                   ('HAIR_HIDDEN', "Hair Hidden", "Hair is hidden, but not beard"),
                   ('PARTIAL_HAIR', "Partial Hair", "Hair is partially hidden"),
                   ('HEAD_HIDDEN', "Head Hidden", "Head is hidden")),
            name="Helm-Hair Hiding",
            description="Helm-Hair hiding behavior")


class OBJECT_PT_nwn2mdk(bpy.types.Panel):
    """Neverwinter Night 2 Object Properties"""
    bl_label = "NWN2"
    bl_idname = "OBJECT_PT_nwn2mdk"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        obj = context.object

        layout.prop(obj.nwn2mdk, "object_type")

        if obj.nwn2mdk.object_type == 'MESH':
            layout.prop(obj.nwn2mdk, "tint_map")
            layout.prop(obj.nwn2mdk, "diffuse_color")
            layout.prop(obj.nwn2mdk, "specular_color")
            layout.prop(obj.nwn2mdk, "specular_level")
            layout.prop(obj.nwn2mdk, "glossiness")
            layout.prop(obj.nwn2mdk, "use_transparency_mask")
            layout.prop(obj.nwn2mdk, "is_head")
            layout.prop(obj.nwn2mdk, "cast_no_shadows")
            layout.prop(obj.nwn2mdk, "use_environment_map")
            layout.prop(obj.nwn2mdk, "glow")
            layout.prop(obj.nwn2mdk, "receive_projected_textures")
        elif obj.nwn2mdk.object_type == 'HAIR_INFO':
            layout.prop(obj.nwn2mdk, "hair_shortening_behavior")
        elif obj.nwn2mdk.object_type == 'HELM_INFO':
            layout.prop(obj.nwn2mdk, "helm_hair_hiding_behavior")


def menu_func_import(self, context):
    self.layout.operator(ImportMDBGR2.bl_idname, text="Neverwinter Nights 2 (MDK) (.mdb/.gr2)")


def menu_func_export(self, context):
    self.layout.operator(ExportMDB.bl_idname, text="Neverwinter Nights 2 (MDK) (.mdb)")
    self.layout.operator(ExportGR2.bl_idname, text="Neverwinter Nights 2 (MDK) (.gr2)")


classes = (
    ImportMDBGR2,
    NWN2MDK_PT_import_armature,
    ExportMDB,
    ExportGR2,
    NWN2MDK_PT_export_bake_animation,
    NWN2ObjectProperties,
    OBJECT_PT_nwn2mdk,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

    bpy.types.Object.nwn2mdk = bpy.props.PointerProperty(type=NWN2ObjectProperties)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
