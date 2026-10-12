// ============================================================
// ELEMENTS PRINCIPAUX
// ============================================================

const form =
    document.getElementById("simulationForm");

const statusElement =
    document.getElementById("status");

const resultsElement =
    document.getElementById("results");

const emptyState =
    document.getElementById("emptyState");

const comparisonSection =
    document.getElementById("comparisonSection");

const STORAGE_KEY =
    "umts_handover_saved_scenarios_v6";


// ============================================================
// LECTURE NUMERIQUE
// ============================================================

function numberValue(id) {

    const element =
        document.getElementById(id);

    if (!element) {

        throw new Error(
            `Champ introuvable : ${id}`
        );
    }

    const value =
        element
            .value
            .trim()
            .replace(",", ".");

    if (value === "") {

        throw new Error(
            `Champ manquant : ${id}`
        );
    }

    const number =
        Number(value);

    if (!Number.isFinite(number)) {

        throw new Error(
            `Valeur numérique invalide : ${id}`
        );
    }

    return number;
}


// ============================================================
// PARAMETRES
// ============================================================

function getParameters() {

    return {

        node_distance_m:
            numberValue(
                "nodeDistance"
            ),

        mobile_start_m:
            numberValue(
                "mobileStart"
            ),

        speed_kmh:
            numberValue(
                "speed"
            ),

        tx_power_dbm:
            numberValue(
                "txPower"
            ),

        propagation_model:
            document
                .getElementById(
                    "propagationModel"
                )
                .value,

        add_threshold_db:
            numberValue(
                "addThreshold"
            ),

        drop_threshold_db:
            numberValue(
                "dropThreshold"
            ),

        hysteresis_db:
            numberValue(
                "hysteresis"
            ),

        frequency_mhz:
            numberValue(
                "frequency"
            ),

        cpich_percent:
            numberValue(
                "cpich"
            ),

        exponent_n:
            numberValue(
                "exponent"
            ),

        shadowing_sigma_db:
            numberValue(
                "shadowing"
            ),

        decorrelation_distance_m:
            numberValue(
                "decorrelation"
            ),

        noise_figure_db:
            numberValue(
                "noiseFigure"
            ),

        bandwidth_mhz:
            numberValue(
                "bandwidth"
            ),

        ttt_s:
            numberValue(
                "ttt"
            ),

        number_points:
            numberValue(
                "numberPoints"
            ),

        pingpong_window_s:
            numberValue(
                "pingpongWindow"
            ),

        seed:
            numberValue(
                "seed"
            )
    };
}


// ============================================================
// STATUS
// ============================================================

function setStatus(
    text,
    type
) {

    statusElement.textContent =
        "● " + text;

    statusElement.className =
        "status " + type;
}


// ============================================================
// VALIDATION
// ============================================================

function validateFrontendParameters(
    parameters
) {

    if (
        !parameters.propagation_model
    ) {

        throw new Error(
            "Choisissez un modèle de propagation."
        );
    }

    if (
        parameters.node_distance_m <= 0
    ) {

        throw new Error(
            "La distance entre les Node B doit être positive."
        );
    }

    if (
        parameters.mobile_start_m < 0
        ||
        parameters.mobile_start_m >
        parameters.node_distance_m
    ) {

        throw new Error(
            "La position du mobile doit être comprise entre 0 et la distance entre les Node B."
        );
    }

    if (
        parameters.speed_kmh <= 0
    ) {

        throw new Error(
            "La vitesse doit être positive."
        );
    }

    if (
        parameters.add_threshold_db
        <=
        parameters.drop_threshold_db
    ) {

        throw new Error(
            "Le seuil d'ajout doit être supérieur au seuil de suppression."
        );
    }

    if (
        parameters.hysteresis_db < 0
    ) {

        throw new Error(
            "L'hystérésis ne peut pas être négative."
        );
    }

    if (
        parameters.ttt_s < 0
    ) {

        throw new Error(
            "Le TTT ne peut pas être négatif."
        );
    }

    if (
        parameters.number_points < 50
    ) {

        throw new Error(
            "Utilisez au moins 50 points."
        );
    }
}


// ============================================================
// SIMULATION
// ============================================================

