"""
MongoDB to BigQuery Schema Auto-Generator

This script connects to a MongoDB collection, analyzes its schema by sampling documents,
and generates a YAML DAG definition for ingesting data from MongoDB to BigQuery.
"""

import argparse
import sys
import os
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import OrderedDict
from textwrap import indent
from pymongo import MongoClient
from bson import ObjectId
import yaml
from dotenv import load_dotenv


class MongoSchemaAnalyzer:
    """Analyzes MongoDB collection schema and generates BigQuery-compatible definitions."""

    DEFAULT_OUTPUT_FORMAT = 'universal_parser_task'
    LEGACY_OUTPUT_FORMAT = 'legacy'

    # Load strategies for universal_parser_task output
    LOAD_STRATEGY_FULL_REFRESH = 'full_refresh'
    LOAD_STRATEGY_INCREMENTAL  = 'incremental'   # delete-then-insert scoped by time_ranged_filter
    LOAD_STRATEGY_MERGE        = 'merge'          # MERGE/upsert keyed on unique_identifier
    LOAD_STRATEGIES = [LOAD_STRATEGY_FULL_REFRESH, LOAD_STRATEGY_INCREMENTAL, LOAD_STRATEGY_MERGE]
    
    # MongoDB to BigQuery type mapping
    TYPE_MAPPING = {
        'string': 'STRING',
        'int': 'INT64',
        'long': 'INT64',
        'double': 'FLOAT64',
        'bool': 'BOOL',
        'date': 'TIMESTAMP',
        'timestamp': 'TIMESTAMP',
        'objectId': 'STRING',
        'object': 'STRING',  # JSON objects as STRING
        'array': 'STRING',   # Arrays as STRING (JSON)
        'null': 'STRING',    # Default to STRING for nulls
        'binary': 'BYTES',
        'decimal': 'NUMERIC',
    }
    
    def __init__(self, conn_id: str, collection_name: str, sample_size: int = 1000):
        """
        Initialize the schema analyzer.
        
        Args:
            conn_id: MongoDB connection ID to look up in .env file
            collection_name: Name of the collection to analyze
            sample_size: Number of documents to sample for schema detection
        """
        self.conn_id = conn_id
        self.collection_name = collection_name
        self.sample_size = sample_size
        self.client = None
        self.db = None
        self.collection = None
        self.connection_string = self._get_connection_string()
        
    def _get_connection_string(self) -> str:
        """
        Get connection string from .env file using connection ID.
        
        Returns:
            MongoDB connection string
        """
        # Load environment variables from .env file
        load_dotenv()
        
        # Try different possible environment variable names for the connection ID
        env_var_names = [
            self.conn_id.upper(),
            f"MONGO_{self.conn_id.upper()}",
            f"MONGODB_{self.conn_id.upper()}",
            f"{self.conn_id.upper()}_CONNECTION_STRING",
            f"MONGO_{self.conn_id.upper()}_CONNECTION_STRING",
            f"MONGODB_{self.conn_id.upper()}_CONNECTION_STRING"
        ]
        
        for env_var in env_var_names:
            connection_string = os.getenv(env_var)
            if connection_string:
                print(f"✓ Found connection string for conn_id '{self.conn_id}' in environment variable '{env_var}'")
                return connection_string
        
        # If not found, raise an error with helpful message
        available_vars = [var for var in os.environ.keys() if 'mongo' in var.lower()]
        error_msg = f"Connection string not found for conn_id '{self.conn_id}'. "
        error_msg += f"Tried environment variables: {', '.join(env_var_names)}. "
        if available_vars:
            error_msg += f"Available MongoDB-related variables: {', '.join(available_vars)}"
        else:
            error_msg += "No MongoDB-related environment variables found."
        
        raise ValueError(error_msg)
        
    def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            # Extract database name from connection string or use the database from connection
            db_name = self.client.get_database().name
            self.db = self.client[db_name]
            self.collection = self.db[self.collection_name]
            print(f"✓ Connected to MongoDB database: {db_name}, collection: {self.collection_name}")
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            sys.exit(1)
    
    def get_all_fields(self) -> List[str]:
        """
        Get all possible field names in the collection preserving order.
        Fields are collected in the order they first appear in documents.
        """
        print(f"→ Discovering all fields in collection...")
        try:
            # Use OrderedDict to preserve insertion order while avoiding duplicates
            seen_fields = OrderedDict()
            
            # Sample documents to discover fields
            sample_docs = self.collection.find().limit(self.sample_size)
            
            for doc in sample_docs:
                # Get all keys from the document in their natural order
                for key in doc.keys():
                    if key not in seen_fields:
                        seen_fields[key] = True
            
            fields = list(seen_fields.keys())
            print(f"✓ Found {len(fields)} unique fields")
            return fields
        except Exception as e:
            print(f"✗ Error discovering fields: {e}")
            return []
    
    def detect_python_type(self, value: Any) -> str:
        """Detect the Python type of a value."""
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'double'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, ObjectId):
            return 'objectId'
        elif isinstance(value, datetime):
            return 'timestamp'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        elif isinstance(value, bytes):
            return 'binary'
        else:
            return 'string'
    
    def analyze_field_types(self, fields: List[str]) -> Dict[str, str]:
        """
        Analyze field types by sampling documents.
        
        Args:
            fields: List of field names to analyze
            
        Returns:
            OrderedDict mapping field names to their detected BigQuery types
        """
        print(f"→ Analyzing field types (sampling {self.sample_size} documents)...")
        
        field_types: Dict[str, Set[str]] = {field: set() for field in fields}
        
        # Sample documents from the collection
        sample_docs = self.collection.aggregate([
            {"$sample": {"size": self.sample_size}}
        ])
        
        sampled_count = 0
        for doc in sample_docs:
            sampled_count += 1
            for field in fields:
                # Handle nested fields (e.g., "field.subfield")
                value = self._get_nested_value(doc, field)
                if value is not None or field in doc:
                    python_type = self.detect_python_type(value)
                    field_types[field].add(python_type)
        
        print(f"✓ Analyzed {sampled_count} documents")
        
        # Determine the most appropriate BigQuery type for each field
        result = OrderedDict()
        for field, types in field_types.items():
            if not types or types == {'null'}:
                result[field] = 'STRING'  # Default to STRING for unknown types
            else:
                # Remove null from consideration if other types exist
                non_null_types = types - {'null'}
                if non_null_types:
                    # If multiple types, prioritize in this order: timestamp > double > int > string
                    priority = ['timestamp', 'date', 'double', 'int', 'long', 'bool', 'string']
                    selected_type = 'string'
                    for ptype in priority:
                        if ptype in non_null_types:
                            selected_type = ptype
                            break
                    result[field] = self.TYPE_MAPPING.get(selected_type, 'STRING')
                else:
                    result[field] = 'STRING'
        
        return result
    
    def _get_nested_value(self, doc: Dict, field: str) -> Any:
        """Get value from potentially nested field using dot notation."""
        keys = field.split('.')
        value = doc
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    def generate_projection(self, fields: List[str]) -> Dict[str, int]:
        """Generate MongoDB projection dict."""
        return {field: 1 for field in fields}

    def render_projection_yaml(self, fields: List[str], indentation: int = 6) -> str:
        """Render MongoDB projection as YAML with the requested indentation."""
        projection = self.generate_projection(fields)
        projection_yaml = yaml.safe_dump(
            projection,
            default_flow_style=False,
            sort_keys=False,
            width=1000,
        ).rstrip()
        return indent(projection_yaml, ' ' * indentation)

    def build_cast_expression(self, field: str, bq_type: str) -> str:
        """Build BigQuery-safe cast expression for one field."""
        field_ref = f"`{field}`"
        field_alias = f"`{field}`"

        if bq_type == 'TIMESTAMP':
            return (
                f"SAFE_CAST(SAFE_CAST({field_ref} AS STRING) AS TIMESTAMP) "
                f"AS {field_alias}"
            )

        return f"CAST({field_ref} AS {bq_type}) AS {field_alias}"
    
    def generate_columns_definition(self, field_types: Dict[str, str]) -> str:
        """Generate BigQuery column definitions with CAST statements."""
        definitions = []
        
        for field, bq_type in field_types.items():
            definitions.append(self.build_cast_expression(field, bq_type))
        
        # Add metadata columns
        definitions.append("TIMESTAMP('{{ data_interval_start }}') AS `__scheduled_at__`")
        definitions.append("CURRENT_TIMESTAMP() AS `__extracted_at__`")
        
        return ",\n".join(definitions)

    def build_mongo_filter_yaml(
        self,
        filter_column: str,
        lookback_days: int = 0,
    ) -> str:
        """Return an indented YAML block for the MongoDB filter expression.

        The MongoDB driver receives Jinja template strings as-is; `MongoToGCSOperator`
        renders them at task-execution time.

        Args:
            filter_column: Document field used as the range filter (e.g. ``updated_at``).
            lookback_days: Extra look-back buffer subtracted from ``data_interval_start``.
                           Useful for late-arriving documents.
        """
        gte_expr = (
            f"'{{{{ data_interval_start.subtract(days={lookback_days}) }}}}'" 
            if lookback_days > 0
            else "'{{ data_interval_start }}'"
        )
        return (
            f"    filter:\n"
            f"      {filter_column}:\n"
            f"        $gte: {gte_expr}\n"
            f"        $lt : '{{{{ data_interval_end }}}}'"
        )

    def build_bq_time_ranged_filter(
        self,
        filter_column: str,
        lookback_days: int = 0,
    ) -> str:
        """Return the BigQuery WHERE-clause fragment used in ``time_ranged_filter``.

        Filters on the *cast* column (already present in ``columns_definition``),
        not on the external-table raw column, so the expression uses the same
        Jinja variables as the MongoDB filter.

        Args:
            filter_column: BigQuery column name (should match the cast alias).
            lookback_days: Must be the same value used in :meth:`build_mongo_filter_yaml`.
        """
        gte_expr = (
            f"'{{{{ data_interval_start.subtract(days={lookback_days}) }}}}'"
            if lookback_days > 0
            else "'{{ data_interval_start }}'"
        )
        return (
            f"AND `{filter_column}` >= {gte_expr}\n"
            f"          AND `{filter_column}` <  '{{{{ data_interval_end }}}}'"
        )

    def generate_universal_parser_task_yaml(
        self,
        destination_table: str,
        field_types: Dict[str, str],
        load_strategy: str = LOAD_STRATEGY_FULL_REFRESH,
        filter_column: str = None,
        lookback_days: int = 0,
        unique_identifier: str = None,
    ) -> str:
        """Generate one entity task block for ``task_group.tasks[].tasks[]``.

        Args:
            destination_table: BigQuery table name.
            field_types: Ordered dict of field → BigQuery type from schema analysis.
            load_strategy: One of ``full_refresh``, ``incremental``, or ``merge``.

                * ``full_refresh`` — no MongoDB filter, uses
                  ``full_refresh_from_external_gcs.sql``.
                * ``incremental`` — scopes the Mongo extraction and the BigQuery
                  DELETE+INSERT to ``[data_interval_start, data_interval_end)``
                  via ``time_ranged_filter``. Requires ``filter_column``.
                * ``merge`` — scopes the Mongo extraction to
                  ``[data_interval_start, data_interval_end)`` but performs a
                  BigQuery MERGE keyed on ``unique_identifier`` instead of a
                  time-range delete; ``time_ranged_filter`` is left empty.
                  Requires both ``filter_column`` and ``unique_identifier``.

            filter_column: Datetime field used to window the MongoDB query
                (required for ``incremental`` and ``merge`` strategies).
            lookback_days: Extra look-back buffer (days) subtracted from
                ``data_interval_start`` in the Mongo query (and in the BQ
                ``time_ranged_filter`` for the ``incremental`` strategy).
            unique_identifier: Primary-key / unique column for MERGE ON.
                Required when ``load_strategy='merge'``.
        """
        fields = list(field_types.keys())
        projection_yaml = self.render_projection_yaml(fields)
        columns_def = self.generate_columns_definition(field_types)
        gcs_path = f"collection={self.collection_name}/date={{{{ ds }}}}/ts={{{{ ts_nodash }}}}.parquet"

        columns_definition_yaml = indent(columns_def, ' ' * 8)

        # ── ingest-to-gcs filter block ────────────────────────────────────────
        if filter_column and load_strategy in (self.LOAD_STRATEGY_INCREMENTAL, self.LOAD_STRATEGY_MERGE):
            filter_block = self.build_mongo_filter_yaml(filter_column, lookback_days)
        else:
            filter_block = "    filter: {}"

        # ── load-to-gbq-config: vary per strategy ─────────────────────────────
        if load_strategy == self.LOAD_STRATEGY_INCREMENTAL:
            sql_file = "load_data_from_gcs_to_gbq.sql"
            bq_filter_value = self.build_bq_time_ranged_filter(filter_column, lookback_days)
            time_ranged_filter_line = (
                f"      time_ranged_filter: >\n"
                f"          {bq_filter_value}"
            )
            partition_by_field = f"DATE(`{filter_column}`)"
            extra_params = ""

        elif load_strategy == self.LOAD_STRATEGY_MERGE:
            sql_file = "load_data_from_gcs_to_gbq_merge_insert_strategy.sql"
            time_ranged_filter_line = "      time_ranged_filter: ''"
            partition_by_field = f"DATE(`{filter_column}`)"
            extra_params = f"      unique_identifier: `{unique_identifier}`\n"

        else:  # full_refresh
            sql_file = "full_refresh_from_external_gcs.sql"
            time_ranged_filter_line = "      time_ranged_filter: ''"
            partition_by_field = "DATE_TRUNC(`__scheduled_at__`, DAY)"
            extra_params = ""

        return (
            f"- id: {destination_table}\n"
            f"  ingest-to-gcs:\n"
            f"    collection: {self.collection_name}\n"
            f"{filter_block}\n"
            f"    projection:\n"
            f"{projection_yaml}\n"
            f"    gcs_dest_path: {gcs_path}\n"
            f"    dest_data_type: parquet\n"
            f"  load-to-gbq-config:\n"
            f"    sql: {sql_file}\n"
            f"    params:\n"
            f"      project_id: *gcp_project_id\n"
            f"      dataset_id: *gcp_dataset_id\n"
            f"      table_id: {destination_table}\n"
            f"      external_table_format: PARQUET\n"
            f"      partition_by_field: {partition_by_field}\n"
            f"      cluster_by_fields: ''\n"
            f"{time_ranged_filter_line}\n"
            f"{extra_params}"
            f"      columns_definition: >\n"
            f"{columns_definition_yaml}\n"
        )

    def generate_legacy_dag_yaml(self, destination_table: str, field_types: Dict[str, str]) -> str:
        """Generate the legacy standalone YAML structure."""
        fields = list(field_types.keys())
        projection = self.generate_projection(fields)
        columns_def = self.generate_columns_definition(field_types)

        dag_name = f"mongo-to-gbq-{destination_table}"
        gcs_path = f"collection={self.collection_name}/date={{{{ ds }}}}/ts={{{{ ts_nodash }}}}.parquet"

        dag_structure = {
            dag_name: {
                'ingest-to-gcs': {
                    'collection': self.collection_name,
                    'projection': projection,
                    'gcs_dest_path': gcs_path,
                    'mongo_conn_id': f'*{self.conn_id}',
                    'dest_data_type': 'parquet'
                },
                'load-gcs-to-gbq': {
                    'sql': 'load_data_from_gcs_to_gbq.sql',
                    'params': {
                        'project_id': '*default_project_id',
                        'dataset_id': '*default_dataset_id',
                        'table_id': destination_table,
                        'columns_definition': columns_def,
                        'external_table_format': 'parquet',
                        'time_ranged_filter': '',
                        'external_table_path': gcs_path,
                        'partition_by_field': 'DATE_TRUNC(`__scheduled_at__`, DAY)',
                        'cluster_by_fields': ''
                    }
                }
            }
        }

        yaml.add_representer(
            str,
            lambda dumper, data: dumper.represent_scalar(
                'tag:yaml.org,2002:str', data, style='>' if '\n' in data else None
            )
        )

        return yaml.dump(dag_structure, default_flow_style=False, sort_keys=False, width=1000)

    def generate_dag_yaml(
        self,
        destination_table: str,
        field_types: Dict[str, str],
        output_format: str = DEFAULT_OUTPUT_FORMAT,
        load_strategy: str = LOAD_STRATEGY_FULL_REFRESH,
        filter_column: str = None,
        lookback_days: int = 0,
        unique_identifier: str = None,
    ) -> str:
        """Generate YAML output in the requested format."""
        if output_format == self.LEGACY_OUTPUT_FORMAT:
            return self.generate_legacy_dag_yaml(destination_table, field_types)

        return self.generate_universal_parser_task_yaml(
            destination_table,
            field_types,
            load_strategy=load_strategy,
            filter_column=filter_column,
            lookback_days=lookback_days,
            unique_identifier=unique_identifier,
        )
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")


