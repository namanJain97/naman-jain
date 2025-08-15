import React from "react";
import { Link } from "react-router-dom";

export default function Home() {
  return (
    <main className="max-w-6xl mx-auto p-6">
      {/* Hero Section */}
      <section className="text-center mt-12 bg-gradient-to-b from-gray-50 to-white rounded-2xl p-10 shadow-sm">
        <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
          Agent Central
        </h1>
        <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
          One place for all your AI agents — login once, access many powerful tools instantly.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link
            to="/agents"
            className="px-6 py-3 bg-blue-600 text-white rounded-md shadow-sm hover:bg-blue-700 transition"
          >
            Explore Agents
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          {
            title: "SEO Blogs",
            desc: "Generate SEO-focused long-form content using advanced LLMs.",
          },
          {
            title: "Social Posts",
            desc: "Create catchy, platform-optimized social media posts in seconds.",
          },
          {
            title: "Ad Copy",
            desc: "Write compelling ads, CTAs, and A/B test-ready variations.",
          },
        ].map((feature, idx) => (
          <div
            key={idx}
            className="p-6 bg-white rounded-xl shadow hover:shadow-md transition hover:translate-y-[-2px]"
          >
            <h3 className="font-semibold text-lg text-gray-900">{feature.title}</h3>
            <p className="mt-2 text-sm text-gray-600">{feature.desc}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
