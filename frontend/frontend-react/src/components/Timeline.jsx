import React, { useState } from 'react';
import { Play, FileText } from 'lucide-react';

const Timeline = () => {
    const [activeStep, setActiveStep] = useState(3);
    const steps = ['Now', '+1h', '+2h', '+3h', '+4h', '+5h', '+6h'];

    return (
        <div className="h-full bg-white dark:bg-slate-900 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-800 p-5 flex flex-col justify-between overflow-hidden">
            <div className="flex items-center gap-2">
                <FileText size={16} className="text-blue-600" />
                <h3 className="text-sm font-black text-slate-800 dark:text-white">Forecast Timeline <span className="text-slate-400 font-bold ml-1 text-xs">(Next 6 Hours)</span></h3>
            </div>
            
            <div className="flex items-center gap-6 mt-2">
                <button className="w-12 h-12 bg-blue-600 hover:bg-blue-700 rounded-full flex items-center justify-center text-white shadow-lg shadow-blue-500/30 transition-transform hover:scale-105 shrink-0 border-2 border-white dark:border-slate-900">
                    <Play size={20} className="fill-white ml-1" />
                </button>
                
                <div className="flex-1 relative pl-2 pr-6">
                    <div className="absolute top-1/2 left-0 right-6 h-1.5 bg-slate-100 dark:bg-slate-800 -translate-y-1/2 rounded-full"></div>
                    <div className="absolute top-1/2 left-0 h-1.5 bg-blue-500 -translate-y-1/2 rounded-full transition-all duration-300" style={{ width: `${(activeStep / (steps.length - 1)) * 100}%` }}></div>
                    
                    <div className="relative flex justify-between">
                        {steps.map((time, i) => (
                            <div key={i} onClick={() => setActiveStep(i)} className="flex flex-col items-center gap-2 relative z-10 -ml-2 cursor-pointer group">
                                <div className={`w-3.5 h-3.5 rounded-full border-[3px] border-white dark:border-slate-900 transition-all ${i <= activeStep ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'} ${i === activeStep ? 'ring-4 ring-blue-100 dark:ring-blue-900/50 scale-125' : 'group-hover:scale-110'}`}></div>
                                <span className={`text-[11px] font-black transition-colors ${i === activeStep ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300'} mt-1`}>{time}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Timeline;
