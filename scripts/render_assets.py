"""Render original, standalone animated artwork for Ayush's GitHub profile.

Requires Pillow and NumPy. GIF assets work in GitHub READMEs without scripting.
Run: python scripts/render_assets.py
"""
from __future__ import annotations
from pathlib import Path
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)
RANDOM = random.Random(1543)

FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

# Fallback font paths for regeneration on systems without the CI image's fonts.
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()

WHITE = (233,244,255,255)
ICE = (122,225,247,255)
LAV = (168,139,250,255)
MUTED = (151,169,199,255)


def background(w, h, seed=5):
    """Deep-space atmospheric gradient with soft multi-color nebulae."""
    yy, xx = np.mgrid[0:h,0:w].astype(np.float32)
    nx,ny=xx/w, yy/h
    col = np.empty((h,w,3), dtype=np.float32)
    col[:,:,0] = 5 + 6*nx
    col[:,:,1] = 10 + 9*nx + 2*ny
    col[:,:,2] = 24 + 21*nx + 4*ny
    for cx,cy,sx,sy,color,strength in [
       (.78,.49,.26,.52,(29,67,128),.88),
       (.93,.12,.28,.38,(106,41,154),.65),
       (.58,.90,.29,.32,(0,104,123),.32),
       (.17,.12,.28,.38,(24,37,91),.34),
    ]:
        g=np.exp(-(((nx-cx)/sx)**2+((ny-cy)/sy)**2)*1.7)*strength
        for k in range(3):col[:,:,k]+=color[k]*g
    # Darken border for editorial vignette.
    vig=np.clip((nx-.51)**2*0.35+(ny-.50)**2*.45,0,.35)
    col*=(1-vig[:,:,None])
    rng=np.random.default_rng(seed)
    col+=rng.normal(0,0.7,(h,w,1))
    a=np.full((h,w,1),255,np.uint8)
    return Image.fromarray(np.concatenate([np.uint8(np.clip(col,0,255)),a],axis=2),'RGBA')


def glow_dot(layer, x,y, r,color, strength=0.8):
    # Requires RGBA input, draw a blurred halo on its own transparent layer.
    halo=Image.new('RGBA', layer.size)
    d=ImageDraw.Draw(halo)
    rr=int(max(4,r*3))
    d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(*color,int(85*strength)))
    halo=halo.filter(ImageFilter.GaussianBlur(max(3,r*3)))
    layer.alpha_composite(halo)
    dr=ImageDraw.Draw(layer)
    dr.ellipse((x-r,y-r,x+r,y+r),fill=(*color,230))


def halo_ellipse(base, box, color, radius=9, alpha=75, width=2):
    ly=Image.new('RGBA',base.size)
    d=ImageDraw.Draw(ly)
    d.ellipse(box,outline=(*color,alpha),width=width)
    base.alpha_composite(ly.filter(ImageFilter.GaussianBlur(radius)))
    d=ImageDraw.Draw(base)
    d.ellipse(box,outline=(*color,170),width=width)

W,H=1200,394
bg=background(W,H)
base=bg.copy()
# Dim plotting grid on the right.
d=ImageDraw.Draw(base)
for gx in range(620,1200,38):
    d.line((gx,20,gx,H-20),fill=(86,120,171,15),width=1)
for gy in range(20,H-15,38):
    d.line((605,gy,W-25,gy),fill=(86,120,171,12),width=1)

