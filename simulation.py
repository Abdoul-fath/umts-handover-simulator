import numpy as np

from propagation import (
    calculate_radio_parameters
)

from handover import (
    run_handover_algorithm
)


# ============================================================
# CONVERSION
# ============================================================

def _float(
    data,
    key,
    label
):

    try:

        return float(
            data[key]
        )

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        raise ValueError(
            f"Valeur invalide : {label}."
        )


def _int(
    data,
    key,
    label
):

    try:

        return int(
            float(
                data[key]
            )
        )

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        raise ValueError(
            f"Valeur invalide : {label}."
        )


# ============================================================
# VALIDATION
# ============================================================

def validate_parameters(
    data
):

    p = {

        "node_distance_m":
            _float(
                data,
                "node_distance_m",
                "Distance entre Node B"
            ),

        "mobile_start_m":
            _float(
                data,
                "mobile_start_m",
                "Position du mobile"
            ),

        "speed_kmh":
            _float(
                data,
                "speed_kmh",
                "Vitesse du mobile"
            ),

        "tx_power_dbm":
            _float(
                data,
                "tx_power_dbm",
                "Puissance d'émission"
            ),

        "propagation_model":
            data.get(
                "propagation_model",
                ""
            ),

        "add_threshold_db":
            _float(
                data,
                "add_threshold_db",
                "Seuil d'ajout"
            ),

        "drop_threshold_db":
            _float(
                data,
                "drop_threshold_db",
                "Seuil de suppression"
            ),

        "hysteresis_db":
            _float(
                data,
                "hysteresis_db",
                "Hystérésis"
            ),

        "frequency_mhz":
            _float(
                data,
                "frequency_mhz",
                "Fréquence"
            ),

        "cpich_percent":
            _float(
                data,
                "cpich_percent",
                "CPICH"
            ),

        "exponent_n":
            _float(
                data,
                "exponent_n",
                "Exposant n"
            ),

        "shadowing_sigma_db":
            _float(
                data,
                "shadowing_sigma_db",
                "Shadowing sigma"
            ),

        "decorrelation_distance_m":
            _float(
                data,
                "decorrelation_distance_m",
                "Distance de décorrélation"
            ),

        "noise_figure_db":
            _float(
                data,
                "noise_figure_db",
                "Noise Figure"
            ),

        "bandwidth_mhz":
            _float(
                data,
                "bandwidth_mhz",
                "Bande WCDMA"
            ),

        "ttt_s":
            _float(
                data,
                "ttt_s",
                "Time-To-Trigger"
            ),

        "number_points":
            _int(
                data,
                "number_points",
                "Nombre de points"
            ),

        "pingpong_window_s":
            _float(
                data,
                "pingpong_window_s",
                "Fenêtre ping-pong"
            ),

        "seed":
            _int(
                data,
                "seed",
                "Seed aléatoire"
            )
    }

    if p["node_distance_m"] <= 0:

        raise ValueError(
            "La distance entre les Node B "
            "doit être positive."
        )

    if not (
        0
        <= p["mobile_start_m"]
        <= p["node_distance_m"]
    ):

        raise ValueError(
            "La position du mobile doit être "
            "entre 0 et la distance entre les Node B."
        )

    if p["speed_kmh"] <= 0:

        raise ValueError(
            "La vitesse doit être positive."
        )

    if p["number_points"] < 50:

        raise ValueError(
            "Utilisez au moins 50 points."
        )

    if p["frequency_mhz"] <= 0:

        raise ValueError(
            "La fréquence doit être positive."
        )

    if not (
        0
        < p["cpich_percent"]
        <= 100
    ):

        raise ValueError(
            "Le CPICH doit être entre 0 et 100 %."
        )

    if p["exponent_n"] <= 0:

        raise ValueError(
            "L'exposant n doit être positif."
        )

    if p["shadowing_sigma_db"] < 0:

        raise ValueError(
            "Le shadowing ne peut pas être négatif."
        )

    if (
        p["decorrelation_distance_m"]
        <= 0
    ):

        raise ValueError(
            "La distance de décorrélation "
            "doit être positive."
        )

    if p["bandwidth_mhz"] <= 0:

        raise ValueError(
            "La bande doit être positive."
        )

    if p["hysteresis_db"] < 0:

        raise ValueError(
            "L'hystérésis ne peut pas être négative."
        )

    if p["ttt_s"] < 0:

        raise ValueError(
            "Le TTT ne peut pas être négatif."
        )

    if p["pingpong_window_s"] < 0:

        raise ValueError(
            "La fenêtre ping-pong "
            "ne peut pas être négative."
        )

    if p["propagation_model"] not in (
        "log_distance",
        "free_space"
    ):

        raise ValueError(
            "Choisissez un modèle de propagation."
        )

    if (
        p["add_threshold_db"]
        <= p["drop_threshold_db"]
    ):

        raise ValueError(
            "Le seuil d'ajout doit être supérieur "
            "au seuil de suppression. "
            "Exemple : -15 dB / -18 dB."
        )

    return p


