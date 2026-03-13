Proyecto: Desencriptador + API

Resumen

- API Python (Flask) en `api/index.py` con endpoint `/api/decrypt` y `/api/predict`.
- Interfaz estática: `index.html` (UI del desencriptador).
- Modelos cargados (si existen) en `api/`: `modelo_cifrado_mlp.pkl`, `scaler_cifrado.pkl`.

Probar localmente

1. Crear y activar virtualenv, instalar deps:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ejecutar servidor Flask (desde la raíz del proyecto):

```powershell
$env:FLASK_APP="api/index.py"
.\venv\Scripts\python -m flask run --host=127.0.0.1 --port=5000
```

3. Abrir la UI en el navegador:

- http://127.0.0.1:5000

4. Pruebas de API (ejemplos):

- Desencriptar (base64):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/decrypt -Method Post -Body '{"texto":"SGVsbG8gd29ybGQ="}' -ContentType 'application/json' | ConvertTo-Json -Depth 5
```

- Predecir (modelo tiroideo):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/predict -Method Post -Body '{"t3_resin":1.2,"t4_total":10.5,"t3_total":2.9,"tsh":0.8,"t4_diff":0.3}' -ContentType 'application/json' | ConvertTo-Json -Depth 5
```

Preparar para Vercel (resumen)

1. Asegúrate de que `vercel.json` existe (ya incluido) y en la raíz del repo. Contiene builds para `api/index.py` y `index.html`.
2. Incluye los archivos de modelo en `api/` (ya presentes según tu repo). Vercel desplegará esos archivos si están en Git.
3. No subas el `venv/` (ya está en `.gitignore`).
4. Sube el repositorio a GitHub/GitLab/Bitbucket y conéctalo a Vercel (o usa `vercel` CLI para desplegar).

Compatibilidad de scikit-learn y pickles

- Si los pickles (`.pkl`) fueron creados con otra versión de `scikit-learn`, es probable que aparezcan warnings o errores al deserializarlos en la nube. Recomendaciones:
  - Opción A (recomendado si ves errores): recrear los pickles usando la versión de `scikit-learn` que usarás en producción y volver a subirlos.
  - Opción B: fijar la versión en `requirements.txt` a la versión con la que se serializaron los objetos (por ejemplo `scikit-learn==1.6.1`).

Ejemplo: para fijar scikit-learn a 1.6.1 (si los pickles se hicieron con esa versión), actualiza `requirements.txt` o instala y prueba localmente:

```powershell
pip install scikit-learn==1.6.1
```

Consejos de despliegue en Vercel

- Conectar tu repo a Vercel: sigue el asistente (Project → Import Project → seleccionar repo) y Vercel detectará la configuración en `vercel.json`.
- Variables de entorno: si en el futuro necesitas claves (p.ej. para AES), configúralas en Vercel Dashboard.
- Verifica logs en Vercel si hay errores al cargar modelos.

Archivos importantes

- `api/index.py` — servidor Flask (endpoints)
- `index.html` — UI del desencriptador
- `vercel.json` — configuración de build/redirecciones para Vercel
- `requirements.txt` — dependencias
- `api/modelo_cifrado_mlp.pkl`, `api/scaler_cifrado.pkl` — modelos que proporcionaste

¿Quieres que:

- actualice `requirements.txt` para fijar `scikit-learn` a la versión usada para generar los pickles (dime la versión), o
- ejecute un despliegue de prueba con la CLI `vercel` desde aquí (necesitarás proporcionar token/credenciales), o
- cree un `.vercelignore` para excluir archivos innecesarios?

Si todo está correcto, los pasos finales son: agregar/commitar los cambios, push al repo remoto y crear el proyecto en Vercel o ejecutar `vercel` para desplegar.
