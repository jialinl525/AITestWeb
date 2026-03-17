import axios from 'axios'
import { ref } from 'vue'

const ROLE_KEY = 'user_role'
const USER_KEY = 'user_name'
const USERNAME_KEY = 'auth_username'
const CAN_EDIT_KEY = 'can_edit_test'
const GROUPS_KEY = 'auth_groups'

export const userRole = ref(localStorage.getItem(ROLE_KEY) || 'viewer')
export const userName = ref(localStorage.getItem(USER_KEY) || '')
export const currentUsername = ref(localStorage.getItem(USERNAME_KEY) || '')
export const canEditTest = ref(localStorage.getItem(CAN_EDIT_KEY) === '1')
export const userGroups = ref([])

try {
  const raw = localStorage.getItem(GROUPS_KEY)
  userGroups.value = raw ? JSON.parse(raw) : []
} catch {
  userGroups.value = []
}

function applySession(data) {
  const role = (data?.role || 'viewer').toLowerCase()
  const isEditable = Boolean(data?.can_edit_test || role === 'manager')
  const username = (data?.username || '').trim().toLowerCase()

  userRole.value = role
  userName.value = data?.display_name || username || ''
  currentUsername.value = username
  canEditTest.value = isEditable
  userGroups.value = data?.groups || []

  localStorage.setItem(ROLE_KEY, userRole.value)
  localStorage.setItem(USER_KEY, userName.value)
  localStorage.setItem(USERNAME_KEY, currentUsername.value)
  localStorage.setItem(CAN_EDIT_KEY, canEditTest.value ? '1' : '0')
  localStorage.setItem(GROUPS_KEY, JSON.stringify(userGroups.value))
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
  userGroups.value = []

  localStorage.setItem(ROLE_KEY, 'viewer')
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.setItem(CAN_EDIT_KEY, '0')
  localStorage.removeItem(GROUPS_KEY)
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
