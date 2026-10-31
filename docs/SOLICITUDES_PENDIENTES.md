# Solicitudes pendientes — borradores para enviar

Estos son **borradores** de correo/carta para pedir autorización explícita
de reutilización a cada institución. Contactar organismos externos es una
acción que le corresponde al usuario, no al asistente — estos textos están
listos para ajustar (llenar los datos entre `[corchetes]`) y enviar, no
para enviarse automáticamente.

Cada borrador resume lo que ya se investigó (ver `rights/` para el
detalle completo) y pide exactamente lo que falta: una confirmación
explícita por escrito de los tres permisos que este proyecto necesita
verificar antes de ingerir cualquier contenido — entrenamiento de
modelos de IA, uso comercial, y creación de obras derivadas (resúmenes,
respuestas generadas, comparaciones de versiones).

---

## 1. Biblioteca del Congreso Nacional (Ley Chile / BCN)

**Para**: Biblioteca del Congreso Nacional de Chile — área de datos
abiertos / atención a usuarios (`datos.bcn.cl` o el canal de contacto
institucional que corresponda)
**Asunto**: Consulta sobre términos de reutilización de Ley Chile para un
sistema de apoyo informativo con IA

> Estimados/as,
>
> Mi nombre es [NOMBRE], represento a [ORGANIZACIÓN/PROYECTO — Amalan].
> Estamos desarrollando un sistema de apoyo informativo (no un servicio
> jurídico) especializado en derecho de la construcción en Chile, que
> utiliza recuperación de información con citas exactas a las fuentes
> oficiales.
>
> Revisamos el catálogo de datos abiertos en `datos.bcn.cl`, que declara
> reutilización sin restricciones de copyright, pero no logramos
> confirmar si ese mismo régimen aplica al texto legal completo publicado
> en `leychile.cl` (no solo a los metadatos estructurados), ni si cubre
> específicamente:
>
> 1. El uso del texto para generar embeddings/índices de búsqueda y
>    entrenar o ajustar modelos de lenguaje.
> 2. El uso comercial de un producto que se apoye en ese texto.
> 3. La generación de resúmenes o comparaciones entre versiones de una
>    norma como obra derivada.
>
> ¿Podrían confirmarnos por escrito si estos tres usos están autorizados
> para el texto completo de Ley Chile, y bajo qué condiciones (atribución,
> no alteración, etc.)? Si existe una licencia o resolución formal que lo
> regule, agradeceríamos una copia o referencia.
>
> Quedamos atentos.
> [NOMBRE Y DATOS DE CONTACTO]

**Contexto para quien envía**: ver `rights/rights_manifest_src-leychile-bcn.json`
para el detalle completo de lo ya investigado (incluyendo el hallazgo del
Art. 88 de la Ley 17.336 sobre titularidad estatal, que conviene mencionar
si la institución pregunta por qué se solicita esto explícitamente).

---

## 2. Ministerio de Vivienda y Urbanismo (MINVU)

**Para**: Minvu Aló (600 901 11 11) o el canal de contacto institucional
de MINVU
**Asunto**: Consulta sobre términos de reutilización de la OGUC y
circulares DDU para un sistema de apoyo informativo con IA

> Estimados/as,
>
> [mismo encabezado que la carta anterior — ajustar nombre/proyecto]
>
> No encontramos en minvu.gob.cl una página de términos de uso o licencia
> de reutilización de contenidos, específicamente para la Ordenanza
> General de Urbanismo y Construcciones (OGUC) y las circulares de la
> División de Desarrollo Urbano (DDU).
>
> Quisiéramos solicitar autorización explícita para:
>
> 1. Usar el texto de la OGUC y sus circulares para generar índices de
>    búsqueda y, eventualmente, entrenar o ajustar modelos de lenguaje.
> 2. Ofrecer un producto comercial que se apoye en ese texto, siempre con
>    cita exacta a la fuente y advertencia de que no sustituye asesoría
>    profesional ni consulta directa con la DOM competente.
> 3. Generar resúmenes o comparaciones entre versiones de una circular.
>
> Agradeceríamos una respuesta por escrito confirmando si esto está
> permitido y bajo qué condiciones.
>
> Quedamos atentos.
> [NOMBRE Y DATOS DE CONTACTO]

**Contexto para quien envía**: ver `rights/rights_manifest_src-minvu.json`.
Por defecto se aplicó el Art. 88 de la Ley 17.336 (titularidad estatal) de
forma conservadora — esta carta es precisamente el paso para revertir esa
posición conservadora con una autorización explícita.

---

## 3. Contraloría General de la República

**Para**: Contraloría General de la República — Oficina de Partes o canal
de contacto institucional
**Asunto**: Consulta sobre términos de reutilización de dictámenes para un
sistema de apoyo informativo con IA

