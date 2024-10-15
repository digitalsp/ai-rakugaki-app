'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Pencil, Eraser, RotateCcw, Send, Play, XCircle, CheckCircle } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export default function DrawingPage() {
  const [isDrawing, setIsDrawing] = useState(false)
  const [tool, setTool] = useState<'pencil' | 'eraser'>('pencil')
  const [timeLeft, setTimeLeft] = useState(30)
  const [isTimeUp, setIsTimeUp] = useState(false)
  const [isStarted, setIsStarted] = useState(false)
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const contextRef = useRef<CanvasRenderingContext2D | null>(null)
  const isSavedRef = useRef(false)
  const timerRef = useRef<NodeJS.Timeout | null>(null)

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
            saveImage()
            return 0
          }
          return prevTime - 1
        })
      }, 1000)
    } else if (!isStarted || isTimeUp || isConfirmDialogOpen) {
      clearInterval(timerRef.current as NodeJS.Timeout)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isStarted, timeLeft, isConfirmDialogOpen, isTimeUp])

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
      } else {
        contextRef.current.globalCompositeOperation = 'source-over'
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

  const saveImage = async () => {
    if (canvasRef.current && !isSavedRef.current) {
      const image = canvasRef.current.toDataURL('image/png')
      try {
        const response = await fetch('/api/save-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image }),
        })
        const data = await response.json()
        if (data.success) {
          console.log('画像が保存されました:', data.fileName)
          isSavedRef.current = true
        }
      } catch (error) {
        console.error('画像の保存に失敗しました:', error)
      }
    }
  }

  const handleStart = () => {
    setIsStarted(true)
    setTimeLeft(30)
    setIsTimeUp(false)
    clearCanvas()
    isSavedRef.current = false
  }

  const handleFinish = () => {
    if (!isTimeUp) {
      setIsConfirmDialogOpen(true)
    } else {
      saveImage()
    }
  }

  const confirmFinish = () => {
    setIsConfirmDialogOpen(false)
    setIsTimeUp(true)
    saveImage()
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
              <p className="text-white text-3xl font-bold">終了！</p>
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
            <Button onClick={handleStart} className="bg-green-500 hover:bg-green-600">
              <Play className="h-4 w-4 mr-2" />
              スタート
            </Button>
          ) : (
            <Button onClick={handleFinish} disabled={isTimeUp && isSavedRef.current} className="bg-green-500 hover:bg-green-600">
              <Send className="h-4 w-4 mr-2" />
              {isTimeUp ? '保存' : '終了'}
            </Button>
          )}
        </div>

        <div className="flex items-center space-x-4">
          <Progress value={(timeLeft / 30) * 100} className="flex-grow" />
          <span className="text-lg font-semibold text-blue-600">{timeLeft}秒</span>
        </div>
      </Card>

      {/* 改良された確認ダイアログ */}
      <Dialog open={isConfirmDialogOpen} onOpenChange={setIsConfirmDialogOpen}>
        <DialogContent className="bg-gradient-to-b from-blue-100 to-purple-100 p-6 rounded-xl shadow-lg">
          <DialogHeader>
            <div className="flex items-center mb-4">
              <XCircle className="h-6 w-6 text-red-600 mr-2" />
              <DialogTitle className="text-2xl text-gray-800">描画を終了しますか？</DialogTitle>
            </div>
            <DialogDescription className="text-gray-700">
              まだ時間が残っていますが、本当に描くのを終了してもいいですか？
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex justify-end space-x-4">
            <Button
              variant="outline"
              className="border-gray-300 text-gray-700 hover:bg-gray-100"
              onClick={() => setIsConfirmDialogOpen(false)}
            >
              キャンセル
            </Button>
            <Button
              className="bg-red-500 text-white hover:bg-red-600 flex items-center"
              onClick={confirmFinish}
            >
              <CheckCircle className="h-5 w-5 mr-2" />
              終了する
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
