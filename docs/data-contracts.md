# Contratos de datos — SQX Edge Pro

## Fuentes de verdad

1. Catálogo Edge: reglas estratégicas, categorías, ratings, direcciones y timeframes.
2. Quality Snapshot: datos importados desde MT5, siempre asociados a broker, símbolo, rango e instante de importación.
3. Operational Profile: combinación de broker, aliases, filtros y universo de activos.

## Convenciones

- `asset_id`: identificador canónico, por ejemplo `EURUSD`.
- `raw_symbol`: símbolo exacto del broker, por ejemplo `EURUSD.pa`.
- Los snapshots nunca se sobrescriben: una importación futura crea una nueva versión.
- Las estadísticas globales de spread proceden de la fila `Year=ALL`; los percentiles no se calculan como una media de percentiles anuales.

El EA MT5 exporta columnas como `Symbol`, `Year`, `AvgSpread`, `P50`, `P75`, `P90`, `P99`, `SamplesCount`, `NegSpreadCount` y propiedades estáticas del instrumento. El reporte horario usa `Hour`, `Session` y los percentiles equivalentes.
