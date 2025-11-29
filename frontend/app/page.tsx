'use client'

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Mic, Volume2, Sparkles, Plane, Upload, X, History, ChevronLeft, ExternalLink, ShoppingCart, User, CreditCard, Mail, Phone, Calendar, MessageSquarePlus, Trash2, Edit2, Check, X as XIcon } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import UserOnboarding from '../components/UserOnboarding'

// Function to clean policy names for display
function cleanPolicyName(name: string): string {
  if (!name) return '';
  return name
    .replace(/#+/g, '') // Remove hashes
    .replace(/[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~]/g, ' ') // Remove special chars
    .replace(/^\s+|\s+$/g, '') // Trim
    .replace(/\s+/g, ' '); // Normalize spaces
}

// Function to auto-download policy receipt
function downloadPolicyReceipt(receiptData: {
  policyName: string
  policyNumber: string
  policyType: string
  price: number
  currency: string
  travelers: any[]
  tripDetails?: any
  purchaseDate: string
}) {
  try {
    // Generate PDF content as HTML
    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      padding: 40px;
      background: #f5f5f5;
    }
    .receipt-container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      padding: 40px;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #0066cc;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .logo {
      font-size: 32px;
      font-weight: bold;
      color: #0066cc;
      margin-bottom: 10px;
    }
    .subtitle {
      color: #666;
      font-size: 14px;
    }
    .receipt-title {
      font-size: 28px;
      color: #333;
      margin-bottom: 10px;
      font-weight: 600;
    }
    .section {
      margin-bottom: 30px;
    }
    .section-title {
      font-size: 18px;
      font-weight: 600;
      color: #0066cc;
      margin-bottom: 15px;
      border-left: 4px solid #0066cc;
      padding-left: 10px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #eee;
    }
    .info-label {
      font-weight: 600;
      color: #666;
      flex: 1;
    }
    .info-value {
      color: #333;
      flex: 2;
      text-align: right;
    }
    .highlight {
      background: #f0f9ff;
      padding: 15px;
      border-radius: 8px;
      border-left: 4px solid #0066cc;
      margin-top: 10px;
    }
    .amount {
      font-size: 36px;
      font-weight: bold;
      color: #0066cc;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #eee;
      text-align: center;
      color: #666;
      font-size: 12px;
    }
    .policy-number {
      font-family: 'Courier New', monospace;
      font-size: 20px;
      font-weight: bold;
      color: #0066cc;
      letter-spacing: 1px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #eee;
    }
    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #666;
    }
    .success-badge {
      display: inline-block;
      background: #10b981;
      color: white;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 20px;
    }
  </style>
</head>
<body>
  <div class="receipt-container">
    <div class="header">
      <div class="logo">🛡️ WanderSure</div>
      <div class="subtitle">Travel Insurance Policy Receipt</div>
    </div>
    
    <div class="success-badge">✓ Payment Confirmed</div>
    <div class="receipt-title">Policy Receipt</div>
    
    <div class="section">
      <div class="section-title">Policy Information</div>
      <div class="info-row">
        <span class="info-label">Policy Name:</span>
        <span class="info-value">${receiptData.policyName}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Policy Number:</span>
        <span class="info-value policy-number">${receiptData.policyNumber}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Policy Type:</span>
        <span class="info-value">${receiptData.policyType}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Purchase Date:</span>
        <span class="info-value">${new Date(receiptData.purchaseDate).toLocaleString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
      </div>
    </div>

    ${receiptData.tripDetails ? `
    <div class="section">
      <div class="section-title">Trip Information</div>
      ${receiptData.tripDetails.destination ? `
      <div class="info-row">
        <span class="info-label">Destination:</span>
        <span class="info-value">${receiptData.tripDetails.destination}</span>
      </div>
      ` : ''}
      ${receiptData.tripDetails.source ? `
      <div class="info-row">
        <span class="info-label">Origin:</span>
        <span class="info-value">${receiptData.tripDetails.source}</span>
      </div>
      ` : ''}
      ${receiptData.tripDetails.departure_date && receiptData.tripDetails.return_date ? `
      <div class="info-row">
        <span class="info-label">Travel Period:</span>
        <span class="info-value">
          ${new Date(receiptData.tripDetails.departure_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })} - 
          ${new Date(receiptData.tripDetails.return_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
        </span>
      </div>
      ` : ''}
    </div>
    ` : ''}

    <div class="section">
      <div class="section-title">Travelers</div>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Date of Birth</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          ${receiptData.travelers.map((t: any) => `
          <tr>
            <td>${t.firstName || t.name || 'N/A'} ${t.lastName || ''}</td>
            <td>${t.dateOfBirth || t.dob || 'N/A'}</td>
            <td>${t.email || 'N/A'}</td>
          </tr>
          `).join('')}
        </tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Payment Summary</div>
      <div class="highlight">
        <div class="info-row">
          <span class="info-label">Total Amount Paid:</span>
          <span class="info-value amount">${receiptData.currency} ${receiptData.price.toFixed(2)}</span>
        </div>
      </div>
    </div>

    <div class="footer">
      <p>This is a computer-generated receipt. Please keep this for your records.</p>
      <p style="margin-top: 10px;">
        For support, please contact us at support@wandersure.com
      </p>
      <p style="margin-top: 5px; color: #999;">
        Generated on ${new Date().toLocaleString('en-US')}
      </p>
    </div>
  </div>
</body>
</html>
    `.trim()
    
    // Create blob and download
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Policy_Receipt_${receiptData.policyNumber}_${Date.now()}.html`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    console.log('✅ Policy receipt downloaded successfully')
  } catch (error) {
    console.error('Failed to download receipt:', error)
  }
}

// Policy Card Component - Beautiful card for displaying policy info
function PolicyCard({ policyName, onClick, isAncileo, source }: { 
  policyName: string
  onClick: () => void
  isAncileo?: boolean
  source?: string
}) {
  const cleanedName = cleanPolicyName(policyName);
  const getPolicyStyles = (name: string) => {
    if (isAncileo || source === 'ancileo') {
      return 'from-purple-600 to-pink-600 shadow-purple-500/20 hover:shadow-purple-500/40'
    }
    const lowerName = name.toLowerCase();
    // Removed TravelEasy - doesn't exist in Policy_Wordings
    // Only these policies exist: INTERNATIONAL TRAVEL, MHInsure Travel, Scootsurance
    if (lowerName.includes('international travel') || lowerName.includes('msig')) {
      return 'from-blue-500 to-cyan-500 shadow-blue-500/20 hover:shadow-blue-500/40'
    }
    if (lowerName.includes('mhinsure')) {
      return 'from-emerald-500 to-teal-500 shadow-emerald-500/20 hover:shadow-emerald-500/40'
    }
    if (lowerName.includes('scootsurance')) {
      return 'from-purple-500 to-pink-500 shadow-purple-500/20 hover:shadow-purple-500/40'
    }
    return 'from-indigo-500 to-blue-500 shadow-indigo-500/20 hover:shadow-indigo-500/40'
  }
  
  return (
    <button
      onClick={onClick}
      className={`group relative overflow-hidden rounded-xl bg-gradient-to-br ${getPolicyStyles(cleanedName)} p-5 text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl border border-white/10 h-full flex flex-col min-h-[140px]`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
      <div className="relative z-10 flex flex-col flex-1">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-bold text-white text-lg drop-shadow-lg line-clamp-2 flex-1">{cleanedName}</h3>
          {isAncileo || source === 'ancileo' ? (
            <span className="ml-2 px-2 py-1 bg-white/20 text-white text-xs font-semibold rounded-full flex items-center gap-1 flex-shrink-0">
              <Sparkles className="w-3 h-3" />
              Ancileo
            </span>
          ) : (
            <span className="ml-2 px-2 py-1 bg-white/20 text-white text-xs font-semibold rounded-full flex-shrink-0">
              Local
            </span>
          )}
        </div>
        <p className="text-white/90 text-sm font-medium mt-auto">View full policy details</p>
      </div>
    </button>
  )
}

// Policy Modal Component
function PolicyModal({ policyName, isOpen, onClose, productCode, offerId, quoteId }: { 
  policyName: string
  isOpen: boolean
  onClose: () => void
  productCode?: string
  offerId?: string
  quoteId?: string
}) {
  const [details, setDetails] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isAncileo, setIsAncileo] = useState(false)
  const cleanedName = cleanPolicyName(policyName)
  
  useEffect(() => {
    if (isOpen && !details) {
      setIsLoading(true)
      
      // Try Ancileo API - Note: According to Ancileo docs, getPolicy requires policyId (from purchase) and email
      // For now, if we have offer_id but not policy_id, we'll use local policy details
      // The policy wordings can only be fetched after purchase
      setIsAncileo(false)
      
      // For purchased policies, we could fetch wordings, but we need policy_id and email
      // This would need to be called after purchase with the purchasedOfferId
      // For now, fallback to local policy details
      fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/api/policy/details?policy_name=${encodeURIComponent(cleanedName)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            setDetails(data.summary)
            setIsAncileo(false)
          }
          setIsLoading(false)
        })
        .catch(() => setIsLoading(false))
    }
  }, [isOpen, cleanedName, details, productCode, offerId, quoteId])
  
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="relative bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-3xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between border-b border-gray-700">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white">{cleanedName}</h2>
            {isAncileo && (
              <span className="px-2 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-semibold rounded-full flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Ancileo API
              </span>
            )}
            {!isAncileo && (
              <span className="px-2 py-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-xs font-semibold rounded-full">
                Local
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : details ? (
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="text-gray-200 mb-3 leading-relaxed">{children}</p>,
                  strong: ({ children }) => <strong className="text-blue-300 font-semibold">{children}</strong>,
                  ul: ({ children }) => <ul className="list-disc list-inside space-y-2 mb-4 text-gray-200">{children}</ul>,
                  li: ({ children }) => <li className="text-gray-300">{children}</li>,
                }}
              >
                {details}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-gray-400">Unable to load policy details.</p>
          )}
        </div>
      </div>
    </div>
  )
}

