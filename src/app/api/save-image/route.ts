import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

function generateRandomString() {
  return crypto.randomBytes(3).toString('hex')
}

export async function POST(request: Request) {
  const { image } = await request.json()
  
  // Base64エンコードされた画像データをデコード
  const base64Data = image.replace(/^data:image\/png;base64,/, "")
  const buffer = Buffer.from(base64Data, 'base64')
  
  // 保存先のディレクトリを作成（存在しない場合）
  const saveDir = path.join(process.cwd(), 'public', 'saved-images')
  if (!fs.existsSync(saveDir)){
    fs.mkdirSync(saveDir, { recursive: true })
  }
  
  // 現在の日時とランダムな文字列を使用してファイル名を生成
  const now = new Date()
  const dateString = now.toISOString().replace(/[-:]/g, '').slice(0, 15)
  const randomString = generateRandomString()
  const fileName = `${dateString}-${randomString}.png`
  const filePath = path.join(saveDir, fileName)
  
  // 画像を保存
  fs.writeFileSync(filePath, buffer)
  
  return NextResponse.json({ success: true, fileName })
}
