import React, { useState } from 'react';
import { Play, Loader2, CheckCircle2, AlertCircle, ShieldAlert, History, Database, Search, FileText, Info, Server, Lightbulb, XCircle, Beaker } from 'lucide-react';

interface AgentState {
  incident: string;
  status: string;
  hypotheses: string[];
  investigation_history: string[];
  evidence: any[];
  observed_facts: string[];
  uncertainties: string[];
  alternative_explanations: string[];
  root_cause: string;
  confidence: number;
  iteration: number;
  next_action: string;
}

const App: React.FC = () => {
  const [incident, setIncident] = useState('');
  const [demoMode, setDemoMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startInvestigation = async (isDemo: boolean) => {
    if (!incident.trim()) return;
    setLoading(true);
    setAgentState(null);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/investigate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident, demo_mode: isDemo }),
      });

      if (!response.ok) throw new Error("Failed to start investigation");
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');
      
      if (!reader) throw new Error("No reader");
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '');
            if (dataStr) {
               try {
                   const state = JSON.parse(dataStr);
                   setAgentState(state);
               } catch (e) {
                   console.error("Parse error:", e);
               }
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const statusColors = {
    "INVESTIGATING": "bg-blue-500/20 text-blue-300 border-blue-500/30",
    "ROOT_CAUSE_CONFIRMED": "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    "INSUFFICIENT_EVIDENCE": "bg-amber-500/20 text-amber-300 border-amber-500/30",
    "RATE_LIMITED": "bg-orange-500/20 text-orange-300 border-orange-500/30",
    "ERROR": "bg-rose-500/20 text-rose-300 border-rose-500/30",
  };
  
  const currentStatus = agentState?.status || "READY";
  const statusBadgeClass = (statusColors as any)[currentStatus] || "bg-[#2a2a2a]/60 text-gray-300 border-white/20";

  return (
    <>
      <div className="bg-overlay"></div>
      
      {/* MAIN APPLICATION WINDOW */}
      <div className="w-full max-w-[1500px] h-[96vh] bg-[#141414]/40 backdrop-blur-[20px] border border-white/10 rounded-xl shadow-[0_10px_50px_rgba(0,0,0,0.8)] flex flex-col overflow-hidden m-4 md:m-6">
        
        {/* Title Bar */}
        <div className="bg-[#0f0f12]/50 border-b border-black/80 px-6 py-3 flex items-center justify-between select-none shrink-0">
          <div className="w-[60px]"></div>
          <div className="text-[13px] font-[600] text-gray-400 tracking-wide">
            Kubernetes RCA Dashboard
          </div>
          <div className="w-[60px]"></div>
        </div>

        {/* Scrollable Workspace */}
        <div className="flex-1 overflow-y-auto p-6 md:p-10 space-y-8">
          
          {/* HEADER SECTION */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
             <div>
                <h1 className="text-[32px] font-[800] text-white tracking-tight flex items-center gap-3">
                  <Database className="w-8 h-8 text-blue-500" />
                  Kubernetes RCA
                </h1>
                <p className="text-[16px] text-gray-400 mt-2 font-[500]">
                  Automated incident investigation and root cause analysis
                </p>
             </div>
             
             <div className={`px-5 py-2.5 rounded-[8px] border font-[700] text-[15px] tracking-wide flex items-center gap-3 backdrop-blur-md shadow-sm ${statusBadgeClass}`}>
               {loading && <Loader2 className="w-5 h-5 animate-spin" />}
               {currentStatus.replace(/_/g, ' ')}
             </div>
          </div>

          {/* INCIDENT INPUT & CONTROLS */}
          <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/15 p-[24px] rounded-xl shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-6">
             <div className="flex flex-col gap-3">
               <label className="text-[17px] font-[700] text-gray-100 flex items-center gap-2">
                 <Search className="w-5 h-5 text-gray-400" />
                 Incident Description
               </label>
               <textarea 
                  className="w-full min-h-[120px] bg-[#111111]/40 border border-white/20 focus:border-blue-500/80 rounded-[10px] p-[16px] text-[16px] text-white placeholder-gray-500 outline-none ring-4 ring-transparent focus:ring-blue-500/20 transition-all shadow-inner resize-y font-sans leading-relaxed"
                  placeholder="Describe the incident... e.g. The frontend is returning HTTP 502 errors and payment service is timing out."
                  value={incident}
                  onChange={e => setIncident(e.target.value)}
                  disabled={loading}
               />
             </div>
             
             {/* ACTIONS ROW */}
             <div className="flex flex-col xl:flex-row justify-between gap-6 xl:items-center">
                
                <div className="flex flex-wrap items-center gap-4">
                  <span className="text-[14px] text-gray-400 font-[600]">Presets:</span>
                  <button 
                     onClick={() => setIncident("The frontend is returning HTTP 502 errors.")} 
                     className="h-[42px] px-[16px] text-[14px] font-[600] rounded-[8px] bg-white/5 hover:bg-white/10 border border-white/15 text-gray-200 shadow-sm transition-all"
                  >
                    Frontend 502
                  </button>
                  <button 
                     onClick={() => setIncident("Payment workload keeps restarting")} 
                     className="h-[42px] px-[16px] text-[14px] font-[600] rounded-[8px] bg-white/5 hover:bg-white/10 border border-white/15 text-gray-200 shadow-sm transition-all"
                  >
                    Workload Restarting
                  </button>
                </div>
                
                <div className="flex flex-wrap items-center gap-4 w-full xl:w-auto justify-end">
                  <label className="flex items-center gap-3 cursor-pointer group bg-black/20 px-4 py-2 rounded-lg border border-white/5 hover:border-white/15 transition-all">
                     <input type="checkbox" checked={demoMode} onChange={e => setDemoMode(e.target.checked)} className="w-5 h-5 rounded border-gray-600 bg-gray-700 accent-blue-500 cursor-pointer" />
                     <span className="text-[15px] text-gray-300 group-hover:text-white font-[600] transition-colors">Use Mock LLM</span>
                  </label>
                  
                  <button 
                    onClick={() => startInvestigation(true)}
                    disabled={loading || !incident}
                    className="h-[46px] px-[20px] text-[15px] font-[600] rounded-[10px] bg-[#2a2a2a]/80 hover:bg-[#3a3a3a] border border-white/20 text-gray-100 shadow-md flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Beaker className="w-5 h-5 text-purple-400" />
                    Run Demo
                  </button>

                  <button 
                    onClick={() => startInvestigation(false)}
                    disabled={loading || !incident}
                    className="h-[48px] px-[24px] text-[16px] font-[700] rounded-[10px] bg-blue-600/90 hover:bg-blue-500 border border-blue-400/50 text-white shadow-[0_4px_15px_rgba(37,99,235,0.4)] flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 fill-white" />}
                    Investigate
                  </button>
                </div>
             </div>
          </div>

          {error && (
            <div className="bg-rose-900/40 border border-rose-500/50 p-[20px] text-rose-100 text-[16px] font-[600] flex items-center gap-4 rounded-xl backdrop-blur-md shadow-lg">
               <AlertCircle className="w-6 h-6 shrink-0 text-rose-400" />
               {error}
            </div>
          )}

          {agentState && (
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
              
              {/* LEFT COLUMN (Timeline & Security) */}
              <div className="flex flex-col gap-8 xl:col-span-4">
                
                {/* TIMELINE */}
                <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/10 rounded-xl p-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex-1">
                  <h2 className="text-[19px] font-[700] text-gray-100 mb-6 flex items-center gap-3">
                     <History className="w-6 h-6 text-blue-400" /> 
                     Investigation Timeline
                  </h2>
                  <div className="space-y-6">
                    {agentState.investigation_history.length === 0 && <span className="text-[15px] text-gray-500 italic">No events recorded.</span>}
                    
                    {agentState.investigation_history.map((h, i) => {
                      const isBlock = h.includes("SECURITY BLOCK");
                      const isCall = h.includes("Called");
                      let dotColor = "bg-blue-500 shadow-[0_0_8px_#3b82f6]";
                      let textColor = "text-gray-200";
                      let bgBlock = "bg-transparent";
                      let p = "p-0";
                      
                      if (isBlock) { 
                        dotColor = "bg-rose-500 shadow-[0_0_8px_#f43f5e]"; 
                        textColor = "text-rose-200 font-[600]"; 
                        bgBlock = "bg-rose-500/15 border border-rose-500/30 rounded-lg"; 
                        p = "p-4";
                      }
                      else if (isCall) { 
                        dotColor = "bg-purple-500 shadow-[0_0_8px_#a855f7]"; 
                        textColor = "text-gray-300 font-mono text-[14px]"; 
                        bgBlock = "bg-black/40 border border-white/10 rounded-lg";
                        p = "p-4";
                      }
                      
                      return (
                        <div key={i} className="flex items-start gap-4">
                          <div className="relative flex flex-col items-center shrink-0">
                            <div className={`w-3.5 h-3.5 rounded-full ${dotColor} mt-1.5`}></div>
                            {i !== agentState.investigation_history.length - 1 && (
                               <div className="w-px h-[calc(100%+24px)] bg-white/10 absolute top-5"></div>
                            )}
                          </div>
                          <div className={`flex-1 ${bgBlock} ${p}`}>
                            <div className={`text-[15px] leading-relaxed ${textColor}`}>{h}</div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* SECURITY STATUS */}
                <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/10 rounded-xl p-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                  <h2 className="text-[19px] font-[700] text-gray-100 mb-6 flex items-center gap-3">
                    <ShieldAlert className="w-6 h-6 text-emerald-400" /> 
                    Security Policies
                  </h2>
                  <div className="space-y-4 text-[15px] text-gray-200 font-[500]">
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/5"><CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0"/> Read-only investigation boundaries</div>
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/5"><CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0"/> Namespace strictly limited to rca-demo</div>
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/5"><CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0"/> Approved tool allowlist enforced</div>
                    <div className="flex items-center gap-3 bg-white/5 p-3 rounded-lg border border-white/5"><CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0"/> Untrusted telemetry sanitized</div>
                    
                    {agentState.evidence.filter(e => e.type === "error" && e.source === "system").map((e, i) => (
                      <div key={i} className="mt-6 p-5 bg-rose-900/30 border border-rose-500/40 text-rose-100 rounded-xl shadow-lg">
                         <div className="font-[700] text-[16px] flex items-center gap-2 mb-3 text-rose-400">
                           <XCircle className="w-5 h-5"/> ACTION INTERCEPTED
                         </div>
                         <div className="text-[14px] font-mono bg-black/50 px-3 py-2 rounded-lg border border-rose-500/20 mb-3 text-rose-200">
                           CMD: {e.resource}
                         </div>
                         <div className="text-[14px] font-[500] leading-relaxed opacity-90">{e.observation}</div>
                      </div>
                    ))}
                  </div>
                </div>
                
              </div>

              {/* RIGHT COLUMN (Data & Conclusions) */}
              <div className="flex flex-col gap-8 xl:col-span-8">
                
                {/* RCA CONCLUSION CARDS */}
                {agentState.status === "ROOT_CAUSE_CONFIRMED" && (
                  <div className="bg-[#102a1e]/40 backdrop-blur-xl border-2 border-emerald-500/50 p-[32px] rounded-xl shadow-[0_10px_40px_rgba(16,185,129,0.2)] relative overflow-hidden">
                    <div className="absolute -top-20 -right-20 w-64 h-64 bg-emerald-500/15 rounded-full blur-[80px] pointer-events-none"></div>
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 pb-6 border-b border-emerald-500/20 relative z-10 gap-4">
                       <h2 className="text-[26px] font-[800] text-emerald-400 flex items-center gap-3 tracking-tight">
                         <CheckCircle2 className="w-8 h-8" /> 
                         ROOT CAUSE CONFIRMED
                       </h2>
                       <div className="text-[16px] text-emerald-200 font-[700] bg-emerald-500/20 border border-emerald-500/40 px-4 py-2 rounded-lg shadow-sm tracking-wide">
                          CONFIDENCE: {(agentState.confidence * 100).toFixed(0)}%
                       </div>
                    </div>
                    <p className="text-emerald-50 whitespace-pre-wrap leading-[1.7] text-[17px] relative z-10 font-[600]">{agentState.root_cause}</p>
                  </div>
                )}

                {agentState.status === "INSUFFICIENT_EVIDENCE" && (
                  <div className="bg-[#2a1a0a]/40 backdrop-blur-xl border-2 border-amber-500/50 p-[32px] rounded-xl shadow-[0_10px_40px_rgba(245,158,11,0.2)]">
                    <div className="flex items-center justify-between mb-6 pb-6 border-b border-amber-500/20">
                       <h2 className="text-[26px] font-[800] text-amber-400 flex items-center gap-3 tracking-tight">
                         <AlertCircle className="w-8 h-8" /> 
                         INSUFFICIENT EVIDENCE
                       </h2>
                    </div>
                    <p className="text-amber-100 text-[17px] whitespace-pre-wrap leading-[1.7] font-[600]">{agentState.root_cause}</p>
                  </div>
                )}
                
                {agentState.status === "RATE_LIMITED" && (
                  <div className="bg-[#2a100a]/40 backdrop-blur-xl border-2 border-orange-500/50 p-[32px] rounded-xl shadow-[0_10px_40px_rgba(249,115,22,0.2)]">
                    <h2 className="text-[26px] font-[800] text-orange-400 flex items-center gap-3 mb-4 tracking-tight">
                      <AlertCircle className="w-8 h-8" /> 
                      API RATE LIMITED
                    </h2>
                    <p className="text-orange-100 text-[17px] leading-[1.7] font-[600]">Investigation paused because the API rate limit was reached. Partial state has been preserved.</p>
                  </div>
                )}

                {/* FACTS & HYPOTHESES GRID */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                   <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/10 rounded-xl p-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                      <h2 className="text-[19px] font-[700] text-gray-100 mb-6 flex items-center gap-3">
                         <FileText className="w-6 h-6 text-blue-400" />
                         Observed Facts
                      </h2>
                      <div className="space-y-4">
                        {agentState.observed_facts.length === 0 && <div className="text-gray-500 text-[15px] italic p-4 bg-white/5 rounded-lg">No facts gathered yet.</div>}
                        {agentState.observed_facts.map((f, i) => (
                          <div key={i} className="flex items-start gap-4 p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-colors">
                            <CheckCircle2 className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                            <span className="text-[15px] text-gray-200 leading-relaxed font-[500]">{f}</span>
                          </div>
                        ))}
                      </div>
                   </div>

                   <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/10 rounded-xl p-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                      <h2 className="text-[19px] font-[700] text-gray-100 mb-6 flex items-center gap-3">
                         <Lightbulb className="w-6 h-6 text-purple-400" />
                         Active Hypotheses
                      </h2>
                      <div className="space-y-4">
                        {agentState.hypotheses.length === 0 && <div className="text-gray-500 text-[15px] italic p-4 bg-white/5 rounded-lg">No active hypotheses.</div>}
                        {agentState.hypotheses.map((h, i) => (
                          <div key={i} className="flex items-start gap-4 p-4 bg-white/5 border border-white/5 rounded-xl hover:bg-white/10 transition-colors">
                            <Info className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
                            <span className="text-[15px] text-gray-200 leading-relaxed font-[500]">{h}</span>
                          </div>
                        ))}
                      </div>
                   </div>
                </div>
                
                {/* ALTERNATIVES & UNCERTAINTY */}
                {(agentState.alternative_explanations.length > 0 || agentState.uncertainties.length > 0) && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                     <div className="bg-[#191919]/15 backdrop-blur-md border border-white/5 rounded-xl p-[24px] shadow-lg">
                        <h2 className="text-[18px] font-[600] text-gray-300 mb-5">
                           Alternative Explanations
                        </h2>
                        <ul className="space-y-4">
                          {agentState.alternative_explanations.map((a, i) => (
                            <li key={i} className="flex items-start gap-4">
                              <span className="w-2 h-2 rounded-full bg-gray-500 mt-2 shrink-0"></span>
                              <span className="text-[15px] text-gray-400 leading-relaxed font-[400]">{a}</span>
                            </li>
                          ))}
                        </ul>
                     </div>

                     <div className="bg-[#191919]/15 backdrop-blur-md border border-white/5 rounded-xl p-[24px] shadow-lg">
                        <h2 className="text-[18px] font-[600] text-gray-300 mb-5">
                           Remaining Uncertainty
                        </h2>
                        <ul className="space-y-4">
                          {agentState.uncertainties.length === 0 && <li className="text-gray-500 text-[15px] italic">No significant uncertainty.</li>}
                          {agentState.uncertainties.map((u, i) => (
                            <li key={i} className="flex items-start gap-4">
                              <span className="w-2 h-2 rounded-full bg-gray-500 mt-2 shrink-0"></span>
                              <span className="text-[15px] text-gray-400 leading-relaxed font-[400]">{u}</span>
                            </li>
                          ))}
                        </ul>
                     </div>
                  </div>
                )}

                {/* EVIDENCE SECTION */}
                <div className="bg-[#191919]/25 backdrop-blur-[16px] border border-white/10 rounded-xl p-[24px] shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
                  <h2 className="text-[19px] font-[700] text-gray-100 mb-6 flex items-center gap-3">
                     <Server className="w-6 h-6 text-indigo-400" />
                     Collected Evidence Log
                  </h2>
                  <div className="space-y-5">
                    {agentState.evidence.length === 0 && <p className="text-gray-500 italic text-[15px] p-4 bg-white/5 rounded-xl border border-white/5">No evidence collected yet.</p>}
                    {agentState.evidence.map((ev, i) => (
                      <div key={i} className="bg-black/30 border border-white/10 rounded-xl overflow-hidden shadow-sm">
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-[20px] bg-white/5 border-b border-white/5">
                          <div className="flex items-center gap-4">
                            <span className="px-3 py-1.5 bg-indigo-600/30 text-indigo-200 border border-indigo-500/40 text-[13px] font-[700] font-mono rounded-md shadow-sm uppercase tracking-wider shrink-0">
                              {ev.source}
                            </span>
                            <span className="text-[15px] font-[600] text-gray-200">{ev.type}</span>
                          </div>
                          <div className="text-[13px] text-gray-500 font-mono font-[500]">{ev.timestamp}</div>
                        </div>
                        
                        <div className="p-[20px] space-y-4">
                           <div className="text-[15px] text-gray-200 leading-relaxed font-[500]">
                              {ev.observation}
                           </div>
                           
                           <div className="text-[14px] text-gray-500 font-mono pt-2 border-t border-white/5">
                              Target: {ev.resource}
                           </div>

                           {ev.metadata && (
                              <div className="mt-4">
                                <pre className="bg-[#0a0a0a]/80 border border-white/5 text-gray-400 p-[16px] rounded-lg text-[13px] font-mono overflow-x-auto custom-scrollbar shadow-inner">
                                  {JSON.stringify(ev.metadata, null, 2)}
                                </pre>
                              </div>
                           )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </div>
          )}
          
        </div>

        {/* FOOTER */}
        <div className="bg-black/20 border-t border-white/5 py-3 text-center text-[13px] text-gray-400 font-[500] tracking-wider shrink-0 mt-auto backdrop-blur-md">
           Made By Prabhat Kumar Jha
        </div>
      </div>
    </>
  );
}

export default App;
