import React from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <main className="max-w-6xl mx-auto p-6">
      <section className="text-center mt-12">
        <h1 className="text-4xl font-extrabold">WriteAiDaily Portal</h1>
        <p className="mt-4 text-gray-600">One place for all your AI agents. Login once, use many.</p>
        <div className="mt-8 flex justify-center gap-4">
          <Link to="/agent/writeaidaily" className="px-6 py-3 bg-green-600 text-white rounded-lg">Open WriteAiDaily</Link>
          <Link to="/agents" className="px-6 py-3 border rounded-lg">Explore Agents</Link>
        </div>
      </section>

      <section className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-white rounded-xl shadow">
          <h3 className="font-semibold">SEO Blogs</h3>
          <p className="mt-2 text-sm text-gray-600">Generate SEO-focused long-form content using LLMs.</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow">
          <h3 className="font-semibold">Social Posts</h3>
          <p className="mt-2 text-sm text-gray-600">Create catchy social posts in seconds.</p>
        </div>
        <div className="p-6 bg-white rounded-xl shadow">
          <h3 className="font-semibold">Ad Copy</h3>
          <p className="mt-2 text-sm text-gray-600">Ads, CTAs and A/B ready variants.</p>
        </div>
      </section>
    </main>
  )
}
