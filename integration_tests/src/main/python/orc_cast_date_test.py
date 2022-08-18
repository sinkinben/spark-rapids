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

from asserts import assert_gpu_and_cpu_are_equal_collect, assert_gpu_and_cpu_error
from data_gen import *
from pyspark.sql.types import *
from spark_session import with_cpu_session


@pytest.mark.parametrize('to_type', ['timestamp', 'string'])
def test_casting_from_date(spark_tmp_path, to_type):
    orc_path = spark_tmp_path + '/orc_casting_from_date'

    # This case is failed
    # data_gen = [('date_column', DateGen(end=date(1582, 1, 1)))]
    # length = 10

    # This case is fine
    data_gen = [('date_column', DateGen(start=date(1582,10,15)))]
    length = 2048

    with_cpu_session(
        func=lambda spark: gen_df(spark, data_gen, length=length).write.orc(orc_path),
    )

    assert_gpu_and_cpu_are_equal_collect(
        func=lambda spark: spark.read.schema("date_column {}".format(to_type)).orc(orc_path),
    )