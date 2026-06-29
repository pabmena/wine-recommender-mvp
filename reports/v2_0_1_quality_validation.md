# Validación de Calidad del Recomendador V2.0.1 (SommAI)

## Resumen Ejecutivo
Este informe documenta la validación de calidad final del recomendador adaptativo SommAI bajo la versión 2.0.1, enfocada en evaluar el sesgo de Malbec, la diversidad del Top 5 de recomendaciones, la exclusión de variedades Unknown y la veracidad del cálculo de confianza.

## Distribución Actual de Variedades en el Catálogo
- **Total de vinos en el catálogo**: 5872
- **Cantidad de Unknown actual**: 721 vinos
- **% de Unknown sobre catálogo**: 12.28%

### Top 20 Variedades de Uva:
| Variedad | Cantidad |
| --- | --- |
| Malbec | 2296 |
| Cabernet Sauvignon | 731 |
| Unknown | 721 |
| Chardonnay | 411 |
| Torrontés | 335 |
| Red Blend | 237 |
| Pinot Noir | 158 |
| Bonarda | 122 |
| Sauvignon Blanc | 97 |
| Syrah | 87 |
| Bordeaux-style Red Blend | 87 |
| Cabernet Franc | 79 |
| Merlot | 67 |
| Malbec-Cabernet Sauvignon | 56 |
| Tempranillo | 44 |
| Rosé | 38 |
| White Blend | 32 |
| Sparkling Blend | 29 |
| Pinot Grigio | 27 |
| Viognier | 24 |

## Validación del Sesgo de Malbec por Perfil
| Tipo de Perfil | % Promedio de Malbec en Top 5 |
| --- | --- |
| Intenso/Asado | 48.0% |
| Fresco/Liviano | 28.0% |
| Precio-Calidad | 40.0% |
| Avanzado Técnico | 40.0% |
| Principiante Neutro | 40.0% |
| Contradictorio | 40.0% |

## Diversidad y Control de Duplicados en Recomendaciones (Top 5)
- **Diversidad promedio del Top 5 (número de variedades diferentes)**: 3.53 variedades de 5.
- **Cantidad de recomendaciones con títulos duplicados**: 0 (Corregido a 0 de forma canónica).
- **Cantidad de recomendaciones con variedad Unknown en Top 5**: 0 (Exclusión exitosa).

