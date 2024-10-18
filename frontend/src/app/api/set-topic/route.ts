import { NextResponse } from 'next/server'

let currentTopic = ''

export async function POST(request: Request) {
  const { topic } = await request.json()
  currentTopic = topic
  return NextResponse.json({ success: true })
}

export async function GET() {
  return NextResponse.json({ topic: currentTopic })
}
