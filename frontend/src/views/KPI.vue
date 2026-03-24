<template>
  <div class="page-shell kpi-container">
    <section class="page-hero">
      <div class="page-hero__content">
        <div class="page-hero__eyebrow">{{ LT.heroEyebrow }}</div>
        <h2 class="page-hero__title">{{ LT.heroTitle }}</h2>
        <p class="page-hero__desc">{{ DT.hero }}</p>
      </div>
      <div class="page-hero__actions">
        <div class="glass-pill">{{ DT.scope }}</div>
        <div v-if="showScatterChart" class="glass-pill">Comparison Axes: {{ getMetricName(scatterXMetric) }} / {{ getMetricName(scatterYMetric) }}</div>
        <div v-if="showScatterChart" class="glass-pill">Best Region: {{ getScatterBestRegionText(scatterXMetric, scatterYMetric) }}</div>
      </div>
    </section>

    <el-card class="section-card category-focus-card">
      <div class="category-focus">
        <div class="category-focus__left">
          <div class="category-focus__eyebrow">{{ LT.category.eyebrow }}</div>
          <h3 class="category-focus__title">{{ LT.category.title }}</h3>
          <p class="category-focus__desc">{{ DT.categoryCurrentPrefix }} <strong>{{ modelCategory }}</strong>. {{ DT.categoryCurrentSuffix }}</p>
        </div>
      </div>

      <div class="category-explorer">
        <aside class="category-explorer__sidebar">
          <div class="category-explorer__toolbar">
            <div class="category-explorer__summary">
              <span class="category-explorer__count">{{ filteredSchemaCategories.length }} / {{ MODEL_CATEGORY_KEYS.length }} model types</span>
              <span class="category-explorer__hint">Compact navigator for future expansion</span>
            </div>
            <el-input
              v-model="categoryKeyword"
              clearable
              placeholder="Search model type"
              class="category-search-input"
            />
          </div>

          <div v-if="filteredSchemaCategories.length" class="category-nav-list">
            <button
              v-for="category in filteredSchemaCategories"
              :key="category.key"
              type="button"
              class="category-nav-item"
              :class="{ 'is-active': category.key === modelCategory }"
              @click="selectModelCategory(category.key)"
            >
              <span class="category-nav-item__title">{{ category.key }}</span>
            </button>
          </div>

          <div v-else class="category-empty-state">
            No model type matches "{{ categoryKeyword }}"
          </div>
        </aside>

        <section v-if="activeCategoryMeta" class="category-detail-card">
          <div class="category-detail-card__header">
            <div>
              <div class="category-detail-card__eyebrow">Current model type</div>
              <h4 class="category-detail-card__title">{{ activeCategoryMeta.label || activeCategoryMeta.key }}</h4>
            </div>
            <div class="category-detail-card__header-actions">
              <el-tag size="small" type="success">{{ LT.category.current }}</el-tag>
              <div v-if="canCreateOrEditTest()" class="category-schema-actions">
                <el-button size="small" type="primary" @click="openCreateCategoryDialog">New Type</el-button>
                <el-button size="small" @click="openEditCategoryDialog(activeCategoryMeta)">Edit</el-button>
                <el-button size="small" type="danger" plain @click="deleteCategoryDefinition(activeCategoryMeta)">Delete</el-button>
              </div>
            </div>
          </div>

          <p class="category-detail-card__desc">{{ activeCategoryMeta.description || MODEL_CATEGORY_INFO[activeCategoryMeta.key] }}</p>

          <div class="category-detail-section">
            <div class="category-detail-section__title">Typical implementation</div>
            <p class="category-detail-section__body">
              {{ activeCategoryMeta.implementation_notes || 'No implementation notes have been defined yet.' }}
            </p>
          </div>

          <div class="category-detail-section">
            <div class="category-detail-section__title">Parameter definitions</div>
            <div class="category-parameter-list">
              <article
                v-for="metric in getMetricDefsForCategory(activeCategoryMeta.key)"
                :key="`${activeCategoryMeta.key}-${metric.value}`"
                class="category-parameter-item"
              >
                <div class="category-parameter-item__header">
                  <div>
                    <div class="category-parameter-item__title">{{ metric.label }}</div>
                    <div class="category-parameter-item__meta">
                      {{ metric.value }}
                      <span v-if="metric.unit"> · {{ metric.unit }}</span>
                      <span> · {{ getMetricPreferenceText(metric.value) }}</span>
                    </div>
                  </div>
                </div>
                <p class="category-parameter-item__desc">{{ metric.definition || 'No parameter definition has been defined yet.' }}</p>
              </article>
            </div>
          </div>
        </section>
      </div>
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.ladder }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.ladder }}</span>
          </div>
          <div class="metric-tag-group" role="tablist" aria-label="Ladder metric selector">
            <button
              v-for="item in LADDER_METRIC_OPTIONS"
              :key="item.value"
              type="button"
              class="metric-tag"
              :class="{ 'is-active': ladderMetric === item.value }"
              role="tab"
              :aria-selected="ladderMetric === item.value"
              @click="selectLadderMetric(item.value)"
            >
              {{ item.label }}
            </button>
          </div>
        </div>
      </template>
      <v-chart
        class="chart"
        :option="ladderChartOption"
        v-loading="ladderLoading"
        @click="handleChartSingleClick"
        @dblclick="handleChartDoubleClick"
        style="height: 400px"
      />
    </el-card>

    <el-card v-if="showScatterChart" class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>{{ LT.section.scatter }}</h3>
            <span class="section-title__meta">{{ DT.sectionMeta.scatter }}</span>
          </div>
          <div class="scatter-selector-wrap">
            <div class="metric-tag-group" role="group" aria-label="Scatter plot metric selector">
              <button
                v-for="item in SCATTER_METRIC_OPTIONS"
                :key="item.value"
                type="button"
                class="metric-tag"
                :class="{ 'is-active': scatterMetricSelection.includes(item.value) }"
                @click="toggleScatterMetric(item.value)"
              >
                {{ item.label }}
              </button>
            </div>
            <span class="selector-hint">{{ DT.scatterHint }}</span>
          </div>
        </div>
      </template>
      <v-chart
        class="chart"
        :option="scatterChartOption"
        v-loading="scatterLoading"
        @click="handleChartSingleClick"
        @dblclick="handleChartDoubleClick"
        style="height: 400px"
      />
    </el-card>

    <el-card class="section-card">
      <template #header>
        <div class="section-title">
          <div class="section-title__main">
            <h3>Model List</h3>
            <span class="section-title__meta">Only latest test-time data is shown for each model name</span>
          </div>
          <div class="compare-toolbar">
            <el-button type="primary" @click="openCompareDialog">{{ BT.compareModels }}</el-button>
            <template v-if="canManageKPI">
              <el-button type="warning" @click="openUpdatePickerDialog">Update Model</el-button>
              <el-button type="success" @click="openCreateModelDialog">New Model</el-button>
            </template>
          </div>
        </div>
      </template>

      <el-table :data="modelList" v-loading="modelListLoading" stripe table-layout="fixed" class="model-list-table">
        <el-table-column prop="model_name" label="Model Name" align="center" header-align="center">
          <template #default="{ row }">
            <button type="button" class="model-link-btn" @click="goModelDetail(row.model_name)">
              {{ row.model_name }}
            </button>
          </template>
        </el-table-column>
        <el-table-column prop="test_version" label="Test Version" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="model_size" label="Model Size" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="source" label="Source" align="center" header-align="center" show-overflow-tooltip />
        <el-table-column prop="test_date" label="Test Time" align="center" header-align="center">
          <template #default="{ row }">{{ formatDateTime(row.test_date) }}</template>
        </el-table-column>
        <el-table-column v-if="canManageKPI" label="Actions" align="center" header-align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <el-button size="small" @click="openEditModelDialog(row)">Update</el-button>
              <el-button size="small" type="danger" plain @click="deleteModelRow(row)">Delete</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showModelDialog" :title="isEditingModel ? 'Edit Model (Latest Test Run)' : 'New Model Test Run'" width="760px">
      <el-form :model="modelForm" label-width="170px" class="model-dialog-form">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Model Category">
              <el-select v-model="modelForm.model_category" style="width: 100%">
                <el-option v-for="key in MODEL_CATEGORY_KEYS" :key="key" :label="key" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model Name">
              <el-input v-model="modelForm.model_name" :disabled="isEditingModel" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Source">
              <el-input v-model="modelForm.source" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model Size">
              <el-input v-model="modelForm.model_size" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description">
          <el-input v-model="modelForm.description" type="textarea" :rows="2" />
        </el-form-item>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Test Time">
              <el-date-picker
                v-model="modelForm.test_date"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Test Platform">
              <el-input v-model="modelForm.test_platform" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Test Version">
              <el-input v-model="modelForm.test_version" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Test Condition">
              <el-input v-model="modelForm.test_condition" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="12">
          <el-col v-for="metric in MODEL_FORM_METRICS" :key="metric.value" :span="24">
            <el-form-item :label="metric.label">
              <el-input-number
                v-model="modelForm.metrics[metric.value]"
                :min="getMetricMin(metric.value)"
                :max="getMetricMax(metric.value)"
                :step="0.01"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showModelDialog = false">Cancel</el-button>
        <el-button v-if="canManageKPI" type="primary" :loading="modelDialogSaving" @click="saveModelDialog">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCompareDialog" :title="LT.compare.title" width="920px">
      <div class="compare-toolbar">
        <el-select v-model="compareModelA" :placeholder="DT.placeholders.selectModelA" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`a-${name}`" :label="name" :value="name" />
        </el-select>
        <el-select v-model="compareModelB" :placeholder="DT.placeholders.selectModelB" style="width: 240px">
          <el-option v-for="name in availableModelNames" :key="`b-${name}`" :label="name" :value="name" />
        </el-select>
      </div>

      <el-table :data="compareRows" stripe :empty-text="DT.placeholders.compareEmpty">
        <el-table-column prop="label" :label="LT.compare.parameter" width="220" />
        <el-table-column prop="modelA" :label="compareModelA || LT.compare.modelA" min-width="220" />
        <el-table-column prop="modelB" :label="compareModelB || LT.compare.modelB" min-width="220" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="showUpdatePickerDialog" title="Update Existing Model" width="500px">
      <el-form label-width="110px">
        <el-form-item label="Model Name">
          <el-select v-model="selectedUpdateModelName" style="width: 100%" filterable placeholder="Select model to update">
            <el-option
              v-for="row in modelList"
              :key="`update-${row.model_name}`"
              :label="row.model_name"
              :value="row.model_name"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpdatePickerDialog = false">Cancel</el-button>
        <el-button v-if="canManageKPI" type="primary" @click="confirmUpdateModelSelection">Update</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCategoryDialog" :title="isEditingCategory ? 'Edit Model Type' : 'New Model Type'" width="960px">
      <el-form :model="categoryForm" label-width="170px" class="model-dialog-form">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Model Type Key">
              <el-input v-model="categoryForm.key" :disabled="isEditingCategory" placeholder="For example: Noise Suppression" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Display Label">
              <el-input v-model="categoryForm.label" placeholder="Displayed title" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Function Description">
          <el-input v-model="categoryForm.description" type="textarea" :rows="3" placeholder="What this model type is used for" />
        </el-form-item>

        <el-form-item label="Typical Implementation">
          <el-input v-model="categoryForm.implementation_notes" type="textarea" :rows="4" placeholder="How this model type is commonly implemented" />
        </el-form-item>

        <div class="category-editor-head">
          <div>
            <h4 class="category-editor-head__title">Parameters</h4>
            <p class="category-editor-head__desc">Define the metrics shown in charts, forms, and descriptions.</p>
          </div>
          <el-button type="primary" plain @click="addCategoryMetricRow">Add Parameter</el-button>
        </div>

        <div class="category-editor-list">
          <section v-for="(metric, index) in categoryForm.metrics" :key="`category-metric-${index}`" class="category-editor-item">
            <div class="category-editor-item__toolbar">
              <strong>Parameter {{ index + 1 }}</strong>
              <el-button type="danger" link @click="removeCategoryMetricRow(index)">Remove</el-button>
            </div>

            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="Metric Key" label-width="120px">
                  <el-input v-model="metric.key" placeholder="For example: snr_score" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Label" label-width="120px">
                  <el-input v-model="metric.label" placeholder="Display name" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Unit" label-width="120px">
                  <el-input v-model="metric.unit" placeholder="For example: ms / % / W" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="Direction" label-width="120px">
                  <el-select v-model="metric.direction" style="width: 100%">
                    <el-option label="Higher is better" value="higher" />
                    <el-option label="Lower is better" value="lower" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="16">
                <el-form-item label="Chart Roles" label-width="120px">
                  <el-select v-model="metric.chart_roles" multiple collapse-tags collapse-tags-tooltip style="width: 100%">
                    <el-option label="ladder" value="ladder" />
                    <el-option label="scatter" value="scatter" />
                    <el-option label="table" value="table" />
                    <el-option label="form" value="form" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Definition" label-width="120px">
              <el-input v-model="metric.definition" type="textarea" :rows="3" placeholder="Explain what this parameter means" />
            </el-form-item>
          </section>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showCategoryDialog = false">Cancel</el-button>
        <el-button type="primary" :loading="categoryDialogSaving" @click="saveCategoryDialog">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createKPISchemaCategory,
  deleteKPISchemaCategory,
  getKPISchema,
  getKPIMetrics,
  getLadderChartData,
  getScatterChartData,
  getKPIModelLatestList,
  createKPIModel,
  updateKPISchemaCategory,
  updateKPILatestModel,
  deleteKPIModel
} from '../api/kpi'
import { canCreateOrEditTest } from '../stores/auth'
import { LabelText } from '../texts/LabelText'
import { ButtonText } from '../texts/ButtonText'
import { DescriptionText } from '../texts/DescriptionText'

