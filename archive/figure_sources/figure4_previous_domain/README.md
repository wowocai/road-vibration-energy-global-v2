# Nine-panel road energy figure — repaired contact model, 2026-11-17

Panels a–h preserve the approved supply–demand figure. Panel i replaces the former unconverged high-speed H estimates with a unified repaired model and explicit road-class–speed reference scenarios: A–F at 50 km/h, G at 5 km/h, and H at 2 km/h. These are joint scenarios, not an isolated roughness comparison at fixed speed. The selected low speeds are computational reference assumptions, not ISO-prescribed speed limits or established safe speeds.

## Panel i

Two-tonne vehicle, 20 actually engaged harvester pairs/km, and 5/10/25 mm stroke limits. All cases use the finite-angle seven-degree-of-freedom vehicle model, two overdamped compliant plates, unilateral tyre contact, suspension travel stops and adaptive contact-event integration. Paired installed/uninstalled simulations share the same road and initial-equilibrium procedure. See `../repaired_model` and `../H_validation/out/H级车速与能耗核验_20261117.md` for equations, settings and validation.

Pale broad bars are additional net wheel work (installed minus reference). Dark narrower hatched bars are delivered electricity. Both begin at zero; they are overlaid, NOT stacked. Electricity is plate dissipation × (144.8/239.4) × 0.8. This fixed conversion assumption is not a measured low-speed output calibration. The H inset enlarges exactly the same H data without changing their units. No negative estimate is clipped, no failed simulation is filled with zero, and no electricity estimate is capped to force visual containment.

Whiskers are two-sided 95% Student-t sampling intervals on wheel work. Sign-reversed road pairs are averaged within each independent random seed before inference. A–G: 16 independent seeds/class/stroke (32 trajectories); H: 32 independent seeds/stroke (64 trajectories). Each trajectory has 200 m warm-up and 1 km measurement on a periodic 1 km spatial road; this does not imply a 1 km independent spatial realization for every pass. All 864 trajectories used in the plotted means completed. Parameter/model uncertainty is not included in these sampling intervals.

H at 2 km/h has passed the previously reported step/tolerance, duration and independent-road checks. Those precision checks should not be generalized as parameter validation or field validation of all A–G scenarios. Additional wheel work is wheel-level mechanical energy, not a fuel/electricity consumption estimate for the vehicle powertrain. It can be smaller than absorbed device energy when suspension/tyre/stop losses decline relative to the uninstalled baseline.

Panel i is a stroke-limited equivalent device model, distinct from the measured Duarte anchors and array cases in a–h. Their energies must not be subtracted to claim one validated global net-energy budget. Earlier unconverged H results remain under legacy filenames for audit only; they are superseded by the active `data/current_joint_scenarios.csv`.

## Reproduction

Compile `../repaired_model/model.c` using `gcc -O3 -shared -fPIC model.c -o model.so -lm`; Python dependencies: numpy, scipy, pandas, matplotlib, pillow. Run `../compute.py` to regenerate A–G trajectories, then `../aggregate.py`, then `python render.py`. For aggregation, preserve the relative layout of `reference_runs`, `figure`, and `H_validation/out` as in this archive. The supplied `data/current_joint_scenarios.csv` suffices for rendering without simulation. The pre-existing bundled font extraction script and original installer are retained; extract the font before rendering. All charts use Times New Roman. The original source package and adaptive-validation audit are retained alongside this update.

## Figure label update

The x-axis is labelled `ISO road class`, with A–H ticks only. Speed annotations and bottom explanatory text have been removed from the artwork; calculation conditions are retained in `../SI_note_panel_i.md`. Data are unchanged.
