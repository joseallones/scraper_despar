import os
import shutil
from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import get_current_context

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def move_existing_files(**context):
    output_dir = '/usr/local/airflow/dags/desparScraper/output'
    previous_dir = '/usr/local/airflow/dags/desparScraper/previous_outputs'

    os.makedirs(previous_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)  # Ensure that output_dir exists

    moved_files = []
    for filename in [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]:
        try:
            src_path = os.path.join(output_dir, filename)
            dst_path = os.path.join(previous_dir, filename)
            shutil.move(src_path, dst_path)
            moved_files.append(filename)
            print(f"[MOVE] Moved: {filename}")
        except Exception as e:
            print(f"[ERROR] Some problem to move {filename}: {str(e)}")

    remaining = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
    assert not remaining, f"Error: Files not moved: {remaining}"

    print(f"[MOVE] Operation completed. Total moved: {len(moved_files)}")
    if not moved_files:
        print("[MOVE] No files to move in the output directory")
    else:
        print(f"[MOVE] Total files moved: {len(moved_files)}")


def upload_all_files(**context):
    """Uploads all files from the output directory to GCS"""
    output_dir = '/usr/local/airflow/dags/desparScraper/output'
    files_to_upload = [f for f in os.listdir(output_dir) if
                       os.path.isfile(os.path.join(output_dir, f)) and f.lower().endswith('.csv')]

    if not files_to_upload:
        print("[UPLOAD] No files to upload in the output directory")
        return

    for filename in files_to_upload:
        src_path = os.path.join(output_dir, filename)
        dst_path = f'despar-data/output/{filename}'

        upload_task = LocalFilesystemToGCSOperator(
            task_id=f'upload_{filename.replace(".", "_").replace("+", "_")}',
            src=src_path,
            dst=dst_path,
            bucket='despar-data',
            gcp_conn_id='google_cloud_default',
            dag=dag
        )

        # Execute the upload task immediately
        upload_task.execute(context)


with DAG(
        'despar_scraper',
        default_args=default_args,
        description='DAG to run scraper',
        schedule_interval=None,
        start_date=pendulum.datetime(2025, 4, 1, tz='UTC'),
        catchup=False,
) as dag:
    move_files = PythonOperator(
        task_id='move_existing_files',
        python_callable=move_existing_files,
        provide_context=True,
    )

    run_scraper = BashOperator(
        task_id='run_scraper',
        bash_command='python despar_scraper.py',
        cwd='/usr/local/airflow/dags/desparScraper'
    )

    upload_files = PythonOperator(
        task_id='upload_all_files',
        python_callable=upload_all_files,
        provide_context=True,
    )

    move_files >> run_scraper >> upload_files
