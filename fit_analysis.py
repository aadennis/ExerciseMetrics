import pandas as pd, json
f='data/output/23567118490_ACTIVITY-fit.csv'
d=pd.read_csv(f)
d['cadence_spm']=pd.to_numeric(d['cadence_spm'],errors='coerce')
d['heart_rate']=pd.to_numeric(d['heart_rate'],errors='coerce')
d['enhanced_speed']=pd.to_numeric(d['enhanced_speed'],errors='coerce')
 # moving only
d.dropna(subset=['cadence_spm','heart_rate','enhanced_speed'],inplace=True)
 
# exclude standing
m=d[d.cadence_spm>100]

target=m[(m.heart_rate>=123)&(m.heart_rate<=127)]
res={
 'avg_cad':round(m.cadence_spm.mean(),1),
 'sd_cad':round(m.cadence_spm.std(),1),
 'avg_hr':round(m.heart_rate.mean(),1),
 'avg_speed':round(m.enhanced_speed.mean(),3),
 'target125_speed':round(target.enhanced_speed.mean(),3),
 'target125_cad':round(target.cadence_spm.mean(),1),
 'hr_start':round(m.head(len(m)//10).heart_rate.mean(),1),
 'hr_end':round(m.tail(len(m)//10).heart_rate.mean(),1),
 }
print(f"stats results from [{f}]")
print(json.dumps(res,indent=2))
