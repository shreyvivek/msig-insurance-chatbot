'use client'

import React, { useState } from 'react'
import { Instagram, Mail, X, CheckCircle, Loader2, AlertCircle } from 'lucide-react'

interface ProfileConnectProps {
  onConnected: (profileData: any) => void
  onSkip?: () => void
}

export default function ProfileConnect({ onConnected, onSkip }: ProfileConnectProps) {
  const [instagramUsername, setInstagramUsername] = useState('')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profileData, setProfileData] = useState<any>(null)
  const [showConsent, setShowConsent] = useState(true)

  const handleFetch = async () => {
    if (!instagramUsername.trim()) {
      setError('Instagram username is required')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/v1/user/fetch-profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          instagram_username: instagramUsername.trim().replace('@', ''),
          email: email.trim() || undefined
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch profile')
      }

      setProfileData(data)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Error fetching profile')
      setIsLoading(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleConfirm = () => {
    if (profileData) {
      onConnected(profileData)
    }
  }

  if (!showConsent) {
    if (profileData) {
      return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl shadow-2xl border border-slate-700/50 max-w-md w-full p-8 space-y-6 backdrop-blur-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Profile Analysis</h3>
              <button onClick={() => setShowConsent(true)} className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-all duration-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Instagram className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-gray-900">@{profileData.profile_data?.instagram_username}</span>
                </div>
                {profileData.profile_data?.instagram_bio && (
                  <p className="text-sm text-gray-600">{profileData.profile_data.instagram_bio}</p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-blue-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Adventure Score</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {(profileData.profile_data?.adventurous_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Tier</p>
                  <p className="text-lg font-bold text-green-600 capitalize">
                    {profileData.tier_recommendation?.tier || 'free'}
                  </p>
                </div>
              </div>

              {profileData.profile_data?.likely_activities?.length > 0 && (
                <div>
                  <p className="text-sm font-semibold text-gray-700 mb-2">Detected Activities:</p>
                  <div className="flex flex-wrap gap-2">
                    {profileData.profile_data.likely_activities.slice(0, 6).map((activity: string, idx: number) => (
                      <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">
                        {activity}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-2 space-y-2">
                <button
                  onClick={handleConfirm}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-2 rounded-lg font-semibold hover:shadow-lg transition-shadow"
                >
                  Use This Profile
                </button>
                <button
                  onClick={() => {
                    setShowConsent(true)
                    setProfileData(null)
                  }}
                  className="w-full text-gray-600 py-2 rounded-lg font-medium hover:bg-gray-50"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return null
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl shadow-2xl border border-slate-700/50 max-w-md w-full p-8 space-y-6 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Connect Your Profile
          </h2>
          {onSkip && (
            <button onClick={onSkip} className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-lg transition-all duration-200">
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        <p className="text-slate-400 text-sm leading-relaxed">
          We'll analyze your public Instagram profile to personalize your travel insurance recommendations.
        </p>

        <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 backdrop-blur-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-slate-300 leading-relaxed">
              <p className="font-semibold mb-1.5 text-blue-300">Privacy Note:</p>
              <p>We only access publicly available data. Private profiles cannot be analyzed. Your data is stored securely and you can delete it anytime.</p>
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-200 mb-2.5">
              Instagram Username <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <Instagram className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={instagramUsername}
                onChange={(e) => setInstagramUsername(e.target.value)}
                placeholder="@username or username"
                className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-200 mb-2.5">
              Email (Optional)
            </label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                className="w-full pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl text-slate-100 placeholder-slate-500 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3 backdrop-blur-sm">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleFetch}
              disabled={isLoading || !instagramUsername.trim()}
              className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:scale-[1.02] disabled:hover:scale-100"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Instagram className="w-5 h-5" />
                  Fetch Profile
                </>
              )}
            </button>
            {onSkip && (
              <button
                onClick={onSkip}
                disabled={isLoading}
                className="px-5 py-3 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 disabled:opacity-50 transition-all duration-200"
              >
                Skip
              </button>
            )}
          </div>
        </div>

        {profileData && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => setShowConsent(false)}
              className="w-full bg-green-50 text-green-700 py-2 rounded-lg font-semibold hover:bg-green-100 transition-colors flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              View Analysis Results
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

