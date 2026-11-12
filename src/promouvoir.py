import os, sys
import mlflow
from mlflow import MlflowClient
NOM = sys.argv[1] if len(sys.argv) > 1 else 'fraude-h2o'             # fraude-h2o ou fraude-flaml
mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'http://127.0.0.1:5000'))
c = MlflowClient()
v = max(int(m.version) for m in c.search_model_versions(f"name='{NOM}'"))
c.set_registered_model_alias(NOM, 'production', v)                  # derniere version
print('version', v, 'promue')
