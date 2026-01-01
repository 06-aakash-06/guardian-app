"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Shield, AlertTriangle, Check, ScanFace, FileText, Download, Zap } from "lucide-react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [protectedImageUrl, setProtectedImageUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
      setReport(null);
      setProtectedImageUrl(null);
      setSelectedIndices(new Set());
    }
  };

  const runScan = async () => {
    if (!file) return;
    setIsScanning(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // Connect to Python Backend running on port 8000
      const res = await fetch("http://127.0.0.1:8000/api/scan", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setReport(data);
    } catch (error) {
      alert("Backend Error: Ensure server.py is running!");
    } finally {
      setIsScanning(false);
    }
  };

  const applyProtection = async (actionType: "blur_selected" | "cloak") => {
    if (!file) return;
    const formData = new FormData();
    formData.append("action", actionType);
    formData.append("indices", Array.from(selectedIndices).join(","));

    try {
      const res = await fetch("http://127.0.0.1:8000/api/protect", {
        method: "POST",
        body: formData,
      });
      const imageBlob = await res.blob();
      setProtectedImageUrl(URL.createObjectURL(imageBlob));
    } catch (error) {
      console.error(error);
    }
  };

  const toggleSelection = (index: number) => {
    const next = new Set(selectedIndices);
    if (next.has(index)) next.delete(index);
    else next.add(index);
    setSelectedIndices(next);
  };

  return (
    <main className="min-h-screen p-8 font-sans flex flex-col gap-6 max-w-6xl mx-auto">
      <header className="flex items-center gap-3 mb-4">
        <div className="p-3 bg-white/40 rounded-2xl glass shadow-lg">
          <Shield className="w-8 h-8 text-indigo-700" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Guardian AI</h1>
          <p className="text-xs font-bold text-indigo-600 uppercase tracking-widest">Universal Safety Suite</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* LEFT PANEL: VISUALIZER */}
        <section className="lg:col-span-7 flex flex-col gap-6">
          <div className="glass rounded-3xl p-4 relative min-h-[500px] flex items-center justify-center overflow-hidden bg-white/20 shadow-xl">
            {!previewUrl && (
              <label className="cursor-pointer flex flex-col items-center gap-4 p-12 hover:scale-105 transition-transform text-gray-600">
                <div className="w-20 h-20 rounded-full bg-white/40 flex items-center justify-center shadow-inner">
                   <Upload className="w-8 h-8 text-indigo-600" />
                </div>
                <span className="text-xl font-bold">Drop Image to Analyze</span>
                <input type="file" onChange={handleFileChange} className="hidden" />
              </label>
            )}

            {isScanning && (
              <div className="absolute inset-0 z-50 bg-white/60 backdrop-blur-md flex flex-col items-center justify-center">
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}>
                  <Zap className="w-16 h-16 text-indigo-600" />
                </motion.div>
                <p className="mt-4 font-bold text-indigo-800 animate-pulse">Running Forensics...</p>
              </div>
            )}

            {(previewUrl || protectedImageUrl) && (
              <motion.img 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                src={protectedImageUrl || previewUrl || ""} 
                className="max-h-[600px] w-auto rounded-xl shadow-2xl" 
              />
            )}
          </div>

          {report && !protectedImageUrl && (
            <div className="glass p-6 rounded-3xl flex flex-col gap-4 shadow-lg">
               <h3 className="font-bold text-gray-700 uppercase text-sm">Select Items to Redact</h3>
               <div className="flex gap-3 overflow-x-auto pb-2">
                 {report.detections.length === 0 && <p className="text-sm text-gray-500 italic">No items found.</p>}
                 {report.detections.map((det: any, i: number) => (
                    <button key={i} onClick={() => toggleSelection(i)}
                      className={`flex-shrink-0 px-4 py-3 rounded-xl border transition-all flex flex-col items-center min-w-[80px]
                        ${selectedIndices.has(i) ? "bg-indigo-600 text-white shadow-lg scale-105" : "bg-white/40 hover:bg-white/60 text-gray-700"}
                      `}>
                      {det.type === "FACE" ? <ScanFace className="mb-2"/> : <FileText className="mb-2"/>}
                      <span className="text-xs font-bold">#{i}</span>
                    </button>
                 ))}
               </div>
               <div className="flex gap-4 mt-2">
                 <button onClick={() => applyProtection("blur_selected")} disabled={selectedIndices.size === 0}
                    className="flex-1 py-4 bg-gray-900 text-white rounded-xl font-bold hover:bg-gray-800 disabled:opacity-50 transition-all shadow-lg">
                    Blur Selected
                 </button>
                 <button onClick={() => applyProtection("cloak")}
                    className="flex-1 py-4 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-500 transition-all shadow-lg">
                    AI Cloaking
                 </button>
               </div>
            </div>
          )}
          
          {protectedImageUrl && (
             <div className="glass p-6 rounded-3xl flex justify-between items-center bg-green-50/50 border-green-200 shadow-lg">
                <div className="flex items-center gap-3">
                   <div className="p-2 bg-green-200 rounded-full text-green-800"><Check /></div>
                   <div className="text-green-900 font-bold">Image Secured Successfully</div>
                </div>
                <a href={protectedImageUrl} download="guardian_safe.jpg" className="px-6 py-3 bg-green-600 text-white rounded-xl font-bold hover:bg-green-500 flex gap-2 shadow-md">
                   <Download className="w-5 h-5"/> Download
                </a>
             </div>
          )}
        </section>

        {/* RIGHT PANEL: INTELLIGENCE REPORT */}
        <section className="lg:col-span-5 flex flex-col gap-6">
          {!report ? (
             <div className="h-full glass rounded-3xl p-10 flex flex-col items-center justify-center text-center text-gray-500 border-2 border-dashed border-white/30 shadow-sm">
                <Shield className="w-20 h-20 mb-4 opacity-30" />
                <p className="font-medium">Upload an image to unlock<br/>forensic intelligence.</p>
                {previewUrl && !isScanning && (
                   <button onClick={runScan} className="mt-8 px-8 py-3 bg-indigo-600 text-white rounded-full font-bold hover:scale-105 transition-transform shadow-xl">
                      Run Analysis
                   </button>
                )}
             </div>
          ) : (
             <AnimatePresence>
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
                   <div className="glass rounded-3xl p-8 relative overflow-hidden bg-white/40 shadow-xl">
                      <h2 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Trust Score</h2>
                      <div className="flex items-baseline gap-2">
                         <span className={`text-7xl font-black ${report.score < 50 ? 'text-red-600' : 'text-green-600'}`}>{report.score}</span>
                         <span className="text-gray-400 font-bold text-xl">/ 100</span>
                      </div>
                      <div className="mt-4">
                         {report.score < 50 
                             ? <span className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-bold flex w-fit items-center gap-2"><AlertTriangle className="w-4 h-4"/> High Risk</span>
                             : <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-bold flex w-fit items-center gap-2"><Check className="w-4 h-4"/> Verified Safe</span>
                         }
                      </div>
                   </div>

                   <div className="glass rounded-3xl p-6 bg-white/30 shadow-lg">
                      <h3 className="font-bold text-gray-800 mb-4 uppercase text-xs tracking-wider">Detected Threats</h3>
                      <div className="space-y-3">
                         {report.threats.length === 0 ? <div className="text-gray-500 italic">No visible threats.</div> : 
                            report.threats.map((t: string, i: number) => (
                               <div key={i} className="flex items-start gap-3 p-3 bg-white/50 rounded-xl border border-white/40">
                                  <div className="mt-1 min-w-[8px] h-2 rounded-full bg-red-500" />
                                  <span className="text-sm font-bold text-gray-700 leading-snug">{t}</span>
                               </div>
                            ))
                         }
                      </div>
                   </div>

                   <div className="glass rounded-3xl p-6 shadow-lg bg-white/30">
                       <h3 className="font-bold text-gray-800 mb-4 uppercase text-xs tracking-wider">Metadata Forensics</h3>
                       <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 bg-white/50 rounded-xl">
                             <div className="text-[10px] text-gray-500 uppercase font-bold">GPS Location</div>
                             <div className={`font-bold ${report.meta.gps_found ? 'text-red-600' : 'text-green-600'}`}>
                                {report.meta.gps_found ? "DETECTED" : "CLEAN"}
                             </div>
                          </div>
                          <div className="p-4 bg-white/50 rounded-xl">
                             <div className="text-[10px] text-gray-500 uppercase font-bold">Device Fingerprint</div>
                             <div className="font-bold text-gray-700 truncate text-sm">
                                {report.meta.device_info}
                             </div>
                          </div>
                       </div>
                   </div>
                </motion.div>
             </AnimatePresence>
          )}
        </section>
      </div>
    </main>
  );
}