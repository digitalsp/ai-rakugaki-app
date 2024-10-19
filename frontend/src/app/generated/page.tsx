// frontend/src/app/generated/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function GeneratedPage() {
  const [canvasImage, setCanvasImage] = useState<string | null>(null)
  const [generatedImage, setGeneratedImage] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    const fetchImages = async () => {
      const deviceId = localStorage.getItem('device_id')
      if (!deviceId) {
        router.push('/')
        return
      }

      try {
        // 最新の画像情報をバックエンドから取得
        const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_URL}/latest-images`, {
          params: { device_id: deviceId },
        })

        if (response.data.success) {
          const { canvas_image_url, generated_image_url } = response.data
          setCanvasImage(canvas_image_url)
          setGeneratedImage(generated_image_url)
        } else {
          console.error('画像情報の取得に失敗しました')
        }
      } catch (error) {
        console.error('画像情報の取得中にエラーが発生しました:', error)
      }
    }

    fetchImages()
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex items-center justify-center p-4">
      <Card className="max-w-4xl w-full mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
        <h1 className="text-3xl sm:text-4xl font-bold mb-6 text-purple-600">生成された画像</h1>

        <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-8">
          {canvasImage && (
            <div className="flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-2 text-blue-500">保存済みキャンバス画像</h2>
              <img src={canvasImage} alt="Canvas" className="w-48 h-auto rounded-lg shadow-md" />
            </div>
          )}
          {generatedImage && (
            <div className="flex flex-col items-center">
              <h2 className="text-xl font-semibold mb-2 text-blue-500">生成後の画像</h2>
              <img src={generatedImage} alt="Generated" className="w-96 h-auto rounded-lg shadow-md" />
            </div>
          )}
        </div>

        <div className="mt-8">
          <Button onClick={() => router.push('/')} className="bg-green-500 hover:bg-green-600 text-white px-6 py-3">
            別のお題に挑戦
          </Button>
        </div>
      </Card>
    </div>
  )
}
