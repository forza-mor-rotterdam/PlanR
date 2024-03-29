# rd_convert.py

"""
Copyright Jonathan de Bruin (2016)
"""

from __future__ import division, print_function

X0 = 155000
Y0 = 463000
PHI0 = 52.15517440
LAM0 = 5.38720621


def rd_to_wgs(x, y):
    """
    Convert rijksdriehoekcoordinates into WGS84 cooridnates. Input parameters: x (float), y (float).
    """

    if isinstance(x, (list, tuple)):
        x, y = x

    pqk = [
        (0, 1, 3235.65389),
        (2, 0, -32.58297),
        (0, 2, -0.24750),
        (2, 1, -0.84978),
        (0, 3, -0.06550),
        (2, 2, -0.01709),
        (1, 0, -0.00738),
        (4, 0, 0.00530),
        (2, 3, -0.00039),
        (4, 1, 0.00033),
        (1, 1, -0.00012),
    ]

    pql = [
        (1, 0, 5260.52916),
        (1, 1, 105.94684),
        (1, 2, 2.45656),
        (3, 0, -0.81885),
        (1, 3, 0.05594),
        (3, 1, -0.05607),
        (0, 1, 0.01199),
        (3, 2, -0.00256),
        (1, 4, 0.00128),
        (0, 2, 0.00022),
        (2, 0, -0.00022),
        (5, 0, 0.00026),
    ]

    dx = 1e-5 * (x - X0)
    dy = 1e-5 * (y - Y0)

    phi = PHI0
    lam = LAM0

    for p, q, k in pqk:
        phi += k * dx**p * dy**q / 3600

    for p, q, l in pql:
        lam += l * dx**p * dy**q / 3600

    return [phi, lam]


def wgs_to_rd(phi, lam):
    """
    Convert WGS84 cooridnates into rijksdriehoekcoordinates. Input parameters: phi (float), lambda (float).
    """

    pqr = [
        (0, 1, 190094.945),
        (1, 1, -11832.228),
        (2, 1, -114.221),
        (0, 3, -32.391),
        (1, 0, -0.705),
        (3, 1, -2.34),
        (1, 3, -0.608),
        (0, 2, -0.008),
        (2, 3, 0.148),
    ]

    pqs = [
        (1, 0, 309056.544),
        (0, 2, 3638.893),
        (2, 0, 73.077),
        (1, 2, -157.984),
        (3, 0, 59.788),
        (0, 1, 0.433),
        (2, 2, -6.439),
        (1, 1, -0.032),
        (0, 4, 0.092),
        (1, 4, -0.054),
    ]

    dphi = 0.36 * (phi - PHI0)
    dlam = 0.36 * (lam - LAM0)

    X = X0
    Y = Y0

    for p, q, r in pqr:
        X += r * dphi**p * dlam**q

    for p, q, s in pqs:
        Y += s * dphi**p * dlam**q

    return [X, Y]


if __name__ == "__main__":
    coord_rd = [
        [121687, 487484],  # Amsterdam
        [92565, 437428],  # Rotterdam
        [176331, 317462],  # Maastricht
        [93204, 431785],
    ]  # Rotterdam zuid

    coord_wgs = [
        [52.37422, 4.89801],  # Amsterdam
        [51.92183, 4.47959],  # Rotterdam
        [50.84660, 5.69006],
    ]  # Maastricht

    for x, y in coord_rd:
        print(rd_to_wgs(x, y))

    for phi, lam in coord_wgs:
        print(wgs_to_rd(phi, lam))
