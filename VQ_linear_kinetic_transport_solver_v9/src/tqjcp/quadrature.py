from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class AngularQuadrature2D:
    """Upper-hemisphere product quadrature used by the reduced 2D solver."""

    order: int
    ox: np.ndarray
    oy: np.ndarray
    oz: np.ndarray
    w: np.ndarray

    @property
    def n_angles(self) -> int:
        return int(self.w.size)

    @property
    def directions(self) -> np.ndarray:
        return np.column_stack((self.ox, self.oy, self.oz))


def upper_hemisphere_product_quadrature(order: int, dtype=np.float64) -> AngularQuadrature2D:
    """Return the N^2 upper-hemisphere product rule used in the benchmarks.

    The polar coordinate z=cos(theta) is integrated by Gauss-Legendre on
    [0,1], and the azimuth uses a midpoint rule. Weights are normalized to
    sum to one. Consequently, a direction-independent angular field has
    scalar flux equal to that common value.
    """
    if int(order) < 2:
        raise ValueError("order must be at least 2")
    order = int(order)
    z_nodes, z_weights = np.polynomial.legendre.leggauss(order)
    z = 0.5 * (z_nodes + 1.0)
    wz = 0.5 * z_weights
    alpha = (np.arange(order, dtype=np.float64) + 0.5) * (2.0 * np.pi / order)

    ox: list[float] = []
    oy: list[float] = []
    oz: list[float] = []
    weights: list[float] = []
    for iz in range(order):
        radius = math.sqrt(max(0.0, 1.0 - float(z[iz]) ** 2))
        for ia in range(order):
            ox.append(radius * math.cos(float(alpha[ia])))
            oy.append(radius * math.sin(float(alpha[ia])))
            oz.append(float(z[iz]))
            weights.append(float(wz[iz]) / order)

    w = np.asarray(weights, dtype=dtype)
    w /= np.sum(w)
    return AngularQuadrature2D(
        order=order,
        ox=np.asarray(ox, dtype=dtype),
        oy=np.asarray(oy, dtype=dtype),
        oz=np.asarray(oz, dtype=dtype),
        w=w,
    )


def moments_2d(psi: np.ndarray, quadrature: AngularQuadrature2D) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return scalar flux and the Cartesian current components."""
    arr = np.asarray(psi)
    if arr.shape[-1] != quadrature.n_angles:
        raise ValueError("angular dimension does not match the quadrature")
    phi = np.tensordot(arr, quadrature.w, axes=([-1], [0]))
    jx = np.tensordot(arr, quadrature.w * quadrature.ox, axes=([-1], [0]))
    jy = np.tensordot(arr, quadrature.w * quadrature.oy, axes=([-1], [0]))
    return phi, jx, jy
