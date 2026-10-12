import numpy as np


# ============================================================
# FREE SPACE PATH LOSS
# ============================================================

def fspl(distance_m, frequency_mhz):
    """
    Free Space Path Loss.

    PL(dB) =
        32.44
        + 20 log10(f_MHz)
        + 20 log10(d_km)

    Les distances inférieures à 1 m sont ramenées à 1 m
    afin d'éviter log10(0).
    """

    distance_m = np.maximum(
        np.asarray(distance_m, dtype=float),
        1.0
    )

    distance_km = distance_m / 1000.0

    return (
        32.44
        + 20.0 * np.log10(frequency_mhz)
        + 20.0 * np.log10(distance_km)
    )


# ============================================================
# LOG-DISTANCE
# ============================================================

def log_distance_path_loss(
    distance_m,
    frequency_mhz,
    exponent_n
):
    """
    Modèle Log-Distance.

    PL(d) = PL(d0) + 10*n*log10(d/d0)

    avec d0 = 1 m.
    """

    distance_m = np.maximum(
        np.asarray(distance_m, dtype=float),
        1.0
    )

    d0 = 1.0

    pl_d0 = fspl(
        np.array([d0]),
        frequency_mhz
    )[0]

    return (
        pl_d0
        + 10.0
        * exponent_n
        * np.log10(distance_m / d0)
    )


# ============================================================
# SHADOWING CORRELE
# ============================================================

def correlated_shadowing(
    number_points,
    sigma_db,
    step_m,
    decorrelation_distance_m,
    seed
):
    """
    Shadowing log-normal spatialement corrélé.

    Modèle AR(1) :

        S[k] =
            rho*S[k-1]
            + sigma*sqrt(1-rho²)*w[k]

    avec :

        rho = exp(-delta_d / d_corr)

    sigma_db = 0 :
        shadowing désactivé.
    """

    if sigma_db <= 0:
        return np.zeros(number_points)

    rng = np.random.default_rng(seed)

    step_m = max(
        float(step_m),
        1e-6
    )

    decorrelation_distance_m = max(
        float(decorrelation_distance_m),
        1e-6
    )

    rho = np.exp(
        -step_m
        / decorrelation_distance_m
    )

    white_noise = rng.normal(
        0.0,
        1.0,
        number_points
    )

    shadowing = np.zeros(
        number_points,
        dtype=float
    )

    shadowing[0] = (
        sigma_db
        * white_noise[0]
    )

    innovation_std = (
        sigma_db
        * np.sqrt(
            max(
                0.0,
                1.0 - rho ** 2
            )
        )
    )

    for i in range(
        1,
        number_points
    ):
        shadowing[i] = (
            rho * shadowing[i - 1]
            + innovation_std
            * white_noise[i]
        )

    return shadowing


# ============================================================
# CALCUL RADIO
# ============================================================