const LT = LabelText.kpi
const BT = ButtonText.kpi
const DT = DescriptionText.kpi
const router = useRouter()
const canManageKPI = computed(() => canCreateOrEditTest())

const SCATTER_PALETTE = ['#22d3ee', '#60a5fa', '#a78bfa', '#f472b6', '#fb7185', '#f59e0b', '#34d399', '#facc15', '#38bdf8', '#818cf8']

const kpiSchema = ref({ categories: [] })

const schemaCategories = computed(() => {
  return Array.isArray(kpiSchema.value?.categories) ? kpiSchema.value.categories : []
})

const MODEL_CATEGORY_INFO = computed(() => {
  return Object.fromEntries(
    schemaCategories.value.map((category) => [
      category.key,
      category.description || `${category.key} metrics`
    ])
  )
})

const MODEL_CATEGORY_KEYS = computed(() => schemaCategories.value.map((category) => category.key))

const CATEGORY_METRIC_DEFS = computed(() => {
  const mapping = {}
  schemaCategories.value.forEach((category) => {
    mapping[category.key] = (category.metrics || []).map((metric) => ({
      label: metric.label || metric.key,
      value: metric.key,
      unit: metric.unit || '',
      direction: metric.direction || 'higher',
      chart_roles: Array.isArray(metric.chart_roles) ? metric.chart_roles : [],
      definition: metric.definition || ''
    }))
  })
  return mapping
})

