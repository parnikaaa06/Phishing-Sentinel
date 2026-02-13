import './Dashboard.css';
import React from 'react';
import { useState, useEffect } from 'react';

import { AlertTriangle, CheckCircle, Activity, Globe, Lock, RefreshCw } from 'lucide-react';

function Dashboard({ stats, recentEvents, loading }) {

    const displayStats = stats || { scanned: 0, threatsBlocked: 0, trustScore: 100 };
    return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-8">
      {/* Header */}
      <header className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <img src="/assets/phishingSentinelLogo.png" alt="Phishing Sentinel logo" className="w-10 h-10 object-contain" />

          <h1 className="text-3xl font-bold tracking-tight">SENTINEL <span className="text-cyan-400">HUB</span></h1>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg flex items-center gap-2">
            <Activity className={`w-4 h-4 ${loading ? 'text-slate-500 animate-spin' : 'text-cyan-400'}`} />
            <span className="text-sm font-medium">{loading ? 'Syncing...' : 'System Live'}</span>
          </div>
        </div>
      </header>

      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatCard title="Total Pages Scanned" value={stats.scanned} icon={<Globe className="text-blue-400" />} />
        <StatCard title="Threats Neutralized" value={stats.threatsBlocked} icon={<AlertTriangle className="text-red-400" />} />
        <StatCard title="Security Trust Score" value={`${stats.trustScore}%`} icon={<Lock className="text-green-400" />} />
      </div>

      {/* Real-Time Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center">
          <h2 className="text-xl font-semibold">Real-Time Observation Log</h2>
          <span className="text-xs font-mono text-slate-500">POLLING ACTIVE</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-950 text-slate-400 text-sm uppercase">
              <tr>
                <th className="px-6 py-4">Target URL</th>
                <th className="px-6 py-4">Classification</th>
                <th className="px-6 py-4">Confidence</th>
                <th className="px-6 py-4">Threat Level</th>
                <th className="px-6 py-4">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {recentEvents?.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-slate-500 italic">
                    No scan data received yet. Browse websites with the Sentinel extension to see live data.
                  </td>
                </tr>
              ) : (
                recentEvents.map((event) => (
                  <tr key={event.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-slate-300 max-w-md truncate">
                      {event.url}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`flex items-center gap-2 text-sm font-medium ${!event.is_spoof ? 'text-green-400' : 'text-red-400'}`}>
                        {!event.is_spoof ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                        {!event.is_spoof ? 'Legitimate' : 'Phishing'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-sm">
                      {(event.confidence_score * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        event.threat_level === 'high' ? 'bg-red-400/10 text-red-400' : 
                        event.threat_level === 'medium' ? 'bg-orange-400/10 text-orange-400' : 
                        'bg-green-400/10 text-green-400'
                      }`}>
                        {event.threat_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
    );
}

const StatCard = ({ title, value, icon }) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl relative overflow-hidden group">
    <div className="flex justify-between items-start mb-4 relative z-10">
      <div className="p-3 bg-slate-950 rounded-lg group-hover:scale-110 transition-transform">{icon}</div>
    </div>
    <div className="relative z-10">
      <h3 className="text-slate-400 text-sm font-medium mb-1">{title}</h3>
      <p className="text-3xl font-bold tracking-tight">{value}</p>
    </div>
    {/* Decorative background element */}
    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
      {React.cloneElement(icon, { size: 100 })}
    </div>
  </div>
);


export default Dashboard;