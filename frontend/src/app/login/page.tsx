'use client'

// =============================================
// 登入頁面 - Future Tech 設計
// =============================================

import { useState, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { GoogleLogin } from '@react-oauth/google'
import { motion } from 'framer-motion'
import { useAuth } from '@/components/providers/auth-provider'
import { useLocale } from '@/components/providers/locale-provider'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import {
  DataStreamBg,
  HoloCard,
  HoloButton,
  PageTransition,
} from '@/components/ui/future-tech'
import { Lock, Mail, Zap } from 'lucide-react'

export default function LoginPage() {
  const { login, loginGoogle } = useAuth()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const { t } = useLocale()

  const formSchema = useMemo(() => z.object({
    username: z.string().email({ message: t['login.email_invalid'] }),
    password: z.string().min(1, { message: t['login.password_required'] }),
  }), [t])

  // 開發模式測試帳號
  const devAccounts = useMemo(() => [
    { email: 'admin@dev.local', password: 'admin123', role: t['common.admin'], color: 'from-red-500 to-orange-500' },
    { email: 'operator@dev.local', password: 'operator123', role: t['common.operator'], color: 'from-blue-500 to-cyan-500' },
    { email: 'viewer@dev.local', password: 'viewer123', role: t['common.viewer'], color: 'from-green-500 to-emerald-500' },
  ], [t])

  // 檢測是否為開發環境
  const isDevelopment = typeof window !== 'undefined' && (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname.includes('192.168')
  )

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true)
    try {
      await login(values)
      toast({
        title: t['login.success'],
        description: t['login.welcome_desc'],
      })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t['login.failed'],
        description: error.message || t['login.invalid_credentials'],
      })
    } finally {
      setIsLoading(false)
    }
  }

  // 開發模式快速登入
  async function quickLogin(email: string, password: string, role: string) {
    setIsLoading(true)
    try {
      await login({ username: email, password })
      toast({
        title: t['login.dev_success'],
        description: t['login.dev_success_desc'].replace('{role}', role),
      })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t['login.dev_failed'],
        description: error.message || t['login.dev_failed_desc'],
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <PageTransition>
      <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* 背景效果 */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/50" />
        <DataStreamBg density="low" color="cyan" className="opacity-20" />

        {/* 裝飾元素 */}
        <div className="absolute top-20 left-20 w-72 h-72 bg-cyan-400/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl animate-float-delayed" />

        {/* 登入卡片 */}
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="relative z-10 w-full max-w-md mx-4"
        >
          <HoloCard glowColor="cyan" scanLine className="p-8">
            {/* Logo 區域 */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                className="inline-block mb-4"
              >
                <img
                  src="/images/GGJ_small_logo_001.ico"
                  alt="GoGoJap Logo"
                  className="w-[120px] h-[120px] object-contain"
                />
              </motion.div>
              <h1 className="text-2xl font-bold text-slate-800">{t['login.welcome_back']}</h1>
              <p className="text-slate-500 mt-1">{t['login.subtitle']}</p>
            </div>

            {/* 登入表單 */}
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-700">{t['login.email']}</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                          <Input
                            placeholder="name@example.com"
                            className="pl-10 bg-white/50 border-slate-200 focus:border-cyan-400 focus:ring-cyan-400/20"
                            {...field}
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-700">{t['login.password']}</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                          <Input
                            type="password"
                            placeholder="••••••••"
                            className="pl-10 bg-white/50 border-slate-200 focus:border-cyan-400 focus:ring-cyan-400/20"
                            {...field}
                          />
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <HoloButton
                  type="submit"
                  className="w-full"
                  disabled={isLoading}
                  loading={isLoading}
                >
                  {isLoading ? t['login.logging_in'] : t['login.login']}
                </HoloButton>
              </form>
            </Form>

            {/* 分隔線 */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white/80 backdrop-blur-sm px-3 text-slate-400">
                  {t['login.or_use']}
                </span>
              </div>
            </div>

            {/* Google 登入 */}
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={credentialResponse => {
                  if (credentialResponse.credential) {
                    loginGoogle(credentialResponse.credential)
                      .then(() => {
                        toast({
                          title: t['login.success'],
                          description: t['login.welcome_desc'],
                        })
                      })
                      .catch(err => {
                        toast({
                          variant: 'destructive',
                          title: t['login.google_failed'],
                          description: err.message
                        })
                      })
                  }
                }}
                onError={() => {
                  toast({
                    variant: 'destructive',
                    title: t['login.google_failed'],
                    description: t['login.google_error_desc']
                  })
                }}
                useOneTap
                width="350"
              />
            </div>

            {/* 開發模式快速登入 */}
            {isDevelopment && (
              <>
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-amber-200" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-amber-50 backdrop-blur-sm px-3 text-amber-600 font-medium flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      {t['login.dev_quick_login']}
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {devAccounts.map((account) => (
                    <motion.button
                      key={account.email}
                      type="button"
                      onClick={() => quickLogin(account.email, account.password, account.role)}
                      disabled={isLoading}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-full px-4 py-3 rounded-lg bg-gradient-to-r ${account.color} text-white font-medium text-sm
                                 shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                                 flex items-center justify-between`}
                    >
                      <span className="flex items-center gap-2">
                        <Zap className="w-4 h-4" />
                        {account.role}
                      </span>
                      <span className="text-xs opacity-75">{account.email}</span>
                    </motion.button>
                  ))}
                  <p className="text-xs text-amber-600 text-center mt-3 flex items-center justify-center gap-1">
                    <span>⚠️</span>
                    <span>{t['login.dev_only_hint']}</span>
                  </p>
                </div>
              </>
            )}

          </HoloCard>
        </motion.div>
      </div>
    </PageTransition>
  )
}
