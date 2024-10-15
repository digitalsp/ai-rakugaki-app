'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Pencil, Eraser, RotateCcw, Send } from 'lucide-react'

export default function DrawingPage() {
  const [isDrawing, setIsDrawing] = useState(false)
  const [tool, setTool] = useState<'pencil' | 'eraser'>('pencil')
  const [timeLeft, setTimeLeft] = useState(30)
  const [isTimeUp, setIsTimeUp] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const contextRef = useRef<CanvasRenderingContext2D | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
      const context = canvas.getContext('2d')
      if (context) {
        context.lineCap = 'round'
        context.strokeStyle = 'black'
        context.lineWidth = 5
        contextRef.current = context
      }
    }

    const timer = setInterval(() => {
      setTimeLeft((prevTime) => {
        if (prevTime <= 1) {
          clearInterval(timer)
          setIsTimeUp(true)
          return 0
        }
        return prevTime - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const startDrawing = ({ nativeEvent }: React.MouseEvent<HTMLCanvasElement>) => {
    const { offsetX, offsetY } = nativeEvent
    if (contextRef.current) {
      contextRef.current.beginPath()
      contextRef.current.moveTo(offsetX, offsetY)
      setIsDrawing(true)
    }
  }

  const finishDrawing = () => {
    if (contextRef.current) {
      contextRef.current.closePath()
      setIsDrawing(false)
    }
  }

  const draw = ({ nativeEvent }: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return
    const { offsetX, offsetY } = nativeEvent
    if (contextRef.current) {
      if (tool === 'eraser') {
        contextRef.current.globalCompositeOperation = 'destination-out'
      } else {
        contextRef.current.globalCompositeOperation = 'source-over'
      }
      contextRef.current.lineTo(offsetX, offsetY)
      contextRef.current.stroke()
    }
  }

  const clearCanvas = () => {
    if (contextRef.current && canvasRef.current) {
      contextRef.current.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    }
  }

  const handleSubmit = () => {
    // ここに描画した画像を送信する処理を実装
    console.log('画像を送信しました')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 p-8">
      <Card className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-4 text-purple-600">お絵かきチャレンジ！</h1>
        <h2 className="text-xl font-semibold text-center mb-6 text-blue-500">お題：「うちゅうせん」</h2>
        
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
              <p className="text-white text-3xl font-bold">時間切れ！</p>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center mb-4">
          <div className="flex space-x-2">
            <Button
              variant={tool === 'pencil' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTool('pencil')}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant={tool === 'eraser' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setTool('eraser')}
            >
              <Eraser className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={clearCanvas}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
          <Button onClick={handleSubmit} disabled={isTimeUp} className="bg-green-500 hover:bg-green-600">
            <Send className="h-4 w-4 mr-2" />
            送信
          </Button>
        </div>

        <div className="flex items-center space-x-4">
          <Progress value={(timeLeft / 30) * 100} className="flex-grow" />
          <span className="text-lg font-semibold text-blue-600">{timeLeft}秒</span>
        </div>
      </Card>
    </div>
  )
}
