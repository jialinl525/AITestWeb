<template>
  <el-container class="app-shell">
    <el-aside width="248px" class="app-sidebar">
      <div class="sidebar-panel">
        <div class="sidebar-brand">
          <img :src="voiceAiLogo" alt="VoiceAI logo" class="brand-logo" />
          <div class="brand-copy">
            <div class="brand-subtitle">{{ LT.brandSubtitle }}</div>
          </div>
        </div>

        <div class="sidebar-section-title">{{ LT.navigation }}</div>
        <el-menu
          :default-active="activeMenu"
          router
          class="sidebar-menu"
          background-color="transparent"
          text-color="rgba(226, 232, 240, 0.78)"
          active-text-color="#ffffff"
        >
          <el-menu-item index="/test-progress">
            <el-icon><Document /></el-icon>
            <span>{{ LT.menu.testProgress }}</span>
          </el-menu-item>
          <el-menu-item v-if="canViewAllMenu" index="/work-tasks">
            <el-icon><Document /></el-icon>
            <span>{{ LT.menu.workTasks }}</span>
          </el-menu-item>
          <el-menu-item v-if="canViewAllMenu" index="/bugs">
            <el-icon><Warning /></el-icon>
            <span>{{ LT.menu.bugs }}</span>
          </el-menu-item>
          <el-menu-item v-if="canViewAllMenu" index="/personnel">
            <el-icon><UserFilled /></el-icon>
            <span>{{ LT.menu.personnel }}</span>
          </el-menu-item>
          <el-menu-item index="/kpi">
            <el-icon><DataAnalysis /></el-icon>
            <span>{{ LT.menu.kpi }}</span>
          </el-menu-item>
        </el-menu>
      </div>
    </el-aside>

    <!-- Login Dialog -->
    <el-dialog v-model="showLoginDialog" :title="BT.login" width="400px">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item :label="LT.form.username">
          <el-input v-model="loginForm.username" :placeholder="DT.login.usernamePlaceholder" />
        </el-form-item>
        <el-form-item :label="LT.form.password">
          <el-input v-model="loginForm.password" type="password" :placeholder="DT.login.passwordPlaceholder" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLoginDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" @click="handleLogin">{{ BT.login }}</el-button>
      </template>
    </el-dialog>

    <!-- Change Password Dialog -->
    <el-dialog v-model="showPasswordDialog" :title="BT.changePassword" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item :label="LT.form.currentPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password :placeholder="DT.password.currentPlaceholder" />
        </el-form-item>
        <el-form-item :label="LT.form.newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password :placeholder="DT.password.newPlaceholder" />
        </el-form-item>
        <el-form-item :label="LT.form.confirmNewPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password :placeholder="DT.password.confirmPlaceholder" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">{{ BTCommon.cancel }}</el-button>
        <el-button type="primary" @click="handleChangePassword">{{ BTCommon.confirm }}</el-button>
      </template>
    </el-dialog>

    <el-container class="app-workspace">
      <el-header class="app-header">
        <div>
          <div class="header-title">{{ LT.headerTitle }}</div>
          <div class="header-subtitle">{{ LT.headerSubtitle }}</div>
        </div>
        <div class="auth-area">
          <div class="user-pill">
            <span class="dot" :class="canEditTest ? 'dot-cyan' : 'dot-gray'"></span>
            <div>
              <div class="user-name">{{ userName || LT.guestMode }}</div>
              <div class="user-role">{{ getRoleLabel(userRole) }} / {{ canEditTest ? LT.canEditTests : LT.readOnly }}</div>
            </div>
          </div>
          <div class="auth-actions">
            <el-button
              v-if="!isLoggedIn"
              size="small"
              class="auth-btn auth-btn--main"
              @click="showLoginDialog = true"
            >
              {{ BT.login }}
            </el-button>
            <template v-else>
              <el-button size="small" class="auth-btn" @click="showPasswordDialog = true">{{ BT.changePassword }}</el-button>
              <el-button size="small" class="auth-btn" @click="handleLogout">{{ BT.logout }}</el-button>
            </template>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Warning, DataAnalysis, UserFilled } from '@element-plus/icons-vue'
import voiceAiLogo from './assets/voiceai-logo.svg'
import { LabelText } from './texts/LabelText'
import { ButtonText } from './texts/ButtonText'
import { DescriptionText } from './texts/DescriptionText'
import {
  userRole,
  userName,
  canEditTest,
  currentUsername,
  canViewAllPages,
  isInternalUser,
  login,
  logout,
  changePassword,
  refreshCurrentUser
} from './stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const showLoginDialog = ref(false)
const showPasswordDialog = ref(false)
const loginForm = ref({ username: 'Internal', password: '' })
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const LT = LabelText.app
const BT = ButtonText.app
const BTCommon = ButtonText.common
const DT = DescriptionText.app

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/test-progress')) return '/test-progress'
  if (p.startsWith('/bugs')) return '/bugs'
  if (p.startsWith('/kpi')) return '/kpi'
  if (p.startsWith('/personnel')) return '/personnel'
  if (p.startsWith('/work-tasks')) return '/work-tasks'
  return p
})

const isLoggedIn = computed(() => Boolean(currentUsername.value))
const canViewAllMenu = computed(() => canViewAllPages())

const getRoleLabel = (role) => {
  const map = LT.roleMap
  if (isInternalUser()) return 'Internal'
  return map[role] || role
}

