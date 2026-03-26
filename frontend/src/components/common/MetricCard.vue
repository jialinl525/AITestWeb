<template>
  <article class="metric-card" :class="[`accent-${accent}`, `size-${size}`]">
    <div class="metric-card__label">{{ label }}</div>
    <div class="metric-card__value">{{ value }}</div>
    <div v-if="meta" class="metric-card__meta">{{ meta }}</div>
  </article>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '' },
  meta: { type: String, default: '' },
  /** Color accent: white | yellow | green | red | cyan | blue */
  accent: { type: String, default: 'white' },
  /** Card size: sm | md | lg */
  size: { type: String, default: 'md' }
})
</script>

<style scoped>
/* ── Base card ─────────────────────────────────────────────────────────────── */
.metric-card {
  padding: 12px 10px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(148, 163, 184, 0.14);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 0;
  transition: border-color 0.2s ease;
}

/* ── Size variants ─────────────────────────────────────────────────────────── */
.metric-card.size-sm { min-height: 80px; padding: 8px; }
.metric-card.size-md { min-height: 112px; }
.metric-card.size-lg { min-height: 140px; padding: 16px 12px; }

/* ── Label ─────────────────────────────────────────────────────────────────── */
.metric-card__label {
  font-weight: 800;
  margin-bottom: 10px;
}
.size-sm .metric-card__label { font-size: 12px; }
.size-md .metric-card__label { font-size: 13px; }
.size-lg .metric-card__label { font-size: 14px; }

/* ── Value ─────────────────────────────────────────────────────────────────── */
.metric-card__value {
  font-weight: 800;
  line-height: 1.2;
}
.size-sm .metric-card__value { font-size: 18px; }
.size-md .metric-card__value { font-size: 22px; }
.size-lg .metric-card__value { font-size: 28px; }

/* ── Meta ──────────────────────────────────────────────────────────────────── */
.metric-card__meta {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.82);
  margin-top: 10px;
  line-height: 1.4;
}

/* ── Accent: white ─────────────────────────────────────────────────────────── */
.accent-white { border-color: rgba(248, 250, 252, 0.14); }
.accent-white .metric-card__label { color: #f8fafc; }
.accent-white .metric-card__value { color: #f8fafc; }

/* ── Accent: yellow ────────────────────────────────────────────────────────── */
.accent-yellow { border-color: rgba(251, 191, 36, 0.22); }
.accent-yellow .metric-card__label { color: #fbbf24; }
.accent-yellow .metric-card__value { color: #fbbf24; }

/* ── Accent: green ─────────────────────────────────────────────────────────── */
.accent-green { border-color: rgba(94, 234, 212, 0.22); }
.accent-green .metric-card__label { color: #5eead4; }
.accent-green .metric-card__value { color: #5eead4; }

/* ── Accent: red ───────────────────────────────────────────────────────────── */
.accent-red { border-color: rgba(248, 113, 113, 0.22); }
.accent-red .metric-card__label { color: #f87171; }
.accent-red .metric-card__value { color: #f87171; }

/* ── Accent: cyan ──────────────────────────────────────────────────────────── */
.accent-cyan { border-color: rgba(34, 211, 238, 0.22); }
.accent-cyan .metric-card__label { color: #22d3ee; }
.accent-cyan .metric-card__value { color: #22d3ee; }

/* ── Accent: blue ──────────────────────────────────────────────────────────── */
.accent-blue { border-color: rgba(96, 165, 250, 0.22); }
.accent-blue .metric-card__label { color: #60a5fa; }
.accent-blue .metric-card__value { color: #60a5fa; }
</style>
