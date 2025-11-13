'use client'

import React, { useState } from 'react'
import { User, Heart, X, CheckCircle, Loader2, Calendar, Activity } from 'lucide-react'

interface UserOnboardingProps {
  onComplete: (userData: any) => void
  onSkip?: () => void
}

export default function UserOnboarding({ onComplete, onSkip }: UserOnboardingProps) {
  const [step, setStep] = useState(1)
  const [age, setAge] = useState('')
  const [interests, setInterests] = useState<string[]>([])
  const [medicalConditions, setMedicalConditions] = useState<string[]>([])
  const [customMedical, setCustomMedical] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const interestOptions = [
    'Skiing/Snowboarding',
    'Scuba Diving',
    'Hiking/Trekking',
    'Beach/Relaxation',
    'City Tours',
    'Adventure Sports',
    'Cultural Exploration',
    'Shopping',
    'Food & Dining',
    'Photography'
  ]

  const medicalConditionOptions = [
    'Diabetes',
    'High Blood Pressure',
    'Heart Condition',
    'Asthma',
    'None'
  ]

  const handleInterestToggle = (interest: string) => {
    setInterests(prev => 
      prev.includes(interest) 
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    )
  }

  const handleMedicalToggle = (condition: string) => {
    if (condition === 'None') {
      setMedicalConditions([])
    } else {
      setMedicalConditions(prev => 
        prev.includes(condition)
          ? prev.filter(c => c !== condition)
          : [...prev, condition].filter(c => c !== 'None')
      )
    }
  }

  const handleNext = () => {
    if (step === 1 && age) {
      setStep(2)
    } else if (step === 2 && interests.length > 0) {
      setStep(3)
    } else if (step === 3) {
      handleComplete()
    }
  }

  const handleComplete = async () => {
    setIsLoading(true)
    
    // Ensure age is a number, not a string
    const ageNum = typeof age === 'string' ? parseInt(age) : age
    const userData = {
      age: ageNum, // Ensure it's a number
      interests: interests,
      medical_conditions: [...medicalConditions, ...(customMedical ? [customMedical] : [])].filter(Boolean),
      created_at: new Date().toISOString()
    }

    console.log('💾 Saving user data:', userData)

    // Save to localStorage
    localStorage.setItem('wandersure_user_data', JSON.stringify(userData))
    localStorage.setItem('wandersure_onboarded', 'true')

    console.log('✅ User data saved to localStorage')

    setIsLoading(false)
    onComplete(userData)
  }

  // Always show if component is rendered (parent controls visibility)
  // Remove the early return that was preventing display

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[9999] flex items-center justify-center p-4" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}>
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl shadow-2xl border border-slate-700/50 max-w-md w-full p-8 space-y-6 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Tell Us About Yourself
          </h2>
          {/* Removed close button - user must complete onboarding */}
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
            <span className="font-medium">Step {step} of 3</span>
            <div className="flex-1 h-2 bg-slate-700/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 transition-all duration-300 rounded-full shadow-lg"
                style={{ width: `${(step / 3) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Step 1: Age */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Calendar className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                What is your age? <span className="text-red-400">*</span>
              </label>
            </div>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter your age"
              min="1"
              max="120"
              className="w-full px-4 py-3.5 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-lg text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
              disabled={isLoading}
            />
            <button
              onClick={handleNext}
              disabled={!age || isLoading}
              className="w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-3.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
            >
              Next
            </button>
          </div>
        )}

        {/* Step 2: Interests */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Activity className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                What are your travel interests? <span className="text-red-400">*</span>
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">Select all that apply</p>
            <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
              {interestOptions.map((interest) => (
                <button
                  key={interest}
                  onClick={() => handleInterestToggle(interest)}
                  className={`px-4 py-2.5 rounded-xl border-2 transition-all duration-200 text-sm font-medium ${
                    interests.includes(interest)
                      ? 'border-blue-500 bg-blue-500/20 text-blue-300 font-semibold shadow-lg shadow-blue-500/20'
                      : 'border-slate-600/50 hover:border-blue-400/50 text-slate-300 bg-slate-800/50 backdrop-blur-sm hover:bg-slate-700/50'
                  }`}
                  disabled={isLoading}
                >
                  {interest}
                </button>
              ))}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep(1)}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={interests.length === 0 || isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Medical Conditions */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Heart className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Do you have any medical conditions?
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">This helps us recommend the right coverage</p>
            <div className="space-y-2">
              {medicalConditionOptions.map((condition) => (
                <button
                  key={condition}
                  onClick={() => handleMedicalToggle(condition)}
                  className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 text-left font-medium ${
                    medicalConditions.includes(condition) || (condition === 'None' && medicalConditions.length === 0)
                      ? 'border-blue-500 bg-blue-500/20 text-blue-300 font-semibold shadow-lg shadow-blue-500/20'
                      : 'border-slate-600/50 hover:border-blue-400/50 text-slate-300 bg-slate-800/50 backdrop-blur-sm hover:bg-slate-700/50'
                  }`}
                  disabled={isLoading}
                >
                  {condition}
                </button>
              ))}
            </div>
            <div>
              <input
                type="text"
                value={customMedical}
                onChange={(e) => setCustomMedical(e.target.value)}
                placeholder="Or specify other conditions (optional)"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep(2)}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={isLoading}
                className="flex-1 bg-gradient-to-r from-emerald-600 via-green-600 to-teal-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-emerald-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 hover:scale-[1.02] disabled:hover:scale-100"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Complete Setup
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Removed skip button - user must complete onboarding */}
      </div>
    </div>
  )
}

