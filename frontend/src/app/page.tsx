// frontend/src/app/page.tsx

'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import axios from 'axios'

export default function LandingPage() {
  const router = useRouter()
  const [deviceId, setDeviceId] = useState<string>('')
  // const [topic, setTopic] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // デバイスIDを取得または生成
    const storedDeviceId = localStorage.getItem('device_id')
    if (storedDeviceId) {
      setDeviceId(storedDeviceId)
      verifyDevice(storedDeviceId)
    } else {
      registerDevice()
    }
  }, [])

  const registerDevice = async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await axios.post(`${backendUrl}/register-device`)
      const newDeviceId = response.data.id
      localStorage.setItem('device_id', newDeviceId)
      setDeviceId(newDeviceId)
      // 初期トピックと画像エントリが含まれている
      if (response.data.images && response.data.images.length > 0) {
        const initialImage = response.data.images[0]
        localStorage.setItem('current_topic', initialImage.topic.name)
        localStorage.setItem('current_image_id', initialImage.id)
      }
    } catch (err) {
      console.error('デバイス登録中にエラーが発生しました:', err)
      setError('デバイスの登録に失敗しました。再試行してください。')
    }
  }

  const verifyDevice = async (deviceId: string) => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await axios.post(`${backendUrl}/verify-device`, { device_id: deviceId })
      // 最新の画像エントリからお題と画像IDを取得
      if (response.data.images && response.data.images.length > 0) {
        const latestImage = response.data.images[0]
        localStorage.setItem('current_topic', latestImage.topic.name)
        localStorage.setItem('current_image_id', latestImage.id)
      }
    } catch (err) {
      console.error('デバイス検証中にエラーが発生しました:', err)
      setError('デバイスの検証に失敗しました。再登録してください。')
      // デバイスを再登録
      localStorage.removeItem('device_id')
      registerDevice()
    }
  }

  const startGame = async () => {
    setLoading(true)
    setError(null)
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
      const response = await axios.post(`${backendUrl}/get-new-topic`, {
        device_id: deviceId
      })
      if (response.data.success) {
        const newTopic = response.data.topic
        const imageId = response.data.image_id
        // お題と画像IDをローカルストレージに保存
        localStorage.setItem('current_topic', newTopic)
        localStorage.setItem('current_image_id', imageId)
        // お絵かきページに遷移
        router.push(`/draw?image_id=${imageId}`)
      } else {
        setError('お題の取得に失敗しました。再試行してください。')
      }
    } catch (error) {
      console.error('お題の取得中にエラーが発生しました:', error)
      setError('お題の取得中にエラーが発生しました。再試行してください。')
    }
    setLoading(false)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 p-8">
      <h1 className="text-5xl font-bold text-purple-600 mb-8">AIお絵かきチャレンジ！</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}
      <Button onClick={startGame} disabled={loading}>
        {loading ? 'お題を取得中...' : 'スタート'}
      </Button>
    </div>
  )
}
