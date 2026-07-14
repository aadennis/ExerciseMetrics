import pandas as pd, numpy as np, json
f1='data/260702 - Copy.csv'
f2='data/260704 - Copy.csv'
d1=pd.read_csv(f1)
d2=pd.read_csv(f2)
for d in (d1,d2):
 d['cadence_spm']=pd.to_numeric(d['cadence_spm'],errors='coerce')
 d['heart_rate']=pd.to_numeric(d['heart_rate'],errors='coerce')
 d['enhanced_speed']=pd.to_numeric(d['enhanced_speed'],errors='coerce')
 # moving only
 d.dropna(subset=['cadence_spm','heart_rate','enhanced_speed'],inplace=True)
 
# exclude standing
m1=d1[d1.cadence_spm>100]
m2=d2[d2.cadence_spm>100]
res={}
for name,m in [('260702',m1),('260704',m2)]:
 target=m[(m.heart_rate>=123)&(m.heart_rate<=127)]
 res[name]={
 'avg_cad':round(m.cadence_spm.mean(),1),
 'sd_cad':round(m.cadence_spm.std(),1),
 'avg_hr':round(m.heart_rate.mean(),1),
 'avg_speed':round(m.enhanced_speed.mean(),3),
 'target125_speed':round(target.enhanced_speed.mean(),3),
 'target125_cad':round(target.cadence_spm.mean(),1),
 'hr_start':round(m.head(len(m)//10).heart_rate.mean(),1),
 'hr_end':round(m.tail(len(m)//10).heart_rate.mean(),1),
 }
print(json.dumps(res,indent=2))
