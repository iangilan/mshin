from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Problem2D:
    name: str
    nx: int
    ny: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    final_time: float
    cfl: float
    sigma_a: np.ndarray
    sigma_s: np.ndarray
    q: np.ndarray
    phi0: np.ndarray
    left_inflow: float
    right_inflow: float
    bottom_inflow: float
    top_inflow: float
    metadata: dict[str, Any]

    @property
    def dx(self) -> float:
        return (self.x_max - self.x_min) / self.nx

    @property
    def dy(self) -> float:
        return (self.y_max - self.y_min) / self.ny

    @property
    def x(self) -> np.ndarray:
        return self.x_min + (np.arange(self.nx) + 0.5) * self.dx

    @property
    def y(self) -> np.ndarray:
        return self.y_min + (np.arange(self.ny) + 0.5) * self.dy

    @property
    def sigma_t(self) -> np.ndarray:
        return self.sigma_a + self.sigma_s


def _mesh(nx: int, ny: int, bounds: tuple[float, float, float, float]):
    x_min, x_max, y_min, y_max = bounds
    x = x_min + (np.arange(nx) + 0.5) * ((x_max - x_min) / nx)
    y = y_min + (np.arange(ny) + 0.5) * ((y_max - y_min) / ny)
    return np.meshgrid(x, y, indexing="ij")


def make_problem_2d(name: str, nx: int, ny: int | None = None) -> Problem2D:
    """Construct line-source, lattice, or modified-hohlraum data.

    V9 uses the line source for the mixed-angular-order study. The other two
    definitions are retained so the same solver can be extended after the
    line-source validation is complete.
    """
    canonical = name.lower().replace("-", "_")
    nx = int(nx)
    ny = nx if ny is None else int(ny)
    if nx < 3 or ny < 3:
        raise ValueError("nx and ny must be at least 3")

    if canonical == "line_source":
        bounds = (-1.5, 1.5, -1.5, 1.5)
        X, Y = _mesh(nx, ny, bounds)
        zeta = 0.03
        phi0 = (1.0 / (2.0 * np.pi * zeta)) * np.exp(-(X * X + Y * Y) / (2.0 * zeta))
        sigma_a = np.zeros((nx, ny), dtype=np.float64)
        sigma_s = np.ones((nx, ny), dtype=np.float64)
        q = np.zeros((nx, ny), dtype=np.float64)
        final_time, cfl = 1.0, 0.5
        bcs = (0.0, 0.0, 0.0, 0.0)
        metadata = {
            "benchmark_source": "Krotz-Hauck-McClarren line source",
            "domain": "[-1.5,1.5]^2",
            "zeta": zeta,
            "recommended_mixed_order": {"N_u": 32, "N_c": 8},
        }
    elif canonical == "lattice":
        bounds = (0.0, 7.0, 0.0, 7.0)
        X, Y = _mesh(nx, ny, bounds)
        sigma_a = np.zeros((nx, ny), dtype=np.float64)
        sigma_s = np.ones((nx, ny), dtype=np.float64)
        q = np.zeros((nx, ny), dtype=np.float64)
        I = np.clip(np.floor(X).astype(int), 0, 6)
        J = np.clip(np.floor(Y).astype(int), 0, 6)
        source = (I == 3) & (J == 3)
        absorbers = (
            ((I == 1) & (J == 5)) | ((I == 5) & (J == 5)) |
            ((I == 2) & (J == 4)) | ((I == 4) & (J == 4)) |
            ((I == 1) & (J == 3)) | ((I == 5) & (J == 3)) |
            ((I == 2) & (J == 2)) | ((I == 4) & (J == 2)) |
            ((I == 1) & (J == 1)) | ((I == 3) & (J == 1)) | ((I == 5) & (J == 1))
        )
        sigma_a[absorbers] = 10.0
        sigma_s[absorbers] = 0.0
        q[source] = 1.0
        phi0 = np.zeros((nx, ny), dtype=np.float64)
        final_time, cfl = 3.2, 25.6
        bcs = (0.0, 0.0, 0.0, 0.0)
        metadata = {"benchmark_source": "Krotz-Hauck-McClarren lattice", "domain": "[0,7]^2"}
    elif canonical in {"hohlraum", "modified_hohlraum"}:
        canonical = "hohlraum"
        bounds = (0.0, 1.3, 0.0, 1.3)
        X, Y = _mesh(nx, ny, bounds)
        sigma_a = np.zeros((nx, ny), dtype=np.float64)
        sigma_s = np.full((nx, ny), 0.1, dtype=np.float64)
        q = np.zeros((nx, ny), dtype=np.float64)
        wall = 0.05
        black = (X > 1.3 - wall) | (Y < wall) | (Y > 1.3 - wall)
        sigma_s[black] = 100.0
        red = (X < wall) & (Y >= 0.20) & (Y <= 1.00)
        sigma_a[red], sigma_s[red] = 5.0, 95.0
        shell = (X >= 0.40) & (X <= 0.90) & (Y >= 0.25) & (Y <= 1.05)
        core = (X >= 0.45) & (X <= 0.85) & (Y >= 0.30) & (Y <= 1.00)
        sigma_a[shell], sigma_s[shell] = 10.0, 90.0
        sigma_a[core], sigma_s[core] = 50.0, 50.0
        phi0 = np.zeros((nx, ny), dtype=np.float64)
        final_time, cfl = 2.6, 52.0
        bcs = (1.0, 0.0, 0.0, 0.0)
        metadata = {"benchmark_source": "modified Krotz-Hauck-McClarren hohlraum", "domain": "[0,1.3]^2"}
    else:
        raise ValueError(f"unknown 2D problem: {name!r}")

    return Problem2D(
        name=canonical,
        nx=nx,
        ny=ny,
        x_min=bounds[0],
        x_max=bounds[1],
        y_min=bounds[2],
        y_max=bounds[3],
        final_time=final_time,
        cfl=cfl,
        sigma_a=sigma_a,
        sigma_s=sigma_s,
        q=q,
        phi0=phi0,
        left_inflow=bcs[0],
        right_inflow=bcs[1],
        bottom_inflow=bcs[2],
        top_inflow=bcs[3],
        metadata=metadata,
    )
