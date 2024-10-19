// frontend/src/app/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Shuffle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function LandingPage() {
  const [currentTopic, setCurrentTopic] = useState<string>('')
  const [deviceId, setDeviceId] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const storedDeviceId = localStorage.getItem('device_id')
    const storedTopic = localStorage.getItem('current_topic')

    if (storedDeviceId && storedTopic) {
      setDeviceId(storedDeviceId)
      setCurrentTopic(storedTopic)
    } else {
      // デバイス登録を自動的に行う
      registerDevice()
    }
  }, [])

  const registerDevice = async () => {
    setLoading(true)
    setError(null)
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await axios.post(`${backendUrl}/register-device`, {})
      if (response.data.success) {
        const { device_id, topic } = response.data
        // デバイスIDとお題をローカルストレージに保存
        localStorage.setItem('device_id', device_id)
        localStorage.setItem('current_topic', topic || '')
        setDeviceId(device_id)
        setCurrentTopic(topic || '')
      } else {
        setError('デバイスの登録に失敗しました')
        console.error('デバイスの登録に失敗しました')
      }
    } catch (error) {
      setError('デバイスの登録中にエラーが発生しました')
      console.error('デバイスの登録中にエラーが発生しました:', error)
    } finally {
      setLoading(false)
    }
  }

  const selectRandomTopic = async () => {
    if (!deviceId) {
      setError('デバイスIDが存在しません。しばらく待ってから再試行してください。')
      return
    }

    setLoading(true)
    setError(null)
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await axios.post(`${backendUrl}/get-new-topic`, {
        device_id: deviceId,
      })
      if (response.data.success && response.data.topic) {
        const newTopic = response.data.topic
        localStorage.setItem('current_topic', newTopic)
        setCurrentTopic(newTopic)
      } else {
        setError('新しいお題の取得に失敗しました')
        console.error('新しいお題の取得に失敗しました')
      }
    } catch (error) {
      setError('新しいお題の取得中にエラーが発生しました')
      console.error('新しいお題の取得中にエラーが発生しました:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStartDrawing = () => {
    if (currentTopic) {
      router.push('/draw')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
        <h1 className="text-4xl sm:text-5xl font-bold mb-6 text-purple-600">
          <span className="inline-block">Quick Diffusion</span>
        </h1>

        <h2 className="text-2xl sm:text-3xl font-semibold mb-8 text-blue-500">
          お題：「{currentTopic || '...'}」
        </h2>

        {error && <p className="text-red-500 mb-4">{error}</p>}

        <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Button
            onClick={selectRandomTopic}
            className="bg-purple-500 hover:bg-purple-600 text-white flex items-center px-6 py-3"
            disabled={loading || !deviceId}
          >
            <Shuffle className="mr-2 h-5 w-5" />
            お題を選び直す
          </Button>

          <Button
            onClick={handleStartDrawing}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3"
            disabled={!currentTopic || loading}
          >
            描き始める
          </Button>
        </div>
      </Card>
    </div>
  )
}
