# Matched coupled reference

This supplementary module reproduces the coupled mechanical reference underlying current Fig. 4i and Supplementary Note 19. It retains the archived model equations and settings. It does not replace the separate common-speed roughness response used for Fig. 3 and Fig. 4g.

```
python modules/matched_reference/run_reference.py --quick
python modules/matched_reference/run_reference.py --workers 4
```

Requires the root Python environment and a C compiler. A local shared library is compiled from `inertial/model.c`; binaries are not distributed. The quick command is a single-profile execution check, not a full ensemble. The full command runs 16 road seeds and both signs for each A–H scenario, then calculates seed means and two-sided 95% Student-t intervals. A–F: 50 km/h and loading resistance 2,446.710406 Ns/m. G/H: 5/2 km/h and loading resistance 4,000 Ns/m, as in the archived low-speed records. Return resistance is 800 Ns/m. Thus G/H are prescribed road–device scenarios and are not used to isolate roughness effects at common vehicle and device settings.

Pair energy is obtained by dividing simulated 1-km measurement work by 20 effective module-pair encounters. Network per-traffic-vehicle results then use 20 installed pairs/km and effective interaction 0.5. Delivered electricity uses the measured 144.8/239.4 ratio and downstream retention 0.8. Original 5/10/25-mm simplified-cover runs remain separate sensitivities.

Code provenance: the original inertial solver and wrapper used for the 20 November 2026 matched-reference calculations. The ensemble wrapper makes every archived A–H setting explicit. It writes raw trajectories, seed means and summaries. Source Data includes the archived numerical records so that a rerun can be compared without estimating values from figures.
