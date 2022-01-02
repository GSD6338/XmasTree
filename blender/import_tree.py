import bpy
import csv

def read_tree_data(context, filepath, tree_scale):
    print("running read_tree_data...")
    
    scale = float(tree_scale)
    with open(filepath, mode ='r', encoding='utf-8-sig')as file:
   
        # reading the CSV file
        csvFile = csv.reader(file)
     
        # displaying the contents of the CSV file
        for line in csvFile:
            create_node(scale=scale, x=float(line[0]), y=float(line[1]), z=float(line[2]))
           
        file.close()

    return {'FINISHED'}

def create_node(size = 0.5, scale = 100, x=0.0, y=0.0, z=0.0):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, location=(x*scale, y*scale, z*scale))

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportTreeData(Operator, ImportHelper):
    """Import CSV containing locations"""
    bl_idname = "import_tree.tree_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Tree Data"

    # ImportHelper mixin class uses this
    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    
    tree_scale: StringProperty(
        name='Tree Scale:',
        description='amount to scale the imported coordinates by',
        default='10',
        maxlen=4,
    )

    def execute(self, context):
        return read_tree_data(context, self.filepath, self.tree_scale)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportTreeData.bl_idname, text="Import CSV Tree")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    bpy.utils.register_class(ImportTreeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportTreeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.import_tree.tree_data('INVOKE_DEFAULT')
