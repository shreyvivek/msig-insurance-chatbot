'use client'

import React, { useState, useMemo } from 'react'
import { User, Heart, X, CheckCircle, Loader2, Calendar, Activity, Mail, Phone, CreditCard, Shield, ChevronDown, AlertCircle } from 'lucide-react'

interface UserOnboardingProps {
  onComplete: (userData: any) => void
  onSkip?: () => void
}

// Country codes for phone selector
const countryCodes = [
  { code: '+65', country: 'Singapore', flag: '🇸🇬' },
  { code: '+60', country: 'Malaysia', flag: '🇲🇾' },
  { code: '+62', country: 'Indonesia', flag: '🇮🇩' },
  { code: '+66', country: 'Thailand', flag: '🇹🇭' },
  { code: '+63', country: 'Philippines', flag: '🇵🇭' },
  { code: '+84', country: 'Vietnam', flag: '🇻🇳' },
  { code: '+1', country: 'USA/Canada', flag: '🇺🇸' },
  { code: '+44', country: 'UK', flag: '🇬🇧' },
  { code: '+61', country: 'Australia', flag: '🇦🇺' },
  { code: '+86', country: 'China', flag: '🇨🇳' },
  { code: '+81', country: 'Japan', flag: '🇯🇵' },
  { code: '+82', country: 'South Korea', flag: '🇰🇷' },
  { code: '+91', country: 'India', flag: '🇮🇳' },
  { code: '+971', country: 'UAE', flag: '🇦🇪' },
]

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

// Luhn algorithm for card validation
function validateCardNumber(cardNumber: string): boolean {
  const cleaned = cardNumber.replace(/\s/g, '')
  if (!/^\d{13,19}$/.test(cleaned)) return false
  
  let sum = 0
  let isEven = false
  
  for (let i = cleaned.length - 1; i >= 0; i--) {
    let digit = parseInt(cleaned[i])
    
    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }
    
    sum += digit
    isEven = !isEven
  }
  
  return sum % 10 === 0
}

// Validate expiry date
function validateExpiryDate(expiry: string): boolean {
  const cleaned = expiry.replace(/\D/g, '')
  if (cleaned.length !== 4) return false
  
  const month = parseInt(cleaned.substring(0, 2))
  const year = parseInt('20' + cleaned.substring(2, 4))
  
  if (month < 1 || month > 12) return false
  
  const now = new Date()
  const expiryDate = new Date(year, month - 1)
  
  return expiryDate > now
}

