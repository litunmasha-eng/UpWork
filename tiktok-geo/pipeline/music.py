import numpy as np, soundfile as sf
from scipy import signal
SR=44100; BPM=120; BEAT=60/BPM; BAR=4*BEAT; DUR=76.0
N=int(DUR*SR); L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def t(n): return np.arange(n)/SR
def add(buf,x,at,gain=1.0):
    i=int(at*SR); j=min(N,i+len(x))
    if i<N: buf[i:j]+=gain*x[:j-i]
def addst(x,at,g=1.0,pan=0.0):
    add(L,x,at,g*(1-pan)*0.5**0.5*1.41/1.41); add(R,x,at,g*(1+pan)*0.5**0.5*1.41/1.41)
def lp(x,fc,o=2): return signal.sosfilt(signal.butter(o,fc,'low',fs=SR,output='sos'),x)
def hp(x,fc,o=2): return signal.sosfilt(signal.butter(o,fc,'high',fs=SR,output='sos'),x)
def bp(x,f1,f2): return signal.sosfilt(signal.butter(2,[f1,f2],'band',fs=SR,output='sos'),x)
def saw(f,n,det=0.0):
    ph=np.cumsum(np.full(n,f*(1+det))/SR); return 2*(ph%1)-1
def note(m): return 440*2**((m-69)/12)
# --- instruments
def kick():
    n=int(0.42*SR); tt=t(n)
    f=45+95*np.exp(-tt*28); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-tt*7.5)
    x=np.tanh(2.2*x)*0.9
    click=hp(rng.standard_normal(n),3000)*np.exp(-tt*300)*0.25
    return x+click
def clap():
    n=int(0.3*SR); tt=t(n); nz=rng.standard_normal(n)
    env=np.zeros(n)
    for k,o in enumerate([0,0.011,0.022]): env+=np.where(tt>=o,np.exp(-(tt-o)*(160 if k<2 else 22)),0)
    return bp(nz,900,5000)*env*0.55
def hat(open_=False):
    n=int((0.22 if open_ else 0.06)*SR); tt=t(n)
    return hp(rng.standard_normal(n),7000,4)*np.exp(-tt*(18 if open_ else 90))*0.28
def pluck(m,dur=0.22,bright=3500):
    n=int(dur*SR*1.8); tt=t(n); f=note(m)
    x=0.5*saw(f,n,0.003)+0.5*saw(f,n,-0.003)+0.3*np.sign(np.sin(2*np.pi*f*tt))
    x=lp(x,bright)*np.exp(-tt*11)
    return x*0.22
def bass(m,dur):
    n=int(dur*SR); tt=t(n); f=note(m)
    x=0.6*saw(f,n)+0.6*np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*f/2*tt)
    x=lp(x,650)*np.minimum(1,tt*200)*np.exp(-tt*2.2)
    return np.tanh(1.4*x)*0.42
def pad(ms,dur,fc=1800):
    n=int(dur*SR); tt=t(n); x=np.zeros(n)
    for m in ms:
        for d in (-0.007,0,0.006): x+=saw(note(m),n,d)
    x=lp(x/len(ms)/3,fc)
    env=np.minimum(1,tt/0.25)*np.minimum(1,(dur-tt)/0.3)
    return x*env*0.20
def riser(dur):
    n=int(dur*SR); tt=t(n); nz=rng.standard_normal(n)
    out=np.zeros(n); B=2048
    for i in range(0,n,B):
        fc=300+9000*(i/n)**2; out[i:i+B]=bp(nz[i:i+B+1][:len(out[i:i+B])],max(200,fc*0.6),min(18000,fc*1.4))
    return out*(tt/dur)**2*0.35
# chords: Am F C G (midi roots) ; arp tones
prog=[(57,[57,60,64]),(53,[53,57,60]),(48,[48,52,55]),(55,[55,59,62])]
arp_pat=[0,1,2,1, 2,1,0,2, 0,1,2,3, 2,1,0,1]
nb=int(np.ceil(DUR/BAR))
sc=np.ones(N)  # sidechain envelope from kicks
def section(b):
    tt=b*BAR
    if tt<14: return 'A'
    if tt<16: return 'SCI'
    if tt<52: return 'A2'
    if tt<56: return 'BRK'
    if tt<68: return 'A3'
    if tt<72: return 'BUILD'
    return 'OUT'
for b in range(nb):
    t0=b*BAR; s=section(b); root,ch=prog[b%4]
    kicks = s in ('A','A2','A3','OUT')
    for q in range(4):
        tq=t0+q*BEAT
        if kicks:
            addst(kick(),tq,0.95)
            i=int(tq*SR); m=int(0.28*SR); e=1-0.65*np.exp(-np.arange(m)/SR*9)
            j=min(N,i+m); sc[i:j]=np.minimum(sc[i:j],e[:j-i])
        if s in ('A2','A3','OUT') and q in (1,3): addst(clap(),tq,0.8)
        if s!='BRK':
            addst(hat(),tq+BEAT/2,0.9,0.3)
            if s in ('A2','A3','OUT'):
                addst(hat(),tq+BEAT/4,0.45,-0.3); addst(hat(),tq+3*BEAT/4,0.45,-0.3)
    # bass: offbeat 8ths
    if s=='BRK':
        addst(bass(root-12,BAR*0.95),t0,1.0)
    elif s=='SCI':
        pass
    else:
        for e in range(8):
            if e%2==1 or s in ('A3','BUILD'):
                addst(bass(root-12+(12 if (s=='A3' and e==7) else 0),BEAT/2*0.9),t0+e*BEAT/2,1.0)
    # arp 16ths
    if s not in ('BRK',):
        tones=ch+[ch[0]+12]
        for k in range(16):
            m=tones[arp_pat[k]]+12
            br=2200 if s=='SCI' else (4200 if s in ('A3','OUT') else 3400)
            g=0.8 if s!='SCI' else 0.5
            x=pluck(m,0.16,br); pan=0.35*np.sin(k*1.3)
            addst(x,t0+k*BEAT/4,g,pan)
            addst(lp(x,2000)*0.35,t0+k*BEAT/4+0.375,1.0,-pan)  # dotted-8th echo
    # pad
    fc={'BRK':900,'SCI':700,'BUILD':1400}.get(s,1700)
    addst(pad([m+12 for m in ch],BAR,fc),t0,1.1 if s=='BRK' else 0.8)
# build snare roll + riser
for k in range(32):
    tq=68+k*(4/32)
    if tq<71.4: addst(clap()*0.5,tq,0.25+0.6*k/32)
r=riser(3.4); addst(r,68.0,0.8)
# final hit at 72
addst(kick(),72.0,1.2)
# sci-fi tape-stop-ish swell
sw=riser(1.2)[::-1]; addst(sw,14.6,0.6)
# apply sidechain to everything except kicks? approximate: duck whole mix mildly, kicks already summed (minor)
L*=0.55+0.45*sc; R*=0.55+0.45*sc
mix=np.stack([L,R],1)
# master: gentle glue
mix=np.tanh(mix*1.1)
# fades
fi=int(0.03*SR); mix[:fi]*=np.linspace(0,1,fi)[:,None]
fo=int(2.5*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]**1.5
import pyloudnorm as pyln
meter=pyln.Meter(SR); lu=meter.integrated_loudness(mix); mix=pyln.normalize.loudness(mix,lu,-15.0)
pk=np.abs(mix).max()
if pk>0.89: mix*=0.89/pk
sf.write('/tmp/claude-0/work/proj/assets/music.wav',mix,SR)
print('LUFS before',lu,'peak',pk)
