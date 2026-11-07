import bpy, math
from mathutils import Vector

# Nightfall: The Last Oath — character generator
# Run this script in Blender's Scripting workspace.
# Builds a detailed, stylised dark-fantasy character with Idle / Walk / Run actions.
# Exports only the character and armature as a GLB beside this .blend file.

EXPORT_PATH = bpy.path.abspath("//nightfall_knight.glb")
scene = bpy.context.scene
scene.render.fps = 30

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, rough=0.5, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = rough
    if emission:
        bs.inputs["Emission Color"].default_value = (*emission, 1)
        bs.inputs["Emission Strength"].default_value = strength
    return m

steel = mat("Midnight steel", (0.065,0.09,0.14), .85, .25)
silver = mat("Pale steel edges", (.38,.48,.58), .9, .22)
gold = mat("Aged gold trim", (.48,.29,.09), .8, .3)
cloth = mat("Deep wine cloth", (.12,.018,.04), .05, .8)
leather = mat("Dark leather", (.045,.025,.018), .05, .65)
dark = mat("Charcoal undersuit", (.015,.022,.03), 0, .85)
cyan = mat("Cold cyan rune", (.01,.22,.32), .2, .2, (.02,.55,.9), 2.5)

def finish(o, material, smooth=True):
    o.data.materials.append(material)
    if smooth and o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
    return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o,material)

def box(name, loc, dims, material, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(o,material,False)
    if bevel:
        b=o.modifiers.new("Rounded armour edges",'BEVEL'); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted normals",'WEIGHTED_NORMAL')
    return o

def rod(name, a, b, radius, material, radius2=None):
    a,b=Vector(a),Vector(b); d=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=radius if radius2 is None else radius2,
                                   radius2=radius, depth=d.length, location=(a+b)/2)
    o=bpy.context.object; o.name=name
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y')
    finish(o,material)
    be=o.modifiers.new("Soft edges",'BEVEL'); be.width=.018; be.segments=2
    return o

bpy.ops.object.armature_add(enter_editmode=True)
rig=bpy.context.object; rig.name="Nightfall_Rig"; rig.data.name="Nightfall_Skeleton"
bones=rig.data.edit_bones
root=bones[0]; root.name="root"; root.head=(0,0,0); root.tail=(0,0,.2)
def addbone(name, head, tail, parent):
    b=bones.new(name); b.head=head; b.tail=tail; b.parent=bones[parent]; return b
addbone("pelvis",(0,0,.92),(0,0,1.12),"root")
addbone("spine",(0,0,1.12),(0,0,1.52),"pelvis")
addbone("chest",(0,0,1.52),(0,0,1.8),"spine")
addbone("neck",(0,0,1.8),(0,0,1.96),"chest")
addbone("head",(0,0,1.96),(0,0,2.25),"neck")
for s,sgn in (("L",1),("R",-1)):
    addbone("upper_arm."+s,(sgn*.28,0,1.7),(sgn*.55,0,1.47),"chest")
    addbone("forearm."+s,(sgn*.55,0,1.47),(sgn*.67,0,1.2),"upper_arm."+s)
    addbone("hand."+s,(sgn*.67,0,1.2),(sgn*.69,0,1.08),"forearm."+s)
    addbone("thigh."+s,(sgn*.14,0,1.02),(sgn*.16,0,.62),"pelvis")
    addbone("shin."+s,(sgn*.16,0,.62),(sgn*.16,0,.18),"thigh."+s)
    addbone("foot."+s,(sgn*.16,0,.18),(sgn*.16,-.22,.1),"shin."+s)
addbone("cape",(0,.04,1.65),(0,.34,.75),"chest")
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True

parts=[]
def attach(o,bone_name):
    o.parent=rig; o.parent_type='BONE'; o.parent_bone=bone_name
    o.matrix_parent_inverse=rig.matrix_world.inverted()
    parts.append(o); return o

