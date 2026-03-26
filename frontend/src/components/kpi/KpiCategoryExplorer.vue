<template>
  <el-card class="section-card category-focus-card">
    <div class="category-focus">
      <div class="category-focus__left">
        <div class="category-focus__eyebrow">{{ LT.category.eyebrow }}</div>
        <h3 class="category-focus__title">{{ LT.category.title }}</h3>
        <p class="category-focus__desc">
          {{ DT.categoryCurrentPrefix }} <strong>{{ modelCategory }}</strong>. {{ DT.categoryCurrentSuffix }}
        </p>
      </div>
    </div>

    <div class="category-explorer">
      <aside class="category-explorer__sidebar">
        <div class="category-explorer__toolbar">
          <div class="category-explorer__summary">
            <span class="category-explorer__count">{{ filteredCategories.length }} / {{ totalCount }} model types</span>
            <span class="category-explorer__hint">Compact navigator for future expansion</span>
          </div>
          <el-input v-model="keyword" clearable placeholder="Search model type" class="category-search-input" />
        </div>
        <div v-if="filteredCategories.length" class="category-nav-list">
          <button
            v-for="category in filteredCategories"
            :key="category.key"
            type="button"
            class="category-nav-item"
            :class="{ 'is-active': category.key === modelCategory }"
            @click="$emit('select-category', category.key)"
          >
            <span class="category-nav-item__title">{{ category.key }}</span>
          </button>
        </div>
        <div v-else class="category-empty-state">No model type matches "{{ keyword }}"</div>
      </aside>

      <section v-if="activeMeta" class="category-detail-card">
        <div class="category-detail-card__header">
          <div>
            <div class="category-detail-card__eyebrow">Current model type</div>
            <h4 class="category-detail-card__title">{{ activeMeta.label || activeMeta.key }}</h4>
          </div>
          <div class="category-detail-card__header-actions">
            <el-tag size="small" type="success">{{ LT.category.current }}</el-tag>
            <div v-if="canManage" class="category-schema-actions">
              <el-button size="small" type="primary" @click="$emit('create')">New Type</el-button>
              <el-button size="small" @click="$emit('edit', activeMeta)">Edit</el-button>
              <el-button size="small" type="danger" plain @click="$emit('delete', activeMeta)">Delete</el-button>
            </div>
          </div>
        </div>
        <p class="category-detail-card__desc">{{ activeMeta.description || categoryInfo[activeMeta.key] }}</p>
        <div class="category-detail-section">
          <div class="category-detail-section__title">Typical implementation</div>
          <p class="category-detail-section__body">
            {{ activeMeta.implementation_notes || 'No implementation notes have been defined yet.' }}
          </p>
        </div>
        <div class="category-detail-section">
          <div class="category-detail-section__title">Parameter definitions</div>
          <div class="category-parameter-list">
            <article
              v-for="metric in metricDefs"
              :key="`${activeMeta.key}-${metric.value}`"
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
              <p class="category-parameter-item__desc">
                {{ metric.definition || 'No parameter definition has been defined yet.' }}
              </p>
            </article>
          </div>
        </div>
      </section>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { LabelText } from '../../texts/LabelText'
import { DescriptionText } from '../../texts/DescriptionText'

const LT = LabelText.kpi
const DT = DescriptionText.kpi

const props = defineProps({
  modelCategory: { type: String, default: '' },
  schemaCategories: { type: Array, default: () => [] },
  categoryInfo: { type: Object, default: () => ({}) },
  metricDefs: { type: Array, default: () => [] },
  canManage: { type: Boolean, default: false },
  getMetricPreferenceText: { type: Function, required: true }
})

defineEmits(['select-category', 'create', 'edit', 'delete'])

const keyword = ref('')

const totalCount = computed(() => props.schemaCategories.length)

const filteredCategories = computed(() => {
  const kw = String(keyword.value || '').trim().toLowerCase()
  if (!kw) return props.schemaCategories
  const matched = props.schemaCategories.filter(c =>
    [c.key, c.label, c.description].filter(Boolean).join(' ').toLowerCase().includes(kw)
  )
  const current = props.schemaCategories.find(c => c.key === props.modelCategory)
  if (current && !matched.some(c => c.key === current.key)) return [current, ...matched]
  return matched
})

const activeMeta = computed(() =>
  props.schemaCategories.find(c => c.key === props.modelCategory) || null
)
</script>

