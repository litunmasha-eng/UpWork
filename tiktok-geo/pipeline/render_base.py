import math, json, numpy as np
from PIL import Image, ImageDraw, ImageFilter
T='/tmp/claude-0/work/tiles/'; NE='/tmp/claude-0/work/ne/'; OUT='/tmp/claude-0/work/proj/assets/'
import os; os.makedirs(OUT,exist_ok=True)
def xy(lon,lat,z):
    n=2**z; x=(lon+180)/360*n
    y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x,y
def mosaic(z,box):
    lo0,la1,lo1,la0=box
    x0,y0=xy(lo0,la1,z); x1,y1=xy(lo1,la0,z)
    tx0,ty0,tx1,ty1=int(x0),int(y0),int(x1),int(y1)
    W=(tx1-tx0+1)*256; H=(ty1-ty0+1)*256
    E=np.zeros((H,W),np.float32)
    for tx in range(tx0,tx1+1):
        for ty in range(ty0,ty1+1):
            a=np.asarray(Image.open(f'{T}{z}_{tx}_{ty}.png').convert('RGB')).astype(np.float32)
            E[(ty-ty0)*256:(ty-ty0+1)*256,(tx-tx0)*256:(tx-tx0+1)*256]=a[...,0]*256+a[...,1]+a[...,2]/256-32768
    return E,tx0*256,ty0*256
def polys(fn,bbox):
    g=json.load(open(NE+fn))
    out=[]
    for f in g['features']:
        geom=f['geometry']
        if geom is None: continue
        P=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for p in P:
            ring=p[0]
            lons=[c[0] for c in ring]; lats=[c[1] for c in ring]
            if max(lons)<bbox[0] or min(lons)>bbox[2] or max(lats)<bbox[3] or min(lats)>bbox[1]: continue
            out.append(p)
    return out
def mask(z,ox,oy,W,H,box):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    def pts(ring): 
        r=[]
        for lon,lat in ring:
            lat=max(min(lat,85),-85); x,y=xy(lon,lat,z); r.append((x*256-ox,y*256-oy))
        return r
    for p in polys('ne_10m_land.geojson',box)+polys('ne_10m_minor_islands.geojson',box):
        d.polygon(pts(p[0]),fill=255)
        for h in p[1:]: d.polygon(pts(h),fill=0)
    lk=Image.new('L',(W,H),0); dl=ImageDraw.Draw(lk)
    for p in polys('ne_10m_lakes.geojson',box): dl.polygon(pts(p[0]),fill=255)
    return np.asarray(m)>127, np.asarray(lk)>127
def ramp(v,stops):
    xs=np.array([s[0] for s in stops],np.float32); cs=np.array([[int(s[1][i:i+2],16) for i in (1,3,5)] for s in stops],np.float32)
    return np.stack([np.interp(v,xs,cs[:,i]) for i in range(3)],-1)
SEA=[(-6000,'#06152a'),(-3000,'#081b34'),(-1000,'#0c2643'),(-500,'#103052'),(-250,'#163c62'),(-120,'#1c4a72'),(-60,'#22567f'),(-25,'#29648c'),(0,'#2f7096')]
LAND=[(0,'#5f6f55'),(150,'#6c7859'),(400,'#7f8262'),(800,'#918a6d'),(1500,'#a59d86'),(2500,'#c4bfb3'),(3500,'#e9e7e1')]
def shade(E,z,oy,zf):
    H,W=E.shape
    lat_rows=np.array([math.degrees(math.atan(math.sinh(math.pi*(1-2*(oy+i)/(256*2**z))))) for i in range(H)],np.float32)
    px=156543.03*np.cos(np.radians(lat_rows))/2**z
    gy,gx=np.gradient(E)
    gx=gx/px[:,None]*zf; gy=gy/px[:,None]*zf
    out=np.zeros_like(E)
    for az,alt,w in [(315,45,0.6),(270,50,0.2),(0,50,0.2)]:
        a=math.radians(az); al=math.radians(alt)
        slope=np.arctan(np.hypot(gx,gy)); aspect=np.arctan2(-gx,gy)
        hs=np.sin(al)*np.cos(slope)+np.cos(al)*np.sin(slope)*np.cos(a-aspect-math.pi/2)
        out+=w*hs
    return np.clip(out,0,1)
def render(name,z,box,zf_land,zf_sea):
    E,ox,oy=mosaic(z,box); H,W=E.shape
    land,lake=mask(z,ox,oy,W,H,box)
    hsL=shade(np.where(land,np.maximum(E,0),0),z,oy,zf_land)
    hsS=shade(np.minimum(np.where(land,0,E),0),z,oy,zf_sea)
    sea=ramp(E,SEA); lc=ramp(np.maximum(E,0),LAND)
    f=0.62+0.62*(hsL-0.55)/0.45; f=np.clip(f,0.45,1.25)
    lc=lc*f[...,None]
    fs=np.clip(0.9+0.35*(hsS-0.7),0.75,1.1); sea=sea*fs[...,None]
    img=np.where(land[...,None],lc,sea)
    img=np.where((lake&land)[...,None],ramp(np.full_like(E,-20),SEA),img)
    img=np.clip(img,0,255).astype(np.uint8)
    Image.fromarray(img).save(OUT+name+'.jpg',quality=88)
    meta=dict(z=z,ox=ox,oy=oy,W=W,H=H,scale=2**(8-z))
    print(name,meta)
    if name=='detail':
        fl=(land&(E<1.2)&~lake).astype(np.uint8)*255
        Image.fromarray(fl).filter(ImageFilter.GaussianBlur(1.2)).save(OUT+'flood_mask.png')
    return meta
m={}
m['wide']=render('wide',6,(-40,74,48,26),2.2,1.2)
m['detail']=render('detail',8,(-9,64,13,46),1.6,0.9)
json.dump(m,open(OUT+'basemaps.json','w'))
