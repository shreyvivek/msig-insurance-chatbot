'use client'

import React, { useState } from 'react'
import { User, Heart, X, CheckCircle, Loader2, Calendar, Activity } from 'lucide-react'

interface UserOnboardingProps {
  onComplete: (userData: any) => void
  onSkip?: () => void
}

export default function UserOnboarding({ onComplete, onSkip }: UserOnboardingProps) {
  const [step, setStep] = useState(1)
  const [numTravelers, setNumTravelers] = useState('1')
  const [travelers, setTravelers] = useState<Array<{
    name: string
    age: string
    interests: string[]
    medicalConditions: string[]
    customMedical: string
  }>>([{ name: '', age: '', interests: [], medicalConditions: [], customMedical: '' }])
  const [currentTravelerIndex, setCurrentTravelerIndex] = useState(0)
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
    if (step === 1) {
      // Step 1: Number of travelers
      const num = parseInt(numTravelers) || 1
      // Initialize travelers array
      const newTravelers = Array.from({ length: num }, (_, i) => 
        travelers[i] || { name: '', age: '', interests: [], medicalConditions: [], customMedical: '' }
      )
      setTravelers(newTravelers)
      setCurrentTravelerIndex(0)
      setStep(2)
    } else if (step === 2) {
      // Step 2: Current traveler's age and interests
      const current = travelers[currentTravelerIndex]
      if (current.age && current.interests.length > 0) {
        if (currentTravelerIndex < travelers.length - 1) {
          // Move to next traveler
          setCurrentTravelerIndex(currentTravelerIndex + 1)
        } else {
          // All travelers done, move to medical conditions
          setCurrentTravelerIndex(0)
          setStep(3)
        }
      }
    } else if (step === 3) {
      // Step 3: Medical conditions - check if all travelers are done
      if (currentTravelerIndex < travelers.length - 1) {
        setCurrentTravelerIndex(currentTravelerIndex + 1)
      } else {
        handleComplete()
      }
    }
  }

  const handleComplete = async () => {
    setIsLoading(true)
    
    // Process all travelers' data
    const travelersData = travelers.map((t, idx) => ({
      name: t.name || `Traveler ${idx + 1}`,
      age: parseInt(t.age) || 30,
      interests: t.interests || [],
      medical_conditions: [...(t.medicalConditions || []), ...(t.customMedical ? [t.customMedical] : [])].filter(Boolean),
    }))
    
    // Primary user is the first traveler
    const primaryUser = travelersData[0]
    const userData = {
      ...primaryUser,
      travelers: travelersData, // Store all travelers
      num_travelers: travelersData.length,
      created_at: new Date().toISOString()
    }

    console.log('💾 Saving user data with all travelers:', userData)

    // Save to localStorage
    localStorage.setItem('wandersure_user_data', JSON.stringify(userData))
    localStorage.setItem('wandersure_onboarded', 'true')

    console.log('✅ User data with all travelers saved to localStorage')

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
            <span className="font-medium">
              {step === 1 ? 'Step 1 of 3' : 
               step === 2 ? `Step 2 of 3 - Traveler ${currentTravelerIndex + 1} of ${travelers.length}` :
               `Step 3 of 3 - Traveler ${currentTravelerIndex + 1} of ${travelers.length}`}
            </span>
            <div className="flex-1 h-2 bg-slate-700/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 transition-all duration-300 rounded-full shadow-lg"
                style={{ width: `${(step / 3) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Step 1: Number of travelers */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <User className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                How many travelers? <span className="text-red-400">*</span>
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">We'll collect details for each traveler</p>
            <input
              type="number"
              value={numTravelers}
              onChange={(e) => setNumTravelers(e.target.value)}
              placeholder="Enter number of travelers"
              min="1"
              max="10"
              className="w-full px-4 py-3.5 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-lg text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
              disabled={isLoading}
            />
            <button
              onClick={handleNext}
              disabled={!numTravelers || parseInt(numTravelers) < 1 || isLoading}
              className="w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-3.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
            >
              Next
            </button>
          </div>
        )}

        {/* Step 2: Age and Interests for current traveler */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-2">
              <User className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Traveler {currentTravelerIndex + 1} Details <span className="text-red-400">*</span>
              </label>
            </div>
            <input
              type="text"
              value={travelers[currentTravelerIndex]?.name || ''}
              onChange={(e) => {
                const updated = [...travelers]
                updated[currentTravelerIndex].name = e.target.value
                setTravelers(updated)
              }}
              placeholder="Traveler name (optional)"
              className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm mb-3"
              disabled={isLoading}
            />
            <div className="flex items-center gap-2 text-slate-200 mb-2">
              <Calendar className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Age <span className="text-red-400">*</span>
              </label>
            </div>
            <input
              type="number"
              value={travelers[currentTravelerIndex]?.age || ''}
              onChange={(e) => {
                const updated = [...travelers]
                updated[currentTravelerIndex].age = e.target.value
                setTravelers(updated)
              }}
              placeholder="Enter age"
              min="1"
              max="120"
              className="w-full px-4 py-2.5 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm mb-3"
              disabled={isLoading}
            />
            <div className="flex items-center gap-2 text-slate-200 mb-2">
              <Activity className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Travel interests <span className="text-red-400">*</span>
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-2">Select all that apply</p>
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
              {interestOptions.map((interest) => (
                <button
                  key={interest}
                  onClick={() => {
                    const updated = [...travelers]
                    const currentInterests = updated[currentTravelerIndex].interests || []
                    if (currentInterests.includes(interest)) {
                      updated[currentTravelerIndex].interests = currentInterests.filter(i => i !== interest)
                    } else {
                      updated[currentTravelerIndex].interests = [...currentInterests, interest]
                    }
                    setTravelers(updated)
                  }}
                  className={`px-3 py-2 rounded-xl border-2 transition-all duration-200 text-xs font-medium ${
                    travelers[currentTravelerIndex]?.interests?.includes(interest)
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
                onClick={() => {
                  if (currentTravelerIndex > 0) {
                    setCurrentTravelerIndex(currentTravelerIndex - 1)
                  } else {
                    setStep(1)
                  }
                }}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={!travelers[currentTravelerIndex]?.age || travelers[currentTravelerIndex]?.interests?.length === 0 || isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
              >
                {currentTravelerIndex < travelers.length - 1 ? 'Next Traveler' : 'Next'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Medical Conditions for current traveler */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Heart className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Traveler {currentTravelerIndex + 1} - Medical Conditions
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">This helps us recommend the right coverage</p>
            <div className="space-y-2">
              {medicalConditionOptions.map((condition) => (
                <button
                  key={condition}
                  onClick={() => {
                    const updated = [...travelers]
                    const current = updated[currentTravelerIndex].medicalConditions || []
                    if (condition === 'None') {
                      updated[currentTravelerIndex].medicalConditions = []
                    } else {
                      if (current.includes(condition)) {
                        updated[currentTravelerIndex].medicalConditions = current.filter(c => c !== condition)
                      } else {
                        updated[currentTravelerIndex].medicalConditions = [...current.filter(c => c !== 'None'), condition]
                      }
                    }
                    setTravelers(updated)
                  }}
                  className={`w-full px-4 py-3 rounded-xl border-2 transition-all duration-200 text-left font-medium ${
                    travelers[currentTravelerIndex]?.medicalConditions?.includes(condition) || 
                    (condition === 'None' && (!travelers[currentTravelerIndex]?.medicalConditions || travelers[currentTravelerIndex].medicalConditions.length === 0))
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
                value={travelers[currentTravelerIndex]?.customMedical || ''}
                onChange={(e) => {
                  const updated = [...travelers]
                  updated[currentTravelerIndex].customMedical = e.target.value
                  setTravelers(updated)
                }}
                placeholder="Or specify other conditions (optional)"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => {
                  if (currentTravelerIndex > 0) {
                    setCurrentTravelerIndex(currentTravelerIndex - 1)
                  } else {
                    setStep(2)
                    setCurrentTravelerIndex(travelers.length - 1)
                  }
                }}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
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
                    {currentTravelerIndex < travelers.length - 1 ? 'Next Traveler' : 'Complete Setup'}
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