form.addEventListener(

    "submit",

    async event => {

        event.preventDefault();

        try {

            const parameters =
                getParameters();

            validateFrontendParameters(
                parameters
            );

            setStatus(
                "Simulation en cours",
                "running"
            );

            const response =
                await fetch(

                    "/api/simulate",

                    {
                        method:
                            "POST",

                        headers: {

                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                parameters
                            )
                    }
                );

            const data =
                await response.json();

            if (
                !response.ok
                ||
                !data.success
            ) {

                throw new Error(
                    data.error
                    ||
                    "Erreur pendant la simulation."
                );
            }

            renderSimulation(
                data.result
            );

            setStatus(
                "Simulation terminée",
                "success"
            );
        }

        catch (error) {

            console.error(error);

            setStatus(
                "Erreur",
                "error"
            );

            alert(
                error.message
            );
        }
    }
);


// ============================================================
// AFFICHAGE RESULTATS
// ============================================================

function renderSimulation(
    result
) {

    emptyState
        .classList
        .add("hidden");

    comparisonSection
        .classList
        .add("hidden");

    resultsElement
        .classList
        .remove("hidden");

    const summary =
        result.summary;

    const movement =
        result.movement;


    document
        .getElementById(
            "analysisPosition"
        )
        .textContent =
        `${movement.analysis_position_m.toFixed(1)} m`;


    document
        .getElementById(
            "analysisTime"
        )
        .textContent =
        `${movement.analysis_time_s.toFixed(2)} s`;


    document
        .getElementById(
            "journeyTime"
        )
        .textContent =
        `${movement.total_travel_time_s.toFixed(2)} s`;


    document
        .getElementById(
            "softTime"
        )
        .textContent =
        `${summary.soft_handover_time_s.toFixed(2)} s`;


    // --------------------------------------------------------
    // RSCP
    // --------------------------------------------------------

    document
        .getElementById(
            "resultRscp"
        )
        .innerHTML = `

            <span>
                A : ${summary.rscp.a_dbm} dBm
            </span>

            <span>
                B : ${summary.rscp.b_dbm} dBm
            </span>
        `;


    document
        .getElementById(
            "rscpPositionText"
        )
        .textContent =
        `À x = ${summary.rscp.position_m.toFixed(1)} m`;


    // --------------------------------------------------------
    // ECNO
    // --------------------------------------------------------

    document
        .getElementById(
            "resultEcno"
        )
        .innerHTML = `

            <span>
                A : ${summary.ecno.a_db} dB
            </span>

            <span>
                B : ${summary.ecno.b_db} dB
            </span>
        `;


    document
        .getElementById(
            "ecnoPositionText"
        )
        .textContent =
        `À x = ${summary.ecno.position_m.toFixed(1)} m`;


    // --------------------------------------------------------
    // SERVING
    // --------------------------------------------------------

    document
        .getElementById(
            "resultServing"
        )
        .textContent =
        summary.serving_cell;


    // --------------------------------------------------------
    // ACTIVE SET
    // --------------------------------------------------------

    document
        .getElementById(
            "resultActive"
        )
        .textContent =
        summary.active_set;


    // --------------------------------------------------------
    // SOFT
    // --------------------------------------------------------

    renderSoftZoneResult(
        summary.soft_handover_zone
    );


    // --------------------------------------------------------
    // HANDOVERS
    // --------------------------------------------------------

    document
        .getElementById(
            "resultHandover"
        )
        .textContent =
        summary.handover_count;


    document
        .getElementById(
            "resultSoftHandover"
        )
        .textContent =
        summary.soft_handover_count;


    document
        .getElementById(
            "resultHardHandover"
        )
        .textContent =
        summary.hard_handover_count;


    renderDropResults(
        summary.drop
    );


    renderPingPong(
        summary.pingpong
    );


    renderHandoverEvents(
        result
    );


    updateTrajectory(
        result
    );


    plotCharts(
        result
    );
}


// ============================================================
// SOFT ZONE
// ============================================================

function renderSoftZoneResult(
    softZone
) {

    const element =
        document.getElementById(
            "resultSoftZone"
        );

    if (
        !softZone.detected
    ) {

        element.textContent =
            "Aucune";

        return;
    }

    element.innerHTML = `

        ${softZone.total_length_m.toFixed(1)} m

        <small>
            ${softZone.count} zone(s)
            ·
            ${softZone.total_duration_s.toFixed(2)} s
        </small>
    `;
}


