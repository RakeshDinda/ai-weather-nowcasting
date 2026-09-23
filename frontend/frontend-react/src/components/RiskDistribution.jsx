import React from 'react';

const RiskDistribution = ({ locations = [], allCitiesData = [] }) => {
    const list = locations.length > 0 ? locations : allCitiesData;
    let critical = 0, high = 0, medium = 0, low = 0;
    
    list.forEach(city => {
        const risk = (city.risk_level || city.risk || city.prediction?.risk_text || "LOW").toUpperCase();
        const rain = Number(city.weather?.rainfall || 0);
        
        if (risk === "HIGH") {
            if (rain > 25.0) {
                critical++;
            } else {
                high++;
            }
        } else if (risk === "MODERATE") {
            medium++;
        } else {
            low++;
        }
    });

    if (list.length === 0) {
        critical = 0; high = 0; medium = 0; low = 0;
    }

    const total = critical + high + medium + low;

    return (
        <div className="h-full bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-800 p-5 flex flex-col justify-between">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-black text-slate-800 dark:text-white">Risk Distribution <span className="text-slate-400 font-bold text-xs ml-1">({total} Zones)</span></h3>
                <button className="text-blue-600 dark:text-blue-400 text-[11px] font-black hover:underline tracking-wide">View Details ➔</button>
            </div>
            
            <div className="flex items-center justify-between gap-2.5 mt-2">
                <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-xl p-2.5 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-1.5 mb-1">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-600 shadow-sm shadow-red-500/50"></div>
                        <span className="text-xl font-black text-slate-800 dark:text-white leading-none">{critical}</span>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Critical</span>
                </div>
                
                <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-xl p-2.5 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-1.5 mb-1">
                        <div className="w-2.5 h-2.5 rounded-full bg-orange-500 shadow-sm shadow-orange-500/50"></div>
                        <span className="text-xl font-black text-slate-800 dark:text-white leading-none">{high}</span>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">High</span>
                </div>
                
                <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-xl p-2.5 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-1.5 mb-1">
                        <div className="w-2.5 h-2.5 rounded-full bg-yellow-400 shadow-sm shadow-yellow-400/50"></div>
                        <span className="text-xl font-black text-slate-800 dark:text-white leading-none">{medium}</span>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Medium</span>
                </div>
                
                <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 rounded-xl p-2.5 flex flex-col items-center justify-center">
                    <div className="flex items-center gap-1.5 mb-1">
                        <div className="w-2.5 h-2.5 rounded-full bg-teal-500 shadow-sm shadow-teal-500/50"></div>
                        <span className="text-xl font-black text-slate-800 dark:text-white leading-none">{low}</span>
                    </div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">Low</span>
                </div>
            </div>
        </div>
    );
};

export default RiskDistribution;
