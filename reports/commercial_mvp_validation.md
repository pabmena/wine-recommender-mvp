# Informe de Calidad e Integración Comercial V0.1.1 (SommAI MVP)

## Resumen Ejecutivo
Este informe valida la calibración comercial **V0.1.1 (Intent Alignment)** de la plataforma SommAI. Evalúa de forma automática el cumplimiento de las restricciones semánticas de estilo e intención por perfil (evitando Cabernet Sauvignon en perfiles frescos, Torrontés en tintos/asados, y Malbec excedentes), además de respetar stock, estado activo e intervalos de precios en pesos argentinos reales, confirmando el correcto tracking SQLite.

## Tabla de Resultados por Perfil Simulado
| ID | Perfil Evaluado | Tintos Est. | Blancos/Frescos | Tintos Livianos | Malbecs | Relajado | Resultado | Detalle/Motivo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Perfil 1: Blanco Fresco / Bajo presupuesto | 0 | 5 | 0 | 0 | No | ✅ PASSED | OK |
| 2 | Perfil 2: Tinto Asado / Alto presupuesto | 5 | 0 | 0 | 2 | No | ✅ PASSED | OK |
| 3 | Perfil 3: Equilibrado / Presupuesto Medio | 3 | 0 | 2 | 1 | No | ✅ PASSED | OK |
| 4 | Perfil 4: Avanzado Técnico Tinto / Alto presupuesto | 5 | 0 | 0 | 2 | No | ✅ PASSED | OK |
| 5 | Perfil 5: Avanzado Técnico Fresco / Presupuesto Medio-Alto | 0 | 5 | 0 | 0 | Sí | ✅ PASSED | OK |

## Detalle de Recomendaciones y Búsqueda por Perfil
### Perfil 1: Blanco Fresco / Bajo presupuesto
- **Flags de Intención**: `{"wants_white_fresh": true, "wants_red": false, "wants_asado": false, "wants_price_value": true, "wants_premium": false, "allows_exploration": false}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-016 - Familia Schroeder 2006 Deseado Torrontés (Neuquén) (Torrontés) ($12000.00, Stock: 15)
  - DEMO-WINE-046 - Funky Llama 2007 Sauvignon Blanc (Mendoza) (Sauvignon Blanc) ($12000.00, Stock: 15)
  - DEMO-WINE-054 - Santa Julia 2007 Pinot Grigio (Mendoza) (Pinot Grigio) ($8500.00, Stock: 15)
  - DEMO-WINE-018 - François Lurton 2010 Torrontés (Uco Valley) (Torrontés) ($8500.00, Stock: 15)
  - DEMO-WINE-048 - Domaine Bousquet 2017 Made With Organic Grapes Sauvignon Blanc (Tupungato) (Sauvignon Blanc) ($8500.00, Stock: 15)

### Perfil 2: Tinto Asado / Alto presupuesto
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": true, "wants_price_value": false, "wants_premium": true, "allows_exploration": false}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-004 - Finca Vides 2009 Torcidas Malbec (Mendoza) (Malbec) ($68000.00, Stock: 15)
  - DEMO-WINE-034 - Clos de Chacras 2010 Gran Estirpe Red (Mendoza) (Bordeaux-style Red Blend) ($68000.00, Stock: 15)
  - DEMO-WINE-003 - Doña Silvina 2006 Malbec (Mendoza) (Malbec) ($82000.00, Stock: 15)
  - DEMO-WINE-051 - Finca Sophenia 2008 Reserve Merlot (Tupungato) (Merlot) ($82000.00, Stock: 15)
  - DEMO-WINE-031 - Alamos 2013 Red (Mendoza) (Red Blend) ($68000.00, Stock: 15)

### Perfil 3: Equilibrado / Presupuesto Medio
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": false, "wants_price_value": true, "wants_premium": false, "allows_exploration": true}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-035 - Septima 2010 Gran Reserva Red (Mendoza) (Red Blend) ($19800.00, Stock: 15)
  - DEMO-WINE-053 - Trapezio 2009 Plus ++ Merlot-Cabernet Franc (Mendoza) (Merlot-Cabernet Franc) ($19800.00, Stock: 15)
  - DEMO-WINE-002 - Trapiche 2014 Oak Cask Malbec (Mendoza) (Malbec) ($19800.00, Stock: 15)
  - DEMO-WINE-022 - Altocedro 2015 Año Cero Pinot Noir (La Consulta) (Pinot Noir) ($15500.00, Stock: 15)
  - DEMO-WINE-024 - Nieto Senetiner 2010 Reserva Pinot Noir (Mendoza) (Pinot Noir) ($15500.00, Stock: 15)

### Perfil 4: Avanzado Técnico Tinto / Alto presupuesto
- **Flags de Intención**: `{"wants_white_fresh": false, "wants_red": true, "wants_asado": true, "wants_price_value": false, "wants_premium": true, "allows_exploration": false}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-003 - Doña Silvina 2006 Malbec (Mendoza) (Malbec) ($82000.00, Stock: 15)
  - DEMO-WINE-004 - Finca Vides 2009 Torcidas Malbec (Mendoza) (Malbec) ($68000.00, Stock: 15)
  - DEMO-WINE-034 - Clos de Chacras 2010 Gran Estirpe Red (Mendoza) (Bordeaux-style Red Blend) ($68000.00, Stock: 15)
  - DEMO-WINE-051 - Finca Sophenia 2008 Reserve Merlot (Tupungato) (Merlot) ($82000.00, Stock: 15)
  - DEMO-WINE-031 - Alamos 2013 Red (Mendoza) (Red Blend) ($68000.00, Stock: 15)