const METRIC_META_MAP = computed(() => {
  const mapping = {}
  Object.values(CATEGORY_METRIC_DEFS.value)
    .flat()
    .forEach((metric) => {
      if (!mapping[metric.value]) {
        mapping[metric.value] = metric
      }
    })
  return mapping
})

const METRIC_LABEL_MAP = computed(() => {
  return Object.fromEntries(
    Object.entries(METRIC_META_MAP.value).map(([key, meta]) => [key, meta.label || key])
  )
})

const METRIC_UNITS = computed(() => {
  return Object.fromEntries(
    Object.entries(METRIC_META_MAP.value).map(([key, meta]) => [key, meta.unit || ''])
  )
})

const LOWER_IS_BETTER_METRICS = computed(() => {
  return new Set(
    Object.entries(METRIC_META_MAP.value)
      .filter(([, meta]) => String(meta.direction || 'higher').toLowerCase() === 'lower')
      .map(([key]) => key)
  )
})

const LEGACY_METRIC_FALLBACKS = {
  accuracy_total: ['accuracy_overall'],
  accuracy_cn: ['accuracy_zh'],
  e2e_latency: ['latency']
}

const getMetricDefsForCategory = (category, role = null) => {
  const categoryMap = CATEGORY_METRIC_DEFS.value || {}
  const fallbackCategory = schemaCategories.value[0]?.key
  const defs = categoryMap[category] || (fallbackCategory ? categoryMap[fallbackCategory] : []) || []
  if (!role) {
    return defs
  }
  return defs.filter((metric) => {
    const roles = Array.isArray(metric.chart_roles) ? metric.chart_roles : []
    return roles.includes(role)
  })
}

const getMetricValueByKey = (metrics = {}, metricKey = '') => {
  if (!metricKey) return null
  if (metrics?.[metricKey] !== undefined) {
    return metrics[metricKey]
  }
  const fallbacks = LEGACY_METRIC_FALLBACKS[metricKey] || []
  for (const fallbackKey of fallbacks) {
    if (metrics?.[fallbackKey] !== undefined) {
      return metrics[fallbackKey]
    }
  }
  return null
}

const MODEL_META_INFO = {
  'Model-A': {
    description: 'A lightweight model optimized for general speech recognition, with emphasis on real-time transcription and edge deployment.',
    source: 'Internal Benchmark Set A',
    modelSize: '1.2B'
  },
  'Model-B': {
    description: 'A standard baseline model for speech synthesis that balances voice stability and latency.',
    source: 'Internal TTS Baseline',
    modelSize: '980M'
  },
  'Model-C': {
    description: 'A multilingual translation model focused on accuracy and throughput across Chinese, English, and Spanish.',
    source: 'Translation Eval Pack',
    modelSize: '1.6B'
  },
  'Model-D': {
    description: 'A real-time call translation model optimized for streaming speech processing and pipeline stability.',
    source: 'Voicecall Solution Suite',
    modelSize: '2.1B'
  },
  'Model-E': {
    description: 'An enhanced ASR model focused on recognition robustness in complex noisy environments.',
    source: 'ASR Robustness Set',
    modelSize: '1.4B'
  },
  'Model-F': {
    description: 'A next-generation multilingual translation model focused on long-sentence semantics and cross-domain terminology consistency.',
    source: 'Global Translation Benchmark v2',
    modelSize: '1.9B'
  }
}

const getModelColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return SCATTER_PALETTE[(seed + index) % SCATTER_PALETTE.length]
}

const roundToTwo = (value) => Number(value.toFixed(2))

const toDisplayMetricNumber = (value, metricName = '') => {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) {
    return null
  }
  return roundToTwo(numeric)
}

const isLowerBetterMetric = (metricName = '') => LOWER_IS_BETTER_METRICS.value.has(String(metricName || '').trim())

const getMetricPreferenceText = (metricName = '') => (isLowerBetterMetric(metricName) ? 'lower is better' : 'higher is better')

const getLadderMetricTitle = (metricName = '') => `${getMetricName(metricName)} Ranking • ${getMetricPreferenceText(metricName)}`

const getScatterBestRegionText = (xMetric = '', yMetric = '') => {
  const horizontal = isLowerBetterMetric(xMetric) ? 'left' : 'right'
  const vertical = isLowerBetterMetric(yMetric) ? 'bottom' : 'top'
  return `${vertical}-${horizontal}`
}

const getScatterMetricTitle = (xMetric = '', yMetric = '') => {
  return `${getMetricName(xMetric)} vs ${getMetricName(yMetric)} • Best region: ${getScatterBestRegionText(xMetric, yMetric)}`
}

const isMetricBetterOrEqual = (candidate, target, metricName = '') => {
  return isLowerBetterMetric(metricName) ? candidate <= target : candidate >= target
}

const isMetricStrictlyBetter = (candidate, target, metricName = '') => {
  return isLowerBetterMetric(metricName) ? candidate < target : candidate > target
}

const isParetoDominated = (candidate, target, xMetric = '', yMetric = '') => {
  const betterOrEqualX = isMetricBetterOrEqual(candidate.rawX, target.rawX, xMetric)
  const betterOrEqualY = isMetricBetterOrEqual(candidate.rawY, target.rawY, yMetric)
  const strictlyBetterX = isMetricStrictlyBetter(candidate.rawX, target.rawX, xMetric)
  const strictlyBetterY = isMetricStrictlyBetter(candidate.rawY, target.rawY, yMetric)

  return betterOrEqualX && betterOrEqualY && (strictlyBetterX || strictlyBetterY)
}

const buildParetoFront = (points = [], xMetric = '', yMetric = '') => {
  return points.filter((target) => {
    return !points.some((candidate) => {
      if (candidate.modelName === target.modelName) {
        return false
      }
      return isParetoDominated(candidate, target, xMetric, yMetric)
    })
  })
}

const getLadderBarColor = (modelName, index) => {
  const seed = [...(modelName || '')].reduce((sum, ch) => sum + ch.charCodeAt(0), 0)
  return SCATTER_PALETTE[(seed + index * 3) % SCATTER_PALETTE.length]
}

const calcAxisRange = (values) => {
  if (!values.length) {
    return { min: null, max: null }
  }

  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)

  if (minVal === maxVal) {
    const pad = Math.max(Math.abs(minVal) * 0.08, 1)
    return {
      min: roundToTwo(minVal - pad),
      max: roundToTwo(maxVal + pad)
    }
  }

  const span = maxVal - minVal
  const pad = span * 0.18

  return {
    min: roundToTwo(minVal - pad),
    max: roundToTwo(maxVal + pad)
  }
}

const ladderLoading = ref(false)
const scatterLoading = ref(false)
const ladderMetric = ref('')
const modelCategory = ref('')
const categoryKeyword = ref('')
const scatterMetricSelection = ref([])
const scatterXMetric = ref('')
const scatterYMetric = ref('')
const selectedModelName = ref('')
const showCompareDialog = ref(false)
const compareModelA = ref('')
const compareModelB = ref('')
const ladderRecords = ref([])
const scatterRecords = ref([])
const kpiMetrics = ref([])
const modelList = ref([])
const modelListLoading = ref(false)
const showModelDialog = ref(false)
const modelDialogSaving = ref(false)
const editingModelName = ref('')
const showUpdatePickerDialog = ref(false)
const selectedUpdateModelName = ref('')
const showCategoryDialog = ref(false)
const categoryDialogSaving = ref(false)
const editingCategoryKey = ref('')