# Frame and technical annotations.
d.rounded_rectangle((17,17,W-18,H-18),radius=19,outline=(79,116,174,95),width=1)
d.line((37,44,184,44), fill=(93,201,228,155), width=2)
d.line((1000,H-45,1164,H-45), fill=(149,105,230,110),width=2)
d.text((44,57),'INCOMING TRANSMISSION  //  001',font=font(FONT_MONO,15),fill=(115,217,238))
d.text((44,95),'AYUSH',font=font(FONT_BOLD,76),fill=(246,249,255))
d.text((39,170),'KHATRI',font=font(FONT_BOLD,77),fill=(240,247,255))
d.rounded_rectangle((47,270,345,308),radius=13,fill=(25,56,79,185),outline=(68,194,228,140),width=1)
d.text((63,280),'FULL-STACK DEVELOPER',font=font(FONT_MONO,15),fill=(154,231,247))
d.text((44,324),'From first pixel to production.',font=font(FONT_REG,19),fill=(177,198,221))
d.text((772,351),'SYSTEM : CREATIVE ENGINEERING',font=font(FONT_MONO,12),fill=(125,159,195))
# Minimal small squares and frequency ticks.
for i in range(16):
    x=440+i*17
    h=3+((i*13)%18)
    d.rectangle((x,286-h,x+6,286),fill=(83,183,211,75))

stars=[]
for i in range(116):
    x=RANDOM.randrange(25,W-25);y=RANDOM.randrange(20,H-24)
    if x<500 and 90<y<340:continue
    stars.append((x,y,RANDOM.choice((1,1,1,1,2)),RANDOM.random()*6.28,RANDOM.random()*.35+.32))

cx,cy=948,191
# Planet base, processed only once.
planet_base=Image.new('RGBA',(W,H))
planet_halo=Image.new('RGBA',(W,H))
ph=ImageDraw.Draw(planet_halo)
ph.ellipse((cx-133,cy-133,cx+133,cy+133),fill=(66,132,238,85))
planet_base.alpha_composite(planet_halo.filter(ImageFilter.GaussianBlur(31)))
# Generate transparent shaded planet disk vectorized.
r=91
py,px=np.mgrid[-r:r+1,-r:r+1].astype(float)
mask=(px*px+py*py)<=r*r
light=np.clip(.95-(px/r)*.42-(py/r)*.20,0,1)
term=np.clip((r-px)/r,0,1)
noise=np.sin(px*.065+py*.034)*.033+np.cos(py*.11)*.027
arr=np.zeros((2*r+1,2*r+1,4),np.uint8)
for i,cc in enumerate((40,98,184)):
    arr[:,:,i]=np.clip((cc+65*light-35*(1-term)+100*noise),0,255).astype('uint8')
arr[:,:,3]=np.where(mask,255,0).astype('uint8')
planet_base.alpha_composite(Image.fromarray(arr,'RGBA'),(cx-r,cy-r))
ImageDraw.Draw(planet_base).ellipse((cx-r,cy-r,cx+r,cy+r),outline=(107,200,246,130),width=2)

frames=[]
NUM=36
for f in range(NUM):
    img=base.copy()
    star=ImageDraw.Draw(img)
    for x,y,rr,p,q in stars:
        lum=int(65+145*(q+.3*math.sin(f/NUM*math.tau+p)))
        star.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(161,204,255,max(45,min(255,lum))))
    img.alpha_composite(planet_base)
    # Two dynamic orbit rings, plus orbital telemetry tracks.
    halo_ellipse(img,(cx-170,cy-46,cx+170,cy+46),(89,196,232),radius=6,alpha=68,width=2)
    halo_ellipse(img,(cx-141,cy-120,cx+141,cy+120),(132,112,228),radius=4,alpha=40,width=1)
    d=ImageDraw.Draw(img)
    # Shimmering orbital particles.
    theta=math.tau*f/NUM
    x1=cx+170*math.cos(theta)
    y1=cy+46*math.sin(theta)
    glow_dot(img,int(x1),int(y1),4,(125,236,250))
    theta2=math.tau*(f/NUM+.44)
    x2=cx+141*math.cos(theta2)
    y2=cy+120*math.sin(theta2)
    glow_dot(img,int(x2),int(y2),3,(183,147,255))
    # Scanning longitude across disk.
    scan_x=cx-r+(f/NUM)*(2*r)
    d=ImageDraw.Draw(img)
    chord=math.sqrt(max(0,r*r-(scan_x-cx)**2))
    if chord>4:
        d.line((scan_x,cy-chord,scan_x,cy+chord),fill=(158,234,255,85),width=2)
    # Animated shooting star; away from the title.
    sx=700+((f*19)%440); sy=65+((f*7)%75)
    d.line((sx-34,sy+16,sx,sy),fill=(106,183,250,105),width=2)
    d.ellipse((sx-2,sy-2,sx+2,sy+2),fill=(216,243,255,240))
    # Dynamic progress line and tiny status dot.
    d.rounded_rectangle((44,359,400,363),radius=2,fill=(45,67,91))
    d.rounded_rectangle((44,359,44+int(356*(.10+.90*(f+1)/NUM)),363),radius=2,fill=(86,209,236))
    d.ellipse((1133,54,1144,65),fill=(84,233,183) if f%9<7 else (51,99,87))
    d.text((1005,75),'SIGNAL  ACTIVE',font=font(FONT_MONO,12),fill=(141,222,226))
    frames.append(img.convert('RGB'))