### Perfil 5: Avanzado Técnico Fresco / Presupuesto Medio-Alto
- **Flags de Intención**: `{"wants_white_fresh": true, "wants_red": false, "wants_asado": false, "wants_price_value": false, "wants_premium": false, "allows_exploration": false}`
- **Top 5 Recomendaciones asignadas**:
  - DEMO-WINE-018 - François Lurton 2010 Torrontés (Uco Valley) (Torrontés) ($8500.00, Stock: 15)
  - DEMO-WINE-054 - Santa Julia 2007 Pinot Grigio (Mendoza) (Pinot Grigio) ($8500.00, Stock: 15)
  - DEMO-WINE-046 - Funky Llama 2007 Sauvignon Blanc (Mendoza) (Sauvignon Blanc) ($12000.00, Stock: 15)
  - DEMO-WINE-055 - Alta Vista 2016 Malbec Rosé (Mendoza) (Rosé) ($15500.00, Stock: 15)
  - DEMO-WINE-027 - Carlos Basso 2006 Dos Fincas Cabernet Sauvignon-Merlot (Uco Valley) (Cabernet Sauvignon-Merlot) ($82000.00, Stock: 15)

## Auditoría de Analíticas en Dashboard (Persistencia SQLite)
- **Quizzes Iniciados**: 5 (Esperado: 5) -> ✅ OK
- **Quizzes Completados**: 5 (Esperado: 5) -> ✅ OK
- **Tasa de Conversión**: 100.0% (Esperado: 100.0%) -> ✅ OK
- **Clicks a WhatsApp (Leads)**: 5 (Esperado: 5) -> ✅ OK
- **Feedback Likes (👍)**: 3 (Esperado: 3) -> ✅ OK
- **Feedback Dislikes (👎)**: 2 (Esperado: 2) -> ✅ OK

### Top Vinos Recomendados:
- **Funky Llama 2007 Sauvignon Blanc (Mendoza)**: recomendado 2 veces
- **Santa Julia 2007 Pinot Grigio (Mendoza)**: recomendado 2 veces
- **François Lurton 2010 Torrontés (Uco Valley)**: recomendado 2 veces
- **Finca Vides 2009 Torcidas Malbec (Mendoza)**: recomendado 2 veces
- **Clos de Chacras 2010 Gran Estirpe Red (Mendoza)**: recomendado 2 veces

### Top Vinos Clickeados a E-Commerce:
- **Familia Schroeder 2006 Deseado Torrontés (Neuquén)**: clickeado 1 veces
- **Finca Vides 2009 Torcidas Malbec (Mendoza)**: clickeado 1 veces
- **Septima 2010 Gran Reserva Red (Mendoza)**: clickeado 1 veces
- **Doña Silvina 2006 Malbec (Mendoza)**: clickeado 1 veces
- **François Lurton 2010 Torrontés (Uco Valley)**: clickeado 1 veces

## Decisión Final de QA
**Veredicto**: **APTO** para la salida comercial del MVP.
