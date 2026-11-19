from pathlib import Path
import pandas as pd,json,shutil,zipfile
P=Path(__file__).resolve().parent;O=P/'out';T=pd.read_csv(O/'cross_statistics_all_scenarios.csv');a=json.loads((O/'audit.json').read_text())
names={1:'每公里1个交通雷达电子部件',2:'每公里3个雷达电子部件与1个基础气象节点的功率预算',3:'每公里1个雷达电子部件与1个间歇加热气象节点的功率预算',4:'每公里1个较高加热占空比气象节点的功率预算',5:'每公里1盏路灯',6:'图4g中5盏灯配置的既定功率预算',7:'每公里20盏路灯'}
def view(group,traffic='median',iso='A'):
 return T[(T.traffic==traffic)&(T.ISO==iso)&(T.nightlight_group==group)].copy()
s=view('whole_record_no_positive');s['设施配置']=s.load_level.map(names)
s.to_csv(O/'SI_Table_X_strict_dark_ISO_A.csv',index=False,encoding='utf-8-sig')
lines=['# SI补充说明：夜光筛查与采能年度供需达标的交叉统计（2026-11-18）','','## 研究范围与定义','',f"研究输入为{a['records']:,}条道路记录，总长{a['road_length_km']:,.3f} km，属既有交通清单中的城外高速公路、一级和二级道路。交通基准为2015年，夜光缓存对应2021年masked VIIRS产品。该范围不是全部全球道路，也不是完整的未铺装道路清单。",'',f"主统计选择整条记录的正夜光采样比例为0且栅格范围外采样比例为0的道路，共{a['group_nonzero_record_counts']['whole_record_no_positive']:,}条、{a['group_totals_km']['whole_record_no_positive']:,.3f} km，占研究道路总长度的{100*a['group_totals_km']['whole_record_no_positive']/a['road_length_km']:.2f}%。将其称为‘沿线采样均未检出正夜光的路段’，不直接判定为缺电、照明不足或有必要新装路灯。混合明暗记录不进入这一主分组。",'',f"敏感性分组包括：正夜光比例≤10%的整条记录（{a['group_totals_km']['whole_record_positive_le10pct']:,.3f} km）；正夜光比例≥90%的记录；全部采样均为正夜光的记录；以及按采样比例折算的正夜光与无正夜光等效路长。栅格范围外部分约{a['outside_raster_km']:.3f} km不计入无正夜光等效路长。无正夜光等效路长合计{a['nonpositive_in_bounds_km']:,.3f} km，其中包含混合记录的无正夜光份额。该数字与严格整条记录分组分母不同。",'','夜光仅用于空间筛查，不用于计算用电量。masked产品的零值不等同于经过现场核实的未照明状态，低亮度灯具、植被/建筑遮挡、采样与像元分辨率均可能影响识别。不能套用其他研究4 nW/cm²/sr阈值的验证性能，也未将低夜光直接归因为缺乏电网。','','## 供电与需求口径','','沿用已确认图4a–g的Duarte最高实测输出锚点：ISO A下144.8 J/对/交互车辆；交互比例0.5、下游电量保留系数0.8，布设密度为每公里1对或20对。ISO B–H沿用图4的相对机械输入响应系数和固定转换效率，未使用新增图4i的低速模型结果替换本分支。ISO等级为统一情景，不是逐道路观测路况。','','每公里年度供电量（kWh/km/年）为：AADT × 365 × 装置对数/km × 0.5 × 144.8 × ISO响应系数 × 0.8 / 3,600,000。每公里年度需求为规定年平均功率W/km × 8.76。路段供需两端均乘以同一路段长度。零夜光路段仍赋予相同设施配置的非零需求。','','路长达标比例＝分组内年度供电量≥年度需求的路段长度之和/分组总路长。该指标是年度电量平衡，不是全年连续离网供电。所有供电与需求参数与图4一致；不同设施配置分别评估，不将其电量收益相加。','','## 补充表X：ISO A严格无正夜光记录的交叉结果','','|采能装置对数/km|拟供电设施配置|年平均功率预算W/km|达标路长km|分组内达标比例|所需AADT辆/日|','|---:|---|---:|---:|---:|---:|']
for r in s.itertuples():lines.append(f'|{r.pairs_per_km}|{names[r.load_level]}|{r.power_W_per_km:.6f}|{r.balanced_weighted_length_km:,.3f}|{r.annual_balance_length_pct:.4f}%|{r.threshold_aadt:,.2f}|')
lines+=['','‘气象节点’各档为既定功率预算支持的配置，不是新的设备实测产电或功耗试验；具体设备功耗、运行时间和组合沿用已确认设施参数表。图4g第六档预算为105.366453663 W/km，不能另换为5倍单灯功率；其源标签及预算完整保留。','','## ISO敏感性：20对装置/km、1盏灯/km','','|ISO情景|严格无正夜光路段达标路长km|严格无正夜光达标比例|全部采样为正夜光路段达标比例|','|---|---:|---:|---:|']
for iso in 'ABCDEFGH':
 r=view('whole_record_no_positive',iso=iso);r=r[(r.pairs_per_km==20)&(r.load_level==5)].iloc[0];b=view('whole_record_all_positive',iso=iso);b=b[(b.pairs_per_km==20)&(b.load_level==5)].iloc[0]
 lines.append(f'|{iso}|{r.balanced_weighted_length_km:,.3f}|{r.annual_balance_length_pct:.4f}%|{b.annual_balance_length_pct:.4f}%|')
