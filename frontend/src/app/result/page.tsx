// frontend/src/app/result/page.tsx
'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Card } from "@/components/ui/card"
import { ArrowRight } from 'lucide-react'
import Image from 'next/image'

export default function ResultPage() {
  const router = useRouter()
  const [canvasImageUrl, setCanvasImageUrl] = useState<string>('')
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string>('')
  const [topic, setTopic] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [deviceId, setDeviceId] = useState<string>('')

  useEffect(() => {
    const query = new URLSearchParams(window.location.search)
    const canvasUrl = query.get('canvasImageUrl') || ''
    const device_id = query.get('deviceId') || ''
    const currentTopic = query.get('topic') || ''

    if (canvasUrl && device_id && currentTopic) {
      setCanvasImageUrl(canvasUrl)
      setDeviceId(device_id)
      setTopic(currentTopic)
      setIsLoading(false)
    } else {
      // 必要なクエリパラメータが不足している場合、ホームページにリダイレクト
      router.push('/')
    }
  }, [router])

  useEffect(() => {
    if (deviceId) {
      // WebSocketの設定
      const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://'
      const wsHost = process.env.NEXT_PUBLIC_BACKEND_WS_HOST || 'localhost:8000'
      const socket = new WebSocket(`${wsProtocol}${wsHost}/ws/${deviceId}`)

      socket.onopen = () => {
        console.log('WebSocket接続が確立しました')
      }

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setGeneratedImageUrl(data.generatedImageUrl)
          console.log('生成された画像を受信しました:', data)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      socket.onerror = (error) => {
        console.error('WebSocketエラー:', error)
      }

      return () => {
        socket.close()
      }
    }
  }, [deviceId])

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">画像を読み込んでいます...</div>
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 p-4 sm:p-6 lg:p-8">
      <Card className="max-w-6xl mx-auto p-6 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-6 text-purple-600">生成結果</h1>
        <h2 className="text-xl font-semibold text-center mb-8 text-blue-500">お題：「{topic}」</h2>

        <div className="flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0 md:space-x-4">
          <div className="w-full md:w-1/3">
            <div className="relative aspect-square">
              <Image
                src={canvasImageUrl}
                alt="キャンバスの画像"
                fill
                style={{ objectFit: 'contain' }}
                className="rounded-lg shadow-md"
              />
            </div>
            <p className="text-center mt-2 text-gray-600">あなたの描いた絵</p>
          </div>

          <div className="flex items-center justify-center w-full md:w-1/6">
            <ArrowRight className="h-12 w-12 text-purple-500" />
          </div>

          <div className="w-full md:w-1/2">
            <div className="relative aspect-square">
              {generatedImageUrl ? (
                <Image
                  src={generatedImageUrl}
                  alt="生成された画像"
                  fill
                  style={{ objectFit: 'contain' }}
                  className="rounded-lg shadow-md"
                />
              ) : (
                <div className="absolute inset-0 bg-gray-200 flex items-center justify-center rounded-lg">
                  <p className="text-gray-500 text-xl">生成中...</p>
                </div>
              )}
            </div>
            <p className="text-center mt-2 text-gray-600">AIが生成した画像</p>
          </div>
        </div>
      </Card>
    </div>
  )
}
