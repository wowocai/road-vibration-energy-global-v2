# 道路振动能研究：代码与处理后数据发布包

本包以2026年11月19日版本为准。主结果统一采用完整路段长度，夜光仅用于补充分组与历史口径比较。

## 使用

将“GitHub代码包”和“Zenodo数据包”解压到同一个目录，或直接解压完整包。Python 3.12安装依赖后执行：

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py --stage quick
python scripts/run_pipeline.py --stage national
python scripts/run_pipeline.py --stage cost
```

quick重新计算逐路段供需、年度发电量、密集阵列、供需阈值、覆盖曲线，并汇总车辆额外功记录及多能源分钟序列。national重新训练国家交通重建与逐国留出验证；cost重新编译储能调度并优化全生命周期成本。二者均计算而非仅复制既有表格。昂贵的全动力学积分另设入口。

文件级流程、输入输出、单位、参数来源、运行顺序及结果检查见docs文件夹。既有模拟JSON与分钟输入被作为可复算中间数据保存；原始完整SHP、全球VIIRS栅格不在包内，所附压缩道路几何用于显示，统计长度取源属性。

数据已发布于Zenodo：https://doi.org/10.5281/zenodo.24359475（记录：https://zenodo.org/records/24359475）。代码仓库：https://github.com/wowocai/road-vibration-energy-global-v2。数据记录中的压缩包名为Road_Vibration_Energy_Global_data.zip。将其中road-vibration-energy-global目录的内容与代码合并到同一工作目录后运行。数据说明与第三方来源见README_ZENODO_DATA.md和EXTERNAL_PUBLIC_DATA_URLS.md。论文正文与审稿材料不包含在公开仓库中。

