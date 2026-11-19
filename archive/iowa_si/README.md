# Iowa 案例：27 组敏感性核对及补充图
图 a 比较同一批 3,903 条记录的三种路面输入；图 b 展示 27 组重新计算的结果。建议放入补充说明 21，图号随终稿统一。

## 情景设置与核对
- 路面单边谱形式 G(n)=G₀(n/0.1)^(-w)，w=1.5、2.0、2.5；积分频段 0.01–3 cycle/m。对每个 w 重新标定 Golden Car IRI–谱幅值映射，而非沿用 w=2 的换算系数。三个系数分别约为 743.709、543.142、421.147，单位为 (m/km)/sqrt(m³)。
- 运行车速设为各记录限速的 80%、各记录限速、统一 20 m/s；这些是情景设置。
- 将记录货车交通量的 0%、50%、100% 分配给重型货运代表模型，余量采用乘用车模型作为轻端响应代理。车辆总数不变；0% 不表示删除货车。
- 每组使用相同 3,903 条记录及交通量，左右轮迹相关系数 0.5，计入轴距时延。图 b 中的 ISO A 参照与该单元车速和车型映射一致，谱指数固定为 2.0，参考幅值 16×10⁻⁶ m³。
- 另比较相同车速、车型和谱指数下固定参考幅值 16×10⁻⁶ m³ 的情景。指数偏离 2.0 时，称为固定幅值参照，不称 ISO A 标准谱。

## 核对结果
基准 IRI/ISO A/ISO B 分别为 9.928241、21.839061、87.356244 GWh/年。27 个唯一组合的耗散为 5.384708–13.329144 GWh/年，分别相当于逐组匹配 ISO A 对照的 36.0%–59.4%。在逐组匹配谱指数的固定幅值参照下也全部低于对照（24.8%–84.0%）。27 个 IRI 约束情景均未触发静载减去三倍动态轮载均方根小于零的筛查判据。此为所考察的模型情景范围。

存档正文给出基准与区间端点（5.385–13.329 GWh/年），存档补充方法给出谱指数与基准速度，未找到历史逐组明细及其余车速和货运分配的完整定义。本包采用上面明确列出的设置进行逐组复算，基准和区间端点与存档吻合；端点吻合本身不能证明所有历史中间组合及数值相同。

## 可直接使用的英文图注
Supplementary Fig. X | Road-profile inputs and scenario sensitivity for the Iowa road inventory. **a**, Modelled annual suspension dissipation for the same 3,903 screened records using uniform ISO A and ISO B reference spectra or spectra constrained by recorded IRI. **b**, Twenty-seven combinations of spectral exponent, operating speed and the fraction of reported truck traffic assigned to the heavy-vehicle proxy. The remaining truck traffic is represented by the passenger-car response as a light-end proxy. Each cell shows the IRI-constrained dissipation in GWh per year (top) and its percentage of the ISO A reference evaluated at the same speed and vehicle mapping (bottom). The orange outline marks the baseline. Across the tested combinations, IRI-constrained dissipation remained below its corresponding ISO A reference.

## 数据及复算
inputs.csv 为上轮 Iowa DOT 查询及筛选后使用的六个原始字段；数据源 https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/Pavement_View/FeatureServer/0 。IRI 为英寸/英里，长度为英里，限速为 mph；转换在脚本内。source_vehicle_model.py 随包提供既有模型实现，重算脚本仅读取其中车辆参数和组装函数。用 Python（numpy≥2、pandas、matplotlib）运行 `python recompute_sensitivity.py`，再运行 `python plot_si.py`。Iowa_27_scenarios.csv 含逐组结果与筛查字段；图件提供 PNG、PDF、SVG。