# ============================================================
# CONSTRUCTION DES ZONES CONTINUES
# ============================================================

def _build_continuous_zones(
    mask,
    positions,
    time_s
):

    mask = np.asarray(
        mask,
        dtype=bool
    )

    positions = np.asarray(
        positions,
        dtype=float
    )

    time_s = np.asarray(
        time_s,
        dtype=float
    )

    indexes = np.where(
        mask
    )[0]

    if len(indexes) == 0:

        return []

    groups = []

    start = int(
        indexes[0]
    )

    previous = int(
        indexes[0]
    )

    for index in indexes[1:]:

        index = int(
            index
        )

        if index != previous + 1:

            groups.append(
                (
                    start,
                    previous
                )
            )

            start = index

        previous = index

    groups.append(
        (
            start,
            previous
        )
    )

    zones = []

    for (
        start_index,
        end_index
    ) in groups:

        start_position = float(
            positions[start_index]
        )

        end_position = float(
            positions[end_index]
        )

        start_time = float(
            time_s[start_index]
        )

        end_time = float(
            time_s[end_index]
        )

        zones.append({

            "start_index":
                int(start_index),

            "end_index":
                int(end_index),

            "start_m":
                start_position,

            "end_m":
                end_position,

            "length_m":
                float(
                    abs(
                        end_position
                        - start_position
                    )
                ),

            "start_time_s":
                start_time,

            "end_time_s":
                end_time,

            "duration_s":
                float(
                    max(
                        0.0,
                        end_time
                        - start_time
                    )
                )
        })

    return zones


# ============================================================
# SOFT HANDOVER
# ============================================================

def get_soft_handover_zone(
    positions,
    time_s,
    active_state
):

    active_state = np.asarray(
        active_state,
        dtype=int
    )

    zones = _build_continuous_zones(
        active_state == 2,
        positions,
        time_s
    )

    if not zones:

        return {

            "detected":
                False,

            "count":
                0,

            "start_m":
                None,

            "end_m":
                None,

            "length_m":
                0.0,

            "start_time_s":
                None,

            "end_time_s":
                None,

            "duration_s":
                0.0,

            "total_length_m":
                0.0,

            "total_duration_s":
                0.0,

            "zones":
                []
        }

    largest = max(
        zones,
        key=lambda zone:
            zone["length_m"]
    )

    total_length_m = sum(
        zone["length_m"]
        for zone in zones
    )

    total_duration_s = sum(
        zone["duration_s"]
        for zone in zones
    )

    return {

        "detected":
            True,

        "count":
            len(zones),

        "start_m":
            largest["start_m"],

        "end_m":
            largest["end_m"],

        "length_m":
            largest["length_m"],

        "start_time_s":
            largest["start_time_s"],

        "end_time_s":
            largest["end_time_s"],

        "duration_s":
            largest["duration_s"],

        "total_length_m":
            float(total_length_m),

        "total_duration_s":
            float(total_duration_s),

        "zones":
            zones
    }


# ============================================================
# COUPURES
# ============================================================

def get_drop_zones(
    positions,
    time_s,
    outage_history
):

    zones = _build_continuous_zones(
        outage_history,
        positions,
        time_s
    )

    total_duration_s = sum(
        zone["duration_s"]
        for zone in zones
    )

    total_length_m = sum(
        zone["length_m"]
        for zone in zones
    )

    return {

        "detected":
            bool(
                len(zones) > 0
            ),

        "count":
            int(
                len(zones)
            ),

        "zones":
            zones,

        "total_duration_s":
            float(
                total_duration_s
            ),

        "total_length_m":
            float(
                total_length_m
            )
    }