attach(sphere("Torso undersuit",(0,0,1.47),(.31,.21,.42),dark),"spine")
attach(sphere("Chest cuirass",(0,-.015,1.62),(.36,.24,.29),steel),"chest")
attach(box("Central breastplate",(0,-.235,1.62),(.12,.025,.32),silver,.02),"chest")
attach(sphere("Upper chest guard",(0,0,1.82),(.22,.18,.12),steel),"chest")
for z,w in ((1.73,.27),(1.59,.29),(1.44,.23)):
    attach(box("Gold cuirass inlay",(0,-.225,z),(w,.018,.022),gold,.008),"chest")
attach(box("Waist belt",(0,0,1.14),(.47,.27,.11),leather,.025),"pelvis")
attach(sphere("Belt clasp",(0,-.145,1.15),(.065,.025,.065),gold),"pelvis")

attach(sphere("Helmet shell",(0,0,2.08),(.22,.2,.27),steel),"head")
attach(sphere("Helmet crown",(0,0,2.26),(.16,.16,.11),silver),"head")
attach(box("Visor recess",(0,-.19,2.105),(.25,.022,.055),dark,.01),"head")
attach(box("Glowing visor",(0,-.207,2.105),(.18,.012,.014),cyan,.006),"head")
for s in (-1,1):
    attach(sphere("Cheek guard",(s*.16,-.035,2.0),(.07,.14,.13),silver),"head")
    attach(rod("Helm crest",(s*.15,0,2.13),(s*.24,.015,2.29),.025,gold),"head")

for side,sgn in (("L",1),("R",-1)):
    attach(sphere("Shoulder pauldron",(sgn*.36,0,1.74),(.18,.21,.15),silver),"chest")
    attach(sphere("Pauldron inset",(sgn*.36,-.19,1.74),(.11,.025,.09),steel),"chest")
    attach(rod("Upper arm plate",(sgn*.39,0,1.68),(sgn*.55,0,1.49),.095,steel,.13),"upper_arm."+side)
    attach(sphere("Elbow joint",(sgn*.56,0,1.46),(.095,.1,.095),gold),"forearm."+side)
    attach(rod("Forearm bracer",(sgn*.57,0,1.43),(sgn*.67,0,1.21),.075,silver,.105),"forearm."+side)
    attach(sphere("Glove",(sgn*.69,-.01,1.12),(.085,.1,.11),leather),"hand."+side)

for side,sgn in (("L",1),("R",-1)):
    attach(sphere("Hip guard",(sgn*.15,0,1.02),(.16,.18,.15),steel),"pelvis")
    attach(rod("Thigh armour",(sgn*.15,0,.98),(sgn*.16,0,.65),.105,steel,.14),"thigh."+side)
    attach(sphere("Knee plate",(sgn*.16,-.115,.62),(.11,.06,.11),silver),"thigh."+side)
    attach(rod("Greave",(sgn*.16,0,.58),(sgn*.16,0,.2),.085,steel,.11),"shin."+side)
    attach(box("Boot",(sgn*.16,-.08,.12),(.19,.34,.17),leather,.045),"foot."+side)
    attach(box("Boot toe cap",(sgn*.16,-.225,.17),(.18,.1,.075),silver,.02),"foot."+side)

attach(box("Front tabard",(0,-.15,.91),(.26,.045,.4),cloth,.018),"pelvis")
attach(box("Rear tabard",(0,.15,.91),(.26,.045,.4),cloth,.018),"pelvis")
verts=[(-.22,.08,1.76),(.22,.08,1.76),(-.36,.36,.72),(.36,.36,.72),
       (-.18,.18,1.7),(.18,.18,1.7),(-.28,.4,.74),(.28,.4,.74)]
