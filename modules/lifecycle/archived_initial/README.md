# 三类路侧能源生命周期成本测算

公开价格核对日期：2026-11-13。所有金额为USD。

## 已核验硬件报价

|编号|商品|报价|单位|来源|口径|
|---|---|---:|---|---|---|
|Q1|SunGoldPower SG500WM, 2 x 500 W pack|803|USD/2 panels|https://techwaveessentials.com/products/sungoldpower-500w-mono-black-perc-solar-panel-ul61730-cec-listed|Retail 2-pack cost; 10 packs/km. Reference output model is unchanged; price is not a new performance measurement.|
|Q2|Bayoung FS105 600 W vertical-axis turbine|563.99|USD/turbine|https://www.ebay.com/itm/176297608650|Current displayed price; 0.52 m rotor, NOT Ahmad 0.65 m tested prototype. Cost analogue only; seller wattage not used for energy.|
|Q3|LiTime 51.2 V 100 Ah ComFlex battery|1097.99|USD/5.12 kWh module|https://www.litime.com/products/litime-48v-100ah-smart-comflex-lithium-battery|Two modules/km in common-storage case. Five-year warranty and up-to-10-year claimed life do not prove field life. 10-year replacement is prescribed.|
|Q4|LiTime 48 V 5 kW inverter/charger|699.99|USD/unit|https://www.litime.com/products/48v-5kw-solar-inverter-charger?variant=46957458981084|Two units used as common power-stage cost reference; input rectification/DC conditioning separately allowed. Not a certified cross-technology wiring design.|
|Q5|IstaBreeze 500 W permanent-magnet alternator|174.47|USD/unit|https://www.ebay.com/itm/168391868944|Latest opened display, not stale search-snippet USD134.03. Two per road pair. Bare generator is not a Duarte installation.|
|Q6|MOTIONTEK 1000 mm rack and 20T pinion kit|142|USD/kit|https://www.ebay.com/itm/155555923623|Two kits/road pair. Quote excludes displayed destination-specific freight and import charges; contingency covers landed-cost range.|
|Q7|Compression spring 1.5 inch x 1.25 inch OD, 496 lb listed|13.99|USD/unit|https://www.ebay.com/itm/196009943219|Four/road pair as cost references only. Spring force/stroke matching is not validated by this quote.|
|Q8|UCP205-16 1 inch pillow block bearing|12.75|USD/unit|https://surpluscenter.com/bearings/cast-iron-pillow-block-bearings/|Four/road pair; cost reference only.|
|Q9|SunGoldPower SG500WM 32-panel pallet|5690|USD/32 panels|https://sungoldpower.com/collections/all-1/products/500w-mono-black-perc-solar-panel-full-pallet-32-panels|Bulk reference USD177.8125/panel; availability notification shown. Not selected as single-panel current retail price.|

## 计算方法及边界

### 51.1 Comparison and costing boundary

The comparison retains Figure 5 generation and load chronologies: twenty 500 Wp PV panels, twenty wind turbines, or twenty road-harvester pairs per kilometre. Annual demand is 3581.279266 kWh/km for twenty lamps plus one radar component. The assessment period is twenty years, with a prescribed real discount rate of 5% (3% and 8% sensitivities). Retail prices were checked on 13 November 2026, denominated in USD, and held constant in the reference real-cost scenario. Performance uses the archived 2023 weather and traffic chronology. This separates the performance reference year from the equipment-price date.

### 51.2 Public prices and device matching

The price-source table records the vendor page, package size and role of every quote. Q2 is an analogous commercial vertical-axis turbine, not the Ahmad tested prototype; Q5-Q8 anchor a reconstructed mechanism cost, not a quotation for the Duarte prototype. These quotes do not transfer performance claims, certify roadside durability, or establish exact component compatibility. The reported 144.8 J/pair/pass and Savonius bench curve remain unchanged. Two 5.12 kWh battery modules provide the common 10.24 kWh storage case. Two quoted 5 kW inverter/chargers provide a common power-stage cost reference, with conservative aggregate dispatch power limited to 5 kW. Steel/frame/housing, remaining drivetrain parts, DC conditioning, assembly hours, mounting hardware and field construction are separately itemized engineering allowances.

### 51.3 Installation, maintenance and replacements

PV comprises ten USD803 two-panel packs, USD2000 racking and USD1000 electrical balance, plus USD2500 field installation. Wind comprises twenty USD563.99 analogous turbines, USD2000 mounts and USD1000 electrical balance, plus USD5000 installation. Road equipment is twenty reconstructed USD1959.90 pairs, plus USD10000 installation. These field costs are prescribed scenarios, including access, installation labor and reinstatement allowances, not contractor quotations. Annual routine O&M is USD300 for PV and 2% of initial generation equipment plus field installation for wind and road. It excludes the explicit major replacements: wind equipment plus USD2500 labor at year 10; road equipment plus USD5000 labor at year 10; common power electronics plus USD200 labor at year 10. No PV-module replacement is imposed within twenty years. This is an assumed schedule, not an experimentally established service life. Storage initial cost includes battery-module purchases plus USD300 cabinet and USD320 installation; annual storage O&M is 1% of that total. Modules plus USD200 replacement labor are replaced at year 10. Battery augmentation is not also charged. Routine O&M and major replacements are accounted separately. Zero net end-of-life/salvage cost is the reference assumption.

