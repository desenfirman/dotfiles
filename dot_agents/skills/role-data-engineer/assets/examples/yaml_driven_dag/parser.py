
import os
import sys

# Add templates directory to path to import universal parser
templates_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, templates_dir)

from lnk.shared_libs.parser.universal_parser import generate_dags

# Generate DAGs from config.yml in the same directory
config_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'config.yml'
)

if all([
    os.path.exists(config_file),
]):
    # Get the generated DAGs
    generated_dags = generate_dags(config_file)
    
    # Expose each DAG to the global namespace
    # This makes them discoverable by Airflow
    for dag in generated_dags:
        globals()[dag.dag_id] = dag

