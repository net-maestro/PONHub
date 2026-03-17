<template>
  <div class="pon-card">

    <!-- TITLE -->
    <div class="card-header">
      <div class="d-flex align-items-center">
        <i class="bi bi-router fs-5 me-2 text-cyan"></i>
        <div>
          <h4 class="mb-0 fw-bold">Рекомендації PON</h4>
          <div class="subtitle">
            Орієнтовні значення для планування та експлуатації PON-мереж
          </div>
        </div>
      </div>
    </div>

    <!-- ONU Density - Compact Table -->
    <div class="card-section">
      <div class="section-header">
        <i class="bi bi-hdd-network me-2 text-cyan"></i>
        <span class="fw-semibold">Щільність ONU на порт</span>
      </div>
      <div class="section-content">
        <div class="density-table">
          <div v-for="item in density" :key="item.tech" class="density-row">
            <span class="tech-name">{{ item.tech }}</span>
            <span class="tech-value mono">{{ item.value }}</span>
            <span class="tech-desc text-muted">{{ item.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Capacity -->
    <div class="card-section">
      <div class="section-header">
        <i class="bi bi-arrow-left-right me-2 text-cyan"></i>
        <span class="fw-semibold">Пропускна здатність</span>
      </div>
      <div class="section-content">
        <div v-for="item in capacity" :key="item.tech" class="compact-row">
          <div>
            <strong>{{ item.tech }}</strong>
            <a :href="item.link" target="_blank" class="std-link small">
              {{ item.standard }}
            </a>
          </div>
          <span class="mono">{{ item.speed }}</span>
        </div>
      </div>
    </div>

    <!-- RX Power -->
    <div class="card-section">
      <div class="section-header">
        <i class="bi bi-wifi me-2 text-cyan"></i>
        <span class="fw-semibold">RX Power (ONU)</span>
      </div>
      <div class="section-content">
        <div v-for="zone in rxZones" :key="zone.range" class="rx-compact" :class="zone.class">
          <span class="mono">{{ zone.range }}</span>
          <span class="rx-label">{{ zone.label }}</span>
        </div>
        <div class="hint-compact">
          <i class="bi bi-check-circle me-1"></i>
          Оптимально: <strong>−18…−22 dBm</strong>
        </div>
      </div>
    </div>

    <!-- Port Load -->
    <div class="card-section">
      <div class="section-header">
        <i class="bi bi-speedometer2 me-2 text-cyan"></i>
        <span class="fw-semibold">Завантаження порту</span>
      </div>
      <div class="section-content">
        <div class="load-pills">
          <span class="pill-compact green">&lt;60%</span>
          <span class="pill-compact yellow">60–75%</span>
          <span class="pill-compact orange">75–85%</span>
          <span class="pill-compact red">&gt;85%</span>
        </div>
        <div class="hint-compact">
          <i class="bi bi-exclamation-triangle me-1"></i>
          Розвантаження при <strong>≥75%</strong>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>

const density = [
  { tech: 'GPON', value: '40–56', desc: 'Тарифи до 300 Мбіт/с' },
  { tech: 'XG-PON', value: '48–56', desc: '500–1000 Мбіт/с' },
  { tech: 'XGS-PON', value: '56–64', desc: '1 Гбіт симетрія' },
  { tech: 'Combo', value: '32–40', desc: 'Змішане навантаження' }
]

const capacity = [
  {
    tech: 'GPON',
    speed: '2.5↓/1.25↑ Гбіт/с',
    standard: 'G.984',
    link: 'https://www.itu.int/rec/T-REC-G.984'
  },
  {
    tech: 'XG-PON',
    speed: '10↓/2.5↑ Гбіт/с',
    standard: 'G.987',
    link: 'https://www.itu.int/rec/T-REC-G.987'
  },
  {
    tech: 'XGS-PON',
    speed: '10↓/10↑ Гбіт/с',
    standard: 'G.9807.1',
    link: 'https://www.itu.int/rec/T-REC-G.9807.1'
  }
]

const rxZones = [
  { range: '> -8', label: 'Перевантаження приймача ONU', class: 'red' },
  { range: '-8 … -15', label: 'Сильний сигнал (працює)', class: 'yellow' },
  { range: '-15 … -23', label: 'Оптимальний рівень сигналу', class: 'green' },
  { range: '-23 … -27', label: 'Добрий рівень сигналу', class: 'blue' },
  { range: '-27 … -30', label: 'Критичний рівень (контроль)', class: 'orange' },
  { range: '< -30', label: "Відсутність стабільного зв'язку", class: 'red' }
]

</script>

<style scoped>

/* ============================================
🔹 LEGACY FIX
============================================ */
.pon-card {
  all: initial;
  font-size: 0.9rem !important;
  line-height: 1.4 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  box-sizing: border-box;
  display: block;
}

.pon-card *,
.pon-card *::before,
.pon-card *::after {
  box-sizing: inherit;
  font-family: inherit;
}

/* ============================================
ОСНОВНИЙ КОНТЕЙНЕР
============================================ */
.pon-card {
  --bg-primary: #f8f9fa;
  --bg-secondary: #ffffff;
  --bg-card: #ffffff;
  --bg-hover: #f1f3f5;
  --border-color: #dee2e6;
  --text-primary: #212529;
  --text-secondary: #6c757d;
  --text-muted: #adb5bd;
  --accent-primary: #2A3F54;
  --accent-cyan: #00a8cc;
  --accent-green: #198754;
  --accent-red: #dc3545;
  --accent-yellow: #ffc107;
  
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  max-width: 700px;
  color: var(--text-primary);
}

/* ============================================
🔹 ЗАГОЛОВОК
============================================ */
.card-header {
  background: linear-gradient(135deg, var(--accent-primary) 0%, #1a2838 100%);
  border-radius: 6px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.85rem;
}

.card-header h4 {
  color: #ffffff !important;
  font-size: 1.1rem !important;
}

.subtitle {
  font-size: 0.85rem !important;
  color: rgba(255, 255, 255, 0.85) !important;
  margin-top: 0.15rem;
}

.text-cyan { color: #00d4ff !important; }
.text-primary { color: var(--accent-cyan) !important; }
.text-muted { color: var(--text-muted) !important; }

/* ============================================
🔹 СЕКЦІЇ
============================================ */
.card-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-bottom: 0.65rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 0.55rem 0.85rem;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.95rem;
}

.section-content {
  padding: 0.65rem 0.85rem;
}

/* ============================================
🔹 ЩІЛЬНІСТЬ ONU - TABLE
============================================ */
.density-table {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.density-row {
  display: grid;
  grid-template-columns: 90px 80px 1fr;
  gap: 0.5rem;
  align-items: center;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.density-row:last-child {
  border-bottom: none;
}

.tech-name {
  font-weight: 600;
  color: var(--text-primary);
}

.tech-value {
  background: var(--accent-primary);
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  text-align: center;
  font-size: 0.85rem;
}

.tech-desc {
  font-size: 0.85rem;
}

/* ============================================
🔹 COMPACT ROWS
============================================ */
.compact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.compact-row:last-child {
  border-bottom: none;
}

.std-link {
  margin-left: 0.4rem;
  text-decoration: none;
  color: var(--accent-cyan);
  font-size: 0.8rem;
}

.std-link:hover {
  text-decoration: underline;
}

.mono {
  font-family: 'Courier New', Consolas, monospace;
  font-weight: 600;
}

/* ============================================
🔹 RX POWER - COMPACT
============================================ */
.rx-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.35rem 0.65rem;
  border-radius: 4px;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
  border: 1px solid transparent;
}

.rx-label {
  color: var(--text-secondary);
}

.rx-compact.green {
  background: rgba(25, 135, 84, 0.1);
  border-color: var(--accent-green);
  color: #0f5132;
}

.rx-compact.blue {
  background: rgba(13, 202, 240, 0.1);
  border-color: #0dcaf0;
  color: #055160;
}

.rx-compact.yellow {
  background: rgba(255, 193, 7, 0.1);
  border-color: var(--accent-yellow);
  color: #997404;
}

.rx-compact.orange {
  background: rgba(253, 126, 20, 0.1);
  border-color: #fd7e14;
  color: #995404;
}

.rx-compact.red {
  background: rgba(220, 53, 69, 0.1);
  border-color: var(--accent-red);
  color: #842029;
}

/* ============================================
🔹 LOAD PILLS - COMPACT
============================================ */
.load-pills {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-bottom: 0.4rem;
}

.pill-compact {
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid;
}

.pill-compact.green {
  background: rgba(25, 135, 84, 0.15);
  color: #0f5132;
  border-color: var(--accent-green);
}

.pill-compact.yellow {
  background: rgba(255, 193, 7, 0.15);
  color: #997404;
  border-color: var(--accent-yellow);
}

.pill-compact.orange {
  background: rgba(253, 126, 20, 0.15);
  color: #995404;
  border-color: #fd7e14;
}

.pill-compact.red {
  background: rgba(220, 53, 69, 0.15);
  color: #842029;
  border-color: var(--accent-red);
}

/* ============================================
🔹 HINTS
============================================ */
.hint-compact {
  margin-top: 0.5rem;
  padding: 0.45rem 0.65rem;
  background: var(--bg-hover);
  border-left: 2px solid var(--accent-cyan);
  border-radius: 0 4px 4px 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.hint-compact i {
  color: var(--accent-cyan);
}

/* ============================================
🔹 HELPERS
============================================ */
.d-flex { display: flex; }
.align-items-center { align-items: center; }
.fw-bold { font-weight: 700 !important; }
.fw-semibold { font-weight: 600 !important; }
.mb-0 { margin-bottom: 0; }
.me-1 { margin-right: 0.25rem; }
.me-2 { margin-right: 0.4rem; }
.fs-5 { font-size: 1.1rem !important; }
.small { font-size: 0.8rem !important; }

/* ============================================
🔹 RESPONSIVE
============================================ */
@media (max-width: 768px) {
  .pon-card {
    padding: 0.75rem;
    max-width: 100%;
  }
  
  .density-row {
    grid-template-columns: 70px 70px 1fr;
    font-size: 0.85rem;
  }
  
  .card-header h4 {
    font-size: 1rem !important;
  }
  
  .load-pills {
    gap: 0.3rem;
  }
  
  .pill-compact {
    padding: 0.3rem 0.5rem;
    font-size: 0.8rem;
  }
}

</style>