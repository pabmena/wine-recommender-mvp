# Informe de Calidad e Integración Comercial V0.1.1 (SommAI MVP)

## Resumen Ejecutivo
Este informe valida la calibración comercial **V0.1.1 (Intent Alignment)** de la plataforma SommAI. Evalúa de forma automática el cumplimiento de las restricciones semánticas de estilo e intención por perfil (evitando Cabernet Sauvignon en perfiles frescos, Torrontés en tintos/asados, y Malbec excedentes), además de respetar stock, estado activo e intervalos de precios en pesos argentinos reales, confirmando el correcto tracking SQLite.

## Tabla de Resultados por Perfil Simulado
| ID | Perfil Evaluado | Tintos Est. | Blancos/Frescos | Tintos Livianos | Malbecs | Relajado | Resultado | Detalle/Motivo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Perfil 1: Blanco Fresco / Bajo presupuesto | 0 | 5 | 0 | 0 | No | ❌ FAILED | Presupuesto mal acotado en ARS (35000.0/12000).  |
| 2 | Perfil 2: Tinto Asado / Alto presupuesto | 5 | 0 | 0 | 3 | No | ❌ FAILED | Presupuesto inicial mal mapeado a ARS (15000.0/60000).  |
| 3 | Perfil 3: Equilibrado / Presupuesto Medio | 4 | 0 | 0 | 2 | No | ❌ FAILED | Rango de precio medio incorrecto ($15000.0 - $35000.0).  |
| 4 | Perfil 4: Avanzado Técnico Tinto / Alto presupuesto | 5 | 0 | 0 | 3 | No | ❌ FAILED | Exceso de Malbec (3/2).  |
| 5 | Perfil 5: Avanzado Técnico Fresco / Presupuesto Medio-Alto | 0 | 5 | 0 | 0 | No | ✅ PASSED | OK |

