# MEMERAG: base experimental de jueces LLM (español)

Experimento piloto: comparar un juez LLM con anotaciones humanas de fidelidad **por oración**.

## Preparación (Windows PowerShell)

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Colocar la clave de API en `.env`. 

## Dataset

Fuente oficial: https://github.com/amazon-science/MEMERAG

Descargar el JSONL de español del dataset original o de la versión de votación mayoritaria y colocarlo en `data/raw/es.jsonl`. Verificar en el repositorio oficial el nombre y ubicación exactos del archivo, y que el esquema contenga `query`, `context`, `answer` con `sentence`, `sentence_id` y `factuality`. El script **no** utiliza predicciones precomputadas.

## Ejecutar

```powershell
python src/prepare_data.py --file data/raw/es.jsonl --n 30 --seed 42
python src/run_experiment.py
python src/evaluate.py
```

Archivos de salida: `results/predictions.csv`, `results/metrics.json`, `results/disagreements.csv` y `results/confusion_matrix.png`.

## Metodología

- Etiquetas humanas: `Supported` (1) y `Not Supported` (0).
- Se excluyen las etiquetas humanas `Challenging to determine` del piloto binario.
- La unidad de evaluación es una oración de respuesta, no una respuesta completa.
- El juez no recibe la etiqueta humana.
- Se guarda la respuesta textual del juez para auditoría.
- Se registra el modelo y se fija la semilla de muestreo.
- El tamaño pequeño sirve para validar la infraestructura, no para sacar conclusiones generales.

## Limitaciones

La selección es aleatoria simple, no estratificada. Puede presentar desequilibrio de clases. La temperatura 0 no garantiza determinismo completo. Documentar versión del modelo, fecha, costos y procedencia exacta del dataset. Para una comparación formal con el artículo MEMERAG, usar sus prompts y protocolo oficial.
