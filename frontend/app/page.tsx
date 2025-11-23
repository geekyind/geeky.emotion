'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Heart, Shield, Users, Lock } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="mb-6">
            <Heart className="w-16 h-16 mx-auto text-primary-blue" />
          </div>
          
          <h1 className="text-5xl font-semibold text-neutral-charcoal mb-6">
            Welcome to your safe space
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Share your thoughts and feelings anonymously. Connect with others
            who understand. Get support from caring professionals.
          </p>
          
          <div className="flex gap-4 justify-center">
            <Link href="/auth/signin">
              <button className="btn-primary px-8 py-4 text-lg">
                Sign In
              </button>
            </Link>
            
            <Link href="/auth/signup">
              <button className="btn-secondary px-8 py-4 text-lg">
                Get Started
              </button>
            </Link>
          </div>
          
          <div className="mt-8 flex items-center justify-center gap-2 text-sm text-gray-500">
            <Lock className="w-4 h-4" />
            <span>Your identity is protected and never shared</span>
          </div>
        </motion.div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-semibold text-center mb-12">
            Why Lore Emotion?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="Privacy First"
              description="All posts are anonymized by default. Your identity is protected with military-grade encryption."
            />
            
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Community Support"
              description="Connect with others who share similar experiences. You're not alone in your journey."
            />
            
            <FeatureCard
              icon={<Heart className="w-8 h-8" />}
              title="Professional Care"
              description="Access support from trained mental health professionals available 24/7."
            />
          </div>
        </div>
      </div>

      {/* Safety Badge */}
      <div className="container mx-auto px-4 py-16">
        <div className="card max-w-2xl mx-auto text-center">
          <h3 className="text-2xl font-semibold mb-4">Your Safety Matters</h3>
          <div className="space-y-2 text-gray-600">
            <p>✓ Moderated by professionals</p>
            <p>✓ Community guidelines enforced</p>
            <p>✓ 24/7 crisis support available</p>
          </div>
        </div>
      </div>

      {/* Crisis Resources */}
      <div className="bg-accent-mint bg-opacity-20 py-12">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-xl font-semibold mb-4">
            Need immediate help?
          </h3>
          <p className="text-gray-600 mb-4">
            If you're in crisis, please reach out to these resources:
          </p>
          <div className="space-y-2">
            <p className="font-semibold">
              US: <a href="tel:988" className="text-primary-blue hover:underline">988</a> (Suicide & Crisis Lifeline)
            </p>
            <p>
              Text <strong>HOME</strong> to <strong>741741</strong> (Crisis Text Line)
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

function FeatureCard({ 
  icon, 
  title, 
  description 
}: { 
  icon: React.ReactNode
  title: string
  description: string 
}) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="card text-center"
    >
      <div className="text-primary-blue mb-4 flex justify-center">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  )
}