lines+=['','## 分组与交通敏感性','','|分组|交通情景|雷达1对/km达标比例|1盏灯20对/km达标比例|','|---|---|---:|---:|']
for group in ['whole_record_no_positive','whole_record_positive_le10pct','nonpositive_in_bounds']:
 for q in ['median','q05','q95']:
  z=view(group,traffic=q);r=z[(z.pairs_per_km==1)&(z.load_level==1)].iloc[0];l=z[(z.pairs_per_km==20)&(z.load_level==5)].iloc[0]
  lines.append(f'|{group}|{q}|{r.annual_balance_length_pct:.4f}%|{l.annual_balance_length_pct:.4f}%|')
lines+=['','q05与q95沿用原交通数据中的预测情景，不是新估计的联合置信区间；各记录逐一同时取q05或q95也不是全球概率分布。它们说明结果对交通输入有明显敏感性。','','## 可用于正文的结果段落','','为判断上述供电潜力能否覆盖照明覆盖有限的道路，我们进一步将夜光筛查结果与采能供电能力进行交叉统计。在研究路网中，沿线采样均未检出正夜光的路段总长约119.79万km。在ISO A参考情景下，每公里布设1对采能装置，可在其中104.44万km、即87.19%的路长上满足每公里1个交通雷达电子部件的年度用电需求；每公里布设20对装置时，可在31.96万km、即26.68%的路长上满足每公里1盏路灯的年度用电需求。ISO B和C下，后一比例分别为27.09%和28.08%。这些结果表明，未检出夜光的道路与低功耗监测供电机会存在较广泛的空间交集，分散照明也具有一定部署范围，其覆盖程度取决于交通量、设施负载和采能布设规模（补充表X）。','','不能据此写‘采能机会更集中于未照明道路’：同一配置下有正夜光的道路达标比例更高。也不能将本表认定为未铺装道路统计；原文65%未铺装比例作为独立文献背景保留，不进入本交叉分析的计算。','','## 复现与核验','',f"独立重现已确认图4全部112个设施标记结果，最大绝对差为{a['max_reproduction_error_pct']:.3g}个百分点；检查路长分割、交通情景顺序、记录ID唯一性和供需阈值。数据及脚本不修改既有图4结果。",'','来源：道路振动能论文_数据与代码.zip（libfile_32fc33fc73a8819184fa92a3c3d65203），以及Road_energy_9panels_source_package.zip v5（libfile_a8b782480cfc81918802971f3077ae26）。原始331个缓存文件的组合SHA256见audit.json。','','复现：安装numpy与pandas；从上述代码包提取outputs/Global_nightlight_20260928/global_segment_cache；运行 python calculate_cross_statistics.py --cache <缓存目录> --figure-data input_data --out out。严格无正夜光记录及三项主配置的达标标记见strict_dark_records.csv.gz；完整2352组交叉结果见cross_statistics_all_scenarios.csv。']
report=O/'SI_夜光与采能供电交叉统计_20261118.md';report.write_text('\n'.join(lines)+'\n')
B=P/'deliverable';(B/'input_data').mkdir(parents=True,exist_ok=True)
for n in ['ISO_A_H_response_factors.csv','coverage_device_markers.csv']:shutil.copy2(P/'current_figure/figure/sources/Figure4_density_comparison_package/work/data'/n,B/'input_data'/n)
shutil.copy2(P/'calculate_cross_statistics.py',B/'calculate_cross_statistics.py');shutil.copy2(P/'build_report.py',B/'build_report.py')
for f in O.iterdir():shutil.copy2(f,B/f.name)
with zipfile.ZipFile(P/'Nightlight_harvesting_overlap_20261118.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in B.rglob('*'):
  if f.is_file():z.write(f,str(f.relative_to(B)))
print('report',report,'zip bytes',(P/'Nightlight_harvesting_overlap_20261118.zip').stat().st_size)
