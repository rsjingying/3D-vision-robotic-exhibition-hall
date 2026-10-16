from pathlib import Path
import xml.etree.ElementTree as ET,json,math,struct
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/'dist/models';OUT.mkdir(parents=True,exist_ok=True)
def rot(axis,angle):
 a=np.array(axis,float);a/=np.linalg.norm(a);x,y,z=a;c=math.cos(angle);s=math.sin(angle);C=1-c
 return np.array([[c+x*x*C,x*y*C-z*s,x*z*C+y*s],[y*x*C+z*s,c+y*y*C,y*z*C-x*s],[z*x*C-y*s,z*y*C+x*s,c+z*z*C]])
def rpy(v):return rot([0,0,1],v[2])@rot([0,1,0],v[1])@rot([1,0,0],v[0])
def nums(s):return [float(x) for x in (s or '0 0 0').split()]
def scalar(s):
 if s.startswith('${radians('):return math.radians(float(s[10:-2]))
 return float(s)
def dae(path):
 r=ET.parse(path).getroot();ns={'c':r.tag.split('}')[0][1:]};find=lambda e,p:e.find(p,ns);allf=lambda e,p:e.findall(p,ns)
 unit=find(r,'c:asset/c:unit');meter=float(unit.get('meter','1')) if unit is not None else 1
 nodes={n.get('id'):n for n in allf(r,'.//c:node') if n.get('id')};geos={n.get('id'):n for n in allf(r,'c:library_geometries/c:geometry')}
 effects={}
 for e in allf(r,'c:library_effects/c:effect'):
  c=find(e,'.//c:diffuse/c:color');effects[e.get('id')]=tuple(nums(c.text)) if c is not None else (.82,.85,.87,1)
 mats={m.get('id'):effects.get(find(m,'c:instance_effect').get('url')[1:],(.82,.85,.87,1)) for m in allf(r,'c:library_materials/c:material')}
 result=[]
 def transform(node):
  T=np.eye(4)
  for e in node:
   tag=e.tag.split('}')[-1]
   if tag=='matrix':T=T@np.array(nums(e.text)).reshape(4,4)
   if tag=='translate':u=np.eye(4);u[:3,3]=nums(e.text);T=T@u
   if tag=='rotate':v=nums(e.text);u=np.eye(4);u[:3,:3]=rot(v[:3],math.radians(v[3]));T=T@u
   if tag=='scale':u=np.eye(4);u[:3,:3]=np.diag(nums(e.text));T=T@u
  return T
 def geometry(geo,T,bindings):
  mesh=find(geo,'c:mesh');src={}
  for e in allf(mesh,'c:source'):
   ar=find(e,'c:float_array');acc=find(e,'c:technique_common/c:accessor');stride=int(acc.get('stride','3'));src[e.get('id')]=np.fromstring(ar.text,sep=' ').reshape(-1,stride)
  vertices={e.get('id'):{i.get('semantic'):i.get('source')[1:] for i in allf(e,'c:input')} for e in allf(mesh,'c:vertices')}
  for e in mesh:
   tag=e.tag.split('}')[-1]
   if tag not in ['triangles','polylist']:continue
   ins=allf(e,'c:input');stride=max(int(i.get('offset','0')) for i in ins)+1;ps=allf(e,'c:p');indices=np.concatenate([np.fromstring(p.text,sep=' ',dtype=int) for p in ps]).reshape(-1,stride)
   if tag=='polylist':
    counts=np.fromstring(find(e,'c:vcount').text,sep=' ',dtype=int);tris=[];pos=0
    for count in counts:
     for j in range(1,count-1):tris.extend([indices[pos],indices[pos+j],indices[pos+j+1]])
     pos+=count
    indices=np.array(tris)
   vinput=next(i for i in ins if i.get('semantic')=='VERTEX');vd=vertices[vinput.get('source')[1:]];P=src[vd['POSITION']][indices[:,int(vinput.get('offset','0'))],:3]
   ni=next((i for i in ins if i.get('semantic')=='NORMAL'),None)
   if ni is not None:N=src[ni.get('source')[1:]][indices[:,int(ni.get('offset','0'))],:3]
   else:
    p3=P.reshape(-1,3,3);face=np.cross(p3[:,1]-p3[:,0],p3[:,2]-p3[:,0]);N=np.repeat(face,3,axis=0)
   P=(P@T[:3,:3].T+T[:3,3])*meter;N=N@np.linalg.inv(T[:3,:3]);N/=np.maximum(1e-10,np.linalg.norm(N,axis=1))[:,None]
   color=mats.get(bindings.get(e.get('material')), (.82,.85,.87,1));result.append((P,N,color))
 def walk(node,parent):
  T=parent@transform(node)
  for inst in allf(node,'c:instance_geometry'):
   bind={m.get('symbol'):m.get('target')[1:] for m in allf(inst,'.//c:instance_material')};geometry(geos[inst.get('url')[1:]],T,bind)
  for child in allf(node,'c:node'):walk(child,T)
  for inst in allf(node,'c:instance_node'):walk(nodes[inst.get('url')[1:]],T)
 sc=find(r,'c:library_visual_scenes/c:visual_scene')
 for n in allf(sc,'c:node'):walk(n,np.eye(4))
 return result
