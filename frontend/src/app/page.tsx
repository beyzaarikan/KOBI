"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface DashboardMetrics {
  total_orders_today: number;
  low_stock_alerts: number;
  delayed_shipments: number;
  revenue_today: number;
}

interface InventoryInsight {
  product_name: string;
  status: string;
  reason: string;
  predicted_depletion_days: number;
  restock_recommendation: number;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [insights, setInsights] = useState<InventoryInsight[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLog, setChatLog] = useState<{ role: string; content: string }[]>([]);

  useEffect(() => {
    // Fetch metrics
    fetch("http://localhost:8000/api/v1/inventory/dashboard/metrics")
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch((err) => console.error(err));

    // Fetch AI insights
    fetch("http://localhost:8000/api/v1/inventory/ai/inventory-insights")
      .then((res) => res.json())
      .then((data) => setInsights(data.insights))
      .catch((err) => console.error(err));
  }, []);

  const handleChat = async () => {
    if (!chatInput.trim()) return;
    
    const userMsg = { role: "user", content: chatInput };
    setChatLog((prev) => [...prev, userMsg]);
    setChatInput("");

    try {
      const res = await fetch("http://localhost:8000/api/v1/orders/support-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMsg.content }),
      });
      const data = await res.json();
      setChatLog((prev) => [...prev, { role: "ai", content: data.response }]);
    } catch {
      setChatLog((prev) => [...prev, { role: "ai", content: "Bağlantı hatası." }]);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        <header className="flex justify-between items-center pb-6 border-b border-neutral-800">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Kobi.app</h1>
            <p className="text-neutral-400 mt-1">AI-Powered Inventory & Order Management</p>
          </div>
          <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
            System Healthy
          </Badge>
        </header>

        {/* METRICS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Total Orders (Today)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{metrics?.total_orders_today || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Low Stock Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-rose-500">{metrics?.low_stock_alerts || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Delayed Shipments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-500">{metrics?.delayed_shipments || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Revenue (Today)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">₺{metrics?.revenue_today || "0.00"}</div>
            </CardContent>
          </Card>
        </div>

        {/* MAIN CONTENT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* AI INVENTORY INSIGHTS */}
          <Card className="col-span-2 bg-neutral-900 border-neutral-800 flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse"></span>
                Inventory Intelligence Engine
              </CardTitle>
              <CardDescription className="text-neutral-400">
                AI-driven predictions based on recent sales velocity.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-4">
                  {insights.length === 0 ? (
                    <div className="text-neutral-500 text-sm">Analyzing inventory...</div>
                  ) : (
                    insights.map((item, idx) => (
                      <div key={idx} className="p-4 rounded-lg bg-neutral-950 border border-neutral-800">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-white">{item.product_name}</h4>
                          <Badge variant={item.status === 'Critical' ? 'destructive' : 'default'} className={item.status === 'Critical' ? 'bg-rose-500/10 text-rose-500 border-none' : ''}>
                            {item.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-neutral-400 mb-3">{item.reason}</p>
                        <div className="flex gap-4 text-xs font-medium">
                          <div className="bg-neutral-800/50 px-2 py-1 rounded">
                            <span className="text-neutral-500">Depletes in:</span> <span className="text-white">{item.predicted_depletion_days} days</span>
                          </div>
                          <div className="bg-indigo-500/10 px-2 py-1 rounded text-indigo-400">
                            Restock: {item.restock_recommendation} units
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* AI CUSTOMER SUPPORT CHAT */}
          <Card className="bg-neutral-900 border-neutral-800 flex flex-col h-[520px]">
            <CardHeader className="pb-3 border-b border-neutral-800">
              <CardTitle className="text-lg">AI Support Agent</CardTitle>
              <CardDescription className="text-neutral-400">Natural language order tracking</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col pt-4 overflow-hidden">
              <ScrollArea className="flex-1 pr-4 mb-4">
                <div className="space-y-4">
                  {chatLog.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-neutral-800 text-neutral-200'}`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {chatLog.length === 0 && (
                    <p className="text-neutral-500 text-sm text-center mt-10">
                      Ask about an order (e.g., &quot;Siparişim nerede?&quot;)
                    </p>
                  )}
                </div>
              </ScrollArea>
              <div className="flex gap-2 mt-auto pt-2">
                <Input 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Type a message..." 
                  className="bg-neutral-950 border-neutral-800"
                />
                <Button onClick={handleChat} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  Send
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