// ============================================================
// PING-PONG
// ============================================================

function renderPingPong(
    pingpong
) {

    const element =
        document.getElementById(
            "resultPingpong"
        );

    const details =
        document.getElementById(
            "pingpongDetails"
        );

    const list =
        document.getElementById(
            "pingpongEventsList"
        );


    if (
        !pingpong.detected
        ||
        !Array.isArray(
            pingpong.events
        )
        ||
        pingpong.events.length === 0
    ) {

        element.textContent =
            "Non";

        details
            .classList
            .add(
                "hidden"
            );

        list.innerHTML =
            "";

        return;
    }


    element.innerHTML = `

        Oui

        <small>
            ${pingpong.count}
            retour(s) rapide(s)
        </small>
    `;


    details
        .classList
        .remove(
            "hidden"
        );


    list.innerHTML =
        pingpong.events
            .map(
                (
                    event,
                    index
                ) => `

                    <div class="event-row">

                        <strong>
                            Ping-pong ${index + 1}
                        </strong>

                        <span>
                            ${event.sequence}
                        </span>

                        <span>

                            Position :

                            ${event.start_m.toFixed(1)}
                            →
                            ${event.end_m.toFixed(1)} m

                        </span>

                        <span>

                            Durée :
                            ${event.duration_s.toFixed(2)} s

                        </span>

                    </div>

                    <div class="event-row">

                        <strong>
                            Ec/No
                        </strong>

                        <span>

                            Début :
                            A =
                            ${event.first_ecno_a_db.toFixed(2)} dB

                            · B =
                            ${event.first_ecno_b_db.toFixed(2)} dB

                        </span>

                        <span>

                            Fin :
                            A =
                            ${event.second_ecno_a_db.toFixed(2)} dB

                            · B =
                            ${event.second_ecno_b_db.toFixed(2)} dB

                        </span>

                        <span>

                            t =
                            ${event.start_time_s.toFixed(2)}
                            →
                            ${event.end_time_s.toFixed(2)} s

                        </span>

                    </div>
                `
            )
            .join("");
}


// ============================================================
// COUPURES
// ============================================================

function renderDropResults(
    drop
) {

    const resultDrop =
        document.getElementById(
            "resultDrop"
        );

    const details =
        document.getElementById(
            "dropDetails"
        );

    const zonesList =
        document.getElementById(
            "dropZonesList"
        );


    if (
        !drop.detected
    ) {

        resultDrop.textContent =
            "Non";

        details
            .classList
            .add(
                "hidden"
            );

        zonesList.innerHTML =
            "";

        return;
    }


    resultDrop.innerHTML = `

        Oui

        <small>

            ${drop.count} coupure(s)
            ·
            ${drop.total_duration_s.toFixed(2)} s

        </small>
    `;


    details
        .classList
        .remove(
            "hidden"
        );


    zonesList.innerHTML =
        drop.zones
            .map(
                (
                    zone,
                    index
                ) => `

                    <div class="event-row drop-row">

                        <strong>
                            Coupure ${index + 1}
                        </strong>

                        <span>

                            Position :

                            ${zone.start_m.toFixed(1)}
                            →
                            ${zone.end_m.toFixed(1)} m

                        </span>

                        <span>

                            Temps :

                            ${zone.start_time_s.toFixed(2)}
                            →
                            ${zone.end_time_s.toFixed(2)} s

                        </span>

                        <span>

                            Durée :
                            ${zone.duration_s.toFixed(2)} s

                        </span>

                    </div>
                `
            )
            .join("");
}


// ============================================================
// EVENEMENTS DE HANDOVER
// ============================================================