const LADDER_METRIC_OPTIONS = computed(() => getMetricDefsForCategory(modelCategory.value, 'ladder'))

const SCATTER_METRIC_OPTIONS = computed(() => getMetricDefsForCategory(modelCategory.value, 'scatter'))

const showScatterChart = computed(() => SCATTER_METRIC_OPTIONS.value.length > 1)

const MODEL_FORM_METRICS = computed(() => {
  const preferred = getMetricDefsForCategory(modelForm.value.model_category || modelCategory.value, 'form')
  return preferred.length ? preferred : getMetricDefsForCategory(modelForm.value.model_category || modelCategory.value)
})

const filteredSchemaCategories = computed(() => {
  const keyword = String(categoryKeyword.value || '').trim().toLowerCase()
  if (!keyword) {
    return schemaCategories.value
  }

  const matched = schemaCategories.value.filter((category) => {
    const haystack = [category.key, category.label, category.description]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return haystack.includes(keyword)
  })

  const current = schemaCategories.value.find((category) => category.key === modelCategory.value)
  if (current && !matched.some((category) => category.key === current.key)) {
    return [current, ...matched]
  }

  return matched
})

const activeCategoryMeta = computed(() => {
  return schemaCategories.value.find((category) => category.key === modelCategory.value) || null
})

const createEmptyCategoryMetric = () => ({
  key: '',
  label: '',
  unit: '',
  direction: 'higher',
  chart_roles: ['ladder', 'table', 'form'],
  definition: ''
})

const createDefaultCategoryForm = () => ({
  key: '',
  label: '',
  description: '',
  implementation_notes: '',
  metrics: [createEmptyCategoryMetric()]
})

const categoryForm = ref(createDefaultCategoryForm())
const isEditingCategory = computed(() => Boolean(editingCategoryKey.value))

const buildDefaultMetricsForCategory = (category) => {
  const defaults = {}
  const defs = getMetricDefsForCategory(category, 'form')
  const selectedDefs = defs.length ? defs : getMetricDefsForCategory(category)
  selectedDefs.forEach((metric) => {
    defaults[metric.value] = 0
  })
  return defaults
}

const createDefaultModelForm = (category = (modelCategory.value || schemaCategories.value[0]?.key || '')) => ({
  model_category: category,
  model_name: '',
  source: '',
  model_size: '',
  description: '',
  test_date: '',
  test_platform: '',
  test_version: '',
  test_condition: '',
  metrics: buildDefaultMetricsForCategory(category)
})

const modelForm = ref(createDefaultModelForm())
const isEditingModel = computed(() => Boolean(editingModelName.value))

const metricsByModel = computed(() => {
  const grouped = {}
  for (const item of kpiMetrics.value) {
    if (!grouped[item.model_name]) {
      grouped[item.model_name] = {}
    }
    grouped[item.model_name][item.metric_name] = item.metric_value
  }
  return grouped
})

const modelMetaByName = computed(() => {
  const grouped = {}
  for (const item of kpiMetrics.value) {
    const existing = grouped[item.model_name]
    const currentDate = item.test_date ? new Date(item.test_date).getTime() : 0
    const existingDate = existing?.__date || 0

    if (!existing || currentDate >= existingDate) {
      grouped[item.model_name] = {
        source: item.source || '',
        modelSize: item.model_size || '',
        description: item.description || '',
        __date: currentDate
      }
    }
  }

  Object.keys(grouped).forEach((name) => {
    delete grouped[name].__date
  })

  return grouped
})

const availableModelNames = computed(() => Object.keys(metricsByModel.value))

const selectedModelInfo = computed(() => {
  const name = selectedModelName.value || ladderSummary.value.topModel || '--'
  const dynamicMeta = modelMetaByName.value[name] || {}
  const staticMeta = MODEL_META_INFO[name] || {
    description: 'Add a detailed description for this model in MODEL_META_INFO.',
    source: 'TBD',
    modelSize: 'TBD'
  }

  return {
    name,
    ...staticMeta,
    ...dynamicMeta,
    metrics: metricsByModel.value[name] || {}
  }
})

const compareRows = computed(() => {
  if (!compareModelA.value || !compareModelB.value || compareModelA.value === compareModelB.value) {
    return []
  }

  const modelAInfo = buildModelInfo(compareModelA.value)
  const modelBInfo = buildModelInfo(compareModelB.value)

  const baseRows = [
    { label: 'Model Category', modelA: modelCategory.value, modelB: modelCategory.value },
    { label: 'Description', modelA: modelAInfo.description, modelB: modelBInfo.description },
    { label: 'Source', modelA: modelAInfo.source, modelB: modelBInfo.source },
    { label: 'Model Size', modelA: modelAInfo.modelSize, modelB: modelBInfo.modelSize }
  ]

  const metricRows = getMetricDefsForCategory(modelCategory.value).map((metric) => ({
    label: metric.label,
    modelA: formatMetricValue(getMetricValueByKey(modelAInfo.metrics, metric.value), metric.value),
    modelB: formatMetricValue(getMetricValueByKey(modelBInfo.metrics, metric.value), metric.value)
  }))

  return [...baseRows, ...metricRows]
})

const ladderChartOption = ref({
  title: {
    text: 'Model Performance Ranking',
    left: 'center',
    textStyle: {
      color: '#f8fafc',
      fontSize: 18,
      fontWeight: 700
    }
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params) => {
      const row = Array.isArray(params) ? params[0] : params
      if (!row) return ''
      const modelName = row.name || row.axisValue || ''
      const rawValue = typeof row.data === 'object' && row.data !== null ? row.data.value : row.value
      return `${modelName}<br/>${getMetricName(ladderMetric.value)}: ${formatMetricValue(rawValue, ladderMetric.value, { alreadyDisplay: true })}`
    }
  },
  grid: {
    left: 24,
    right: 36,
    top: 70,
    bottom: 24,
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Metric Value',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'category',
    data: [],
    name: 'Model Name',
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' }
  },
  series: [
    {
      name: 'Performance Metric',
      type: 'bar',
      data: [],
      barWidth: 14,
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: '#22d3ee' },
            { offset: 1, color: '#818cf8' }
          ]
        },
        borderRadius: [0, 10, 10, 0]
      },
      label: {
        show: true,
        position: 'right',
        color: '#e2e8f0'
      }
    }
  ]
})

