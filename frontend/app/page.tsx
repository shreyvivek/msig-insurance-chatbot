'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Mic, Volume2, Sparkles, Plane, Upload, X, History, ChevronLeft, ExternalLink } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

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

  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = language === 'en' ? 'en-US' : language
      utterance.rate = 1.0
      utterance.pitch = 1.1
      utterance.volume = 1.0
      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(utterance)
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
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex items-start gap-3 max-w-[85%]">
                      <div className="relative flex-shrink-0">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg blur opacity-50"></div>
                        <div className="relative bg-gradient-to-br from-blue-500 to-indigo-500 p-2 rounded-lg shadow-lg">
                          <Sparkles className="w-4 h-4 text-white" />
                        </div>
                      </div>
                      <div className="relative group flex-1">
                        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600/20 via-indigo-600/20 to-purple-600/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div className="relative bg-gradient-to-br from-gray-800 via-gray-800 to-gray-900 rounded-2xl px-6 py-5 shadow-2xl border border-gray-700/50 backdrop-blur-sm">
                          <div className="prose prose-invert prose-sm max-w-none" style={{ fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <p className="mb-3 text-gray-200 leading-relaxed whitespace-pre-wrap font-normal text-[15px]" style={{ letterSpacing: '0.01em' }}>{children}</p>,
                            ul: ({ children }) => <ul className="mb-4 space-y-2 list-none pl-0 my-3">{children}</ul>,
                            ol: ({ children }) => <ol className="mb-4 space-y-2 list-decimal pl-5 my-3">{children}</ol>,
                            li: ({ children, node }) => {
                              const text = typeof children === 'string' ? children : String(children)
                              const isPolicy = /Policy:|\[Policy:|TravelEasy|Scootsurance|MSIG/i.test(text)
                              
                              const processText = (text: string) => {
                                const policyRegex = /(TravelEasy|Scootsurance|MSIG|Policy:\s*[^\]]+)/gi
                                const parts = []
                                let lastIndex = 0
                                let match
                                
                                while ((match = policyRegex.exec(text)) !== null) {
                                  if (match.index > lastIndex) {
                                    parts.push(text.substring(lastIndex, match.index))
                                  }
                                  
                                  const policyName = match[1].replace(/Policy:\s*/i, '').trim()
                                  parts.push(
                                    <PolicyTooltip key={match.index} policyName={policyName}>
                                      <span className="text-blue-300 font-medium cursor-help hover:text-blue-200 transition-colors underline decoration-blue-500/30 decoration-dotted underline-offset-2">
                                        {match[0]}
                                      </span>
                                    </PolicyTooltip>
                                  )
                                  
                                  lastIndex = match.index + match[0].length
                                }
                                
                                if (lastIndex < text.length) {
                                  parts.push(text.substring(lastIndex))
                                }
                                
                                return parts.length > 0 ? parts : [text]
                              }
                              
                              return (
                                <li className="flex items-start gap-3 text-gray-200 mb-3 leading-relaxed group/item">
                                  <span className="text-blue-400 mt-1 flex-shrink-0 font-bold text-xl leading-none">•</span>
                                  <span className={`flex-1 text-[15px] font-normal ${isPolicy ? 'font-medium' : ''}`} style={{ letterSpacing: '0.01em', lineHeight: '1.6' }}>
                                    {text.replace(/^•\s*/, '').split('\n').map((line, i, arr) => (
                                      <span key={i}>
                                        {processText(line)}
                                        {i < arr.length - 1 && <br />}
                                      </span>
                                    ))}
                                  </span>
                                </li>
                              )
                            },
                            strong: ({ children }) => {
                              const text = String(children)
                              const policyMatch = text.match(/(TravelEasy|Scootsurance|MSIG|Policy:?\s*[^\]\s]+)/i)
                              
                              if (policyMatch) {
                                const policyName = policyMatch[1].replace(/Policy:\s*/i, '').trim()
                                return (
                                  <PolicyTooltip policyName={policyName}>
                                    <strong className="text-blue-400 font-semibold bg-blue-900/40 px-2 py-1 rounded-md cursor-help hover:bg-blue-900/60 transition-all border border-blue-700/40 shadow-sm hover:shadow-md hover:scale-105">
                                      {children}
                                    </strong>
                                  </PolicyTooltip>
                                )
                              }
                              return <strong className="text-white font-semibold">{children}</strong>
                            },
                            hr: () => <div className="my-6"><hr className="border-gray-700/50" /></div>,
                            h1: ({ children }) => <h1 className="text-xl font-bold text-white mb-4 mt-6 tracking-tight" style={{ letterSpacing: '-0.02em' }}>{children}</h1>,
                            h2: ({ children }) => <h2 className="text-lg font-semibold text-white mb-3 mt-5 tracking-tight" style={{ letterSpacing: '-0.01em' }}>{children}</h2>,
                            h3: ({ children }) => <h3 className="text-base font-semibold text-gray-200 mb-2 mt-4 tracking-tight">{children}</h3>
                          }}
                        >
                          {message.content
                            .replace(/━━━+/g, '\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n')
                            .replace(/\*\*(Policy:|TravelEasy|Scootsurance|MSIG[^\*]*)\*\*/gi, '**$1**')
                            .replace(/(Policy:|TravelEasy|Scootsurance|MSIG[^•\n]*)/gi, '**$1**')
                          }
                        </ReactMarkdown>
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
                  <div className="relative group max-w-[85%]">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
                    <div className="relative bg-gradient-to-br from-blue-600 via-blue-500 to-indigo-600 rounded-2xl px-6 py-4 shadow-xl border border-blue-400/20">
                      <p className="text-white font-medium whitespace-pre-wrap leading-relaxed tracking-wide">{message.content}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
            </div>
            
            {isLoading && (
              <div className="flex justify-start gap-3">
                <div className="relative flex-shrink-0">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg blur opacity-50"></div>
                  <div className="relative bg-gradient-to-br from-blue-500 to-indigo-500 p-2 rounded-lg shadow-lg">
                    <Sparkles className="w-4 h-4 text-white animate-spin" />
                  </div>
                </div>
                <div className="relative">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 rounded-xl blur"></div>
                  <div className="relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl px-5 py-4 shadow-xl border border-gray-700/50">
                    <div className="flex gap-2">
                      <div className="w-2.5 h-2.5 bg-blue-400 rounded-full animate-bounce shadow-lg shadow-blue-500/50" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-indigo-400 rounded-full animate-bounce shadow-lg shadow-indigo-500/50" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2.5 h-2.5 bg-purple-400 rounded-full animate-bounce shadow-lg shadow-purple-500/50" style={{ animationDelay: '300ms' }}></div>
                    </div>
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

