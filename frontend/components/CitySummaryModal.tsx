'use client'

import React, { useState } from 'react'

interface CitySummaryData {
  city: string
  summary: string
  statistics: {
    total_posts: number
    positive: number
    neutral: number
    negative: number
    average_score: number
  }
  sample_posts?: Array<{
    text: string
    platform: string
    score: number
    label: string
    url?: string  // Reddit post URL
    author?: string  // Reddit author
  }>
  timestamp: string
}

interface CitySummaryModalProps {
  open: boolean
  city?: string
  onClose: () => void
  apiBaseUrl: string
}

export default function CitySummaryModal({
  open,
  city,
  onClose,
  apiBaseUrl
}: CitySummaryModalProps) {
  const [summaryData, setSummaryData] = useState<CitySummaryData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioLoading, setAudioLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [audioPlaying, setAudioPlaying] = useState(false)
  const audioRef = React.useRef<HTMLAudioElement | null>(null)

  React.useEffect(() => {
    if (open && city && !summaryData) {
      fetchCitySummary()
    }
    if (!open) {
      // Reset state when modal closes
      setSummaryData(null)
      setError(null)
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
      setAudioUrl(null)
      setAudioPlaying(false)
    }
  }, [open, city])

  const fetchCitySummary = async () => {
    if (!city) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/city/summary?city=${encodeURIComponent(city)}&limit=50`
      )
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || `Failed to fetch summary: ${response.status}`
        
        // Check if it's a "no posts found" error (404)
        if (response.status === 404 || errorMessage.includes('No Reddit posts found')) {
          throw new Error(`No recent discussions found for ${city} on Reddit. This city might not have active Reddit communities or recent posts mentioning it. Try a different city or check back later.`)
        }
        
        throw new Error(errorMessage)
      }
      
      const data = await response.json()
      setSummaryData(data)
    } catch (err) {
      console.error('Error fetching city summary:', err)
      setError(err instanceof Error ? err.message : 'Failed to load summary')
    } finally {
      setLoading(false)
    }
  }

  const generateAudio = async () => {
    if (!city || !summaryData) return
    
    setAudioLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `${apiBaseUrl}/api/city/summary/audio?city=${encodeURIComponent(city)}&limit=50&format=base64`
      )
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail?.error || errorData.detail || 'Failed to generate audio')
      }
      
      const data = await response.json()
      
      // Convert base64 to blob URL
      const audioBlob = base64ToBlob(data.audio_base64, 'audio/mpeg')
      const url = URL.createObjectURL(audioBlob)
      setAudioUrl(url)
      
      // Create and configure audio element
      const audio = new Audio(url)
      audioRef.current = audio
      
      audio.onended = () => {
        setAudioPlaying(false)
      }
      
      audio.onerror = () => {
        setError('Failed to play audio')
        setAudioPlaying(false)
      }
      
      // Auto-play the audio
      audio.play()
      setAudioPlaying(true)
    } catch (err) {
      console.error('Error generating audio:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate audio')
    } finally {
      setAudioLoading(false)
    }
  }

  const togglePlayPause = () => {
    if (!audioRef.current) return

    if (audioPlaying) {
      audioRef.current.pause()
      setAudioPlaying(false)
    } else {
      audioRef.current.play()
      setAudioPlaying(true)
    }
  }

  const playAudio = (url: string) => {
    const audio = new Audio(url)
    audio.play()
    setAudioPlaying(true)
    
    audio.onended = () => {
      setAudioPlaying(false)
    }
    
    audio.onerror = () => {
      setError('Failed to play audio')
      setAudioPlaying(false)
    }
  }

  const base64ToBlob = (base64: string, mimeType: string): Blob => {
    const byteCharacters = atob(base64)
    const byteNumbers = new Array(byteCharacters.length)
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    
    const byteArray = new Uint8Array(byteNumbers)
    return new Blob([byteArray], { type: mimeType })
  }

  const getColorForSentiment = (score: number): string => {
    if (score > 0.3) return '#22c55e' // Green for positive
    if (score < -0.3) return '#ef4444' // Red for negative
    return '#eab308' // Yellow for neutral
  }

  const getSentimentLabel = (score: number): string => {
    if (score > 0.3) return 'Positive'
    if (score < -0.3) return 'Negative'
    return 'Neutral'
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 w-full max-w-3xl rounded-2xl border border-gray-700/50 shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-2xl">📍</span>
            </div>
            <div>
              <h3 className="font-bold text-xl text-white">
                {city || 'City'} Sentiment Summary
              </h3>
              <p className="text-sm text-gray-400">Real-time emotional analysis</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-gray-700/50 hover:bg-gray-600/50 transition-colors"
            aria-label="Close modal"
          >
            <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading && (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
              <p className="text-gray-300">Analyzing sentiment data for {city}...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <h4 className="font-semibold text-red-400">Error</h4>
                  <p className="text-sm text-red-300 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {summaryData && !loading && (
            <>
              {/* Statistics Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                  <p className="text-xs text-gray-400 mb-1">Total Posts</p>
                  <p className="text-2xl font-bold text-white">{summaryData.statistics.total_posts}</p>
                </div>
                <div className="bg-green-900/20 rounded-lg p-4 border border-green-500/30">
                  <p className="text-xs text-green-400 mb-1">Positive</p>
                  <p className="text-2xl font-bold text-green-400">{summaryData.statistics.positive}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {((summaryData.statistics.positive / summaryData.statistics.total_posts) * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-yellow-900/20 rounded-lg p-4 border border-yellow-500/30">
                  <p className="text-xs text-yellow-400 mb-1">Neutral</p>
                  <p className="text-2xl font-bold text-yellow-400">{summaryData.statistics.neutral}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {((summaryData.statistics.neutral / summaryData.statistics.total_posts) * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="bg-red-900/20 rounded-lg p-4 border border-red-500/30">
                  <p className="text-xs text-red-400 mb-1">Negative</p>
                  <p className="text-2xl font-bold text-red-400">{summaryData.statistics.negative}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {((summaryData.statistics.negative / summaryData.statistics.total_posts) * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Average Score */}
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-400">Average Sentiment Score</p>
                  <p className="text-sm font-semibold" style={{ color: getColorForSentiment(summaryData.statistics.average_score) }}>
                    {getSentimentLabel(summaryData.statistics.average_score)}
                  </p>
                </div>
                <div className="relative w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="absolute h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.abs(summaryData.statistics.average_score) * 100}%`,
                      left: summaryData.statistics.average_score < 0 ? `${50 - Math.abs(summaryData.statistics.average_score) * 50}%` : '50%',
                      backgroundColor: getColorForSentiment(summaryData.statistics.average_score)
                    }}
                  ></div>
                  <div className="absolute top-0 left-1/2 w-0.5 h-full bg-gray-500"></div>
                </div>
                <div className="flex justify-between mt-1 text-xs text-gray-500">
                  <span>-1.0</span>
                  <span>0</span>
                  <span>+1.0</span>
                </div>
              </div>

              {/* AI Summary */}
              <div className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-lg p-5 border border-blue-500/30">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-xl">🤖</span>
                  <h4 className="font-semibold text-blue-300">AI-Generated Summary</h4>
                </div>
                <p className="text-gray-200 leading-relaxed">{summaryData.summary}</p>
                <p className="text-xs text-gray-500 mt-3">
                  Generated at {new Date(summaryData.timestamp).toLocaleString()}
                </p>
              </div>

              {/* Audio Generation and Controls */}
              <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 rounded-lg p-5 border border-purple-500/30">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-xl">🎙️</span>
                  <h4 className="font-semibold text-purple-300">Voice Narration</h4>
                </div>
                
                {!audioUrl && !audioLoading && (
                  <button
                    onClick={generateAudio}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 shadow-lg"
                  >
                    <span className="text-xl">🎙️</span>
                    <span>Generate Audio Summary</span>
                  </button>
                )}

                {audioLoading && (
                  <div className="flex flex-col items-center justify-center py-8 gap-3">
                    <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin"></div>
                    <p className="text-purple-300">Synthesizing voice with ElevenLabs...</p>
                  </div>
                )}

                {audioUrl && !audioLoading && (
                  <div className="space-y-4">
                    {/* Play/Pause Control */}
                    <div className="flex items-center justify-center gap-6">
                      <button
                        onClick={togglePlayPause}
                        className="group relative bg-gradient-to-br from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-full p-6 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                        aria-label={audioPlaying ? 'Pause' : 'Play'}
                      >
                        {audioPlaying ? (
                          // Pause Icon
                          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                          </svg>
                        ) : (
                          // Play Icon
                          <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        )}
                        
                        {/* Ripple effect when playing */}
                        {audioPlaying && (
                          <span className="absolute inset-0 rounded-full bg-purple-500/30 animate-ping"></span>
                        )}
                      </button>

                      <div className="text-center">
                        <p className="text-white font-medium">
                          {audioPlaying ? '🔊 Now Playing' : '⏸️ Paused'}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          ElevenLabs AI Voice
                        </p>
                      </div>
                    </div>

                    {/* Waveform Visualization (when playing) */}
                    {audioPlaying && (
                      <div className="flex items-center justify-center gap-1 h-16 bg-black/20 rounded-lg p-2">
                        {[...Array(24)].map((_, i) => (
                          <div
                            key={i}
                            className="flex-1 bg-gradient-to-t from-purple-500 to-pink-500 rounded-full animate-pulse"
                            style={{
                              height: `${Math.random() * 60 + 20}%`,
                              animationDelay: `${i * 0.05}s`,
                              animationDuration: `${0.6 + Math.random() * 0.4}s`
                            }}
                          ></div>
                        ))}
                      </div>
                    )}

                    {/* Regenerate Button */}
                    <button
                      onClick={() => {
                        if (audioRef.current) {
                          audioRef.current.pause()
                          audioRef.current = null
                        }
                        if (audioUrl) {
                          URL.revokeObjectURL(audioUrl)
                        }
                        setAudioUrl(null)
                        setAudioPlaying(false)
                      }}
                      className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors text-sm"
                    >
                      Generate New Audio
                    </button>
                  </div>
                )}
              </div>

              {/* Sample Posts */}
              {summaryData.sample_posts && summaryData.sample_posts.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-300 text-sm">Sample Posts</h4>
                  {summaryData.sample_posts.map((post, i) => (
                    <div key={i} className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50 hover:border-gray-600/50 transition-colors">
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2 text-xs flex-wrap">
                          <span className="px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                            {post.platform}
                          </span>
                          <span 
                            className="px-2 py-0.5 rounded-full font-medium"
                            style={{ 
                              backgroundColor: `${getColorForSentiment(post.score)}20`,
                              color: getColorForSentiment(post.score)
                            }}
                          >
                            {post.label}
                          </span>
                          <span className="text-gray-500">
                            {post.score >= 0 ? '+' : ''}{post.score.toFixed(2)}
                          </span>
                          {post.author && (
                            <span className="text-gray-500">
                              by u/{post.author}
                            </span>
                          )}
                        </div>
                        {post.url && (
                          <a
                            href={post.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 px-2 py-1 rounded bg-orange-600/20 hover:bg-orange-600/30 text-orange-400 text-xs font-medium transition-colors whitespace-nowrap"
                            title="View on Reddit"
                          >
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
                            </svg>
                            <span>Reddit</span>
                          </a>
                        )}
                      </div>
                      <p className="text-sm text-gray-300 line-clamp-2">{post.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700/50 bg-gray-800/30">
          <button
            onClick={onClose}
            className="w-full bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
