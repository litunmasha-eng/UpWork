import json, math, numpy as np
NE='/tmp/claude-0/work/ne/'; OUT='/tmp/claude-0/work/proj/assets/geo.json'
OX,OY=24576,12288
def P(lon,lat):
    n=2**8*256; x=(lon+180)/360*n
    lat=max(min(lat,85),-85)
    y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x-OX,y-OY
def rdp(pts,eps):
    pts=np.asarray(pts)
    if len(pts)<3: return pts
    keep=np.zeros(len(pts),bool); keep[0]=keep[-1]=True
    st=[(0,len(pts)-1)]
    while st:
        a,b=st.pop()
        if b<=a+1: continue
        A,B=pts[a],pts[b]; seg=pts[a+1:b]
        d=B-A; L=np.hypot(*d)
        dist=np.abs(d[0]*(seg[:,1]-A[1])-d[1]*(seg[:,0]-A[0]))/L if L>0 else np.hypot(*(seg-A).T)
        i=int(np.argmax(dist))
        if dist[i]>eps: keep[a+1+i]=True; st+= [(a,a+1+i),(a+1+i,b)]
    return pts[keep]
def inb(ring,b):
    lo=[c[0] for c in ring]; la=[c[1] for c in ring]
    return not(max(lo)<b[0] or min(lo)>b[2] or max(la)<b[1] or min(la)>b[3])
def path(rings,eps,closed=True,minlen=3):
    s=[]
    for r in rings:
        p=rdp([P(*c[:2]) for c in r],eps)
        if len(p)<minlen: continue
        s.append('M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in p)+('Z' if closed else ''))
    return ''.join(s)
def polyrings(geom,b,holes=True):
    P_=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    out=[]
    for p in P_:
        if inb(p[0],b): out+= p if holes else [p[0]]
    return out
B=(-14,44,20,66)
geo={}
# coastline
g=json.load(open(NE+'ne_10m_coastline.geojson'))
rings=[]
for f in g['features']:
    gm=f['geometry']; L=gm['coordinates'] if gm['type']=='MultiLineString' else [gm['coordinates']]
    for l in L:
        if inb(l,B): rings.append(l)
geo['coast']=path(rings,1.6,False,4)
# north sea
g=json.load(open(NE+'ne_10m_geography_marine_polys.geojson'))
rings=[]
for f in g['features']:
    if f['properties']['name'] in ('North Sea','English Channel','Skagerrak','Kattegat','Waddenzee'):
        rings+=polyrings(f['geometry'],(-180,-90,180,90),False)
geo['northsea']=path(rings,1.5)
# countries
g=json.load(open(NE+'ne_10m_admin_0_countries.geojson'))
CB=(-11,41,32,72)
geo['countries']={}
for f in g['features']:
    a=f['properties']['ADM0_A3']
    if a in ('GBR','NOR','DNK','DEU','NLD','BEL','FRA'):
        rings=polyrings(f['geometry'],CB)
        rings=[r for r in rings if CB[0]<np.mean([c[0] for c in r])<CB[2] and CB[1]<np.mean([c[1] for c in r])<CB[3]]
        geo['countries'][a]=path(rings,2.0)
# rivers, oriented toward mouth
mouths={'Rhein':(4.1,51.95),'Elbe':(8.8,53.9),'Thames':(0.9,51.5)}
names={'Rhein':('Rhein','Rhine','Rhin','Waal'),'Elbe':('Elbe',),'Thames':('Thames',)}
geo['rivers']={}
for fn in ['ne_10m_rivers_lake_centerlines.geojson']:
    g=json.load(open(NE+fn))
    for k,ns in names.items():
        segs=[]
        for f in g['features']:
            p=f['properties']
            if p.get('name') in ns or p.get('name_en') in ns:
                gm=f['geometry']; L=gm['coordinates'] if gm['type']=='MultiLineString' else [gm['coordinates']]
                for l in L:
                    m=mouths[k]
                    d0=math.hypot(l[0][0]-m[0],l[0][1]-m[1]); d1=math.hypot(l[-1][0]-m[0],l[-1][1]-m[1])
                    if d0<d1: l=l[::-1]
                    segs.append(l)
        geo['rivers'][k]=path(segs,1.2,False,2)
# extra European river network for glow (other big rivers flowing into north sea)
json.dump(geo,open(OUT,'w'))
print({k:(len(v) if isinstance(v,str) else {kk:len(vv) for kk,vv in v.items()}) for k,v in geo.items()})
