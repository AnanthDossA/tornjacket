import sys, math, subprocess; sys.path.insert(0,'/root/sg')
import numpy as np, skia, toon
from toon import Track
from chars import SHIRLEY, GABBY
W,H,FPS=1280,720,24; dt=1/FPS; END=5.0
S=toon.Character(SHIRLEY); G=toon.Character(GABBY)
GX=Track([(0,-150),(1.6,700,"out")]); SX=Track([(0.4,-300),(2.4,380,"out")])
GG=Track([(0,0),(2.3,0),(2.55,1,"back"),(3.6,1),(3.9,0)])
SG=Track([(0,0),(2.7,0),(3.0,1,"back")])
GE=Track([(0,"happy"),(1.7,"panic"),(3.9,"starstruck")]); SE=Track([(0,"neutral"),(2.6,"deadpan"),(4.0,"annoyed")])
GF=Track([(0,1.0),(1.75,1.0),(1.95,-0.8,"snap")])
st={"G":0.0,"S":1.2}; prev={"G":GX(0),"S":SX(0)}
arr=np.zeros((H,W,4),np.uint8); cv=skia.Surface(arr).getCanvas()
ff=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-crf","20","-pix_fmt","yuv420p","out/02_motion_test.mp4"],stdin=subprocess.PIPE)
for f in range(int(END*FPS)):
    t=f*dt; cv.clear(toon.C((236,226,204))); cv.drawRect(skia.Rect.MakeLTRB(0,600,W,H),toon.fillp((214,200,176)))
    cv.save(); cv.scale(0.8,0.8)
    for key,ch,xt,gest,gname,et,ft in (("S",S,SX,SG,"arms_crossed",SE,lambda t:0.85),("G",G,GX,GG,"point_back",GE,GF)):
        x=xt(t); dx=x-prev[key]; prev[key]=x; st[key]+=abs(dx)/(170 if key=="G" else 190)*2*math.pi
        w=min(1,abs(dx)*FPS/160); p=toon.blend(toon.pose_idle(t),toon.pose_walk(st[key]),w); p=toon.apply_gesture(p,gname,gest,t)
        ch.update(t,x,dt,p,ft(t),et(t))
        ch.draw(cv,x,860 if key=="S" else 880,1.0,p,ft(t),{"expr":et(t),"blink":ch.blink(t),"look":(1,0)})
    cv.restore(); ff.stdin.write(arr.tobytes())
ff.stdin.close(); ff.wait()