## Detalle de Recomendaciones y Búsqueda por Perfil
### Perfil 1: Blanco Fresco / Bajo presupuesto
- **Flags de Intención**: `{"wants_white_fresh": true, "wants_red": false, "wants_asado": false, "wants_price_value": true, "wants_premium": false, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-001 - Antucura NV Chérie Sparkling Pinot Noir Rosé Sparkling (Vista Flores) (Sparkling Blend) ($24000.00, Stock: 25)
  - DEMO-WINE-010 - Baja Tanga NV Sparkling Sec Cuvée Rosé Sparkling (Mendoza) (Sparkling Blend) ($24000.00, Stock: 25)
  - DEMO-WINE-016 - Zorzal 2016 Terroir Único Pinot Noir Rosé (Tupungato) (Rosé) ($19800.00, Stock: 25)
  - DEMO-WINE-025 - Benvenuto de la Serna 2015 Mil Piedras Viognier (Vista Flores) (Viognier) ($22000.00, Stock: 25)
  - DEMO-WINE-031 - Casa Montes 2015 Ampakama Viognier (San Juan) (Viognier) ($22000.00, Stock: 25)

### Perfil 2: Tinto Asado / Alto presupuesto
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": true, "wants_price_value": false, "wants_premium": true, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-037 - Finca Vides 2009 Torcidas Malbec (Mendoza) (Malbec) ($28000.00, Stock: 25)
  - DEMO-WINE-043 - Ricominciare 2010 Malbec-Tannat (Uco Valley) (Malbec-Tannat) ($28000.00, Stock: 25)
  - DEMO-WINE-040 - Alamos 2013 Red (Mendoza) (Red Blend) ($28000.00, Stock: 25)
  - DEMO-WINE-049 - Domaine Bousquet 2016 Finca Lalande Malbec (Mendoza) (Malbec) ($28000.00, Stock: 25)
  - DEMO-WINE-052 - Riglos 2010 Gran Las Divas Vineyard Cabernet Franc (Tupungato) (Cabernet Franc) ($28000.00, Stock: 25)

### Perfil 3: Equilibrado / Presupuesto Medio
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": false, "wants_price_value": true, "wants_premium": false, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-037 - Finca Vides 2009 Torcidas Malbec (Mendoza) (Malbec) ($28000.00, Stock: 25)
  - DEMO-WINE-043 - Ricominciare 2010 Malbec-Tannat (Uco Valley) (Malbec-Tannat) ($28000.00, Stock: 25)
  - DEMO-WINE-040 - Alamos 2013 Red (Mendoza) (Red Blend) ($28000.00, Stock: 25)
  - DEMO-WINE-052 - Riglos 2010 Gran Las Divas Vineyard Cabernet Franc (Tupungato) (Cabernet Franc) ($28000.00, Stock: 25)
  - DEMO-WINE-004 - Viniterra NV Método Tradicional Extra Brut  (Mendoza) (Champagne Blend) ($24000.00, Stock: 25)

### Perfil 4: Avanzado Técnico Tinto / Alto presupuesto
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": true, "wants_price_value": false, "wants_premium": true, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-037 - Finca Vides 2009 Torcidas Malbec (Mendoza) (Malbec) ($28000.00, Stock: 25)
  - DEMO-WINE-043 - Ricominciare 2010 Malbec-Tannat (Uco Valley) (Malbec-Tannat) ($28000.00, Stock: 25)
  - DEMO-WINE-040 - Alamos 2013 Red (Mendoza) (Red Blend) ($28000.00, Stock: 25)
  - DEMO-WINE-049 - Domaine Bousquet 2016 Finca Lalande Malbec (Mendoza) (Malbec) ($28000.00, Stock: 25)
  - DEMO-WINE-052 - Riglos 2010 Gran Las Divas Vineyard Cabernet Franc (Tupungato) (Cabernet Franc) ($28000.00, Stock: 25)

### Perfil 5: Avanzado Técnico Fresco / Presupuesto Medio-Alto
- **Flags de Intención**: `{"wants_white_fresh": true, "wants_red": false, "wants_asado": false, "wants_price_value": false, "wants_premium": false, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-001 - Antucura NV Chérie Sparkling Pinot Noir Rosé Sparkling (Vista Flores) (Sparkling Blend) ($24000.00, Stock: 25)
  - DEMO-WINE-010 - Baja Tanga NV Sparkling Sec Cuvée Rosé Sparkling (Mendoza) (Sparkling Blend) ($24000.00, Stock: 25)
  - DEMO-WINE-016 - Zorzal 2016 Terroir Único Pinot Noir Rosé (Tupungato) (Rosé) ($19800.00, Stock: 25)
  - DEMO-WINE-025 - Benvenuto de la Serna 2015 Mil Piedras Viognier (Vista Flores) (Viognier) ($22000.00, Stock: 25)
  - DEMO-WINE-031 - Casa Montes 2015 Ampakama Viognier (San Juan) (Viognier) ($22000.00, Stock: 25)

## Auditoría de Analíticas en Dashboard (Persistencia SQLite)
- **Quizzes Iniciados**: 5 (Esperado: 5) -> ✅ OK
- **Quizzes Completados**: 5 (Esperado: 5) -> ✅ OK
- **Tasa de Conversión**: 100.0% (Esperado: 100.0%) -> ✅ OK
- **Clicks a WhatsApp (Leads)**: 5 (Esperado: 5) -> ✅ OK
- **Feedback Likes (👍)**: 3 (Esperado: 3) -> ✅ OK
- **Feedback Dislikes (👎)**: 2 (Esperado: 2) -> ✅ OK

### Top Vinos Recomendados:
- **Finca Vides 2009 Torcidas Malbec (Mendoza)**: recomendado 3 veces
- **Ricominciare 2010 Malbec-Tannat (Uco Valley)**: recomendado 3 veces
- **Alamos 2013 Red (Mendoza)**: recomendado 3 veces
- **Riglos 2010 Gran Las Divas Vineyard Cabernet Franc (Tupungato)**: recomendado 3 veces
- **Antucura NV Chérie Sparkling Pinot Noir Rosé Sparkling (Vista Flores)**: recomendado 2 veces

### Top Vinos Clickeados a E-Commerce:
- **Finca Vides 2009 Torcidas Malbec (Mendoza)**: clickeado 3 veces
- **Antucura NV Chérie Sparkling Pinot Noir Rosé Sparkling (Vista Flores)**: clickeado 2 veces

## Decisión Final de QA
**Veredicto**: **NO APTO** para la salida comercial del MVP.
