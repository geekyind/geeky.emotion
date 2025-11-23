'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Heart, MessageCircle, TrendingUp, Settings, LogOut } from 'lucide-react'
import { useAuthStore } from '@/lib/store'
import { apiClient } from '@/lib/api'
import { authService } from '@/lib/auth'

export default function DashboardPage() {
  const router = useRouter()
  const { user, clearAuth } = useAuthStore()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check authentication
    const checkAuth = async () => {
      try {
        const session = await authService.getSession()
        if (!session) {
          router.push('/auth/signin')
          return
        }
        setLoading(false)
      } catch (error) {
        router.push('/auth/signin')
      }
    }

    checkAuth()
  }, [router])

  const handleSignOut = () => {
    authService.signOut()
    clearAuth()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Heart className="w-12 h-12 text-primary-blue mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading your safe space...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-neutral-gray">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Heart className="w-6 h-6 text-primary-blue" />
              <span className="font-semibold text-lg">Lore Emotion</span>
            </div>
            
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 text-gray-600 hover:text-primary-blue transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-semibold mb-2">
            Welcome back
          </h1>
          <p className="text-gray-600 mb-8">
            Your anonymous ID: <code className="px-2 py-1 bg-neutral-gray rounded text-sm">{user?.anonymous_id || 'Loading...'}</code>
          </p>

          {/* Wellness Snapshot */}
          <div className="card mb-8">
            <h2 className="text-xl font-semibold mb-4">Your Wellness Snapshot</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <StatCard
                icon={<MessageCircle className="w-6 h-6" />}
                label="Posts Shared"
                value="0"
              />
              <StatCard
                icon={<Heart className="w-6 h-6" />}
                label="Support Received"
                value="0"
              />
              <StatCard
                icon={<TrendingUp className="w-6 h-6" />}
                label="Day Streak"
                value="1"
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid md:grid-cols-2 gap-6">
            <ActionCard
              title="Share Your Thoughts"
              description="Express what's on your mind in a safe, anonymous space"
              buttonText="Create Post"
              onClick={() => router.push('/dashboard/new-post')}
              icon={<MessageCircle className="w-8 h-8 text-primary-blue" />}
            />

            <ActionCard
              title="Browse Community"
              description="Find others sharing similar experiences and offer support"
              buttonText="Explore"
              onClick={() => router.push('/dashboard/feed')}
              icon={<Heart className="w-8 h-8 text-accent-mint" />}
            />
          </div>

          {/* Settings Link */}
          <div className="mt-8 text-center">
            <button
              onClick={() => router.push('/dashboard/settings')}
              className="text-gray-600 hover:text-primary-blue transition-colors inline-flex items-center gap-2"
            >
              <Settings className="w-5 h-5" />
              <span>Privacy & Settings</span>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="p-4 bg-neutral-white rounded-lg border border-neutral-gray">
      <div className="flex items-center gap-3 mb-2">
        <div className="text-primary-blue">{icon}</div>
        <span className="text-sm text-gray-600">{label}</span>
      </div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  )
}

function ActionCard({
  title,
  description,
  buttonText,
  onClick,
  icon,
}: {
  title: string
  description: string
  buttonText: string
  onClick: () => void
  icon: React.ReactNode
}) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="card"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <button onClick={onClick} className="btn-primary">
        {buttonText}
      </button>
    </motion.div>
  )
}
