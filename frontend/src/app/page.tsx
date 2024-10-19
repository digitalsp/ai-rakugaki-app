// frontend/src/app/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Shuffle } from 'lucide-react'
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function LandingPage() {
  const [currentTopic, setCurrentTopic] = useState('')
  const router = useRouter()

  useEffect(() => {
    registerDevice()
  }, [])

  const registerDevice = async () => {
    try {
      // デバイス登録リクエスト
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register-device`, {})
      if (response.data.success) {
        const { device_id, topic } = response.data
        // デバイスIDとお題をローカルストレージに保存
        localStorage.setItem('device_id', device_id)
        localStorage.setItem('current_topic', topic || '')
        setCurrentTopic(topic || '')
        // 描画ページにリダイレクト
        router.push('/draw')
      } else {
        console.error('デバイスの登録に失敗しました')
      }
    } catch (error) {
      console.error('デバイスの登録中にエラーが発生しました:', error)
    }
  }

  const selectRandomTopic = async () => {
    try {
      // 再度デバイスを登録し、新しいお題を取得
      const response = await axios.post(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register-device`, {})
      if (response.data.success) {
        const { topic } = response.data
        localStorage.setItem('current_topic', topic || '')
        setCurrentTopic(topic || '')
      } else {
        console.error('新しいお題の取得に失敗しました')
      }
    } catch (error) {
      console.error('新しいお題の取得中にエラーが発生しました:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
        <h1 className="text-4xl sm:text-5xl font-bold mb-6 text-purple-600">
          <span className="inline-block">Quick Diffusion</span>
        </h1>
        
        <h2 className="text-2xl sm:text-3xl font-semibold mb-8 text-blue-500">
          お題：「{currentTopic || '...' }」
        </h2>
        
        <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Button
            onClick={selectRandomTopic}
            className="bg-purple-500 hover:bg-purple-600 text-white flex items-center px-6 py-3"
          >
            <Shuffle className="mr-2 h-5 w-5" />
            お題を選び直す
          </Button>
          
          <Button
            onClick={() => router.push('/draw')}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3"
            disabled={!currentTopic}
          >
            描き始める
          </Button>
        </div>
      </Card>
    </div>
  )
}
