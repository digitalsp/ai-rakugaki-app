// frontend/src/app/draw/page.tsx
'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Pencil, Eraser, RotateCcw, Send, Play, XCircle } from 'lucide-react'
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

import { useRouter } from 'next/navigation'
import axios from 'axios'

export default function DrawingPage() {
  const [isDrawing, setIsDrawing] = useState(false)
  const [tool, setTool] = useState<'pencil' | 'eraser'>('pencil')
  const [timeLeft, setTimeLeft] = useState(30) // 30秒に設定
  const [isTimeUp, setIsTimeUp] = useState(false)
  const [isStarted, setIsStarted] = useState(false)
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const [currentTopic, setCurrentTopic] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const contextRef = useRef<CanvasRenderingContext2D | null>(null)
  const isSavedRef = useRef(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const router = useRouter()
  const [deviceId, setDeviceId] = useState<string>('')

  useEffect(() => {
    // ローカルストレージからデバイスIDとお題を取得
    const storedDeviceId = localStorage.getItem('device_id')
    const storedTopic = localStorage.getItem('current_topic')
    if (storedDeviceId && storedTopic) {
      setDeviceId(storedDeviceId)
      setCurrentTopic(storedTopic)
    } else {
      // デバイスIDが存在しない場合はランディングページにリダイレクト
      router.push('/')
    }
  }, [router])

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      const context = canvas.getContext('2d')
      if (context) {
        context.lineCap = 'round'
        context.strokeStyle = 'black'
        context.lineWidth = 4
        contextRef.current = context
        clearCanvas()
      }
    }
  }, [])

  useEffect(() => {
    if (isStarted && timeLeft > 0 && !isConfirmDialogOpen) {
      timerRef.current = setInterval(() => {
        setTimeLeft((prevTime) => {
          if (prevTime <= 1) {
            clearInterval(timerRef.current as NodeJS.Timeout)
            setIsTimeUp(true)
            setIsStarted(false)
            saveCanvasImage()
            return 0
          }
          return prevTime - 1
        })
      }, 1000) // 毎秒実行
    } else {
      clearInterval(timerRef.current as NodeJS.Timeout)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isStarted, isConfirmDialogOpen])

  const startDrawing = ({ nativeEvent }: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isStarted || isTimeUp) return
    const { offsetX, offsetY } = nativeEvent
    if (contextRef.current) {
      contextRef.current.beginPath()
      contextRef.current.moveTo(offsetX, offsetY)
      setIsDrawing(true)
    }
  }

  const finishDrawing = () => {
    if (!isStarted || isTimeUp) return
    if (contextRef.current) {
      contextRef.current.closePath()
      setIsDrawing(false)
    }
  }

  const draw = ({ nativeEvent }: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !isStarted || isTimeUp) return
    const { offsetX, offsetY } = nativeEvent
    if (contextRef.current) {
      if (tool === 'eraser') {
        contextRef.current.globalCompositeOperation = 'destination-out'
        contextRef.current.lineWidth = 10
      } else {
        contextRef.current.globalCompositeOperation = 'source-over'
        contextRef.current.lineWidth = 4
      }
      contextRef.current.lineTo(offsetX, offsetY)
      contextRef.current.stroke()
    }
  }

  const clearCanvas = () => {
    if (contextRef.current && canvasRef.current) {
      contextRef.current.fillStyle = 'white'
      contextRef.current.fillRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    }
  }

  const saveCanvasImage = async () => {
    if (canvasRef.current && deviceId && !isSavedRef.current) {
      isSavedRef.current = true // 二重保存を防ぐフラグ
      const image = canvasRef.current.toDataURL('image/png')
      try {
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
        const response = await axios.post(`${backendUrl}/save-canvas`, {
          device_id: deviceId,
          image_data: image,
        })
        if (response.data.success) {
          console.log('キャンバス画像が保存されました:', response.data.file_name)
          // 結果ページへ遷移し、キャンバス画像URLとデバイスIDをクエリパラメータとして渡す
          const canvasImageUrl = `${backendUrl}/saved-images/${response.data.file_name}`
          const destinationUrl = `/result?canvasImageUrl=${encodeURIComponent(canvasImageUrl)}&deviceId=${encodeURIComponent(deviceId)}&topic=${encodeURIComponent(currentTopic)}`
          router.push(destinationUrl)
        } else {
          console.error('キャンバス画像の保存に失敗しました')
          setError('キャンバス画像の保存に失敗しました')
        }
      } catch (error) {
        console.error('キャンバス画像の保存中にエラーが発生しました:', error)
        setError('キャンバス画像の保存中にエラーが発生しました')
      }
    }
  }

  const handleStart = () => {
    setIsStarted(true)
    setTimeLeft(30) // 30秒に設定
    setIsTimeUp(false)
    clearCanvas()
    isSavedRef.current = false
  }

  const handleStop = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    setIsTimeUp(true)
    setIsStarted(false)
    saveCanvasImage()
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 p-8">
      <Card className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-4 text-purple-600">AIお絵かきチャレンジ！</h1>
        <h2 className="text-xl font-semibold text-center mb-6 text-blue-500">お題：「{currentTopic}」</h2>

        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}

        <div className="relative mb-4">
          <canvas
            ref={canvasRef}
            onMouseDown={startDrawing}
            onMouseUp={finishDrawing}
            onMouseMove={draw}
            className="border-4 border-dashed border-purple-300 rounded-lg w-full h-[400px] cursor-crosshair"
          />
          {isTimeUp && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
              <p className="text-white text-3xl font-bold">時間終了！</p>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-2">
            <Button
              variant={tool === 'pencil' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTool('pencil')}
              disabled={!isStarted || isTimeUp}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant={tool === 'eraser' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTool('eraser')}
              disabled={!isStarted || isTimeUp}
            >
              <Eraser className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={clearCanvas} disabled={!isStarted || isTimeUp}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
          {!isStarted ? (
            <Button
              onClick={handleStart}
              className="bg-green-500 hover:bg-green-600 flex items-center"
              disabled={!currentTopic}
            >
              スタート
              <Play className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={() => setIsConfirmDialogOpen(true)}
              disabled={isTimeUp && isSavedRef.current}
              className="bg-orange-500 hover:bg-orange-600 flex items-center"
            >
              終了
              <Send className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <Progress value={(timeLeft / 30) * 100} className="flex-grow" /> {/* 30秒に合わせて調整 */}
          <span className="text-lg font-semibold text-blue-600">{timeLeft}秒</span>
        </div>
      </Card>

      {/* 確認ダイアログ */}
      <AlertDialog open={isConfirmDialogOpen} onOpenChange={setIsConfirmDialogOpen}>
        <AlertDialogContent className="bg-gradient-to-b from-blue-100 to-purple-100 rounded-xl p-6 shadow-lg">
          <AlertDialogHeader>
            <div className="flex items-center mb-4">
              <XCircle className="h-6 w-6 text-red-600 mr-2" />
              <AlertDialogTitle className="text-2xl text-gray-800">描画を終了しますか？</AlertDialogTitle>
            </div>
            <AlertDialogDescription className="text-gray-700">
              まだ時間が残っています。本当に描くのを終了してもいいですか？
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="flex justify-end space-x-4">
            <Button
              variant="outline"
              className="border-gray-300 text-gray-700 hover:bg-gray-100"
              onClick={() => setIsConfirmDialogOpen(false)}
            >
              まだ描く
            </Button>
            <Button
              className="bg-red-500 text-white hover:bg-red-600 flex items-center"
              onClick={() => {
                setIsConfirmDialogOpen(false)
                handleStop()
              }}
            >
              終わる
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
