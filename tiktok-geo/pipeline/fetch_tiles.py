import math, os, sys, concurrent.futures as cf, urllib.request
def xy(lon,lat,z):
    n=2**z; x=(lon+180)/360*n
    y=(1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n
    return x,y
def fetch(z,x,y):
    p=f'/tmp/claude-0/work/tiles/{z}_{x}_{y}.png'
    if os.path.exists(p): return
    for i in range(4):
        try:
            d=urllib.request.urlopen(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',timeout=30).read()
            open(p,'wb').write(d); return
        except Exception as e: err=e
    print('fail',z,x,y,err)
jobs=[]
for z,(lo0,la1,lo1,la0) in [(6,(-40,74,48,26)),(8,(-9,64,13,46))]:
    x0,y0=xy(lo0,la1,z); x1,y1=xy(lo1,la0,z)
    for x in range(int(x0),int(x1)+1):
        for y in range(int(y0),int(y1)+1): jobs.append((z,x,y))
print(len(jobs))
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(lambda j: fetch(*j), jobs))
