#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import json

from airflow.providers.apache.druid.operators.druid import DruidOperator
from airflow.utils import timezone

DEFAULT_DATE = timezone.datetime(2017, 1, 1)

JSON_INDEX_STR = """
    {
        "type": "{{ params.index_type }}",
        "datasource": "{{ params.datasource }}",
        "spec": {
            "dataSchema": {
                "granularitySpec": {
                    "intervals": ["{{ ds }}/{{ macros.ds_add(ds, 1) }}"]
                }
            }
        }
    }
"""

RENDERED_INDEX = {
    "type": "index_hadoop",
    "datasource": "datasource_prd",
    "spec": {"dataSchema": {"granularitySpec": {"intervals": ["2017-01-01/2017-01-02"]}}},
}


def test_render_template(dag_maker):
    with dag_maker("test_druid_render_template", default_args={"start_date": DEFAULT_DATE}):
        operator = DruidOperator(
            task_id="spark_submit_job",
            json_index_file=JSON_INDEX_STR,
            params={"index_type": "index_hadoop", "datasource": "datasource_prd"},
        )

    dag_maker.create_dagrun().task_instances[0].render_templates()
    assert RENDERED_INDEX == json.loads(operator.json_index_file)


def test_render_template_from_file(tmp_path, dag_maker):
    json_index_file = tmp_path.joinpath("json_index.json")
    json_index_file.write_text(JSON_INDEX_STR)

    with dag_maker(
        "test_druid_render_template_from_file",
        template_searchpath=[str(tmp_path)],
        default_args={"start_date": DEFAULT_DATE},
    ):
        operator = DruidOperator(
            task_id="spark_submit_job",
            json_index_file=json_index_file.name,
            params={"index_type": "index_hadoop", "datasource": "datasource_prd"},
        )

    dag_maker.create_dagrun().task_instances[0].render_templates()
    assert RENDERED_INDEX == json.loads(operator.json_index_file)
