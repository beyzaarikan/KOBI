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
import { Mail, AlertCircle, TrendingUp } from "lucide-react";

interface DashboardMetrics {
  total_orders_today: number;
  low_stock_alerts: number;
  delayed_shipments: number;
  revenue_today: number;
}

interface InventoryInsight {
  product_name: string;
  status: string;
  critical_explanation: string;
  order_recommendation: string;
  supplier_email_draft: string;
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [insights, setInsights] = useState<InventoryInsight[]>([]);
  const [isLoadingInsights, setIsLoadingInsights] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [chatLog, setChatLog] = useState<{ role: string; content: string }[]>([]);
  const [openEmailDraft, setOpenEmailDraft] = useState<number | null>(null);

  useEffect(() => {
    // Fetch metrics
    fetch("http://localhost:8000/api/v1/inventory/dashboard/metrics")
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch((err) => console.error(err));

    // Fetch AI insights
    fetch("http://localhost:8000/api/v1/inventory/ai/inventory-insights")
      .then((res) => res.json())
      .then((data) => {
        setInsights(data.insights || []);
        setIsLoadingInsights(false);
      })
      .catch((err) => {
        console.error(err);
        setIsLoadingInsights(false);
      });
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
            <p className="text-neutral-400 mt-1">Yapay Zeka Destekli Envanter ve Sipariş Yönetimi</p>
          </div>
          <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
            Sistem Sağlıklı
          </Badge>
        </header>

        {/* METRICS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Toplam Sipariş (Bugün)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{metrics?.total_orders_today || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Düşük Stok Uyarıları</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-rose-500">{metrics?.low_stock_alerts || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Geciken Teslimatlar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-500">{metrics?.delayed_shipments || 0}</div>
            </CardContent>
          </Card>
          <Card className="bg-neutral-900 border-neutral-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-neutral-400">Gelir (Bugün)</CardTitle>
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
                Envanter Zeka Motoru
              </CardTitle>
              <CardDescription className="text-neutral-400">
                Son satış hızına dayalı yapay zeka destekli tahminler.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1">
              <ScrollArea className="h-[400px] pr-4">
                <div className="space-y-4">
                  {isLoadingInsights ? (
                    <div className="text-neutral-500 text-sm">Envanter analiz ediliyor...</div>
                  ) : insights.length === 0 ? (
                    <div className="text-neutral-500 text-sm">Tüm envanter sağlıklı durumda. Kritik uyarı bulunmuyor.</div>
                  ) : (
                    insights.map((item, idx) => (
                      <div key={idx} className="p-4 rounded-lg bg-neutral-950 border border-neutral-800">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-white">{item.product_name}</h4>
                          <Badge variant={item.status === 'Critical' ? 'destructive' : 'default'} className={item.status === 'Critical' ? 'bg-rose-500/10 text-rose-500 border-none' : ''}>
                            {item.status}
                          </Badge>
                        </div>
                        <div className="space-y-3 mb-3">
                          <div className="flex gap-2 text-sm text-neutral-300">
                            <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                            <p>{item.critical_explanation}</p>
                          </div>
                          <div className="flex gap-2 text-sm text-neutral-300">
                            <TrendingUp className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                            <p>{item.order_recommendation}</p>
                          </div>
                        </div>
                        
                        <div className="mt-4 border-t border-neutral-800 pt-3">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="text-indigo-400 hover:text-indigo-300 hover:bg-indigo-500/10 h-8 px-2"
                            onClick={() => setOpenEmailDraft(openEmailDraft === idx ? null : idx)}
                          >
                            <Mail className="w-4 h-4 mr-2" />
                            Tedarikçi Mail Taslağı
                          </Button>
                          
                          {openEmailDraft === idx && (
                            <div className="mt-2 p-3 bg-neutral-900 rounded border border-neutral-800 text-sm text-neutral-300 whitespace-pre-wrap font-mono relative">
                              {item.supplier_email_draft}
                              <Button 
                                size="sm" 
                                variant="secondary" 
                                className="absolute top-2 right-2 h-6 text-xs bg-neutral-800 hover:bg-neutral-700"
                                onClick={() => navigator.clipboard.writeText(item.supplier_email_draft)}
                              >
                                Kopyala
                              </Button>
                            </div>
                          )}
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
              <CardTitle className="text-lg">Yapay Zeka Destek Asistanı</CardTitle>
              <CardDescription className="text-neutral-400">Doğal dil ile sipariş takibi</CardDescription>
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
                      Bir sipariş hakkında soru sorun (örn. &quot;Siparişim nerede?&quot;)
                    </p>
                  )}
                </div>
              </ScrollArea>
              <div className="flex gap-2 mt-auto pt-2">
                <Input 
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Bir mesaj yazın..." 
                  className="bg-neutral-950 border-neutral-800"
                />
                <Button onClick={handleChat} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                  Gönder
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
