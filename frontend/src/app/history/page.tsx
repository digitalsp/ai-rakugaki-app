// frontend/src/app/history/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { Card } from "@/components/ui/card"

interface ImageEntry {
    id: number
    topic: string
    request_time: string
    canvas_image_filename: string
    controlnet_image_filename?: string
    generated_image_filename?: string
}

export default function HistoryPage() {
    const [images, setImages] = useState<ImageEntry[]>([])
    const [loading, setLoading] = useState<boolean>(false)
    const [error, setError] = useState<string | null>(null)
    const [selectedImage, setSelectedImage] = useState<string | null>(null)
    const router = useRouter()

    useEffect(() => {
        const fetchImages = async () => {
            const deviceId = localStorage.getItem('device_id')
            if (!deviceId) {
                setError('デバイスIDが存在しません。トップページからデバイスを登録してください。')
                return
            }

            setLoading(true)
            setError(null)
            try {
                const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
                const response = await axios.get(`${backendUrl}/images/${deviceId}`)
                console.log('Response from /images:', response.data)

                if (response.data.success && response.data.images) {
                    setImages(response.data.images)
                } else {
                    setError(response.data.detail || '画像の取得に失敗しました。')
                }
            } catch (error: any) {
                setError('画像の取得中にエラーが発生しました。')
                console.error('Error fetching images:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchImages()
    }, [])

    const handleImageClick = (imageUrl: string) => {
        setSelectedImage(imageUrl)
    }

    const closeModal = () => {
        setSelectedImage(null)
    }

    return (
        <div className="min-h-screen bg-gray-100 p-4">
            <div className="max-w-4xl mx-auto">
                <h1 className="text-3xl font-bold mb-6 text-center">画像履歴</h1>

                {loading && <p className="text-center">読み込み中...</p>}
                {error && <p className="text-red-500 text-center mb-4">{error}</p>}

                {!loading && !error && images.length === 0 && (
                    <p className="text-center">まだ画像が生成されていません。</p>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {images.map(image => (
                        <Card key={image.id} className="cursor-pointer" onClick={() => {
                            if (image.generated_image_filename) {
                                handleImageClick(`http://localhost:8000/generated-images/${image.generated_image_filename}`)
                            }
                        }}>
                            <img
                                src={image.generated_image_filename ? `http://localhost:8000/generated-images/${image.generated_image_filename}` : `http://localhost:8000/saved-images/${image.canvas_image_filename}`}
                                alt={`Image ${image.id}`}
                                className="w-full h-40 object-cover rounded-lg"
                            />
                            <div className="mt-2">
                                <p className="text-sm text-gray-700">お題: {image.topic}</p>
                                <p className="text-xs text-gray-500">生成日時: {new Date(image.request_time).toLocaleString()}</p>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Modal for displaying selected image */}
            {selectedImage && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-4 rounded-lg relative">
                        <button
                            onClick={closeModal}
                            className="absolute top-2 right-2 text-gray-700"
                        >
                            ✖️
                        </button>
                        <img src={selectedImage} alt="Selected" className="max-w-full max-h-screen" />
                    </div>
                </div>
            )}
        </div>
    )
}
