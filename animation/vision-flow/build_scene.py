import bpy, math, random, os, sys
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=360
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.filepath=os.path.join(ROOT,'frames','frame_')
scene.render.film_transparent=False
scene.world.color=(.24,.24,.24)
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.67,.75,.79,1);world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='AgX'
try: scene.eevee.taa_render_samples=32
except: pass
def mat(name,color,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.clear();p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
M={
 'floor':mat('Studio / warm mineral',(.49,.57,.57),.12,.38),
 'silver':mat('Brushed aluminium',(.55,.64,.67),.8,.28),
 'roller':mat('Stainless roller',(.7,.76,.8),.86,.2),
 'dark':mat('Graphite coating',(.025,.055,.065),.35,.3),
 'orange':mat('Robot / safety orange',(.93,.23,.028),.28,.27),
 'teal':mat('AGV / petrol teal',(.015,.3,.28),.3,.25),
 'white':mat('Off-white body panels',(.79,.85,.84),.22,.33),
 'rubber':mat('Rubber',(.018,.027,.032),0,.62),
 'wood':mat('Pallet / timber',(.42,.25,.11),0,.68),
 'box':mat('Kraft cardboard',(.58,.36,.17),0,.68),
 'tape':mat('Packing tape',(.7,.51,.26),0,.35),
 'label':mat('Shipping label',(.9,.91,.86),0,.7),
 'cyan':mat('Vision cyan',(.015,.72,.8),.1,.22,2),
 'led':mat('Green status LED',(.08,.75,.46),0,.3,2),
 'yellow':mat('Safety marking',(.9,.57,.08),0,.5),
 }
# Small texture variation keeps cardboard and flooring from looking flat.
for name,scale,strength in [('box',125,.13),('floor',18,.07),('wood',10,.15)]:
 nodes=M[name].node_tree.nodes;links=M[name].node_tree.links;n=nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;b=nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.035;links.new(n.outputs['Fac'],b.inputs['Height']);links.new(b.outputs['Normal'],next(n for n in nodes if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
def finish(o,name,m,bevel=0,parent=None):
 o.name=name;o.data.materials.append(M[m] if isinstance(m,str) else m)
 if bevel:
  b=o.modifiers.new('Machined edge radius','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 if parent:o.parent=parent
 return o
def cube(name,loc,size,m,bevel=.02,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,m,bevel,parent)
def cylinder(name,loc,r,depth,m,axis='Z',parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 for p in o.data.polygons:p.use_smooth=True
 return finish(o,name,m,.008,parent)
def empty(name,loc=(0,0,0)):
 o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);o.location=loc;return o
def tube(name,pts,r,m,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);o.data.materials.append(M[m]);o.parent=parent;return o
def text(name,body,loc,size,m,rotation=(0,0,0),parent=None):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.extrude=.0008;c.align_x='CENTER';o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=rotation;o.data.materials.append(M[m]);o.parent=parent;return o
def key(o,frame,loc=None,rot=None):
 if loc is not None:o.location=loc;o.keyframe_insert('location',frame=frame)
 if rot is not None:o.rotation_euler=rot;o.keyframe_insert('rotation_euler',frame=frame)
def visibility(o,begin,end):
 for frame,hidden in [(1,True),(begin,False),(end,True)]:
  o.hide_render=hidden;o.hide_viewport=hidden;o.keyframe_insert('hide_render',frame=frame);o.keyframe_insert('hide_viewport',frame=frame)
floor=cube('Workcell / studio floor',(0,0,-.12),(100,100,.2),'floor',.04)
# Fine expansion joints and restrained cell markings.
for x in range(-10,11,2):cube('Floor joint',(x,0,-.016),(.009,18,.004),'dark',0)
for y in range(-8,9,2):cube('Floor joint',(0,y,-.016),(22,.009,.004),'dark',0)
for a,b in [((-4.5,-2.4,.001),(2.5,-2.4,.001)),((-4.5,2.8,.001),(2.5,2.8,.001))]:tube('Workcell boundary',[a,b],.012,'yellow')
for y in [i*.7-5.3 for i in range(11)]:cube('AGV lane dash',(6.1,y,.002),(.045,.32,.009),'teal',.006)
text('Floor / route ID','LOGISTICS / 01',(5.45,-3.4,.012),.17,'white',rotation=(0,0,math.pi/2))

def conveyor(name,cx,cy,length,width,z):
 g=empty(name,(cx,cy,0))
 for yy in [-width/2,width/2]:
  cube(name+' / side extrusion',(0,yy,z),(length,.085,.19),'silver',.018,g)
  cube(name+' / dark rail',(0,yy,z+.12),(length,.045,.035),'dark',.008,g)
 for xx in [-length/2+.3,length/2-.3]:
  for yy in [-width/2+.08,width/2-.08]:
   cube(name+' / support',(xx,yy,z/2),(.075,.075,z),'silver',.01,g)
   cylinder(name+' / leveling foot',(xx,yy,.06),.07,.06,'dark',parent=g)
  cube(name+' / cross member',(xx,0,.28),(.07,width,.07),'silver',.01,g)
 for i in range(int(length/.14)):
  x=-length/2+.1+i*.14;cylinder(name+' / roller %02d'%i,(x,0,z+.08),.045,width-.12,'roller','Y',g)
  for yy in [-width/2,width/2]:cylinder(name+' / axle',(x,yy,z+.08),.018,.02,'dark','Y',g)
 cube(name+' / motor',(length/2-.45,width/2+.12,z-.07),(.3,.23,.23),'dark',.025,g)
 for yy in [-width/2,width/2]:
  cube(name+' / sensor',(length/2-.2,yy,z+.18),(.07,.065,.09),'dark',.008,g)
  cube(name+' / sensor LED',(length/2-.2,yy-.036,z+.18),(.018,.007,.023),'led',.002,g)
 return g
conveyor('01 / Pallet infeed',-3.0,0,4.1,1.7,.58)
conveyor('04 / Outfeed conveyor',3.18,1.35,4.6,.92,.96)

pallet=empty('Pallet / timber',(-2.2,0,.72))
for y in [-.55,0,.55]:cube('Pallet / runner',(0,y,.04),(1.45,.14,.08),'wood',.012,pallet)
for x in [-.55,0,.55]:
 for y in [-.52,.52]:cube('Pallet / block',(x,y,.105),(.18,.18,.13),'wood',.012,pallet)
for y in [-.58,-.29,0,.29,.58]:cube('Pallet / deck',(0,y,.19),(1.45,.23,.07),'wood',.008,pallet)

def make_carton(name,loc):
 g=empty(name,loc);cube(name+' / body',(0,0,0),(.62,.56,.48),'box',.008,g)
 cube(name+' / top tape',(0,0,.241),(.07,.56,.004),'tape',.001,g)
 cube(name+' / front tape',(0,-.281,0),(.07,.003,.48),'tape',.001,g)
 cube(name+' / label',(.155,-.284,.03),(.16,.004,.11),'label',.001,g)
 for i in range(13):cube(name+' / barcode',(.09+i*.01,-.288,.035),(.003 if i%3 else .006,.002,.055),'dark',0,g)
 for y in [-.16,.16]:cube(name+' / flap seam',(0,y,.243),(.6,.002,.002),'dark',0,g)
 text(name+' / stencil','FRAGILE',(-.15,-.286,-.09),.035,'dark',(math.pi/2,0,0),g)
 return g
cartons=[]
for iz in range(3):
 for iy in range(2):
  for ix in range(2):cartons.append(make_carton('Carton / %02d'%len(cartons),(-2.2+(ix-.5)*.65,(iy-.5)*.59,.96+.24+iz*.48)))
payload=cartons[-1];pick_center=payload.location.copy();pick=pick_center+Vector((0,0,.36))

# Fixed 3D camera gantry with mounting plate, fasteners, cable and optics.
for y in [-1.08,1.08]:
 cube('Vision / support post',(-3.35,y,2.13),(.1,.1,4.22),'silver',.008)
 cube('Vision / base plate',(-3.35,y,.035),(.36,.3,.06),'dark',.012)
 for xoff in [-.12,.12]:
  for yoff in [-.09,.09]:cylinder('Vision / anchor bolt',(-3.35+xoff,y+yoff,.072),.018,.014,'roller')
cube('Vision / top beam',(-3.35,0,4.24),(.1,2.36,.1),'silver',.008)
cube('Vision / camera arm',(-2.77,0,4.24),(1.26,.1,.1),'silver',.008)
camera_body=cube('Vision / 3D camera',(-2.2,0,4.13),(.47,.18,.14),'dark',.015)
for x in [-2.36,-2.04]:
 cylinder('Vision / lens rim',(x,0,4.049),.047,.025,'silver')
 cylinder('Vision / optical glass',(x,0,4.033),.036,.008,'cyan')
for i in range(7):cube('Vision / heatsink',(-2.39+i*.06,0,4.21),(.016,.17,.025),'dark',.003)
text('Vision / housing mark','3D VISION',(-2.2,-.092,4.14),.045,'white',(math.pi/2,0,0))
tube('Vision / network cable',[(-2.4,.08,4.13),(-2.7,.1,4.3),(-3.35,.1,4.3),(-3.4,-1.1,4.2),(-3.4,-1.1,.2)],.016,'dark')
# Scanner graphics are geometry, so they are editable in the scene.
vision_graphics=[]
top=2.40
corners=[(-2.9,-.68,top+.01),(-1.5,-.68,top+.01),(-1.5,.68,top+.01),(-2.9,.68,top+.01)]
for p in corners:vision_graphics.append(tube('Vision / field boundary',[(-2.2,0,4.04),p],.004,'cyan'))
vision_graphics.append(tube('Vision / target-plane border',corners+[corners[0]],.005,'cyan'))
scan=cube('Vision / scan stripe',(-2.2,-.58,top+.012),(1.27,.015,.008),'cyan',.002)
key(scan,25,(-2.2,-.58,top+.012));key(scan,55,(-2.2,.58,top+.012));visibility(scan,25,56)
random.seed(41)
cloud_vertices=[];cloud_faces=[]
for i in range(650):
 x=-2.2+random.uniform(-.62,.62);y=random.uniform(-.54,.54);z=top+.014+random.random()*.008;r=.009;n=len(cloud_vertices);cloud_vertices.extend([(x-r,y,z),(x+r,y,z),(x,y+r,z)]);cloud_faces.append((n,n+1,n+2))
data=bpy.data.meshes.new('Synthetic surface points');data.from_pydata(cloud_vertices,[],cloud_faces);data.update();cloud=bpy.data.objects.new('Vision / simulated point cloud',data);scene.collection.objects.link(cloud);data.materials.append(M['cyan']);vision_graphics.append(cloud)
for o in vision_graphics:visibility(o,25,73)
target_bounds=[]
for z in [-.245,.245]:target_bounds.append(tube('Vision / detected carton',[(pick_center.x+x,pick_center.y+y,pick_center.z+z) for x,y in [(-.315,-.285),(.315,-.285),(.315,.285),(-.315,.285),(-.315,-.285)]],.006,'cyan'))
for x in [-.315,.315]:
 for y in [-.285,.285]:target_bounds.append(tube('Vision / detected carton',[(pick_center.x+x,pick_center.y+y,pick_center.z-.245),(pick_center.x+x,pick_center.y+y,pick_center.z+.245)],.006,'cyan'))
for o in target_bounds:visibility(o,55,106)

# Industrial arm: base swivel, shoulder, elbow, wrist housings and four vacuum cups.
base=Vector((.0,-.65,0));shoulder=base+Vector((0,0,.82))
cube('Robot / mounting pedestal',base+Vector((0,0,.13)),(.86,.86,.26),'dark',.035)
for x in [-.32,.32]:
 for y in [-.32,.32]:cylinder('Robot / anchor',base+Vector((x,y,.277)),.028,.018,'roller')
cylinder('Robot / axis 1 turntable',base+Vector((0,0,.37)),.3,.28,'orange')
cylinder('Robot / base collar',base+Vector((0,0,.56)),.26,.12,'dark')
cube('Robot / controller',(.5,-1.67,.62),(.55,.4,1.24),'white',.025)
cube('Robot / controller display',(.5,-1.875,.87),(.32,.012,.2),'dark',.008)
cube('Robot / controller screen',(.5,-1.884,.87),(.26,.004,.14),'teal',.004)
cylinder('Robot / emergency stop',(.66,-1.888,.59),.038,.02,'orange','Y')
text('Robot / controller label','CELL 01',(.5,-1.886,1.08),.06,'dark',(math.pi/2,0,0))
for z,m in [(1.42,'led'),(1.5,'yellow'),(1.58,'orange')]:cylinder('Robot / tower light',(.5,-1.67,z),.04,.065,m)
links=[cube('Robot / upper arm',(0,0,0),(.25,.28,1),'orange',.055),cube('Robot / forearm',(0,0,0),(.21,.24,1),'orange',.045)]
panels=[cube('Robot / upper-arm cover',(0,0,0),(.255,.285,.72),'white',.02),cube('Robot / forearm cover',(0,0,0),(.215,.245,.6),'dark',.02)]
joints=[cylinder('Robot / axis '+str(i+2),(0,0,0),r,d,'dark','Y') for i,r,d in [(0,.22,.36),(1,.18,.31),(2,.14,.27)]]
jointcaps=[cylinder('Robot / joint end-cap',(0,0,0),r,.014,'silver','Y') for r in [.15,.12,.085]]
grip=empty('Robot / vacuum end effector')
cylinder('Robot / wrist flange',(0,0,.09),.11,.12,'silver',parent=grip)
cube('Robot / tool plate',(0,0,0),(.5,.4,.075),'dark',.012,grip)
for x in [-.17,.17]:
 for y in [-.13,.13]:
  cylinder('Robot / vacuum stem',(x,y,-.055),.023,.1,'silver',parent=grip)
  cylinder('Robot / vacuum cup',(x,y,-.105),.055,.035,'rubber',parent=grip)
  tube('Robot / vacuum tube',[(x,y,.01),(x,y,.13),(0,0,.15)],.012,'teal',grip)
cables=tube('Robot / cable loom',[(0,0,0),(0,0,1)],.028,'dark')
home=Vector((-.05,.1,1.9));place=Vector((1.1,1.35,1.685));above_pick=pick+Vector((0,0,.36));above_place=place+Vector((0,0,.9))
def lerp(a,b,u):
 u=max(0,min(1,u));u=u*u*(3-2*u);return Vector(a).lerp(Vector(b),u)
def path(t,points):
 for i in range(len(points)-1):
  fa,a=points[i];fb,b=points[i+1]
  if fa<=t<=fb:return lerp(a,b,(t-fa)/(fb-fa))
 return Vector(points[0][1] if t<points[0][0] else points[-1][1])
targets=[(1,home),(73,home),(88,Vector((-.05,.1,2.9))),(100,above_pick),(108,pick),(116,pick),(134,above_pick),(165,above_place),(186,place),(192,place),(204,above_place),(238,home),(360,home)]
cartonpath=[(1,pick_center),(108,pick_center),(116,pick_center),(134,above_pick-Vector((0,0,.36))),(165,above_place-Vector((0,0,.36))),(186,place-Vector((0,0,.36))),(192,place-Vector((0,0,.36))),(225,Vector((5.30,1.35,1.325))),(252,Vector((6.1,1.35,1.325))),(264,Vector((6.1,1.35,1.325))),(360,Vector((6.1,-4.8,1.325)))]
for f in range(1,361):
 target=path(f,targets);end=target+Vector((0,0,.15));delta=end-shoulder;d=delta.length;l1,l2=1.68,1.6;axis=delta.normalized();perp=(Vector((0,0,1))-axis*axis.z).normalized();a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a));elbow=shoulder+axis*a+perp*h
 for o,panel,A,B in zip(links,panels,[shoulder,elbow],[elbow,end]):
  o.location=(A+B)/2;o.rotation_euler=(B-A).to_track_quat('Z','Y').to_euler();o.scale.z=(B-A).length;o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f);o.keyframe_insert('scale',frame=f)
  panel.location=o.location;panel.rotation_euler=o.rotation_euler;panel.keyframe_insert('location',frame=f);panel.keyframe_insert('rotation_euler',frame=f)
 for j,cap,pos in zip(joints,jointcaps,[shoulder,elbow,end]):
  key(j,f,pos);key(cap,f,pos+Vector((0,-.19,0)))
 key(grip,f,target);key(payload,f,path(f,cartonpath))
 # Cable sleeve follows the same limb path, offset from its surface.
 pts=[shoulder+Vector((0,.19,0)),elbow+Vector((0,.19,.07)),end+Vector((0,.17,.02))];s=cables.data.splines[0]
 if len(s.points)<3:s.points.add(1)
 for point,pos in zip(s.points,pts):point.co=(*pos,1);point.keyframe_insert('co',frame=f)

# Roller-top AGV, aligned with the outfeed plane (box bottom = 1.065 - .24).
agv=empty('05 / Roller-top AGV',(6.1,1.35,0))
cube('AGV / lower bumper',(0,0,.21),(1.3,1.05,.28),'rubber',.09,agv)
cube('AGV / main body',(0,0,.42),(1.3,1.02,.34),'teal',.075,agv)
cube('AGV / upper deck',(0,0,.65),(1.25,1,.14),'white',.035,agv)
for y in [-.43,.43]:cube('AGV / roller rail',(0,y,.77),(1.25,.055,.1),'silver',.01,agv)
for i in range(9):cylinder('AGV / transfer roller',(-.53+i*.13,0,.78),.045,.8,'roller','Y',agv)
for x in [-.43,.43]:
 for y in [-.49,.49]:
  cylinder('AGV / wheel',(x,y,.19),.17,.075,'rubber','Y',agv)
  cylinder('AGV / wheel hub',(x,y-.045,.19),.072,.01,'silver','Y',agv)
cylinder('AGV / lidar',(.42,.33,.78),.09,.15,'dark',parent=agv)
cylinder('AGV / lidar lens',(.42,.33,.8),.092,.022,'cyan',parent=agv)
cube('AGV / status strip',(0,-.518,.49),(.5,.012,.018),'led',.005,agv)
text('AGV / ID','AGV 01',(0,-.52,.34),.1,'white',(math.pi/2,0,0),agv)
for f in range(1,361):key(agv,f,(6.1,1.35 if f<265 else path(f,[(264,(0,1.35,0)),(360,(0,-4.8,0))]).y,0))
# Match the receiving roller height exactly to the conveyor surface.
for o in agv.children:
 if 'roller' in o.name.lower() or 'upper deck' in o.name:o.location.z+=.255

def area(name,loc,power,size,color,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Lighting / large key',(-3,-4,8),1900,7,(1,.86,.72),(-1,0,0))
area('Lighting / cool fill',(4,5,6),1400,6,(.72,.88,1),(1,0,1))
area('Lighting / rim',(3,-2,7),1300,4,(1,1,1),(2,1,1))
def camera(name,start,end,targets,lens,begin,finish):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);d.lens=lens;d.clip_end=100;d.dof.use_dof=False
 for f in [begin,finish]:
  u=(f-begin)/(finish-begin);pos=Vector(start).lerp(Vector(end),u);target=Vector(targets[0]).lerp(Vector(targets[1]),u);key(o,f,pos,(target-pos).to_track_quat('-Z','Y').to_euler())
 marker=scene.timeline_markers.new(name,frame=begin);marker.camera=o;return o
c1=camera('SHOT 01 / Vision scan',(-5.2,-6.3,5.2),(-4.4,-5.5,4.6),[(-2.15,0,2.9),(-2.15,0,2.9)],42,1,72)
c2=camera('SHOT 02 / Guided pick',(5.5,-8,5.1),(4.6,-7.2,4.8),[(-.55,.2,1.8),(-.1,.6,1.7)],43,73,186)
c3=camera('SHOT 03 / Conveyor handoff',(2,-3.7,3.2),(7,-3.7,3.2),[(1.3,1.35,1.15),(5.6,1.35,1.15)],47,187,264)
c4=camera('SHOT 04 / Autonomous transport',(10.3,-4.2,4.8),(11,-9.3,6.5),[(5.7,.85,.8),(5.1,-3.6,.9)],42,265,360)
for f in range(187,265):
 target=path(f,cartonpath)+Vector((0,0,-.15));pos=target+Vector((.7,-5.2,2.1));key(c3,f,pos,(target-pos).to_track_quat('-Z','Y').to_euler())
scene.camera=c1
for obj in bpy.data.objects:
 if obj.animation_data and obj.animation_data.action:
  try:
   for fc in obj.animation_data.action.fcurves:
    for k in fc.keyframe_points:
     if fc.data_path in ('location','rotation_euler','scale'):k.interpolation='LINEAR'
  except:pass
# Render configuration and scene notes remain editable in the .blend.
scene['Project']='VISION FLOW / industrial concept animation'
scene['Notes']='Generic procedural assets. Simplified arm motion; synthetic point cloud. No engineering validation.'
scene['Shot list']='01 scan, 02 pick, 03 conveyor handoff, 04 AGV departure'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'delivery','Vision_Flow.blend'))
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if 'preview' in args:
 scene.render.resolution_percentage=60
 for f in [45,110,160,205,245,310,355]:
  scene.frame_set(f);scene.render.filepath=os.path.join(ROOT,'previews','preview_%03d.png'%f);bpy.ops.render.render(write_still=True)
elif 'shot3' in args:
 scene.frame_start=187;scene.frame_end=264;scene.render.filepath=os.path.join(ROOT,'frames','frame_');bpy.ops.render.render(animation=True)
elif 'render' in args:
 scene.render.filepath=os.path.join(ROOT,'frames','frame_');bpy.ops.render.render(animation=True)
