from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json,hashlib
root=Path('/Users/evilius/Documents/GitHub/agents-agenticrag/artifacts/phase-7/7b')
out=root/'image-review';out.mkdir(exist_ok=True)
manifest=[]
for engine in ['chromium','webkit']:
 for width in ['390','1440']:
  for theme in ['light','dark']:
   files=sorted(p for p in root.rglob('*.png') if f'{width}-{theme}-{engine}' in p.name)
   assert len(files)==13,(engine,width,theme,len(files))
   for batch in range(4):
    current=files[batch*4:batch*4+4]
    if not current: continue
    canvas=Image.new('RGB',(1400,1800),(238,238,238));draw=ImageDraw.Draw(canvas)
    for i,file in enumerate(current):
     x=(i%2)*700;y=(i//2)*900
     draw.text((x+12,y+8),file.name,fill=(0,0,0))
     image=Image.open(file).convert('RGB');image.thumbnail((680,860))
     canvas.paste(image,(x+10+(680-image.width)//2,y+30))
     manifest.append({'path':str(file.relative_to(root)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    canvas.save(out/f'fake-review-{width}-{theme}-{engine}-{batch}.jpg',quality=88)
(out/'manifest.json').write_text(json.dumps({'synthetic_only':True,'images':manifest,'capture_source':'Full frozen browser invocation against isolated fake server; no production data.'},indent=2)+'\n')
print(len(manifest),'synthetic captures grouped into 32 contact sheets')
