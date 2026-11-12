import json, subprocess, yaml
from prefect import flow, task, get_run_logger

@task(retries=2, retry_delay_seconds=10)                # 2 reessais en cas d'echec
def rejouer_pipeline():
    r = subprocess.run(['dvc', 'repro'], capture_output=True, text=True)
    get_run_logger().info(r.stdout[-800:])
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-500:])
    return 'pipeline rejoue'

@task
def lire_metriques():
    return json.load(open('reports/metrics.json'))

@task
def valider(mets):
    seuil = yaml.safe_load(open('params.yaml'))['validation']['seuil_f1']
    if mets['f1'] < seuil:                              # regle de qualite
        raise ValueError(f"F1 {mets['f1']} < seuil {seuil} : modele refuse")
    get_run_logger().info(f"F1 {mets['f1']} >= {seuil} : modele accepte")
    return True

@task
def notifier(mets):
    get_run_logger().info(f"NOTIFICATION equipe : nouveau modele F1={mets['f1']}")

@flow(name='reentrainement-fraude', log_prints=True)
def reentrainement():
    rejouer_pipeline()
    mets = lire_metriques()
    valider(mets)
    notifier(mets)

if __name__ == '__main__':
    reentrainement()
