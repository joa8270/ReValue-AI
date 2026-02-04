"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronRight, Play, Apple as AppleIcon, Search, ShoppingBag } from 'lucide-react'

export default function Home() {
  const banners = [
    {
      title: "iPhone",
      subtitle: "新一代 iPhone，快來認識一下。",
      image: "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=1200&q=80",
      cta1: "進一步了解",
      cta2: "選購 iPhone",
      color: "white"
    },
    {
      title: "Apple Watch Series 11",
      subtitle: "絕技在手，全方位看顧你的健康。",
      image: "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=1200&q=80",
      cta1: "進一步了解",
      cta2: "購買",
      color: "white"
    },
    {
      title: "MacBook Air",
      subtitle: "全新天藍色，M4 效能沖天。",
      image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1200&q=80",
      cta1: "進一步了解",
      cta2: "購買",
      color: "white"
    },
    {
      title: "iPad Air",
      subtitle: "現在超強驅動來自 M3 晶片。",
      image: "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=1200&q=80",
      cta1: "進一步了解",
      cta2: "購買",
      color: "white"
    }
  ]

  const sections = [
    {
      title: "Apple Trade In 換購方案",
      subtitle: "以裝置換購，獲享折抵優惠。",
      description: "查看你裝置的估價",
      image: "https://images.unsplash.com/photo-1606216794074-735e91aa2c92?w=1200&q=80",
      bg: "black"
    },
    {
      title: "Apple TV+",
      subtitle: "原創內容，獨家呈獻。",
      description: "立即訂閱",
      image: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=1200&q=80",
      bg: "black"
    }
  ]

  return (
    <div className="min-h-screen bg-white text-black overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between h-12">
            <AppleIcon className="w-5 h-5 text-black" />
            <div className="hidden md:flex items-center gap-8 text-xs">
              <a href="#" className="hover:text-gray-600 transition-colors">商店</a>
              <a href="#" className="hover:text-gray-600 transition-colors">Mac</a>
              <a href="#" className="hover:text-gray-600 transition-colors">iPad</a>
              <a href="#" className="hover:text-gray-600 transition-colors">iPhone</a>
              <a href="#" className="hover:text-gray-600 transition-colors">Watch</a>
              <a href="#" className="hover:text-gray-600 transition-colors">AirPods</a>
              <a href="#" className="hover:text-gray-600 transition-colors">TV</a>
            </div>
            <div className="flex items-center gap-6">
              <Search className="w-4 h-4 cursor-pointer hover:text-gray-600 transition-colors" />
              <ShoppingBag className="w-4 h-4 cursor-pointer hover:text-gray-600 transition-colors" />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Banner - MIRRA */}
      <section className="relative h-[90vh] flex items-center justify-center overflow-hidden mt-12 bg-black">
        <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-6xl md:text-8xl font-semibold tracking-tight mb-4 text-white"
          >
            MIRRA
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-2xl md:text-3xl text-gray-300 font-light mb-12"
          >
            Market Intelligence & Reality Rendering Agent
          </motion.p>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="flex gap-6 justify-center"
          >
            <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg font-medium transition-all">
              進一步了解
            </button>
            <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg font-medium transition-all">
              購買
            </button>
          </motion.div>
        </div>
      </section>

      {/* Product Banners */}
      {banners.map((banner, index) => (
        <section
          key={index}
          className={`relative h-[85vh] flex items-center justify-center overflow-hidden ${
            index % 2 === 0 ? 'bg-white' : 'bg-black'
          }`}
        >
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${banner.image})` }}
          />
          <div
            className={`absolute inset-0 ${
              index % 2 === 0 ? 'bg-black/10' : 'bg-white/10'
            }`}
          />
          <div
            className={`relative z-10 text-center px-4 max-w-4xl mx-auto ${
              index % 2 === 0 ? 'text-black' : 'text-white'
            }`}
          >
            <motion.h2
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-semibold tracking-tight mb-4"
            >
              {banner.title}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl mb-10"
            >
              {banner.subtitle}
            </motion.p>
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex gap-6 justify-center"
            >
              <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg font-medium transition-all flex items-center gap-2">
                {banner.cta1}
                <ChevronRight className="w-4 h-4" />
              </button>
              <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg font-medium transition-all">
                {banner.cta2}
              </button>
            </motion.div>
          </div>
        </section>
      ))}

      {/* Smaller Sections */}
      {sections.map((section, index) => (
        <section
          key={index}
          className={`relative h-[60vh] flex items-center justify-center overflow-hidden ${
            index % 2 === 0 ? 'bg-white' : 'bg-black'
          }`}
        >
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${section.image})` }}
          />
          <div
            className={`absolute inset-0 ${
              index % 2 === 0 ? 'bg-black/30' : 'bg-white/30'
            }`}
          />
          <div
            className={`relative z-10 text-center px-4 max-w-3xl mx-auto ${
              index % 2 === 0 ? 'text-black' : 'text-white'
            }`}
          >
            <motion.h3
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-4xl md:text-5xl font-semibold tracking-tight mb-3"
            >
              {section.title}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl mb-8"
            >
              {section.subtitle}
            </motion.p>
            <motion.button
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white text-lg font-medium transition-all flex items-center gap-2"
            >
              {section.description}
              <ChevronRight className="w-4 h-4" />
            </motion.button>
          </div>
        </section>
      ))}

      {/* Footer */}
      <footer className="bg-[#f5f5f7] text-gray-800 py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-xs text-gray-600 mb-8 pb-8 border-b border-gray-300">
            <p className="mb-4">
              * 所列功能會隨情況而有所變動。部分功能、應用程式與服務可能未在所有地區提供。
            </p>
            <p>使用 Apple TV 須訂閱服務。</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <div>
              <h4 className="font-semibold text-xs mb-4">選購與了解產品</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">商店</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Mac</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">iPad</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">iPhone</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Watch</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Vision</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">AirPods</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">TV 和家庭</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-xs mb-4">服務</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple Music</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple TV+</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple Arcade</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">iCloud</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple Pay</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-xs mb-4">Apple Store</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">尋找直營店</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Genius Bar 天才吧</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Today at Apple</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple 夏令營</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple Store App</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-xs mb-4">商務應用</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple 與商務</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">商務選購</a></li>
              </ul>
              <h4 className="font-semibold text-xs mb-4 mt-6">教育應用</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">Apple 與教育</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">學生專屬優惠</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-xs mb-4">Apple 價值理念</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">輔助使用</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">環境</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">隱私權</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">供應鏈創新</a></li>
              </ul>
              <h4 className="font-semibold text-xs mb-4 mt-6">關於 Apple</h4>
              <ul className="space-y-2 text-xs text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition-colors">Newsroom</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">工作機會</a></li>
                <li><a href="#" className="hover:text-gray-900 transition-colors">聯絡 Apple</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-300 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-start gap-4">
              <p className="text-xs text-gray-600">
                更多選購方式：尋找當地的 Apple 直營店或其他零售商，或致電 0800-020-021。
              </p>
              <p className="text-xs text-gray-600">台灣</p>
            </div>
            <div className="flex flex-col md:flex-row justify-between items-start gap-4 mt-4 text-xs text-gray-600">
              <p>Copyright © 2026 MIRRA Inc. 保留一切權利。</p>
              <div className="flex gap-4">
                <a href="#" className="hover:text-gray-900 transition-colors">隱私權政策</a>
                <a href="#" className="hover:text-gray-900 transition-colors">使用條款</a>
                <a href="#" className="hover:text-gray-900 transition-colors">銷售及退款</a>
                <a href="#" className="hover:text-gray-900 transition-colors">法律聲明</a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
