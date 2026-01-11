'use client'

// =============================================
// 登入頁面 - Future Tech 設計
// =============================================

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { GoogleLogin } from '@react-oauth/google'
import { motion } from 'framer-motion'
import { useAuth } from '@/components/providers/auth-provider'
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
import { Sparkles, Lock, Mail } from 'lucide-react'

const formSchema = z.object({
  username: z.string().email({ message: '請輸入有效的電子郵件地址' }),
  password: z.string().min(1, { message: '請輸入密碼' }),
})

export default function LoginPage() {
  const { login, loginGoogle } = useAuth()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)

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
        title: '登入成功',
        description: '歡迎回來！',
      })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: '登入失敗',
        description: error.message || '無效的電子郵件或密碼',
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
                  className="w-20 h-20 object-contain"
                />
              </motion.div>
              <h1 className="text-2xl font-bold text-slate-800">歡迎回來</h1>
              <p className="text-slate-500 mt-1">登入 GoGoJap AI 營運系統</p>
            </div>

            {/* 登入表單 */}
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-700">電子郵件</FormLabel>
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
                      <FormLabel className="text-slate-700">密碼</FormLabel>
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
                  {isLoading ? '登入中...' : '登入'}
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
                  或使用以下方式
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
                          title: '登入成功',
                          description: '歡迎回來！',
                        })
                      })
                      .catch(err => {
                        toast({
                          variant: 'destructive',
                          title: 'Google 登入失敗',
                          description: err.message
                        })
                      })
                  }
                }}
                onError={() => {
                  toast({
                    variant: 'destructive',
                    title: 'Google 登入失敗',
                    description: '登入視窗已關閉或發生錯誤'
                  })
                }}
                useOneTap
                width="350"
              />
            </div>

            {/* 底部裝飾 */}
            <div className="mt-8 pt-6 border-t border-slate-100 text-center">
              <p className="text-xs text-slate-400 flex items-center justify-center gap-1">
                <Sparkles className="w-3 h-3" />
                由 AI 驅動的智能營運平台
              </p>
            </div>
          </HoloCard>
        </motion.div>
      </div>
    </PageTransition>
  )
}