# ============================================================
# CONVERSION PING-PONG -> POSITIONS
# ============================================================

def get_pingpong_positions(
    pingpong_events,
    positions,
    ecno_a,
    ecno_b
):
    """
    Transforme les index des événements ping-pong
    en positions réelles du mobile.

    On ajoute également les valeurs Ec/No au moment
    des deux changements de cellule.
    """

    result = []

    for event in pingpong_events:

        first_index = int(
            event["first_index"]
        )

        second_index = int(
            event["second_index"]
        )

        first_position = float(
            positions[first_index]
        )

        second_position = float(
            positions[second_index]
        )

        center_position = float(
            (
                first_position
                + second_position
            )
            / 2.0
        )

        sequence = (
            f"{event['first_from']}"
            f" → "
            f"{event['first_to']}"
            f" → "
            f"{event['second_to']}"
        )

        result.append({

            "start_m":
                first_position,

            "end_m":
                second_position,

            "center_m":
                center_position,

            "start_time_s":
                float(
                    event["first_time_s"]
                ),

            "end_time_s":
                float(
                    event["second_time_s"]
                ),

            "duration_s":
                float(
                    event["duration_s"]
                ),

            "sequence":
                sequence,

            "first_type":
                event["first_type"],

            "second_type":
                event["second_type"],

            "first_ecno_a_db":
                float(
                    ecno_a[first_index]
                ),

            "first_ecno_b_db":
                float(
                    ecno_b[first_index]
                ),

            "second_ecno_a_db":
                float(
                    ecno_a[second_index]
                ),

            "second_ecno_b_db":
                float(
                    ecno_b[second_index]
                )
        })

    return result


# ============================================================
# SIMULATION
# ============================================================

