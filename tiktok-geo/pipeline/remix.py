import re, subprocess, numpy as np, soundfile as sf, pyloudnorm as pyln
SR=48000; DUR=75.5; N=int(DUR*SR)
def load(p):
    raw=subprocess.run(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac','2','-ar',str(SR),'-'],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()
meter=pyln.Meter(SR)
def norm(x,lufs): return pyln.normalize.loudness(x,meter.integrated_loudness(x),lufs)
html=open('index.html').read()
voice=norm(load('assets/voice.mp3'),-16.0)
music=norm(load('assets/music.wav'),-16.0)
out=np.zeros((N,2),np.float32)
v=voice[:N]; out[:len(v)]+=v
# music bed ~17 dB under the voice, ducked a further 4 dB while speech is present
env=np.abs(voice[:,0]); k=int(0.25*SR)
env=np.convolve(env,np.ones(k)/k,'same'); speech=np.zeros(N); speech[:len(env)]=(env>0.01)
sm=np.convolve(speech,np.ones(int(0.3*SR))/int(0.3*SR),'same')
mg=10**(-17/20)*(1-0.37*sm)
m=music[:N]; out[:len(m)]+=m*mg[:len(m),None]
fade=int(2*SR); out[N-fade:]*=np.linspace(1,0,fade)[:,None]**0  # music fades handled below
mm=np.zeros((N,2),np.float32)
# sfx: original per-clip volume x 0.22 (about -13 dB)
for m_ in re.finditer(r'<audio id="sfx\d+" class="clip" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)"(?: data-media-start="([\d.]+)")?[^>]*data-volume="([\d.]+)"',html):
    src,st,du,ms,vol=m_.groups(); st=float(st); du=float(du); ms=float(ms or 0); vol=float(vol)
    x=load(src)[int(ms*SR):int((ms+du)*SR)]
    f=min(len(x),int(0.05*SR)); 
    if f: x[-f:]*=np.linspace(1,0,f)[:,None]
    i=int(st*SR); j=min(N,i+len(x)); out[i:j]+=x[:j-i]*vol*0.12
fo=int(1.5*SR); out[-fo:]*=np.linspace(1,0,fo)[:,None]
out=norm(out,-14.0)
pk=np.abs(out).max()
if pk>0.84: out*=0.84/pk
sf.write('/tmp/claude-0/work/mix.wav',out,SR)
print('voice LUFS', meter.integrated_loudness(voice), 'peak', pk)
