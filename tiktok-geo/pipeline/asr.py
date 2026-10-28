import sherpa_onnx, soundfile as sf, json, sys
d='/tmp/claude-0/work/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/'
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=d+'encoder.int8.onnx',decoder=d+'decoder.int8.onnx',joiner=d+'joiner.int8.onnx',tokens=d+'tokens.txt',model_type='nemo_transducer',num_threads=4)
x,sr=sf.read(sys.argv[1],dtype='float32')
# chunk at ~ 20 s on silences to stay in model limits
import numpy as np
out=[]
step=20*sr; i=0
bounds=[0,9.32,22.07,34.84,47.92,60.09,len(x)/sr]
for a,b in zip(bounds,bounds[1:]):
  s=r.create_stream(); s.accept_waveform(sr,x[int(a*sr):int(b*sr)]); r.decode_stream(s)
  res=s.result
  for t,ts in zip(res.tokens,res.timestamps): out.append([t,round(ts+a,3)])
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(''.join(t for t,_ in out))