function renderHandoverEvents(
    result
) {

    const section =
        document.getElementById(
            "handoverDetails"
        );

    const container =
        document.getElementById(
            "handoverEventsList"
        );

    const events =
        result.handover_events
        || [];


    if (
        events.length === 0
    ) {

        section
            .classList
            .add(
                "hidden"
            );

        container.innerHTML =
            "";

        return;
    }


    section
        .classList
        .remove(
            "hidden"
        );


    container.innerHTML =
        events
            .map(
                (
                    event,
                    index
                ) => {

                    const label =
                        event.type === "soft"
                            ? "Soft HO"
                            : "Hard HO";

                    return `

                        <div class="event-row">

                            <strong>
                                ${label} ${index + 1}
                            </strong>

                            <span>

                                ${event.from}
                                →
                                ${event.to}

                            </span>

                            <span>

                                Temps :
                                ${Number(event.time).toFixed(2)} s

                            </span>

                            <span>

                                Type :
                                ${event.type}

                            </span>

                        </div>
                    `;
                }
            )
            .join("");
}


// ============================================================
// TRAJET
// ============================================================

function updateTrajectory(
    result
) {

    const parameters =
        result.parameters;

    const movement =
        result.movement;

    const softInfo =
        result
            .summary
            .soft_handover_zone;

    const marker =
        document.getElementById(
            "ueMarker"
        );

    const container =
        document.getElementById(
            "softZonesTrack"
        );


    const ratio =
        movement.analysis_position_m
        /
        parameters.node_distance_m;


    marker.style.left =
        `${Math.max(
            0,
            Math.min(
                100,
                ratio * 100
            )
        )}%`;


    container.innerHTML =
        "";


    if (
        !softInfo.detected
        ||
        !Array.isArray(
            softInfo.zones
        )
    ) {

        return;
    }


    softInfo.zones.forEach(

        zone => {

            const element =
                document.createElement(
                    "div"
                );

            element.className =
                "soft-zone-track";


            const left =
                (
                    zone.start_m
                    /
                    parameters.node_distance_m
                )
                * 100;


            const width =
                (
                    zone.length_m
                    /
                    parameters.node_distance_m
                )
                * 100;


            element.style.display =
                "block";

            element.style.left =
                `${left}%`;

            element.style.width =
                `${Math.max(
                    width,
                    0.2
                )}%`;


            container.appendChild(
                element
            );
        }
    );
}


// ============================================================
// ZONES SOFT
// ============================================================

function softZoneShapes(
    result
) {

    const softInfo =
        result
            .summary
            .soft_handover_zone;


    if (
        !softInfo.detected
        ||
        !Array.isArray(
            softInfo.zones
        )
    ) {

        return [];
    }


    return softInfo.zones.map(

        zone => ({

            type:
                "rect",

            xref:
                "x",

            yref:
                "paper",

            x0:
                zone.start_m,

            x1:
                zone.end_m,

            y0:
                0,

            y1:
                1,

            fillcolor:
                "rgba(50,220,180,0.12)",

            line: {

                width:
                    0
            },

            layer:
                "below"
        })
    );
}


// ============================================================
// DROP ZONES
// ============================================================

function dropZoneShapes(
    result
) {

    const zones =
        result
            .summary
            .drop
            .zones
        || [];


    return zones.map(

        zone => ({

            type:
                "rect",

            xref:
                "x",

            yref:
                "paper",

            x0:
                zone.start_m,

            x1:
                zone.end_m,

            y0:
                0,

            y1:
                1,

            fillcolor:
                "rgba(255,80,100,0.16)",

            line: {

                width:
                    0
            },

            layer:
                "below"
        })
    );
}


// ============================================================
// POSITION ANALYSEE
// ============================================================

function analysisPositionShape(
    result
) {

    return {

        type:
            "line",

        xref:
            "x",

        yref:
            "paper",

        x0:
            result
                .movement
                .analysis_position_m,

        x1:
            result
                .movement
                .analysis_position_m,

        y0:
            0,

        y1:
            1,

        line: {

            color:
                "#36d9ef",

            width:
                2,

            dash:
                "dash"
        }
    };
}


// ============================================================
// LAYOUT
// ============================================================

