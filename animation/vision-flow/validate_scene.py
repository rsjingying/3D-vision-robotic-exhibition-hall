import bpy,json,os
ROOT=os.path.dirname(os.path.abspath(__file__))
s=bpy.context.scene
payload=bpy.data.objects['Carton / 11']
grip=bpy.data.objects['Robot / vacuum end effector']
agv=bpy.data.objects['05 / Roller-top AGV']
checks=[]
for f in [110,116,134,160,186]:
 s.frame_set(f);error=abs((grip.location.z-.12)-(payload.location.z+.24));checks.append({'frame':f,'check':'cup to carton-top contact','error_m':round(error,5),'passed':error<.003})
for f in [192,205,225]:
 s.frame_set(f);error=abs(payload.location.z-.24-1.085);checks.append({'frame':f,'check':'carton bottom on outfeed','error_m':round(error,5),'passed':error<.003})
for f in [264,310,360]:
 s.frame_set(f);delta=payload.location-agv.location;checks.append({'frame':f,'check':'load follows AGV','relative':list(delta),'passed':abs(delta.x)<.001 and abs(delta.y)<.001 and abs(delta.z-1.325)<.001})
checks.append({'check':'four edited shots','passed':len([m for m in s.timeline_markers if m.camera])==4})
checks.append({'check':'720p / 24fps / 360 frames','passed':s.render.resolution_x==1280 and s.render.resolution_y==720 and s.render.fps==24 and s.frame_end==360})
path=os.path.join(ROOT,'delivery','场景检查.json')
with open(path,'w') as f:json.dump(checks,f,ensure_ascii=False,indent=2)
print('SCENE CHECKS:',sum(c['passed'] for c in checks),'/',len(checks))
assert all(c['passed'] for c in checks),checks