<style scoped>
.category-focus-card :deep(.el-card__body) { display: flex; flex-direction: column; gap: 16px; }
.category-focus { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.category-focus__eyebrow { color: #5eead4; font-size: 12px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
.category-focus__title { margin: 8px 0 0; font-size: 22px; }
.category-focus__desc { margin: 8px 0 0; color: rgba(226, 232, 240, 0.74); font-size: 14px; }

.category-explorer { display: grid; grid-template-columns: minmax(240px, 300px) minmax(0, 1fr); gap: 16px; }
.category-explorer__sidebar { display: flex; flex-direction: column; gap: 12px; min-height: 0; }
.category-explorer__toolbar { display: flex; flex-direction: column; gap: 10px; }
.category-explorer__summary { display: flex; flex-direction: column; gap: 4px; }
.category-explorer__count { color: #f8fafc; font-size: 13px; font-weight: 700; }
.category-explorer__hint { color: rgba(148, 163, 184, 0.78); font-size: 12px; }
.category-search-input :deep(.el-input__wrapper) { background: rgba(255, 255, 255, 0.04); box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.18); }

.category-nav-list { display: flex; flex-direction: column; gap: 10px; max-height: 380px; overflow-y: auto; padding-right: 4px; }
.category-nav-item { appearance: none; border: 1px solid rgba(148, 163, 184, 0.14); background: rgba(255, 255, 255, 0.03); color: #f8fafc; border-radius: 14px; padding: 12px 14px; cursor: pointer; text-align: center; display: flex; flex-direction: column; gap: 4px; transition: all 0.2s ease; }
.category-nav-item:hover { border-color: rgba(96, 165, 250, 0.32); background: rgba(96, 165, 250, 0.09); transform: translateY(-1px); }
.category-nav-item.is-active { border-color: rgba(94, 234, 212, 0.36); background: rgba(94, 234, 212, 0.08); }
.category-nav-item:focus-visible { outline: 2px solid rgba(94, 234, 212, 0.8); outline-offset: 2px; }
.category-nav-item__title { font-size: 16px; font-weight: 700; }
.category-empty-state { padding: 16px; border-radius: 14px; border: 1px dashed rgba(148, 163, 184, 0.22); color: rgba(226, 232, 240, 0.72); font-size: 13px; }

.category-detail-card { padding: 18px; border-radius: 18px; border: 1px solid rgba(148, 163, 184, 0.14); background: radial-gradient(circle at top right, rgba(34, 211, 238, 0.16), transparent 34%), rgba(255, 255, 255, 0.03); min-height: 100%; }
.category-detail-card__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.category-detail-card__header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
.category-schema-actions { display: flex; align-items: center; justify-content: flex-end; gap: 8px; flex-wrap: wrap; }
.category-detail-card__eyebrow { color: #5eead4; font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.category-detail-card__title { margin: 8px 0 0; color: #f8fafc; font-size: 24px; }
.category-detail-card__desc { margin: 14px 0 0; color: rgba(226, 232, 240, 0.8); font-size: 14px; line-height: 1.7; }
.category-detail-section { margin-top: 16px; }
.category-detail-section__title { color: #f8fafc; font-size: 13px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
.category-detail-section__body { margin: 8px 0 0; color: rgba(226, 232, 240, 0.8); font-size: 14px; line-height: 1.7; }

.category-parameter-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin-top: 12px; }
.category-parameter-item { padding: 14px; border-radius: 16px; background: rgba(15, 23, 42, 0.3); border: 1px solid rgba(148, 163, 184, 0.18); }
.category-parameter-item__header { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.category-parameter-item__title { color: #f8fafc; font-size: 15px; font-weight: 700; }
.category-parameter-item__meta { margin-top: 4px; color: rgba(148, 163, 184, 0.82); font-size: 12px; }
.category-parameter-item__desc { margin: 10px 0 0; color: rgba(226, 232, 240, 0.8); font-size: 13px; line-height: 1.65; }

@media (max-width: 768px) {
  .category-explorer { grid-template-columns: 1fr; }
  .category-detail-card__header { flex-direction: column; }
  .category-detail-card__header-actions { width: 100%; align-items: flex-start; }
  .category-schema-actions { justify-content: flex-start; }
  .category-nav-list { max-height: 240px; }
  .category-parameter-list { grid-template-columns: 1fr; }
}
</style>
