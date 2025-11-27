'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Mic, Volume2, Sparkles, Plane, Upload, X, History, ChevronLeft, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
<<<<<<< Updated upstream
=======
import UserOnboarding from '../components/UserOnboarding'

// Declare Google Translate types at top level
declare global {
  interface Window {
    google?: {
      translate?: {
        TranslateElement: {
          new (options: any, elementId: string): any;
          InlineLayout: {
            SIMPLE: string;
          };
        };
      };
    };
    loadGoogleTranslate?: () => void;
  }
}

// Function to clean policy names for display
function cleanPolicyName(name: string): string {
  if (!name) return '';
  return name
    .replace(/#+/g, '') // Remove hashes
    .replace(/[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./`~]/g, ' ') // Remove special chars
    .replace(/^\s+|\s+$/g, '') // Trim
    .replace(/\s+/g, ' '); // Normalize spaces
}

// Function to normalize names by removing repeated characters
// Example: "MMMMssss SSSSaaaarrrroooojjjjiiiinnnniiii" -> "Ms Sarojini"
function normalizeName(name: string): string {
  if (!name) return '';
  
  // Remove consecutive duplicate characters (case-insensitive)
  // This handles cases like "MMMMssss" -> "Ms"
  let normalized = name
    .split('')
    .reduce((acc, char, index, arr) => {
      // Keep the character if it's different from the previous one (case-insensitive)
      // or if it's a space
      const prevChar = index > 0 ? arr[index - 1] : '';
      const isSpace = char === ' ';
      const isDifferent = char.toLowerCase() !== prevChar.toLowerCase();
      
      if (isSpace || isDifferent) {
        return acc + char;
      }
      return acc;
    }, '');
  
  // Clean up multiple spaces
  normalized = normalized.replace(/\s+/g, ' ').trim();
  
  // Capitalize properly (first letter of each word)
  normalized = normalized
    .split(' ')
    .map(word => {
      if (!word) return '';
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
  
  return normalized;
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
>>>>>>> Stashed changes

// Policy Card Component - Beautiful card for displaying policy info
function PolicyCard({ policyName, onClick }: { policyName: string; onClick: () => void }) {
  const getPolicyStyles = (name: string) => {
    if (name.includes('TravelEasy')) {
      return 'from-blue-500 to-cyan-500 shadow-blue-500/20 hover:shadow-blue-500/40'
    }
    if (name.includes('Scootsurance')) {
      return 'from-purple-500 to-pink-500 shadow-purple-500/20 hover:shadow-purple-500/40'
    }
    return 'from-indigo-500 to-blue-500 shadow-indigo-500/20 hover:shadow-indigo-500/40'
  }
  
  return (
    <button
      onClick={onClick}
      className={`group relative overflow-hidden rounded-xl bg-gradient-to-br ${getPolicyStyles(policyName)} p-5 text-left transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl border border-white/10`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500"></div>
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-bold text-white text-lg drop-shadow-lg">{policyName}</h3>
          <div className="p-2 bg-white/20 rounded-lg group-hover:bg-white/30 transition-colors">
            <ExternalLink className="w-4 h-4 text-white" />
          </div>
        </div>
        <p className="text-white/90 text-sm font-medium">View full policy details</p>
      </div>
    </button>
  )
}

// Policy Modal Component
function PolicyModal({ policyName, isOpen, onClose }: { policyName: string; isOpen: boolean; onClose: () => void }) {
  const [details, setDetails] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    if (isOpen && !details) {
      setIsLoading(true)
      fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'}/api/policy/details?policy_name=${encodeURIComponent(policyName)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            setDetails(data.summary)
          }
          setIsLoading(false)
        })
        .catch(() => setIsLoading(false))
    }
  }, [isOpen, policyName, details])
  
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="relative bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 max-w-3xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between border-b border-gray-700">
          <h2 className="text-xl font-bold text-white">{policyName}</h2>
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

<<<<<<< Updated upstream
// Enhanced Message Renderer with cards
function EnhancedMarkdown({ content }: { content: string }) {
  const [selectedPolicy, setSelectedPolicy] = useState<string | null>(null)
=======
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
      
      // Priority: Use extracted_data from PDF first, then tripDetails.travelers
      const extractedTravelers = tripDetails?.extracted_data?.travelers || tripDetails?.travelers
      
      if (Array.isArray(extractedTravelers) && extractedTravelers.length > 0) {
        // Use ONLY names from PDF - leave age, email, phone empty for user to enter
        initialTravelers = extractedTravelers.map((t: any) => {
          const rawName = t.name || t.firstName || t.first_name || '';
          return {
            name: normalizeName(rawName), // ONLY autofill name (normalized to remove repeated chars)
            age: 0, // User must enter
            email: '', // User must enter
            phone: '', // User must enter (only for Traveller 1)
            dob: ''
          }
        })
      } else if (Array.isArray(tripDetails.travelers)) {
        // Fallback to tripDetails.travelers if extracted_data not available
        initialTravelers = tripDetails.travelers.map((t: any) => {
          const rawName = t.name || t.firstName || t.first_name || '';
          return {
            name: normalizeName(rawName), // ONLY autofill name (normalized to remove repeated chars)
            age: 0, // User must enter
            email: '', // User must enter
            phone: '', // User must enter (only for Traveller 1)
            dob: ''
          }
        })
      } else if (tripDetails.travelers && typeof tripDetails.travelers === 'number') {
        // If travelers is a number, create empty slots
        const numTravelers = tripDetails.travelers
        initialTravelers = Array(numTravelers).fill(null).map(() => ({
          name: '',
          age: 0,
          email: '',
          phone: '',
          dob: ''
        }))
      } else {
        // Try to get count from adults + children
        const numAdults = tripDetails.adults || 1
        const numChildren = tripDetails.children || 0
        const totalTravelers = numAdults + numChildren
        initialTravelers = Array(totalTravelers).fill(null).map(() => ({
          name: '',
          age: 0, // User must enter - no default
          email: '',
          phone: '',
          dob: ''
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
    // Validation: Different requirements for Traveller 1 vs others
    const isTraveller1 = step === 1
    const hasName = currentTraveler.name.trim() !== ''
    const hasAge = currentTraveler.age > 0
    
    // Traveller 1 requires: name, age, email, phone
    // Travellers 2+ require: name, age only
    const isValid = hasName && hasAge && (
      isTraveller1 
        ? (currentTraveler.email.trim() !== '' && currentTraveler.phone.trim() !== '')
        : true // Travellers 2+ don't need email/phone
    )
    
    if (isValid) {
      const updated = [...travelers]
      // Update existing traveler if editing, otherwise add new
      if (step <= travelers.length) {
        updated[step - 1] = currentTraveler
      } else {
        updated.push(currentTraveler)
      }
      setTravelers(updated)
      
      // Calculate numTravelers for this check
      const totalTravelers = (() => {
        if (!tripDetails) return Math.max(travelers.length, 1)
        if (Array.isArray(tripDetails.travelers)) {
          return tripDetails.travelers.length
        }
        if (typeof tripDetails.travelers === 'number') {
          return tripDetails.travelers
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
        // All travelers complete - move to payment step
        setStep(totalTravelers + 1)
        // Auto-fill payment cardholder name with Traveller 1's name
        if (updated[0] && updated[0].name) {
          setPaymentInfo(prev => ({ ...prev, cardName: updated[0].name }))
        }
      }
    }
  }
  
  useEffect(() => {
    // Pre-fill current traveler data if editing existing
    if (step <= travelers.length && travelers[step - 1]) {
      setCurrentTraveler(travelers[step - 1])
    } else if (step > travelers.length) {
      // Payment step - auto-fill cardholder name with Traveller 1's name
      if (travelers.length > 0 && travelers[0]?.name) {
        setPaymentInfo(prev => ({ ...prev, cardName: travelers[0].name }))
      }
      // Clear for new traveler (not applicable for payment step)
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
    
    // Get extracted data from PDF - check multiple sources
    const extractedTravelers = tripDetails?.extracted_data?.travelers || tripDetails?.travelers || []
    
    // Only autofill if we have REAL extracted data from PDF
    if (!extractedTravelers || extractedTravelers.length === 0) {
      alert('No traveler information found in uploaded document. Please enter details manually.')
      setIsAutoFilling(false)
      return
    }
    
    // Auto-fill ONLY names from PDF - leave age, email, phone empty
    const autoTravelers = travelers.map((t, idx) => {
      const extracted = extractedTravelers[idx]
      
      if (!extracted) {
        // If no extracted data for this traveler, leave everything empty
        return {
          name: '',
          age: 0,
          email: '',
          phone: '',
          dob: ''
        }
      }
      
      // ONLY autofill name from PDF - user must enter age, email, phone
      // Normalize the name to remove repeated characters (common in PDF extraction)
      const rawName = extracted.name || extracted.firstName || extracted.first_name || '';
      const normalizedName = normalizeName(rawName);
      
      return {
        name: normalizedName,
        age: 0, // User must enter
        email: '', // User must enter (only for Traveller 1)
        phone: '', // User must enter (only for Traveller 1)
        dob: ''
      }
    })
    
    // Fill all travelers with names only
    setTravelers(autoTravelers)
    
    // If single traveller, go to step 1 and let them fill age/email/phone
    // If multiple travellers, start at step 1
    setStep(1)
    setCurrentTraveler(autoTravelers[0] || { name: '', age: 0, email: '', phone: '', dob: '' })
    
    await delay(500)
    setIsAutoFilling(false)
  }

  if (!isOpen) return null

  const cleanedName = cleanPolicyName(quote.plan_name)
  
  // Calculate number of travelers - use actual travelers array length if available
  const numTravelers = (() => {
    // Priority: Use actual travelers array length (from extracted PDF data)
    if (travelers.length > 0) {
      return travelers.length
    }
    // Fallback to tripDetails
    if (!tripDetails) return 1
    if (Array.isArray(tripDetails.travelers)) {
      return tripDetails.travelers.length
    }
    if (typeof tripDetails.travelers === 'number') {
      return tripDetails.travelers
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
            <p className="text-sm text-white/80">Step {step} of {numTravelers + 1}</p>
          </div>
          <div className="flex items-center gap-2">
            {!isAutoFilling && (
              <button 
                onClick={handleAutoFill}
                className="px-3 py-1.5 bg-white/20 hover:bg-white/30 border border-white/30 rounded-lg transition-all text-white text-xs font-semibold flex items-center gap-1.5 backdrop-blur-sm"
                title="Auto-fill traveler details from uploaded PDF"
              >
                <Sparkles className="w-3 h-3" />
                AI Auto-Fill from PDF
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
                {/* Email and Phone only required for Traveller 1 */}
                {step === 1 && (
                  <>
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
                  </>
                )}
                <button
                  onClick={handleAddTraveler}
                  disabled={(() => {
                    const hasName = currentTraveler.name.trim() !== ''
                    const hasAge = currentTraveler.age > 0
                    const isTraveller1 = step === 1
                    // Traveller 1 needs: name, age, email, phone
                    // Travellers 2+ need: name, age only
                    if (isTraveller1) {
                      return !hasName || !hasAge || currentTraveler.email.trim() === '' || currentTraveler.phone.trim() === ''
                    } else {
                      return !hasName || !hasAge
                    }
                  })()}
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
                    value={paymentInfo.cardName || (travelers[0]?.name || '')}
                    onChange={(e) => setPaymentInfo({ ...paymentInfo, cardName: e.target.value })}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                    placeholder="John Doe"
                  />
                  {travelers[0]?.name && (
                    <p className="text-xs text-gray-400 mt-1">Auto-filled from Traveller 1: {travelers[0].name}</p>
                  )}
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
function QuoteCard({ quote, quoteId, tripDetails, onPurchase, language = 'en', claimsAnalysis }: { 
  quote: { plan_name: string; price: number; currency: string; recommended_for: string; offer_id?: string; product_code?: string; source?: string; score?: number; benefits?: string[]; reasons?: string[]; cost_source?: string; claims_analysis?: any }
  quoteId?: string
  tripDetails?: any
  onPurchase: (quote: any, insureds: any[], paymentInfo: any) => void
  language?: string
  claimsAnalysis?: any
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
        {/* Claims Analysis Display */}
        {(claimsAnalysis || quote.claims_analysis) && (() => {
          const analysis = claimsAnalysis || quote.claims_analysis
          const policyAnalysis = analysis?.policy_analysis?.[quote.plan_name]
          if (policyAnalysis && policyAnalysis.total_claims > 0) {
            return (
              <div className="mb-4 p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
                <p className="text-xs text-blue-300 font-semibold mb-2">📊 Historical Claims Data</p>
                <div className="space-y-1 text-xs text-gray-300">
                  <div className="flex justify-between">
                    <span>Total Claims:</span>
                    <span className="text-blue-400">{policyAnalysis.total_claims}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Approval Rate:</span>
                    <span className="text-green-400">{policyAnalysis.approval_rate}%</span>
                  </div>
                  {policyAnalysis.average_payout > 0 && (
                    <div className="flex justify-between">
                      <span>Avg Payout:</span>
                      <span className="text-yellow-400">${policyAnalysis.average_payout.toLocaleString()}</span>
                    </div>
                  )}
                </div>
              </div>
            )
          }
          return null
        })()}
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
function EnhancedMarkdown({ content, quotes, language = 'en', claimsData }: { content: string; quotes?: any[]; language?: string; claimsData?: any }) {
  const [selectedPolicy, setSelectedPolicy] = useState<any | null>(null)
>>>>>>> Stashed changes
  
  // Extract policy mentions
  const policyRegex = /(TravelEasy|Scootsurance|MSIG|Policy:\s*[^\]]+)/gi
  const policies = Array.from(new Set(content.match(policyRegex)?.map(m => m.replace(/Policy:\s*/i, '').trim()) || []))
  
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
            const policyMatch = text.match(/(TravelEasy|Scootsurance|MSIG|Policy:?\s*[^\]\s]+)/i)
            
            if (policyMatch) {
              const policyName = policyMatch[1].replace(/Policy:\s*/i, '').trim()
              return (
                <button
                  onClick={() => setSelectedPolicy(policyName)}
                  className="text-blue-400 font-semibold bg-blue-900/40 px-2 py-1 rounded-md hover:bg-blue-900/60 transition-all border border-blue-700/40 shadow-sm hover:shadow-md hover:scale-105 inline-flex items-center gap-1"
                >
                  {children}
                  <ExternalLink className="w-3 h-3" />
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
            <h1 className="text-2xl font-bold text-white mb-4 mt-6 bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-white mb-3 mt-5 bg-gradient-to-r from-blue-300 to-indigo-300 bg-clip-text text-transparent">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-gray-200 mb-2 mt-4">{children}</h3>
          ),
          hr: () => (
            <div className="my-6">
              <hr className="border-gray-700/50" />
            </div>
          ),
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
      
      {/* Policy Cards Section */}
      {policies.length > 0 && (
        <div className="mt-8 pt-6 border-t border-gray-700/50">
          <div className="mb-5">
            <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-400" />
              Referenced Policies
            </h3>
            <p className="text-gray-400 text-sm">Click any policy to view detailed information</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {policies.map((policy, idx) => (
              <PolicyCard
                key={idx}
                policyName={policy}
                onClick={() => setSelectedPolicy(policy)}
              />
            ))}
          </div>
        </div>
      )}
      
      {/* Policy Modal */}
      {selectedPolicy && (
        <PolicyModal
          policyName={selectedPolicy}
          isOpen={!!selectedPolicy}
          onClose={() => setSelectedPolicy(null)}
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
          setPolicyDetails(`Policy: ${policyName}\n\nUnable to load details.`)
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
  images?: Array<{ destination: string; keyword: string; url: string }>
  booking_links?: Array<{ type: string; platform: string; url: string; text: string }>
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
  const [language, setLanguage] = useState('en')
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [showHistory, setShowHistory] = useState(true)
  const [conversationThreads, setConversationThreads] = useState<ConversationThread[]>([])
  const [currentThreadId, setCurrentThreadId] = useState<string>('default')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<any>(null)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

  // Load chat history from localStorage
  useEffect(() => {
    const savedThreads = localStorage.getItem('wandersure_conversation_threads')
    if (savedThreads) {
      try {
        const threads = JSON.parse(savedThreads)
        setConversationThreads(threads.map((t: any) => ({
          ...t,
          timestamp: new Date(t.timestamp),
        })))
      } catch (e) {
        console.error('Failed to load conversation threads:', e)
      }
    }
  }, [])

  // Save conversation threads
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      const title = messages[0].role === 'assistant' 
        ? messages[0].content.substring(0, 50).replace(/[#*━]/g, '').trim()
        : messages[0].content.substring(0, 50).trim()
      
      const thread: ConversationThread = {
        id: currentThreadId,
        title: title || 'New Conversation',
        lastMessage: lastMessage.content.substring(0, 80).replace(/[#*━]/g, '').trim(),
        timestamp: lastMessage.timestamp,
        role: 'travel_agent', // Default role for compatibility
        messageCount: messages.length,
      }

      setConversationThreads(prev => {
        const filtered = prev.filter(t => t.id !== currentThreadId)
        const updated = [thread, ...filtered].slice(0, 20)
        localStorage.setItem('wandersure_conversation_threads', JSON.stringify(updated))
        return updated
      })
    }
  }, [messages.length])

  useEffect(() => {
    scrollToBottom()
    if (messages.length === 0) {
      initializeGreeting()
    }
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
<<<<<<< Updated upstream

  const initializeGreeting = async () => {
    try {
      const response = await fetch(`${API_URL}/api/greeting?user_id=user_${Date.now()}&language=${language}`)
      const data = await response.json()
      setMessages([{
        role: 'assistant',
        content: data.greeting || "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👋 Welcome! I'm Wanda, Your Travel Insurance Agent\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n• Expert travel insurance advice\n• Compare policies instantly\n• Get quotes in seconds\n• Secure payment in chat\n\nHow can I help protect your trip? ✈️",
        timestamp: new Date()
      }])
    } catch (error) {
      setMessages([{
        role: 'assistant',
        content: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👋 Welcome! I'm Wanda, Your Travel Insurance Agent\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n• Expert travel insurance advice\n• Compare policies instantly\n• Get quotes in seconds\n\nHow can I help protect your trip? ✈️",
        timestamp: new Date()
      }])
=======
  
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
  
  // Create new chat
  const createNewChat = () => {
    // Save current chat to history
    if (messages.length > 0) {
      const title = messages[0].content.substring(0, 50).replace(/[#*━]/g, '').trim() || 'Chat'
      const newThread: ConversationThread = {
        id: `thread_${Date.now()}`,
        title: title,
        lastMessage: messages[messages.length - 1].content.substring(0, 80),
        timestamp: new Date(),
        role: 'travel_agent',
        messageCount: messages.length
      }
      
      setConversationThreads(prev => [newThread, ...prev])
      
      // Save to localStorage
      const threads = JSON.parse(localStorage.getItem('wandersure_conversation_threads') || '[]')
      threads.unshift({
        ...newThread,
        messages: messages.map(m => ({ ...m, timestamp: m.timestamp.toISOString() }))
      })
      localStorage.setItem('wandersure_conversation_threads', JSON.stringify(threads))
    }
    
    // Save current messages before switching
    if (messages.length > 0 && currentThreadId) {
      localStorage.setItem(`wandersure_thread_${currentThreadId}`, JSON.stringify(
        messages.map(m => ({ ...m, timestamp: m.timestamp.toISOString() }))
      ))
    }
    
    // Reset for new chat
    setMessages([])
    const newThreadId = `thread_${Date.now()}`
    setCurrentThreadId(newThreadId)
    initializeGreeting()
  }

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
      window.loadGoogleTranslate = function() {
        if (window.google && window.google.translate && window.google.translate.TranslateElement) {
          new window.google.translate.TranslateElement({
            pageLanguage: 'en',
            includedLanguages: 'en,ta,zh-CN,ms-MY',
            layout: window.google.translate.TranslateElement.InlineLayout.SIMPLE,
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
      } else if (window.loadGoogleTranslate) {
        // Script already loaded, just call it
        window.loadGoogleTranslate();
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
    
    // Try to fetch personalized greeting from API using robust client
    try {
      const apiModule = await import('../lib/api-client')
      const result = await apiModule.api.greeting(`user_${Date.now()}`, language)
      
      if (result.success && (result.data as any)?.greeting) {
        setMessages([{
          role: 'assistant',
          content: (result.data as any).greeting,
          timestamp: new Date()
        }])
      }
    } catch (error) {
      // Keep the default greeting if API fails
      console.log('Greeting API not available, using default:', error)
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
      const response = await fetch(`${API_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentInput,
          language: language,
          user_id: 'default_user',
          is_voice: false
        })
=======
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
      
      // Use robust API client
      const apiModule = await import('../lib/api-client')
      const result = await apiModule.api.ask(currentInput, {
        userId: userData?.user_id || 'default_user',
        language: language,
        contextData: {
          ...contextData,
          user_data: userData  // Pass user data (age, interests, medical conditions)
        },
        isVoice: false
>>>>>>> Stashed changes
      })

      if (!result.success) {
        // Handle API errors
        let errorContent = ''
        switch (result.error_code) {
          case 'NETWORK_ERROR':
            errorContent = '**🔌 Connection Error**\n\n• Cannot connect to the backend server\n• **The server might not be running!**\n\n**To fix:**\n1. Open terminal in the project folder\n2. Run: `PORT=8002 python3 run_server.py`\n3. Wait for "Application startup complete"\n4. Try again\n\n**Or check:**\n• Is the server running? (Check terminal)\n• Is it on port 8002?'
            break
          case 'TIMEOUT':
            errorContent = '**⏱️ Request Timeout**\n\n• Your request took too long to process\n• The server may be slow or overloaded\n\n**Try:**\n• Wait a moment and try again\n• Rephrase your question to be simpler'
            break
          case 'VALIDATION_ERROR':
            errorContent = `**⚠️ Validation Error**\n\n${result.message}\n\nPlease check your input and try again.`
            break
          case 'SERVER_ERROR':
            errorContent = '**⚠️ Server Error**\n\n• The server is experiencing issues\n• This is usually temporary\n• Please try again in a moment'
            break
          default:
            errorContent = `**😅 Oops!**\n\n${result.message || 'An unexpected error occurred'}\n\n**Try:**\n• Rephrasing your question\n• Asking something simpler like "What can you help me with?"`
        }
        
        const errorMessage: Message = {
          role: 'assistant',
          content: errorContent,
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
        return
      }

<<<<<<< Updated upstream
      const data = await response.json()
      
      const answerText = typeof data === 'string' ? data : (data.answer || data.message || 'I apologize, but I encountered an error.')
=======
      const data = result.data as any
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
>>>>>>> Stashed changes
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: answerText,
        timestamp: new Date(),
        images: data.images || [],
        booking_links: data.booking_links || []
      }

      setMessages(prev => [...prev, assistantMessage])
      
      if (isSpeaking) {
        speakText(answerText)
      }
<<<<<<< Updated upstream
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: '⚠️ **Error**\n\n• I encountered an error processing your request\n• Please try again',
=======
    } catch (error: any) {
      console.error('Unexpected error:', error)
      
      const errorMessage: Message = {
        role: 'assistant',
        content: '**😅 Oops!**\n\n• I encountered an unexpected error\n• But don\'t worry - I\'m here to help!\n\n**Try:**\n• Rephrasing your question\n• Asking something simpler like "What can you help me with?"\n• Or just say "hi" to start fresh',
>>>>>>> Stashed changes
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
    
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target?.result as string
      
      try {
        const extractResponse = await fetch(`${API_URL}/api/extract`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            document_data: base64,
            document_type: file.type.includes('pdf') ? 'pdf' : file.type.includes('image') ? 'image' : 'text'
          })
        })
        
        if (!extractResponse.ok) {
          throw new Error(`Extract failed: ${extractResponse.status}`)
        }
        
        const extractData = await extractResponse.json()
        console.log('Extract response:', extractData)
        
        if (extractData.success && extractData.extracted_data) {
          const tripInfo = extractData.extracted_data
          
          const quoteResponse = await fetch(`${API_URL}/api/quote`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              destination: tripInfo.destination || 'Unknown',
              start_date: tripInfo.departure_date || tripInfo.start_date,
              end_date: tripInfo.return_date || tripInfo.end_date,
              travelers: tripInfo.travelers?.length || 1,
              ages: tripInfo.travelers?.map((t: any) => t.age).filter(Boolean) || [],
              activities: tripInfo.activities || [],
              trip_cost: tripInfo.trip_cost
            })
          })
          
          const quoteData = await quoteResponse.json()
          
          // Ensure extracted_data is preserved in trip_details
          const tripDetailsWithExtracted = {
            ...(quoteData.trip_details || tripInfo),
            extracted_data: extractData.extracted_data || tripInfo, // Preserve full extracted data
            travelers: tripInfo.travelers || quoteData.trip_details?.travelers || []
          }
          
          const successMsg: Message = {
            role: 'assistant',
<<<<<<< Updated upstream
            content: `✅ **Document Processed Successfully!**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📄 Trip Details Extracted\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n${tripInfo.destination ? `• Destination: ${tripInfo.destination}` : ''}${tripInfo.departure_date ? `\n• Departure: ${tripInfo.departure_date}` : ''}${tripInfo.return_date ? `\n• Return: ${tripInfo.return_date}` : ''}${tripInfo.travelers?.length ? `\n• Travelers: ${tripInfo.travelers.length}` : ''}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💡 Insurance Recommendations\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n${quoteData.quotes?.map((q: any, i: number) => `• **${q.plan_name}**: $${q.price.toFixed(2)} - ${q.recommended_for}`).join('\n')}\n\nWhich plan would you like to learn more about?`,
            timestamp: new Date()
          }
          
          setMessages(prev => [...prev, successMsg])
