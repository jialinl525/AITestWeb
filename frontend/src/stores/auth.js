import { ref } from 'vue'

const ROLE_KEY = 'user_role'
const USER_KEY = 'user_name'
const USERS_KEY = 'auth_users'
const DEFAULT_PASSWORD = '123456'

// 默认用户：manager/123456
const defaultUsers = {
  manager: { password: DEFAULT_PASSWORD, role: 'manager', name: '管理员' }
}

export function getUsers() {
  try {
    const s = localStorage.getItem(USERS_KEY)
    return s ? { ...defaultUsers, ...JSON.parse(s) } : { ...defaultUsers }
  } catch {
    return { ...defaultUsers }
  }
}

function saveUsers(users) {
  const custom = {}
  for (const [k, v] of Object.entries(users)) {
    if (v.password !== defaultUsers[k]?.password || v.role !== defaultUsers[k]?.role) {
      custom[k] = v
    }
  }
  localStorage.setItem(USERS_KEY, JSON.stringify(custom))
}

const stored = localStorage.getItem(ROLE_KEY) || 'viewer'
const storedName = localStorage.getItem(USER_KEY) || ''

export const userRole = ref(stored)
export const userName = ref(storedName)
export const currentUsername = ref(localStorage.getItem('auth_username') || '')

export function setRole(role) {
  if (['manager', 'viewer'].includes(role)) {
    userRole.value = role
    localStorage.setItem(ROLE_KEY, role)
  }
}

export function login(username, password) {
  const users = getUsers()
  const key = (username || '').toLowerCase().trim()
  if (!key) return false
  const user = users[key]
  const pwd = user?.password ?? (key === 'manager' ? DEFAULT_PASSWORD : null)
  if (!pwd || password !== pwd) {
    return false
  }
  const r = user?.role || (key === 'manager' ? 'manager' : null)
  if (r && r === 'manager') {
    userRole.value = r
    userName.value = user?.name || '管理员'
    currentUsername.value = key
    localStorage.setItem(ROLE_KEY, r)
    localStorage.setItem(USER_KEY, userName.value)
    localStorage.setItem('auth_username', key)
    return true
  }
  return false
}

export function changePassword(newPassword) {
  if (!currentUsername.value) return false
  const users = getUsers()
  const key = currentUsername.value
  if (!users[key]) {
    users[key] = { password: DEFAULT_PASSWORD, role: userRole.value, name: userName.value }
  }
  users[key].password = newPassword
  users[key].name = userName.value
  users[key].role = userRole.value
  saveUsers(users)
  return true
}

export function logout() {
  userRole.value = 'viewer'
  userName.value = ''
  currentUsername.value = ''
  localStorage.setItem(ROLE_KEY, 'viewer')
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem('auth_username')
}

export function canCreateOrEditTest() {
  return userRole.value === 'manager'
}

export function canCreateBug() {
  return userRole.value === 'manager'
}

export function canEditBug() {
  return userRole.value === 'manager'
}

export function canDeleteBug() {
  return userRole.value === 'manager'
}