const handleLogin = async () => {
  const ok = await login(loginForm.value.username, loginForm.value.password)
  if (ok) {
    showLoginDialog.value = false
    loginForm.value = { username: 'Internal', password: '' }
    ElMessage.success(DT.toast.loginSuccess)
  } else {
    ElMessage.error(DT.toast.loginFailed)
  }
}

const handleChangePassword = async () => {
  const { oldPassword, newPassword, confirmPassword } = passwordForm.value
  if (!newPassword || newPassword.length < 6) {
    ElMessage.warning(DT.toast.newPasswordTooShort)
    return
  }
  if (newPassword !== confirmPassword) {
    ElMessage.warning(DT.toast.newPasswordMismatch)
    return
  }
  try {
    await changePassword(oldPassword, newPassword)
    showPasswordDialog.value = false
    passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
    ElMessage.success(DT.toast.passwordChangedSuccess)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || DT.toast.passwordChangedFailed)
  }
}

const handleLogout = () => {
  logout()
}

onMounted(() => {
  refreshCurrentUser()
})
</script>

<style>
* {
  box-sizing: border-box;
}

#app {
  width: 100%;
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
}

.app-sidebar {
  flex: 0 0 248px;
  padding: 18px;
  border-right: none;
  background: rgba(2, 8, 23, 0.34);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

.sidebar-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 22px;
  height: 100%;
  min-height: 100%;
  width: 100%;
  padding: 18px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(5, 11, 21, 0.96), rgba(8, 15, 28, 0.92));
  box-shadow: 0 24px 60px rgba(2, 8, 23, 0.32);
}

.sidebar-panel > * {
  width: 100%;
}

.sidebar-brand {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  text-align: center;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
}

.brand-logo {
  display: block;
  width: 100%;
  max-width: 188px;
  height: auto;
  margin: 0 auto;
  filter: drop-shadow(0 8px 24px rgba(30, 128, 189, 0.26));
}

.brand-copy {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar-section-title {
  padding: 0 6px;
  color: rgba(148, 163, 184, 0.78);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-align: left;
  text-transform: uppercase;
}

.brand-title {
  font-size: 18px;
  font-weight: 700;
  color: #d8f3ff;
  letter-spacing: 0.03em;
}

.brand-subtitle {
  margin-top: 4px;
  color: rgba(186, 228, 249, 0.75);
  font-size: 12px;
  line-height: 1.5;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  background: transparent;
  overflow: hidden;
}

.sidebar-menu.el-menu {
  border-right: none !important;
}

.sidebar-menu .el-menu-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  height: 52px;
  margin-bottom: 10px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 16px;
  color: rgba(226, 232, 240, 0.78);
  transition: all 0.22s ease;
}

.sidebar-menu .el-menu-item .el-icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
}

.sidebar-menu .el-menu-item:hover {
  border-color: rgba(96, 165, 250, 0.18);
  background: rgba(96, 165, 250, 0.08);
  color: #fff;
  transform: translateX(2px);
}

.sidebar-menu .el-menu-item.is-active {
  border-color: rgba(96, 165, 250, 0.2);
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.24), rgba(129, 140, 248, 0.24));
  color: #fff;
}

.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  bottom: 10px;
  width: 3px;
  border-radius: 999px;
  background: linear-gradient(180deg, #22d3ee, #818cf8);
}

.sidebar-menu .el-menu-item.is-active .el-icon {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.app-workspace {
  min-width: 0;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 88px;
  padding: 20px 28px 12px;
  background: transparent;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  color: #f8fafc;
}

.header-subtitle {
  margin-top: 6px;
  color: rgba(226, 232, 240, 0.68);
  font-size: 13px;
}

.auth-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.auth-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
}

.auth-btn {
  min-width: 76px;
  border-radius: 10px;
  border: 1px solid rgba(226, 232, 240, 0.78);
  background: rgba(241, 245, 249, 0.92);
  color: #0f172a !important;
}

.auth-btn:hover {
  border-color: rgba(203, 213, 225, 1);
  background: rgba(226, 232, 240, 0.96);
  color: #0f172a !important;
}

.auth-btn :deep(span) {
  color: inherit;
}

.auth-btn--main {
  border-color: rgba(94, 234, 212, 0.5);
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.24), rgba(16, 185, 129, 0.26));
  color: #ecfeff;
}

.auth-btn--main:hover {
  border-color: rgba(34, 211, 238, 0.66);
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.34), rgba(16, 185, 129, 0.36));
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(255, 255, 255, 0.04);
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #f8fafc;
}

.user-role {
  margin-top: 2px;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.82);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #94a3b8;
  box-shadow: 0 0 16px currentColor;
}

.dot-green {
  color: #34d399;
  background: #34d399;
}

.dot-cyan {
  color: #22d3ee;
  background: #22d3ee;
}

.dot-gray {
  color: #94a3b8;
  background: #94a3b8;
}

.app-main {
  padding: 8px 28px 28px;
  background: transparent;
}

@media (max-width: 980px) {
  .app-sidebar {
    width: 220px !important;
    flex-basis: 220px;
    padding: 14px;
  }

  .sidebar-panel {
    min-height: calc(100vh - 28px);
    padding: 16px;
  }

  .app-header {
    height: auto;
    padding-top: 18px;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