=======
            content: `✅ **Document Processed Successfully!**\n\n### 📄 Trip Details Extracted\n\n${tripInfo.destination ? `• Destination: ${tripInfo.destination}` : ''}${tripInfo.departure_date ? `\n• Departure: ${tripInfo.departure_date}` : ''}${tripInfo.return_date ? `\n• Return: ${tripInfo.return_date}` : ''}${tripInfo.pax ? `\n• Travelers: ${tripInfo.pax}` : tripInfo.travelers?.length ? `\n• Travelers: ${tripInfo.travelers.length}` : ''}${claimsSection}\n\n### 💡 Insurance Recommendations\n\n${quotes.length > 0 ? quotes.map((q: any, i: number) => `• **${q.plan_name}**: $${q.price.toFixed(2)} ${q.currency || 'SGD'} ${q.score ? `(Score: ${q.score}/100)` : ''} - ${q.recommended_for}`).join('\n') : 'No quotes available'}\n\nWhich plan would you like to learn more about?`,
            timestamp: new Date(),
            quotes: quotes,
            quote_id: quoteData.quote_id || null,
            trip_details: tripDetailsWithExtracted
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
          
          // Preserve extracted_data in trip_details
          const tripDetailsWithExtracted = {
            ...tripInfo,
            extracted_data: tripInfo // The extracted_data IS tripInfo in this case
          }
          
          const partialMsgObj: Message = {
            role: 'assistant',
            content: partialMsg,
            timestamp: new Date(),
            trip_details: tripDetailsWithExtracted
          }
          setMessages(prev => [...prev, partialMsgObj])
