'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Mic, Volume2, Sparkles, Plane, Upload, X, History, ChevronLeft, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

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

// Enhanced Message Renderer with cards
function EnhancedMarkdown({ content }: { content: string }) {
  const [selectedPolicy, setSelectedPolicy] = useState<string | null>(null)
  
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
      const response = await fetch(`${API_URL}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: currentInput,
          language: language,
          user_id: 'default_user',
          is_voice: false
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const answerText = typeof data === 'string' ? data : (data.answer || data.message || 'I apologize, but I encountered an error.')
      
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
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: '⚠️ **Error**\n\n• I encountered an error processing your request\n• Please try again',
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
          
          const successMsg: Message = {
            role: 'assistant',
            content: `✅ **Document Processed Successfully!**\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📄 Trip Details Extracted\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n${tripInfo.destination ? `• Destination: ${tripInfo.destination}` : ''}${tripInfo.departure_date ? `\n• Departure: ${tripInfo.departure_date}` : ''}${tripInfo.return_date ? `\n• Return: ${tripInfo.return_date}` : ''}${tripInfo.travelers?.length ? `\n• Travelers: ${tripInfo.travelers.length}` : ''}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n💡 Insurance Recommendations\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n${quoteData.quotes?.map((q: any, i: number) => `• **${q.plan_name}**: $${q.price.toFixed(2)} - ${q.recommended_for}`).join('\n')}\n\nWhich plan would you like to learn more about?`,
            timestamp: new Date()
          }
          
          setMessages(prev => [...prev, successMsg])
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
                            .replace(/━━━+/g, '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n')
                            .replace(/\*\*(Policy:|TravelEasy|Scootsurance|MSIG[^\*]*)\*\*/gi, '**$1**')
                            .replace(/(Policy:|TravelEasy|Scootsurance|MSIG[^•\n]*)/gi, '**$1**')}
                        />
                        </div>
                      
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

