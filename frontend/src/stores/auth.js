import axios from 'axios'
import { ref } from 'vue'

const ROLE_KEY = 'user_role'
const USER_KEY = 'user_name'
const USERNAME_KEY = 'auth_username'
const CAN_EDIT_KEY = 'can_edit_test'

export const userRole = ref(localStorage.getItem(ROLE_KEY) || 'viewer')
export const userName = ref(localStorage.getItem(USER_KEY) || '')
export const currentUsername = ref(localStorage.getItem(USERNAME_KEY) || '')
export const canEditTest = ref(localStorage.getItem(CAN_EDIT_KEY) === '1')

function applySession(data) {
  const role = (data?.role || 'viewer').toLowerCase()
  const isEditable = role === 'manager'
  const username = (data?.username || '').trim().toLowerCase()

  userRole.value = role
  userName.value = data?.display_name || username || ''
  currentUsername.value = username
  canEditTest.value = isEditable

  localStorage.setItem(ROLE_KEY, userRole.value)
  localStorage.setItem(USER_KEY, userName.value)
  localStorage.setItem(USERNAME_KEY, currentUsername.value)
  localStorage.setItem(CAN_EDIT_KEY, canEditTest.value ? '1' : '0')
  localStorage.removeItem('auth_groups')
}

function authHeaders() {
  return {
    'X-User-Name': currentUsername.value,
    'X-User-Role': userRole.value
  }
}

export async function login(username, password) {
  const key = (username || '').trim().toLowerCase()
  if (!key) return false

  try {
    const response = await axios.post('/api/personnel/login', {
      username: key,
      password
    })
    applySession(response.data)
    return true
  } catch {
    return false
  }
}

export async function refreshCurrentUser() {
  if (!currentUsername.value) return false
  try {
    const response = await axios.get('/api/personnel/me', {
      headers: authHeaders()
    })
    applySession(response.data)
    return true
  } catch {
    logout()
    return false
  }
}

export async function changePassword(oldPassword, newPassword) {
  if (!currentUsername.value) return false
  await axios.post(
    '/api/personnel/change-password',
    {
      old_password: oldPassword,
      new_password: newPassword
    },
    {
      headers: authHeaders()
    }
  )
  return true
}

export function logout() {
  userRole.value = 'viewer'
  userName.value = ''
  currentUsername.value = ''
  canEditTest.value = false

  localStorage.setItem(ROLE_KEY, 'viewer')
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.setItem(CAN_EDIT_KEY, '0')
  localStorage.removeItem('auth_groups')
}

export function canCreateOrEditTest() {
  return canEditTest.value
}

export function canCreateBug() {
  return canEditTest.value
}

export function canEditBug() {
  return canEditTest.value
}

export function canDeleteBug() {
  return canEditTest.value
}

export function isAdminAccount() {
  return String(currentUsername.value || '').trim().toLowerCase() === 'manager'
}

export function canViewAllPages() {
  return true
}

export function canManagePersonnelUsers() {
  return isAdminAccount()
}

export function canEditPersonnelProfile(targetUsername = '') {
  const normalizedTarget = String(targetUsername || '').trim().toLowerCase()
  if (!normalizedTarget) {
    return false
  }
  if (isAdminAccount()) {
    return true
  }
  return canEditTest.value && normalizedTarget === String(currentUsername.value || '').trim().toLowerCase()
}

export function canAccessAuditDashboard() {
  return isAdminAccount()
}
