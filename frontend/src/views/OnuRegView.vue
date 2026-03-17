<template>
  <div class="olt-container">
    <!-- 🔹 ВНУТРІШНІЙ SPINNER LOADER -->
    <div v-if="isLoading" class="spinner-overlay">
      <div class="spinner-container">
        <div class="spinner"></div>
        <div class="spinner-text">Завантаження...</div>
      </div>
    </div>

    <!-- 🔹 УНІВЕРСАЛЬНІ FLASH МЕСЕДЖІ -->
    <div class="flash-container">
      <transition-group name="flash-list" tag="div">
        <div
          v-for="(msg, index) in flashMessages"
          :key="`${msg.category}-${index}-${msg.text}`"
          :class="`flash-item alert alert-${msg.category}`"
          role="alert"
        >
          <div class="alert-content">
            <i :class="getIconClass(msg.category)" class="alert-icon"></i>
            <div class="alert-text">{{ msg.text }}</div>
            <button
              type="button"
              class="alert-close"
              @click="removeFlashMessage(index)"
              aria-label="Close"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- Header -->
    <div class="olt-header">
      <div class="header-top">
        <div class="d-flex align-items-center justify-content-between">
          <div class="d-flex align-items-center">
            <i class="bi bi-router fs-5 me-2 text-cyan"></i>
            <div>
              <h4 class="mb-0 fw-bold text-header">
                {{ selectedOlt?.deviceName || '...' }} - {{ selectedOlt?.deviceIp || '...' }}
              </h4>
            </div>
          </div>
          <!-- 🔹 OLT SELECTOR -->
          <div v-if="olts.length > 1" class="olt-selector">
            <label class="olt-selector-label">
              <i class="bi bi-stack me-1"></i>OLT:
            </label>
            <select
              v-model="activeOltId"
              class="olt-selector-select"
              @change="onOltChange"
            >
              <option
                v-for="olt in olts"
                :key="olt.oltId"
                :value="olt.oltId"
                :disabled="!olt.enabled"
              >
                {{ olt.deviceIp }} {{ !olt.enabled ? '🔴' : '🟢' }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <!-- 🔹 OLT TABS -->
      <div class="header-tabs">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
          type="button"
        >
          <i class="bi bi-plus-lg me-1"></i>Реєстрація
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'discovery' }"
          @click="activeTab = 'discovery'"
          type="button"
        >
          <i class="bi bi-search me-1"></i>Discovery
        </button>
        <!-- 🔹 НОВИЙ ТАБ ПРИВ'ЯЗКИ (з'являється після реєстрації) -->
        <button
          v-if="isOnuRegistered"
          class="tab-btn"
          :class="{ active: activeTab === 'binding' }"
          @click="activeTab = 'binding'"
          type="button"
        >
          <i class="bi bi-link-45deg me-1"></i>Прив'язка
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Registration Tab -->
      <div v-if="activeTab === 'register'" class="registration-grid">
        <!-- Left Panel - Form -->
        <div class="left-panel">
          <!-- PON Port -->
          <div class="card-section">
            <div
              class="section-header"
              @click="toggleSection('pon')"
              role="button"
              tabindex="0"
            >
              <div class="d-flex align-items-center">
                <i class="bi bi-grid-3x3-gap me-2 text-cyan"></i>
                <span class="fw-semibold">PON порт</span>
              </div>
              <i
                class="bi bi-chevron-down"
                :class="{ rotated: sections.pon }"
              ></i>
            </div>
            <div v-show="sections.pon" class="section-content">
              <div class="mb-3">
                <label class="form-label small text-muted">ONUID режим:</label>
                <div class="mode-selector">
                  <div
                    class="mode-option"
                    :class="{ active: onuIdMode === 'auto' }"
                    @click="onuIdMode = 'auto'"
                    role="radio"
                    :aria-checked="onuIdMode === 'auto'"
                    tabindex="0"
                  >
                    <div class="mode-radio"><div class="radio-dot"></div></div>
                    <div class="mode-info">
                      <div class="mode-title">Авто (next free)</div>
                      <div class="mode-desc">Автоматичний вибір</div>
                    </div>
                    <button
                      class="btn-auto"
                      @click.stop="fetchFreeOnuId"
                      type="button"
                      :disabled="!form.interface"
                    >
                      АВТО+ <i class="bi bi-chevron-down"></i>
                    </button>
                  </div>
                  <div
                    class="mode-option"
                    :class="{ active: onuIdMode === 'manual' }"
                    @click="onuIdMode = 'manual'"
                    role="radio"
                    :aria-checked="onuIdMode === 'manual'"
                    tabindex="0"
                  >
                    <div class="mode-radio"><div class="radio-dot"></div></div>
                    <div class="mode-info">
                      <div class="mode-title">Ручний</div>
                      <div class="mode-desc">Вкажіть номер вручну</div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row">
                <div class="col-7">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-hdd-network me-1"></i>Інтерфейс</label
                  >
                  <select v-model="form.interface" class="form-control-light">
                    <option value="" disabled>Оберіть порт</option>
                    <option
                      v-for="(name, key) in interfaces"
                      :key="key"
                      :value="name"
                    >
                      {{ name }}
                    </option>
                  </select>
                </div>
                <div class="col-5">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-hash me-1"></i>ONU ID</label
                  >
                  <input
                    v-model="form.onuId"
                    type="number"
                    class="form-control-light"
                    :disabled="onuIdMode === 'auto'"
                    placeholder="1-128"
                    min="1"
                    max="128"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- ONU Type -->
          <div class="card-section">
            <div
              class="section-header"
              @click="toggleSection('type')"
              role="button"
              tabindex="0"
            >
              <div class="d-flex align-items-center">
                <i class="bi bi-cpu me-2 text-cyan"></i>
                <span class="fw-semibold">Тип ONU</span>
              </div>
              <i
                class="bi bi-chevron-down"
                :class="{ rotated: sections.type }"
              ></i>
            </div>
            <div v-show="sections.type" class="section-content">
              <div class="onu-types-grid">
                <div
                  v-for="(typeData, key) in onuTypes"
                  :key="key"
                  class="onu-type-card"
                  :class="{ selected: form.onuType === key }"
                  @click="selectOnuType(key)"
                  role="radio"
                  :aria-checked="form.onuType === key"
                  tabindex="0"
                >
                  <div class="type-radio"><div class="radio-inner"></div></div>
                  <div class="type-name">{{ typeData.model }}</div>
                  <div class="type-specs">
                    {{ typeData.eth_ports }} LAN {{ typeData.has_wifi ? '+ WiFi' : '' }}
                  </div>
                  <div class="type-badge">{{ typeData.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Service -->
          <div class="card-section">
            <div
              class="section-header"
              @click="toggleSection('service')"
              role="button"
              tabindex="0"
            >
              <div class="d-flex align-items-center">
                <i class="bi bi-speedometer2 me-2 text-cyan"></i>
                <span class="fw-semibold">Сервіс</span>
              </div>
              <i
                class="bi bi-chevron-down"
                :class="{ rotated: sections.service }"
              ></i>
            </div>
            <div v-show="sections.service" class="section-content">
              <div class="row">
                <div class="col-5">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-speedometer me-1"></i>Швидкість</label
                  >
                  <select v-model="form.speed" class="form-control-light">
                    <option value="" disabled>Оберіть швидкість</option>
                    <option v-for="speed in speeds" :key="speed" :value="speed">
                      {{ speed }} Mbps
                    </option>
                  </select>
                </div>
                <div class="col-7">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-diagram-3 me-1"></i>Service-профіль</label
                  >
                  <select v-model="form.vlan" class="form-control-light" required>
                    <option value="" disabled>Оберіть VLAN</option>
                    <option
                      v-for="(displayName, profileKey) in lineProfilesDisplay"
                      :key="profileKey"
                      :value="`${profileKey}+++${lineProfilesRaw[profileKey]}`"
                      :class="{
                        'fw-bold text-primary': isRecommendedVlan(profileKey),
                      }"
                    >
                      {{ displayName }}
                      <span
                        v-if="isRecommendedVlan(profileKey)"
                        class="badge-recommended-option"
                      >рекомендовано</span>
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Billing -->
          <div class="card-section">
            <div
              class="section-header"
              @click="toggleSection('billing')"
              role="button"
              tabindex="0"
            >
              <div class="d-flex align-items-center">
                <i class="bi bi-person-badge me-2 text-cyan"></i>
                <span class="fw-semibold">Абонент</span>
              </div>
              <i
                class="bi bi-chevron-down"
                :class="{ rotated: sections.billing }"
              ></i>
            </div>
            <div v-show="sections.billing" class="section-content">
              <div class="mb-3">
                <label class="form-label small text-muted"
                  ><i class="bi bi-fingerprint me-1"></i>Серійний номер (SN)</label
                >
                <!-- 🔹 ПОЛЕ SN З КНОПКОЮ "ЗНАЙТИ ONU" В ОДИН РЯДОК -->
                <div class="sn-input-row">
                  <input
                    v-model="form.sn"
                    type="text"
                    class="form-control-light"
                    placeholder="ZTEGC690F05D"
                    @input="formatSnInput"
                    maxlength="20"
                  />
                  <button
                    class="btn-find-onu"
                    @click="openDiscoveryForSn"
                    type="button"
                    title="Знайти незареєстровані ONU"
                  >
                    <i class="bi bi-search"></i>
                    <span>Знайти ONU</span>
                  </button>
                </div>
                <div class="form-text small">
                  <i class="bi bi-info-circle me-1"></i>SN має містити щонайменше
                  8 символів
                </div>
              </div>
              <div>
                <label class="form-label small text-muted"
                  ><i class="bi bi-file-text me-1"></i>№ договору /
                  Коментар</label
                >
                <input
                  v-model="form.comment"
                  type="text"
                  class="form-control-light"
                  placeholder="1404"
                />
              </div>
            </div>
          </div>

          <!-- Status Bar -->
          <div class="status-bar">
            <div class="status-text">
              <span
                class="status-indicator"
                :class="isFormValid ? 'bg-success' : 'bg-warning'"
              ></span>
              <span class="status-label">STATUS:</span>
              <span :class="isFormValid ? 'text-success' : 'text-warning'">{{
                isFormValid ? 'Ready to provision' : 'Заповніть всі поля'
              }}</span>
            </div>
            <div class="status-actions">
              <button
                class="btn-status btn-preview"
                @click="previewConfig"
                :disabled="!isFormValid || isLoading"
                type="button"
              >
                <i class="bi bi-eye me-1"></i>Перегляд
              </button>
              <button
                class="btn-status btn-register"
                @click="registerONU"
                :disabled="!isFormValid || isLoading"
                type="button"
              >
                <i class="bi bi-check-lg me-1"></i>Зареєструвати
              </button>
              <button
                class="btn-status btn-cancel"
                @click="resetForm"
                type="button"
              >
                <i class="bi bi-x-lg me-1"></i>Скасувати
              </button>
            </div>
          </div>
        </div>

        <!-- Right Panel - CLI -->
        <div class="right-panel">
          <div class="cli-header">
            <div class="cli-tabs">
              <button class="cli-tab active" type="button">
                <i class="bi bi-file-earmark-code me-2"></i>
                Статус реєстрації
                <span v-if="form.comment"> договору №{{ form.comment }} </span>
              </button>
            </div>
          </div>
          <div class="cli-content">
            <div class="cli-section">
              <div class="steps-list">
                <div class="step-item" :class="{ active: currentStep >= 1 }">
                  <div class="step-number">1</div>
                  <div class="step-text">Вибір порту та ONU ID</div>
                </div>
                <div class="step-connector"></div>
                <div class="step-item" :class="{ active: currentStep >= 2 }">
                  <div class="step-number">2</div>
                  <div class="step-text">Налаштування VLAN</div>
                </div>
                <div class="step-connector"></div>
                <div class="step-item" :class="{ active: currentStep >= 3 }">
                  <div class="step-number">3</div>
                  <div class="step-text">Введення даних абонента</div>
                </div>
                <div class="step-connector"></div>
                <div class="step-item" :class="{ active: currentStep >= 4 }">
                  <div class="step-number">4</div>
                  <div class="step-text">Реєстрація на OLT</div>
                </div>
              </div>
            </div>
            <div class="quick-info-card">
              <div class="quick-info-title">
                <i class="bi bi-lightbulb me-2"></i>Підказка
              </div>
              <div class="quick-info-text">
                Після реєстрації ONU з'явиться вкладка <strong>"Прив'язка"</strong>.
              </div>
            </div>
            <OnuRecommendationsView />
          </div>
        </div>
      </div>

      <!-- Discovery Tab -->
      <div v-if="activeTab === 'discovery'" class="discovery-panel">
        <div class="search-bar">
          <i class="bi bi-search me-2"></i><span>Незареєстровані ONU</span>
        </div>
        <!-- 🔹 НОВИЙ ФОРМАТ ВІДОБРАЖЕННЯ ONU З КНОПКАМИ -->
        <div v-if="parsedUncfgOnu && parsedUncfgOnu.length > 0" class="onu-discovery-list">
          <div
            v-for="(onu, index) in parsedUncfgOnu"
            :key="index"
            class="onu-discovery-item"
          >
            <div class="onu-info">
              <div class="onu-port">
                <i class="bi bi-hdd-network me-2 text-cyan"></i>
                <span class="fw-semibold">Порт:</span> {{ onu.port }}
              </div>
              <div class="onu-sn">
                <i class="bi bi-fingerprint me-2 text-cyan"></i>
                <span class="fw-semibold">SN:</span>
                <span class="sn-value">{{ onu.sn }}</span>
              </div>
            </div>
            <div class="onu-actions">
              <!-- 🔹 НОВА КНОПКА "ОБРАТИ" -->
              <button
                class="btn-select-onu"
                @click="selectOnuFromDiscovery(onu.sn)"
                type="button"
                :title="'Обрати SN: ' + onu.sn"
              >
                <i class="bi bi-check-lg me-1"></i>
                Обрати
              </button>
              <!-- КНОПКА КОПІЮВАННЯ -->
              <button
                class="btn-copy-sn"
                @click="copySnToClipboard(onu.sn)"
                type="button"
                :title="'Копіювати SN: ' + onu.sn"
              >
                <i class="bi bi-clipboard me-1"></i>
                Копіювати SN
              </button>
            </div>
          </div>
        </div>
        <!-- Показуємо старий формат якщо дані не розпарсились -->
        <div v-else-if="consoleOutput" class="console-output" ref="consoleElement">
          <pre class="console-text">{{ consoleOutput }}</pre>
        </div>
        <!-- Повідомлення якщо ONU не знайдено -->
        <div v-else class="no-onu-message">
          <i class="bi bi-inbox me-2"></i>
          <span>Незареєстровані ONU не знайдено</span>
        </div>
        <button
          class="btn-search"
          @click="fetchUncfgOnu"
          :disabled="isLoading"
          type="button"
        >
          <i class="bi bi-search me-2"></i>Знайти ONU
        </button>
      </div>

      <!-- 🔹 НОВИЙ ТАБ: ПРИВ'ЯЗКА В БІЛЛІНГУ -->
      <div v-if="activeTab === 'binding' && isOnuRegistered" class="binding-panel">
        <div class="binding-header">
          <i class="bi bi-link-45deg me-2"></i>
          <span>Прив'язка ONU в біллінгу</span>
        </div>
        <div class="binding-form">
          <!-- ONU Information -->
          <div class="card-section">
            <div class="section-header">
              <i class="bi bi-info-circle me-2 text-cyan"></i>
              <span class="fw-semibold">Інформація про ONU</span>
            </div>
            <div class="section-content">
              <div class="info-grid">
                <div class="info-item">
                  <label class="info-label">OLT</label>
                  <div class="info-value">{{ deviceName }} ({{ deviceIp }})</div>
                </div>
                <div class="info-item">
                  <label class="info-label">Інтерфейс</label>
                  <div class="info-value">{{ bindingForm.interface }}</div>
                </div>
                <div class="info-item">
                  <label class="info-label">ONU ID</label>
                  <div class="info-value">{{ bindingForm.onuId }}</div>
                </div>
                <div class="info-item">
                  <label class="info-label">Серійний номер</label>
                  <div class="info-value mono">{{ bindingForm.onu_sn }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Binding Parameters -->
          <div class="card-section">
            <div class="section-header">
              <i class="bi bi-file-text me-2 text-cyan"></i>
              <span class="fw-semibold">Параметри прив'язки</span>
            </div>
            <div class="section-content">
              <div class="row">
                <div class="col-6">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-file-earmark-text me-1"></i>№ договору</label
                  >
                  <input
                    v-model="bindingForm.agreement"
                    type="text"
                    class="form-control-light"
                    placeholder="1404"
                  />
                </div>
                <div class="col-6">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-hdd-network me-1"></i>Switch IP</label
                  >
                  <input
                    v-model="bindingForm.switch"
                    type="text"
                    class="form-control-light"
                    :disabled="true"
                  />
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-6">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-plug me-1"></i>Port</label
                  >
                  <input
                    v-model="bindingForm.port"
                    type="text"
                    class="form-control-light"
                    :disabled="true"
                  />
                </div>
                <div class="col-6">
                  <label class="form-label small text-muted"
                    ><i class="bi bi-pc-display me-1"></i>IP адреса</label
                  >
                  <input
                    v-model="bindingForm.ip"
                    type="text"
                    class="form-control-light"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- User MAC Address -->
          <div class="card-section">
            <div class="section-header">
              <i class="bi bi-hdd-network me-2 text-cyan"></i>
              <span class="fw-semibold">MAC адреса абонентського роутера</span>
            </div>
            <div class="section-content">
              <div class="mb-3">
                <label class="form-label small text-muted"
                  ><i class="bi bi-fingerprint me-1"></i>User MAC</label
                >
                <div class="d-flex gap-2">
                  <input
                    v-model="bindingForm.user_mac"
                    type="text"
                    class="form-control-light"
                    placeholder="AA:10:BB:20:CC:30"
                    :disabled="isFetchingMac"
                  />
                  <button
                    class="btn-fetch-mac"
                    @click="fetchUserMac"
                    type="button"
                    :disabled="isFetchingMac || !canFetchMac"
                    :title="canFetchMac ? 'Отримати MAC адресу' : 'Заповніть всі поля реєстрації'"
                  >
                    <i v-if="isFetchingMac" class="bi bi-arrow-clockwise spinning me-1"></i>
                    <i v-else class="bi bi-search me-1"></i>
                    {{ isFetchingMac ? 'Отримання...' : 'Отримати MAC' }}
                  </button>
                </div>
                <div class="form-text small">
                  <i class="bi bi-info-circle me-1"></i>
                  MAC адреса отримуватиметься з OLT за інтерфейсом
                  <strong>{{ bindingForm.interface }}:{{ bindingForm.onuId }}</strong>
                </div>
                <!-- 🔹 УНІВЕРСАЛЬНИЙ ALERT ДЛЯ ПОМИЛОК MAC -->
                <div v-if="macError" class="alert alert-danger">
                  <i class="bi bi-exclamation-triangle-fill alert-icon"></i>
                  <span class="alert-text">{{ macError }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="binding-actions">
            <a
              :href="billingBindingLink || '#'"
              target="_blank"
              class="btn btn-binding"
              :class="{
                disabled: !billingBindingLink,
                'opacity-50 cursor-not-allowed': !billingBindingLink,
              }"
              :title="
                billingBindingLink
                  ? 'Перейти до привʼязки в біллінгу'
                  : 'Заповніть всі обовʼязкові поля'
              "
            >
              <i class="bi bi-box-arrow-up-right me-2"></i>
              Перейти до прив'язки в біллінгу
            </a>
            <button
              class="btn btn-secondary"
              @click="resetBindingForm"
              type="button"
            >
              <i class="bi bi-arrow-counterclockwise me-1"></i>
              Скинути
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showConfigModal" class="modal-wrapper">
        <div class="modal-container" :class="modalState">
          <div class="modal-header">
            <div class="d-flex align-items-center">
              <i :class="modalHeaderIcon" class="me-2 fs-5"></i>
              <h5 class="modal-title mb-0">{{ modalTitle }}</h5>
            </div>
            <button
              class="btn-close-modal"
              @click="closeModal"
              aria-label="Close"
              type="button"
            >
              <i class="bi bi-x-lg"></i>
            </button>
          </div>
          <div class="modal-body">
            <div
              v-if="modalState === 'preview' && previewSummary"
              class="preview-summary mb-3"
            >
              <div class="summary-header">
                <i class="bi bi-card-checklist me-2"></i
                ><span>Параметри конфігурації</span>
              </div>
              <div class="summary-grid">
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-hdd-network me-1"></i>OLT</span
                  ><span class="summary-value">{{ selectedOlt?.deviceName }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-hdd-network me-1"></i>Порт</span
                  ><span class="summary-value">{{ previewSummary.interface }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-hash me-1"></i>ONU ID</span
                  ><span class="summary-value">#{{ previewSummary.onu_id }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-cpu me-1"></i>Тип</span
                  ><span class="summary-value">{{ previewSummary.onu_type }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-fingerprint me-1"></i>SN</span
                  ><span class="summary-value font-monospace">{{
                    previewSummary.sn
                  }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-diagram-3 me-1"></i>VLAN</span
                  ><span class="summary-value">{{ previewSummary.vlan }}</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label"
                    ><i class="bi bi-speedometer me-1"></i>Швидкість</span
                  ><span class="summary-value">{{ previewSummary.speed }}</span>
                </div>
              </div>
              <div v-if="configAnalysis" class="analysis-bar mt-3">
                <span class="analysis-badge"
                  ><i class="bi bi-file-earmark-code me-1"></i
                  >{{ configAnalysis.commands_count }} команд</span
                >
                <span class="analysis-badge"
                  ><i class="bi bi-clock me-1"></i
                  >{{ configAnalysis.estimated_execution_time }}</span
                >
                <span
                  v-if="configAnalysis.sections?.security"
                  class="analysis-badge badge-success"
                  ><i class="bi bi-shield-check me-1"></i>Security</span
                >
              </div>
            </div>
            <div class="config-wrapper">
              <div class="config-header">
                <span class="config-title"
                  ><i class="bi bi-terminal me-1"></i>{{ configTitle }}</span
                >
                <button class="btn-copy-inline" @click="copyConfig" type="button">
                  <i class="bi bi-clipboard"></i
                  ><span class="btn-copy-text">Копіювати</span>
                </button>
              </div>
              <pre class="config-code" ref="configCodeRef">{{ configToShow }}</pre>
            </div>
            <!-- 🔹 УНІВЕРСАЛЬНІ ALERTS В МОДАЛЬНОМУ ВІКНІ -->
            <div
              v-if="modalState === 'preview'"
              class="alert alert-warning"
            >
              <i class="bi bi-exclamation-triangle-fill alert-icon"></i>
              <div class="alert-text">
                <strong>Увага:</strong> Застосування конфігурації змінить
                налаштування OLT.
              </div>
            </div>
            <div
              v-if="modalState === 'success'"
              class="alert alert-success"
            >
              <i class="bi bi-check-circle-fill alert-icon"></i>
              <div class="alert-text">
                <strong>Успішно!</strong> ONU зареєстровано.
              </div>
            </div>
            <div
              v-if="modalState === 'error' && errorMessage"
              class="alert alert-danger"
            >
              <i class="bi bi-exclamation-circle-fill alert-icon"></i>
              <div class="alert-text">
                <strong>Помилка:</strong> {{ errorMessage }}
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <template v-if="modalState === 'preview'">
              <button
                class="btn-modal btn-secondary"
                @click="closeModal"
                :disabled="isApplying"
                type="button"
              >
                <i class="bi bi-x-lg me-1"></i>Скасувати
              </button>
              <button
                class="btn-modal btn-warning"
                @click="confirmAndApply"
                :disabled="isApplying"
                type="button"
              >
                <i class="bi bi-arrow-return-right me-1"></i>{{
                  isApplying ? 'Застосовую...' : 'Застосувати конфіг'
                }}
              </button>
            </template>
            <template v-else-if="modalState === 'success'">
              <button class="btn-modal btn-secondary" @click="copyConfig" type="button">
                <i class="bi bi-clipboard me-1"></i>Копіювати
              </button>
           
              <button class="btn-modal btn-success" @click="closeModal" type="button">
                <i class="bi bi-check-lg me-1"></i>Готово
              </button>
            </template>
            <template v-else-if="modalState === 'error'">
              <button class="btn-modal btn-secondary" @click="closeModal" type="button">
                Закрити
              </button>
              <button
                class="btn-modal btn-danger"
                @click="retryRegistration"
                :disabled="isApplying"
                type="button"
              >
                <i class="bi bi-arrow-clockwise me-1"></i>{{
                  isApplying ? 'Повтор...' : 'Повторити'
                }}
              </button>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, onUnmounted } from 'vue';
import OnuRecommendationsView from './OnuRecommendationsView.vue';

// 🔹 Присвоюємо props змінній для доступу в скрипті
const props = defineProps({
  agreement: String
});

// 🔹 Читаем URL из переменных окружения (.env)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BILLING_BINDINGS_URL = import.meta.env.VITE_BILLING_BINDINGS_URL;

// 🔹 Fallback на дефолтные значения
const API_URL = API_BASE_URL || 'http://localhost:8000/api';
const BILLING_URL = BILLING_BINDINGS_URL || 'http://localhost:8000/billing/bind';

const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_URL}${endpoint}`;
  const method = options.method || 'GET';
  const config = { method, headers: { 'Content-Type': 'application/json' } };
  if (options.body)
    config.body =
      typeof options.body === 'string'
        ? options.body
        : JSON.stringify(options.body);
  try {
    const response = await fetch(url, config);
    const contentType = response.headers.get('content-type');
    let data = {};
    if (contentType && contentType.includes('application/json'))
      data = await response.json();
    else
      throw new Error(
        `Server returned non-JSON: ${await response.text().then((t) => t.substring(0, 200))}`
      );
    if (!response.ok || data.status === 'error' || data.success === false)
      throw new Error(data.message || data.error || `HTTP ${response.status}`);
    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch'))
      throw new Error('Не вдалося підключитися до сервера.');
    throw error;
  }
};

// 🔹 MULTI-OLT STATE
const olts = ref([]);
const activeOltId = ref(null);
const activeTab = ref('register');
const isLoading = ref(false);
const isApplying = ref(false);
const flashMessages = ref([]);
const consoleOutput = ref('');
const consoleElement = ref(null);
const sections = reactive({ pon: true, type: true, service: true, billing: true });
const onuIdMode = ref('auto');

// 🔹 Ініціалізація form.comment з props.agreement
const form = reactive({
  interface: '',
  onuId: '',
  onuType: '',
  speed: '100',
  vlan: '',
  sn: '',
  comment: props.agreement || '',
});

// 🔹 ФОРМА ДЛЯ ПРИВ'ЯЗКИ В БІЛЛІНГУ
const bindingForm = reactive({
  agreement: '',
  switch: '',
  port: '',
  ip: '',
  onu_sn: '',
  user_mac: '',
  interface: '',
  onuId: ''
});

const activeOnuCount = ref(0);
const interfaces = ref({});
const onuTypes = ref({});
const speeds = ref([]);
const lineProfilesRaw = ref({});
const portVlanMapping = ref({});
const showConfigModal = ref(false);
const configToShow = ref('');
const modalState = ref('preview');
const previewSummary = ref(null);
const configAnalysis = ref(null);
const errorMessage = ref('');
const configCodeRef = ref(null);
const pendingRegistrationPayload = ref(null);
const freeIp = ref(null);
const isFetchingIp = ref(false);
const ipError = ref(null);

// 🔹 НОВІ ЗМІННІ ДЛЯ MAC
const isFetchingMac = ref(false);
const macError = ref(null);
const isOnuRegistered = ref(false);

// 🔹 SELECTED OLT COMPUTED
const selectedOlt = computed(() => {
  return olts.value.find(olt => olt.oltId === activeOltId.value) || null;
});

// 🔹 OLT DATA FROM SELECTED OLT
const deviceName = computed(() => selectedOlt.value?.deviceName || '');
const deviceIp = computed(() => selectedOlt.value?.deviceIp || '');

const lineProfilesDisplay = computed(() => {
  const result = {};
  for (const [key, vlanNumber] of Object.entries(lineProfilesRaw.value))
    result[key] = `${key} (VLAN ${vlanNumber})`;
  return result;
});

const isFormValid = computed(
  () =>
    form.interface &&
    form.onuId &&
    form.onuType &&
    form.speed &&
    form.vlan &&
    form.sn &&
    form.sn.length >= 8
);

const currentStep = computed(() => {
  if (!form.interface || !form.onuId) return 0;
  if (!form.vlan) return 1;
  if (!form.sn || !form.comment) return 2;
  return 4;
});

const isRecommendedVlan = (profileKey) =>
  form.interface && portVlanMapping.value[form.interface]?.includes(profileKey);

// 🔹 ПОСИЛАННЯ ДЛЯ ПРИВ'ЯЗКИ В БІЛЛІНГУ
const billingBindingLink = computed(() => {
  if (
    !bindingForm.switch ||
    !bindingForm.port ||
    !bindingForm.agreement ||
    !bindingForm.ip
  ) {
    return null;
  }
  const params = new URLSearchParams({
    agreement: bindingForm.agreement,
    switch: bindingForm.switch,
    port: bindingForm.port,
    ip: bindingForm.ip,
    onu_sn: bindingForm.onu_sn,
    ...(bindingForm.user_mac && { mac: bindingForm.user_mac })
  });
  return `${BILLING_URL}?${params.toString()}`;
});

// 🔹 ЧИ МОЖНА ОТРИМАТИ MAC
const canFetchMac = computed(() => {
  return bindingForm.interface && bindingForm.onuId && activeOltId.value;
});

const modalTitle = computed(() => ({
  preview: 'Перегляд конфігурації',
  success: 'Конфігурацію застосовано',
  error: 'Помилка застосування',
}[modalState.value]));

const modalHeaderIcon = computed(() => ({
  preview: 'bi bi-eye-fill text-warning',
  success: 'bi bi-check-circle-fill text-success',
  error: 'bi bi-exclamation-triangle-fill text-danger',
}[modalState.value]));

const configTitle = computed(() => ({
  preview: 'Буде виконано:',
  success: 'Виконано:',
  error: 'Помилка:',
}[modalState.value]));

// 🔹 PARSED UNCFG ONU - підтримує { data: [...] } та прямий масив
const parsedUncfgOnu = computed(() => {
  if (!consoleOutput.value) return [];
  try {
    // Якщо consoleOutput вже об'єкт/масив (не рядок)
    if (typeof consoleOutput.value !== 'string') {
      const val = consoleOutput.value;
      if (Array.isArray(val)) return val;
      if (val?.data && Array.isArray(val.data)) return val.data;
      return [];
    }
    // Якщо це JSON-строка
    const parsed = JSON.parse(consoleOutput.value);
    if (parsed?.data && Array.isArray(parsed.data)) return parsed.data;
    if (Array.isArray(parsed)) return parsed;
    return [];
  } catch (err) {
    console.warn('Failed to parse uncfg ONU:', err);
    return [];
  }
});

// 🔹 OLT CHANGE HANDLER
const onOltChange = async () => {
  isLoading.value = true;
  try {
    await fetchOltConfig(activeOltId.value);
    resetForm();
    addFlashMessage('success', `OLT змінено: ${selectedOlt.value?.deviceName}`);
  } catch (error) {
    addFlashMessage('danger', `Помилка зміни OLT: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

watch(() => form.interface, async (newInterface, oldInterface) => {
  if (!newInterface) {
    form.vlan = '';
    return;
  }
  if (form.vlan && oldInterface !== newInterface) form.vlan = '';
  const recommendedKey = portVlanMapping.value[newInterface]?.[0];
  if (
    recommendedKey &&
    lineProfilesRaw.value[recommendedKey] !== undefined
  ) {
    form.vlan = `${recommendedKey}+++${lineProfilesRaw.value[recommendedKey]}`;
  }
  if (onuIdMode.value === 'auto') await fetchFreeOnuId();
});

watch(() => onuIdMode.value, async (newMode) => {
  if (newMode === 'auto' && form.interface) await fetchFreeOnuId();
  else if (newMode === 'manual') form.onuId = '';
});

watch(
  () => form.vlan,
  async (vlan) => {
    freeIp.value = null;
    ipError.value = null;
    if (!vlan) return;
    isFetchingIp.value = true;
    try {
      const profileKey = vlan.split('+++')[0];
      const vlanNumber = lineProfilesRaw.value[profileKey];
      if (vlanNumber === undefined) {
        console.warn('Не знайдено номер VLAN для профілю:', profileKey);
        ipError.value = 'VLAN не знайдено';
        return;
      }
      const apiUrl = `${API_URL}/get-free-ip?vlan_name=${encodeURIComponent(vlanNumber)}`;
      console.log('🔍 Запит вільного IP:', apiUrl);
      const res = await fetch(apiUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log('✅ Відповідь API:', data);
      freeIp.value = Array.isArray(data.free_ip)
        ? data.free_ip[0]?.free_ip
        : data.free_ip || data?.data?.free_ip || null;
      if (!freeIp.value) {
        ipError.value = 'Вільних IP не знайдено';
        addFlashMessage('warning', 'Немає вільних IP-адрес у цьому VLAN');
      }
    } catch (e) {
      console.error('❌ Помилка отримання IP:', e);
      ipError.value = `Помилка: ${e.message}`;
      addFlashMessage('danger', `Не вдалося отримати IP: ${e.message}`);
    } finally {
      isFetchingIp.value = false;
    }
  }
);

const toggleSection = (section) => (sections[section] = !sections[section]);
const selectOnuType = (type) => (form.onuType = type);
const formatSnInput = (event) =>
  (form.sn = event.target.value.toUpperCase().replace(/\s/g, ''));

const getIconClass = (category) => ({
  success: 'bi bi-check-circle-fill',
  danger: 'bi bi-exclamation-triangle-fill',
  warning: 'bi bi-exclamation-circle-fill',
  info: 'bi bi-info-circle-fill',
}[category] || 'bi bi-info-circle-fill');

const addFlashMessage = (category, text) => {
  if (
    flashMessages.value.some(
      (msg) => msg.category === category && msg.text === text
    )
  )
    return;
  flashMessages.value.push({ category, text });
  setTimeout(
    () => removeFlashMessageByContent(category, text),
    category === 'success' ? 5000 : 10000
  );
};

const removeFlashMessage = (index) => flashMessages.value.splice(index, 1);
const removeFlashMessageByContent = (category, text) => {
  const index = flashMessages.value.findIndex(
    (msg) => msg.category === category && msg.text === text
  );
  if (index !== -1) flashMessages.value.splice(index, 1);
};

// 🔹 КОПІЮВАННЯ SN В CLIPBOARD
const copySnToClipboard = async (sn) => {
  if (!sn) {
    addFlashMessage('warning', 'Немає SN для копіювання');
    return;
  }
  try {
    await navigator.clipboard.writeText(sn);
    addFlashMessage('success', `SN ${sn} скопійовано!`);
  } catch (err) {
    console.warn('Clipboard API не доступний, використовуємо fallback:', err);
    const textarea = document.createElement('textarea');
    textarea.value = sn;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        addFlashMessage('success', `SN ${sn} скопійовано!`);
      } else {
        addFlashMessage('warning', 'Не вдалося скопіювати SN');
      }
    } catch (execErr) {
      console.error('Fallback copy failed:', execErr);
      addFlashMessage('warning', 'Не вдалося скопіювати SN');
    }
    document.body.removeChild(textarea);
  }
};

// 🔹 ОБРАТИ ONU З DISCOVERY
const selectOnuFromDiscovery = async (sn) => {
  if (!sn) {
    addFlashMessage('warning', 'Немає SN для вибору');
    return;
  }
  // Заповнюємо поле SN
  form.sn = sn.toUpperCase().replace(/\s/g, '');
  // Перемикаємо на вкладку Реєстрація
  activeTab.value = 'register';
  addFlashMessage('success', `SN ${sn} обрано. Перехід до реєстрації.`);
};

// 🔹 ВІДКРИТИ DISCOVERY ДЛЯ ПОШУКУ SN
const openDiscoveryForSn = async () => {
  activeTab.value = 'discovery';
  addFlashMessage('info', 'Перехід до пошуку незареєстрованих ONU');
  // Автоматично запускаємо пошук
  await fetchUncfgOnu();
};

// 🔹 ОТРИМАТИ ВСІ OLT
const fetchConfig = async () => {
  isLoading.value = true;
  try {
    const response = await apiRequest('/device/config');
    const configData = response.success ? response.data : response;
    // 🔹 MULTI-OLT: тепер це масив
    if (Array.isArray(configData)) {
      olts.value = configData;
      // 🔹 Фільтруємо тільки enabled OLT
      const enabledOlts = olts.value.filter(olt => olt.enabled);
      if (enabledOlts.length > 0) {
        // 🔹 Вибираємо перший enabled OLT
        activeOltId.value = enabledOlts[0].oltId;
        await fetchOltConfig(activeOltId.value);
      } else if (olts.value.length > 0) {
        // 🔹 Якщо немає enabled, беремо перший
        activeOltId.value = olts.value[0].oltId;
        await fetchOltConfig(activeOltId.value);
      } else {
        addFlashMessage('danger', 'Немає доступних OLT');
      }
    } else {
      // 🔹 Fallback для старої версії API (один OLT)
      olts.value = [{ ...configData, oltId: 1, enabled: true }];
      activeOltId.value = 1;
      loadOltData(configData);
    }
  } catch (error) {
    addFlashMessage('danger', `Помилка завантаження: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

// 🔹 ОТРИМАТИ КОНКРЕТНИЙ OLT
const fetchOltConfig = async (oltId) => {
  try {
    // 🔹 Новий endpoint для конкретного OLT
    const response = await apiRequest(`/device/config/${oltId}`);
    const configData = response.success ? response.data : response;
    loadOltData(configData);
  } catch (error) {
    addFlashMessage('danger', `Помилка завантаження OLT: ${error.message}`);
    throw error;
  }
};

// 🔹 ЗАВАНТАЖИТИ ДАНІ OLT
const loadOltData = (configData) => {
  deviceName.value = configData.deviceName || 'ZTE';
  deviceIp.value = configData.deviceIp || '';
  interfaces.value = configData.interfaces || {};
  onuTypes.value = configData.onuTypes || {};
  speeds.value = configData.speeds || [];
  activeOnuCount.value = configData.activeOnuCount || 0;
  const allVlans = configData.vlans || {};
  lineProfilesRaw.value = {};
  for (const [key, value] of Object.entries(allVlans))
    lineProfilesRaw.value[key] = typeof value === 'object' ? value.id : value;
  portVlanMapping.value = configData.portVlanMapping || {};
  const firstType = Object.keys(onuTypes.value)[0];
  if (firstType) form.onuType = firstType;
};

const fetchUncfgOnu = async () => {
  isLoading.value = true;
  try {
    // 🔹 Додаємо oltId до запиту
    const response = await apiRequest(`/show-uncfg-onu?olt_id=${activeOltId.value}`);
    // 🔹 Зберігаємо ВСЮ відповідь як JSON-строку для коректного парсингу
    consoleOutput.value = JSON.stringify(response);
    addFlashMessage('success', 'Список ONU оновлено');
    setTimeout(() => {
      if (consoleElement.value)
        consoleElement.value.scrollTop = consoleElement.value.scrollHeight;
    }, 100);
  } catch (error) {
    addFlashMessage('danger', `Помилка: ${error.message}`);
    consoleOutput.value = `Error: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
};

const fetchFreeOnuId = async () => {
  if (!form.interface) return;
  isLoading.value = true;
  try {
    // 🔹 Додаємо oltId до запиту
    const response = await apiRequest('/get-free-onu', {
      method: 'POST',
      body: {
        interface: form.interface,
        olt_id: activeOltId.value
      },
    });
    if (response.status === 'success' && response.onuId) {
      form.onuId = response.onuId;
      addFlashMessage('success', `Вільний ONU ID: ${response.onuId}`);
    } else throw new Error(response.message || 'Не вдалося отримати вільний ONU ID');
  } catch (error) {
    addFlashMessage('danger', `Помилка: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

// 🔹 ФУНКЦІЯ НОРМАЛІЗАЦІЇ ІНТЕРФЕЙСУ (olt → onu зі збереженням формату)
const normalizeInterface = (iface) => {
  if (!iface) return '';
  // Просто замінюємо olt на onu, всі інші символи залишаються без змін
  return iface.replace(/olt/gi, 'onu');
};

// 🔹 ОТРИМАТИ MAC АДРЕСУ КОРИСТУВАЧА
const fetchUserMac = async () => {
  if (!canFetchMac.value) {
    macError.value = 'Заповніть інтерфейс та ONU ID';
    return;
  }
  isFetchingMac.value = true;
  macError.value = null;
  try {
    // 🔹 Використовуємо вже нормалізований bindingForm.interface
    const fullInterface = `${bindingForm.interface}:${bindingForm.onuId}`;
    
    const response = await apiRequest(
      `/get-onu-user-mac?olt_id=${activeOltId.value}&interface=${encodeURIComponent(fullInterface)}`
    );
    if (response.status === 'success' && response.mac_address) {
      bindingForm.user_mac = response.mac_address;
      addFlashMessage('success', `MAC адресу отримано: ${response.mac_address}`);
    } else {
      macError.value = response.message || 'MAC адресу не знайдено';
      addFlashMessage('warning', macError.value);
    }
  } catch (error) {
    macError.value = `Помилка отримання MAC: ${error.message}`;
    addFlashMessage('danger', macError.value);
  } finally {
    isFetchingMac.value = false;
  }
};

const previewConfig = async () => {
  if (!isFormValid.value) {
    addFlashMessage('warning', 'Заповніть всі поля');
    return;
  }
  isLoading.value = true;
  try {
    const [vlanName, vlanId] = form.vlan.split('+++');
    if (!vlanName || !vlanId) throw new Error('Невірний формат VLAN');
    const payload = {
      interface: form.interface,
      onuId: Number(form.onuId),
      onuType: form.onuType,
      speed: Number(form.speed),
      vlan: form.vlan,
      sn: form.sn,
      comment: form.comment,
      olt_id: activeOltId.value,
    };
    const response = await apiRequest('/preview-onu-config', {
      method: 'POST',
      body: payload,
    });
    if (response.status === 'preview') {
      pendingRegistrationPayload.value = payload;
      showConfigModal.value = true;
      modalState.value = 'preview';
      configToShow.value = response.config || '';
      previewSummary.value = response.payload_summary || null;
      configAnalysis.value = response.config_analysis || null;
      errorMessage.value = '';
    } else throw new Error(response.message || 'Невідома помилка');
  } catch (error) {
    addFlashMessage('danger', `Помилка перегляду: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

const confirmAndApply = async () => {
  if (!pendingRegistrationPayload.value) {
    addFlashMessage('danger', 'Немає даних');
    closeModal();
    return;
  }
  isApplying.value = true;
  try {
    const response = await apiRequest('/register-onu', {
      method: 'POST',
      body: pendingRegistrationPayload.value,
    });
    if (response.status === 'success') {
      modalState.value = 'success';
      configToShow.value = response.config || 'Конфігурацію застосовано';
      addFlashMessage('success', `ONU ${form.sn} зареєстровано!`);
      // 🔹 ПІДГОТОВЛЯЄМО ДАНІ ДЛЯ ПРИВ'ЯЗКИ
      prepareBindingData();
      resetForm();
      pendingRegistrationPayload.value = null;
      // 🔹 АВТОМАТИЧНИЙ ПЕРЕХІД НА ВКЛАДКУ ПРИВ'ЯЗКИ
      goToBindingTab();
    } else throw new Error(response.message || 'Помилка реєстрації');
  } catch (error) {
    modalState.value = 'error';
    errorMessage.value = error.message;
    configToShow.value = error.config || configToShow.value;
    addFlashMessage('danger', `Помилка: ${error.message}`);
  } finally {
    isApplying.value = false;
  }
};

// 🔹 ПІДГОТОВКА ДАНИХ ДЛЯ ПРИВ'ЯЗКИ В БІЛЛІНГУ
const prepareBindingData = () => {
  // 🔹 НОРМАЛІЗУЄМО інтерфейс (olt → onu зі збереженням формату)
  const normalizedInterface = normalizeInterface(form.interface);
  
  const port = `${normalizedInterface}:${form.onuId}`;
  
  bindingForm.agreement = form.comment;
  bindingForm.switch = deviceIp.value;
  bindingForm.port = port;
  bindingForm.ip = freeIp.value || '';
  bindingForm.onu_sn = form.sn;
  
  // 🔹 Зберігаємо вже нормалізований інтерфейс (буде правильно відображатися в UI)
  bindingForm.interface = normalizedInterface;
  bindingForm.onuId = form.onuId;
  bindingForm.user_mac = ''; // Скидаємо MAC, потрібно отримати заново
  
  // Показуємо таб прив'язки
  isOnuRegistered.value = true;
};

// 🔹 ПЕРЕЙТИ ДО ТАБУ ПРИВ'ЯЗКИ
const goToBindingTab = () => {
  activeTab.value = 'binding';
};

const retryRegistration = () => {
  if (pendingRegistrationPayload.value) confirmAndApply();
};

const registerONU = async () => {
  if (!isFormValid.value) {
    addFlashMessage('warning', 'Заповніть всі поля');
    return;
  }
  isLoading.value = true;
  try {
    const [vlanName, vlanId] = form.vlan.split('+++');
    if (!vlanName || !vlanId) throw new Error('Невірний формат VLAN');
    const payload = {
      interface: form.interface,
      onuId: Number(form.onuId),
      onuType: form.onuType,
      speed: Number(form.speed),
      vlan: form.vlan,
      sn: form.sn,
      comment: form.comment,
      olt_id: activeOltId.value,
    };
    const response = await apiRequest('/register-onu', {
      method: 'POST',
      body: payload,
    });
    if (response.status === 'success') {
      showConfigModal.value = true;
      modalState.value = 'success';
      configToShow.value = response.config || 'Конфігурацію застосовано';
      addFlashMessage('success', `ONU ${form.sn} зареєстровано!`);
      // 🔹 ПІДГОТОВЛЯЄМО ДАНІ ДЛЯ ПРИВ'ЯЗКИ
      prepareBindingData();
      resetForm();
      // 🔹 АВТОМАТИЧНИЙ ПЕРЕХІД НА ВКЛАДКУ ПРИВ'ЯЗКИ
      goToBindingTab();
    } else throw new Error(response.message || 'Помилка реєстрації');
  } catch (error) {
    modalState.value = 'error';
    showConfigModal.value = true;
    errorMessage.value = error.message;
    configToShow.value = error.config || error.message || 'Невідома помилка';
    addFlashMessage('danger', `Помилка: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};

const closeModal = () => {
  if (isApplying.value) return;
  if (modalState.value === 'preview') pendingRegistrationPayload.value = null;
  showConfigModal.value = false;
  setTimeout(() => {
    if (!showConfigModal.value) {
      modalState.value = 'preview';
      errorMessage.value = '';
    }
  }, 200);
};

const resetForm = () => {
  form.interface = '';
  form.onuId = '';
  form.speed = '';
  form.vlan = '';
  form.sn = '';
  form.comment = props.agreement || '';
  const firstType = Object.keys(onuTypes.value)[0];
  if (firstType) form.onuType = firstType;
  onuIdMode.value = 'auto';
  freeIp.value = null;
  ipError.value = null;
};

// 🔹 СКИНУТИ ФОРМУ ПРИВ'ЯЗКИ
const resetBindingForm = () => {
  bindingForm.agreement = '';
  bindingForm.switch = '';
  bindingForm.port = '';
  bindingForm.ip = '';
  bindingForm.onu_sn = '';
  bindingForm.user_mac = '';
  bindingForm.interface = '';
  bindingForm.onuId = '';
  macError.value = null;
  addFlashMessage("info", "Форму прив'язки скинуто");
};

const copyConfig = async () => {
  const text = configToShow.value;
  if (!text || text.trim() === '') {
    addFlashMessage('warning', 'Немає конфігурації для копіювання');
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    addFlashMessage('success', 'Конфігурацію скопійовано!');
  } catch (err) {
    console.warn('Clipboard API не доступний, використовуємо fallback:', err);
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        addFlashMessage('success', 'Конфігурацію скопійовано!');
      } else {
        addFlashMessage('warning', 'Не вдалося скопіювати');
      }
    } catch (execErr) {
      console.error('Fallback copy failed:', execErr);
      addFlashMessage('warning', 'Не вдалося скопіювати');
    }
    document.body.removeChild(textarea);
  }
};

onMounted(() => {
  if (!import.meta.env.VITE_API_BASE_URL) {
    console.warn('⚠️ VITE_API_BASE_URL не задан в .env, використовується дефолт');
  }
  if (!import.meta.env.VITE_BILLING_BINDINGS_URL) {
    console.warn('⚠️ VITE_BILLING_BINDINGS_URL не задан в .env, використовується дефолт');
  }
  fetchConfig();
  const handleKeydown = (e) => {
    if (!showConfigModal.value) return;
    if (modalState.value === 'preview') {
      if (e.key === 'Enter' && !isApplying.value) {
        e.preventDefault();
        confirmAndApply();
      }
      if (e.key === 'Escape') {
        e.preventDefault();
        closeModal();
      }
    } else if (
      (modalState.value === 'success' || modalState.value === 'error') &&
      (e.key === 'Escape' || e.key === 'Enter')
    ) {
      e.preventDefault();
      closeModal();
    }
  };
  window.addEventListener('keydown', handleKeydown);
  onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
});
</script>

<style>
/* ============================================
🔹 LEGACY FIX: ЗАХИСТ ВІД СТИЛІВ РОДИТЕЛЯ
============================================ */
.olt-container {
  all: initial;
  font-size: 18px !important;
  line-height: 1.5 !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  box-sizing: border-box;
}

.olt-container *,
.olt-container *::before,
.olt-container *::after {
  box-sizing: inherit;
  font-family: inherit;
}

/* ============================================
ОСНОВНИЙ КОНТЕЙНЕР - СВІТЛА ТЕМА
============================================ */
.olt-container {
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
  --alert-success-bg: #d1e7dd;
  --alert-success-border: #badbcc;
  --alert-success-text: #0f5132;
  --alert-danger-bg: #f8d7da;
  --alert-danger-border: #f5c2c7;
  --alert-danger-text: #842029;
  --alert-warning-bg: #fff3cd;
  --alert-warning-border: #ffecb5;
  --alert-warning-text: #997404;
  --alert-info-bg: #cff4fc;
  --alert-info-border: #b6effb;
  --alert-info-text: #055160;
  background: var(--bg-primary);
  min-height: 100vh;
  color: var(--text-primary);
  display: block;
}

/* ============================================
🔹 УНІВЕРСАЛЬНІ ALERTS - ОДИНАКОВИЙ ДИЗАЙН ВЕЗДИ
============================================ */
.olt-container .alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border-radius: 8px;
  border: 1px solid;
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 0.75rem;
}

.olt-container .alert-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.olt-container .alert-text {
  flex: 1;
  color: inherit;
}

.olt-container .alert-success {
  background: var(--alert-success-bg);
  border-color: var(--alert-success-border);
  color: var(--alert-success-text);
}

.olt-container .alert-danger {
  background: var(--alert-danger-bg);
  border-color: var(--alert-danger-border);
  color: var(--alert-danger-text);
}

.olt-container .alert-warning {
  background: var(--alert-warning-bg);
  border-color: var(--alert-warning-border);
  color: var(--alert-warning-text);
}

.olt-container .alert-info {
  background: var(--alert-info-bg);
  border-color: var(--alert-info-border);
  color: var(--alert-info-text);
}

/* ============================================
🔹 FLASH МЕСЕДЖІ З УНІВЕРСАЛЬНИМИ ALERTS
============================================ */
.flash-container {
  position: fixed;
  top: 0.85rem;
  right: 0.85rem;
  z-index: 10000;
  max-width: 450px;
  width: calc(100% - 2rem);
}

.flash-item {
  margin-bottom: 0.65rem;
  animation: slideIn 0.3s ease-out;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flash-item .alert-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
}

.flash-item .alert-close {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  opacity: 0.7;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.flash-item .alert-close:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.1);
}

/* ============================================
🔹 ЗБІЛЬШЕНІ ШРИФТИ ДЛЯ LEGACY
============================================ */
.olt-container .form-control-light,
.olt-container .form-label,
.olt-container .mode-title,
.olt-container .type-name,
.olt-container .step-text,
.olt-container .summary-value,
.olt-container .config-code,
.olt-container .modal-title,
.olt-container .section-header span,
.olt-container .cli-tab,
.olt-container .tab-btn,
.olt-container .btn-status,
.olt-container .btn-modal,
.olt-container .btn-search,
.olt-container .btn-auto,
.olt-container .quick-info-text,
.olt-container .flash-item,
.olt-container .spinner-text,
.olt-container .onu-port,
.olt-container .onu-sn,
.olt-container .sn-value,
.olt-container .btn-copy-sn,
.olt-container .btn-select-onu,
.olt-container .btn-fetch-mac,
.olt-container .btn-find-onu {
  font-size: 1.15rem !important;
}

.olt-container .form-label,
.olt-container .mode-desc,
.olt-container .type-specs,
.olt-container .form-text,
.olt-container .quick-info-text,
.olt-container .summary-label,
.olt-container .analysis-badge,
.olt-container .status-label {
  font-size: 1.05rem !important;
}

.olt-container .modal-title,
.olt-container .section-header span,
.olt-container h4,
.olt-container .fw-bold {
  font-size: 1.35rem !important;
}

.olt-container .config-code {
  font-size: 1.1rem !important;
  line-height: 1.6 !important;
}

.olt-container input,
.olt-container select,
.olt-container button,
.olt-container textarea {
  font-size: 1.1rem !important;
  font-family: inherit !important;
}

/* ============================================
ВНУТРІШНІЙ SPINNER LOADER
============================================ */
.spinner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--bg-hover);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-text {
  color: var(--text-secondary);
  font-weight: 500;
}

/* ============================================
🔹 КОМПАКТНИЙ ЗАГОЛОВОК (HEADER)
============================================ */
.olt-header {
  background: linear-gradient(135deg, var(--accent-primary) 0%, #1a2838 100%);
  border-bottom: 1px solid var(--border-color);
  padding: 0.75rem 1.25rem !important;
}

.header-top {
  margin-bottom: 0.5rem !important;
}

.text-cyan { color: #00d4ff !important; }
.text-cyan-opacity { color: rgba(0, 212, 255, 0.8) !important; }
.text-header { color: #ffffff !important; }
.header-tabs {
  display: flex;
  gap: 0.4rem;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
  padding: 0.45rem 1rem !important;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab-btn:hover { background: rgba(255, 255, 255, 0.2); color: white; }
.tab-btn.active { background: white; color: var(--accent-primary); border-color: white; }

/* ============================================
🔹 OLT SELECTOR STYLES
============================================ */
.olt-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.olt-selector-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  font-weight: 500;
}

.olt-selector-select {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.olt-selector-select:hover {
  background: rgba(255, 255, 255, 0.25);
}

.olt-selector-select:focus {
  outline: none;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.3);
}

.olt-selector-select option {
  background: var(--accent-primary);
  color: white;
}

.olt-selector-select option:disabled {
  background: #4a5568;
  color: #a0aec0;
}

/* ============================================
ОСНОВНИЙ КОНТЕНТ
============================================ */
.main-content { padding: 1.25rem 1.5rem; }

/* ============================================
🔹 ПАНЕЛЬ ПРИВ'ЯЗКИ (BINDING PANEL)
============================================ */
.binding-panel {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  max-width: 900px;
  margin: 0 auto;
}

.binding-header {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--accent-primary) 0%, #1a2838 100%);
  color: white;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.binding-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.85rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 500;
}

.info-value {
  font-weight: 600;
  color: var(--text-primary);
  padding: 0.4rem 0.65rem;
  background: var(--bg-hover);
  border-radius: 6px;
}

.mono {
  font-family: 'Courier New', Consolas, monospace;
}

.btn-fetch-mac {
  background: var(--accent-cyan);
  color: white;
  border: none;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-fetch-mac:hover:not(:disabled) {
  background: #008ba8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 168, 204, 0.4);
}

.btn-fetch-mac:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.binding-actions {
  display: flex;
  gap: 0.85rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.btn-binding {
  flex: 1;
  background: var(--accent-green);
  color: white;
  border: none;
  padding: 0.85rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-binding:hover:not(.disabled) {
  background: #157347;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.4);
}

.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 0.85rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

/* ============================================
🔹 ПОЛЕ SN З КНОПКОЮ В ОДИН РЯДОК
============================================ */
.sn-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
}

.sn-input-row .form-control-light {
  flex: 1;
  min-width: 0;
}

/* 🔹 КНОПКА "ЗНАЙТИ ONU" В ЄДИНОМУ СТИЛІ */
.btn-find-onu {
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.btn-find-onu:hover {
  background: #1a2838;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(42, 63, 84, 0.4);
}

.btn-find-onu:active {
  transform: translateY(0);
}

.btn-find-onu i {
  font-size: 1.1rem;
}

/* ============================================
ПАНЕЛЬ DISCOVERY
============================================ */
.discovery-panel {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-bar {
  display: flex;
  align-items: center;
  background: var(--bg-hover);
  padding: 0.6rem 0.85rem;
  border-radius: 8px;
  margin-bottom: 0.85rem;
  border: 1px solid var(--border-color);
}

/* 🔹 НОВИЙ СПИСОК ONU В DISCOVERY */
.onu-discovery-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.onu-discovery-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #1a1a1a;
  border: 2px solid #333;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  transition: all 0.3s ease;
}

.onu-discovery-item:hover {
  border-color: var(--accent-cyan);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
}

.onu-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.onu-port,
.onu-sn {
  color: #00ff00;
  font-family: 'Courier New', Consolas, monospace;
  display: flex;
  align-items: center;
}

.sn-value {
  font-weight: 700;
  color: #fff;
}

/* 🔹 КОНТЕЙНЕР ДЛЯ КНОПОК В DISCOVERY */
.onu-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: 1rem;
}

/* 🔹 КНОПКА "ОБРАТИ" */
.btn-select-onu {
  background: var(--accent-green);
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-select-onu:hover {
  background: #157347;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(25, 135, 84, 0.4);
}

.btn-select-onu:active {
  transform: translateY(0);
}

/* 🔹 КНОПКА КОПІЮВАННЯ SN */
.btn-copy-sn {
  background: var(--accent-cyan);
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-copy-sn:hover {
  background: #008ba8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 168, 204, 0.4);
}

.btn-copy-sn:active {
  transform: translateY(0);
}

/* Повідомлення коли ONU не знайдено */
.no-onu-message {
  background: var(--bg-hover);
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 0.85rem;
}

.console-output {
  background: #1a1a1a;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.85rem;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
  font-family: 'Courier New', Consolas, monospace;
  margin-bottom: 0.85rem;
}

.console-text {
  color: #00ff00;
  background: black;
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.6;
}

.btn-search {
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 0.65rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-search:hover { background: #1a2838; transform: translateY(-1px); }
.btn-search:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* ============================================
СІТКА РЕЄСТРАЦІЇ
============================================ */
.registration-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 1.25rem;
}

/* ============================================
СЕКЦІЇ КАРТОК
============================================ */
.card-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  margin-bottom: 0.85rem;
  overflow: hidden;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
}

.section-content { padding: 1rem; }

/* ============================================
ЕЛЕМЕНТИ ФОРМИ
============================================ */
.form-control-light {
  width: 100%;
  background: white;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.form-control-light:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(42, 63, 84, 0.15);
}

.form-control-light:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: var(--bg-hover);
}

.form-text {
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.form-label {
  margin-bottom: 0.35rem;
  display: block;
  color: var(--text-secondary);
}

/* ============================================
ВИБІР РЕЖИМУ (MODE SELECTOR)
============================================ */
.mode-selector { display: flex; flex-direction: column; gap: 0.65rem; }

.mode-option {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-option:hover { background: var(--bg-hover); }

.mode-option.active {
  border-color: var(--accent-primary);
  background: rgba(42, 63, 84, 0.05);
}

.mode-radio {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.mode-option.active .mode-radio { border-color: var(--accent-primary); }

.radio-dot {
  width: 10px;
  height: 10px;
  background: var(--accent-primary);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.mode-option.active .radio-dot { opacity: 1; }

.mode-info { flex: 1; }

.mode-title {
  font-weight: 600;
  color: var(--text-primary);
}

.mode-desc {
  color: var(--text-muted);
}

.btn-auto {
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-auto:hover {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
}

.btn-auto:disabled { opacity: 0.6; cursor: not-allowed; }

/* ============================================
СІТКА ТИПІВ ONU
============================================ */
.onu-types-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.65rem;
}

.onu-type-card {
  position: relative;
  padding: 0.85rem;
  background: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s ease;
}

.onu-type-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.onu-type-card.selected {
  border-color: var(--accent-primary);
  background: rgba(42, 63, 84, 0.05);
}

.type-radio {
  width: 22px;
  height: 22px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  margin: 0 auto 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.onu-type-card.selected .type-radio { border-color: var(--accent-primary); }

.radio-inner {
  width: 12px;
  height: 12px;
  background: var(--accent-primary);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.onu-type-card.selected .radio-inner { opacity: 1; }

.type-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--text-primary);
}

.type-specs { color: var(--text-muted); }

.type-badge {
  position: absolute;
  top: 0.4rem;
  right: 0.4rem;
  background: var(--accent-primary);
  color: white;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

/* ============================================
СТАТУС БАР
============================================ */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.85rem 1.25rem;
  margin-top: 0.85rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.status-text { display: flex; align-items: center; gap: 0.65rem; font-weight: 500; }
.status-label { color: var(--text-secondary); }

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-actions { display: flex; gap: 0.65rem; }

.btn-status {
  padding: 0.6rem 1.15rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-preview { background: var(--accent-yellow); color: #000; }
.btn-preview:hover:not(:disabled) { background: #e0a800; color: #000; transform: translateY(-1px); }
.btn-preview:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.btn-register { background: var(--accent-green); color: white; }
.btn-register:hover:not(:disabled) { background: #157347; transform: translateY(-1px); }
.btn-register:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

.btn-cancel { background: var(--accent-red); color: white; }
.btn-cancel:hover { background: #bb2d3b; }

.btn-status:disabled { opacity: 0.6; cursor: not-allowed; }

/* ============================================
ПРАВА ПАНЕЛЬ - CLI
============================================ */
.right-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.cli-header {
  display: flex;
  padding: 0.75rem;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
}

.cli-tabs { display: flex; gap: 0.4rem; }

.cli-tab {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 0.45rem 0.85rem;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.cli-tab.active {
  background: white;
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.cli-content { flex: 1; overflow-y: auto; padding: 0.85rem; }

.cli-section {
  margin-bottom: 1.25rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
}

.cli-section:last-child { border-bottom: none; }

.steps-list { display: flex; flex-direction: column; gap: 0; }

.step-item {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.step-item.active { opacity: 1; }

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-hover);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
  color: var(--text-secondary);
}

.step-item.active .step-number {
  background: var(--accent-green);
  border-color: var(--accent-green);
  color: white;
}

.step-text { color: var(--text-secondary); }

.step-item.active .step-text {
  color: var(--text-primary);
  font-weight: 500;
}

.step-connector {
  width: 2px;
  height: 20px;
  background: var(--border-color);
  margin-left: 13px;
}

/* ============================================
КАРТКА ПІДКАЗКИ
============================================ */
.quick-info-card {
  background: rgba(42, 63, 84, 0.05);
  border: 1px solid var(--accent-primary);
  border-radius: 8px;
  padding: 0.85rem;
  margin-top: 0.85rem;
}

.quick-info-title {
  font-weight: 600;
  color: var(--accent-primary);
  margin-bottom: 0.4rem;
}

.quick-info-text {
  color: var(--text-secondary);
  line-height: 1.5;
}

/* ============================================
МОДАЛЬНЕ ВІКНО
============================================ */
.modal-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  background: rgba(0, 0, 0, 0.5);
}

.modal-container {
  position: relative;
  background: #ffffff;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  pointer-events: auto;
  z-index: 2;
}

.modal-container.preview { border-top: 4px solid var(--accent-yellow); }
.modal-container.success { border-top: 4px solid var(--accent-green); }
.modal-container.error { border-top: 4px solid var(--accent-red); }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-hover);
}

.modal-title { margin: 0; font-weight: 600; color: var(--text-primary); }

.btn-close-modal {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-modal:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
  background: white;
}

/* ============================================
ПОПЕРЕДНІЙ ПЕРЕГЛЯД (PREVIEW SUMMARY)
============================================ */
.preview-summary {
  background: var(--bg-hover);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.85rem;
  margin-bottom: 0.85rem;
}

.summary-header {
  display: flex;
  align-items: center;
  font-weight: 600;
  margin-bottom: 0.85rem;
  color: var(--text-primary);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem 0.85rem;
}

.summary-item { display: flex; flex-direction: column; gap: 0.25rem; }

.summary-label {
  text-transform: uppercase;
  display: flex;
  align-items: center;
  letter-spacing: 0.5px;
}

.summary-value {
  font-weight: 600;
  color: var(--text-primary);
}

.font-monospace { font-family: 'Courier New', Consolas, monospace; }

/* ============================================
ПАНЕЛЬ АНАЛІЗУ КОНФІГУРАЦІЇ
============================================ */
.analysis-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
  margin-top: 0.85rem;
}

.analysis-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.65rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-secondary);
}

.analysis-badge.badge-success {
  background: rgba(25, 135, 84, 0.1);
  border-color: var(--accent-green);
  color: var(--accent-green);
}

/* ============================================
ВІДОБРАЖЕННЯ КОНФІГУРАЦІЇ (CODE BLOCK)
============================================ */
.config-wrapper {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
}

.config-title {
  font-weight: 600;
  color: var(--text-primary);
}

.config-actions { display: flex; gap: 0.4rem; }

.btn-copy-inline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-copy-inline:hover {
  background: white;
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.btn-copy-text { display: none; }

@media (min-width: 768px) { .btn-copy-text { display: inline; } }

.config-code {
  background: #1a1a1a;
  padding: 0.85rem;
  color: #00ff00;
  font-family: 'Courier New', Consolas, monospace;
  margin: 0;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}

/* ============================================
ФУТЕР МОДАЛЬНОГО ВІКНА
============================================ */
.modal-footer {
  display: flex;
  gap: 0.65rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color);
  justify-content: flex-end;
  background: var(--bg-hover);
}

.btn-modal {
  padding: 0.6rem 1.15rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-modal.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-modal.btn-secondary:hover { background: var(--bg-hover); }

.btn-modal.btn-primary { background: var(--accent-primary); color: white; }
.btn-modal.btn-primary:hover:not(:disabled) { background: #1a2838; }

.btn-modal.btn-warning { background: var(--accent-yellow); color: #000; }
.btn-modal.btn-warning:hover:not(:disabled) { background: #e0a800; color: #000; }

.btn-modal.btn-danger { background: var(--accent-red); color: white; }
.btn-modal.btn-danger:hover:not(:disabled) { background: #bb2d3b; }

.btn-modal.btn-success { background: black; color: white; }
.btn-modal.btn-success:hover:not(:disabled) { background: #157347; }

.btn-modal:disabled { opacity: 0.6; cursor: not-allowed; transform: none !important; }
.btn-modal:hover:not(:disabled) { transform: translateY(-1px); }

/* ============================================
СПАЛИВАЮЧІ ПОВІДОМЛЕННЯ (FLASH MESSAGES)
============================================ */
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.flash-list-leave-active { animation: slideOut 0.3s ease-in; }

@keyframes slideOut {
  to { transform: translateX(100%); opacity: 0; }
}

/* ============================================
BADGE ДЛЯ РЕКОМЕНДОВАНИХ VLAN
============================================ */
.badge-recommended-option {
  float: right;
  background: var(--accent-green);
  color: white;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  margin-left: 0.4rem;
}

option.fw-bold { font-weight: bold; }
option.text-primary { color: var(--accent-primary); }

/* ============================================
GRID SYSTEM (ROW/COL)
============================================ */
.row { display: flex; flex-wrap: wrap; margin: 0 -0.4rem; }
.col-5 { flex: 0 0 41.666667%; max-width: 41.666667%; padding: 0 0.4rem; }
.col-6 { flex: 0 0 50%; max-width: 50%; padding: 0 0.4rem; }
.col-7 { flex: 0 0 58.333367%; max-width: 58.333367%; padding: 0 0.4rem; }
.g-2 { gap: 0.4rem; }

/* ============================================
КНОПКА ПРИВʼЯЗКИ В БІЛЛІНГУ
============================================ */
.btn-outline-primary {
  background: transparent;
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
  transition: all 0.2s ease;
}

.btn-outline-primary:hover:not(.disabled) {
  background: var(--accent-primary);
  color: white;
}

.btn-outline-primary.disabled,
.btn-outline-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cursor-not-allowed { cursor: not-allowed; }
.spinning { display: inline-block; animation: spin 1s linear infinite; }
.border-top { border-top: 1px solid var(--border-color) !important; }
.border-secondary { border-color: var(--border-color) !important; }
.opacity-50 { opacity: 0.5; }
.d-flex { display: flex; }
.gap-2 { gap: 0.5rem; }

/* ============================================
АДАПТИВНІСТЬ (RESPONSIVE)
============================================ */
@media (max-width: 1200px) {
  .registration-grid { grid-template-columns: 1fr; }
  .right-panel { max-height: 600px; }
}

@media (max-width: 768px) {
  .olt-header { padding: 0.65rem 0.85rem !important; }
  .header-top { flex-direction: column; gap: 0.5rem; }
  .olt-selector { width: 100%; }
  .olt-selector-select { width: 100%; }
  .main-content { padding: 0.85rem; }
  .onu-types-grid { grid-template-columns: 1fr; }
  .status-bar { flex-direction: column; gap: 0.85rem; text-align: center; }
  .status-actions { width: 100%; flex-direction: column; }
  .btn-status { width: 100%; }
  .summary-grid { grid-template-columns: 1fr; }
  .analysis-bar { flex-direction: column; align-items: flex-start; }
  .modal-footer { flex-direction: column; }
  .btn-modal { width: 100%; }
  .onu-discovery-item { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
  .onu-actions { width: 100%; margin-left: 0; flex-direction: column; }
  .btn-select-onu,
  .btn-copy-sn { width: 100%; }
  .info-grid { grid-template-columns: 1fr; }
  .binding-actions { flex-direction: column; }
  .btn-binding,
  .btn-secondary { width: 100%; }
  .sn-input-row { flex-direction: column; }
  .btn-find-onu { width: 100%; justify-content: center; }
}

/* ============================================
СКРОЛБАР (CUSTOM SCROLLBAR)
============================================ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-hover); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ============================================
ДОПОМІЖНІ КЛАСИ
============================================ */
.d-flex { display: flex; }
.align-items-center { align-items: center; }
.align-items-start { align-items: flex-start; }
.justify-content-between { justify-content: space-between; }
.justify-content-center { justify-content: center; }
.flex-grow-1 { flex-grow: 1; }
.fw-bold { font-weight: 700 !important; }
.fw-semibold { font-weight: 600 !important; }
.mb-0 { margin-bottom: 0; }
.mb-3 { margin-bottom: 0.85rem; }
.mt-1 { margin-top: 0.25rem; }
.mt-3 { margin-top: 0.85rem; }
.me-1 { margin-right: 0.25rem; }
.me-2 { margin-right: 0.4rem; }
.me-3 { margin-right: 0.85rem; }
.ms-2 { margin-left: 0.4rem; }
.fs-4 { font-size: 1.5rem !important; }
.fs-5 { font-size: 1.25rem !important; }
.small { font-size: 0.9rem !important; }
.text-white { color: white !important; }
.text-muted { color: var(--text-muted) !important; }
.text-success { color: var(--accent-green) !important; }
.text-warning { color: #997404 !important; }
.text-danger { color: var(--accent-red) !important; }
.text-info { color: #0dcaf0 !important; }
.text-primary { color: var(--accent-primary) !important; }
.bg-success { background-color: var(--accent-green) !important; }
.bg-warning { background-color: var(--accent-yellow) !important; }
.fst-italic { font-style: italic; }
.text-center { text-align: center; }
.d-block { display: block; }
</style>