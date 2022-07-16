# Copyright (c) 2020-2022, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from asserts import assert_gpu_and_cpu_are_equal_collect, assert_gpu_and_cpu_are_equal_sql
from data_gen import *
from spark_session import is_before_spark_340


@pytest.mark.parametrize('data_gen', all_basic_gens + decimal_gens + array_gens_sample + map_gens_sample + struct_gens_sample, ids=idfn)
def test_simple_limit(data_gen):
    assert_gpu_and_cpu_are_equal_collect(
            # We need some processing after the limit to avoid a CollectLimitExec
            lambda spark : unary_op_df(spark, data_gen, num_slices=1).limit(10).repartition(1),
            conf = {'spark.sql.execution.sortBeforeRepartition': 'false'})


# This conf allows CollectLimitExec and GlobalLimitExec to run on GPU
offset_test_conf = {
    'spark.rapids.sql.exec.CollectLimitExec': 'true',
    'spark.rapids.sql.exec.GlobalLimitExec': 'true'
}


@pytest.mark.parametrize('offset', [0, 10, 2048, 4096])
@pytest.mark.skipif(is_before_spark_340(), reason='offset is introduced from Spark 3.4.0')
def test_non_zero_offset(offset):
    # offset is used in the test cases having no limit
    # 0: corner case
    # 1024: offset < df.numRows
    # 2048: offset = df.numRows
    # 4096: offset > df.numRows

    offset_sql = "select * from tmp_table offset {}".format(offset)
    data_gen = StructGen([('c1', int_gen),('c2', int_gen),('c3', int_gen)], nullable=False)
    assert_gpu_and_cpu_are_equal_sql(lambda spark: gen_df(spark, data_gen, length=2048), 'tmp_table',
                                     offset_sql, conf=offset_test_conf)


@pytest.mark.parametrize('limit, offset', [(0, 0), (1024, 500), (2048, 456), (3000, 111), (500, 500), (100, 600)])
@pytest.mark.skipif(is_before_spark_340(), reason='offset is introduced from Spark 3.4.0')
def test_non_zero_offset_with_limit(limit, offset):
    # In CPU version of spark, (limit, offset) can not be negative number.
    # Test case description:
    # (0, 0): Corner case: both limit and offset are 0
    # (1024, 500): offset < limit && limit < df.numRows
    # (2048, 456): offset < limit && limit = df.numRows
    # (3000, 111): offset < limit && limit > df.numRows
    # (500, 500): limit = offset
    # (100, 600): limit > offset

    data_gen = StructGen([('c1', int_gen),('c2', int_gen),('c3', int_gen)], nullable=False)
    limit_offset_sql = "select * from tmp_table limit {} offset {}".format(limit, offset)
    assert_gpu_and_cpu_are_equal_sql(lambda spark: gen_df(spark, data_gen, length=2048), 'tmp_table',
                                     limit_offset_sql, conf=offset_test_conf)