const scatterChartOption = ref({
  title: {
    text: 'Model Performance Comparison',
    subtext: '',
    left: 'center',
    textStyle: {
      color: '#f8fafc',
      fontSize: 18,
      fontWeight: 700
    },
    subtextStyle: {
      color: 'rgba(226, 232, 240, 0.72)',
      fontSize: 12
    }
  },
  tooltip: {
    trigger: 'item',
    formatter: (params) => {
      const modelName = params?.data?.modelName
      const point = params?.data?.value
      if (!modelName || !Array.isArray(point)) {
        return ''
      }
      const paretoTag = params?.data?.isParetoOptimal ? '<br/><strong>Pareto-optimal</strong>' : ''
      return `${modelName}<br/>${getMetricName(scatterXMetric.value)}: ${formatMetricValue(point[0], scatterXMetric.value, { alreadyDisplay: true })}<br/>${getMetricName(scatterYMetric.value)}: ${formatMetricValue(point[1], scatterYMetric.value, { alreadyDisplay: true })}${paretoTag}`
    }
  },
  grid: {
    left: 30,
    right: 24,
    top: 70,
    bottom: 42,
    containLabel: true
  },
  xAxis: {
    type: 'value',
    name: 'Power Consumption',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  yAxis: {
    type: 'value',
    name: 'Latency',
    scale: true,
    axisLabel: { color: 'rgba(226, 232, 240, 0.72)' },
    nameTextStyle: { color: 'rgba(226, 232, 240, 0.72)' },
    splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.12)' } }
  },
  series: [
    {
      name: 'Model Performance',
      type: 'scatter',
      data: [],
      symbolSize: 18,
      itemStyle: {
        borderColor: 'rgba(248, 250, 252, 0.85)',
        borderWidth: 1,
        shadowBlur: 16
      },
      label: {
        show: true,
        formatter: (params) => {
          return params.data.modelName
        },
        position: 'top',
        color: '#cbd5e1'
      },
      labelLayout: {
        hideOverlap: false,
        moveOverlap: 'shiftY'
      }
    }
  ]
})

const ladderSummary = computed(() => {
  if (!ladderRecords.value.length) {
    return {
      topModel: '--',
      topValue: '--',
      average: '--'
    }
  }

  const sorted = [...ladderRecords.value].sort((a, b) => {
    if (isLowerBetterMetric(ladderMetric.value)) {
      return a.value - b.value
    }
    return b.value - a.value
  })
  const avg = sorted.reduce((sum, item) => sum + item.value, 0) / sorted.length

  return {
    topModel: sorted[0].model_name,
    topValue: Number(sorted[0].value).toFixed(2),
    average: Number(avg).toFixed(2)
  }
})

const buildModelInfo = (name) => {
  const dynamicMeta = modelMetaByName.value[name] || {}
  const staticMeta = MODEL_META_INFO[name] || {
    description: 'Add a detailed description for this model in MODEL_META_INFO.',
    source: 'TBD',
    modelSize: 'TBD'
  }

  const meta = {
    ...staticMeta,
    ...dynamicMeta
  }

  return {
    ...meta,
    metrics: metricsByModel.value[name] || {}
  }
}

const getCategoryRoleCount = (categoryKey, role) => getMetricDefsForCategory(categoryKey, role).length

const normalizeCategoryMetrics = (metrics = []) => {
  return metrics.map((metric) => {
    const roles = Array.isArray(metric.chart_roles) ? metric.chart_roles : []
    const uniqueRoles = [...new Set(roles.map((role) => String(role || '').trim().toLowerCase()).filter(Boolean))]
    return {
      key: String(metric.key || '').trim(),
      label: String(metric.label || '').trim(),
      unit: String(metric.unit || '').trim(),
      direction: String(metric.direction || 'higher').trim().toLowerCase() === 'lower' ? 'lower' : 'higher',
      chart_roles: uniqueRoles,
      definition: String(metric.definition || '').trim()
    }
  })
}

const openCreateCategoryDialog = () => {
  editingCategoryKey.value = ''
  categoryForm.value = createDefaultCategoryForm()
  showCategoryDialog.value = true
}

const openEditCategoryDialog = (category) => {
  if (!category) {
    return
  }
  editingCategoryKey.value = category.key
  categoryForm.value = {
    key: category.key || '',
    label: category.label || category.key || '',
    description: category.description || '',
    implementation_notes: category.implementation_notes || '',
    metrics: normalizeCategoryMetrics(category.metrics || []).length
      ? normalizeCategoryMetrics(category.metrics || [])
      : [createEmptyCategoryMetric()]
  }
  showCategoryDialog.value = true
}

const addCategoryMetricRow = () => {
  categoryForm.value.metrics.push(createEmptyCategoryMetric())
}

const removeCategoryMetricRow = (index) => {
  if ((categoryForm.value.metrics || []).length <= 1) {
    ElMessage.warning('At least one parameter is required')
    return
  }
  categoryForm.value.metrics.splice(index, 1)
}

const reloadSchemaDrivenView = async (preferredCategory = '') => {
  const ready = await loadKPISchema()
  if (!ready) {
    return
  }

  if (preferredCategory && MODEL_CATEGORY_KEYS.value.includes(preferredCategory)) {
    modelCategory.value = preferredCategory
    modelForm.value.model_category = preferredCategory
    syncMetricSelectionsForCategory()
  }

  categoryKeyword.value = ''
  const refreshTasks = [loadMetricDetails(), loadLadderData(), loadModelList()]
  if (showScatterChart.value) {
    refreshTasks.push(loadScatterData())
  }
  await Promise.all(refreshTasks)
}

const saveCategoryDialog = async () => {
  const categoryKey = String(categoryForm.value.key || '').trim()
  if (!categoryKey) {
    ElMessage.warning('Model type key is required')
    return
  }

  const metrics = normalizeCategoryMetrics(categoryForm.value.metrics || [])
  if (!metrics.length) {
    ElMessage.warning('At least one parameter is required')
    return
  }

  const invalidMetric = metrics.find((metric) => !metric.key)
  if (invalidMetric) {
    ElMessage.warning('Every parameter must have a metric key')
    return
  }

  const duplicateMetricKeys = new Set()
  const seenMetricKeys = new Set()
  metrics.forEach((metric) => {
    const token = metric.key.toLowerCase()
    if (seenMetricKeys.has(token)) {
      duplicateMetricKeys.add(metric.key)
    }
    seenMetricKeys.add(token)
  })
  if (duplicateMetricKeys.size) {
    ElMessage.warning(`Duplicate metric keys: ${[...duplicateMetricKeys].join(', ')}`)
    return
  }

  const payload = {
    key: categoryKey,
    label: String(categoryForm.value.label || categoryKey).trim(),
    description: String(categoryForm.value.description || '').trim(),
    implementation_notes: String(categoryForm.value.implementation_notes || '').trim(),
    metrics: metrics.map((metric) => ({
      ...metric,
      label: metric.label || metric.key,
      chart_roles: metric.chart_roles.length ? metric.chart_roles : ['table', 'form']
    }))
  }

  categoryDialogSaving.value = true
  try {
    if (isEditingCategory.value) {
      await updateKPISchemaCategory(editingCategoryKey.value, payload)
      ElMessage.success('Model type updated')
    } else {
      await createKPISchemaCategory(payload)
      ElMessage.success('Model type created')
    }
    showCategoryDialog.value = false
    editingCategoryKey.value = ''
    await reloadSchemaDrivenView(payload.key)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save model type')
  } finally {
    categoryDialogSaving.value = false
  }
}

