# VQ Linear Kinetic Transport Solver v9

This package implements the v9 revisions requested after the research discussion with Ryan McClarren.

## New in v9

1. **Mixed-angular-order collision split for the 2D line-source benchmark**
   - high angular order for the uncollided equation: `N_u=32` by default;
   - lower angular order for the collided equation: `N_c in {4,8,16,32}`;
   - moment-preserving transfer from the collided quadrature to the uncollided quadrature for time-step relabeling;
   - moment-preserving randomized quantization applied only to the low-order collided angular residual;
   - separate reporting of mixed-order discretization error and the additional quantization perturbation.

2. **Correct process-memory measurements**
   - every profiled case runs in a fresh subprocess;
   - peak resident set size (RSS) is sampled for the complete process tree with `psutil`;
   - peak unique set size (USS), baseline RSS, peak-minus-baseline RSS, final RSS, and Linux `ru_maxrss` are recorded when available;
   - Python `tracemalloc` is not reported as process peak memory;
   - analytical packed representation sizes are kept separate from measured process-memory values.

The line-source problem is the primary mixed-order benchmark because its uncollided component is strongly directional while scattering relaxes the collided component toward a less anisotropic distribution. This provides the cleanest test of a high-order uncollided / low-order collided discretization before adding material-interface effects from the lattice or hohlraum problems.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

For high-resolution runs, Numba is strongly recommended and is installed by the package requirements.

## Tests

```bash
make test
make smoke
make memory-smoke
```

## Full mixed-order line-source matrix

```bash
make mixed-order-line-source
```

The full target runs

- `N_x=N_y=201`,
- `N_u=32`,
- `N_c in {4,8,16,32}`,
- uncompressed mixed-order baselines,
- residual bit widths `b in {3,5,8}`.

All raw arrays, per-case summaries, memory profiles, CSV analyses, and 300-dpi figures are written below `results/v9_line_source/`.

## Error separation

Let `phi_32,32` be the uncompressed `N_u=N_c=32` split reference, `phi_32,Nc` the uncompressed mixed-order result, and `phi_32,Nc^(b)` the compressed mixed-order result. The package reports

```text
mixed_order_error = ||phi_32,Nc - phi_32,32|| / ||phi_32,32||
quantization_error = ||phi_32,Nc^(b) - phi_32,Nc|| / ||phi_32,Nc||
total_error = ||phi_32,Nc^(b) - phi_32,32|| / ||phi_32,32||
```

These quantities must not be conflated.

## Memory interpretation

`peak_rss_mib` is the principal measured process-memory metric. `packed_collided_mib` is an analytical representation-size estimate. A reduction in the latter does not imply an equal reduction in peak RSS unless a production implementation keeps the residual packed throughout the relevant storage or communication path.
