import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import crypto from 'crypto'

function generateRandomString() {
  return crypto.randomBytes(3).toString('hex')
}

function formatDate(date: Date): string {
  const pad = (n: number) => n.toString().padStart(2, '0')
  const year = date.getFullYear()
  const month = pad(date.getMonth() + 1)
  const day = pad(date.getDate())
  const hours = pad(date.getHours())
  const minutes = pad(date.getMinutes())
  const seconds = pad(date.getSeconds())
  return `${year}-${month}-${day}-${hours}${minutes}-${seconds}`
}

export async function POST(request: Request) {
  const { image } = await request.json()
  
  const base64Data = image.replace(/^data:image\/png;base64,/, "")
  const buffer = Buffer.from(base64Data, 'base64')
  
  const saveDir = path.join(process.cwd(), 'public', 'saved-images')
  if (!fs.existsSync(saveDir)){
    fs.mkdirSync(saveDir, { recursive: true })
  }
  
  const now = new Date()
  const formattedDate = formatDate(now)
  const randomString = generateRandomString()
  
  const fileName = `${formattedDate}-${randomString}.png`
  const filePath = path.join(saveDir, fileName)
  
  fs.writeFileSync(filePath, buffer)
  
  return NextResponse.json({ success: true, fileName })
}