// Purchase Form Modal - Step by step form for collecting traveler details
function PurchaseForm({ quote, quoteId, tripDetails, isOpen, onClose, onComplete }: {
  quote: any
  quoteId?: string
  tripDetails?: any
  isOpen: boolean
  onClose: () => void
  onComplete: (insureds: any[], paymentInfo: any) => void
}) {
  const [step, setStep] = useState(1)
  const [travelers, setTravelers] = useState<Array<{ name: string; age: number; email: string; phone: string; dob: string }>>([])
  const [currentTraveler, setCurrentTraveler] = useState({ name: '', age: 0, email: '', phone: '', dob: '' })
  const [paymentInfo, setPaymentInfo] = useState({ cardNumber: '', expiryDate: '', cvv: '', cardName: '' })
  const [isAutoFilling, setIsAutoFilling] = useState(false)

  useEffect(() => {
    if (!isOpen) {
      // Reset form when closed
      setStep(1)
      setTravelers([])
      setCurrentTraveler({ name: '', age: 0, email: '', phone: '', dob: '' })
      setPaymentInfo({ cardNumber: '', expiryDate: '', cvv: '', cardName: '' })
      return
    }
    
    if (isOpen && tripDetails) {
      // Handle different tripDetails structures
      let initialTravelers: Array<{ name: string; age: number; email: string; phone: string; dob: string }> = []
      
      // Determine number of travelers - check multiple sources
      let numTravelers = 1
      if (Array.isArray(tripDetails.travelers)) {
        numTravelers = tripDetails.travelers.length
      } else if (tripDetails.traveler_names && Array.isArray(tripDetails.traveler_names)) {
        numTravelers = tripDetails.traveler_names.length
      } else if (tripDetails.travelers && typeof tripDetails.travelers === 'number') {
        numTravelers = tripDetails.travelers
      } else if (tripDetails.pax && typeof tripDetails.pax === 'number') {
        numTravelers = tripDetails.pax
      } else {
        const numAdults = tripDetails.adults || 1
        const numChildren = tripDetails.children || 0
        numTravelers = numAdults + numChildren
      }
      
      // Now create travelers array with extracted data
      if (Array.isArray(tripDetails.travelers)) {
        // If travelers is an array with data, map it
        initialTravelers = tripDetails.travelers.map((t: any) => ({
          name: t.name || '',
          age: t.age || 0,
          email: t.email || '',
          phone: t.phone || '',
          dob: '' // NEVER auto-fill DOB
        }))
        // Ensure we have the right number
        while (initialTravelers.length < numTravelers) {
          initialTravelers.push({ name: '', age: 0, email: '', phone: '', dob: '' })
        }
      } else if (tripDetails.traveler_names && Array.isArray(tripDetails.traveler_names)) {
        // If we have traveler names, use them
        initialTravelers = tripDetails.traveler_names.map((name: string, idx: number) => ({
          name: name || '',
          age: tripDetails.ages?.[idx] || tripDetails.travelers?.[idx]?.age || 0,
          email: '',
          phone: '',
          dob: '' // NEVER auto-fill DOB
        }))
      } else {
        // Create empty slots with correct count
        initialTravelers = Array(numTravelers).fill(null).map(() => ({
          name: '',
          age: 0,
          email: '',
          phone: '',
          dob: '' // NEVER auto-fill DOB
        }))
      }
      
      setTravelers(initialTravelers)
      if (initialTravelers.length > 0) {
        setCurrentTraveler(initialTravelers[0])
        setStep(1)
      } else {
        // If no travelers, create at least one empty slot
        const emptyTraveler = { name: '', age: 0, email: '', phone: '', dob: '' }
        setTravelers([emptyTraveler])
        setCurrentTraveler(emptyTraveler)
        setStep(1)
      }
    } else if (isOpen && !tripDetails) {
      // No trip details, create single empty traveler
      const emptyTraveler = { name: '', age: 0, email: '', phone: '', dob: '' }
      setTravelers([emptyTraveler])
      setCurrentTraveler(emptyTraveler)
      setStep(1)
    }
  }, [isOpen, tripDetails])

  const handleAddTraveler = () => {
    if (currentTraveler.name && currentTraveler.age > 0 && currentTraveler.email && currentTraveler.phone) {
      const updated = [...travelers]
      // Update existing traveler if editing, otherwise add new
      if (step <= travelers.length) {
        updated[step - 1] = currentTraveler
      } else {
        updated.push(currentTraveler)
      }
      setTravelers(updated)
      
      // Calculate numTravelers for this check - check all possible sources
      const totalTravelers = (() => {
        if (!tripDetails) return Math.max(travelers.length, 1)
        if (Array.isArray(tripDetails.travelers)) {
          return tripDetails.travelers.length
        }
        if (tripDetails.traveler_names && Array.isArray(tripDetails.traveler_names)) {
          return tripDetails.traveler_names.length
        }
        if (typeof tripDetails.travelers === 'number') {
          return tripDetails.travelers
        }
        if (tripDetails.pax && typeof tripDetails.pax === 'number') {
          return tripDetails.pax
        }
        const numAdults = tripDetails.adults || 1
        const numChildren = tripDetails.children || 0
        return numAdults + numChildren
      })()
      
      if (step < totalTravelers) {
        // Move to next traveler
        setStep(step + 1)
        // Load next traveler if exists, otherwise clear
        if (updated[step]) {
          setCurrentTraveler(updated[step])
        } else {
          setCurrentTraveler({ name: '', age: 0, email: '', phone: '', dob: '' })
        }
      } else {
        // Move to payment step
        setStep(totalTravelers + 1)
      }
    }
  }
  
  useEffect(() => {
    // Pre-fill current traveler data if editing existing
    if (step <= travelers.length && travelers[step - 1]) {
      setCurrentTraveler(travelers[step - 1])
    } else if (step > travelers.length) {
      // Clear for new traveler
      setCurrentTraveler({ name: '', age: 0, email: '', phone: '', dob: '' })
    }
  }, [step, travelers])

  const handleComplete = () => {
    if (paymentInfo.cardNumber && paymentInfo.expiryDate && paymentInfo.cvv) {
      const insureds = travelers.map(t => ({
        firstName: t.name.split(' ')[0] || t.name,
        lastName: t.name.split(' ').slice(1).join(' ') || '',
        dateOfBirth: t.dob || new Date(new Date().setFullYear(new Date().getFullYear() - t.age)).toISOString().split('T')[0],
        email: t.email,
        phone: t.phone
      }))
      onComplete(insureds, paymentInfo)
      setStep(1)
      setTravelers([])
      setCurrentTraveler({ name: '', age: 0, email: '', phone: '', dob: '' })
      setPaymentInfo({ cardNumber: '', expiryDate: '', cvv: '', cardName: '' })
    }
  }

  const handleAutoFill = async () => {
    setIsAutoFilling(true)
    
    // Simulate AI auto-fill with animation
    const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
    
    // Get user data from localStorage if available
    let userData = null
    try {
      const stored = localStorage.getItem('wandersure_user_data')
      if (stored) {
        userData = JSON.parse(stored)
      }
    } catch (e) {
      console.warn('Could not parse user data:', e)
    }
    
    // Auto-fill travelers with ONLY extracted/real data - no dummy data
    const autoTravelers = travelers.map((t, idx) => {
      // Use extracted data from tripDetails if available
      const extractedName = tripDetails?.travelers?.[idx]?.name || 
                            tripDetails?.traveler_names?.[idx] || 
                            ''
      const extractedAge = tripDetails?.travelers?.[idx]?.age || 
                          tripDetails?.ages?.[idx] || 
                          0
      
      // Use real data from user profile or extracted data only
      const travelerData = userData?.travelers?.[idx] || (idx === 0 ? userData : null)
      const realName = extractedName || travelerData?.name || ''
      const realAge = extractedAge || travelerData?.age || 0
      const realEmail = travelerData?.email || ''
      const realPhone = travelerData?.phone || ''
      
      return {
        name: realName, // Only use real names, leave empty if not available
        age: realAge || 0, // Only use real ages, leave 0 if not available
        email: realEmail, // Only use real emails, leave empty if not available
        phone: realPhone, // Only use real phones, leave empty if not available
        dob: '' // NEVER auto-fill DOB/birthday
      }
    })
    
    // Fill all travelers at once (don't animate through steps)
    setTravelers(autoTravelers)
    
    // Update current traveler to first one if on first step
    if (step === 1) {
      setCurrentTraveler(autoTravelers[0] || { name: '', age: 0, email: '', phone: '', dob: '' })
    }
    
    // Fill payment info with ONLY real data - no dummy/test card data
    const realCardName = autoTravelers[0]?.name || userData?.name || userData?.travelers?.[0]?.name || ''
    // DO NOT fill card number, expiry, or CVV - these should always be entered by user
    // Only fill card name if we have real data
    setPaymentInfo({
      cardName: realCardName, // Only real name, leave empty if not available
      cardNumber: '', // NEVER auto-fill card number
      expiryDate: '', // NEVER auto-fill expiry
      cvv: '' // NEVER auto-fill CVV
    })
    
    await delay(300)
    setIsAutoFilling(false)
    
    // DO NOT automatically jump to payment page - let user fill in the blanks first
    // User can manually proceed through the steps after reviewing autofilled data
  }

  if (!isOpen) return null

  const cleanedName = cleanPolicyName(quote.plan_name)
  
  // Calculate number of travelers from tripDetails - check all possible sources
  const numTravelers = (() => {
    if (!tripDetails) return 1
    if (Array.isArray(tripDetails.travelers)) {
      return tripDetails.travelers.length
    }
    if (tripDetails.traveler_names && Array.isArray(tripDetails.traveler_names)) {
      return tripDetails.traveler_names.length
    }
    if (typeof tripDetails.travelers === 'number') {
      return tripDetails.travelers
    }
    if (tripDetails.pax && typeof tripDetails.pax === 'number') {
      return tripDetails.pax
    }
    const numAdults = tripDetails.adults || 1
    const numChildren = tripDetails.children || 0
    return numAdults + numChildren
  })()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="relative bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-2xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between border-b border-gray-700">
          <div>
            <h2 className="text-xl font-bold text-white">Purchase: {cleanedName}</h2>
            <p className="text-sm text-white/80">Step {step} of {numTravelers > travelers.length ? numTravelers + 1 : numTravelers}</p>
          </div>
          <div className="flex items-center gap-2">
            {!isAutoFilling && (
              <button 
                onClick={handleAutoFill}
                className="px-3 py-1.5 bg-white/20 hover:bg-white/30 border border-white/30 rounded-lg transition-all text-white text-xs font-semibold flex items-center gap-1.5 backdrop-blur-sm"
              >
                <Sparkles className="w-3 h-3" />
                AI Auto-Fill
              </button>
            )}
            {isAutoFilling && (
              <div className="px-3 py-1.5 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-white text-xs font-semibold flex items-center gap-1.5">
                <div className="animate-spin">
                  <Sparkles className="w-3 h-3" />
                </div>
                Auto-filling...
              </div>
            )}
            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
              <X className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {step <= numTravelers ? (
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-blue-400" />
                Traveler {step} Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Full Name *</label>
                  <input
                    type="text"
                    value={currentTraveler.name}
                    onChange={(e) => setCurrentTraveler({ ...currentTraveler, name: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Age *</label>
                  <input
                    type="number"
                    value={currentTraveler.age || ''}
                    onChange={(e) => setCurrentTraveler({ ...currentTraveler, age: parseInt(e.target.value) || 0 })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="30"
                    min="0"
                    max="120"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Email *</label>
                  <input
                    type="email"
                    value={currentTraveler.email}
                    onChange={(e) => setCurrentTraveler({ ...currentTraveler, email: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="john@example.com"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Phone *</label>
                  <input
                    type="tel"
                    value={currentTraveler.phone}
                    onChange={(e) => setCurrentTraveler({ ...currentTraveler, phone: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="+65 9123 4567"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Date of Birth *</label>
                  <input
                    type="date"
                    value={currentTraveler.dob || ''}
                    onChange={(e) => setCurrentTraveler({ ...currentTraveler, dob: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    max={new Date().toISOString().split('T')[0]}
                  />
                </div>
                <button
                  onClick={handleAddTraveler}
                  disabled={!currentTraveler.name || !currentTraveler.age || !currentTraveler.email || !currentTraveler.phone || !currentTraveler.dob}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-all"
                >
                  {step < numTravelers ? 'Next Traveler' : 'Continue to Payment'}
                </button>
              </div>
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-blue-400" />
                Payment Information
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Cardholder Name *</label>
                  <input
                    type="text"
                    value={paymentInfo.cardName}
                    onChange={(e) => setPaymentInfo({ ...paymentInfo, cardName: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 text-sm mb-2">Card Number *</label>
                  <input
                    type="text"
                    value={paymentInfo.cardNumber}
                    onChange={(e) => setPaymentInfo({ ...paymentInfo, cardNumber: e.target.value.replace(/\D/g, '').slice(0, 16) })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="1234 5678 9012 3456"
                    maxLength={16}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-300 text-sm mb-2">Expiry Date *</label>
                    <input
                      type="text"
                      value={paymentInfo.expiryDate}
                      onChange={(e) => setPaymentInfo({ ...paymentInfo, expiryDate: e.target.value.replace(/\D/g, '').slice(0, 4).replace(/(\d{2})(\d)/, '$1/$2') })}
                      className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="MM/YY"
                      maxLength={5}
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-2">CVV *</label>
                    <input
                      type="text"
                      value={paymentInfo.cvv}
                      onChange={(e) => setPaymentInfo({ ...paymentInfo, cvv: e.target.value.replace(/\D/g, '').slice(0, 4) })}
                      className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="123"
                      maxLength={4}
                    />
                  </div>
                </div>
                <div className="pt-4 border-t border-gray-700">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-gray-300">Total Amount:</span>
                    <span className="text-2xl font-bold text-blue-400">{quote.currency || 'SGD'} {quote.price.toFixed(2)}</span>
                  </div>
                  <button
                    onClick={handleComplete}
                    disabled={!paymentInfo.cardNumber || !paymentInfo.expiryDate || !paymentInfo.cvv || !paymentInfo.cardName}
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2"
                  >
                    <ShoppingCart className="w-5 h-5" />
                    Complete Purchase
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Quote Card with Purchase Button
function QuoteCard({ quote, quoteId, tripDetails, onPurchase, language = 'en' }: { 
  quote: { plan_name: string; price: number; currency: string; recommended_for: string; offer_id?: string; product_code?: string; source?: string; score?: number; benefits?: string[]; reasons?: string[]; cost_source?: string }
  quoteId?: string
  tripDetails?: any
  onPurchase: (quote: any, insureds: any[], paymentInfo: any) => void
  language?: string
}) {
  const cleanedName = cleanPolicyName(quote.plan_name)
  const [showPurchaseForm, setShowPurchaseForm] = useState(false)
  const isAncileo = quote.source === 'ancileo' || quote.offer_id
  
  // UI Translations
  const translations = {
    en: { buyNow: 'Buy Now', matchScore: 'Match Score', keyBenefits: 'Key Benefits' },
    ta: { buyNow: 'இப்போது வாங்க', matchScore: 'பொருந்தும் மதிப்பெண்', keyBenefits: 'முக்கிய நன்மைகள்' },
    zh: { buyNow: '立即购买', matchScore: '匹配分数', keyBenefits: '主要福利' },
    ms: { buyNow: 'Beli Sekarang', matchScore: 'Skor Padanan', keyBenefits: 'Faedah Utama' }
  }
  const t = translations[language as keyof typeof translations] || translations.en
  
  return (
    <>
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-5 border border-gray-700 hover:border-blue-500/50 transition-all relative">
        {/* Source Badge */}
        <div className="absolute top-3 right-3">
          {isAncileo ? (
            <span className="px-2 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-semibold rounded-full flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Ancileo
            </span>
          ) : (
            <span className="px-2 py-1 bg-gradient-to-r from-blue-600 to-cyan-600 text-white text-xs font-semibold rounded-full">
              Local
            </span>
          )}
        </div>
        
        <div className="flex items-start justify-between mb-4 pr-16">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">{cleanedName}</h3>
            <p className="text-2xl font-bold text-blue-400">
              {quote.currency || 'SGD'} {quote.price.toFixed(2)}
            </p>
          </div>
        </div>
        <p className="text-gray-400 text-sm mb-4">{quote.recommended_for}</p>
        {quote.score !== undefined && (
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">{t.matchScore}</span>
              <span className="text-sm font-semibold text-blue-400">{quote.score}/100</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all"
                style={{ width: `${quote.score}%` }}
              />
            </div>
          </div>
        )}
        {quote.benefits && quote.benefits.length > 0 && (
          <div className="mb-4">
            <p className="text-xs text-gray-400 mb-1">{t.keyBenefits}:</p>
            <ul className="text-xs text-gray-300 space-y-1">
              {quote.benefits.slice(0, 3).map((benefit: string, idx: number) => (
                <li key={idx} className="flex items-start gap-1">
                  <span className="text-blue-400 mt-0.5">•</span>
                  <span>{benefit}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        <button
          onClick={() => setShowPurchaseForm(true)}
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2"
        >
          <ShoppingCart className="w-4 h-4" />
          {t.buyNow}
        </button>
      </div>

      {showPurchaseForm && (
        <PurchaseForm
          quote={quote}
          quoteId={quoteId}
          tripDetails={tripDetails}
          isOpen={showPurchaseForm}
          onClose={() => setShowPurchaseForm(false)}
          onComplete={(insureds, paymentInfo) => {
            setShowPurchaseForm(false)
            onPurchase(quote, insureds, paymentInfo)
          }}
        />
      )}
    </>
  )
}

// Enhanced Message Renderer with cards
function EnhancedMarkdown({ content, quotes, language = 'en' }: { content: string; quotes?: any[]; language?: string }) {
  const [selectedPolicy, setSelectedPolicy] = useState<any | null>(null)
  
  // UI Translations
  const translations = {
    en: { buyNow: 'Buy Now', availablePlans: 'Available Insurance Plans', matchScore: 'Match Score', keyBenefits: 'Key Benefits', suggestedQuestions: 'Suggested Questions:' },
    ta: { buyNow: 'இப்போது வாங்க', availablePlans: 'கிடைக்கும் காப்பீட்டு திட்டங்கள்', matchScore: 'பொருந்தும் மதிப்பெண்', keyBenefits: 'முக்கிய நன்மைகள்', suggestedQuestions: 'பரிந்துரைக்கப்பட்ட கேள்விகள்:' },
    zh: { buyNow: '立即购买', availablePlans: '可用保险计划', matchScore: '匹配分数', keyBenefits: '主要福利', suggestedQuestions: '建议问题:' },
    ms: { buyNow: 'Beli Sekarang', availablePlans: 'Pelan Insurans Tersedia', matchScore: 'Skor Padanan', keyBenefits: 'Faedah Utama', suggestedQuestions: 'Cadangan Soalan:' }
  }
  const t = translations[language as keyof typeof translations] || translations.en
  
  // Extract policy mentions from text content (local policies) - only if content actually mentions policies
  const policyRegex = /(INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG|Policy:\s*[^\]]+)/gi
  const textPolicies = Array.from(new Set(
    (content.match(policyRegex)?.map(m => cleanPolicyName(m.replace(/Policy:\s*/i, '').trim())) || [])
      .filter(Boolean)
  )).map(name => ({
    name,
    isAncileo: false,
    source: 'local'
  }))
  
  // Only show policies if there are actual policy mentions OR quotes provided
  const hasPolicyContent = textPolicies.length > 0 || (quotes && quotes.length > 0)
  
  // Extract Ancileo policies from quotes
  const ancileoPolicies = (quotes || [])
    .filter(q => q.source === 'ancileo' || q.offer_id)
    .map(q => ({
      name: cleanPolicyName(q.plan_name),
      isAncileo: true,
      source: 'ancileo',
      quote: q,
      productCode: q.product_code,
      offerId: q.offer_id
    }))
  
  // Combine all policies, removing duplicates (prioritize Ancileo)
  const allPoliciesMap = new Map<string, any>()
  
  // First add text policies
  textPolicies.forEach(p => {
    if (!allPoliciesMap.has(p.name.toLowerCase())) {
      allPoliciesMap.set(p.name.toLowerCase(), p)
    }
  })
  
  // Then add/override with Ancileo policies
  ancileoPolicies.forEach(p => {
    allPoliciesMap.set(p.name.toLowerCase(), p)
  })
  
  const policies = Array.from(allPoliciesMap.values())
  
  return (
    <>
      <ReactMarkdown
        components={{
          p: ({ children }) => (
            <p className="mb-4 text-gray-200 leading-relaxed font-normal text-[15px]">
              {children}
            </p>
          ),
          strong: ({ children }) => {
            const text = String(children)
            const policyMatch = text.match(/(INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG|Policy:?\s*[^\]\s]+)/i)
            
            if (policyMatch) {
              const policyName = policyMatch[1].replace(/Policy:\s*/i, '').trim()
              
              // Check if this policy is from Ancileo quotes
              const ancileoQuote = quotes?.find(q => cleanPolicyName(q.plan_name) === cleanPolicyName(policyName))
              
              return (
                <button
                  onClick={() => setSelectedPolicy({
                    name: policyName,
                    isAncileo: !!ancileoQuote,
                    productCode: ancileoQuote?.product_code,
                    offerId: ancileoQuote?.offer_id,
                    quoteId: quotes?.[0]?.quote_id || quotes?.find((q: any) => q.quote_id)?.quote_id
                  })}
                  className={`font-semibold px-2 py-1 rounded-md transition-all border shadow-sm hover:shadow-md hover:scale-105 inline-flex items-center gap-1 ${
                    ancileoQuote 
                      ? 'text-purple-300 bg-purple-900/40 border-purple-700/40 hover:bg-purple-900/60' 
                      : 'text-blue-400 bg-blue-900/40 border-blue-700/40 hover:bg-blue-900/60'
                  }`}
                >
                  {children}
                  {ancileoQuote && <Sparkles className="w-3 h-3 text-purple-300" />}
                  {!ancileoQuote && <ExternalLink className="w-3 h-3" />}
                </button>
              )
            }
            
            return (
              <strong className="text-blue-300 font-semibold bg-gradient-to-r from-blue-400/20 to-purple-400/20 px-1.5 py-0.5 rounded">
                {children}
              </strong>
            )
          },
          em: ({ children }) => (
            <em className="text-gray-300 italic">{children}</em>
          ),
          ul: ({ children }) => (
            <ul className="mb-4 space-y-2 list-none pl-0 my-4">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-4 space-y-2 list-decimal pl-6 my-4">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start gap-3 text-gray-200 mb-3 leading-relaxed">
              <span className="text-blue-400 mt-1.5 flex-shrink-0 font-bold text-lg">•</span>
              <span className="flex-1 text-[15px] font-normal">{children}</span>
            </li>
          ),
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-white mb-5 mt-8 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-bold text-white mb-4 mt-7 first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold text-gray-100 mb-3 mt-6 first:mt-0">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-lg font-semibold text-gray-200 mb-3 mt-5 first:mt-0">{children}</h4>
          ),
          hr: () => null, // Remove separators - use font size instead
          code: ({ children }) => (
            <code className="bg-gray-700/50 text-blue-300 px-2 py-1 rounded text-sm font-mono border border-blue-500/20">
              {children}
            </code>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-300 my-4 bg-blue-500/5 py-2 rounded-r">
              {children}
            </blockquote>
          )
        }}
      >
        {content}
      </ReactMarkdown>
      
      {/* Policy Cards Section - Including Ancileo Policies - Only show if policies are mentioned */}
      {hasPolicyContent && policies.length > 0 && (
        <div className="mt-8 pt-6">
          <div className="mb-5">
            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-400" />
              Referenced Policies
            </h3>
            <p className="text-gray-400 text-sm">
              {ancileoPolicies.length > 0 && (
                <span className="inline-flex items-center gap-1 text-purple-300">
                  <Sparkles className="w-3 h-3" />
                  {ancileoPolicies.length} Ancileo {ancileoPolicies.length === 1 ? 'policy' : 'policies'} available
                </span>
              )}
              {ancileoPolicies.length > 0 && textPolicies.length > 0 && <span className="mx-2">•</span>}
              {textPolicies.length > 0 && (
                <span className="text-blue-300">{textPolicies.length} Local {textPolicies.length === 1 ? 'policy' : 'policies'}</span>
              )}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {policies.map((policy, idx) => (
              <PolicyCard
                key={idx}
                policyName={typeof policy === 'string' ? policy : policy.name}
                isAncileo={typeof policy === 'object' ? policy.isAncileo : false}
                source={typeof policy === 'object' ? policy.source : 'local'}
                onClick={() => setSelectedPolicy(typeof policy === 'object' ? {
                  name: policy.name,
                  isAncileo: policy.isAncileo,
                  productCode: policy.productCode,
                  offerId: policy.offerId,
                  quoteId: quotes?.[0]?.quote_id
                } : policy)}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Policy Modal */}
      {selectedPolicy && (
        <PolicyModal
          policyName={typeof selectedPolicy === 'string' ? selectedPolicy : selectedPolicy.name}
          isOpen={!!selectedPolicy}
          onClose={() => setSelectedPolicy(null)}
          productCode={typeof selectedPolicy === 'object' ? selectedPolicy.productCode : undefined}
          offerId={typeof selectedPolicy === 'object' ? selectedPolicy.offerId : undefined}
          quoteId={typeof selectedPolicy === 'object' ? selectedPolicy.quoteId : undefined}
        />
      )}
    </>
  )
}

// Policy Tooltip Component with Enhanced Details
function PolicyTooltip({ policyName, children }: { policyName: string; children: React.ReactNode }) {
  const [showTooltip, setShowTooltip] = useState(false)
  const [policyDetails, setPolicyDetails] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  const handleMouseEnter = async () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    
    timeoutRef.current = setTimeout(async () => {
      setShowTooltip(true)
      if (!policyDetails && !isLoading) {
        setIsLoading(true)
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/api/policy/details?policy_name=${encodeURIComponent(policyName)}`)
          const data = await response.json()
          if (data.success) {
            setPolicyDetails(data.summary)
          } else {
            setPolicyDetails(`Policy: ${policyName}\n\nTravel insurance policy. Hover to learn more.`)
          }
        } catch (error) {
          console.error('Failed to load policy details:', error)
          // Try with cleaned name
          const cleaned = cleanPolicyName(policyName)
          if (cleaned && cleaned !== policyName) {
            try {
              const retryResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/api/policy/details?policy_name=${encodeURIComponent(cleaned)}`)
              const retryData = await retryResponse.json()
              if (retryData.success) {
                setPolicyDetails(retryData.summary)
              } else {
                setPolicyDetails(`Policy: ${policyName}\n\nUnable to load policy details. Please try again later.`)
              }
            } catch (retryError) {
              setPolicyDetails(`Policy: ${policyName}\n\nUnable to load policy details. Please try again later.`)
            }
          } else {
            setPolicyDetails(`Policy: ${policyName}\n\nUnable to load policy details. Please try again later.`)
          }
        } finally {
          setIsLoading(false)
        }
      }
    }, 300)
  }

  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setShowTooltip(false)
  }

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  return (
    <span 
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {children}
      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-96 bg-gray-800 border border-gray-600 rounded-lg shadow-2xl p-4 animate-fade-in max-h-96 overflow-y-auto">
          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-3 h-3 bg-gray-800 border-r border-b border-gray-600"></div>
          {isLoading ? (
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <div className="w-4 h-4 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
              <span>Loading policy details...</span>
            </div>
          ) : (
            <div className="text-gray-200 text-sm whitespace-pre-wrap leading-relaxed">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 font-normal text-[14px]" style={{ lineHeight: '1.6' }}>{children}</p>,
                  ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1.5">{children}</ul>,
                  li: ({ children }) => <li className="text-gray-300 font-normal text-[14px]" style={{ lineHeight: '1.6' }}>{children}</li>,
                  strong: ({ children }) => <strong className="text-blue-400 font-semibold">{children}</strong>,
                  hr: () => <hr className="my-2 border-gray-700" />
                }}
              >
                {policyDetails || 'Loading policy details...'}
              </ReactMarkdown>
            </div>
          )}
        </div>
      )}
    </span>
  )
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  booking_links?: Array<{ type: string; platform: string; url: string; text: string }>
  suggested_questions?: Array<{ question: string; icon: string; priority: string }>
  quotes?: Array<{ plan_name: string; price: number; currency: string; recommended_for: string; source?: string; offer_id?: string; product_code?: string; score?: number; benefits?: string[]; reasons?: string[]; cost_source?: string }>
  quote_id?: string
  trip_details?: any
}

interface ConversationThread {
  id: string
  title: string
  lastMessage: string
  timestamp: Date
  role: string
  messageCount: number
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [language, setLanguage] = useState('en') // For UI translations only - Google Translate handles page translation
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [showHistory, setShowHistory] = useState(true)
  const [conversationThreads, setConversationThreads] = useState<ConversationThread[]>([])
  const [currentThreadId, setCurrentThreadId] = useState<string>('default')
  const [editingThreadId, setEditingThreadId] = useState<string | null>(null)
  const [editingThreadTitle, setEditingThreadTitle] = useState<string>('')
  // Removed manual language selector - using Google Translate only
  // FORCE onboarding to show by default - will only hide if data is 100% complete
  const [showOnboarding, setShowOnboarding] = useState(true)
  const [userData, setUserData] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<any>(null)
  const onboardingCheckedRef = useRef<boolean>(false) // Track if we've already checked
  // Auto-detect API URL - try 8002 first (backend default), fallback to 8003, then 8004
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'
  
  // Language options
  const languages = [
    { code: 'en', name: 'English', native: 'English', emoji: '🇬🇧' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்', emoji: '🇮🇳' },
    { code: 'zh', name: 'Chinese', native: '中文', emoji: '🇨🇳' },
    { code: 'ms', name: 'Malay', native: 'Bahasa Melayu', emoji: '🇲🇾' }
  ]

  // UI Translations
  const translations = {
    en: {
      buyNow: 'Buy Now',
      availablePlans: 'Available Insurance Plans',
      matchScore: 'Match Score',
      keyBenefits: 'Key Benefits',
      suggestedQuestions: 'Suggested Questions:'
    },
    ta: {
      buyNow: 'இப்போது வாங்க',
      availablePlans: 'கிடைக்கும் காப்பீட்டு திட்டங்கள்',
      matchScore: 'பொருந்தும் மதிப்பெண்',
      keyBenefits: 'முக்கிய நன்மைகள்',
      suggestedQuestions: 'பரிந்துரைக்கப்பட்ட கேள்விகள்:'
    },
    zh: {
      buyNow: '立即购买',
      availablePlans: '可用保险计划',
      matchScore: '匹配分数',
      keyBenefits: '主要福利',
      suggestedQuestions: '建议问题:'
    },
    ms: {
      buyNow: 'Beli Sekarang',
      availablePlans: 'Pelan Insurans Tersedia',
      matchScore: 'Skor Padanan',
      keyBenefits: 'Faedah Utama',
      suggestedQuestions: 'Cadangan Soalan:'
    }
  }

  const t = translations[language as keyof typeof translations] || translations.en

  // Load chat history from localStorage and remove duplicates
  useEffect(() => {
    const savedThreads = localStorage.getItem('wandersure_conversation_threads')
    if (savedThreads) {
      try {
        const threads = JSON.parse(savedThreads)
        
        // Remove duplicates based on thread ID (keep first occurrence)
        const uniqueThreads = threads.filter((t: any, index: number, self: any[]) => 
          index === self.findIndex((t2: any) => t2.id === t.id)
        )
        
        // If duplicates were found, update localStorage
        if (uniqueThreads.length !== threads.length) {
          console.log(`🧹 Cleaned up ${threads.length - uniqueThreads.length} duplicate threads`)
          localStorage.setItem('wandersure_conversation_threads', JSON.stringify(uniqueThreads))
        }
        
        setConversationThreads(uniqueThreads.map((t: any) => ({
          ...t,
          timestamp: new Date(t.timestamp),
        })))
      } catch (e) {
        console.error('Failed to load conversation threads:', e)
      }
    }
  }, [])

  // Helper function to generate a better chat title
  const generateChatTitle = (messages: Message[]): string => {
    if (messages.length === 0) return 'New Chat'
    
    // Skip greeting messages and find first meaningful message
    const greetingPatterns = [
      /^👋\s*Welcome/i,
      /^👋\s*Hi/i,
      /Welcome!.*Travel/i,
      /I'm Wanda/i
    ]
    
    // Find first user message or first non-greeting assistant message
    let titleMessage = null
    for (const msg of messages) {
      if (msg.role === 'user') {
        titleMessage = msg
        break
      } else if (msg.role === 'assistant' && !greetingPatterns.some(pattern => pattern.test(msg.content))) {
        titleMessage = msg
        break
      }
    }
    
    // If no good message found, use first message but clean it up
    if (!titleMessage) {
      titleMessage = messages[0]
    }
    
    // Extract title from message content
    let title = titleMessage.content
      .replace(/[#*━]/g, '') // Remove markdown
      .replace(/👋/g, '') // Remove emojis that might cause issues
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold markers but keep text
      .replace(/\[IMAGE:[^\]]+\]/g, '') // Remove image tags
      .replace(/\n+/g, ' ') // Replace newlines with spaces
      .trim()
    
    // Take first 40 characters and try to end at word boundary
    if (title.length > 40) {
      title = title.substring(0, 40)
      const lastSpace = title.lastIndexOf(' ')
      if (lastSpace > 20) {
        title = title.substring(0, lastSpace)
      }
      title += '...'
    }
    
    // If still empty or just greeting, use default
    if (!title || title.length < 3 || greetingPatterns.some(pattern => pattern.test(title))) {
      // Try to extract from trip details if available
      const tripDetails = messages.find(m => m.trip_details)?.trip_details
      if (tripDetails?.destination) {
        return `Trip to ${tripDetails.destination}`
      }
      return 'New Chat'
    }
    
    return title || 'New Chat'
  }

  // Track saved threads to prevent duplicates
  const lastSavedStateRef = useRef<{ threadId: string; messageCount: number } | null>(null)
  
  // Save conversation threads - but only update existing, don't create duplicates
  useEffect(() => {
    // Skip if creating new chat, no messages, or default thread
    if (messages.length === 0 || isCreatingNewChatRef.current || currentThreadId === 'default') {
      return
    }
    
    // Don't save if we just saved this exact state (prevent duplicate saves)
    if (lastSavedStateRef.current?.threadId === currentThreadId && 
        lastSavedStateRef.current?.messageCount === messages.length) {
      return
    }
    
    const lastMessage = messages[messages.length - 1]
    const title = generateChatTitle(messages)
    
    // Don't save empty or greeting-only chats (wait for user interaction)
    if (title === 'New Chat' && messages.length === 1 && messages[0].role === 'assistant') {
      return
    }
    
    const thread: ConversationThread = {
      id: currentThreadId,
      title: title,
      lastMessage: lastMessage.content.substring(0, 80).replace(/[#*━]/g, '').trim(),
      timestamp: lastMessage.timestamp,
      role: 'travel_agent', // Default role for compatibility
      messageCount: messages.length,
    }

    setConversationThreads(prev => {
      // Remove any existing threads with this ID first (prevent duplicates)
      const filtered = prev.filter(t => t.id !== currentThreadId)
      
      // Check localStorage for duplicates too
      const storedThreads = JSON.parse(localStorage.getItem('wandersure_conversation_threads') || '[]')
      const cleanedStored = storedThreads.filter((t: any) => t.id !== currentThreadId)
      
      // Add thread to front, remove duplicates, limit to 20
      const updated = [thread, ...filtered]
      const unique = updated.filter((t, idx, arr) => arr.findIndex(t2 => t2.id === t.id) === idx)
      const limited = unique.slice(0, 20)
      
      // Save to localStorage
      localStorage.setItem('wandersure_conversation_threads', JSON.stringify(limited.map(t => ({
        ...t,
        timestamp: t.timestamp.toISOString()
      }))))
      
      // Track what we just saved
      lastSavedStateRef.current = { threadId: currentThreadId, messageCount: messages.length }
      
      return limited
    })
  }, [messages.length, currentThreadId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize greeting only once on mount, but only if onboarding is not active
  useEffect(() => {
    // Wait a bit to ensure onboarding check has run first
    const timer = setTimeout(() => {
      if (!showOnboarding) {
        initializeGreeting()
      }
    }, 200)
    
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showOnboarding])
  
  // Check onboarding status ONCE on mount - use ref to prevent multiple checks
  useEffect(() => {
    // Only check once
    if (onboardingCheckedRef.current) {
      console.log('⏭️ Skipping onboarding check - already checked')
      return
    }
    
    onboardingCheckedRef.current = true
    console.log('🔍 Onboarding check on mount (FIRST TIME ONLY)...')
    
    // Add a small delay to ensure component is fully mounted
    const checkTimer = setTimeout(() => {
      const hasOnboarded = localStorage.getItem('wandersure_onboarded')
      const savedUserData = localStorage.getItem('wandersure_user_data')
      
      console.log('🔍 Found in localStorage:', { hasOnboarded, hasUserData: !!savedUserData })
      
      // ONLY hide if we have BOTH flag AND complete valid data
      if (hasOnboarded === 'true' && savedUserData) {
        try {
          const parsed = JSON.parse(savedUserData)
          console.log('🔍 Parsed data:', parsed)
          
          // Check if data has travelers array (new structure) or old structure
          const hasTravelersArray = Array.isArray(parsed.travelers) && parsed.travelers.length > 0
          const hasOldStructure = parsed.age && typeof parsed.age === 'number' && parsed.age > 0 && parsed.age <= 120 && Array.isArray(parsed.interests) && parsed.interests.length > 0
          
          // Validate travelers array structure if present
          let hasValidTravelers = false
          if (hasTravelersArray) {
            hasValidTravelers = parsed.travelers.every((t: any) => 
              t.age && typeof t.age === 'number' && t.age > 0 && t.age <= 120 &&
              Array.isArray(t.interests) && t.interests.length > 0
            )
          }
          
          console.log('🔍 Validation:', { hasTravelersArray, hasValidTravelers, hasOldStructure, travelers: parsed.travelers })
          
          if (hasValidTravelers || hasOldStructure) {
            // Data is 100% complete - hide onboarding
            setUserData(parsed)
            setShowOnboarding(false)
            console.log('✅ Hiding onboarding - data is complete')
          } else {
            // Data incomplete - CLEAR everything and FORCE show onboarding
            localStorage.removeItem('wandersure_onboarded')
            localStorage.removeItem('wandersure_user_data')
            setShowOnboarding(true)
            console.log('⚠️ FORCE showing onboarding - data incomplete, cleared all data')
          }
        } catch (e) {
          // Invalid data - FORCE show onboarding and clear everything
          localStorage.removeItem('wandersure_onboarded')
          localStorage.removeItem('wandersure_user_data')
          setShowOnboarding(true)
          console.log('⚠️ FORCE showing onboarding - parse error, cleared storage:', e)
        }
      } else {
        // No data - CLEAR any partial data and FORCE show onboarding
        localStorage.removeItem('wandersure_onboarded')
        localStorage.removeItem('wandersure_user_data')
        setShowOnboarding(true)
        console.log('⚠️ FORCE showing onboarding - no data found, cleared any partial data')
      }
    }, 100) // Small delay to ensure component is ready
    
    return () => clearTimeout(checkTimer)
  }, []) // Run ONLY once on mount
  
  // REMOVED: Watch effect that was causing popup to disappear
  // The validation now only happens on mount, and the popup will stay open
  // until the user explicitly completes the onboarding via handleOnboardingComplete

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  // Handle user onboarding completion
  const handleOnboardingComplete = (userData: any) => {
    setUserData(userData)
    setShowOnboarding(false)
    
    const welcomeMsg: Message = {
      role: 'assistant',
      content: `🎉 **Welcome!**\n\n✅ Your profile has been saved\n${userData.interests?.length > 0 ? `🎯 Interests: ${userData.interests.slice(0, 5).join(', ')}` : ''}\n\nReady to find the perfect travel insurance? Upload your travel itinerary to get started!`,
      timestamp: new Date()
    }
    setMessages([welcomeMsg])
  }
  
  const handleSkipOnboarding = () => {
    // Don't allow skipping - user must complete onboarding
    // Show alert to guide them
    alert('Please complete the onboarding to get personalized recommendations. You can select "None" for medical conditions if you don\'t have any.')
    // Keep modal open - don't hide it
  }

  // Clear all chat history
  const clearChatHistory = () => {
    if (window.confirm('Are you sure you want to delete all chat history? This action cannot be undone.')) {
      setConversationThreads([])
      localStorage.removeItem('wandersure_conversation_threads')
      // Also clear all thread messages
      const keys = Object.keys(localStorage)
      keys.forEach(key => {
        if (key.startsWith('wandersure_thread_')) {
          localStorage.removeItem(key)
        }
      })
      // Reset to default thread
      setCurrentThreadId('default')
      setMessages([])
      initializeGreeting()
    }
  }

  // Rename thread
  const renameThread = (threadId: string, newTitle: string) => {
    if (!newTitle.trim()) {
      setEditingThreadId(null)
      return
    }
    
    setConversationThreads(prev => prev.map(t => 
      t.id === threadId ? { ...t, title: newTitle.trim() } : t
    ))
    
    // Update in localStorage
    const threads = JSON.parse(localStorage.getItem('wandersure_conversation_threads') || '[]')
    const updatedThreads = threads.map((t: any) => 
      t.id === threadId ? { ...t, title: newTitle.trim() } : t
    )
    localStorage.setItem('wandersure_conversation_threads', JSON.stringify(updatedThreads))
    
    setEditingThreadId(null)
    setEditingThreadTitle('')
  }
  
  // Start editing thread title
  const startEditingThread = (thread: ConversationThread, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent thread loading
    setEditingThreadId(thread.id)
    setEditingThreadTitle(thread.title)
  }
  
  // Load conversation thread
  const loadThread = (threadId: string) => {
    // Save current messages before switching
    if (messages.length > 0 && currentThreadId) {
      localStorage.setItem(`wandersure_thread_${currentThreadId}`, JSON.stringify(
        messages.map(m => ({ ...m, timestamp: m.timestamp.toISOString() }))
      ))
    }
    
    setCurrentThreadId(threadId)
    
    // Load messages from localStorage
    const savedMessages = localStorage.getItem(`wandersure_thread_${threadId}`)
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        setMessages(parsed.map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp)
        })))
      } catch (e) {
        console.error('Failed to load thread messages:', e)
        setMessages([])
        initializeGreeting()
      }
    } else {
      // If no saved messages, start fresh
      setMessages([])
      initializeGreeting()
    }
  }
  
  // Track if new chat is being created to prevent duplicates
  const isCreatingNewChatRef = useRef(false)
  const [isCreatingNewChat, setIsCreatingNewChatState] = useState(false)
  
  // Create new chat
  const createNewChat = useCallback(() => {
    // Prevent duplicate creation using ref (more reliable than state)
    if (isCreatingNewChatRef.current) {
      console.log('⏭️ Already creating new chat, skipping duplicate request')
      return
    }
    
    isCreatingNewChatRef.current = true
    setIsCreatingNewChatState(true)
    
    // Save current messages to thread storage BEFORE switching (synchronous save)
    if (messages.length > 0 && currentThreadId && currentThreadId !== 'default') {
      try {
        // Save messages immediately before state changes
        const messagesToSave = messages.map(m => ({ ...m, timestamp: m.timestamp.toISOString() }))
        localStorage.setItem(`wandersure_thread_${currentThreadId}`, JSON.stringify(messagesToSave))
        console.log(`💾 Saved ${messages.length} messages to thread ${currentThreadId}`)
      } catch (error) {
        console.error('Failed to save messages before switching:', error)
      }
      
      // The useEffect will handle saving to threads list automatically
      // Don't manually add here to avoid duplicates
    }
    
    // Create unique thread ID using timestamp + random number to avoid collisions
    // Use performance.now() for better precision
    const timestamp = Date.now()
    const random = Math.random().toString(36).substring(2, 9)
    const newThreadId = `thread_${timestamp}_${random}`
    
    // Reset state for new chat - trigger onboarding popup for new chat
    // IMPORTANT: Clear messages AFTER saving to prevent loss
    setMessages([])
    setCurrentThreadId(newThreadId)
    
    // Reset saved state tracking
    lastSavedStateRef.current = null
    
    // Clear onboarding flag to show popup for new chat
    localStorage.removeItem('wandersure_onboarded')
    setShowOnboarding(true)
    
    // Reset creating flag after a delay (allows useEffect to process)
    setTimeout(() => {
      isCreatingNewChatRef.current = false
      setIsCreatingNewChatState(false)
    }, 2000) // Increased delay to ensure useEffect completes and prevents rapid clicks
    
    // Don't initialize greeting immediately - wait for onboarding
    // initializeGreeting()
  }, [messages, currentThreadId])

  // Save messages to localStorage when they change
  useEffect(() => {
    if (messages.length > 0 && currentThreadId && currentThreadId !== 'default') {
      localStorage.setItem(`wandersure_thread_${currentThreadId}`, JSON.stringify(
        messages.map(m => ({ ...m, timestamp: m.timestamp.toISOString() }))
      ))
    }
  }, [messages, currentThreadId])
  
  // Google Translate handles everything - no custom translation needed
  useEffect(() => {
    // Load Google Translate script dynamically
    if (typeof window !== 'undefined') {
      // Declare function globally
      (window as any).loadGoogleTranslate = function() {
        if (typeof google !== 'undefined' && google.translate && google.translate.TranslateElement) {
          new google.translate.TranslateElement({
            pageLanguage: 'en',
            includedLanguages: 'en,ta,zh-CN,ms-MY',
            layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
            autoDisplay: false
          }, 'google_translate_element');
        }
      }
      
      // Load the script if not already loaded
      if (!document.querySelector('script[src*="translate.google.com"]')) {
        const script = document.createElement('script');
        script.src = '//translate.google.com/translate_a/element.js?cb=loadGoogleTranslate';
        script.async = true;
        document.body.appendChild(script);
      } else if ((window as any).loadGoogleTranslate) {
        // Script already loaded, just call it
        (window as any).loadGoogleTranslate();
      }
    }
  }, [])

  const initializeGreeting = async () => {
    // Don't show greeting if onboarding is active - wait for user to complete onboarding
    if (showOnboarding) {
      console.log('⏸️ Greeting skipped - onboarding is active')
      return
    }
    
    // Set initial greeting immediately so user sees something
    if (messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: "### 👋 Welcome! I'm Wanda, Your Travel Insurance Agent\n\n• Expert travel insurance advice\n• Compare policies instantly\n• Get quotes in seconds\n\nHow can I help protect your trip? ✈️",
        timestamp: new Date()
      }])
    }
    
    // Try to fetch personalized greeting from API
    try {
      const response = await fetch(`${API_URL}/api/greeting?user_id=user_${Date.now()}&language=${language}`)
      if (response.ok) {
        const data = await response.json()
        if (data.greeting) {
      setMessages([{
        role: 'assistant',
            content: data.greeting,
        timestamp: new Date()
      }])
        }
      }
    } catch (error) {
      // Keep the default greeting if API fails
      console.log('Greeting API not available, using default')
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setIsLoading(true)

    try {
      // Get latest quotes and trip details from messages for context
      const latestQuoteData = messages
        .filter((m: Message) => m.quotes && m.quotes.length > 0)
        .slice(-1)[0]
      
      const latestTripDetails = messages
        .filter((m: Message) => m.trip_details)
        .slice(-1)[0]?.trip_details
      
      const contextData: any = {}
      if (latestQuoteData?.quotes) {
        contextData.quotes = latestQuoteData.quotes
        contextData.trip_details = latestQuoteData.trip_details || latestTripDetails
      } else if (latestTripDetails) {
        contextData.trip_details = latestTripDetails
      }
      
      const response = await fetch(`${API_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentInput,
          language: language,
          user_id: userData?.user_id || 'default_user',
          is_voice: false,
          context_data: {
            ...contextData,
            user_data: userData  // Pass user data (age, interests, medical conditions)
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const answerText = typeof data === 'string' ? data : (data.answer || data.message || data.content || 'I apologize, but I encountered an error.')
      
      // Add claims data to message if available
      let finalContent = answerText
      if (data.claims_analysis && data.claims_analysis.has_data) {
        const claims = data.claims_analysis
        if (claims.recommendations && claims.recommendations.length > 0) {
          const top = claims.recommendations[0]
          const claimsSection = `\n\n### 🎯 Claims Insights for ${claims.destination || 'Your Destination'}\n\n**${top.incidence_rate || 'N/A'}** of travelers have claimed for **${top.claim_type || 'incidents'}** with an average cost of **$${top.average_cost?.toFixed(2) || '0.00'} SGD**.\n\nWould you like to purchase insurance to specifically cover this highly likely incident?`
          finalContent = claimsSection + '\n\n' + answerText
        }
      }
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: finalContent,
        timestamp: new Date(),
        booking_links: data.booking_links || [],
        suggested_questions: data.suggested_questions || [],
        quotes: data.quotes || [],
        quote_id: data.quote_id || null,
        trip_details: data.trip_details || null
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (isSpeaking) {
        speakText(answerText)
      }
    } catch (error: any) {
      console.error('Error:', error)
      
      // Provide helpful error messages based on error type
      let errorContent = ''
      if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        errorContent = '**🌐 Connection Issue**\n\n• I\'m having trouble connecting to the server\n• Please check your internet connection\n• The server might be restarting - try again in a moment'
      } else if (error.message?.includes('status') || error.message?.includes('HTTP')) {
        errorContent = '**⚠️ Server Error**\n\n• The server is experiencing issues\n• This is usually temporary\n• Please try again in a moment, or try rephrasing your question'
      } else {
        errorContent = '**😅 Oops!**\n\n• I encountered an issue processing your question\n• But don\'t worry - I\'m here to help!\n\n**Try:**\n• Rephrasing your question\n• Asking something simpler like "What can you help me with?"\n• Or just say "hi" to start fresh'
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    setIsUploading(true)
    setUploadedFile(file)
    
    // First, test server connection
    console.log('🔍 Testing server connection...')
    try {
      const testHealth = await fetch('http://localhost:8002/health', {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      })
      if (testHealth.ok) {
        console.log('✅ Server connection test passed!')
      } else {
        console.warn('⚠️ Server health check returned non-OK status:', testHealth.status)
      }
    } catch (testError: any) {
      console.error('❌ Server connection test failed:', testError.message)
      // Don't fail here, continue to try extract
    }
    
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target?.result as string
      
      try {
        // Try both ports if default fails
        let extractResponse: Response | undefined
        let lastError: any = null
        
        const portsToTry = [8002, 8003, 8004]
        let triedPorts: number[] = []
        
        for (const port of portsToTry) {
          const testUrl = `http://localhost:${port}`
          triedPorts.push(port)
          
          try {
            console.log(`🔌 Attempting connection to ${testUrl}/api/extract`)
            
            // First verify server is reachable with a quick health check
            try {
              const healthResponse = await fetch(`${testUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
              })
              if (!healthResponse.ok) {
                console.log(`⚠️ Health check failed for port ${port}, trying next...`)
                continue
              }
              console.log(`✅ Health check passed for port ${port}`)
            } catch (healthError: any) {
              console.log(`⚠️ Health check error for port ${port}:`, healthError.message)
              continue
            }
            
            // Server is reachable, try the extract endpoint
            console.log(`📤 Sending extract request to port ${port}...`)
            extractResponse = await fetch(`${testUrl}/api/extract`, {
              method: 'POST',
              headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
              },
              body: JSON.stringify({
                document_data: base64,
                document_type: file.type.includes('pdf') ? 'pdf' : file.type.includes('image') ? 'image' : 'text'
              }),
              signal: AbortSignal.timeout(60000) // 60 second timeout for document processing
            })
            
            console.log(`✅ Successfully connected to port ${port}! Status: ${extractResponse.status}`)
            break
            
          } catch (fetchError: any) {
            lastError = fetchError
            console.error(`❌ Port ${port} connection failed:`, {
              message: fetchError.message,
              name: fetchError.name,
              stack: fetchError.stack?.substring(0, 200)
            })
            continue
          }
        }
        
        if (!extractResponse) {
          const errorDetails = lastError ? ` Last error: ${lastError.message}` : ''
          console.error('❌ All ports failed:', triedPorts, errorDetails)
          throw new Error(`Cannot connect to backend server on ports ${triedPorts.join(', ')}.${errorDetails} Make sure the server is running with: PORT=8002 python3 run_server.py`)
        }
        
        if (!extractResponse.ok) {
          throw new Error(`Extract failed: ${extractResponse.status} ${extractResponse.statusText}`)
        }
        
        const extractData = await extractResponse.json()
        console.log('Extract response:', extractData)
        
        if (extractData.success && extractData.extracted_data) {
          const tripInfo = extractData.extracted_data
          const claimsData = extractData.claims_analysis
          
          // Use the working port from extract (or fallback to API_URL)
          const workingPort = extractResponse.url.match(/localhost:(\d+)/)?.[1] || '8002'
          const quoteUrl = `http://localhost:${workingPort}/api/quote`
          console.log(`📤 Requesting quotes from: ${quoteUrl}`)
          const quoteResponse = await fetch(quoteUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              destination: tripInfo.destination || 'Unknown',
              source: tripInfo.source,
              start_date: tripInfo.departure_date || tripInfo.start_date,
              end_date: tripInfo.return_date || tripInfo.end_date,
              travelers: tripInfo.pax || tripInfo.travelers?.length || 1,
              ages: tripInfo.travelers?.map((t: any) => t.age).filter(Boolean) || [],
              activities: tripInfo.activities || [],
              trip_cost: tripInfo.trip_cost,
              ticket_policies: tripInfo.ticket_policies || [],
              extracted_data: tripInfo,
              // User data from onboarding
              user_age: userData?.age,
              interests: userData?.interests || [],
              medical_conditions: userData?.medical_conditions || []
            })
          })
          
          const quoteData = await quoteResponse.json()
          console.log('📊 Quote Response:', quoteData)
          console.log('📋 Quotes received:', quoteData.quotes?.map((q: any) => q.plan_name))
          
          // Build claims insights message
          let claimsSection = ''
          if (claimsData && claimsData.has_data && claimsData.recommendations && claimsData.recommendations.length > 0) {
            const topRec = claimsData.recommendations[0]
            const topClaimType = topRec.claim_type || 'incidents'
            const incidenceRate = topRec.incidence_rate || '0%'
            const avgCost = topRec.average_cost || 0
            
            claimsSection = `\n\n### 🎯 Claims Insights for ${tripInfo.destination || 'Your Destination'}\n\nBased on historical claims data:\n\n**${incidenceRate} of travelers** have claimed for **${topClaimType}** incidents with an average cost of **$${avgCost.toFixed(2)} SGD**.\n\nWould you like to purchase insurance to specifically cover this highly likely incident?`
            
            // Add other common incidents if available
            if (claimsData.common_incidents && claimsData.common_incidents.length > 1) {
              const otherIncidents = claimsData.common_incidents.slice(1, 3).map((inc: any) => 
                `${inc.incident} (${inc.percentage}%)`
              ).join(', ')
              if (otherIncidents) {
                claimsSection += `\n\nOther common incidents include: ${otherIncidents}.`
              }
            }
          }
          
          // Verify we have the right quotes from Policy_Wordings
          const quotes = quoteData.quotes || []
          const hasGenericNames = quotes.some((q: any) => 
            ['Basic', 'Standard', 'Premium'].includes(q.plan_name)
          )
          
          if (hasGenericNames) {
            console.error('❌ ERROR: Received generic policy names from API!', quotes.map((q: any) => q.plan_name))
          } else {
            console.log('✅ Received Policy_Wordings policies:', quotes.map((q: any) => q.plan_name))
          }
          
          // Build traveler names list - check ALL possible sources
          let travelersInfo = ''
          
          // Helper to clean names (remove repeated characters)
          const cleanName = (name: string) => {
            if (!name) return ''
            // Remove repeated character patterns like "MMMMssss" -> "Ms"
            return name.replace(/(.)\1{2,}/g, '$1').trim()
          }
          
          // Try travelers array first
          if (tripInfo.travelers && Array.isArray(tripInfo.travelers) && tripInfo.travelers.length > 0) {
            const names = tripInfo.travelers
              .map((t: any) => cleanName(t?.name || ''))
              .filter((name: string) => name.trim().length > 0)
            if (names.length > 0) {
              travelersInfo = `\n• Travelers (${names.length}): ${names.join(', ')}`
            }
          }
          
          // If no names from travelers array, try traveler_names
          if (!travelersInfo && tripInfo.traveler_names && Array.isArray(tripInfo.traveler_names) && tripInfo.traveler_names.length > 0) {
            const cleanedNames = tripInfo.traveler_names
              .map((name: string) => cleanName(name))
              .filter((name: string) => name.trim().length > 0)
            if (cleanedNames.length > 0) {
              travelersInfo = `\n• Travelers (${cleanedNames.length}): ${cleanedNames.join(', ')}`
            }
          }
          
          // If still no names, show count
          if (!travelersInfo) {
            const numTravelers = tripInfo.pax || 
                                 (Array.isArray(tripInfo.travelers) ? tripInfo.travelers.length : null) ||
                                 (Array.isArray(tripInfo.traveler_names) ? tripInfo.traveler_names.length : null) ||
                                 (typeof tripInfo.travelers === 'number' ? tripInfo.travelers : null) ||
                                 (tripInfo.adults && tripInfo.children ? (tripInfo.adults + tripInfo.children) : null) ||
                                 1
            if (numTravelers) {
              travelersInfo = `\n• Number of Travelers: ${numTravelers}`
            }
          }
          
          // Build content - ensure we show something even if some fields are missing
          let extractedDetails = ''
          if (tripInfo.destination) extractedDetails += `• Destination: ${tripInfo.destination}\n`
          if (tripInfo.departure_date) extractedDetails += `• Departure: ${tripInfo.departure_date}\n`
          if (tripInfo.return_date) extractedDetails += `• Return: ${tripInfo.return_date}\n`
          
          const content = `✅ **Document Processed Successfully!**\n\n### 📄 Trip Details Extracted\n\n${extractedDetails || 'No trip details extracted. Please provide trip information manually.'}${travelersInfo}${claimsSection}\n\n### 💡 Insurance Recommendations\n\n${quotes.length > 0 ? quotes.map((q: any, i: number) => `• **${q.plan_name}**: $${q.price.toFixed(2)} ${q.currency || 'SGD'} ${q.score ? `(Score: ${q.score}/100)` : ''} - ${q.recommended_for}`).join('\n') : 'No quotes available'}\n\nWhich plan would you like to learn more about?`
          
          const successMsg: Message = {
            role: 'assistant',
            content: content,
            timestamp: new Date(),
            quotes: quotes,
            quote_id: quoteData.quote_id || null,
            trip_details: quoteData.trip_details || tripInfo
          }
          
          setMessages(prev => [...prev, successMsg])
        } else if (extractData.extracted_data && Object.keys(extractData.extracted_data).length > 0) {
          // Partial extraction - show what we got and ask for missing info
          const tripInfo = extractData.extracted_data
          const missingFields = extractData.missing_fields || []
          const validationQuestions = extractData.validation_questions || []
          
          let partialMsg = `📄 **I found some information from your document!**\n\n`
          
          if (tripInfo.destination) partialMsg += `✅ Destination: ${tripInfo.destination}\n`
          if (tripInfo.departure_date) partialMsg += `✅ Departure: ${tripInfo.departure_date}\n`
          if (tripInfo.return_date) partialMsg += `✅ Return: ${tripInfo.return_date}\n`
          if (tripInfo.pax || tripInfo.travelers?.length) partialMsg += `✅ Travelers: ${tripInfo.pax || tripInfo.travelers?.length}\n`
          
          if (missingFields.length > 0) {
            partialMsg += `\n⚠️ **I need a bit more information:**\n\n`
            validationQuestions.forEach((q: string) => {
              partialMsg += `• ${q}\n`
            })
            partialMsg += `\nYou can either:\n• Upload a clearer document\n• Tell me the missing details in chat`
          }
          
          const partialMsgObj: Message = {
            role: 'assistant',
            content: partialMsg,
            timestamp: new Date(),
            trip_details: tripInfo
          }
          setMessages(prev => [...prev, partialMsgObj])
        } else {
          // Complete failure - show helpful error
          const errorMsg = extractData.message || extractData.error || 'Failed to extract trip information'
          const errorMsgObj: Message = {
            role: 'assistant',
            content: `⚠️ **Upload Error**\n\n${errorMsg}\n\n**What you can do:**\n• Upload a clearer, higher quality image/PDF\n• Try describing your trip manually in chat\n• Make sure the document shows:\n  - Destination (city, country)\n  - Travel dates\n  - Number of travelers`,
            timestamp: new Date()
          }
          setMessages(prev => [...prev, errorMsgObj])
        }
      } catch (error: any) {
        console.error('File upload error:', error)
        
        // Check if it's a connection error
        const isConnectionError = error.message?.includes('Failed to fetch') || 
                                  error.message?.includes('NetworkError') || 
                                  error.message?.includes('Cannot connect') ||
                                  error.message?.includes('fetch') ||
                                  error.name === 'TypeError'
        
        let errorContent = ''
        if (isConnectionError) {
          errorContent = `🔌 **Connection Error**\n\n• Cannot connect to the backend server\n• **The server might not be running!**\n\n**To fix:**\n1. Open terminal in the project folder\n2. Run: \`PORT=8002 python3 run_server.py\`\n3. Wait for "Application startup complete"\n4. Try uploading again\n\n**Or check:**\n• Is the server running? (Check terminal)\n• Is it on port 8002? (Frontend will also try 8003 and 8004)\n• Check browser console for more details`
        } else {
          errorContent = `⚠️ **Upload Error**\n\n• Could not process your document\n• ${error.message || 'Please try uploading a clearer document or describe your trip manually'}\n\n**Tips:**\n• Make sure the image/PDF is clear and readable\n• Try taking a better photo if it's blurry\n• You can also just tell me about your trip in chat!`
        }
        
        const errorMsg: Message = {
          role: 'assistant',
          content: errorContent,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMsg])
      } finally {
        setIsUploading(false)
        setUploadedFile(null)
      }
    }
    
    reader.readAsDataURL(file)
  }

  const startVoiceInput = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.continuous = false
      recognition.interimResults = false
      
      // Language mapping for speech recognition
      const langMap: { [key: string]: string } = {
        'en': 'en-US',
        'ta': 'ta-IN',  // Tamil
        'zh': 'zh-CN',  // Chinese
        'ms': 'ms-MY'   // Malay
      }
      recognition.lang = langMap[language] || language || 'en-US'

      recognition.onstart = () => setIsListening(true)
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        setIsListening(false)
        recognition.stop()
      }
      recognition.onerror = () => {
        setIsListening(false)
        recognition.stop()
      }
      recognition.onend = () => setIsListening(false)

      recognitionRef.current = recognition
      recognition.start()
    } else {
      alert('Speech recognition not supported in your browser')
    }
  }

  const stopVoiceInput = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  const cleanTextForSpeech = (text: string): string => {
    if (!text || typeof text !== 'string') {
      return 'I have a response for you. Please check the chat window.';
    }
    
    // Remove emojis and special characters
    let cleaned = text
      .replace(/[\u{1F600}-\u{1F64F}]/gu, '')
      .replace(/[\u{1F300}-\u{1F5FF}]/gu, '')
      .replace(/[\u{1F680}-\u{1F6FF}]/gu, '')
      .replace(/[\u{2600}-\u{26FF}]/gu, '')
      .replace(/[\u{2700}-\u{27BF}]/gu, '')
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(.*?)\*/g, '$1')
      .replace(/━+/g, ' ')
      .replace(/[•▪▫◦]/g, '- ')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/\[IMAGE:[^\]]+\]/g, '')
      .replace(/https?:\/\/[^\s]+/g, '')
      // Remove hashes and symbols from policy names (e.g., "#Policy Name" -> "Policy Name")
      .replace(/#+\s*/g, '')
      // Remove common special characters that shouldn't be read
      .replace(/[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~]/g, ' ')
      // Clean policy names - remove symbols but keep readable text
      .replace(/\b(INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG)[^\s]*/gi, (match) => {
        // Clean up policy names - remove trailing symbols
        return match.replace(/[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~-]+$/g, '').trim();
      })
      .replace(/\s+/g, ' ')
      .trim();
    
    return cleaned.length > 10 ? cleaned : 'I have a response for you. Please check the chat window.';
  }

  // Function to clean policy names for display
  const cleanPolicyName = (name: string): string => {
    if (!name) return '';
    return name
      .replace(/#+/g, '') // Remove hashes
      .replace(/[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~]/g, ' ') // Remove special chars
      .replace(/\s+/g, ' ')
      .trim();
  }

  const getBestVoice = (): SpeechSynthesisVoice | null => {
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return null;
    
    // Prefer high-quality voices in order of preference
    const preferredVoices = [
      'Google US English',
      'Microsoft Zira',
      'Microsoft David',
      'Alex',
      'Samantha',
      'Victoria',
      'Karen',
      'Fiona',
      'Tessa',
      'Moira',
      'Google UK English Female',
      'Google UK English Male',
      'en-US',
      'en-GB'
    ];
    
    // First, try to find a preferred voice
    for (const preferred of preferredVoices) {
      const voice = voices.find(v => 
        v.name.includes(preferred) || 
        v.lang.includes(preferred) ||
        v.voiceURI.includes(preferred)
      );
      if (voice && voice.localService === false) { // Prefer cloud voices
        return voice;
      }
    }
    
    // If no preferred found, get any high-quality English voice
    const englishVoices = voices.filter(v => 
      v.lang.startsWith('en') && 
      !v.name.toLowerCase().includes('novox') && // Skip low-quality voices
      !v.name.toLowerCase().includes('bad')
    );
    
    if (englishVoices.length > 0) {
      // Prefer voices that are not locally synthesized (often better quality)
      const cloudVoice = englishVoices.find(v => !v.localService);
      if (cloudVoice) return cloudVoice;
      return englishVoices[0];
    }
    
    // Fallback to first available voice
    return voices[0];
  }

  const speakText = async (text: string) => {
    try {
      if (!text || typeof text !== 'string') return;
      
      let cleanedText = cleanTextForSpeech(text);
      if (cleanedText.length < 3) return;
      
      setIsSpeaking(true);
      
      // Use Groq TTS API
      try {
        const response = await fetch(`${API_URL}/api/tts/groq`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: cleanedText })
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.audio) {
            // Play audio from base64
            const audio = new Audio(data.audio);
            audio.onended = () => setIsSpeaking(false);
            audio.onerror = () => {
              console.error('Audio playback error');
              setIsSpeaking(false);
              // Fallback to browser TTS
              useBrowserTTS(cleanedText);
            };
            audio.play();
            return;
          }
        }
      } catch (error) {
        console.log('Groq TTS failed, falling back to browser TTS:', error);
      }
      
      // Fallback to browser TTS if Groq fails
      useBrowserTTS(cleanedText);
    } catch (error) {
      console.error('TTS error:', error);
      setIsSpeaking(false);
    }
  }

  const useBrowserTTS = (text: string) => {
    if (!('speechSynthesis' in window)) {
      console.warn('Speech synthesis not supported');
      return;
    }
    
    window.speechSynthesis.cancel(); // Cancel any ongoing speech
    
    // Wait for voices to be loaded
    const speak = () => {
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Get the best available voice based on selected language
      const voices = window.speechSynthesis.getVoices();
      const langMap: { [key: string]: string } = {
        'en': 'en-US',
        'ta': 'ta-IN',  // Tamil
        'zh': 'zh-CN',  // Chinese
        'ms': 'ms-MY'   // Malay
      }
      const targetLang = langMap[language] || language || 'en-US'
      
      // Try to find a voice matching the selected language
      const matchingVoice = voices.find(v => v.lang.startsWith(targetLang.split('-')[0]))
      if (matchingVoice) {
        utterance.voice = matchingVoice;
        utterance.lang = matchingVoice.lang;
      } else {
        // Fallback to best available voice
        const voice = getBestVoice();
        if (voice) {
          utterance.voice = voice;
          utterance.lang = voice.lang;
        } else {
          utterance.lang = targetLang;
        }
      }
      
      // Optimized settings for natural speech
      utterance.rate = 0.95;  // Slightly slower for clarity
      utterance.pitch = 1.05; // Slightly higher for more natural sound
      utterance.volume = 1.0;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        setIsSpeaking(false);
      };
      
      window.speechSynthesis.speak(utterance);
    };
    
    // Load voices if needed
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = speak;
    } else {
      speak();
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 relative overflow-hidden">
      {/* Elegant Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
        <div className="absolute bottom-0 left-1/3 w-[550px] h-[550px] bg-purple-600/10 rounded-full blur-3xl animate-pulse-slow animation-delay-4000"></div>
        
        <div className="absolute inset-0 opacity-20">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1.5 h-1.5 bg-blue-400/40 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${12 + Math.random() * 8}s`
              }}
            ></div>
          ))}
        </div>
        
        <div 
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px'
          }}
        ></div>
      </div>

      <div className="flex flex-col h-screen relative z-10">
        {/* Elegant Chat History Sidebar */}
        <div className={`fixed left-0 top-0 bottom-0 w-80 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 backdrop-blur-2xl border-r border-slate-700/50 z-20 transition-transform duration-300 shadow-2xl ${showHistory ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex flex-col h-full">
            <div className="p-5 border-b border-slate-700/50 bg-slate-800/30">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <History className="w-5 h-5 text-blue-400" />
                  Chat History
                </h2>
                <div className="flex items-center gap-2">
                  {conversationThreads.length > 0 && (
                    <button
                      onClick={clearChatHistory}
                      className="p-2 hover:bg-red-600/20 rounded-lg transition-all duration-200 hover:scale-105 group"
                      title="Clear all chat history"
                    >
                      <Trash2 className="w-4 h-4 text-slate-400 group-hover:text-red-400 transition-colors" />
                    </button>
                  )}
                  <button
                    onClick={() => setShowHistory(false)}
                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    <ChevronLeft className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 scrollbar-thin">
              {conversationThreads.length === 0 ? (
                <div className="text-center text-slate-500 text-sm py-12">
                  <div className="mb-2">No conversation history yet</div>
                  <div className="text-xs text-slate-600">Start a new conversation to get started</div>
                </div>
              ) : (
                conversationThreads.map((thread) => {
                  const isEditing = editingThreadId === thread.id
                  return (
                    <div
                      key={thread.id}
                      onClick={() => !isEditing && loadThread(thread.id)}
                      className={`p-4 rounded-xl cursor-pointer transition-all duration-200 hover:bg-slate-700/40 border backdrop-blur-sm group ${
                        thread.id === currentThreadId 
                          ? 'bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border-blue-500/50 shadow-lg ring-2 ring-blue-500/30' 
                          : 'border-slate-700/50 hover:border-slate-600/50 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-start gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-gradient-to-br from-blue-600/30 to-indigo-600/30">
                          <Sparkles className="w-4 h-4 text-blue-300" />
                        </div>
                        <div className="flex-1 min-w-0">
                          {isEditing ? (
                            <div className="flex items-center gap-2">
                              <input
                                type="text"
                                value={editingThreadTitle}
                                onChange={(e) => setEditingThreadTitle(e.target.value)}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    renameThread(thread.id, editingThreadTitle)
                                  } else if (e.key === 'Escape') {
                                    setEditingThreadId(null)
                                    setEditingThreadTitle('')
                                  }
                                }}
                                onClick={(e) => e.stopPropagation()}
                                className="flex-1 px-2 py-1 bg-slate-700/50 border border-blue-500/50 rounded text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                autoFocus
                              />
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  renameThread(thread.id, editingThreadTitle)
                                }}
                                className="p-1 hover:bg-green-600/20 rounded transition-colors"
                                title="Save"
                              >
                                <Check className="w-4 h-4 text-green-400" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setEditingThreadId(null)
                                  setEditingThreadTitle('')
                                }}
                                className="p-1 hover:bg-red-600/20 rounded transition-colors"
                                title="Cancel"
                              >
                                <XIcon className="w-4 h-4 text-red-400" />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-sm font-semibold text-white break-words" style={{ 
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                                wordBreak: 'break-word'
                              }} title={thread.title}>{thread.title}</p>
                              <button
                                onClick={(e) => startEditingThread(thread, e)}
                                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600/50 rounded transition-all flex-shrink-0"
                                title="Rename chat"
                              >
                                <Edit2 className="w-3 h-3 text-slate-400 hover:text-blue-400" />
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                      {!isEditing && (
                        <>
                          <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">{thread.lastMessage}</p>
                          <div className="flex items-center justify-between text-xs text-slate-500">
                            <span className="font-medium">{thread.messageCount} messages</span>
                            <span>{new Date(thread.timestamp).toLocaleDateString()}</span>
                          </div>
                        </>
                      )}
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className={`flex-1 flex flex-col h-full overflow-hidden transition-all duration-300 ${showHistory ? 'ml-80' : 'ml-0'}`}>
          {/* Elegant Professional Header */}
          <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 backdrop-blur-xl border-b border-slate-700/50 shadow-2xl flex-shrink-0">
            <div className="max-w-6xl mx-auto px-6 py-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {!showHistory && (
                    <button
                      onClick={() => setShowHistory(true)}
                      className="p-2.5 hover:bg-slate-700/50 rounded-xl transition-all duration-200 hover:scale-105"
                    >
                      <History className="w-5 h-5 text-slate-300" />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      createNewChat()
                    }}
                    disabled={isCreatingNewChat}
                    className="p-2.5 hover:bg-slate-700/50 rounded-xl transition-all duration-200 hover:scale-105"
                    title="New Chat"
                  >
                    <MessageSquarePlus className="w-5 h-5 text-slate-300" />
                  </button>
                  <div className="relative flex items-center gap-3">
                    {/* WanderSure Logo */}
                    <div className="relative">
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 rounded-xl blur-sm opacity-60 animate-pulse-slow"></div>
                      <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-white">
                          <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor" opacity="0.9"/>
                          <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <circle cx="12" cy="7" r="1.5" fill="currentColor" opacity="0.8"/>
                        </svg>
                      </div>
                    </div>
                    <div className="pl-1">
                      <h1 className="text-2xl font-bold bg-gradient-to-r from-white via-blue-100 to-indigo-100 bg-clip-text text-transparent tracking-tight flex items-center gap-2">
                        <span>WanderSure</span>
                        <span className="text-lg">✈️</span>
                      </h1>
                      <p className="text-sm text-slate-400 font-medium mt-0.5">Your Intelligent Travel Insurance Assistant</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {/* Google Translate Widget */}
                  <div id="google_translate_element" className="flex items-center">
                    {/* Will be populated by Google Translate automatically */}
                  </div>
                  <style jsx>{`
                    #google_translate_element {
                      font-size: 14px !important;
                    }
                    .goog-te-banner-frame {
                      display: none !important;
                    }
                    body {
                      top: 0 !important;
                    }
                    .goog-te-balloon-frame {
                      display: none !important;
                    }
                    .goog-text-highlight {
                      background: transparent !important;
                      box-shadow: none !important;
                    }
                    /* Style Google Translate button - make it match the dark theme */
                    .goog-te-gadget {
                      color: rgb(226, 232, 240) !important;
                      font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
                    }
                    .goog-te-gadget-simple {
                      background-color: rgba(30, 41, 59, 0.8) !important;
                      border: 1px solid rgba(100, 116, 139, 0.5) !important;
                      border-radius: 0.75rem !important;
                      padding: 0.5rem 0.75rem !important;
                      backdrop-filter: blur(8px) !important;
                      transition: all 0.2s !important;
                    }
                    .goog-te-gadget-simple:hover {
                      background-color: rgba(51, 65, 85, 0.9) !important;
                      border-color: rgba(59, 130, 246, 0.5) !important;
                    }
                    .goog-te-gadget-simple .goog-te-menu-value {
                      color: rgb(226, 232, 240) !important;
                      font-size: 14px !important;
                    }
                    .goog-te-gadget-simple .goog-te-menu-value span {
                      color: rgb(148, 163, 184) !important;
                    }
                    .goog-te-gadget-icon {
                      margin-left: 0.5rem !important;
                      margin-right: 0 !important;
                    }
                    .goog-te-menu-value {
                      color: rgb(226, 232, 240) !important;
                    }
                  `}</style>
                </div>
              </div>
            </div>
          </header>
          
          {/* Onboarding Modal - User data collection */}
          {showOnboarding ? (
            <div data-onboarding-active="true" style={{ position: 'fixed', zIndex: 99999, inset: 0 }}>
              <UserOnboarding
                onComplete={handleOnboardingComplete}
                onSkip={handleSkipOnboarding}
              />
            </div>
          ) : (
            <div data-onboarding-hidden="true" style={{ display: 'none' }}>
              {/* Debug: Onboarding is hidden, showOnboarding={showOnboarding} */}
            </div>
          )}

          {/* Messages - Dark Mode */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 py-6 scrollbar-thin" style={{ minHeight: 0 }}>
            <div className="max-w-4xl mx-auto space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} message-enter`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  {message.role === 'assistant' && (
                    <div className="flex items-start gap-4 max-w-[85%] animate-slide-in-left">
                      <div className="relative flex-shrink-0 group/avatar">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 rounded-xl blur-md opacity-40 animate-pulse-slow"></div>
                        <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 p-2.5 rounded-xl shadow-xl transform transition-all duration-300 group-hover/avatar:scale-110 group-hover/avatar:shadow-2xl">
                          <Sparkles className="w-5 h-5 text-white" />
                        </div>
                      </div>
                      <div className="relative group flex-1">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600/30 via-indigo-600/30 to-purple-600/30 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="relative bg-gradient-to-br from-slate-800 via-slate-800 to-slate-900 rounded-2xl px-6 py-5 shadow-2xl border border-slate-700/60 backdrop-blur-xl">
                          {/* Enhanced content with cards */}
                          <div className="relative prose prose-invert prose-sm max-w-none" style={{ fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
                        <EnhancedMarkdown
                          content={message.content
                            .replace(/━━━+/g, '\n\n### ') // Convert separator lines to section headers
                            .replace(/^━+$/gm, '### ') // Convert standalone separator lines
                            .replace(/\*\*(Policy:|INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG[^\*]*)\*\*/gi, '**$1**')
                            .replace(/(Policy:|INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG[^•\n]*)/gi, '**$1**')}
                          quotes={message.quotes}
                          language={language}
                        />
                        </div>
                      
                        {/* Insurance Quotes with Purchase Option */}
                        {message.quotes && message.quotes.length > 0 && (
                          <div className="mt-6 pt-6">
                            <div className="mb-4 flex items-center justify-between">
                              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-blue-400" />
                                {t.availablePlans}
                                {message.quotes.some((q: any) => q.source === 'taxonomy_match') && (
                                  <span className="ml-2 px-2 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-semibold rounded-full">
                                    Matched via Taxonomy
                                  </span>
                                )}
                                {message.quotes.some((q: any) => q.cost_source === 'ancileo') && (
                                  <span className="ml-2 px-2 py-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-semibold rounded-full">
                                    Prices from Ancileo
                                  </span>
                                )}
                              </h3>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Show all matched policies */}
                              {message.quotes.map((quote: any, idx: number) => (
                                <QuoteCard
                                  key={idx}
                                  quote={quote}
                                  quoteId={message.quote_id}
                                  tripDetails={message.trip_details}
                                  language={language}
                                  onPurchase={async (selectedQuote, insureds, paymentInfo) => {
                                    // Handle purchase - support both Ancileo and local policies
                                    try {
                                      // If it's an Ancileo policy (has offer_id), use Ancileo purchase endpoint
                                      if (selectedQuote.offer_id || selectedQuote.source === 'ancileo') {
                                        // Build insureds array according to Ancileo API format
                                        const ancileoInsureds = (insureds || message.trip_details?.travelers || []).map((t: any, idx: number) => ({
                                          id: t.id || `insured_${idx}`,
                                          title: t.title || (t.gender === 'F' ? 'Ms' : 'Mr'),
                                          firstName: t.firstName || t.first_name || (t.name ? t.name.split(' ')[0] : ''),
                                          lastName: t.lastName || t.last_name || (t.name ? t.name.split(' ').slice(1).join(' ') : ''),
                                          nationality: t.nationality || 'SG',
                                          dateOfBirth: t.dateOfBirth || t.date_of_birth || new Date(new Date().setFullYear(new Date().getFullYear() - (t.age || 30))).toISOString().split('T')[0],
                                          passport: t.passport || '',
                                          cardId: t.cardId || t.card_id || ''
                                        }))
                                        
                                        // Build main contact from first insured or payment info
                                        const firstInsured = ancileoInsureds[0] || {}
                                        const originalFirstInsured = (insureds || message.trip_details?.travelers || [])[0] || {}
                                        const mainContact = {
                                          insuredId: firstInsured.id,
                                          title: firstInsured.title || 'Mr',
                                          firstName: firstInsured.firstName || '',
                                          lastName: firstInsured.lastName || '',
                                          email: originalFirstInsured.email || paymentInfo?.email || '',
                                          phoneNumber: originalFirstInsured.phone || originalFirstInsured.phoneNumber || paymentInfo?.phone || ''
                                        }
                                        
                                        // Build payment structure if provided
                                        const payment = paymentInfo?.cardNumber ? {
                                          pgwPspId: 'stripe',
                                          pgwMerchantId: 'wandersure',
                                          pspIdentifier: 'stripe',
                                          pspTransactionId: paymentInfo.transactionId || `txn_${Date.now()}`,
                                          merchantReference: `ref_${Date.now()}`,
                                          paymentMethod: 'credit-card',
                                          amount: selectedQuote.price,
                                          currency: selectedQuote.currency || 'SGD',
                                          status: 'authorised',
                                          transactionDate: new Date().toISOString(),
                                          paymentName: paymentInfo.cardName || ''
                                        } : undefined
                                        
                                        const purchaseResponse = await fetch(`${API_URL}/api/ancileo/purchase`, {
                                          method: 'POST',
                                          headers: { 'Content-Type': 'application/json' },
                                          body: JSON.stringify({
                                            quote_id: message.quote_id,
                                            offer_id: selectedQuote.offer_id,
                                            product_code: selectedQuote.product_code,
                                            product_type: 'travel-insurance',
                                            unit_price: selectedQuote.price,
                                            currency: selectedQuote.currency || 'SGD',
                                            quantity: 1,
                                            insureds: ancileoInsureds,
                                            main_contact: mainContact,
                                            payment: payment,
                                            market: 'SG',
                                            language_code: 'en'
                                          })
                                        })
                                        
                                        const purchaseData = await purchaseResponse.json()
                                        if (purchaseData.success) {
                                          // Auto-download receipt
                                          downloadPolicyReceipt({
                                            policyName: cleanPolicyName(selectedQuote.plan_name),
                                            policyNumber: purchaseData.policy_number || 'Processing...',
                                            policyType: 'Ancileo',
                                            price: selectedQuote.price,
                                            currency: selectedQuote.currency || 'SGD',
                                            travelers: insureds,
                                            tripDetails: message.trip_details,
                                            purchaseDate: new Date().toISOString()
                                          })
                                          
                                          const purchaseMsg: Message = {
                                            role: 'assistant',
                                            content: `✅ **Purchase Successful!**\n\nYour insurance policy has been purchased:\n\n• Policy: ${cleanPolicyName(selectedQuote.plan_name)}\n• Source: Ancileo\n• Policy Number: ${purchaseData.policy_number || 'Processing...'}\n• Amount: ${selectedQuote.currency || 'SGD'} ${selectedQuote.price.toFixed(2)}\n\n📄 Policy receipt downloaded to your desktop.\n\nConfirmation email will be sent shortly.`,
                                            timestamp: new Date()
                                          }
                                          setMessages((prev: Message[]) => [...prev, purchaseMsg])
                                          return
                                        } else {
                                          throw new Error(purchaseData.error || 'Purchase failed')
                                        }
                                      } else {
                                        // Local/taxonomy-matched policy - use Stripe payment directly
                                        const paymentResponse = await fetch(`${API_URL}/api/payment/create`, {
                                          method: 'POST',
                                          headers: { 'Content-Type': 'application/json' },
                                          body: JSON.stringify({
                                            amount: selectedQuote.price,
                                            currency: selectedQuote.currency || 'SGD',
                                            policy_name: selectedQuote.plan_name,
                                            product_code: selectedQuote.product_code,
                                            trip_details: message.trip_details,
                                            insureds: insureds,
                                            payment_info: paymentInfo
                                          })
                                        })
                                        
                                        const paymentData = await paymentResponse.json()
                                        if (paymentData.success) {
                                          // Auto-download receipt for local policies
                                          downloadPolicyReceipt({
                                            policyName: cleanPolicyName(selectedQuote.plan_name),
                                            policyNumber: paymentData.policy_number || paymentData.payment_id || 'Processing...',
                                            policyType: selectedQuote.source === 'taxonomy_match' ? 'Taxonomy Matched' : 'Local',
                                            price: selectedQuote.price,
                                            currency: selectedQuote.currency || 'SGD',
                                            travelers: insureds,
                                            tripDetails: message.trip_details,
                                            purchaseDate: new Date().toISOString()
                                          })
                                          
                                          const purchaseMsg: Message = {
                                            role: 'assistant',
                                            content: `✅ **Purchase Successful!**\n\nYour insurance policy has been purchased:\n\n• Policy: ${cleanPolicyName(selectedQuote.plan_name)}\n• Source: ${selectedQuote.source === 'taxonomy_match' ? 'Taxonomy Matched' : 'Local'}\n• Policy Number: ${paymentData.policy_number || paymentData.payment_id || 'Processing...'}\n• Amount: ${selectedQuote.currency || 'SGD'} ${selectedQuote.price.toFixed(2)}\n\n📄 Policy receipt downloaded to your desktop.\n\n${paymentData.payment_url ? `[Complete Payment](${paymentData.payment_url})` : 'Confirmation email will be sent shortly.'}`,
                                            timestamp: new Date()
                                          }
                                          setMessages((prev: Message[]) => [...prev, purchaseMsg])
                                          return
                                        } else {
                                          throw new Error(paymentData.error || 'Payment processing failed')
                                        }
                                      }
                                    } catch (error: any) {
                                      const errorMsg: Message = {
                                        role: 'assistant',
                                        content: `⚠️ **Purchase Error**\n\n• ${error.message || 'Unable to process purchase'}\n• Please try again or contact support`,
                                        timestamp: new Date()
                                      }
                                      setMessages((prev: Message[]) => [...prev, errorMsg])
                                    }
                                  }}
                                />
                              ))}
                            </div>
                            {message.quotes.length === 0 && (
                              <div className="text-center py-8 text-gray-400">
                                <p>No insurance plans available. Please upload your itinerary to get matched policies.</p>
                              </div>
                            )}
                          </div>
                        )}
                      
                        {/* Booking Links */}
                        {message.booking_links && message.booking_links.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-gray-700/50">
                            <div className="flex flex-wrap gap-2">
                              {message.booking_links.map((link, i) => (
                                <a
                                  key={i}
                                  href={link.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 rounded-lg text-blue-300 text-sm font-medium transition-all hover:scale-105 group"
                                >
                                  <ExternalLink className="w-4 h-4" />
                                  <span>{link.text}</span>
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Suggested Questions - Clickable Buttons */}
                        {message.suggested_questions && message.suggested_questions.length > 0 && (
                          <div className="mt-6 pt-6 border-t border-gray-700/50">
                            <p className="text-xs text-gray-400 mb-3 font-medium uppercase tracking-wide">💬 {t.suggestedQuestions}</p>
                            <div className="flex flex-wrap gap-2">
                              {message.suggested_questions.map((sq: any, i: number) => (
                                <button
                                  key={i}
                                  onClick={async () => {
                                    if (isLoading) return
                                    
                                    const userMsg: Message = {
                                      role: 'user',
                                      content: sq.question,
                                      timestamp: new Date()
                                    }
                                    setMessages(prev => [...prev, userMsg])
                                    setIsLoading(true)
                                    setInput('')
                                    
                                    try {
                                      const response = await fetch(`${API_URL}/api/ask`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({
                                          question: sq.question,
                                          language: language,
                                          user_id: userData?.user_id || 'default_user',
                                          is_voice: false,
                                          context_data: {
                                            user_data: userData
                                          }
                                        })
                                      })
                                      
                                      const data = await response.json()
                                      const answerText = data.answer || data.message || data.content || 'I apologize, but I encountered an error.'
                                      
                                      const assistantMsg: Message = {
                                        role: 'assistant',
                                        content: answerText,
                                        timestamp: new Date(),
                                        booking_links: data.booking_links || [],
                                        suggested_questions: data.suggested_questions || [],
                                        quotes: data.quotes || [],
                                        quote_id: data.quote_id || null,
                                        trip_details: data.trip_details || null
                                      }
                                      
                                      setMessages(prev => [...prev, assistantMsg])
                                    } catch (error) {
                                      console.error('Error:', error)
                                      setMessages(prev => [...prev, {
                                        role: 'assistant',
                                        content: '⚠️ **Error**\n\n• I encountered an error processing your request\n• Please try again',
                                        timestamp: new Date()
                                      }])
                                    } finally {
                                      setIsLoading(false)
                                    }
                                  }}
                                  disabled={isLoading}
                                  className="inline-flex items-center gap-2 px-3 py-2 bg-gray-700/50 hover:bg-gray-700 border border-gray-600/50 rounded-lg text-gray-200 text-xs font-medium transition-all hover:scale-105 hover:border-blue-500/50 group disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  <span className="text-base">{sq.icon}</span>
                                  <span>{sq.question}</span>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    </div>
                  </div>
                )}
                
                {message.role === 'user' && (
                  <div className="relative group max-w-[85%] animate-slide-in-right">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-2xl blur-md opacity-40 group-hover:opacity-60 transition-opacity"></div>
                    <div className="relative bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-2xl px-6 py-4 shadow-2xl border border-blue-400/30 transform transition-all duration-300 hover:scale-[1.01] hover:shadow-3xl">
                      <p className="text-white font-medium whitespace-pre-wrap leading-relaxed tracking-wide">{message.content}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
            </div>
            
            {isLoading && (
              <div className="flex justify-start gap-3 animate-fade-in">
                <div className="relative flex-shrink-0">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg blur opacity-50 animate-pulse"></div>
                  <div className="relative bg-gradient-to-br from-blue-500 to-indigo-500 p-2 rounded-lg shadow-lg">
                    <Sparkles className="w-4 h-4 text-white animate-spin" />
                  </div>
                </div>
                <div className="relative">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 rounded-xl blur animate-pulse"></div>
                  <div className="relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl px-5 py-4 shadow-xl border border-gray-700/50">
                    <div className="flex gap-2">
                      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce shadow-lg shadow-blue-500/50" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-indigo-400 rounded-full animate-bounce shadow-lg shadow-indigo-500/50" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-purple-400 rounded-full animate-bounce shadow-lg shadow-purple-500/50" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <p className="text-gray-400 text-xs mt-2 animate-pulse">Wanda is thinking...</p>
                  </div>
                </div>
              </div>
            )}
            
            {isListening && (
              <div className="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-6 py-3 rounded-full shadow-xl animate-pulse z-50">
                <div className="flex items-center gap-2">
                  <Mic className="w-5 h-5" />
                  <span className="font-semibold">Listening...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* File Upload Indicator - Dark Mode */}
          {uploadedFile && (
            <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 flex-shrink-0">
              <div className="max-w-5xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Upload className="w-4 h-4 text-blue-400" />
                  <span>{uploadedFile.name}</span>
                  {isUploading && <span className="text-gray-500">Processing...</span>}
                </div>
                <button
                  onClick={() => { setUploadedFile(null); setIsUploading(false); }}
                  className="p-1 hover:bg-gray-700 rounded"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
          )}

          {/* Elegant Input Bar */}
          <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 backdrop-blur-xl border-t border-slate-700/50 p-5 shadow-2xl flex-shrink-0">
          <div className="max-w-5xl mx-auto">
            <div className="flex items-end gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileUpload(file)
                }}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-3 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-xl transition-all duration-200 hover:scale-105"
                title="Upload document"
              >
                <Upload className="w-5 h-5" />
              </button>
              
              <div className="flex-1 relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-indigo-500/20 to-purple-500/20 rounded-2xl blur-xl opacity-0 focus-within:opacity-100 transition-opacity duration-300"></div>
                <div className="relative bg-slate-800/80 rounded-2xl border border-slate-600/50 focus-within:border-blue-500/50 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all backdrop-blur-sm">
                  <textarea
                    value={input}
                    onChange={(e) => {
                      setInput(e.target.value)
                      // Auto-resize textarea
                      e.target.style.height = 'auto'
                      e.target.style.height = `${Math.min(e.target.scrollHeight, 128)}px`
                    }}
                    onKeyDown={handleKeyPress}
                    placeholder="Ask about travel insurance or upload a booking document..."
                    className="w-full bg-transparent border-none outline-none px-5 py-4 text-slate-100 placeholder-slate-400 resize-none min-h-[52px] max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent leading-relaxed"
                    style={{ 
                      fontSize: '15px',
                      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                      letterSpacing: '0.01em'
                    }}
                    disabled={isLoading || isUploading}
                    rows={1}
                  />
                </div>
              </div>
              
              <button
                onClick={isListening ? stopVoiceInput : startVoiceInput}
                className={`p-3 rounded-xl transition-all duration-200 ${
                  isListening 
                    ? 'bg-red-600 text-white animate-pulse shadow-lg shadow-red-500/50' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 hover:scale-105'
                }`}
                title="Voice input"
              >
                <Mic className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setIsSpeaking(!isSpeaking)}
                className={`p-3 rounded-xl transition-all duration-200 ${
                  isSpeaking 
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/50' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 hover:scale-105'
                }`}
                title="Voice output"
              >
                <Volume2 className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim() || isUploading}
                className="relative px-6 py-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-2xl hover:shadow-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 font-semibold hover:scale-105 disabled:hover:scale-100"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-xl blur opacity-0 hover:opacity-50 transition-opacity"></div>
                <Send className="w-5 h-5 relative z-10" />
                <span className="hidden sm:inline relative z-10">Send</span>
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  )
}