### 51.4 Minute dispatch and equivalent service

For generation G_t, load L_t, usable storage S and efficiency eta=sqrt(0.85), direct use is min(G_t,L_t). Renewable surplus charges storage subject to S<=0.8C and the 5 kW rate; discharge supplies remaining load at the same efficiency and rate. The annual state is iterated until initial and final SOC agree within 1e-6 Wh, so initial stored energy gives no free credit. Annual generation equals local delivery plus curtailment plus storage loss within 1e-6 kWh in every run. The common 10.24 kWh case is a controlled cost-component comparison, not an assertion of optimal sizing. Reliable existing grid supply purchases each minute deficit at USD0.16/kWh, so all three alternatives serve exactly the same lamp/radar chronology. No export revenue or grid charging is credited. The shared existing connection and identical load equipment cancel from the incremental comparison; new remote grid extension, direction-dependent collection wiring and separate standby auxiliaries are not priced. Source outputs retain the previous 80% aggregate downstream retention. Thus this is a retail-anchored comparative cost screen, not a turnkey remote installation quotation or net-carbon assessment.

### 51.5 Discounted costs and results

LCC_asset=C_equipment+C_install+C_power+C_storage+sum_t[(C_OM,t+C_replacement,t)/(1+r)^t]. LCC_service=LCC_asset+sum_t[p_grid E_backup,t/(1+r)^t]. Costs are end-of-year except initial equipment/installation. Carbon credits are not deducted, and gross Figure 5d generation value is not confused with local self-consumption savings. Under common 10.24 kWh storage, local delivered electricity is 2500.568, 0.011071 and 726.595 kWh/km/year for PV, wind and road, respectively. The resulting twenty-year discounted service costs are USD26443.62, USD48547.47 and USD101306.23/km. These conditional values reflect different local energy contributions with grid backup ensuring equal total service. They do not establish a universal technology ranking.

### 51.6 Storage interpretation and sensitivity

Without storage, road generation supplies 328.602 kWh/km/year directly to the common load; a 2 kWh nominal buffer raises delivery to 724.960 kWh/km/year. Therefore the claim that road harvesting incurs no storage costs is removed. The storage sweep tests 0, 0.1, 0.25, 0.5, 1, 2, 5, 5.12, 10, 10.24, 15.36, 20.48, 51.2, 102.4 and 204.8 kWh. Additional sweeps independently vary discount (3/5/8%), grid energy value (USD0.08/0.16/0.32 per kWh), technology costs (0.5/1/2 times reference) and battery costs (0.5/1/2). The least-cost sampled configurations at baseline use 10.24 kWh for PV and no battery for wind/road because existing grid backup is inexpensive; that is an economic choice in a grid-supported system, not proof of storage-free autonomous operation. At fixed twenty nodes, wind and road annual energy are insufficient for 99% off-grid energy service regardless of battery size. A theoretical aggregate PV storage screen reaches the 99% energy and full-minute targets at 476.16 kWh, requiring multiple separately engineered banks because one product bank supports at most sixteen modules. This value is not used as a buildable hardware design or in the main three-way service-cost table. Typical-year repetition, maintained output and fixed weather/traffic are prescribed; long-term weather and component reliability are not inferred.

### 51.7 Files and reviewer correspondence

The calculation package contains price_sources.csv, road_pair_BOM.csv, lifecycle_comparison.csv, storage_cost_sweep.csv, cost_sensitivity.csv, offgrid_feasibility.csv, audit.json, the dispatch code and frozen minute inputs. This note supplements Note 50.9 and supports replies R1.5, R2.4, R2.5, R3.8 and R4.2. Equipment price, field installation, routine maintenance, replacement and storage are separately traceable. Unconditional total-cost superiority and zero-storage claims are not retained.

## 不应恢复的原稿句子

“振动采能不需要电池采购、更换等支出”与分钟调度结果不符，不恢复。可改为“道路振动采能的交通触发出力改变了电量产生与需求之间的时间关系，其储能配置应由交通和负载时序共同确定”。

未将尚无完整公开整机报价的Duarte原型写成确定市场售价；以公开部件单价加明示工程余项估算并做成本敏感性。当前成本结果是条件性筛算，正文不能据此宣称普遍成本优势。

## 复现

在解压目录中运行 `g++ -O3 -o dispatch dispatch.cpp`，再运行 `python calculate.py`。需要Python、numpy和pandas。默认源文件为source/Figure5/node20/out/minute_inputs.npz。输出CSV与audit.json包含输入、分项成本及守恒检查。