faces=[(0,1,5,4),(0,4,6,2),(4,5,7,6),(5,1,3,7),(2,6,7,3)]
me=bpy.data.meshes.new("CapeMesh"); me.from_pydata(verts,[],faces); me.materials.append(cloth)
cape=bpy.data.objects.new("Layered cloth cape",me); bpy.context.collection.objects.link(cape)
sol=cape.modifiers.new("Cloth thickness",'SOLIDIFY'); sol.thickness=.025
bev=cape.modifiers.new("Soft cloth edges",'BEVEL'); bev.width=.015; bev.segments=2
attach(cape,"chest")
attach(sphere("Oath rune medallion",(0,-.265,1.36),(.07,.02,.07),cyan),"spine")
for s in (-1,1):
    for z in (1.78,1.72,1.66):
        attach(sphere("Pauldron rivet",(s*.42,-.2,z),(.016,.016,.016),gold),"chest")

def keybone(name, frame, rot):
    p=rig.pose.bones[name]; p.rotation_mode='XYZ'; p.rotation_euler=rot
    p.keyframe_insert(data_path="rotation_euler",frame=frame,group=name)

def create_action(name, frames, mode):
    if rig.animation_data: rig.animation_data.action=None
    else: rig.animation_data_create()
    for f in frames:
        t=(f-frames[0])/max(1,frames[-1]-frames[0])
        wave=math.sin(t*2*math.pi)
        if mode=="Idle":
            keybone("spine",f,(.012*wave,0,.01*wave))
            keybone("head",f,(0,.015*wave,0))
            keybone("cape",f,(.02*wave,0,0))
        else:
            amp=.38 if mode=="Walk" else .62
            a=wave*amp
            keybone("thigh.L",f,(a,0,0)); keybone("thigh.R",f,(-a,0,0))
            keybone("shin.L",f,(max(0,-a)*.7,0,0))
            keybone("shin.R",f,(max(0,a)*.7,0,0))
            keybone("upper_arm.L",f,(-a*.55,0,0))
            keybone("upper_arm.R",f,(a*.55,0,0))
            keybone("forearm.L",f,(-.12,0,0)); keybone("forearm.R",f,(-.12,0,0))
            keybone("spine",f,(.02*wave,0,0)); keybone("cape",f,(.06*wave,0,0))
    act=rig.animation_data.action; act.name=name; act.use_fake_user=True
    for fc in act.fcurves:
        for kp in fc.keyframe_points: kp.interpolation='BEZIER'
    return act

actions=[
    create_action("Idle",[1,16,31],"Idle"),
    create_action("Walk",[1,9,17,25,33],"Walk"),
    create_action("Run",[1,7,13,19,25],"Run")
]
for a in actions: a.use_fake_user=True

# Keep each action on its own NLA track for separate animation export.
rig.animation_data.action=None
for action in actions:
    track=rig.animation_data.nla_tracks.new()
    track.name=action.name
    strip=track.strips.new(action.name,int(action.frame_range[0]),action)
    strip.name=action.name
    strip.blend_type='REPLACE'

world=bpy.data.worlds.new("Nightfall World") if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.012,.018,.03,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.35

bpy.ops.object.camera_add(location=(3.4,-6.8,2.8))
cam=bpy.context.object; cam.name="Preview Camera"
cam.rotation_euler=(Vector((0,0,1.2))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.lens=55; scene.camera=cam
for name,loc,energy,color,size in [
    ("Moon key",(2,-4,4),520,(1,1,1),4),
    ("Cold rim",(-3,1,2.8),700,(.18,.48,1),3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    light=bpy.context.object; light.name=name; light.data.energy=energy
    light.data.color=color; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(Vector((0,0,1.2))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015))
floor=bpy.context.object; floor.name="Preview Ground"
floor.data.materials.append(mat("Preview ground",(.012,.018,.028),.1,.9))

bpy.ops.object.select_all(action='DESELECT')
rig.select_set(True)
for obj in parts: obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=EXPORT_PATH,export_format='GLB',
    use_selection=True,export_animations=True,export_nla_strips=True,export_apply=True)
print("Nightfall character created. GLB exported to:",EXPORT_PATH)
print("Actions created: Idle, Walk, Run")
