from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parent
delivery=ROOT/'delivery'
cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-framerate','24','-start_number','1','-i',str(ROOT/'frames'/'frame_%04d.png'),'-i',str(delivery/'sound-design.wav')]
for i in range(1,5):cmd+=['-loop','1','-framerate','24','-i',str(ROOT/'previews'/f'overlay_{i}.png')]
times=[(0,3),(3,7.75),(7.75,11),(11,15)]
filters=[]
for i,(a,b) in enumerate(times):
 src='0:v' if i==0 else f'v{i}'
 filters.append(f"[{src}][{i+2}:v]overlay=enable='gte(t,{a})*lt(t,{b})':shortest=1[v{i+1}]")
filters.append('[v4]fade=t=in:st=0:d=0.25,fade=t=out:st=14.65:d=0.35,format=yuv420p[final]')
cmd+=['-filter_complex',';'.join(filters),'-map','[final]','-map','1:a','-c:v','libx264','-preset','slow','-crf','18','-c:a','aac','-b:a','160k','-t','15','-movflags','+faststart',str(delivery/'Vision_Flow_15s.mp4')]
subprocess.run(cmd,check=True)
probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,r_frame_rate','-of','json',str(delivery/'Vision_Flow_15s.mp4')],text=True)
(delivery/'视频验证.json').write_text(probe)
print(probe)
