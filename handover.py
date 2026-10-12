import numpy as np


# ============================================================
# OUTILS
# ============================================================

def _samples_for_duration(duration_s, dt_s):
    """
    Convertit une durée exprimée en secondes
    en nombre d'échantillons.
    """

    if duration_s <= 0:
        return 1

    return max(
        1,
        int(
            np.ceil(
                duration_s
                / max(float(dt_s), 1e-9)
            )
        )
    )


# ============================================================
# DETECTION PING-PONG
# ============================================================

def detect_pingpong(
    handover_events,
    window_seconds
):
    """
    Détecte un ping-pong lorsqu'on observe :

        A -> B
        puis
        B -> A

    ou :

        B -> A
        puis
        A -> B

    dans une durée <= window_seconds.

    Contrairement à l'ancienne version,
    on conserve maintenant les événements complets,
    notamment les index et les temps.

    Cela permettra ensuite à simulation.py de convertir
    les index en positions réelles du mobile.
    """

    pingpong_events = []

    if (
        window_seconds <= 0
        or len(handover_events) < 2
    ):
        return pingpong_events

    for i in range(
        1,
        len(handover_events)
    ):

        previous = handover_events[i - 1]
        current = handover_events[i]

        reverse = (
            previous["from"] == current["to"]
            and
            previous["to"] == current["from"]
        )

        delta_t = (
            current["time"]
            - previous["time"]
        )

        fast = (
            0 <= delta_t <= window_seconds
        )

        if reverse and fast:

            pingpong_events.append({

                "first_time_s":
                    float(previous["time"]),

                "second_time_s":
                    float(current["time"]),

                "first_index":
                    int(previous["index"]),

                "second_index":
                    int(current["index"]),

                "first_from":
                    previous["from"],

                "first_to":
                    previous["to"],

                "second_from":
                    current["from"],

                "second_to":
                    current["to"],

                "duration_s":
                    float(delta_t),

                "first_type":
                    previous["type"],

                "second_type":
                    current["type"]
            })

    return pingpong_events


# ============================================================
# ALGORITHME DE HANDOVER
# ============================================================

