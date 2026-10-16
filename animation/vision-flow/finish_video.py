from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import wave

ROOT=Path(__file__).resolve().parent
W,H=1280,720
font='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def f(n,b=False):return ImageFont.truetype(bold if b else font,n)
stages=[('01','三维感知','3D VISION','扫描货垛，识别箱体表面与抓取位置'),('02','视觉引导抓取','GUIDED PICKING','机械臂吸附、抬升，将纸箱放入出料输送线'),('03','输送与交接','MATERIAL TRANSFER','纸箱到达出口，AGV 滚筒对齐接货'),('04','自主运输','AUTONOMOUS TRANSPORT','AGV 携货离站，完成从感知到搬运的协作')]
for idx,(number,title,en,sub) in enumerate(stages):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 for y in range(H):
  a=int(100*max(0,1-y/145)) if y<145 else int(165*max(0,(y-(H-185))/185))
  if a:d.line((0,y,W,y),fill=(8,26,34,a))
 d.rectangle((48,36,53,71),fill=(59,228,210,255));d.text((68,35),'VISION FLOW',font=f(29,True),fill='white')
 d.text((69,73),'INDUSTRIAL VISION  /  CONCEPT FILM',font=f(10,True),fill=(214,232,231,255))
 d.text((W-235,46),'概念动画 · 模拟数据',font=f(16),fill=(235,245,241,255))
 d.text((48,H-129),number+' / '+en,font=f(12,True),fill=(92,233,218,255))
 d.text((48,H-105),title,font=f(30),fill='white')
 d.text((48,H-57),sub,font=f(18),fill=(222,235,233,255))
 d.text((W-180,H-52),'CELL 01  /  15 SEC',font=f(11,True),fill=(210,231,227,255))
 im.save(ROOT/'previews'/f'overlay_{idx+1}.png')

# Original, synthesized sound design: low motor tone, servo motion and scan cue.
rate=48000;duration=15;t=np.arange(rate*duration)/rate
sound=np.zeros(len(t));rng=np.random.default_rng(42)
noise=rng.normal(0,1,len(t))
def envelope(start,end):
 u=np.clip((t-start)/max(.01,end-start),0,1);return np.where((t>=start)&(t<=end),np.sin(np.pi*u)**.75,0)
sound+=.018*np.sin(2*np.pi*85*t)*np.minimum(1,t)*np.minimum(1,(15-t))
for a,b,hz in [(3,4.5,180),(4.8,7.6,145),(7.8,10.4,110),(11,14.9,125)]:
 env=envelope(a,b);sound+=env*(.04*np.sin(2*np.pi*(hz*t+10*np.sin(t*1.3)))+.012*np.sin(2*np.pi*hz*2*t)+.006*noise)
for start in [1.0,1.6,2.3]:
 u=t-start;env=np.where((u>=0)&(u<.18),np.exp(-np.maximum(u,0)*25),0);sound+=.055*np.sin(2*np.pi*960*t)*env
for start in [4.45,7.7,10.5]:
 u=t-start;env=np.where((u>=0)&(u<.12),np.exp(-np.maximum(u,0)*45),0);sound+=.05*noise*env
sound=np.clip(sound,-.8,.8)
with wave.open(str(ROOT/'delivery'/'sound-design.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);stereo=np.column_stack([sound,sound*.93]);w.writeframes((stereo*32767).astype('<i2').tobytes())
print('字幕图层与原创合成音效已生成')