function baseLayout(
    title,
    yTitle,
    result
) {

    return {

        title: {

            text:
                title,

            font: {

                size:
                    15
            }
        },

        paper_bgcolor:
            "rgba(0,0,0,0)",

        plot_bgcolor:
            "rgba(0,0,0,0)",

        font: {

            color:
                "#c9d9ea"
        },

        margin: {

            l:
                70,

            r:
                25,

            t:
                55,

            b:
                60
        },

        xaxis: {

            title:
                "Position du mobile (m)",

            range: [

                0,

                result
                    .parameters
                    .node_distance_m
            ],

            gridcolor:
                "#203b55",

            zerolinecolor:
                "#203b55"
        },

        yaxis: {

            title:
                yTitle,

            gridcolor:
                "#203b55",

            zerolinecolor:
                "#203b55"
        },

        shapes: [

            ...softZoneShapes(
                result
            ),

            ...dropZoneShapes(
                result
            ),

            analysisPositionShape(
                result
            )
        ],

        legend: {

            orientation:
                "h",

            x:
                0.5,

            xanchor:
                "center",

            y:
                1.12
        }
    };
}


// ============================================================
// GRAPHIQUES
// ============================================================

function plotCharts(
    result
) {

    const curves =
        result.curves;

    const x =
        curves.position_m;


    const config = {

        responsive:
            true,

        displaylogo:
            false,

        scrollZoom:
            false
    };


    // ========================================================
    // RSCP
    // ========================================================

    Plotly.react(

        "rscpChart",

        [

            {

                x:
                    x,

                y:
                    curves.rscp_a,

                type:
                    "scatter",

                mode:
                    "lines",

                name:
                    "Node B A",

                line: {

                    color:
                        "#4f9cff",

                    width:
                        2
                }
            },

            {

                x:
                    x,

                y:
                    curves.rscp_b,

                type:
                    "scatter",

                mode:
                    "lines",

                name:
                    "Node B B",

                line: {

                    color:
                        "#ff824d",

                    width:
                        2
                }
            }
        ],

        baseLayout(
            "RSCP = f(distance)",
            "RSCP (dBm)",
            result
        ),

        config
    );


    // ========================================================
    // ECNO
    // ========================================================

    const ecnoLayout =
        baseLayout(
            "Ec/No = f(distance)",
            "Ec/No (dB)",
            result
        );


    ecnoLayout.shapes = [

        ...softZoneShapes(
            result
        ),

        ...dropZoneShapes(
            result
        ),

        analysisPositionShape(
            result
        ),

        {

            type:
                "line",

            xref:
                "paper",

            yref:
                "y",

            x0:
                0,

            x1:
                1,

            y0:
                result
                    .parameters
                    .add_threshold_db,

            y1:
                result
                    .parameters
                    .add_threshold_db,

            line: {

                color:
                    "#8ba0b5",

                width:
                    1.5,

                dash:
                    "dash"
            }
        },

        {

            type:
                "line",

            xref:
                "paper",

            yref:
                "y",

            x0:
                0,

            x1:
                1,

            y0:
                result
                    .parameters
                    .drop_threshold_db,

            y1:
                result
                    .parameters
                    .drop_threshold_db,

            line: {

                color:
                    "#ff6577",

                width:
                    1.5,

                dash:
                    "dot"
            }
        }
    ];


    const ecnoTraces = [

        {

            x:
                x,

            y:
                curves.ecno_a,

            type:
                "scatter",

            mode:
                "lines",

            name:
                "Node B A",

            line: {

                color:
                    "#4f9cff",

                width:
                    2
            }
        },

        {

            x:
                x,

            y:
                curves.ecno_b,

            type:
                "scatter",

            mode:
                "lines",

            name:
                "Node B B",

            line: {

                color:
                    "#ff824d",

                width:
                    2
            }
        }
    ];


    // --------------------------------------------------------
    // MARQUEURS PING-PONG
    // --------------------------------------------------------

    const pingpong =
        result
            .summary
            .pingpong;


    if (
        pingpong.detected
        &&
        Array.isArray(
            pingpong.events
        )
        &&
        pingpong.events.length > 0
    ) {

        ecnoTraces.push({

            x:
                pingpong.events.map(
                    event =>
                        event.center_m
                ),

            y:
                pingpong.events.map(

                    event =>
                        Math.max(
                            event.second_ecno_a_db,
                            event.second_ecno_b_db
                        )
                ),

            type:
                "scatter",

            mode:
                "markers",

            name:
                "Ping-pong",

            marker: {

                symbol:
                    "x",

                size:
                    11,

                color:
                    "#ff4d67",

                line: {

                    width:
                        2
                }
            },

            text:
                pingpong.events.map(

                    (
                        event,
                        index
                    ) =>

                        `Ping-pong ${index + 1}<br>`
                        +
                        `${event.sequence}<br>`
                        +
                        `${event.start_m.toFixed(1)} → ${event.end_m.toFixed(1)} m`
                ),

            hovertemplate:
                "%{text}<extra></extra>"
        });
    }


    Plotly.react(

        "ecnoChart",

        ecnoTraces,

        ecnoLayout,

        config
    );


    // ========================================================
    // CELLULE SERVANTE
    // ========================================================

    const servingLayout =
        baseLayout(

            "Évolution de la cellule servante",

            "Cellule",

            result
        );


    servingLayout.yaxis = {

        title:
            "Cellule servante",

        tickmode:
            "array",

        tickvals: [

            -1,
            0,
            1
        ],

        ticktext: [

            "Coupure",
            "A",
            "B"
        ],

        range: [

            -1.4,
            1.4
        ],

        gridcolor:
            "#203b55"
    };


    Plotly.react(

        "servingChart",

        [

            {

                x:
                    x,

                y:
                    curves.serving,

                type:
                    "scatter",

                mode:
                    "lines",

                name:
                    "Cellule servante",

                line: {

                    color:
                        "#35d7ef",

                    width:
                        3,

                    shape:
                        "hv"
                }
            }
        ],

        servingLayout,

        config
    );


    // ========================================================
    // ACTIVE SET
    // ========================================================

    const activeLayout =
        baseLayout(

            "Évolution de l’Active Set",

            "Active Set",

            result
        );


    activeLayout.yaxis = {

        title:
            "Active Set",

        tickmode:
            "array",

        tickvals: [

            0,
            1,
            2,
            3
        ],

        ticktext: [

            "∅",
            "{A}",
            "{A,B}",
            "{B}"
        ],

        range: [

            -0.4,
            3.4
        ],

        gridcolor:
            "#203b55"
    };


    Plotly.react(

        "activeChart",

        [

            {

                x:
                    x,

                y:
                    curves.active_state,

                type:
                    "scatter",

                mode:
                    "lines",

                name:
                    "Active Set",

                line: {

                    color:
                        "#42e0af",

                    width:
                        3,

                    shape:
                        "hv"
                }
            }
        ],

        activeLayout,

        config
    );
}