const deleteCategoryDefinition = async (category) => {
  if (!category?.key) {
    return
  }

  try {
    await ElMessageBox.confirm(
      `Delete model type ${category.key}? This only removes the schema definition and will be blocked if KPI data still exists.`,
      'Delete Model Type',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    await deleteKPISchemaCategory(category.key)
    ElMessage.success('Model type deleted')
    await reloadSchemaDrivenView('')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete model type')
  }
}

const ensureActiveCategory = () => {
  const categories = schemaCategories.value.map((item) => item.key)
  if (!categories.length) {
    modelCategory.value = ''
    return false
  }

  if (!modelCategory.value || !categories.includes(modelCategory.value)) {
    modelCategory.value = categories[0]
  }

  if (!modelForm.value.model_category || !categories.includes(modelForm.value.model_category)) {
    modelForm.value.model_category = modelCategory.value
  }

  return true
}

const loadKPISchema = async () => {
  try {
    const payload = await getKPISchema()
    const categories = Array.isArray(payload?.categories) ? payload.categories : []
    kpiSchema.value = { categories }
  } catch (error) {
    kpiSchema.value = { categories: [] }
    ElMessage.error(error?.response?.data?.detail || 'Failed to load KPI schema')
  }

  const ready = ensureActiveCategory()
  if (ready) {
    syncMetricSelectionsForCategory()
  }
  return ready
}

const loadModelList = async () => {
  modelListLoading.value = true
  try {
    modelList.value = await getKPIModelLatestList({ model_category: modelCategory.value })
  } catch (error) {
    console.error('Failed to load model list', error)
    ElMessage.error('Failed to load model list')
  } finally {
    modelListLoading.value = false
  }
}

const isAccuracyMetric = (metricName) => String(metricName || '').toLowerCase().startsWith('accuracy')

const getBestLatencyMetricName = (metrics = {}) => {
  const latency = getMetricValueByKey(metrics, 'latency')
  if (latency !== null && latency !== undefined) {
    return 'latency'
  }
  return 'e2e_latency'
}

const getMetricMin = (metricName) => (isAccuracyMetric(metricName) ? 0 : -Infinity)

const getMetricMax = (metricName) => (isAccuracyMetric(metricName) ? 100 : Infinity)

const loadMetricDetails = async () => {
  try {
    const data = await getKPIMetrics({ model_category: modelCategory.value })
    kpiMetrics.value = data || []
    const names = Object.keys(metricsByModel.value)
    if (!selectedModelName.value || !names.includes(selectedModelName.value)) {
      selectedModelName.value = names[0] || ''
    }
    if (!compareModelA.value || !names.includes(compareModelA.value)) {
      compareModelA.value = names[0] || ''
    }
    if (!compareModelB.value || compareModelB.value === compareModelA.value || !names.includes(compareModelB.value)) {
      compareModelB.value = names.find(name => name !== compareModelA.value) || ''
    }
  } catch (error) {
    console.error('Failed to load model details', error)
  }
}

const loadLadderData = async () => {
  ladderLoading.value = true
  try {
    const data = await getLadderChartData(ladderMetric.value, modelCategory.value)
    ladderRecords.value = data.data || []
    const metricName = data.metric_name || ladderMetric.value

    const rawValues = ladderRecords.value
      .map(item => toDisplayMetricNumber(item.value, metricName))
      .filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(rawValues)
    
    const ladderRows = (data.data || []).slice().reverse()
    const modelNames = ladderRows.map(item => item.model_name)
    const values = ladderRows.map((item, index) => ({
      value: toDisplayMetricNumber(item.value, metricName),
      itemStyle: {
        color: getLadderBarColor(item.model_name, index),
        borderRadius: [0, 10, 10, 0]
      },
      label: {
        color: '#e2e8f0'
      }
    }))
    
    ladderChartOption.value = {
      ...ladderChartOption.value,
      title: {
        text: getLadderMetricTitle(metricName),
        left: 'center'
      },
      xAxis: {
        ...ladderChartOption.value.xAxis,
        name: getMetricName(metricName),
        min: xRange.min,
        max: xRange.max
      },
      yAxis: {
        ...ladderChartOption.value.yAxis,
        data: modelNames
      },
      series: [
        {
          ...ladderChartOption.value.series[0],
          data: values
        }
      ]
    }

    const names = ladderRows.map(item => item.model_name)
    if (names.length && !names.includes(selectedModelName.value)) {
      selectedModelName.value = names[0]
    }
  } catch (error) {
    console.error('Failed to load ladder chart data', error)
  } finally {
    ladderLoading.value = false
  }
}

const loadScatterData = async () => {
  scatterLoading.value = true
  try {
    const data = await getScatterChartData(scatterXMetric.value, scatterYMetric.value, modelCategory.value)
    scatterRecords.value = data.data || []
    const xMetric = data.x_metric || scatterXMetric.value
    const yMetric = data.y_metric || scatterYMetric.value

    const xValues = scatterRecords.value.map(item => toDisplayMetricNumber(item.x, xMetric)).filter(v => Number.isFinite(v))
    const yValues = scatterRecords.value.map(item => toDisplayMetricNumber(item.y, yMetric)).filter(v => Number.isFinite(v))
    const xRange = calcAxisRange(xValues)
    const yRange = calcAxisRange(yValues)
    
    const scatterData = data.data.map((item, index) => {
      const color = getModelColor(item.model_name, index)
      return {
        value: [toDisplayMetricNumber(item.x, xMetric), toDisplayMetricNumber(item.y, yMetric)],
        rawX: Number(item.x),
        rawY: Number(item.y),
        modelName: item.model_name,
        itemStyle: {
          color,
          shadowColor: color
        },
        label: {
          show: true,
          color
        }
      }
    }).filter((item) => Number.isFinite(item.value[0]) && Number.isFinite(item.value[1]))

    const paretoFront = buildParetoFront(scatterData, xMetric, yMetric)
    const paretoModelNames = new Set(paretoFront.map((item) => item.modelName))
    const displayScatterData = scatterData.map((item) => {
      const isParetoOptimal = paretoModelNames.has(item.modelName)
      return {
        ...item,
        isParetoOptimal,
        symbolSize: isParetoOptimal ? 24 : 18,
        itemStyle: {
          ...item.itemStyle,
          borderColor: isParetoOptimal ? '#facc15' : 'rgba(248, 250, 252, 0.85)',
          borderWidth: isParetoOptimal ? 3 : 1,
          shadowColor: isParetoOptimal ? '#facc15' : item.itemStyle.shadowColor,
          shadowBlur: isParetoOptimal ? 24 : 16
        },
        label: {
          ...item.label,
          fontWeight: isParetoOptimal ? 700 : 500
        }
      }
    })
    
    scatterChartOption.value = {
      ...scatterChartOption.value,
      title: {
        text: getScatterMetricTitle(xMetric, yMetric),
        subtext: paretoFront.length ? 'Pareto-optimal models are highlighted in gold' : '',
        left: 'center'
      },
      xAxis: {
        ...scatterChartOption.value.xAxis,
        name: getMetricName(xMetric),
        min: xRange.min,
        max: xRange.max
      },
      yAxis: {
        ...scatterChartOption.value.yAxis,
        name: getMetricName(yMetric),
        min: yRange.min,
        max: yRange.max
      },
      series: [
        {
          ...scatterChartOption.value.series[0],
          data: displayScatterData
        }
      ]
    }
  } catch (error) {
    console.error('Failed to load scatter chart data', error)
  } finally {
    scatterLoading.value = false
  }
}

const syncMetricSelectionsForCategory = () => {
  const ladderAvailable = LADDER_METRIC_OPTIONS.value.map((item) => item.value)
  const scatterAvailable = SCATTER_METRIC_OPTIONS.value.map((item) => item.value)

  if (!ladderAvailable.length) {
    ladderMetric.value = ''
  } else {
    const preferredLadder = ladderAvailable.includes('accuracy_total') ? 'accuracy_total' : ladderAvailable[0]
    if (!ladderAvailable.includes(ladderMetric.value)) {
      ladderMetric.value = preferredLadder
    }
  }

  if (!scatterAvailable.length) {
    scatterMetricSelection.value = []
    scatterXMetric.value = ''
    scatterYMetric.value = ''
    return
  }

  const selected = scatterMetricSelection.value.filter((metric) => scatterAvailable.includes(metric))
  for (const metric of scatterAvailable) {
    if (selected.length >= 2) break
    if (!selected.includes(metric)) {
      selected.push(metric)
    }
  }

  if (selected.length === 1) {
    selected.push(selected[0])
  }

  scatterMetricSelection.value = selected.slice(0, 2)
  scatterXMetric.value = scatterMetricSelection.value[0] || scatterAvailable[0]
  scatterYMetric.value = scatterMetricSelection.value[1] || scatterXMetric.value
}

const handleCategoryChange = () => {
  syncMetricSelectionsForCategory()
  loadMetricDetails()
  loadLadderData()
  if (showScatterChart.value) {
    loadScatterData()
  }
  loadModelList()
}

const selectModelCategory = (category) => {
  if (!category || category === modelCategory.value) return
  modelCategory.value = category
  handleCategoryChange()
}

const selectLadderMetric = (metric) => {
  if (!metric || metric === ladderMetric.value) return
  ladderMetric.value = metric
  loadLadderData()
}

const toggleScatterMetric = (metric) => {
  if (!showScatterChart.value) {
    return
  }

  if (scatterMetricSelection.value.includes(metric)) {
    return
  }

  const selected = [...scatterMetricSelection.value]
  selected.push(metric)

  // Queue strategy: keep at most two metrics, and remove the oldest when a third is selected.
  while (selected.length > 2) {
    selected.shift()
  }

  scatterMetricSelection.value = selected
  scatterXMetric.value = selected[0]
  scatterYMetric.value = selected[1]
  loadScatterData()
}

const resolveClickedModelName = (params) => {
  return params?.data?.modelName || params?.name || ''
}

const handleChartSingleClick = (params) => {
  const clickedName = resolveClickedModelName(params)
  if (!clickedName) return
  selectedModelName.value = clickedName
  const info = buildModelInfo(clickedName)
  ElMessage.closeAll()
  ElMessage({
    type: 'info',
    duration: 2400,
    showClose: true,
    message: `${clickedName}: ${info.description || 'No description'}`
  })
}

const goModelDetail = (modelName) => {
  if (!modelName) return
  router.push({ path: `/kpi/models/${encodeURIComponent(modelName)}`, query: { category: modelCategory.value } })
}

const handleChartDoubleClick = (params) => {
  const clickedName = resolveClickedModelName(params)
  if (!clickedName) return
  goModelDetail(clickedName)
}

const openCompareDialog = () => {
  const names = availableModelNames.value
  compareModelA.value = selectedModelName.value || names[0] || ''
  compareModelB.value = names.find(name => name !== compareModelA.value) || ''
  showCompareDialog.value = true
}

const openCreateModelDialog = () => {
  if (!canManageKPI.value) {
    ElMessage.warning('Only manager users can modify KPI models')
    return
  }
  editingModelName.value = ''
  modelForm.value = createDefaultModelForm(modelCategory.value)
  showModelDialog.value = true
}

const openUpdatePickerDialog = () => {
  if (!canManageKPI.value) {
    ElMessage.warning('Only manager users can modify KPI models')
    return
  }
  if (!modelList.value.length) {
    ElMessage.warning('No existing model available for update')
    return
  }
  selectedUpdateModelName.value = modelList.value[0]?.model_name || ''
  showUpdatePickerDialog.value = true
}

const confirmUpdateModelSelection = () => {
  const target = modelList.value.find((row) => row.model_name === selectedUpdateModelName.value)
  if (!target) {
    ElMessage.warning('Please select an existing model')
    return
  }
  showUpdatePickerDialog.value = false
  openEditModelDialog(target)
}

const deleteModelRow = async (row) => {
  if (!canManageKPI.value) {
    ElMessage.warning('Only manager users can modify KPI models')
    return
  }
  const targetName = row?.model_name
  if (!targetName) {
    return
  }

  try {
    await ElMessageBox.confirm(
      `Delete all KPI runs for model ${targetName} in category ${modelCategory.value}?`,
      'Delete Model',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    await deleteKPIModel(targetName, { model_category: modelCategory.value })
    ElMessage.success('Model deleted')

    const refreshTasks = [loadMetricDetails(), loadLadderData(), loadModelList()]
    if (showScatterChart.value) {
      refreshTasks.push(loadScatterData())
    }
    await Promise.all(refreshTasks)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to delete model')
  }
}

const openEditModelDialog = (row) => {
  if (!canManageKPI.value) {
    ElMessage.warning('Only manager users can modify KPI models')
    return
  }
  const targetCategory = row.model_category || modelCategory.value
  const metricDefs = getMetricDefsForCategory(targetCategory)
  const dynamicMetrics = {}
  metricDefs.forEach((metric) => {
    dynamicMetrics[metric.value] = toMetricNumber(getMetricValueByKey(row.metrics, metric.value))
  })

  editingModelName.value = row.model_name || ''
  modelForm.value = {
    model_category: targetCategory,
    model_name: row.model_name || '',
    source: row.source || '',
    model_size: row.model_size || '',
    description: row.description || '',
    test_date: row.test_date ? formatDateTimeForEdit(row.test_date) : '',
    test_platform: row.test_platform || '',
    test_version: row.test_version || '',
    test_condition: row.test_condition || '',
    metrics: dynamicMetrics
  }
  showModelDialog.value = true
}

const saveModelDialog = async () => {
  if (!canManageKPI.value) {
    ElMessage.warning('Only manager users can modify KPI models')
    return
  }
  if (!modelForm.value.model_name?.trim()) {
    ElMessage.warning('Model name is required')
    return
  }

  const metrics = {}
  MODEL_FORM_METRICS.value.forEach((metric) => {
    const raw = modelForm.value.metrics?.[metric.value]
    if (raw === undefined || raw === null || raw === '') return
    const numeric = Number(raw)
    if (Number.isFinite(numeric)) {
      metrics[metric.value] = numeric
    }
  })

  if (!Object.keys(metrics).length) {
    ElMessage.warning('At least one metric value is required')
    return
  }

  const outOfRangeAccuracyMetric = Object.keys(metrics).find(
    (metricName) => isAccuracyMetric(metricName) && (metrics[metricName] < 0 || metrics[metricName] > 100)
  )
  if (outOfRangeAccuracyMetric) {
    ElMessage.warning('Accuracy values must be between 0 and 100')
    return
  }

  const payload = {
    model_category: modelForm.value.model_category || modelCategory.value,
    model_name: modelForm.value.model_name.trim(),
    source: modelForm.value.source || '',
    model_size: modelForm.value.model_size || '',
    description: modelForm.value.description || '',
    test_date: modelForm.value.test_date || null,
    test_platform: modelForm.value.test_platform || '',
    test_version: modelForm.value.test_version || '',
    test_condition: modelForm.value.test_condition || '',
    metrics
  }

  modelDialogSaving.value = true
  try {
    if (isEditingModel.value) {
      await updateKPILatestModel(editingModelName.value, payload)
      ElMessage.success('Model updated')
    } else {
      await createKPIModel(payload)
      ElMessage.success('Model created')
    }
    showModelDialog.value = false
    editingModelName.value = ''
    selectedModelName.value = payload.model_name
    const refreshTasks = [loadMetricDetails(), loadLadderData(), loadModelList()]
    if (showScatterChart.value) {
      refreshTasks.push(loadScatterData())
    }
    await Promise.all(refreshTasks)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'Failed to save model')
  } finally {
    modelDialogSaving.value = false
  }
}

const formatMetricValue = (value, metricName = '', options = {}) => {
  if (value === undefined || value === null || value === '') {
    return '--'
  }
  const alreadyDisplay = options?.alreadyDisplay === true
  const numeric = Number(value)
  const hasNumeric = Number.isFinite(numeric)
  const displayValue = hasNumeric ? numeric : numeric
  const base = hasNumeric ? displayValue.toFixed(2) : String(value)
  const unit = METRIC_UNITS.value[metricName] || ''
  if (!unit) {
    return base
  }
  if (unit === '%') {
    return `${base}${unit}`
  }
  return `${base} ${unit}`
}

const toMetricNumber = (value) => {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : 0
}

const formatDateTime = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  return d.toLocaleString('en-US')
}