def run_simulation(
    data
):

    # --------------------------------------------------------
    # 1. PARAMETRES
    # --------------------------------------------------------

    p = validate_parameters(
        data
    )

    analysis_position = (
        p["mobile_start_m"]
    )

    # --------------------------------------------------------
    # 2. TRAJET COMPLET A -> B
    # --------------------------------------------------------

    start_position = 0.0

    end_position = (
        p["node_distance_m"]
    )

    positions = np.linspace(
        start_position,
        end_position,
        p["number_points"]
    )

    # --------------------------------------------------------
    # 3. TEMPS
    # --------------------------------------------------------

    speed_ms = (
        p["speed_kmh"]
        / 3.6
    )

    time_s = (
        positions
        / speed_ms
    )

    total_distance = (
        end_position
        - start_position
    )

    total_travel_time = (
        total_distance
        / speed_ms
    )

    analysis_time = (
        analysis_position
        / speed_ms
    )

    # --------------------------------------------------------
    # 4. POSITION ANALYSEE
    # --------------------------------------------------------

    analysis_index = int(
        np.argmin(
            np.abs(
                positions
                - analysis_position
            )
        )
    )

    # --------------------------------------------------------
    # 5. PARAMETRES RADIO
    # --------------------------------------------------------

    radio = calculate_radio_parameters(

        positions_m=
            positions,

        node_distance_m=
            p["node_distance_m"],

        tx_power_dbm=
            p["tx_power_dbm"],

        model=
            p["propagation_model"],

        frequency_mhz=
            p["frequency_mhz"],

        cpich_percent=
            p["cpich_percent"],

        exponent_n=
            p["exponent_n"],

        shadowing_sigma_db=
            p["shadowing_sigma_db"],

        decorrelation_distance_m=
            p["decorrelation_distance_m"],

        noise_figure_db=
            p["noise_figure_db"],

        bandwidth_mhz=
            p["bandwidth_mhz"],

        seed=
            p["seed"]
    )

    # --------------------------------------------------------
    # 6. ALGORITHME HANDOVER
    # --------------------------------------------------------

    handover = run_handover_algorithm(

        ecno_a=
            radio["ecno_a"],

        ecno_b=
            radio["ecno_b"],

        time_s=
            time_s,

        add_threshold_db=
            p["add_threshold_db"],

        drop_threshold_db=
            p["drop_threshold_db"],

        hysteresis_db=
            p["hysteresis_db"],

        ttt_s=
            p["ttt_s"],

        pingpong_window_s=
            p["pingpong_window_s"]
    )

    # --------------------------------------------------------
    # 7. SOFT HANDOVER
    # --------------------------------------------------------

    soft_zone = get_soft_handover_zone(

        positions,

        time_s,

        handover[
            "active_state"
        ]
    )

    # --------------------------------------------------------
    # 8. COUPURES
    # --------------------------------------------------------

    drop_info = get_drop_zones(

        positions,

        time_s,

        handover[
            "outage_history"
        ]
    )

    # --------------------------------------------------------
    # 9. POSITIONS DES PING-PONG
    # --------------------------------------------------------

    pingpong_info = get_pingpong_positions(

        handover[
            "pingpong_events"
        ],

        positions,

        radio[
            "ecno_a"
        ],

        radio[
            "ecno_b"
        ]
    )

    # --------------------------------------------------------
    # 10. CELLULE SERVANTE
    # --------------------------------------------------------

    serving_code = int(
        handover[
            "serving"
        ][
            analysis_index
        ]
    )

    if serving_code == 0:

        serving_cell = "A"

    elif serving_code == 1:

        serving_cell = "B"

    else:

        serving_cell = "Aucune"

    # --------------------------------------------------------
    # 11. ACTIVE SET
    # --------------------------------------------------------

    active_labels = {

        0:
            "∅",

        1:
            "{A}",

        2:
            "{A,B}",

        3:
            "{B}"
    }

    active_code = int(
        handover[
            "active_state"
        ][
            analysis_index
        ]
    )

    active_set = active_labels.get(
        active_code,
        "∅"
    )

    # --------------------------------------------------------
    # 12. RSCP POSITION ANALYSEE
    # --------------------------------------------------------

    rscp_a_at_position = float(
        np.interp(
            analysis_position,
            positions,
            radio["rscp_a"]
        )
    )

    rscp_b_at_position = float(
        np.interp(
            analysis_position,
            positions,
            radio["rscp_b"]
        )
    )

    # --------------------------------------------------------
    # 13. EC/NO POSITION ANALYSEE
    # --------------------------------------------------------

    ecno_a_at_position = float(
        np.interp(
            analysis_position,
            positions,
            radio["ecno_a"]
        )
    )

    ecno_b_at_position = float(
        np.interp(
            analysis_position,
            positions,
            radio["ecno_b"]
        )
    )

    # --------------------------------------------------------
    # 14. RESULTAT
    # --------------------------------------------------------

    return {

        "parameters":
            p,

        "movement": {

            "start_m":
                float(
                    start_position
                ),

            "end_m":
                float(
                    end_position
                ),

            "analysis_position_m":
                float(
                    analysis_position
                ),

            "analysis_time_s":
                float(
                    analysis_time
                ),

            "analysis_sample_m":
                float(
                    positions[
                        analysis_index
                    ]
                ),

            "distance_travelled_m":
                float(
                    total_distance
                ),

            "speed_kmh":
                float(
                    p["speed_kmh"]
                ),

            "speed_ms":
                float(
                    speed_ms
                ),

            "total_travel_time_s":
                float(
                    total_travel_time
                )
        },

        "summary": {

            "rscp": {

                "position_m":
                    float(
                        analysis_position
                    ),

                "a_dbm":
                    round(
                        rscp_a_at_position,
                        2
                    ),

                "b_dbm":
                    round(
                        rscp_b_at_position,
                        2
                    )
            },

            "ecno": {

                "position_m":
                    float(
                        analysis_position
                    ),

                "a_db":
                    round(
                        ecno_a_at_position,
                        2
                    ),

                "b_db":
                    round(
                        ecno_b_at_position,
                        2
                    )
            },

            "serving_cell":
                serving_cell,

            "active_set":
                active_set,

            "soft_handover_zone":
                soft_zone,

            "soft_handover_time_s":
                round(
                    float(
                        soft_zone[
                            "total_duration_s"
                        ]
                    ),
                    2
                ),

            "soft_handover_distance_m":
                round(
                    float(
                        soft_zone[
                            "total_length_m"
                        ]
                    ),
                    2
                ),

            "handover_count":
                int(
                    handover[
                        "handover_count"
                    ]
                ),

            "soft_handover_count":
                int(
                    handover[
                        "soft_handover_count"
                    ]
                ),

            "hard_handover_count":
                int(
                    handover[
                        "hard_handover_count"
                    ]
                ),

            "drop": {

                "detected":
                    bool(
                        drop_info[
                            "detected"
                        ]
                    ),

                "count":
                    int(
                        drop_info[
                            "count"
                        ]
                    ),

                "zones":
                    drop_info[
                        "zones"
                    ],

                "total_duration_s":
                    round(
                        float(
                            drop_info[
                                "total_duration_s"
                            ]
                        ),
                        2
                    ),

                "total_length_m":
                    round(
                        float(
                            drop_info[
                                "total_length_m"
                            ]
                        ),
                        2
                    )
            },

            "pingpong": {

                "detected":
                    bool(
                        handover[
                            "pingpong_detected"
                        ]
                    ),

                "count":
                    int(
                        handover[
                            "pingpong_count"
                        ]
                    ),

                "events":
                    pingpong_info
            }
        },

        "curves": {

            "position_m":
                positions.tolist(),

            "time_s":
                time_s.tolist(),

            "rscp_a":
                radio[
                    "rscp_a"
                ].tolist(),

            "rscp_b":
                radio[
                    "rscp_b"
                ].tolist(),

            "ecno_a":
                radio[
                    "ecno_a"
                ].tolist(),

            "ecno_b":
                radio[
                    "ecno_b"
                ].tolist(),

            "serving":
                handover[
                    "serving"
                ].tolist(),

            "active_state":
                handover[
                    "active_state"
                ].tolist(),

            "outage":
                handover[
                    "outage_history"
                ].astype(
                    int
                ).tolist()
        },

        "handover_events":
            handover[
                "handover_events"
            ],

        "soft_handover_events":
            handover[
                "soft_handover_events"
            ],

        "hard_handover_events":
            handover[
                "hard_handover_events"
            ],

        "drop_events":
            handover[
                "drop_events"
            ],

        "recovery_events":
            handover[
                "recovery_events"
            ],

        "pingpong_events":
            pingpong_info
    }


