// frontend/src/app/page.tsx
// 'use client'

// import { useEffect, useState } from 'react'
// import { Button } from "@/components/ui/button"
// import { Card } from "@/components/ui/card"
// import { Shuffle } from 'lucide-react'
// import { useRouter } from 'next/navigation'
// import axios from 'axios'

// export default function LandingPage() {
//   const [currentTopic, setCurrentTopic] = useState<string>('')
//   const [deviceId, setDeviceId] = useState<string>('')
//   const [loading, setLoading] = useState<boolean>(false)
//   const [error, setError] = useState<string | null>(null)
//   const [autoRegisterFailed, setAutoRegisterFailed] = useState<boolean>(false)
//   const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null)
//   const router = useRouter()

//   useEffect(() => {
//     const init = async () => {
//       const storedDeviceId = localStorage.getItem('device_id')
//       const storedTopic = localStorage.getItem('current_topic')

//       if (storedDeviceId && storedTopic) {
//         setDeviceId(storedDeviceId)
//         setCurrentTopic(storedTopic)

//         // バックエンドでデバイスを検証
//         try {
//           const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
//           const response = await axios.post(`${backendUrl}/verify-device`, { device_id: storedDeviceId })
//           console.log('Response from /verify-device:', response.data)

//           if (response.data.success) {
//             // デバイスが有効
//             setCurrentTopic(response.data.topic || '')
//             console.log(`Device verified successfully: ${storedDeviceId}, Topic: ${response.data.topic}`)

//             // WebSocket接続の確立
//             await establishWebSocketConnection(storedDeviceId)
//           } else {
//             // デバイスが無効、localStorageをクリアして自動登録を試みる
//             console.error('Stored device_id is invalid:', response.data.detail)
//             localStorage.removeItem('device_id')
//             localStorage.removeItem('current_topic')
//             setDeviceId('')
//             setCurrentTopic('')
//             // 自動登録を試みる
//             await registerDevice(true)
//           }
//         } catch (error: any) {
//           console.error('Error verifying device_id:', error)
//           setError('デバイスの検証中にエラーが発生しました')
//           // 自動登録を試みる
//           await registerDevice(true)
//         }
//       } else {
//         // 保存されたdevice_idがない場合、自動登録を試みる
//         await registerDevice(true)
//       }
//     }

//     init()
//   }, [])

//   const registerDevice = async (isAuto: boolean = false) => {
//     setLoading(true)
//     setError(null)
//     try {
//       const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
//       console.log(`Sending POST request to ${backendUrl}/register-device`)
//       const response = await axios.post(`${backendUrl}/register-device`, {})
//       console.log('Response from /register-device:', response.data)

//       if (response.data.success) {
//         const { device_id, topic } = response.data
//         if (!device_id) {
//           throw new Error('device_id がレスポンスに含まれていません')
//         }
//         // デバイスIDとお題をlocalStorageに保存
//         localStorage.setItem('device_id', device_id)
//         localStorage.setItem('current_topic', topic || '')
//         setDeviceId(device_id)
//         setCurrentTopic(topic || '')
//         console.log(`Device registered successfully: ${device_id}, Topic: ${topic}`)

//         // WebSocket接続の確立
//         await establishWebSocketConnection(device_id)
//       } else {
//         setError('デバイスの登録に失敗しました')
//         console.error('デバイスの登録に失敗しました', response.data)
//         if (isAuto) {
//           setAutoRegisterFailed(true)
//         }
//       }
//     } catch (error: any) {
//       setError('デバイスの登録中にエラーが発生しました')
//       console.error('デバイスの登録中にエラーが発生しました:', error)
//       if (isAuto) {
//         setAutoRegisterFailed(true)
//       }
//     } finally {
//       setLoading(false)
//     }
//   }

//   const establishWebSocketConnection = async (device_id: string) => {
//     try {
//       const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
//       const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws'
//       const wsHost = backendUrl.replace(/^https?:\/\//, '')
//       const wsUrl = `${wsProtocol}://${wsHost}/ws/${device_id}`

//       const socket = new WebSocket(wsUrl)

//       socket.onopen = () => {
//         console.log('WebSocket connection established')
//       }

