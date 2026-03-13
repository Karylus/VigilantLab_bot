# Guía de Contribución - WATCHMAN

¡Gracias por tu interés en contribuir a WATCHMAN! Este documento proporciona pautas y pasos para colaborar con el proyecto.

## Tabla de Contenidos

- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)

## ¿Cómo Puedo Contribuir?

### Reportar Bugs

Antes de crear un reporte de bug, por favor verifica la lista de issues ya que podrías encontrar que no necesitas crear uno. Si encuentras un bug, por favor:

1. **Usa un título descriptivo** para identificar el problema
2. **Describe los pasos exactos** que reproducen el problema
3. **Proporciona ejemplos específicos** para demostrar esos pasos
4. **Describe el comportamiento observado** y explica qué es lo que está mal
5. **Explica qué comportamiento esperabas** ver y por qué
6. **Incluye capturas de pantalla/logs** si es posible

### Sugerir Mejoras

Las sugerencias de mejora son siempre bienvenidas. Por favor:

1. **Usa un título descriptivo** para la sugerencia
2. **Proporciona una descripción detallada** de la mejora sugerida
3. **Lista algunos ejemplos** que muestren cómo funcionaría la mejora
4. **Explica por qué** crees que esta mejora sería útil

### Pull Requests

- Completa el template de PR proporcionado
- Sigue los [estándares de código](#estándares-de-código)
- Incluye commits atómicos y descriptivos
- Actualiza la documentación según sea necesario
- Asegúrate de que todos los tests pasen

## Configuración del Entorno de Desarrollo

### Prerequisitos

- Python 3.11 o superior
- Git
- `uv` o `pip` para gestión de dependencias

### Setup con `uv` (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/WATCHMAN.git
cd WATCHMAN

# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias incluyendo desarrollo
uv sync --all-extras

# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# o en Windows: .\.venv\Scripts\Activate.ps1
```

### Setup con `pip`

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/WATCHMAN.git
cd WATCHMAN

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o en Windows: .\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements-dev.txt
```

### Verificar Setup

```bash
# Ejecutar tests
pytest

# Ejecutar verificación de tipos
mypy src/

# Ejecutar linter
ruff check src/

# Formatear código
black src/
isort src/
```

## Estándares de Código

### Estilo de Código

- **Formato:** Usamos `black` con línea máxima de 100 caracteres
- **Imports:** Organizamos con `isort` siguiendo el perfil `black`
- **Type Hints:** Alentamos type hints en funciones públicas
- **Docstrings:** Usamos docstrings en formato estándar de Python

### Ejemplo de Función Bien Formateada

```python
async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Execute the command and send response to Telegram.
    
    Args:
        update: The Telegram update object
        context: The Telegram context object
        
    Raises:
        PermissionError: If the user lacks required permissions
    """
    try:
        result = await self.perform_action()
        await self.send_message(update, context, result)
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        await self.send_message(update, context, "❌ Permiso denegado")
```

### Linting y Formatting

```bash
# Formatear automáticamente
black src/
isort src/

# Verificar problemas
ruff check src/
mypy src/

# Ejecutar todo de una vez
black src/ && isort src/ && ruff check src/ && mypy src/
```

### Commits

- Usa mensajes de commit descriptivos
- Empieza con un verbo en imperativo: "Add", "Fix", "Update", "Remove"
- Primera línea máximo 50 caracteres
- Proporciona detalles adicionales en líneas subsecuentes si es necesario

**Ejemplos buenos:**
```
Add /threats command for security analysis
Fix rate limiter not working for sudo commands
Update README with uv installation instructions
Remove deprecated temp_fix.py file
```

## Proceso de Pull Request

1. **Fork el repositorio** en GitHub
2. **Crea una rama** para tu cambio: `git checkout -b feature/mi-feature`
3. **Realiza tus cambios** siguiendo los estándares de código
4. **Ejecuta los tests:** `pytest`
5. **Formatea el código:** `black src/ && isort src/`
6. **Haz push** a tu fork: `git push origin feature/mi-feature`
7. **Abre un Pull Request** contra la rama `main` del repositorio original

### Template de Pull Request

```markdown
## Descripción
<!-- Describe los cambios que haces -->

## Tipo de Cambio
- [ ] Bug fix (cambio que no causa breaking changes)
- [ ] Nueva feature (cambio que no causa breaking changes)
- [ ] Breaking change (fix o feature que podría causar breaking changes)
- [ ] Documentación

## Testing
- [ ] He testeado estos cambios localmente
- [ ] He agregado tests nuevos para mis cambios
- [ ] Todos los tests pasan

## Checklist
- [ ] Mi código sigue los estándares de código del proyecto
- [ ] He actualizado la documentación
- [ ] No he agregado dependencias sin justificación
- [ ] Los mensajes de commit son claros y descriptivos
```

## Reportar Bugs

### Antes de Reportar

- Verifica si el bug ya ha sido reportado
- Asegúrate de que es realmente un bug y no un comportamiento esperado
- Actualiza a la versión más reciente

### Cómo Reportar

1. **Usa un título claro y descriptivo**
2. **Describe los pasos exactos** para reproducir el problema
3. **Proporciona ejemplos específicos** para demostrar esos pasos
4. **Describe el comportamiento observado**
5. **Explica qué comportamiento esperabas**
6. **Incluye logs y detalles del sistema:**
   ```bash
   # Información del sistema
   uname -a
   python --version
   
   # Versión del proyecto
   git log --oneline -1
   ```

## Sugerir Mejoras

### Antes de Sugerir

- Verifica si la mejora ya ha sido sugerida
- Proporciona casos de uso claros

### Cómo Sugerir

1. **Usa un título claro y descriptivo**
2. **Proporciona una descripción detallada** de la mejora sugerida
3. **Lista algunos ejemplos** que muestren cómo funcionaría
4. **Explica por qué** crees que sería útil

## Preguntas

- Abre una **Discussion** en GitHub para preguntas
- Revisa la documentación existente en el README
- Busca en issues cerrados anteriores

## Licencia

Al contribuir a WATCHMAN, aceptas que tus contribuciones serán licenciadas bajo su licencia Apache 2.0.

## Agradecimientos

¡Gracias por contribuir a WATCHMAN! Tu ayuda es invaluable para mejorar el proyecto. 🙏