// ============================================================
// LOCAL STORAGE
// ============================================================

function loadScenarios() {

    try {

        return JSON.parse(

            localStorage.getItem(
                STORAGE_KEY
            )

            ||

            "[]"
        );
    }

    catch {

        return [];
    }
}


function escapeHtml(
    text
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        text;

    return div.innerHTML;
}


// ============================================================
// SUPPRESSION CONFIGURATION
// ============================================================

function deleteScenario(
    id
) {

    const scenarios =
        loadScenarios()
            .filter(

                scenario =>
                    scenario.id !== id
            );


    localStorage.setItem(

        STORAGE_KEY,

        JSON.stringify(
            scenarios
        )
    );


    renderSavedScenarios();
}


window.deleteScenario =
    deleteScenario;


// ============================================================
// CONFIGURATIONS SAUVEGARDEES
// ============================================================

function renderSavedScenarios() {

    const scenarios =
        loadScenarios();


    const count =
        document.getElementById(
            "savedCount"
        );


    const button =
        document.getElementById(
            "compareButton"
        );


    const container =
        document.getElementById(
            "savedScenarios"
        );


    count.textContent =
        scenarios.length;


    button.disabled =
        scenarios.length < 2;


    if (
        scenarios.length === 0
    ) {

        container.innerHTML = `

            <p class="empty">
                Aucune configuration enregistrée.
            </p>
        `;

        return;
    }


    container.innerHTML =
        scenarios
            .map(

                scenario => `

                    <div class="saved-item">

                        <span>

                            ${escapeHtml(
                                scenario.name
                            )}

                        </span>

                        <button
                            type="button"
                            onclick="deleteScenario(${scenario.id})"
                        >

                            ×

                        </button>

                    </div>
                `
            )
            .join("");
}


