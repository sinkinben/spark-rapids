/*
 * Copyright (c) 2022, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.nvidia.spark.rapids.shims

import ai.rapids.cudf.{ColumnView, DType}
import com.nvidia.spark.rapids.GpuOrcScan

import java.util.concurrent.TimeUnit

object OrcCastingShims {

  def castIntegerToTimestamp(col: ColumnView, colType: DType): ColumnView = {
    // For spark >= 320 (except spark-321-cdh), they consider the integers in `col` as seconds
    GpuOrcScan.castIntegersToTimestamp(col, colType, TimeUnit.SECONDS)
  }
}