> Estimados/as,
>
> [mismo encabezado]
>
> No logramos ubicar en contraloria.cl una página de términos de uso o
> licencia de reutilización para los dictámenes publicados en el buscador
> de jurisprudencia administrativa. Entendemos que los dictámenes de
> Contraloría constituyen jurisprudencia administrativa vinculante para
> la Administración del Estado.
>
> Quisiéramos solicitar autorización explícita para:
>
> 1. Usar el texto de dictámenes relacionados con municipalidades,
>    Direcciones de Obras Municipales y permisos de edificación para
>    generar índices de búsqueda y, eventualmente, entrenar o ajustar
>    modelos de lenguaje.
> 2. Ofrecer un producto comercial que se apoye en ese texto, con cita
>    exacta y advertencia de que no sustituye asesoría profesional.
> 3. Generar resúmenes de dictámenes.
>
> Agradeceríamos una respuesta por escrito.
>
> Quedamos atentos.
> [NOMBRE Y DATOS DE CONTACTO]

**Contexto para quien envía**: ver `rights/rights_manifest_src-contraloria.json`.

---

## 4. Poder Judicial (Corporación Administrativa del Poder Judicial)

**Para**: Consejo Superior del Poder Judicial / Corporación Administrativa
del Poder Judicial (canal formal, dado que las condiciones de uso actuales
exigen autorización previa expresa para "tratamiento masivo de datos")
**Asunto**: Solicitud de autorización para tratamiento masivo de datos —
sistema de apoyo informativo con IA (jurisprudencia no vinculante)

> Estimados/as,
>
> [mismo encabezado]
>
> Revisamos las condiciones de uso del portal pjud.cl, que autorizan el
> uso de sentencias solo para "fines particulares o académicos" y exigen
> autorización previa del Consejo Superior para cualquier "tratamiento
> masivo de datos y contenidos". Nuestro proyecto es un sistema de apoyo
> informativo (no jurídico) que necesitaría procesar de forma automatizada
> un conjunto de sentencias relacionadas con contratos de construcción y
> subcontratación, presentando siempre esa jurisprudencia como **no
> vinculante** y con advertencia de que no sustituye asesoría legal.
>
> Solicitamos formalmente autorización para:
>
> 1. El tratamiento masivo de un conjunto acotado de sentencias públicas
>    relacionadas con construcción, para indexación y eventual
>    entrenamiento de modelos de lenguaje.
> 2. Confirmar si esto sería compatible con un uso comercial del producto
>    resultante, o si esa autorización quedaría restringida a fines no
>    comerciales.
>
> Quedamos atentos a los requisitos formales de esta solicitud.
> [NOMBRE Y DATOS DE CONTACTO]

**Contexto para quien envía**: ver `rights/rights_manifest_src-poder-judicial.json`.
Esta es la fuente con el rechazo más explícito encontrado; sin esta
autorización especial, esta fuente permanece bloqueada indefinidamente.

---

## 5. INN — Instituto Nacional de Normalización (bonus: vía comercial, no solo institucional)

A diferencia de las anteriores, INN ya tiene un canal de venta
establecido (`ecommerce.inn.cl`) pero con licencias de uso individual que
prohíben explícitamente la redistribución. Acá el paso no es una carta de
consulta sino una **negociación comercial** directa con INN para una
licencia que cubra específicamente:

1. Ingesta de un catálogo de normas NCh de construcción en un sistema de
   recuperación/IA.
2. Uso comercial del producto resultante.
3. Generación de citas/extractos (no el texto completo redistribuido) a
   partir de esas normas.

**Contexto para quien envía**: ver `rights/rights_manifest_src-inn.json`.
Recomendación: contactar directamente a la Unidad de Venta de Normas de
INN para cotizar esta licencia antes de asumir que es inviable — el
catálogo de normas NCh de construcción es acotado y podría ser más
económico de lo esperado negociarlo directamente en vez de intentar
evitarlo.

---

## Después de enviar

Cuando llegue una respuesta (positiva, negativa, o parcial) de cualquiera
de estas instituciones:

1. Guardar la respuesta como evidencia (correo, carta escaneada, o enlace
   a una resolución/licencia publicada).
2. Actualizar el `rights/rights_manifest_src-*.json` correspondiente:
   fijar `permiso_entrenamiento`, `permiso_uso_comercial` y
   `permiso_derivados` según la respuesta real (nunca inventar), citar la
   evidencia en `evidencia_legal`, y cambiar `estado_verificacion` a
   `"verificado"` o `"rechazado"` según corresponda.
3. Correr `python scripts/ingest_approved_sources.py` y
   `python scripts/coverage_report.py` para confirmar que el cambio se
   refleja correctamente.
4. Solo entonces usar `python scripts/add_verified_document.py` para
   ingresar el primer documento real de esa fuente.
