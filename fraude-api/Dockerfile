# 1. Image de depart : Python 3.12, version legere
FROM python:3.12-slim
# 2. Dossier de travail dans l'image
WORKDIR /app
# 3. Les bibliotheques d'abord (elles changent rarement)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 4. Puis le code et le modele (ils changent souvent)
COPY api/ ./api/
COPY models/ ./models/
# 5. Le port du service et la commande de demarrage
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