def main():
    parser = argparse.ArgumentParser(
        description='Auto-generate BigQuery schema from MongoDB collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python mongodb_schema_generator.py \\
    --conn-id "mongo_default" \\
    --collection "t_board" \\
    --destination-table "t_board" \\
    --sample-size 1000

Universal parser task output (default):
    python mongodb_schema_generator.py \
        --conn-id "prod__mongo__oe_db__rw" \
        --collection "kpi_actualization" \
        --destination-table "kpi_actualization"

Environment variables:
  The script looks for MongoDB connection strings in .env file using these patterns:
  - {CONN_ID}
  - MONGO_{CONN_ID}
  - MONGODB_{CONN_ID}
  - {CONN_ID}_CONNECTION_STRING
  - MONGO_{CONN_ID}_CONNECTION_STRING
  - MONGODB_{CONN_ID}_CONNECTION_STRING
        """
    )
    
    parser.add_argument(
        '--conn-id',
        required=True,
        help='MongoDB connection ID to look up in .env file (e.g., mongo_default, prod_mongo)'
    )
    
    parser.add_argument(
        '--collection',
        required=True,
        help='MongoDB collection name'
    )
    
    parser.add_argument(
        '--destination-table',
        required=True,
        help='BigQuery destination table name'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=1000,
        help='Number of documents to sample for schema detection (default: 1000)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file path (optional, prints to stdout if not specified)'
    )

    parser.add_argument(
        '--output-format',
        choices=[
            MongoSchemaAnalyzer.DEFAULT_OUTPUT_FORMAT,
            MongoSchemaAnalyzer.LEGACY_OUTPUT_FORMAT,
        ],
        default=MongoSchemaAnalyzer.DEFAULT_OUTPUT_FORMAT,
        help=(
            'Output format. '
            'Use universal_parser_task to generate one item for task_group.tasks[].tasks[] '
            '(default), or legacy to keep the previous standalone structure.'
        )
    )

    parser.add_argument(
        '--load-strategy',
        choices=MongoSchemaAnalyzer.LOAD_STRATEGIES,
        default=MongoSchemaAnalyzer.LOAD_STRATEGY_FULL_REFRESH,
        help=(
            'Load strategy for the BigQuery side. '
            'full_refresh: truncate-and-reload via full_refresh_from_external_gcs.sql (default). '
            'incremental: delete-then-insert scoped by time_ranged_filter (requires --filter-column). '
            'merge: MERGE/upsert keyed on --unique-identifier, no time_ranged_filter on load '
            '(requires --filter-column and --unique-identifier).'
        )
    )

    parser.add_argument(
        '--filter-column',
        default=None,
        metavar='COLUMN',
        help=(
            'MongoDB datetime field used to window the extraction query '
            '(e.g. updated_at). Required for incremental and merge strategies. '
            'For incremental: also drives time_ranged_filter on the BQ load. '
            'For merge: scopes Mongo extraction only; BQ load uses MERGE ON unique_identifier.'
        )
    )

    parser.add_argument(
        '--lookback-days',
        type=int,
        default=0,
        metavar='N',
        help=(
            'Subtract N days from data_interval_start in the MongoDB query '
            '(and in time_ranged_filter for the incremental strategy) to catch '
            'late-arriving documents. Requires --filter-column. Default: 0.'
        )
    )

    parser.add_argument(
        '--unique-identifier',
        default=None,
        metavar='COLUMN',
        help=(
            'Primary-key / unique column used in the MERGE ON clause. '
            'Required when --load-strategy=merge (e.g. _id).'
        )
    )

    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env in current directory)'
    )
    
    args = parser.parse_args()
    
    # Set the .env file path if specified
    if args.env_file != '.env':
        load_dotenv(args.env_file)
    
    print("=" * 70)
    print("MongoDB to BigQuery Schema Generator")
    print("=" * 70)
    print(f"Connection ID: {args.conn_id}")
    print(f"Collection: {args.collection}")
    print(f"Destination Table: {args.destination_table}")
    print(f"Sample Size: {args.sample_size}")
    print(f"Env File: {args.env_file}")
    print(f"Output Format: {args.output_format}")
    print(f"Load Strategy: {args.load_strategy}")
    print(f"Filter Column: {args.filter_column or '(none)'}")
    if args.filter_column:
        print(f"Lookback Days: {args.lookback_days}")
    if args.load_strategy == MongoSchemaAnalyzer.LOAD_STRATEGY_MERGE:
        print(f"Unique Identifier: {args.unique_identifier or '(NOT SET — required for merge)'}")
    print("=" * 70)
    
    try:
        # ── validate argument combinations ────────────────────────────────────
        if args.load_strategy in (
            MongoSchemaAnalyzer.LOAD_STRATEGY_INCREMENTAL,
            MongoSchemaAnalyzer.LOAD_STRATEGY_MERGE,
        ) and not args.filter_column:
            parser.error(
                f"--filter-column is required when --load-strategy={args.load_strategy}"
            )

        if args.load_strategy == MongoSchemaAnalyzer.LOAD_STRATEGY_MERGE and not args.unique_identifier:
            parser.error(
                "--unique-identifier is required when --load-strategy=merge"
            )

        # Initialize analyzer
        analyzer = MongoSchemaAnalyzer(
            conn_id=args.conn_id,
            collection_name=args.collection,
            sample_size=args.sample_size
        )
        
        # Connect to MongoDB
        analyzer.connect()
        
        # Get all fields
        fields = analyzer.get_all_fields()
        if not fields:
            print("✗ No fields found in collection")
            sys.exit(1)
        
        # Analyze field types
        field_types = analyzer.analyze_field_types(fields)
        
        # Generate YAML
        print("→ Generating DAG YAML definition...")
        yaml_output = analyzer.generate_dag_yaml(
            args.destination_table,
            field_types,
            output_format=args.output_format,
            load_strategy=args.load_strategy,
            filter_column=args.filter_column,
            lookback_days=args.lookback_days,
            unique_identifier=args.unique_identifier,
        )
        
        # Output results
        print("=" * 70)
        print("✓ Generation complete!")
        print("=" * 70)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(yaml_output)
            print(f"✓ YAML written to: {args.output}")
        else:
            print("\nGenerated YAML:\n")
            print(yaml_output)
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"Summary:")
        print(f"  - Total fields: {len(fields)}")
        print(f"  - Field type breakdown:")
        type_counts = {}
        for bq_type in field_types.values():
            type_counts[bq_type] = type_counts.get(bq_type, 0) + 1
        for bq_type, count in sorted(type_counts.items()):
            print(f"    • {bq_type}: {count}")
        print("=" * 70)
        
    except ValueError as e:
        print(f"✗ Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if 'analyzer' in locals():
            analyzer.close()


if __name__ == '__main__':
    main()