>>>>>>> Stashed changes
        } else {
          throw new Error('Failed to extract trip information')
        }
      } catch (error) {
        console.error('File upload error:', error)
        const errorMsg: Message = {
          role: 'assistant',
          content: '⚠️ **Upload Error**\n\n• Could not extract trip information from document\n• Please try uploading a clearer document or describe your trip manually',
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
      recognition.lang = language === 'en' ? 'en-US' : language

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
      .replace(/━+/g, '')
      .replace(/[•▪▫◦]/g, '-')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/\[IMAGE:[^\]]+\]/g, '')
      .replace(/https?:\/\/[^\s]+/g, '')
      .trim();
    
    return cleaned.length > 10 ? cleaned : 'I have a response for you. Please check the chat window.';
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
      
      // Optionally clean on backend for consistency
      try {
        const response = await fetch(`${API_URL}/api/tts/clean`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: cleanedText })
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.text) {
            cleanedText = data.text;
          }
        }
      } catch (error) {
        // Use frontend-cleaned text if backend fails
        console.log('Backend text cleaning failed, using frontend version');
      }
      
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
      
      // Get the best available voice
      const voice = getBestVoice();
      if (voice) {
        utterance.voice = voice;
        utterance.lang = voice.lang;
      } else {
        utterance.lang = language === 'en' ? 'en-US' : language;
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
    <div className="h-screen bg-gray-900 text-gray-100 relative overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute top-1/4 right-0 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse-slow animation-delay-2000"></div>
        <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse-slow animation-delay-4000"></div>
        
        <div className="absolute inset-0 opacity-30">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${10 + Math.random() * 10}s`
              }}
            ></div>
          ))}
        </div>
        
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }}
        ></div>
      </div>

      <div className="flex flex-col h-screen relative z-10">
        {/* Chat History Sidebar */}
        <div className={`fixed left-0 top-0 bottom-0 w-80 bg-gray-800/95 backdrop-blur-xl border-r border-gray-700 z-20 transition-transform duration-300 ${showHistory ? 'translate-x-0' : '-translate-x-full'}`}>
          <div className="flex flex-col h-full">
            <div className="p-4 border-b border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <History className="w-5 h-5" />
                  Chat History
                </h2>
                <button
                  onClick={() => setShowHistory(false)}
                  className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <ChevronLeft className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-2 min-h-0 scrollbar-thin">
              {conversationThreads.length === 0 ? (
                <div className="text-center text-gray-500 text-sm py-8">
                  No conversation history yet
                </div>
              ) : (
                conversationThreads.map((thread) => {
                  return (
                    <div
                      key={thread.id}
                      onClick={() => {
                        // Load this conversation thread
                        setCurrentThreadId(thread.id)
                      }}
                      className={`p-3 rounded-lg cursor-pointer transition-all hover:bg-gray-700/50 border ${
                        thread.id === currentThreadId ? 'bg-gray-700/50 border-blue-500/50' : 'border-gray-700/50'
                      }`}
                    >
                      <div className="flex items-start gap-2 mb-2">
                        <div className="p-1.5 rounded bg-blue-600/20">
                          <Sparkles className="w-4 h-4 text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">{thread.title}</p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 line-clamp-2 mb-2">{thread.lastMessage}</p>
                      <div className="flex items-center justify-between text-xs text-gray-600">
                        <span>{thread.messageCount} messages</span>
                        <span>{new Date(thread.timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className={`flex-1 flex flex-col h-full overflow-hidden transition-all duration-300 ${showHistory ? 'ml-80' : 'ml-0'}`}>
          {/* Clean, Sleek Header - with backdrop blur */}
          <header className="bg-gray-800/90 backdrop-blur-md border-b border-gray-700 shadow-lg flex-shrink-0">
            <div className="max-w-5xl mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {!showHistory && (
                    <button
                      onClick={() => setShowHistory(true)}
                      className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                    >
                      <History className="w-5 h-5 text-gray-400" />
                    </button>
                  )}
                  <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2.5 rounded-lg shadow-md">
                    <Plane className="w-5 h-5 text-white animate-bounce" style={{ animationDuration: '2s' }} />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-white">WanderSure</h1>
                    <p className="text-xs text-gray-400">Wanda • Travel Insurance Agent</p>
                  </div>
                </div>
              </div>
            </div>
          </header>

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
                    <div className="flex items-start gap-3 max-w-[85%] animate-slide-in-left">
                      <div className="relative flex-shrink-0 group/avatar">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg blur opacity-50 animate-pulse-slow"></div>
                        <div className="relative bg-gradient-to-br from-blue-500 to-indigo-500 p-2 rounded-lg shadow-lg transform transition-transform duration-300 group-hover/avatar:scale-110">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      <div className="relative group flex-1">
                        <div className="absolute -inset-1 bg-gradient-to-r from-blue-600/20 via-indigo-600/20 to-purple-600/20 rounded-xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="relative bg-gray-800/95 rounded-2xl px-6 py-6 shadow-2xl border border-gray-700/50 backdrop-blur-md">
                          {/* Enhanced content with cards */}
                          <div className="relative prose prose-invert prose-sm max-w-none" style={{ fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
                        <EnhancedMarkdown
                          content={message.content
<<<<<<< Updated upstream
                            .replace(/━━━+/g, '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n')
                            .replace(/\*\*(Policy:|TravelEasy|Scootsurance|MSIG[^\*]*)\*\*/gi, '**$1**')
                            .replace(/(Policy:|TravelEasy|Scootsurance|MSIG[^•\n]*)/gi, '**$1**')}
                        />
                        </div>
                      
=======
                            .replace(/━━━+/g, '\n\n### ') // Convert separator lines to section headers
                            .replace(/^━+$/gm, '### ') // Convert standalone separator lines
                            .replace(/\*\*(Policy:|INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG[^\*]*)\*\*/gi, '**$1**')
                            .replace(/(Policy:|INTERNATIONAL TRAVEL|MHInsure Travel|Scootsurance|MSIG[^•\n]*)/gi, '**$1**')}
                          quotes={message.quotes}
                          language={language}
                          claimsData={(message as any).recommendations?.claims_data || (message as any).claims_data}
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
                                  claimsAnalysis={(message as any).recommendations?.claims_data || (message as any).claims_data}
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
                      
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
                        {/* Images - Fixed with proper Unsplash URLs */}
                        {message.images && message.images.length > 0 && (
                          <div className="mt-6 grid grid-cols-2 gap-4">
                            {message.images.map((img, i) => {
                              // Use Unsplash Source API - more reliable
                              const searchQuery = `${img.destination} ${img.keyword} travel`.replace(/\s+/g, '-').toLowerCase()
                              const imageUrl = `https://source.unsplash.com/800x600/?${searchQuery},travel,destination`
                              
                              return (
                                <div key={i} className="relative h-48 rounded-xl overflow-hidden border border-gray-600/50 shadow-lg group/image hover:border-blue-500/50 transition-all hover:scale-[1.02]">
                                  <img
                                    src={imageUrl}
                                    alt={`${img.destination} - ${img.keyword}`}
                                    className="w-full h-full object-cover transition-transform duration-300 group-hover/image:scale-110"
                                    loading="lazy"
                                    onError={(e) => {
                                      // Fallback to a working travel image
                                      const target = e.target as HTMLImageElement
                                      target.src = `https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&h=600&fit=crop&q=80`
                                      target.onerror = () => {
                                        target.src = `https://via.placeholder.com/800x600/1f2937/60a5fa?text=${encodeURIComponent(img.destination)}`
=======
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
                                      // Get latest quotes and trip details from messages for context
                                      const latestQuoteData = messages
                                        .filter((m: Message) => m.quotes && m.quotes.length > 0)
                                        .slice(-1)[0]
                                      
                                      const latestTripDetails = messages
                                        .filter((m: Message) => m.trip_details)
                                        .slice(-1)[0]?.trip_details
                                      
                                      const contextData: any = {
                                        user_data: userData
                                      }
                                      
                                      if (latestQuoteData?.quotes) {
                                        contextData.quotes = latestQuoteData.quotes
                                        contextData.trip_details = latestQuoteData.trip_details || latestTripDetails
                                      } else if (latestTripDetails) {
                                        contextData.trip_details = latestTripDetails
                                      }
                                      
                                      // Use robust API client
                                      const apiModule = await import('../lib/api-client')
                                      const result = await apiModule.api.ask(sq.question, {
                                        userId: userData?.user_id || 'default_user',
                                        language: language,
                                        contextData: contextData,
                                        isVoice: false
                                      })
                                      
                                      if (!result.success) {
                                        // Handle error
                                        const errorMsg: Message = {
                                          role: 'assistant',
                                          content: `**Error**\n\n${result.message || 'An error occurred'}`,
                                          timestamp: new Date()
                                        }
                                        setMessages(prev => [...prev, errorMsg])
                                        return
                                      }
                                      
                                      const data = result.data as any
                                      const answerText = typeof data === 'string' ? data : (data.answer || data.message || data.content || 'I apologize, but I encountered an error.')
                                      
                                      const assistantMsg: Message = {
                                        role: 'assistant',
                                        content: answerText,
                                        timestamp: new Date(),
                                        booking_links: data.booking_links || [],
                                        suggested_questions: data.suggested_questions || [],
                                        quotes: data.quotes || [],
                                        quote_id: data.quote_id || null,
                                        trip_details: data.trip_details || null
>>>>>>> Stashed changes
                                      }
                                    }}
                                  />
                                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent"></div>
                                  <div className="absolute bottom-0 left-0 right-0 p-4">
                                    <p className="text-white text-sm font-semibold drop-shadow-lg">{img.destination}</p>
                                    <p className="text-gray-300 text-xs mt-1">{img.keyword}</p>
                                  </div>
                                </div>
                              )
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {message.role === 'user' && (
                  <div className="relative group max-w-[85%] animate-slide-in-right">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity animate-pulse-glow"></div>
                    <div className="relative bg-gradient-to-br from-blue-600 via-blue-500 to-indigo-600 rounded-2xl px-6 py-4 shadow-xl border border-blue-400/20 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl">
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

          {/* Clean Input Bar - Dark Mode */}
          <div className="bg-gray-800/90 backdrop-blur-md border-t border-gray-700 p-4 shadow-lg flex-shrink-0">
          <div className="max-w-5xl mx-auto">
            <div className="flex items-center gap-2">
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
                className="p-2.5 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded-lg transition-colors"
                title="Upload document"
              >
                <Upload className="w-5 h-5" />
              </button>
              
              <div className="flex-1 bg-gray-700/80 rounded-xl border border-gray-600 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all backdrop-blur-sm">
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
                  className="w-full bg-transparent border-none outline-none px-4 py-3.5 text-gray-100 placeholder-gray-400 resize-none min-h-[48px] max-h-32 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent leading-relaxed"
                  style={{ 
                    fontSize: '15px',
                    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
                    letterSpacing: '0.01em'
                  }}
                  disabled={isLoading || isUploading}
                  rows={1}
                />
              </div>
              
              <button
                onClick={isListening ? stopVoiceInput : startVoiceInput}
                className={`p-2.5 rounded-lg transition-all ${
                  isListening 
                    ? 'bg-red-600 text-white animate-pulse' 
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
                }`}
                title="Voice input"
              >
                <Mic className="w-5 h-5" />
              </button>
              
              <button
                onClick={() => setIsSpeaking(!isSpeaking)}
                className={`p-2.5 rounded-lg transition-all ${
                  isSpeaking 
                    ? 'bg-emerald-600 text-white' 
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
                }`}
                title="Voice output"
              >
                <Volume2 className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim() || isUploading}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 font-semibold"
              >
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>
  )
}

