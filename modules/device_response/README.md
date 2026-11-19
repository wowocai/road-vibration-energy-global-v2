# Duarte 原型：ISO A–H 的单边接触情景计算

**范围。** 比较同一参考原型在八个统一 ISO 路谱上的产电变化。保持 2,000 kg、50 km/h、每公里 20 对、50% 有效触发和 80% 下游电量保留，与图 3 的高输出参照一致。144.8 J/对·次取自 Duarte 等的原型试验，作为 A 情景的输出锚点（试验路面 ISO 等级未报告）；其余情景用同一原型的相对机械响应缩放，不再次乘机电转换效率。归一化后，年供电按原路段交通量折算。照明需求逐段封顶后汇总，继续使用正夜光比例权重与 Fingal 参考需求。

**接触模型。** 沿用七自由度整车、前后轴 2.8 m 空间延迟、左右轮迹相关系数 0.5。垂向轮胎反力为 max(0, 静轮载 + 轮胎刚度 × 相对动态压缩量)，每一步用该反力重新推进整车状态，轮胎重新压到路面时恢复接触。轮胎设为弹簧，未加入冲击阻尼、轮胎包络或悬架限位；装置没有向车辆动力学反馈。采用与旧原型代码相同的有效加载长度 1.1 m 和门函数，主模型用 25 ms 一阶耗散响应。用 10/50 ms、另一套车辆刚度参数以及固定顶板位移轨迹下对轮载线性的做功模型进行敏感性对照。固定行程模型独立归一化至同一试验锚点，仅用于说明装置响应机制对预测的影响。

**数值。** 每个等级共 16 个独立相位组，每组 128 个位置及其反相配对，合计 4,096 次原型通过窗口。车辆时域用 RK4；比较 15.625 mm 和 7.8125 mm 两个空间步长。G/H 另比较一圈和两圈预热，并和 ISO A 一起以 3.90625 mm 网格复核。数值文件中 refinement=1 为 15.625 mm，2 为主结果 7.8125 mm，3 为双倍预热复核，4 为 3.90625 mm 复核。误差条为基于 16 个配对相位组的近似 95% 抽样区间，未覆盖顶板响应、车辆参数及强冲击模型的不确定性。主计算相对旧模型的 A–C 差异最大 0.0051%；15.625/7.8125 mm 对照最大 1.2387%，加密对照最大 0.5921%，延长预热对照最大 0.4466%。最极端相位下单轮平均反力与静载的差异最大约 5.7%（长路段仍有有限窗口与强冲击变化）；所有运行的全车能量收支残差不超过悬架耗散的 0.031%。计算同时保留单一参考车辆的悬架耗散指标，未据此更新全球多车型的图 2。D–H 供电结果为固定车速的条件模拟，不表示已验证装置能在相同实际路况稳定运行。

**运行。** Linux 下需要 C 编译器，以及 Python + NumPy、SciPy、pandas、matplotlib。运行 `python run.py` 生成相位结果；运行 `python summarize.py` 复算和绘图。将目录置于原项目根目录下，第二步调用同级 `duarte_iso/reference_results.csv`、`geo_check/figures/figures/source_data/Figure4_efficiency_scenarios.csv` 以及原全球路段缓存 `geo_check/unpacked/outputs/Global_nightlight_20260928/global_segment_cache/batch_*.npz`。所附 CSV 包含全相位和敏感性结果，可直接查看，无需下载原全球路网。

**来源。** Duarte, Ferreira & Fael (2020), *Road pavement energy harvesting: experimental validation of a new electromechanical system*, TRA，表 1–2及结论：[原文](https://www.researchgate.net/publication/342179415_Road_pavement_energy_harvesting_experimental_validation_of_an_electromechanical_system)。路谱分类：[ISO 8608:2016](https://www.iso.org/standard/71202.html)。接触建模参考：Svahn & Jerrelind (2010), *Suppression of Bumpstop Instabilities in a Quarter-Car Model*, [DOI](https://doi.org/10.1007/978-3-642-01356-0_12)；[技术报告中轮胎离地/再接触说明](https://www.diva-portal.org/smash/get/diva2%3A872185/FULLTEXT01.pdf#page=31)。文献用于说明接触建模思路，未用于标定本原型的 D–H 参数。
