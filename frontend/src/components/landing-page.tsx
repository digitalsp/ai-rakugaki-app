'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Shuffle } from 'lucide-react'
import { useRouter } from 'next/navigation'

const topics = [
  "うちゅうせん",
  "かいじゅう",
  "おばけ",
  "ロボット",
  "まほうつかい",
  "ゆめのせかい",
  "たからもの",
  "ともだち",
  "ぼうけん",
  "おんがく"
]

export default function LandingPage() {
  const [currentTopic, setCurrentTopic] = useState('')
  const router = useRouter()

  useEffect(() => {
    selectRandomTopic()
  }, [])

  const selectRandomTopic = () => {
    const randomIndex = Math.floor(Math.random() * topics.length)
    setCurrentTopic(topics[randomIndex])
  }

  const handleStartDrawing = async () => {
    try {
      const response = await fetch('/api/set-topic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: currentTopic }),
      })
      if (response.ok) {
        router.push('/draw')
      } else {
        console.error('トピックの設定に失敗しました')
      }
    } catch (error) {
      console.error('トピックの設定中にエラーが発生しました:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
        <h1 className="text-4xl sm:text-5xl font-bold mb-6 text-purple-600">
          <span className="inline-block">Quick Diffusion</span>
        </h1>
        
        <h2 className="text-2xl sm:text-3xl font-semibold mb-8 text-blue-500">
          お題：「{currentTopic}」
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
            onClick={handleStartDrawing}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3"
          >
            描き始める
          </Button>
        </div>
      </Card>
    </div>
  )
}
