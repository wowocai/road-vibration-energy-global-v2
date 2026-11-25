# Matched coupled reference

This module reproduces Fig. 4i and Supplementary Note 19. All A–H cases use the same device parameter set calibrated to the Duarte mechanical input. The separate common-speed response calculations used in Fig. 3 and Fig. 4g remain unchanged.

```
python modules/matched_reference/run_reference.py --quick
python modules/matched_reference/run_reference.py --quick --iso H
python modules/matched_reference/run_reference.py --workers 4
```

Requires the root Python environment and a C compiler. The wrapper compiles `inertial/model.c` locally; compiled binaries are not distributed. Quick mode runs one seed/sign for the selected ISO class. Full mode runs 16 independent seeds and both profile signs for each class, computes independent seed means and two-sided 95% Student-t intervals.

The calibrated loading coefficient is 2446.710406022586 Ns/m for all A–H cases (tau = 0.06116776015056465 s with stiffness 40000 N/m). Return damping is 800 Ns/m, cover mass 20 kg, stroke 20 mm and contact patch 0.13625 m. A–F use 50 km/h. Sampled G/H checks at 50 km/h reach the model orientation limit; G at 5 km/h and H at 2 km/h provide prescribed slow-passage references for the same reconstructed device. These are operating scenarios rather than ISO-recommended or measured safe speeds. Within each scenario, installed and uninstalled vehicles share road realization, speed and measurement distance. A–F compare roughness at common speed; G/H evaluate energy balances in very rough-road slow passage.

Simulated 1-km work is divided by 20 effective pair encounters to obtain per-pair inputs. Aggregation per traffic vehicle-km uses 20 installed pairs/km and interaction 0.5. Delivered electricity uses measured efficiency 144.8/239.4 and downstream retention 0.8. Original 5/10/25-mm simplified-cover runs are separate stroke sensitivities. The archived 4000 Ns/m G/H cases are a separate loading-damping sensitivity and do not supply the primary bars.

The C solver is the archived inertial model. The ensemble wrapper explicitly supplies the calibrated coefficient for every class. Current source data retain 256 primary trajectories, 128 seed means, convergence checks and the alternative-damping comparison.