export default function UserOnboarding({ onComplete, onSkip }: UserOnboardingProps) {
  const [step, setStep] = useState(1)
  
  // Step 1: Basic Info
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phoneCode, setPhoneCode] = useState('+65')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [showPhoneDropdown, setShowPhoneDropdown] = useState(false)
  
  // Step 2: Identity Documents
  const [passportNumber, setPassportNumber] = useState('')
  const [nricNumber, setNricNumber] = useState('')
  
  // Step 3: Age & Interests (existing)
  const [age, setAge] = useState('')
  const [interests, setInterests] = useState<string[]>([])
  const [medicalConditions, setMedicalConditions] = useState<string[]>([])
  const [customMedical, setCustomMedical] = useState('')
  
  // Step 4: Payment Card
  const [cardNumber, setCardNumber] = useState('')
  const [cardExpiry, setCardExpiry] = useState('')
  const [cardCVV, setCardCVV] = useState('')
  const [cardName, setCardName] = useState('')
  const [cardErrors, setCardErrors] = useState<{number?: string, expiry?: string, cvv?: string}>({})
  const [isVerifyingCard, setIsVerifyingCard] = useState(false)
  
  const [isLoading, setIsLoading] = useState(false)
  
  const totalSteps = 6

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
  
  const calculateAge = (dob: string): number => {
    if (!dob) return 0
    const birthDate = new Date(dob)
    const today = new Date()
    let age = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--
    }
    return age
  }

  // Check if card details are valid (without setting errors - for display purposes)
  // Use useMemo to compute validation state without side effects
  const isCardValid = useMemo(() => {
    const cleanedCardNumber = cardNumber.replace(/\s/g, '')
    
    if (!cleanedCardNumber || cleanedCardNumber.length < 13) {
      return false
    }
    if (!validateCardNumber(cardNumber)) {
      return false
    }
    if (!cardExpiry || cardExpiry.length !== 5) {
      return false
    }
    if (!validateExpiryDate(cardExpiry)) {
      return false
    }
    if (!cardCVV || cardCVV.length < 3) {
      return false
    }
    if (!cardName) {
      return false
    }
    
    return true
  }, [cardNumber, cardExpiry, cardCVV, cardName])

  const verifyCardDetails = (): boolean => {
    const errors: {number?: string, expiry?: string, cvv?: string} = {}
    let isValid = true
    
    const cleanedCardNumber = cardNumber.replace(/\s/g, '')
    
    if (!cleanedCardNumber || cleanedCardNumber.length < 13) {
      errors.number = 'Card number must be at least 13 digits'
      isValid = false
    } else if (!validateCardNumber(cardNumber)) {
      errors.number = 'Invalid card number'
      isValid = false
    }
    
    if (!cardExpiry || cardExpiry.length !== 5) {
      errors.expiry = 'Expiry date must be in MM/YY format'
      isValid = false
    } else if (!validateExpiryDate(cardExpiry)) {
      errors.expiry = 'Card has expired or invalid date'
      isValid = false
    }
    
    if (!cardCVV || cardCVV.length < 3) {
      errors.cvv = 'CVV must be 3-4 digits'
      isValid = false
    }
    
    if (!cardName) {
      errors.cvv = 'Cardholder name is required'
      isValid = false
    }
    
    setCardErrors(errors)
    return isValid
  }

  // Validation without side effects (for use in JSX/disabled props)
  const checkStepValid = (stepNum: number): boolean => {
    switch(stepNum) {
      case 1:
        return !!(name && email && phoneNumber && dateOfBirth)
      case 2:
        return true // Both passport and NRIC are optional
      case 3:
        return !!(age || dateOfBirth) && interests.length > 0
      case 4:
        return true // Medical conditions are optional
      case 5:
        return isCardValid && !!cardName // Use isCardValid (computed value) instead of verifyCardDetails
      default:
        return true
    }
  }

  const validateStep = (stepNum: number): boolean => {
    switch(stepNum) {
      case 1:
        return !!(name && email && phoneNumber && dateOfBirth)
      case 2:
        return true // Both passport and NRIC are optional
      case 3:
        return !!(age || dateOfBirth) && interests.length > 0
      case 4:
        return true // Medical conditions are optional
      case 5:
        return verifyCardDetails() // This sets errors, only call during form submission
      default:
        return true
    }
  }

  const handleNext = () => {
    if (validateStep(step)) {
      if (step === 1 && dateOfBirth && !age) {
        // Auto-calculate age from DOB
        const calculatedAge = calculateAge(dateOfBirth)
        setAge(calculatedAge.toString())
      }
      
      if (step < totalSteps) {
        setStep(step + 1)
      } else {
      handleComplete()
      }
    }
  }

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    // Format as XXXX XXXX XXXX XXXX
    if (value.length > 16) value = value.substring(0, 16)
    const formatted = value.replace(/(\d{4})(?=\d)/g, '$1 ')
    setCardNumber(formatted)
    setCardErrors({...cardErrors, number: undefined})
  }
  
  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    if (value.length > 4) value = value.substring(0, 4)
    const formatted = value.replace(/(\d{2})(?=\d)/g, '$1/')
    setCardExpiry(formatted)
    setCardErrors({...cardErrors, expiry: undefined})
  }
  
  const handleCVVChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    if (value.length > 4) value = value.substring(0, 4)
    setCardCVV(value)
    setCardErrors({...cardErrors, cvv: undefined})
  }

  const handleComplete = async () => {
    setIsLoading(true)
    
    // Verify card one more time
    if (!verifyCardDetails()) {
      setIsLoading(false)
      return
    }
    
    // Ensure age is a number
    const ageNum = dateOfBirth ? calculateAge(dateOfBirth) : (typeof age === 'string' ? parseInt(age) : age)
    
    const userData = {
      // Basic Info
      name: name,
      email: email,
      phone: `${phoneCode} ${phoneNumber}`,
      phone_code: phoneCode,
      phone_number: phoneNumber,
      date_of_birth: dateOfBirth,
      age: ageNum,
      
      // Identity Documents
      passport_number: passportNumber || null,
      nric_number: nricNumber || null,
      
      // Preferences
      interests: interests,
      medical_conditions: [...medicalConditions, ...(customMedical ? [customMedical] : [])].filter(Boolean),
      
      // Payment Card (stored securely - in production, encrypt this)
      payment_card: {
        number: cardNumber.replace(/\s/g, ''), // Store without spaces
        expiry: cardExpiry,
        cvv: cardCVV,
        name: cardName || name
      },
      
      created_at: new Date().toISOString()
    }

    console.log('💾 Saving enhanced user data:', { ...userData, payment_card: { ...userData.payment_card, number: '****', cvv: '***' } })

    // Save to localStorage
    localStorage.setItem('wandersure_user_data', JSON.stringify(userData))
    localStorage.setItem('wandersure_onboarded', 'true')

    console.log('✅ Enhanced user data saved to localStorage')

    setIsLoading(false)
    onComplete(userData)
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[9999] flex items-center justify-center p-4" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0 }}>
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-3xl shadow-2xl border border-slate-700/50 max-w-md w-full max-h-[90vh] overflow-y-auto p-8 space-y-6 backdrop-blur-xl">
        <div className="flex items-center justify-between mb-4 sticky top-0 bg-slate-900/90 backdrop-blur-sm -mx-8 px-8 py-4 border-b border-slate-700/50">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Complete Your Profile
          </h2>
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
            <span className="font-medium">Step {step} of {totalSteps}</span>
            <div className="flex-1 h-2 bg-slate-700/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 transition-all duration-300 rounded-full shadow-lg"
                style={{ width: `${(step / totalSteps) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Step 1: Basic Information */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <User className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Basic Information <span className="text-red-400">*</span>
              </label>
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="John Doe"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="john@example.com"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Phone Number</label>
              <div className="flex gap-2">
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowPhoneDropdown(!showPhoneDropdown)}
                    className="px-3 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl text-slate-100 flex items-center gap-1 min-w-[100px]"
                  >
                    <span>{phoneCode}</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  {showPhoneDropdown && (
                    <div className="absolute top-full mt-1 left-0 bg-slate-800 border border-slate-600 rounded-xl shadow-xl max-h-64 overflow-y-auto z-50 min-w-[200px]">
                      {countryCodes.map((country) => (
                        <button
                          key={country.code}
                          onClick={() => {
                            setPhoneCode(country.code)
                            setShowPhoneDropdown(false)
                          }}
                          className="w-full px-4 py-2 text-left hover:bg-slate-700 text-slate-100 flex items-center gap-2"
                        >
                          <span>{country.flag}</span>
                          <span className="flex-1">{country.country}</span>
                          <span className="text-slate-400">{country.code}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                  placeholder="9123 4567"
                  className="flex-1 px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                  disabled={isLoading}
                />
              </div>
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Date of Birth</label>
            <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
              disabled={isLoading}
            />
            </div>
            
            <button
              onClick={handleNext}
              disabled={!checkStepValid(1) || isLoading}
              className="w-full bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-3.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
            >
              Next
            </button>
          </div>
        )}

        {/* Step 2: Identity Documents */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Shield className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Identity Documents (Optional)
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">These help us verify your identity faster</p>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Passport Number</label>
              <input
                type="text"
                value={passportNumber}
                onChange={(e) => setPassportNumber(e.target.value.toUpperCase())}
                placeholder="A12345678"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">NRIC Number</label>
              <input
                type="text"
                value={nricNumber}
                onChange={(e) => setNricNumber(e.target.value.toUpperCase())}
                placeholder="S1234567A"
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
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
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 hover:scale-[1.02]"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Age & Interests */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Activity className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Travel Preferences <span className="text-red-400">*</span>
              </label>
            </div>
            
            {!dateOfBirth && (
              <div>
                <label className="block text-xs text-slate-400 mb-2">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="30"
                  min="1"
                  max="120"
                  className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                  disabled={isLoading || !!dateOfBirth}
                />
              </div>
            )}
            
            {dateOfBirth && (
              <div className="px-4 py-3 bg-blue-500/20 border border-blue-500/50 rounded-xl">
                <p className="text-sm text-blue-300">
                  Age: {calculateAge(dateOfBirth)} (calculated from date of birth)
                </p>
              </div>
            )}
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Travel Interests <span className="text-red-400">*</span></label>
              <p className="text-xs text-slate-500 mb-3">Select all that apply</p>
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
                onClick={handleNext}
                disabled={interests.length === 0 || (!age && !dateOfBirth) || isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Medical Conditions */}
        {step === 4 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <Heart className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Medical Conditions (Optional)
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
                onClick={() => setStep(3)}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 hover:scale-[1.02]"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Payment Card */}
        {step === 5 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <CreditCard className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Payment Card Details <span className="text-red-400">*</span>
              </label>
            </div>
            <p className="text-xs text-slate-400 mb-4">For faster checkout in the future</p>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Cardholder Name</label>
              <input
                type="text"
                value={cardName}
                onChange={(e) => setCardName(e.target.value)}
                placeholder={name || "John Doe"}
                className="w-full px-4 py-3 bg-slate-800/50 border border-slate-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm"
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label className="block text-xs text-slate-400 mb-2">Card Number</label>
              <input
                type="text"
                value={cardNumber}
                onChange={handleCardNumberChange}
                placeholder="1234 5678 9012 3456"
                maxLength={19}
                className={`w-full px-4 py-3 bg-slate-800/50 border rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm ${
                  cardErrors.number ? 'border-red-500' : 'border-slate-600/50'
                }`}
                disabled={isLoading}
              />
              {cardErrors.number && (
                <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {cardErrors.number}
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-2">Expiry (MM/YY)</label>
                <input
                  type="text"
                  value={cardExpiry}
                  onChange={handleExpiryChange}
                  placeholder="12/25"
                  maxLength={5}
                  className={`w-full px-4 py-3 bg-slate-800/50 border rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm ${
                    cardErrors.expiry ? 'border-red-500' : 'border-slate-600/50'
                  }`}
                  disabled={isLoading}
                />
                {cardErrors.expiry && (
                  <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    {cardErrors.expiry}
                  </p>
                )}
              </div>
              
              <div>
                <label className="block text-xs text-slate-400 mb-2">CVV</label>
                <input
                  type="text"
                  value={cardCVV}
                  onChange={handleCVVChange}
                  placeholder="123"
                  maxLength={4}
                  className={`w-full px-4 py-3 bg-slate-800/50 border rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-slate-500 transition-all backdrop-blur-sm ${
                    cardErrors.cvv ? 'border-red-500' : 'border-slate-600/50'
                  }`}
                  disabled={isLoading}
                />
                {cardErrors.cvv && (
                  <p className="text-xs text-red-400 mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    {cardErrors.cvv}
                  </p>
                )}
              </div>
            </div>
            
            {isCardValid && cardNumber && cardExpiry && cardCVV && cardName && (
              <div className="px-4 py-3 bg-green-500/20 border border-green-500/50 rounded-xl">
                <p className="text-sm text-green-300 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  Card details verified
                </p>
              </div>
            )}
            
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep(4)}
                className="px-5 py-2.5 text-slate-400 rounded-xl font-medium hover:bg-slate-700/50 hover:text-slate-200 transition-all duration-200"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={handleNext}
                disabled={!checkStepValid(5) || isLoading}
                className="flex-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white py-2.5 rounded-xl font-semibold hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] disabled:hover:scale-100"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {/* Step 6: Review & Complete */}
        {step === 6 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-200 mb-4">
              <CheckCircle className="w-5 h-5 text-blue-400" />
              <label className="block text-sm font-semibold">
                Review Your Information
              </label>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Name</p>
                <p className="text-slate-100">{name}</p>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Email</p>
                <p className="text-slate-100">{email}</p>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Phone</p>
                <p className="text-slate-100">{phoneCode} {phoneNumber}</p>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Date of Birth</p>
                <p className="text-slate-100">{dateOfBirth ? new Date(dateOfBirth).toLocaleDateString() : 'Not provided'}</p>
              </div>
              {passportNumber && (
                <div className="p-3 bg-slate-800/50 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">Passport</p>
                  <p className="text-slate-100">{passportNumber}</p>
                </div>
              )}
              {nricNumber && (
                <div className="p-3 bg-slate-800/50 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">NRIC</p>
                  <p className="text-slate-100">{nricNumber}</p>
                </div>
              )}
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Interests</p>
                <p className="text-slate-100">{interests.join(', ') || 'None selected'}</p>
              </div>
              {medicalConditions.length > 0 && (
                <div className="p-3 bg-slate-800/50 rounded-xl">
                  <p className="text-slate-400 text-xs mb-1">Medical Conditions</p>
                  <p className="text-slate-100">{medicalConditions.join(', ')}</p>
                </div>
              )}
              <div className="p-3 bg-slate-800/50 rounded-xl">
                <p className="text-slate-400 text-xs mb-1">Card</p>
                <p className="text-slate-100">**** **** **** {cardNumber.slice(-4).replace(/\s/g, '')}</p>
              </div>
            </div>
            
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setStep(5)}
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
      </div>
    </div>
  )
}