const formatDateTimeForEdit = (value) => {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`
}

const getMetricName = (metric) => {
  const label = METRIC_LABEL_MAP.value[metric] || metric
  const unit = METRIC_UNITS.value[metric]
  if (!unit) {
    return label
  }
  return `${label} (${unit})`
}

onMounted(async () => {
  const ready = await loadKPISchema()
  if (!ready) {
    return
  }

  loadMetricDetails()
  loadLadderData()
  if (showScatterChart.value) {
    loadScatterData()
  }
  loadModelList()
})
</script>

<style scoped>
.kpi-container {
  width: 100%;
}

.chart {
  width: 100%;
}

.metric-card__value--small {
  font-size: 24px;
  line-height: 1.2;
}

.model-info-card {
  padding-bottom: 24px;
}

.model-info-card__top {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.model-info-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.model-info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(255, 255, 255, 0.03);
}

.model-info-item--full {
  grid-column: 1 / -1;
}

.model-info-item__label {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.model-info-item__value {
  color: #f8fafc;
  font-size: 14px;
  font-weight: 600;
}

.model-info-item__value--multiline {
  line-height: 1.7;
  font-weight: 500;
}

.compare-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.model-dialog-form :deep(.el-form-item__label) {
  white-space: nowrap;
}

.model-link-btn {
  appearance: none;
  border: none;
  background: transparent;
  display: inline-block;
  width: 100%;
  margin: 0;
  padding: 0;
  color: #7dd3fc;
  cursor: pointer;
  font-weight: 700;
  text-align: center;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.model-link-btn:hover {
  color: #bae6fd;
}

.model-link-btn:focus-visible {
  outline: 2px solid rgba(125, 211, 252, 0.75);
  outline-offset: 2px;
  border-radius: 4px;
}

.category-focus-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-focus {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.category-focus__eyebrow {
  color: #5eead4;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.category-focus__title {
  margin: 8px 0 0;
  font-size: 22px;
}

.category-focus__desc {
  margin: 8px 0 0;
  color: rgba(226, 232, 240, 0.74);
  font-size: 14px;
}

.category-select {
  width: 320px;
}

.category-explorer {
  display: grid;
  grid-template-columns: minmax(240px, 300px) minmax(0, 1fr);
  gap: 16px;
}

.category-explorer__sidebar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.category-explorer__toolbar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-explorer__summary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-explorer__count {
  color: #f8fafc;
  font-size: 13px;
  font-weight: 700;
}

.category-explorer__hint {
  color: rgba(148, 163, 184, 0.78);
  font-size: 12px;
}

.category-search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.18);
}

.category-nav-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 380px;
  overflow-y: auto;
  padding-right: 4px;
  text-align: center;
}

.category-nav-item {
  align-items: center;
  appearance: none;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.03);
  color: #f8fafc;
  border-radius: 14px;
  padding: 12px 14px;
  cursor: pointer;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: all 0.2s ease;
}

.category-nav-item:hover {
  border-color: rgba(96, 165, 250, 0.32);
  background: rgba(96, 165, 250, 0.09);
  transform: translateY(-1px);
}

.category-nav-item.is-active {
  border-color: rgba(94, 234, 212, 0.36);
  background: rgba(94, 234, 212, 0.08);
}

.category-nav-item:focus-visible {
  outline: 2px solid rgba(94, 234, 212, 0.8);
  outline-offset: 2px;
}

.category-nav-item__title {
  font-size: 16px;
  font-weight: 700;
}

.category-empty-state {
  padding: 16px;
  border-radius: 14px;
  border: 1px dashed rgba(148, 163, 184, 0.22);
  color: rgba(226, 232, 240, 0.72);
  font-size: 13px;
}

.category-detail-card {
  padding: 18px;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background:
    radial-gradient(circle at top right, rgba(34, 211, 238, 0.16), transparent 34%),
    rgba(255, 255, 255, 0.03);
  min-height: 100%;
}

.category-detail-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.category-detail-card__header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 10px;
}

.category-schema-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.category-detail-card__eyebrow {
  color: #5eead4;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.category-detail-card__title {
  margin: 8px 0 0;
  color: #f8fafc;
  font-size: 24px;
}

.category-detail-card__desc {
  margin: 14px 0 0;
  color: rgba(226, 232, 240, 0.8);
  font-size: 14px;
  line-height: 1.7;
}

.category-detail-section {
  margin-top: 16px;
}

.category-detail-section__title {
  color: #f8fafc;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.category-detail-section__body {
  margin: 8px 0 0;
  color: rgba(226, 232, 240, 0.8);
  font-size: 14px;
  line-height: 1.7;
}

.category-detail-card__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 16px;
}

.category-detail-stat {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.28);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.category-detail-stat__label {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.category-detail-stat strong {
  color: #f8fafc;
  font-size: 14px;
}

.category-parameter-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.category-parameter-item {
  padding: 14px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.category-parameter-item__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.category-parameter-item__title {
  color: #f8fafc;
  font-size: 15px;
  font-weight: 700;
}

.category-parameter-item__meta {
  margin-top: 4px;
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.category-role-tag-group {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.category-parameter-item__desc {
  margin: 10px 0 0;
  color: rgba(226, 232, 240, 0.8);
  font-size: 13px;
  line-height: 1.65;
}

.category-editor-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin: 10px 0 14px;
}

.category-editor-head__title {
  margin: 0;
  color: #f8fafc;
  font-size: 16px;
}

.category-editor-head__desc {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.82);
  font-size: 13px;
}

.category-editor-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.category-editor-item {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.03);
}

.category-editor-item__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
}

.metric-tag-group {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.metric-tag {
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(226, 232, 240, 0.86);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}

.metric-tag:hover {
  border-color: rgba(96, 165, 250, 0.34);
  background: rgba(96, 165, 250, 0.12);
  color: #ffffff;
}

.metric-tag.is-active {
  border-color: rgba(94, 234, 212, 0.48);
  background: rgba(94, 234, 212, 0.16);
  color: #5eead4;
}

.metric-tag:focus-visible {
  outline: 2px solid rgba(94, 234, 212, 0.9);
  outline-offset: 2px;
}

.scatter-selector-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.selector-hint {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

@media (max-width: 768px) {
  .category-explorer {
    grid-template-columns: 1fr;
  }

  .category-detail-card__header {
    flex-direction: column;
  }

  .category-detail-card__header-actions {
    width: 100%;
    align-items: flex-start;
  }

  .category-schema-actions {
    justify-content: flex-start;
  }

  .category-nav-list {
    max-height: 240px;
  }

  .category-detail-card__stats {
    grid-template-columns: 1fr;
  }

  .category-parameter-list {
    grid-template-columns: 1fr;
  }

  .category-editor-head {
    flex-direction: column;
  }

  .scatter-selector-wrap {
    align-items: flex-start;
  }

  .model-info-card__top {
    flex-direction: column;
  }
}
</style>
