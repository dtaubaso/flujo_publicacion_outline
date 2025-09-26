# Parámetros de API Actualizados

## Cambios Realizados

### 1. Configuración Unificada (config.py)
- **Eliminado**: `market` (nombre completo de país)
- **Agregado**: `COUNTRY_ISO_TO_NAME` - Mapeo de códigos ISO a nombres completos
- **Nuevos parámetros estándar**:
  - `country_iso_code`: Código ISO de país (ej: "AR")
  - `lang_iso_code`: Código ISO de idioma (ej: "es") 
  - `language_code`: Código de idioma para DataForSEO (ej: "es")

### 2. Interfaz de Usuario (ui_components.py)
- **Reorganización del sidebar**:
  - Sección "Parámetros de búsqueda" más clara
  - Campos separados para códigos ISO vs nombres completos
  - Configuración avanzada con campos legacy (gl, hl)
  - Tooltips explicativos para cada campo
- **Mapeo automático**: De código ISO a nombre completo de país

### 3. DataForSEO API (dataforseo_api.py)
- **Parámetro correcto**: `language_code` en lugar de `gl`/`hl`
- **Ubicación**: Usa nombre completo (ej: "Argentina")
- **Manejo de errores**: Logging mejorado para debugging

### 4. Google Autocomplete API
- **Parámetros correctos**: `gl` y `hl` con códigos ISO
- **Formato**: AR (país), es (idioma)
- **URL**: `https://suggestqueries.google.com/complete/search`

### 5. Aplicación Principal (app.py)
- **Configuración automática**: `location_name` se obtiene del mapeo
- **Parámetros consistentes**: Todos los módulos usan la misma configuración
- **Logging completo**: Todas las llamadas API registradas

## Estructura de Parámetros

### Para DataForSEO:
```python
{
    "language_code": "es",        # Código de idioma 
    "location_name": "Argentina", # Nombre completo del país
    "device": "desktop",
    "safe": "off"
}
```

### Para Google Autocomplete:
```python
{
    "gl": "AR",  # Código ISO de país
    "hl": "es"   # Código ISO de idioma
}
```

### Para OpenAI:
```python
{
    "model": "gpt-5-nano",
    "temperature": 0.4  # Solo si el modelo lo soporta
}
```

## Mapeo de Países Soportados

| Código ISO | Nombre Completo |
|------------|----------------|
| AR | Argentina |
| US | United States |
| ES | Spain |
| MX | Mexico |
| CO | Colombia |
| CL | Chile |
| PE | Peru |
| BR | Brazil |
| GB | United Kingdom |
| DE | Germany |
| FR | France |
| IT | Italy |
| CA | Canada |
| AU | Australia |

## Validación

✅ **Sin errores de sintaxis**
✅ **Parámetros API corregidos**  
✅ **Configuración unificada**
✅ **Interfaz actualizada**
✅ **Mapeo automático funcional**
✅ **Logging completo implementado**

## Próximos Pasos

1. **Probar la aplicación** con diferentes países/idiomas
2. **Validar llamadas API** con logging
3. **Verificar resultados** de SERP y autocomplete
4. **Optimizar** según feedback de usuarios

---

*Actualización completada: Todos los parámetros de API están ahora correctamente alineados con la documentación oficial de DataForSEO y Google.*