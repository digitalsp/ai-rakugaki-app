// frontend/src/app/result/page.tsx

'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Card } from "@/components/ui/card"
import { ArrowRight } from 'lucide-react'
import Image from 'next/image'
import axios from 'axios'

export default function ResultPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [canvasImageUrl, setCanvasImageUrl] = useState<string>('')
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string>('')
  const [topic, setTopic] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [deviceId, setDeviceId] = useState<string>('')

  useEffect(() => {
    const canvasUrl = searchParams.get('canvasImageUrl') || ''
    const device_id = searchParams.get('deviceId') || ''
    const currentTopic = searchParams.get('topic') || ''
    const genImageUrl = searchParams.get('generatedImageUrl') || ''

    if (canvasUrl && device_id && currentTopic && genImageUrl) {
      setCanvasImageUrl(canvasUrl)
      setGeneratedImageUrl(genImageUrl)
      setDeviceId(device_id)
      setTopic(currentTopic)
      setIsLoading(false)
    } else {
      // 必要なクエリパラメータが不足している場合、ホームページにリダイレクト
      router.push('/')
    }
  }, [searchParams, router])

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 p-4 sm:p-6 lg:p-8">
      {isLoading ? (
        <div className="flex justify-center items-center h-screen">画像を読み込んでいます...</div>
      ) : (
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
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
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
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
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
      )}
    </div>
  )
}