def run_handover_algorithm(
    ecno_a,
    ecno_b,
    time_s,
    add_threshold_db,
    drop_threshold_db,
    hysteresis_db,
    ttt_s,
    pingpong_window_s
):
    """
    Simulation pédagogique du handover entre deux Node B.

    CELLULE SERVANTE
    ----------------
        -1 = aucune cellule / coupure
         0 = Node B A
         1 = Node B B


    ACTIVE SET
    ----------
         0 = ensemble vide
         1 = {A}
         2 = {A,B}
         3 = {B}


    SOFT HANDOVER
    -------------
        {A}
          ↓
        {A,B}
          ↓
        Serving A -> B
          ↓
        {B}


    HARD HANDOVER
    -------------
        {A}
          ↓
        A devient trop faible
          ↓
        B reste utilisable
          ↓
        A -> B directement


    COUPURE / DROP
    --------------
    Si :

        Ec/No A < seuil suppression
        ET
        Ec/No B < seuil suppression

    pendant le TTT :

        serving = aucune
        Active Set = vide
    """

    # ========================================================
    # CONVERSIONS
    # ========================================================

    ecno_a = np.asarray(
        ecno_a,
        dtype=float
    )

    ecno_b = np.asarray(
        ecno_b,
        dtype=float
    )

    time_s = np.asarray(
        time_s,
        dtype=float
    )

    # ========================================================
    # VALIDATIONS
    # ========================================================

    if not (
        len(ecno_a)
        == len(ecno_b)
        == len(time_s)
    ):
        raise ValueError(
            "Ec/No A, Ec/No B et temps "
            "doivent avoir la même taille."
        )

    number_points = len(ecno_a)

    if number_points < 2:
        raise ValueError(
            "Nombre de points insuffisant."
        )

    # ========================================================
    # PAS TEMPOREL
    # ========================================================

    dt_s = float(
        np.mean(
            np.diff(time_s)
        )
    )

    if dt_s <= 0:
        raise ValueError(
            "Le vecteur temps doit être croissant."
        )

    ttt_samples = _samples_for_duration(
        ttt_s,
        dt_s
    )

    # ========================================================
    # ETAT INITIAL
    # ========================================================

    if ecno_a[0] >= ecno_b[0]:

        serving = 0

        active_a = True
        active_b = False

    else:

        serving = 1

        active_a = False
        active_b = True

    service_available = True

    # ========================================================
    # HISTORIQUES
    # ========================================================

    serving_history = np.full(
        number_points,
        -1,
        dtype=int
    )

    active_state = np.zeros(
        number_points,
        dtype=int
    )

    outage_history = np.zeros(
        number_points,
        dtype=bool
    )

    # ========================================================
    # COMPTEURS TTT
    # ========================================================

    add_counter = 0
    soft_switch_counter = 0
    hard_switch_counter = 0
    remove_counter = 0

    outage_counter = 0
    recovery_counter = 0

    # ========================================================
    # EVENEMENTS
    # ========================================================

    handover_events = []

    soft_handover_events = []

    hard_handover_events = []

    drop_events = []

    recovery_events = []

    # ========================================================
    # BOUCLE PRINCIPALE
    # ========================================================

    for i in range(number_points):

        qa = float(ecno_a[i])
        qb = float(ecno_b[i])

        # ====================================================
        # 1. DETECTION COUPURE
        # ====================================================

        both_bad = (
            qa < drop_threshold_db
            and
            qb < drop_threshold_db
        )

        if service_available:

            if both_bad:
                outage_counter += 1

            else:
                outage_counter = 0

            if outage_counter >= ttt_samples:

                drop_events.append({

                    "time":
                        float(time_s[i]),

                    "index":
                        int(i),

                    "type":
                        "drop",

                    "reason":
                        (
                            "Ec/No A et Ec/No B "
                            "sous le seuil de suppression."
                        )
                })

                service_available = False

                serving = -1

                active_a = False
                active_b = False

                outage_counter = 0
                recovery_counter = 0

                add_counter = 0
                soft_switch_counter = 0
                hard_switch_counter = 0
                remove_counter = 0

        # ====================================================
        # 2. RECUPERATION APRES COUPURE
        # ====================================================

        if not service_available:

            best_quality = max(
                qa,
                qb
            )

            if best_quality >= drop_threshold_db:
                recovery_counter += 1

            else:
                recovery_counter = 0

            if recovery_counter >= ttt_samples:

                if qa >= qb:

                    serving = 0

                    active_a = True
                    active_b = False

                else:

                    serving = 1

                    active_a = False
                    active_b = True

                service_available = True

                recovery_events.append({

                    "time":
                        float(time_s[i]),

                    "index":
                        int(i),

                    "cell":
                        (
                            "A"
                            if serving == 0
                            else "B"
                        )
                })

                recovery_counter = 0
                outage_counter = 0

        # ====================================================
        # 3. SERVICE DISPONIBLE
        # ====================================================

        if service_available:

            # =================================================
            # CAS A : ACTIVE SET = {A,B}
            # =================================================

            if active_a and active_b:

                hard_switch_counter = 0
                add_counter = 0

                # ---------------------------------------------
                # SOFT SWITCH
                # ---------------------------------------------

                if serving == 0:

                    q_serving = qa
                    q_target = qb

                    target = 1

                else:

                    q_serving = qb
                    q_target = qa

                    target = 0

                condition_soft_switch = (
                    q_target
                    >=
                    q_serving + hysteresis_db
                )

                if condition_soft_switch:

                    soft_switch_counter += 1

                else:

                    soft_switch_counter = 0

                if soft_switch_counter >= ttt_samples:

                    old_serving = serving

                    serving = target

                    event = {

                        "time":
                            float(time_s[i]),

                        "index":
                            int(i),

                        "from":
                            (
                                "A"
                                if old_serving == 0
                                else "B"
                            ),

                        "to":
                            (
                                "A"
                                if serving == 0
                                else "B"
                            ),

                        "type":
                            "soft"
                    }

                    handover_events.append(
                        event
                    )

                    soft_handover_events.append(
                        event
                    )

                    soft_switch_counter = 0

                # ---------------------------------------------
                # RETRAIT DE L'ANCIENNE CELLULE
                # ---------------------------------------------

                if serving == 0:

                    old_quality = qb

                    serving_quality = qa

                    old_cell = 1

                else:

                    old_quality = qa

                    serving_quality = qb

                    old_cell = 0

                condition_remove = (

                    old_quality
                    <= drop_threshold_db

                    and

                    serving_quality
                    >= old_quality + hysteresis_db
                )

                if condition_remove:

                    remove_counter += 1

                else:

                    remove_counter = 0

                if remove_counter >= ttt_samples:

                    if old_cell == 0:
                        active_a = False

                    else:
                        active_b = False

                    remove_counter = 0

            # =================================================
            # CAS B : UNE SEULE CELLULE ACTIVE
            # =================================================

            else:

                soft_switch_counter = 0

                remove_counter = 0

                if serving == 0:

                    q_serving = qa

                    q_other = qb

                    other = 1

                else:

                    q_serving = qb

                    q_other = qa

                    other = 0

                # ---------------------------------------------
                # B1. AJOUT CELLULE VOISINE
                # ---------------------------------------------

                condition_add = (

                    q_other
                    >= add_threshold_db

                    and

                    q_other
                    >= q_serving - hysteresis_db
                )

                if condition_add:

                    add_counter += 1

                else:

                    add_counter = 0

                if add_counter >= ttt_samples:

                    if other == 0:
                        active_a = True

                    else:
                        active_b = True

                    add_counter = 0

                    hard_switch_counter = 0

                # ---------------------------------------------
                # B2. HARD HANDOVER
                # ---------------------------------------------

                both_active = (
                    active_a
                    and active_b
                )

                if not both_active:

                    condition_hard = (

                        q_serving
                        <= drop_threshold_db

                        and

                        q_other
                        >= drop_threshold_db

                        and

                        q_other
                        >= q_serving + hysteresis_db
                    )

                    if condition_hard:

                        hard_switch_counter += 1

                    else:

                        hard_switch_counter = 0

                    if hard_switch_counter >= ttt_samples:

                        old_serving = serving

                        serving = other

                        if serving == 0:

                            active_a = True
                            active_b = False

                        else:

                            active_a = False
                            active_b = True

                        event = {

                            "time":
                                float(time_s[i]),

                            "index":
                                int(i),

                            "from":
                                (
                                    "A"
                                    if old_serving == 0
                                    else "B"
                                ),

                            "to":
                                (
                                    "A"
                                    if serving == 0
                                    else "B"
                                ),

                            "type":
                                "hard"
                        }

                        handover_events.append(
                            event
                        )

                        hard_handover_events.append(
                            event
                        )

                        hard_switch_counter = 0
                        add_counter = 0

        # ====================================================
        # 4. MEMORISATION ETAT
        # ====================================================

        if not service_available:

            serving_history[i] = -1

            active_state[i] = 0

            outage_history[i] = True

        else:

            serving_history[i] = serving

            outage_history[i] = False

            if active_a and active_b:

                active_state[i] = 2

            elif active_a:

                active_state[i] = 1

            elif active_b:

                active_state[i] = 3

            else:

                serving_history[i] = -1

                active_state[i] = 0

                outage_history[i] = True

    # ========================================================
    # PING-PONG
    # ========================================================

    pingpong_events = detect_pingpong(
        handover_events,
        pingpong_window_s
    )

    pingpong_count = len(
        pingpong_events
    )

    # ========================================================
    # RESULTAT
    # ========================================================

    return {

        "serving":
            serving_history,

        "active_state":
            active_state,

        "outage_history":
            outage_history,

        "handover_events":
            handover_events,

        "handover_count":
            len(handover_events),

        "soft_handover_events":
            soft_handover_events,

        "soft_handover_count":
            len(soft_handover_events),

        "hard_handover_events":
            hard_handover_events,

        "hard_handover_count":
            len(hard_handover_events),

        "drop_events":
            drop_events,

        "drop_count":
            len(drop_events),

        "recovery_events":
            recovery_events,

        "pingpong_events":
            pingpong_events,

        "pingpong_count":
            int(pingpong_count),

        "pingpong_detected":
            bool(
                pingpong_count > 0
            )
    }