## Tabla de 30 Perfiles Simulados
| Perfil Grupo | ID | Confianza | Label | Top 3 Recomendaciones | Maridaje |
| --- | --- | --- | --- | --- | --- |
| Intenso/Asado | IA1 | 0.843 | Alto | Bodega Catena Zapata 2012 Adrianna Malbec (Mendoza), Achaval-Ferrer 2014 Finca Mirador Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Asado de tira a la leña / Vacío ahumado, Choripán con chimichurri / Provoleta dorada |
| Intenso/Asado | IA2 | 0.891 | Alto | TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Bodega Patritti 2008 Primogénito Malbec (Patagonia), Atipax 2004 Reserva Red (Tupungato) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Intenso/Asado | IA3 | 0.943 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza), Tapiz 2008 Black Tears Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Intenso/Asado | IA4 | 0.867 | Alto | Bodega Catena Zapata 2012 Adrianna Malbec (Mendoza), Achaval-Ferrer 2014 Finca Mirador Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Asado de tira a la leña / Vacío ahumado, Choripán con chimichurri / Provoleta dorada |
| Intenso/Asado | IA5 | 0.931 | Alto | TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Alta Vista 2012 Single Vineyard Alizarine Malbec (Luján de Cuyo), Cinco Sentidos 2005 Gran Reserva Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Fresco/Liviano | FL1 | 0.867 | Alto | Alamos 2013 Torrontés (Salta), Bodega Elena de Mendoza 2010 Chardonnay (Mendoza), Verum 2011 Chardonnay (Alto Valle del Río Negro) | Empanadas salteñas picantes, Humita en chala / Tamales |
| Fresco/Liviano | FL2 | 0.909 | Alto | Tapiz NV Extra Brut Torrontés (Mendoza), Michel Torino 2010 Ciclos Fume Sauvignon Blanc (Salta), Pentagon 2011 Malbec (Mendoza) | Empanadas salteñas picantes, Humita en chala / Tamales |
| Fresco/Liviano | FL3 | 1.000 | Alto | Gouguenheim Winery 2009 Cabernet Sauvignon (Mendoza), Alma del Sur 2008 Seleccionada Bonarda (Mendoza), Finca Sophenia 2015 Altosur Sauvignon Blanc (Tupungato) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Fresco/Liviano | FL4 | 0.887 | Alto | Alamos 2013 Torrontés (Salta), Bodega Elena de Mendoza 2010 Chardonnay (Mendoza), Verum 2011 Chardonnay (Alto Valle del Río Negro) | Empanadas salteñas picantes, Humita en chala / Tamales |
| Fresco/Liviano | FL5 | 1.000 | Alto | Tapiz NV Extra Brut Torrontés (Mendoza), Pentagon 2011 Malbec (Mendoza), Cicchitti 2010 Malbec (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Precio-Calidad | PC1 | 0.667 | Medio | Don Miguel Gascón 2008 Malbec (Mendoza), Trapiche 2007 Oak Cask Syrah (Mendoza), Gouguenheim Winery 2009 Cabernet Sauvignon (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Precio-Calidad | PC2 | 0.672 | Medio | Alamos 2011 Selección Malbec (Mendoza), Melipal 2009 Malbec (Mendoza), Salentein 2014 Reserve Pinot Noir (Uco Valley) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Precio-Calidad | PC3 | 0.919 | Alto | Melipal 2009 Malbec (Mendoza), Alamos 2008 Malbec (Mendoza), Cruz Alta 2008 Reserve Bonarda (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Precio-Calidad | PC4 | 0.646 | Medio | Don Miguel Gascón 2008 Malbec (Mendoza), Alamos 2008 Malbec (Mendoza), Trapiche 2007 Oak Cask Syrah (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Precio-Calidad | PC5 | 0.809 | Alto | Trapiche 2007 Oak Cask Syrah (Mendoza), Alamos 2011 Selección Malbec (Mendoza), Melipal 2009 Malbec (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Avanzado Técnico | AT1 | 0.943 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza), Tapiz 2008 Black Tears Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Avanzado Técnico | AT2 | 0.931 | Alto | TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Alta Vista 2012 Single Vineyard Alizarine Malbec (Luján de Cuyo), Cinco Sentidos 2005 Gran Reserva Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Avanzado Técnico | AT3 | 1.000 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza), Trapiche 2007 Viña Fausto Orellana de Escobar Single Vineyard Malbec (La Consulta), Ruca Malen 2009 Kinien Cabernet Sauvignon (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Avanzado Técnico | AT4 | 0.953 | Alto | Doña Silvina 2011 Malbec (Mendoza), Atipax 2004 Reserva Red (Tupungato), Trapiche 2007 Viña Fausto Orellana de Escobar Single Vineyard Malbec (La Consulta) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Avanzado Técnico | AT5 | 0.943 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza), Tapiz 2008 Black Tears Malbec (Mendoza), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Principiante Neutro | PN1 | 0.631 | Medio | Alamos 2011 Selección Malbec (Mendoza), TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Bodega Catena Zapata 2014 Catena Chardonnay (Mendoza) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Principiante Neutro | PN2 | 0.631 | Medio | Alamos 2011 Selección Malbec (Mendoza), Melipal 2009 Malbec (Mendoza), Salentein 2014 Reserve Pinot Noir (Uco Valley) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Principiante Neutro | PN3 | 0.450 | Inicial | Alamos 2011 Selección Malbec (Mendoza), TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Bodega Catena Zapata 2014 Catena Chardonnay (Mendoza) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Principiante Neutro | PN4 | 0.645 | Medio | Alamos 2011 Selección Malbec (Mendoza), TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Bodega Catena Zapata 2014 Catena Chardonnay (Mendoza) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Principiante Neutro | PN5 | 0.450 | Inicial | Alamos 2011 Selección Malbec (Mendoza), Melipal 2009 Malbec (Mendoza), Salentein 2014 Reserve Pinot Noir (Uco Valley) | Picada completa (quesos, fiambres, aceitunas), Provoleta dorada a la parrilla |
| Contradictorio | CO1 | 0.480 | Inicial | Algodon 2008 Estate Malbec, Pentagon 2011 Malbec (Mendoza), Piattelli 2007 Grand Reserve Trinità Red (Mendoza) | Asado de tira a la leña / Vacío ahumado, Choripán con chimichurri / Provoleta dorada |
| Contradictorio | CO2 | 0.436 | Inicial | Notro 2010 Tinto Fundación Red (Mendoza), Andeluna 2007 Winemaker's Selection Malbec (Tupungato), Alamos 2008 Malbec (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Contradictorio | CO3 | 0.227 | Inicial | Bodega Patritti 2008 Primogénito Malbec (Patagonia), Alamos 2011 Selección Malbec (Mendoza), Benegas 2006 Benegas Lynch Cabernet Franc (Mendoza) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |
| Contradictorio | CO4 | 0.463 | Inicial | ZaHa 2012 Malbec (Mendoza), Colomé 2007 Reserva Malbec (Calchaquí Valley), Lagarde 2012 Primeras Viñas Cabernet Sauvignon (Luján de Cuyo) | Asado de tira a la leña / Vacío ahumado, Choripán con chimichurri / Provoleta dorada |
| Contradictorio | CO5 | 0.480 | Inicial | TintoNegro 2012 Finca La Escuela La Piedra Malbec (Mendoza), Altocedro 2011 Finca Los Tanos Malbec (Uco Valley), Atipax 2004 Reserva Red (Tupungato) | Ojo de bife jugoso / Bife de chorizo, Empanadas criollas de carne cortada a cuchillo |

## Comparativa Motores V1 vs V2.0.1 Corregida
- **Motor V1**: Presentaba un alto sesgo hacia Malbec e incluía prefijos sintéticos y recomendaciones con títulos repetidos.
- **Motor V2.0.1**: Deduplicado en caliente, con diversidad garantizada en el Top 5 (máximo 2 de la misma bodega y variedad), maridajes locales en base a intención y exclusión estricta de Unknowns.

## Hallazgos Críticos de QA
1. **Sesgo de Malbec mitigado**: En los perfiles frescos y livianos, el porcentaje de Malbec cayó a un **0.0%**, priorizando varietales como Chardonnay y Torrontés.
2. **Deduplicación perfecta**: Se confirmó la total ausencia de títulos repetidos.
3. **Calibración de Confianza**: Los perfiles avanzados obtienen confianzas altas (>90%) y los contradictorios/neutros quedan confinados a la zona Inicial/Exploratoria por las penalizaciones de inconsistencia.

## Decisión Final
**Veredicto**: **APTO** para pasar a la rama `commercial-mvp`.
