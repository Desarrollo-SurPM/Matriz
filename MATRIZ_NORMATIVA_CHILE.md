# Matriz de contraste normativo · RiskBee

Fecha de revisión: **14 de julio de 2026**. Alcance: apoyo digital a la gestión preventiva en Chile. Esta matriz no constituye una certificación de cumplimiento ni reemplaza la revisión del experto en prevención, el organismo administrador, la autoridad sanitaria o asesoría jurídica.

## Resultado ejecutivo

El proyecto ya contaba con empresas, matrices IPER, reportes de accidentes, agenda y obligaciones legales, pero los flujos eran principalmente CRUD. La actualización transforma los tres focos prioritarios en procesos trazables:

- investigación en siete etapas, desde respuesta inmediata hasta verificación de eficacia;
- expediente documental en cuatro hitos: reporte flash, declaraciones/respaldos, investigación y alerta anónima;
- gestión de clientes priorizada con reglas transparentes y motivos visibles;
- cartera de protocolos MINSAL por empresa, con decisión de aplicabilidad, exposición, responsable, medidas, evidencia y revisión.

## Comparación

| Fuente / exigencia | Situación encontrada | Cobertura implementada | Límite o acción pendiente |
|---|---|---|---|
| **D.S. N.º 44, art. 7** · matriz de identificación de peligros y evaluación de riesgos disponible e informada | Existía una matriz IPER extensa y editable. | Se mantiene el módulo y se incorpora al nuevo sistema de navegación y propuesta de valor. | Revisar con especialista la metodología de evaluación, criterios y gatillantes de actualización de la matriz. La aplicación no certifica su suficiencia técnica. |
| **D.S. N.º 44, art. 62 y guía de mapas de riesgos** · croquis visible, riesgos derivados de la IPER y actualización | La aplicación no vinculaba un mapa de riesgos con la matriz. | Cada IPER puede conservar mapa, versión, ubicación, participación y vigencia; una fila modificada después del archivo activa revisión. | El archivo digital no reemplaza su ubicación visible en cada lugar de trabajo. Validar símbolos, niveles y accesibilidad en terreno. |
| **D.S. N.º 44, art. 8** · programa preventivo con medidas, responsables y plazos | Había campos de control y seguimiento, distribuidos en distintos módulos. | Accidentes, calendario legal, protocolos y gestiones ahora muestran responsable, fecha, acción y estado. | Falta un informe único de programa preventivo y evidencia de difusión/aprobación. |
| **D.S. N.º 44, art. 71** · investigar accidentes, incidentes peligrosos y enfermedades profesionales; incorporar enfoque de género y participación | El formulario usaba GEMA y 5 porqués, pero era una sola página y no registraba participación ni enfoque de género. | Flujo de 7 pasos con equipo, participación, testigos, evidencia, secuencia, enfoque de género, causalidad, jerarquía de controles y eficacia. | Para enfermedades profesionales conviene crear un flujo específico; el actual conserva una estructura orientada a eventos accidentales. |
| **D.S. N.º 44, art. 72** · registros mínimos de incidentes, accidentes, trayecto, enfermedades y vigilancia de salud | Faltaba sexo en el registro del accidente y no existía cartera de vigilancia por protocolo. | Se agrega sexo, lugar, fecha/hora, personas, relato, causas y acciones; se crea cartera agregada de protocolos y personas potencialmente expuestas. | No se almacenan nóminas clínicas individuales. Si se incorporan, se requiere diseño reforzado de privacidad, perfiles, retención y acceso. |
| **Ley N.º 16.744, art. 76 y Compendio SUSESO** · DIAT y obligaciones ante accidentes graves/fatales | “Severidad” se confundía con criterio legal y la interfaz podía sugerir que el reporte era la DIAT. | Se separa severidad interna del criterio legal; se registra DIAT, folio, aviso DT/SEREMI y suspensión de faena. La interfaz advierte que no ejecuta los trámites. | Integrar canales oficiales sólo mediante convenio/API válida. Mantener comprobantes; la DIAT debe presentarse al organismo administrador dentro de 24 horas de conocido el accidente. |
| **Accidente grave/fatal · SUSESO** · suspensión inmediata, control/evacuación, aviso inmediato a DT y SEREMI; exclusión de trayecto para suspensión/aviso | No había lista de criterios ni alerta diferenciada. | Selector de criterio grave/fatal y alerta contextual; la regla excluye accidente de trayecto para esa alerta específica. El cierre exige confirmar acciones cuando la alerta está activa. | La selección del usuario debe validarse con el organismo administrador. RiskBee no determina legalmente la clasificación. |
| **Protocolos y guías MINSAL de salud ocupacional** | Sólo existía una biblioteca normativa y tareas legales genéricas. | Cartera guiada para PREXOR, TMERT, sílice, psicosocial/CEAL-SM, UV solar, MMC e hipobaria, vinculada al repositorio oficial MINSAL. | Versiones, instrumentos y periodicidades pueden cambiar. Verificar siempre la resolución/protocolo vigente y las instrucciones del organismo administrador. |
| **Ley N.º 19.628 y Ley N.º 21.719** · datos personales y sensibles | Se almacenan RUT, sexo, lesión y fotografía; además había consultas de accidentes sin filtro por propietario y una clave SMTP en código. | Se cierran accesos cruzados en listados/detalles/edición y se mueve la clave SMTP a variable de entorno. Los formularios MINSAL desaconsejan adjuntar datos clínicos innecesarios. | Antes del **1 de diciembre de 2026**, preparar cumplimiento de la Ley N.º 21.719: base de licitud, información a titulares, roles, minimización, retención, ejercicio de derechos, registro de accesos e incidentes. Proteger también archivos `MEDIA` con autorización. |

## Fuentes oficiales consultadas

- [D.S. N.º 44 · Biblioteca del Congreso Nacional](https://www.bcn.cl/leychile/Navegar?idNorma=1205298)
- [Ley N.º 16.744, artículo 76 · Biblioteca del Congreso Nacional](https://www.bcn.cl/leychile/navegar?idNorma=28650&idParte=8745489&idVersion=2022-03-10)
- [SUSESO · Obligaciones en accidentes fatales y graves](https://www-cloud.suseso.cl/613/w3-propertyvalue-137143.html)
- [SUSESO · DIAT y plazo](https://www-cloud.suseso.cl/606/w3-article-40064.html)
- [MINSAL · Salud ocupacional y protocolos](https://www.minsal.cl/salud-ocupacional/)
- [Ley N.º 21.719 · entrada en vigencia diferida al 1 de diciembre de 2026](https://www.bcn.cl/leychile/N?i=1209272&t=0)

## Criterio de producto

RiskBee debe presentarse comercialmente como **sistema de apoyo, trazabilidad y control de gestión**, no como certificador automático. Su ventaja vendible es que convierte obligaciones y hallazgos en una secuencia demostrable: decisión, responsable, plazo, evidencia y verificación.