class GLB:
 def __init__(self):self.binary=bytearray();self.d={'asset':{'version':'2.0','generator':'VISION FLOW / ROS-Industrial mesh conversion'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'Robot','rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'children':[1]}],'meshes':[],'materials':[],'accessors':[],'bufferViews':[]};self.colors={}
 def buffer(self,arr,component,count,type_,target):
  while len(self.binary)%4:self.binary.append(0)
  off=len(self.binary);self.binary.extend(arr.tobytes());bv=len(self.d['bufferViews']);self.d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':arr.nbytes,'target':target});a={'bufferView':bv,'componentType':component,'count':count,'type':type_}
  if type_=='VEC3':a['min']=arr.min(axis=0).tolist();a['max']=arr.max(axis=0).tolist()
  index=len(self.d['accessors']);self.d['accessors'].append(a);return index
 def mesh(self,prims):
  grouped={}
  for P,N,c in prims:
   key=tuple(round(x,4) for x in c);grouped.setdefault(key,[]).append((P,N))
  parts=[]
  for color,arrays in grouped.items():
   values=np.concatenate([np.concatenate((p,n),axis=1) for p,n in arrays]);unique,inv=np.unique(np.round(values,6),axis=0,return_inverse=True);P=unique[:,:3].astype('<f4');N=unique[:,3:].astype('<f4');I=inv.astype('<u4')
   if color not in self.colors:
    self.colors[color]=len(self.d['materials']);self.d['materials'].append({'name':'source_'+str(len(self.colors)),'pbrMetallicRoughness':{'baseColorFactor':list(color),'metallicFactor':.18,'roughnessFactor':.4},'doubleSided':False})
   parts.append({'attributes':{'POSITION':self.buffer(P,5126,len(P),'VEC3',34962),'NORMAL':self.buffer(N,5126,len(N),'VEC3',34962)},'indices':self.buffer(I,5125,len(I),'SCALAR',34963),'material':self.colors[color]})
  idx=len(self.d['meshes']);self.d['meshes'].append({'primitives':parts});return idx
 def save(self,path):
  while len(self.binary)%4:self.binary.append(0)
  self.d['buffers']=[{'byteLength':len(self.binary)}];j=json.dumps(self.d,separators=(',',':')).encode();j+=b' '*((-len(j))%4);total=12+8+len(j)+8+len(self.binary);path.write_bytes(struct.pack('<III',0x46546c67,2,total)+struct.pack('<II',len(j),0x4E4F534A)+j+struct.pack('<II',len(self.binary),0x004E4942)+self.binary)
configs=[('kuka','KUKA KR 210 L150','kuka_kr210_support/urdf/kr210l150.urdf','kuka-kr210-l150'),('abb','ABB IRB 4600-40/2.55','abb_irb4600_support/urdf/irb4600_40_255_macro.xacro','abb-irb4600-40-255')]
for brand,label,urdf,slug in configs:
 base=ROOT/'source'/brand;r=ET.parse(base/urdf).getroot();clean=lambda n:n.replace('${prefix}','');links=[e for e in r.iter('link') if e.find('visual/geometry/mesh') is not None];joints=[e for e in r.iter('joint') if e.get('type')=='revolute'];data={'id':slug,'name':label,'source':'https://github.com/ros-industrial/'+('kuka_experimental' if brand=='kuka' else 'abb'),'joints':[],'tcpOffset':.16};glb=GLB();glb.d['nodes'][0]['name']=slug
 linknodes={};triangles=0
 for link in links:
  visual=link.find('visual');origin=visual.find('origin');angles=nums(origin.get('rpy')) if origin is not None else [0,0,0];shift=nums(origin.get('xyz')) if origin is not None else [0,0,0];vmat=rpy(angles);meshpath=visual.find('geometry/mesh').get('filename').replace('package://','');prims=[]
  for P,N,c in dae(base/meshpath):P=P@vmat.T+shift;N=N@vmat.T;prims.append((P,N,c));triangles+=len(P)//3
  allP=np.concatenate([p for p,n,c in prims]);print(label,clean(link.get('name')),'bounds',np.round(allP.min(axis=0),3),np.round(allP.max(axis=0),3))
  name=clean(link.get('name'));idx=len(glb.d['nodes']);linknodes[name]=idx;glb.d['nodes'].append({'name':name,'mesh':glb.mesh(prims),'children':[]})
 for joint in joints:
  origin=joint.find('origin');xyz=nums(origin.get('xyz'));axis=nums(joint.find('axis').get('xyz'));limit=joint.find('limit');parent=clean(joint.find('parent').get('link'));child=clean(joint.find('child').get('link'));name=clean(joint.get('name'));idx=len(glb.d['nodes']);glb.d['nodes'].append({'name':name,'translation':xyz,'children':[linknodes[child]]});glb.d['nodes'][linknodes[parent]]['children'].append(idx);data['joints'].append({'name':name,'origin':xyz,'axis':axis,'lower':scalar(limit.get('lower')),'upper':scalar(limit.get('upper')),'velocity':scalar(limit.get('velocity'))})
 glb.save(OUT/(slug+'.glb'));data['triangles']=triangles;data['sizeBytes']=(OUT/(slug+'.glb')).stat().st_size;(OUT/(slug+'.json')).write_text(json.dumps(data,indent=2));print('Saved',slug,'triangles',triangles,'bytes',data['sizeBytes'])
