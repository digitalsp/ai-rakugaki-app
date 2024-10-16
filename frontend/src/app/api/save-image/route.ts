import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

// ランダム文字列生成関数
function generateRandomString() {
  return crypto.randomBytes(3).toString('hex') // 6文字のランダム文字列
}

// 日時を `YYYY-MM-DD-HHMM-SS` 形式にフォーマットする関数
function formatDate(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0')

  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1) // 月は0ベース
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  const seconds = pad(date.getSeconds())

  return `${year}-${month}-${day}-${hours}${minutes}-${seconds}`
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
  
  // 現在の日時をフォーマット
  const now = new Date()
  const formattedDate = formatDate(now)
  
  // ランダム文字列生成
  const randomString = generateRandomString()
  
  // ファイル名生成
  const fileName = `${formattedDate}-${randomString}.png`
  const filePath = path.join(saveDir, fileName)
  
  // 画像を保存
  fs.writeFileSync(filePath, buffer)
  
  return NextResponse.json({ success: true, fileName })
}
