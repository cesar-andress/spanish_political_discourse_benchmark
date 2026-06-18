# Pragmatic function annotation — worked examples (SPDB v1)

**Ontology:** `labels/pragmatic_functions.tsv`  
**Label IDs:** exactly one `PF_*` per discourse unit (mutually exclusive)  
**Example source:** real units from ParlaMint-ES sessions ingested locally and segmented into SPDB discourse units (`data/processed/parlamint_100_units.jsonl` and `data/processed/parlamint_units.jsonl`).  
**Provenance:** ParlaMint 5.0 Spanish corpus (see `docs/sources/parlamint.md`).

Use these examples for pilot and full annotation training. Quotes are **truncated** where the full unit mixes functions; label the **entire unit**, not the excerpt alone.

---

## PF_ADVOCACY — Policy advocacy

### Definition

Supports or advances a policy position, programme, or normative goal.

### Decision rule

Label `PF_ADVOCACY` when the dominant move is to **argue in favour of** (or against) a policy, law, or normative outcome, including reasoned criticism of a **policy design** (not primarily of a person's character). If the span mainly rebuts an attack on the speaker's group, use `PF_DEFENSE`. If it mainly lists facts without evaluative policy thrust, consider `PF_INFO`.

### Positive examples (ParlaMint sample)

> «En Ciudadanos abogamos […] que se tenía que definir la figura del consumidor vulnerable, que se tenía que definir la figura del consumidor vulnerable en situación extrema, que se tenía que fijar un criterio de renta […]»

— Melisa Rodríguez Hernández (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-ceada2c252a1`.

> «Es el caso, por ejemplo, de la venta de pisos sociales a fondos buitre o es el caso de la reforma fiscal del Gobierno que adaptó las reglas del juego al interés de las Socimi.»

— Enric Bataller Ruiz (CPEUPV, 2017-09-19). Unit: `spdb-v1-unassigned-5e620d9cdeb3`.

> «Mejor una ley que un decreto ley, pero mejor una ley de bases que una ley exhaustiva que no lo puede tocar todo.»

— Joan Olòriz Serra (ERCCATSÍ, 2017-11-28). Unit: `spdb-v1-unassigned-b57f53b63185`.

### Negative examples (same corpus)

> «Contratos temporales. Tienen ustedes la osadía de hablar de la contratación temporal cuando precisamente la reforma del año 1984 es la que rompe el principio de causalidad […]»

— Carolina España Reina (PP, 2017-09-19). Unit: `spdb-v1-unassigned-c6349a3fb522`.  
**Not advocacy:** dominant move is **attacking** opponents' record (`PF_ATTACK`), not advancing a constructive policy programme.

> «Muchas gracias. En el turno de fijación de posiciones […] tiene la palabra […] el señor Alli Martínez.»

— Presidencia (2017-09-19). Unit: `spdb-v1-unassigned-05d607df9c93`.  
**Not advocacy:** chamber management (`PF_PROCEDURAL`).

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ATTACK` | Advocacy criticises **policy**; attack targets **actor competence, integrity, or record**. |
| `PF_PROPOSAL` | Proposal **commits** to a future action; advocacy **argues for** a position (may include reasons, not necessarily a pledge). |
| `PF_INFO` | Advocacy embeds facts in a **normative** argument; info presents facts with **minimal** evaluative framing. |

---

## PF_ATTACK — Position attack

### Definition

Challenges an actor's competence, integrity, legitimacy, or record.

### Decision rule

Label `PF_ATTACK` when the primary target is a **political actor or group** (party, government, opponent), not merely a policy abstractly. Personalised charges, record comparisons, and legitimacy challenges qualify. Evidence-based policy disagreement without personal targeting is usually `PF_ADVOCACY`.

### Positive examples (ParlaMint sample)

> «Lo que no tenemos nada regulado, y es un enorme fraude, son los pretendidos contratos de aprendizaje, que son un bosque de fraude.»

— Joan Olòriz Serra (ERCCATSÍ, 2017-11-28). Unit: `spdb-v1-unassigned-b57f53b63185`.  
*(Note: “fraude” here attacks the regulatory situation and implied bad faith; if the full unit balances policy critique, check whether attack or advocacy dominates.)*

> «Lo que sí es indigno son los salarios de miseria, la explotación de los trabajadores o la discriminación de las mujeres.»

— Adriana Lastra Fernández (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-35a6117f0c82`.

> «Han dicho ustedes que han evitado la subida del IVA […] No es así, señora Arrimadas, no es así. Ustedes ni siquiera han estado sentados en la mesa donde se tomaban estas decisiones […] tampoco han conseguido nada, señora Arrimadas, nada.»

— Pablo Echenique Robba (UP, 2020-11-12). Unit: `spdb-v1-unassigned-b2eaf6b9bc1c`.

> «Lo que se le ocurrió a la que entonces era ministra de Fomento, Ana Pastor, fue presentar una reforma de la LAU que […] serviría para agilizar los desahucios […] Pura retórica de la burbuja en pleno estallido de la misma.»

— Lucía Martín González (ECP, 2017-09-19). Unit: `spdb-v1-unassigned-1b02f725631c`.

### Negative examples

> «Gracias, señora presidenta. El Grupo Parlamentario Socialista nos ha traído una proposición de ley con el propósito de introducir tres modificaciones en la ley 3/2007 […] son tres principalmente las reformas que plantea esta proposición de ley […]»

— Joseba Agirretxea Urresti (EAJPNV, 2017-11-28). Unit: `spdb-v1-unassigned-eb453642ca5f`.  
**Not attack:** neutral **exposition** of bill content (`PF_INFO`).

> «A todos los españoles y a todas las españolas queremos transmitirles un mensaje de esperanza.»

— María Montero Cuadrado (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-2063abcb1366`.  
**Not attack:** **mobilisation** (`PF_APPEAL`).

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ADVOCACY` | Attack centres on **who** is wrong or untrustworthy; advocacy centres on **what** should be done. |
| `PF_DEFENSE` | Defense **rebuts** criticism directed at self/party; attack **initiates** criticism toward others. |
| `PF_DEFLECT` | Deflect **avoids** the question; attack may answer indirectly by counter-charging opponents. |

Fallacy labels (`FAL_*`) are **independent**: a unit can be `PF_ATTACK` with or without `FAL_ADHOM`.

---

## PF_DEFENSE — Defense / rebuttal

### Definition

Rebuts criticism or protects actor or policy reputation.

### Decision rule

Label `PF_DEFENSE` when the speaker responds to **prior or implied criticism** by denying, correcting, or shielding their party, government, or policy. Proactive criticism of others is `PF_ATTACK`. Thanking allies for supporting one's position can be defense when framed as reputational reinforcement.

### Positive examples (ParlaMint sample)

> «Muy brevemente, presidenta. Muchas gracias, señora Lastra y señor Echenique, por sus intervenciones en el turno de fijación de posiciones en defensa de este proyecto de Presupuestos del Estado. […] Me siento orgullosa de ser andaluza, y le puedo asegurar que no me van a distraer […]»

— María Montero Cuadrado (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-082ee9dc9ec7`.

> «Contratos temporales. Tienen ustedes la osadía de hablar de la contratación temporal cuando precisamente la reforma del año 1984 es la que rompe el principio de causalidad […] ¿No nos acordamos de cuando Zapatero encadenó, sin fin, los contratos temporales? […] Falso, no llegan ni al 1 %.»

— Carolina España Reina (PP, 2017-09-19). Unit: `spdb-v1-unassigned-c6349a3fb522`.  
*(Rebuttal of opponents' claims about temporary contracts and fiscal record.)*

> «Cuando he oído a la representante de Ciudadanos decirles que ustedes […] conoce mejor que nadie de su capacidad para llegar a acuerdos, a mí algo me ha resultado raro. Los únicos acuerdos que recuerdo […] son con el Partido Popular […]»

— Oskar Matute García Jalón (ECUP, 2020-11-12). Unit: `spdb-v1-unassigned-405d9499b876`.

### Negative examples

> «Han dicho ustedes que han evitado la subida del IVA […] No es así, señora Arrimadas.»

— Pablo Echenique Robba (UP, 2020-11-12). Unit: `spdb-v1-unassigned-b2eaf6b9bc1c`.  
**Not defense:** speaker **attacks** opponent (`PF_ATTACK`), not protecting own group from attack.

> «Con todo el respeto, creemos que no tiene por qué ser efectiva, sino que ya es efectiva para regular el mercado de viviendas […] nos vemos obligados a abstenernos en esta votación.»

— Íñigo Barandiaran Benito (EAJPNV, 2017-09-19). Unit: `spdb-v1-unassigned-7bc5528e899b`.  
**Not defense:** reasoned **position-taking** on a bill (closer to `PF_ADVOCACY` / voting stance), not rebuttal of a personal attack.

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ATTACK` | Defense is **reactive** to criticism; attack is **offensive** toward a target. |
| `PF_ADVOCACY` | Defense protects **reputation or prior record**; advocacy promotes **policy merits**. |
| `PF_INFO` | “Falso, no llegan ni al 1 %” is defense when correcting opponents' factual claims in a rebuttal context. |

---

## PF_PROPOSAL — Proposal / commitment

### Definition

Commits to future action, concrete measure, or implementation pledge.

### Decision rule

Label `PF_PROPOSAL` when the span contains an explicit **forward-looking commitment** (legislative initiative, amendment, vote intention tied to action, implementation pledge). General policy praise or criticism without a commitment is `PF_ADVOCACY`. Announcing what the chamber **will do today** procedurally is `PF_PROCEDURAL`.

### Positive examples (ParlaMint sample)

> «Desde ahora anunciamos que presentaremos una enmienda de eliminación de los artículos […] y nos comprometemos a que en breve en esta Cámara se debata su toma en consideración […] la aprobación de esta reforma es urgente.»

— María Galovart Carrera (PSOE, 2017-11-28). Unit: `spdb-v1-unassigned-46bb18b3c74a`.

> «Aun así, vamos a votar a favor de la toma en consideración y, si es el caso, presentaremos enmiendas.»

— Míriam Nogueras Camero (JxCAT, 2017-09-19). Unit: `spdb-v1-unassigned-3721ab6f4c7a`.

> «Hoy debatiremos y aprobaremos la actualización y modificación de los limitados instrumentos fiscales y económicos con los que contamos vascos y vascas: el Convenio navarro y el Concierto Económico vasco […]»

— Mertxe Aizpurua Arzallus (EHBI, 2017-11-30). Unit: `spdb-v1-unassigned-78bd9b00e13c`.

> «¿Qué hemos hecho nosotros para no presentar una enmienda a la totalidad? Presentar líneas naranjas al Gobierno […] presentando al Gobierno unas líneas naranjas y diciéndole que, si quiere que estemos en la negociación de presupuestos, estas locuras no pueden estar en el proyecto.»

— Inés Arrimadas García (Cs, 2020-11-12). Unit: `spdb-v1-unassigned-783020218722`.  
*(Describes past negotiating action framed as strategic commitment; borderline with advocacy—flag `borderline` if tied.)*

### Negative examples

> «En Ciudadanos abogamos […] que se tenía que definir la figura del consumidor vulnerable […]»

— Melisa Rodríguez Hernández (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-ceada2c252a1`.  
**Not proposal:** argues what **should** be defined, without speaker **committing** to a concrete legislative act in this span (`PF_ADVOCACY`).

> «Pasamos ahora a votar el Real Decreto-ley 17/2017 […] Comienza la votación.»

— Presidencia (2017-11-30). Unit: `spdb-v1-unassigned-f4efaf8c67ab`.  
**Not proposal:** institutional **procedure** (`PF_PROCEDURAL`).

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ADVOCACY` | Proposal includes **commitment verbs** (presentaremos, nos comprometemos, aprobaremos). |
| `PF_PROCEDURAL` | Presidency announces **chamber actions**; legislators announce **policy/initiative** commitments. |
| `PF_APPEAL` | Appeal seeks **electoral/civic support**; proposal commits to **governance action**. |

---

## PF_APPEAL — Mobilization appeal

### Definition

Seeks electoral or civic support via identity, values, fear, hope, or solidarity.

### Decision rule

Label `PF_APPEAL` when the dominant move **mobilises** the audience (citizens, voters, “all Spaniards”) through shared identity, hope, fear, or solidarity, rather than detailing policy or attacking opponents. Tribute to groups (health workers) can be appeal when it solicits collective behaviour (“protect them by not spreading the virus”).

### Positive examples (ParlaMint sample)

> «A todos los españoles y a todas las españolas queremos transmitirles un mensaje de esperanza. Quiero decirles que lo volveremos a hacer, conseguiremos aplanar la curva como ya hicimos en primavera, y nos recuperaremos; juntos, con responsabilidad, pero también con determinación.»

— María Montero Cuadrado (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-2063abcb1366`.

> «Por eso, lo mejor que podemos hacer por ellos es no contagiarnos nosotros, no contribuir a que el virus siga expandiéndose y proteger a nuestros familiares más vulnerables.»

— María Montero Cuadrado (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-2063abcb1366`.

> «Por eso hoy es un día importante para todos nosotros y para nuestro proyecto de hacer una sociedad más sana y más responsable. […] cuidarse no es un lujo, sino una responsabilidad.»

— Dolors Montserrat Montserrat (PP, 2017-11-30). Unit: `spdb-v1-unassigned-60dd3e86e761`.

### Negative examples

> «había 4,5 millones de españoles con graves problemas para mantener su vivienda a una temperatura razonable de 18 grados […] la electricidad ha subido un 34 % […]»

— Melisa Rodríguez Hernández (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-ceada2c252a1`.  
**Not appeal:** **evidence** for policy argument (`PF_INFO` / `PF_ADVOCACY` depending on full unit).

> «Creo que ha quedado muy claro […] quién quiere que este país pueda salir de la crisis lo antes posible y quién prefiere que no.»

— María Montero Cuadrado (PSOE, 2020-11-12). Unit: `spdb-v1-unassigned-2063abcb1366`.  
**Not appeal:** **implicit attack** on opponents (`PF_ATTACK`), not solidarity mobilisation.

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ADVOCACY` | Appeal targets **hearts/mobilisation**; advocacy targets **policy change**. |
| `PF_ATTACK` | Appeal uses **positive** solidarity/hope; attack uses **negative** othering (often both in one long unit—pick dominant). |
| `PF_INFO` | Appeal is **evaluative/emotional**; info is **descriptive**. |

---

## PF_INFO — Informational

### Definition

Conveys factual or procedural information with minimal evaluative framing.

### Decision rule

Label `PF_INFO` when the span **reports** facts, figures, bill contents, or technical/process information without the dominant move being persuasion, attack, or mobilisation. Brief courtesy formulae inside informational speech do not flip the label. Heavy evaluative framing or moral judgement pushes toward advocacy or attack.

### Positive examples (ParlaMint sample)

> «El Grupo Parlamentario Socialista nos ha traído una proposición de ley con el propósito de introducir tres modificaciones en la ley 3/2007 […] son tres principalmente las reformas que plantea esta proposición de ley: por una parte, permitir la rectificación registral […] En segundo lugar, suprimir la obligación de aportar cualquier tipo de documento médico […] En tercer lugar, posibilitar a las personas extranjeras […]»

— Joseba Agirretxea Urresti (EAJPNV, 2017-11-28). Unit: `spdb-v1-unassigned-eb453642ca5f`.

> «En los dos últimos años […] la electricidad ha subido un 34 %, el gas un 22 %, el butano un 23 % y el agua un 8,5 %. También hemos nombrado […] las directivas europeas […] tanto la Directiva 2009/72, como la Directiva 2009/73.»

— Melisa Rodríguez Hernández (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-ceada2c252a1`.  
*(Excerpt only; full unit adds advocacy—label the whole unit, not this excerpt alone.)*

> «En este sentido, tengo que decir que, efectivamente, la previsión de ingresos puede estar subestimada, pero también porque el método tradicional para elaborar las estimaciones está basado en la elasticidad de los impuestos y en la elasticidad macroeconómica, que no tienen en cuenta un shock como el derivado de la pandemia […]»

— Idoia Sagastizabal Unzetabarrenetxea (EAJPNV, 2020-11-12). Unit: `spdb-v1-unassigned-483e95cc103b`.

### Negative examples

> «Tenemos a seis millones de seres humanos […] afectados por la pobreza energética. Tenemos un millón de hogares que tienen dificultades para pagar su factura de la luz […] más de siete mil muertes al año solamente a causa de la pobreza energética.»

— Yolanda Díaz Pérez (ECUP, 2017-09-19). Unit: `spdb-v1-unassigned-6d6700eea2a4`.  
**Not info:** figures deployed in **advocacy/attack** against opponents (`PF_ADVOCACY` / `PF_ATTACK`).

> «Comenzamos ahora, señorías, con el punto del orden del día relativo a la toma en consideración de la proposición de ley […] tiene la palabra […] el señor Rodríguez Rodríguez.»

— Presidencia (2017-11-28). Unit: `spdb-v1-unassigned-88da342f1158`.  
**Not info:** **procedural** chair speech (`PF_PROCEDURAL`).

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ADVOCACY` | Info **reports**; advocacy **argues** what should follow from facts. |
| `PF_PROCEDURAL` | Procedural info is about **chamber process**; PF_INFO is about **policy/subject matter**. |
| `PF_DEFENSE` | Correcting facts to **rebut** an opponent is often defense, not neutral info. |

---

## PF_DEFLECT — Deflection / evasion

### Definition

Avoids question or topic; pivots without substantive engagement.

### Decision rule

Label `PF_DEFLECT` when the speaker **does not address** the pending question, bill, or challenge and instead shifts topic (often to opponent's unrelated behaviour, media side story, or partisan framing). Counter-attacking on the merits of a different issue is still deflection if the original substantive point is left unanswered. Strong substantive rebuttal is `PF_DEFENSE` or `PF_ATTACK`, not deflection.

### Positive examples (ParlaMint sample)

> «Por cierto, señora García Puig […] Ayer leí un artículo que publicaba en el que decía que la violencia ejercida sobre las personas LGTBI es violencia neoliberal. Normalmente, cuando ustedes utilizan este término la verdad es que suelo perder el interés, pero como este asunto me preocupa especialmente y hoy debatíamos aquí esta ley continué leyéndolo […]»

— Patricia Reyes Rivera (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-e022d9750540`.  
*(Pivots from debate on the law to criticising an opponent's newspaper terminology instead of engaging the bill's substance.)*

> «Seguramente hasta ahí podríamos estar de acuerdo con el análisis de la proponente, pero en la parte dispositiva ocurre algo […] analizamos el tema y la solución que se propone al menos a nosotros no es la que nos gusta. […] presentan una mezcla, un batiburrillo […] en el que mezclan todo con todo: la situación de las zonas rurales, la banda ancha, los autores, el IVA, etcétera.»

— Joseba Agirretxea Urresti (EAJPNV, 2017-11-28). Unit: `spdb-v1-unassigned-68050b0d3785`.  
*(Borderline: critiques dispositivo while sidestepping direct engagement—compare `PF_ADVOCACY`; flag borderline if tied.)*

### Negative examples

> «No es así, señora Arrimadas, no es así. Ustedes ni siquiera han estado sentados en la mesa donde se tomaban estas decisiones.»

— Pablo Echenique Robba (UP, 2020-11-12). Unit: `spdb-v1-unassigned-b2eaf6b9bc1c`.  
**Not deflect:** **direct rebuttal** of opponent's claim (`PF_ATTACK` / `PF_DEFENSE`).

> «nos vemos obligados a abstenernos en esta votación.»

— Íñigo Barandiaran Benito (EAJPNV, 2017-09-19). Unit: `spdb-v1-unassigned-7bc5528e899b`.  
**Not deflect:** clear **position statement**, not evasion.

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_ATTACK` | Attack **engages** opponent on a charge; deflect **changes subject** away from the pending issue. |
| `PF_ADVOCACY` | Advocacy may criticise a bill; deflect **avoids** answering the question asked. |
| `PF_DEFENSE` | Defense addresses the **challenge**; deflect **sidesteps** it. |

Pure deflection is **rare** in prepared plenary set pieces; expect low frequency and higher adjudication rate.

---

## PF_PROCEDURAL — Ritual / procedural

### Definition

Order of business, courtesy, formal parliamentary ritual with political context.

### Decision rule

Label `PF_PROCEDURAL` for the **Presidencia** (or equivalent chair) managing agenda, speaking time, votes, and chamber rules, and for formulaic courtesy openers/closers when **no substantive policy move** dominates the unit. Short “Gracias, presidenta” alone inside a policy speech does not make the whole unit procedural.

### Positive examples (ParlaMint sample)

> «Comenzamos ahora, señorías, con el punto del orden del día relativo a la toma en consideración de la proposición de ley […] reguladora de las prácticas académicas universitarias externas. Para la presentación de la iniciativa, tiene la palabra, en primer lugar, el señor Rodríguez Rodríguez.»

— Presidencia (2017-11-28). Unit: `spdb-v1-unassigned-88da342f1158`.

> «Muchas gracias. En el turno de fijación de posiciones, por el Grupo Parlamentario Mixto, tiene la palabra, en primer lugar, el señor Alli Martínez.»

— Presidencia (2017-09-19). Unit: `spdb-v1-unassigned-05d607df9c93`.

> «Pasamos al punto del orden del día relativo a las proposiciones no de ley. Recuerdo de nuevo a sus señorías que no se pueden hacer vídeos ni fotografías en el hemiciclo.»

— Presidencia (2017-09-19). Unit: `spdb-v1-unassigned-af494fedf1eb`.

> «Pasamos ahora a votar el Real Decreto-ley 17/2017 […] Comienza la votación. Efectuada la votación, esta Presidencia informa del resultado.»

— Presidencia (2017-11-30). Unit: `spdb-v1-unassigned-f4efaf8c67ab`.

### Negative examples

> «Gracias, presidenta. Como decía, había 4,5 millones de españoles con graves problemas […]»

— Melisa Rodríguez Hernández (Cs, 2017-09-19). Unit: `spdb-v1-unassigned-ceada2c252a1`.  
**Not procedural:** courtesy **opener** followed by substantive **advocacy/info**.

> «Buenas tardes a todos y a todas. Señora Lucio, vamos a votar a favor de la toma en consideración […] vamos a enmendar el articulado […]»

— Yolanda Díaz Pérez (ECUP, 2017-09-19). Unit: `spdb-v1-unassigned-6d6700eea2a4`.  
**Not procedural:** **proposal/advocacy** on legislative strategy.

### Common confusions

| Often confused with | How to decide |
|---------------------|---------------|
| `PF_INFO` | Procedural = **chamber** process; info = **policy/subject** content. |
| `PF_APPEAL` | Ritual address to “señorías” about **agenda** is procedural; appeal to **citizens** is mobilisation. |
| `PF_PROPOSAL` | “Vamos a votar” from **chair** is procedural; from **legislator** about **policy** is proposal. |

---

## General annotation reminders

1. Enter **one** label ID per unit in `pragmatic_function` (e.g. `PF_ADVOCACY`), not the English name.
2. Label the **entire unit** in the CSV or Label Studio task, not sentence fragments.
3. If two labels are genuinely tied, choose the function toward the **primary political target** and note `borderline` (≤5% of units expected).
4. Fallacy labels are **independent** of pragmatic function.
5. Examples in this file are drawn from **ParlaMint-ES** material processed for SPDB; do not treat them as gold labels until adjudicated in the pilot.

**Related files:** `annotation/labelstudio/instructions.md`, `annotation/pilot_001/pilot_protocol.md`, `labels/pragmatic_functions.tsv`.