# ============================================================
# COMPARAISON
# ============================================================

def compare_simulations(
    scenarios
):

    rows = []

    for scenario in scenarios:

        name = scenario.get(
            "name",
            "Sans nom"
        )

        parameters = scenario.get(
            "parameters",
            {}
        )

        simulation = run_simulation(
            parameters
        )

        summary = simulation[
            "summary"
        ]

        movement = simulation[
            "movement"
        ]

        zone = summary[
            "soft_handover_zone"
        ]

        rows.append({

            "name":
                name,

            "analysis_position_m":
                round(
                    float(
                        movement[
                            "analysis_position_m"
                        ]
                    ),
                    2
                ),

            "speed_kmh":
                simulation[
                    "parameters"
                ][
                    "speed_kmh"
                ],

            "hysteresis_db":
                simulation[
                    "parameters"
                ][
                    "hysteresis_db"
                ],

            "serving_cell":
                summary[
                    "serving_cell"
                ],

            "active_set":
                summary[
                    "active_set"
                ],

            "soft_zone_m":
                round(
                    float(
                        zone[
                            "total_length_m"
                        ]
                    ),
                    2
                ),

            "soft_zone_count":
                int(
                    zone[
                        "count"
                    ]
                ),

            "soft_time_s":
                summary[
                    "soft_handover_time_s"
                ],

            "handover_count":
                summary[
                    "handover_count"
                ],

            "soft_handover_count":
                summary[
                    "soft_handover_count"
                ],

            "hard_handover_count":
                summary[
                    "hard_handover_count"
                ],

            "drop_count":
                summary[
                    "drop"
                ][
                    "count"
                ],

            "drop_detected":
                summary[
                    "drop"
                ][
                    "detected"
                ],

            "drop_duration_s":
                summary[
                    "drop"
                ][
                    "total_duration_s"
                ],

            "pingpong_count":
                summary[
                    "pingpong"
                ][
                    "count"
                ],

            "pingpong_detected":
                summary[
                    "pingpong"
                ][
                    "detected"
                ]
        })

    return rows