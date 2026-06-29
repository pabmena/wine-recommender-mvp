# Informe de Calidad y Validación V2.0.2 (SommAI)

## Resumen Ejecutivo
Este informe valida la versión de ajuste fino V2.0.2 de SommAI, que implementa el capado visual del score de confianza a un máximo de 95% y la regla anti-dominancia de Malbec en perfiles frescos/livianos.

## Tabla de 6 Perfiles Simulados Obligatorios
| Perfil Evaluado | Raw Conf | Display Conf | Label | Top 5 Recomendaciones (Uva) | Malbec | Frescos | Tintos Est. | Resultado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fresco/Liviano principiante | 0.870 | 0.870 | Alto | Alamos 2013 Torrontés (Salta) (Torrontés), Bodega Elena de Mendoza 2010 Chardonnay (Mendoza) (Chardonnay), Verum 2011 Chardonnay (Alto Valle del Río Negro) (Chardonnay), Tapiz NV Extra Brut Torrontés (Mendoza) (Torrontés), Gaucho Club 2011 Oak Cask Malbec (Mendoza) (Malbec) | 1 | 4 | 1 | ✅ PASSED |
| Fresco/Liviano técnico | 1.000 | 0.950 | Alto | Doña Silvina 2011 Malbec (Mendoza) (Malbec), Ruca Malen 2009 Kinien Cabernet Sauvignon (Mendoza) (Cabernet Sauvignon), Aniello 2015 Soil Blanco de Pinot Noir (Patagonia) (Pinot Noir), Zorzal 2015 Eggo Filoso Pinot Noir (Tupungato) (Pinot Noir), Michel Torino 2013 Don David Finca La Primavera #3 Torrontés (Cafayate) (Torrontés) | 1 | 3 | 2 | ✅ PASSED |
| Intenso/Asado | 0.918 | 0.918 | Alto | Viña Alicia 2010 Coleccion de Familia Brote Negro Malbec (Luján de Cuyo) (Malbec), Valentin Bianchi 2010 Enzo Bianchi Red (Red Blend), Viña Cobos 2012 Bramare Zingaretti Vineyard Malbec (Valle de Uco) (Malbec), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) (Red Blend), Bodega Norton 2005 Perdriel Single Vineyard Red (Mendoza) (Bordeaux-style Red Blend) | 2 | 0 | 5 | ✅ PASSED |
| Precio-Calidad | 0.536 | 0.536 | Medio | Gouguenheim Winery 2009 Cabernet Sauvignon (Mendoza) (Cabernet Sauvignon), Valentin Bianchi 2012 Elsa Bianchi Malbec (Mendoza) (Malbec), Argento 2011 Malbec (Mendoza) (Malbec), Trapiche 2007 Oak Cask Syrah (Mendoza) (Syrah), Rutini 2009 Trumpeter Pinot Noir (Mendoza) (Pinot Noir) | 2 | 1 | 4 | ✅ PASSED |
| Avanzado técnico | 0.943 | 0.943 | Alto | Lamadrid 2007 Matilde Single Vineyard Malbec (Mendoza) (Malbec), Tapiz 2008 Black Tears Malbec (Mendoza) (Malbec), Bodega Catena Zapata 2007 Nicolas Catena Zapata Red (Mendoza) (Red Blend), Ruca Malen 2009 Kinien Cabernet Sauvignon (Mendoza) (Cabernet Sauvignon), Terrazas de Los Andes 2011 Single Vineyard Los Aromos Cabernet Sauvignon (Luján de Cuyo) (Cabernet Sauvignon) | 2 | 0 | 5 | ✅ PASSED |
| Contradictorio/Neutro | 0.480 | 0.480 | Exploratorio | Pulenta Estate 2009 I Malbec (Mendoza) (Malbec), Piattelli 2007 Grand Reserve Trinità Red (Mendoza) (Red Blend), Verum 2015 Pinot Noir (Alto Valle del Río Negro) (Pinot Noir), Luigi Bosca 2008 Reserva Pinot Noir (Maipú) (Pinot Noir), Urraca 2007 Chardonnay (Mendoza) (Chardonnay) | 1 | 3 | 2 | ✅ PASSED |

## Confirmación de Métricas Clave
- **Confianza visual máxima <= 95%**: Sí (Confirmado)
- **Máximo 1 Malbec en perfil fresco/liviano**: Sí (Confirmado)
- **Mínimo 3 vinos frescos/blancos/rosados/livianos en perfil fresco/liviano**: Sí (Confirmado)
- **0 duplicados en Top 5**: Sí (Confirmado)
- **0 Unknown en Top 5**: Sí (Confirmado)
- **Perfil contradictorio no queda como Alto**: Sí (Confirmado)

## Hallazgos Críticos de Backend
1. **Capado de confianza**: Funciona a nivel visual. El backend retiene el valor real para evaluar el quiz pero la interfaz nunca expone más del 95%.
2. **Diversidad adaptativa para Blancos y Frescos**: En los perfiles frescos, el motor limita la dominancia de Malbec a un máximo de 1 vino e inyecta uvas como Chardonnay, Torrontés, Pinot Noir y Sauvignon Blanc de forma mayoritaria en el Top 5.
3. **Compatibilidad con Asado/Intenso**: Los perfiles orientados a asados y carnes pesadas continúan recibiendo recomendaciones ricas en Malbec, Cabernet Sauvignon y Syrah de alta intensidad sin limitaciones artificiales.
4. **Clasificación del Pinot Noir**: Para fines de control de diversidad y el cálculo de `structured_red_count`, la variedad **Pinot Noir** se clasifica comercialmente como tinto liviano/fresco, no como tinto estructurado.

## Decisión Final
**Veredicto**: **APTO** para pasar a la rama `commercial-mvp`.