// ============================================================
// SAUVEGARDE
// ============================================================

document
    .getElementById(
        "saveScenario"
    )
    .addEventListener(

        "click",

        () => {

            try {

                const parameters =
                    getParameters();


                validateFrontendParameters(
                    parameters
                );


                const name =
                    document
                        .getElementById(
                            "scenarioName"
                        )
                        .value
                        .trim();


                if (!name) {

                    throw new Error(
                        "Donnez un nom à la configuration."
                    );
                }


                const scenarios =
                    loadScenarios();


                scenarios.push({

                    id:
                        Date.now(),

                    name:
                        name,

                    parameters:
                        parameters
                });


                localStorage.setItem(

                    STORAGE_KEY,

                    JSON.stringify(
                        scenarios
                    )
                );


                renderSavedScenarios();


                setStatus(
                    "Configuration enregistrée",
                    "success"
                );
            }

            catch (error) {

                alert(
                    error.message
                );
            }
        }
    );


// ============================================================
// COMPARAISON
// ============================================================

document
    .getElementById(
        "compareButton"
    )
    .addEventListener(

        "click",

        async () => {

            const scenarios =
                loadScenarios();


            if (
                scenarios.length < 2
            ) {

                return;
            }


            try {

                setStatus(
                    "Comparaison en cours",
                    "running"
                );


                const response =
                    await fetch(

                        "/api/compare",

                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify({

                                    scenarios:
                                        scenarios
                                })
                        }
                    );


                const data =
                    await response.json();


                if (
                    !response.ok
                    ||
                    !data.success
                ) {

                    throw new Error(

                        data.error
                        ||
                        "Erreur de comparaison."
                    );
                }


                renderComparison(
                    data.result
                );


                setStatus(
                    "Comparaison terminée",
                    "success"
                );
            }

            catch (error) {

                console.error(
                    error
                );


                setStatus(
                    "Erreur",
                    "error"
                );


                alert(
                    error.message
                );
            }
        }
    );


// ============================================================
// TABLEAU COMPARAISON
// ============================================================

function renderComparison(
    rows
) {

    resultsElement
        .classList
        .add(
            "hidden"
        );


    emptyState
        .classList
        .add(
            "hidden"
        );


    comparisonSection
        .classList
        .remove(
            "hidden"
        );


    const body =
        document.getElementById(
            "comparisonBody"
        );


    body.innerHTML =
        rows
            .map(

                row => `

                    <tr>

                        <td>
                            ${escapeHtml(row.name)}
                        </td>

                        <td>
                            ${row.analysis_position_m} m
                        </td>

                        <td>
                            ${row.speed_kmh} km/h
                        </td>

                        <td>
                            ${row.hysteresis_db} dB
                        </td>

                        <td>
                            ${row.serving_cell}
                        </td>

                        <td>
                            ${row.active_set}
                        </td>

                        <td>

                            ${row.soft_zone_m} m

                            <br>

                            <small>
                                ${row.soft_zone_count} zone(s)
                            </small>

                        </td>

                        <td>
                            ${row.soft_time_s} s
                        </td>

                        <td>
                            ${row.handover_count}
                        </td>

                        <td>
                            ${row.soft_handover_count}
                        </td>

                        <td>
                            ${row.hard_handover_count}
                        </td>

                        <td>

                            ${
                                row.drop_detected

                                ?

                                `Oui (${row.drop_count})`

                                :

                                "Non"
                            }

                        </td>

                        <td>
                            ${row.drop_duration_s} s
                        </td>

                        <td>

                            ${
                                row.pingpong_detected

                                ?

                                `Oui (${row.pingpong_count})`

                                :

                                "Non"
                            }

                        </td>

                    </tr>
                `
            )
            .join("");
}


// ============================================================
// FERMETURE COMPARAISON
// ============================================================

document
    .getElementById(
        "closeComparison"
    )
    .addEventListener(

        "click",

        () => {

            comparisonSection
                .classList
                .add(
                    "hidden"
                );


            resultsElement
                .classList
                .remove(
                    "hidden"
                );
        }
    );


// ============================================================
// DEMARRAGE
// ============================================================

renderSavedScenarios();