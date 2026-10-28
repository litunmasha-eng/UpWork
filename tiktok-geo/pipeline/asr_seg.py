import sherpa_onnx, soundfile as sf, sys
d='/tmp/claude-0/work/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8/'
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=d+'encoder.int8.onnx',decoder=d+'decoder.int8.onnx',joiner=d+'joiner.int8.onnx',tokens=d+'tokens.txt',model_type='nemo_transducer',num_threads=4)
x,sr=sf.read(sys.argv[1],dtype='float32')
for seg in sys.argv[2:]:
  a,b=map(float,seg.split('-'))
  s=r.create_stream(); s.accept_waveform(sr,x[int(a*sr):int(b*sr)]); r.decode_stream(s)
  print(seg, s.result.text, [ (t,round(ts+a,2)) for t,ts in zip(s.result.tokens,s.result.timestamps)][:40])
