FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/
COPY models/ ./models/
# PRATIQUE 7 : un utilisateur sans privileges, jamais root
RUN useradd --create-home app
USER app
EXPOSE 8000
# PRATIQUE 3 : aucune cle dans l'image, elle est fournie au lancement
CMD ["uvicorn", "api.main_securisee:app", "--host", "0.0.0.0", "--port", "8000"]