# Quantize each frame using the same palette to avoid animated color shifts.
palette=frames[0].quantize(colors=210,method=Image.Quantize.MEDIANCUT)
qframes=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
qframes[0].save(ASSETS/'stellar-hero.gif', save_all=True,append_images=qframes[1:],duration=90,loop=0,optimize=True,disposal=2)
frames[0].save(ASSETS/'stellar-hero-preview.png',optimize=True)
print('hero:',(ASSETS/'stellar-hero.gif').stat().st_size)

# Compact auxiliary animation: radar waveform / system bus.
SW,SH=1200,132
b=background(SW,SH,9)
d=ImageDraw.Draw(b)
d.rounded_rectangle((2,2,1197,129),radius=14,outline=(84,130,202,125),width=1)
d.text((35,20),'ORBITAL / SIGNAL BUS',font=font(FONT_MONO,15),fill=(140,210,244))
d.text((35,48),'BUILD  /  TEST  /  SHIP  /  EVOLVE',font=font(FONT_BOLD,24),fill=(237,246,255))
d.text((36,96),'STATUS: CREATING BETTER DIGITAL EXPERIENCES',font=font(FONT_MONO,12),fill=(140,174,198))
for k in range(10):
    x=690+k*41
    d.line((x,20,x,113),fill=(73,108,158,38))
strip=[]
for f in range(32):
    im=b.copy();d=ImageDraw.Draw(im)
    pts=[]
    for x in range(690,1136,3):
        # Tuned like a clean oscilloscopic waveform.
        ramp=math.sin(math.pi*(x-690)/(1136-690))**2
        y=66+math.sin((x-690)*.058-f*.31)*23*ramp + math.sin((x-690)*.12+f*.2)*5*ramp
        pts.append((x,int(y)))
    d.line(pts,fill=(73,209,236,205),width=3,joint='curve')
    for j in range(7):
        xp=701+j*67
        yy=66+math.sin((xp-690)*.058-f*.31)*23*math.sin(math.pi*(xp-690)/(1136-690))**2
        d.ellipse((xp-3,yy-3,xp+3,yy+3),fill=(186,161,255,230))
    d.text((1100,22),f'{(f*7)%100:02d}',font=font(FONT_MONO,13),fill=(160,183,234))
    strip.append(im.convert('RGB'))
spal=strip[0].quantize(colors=195,method=Image.Quantize.MEDIANCUT)
sqs=[fr.quantize(palette=spal,dither=Image.Dither.NONE) for fr in strip]
sqs[0].save(ASSETS/'signal-bus.gif',save_all=True,append_images=sqs[1:],duration=90,loop=0,optimize=True,disposal=2)
print('bus:',(ASSETS/'signal-bus.gif').stat().st_size)
