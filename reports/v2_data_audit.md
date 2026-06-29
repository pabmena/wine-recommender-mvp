# Auditoría V2 Wine Recommender (QA Final y Correcciones)

## Resumen ejecutivo
Este reporte valida formalmente las correcciones aplicadas sobre la V2 del recomendador de vinos, cubriendo la deduplicación, recencia, cobertura real y recalibración de confianza.

## Correcciones post-auditoría
- **Deduplicación**: Implementada deduplicación por título canónico y remoción del prefijo 'Recomendación Similar a:'.
- **Maridaje por Intención**: La lógica ahora Prioriza asado/picadas cuando el usuario indica dicha comida en el quiz.
- **Reducción de Unknowns**: Corregido patrón de extracción de variedades desde el título del vino.
- **Trazabilidad**: Integradas y persistidas las columnas de control de APIs en el CSV procesado final.

## Conteo V1
Suma de fuentes originales V1: 5872 filas.
Dataset V1 preparado: 5872 filas. Coincidencia exacta: True

## Conteo V2 y Trazabilidad
- Comentarios de Reddit 2026: 95 filas.
- Comentarios de Mercado Libre 2026: 5 filas.
- Comentarios procesados finales: 105 filas.

## Live vs Fallback
| Fuente | Método | Live/Fallback | Filas | % |
| --- | --- | --- | --- | --- |
| mercadolibre_reviews | MLA API Fallback | Fallback | 5 | 4.76% |
| reddit_argentina | PRAW API | Live | 95 | 90.48% |
| youtube_comments | YT API Fallback | Fallback | 5 | 4.76% |

## Buckets de Recencia
- Últimos 30 días: 4 comentarios.
- Últimos 90 días: 10 comentarios.
- Últimos 365 días: 17 comentarios.
- Más antiguo: 74 comentarios.

## Cobertura de Mercado
- Comentarios nuevos totales: 105
- Comentarios con vino detectado: 105
- Comentarios matcheados al catálogo V2: 11
- Comentarios usados como señal general de mercado: 94
- Cobertura sobre catálogo (vinos con feedback directo): 277 vinos (4.717% del catálogo total).

## Reducción de variedad Unknown
- Vinos Unknown V1: 2116
- Vinos Unknown V2 final: 721
- Vinos Unknown deducidos y reducidos: **1395** vinos.

## Validación de duplicados en recomendaciones
| Perfil | Duplicados Detectados en Recomendaciones |
| --- | --- |
| Perfil A: Principiante Intenso | No (Corregido) |
| Perfil B: Principiante Fresco/Liviano | No (Corregido) |
| Perfil C: Asado Precio-Calidad | No (Corregido) |
| Perfil D: Avanzado Técnico | No (Corregido) |
| Perfil E: Contradictorio/Neutro | No (Corregido) |

## Validación quiz adaptativo recalibrado
| Perfil | Preguntas respondidas | Confidence Score | Confidence Label | Top 3 recomendaciones | Maridaje |
| --- | --- | --- | --- | --- | --- |
| Perfil A: Principiante Intenso | 7 | 0.843 | Alto | Bodega Catena Zapata 2012 Adrianna Malbec (Mendoza), Achaval-Ferrer 2014 Finca Mirador Malbec (Mendoza), Lamadrid 2010 Matilde Single Vineyard Malbec (Agrelo) | Asado de tira a la leña / Vacío ahumado, Choripán con chimichurri / Provoleta dorada |
| Perfil B: Principiante Fresco/Liviano | 7 | 0.867 | Alto | Alamos 2013 Torrontés (Salta), Bodega Elena de Mendoza 2010 Chardonnay (Mendoza), Verum 2011 Chardonnay (Alto Valle del Río Negro) | Empanadas salteñas picantes, Humita en chala / Tamales |
| Perfil C: Asado Precio-Calidad | 7 | 0.667 | Medio | Don Miguel Gascón 2008 Malbec (Mendoza), Trapiche 2007 Oak Cask Syrah (Mendoza), Gouguenheim Winery 2009 Cabernet Sauvignon (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Perfil D: Avanzado Técnico | 7 | 0.943 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza), Tapiz 2008 Black Tears Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Perfil E: Contradictorio/Neutro | 7 | 0.631 | Medio | Alamos 2011 Selección Malbec (Mendoza), TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Ruca Malen 2007 Kinien Malbec (Mendoza) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
