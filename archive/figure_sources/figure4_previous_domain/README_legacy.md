# 九子图总图：3×3排版

保留现有供需总图a–h的数据和功能，新增i柱状图。原八子图文件名为Figure4_with_g_h.png，本次输出采用不预设图号的Road_energy_9panels_3x3，避免与前文图3/图4编号讨论冲突。新增i为作者已指定的ISO A、5/10/25 mm行程对照，不将其认定为Duarte原型实测尺寸。图号及正文引述待作者确认后同步。

- a–f：原六张ISO A年度供需地图，1对/km五档设施，以及20对/km的一灯配置。
- g：原ISO A–H供需达标曲线，保留1/20对每公里两个密度、均匀0–420 W/km轴及七档设备参考虚线。为适应单个网格，参考名称简写；对应设施配置与原始功率表未改变。
- h：原三种密集阵列情景年度照明电量贡献，18.95%、47.81%、67.42%。不将其误称为路长达标比例。
- i：新受限等效模型，ISO A，2 t、50 km/h、20对/km，实际压过全部装置时的每车公里新增轮端机械功和负载侧电量。5/10/25 mm额外轮端功0.842/2.847/9.675 kJ，电量0.211/0.605/1.868 kJ。保留CSV的未舍入值。电量由本次受限模型机械输入同步计算，机械—电转换比144.8/239.4、下游保留比例0.8。不是把原型144.8 J/对次与另一配置的车辆能耗混配。

字体现采用真实Times New Roman，来自已有图包中的Microsoft corefonts原始times32.exe；PNG/PDF和轮廓SVG可直接查看。地图道路层沿用原图包的栅格分类掩膜，底图边界、文字与图表为重新绘制。

## 文件

out/Road_energy_9panels_3x3.png：330 dpi，5940×4950。
out/Road_energy_9panels_3x3.pdf：字体嵌入PDF。
out/Road_energy_9panels_3x3.svg：文本可编辑SVG，需Times New Roman。
out/Road_energy_9panels_3x3_outlined.svg：字体轮廓化SVG。
out/panel_i_source_data.csv：新增柱图全部源数据。
render.py：总图绘图脚本。
data/constrained_summary.csv：本次车辆能耗计算汇总。
sources：原图源数据、图包脚本、字体包及出处。

## 复现

需Python3、numpy、pandas、Pillow、matplotlib、fontTools。脚本读取sources下Times字体；如系统未安装且尚未解包字体，可从所附原始times32.exe提取合法CAB（字节MSCF后四零的标记），运行来源图包tools/extract_fonts.py。不要把字体替代品伪装为Times New Roman。

在本目录运行python render.py。正文、SI和审稿回复未在此次制图中修改。


## 本轮修改：ISO A–H分组

子图i改为横轴A–H、每路况5/10/25 mm三组柱，上图新增车辆轮端功，下图负载侧电量。H的数值尚未通过收敛检查，因此保留H位置并以斜线区域标注Not converged，未绘制不可靠的定量柱。源数据24行完整保留，不将缺柱解释为零。其余a–h未改数据。单独放大图见out/Panel_i_ISO_A_H_three_strokes.png及PDF。此前README关于i仅展示ISO A的说明由本节替代。


## 最新呈现：同轴覆盖柱

子图i将上下两幅合为单轴。各ISO路况内为5/10/25 mm三根宽柱，浅色宽柱编码新增轮端功，同色较窄斜线柱从同一零点覆盖负载侧电量。两者不相加，不是堆叠；未覆盖区域不另行定义成完整损失分项。H仍保留待收敛区域。所有源数值不变，其余a–h数据不变。此前上下分图说明由本节替代。
