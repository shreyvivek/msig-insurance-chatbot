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
    
    const userData = {
      age: parseInt(age),
      interests: interests,
      medical_conditions: [...medicalConditions, ...(customMedical ? [customMedical] : [])].filter(Boolean),
      created_at: new Date().toISOString()
    }

    // Save to localStorage
    localStorage.setItem('wandersure_user_data', JSON.stringify(userData))
    localStorage.setItem('wandersure_onboarded', 'true')

    setIsLoading(false)
    onComplete(userData)
  }

  if (!onSkip && !localStorage.getItem('wandersure_onboarded')) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Tell Us About Yourself
          </h2>
          {onSkip && (
            <button onClick={onSkip} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
            <span>Step {step} of 3</span>
            <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-300"
                style={{ width: `${(step / 3) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Step 1: Age */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-700 mb-4">
              <Calendar className="w-5 h-5 text-blue-600" />
              <label className="block text-sm font-semibold">
                What is your age? <span className="text-red-500">*</span>
              </label>
            </div>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter your age"
              min="1"
              max="120"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg text-gray-900 bg-white"
              disabled={isLoading}
            />
            <button
              onClick={handleNext}
              disabled={!age || isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}

        {/* Step 2: Interests */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-700 mb-4">
              <Activity className="w-5 h-5 text-blue-600" />
              <label className="block text-sm font-semibold">
                What are your travel interests? <span className="text-red-500">*</span>
              </label>
            </div>
            <p className="text-xs text-gray-500 mb-4">Select all that apply</p>
            <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto">
              {interestOptions.map((interest) => (
                <button
                  key={interest}
                  onClick={() => handleInterestToggle(interest)}
                  className={`px-3 py-2 rounded-lg border-2 transition-all text-sm ${
                    interests.includes(interest)
                      ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold'
                      : 'border-gray-200 hover:border-blue-300 text-gray-700'
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
                className="px-4 py-2 text-gray-600 rounded-lg font-medium hover:bg-gray-50"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={interests.length === 0 || isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-2 rounded-lg font-semibold hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Medical Conditions */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-700 mb-4">
              <Heart className="w-5 h-5 text-blue-600" />
              <label className="block text-sm font-semibold">
                Do you have any medical conditions?
              </label>
            </div>
            <p className="text-xs text-gray-500 mb-4">This helps us recommend the right coverage</p>
            <div className="space-y-2">
              {medicalConditionOptions.map((condition) => (
                <button
                  key={condition}
                  onClick={() => handleMedicalToggle(condition)}
                  className={`w-full px-4 py-2 rounded-lg border-2 transition-all text-left ${
                    medicalConditions.includes(condition) || (condition === 'None' && medicalConditions.length === 0)
                      ? 'border-blue-600 bg-blue-50 text-blue-700 font-semibold'
                      : 'border-gray-200 hover:border-blue-300 text-gray-700'
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep(2)}
                className="px-4 py-2 text-gray-600 rounded-lg font-medium hover:bg-gray-50"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleComplete}
                disabled={isLoading}
                className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white py-2 rounded-lg font-semibold hover:shadow-lg transition-shadow disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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

        {onSkip && step === 1 && (
          <button
            onClick={onSkip}
            disabled={isLoading}
            className="w-full text-gray-600 py-2 rounded-lg font-medium hover:bg-gray-50"
          >
            Skip for now
          </button>
        )}
      </div>
    </div>
  )
}