def calculate_radio_parameters(
    positions_m,
    node_distance_m,
    tx_power_dbm,
    model,
    frequency_mhz,
    cpich_percent,
    exponent_n,
    shadowing_sigma_db,
    decorrelation_distance_m,
    noise_figure_db,
    bandwidth_mhz,
    seed
):
    """
    Calcule :

    - distance UE -> Node B A
    - distance UE -> Node B B
    - Path Loss
    - puissance totale reçue
    - RSCP A / B
    - RSSI
    - Ec/No A / B

    Approximation pédagogique :

        Ec/No = RSCP - RSSI
    """

    positions_m = np.asarray(
        positions_m,
        dtype=float
    )

    number_points = len(
        positions_m
    )

    if number_points < 2:
        raise ValueError(
            "Il faut au moins deux points de simulation."
        )

    # --------------------------------------------------------
    # DISTANCES
    # --------------------------------------------------------

    distance_a = np.maximum(
        np.abs(positions_m),
        1.0
    )

    distance_b = np.maximum(
        np.abs(
            node_distance_m
            - positions_m
        ),
        1.0
    )

    step_m = float(
        np.mean(
            np.abs(
                np.diff(
                    positions_m
                )
            )
        )
    )

    # --------------------------------------------------------
    # PROPAGATION
    # --------------------------------------------------------

    if model == "log_distance":

        path_loss_a = (
            log_distance_path_loss(
                distance_a,
                frequency_mhz,
                exponent_n
            )
        )

        path_loss_b = (
            log_distance_path_loss(
                distance_b,
                frequency_mhz,
                exponent_n
            )
        )

        shadow_a = (
            correlated_shadowing(
                number_points,
                shadowing_sigma_db,
                step_m,
                decorrelation_distance_m,
                seed
            )
        )

        # Seed différent pour éviter que les deux cellules
        # subissent exactement le même fading.
        shadow_b = (
            correlated_shadowing(
                number_points,
                shadowing_sigma_db,
                step_m,
                decorrelation_distance_m,
                seed + 1000
            )
        )

    elif model == "free_space":

        path_loss_a = fspl(
            distance_a,
            frequency_mhz
        )

        path_loss_b = fspl(
            distance_b,
            frequency_mhz
        )

        # FSPL pur : pas de shadowing.
        shadow_a = np.zeros(
            number_points
        )

        shadow_b = np.zeros(
            number_points
        )

    else:
        raise ValueError(
            "Modèle de propagation inconnu."
        )

    # --------------------------------------------------------
    # PUISSANCE TOTALE RECUE
    # --------------------------------------------------------

    total_rx_a_dbm = (
        tx_power_dbm
        - path_loss_a
        + shadow_a
    )

    total_rx_b_dbm = (
        tx_power_dbm
        - path_loss_b
        + shadow_b
    )

    # --------------------------------------------------------
    # CPICH
    # --------------------------------------------------------

    cpich_ratio = (
        cpich_percent
        / 100.0
    )

    cpich_power_dbm = (
        tx_power_dbm
        + 10.0
        * np.log10(
            cpich_ratio
        )
    )

    rscp_a = (
        cpich_power_dbm
        - path_loss_a
        + shadow_a
    )

    rscp_b = (
        cpich_power_dbm
        - path_loss_b
        + shadow_b
    )

    # --------------------------------------------------------
    # BRUIT THERMIQUE
    # --------------------------------------------------------

    bandwidth_hz = (
        bandwidth_mhz
        * 1e6
    )

    thermal_noise_dbm = (
        -174.0
        + 10.0
        * np.log10(
            bandwidth_hz
        )
        + noise_figure_db
    )

    # --------------------------------------------------------
    # CONVERSION dBm -> mW
    # --------------------------------------------------------

    rx_a_mw = (
        10.0
        ** (
            total_rx_a_dbm
            / 10.0
        )
    )

    rx_b_mw = (
        10.0
        ** (
            total_rx_b_dbm
            / 10.0
        )
    )

    noise_mw = (
        10.0
        ** (
            thermal_noise_dbm
            / 10.0
        )
    )

    total_wideband_power_mw = (
        rx_a_mw
        + rx_b_mw
        + noise_mw
    )

    rssi_dbm = (
        10.0
        * np.log10(
            total_wideband_power_mw
        )
    )

    # --------------------------------------------------------
    # Ec/No
    # --------------------------------------------------------

    ecno_a = (
        rscp_a
        - rssi_dbm
    )

    ecno_b = (
        rscp_b
        - rssi_dbm
    )

    return {

        "distance_a":
            distance_a,

        "distance_b":
            distance_b,

        "path_loss_a":
            path_loss_a,

        "path_loss_b":
            path_loss_b,

        "shadow_a":
            shadow_a,

        "shadow_b":
            shadow_b,

        "rscp_a":
            rscp_a,

        "rscp_b":
            rscp_b,

        "ecno_a":
            ecno_a,

        "ecno_b":
            ecno_b,

        "rssi":
            rssi_dbm,

        "thermal_noise_dbm":
            float(
                thermal_noise_dbm
            )
    }