//       socket.onmessage = (event) => {
//         console.log('WebSocket message received:', event.data)
//         try {
//           const data = JSON.parse(event.data)
//           if (data.generatedImageUrl) {
//             setGeneratedImageUrl(data.generatedImageUrl)
//           }
//           if (data.topic && data.topic !== currentTopic) {
//             setCurrentTopic(data.topic)
//             localStorage.setItem('current_topic', data.topic)
//             console.log(`Topic updated via WebSocket: ${data.topic}`)
//           }
//         } catch (error) {
//           console.error('Failed to parse WebSocket message:', error)
//         }
//       }

//       socket.onclose = () => {
//         console.log('WebSocket connection closed')
//       }

//       socket.onerror = (error) => {
//         console.error('WebSocket error:', error)
//       }

//     } catch (error) {
//       console.error('Failed to establish WebSocket connection:', error)
//     }
//   }

//   const selectRandomTopic = async () => {
//     if (!deviceId) {
//       setError('デバイスIDが存在しません。しばらく待ってから再試行してください。')
//       return
//     }

//     setLoading(true)
//     setError(null)
//     try {
//       const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
//       console.log(`Sending POST request to ${backendUrl}/get-new-topic with device_id=${deviceId}`)
//       const response = await axios.post(`${backendUrl}/get-new-topic`, {
//         device_id: deviceId,
//       })
//       console.log('Response from /get-new-topic:', response.data)

//       if (response.data.success && response.data.topic) {
//         const newTopic = response.data.topic
//         localStorage.setItem('current_topic', newTopic)
//         setCurrentTopic(newTopic)
//         console.log(`New topic selected: ${newTopic}`)
//       } else {
//         setError('新しいお題の取得に失敗しました')
//         console.error('新しいお題の取得に失敗しました', response.data)
//       }
//     } catch (error) {
//       setError('新しいお題の取得中にエラーが発生しました')
//       console.error('新しいお題の取得中にエラーが発生しました:', error)
//     } finally {
//       setLoading(false)
//     }
//   }

//   const handleStartDrawing = () => {
//     if (currentTopic) {
//       router.push('/draw')
//     }
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-b from-blue-100 to-purple-100 flex items-center justify-center p-4">
//       <Card className="max-w-2xl w-full mx-auto p-8 bg-white rounded-xl shadow-lg text-center">
//         <h1 className="text-4xl sm:text-5xl font-bold mb-6 text-purple-600">
//           <span className="inline-block">Quick Diffusion</span>
//         </h1>

//         <h2 className="text-2xl sm:text-3xl font-semibold mb-8 text-blue-500">
//           お題：「{currentTopic || '...'}」
//         </h2>

//         {error && <p className="text-red-500 mb-4">{error}</p>}

//         {generatedImageUrl && (
//           <div className="mb-4">
//             <img src={generatedImageUrl} alt="Generated" className="w-64 h-auto rounded-lg shadow-md" />
//             <p className="mt-2 text-sm text-gray-600">生成された画像が届きました！</p>
//           </div>
//         )}

//         <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
//           <Button
//             onClick={selectRandomTopic}
//             className="bg-purple-500 hover:bg-purple-600 text-white flex items-center px-6 py-3"
//             disabled={loading || !deviceId}
//           >
//             <Shuffle className="mr-2 h-5 w-5" />
//             お題を選び直す
//           </Button>

//           <Button
//             onClick={handleStartDrawing}
//             className="bg-green-500 hover:bg-green-600 text-white px-6 py-3"
//             disabled={!currentTopic || loading}
//           >
//             描き始める
//           </Button>

//           {/* 手動登録ボタンの追加 */}
//           {autoRegisterFailed && (
//             <Button
//               onClick={() => registerDevice(false)}
//               className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3"
//               disabled={loading}
//             >
//               デバイスを登録する
//             </Button>
//           )}
//         </div>
//       </Card>
//     </div>
//   )
// }

// frontend/src/app/page.tsx

'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import axios from 'axios'

export default function LandingPage() {
  const router = useRouter()
  const [deviceId, setDeviceId] = useState<string>('')
  const [topic, setTopic] = useState<string>('')
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
