<template>
  <el-container class="app-shell">
    <el-aside width="248px" class="app-sidebar">
      <div class="sidebar-panel">
        <div class="sidebar-brand">
          <div class="brand-mark">QA</div>
          <div>
            <div class="brand-title">测试管理驾驶舱</div>
            <div class="brand-subtitle">质量进度、缺陷风险与模型表现统一观测</div>
          </div>
        </div>

        <div class="sidebar-section-title">导航</div>
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
            <span>测试进度</span>
          </el-menu-item>
          <el-menu-item index="/bugs">
            <el-icon><Warning /></el-icon>
            <span>Bug追踪</span>
          </el-menu-item>
          <el-menu-item index="/kpi">
            <el-icon><DataAnalysis /></el-icon>
            <span>KPI表现</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <div class="glass-pill sidebar-pill">
            <span class="dot dot-green"></span>
            当前权限：{{ getRoleLabel(userRole) }}
          </div>
          <div class="sidebar-mini-card">
            <div class="sidebar-mini-card__label">工作台状态</div>
            <div class="sidebar-mini-card__value">Online</div>
            <p>面向测试管理、问题追踪与模型评估的统一业务视图。</p>
          </div>
        </div>
      </div>
    </el-aside>

    <!-- 登录对话框 -->
    <el-dialog v-model="showLoginDialog" title="登录" width="400px">
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="manager (管理员)" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="默认 123456" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLoginDialog = false">取消</el-button>
        <el-button type="primary" @click="handleLogin">登录</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="100px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>

    <el-container class="app-workspace">
      <el-header class="app-header">
        <div>
          <div class="header-title">质量运营总览</div>
          <div class="header-subtitle">以更清晰的层级快速洞察测试推进、缺陷状态与模型表现</div>
        </div>
        <div class="auth-area">
          <div class="user-pill">
            <span class="dot" :class="userRole === 'viewer' ? 'dot-gray' : 'dot-cyan'"></span>
            <div>
              <div class="user-name">{{ userName || '访客模式' }}</div>
              <div class="user-role">{{ getRoleLabel(userRole) }}</div>
            </div>
          </div>
          <template v-if="userRole === 'viewer'">
            <el-button size="small" type="primary" @click="showLoginDialog = true">登录管理端</el-button>
          </template>
          <template v-else>
            <el-button size="small" @click="showPasswordDialog = true">修改密码</el-button>
            <el-button size="small" @click="handleLogout">退出</el-button>
          </template>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Warning, DataAnalysis } from '@element-plus/icons-vue'
import { userRole, userName, login, logout, changePassword, getUsers } from './stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const showLoginDialog = ref(false)
const showPasswordDialog = ref(false)
const loginForm = ref({ username: 'manager', password: '123456' })
const passwordForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/test-progress')) return '/test-progress'
  if (p.startsWith('/bugs')) return '/bugs'
  if (p.startsWith('/kpi')) return '/kpi'
  return p
})

const getRoleLabel = (role) => {
  const map = { manager: '管理员', viewer: '查看者' }
  return map[role] || role
}

const handleLogin = () => {
  const ok = login(loginForm.value.username, loginForm.value.password)
  if (ok) {
    showLoginDialog.value = false
    loginForm.value = { username: 'manager', password: '123456' }
    ElMessage.success('登录成功')
  } else {
    ElMessage.error('用户名或密码错误')
  }
}

const handleChangePassword = () => {
  const { oldPassword, newPassword, confirmPassword } = passwordForm.value
  if (!newPassword || newPassword.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (newPassword !== confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  const users = getUsers()
  const key = localStorage.getItem('auth_username') || ''
  const currentPwd = users[key]?.password ?? '123456'
  if (oldPassword !== currentPwd) {
    ElMessage.error('当前密码错误')
    return
  }
  changePassword(newPassword)
  showPasswordDialog.value = false
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  ElMessage.success('密码修改成功')
}

const handleLogout = () => {
  logout()
}
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
  border-right: 1px solid rgba(148, 163, 184, 0.08);
  background: rgba(2, 8, 23, 0.34);
  backdrop-filter: blur(14px);
}

.sidebar-panel {
  display: flex;
  flex-direction: column;
  gap: 22px;
  height: 100%;
  min-height: calc(100vh - 36px);
  padding: 18px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 28px;
  background: linear-gradient(180deg, rgba(5, 11, 21, 0.96), rgba(8, 15, 28, 0.92));
  box-shadow: 0 24px 60px rgba(2, 8, 23, 0.32);
}

.sidebar-brand {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
}

.sidebar-section-title {
  padding: 0 6px;
  color: rgba(148, 163, 184, 0.78);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 16px;
  background: linear-gradient(135deg, #22d3ee, #818cf8);
  color: #fff;
  font-weight: 800;
  letter-spacing: 0.06em;
}

.brand-title {
  font-size: 17px;
  font-weight: 700;
  color: #f8fafc;
}

.brand-subtitle {
  margin-top: 4px;
  color: rgba(226, 232, 240, 0.68);
  font-size: 12px;
  line-height: 1.5;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  overflow: hidden;
}

.sidebar-menu .el-menu-item {
  position: relative;
  display: flex;
  align-items: center;
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

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.sidebar-pill {
  width: fit-content;
}

.sidebar-mini-card {
  padding: 16px;
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.03));
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.sidebar-mini-card__label {
  color: rgba(148, 163, 184, 0.82);
  font-size: 12px;
}

.sidebar-mini-card__value {
  margin-top: 8px;
  color: #5eead4;
  font-size: 20px;
  font-weight: 700;
}

.sidebar-mini-card p {
  margin: 0;
  margin-top: 10px;
  color: rgba(148, 163, 184, 0.88);
  font-size: 12px;
  line-height: 1.6;
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
