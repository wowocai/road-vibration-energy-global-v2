import numpy as np
PARAMS = {'Passenger': [1600, 60, 2400, 1800, 22000, 1600, 200000, 0.8, 1.2, 1.6], 'Freight': [8000, 200, 25000, 15000, 400000, 60000, 800000, 0.9, 1.5, 2.5], 'Bus': [16000, 450, 150000, 100000, 250000, 35000, 800000, 1.1, 3.5, 5.5]}

def assemble(label):
    ms, mu, ip, ir, ks, cs, kt, t, a, b = PARAMS[label]
    B = np.zeros((4, 7))
    B[:, 0] = 1
    B[:, 1] = [a, a, -b, -b]
    B[:, 2] = [-t, t, -t, t]
    B[np.arange(4), np.arange(3, 7)] = -1
    M = np.diag([ms, ip, ir, mu, mu, mu, mu])
    C = cs * B.T @ B
    K = ks * B.T @ B
    K[3:, 3:] += kt * np.eye(4)
    R = np.zeros((7, 4))
    R[3:] = kt * np.eye(4)
    return (M, C, K, R, B)

def response(label, speed=20.0, rho=0.5, points=12000, g0=0.001024, delay=True):
    M, C, K, R, B = assemble(label)
    ms, mu, ip, ir, ks, cs, kt, t, a, b = PARAMS[label]
    n = np.geomspace(0.01, 3.0, points)
    w = 2 * np.pi * n * speed
    Q = np.zeros((points, 4, 2), complex)
    Q[:, 0, 0] = 1
    Q[:, 1, 1] = 1
    phase = np.exp(-2j * np.pi * n * (a + b)) if delay else np.ones(points)
    Q[:, 2, 0] = phase
    Q[:, 3, 1] = phase
    Z = K[None] - w[:, None, None] ** 2 * M[None] + 1j * w[:, None, None] * C[None]
    H = np.linalg.solve(Z, np.einsum('ij,njk->nik', R, Q))
    V = 1j * w[:, None, None] * np.einsum('ij,njk->nik', B, H)
    S = np.array([[1, rho], [rho, 1]])
    g = g0 * (n / 0.1) ** (-2)
    power = float(np.trapz(cs * np.einsum('nia,ab,nib->n', V, S, V.conj()).real * g, n))
    tire = kt * (Q - H[:, 3:, :])
    forcevar = np.trapz(np.einsum('nia,ab,nib->ni', tire, S, tire.conj()).real * g[:, None], n, axis=0)
    rms = np.sqrt(np.maximum(forcevar, 0))
    static = np.array([ms * 9.81 * b / (2 * (a + b)) + mu * 9.81] * 2 + [ms * 9.81 * a / (2 * (a + b)) + mu * 9.81] * 2)
    return dict(vehicle=label, speed_m_s=speed, rho=rho, points=points, g0_m3=g0, delay=delay, mean_power_W=power, unit_J_km=1000 * power / speed, min_static_minus_3rms_N=float(np.min(static - 3 * rms)), front_dynamic_rms_N=float(rms[0]), rear_dynamic_rms_N=float(rms[2]))
