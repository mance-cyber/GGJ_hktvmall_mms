// =============================================
// PermissionCheck Hook
// =============================================

import { useAuth } from '@/components/providers/auth-provider'
import { useMemo, useCallback } from 'react'

// PermissionConstant定義
export const PERMISSIONS = {
  // SystemManagement
  SYSTEM_SETTINGS_READ: 'system:settings:read',
  SYSTEM_SETTINGS_WRITE: 'system:settings:write',
  SYSTEM_USERS_READ: 'system:users:read',
  SYSTEM_USERS_WRITE: 'system:users:write',
  SYSTEM_USERS_DELETE: 'system:users:delete',

  // CompetitorMonitor
  COMPETITORS_READ: 'competitors:read',
  COMPETITORS_WRITE: 'competitors:write',
  COMPETITORS_DELETE: 'competitors:delete',

  // Price調整
  PRICES_READ: 'prices:read',
  PRICES_WRITE: 'prices:write',
  PRICES_APPROVE: 'prices:approve',

  // 訂單Management
  ORDERS_READ: 'orders:read',
  ORDERS_WRITE: 'orders:write',

  // AI Agent
  AGENT_READ: 'agent:read',
  AGENT_EXECUTE: 'agent:execute',
  AGENT_ADMIN: 'agent:admin',

  // 報表
  REPORTS_READ: 'reports:read',
  REPORTS_EXPORT: 'reports:export',

  // Notification
  NOTIFICATIONS_READ: 'notifications:read',
  NOTIFICATIONS_WRITE: 'notifications:write',
  NOTIFICATIONS_SETTINGS: 'notifications:settings',
} as const

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS]

// Role定義
export type UserRole = 'admin' | 'operator' | 'viewer'

export interface UsePermissionsReturn {
  // 當前用戶Role
  role: UserRole | null
  // 當前用戶PermissionList
  permissions: string[]
  // Check單個Permission
  hasPermission: (permission: string) => boolean
  // Check多個Permission（All滿足）
  hasAllPermissions: (...permissions: string[]) => boolean
  // Check多個Permission（任一滿足）
  hasAnyPermission: (...permissions: string[]) => boolean
  // RoleCheck
  isAdmin: boolean
  isOperator: boolean
  isViewer: boolean
  // 便捷Check
  canManageSystem: boolean
  canManageUsers: boolean
  canWriteCompetitors: boolean
  canDeleteCompetitors: boolean
  canApprovePrice: boolean
  canWriteOrders: boolean
  canExecuteAgent: boolean
  canExportReports: boolean
  canManageNotifications: boolean
}

export function usePermissions(): UsePermissionsReturn {
  const { user } = useAuth()

  const role = user?.role ?? null
  const permissions = user?.permissions ?? []

  const hasPermission = useCallback(
    (permission: string): boolean => {
      return permissions.includes(permission)
    },
    [permissions]
  )

  const hasAllPermissions = useCallback(
    (...perms: string[]): boolean => {
      return perms.every((p) => permissions.includes(p))
    },
    [permissions]
  )

  const hasAnyPermission = useCallback(
    (...perms: string[]): boolean => {
      return perms.some((p) => permissions.includes(p))
    },
    [permissions]
  )

  const derived = useMemo(() => {
    return {
      isAdmin: role === 'admin',
      isOperator: role === 'operator',
      isViewer: role === 'viewer',
      canManageSystem: permissions.includes(PERMISSIONS.SYSTEM_SETTINGS_WRITE),
      canManageUsers: permissions.includes(PERMISSIONS.SYSTEM_USERS_WRITE),
      canWriteCompetitors: permissions.includes(PERMISSIONS.COMPETITORS_WRITE),
      canDeleteCompetitors: permissions.includes(PERMISSIONS.COMPETITORS_DELETE),
      canApprovePrice: permissions.includes(PERMISSIONS.PRICES_APPROVE),
      canWriteOrders: permissions.includes(PERMISSIONS.ORDERS_WRITE),
      canExecuteAgent: permissions.includes(PERMISSIONS.AGENT_EXECUTE),
      canExportReports: permissions.includes(PERMISSIONS.REPORTS_EXPORT),
      canManageNotifications: permissions.includes(PERMISSIONS.NOTIFICATIONS_SETTINGS),
    }
  }, [role, permissions])

  return {
    role,
    permissions,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    ...derived,
  }
}

// =============================================
// Permission門控組items
// =============================================

interface PermissionGateProps {
  children: React.ReactNode
  permission?: string
  permissions?: string[]
  requireAll?: boolean
  fallback?: React.ReactNode
}

export function PermissionGate({
  children,
  permission,
  permissions: requiredPermissions,
  requireAll = true,
  fallback = null,
}: PermissionGateProps) {
  const { hasPermission, hasAllPermissions, hasAnyPermission } = usePermissions()

  let hasAccess = false

  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (requiredPermissions && requiredPermissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(...requiredPermissions)
      : hasAnyPermission(...requiredPermissions)
  } else {
    hasAccess = true
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>
}

// =============================================
// Role門控組items
// =============================================

interface RoleGateProps {
  children: React.ReactNode
  roles: UserRole[]
  fallback?: React.ReactNode
}

export function RoleGate({ children, roles, fallback = null }: RoleGateProps) {
  const { role } = usePermissions()

  if (!role || !roles.includes(role)) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
