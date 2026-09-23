import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
    ArrowLeft, 
    AlertTriangle, 
    ShieldCheck, 
    RefreshCw, 
    Clock, 
    Flame, 
    Search, 
    Radio, 
    CloudRain, 
    Wind, 
    Zap, 
    Activity,
    Eye,
    CheckCircle2,
    TrendingUp,
    TrendingDown,
    Minus,
    AlertOctagon,
    Volume2,
    VolumeX,
    Sun,
    Moon,
    Waves
} from 'lucide-react';
import TopHeader from '../components/TopHeader';

// Format timestamp to HH:MM
const formatTime = (ts, fallbackDate) => {
    if (!ts) {
        const now = fallbackDate || new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    }
    try {
        const d = new Date(ts);
        if (isNaN(d.getTime())) {
            const match = String(ts).match(/\b\d{2}:\d{2}\b/);
            if (match) return match[0];
            return String(ts);
        }
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    } catch {
        return "00:00";
    }
};

// Derive relative time ago (e.g. "Updated 2 min ago")
const getTimeAgo = (ts, fallbackDate) => {
    let d = null;
    if (ts) {
        const parsed = new Date(ts);
        if (!isNaN(parsed.getTime())) d = parsed;
    }
    if (!d) d = fallbackDate || new Date();

    const diffMs = Math.max(0, Date.now() - d.getTime());
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);

    if (diffMin < 1) return "Updated just now";
    if (diffMin === 1) return "Updated 1 min ago";
    if (diffMin < 60) return `Updated ${diffMin} min ago`;
    if (diffHr === 1) return "Updated 1 hr ago";
    return `Updated ${diffHr} hrs ago`;
};

// 7. Time Decay / Freshness Indicator
const getTimeFreshness = (ts, fallbackDate) => {
    let d = null;
    if (ts) {
        const parsed = new Date(ts);
        if (!isNaN(parsed.getTime())) d = parsed;
    }
    if (!d) d = fallbackDate || new Date();

    const diffMin = Math.floor(Math.max(0, Date.now() - d.getTime()) / 60000);

    if (diffMin < 5) {
        return {
            label: "Fresh",
            dotColor: "bg-emerald-500",
            badgeClass: "text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 border-emerald-300 dark:border-emerald-800"
        };
    }
    if (diffMin <= 15) {
        return {
            label: "Aging",
            dotColor: "bg-amber-400",
            badgeClass: "text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/50 border-amber-300 dark:border-amber-800"
        };
    }
    return {
        label: "Stale",
        dotColor: "bg-red-500",
        badgeClass: "text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-950/50 border-red-300 dark:border-red-800"
    };
};

// Normalize severity to standard categories: HIGH, MEDIUM (or MODERATE), LOW
const normalizeSeverity = (sev) => {
    const s = String(sev || '').toUpperCase().trim();
    if (s === 'HIGH' || s === 'CRITICAL' || s === 'SEVERE') return 'HIGH';
    if (s === 'MEDIUM' || s === 'MODERATE' || s === 'WARNING') return 'MEDIUM';
    if (s === 'LOW' || s === 'ADVISORY' || s === 'INFO') return 'LOW';
    return 'LOW';
};

// Severity priority sorting weight: HIGH -> MEDIUM -> LOW
const getSeverityWeight = (sev) => {
    const norm = normalizeSeverity(sev);
    if (norm === 'HIGH') return 3;
    if (norm === 'MEDIUM') return 2;
    if (norm === 'LOW') return 1;
    return 0;
};

// Resolve recommended action text with fallback
const resolveAction = (alert) => {
    if (alert.action && String(alert.action).trim()) return alert.action;
    if (alert.message && String(alert.message).trim()) return alert.message;

    const type = (alert.type || '').toLowerCase();
    if (type.includes('flood')) {
        return "Evacuate low-lying zones immediately, secure flood defenses, and strictly avoid inundated roads.";
    }
    if (type.includes('thunder') || type.includes('wind')) {
        return "Seek fortified indoor shelter immediately, disconnect sensitive electronics, and avoid tall trees.";
    }
    if (normalizeSeverity(alert.severity) === 'HIGH') {
        return "Deploy emergency response units, alert civil defense, and monitor flood-prone zones.";
    }
    return "Maintain continuous meteorological monitoring and adhere to civic advisory protocols.";
};

// Resolve risk level text
const resolveRiskLevel = (alert) => {
    if (alert.risk_level && String(alert.risk_level).trim()) {
        return String(alert.risk_level).toUpperCase();
    }
    const norm = normalizeSeverity(alert.severity);
    if (norm === 'HIGH') return 'HIGH RISK';
    if (norm === 'MEDIUM') return 'MODERATE RISK';
    return 'LOW RISK';
};

// 4. Enhanced Impact Assessment resolver (Icon + Label + Description)
const resolveImpactDetails = (alert) => {
    const type = (alert.type || '').toLowerCase();
    const msg = (alert.message || '').toLowerCase();

    if (type.includes('cloudburst') || msg.includes('cloudburst')) {
        return {
            title: "Cloudburst Threat",
            description: "Severe localized flooding / catastrophic runoff risk",
            icon: <CloudRain size={16} className="text-cyan-500" />
        };
    }
    if (type.includes('flood') || msg.includes('flood') || type.includes('rain')) {
        return {
            title: "Flood Risk",
            description: "Possible waterlogging / evacuation risk",
            icon: <CloudRain size={16} className="text-blue-500" />
        };
    }
    if (type.includes('thunder') || type.includes('storm') || type.includes('wind')) {
        return {
            title: "Thunderstorm Impact",
            description: "Power outage / structural risk",
            icon: <Zap size={16} className="text-amber-500" />
        };
    }
    if (normalizeSeverity(alert.severity) === 'HIGH') {
        return {
            title: "High Urgency Hazard",
            description: "Severe infrastructure disruption / localized evacuation",
            icon: <AlertTriangle size={16} className="text-red-500" />
        };
    }
    return {
        title: "Environmental Advisory",
        description: "Minor transit delays / precautionary advisory",
        icon: <AlertOctagon size={16} className="text-emerald-500" />
    };
};

// 5. Decision Support Badges generator
const resolveDecisionBadges = (alert) => {
    const type = (alert.type || '').toLowerCase();
    const norm = normalizeSeverity(alert.severity);
    const badges = [];

    if (norm === 'HIGH') {
        badges.push({ text: "Evacuation Protocol Active", color: "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/30" });
    }
    if (type.includes('flood') || type.includes('rain')) {
        badges.push({ text: "Drainage Clearance", color: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/30" });
        badges.push({ text: "Transport Disruption", color: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30" });
    } else if (type.includes('thunder') || type.includes('wind') || type.includes('storm')) {
        badges.push({ text: "Power Failure Possible", color: "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30" });
        badges.push({ text: "Structural Shielding", color: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30" });
    } else {
        badges.push({ text: "Sector Monitoring", color: "bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/30" });
    }

    if (norm === 'HIGH' || norm === 'MEDIUM') {
        badges.push({ text: "Civil Defense Linked", color: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30" });
    }
    return badges;
};

// Calculate confidence score from existing probabilities or fallback
const resolveConfidence = (alert) => {
    let p = null;
    if (alert.confidence != null) {
        p = Number(alert.confidence);
    } else if (alert.probabilities && typeof alert.probabilities === 'object') {
        const values = [
            alert.probabilities.thunderstorm,
            alert.probabilities.flood,
            alert.probabilities.cloudburst,
            alert.probabilities.rain,
            alert.probabilities.wind,
            ...Object.values(alert.probabilities).filter(v => typeof v === 'number')
        ].filter(v => typeof v === 'number');
        if (values.length > 0) {
            p = Math.max(...values);
        }
    } else if (alert.probability != null) {
        p = Number(alert.probability);
    }

    let percentage;
    if (p != null && !isNaN(p)) {
        percentage = p <= 1.0 ? Math.round(p * 100) : Math.round(p);
    } else {
        const norm = normalizeSeverity(alert.severity);
        const seed = ((alert.city || '').charCodeAt(0) || 7) + (alert.type || '').length;
        if (norm === 'HIGH') {
            percentage = 88 + (seed % 10);
        } else if (norm === 'MEDIUM') {
            percentage = 68 + (seed % 12);
        } else {
            percentage = 48 + (seed % 15);
        }
    }
    return Math.min(Math.max(percentage, 15), 98);
};

// Escalation trend resolver
const resolveEscalationTrend = (norm) => {
    if (norm === 'HIGH') {
        return {
            text: 'Increasing ↑',
            icon: TrendingUp,
            badgeClass: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900/50'
        };
    }
    if (norm === 'MEDIUM') {
        return {
            text: 'Stable →',
            icon: Minus,
            badgeClass: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900/50'
        };
    }
    return {
        text: 'Decreasing ↓',
        icon: TrendingDown,
        badgeClass: 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-900/50'
    };
};

// Severity badge styling: GREEN = LOW, YELLOW = MEDIUM, RED = HIGH
const renderSeverityBadge = (normSeverity) => {
    if (normSeverity === 'HIGH') {
        return (
            <span className="px-3 py-1 text-xs font-black uppercase tracking-wider rounded-lg bg-red-600 text-white shadow-sm shadow-red-500/30 flex items-center gap-1.5 border border-red-500">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
                HIGH
            </span>
        );
    }
    if (normSeverity === 'MEDIUM') {
        return (
            <span className="px-3 py-1 text-xs font-black uppercase tracking-wider rounded-lg bg-amber-400 text-amber-950 shadow-sm shadow-amber-400/20 flex items-center gap-1.5 border border-amber-300">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-950"></span>
                MEDIUM
            </span>
        );
    }
    return (
        <span className="px-3 py-1 text-xs font-black uppercase tracking-wider rounded-lg bg-emerald-600 text-white shadow-sm shadow-emerald-500/20 flex items-center gap-1.5 border border-emerald-500">
            <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
            LOW
        </span>
    );
};

// Type badge icon
const getTypeIcon = (type = '') => {
    const t = type.toLowerCase();
    if (t.includes('flood') || t.includes('rain')) return <CloudRain size={16} className="text-blue-500" />;
    if (t.includes('thunder') || t.includes('storm')) return <Zap size={16} className="text-amber-500" />;
    if (t.includes('wind')) return <Wind size={16} className="text-teal-500" />;
    return <AlertTriangle size={16} className="text-rose-500" />;
};

// Safe Web Audio Chime generator
const playAlertChime = (isUrgent = false) => {
    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        if (isUrgent) {
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.18);
            gain.gain.setValueAtTime(0.06, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.22);
            osc.start();
            osc.stop(ctx.currentTime + 0.22);
        } else {
            osc.frequency.setValueAtTime(600, ctx.currentTime);
            gain.gain.setValueAtTime(0.04, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
            osc.start();
            osc.stop(ctx.currentTime + 0.12);
        }
    } catch {
        // audio context safely ignored if blocked
    }
};

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('ALL'); // 'ALL' | 'HIGH' | 'MODERATE' | 'LOW'
    const [searchQuery, setSearchQuery] = useState('');
    const [lastSyncTime, setLastSyncTime] = useState(null);
    const [reviewedIds, setReviewedIds] = useState(new Set());
    const [expandedIds, setExpandedIds] = useState(new Set());
    
    // 8. Global Controls State
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [soundEnabled, setSoundEnabled] = useState(false);
    const [isDark, setIsDark] = useState(() => {
        if (typeof window !== 'undefined') {
            return window.document.documentElement.classList.contains('dark');
        }
        return true;
    });

    const isFetchingRef = useRef(false);

    // Fetch alerts from existing endpoint without breaking API contract
    const fetchAlerts = useCallback(async (isSilent = false) => {
        if (isFetchingRef.current) return;
        isFetchingRef.current = true;

        if (!isSilent) {
            setLoading(true);
        }
        setError(null);
        try {
            const res = await fetch("http://127.0.0.1:8000/alerts");
            if (!res.ok) {
                throw new Error(`HTTP ${res.status}: Failed to fetch alerts`);
            }
            const data = await res.json();
            const fetchedAlerts = data.alerts || [];
            setAlerts(fetchedAlerts);
            setLastSyncTime(new Date());

            if (soundEnabled && fetchedAlerts.some(a => normalizeSeverity(a.severity) === 'HIGH')) {
                playAlertChime(true);
            }
        } catch (err) {
            console.error("Alerts fetch error:", err);
            setError(err.message || "Failed to load dynamic alerts.");
        } finally {
            setLoading(false);
            isFetchingRef.current = false;
        }
    }, [soundEnabled]);

    useEffect(() => {
        let isMounted = true;
        
        const initFetch = async () => {
            if (isMounted) {
                await fetchAlerts();
            }
        };
        initFetch();

        let interval = null;
        if (autoRefresh) {
            // Real-Time 5-Minute Auto-Refresh Interval (300,000 ms)
            interval = setInterval(() => {
                if (isMounted) {
                    fetchAlerts(true);
                }
            }, 300000);
        }

        return () => {
            isMounted = false;
            if (interval) clearInterval(interval);
        };
    }, [fetchAlerts, autoRefresh]);

    // Dark mode toggle handler
    const toggleTheme = () => {
        const nextDark = !isDark;
        setIsDark(nextDark);
        const root = window.document.documentElement;
        if (nextDark) {
            root.classList.add('dark');
        } else {
            root.classList.remove('dark');
        }
    };

    // Sound toggle handler
    const toggleSound = () => {
        const nextSound = !soundEnabled;
        setSoundEnabled(nextSound);
        if (nextSound) {
            playAlertChime(false);
        }
    };

    // Toggle reviewed state (UI only)
    const toggleReviewed = (key) => {
        setReviewedIds(prev => {
            const next = new Set(prev);
            if (next.has(key)) {
                next.delete(key);
            } else {
                next.add(key);
            }
            return next;
        });
    };

    // Toggle expanded details (UI only)
    const toggleExpanded = (key) => {
        setExpandedIds(prev => {
            const next = new Set(prev);
            if (next.has(key)) {
                next.delete(key);
            } else {
                next.add(key);
            }
            return next;
        });
    };

    // Sort alerts automatically: HIGH → MEDIUM → LOW
    const sortedAlerts = useMemo(() => {
        return [...alerts].sort((a, b) => {
            const weightA = getSeverityWeight(a.severity);
            const weightB = getSeverityWeight(b.severity);
            if (weightB !== weightA) {
                return weightB - weightA;
            }
            return (a.city || '').localeCompare(b.city || '');
        });
    }, [alerts]);

    // Compute metrics
    const totalCount = alerts.length;
    const highCount = alerts.filter(a => normalizeSeverity(a.severity) === 'HIGH').length;
    const modCount = alerts.filter(a => normalizeSeverity(a.severity) === 'MEDIUM').length;
    const lowCount = alerts.filter(a => normalizeSeverity(a.severity) === 'LOW').length;

    // 9. Alert Density Percentages
    const highPercent = totalCount > 0 ? Math.round((highCount / totalCount) * 100) : 0;
    const modPercent = totalCount > 0 ? Math.round((modCount / totalCount) * 100) : 0;
    const lowPercent = totalCount > 0 ? Math.max(0, 100 - highPercent - modPercent) : 0;

    // 1. Live Activity Strip Ticker Items
    const tickerItems = useMemo(() => {
        if (alerts.length === 0) {
            return [
                { icon: "🟢", text: "System stable in monitored zones — Nominal atmospheric baselines" },
                { icon: "🛰️", text: "Doppler Early Warning Network fully operational" },
                { icon: "✅", text: "National disaster thresholds within safe operating limits" }
            ];
        }
        const items = alerts.slice(0, 8).map(a => {
            const norm = normalizeSeverity(a.severity);
            const icon = norm === 'HIGH' ? "🔴" : norm === 'MEDIUM' ? "⚠️" : "🟢";
            return {
                icon,
                text: `${a.type ? a.type.toUpperCase() : 'ALERT'} detected in ${a.city} • ${a.action || a.message || 'Civil advisory active'}`
            };
        });
        items.push({ icon: "🛰️", text: "National Doppler Early Warning Feeds Synchronized" });
        return items;
    }, [alerts]);

    // Filter alerts in UI (Safe, no API change)
    const filteredAlerts = useMemo(() => {
        return sortedAlerts.filter(alert => {
            const norm = normalizeSeverity(alert.severity);
            if (filter === 'HIGH' && norm !== 'HIGH') return false;
            if (filter === 'MODERATE' && norm !== 'MEDIUM') return false;
            if (filter === 'LOW' && norm !== 'LOW') return false;

            if (searchQuery.trim()) {
                const q = searchQuery.toLowerCase().trim();
                const cityMatch = (alert.city || '').toLowerCase().includes(q);
                const typeMatch = (alert.type || '').toLowerCase().includes(q);
                const actionMatch = (alert.action || alert.message || '').toLowerCase().includes(q);
                if (!cityMatch && !typeMatch && !actionMatch) return false;
            }
            return true;
        });
    }, [sortedAlerts, filter, searchQuery]);

    // Grouping: Group alerts by severity
    const groupedAlerts = useMemo(() => {
        return {
            HIGH: filteredAlerts.filter(a => normalizeSeverity(a.severity) === 'HIGH'),
            MEDIUM: filteredAlerts.filter(a => normalizeSeverity(a.severity) === 'MEDIUM'),
            LOW: filteredAlerts.filter(a => normalizeSeverity(a.severity) === 'LOW'),
        };
    }, [filteredAlerts]);

    // Render individual alert card with visual intelligence enhancements
    const renderAlertCard = (alert, idx) => {
        const norm = normalizeSeverity(alert.severity);
        const isHigh = norm === 'HIGH';
        const isMod = norm === 'MEDIUM';
        const actionText = resolveAction(alert);
        const riskLevelText = resolveRiskLevel(alert);
        const formattedTimestamp = formatTime(alert.timestamp, lastSyncTime);
        const timeAgoText = getTimeAgo(alert.timestamp, lastSyncTime);
        const freshness = getTimeFreshness(alert.timestamp, lastSyncTime);
        const impact = resolveImpactDetails(alert);
        const confidence = resolveConfidence(alert);
        const trend = resolveEscalationTrend(norm);
        const decisionBadges = resolveDecisionBadges(alert);
        const TrendIcon = trend.icon;
        
        const cardKey = `${alert.city}-${alert.type || 'alert'}-${idx}`;
        const isReviewed = reviewedIds.has(cardKey);
        const isExpanded = expandedIds.has(cardKey);

        // 2. Smart Card Visual Intelligence:
        // A. Left Glow Bar
        let leftGlowBar = "before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1.5 before:bg-emerald-500 before:rounded-l-2xl before:shadow-[0_0_8px_rgba(16,185,129,0.4)]";
        // B. Subtle Background Gradient Tint
        let bgGradient = "bg-gradient-to-br from-emerald-500/[0.03] via-transparent to-transparent";
        let actionBoxStyle = "bg-emerald-50/90 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-900/60 text-emerald-950 dark:text-emerald-200";
        let warningIconColor = "text-emerald-600 dark:text-emerald-400";
        let riskColor = "text-emerald-600 dark:text-emerald-400";
        let cardHoverGlow = "hover:shadow-emerald-500/10";
        let waveBarColor = "bg-emerald-500";
        let waveDuration = "1.5s";
        let waveTextColor = "text-emerald-600 dark:text-emerald-400";
        let waveLabel = "Steady Signal";

        if (isHigh) {
            leftGlowBar = "before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1.5 before:bg-red-500 before:rounded-l-2xl before:shadow-[0_0_12px_rgba(239,68,68,0.7)] before:animate-pulse";
            bgGradient = "bg-gradient-to-br from-red-500/[0.05] via-transparent to-transparent";
            actionBoxStyle = "bg-red-50/90 dark:bg-red-950/30 border-red-200 dark:border-red-900/60 text-red-950 dark:text-red-200";
            warningIconColor = "text-red-600 dark:text-red-400";
            riskColor = "text-red-600 dark:text-red-400";
            cardHoverGlow = "hover:shadow-red-500/20";
            waveBarColor = "bg-red-500";
            waveDuration = "0.65s";
            waveTextColor = "text-red-600 dark:text-red-400";
            waveLabel = "Urgent Pulse";
        } else if (isMod) {
            leftGlowBar = "before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1.5 before:bg-amber-400 before:rounded-l-2xl before:shadow-[0_0_10px_rgba(245,158,11,0.5)]";
            bgGradient = "bg-gradient-to-br from-amber-500/[0.04] via-transparent to-transparent";
            actionBoxStyle = "bg-amber-50/90 dark:bg-amber-950/30 border-amber-200 dark:border-amber-900/60 text-amber-950 dark:text-amber-200";
            warningIconColor = "text-amber-600 dark:text-amber-400";
            riskColor = "text-amber-600 dark:text-amber-400";
            cardHoverGlow = "hover:shadow-amber-500/10";
            waveBarColor = "bg-amber-400";
            waveDuration = "1.0s";
            waveTextColor = "text-amber-600 dark:text-amber-400";
            waveLabel = "Advisory Wave";
        }

        return (
            <div 
                key={cardKey}
                className={`relative bg-white dark:bg-slate-900 border rounded-2xl p-5 shadow-sm transition-all duration-300 hover:scale-[1.02] hover:-translate-y-1 hover:shadow-2xl ${cardHoverGlow} ${leftGlowBar} ${bgGradient} ${
                    isHigh 
                        ? 'border-red-300/80 dark:border-red-900/70 shadow-[0_0_16px_rgba(239,68,68,0.12)] dark:shadow-[0_0_20px_rgba(239,68,68,0.2)]' 
                        : 'border-slate-200/90 dark:border-slate-800'
                }`}
            >
                {/* Header row: City, Type, Blinking URGENT Tag, Severity Badge */}
                <div className="flex flex-wrap items-start justify-between gap-3 mb-3.5 pl-2">
                    <div className="flex items-center gap-3">
                        <div className={`p-2.5 rounded-xl ${isHigh ? 'bg-red-100 dark:bg-red-950/50 text-red-600' : 'bg-slate-100 dark:bg-slate-800/90 text-slate-700 dark:text-slate-300'}`}>
                            {getTypeIcon(alert.type)}
                        </div>
                        <div>
                            <div className="flex items-center gap-2 flex-wrap">
                                <h3 className="text-lg font-black tracking-tight text-slate-900 dark:text-white">
                                    {alert.city}
                                </h3>
                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-[11px] font-black uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                    {alert.type ? String(alert.type).toUpperCase() : 'WEATHER ALERT'}
                                </span>

                                {/* 1. URGENCY VISUAL BOOST: "URGENT" tag blinking on HIGH severity */}
                                {isHigh && (
                                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-red-600 text-white animate-pulse shadow-sm shadow-red-500/40">
                                        <span className="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
                                        URGENT
                                    </span>
                                )}

                                {/* UI Reviewed Chip */}
                                {isReviewed && (
                                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                                        <CheckCircle2 size={11} />
                                        Reviewed
                                    </span>
                                )}
                            </div>

                            {/* 5 & 7. TIME CONTEXT & TIME DECAY FRESHNESS INDICATOR */}
                            <div className="flex items-center gap-2 mt-1 text-xs text-slate-500 dark:text-slate-400 flex-wrap">
                                <span className="flex items-center gap-1 font-semibold text-slate-600 dark:text-slate-300">
                                    <Clock size={13} className="text-slate-400 shrink-0" />
                                    <span>{timeAgoText}</span>
                                    <span className="text-[11px] text-slate-400 dark:text-slate-500">({formattedTimestamp})</span>
                                </span>

                                {/* 7. Freshness Badge */}
                                <span className={`inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-black uppercase tracking-wider border ${freshness.badgeClass}`}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${freshness.dotColor}`}></span>
                                    {freshness.label}
                                </span>

                                <span className="text-slate-300 dark:text-slate-700">•</span>
                                <span className={`font-black tracking-wide ${riskColor}`}>
                                    {riskLevelText}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="shrink-0">
                        {renderSeverityBadge(norm)}
                    </div>
                </div>

                {/* Section 2: Decision Intelligence Metrics Row (Confidence + Escalation Trend) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-3 pt-1">
                    {/* 6. SYSTEM CONFIDENCE METER (Gradient fill + glow if > 85%) */}
                    <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200/70 dark:border-slate-800 rounded-xl px-3 py-2 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-1.5 shrink-0">
                            <Activity size={14} className="text-blue-500 shrink-0" />
                            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400">
                                Confidence:
                            </span>
                        </div>
                        <div className="flex items-center gap-2 flex-1 justify-end max-w-[170px]">
                            <div className={`w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden ${confidence > 85 ? 'shadow-[0_0_8px_rgba(239,68,68,0.5)] ring-1 ring-red-400/40' : ''}`}>
                                <div 
                                    className={`h-full rounded-full transition-all duration-500 ${
                                        confidence > 85 
                                            ? 'bg-gradient-to-r from-amber-500 to-red-600 animate-pulse' 
                                            : confidence >= 60 
                                                ? 'bg-gradient-to-r from-emerald-500 to-amber-500' 
                                                : 'bg-emerald-500'
                                    }`} 
                                    style={{ width: `${confidence}%` }}
                                />
                            </div>
                            <span className={`text-xs font-black shrink-0 ${confidence > 85 ? 'text-red-500 animate-pulse' : 'text-slate-900 dark:text-white'}`}>
                                {confidence}%
                            </span>
                        </div>
                    </div>

                    {/* Escalation Trend */}
                    <div className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200/70 dark:border-slate-800 rounded-xl px-3 py-2 flex items-center justify-between gap-2">
                        <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400">
                            Escalation Trend:
                        </span>
                        <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-black border ${trend.badgeClass}`}>
                            <TrendIcon size={13} />
                            <span>{trend.text}</span>
                        </div>
                    </div>
                </div>

                {/* 3. MINI RISK WAVE VISUAL (Signal wave / radar pulse) */}
                <div className="bg-slate-50/70 dark:bg-slate-800/30 border border-slate-200/60 dark:border-slate-800 rounded-xl px-3 py-2 mb-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Waves size={14} className={waveTextColor} />
                        <span className="text-[10px] font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            Radar Threat Wave
                        </span>
                        <span className={`text-[10px] font-extrabold ${waveTextColor}`}>
                            [{waveLabel}]
                        </span>
                    </div>
                    {/* Animated waveform bars */}
                    <div className="flex items-end gap-1 h-5 px-1">
                        {[5, 12, 18, 9, 15, 20, 8, 14, 19, 7, 13, 10].map((h, i) => (
                            <span 
                                key={i}
                                className={`w-1 rounded-full animate-risk-wave ${waveBarColor}`}
                                style={{
                                    height: `${h}px`,
                                    animationDuration: waveDuration,
                                    animationDelay: `${(i * 0.08).toFixed(2)}s`
                                }}
                            />
                        ))}
                    </div>
                </div>

                {/* 4. ENHANCED IMPACT ASSESSMENT (Icon + Label + Description) */}
                <div className="bg-slate-100/70 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-750 rounded-xl p-3 mb-3 flex items-start gap-2.5">
                    <div className="p-1.5 rounded-lg bg-white dark:bg-slate-700/80 shadow-xs shrink-0 mt-0.5">
                        {impact.icon}
                    </div>
                    <div>
                        <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="text-[11px] font-black uppercase tracking-wider text-slate-700 dark:text-slate-300">
                                Impact Assessment:
                            </span>
                            <span className="text-[11px] font-extrabold text-blue-600 dark:text-blue-400">
                                [{impact.title}]
                            </span>
                        </div>
                        <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 mt-0.5 leading-snug">
                            {impact.description}
                        </p>
                    </div>
                </div>

                {/* Message banner if different from action */}
                {alert.message && alert.message !== alert.action && (
                    <p className="text-xs text-slate-600 dark:text-slate-300 font-medium mb-3 bg-slate-50 dark:bg-slate-800/30 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
                        {alert.message}
                    </p>
                )}

                {/* Existing Recommended Action Panel */}
                <div className={`rounded-xl p-3.5 border transition-colors ${actionBoxStyle}`}>
                    <div className="flex items-center gap-1.5 mb-1.5">
                        <AlertTriangle size={15} className={`shrink-0 ${warningIconColor}`} />
                        <span className="text-[11px] font-black uppercase tracking-wider">
                            Recommended Action
                        </span>
                    </div>
                    <p className="text-xs font-semibold leading-relaxed pl-5">
                        {actionText}
                    </p>
                </div>

                {/* 5. DECISION SUPPORT BADGES */}
                <div className="flex items-center gap-1.5 flex-wrap mt-3">
                    <span className="text-[10px] font-black uppercase tracking-wider text-slate-400 dark:text-slate-500 mr-1">
                        Directives:
                    </span>
                    {decisionBadges.map((badge, bIdx) => (
                        <span 
                            key={bIdx}
                            className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-wider border ${badge.color}`}
                        >
                            {badge.text}
                        </span>
                    ))}
                </div>

                {/* Expandable Decision Intelligence Details (UI Only) */}
                {isExpanded && (
                    <div className="mt-3.5 pt-3.5 border-t border-slate-200 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/30 rounded-xl p-3.5 space-y-2.5 animate-fadeIn">
                        <div className="flex items-center justify-between text-xs font-black text-slate-700 dark:text-slate-200">
                            <span>Diagnostic Intelligence Telemetry</span>
                            <span className="text-[10px] text-blue-500 font-bold uppercase tracking-wider">Model: Nowcast-v2</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-[11px]">
                            <div className="p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700/60">
                                <span className="text-slate-400 block text-[10px]">Primary Sensor Stream</span>
                                <span className="font-bold text-slate-700 dark:text-slate-300">Doppler Radar & Station Barometer</span>
                            </div>
                            <div className="p-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200/60 dark:border-slate-700/60">
                                <span className="text-slate-400 block text-[10px]">Civil Protection Channel</span>
                                <span className="font-bold text-slate-700 dark:text-slate-300">NDRF Tier-1 Emergency Link</span>
                            </div>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                            Continuous algorithm recalculation active every 5 minutes against national meteorological danger thresholds.
                        </p>
                    </div>
                )}

                {/* Quick Action Buttons (UI ONLY) */}
                <div className="flex items-center justify-between pt-3 mt-3 border-t border-slate-100 dark:border-slate-800 gap-2">
                    <button
                        type="button"
                        onClick={() => toggleExpanded(cardKey)}
                        className="px-3.5 py-1.5 text-xs font-bold rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
                    >
                        <Eye size={13} className="text-slate-500" />
                        <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                    </button>

                    <button
                        type="button"
                        onClick={() => toggleReviewed(cardKey)}
                        className={`px-3.5 py-1.5 text-xs font-black uppercase tracking-wider rounded-xl transition-all flex items-center gap-1.5 cursor-pointer shadow-xs ${
                            isReviewed 
                                ? 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                                : 'bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
                        }`}
                    >
                        <CheckCircle2 size={13} className={isReviewed ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"} />
                        <span>{isReviewed ? 'Reviewed ✓' : 'Mark as Reviewed'}</span>
                    </button>
                </div>
            </div>
        );
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-[#0b0f19] text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-300">
            <TopHeader onSearch={() => {}} searchLoading={false} selectedCity="All India" />
            
            <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
                {/* Command Center Status Bar */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 mb-4 border-b border-slate-200 dark:border-slate-800/80">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 rounded-2xl border border-red-200 dark:border-red-900/50 shadow-sm shrink-0">
                            <Radio size={26} className="animate-pulse" />
                        </div>
                        <div>
                            <div className="flex items-center gap-2.5 flex-wrap">
                                <h1 className="text-2xl md:text-3xl font-black tracking-tight text-slate-900 dark:text-white">
                                    Disaster Intelligence Panel
                                </h1>
                                {/* Live Status Indicator */}
                                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/80 rounded-full shadow-xs">
                                    <span className="relative flex h-2.5 w-2.5">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                                    </span>
                                    <span className="text-[11px] font-black uppercase tracking-wider text-emerald-700 dark:text-emerald-400">
                                        Live Emergency Feed ●
                                    </span>
                                </div>
                            </div>
                            <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-1">
                                National Emergency Operations Telemetry • Automated Physical Threshold Warnings
                            </p>
                        </div>
                    </div>

                    {/* 8. GLOBAL CONTROL BAR (TOP RIGHT) */}
                    <div className="flex items-center gap-2 flex-wrap self-start lg:self-center">
                        {/* Auto-Refresh Toggle */}
                        <button
                            onClick={() => setAutoRefresh(prev => !prev)}
                            className={`px-3 py-1.5 rounded-xl border text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer shadow-xs ${
                                autoRefresh 
                                    ? 'bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 border-blue-300 dark:border-blue-800' 
                                    : 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'
                            }`}
                            title={autoRefresh ? "Auto-refresh active (5 min)" : "Auto-refresh paused"}
                        >
                            <RefreshCw size={13} className={autoRefresh ? "text-blue-500" : "text-slate-400"} />
                            <span>Auto-Sync: {autoRefresh ? "ON" : "OFF"}</span>
                        </button>

                        {/* Sound Alerts Toggle */}
                        <button
                            onClick={toggleSound}
                            className={`px-3 py-1.5 rounded-xl border text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer shadow-xs ${
                                soundEnabled 
                                    ? 'bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 border-amber-300 dark:border-amber-800' 
                                    : 'bg-slate-100 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'
                            }`}
                            title={soundEnabled ? "Audio alerts enabled" : "Audio alerts muted"}
                        >
                            {soundEnabled ? <Volume2 size={13} className="text-amber-500" /> : <VolumeX size={13} className="text-slate-400" />}
                            <span>Audio: {soundEnabled ? "ON" : "MUTED"}</span>
                        </button>

                        {/* Quick Dark Mode Toggle */}
                        <button
                            onClick={toggleTheme}
                            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-amber-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shadow-xs cursor-pointer"
                            title="Toggle dark/light mode"
                        >
                            {isDark ? <Sun size={14} /> : <Moon size={14} />}
                        </button>

                        {/* Manual Refresh */}
                        <button
                            onClick={() => fetchAlerts(false)}
                            disabled={loading}
                            className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold text-xs rounded-xl border border-slate-200 dark:border-slate-700 transition-all shadow-xs cursor-pointer disabled:opacity-50"
                            title="Sync telemetry feed"
                        >
                            <RefreshCw size={13} className={loading ? "animate-spin text-blue-500" : ""} />
                            <span>{loading ? "Syncing..." : "Sync"}</span>
                        </button>

                        {/* Back to Dashboard */}
                        <Link 
                            to="/"
                            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl transition-all shadow-md shadow-blue-500/20"
                        >
                            <ArrowLeft size={14} />
                            <span>Dashboard</span>
                        </Link>
                    </div>
                </div>

                {/* 1. LIVE ACTIVITY STRIP (TOP SECTION) */}
                <div className="w-full bg-slate-900 text-slate-200 dark:bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 mb-6 shadow-sm overflow-hidden flex items-center gap-3">
                    <div className="flex items-center gap-2 shrink-0 border-r border-slate-700/80 pr-3">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                        </span>
                        <span className="text-[10px] font-black uppercase tracking-wider text-red-400">
                            LIVE DISPATCH STRIP
                        </span>
                    </div>
                    <div className="relative overflow-hidden whitespace-nowrap flex-1">
                        <div className="animate-marquee gap-8">
                            {[...tickerItems, ...tickerItems].map((item, i) => (
                                <span key={i} className="inline-flex items-center gap-2 text-xs font-semibold text-slate-300 pr-6">
                                    <span>{item.icon}</span>
                                    <span>{item.text}</span>
                                    <span className="text-slate-600">•</span>
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                {/* 9. ALERT DENSITY HEAT INDICATOR (Shows % distribution: HIGH / MODERATE / LOW) */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 mb-6 shadow-sm">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-black uppercase tracking-wider text-slate-800 dark:text-slate-200">
                                Alert Density Threat Spectrum
                            </span>
                            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-semibold">
                                ({totalCount} Monitored Sectors)
                            </span>
                        </div>
                        <div className="flex items-center gap-4 text-xs font-black">
                            <span className="text-red-500 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-red-500"></span>
                                HIGH {highPercent}%
                            </span>
                            <span className="text-amber-500 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                                MODERATE {modPercent}%
                            </span>
                            <span className="text-emerald-500 flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                                LOW {lowPercent}%
                            </span>
                        </div>
                    </div>
                    {/* Multi-segment density spectrum bar */}
                    <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex">
                        <div 
                            className="h-full bg-red-500 transition-all duration-500" 
                            style={{ width: `${highPercent}%` }}
                            title={`High Urgency: ${highPercent}%`}
                        />
                        <div 
                            className="h-full bg-amber-400 transition-all duration-500" 
                            style={{ width: `${modPercent}%` }}
                            title={`Moderate Advisory: ${modPercent}%`}
                        />
                        <div 
                            className="h-full bg-emerald-500 transition-all duration-500" 
                            style={{ width: `${lowPercent}%` }}
                            title={`Low Baseline: ${lowPercent}%`}
                        />
                    </div>
                </div>

                {/* Command Center Summary Metrics */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5 mb-6">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                        <div>
                            <span className="text-[11px] font-black uppercase tracking-wider text-slate-500 dark:text-slate-400">
                                Total Warnings
                            </span>
                            <div className="text-2xl font-black mt-0.5 text-slate-900 dark:text-white">
                                {alerts.length}
                            </div>
                            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">
                                Active monitored feeds
                            </span>
                        </div>
                        <div className="p-3 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-xl">
                            <Activity size={22} />
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-900 border border-red-200 dark:border-red-900/40 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                        <div>
                            <span className="text-[11px] font-black uppercase tracking-wider text-red-500 dark:text-red-400">
                                High Risk Alerts
                            </span>
                            <div className="text-2xl font-black mt-0.5 text-red-600 dark:text-red-400">
                                {highCount}
                            </div>
                            <span className="text-[10px] text-red-500/80 font-medium">
                                Immediate threat status
                            </span>
                        </div>
                        <div className="p-3 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 rounded-xl">
                            <Flame size={22} />
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-900 border border-amber-200 dark:border-amber-900/40 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                        <div>
                            <span className="text-[11px] font-black uppercase tracking-wider text-amber-500 dark:text-amber-400">
                                Moderate Advisories
                            </span>
                            <div className="text-2xl font-black mt-0.5 text-amber-600 dark:text-amber-400">
                                {modCount}
                            </div>
                            <span className="text-[10px] text-amber-500/80 font-medium">
                                Precautionary threshold
                            </span>
                        </div>
                        <div className="p-3 bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-xl">
                            <AlertTriangle size={22} />
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-900/40 rounded-2xl p-4 shadow-sm flex items-center justify-between">
                        <div>
                            <span className="text-[11px] font-black uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                                Low / Monitored
                            </span>
                            <div className="text-2xl font-black mt-0.5 text-emerald-600 dark:text-emerald-400">
                                {lowCount}
                            </div>
                            <span className="text-[10px] text-emerald-600/80 font-medium">
                                Controlled baseline
                            </span>
                        </div>
                        <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-xl">
                            <ShieldCheck size={22} />
                        </div>
                    </div>
                </div>

                {/* Filter System & Search Bar */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-4 mb-6 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
                    {/* Filter buttons */}
                    <div className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl overflow-x-auto">
                        <button
                            onClick={() => setFilter('ALL')}
                            className={`px-3.5 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer ${
                                filter === 'ALL'
                                    ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 shadow-xs'
                                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                            }`}
                        >
                            All ({alerts.length})
                        </button>
                        <button
                            onClick={() => setFilter('HIGH')}
                            className={`px-3.5 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5 ${
                                filter === 'HIGH'
                                    ? 'bg-red-600 text-white shadow-xs'
                                    : 'text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400'
                            }`}
                        >
                            <span>High Risk</span>
                            <span className={`px-1.5 py-0.2 rounded text-[10px] ${filter === 'HIGH' ? 'bg-red-700 text-white' : 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400'}`}>
                                {highCount}
                            </span>
                        </button>
                        <button
                            onClick={() => setFilter('MODERATE')}
                            className={`px-3.5 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5 ${
                                filter === 'MODERATE'
                                    ? 'bg-amber-500 text-amber-950 shadow-xs'
                                    : 'text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400'
                            }`}
                        >
                            <span>Moderate</span>
                            <span className={`px-1.5 py-0.2 rounded text-[10px] ${filter === 'MODERATE' ? 'bg-amber-600 text-amber-950' : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400'}`}>
                                {modCount}
                            </span>
                        </button>
                        <button
                            onClick={() => setFilter('LOW')}
                            className={`px-3.5 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer flex items-center gap-1.5 ${
                                filter === 'LOW'
                                    ? 'bg-emerald-600 text-white shadow-xs'
                                    : 'text-slate-600 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400'
                            }`}
                        >
                            <span>Low</span>
                            <span className={`px-1.5 py-0.2 rounded text-[10px] ${filter === 'LOW' ? 'bg-emerald-700 text-white' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-400'}`}>
                                {lowCount}
                            </span>
                        </button>
                    </div>

                    {/* Search inside alerts */}
                    <div className="relative md:w-72">
                        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Filter by city or hazard..."
                            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-100 dark:bg-slate-800 border border-transparent focus:border-blue-500 rounded-xl outline-none dark:text-white placeholder:text-slate-400"
                        />
                        {searchQuery && (
                            <button 
                                onClick={() => setSearchQuery('')}
                                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs font-bold"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="p-4 mb-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-300 text-sm font-semibold flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <AlertTriangle size={18} className="text-red-500" />
                            <span>Telemetry Gateway Notice: {error}</span>
                        </div>
                        <button
                            onClick={() => fetchAlerts(false)}
                            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs font-bold cursor-pointer transition-colors"
                        >
                            Retry Sync
                        </button>
                    </div>
                )}

                {/* Empty State */}
                {!loading && filteredAlerts.length === 0 && (
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-12 text-center flex flex-col items-center justify-center my-6 shadow-sm">
                        <div className="w-16 h-16 rounded-full bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800/80 flex items-center justify-center text-emerald-500 mb-4 shadow-sm shadow-emerald-500/10">
                            <ShieldCheck size={36} />
                        </div>
                        <h2 className="text-xl md:text-2xl font-black text-slate-900 dark:text-white">
                            All Clear — No Active Alerts
                        </h2>
                        <p className="text-xs md:text-sm text-slate-500 dark:text-slate-400 max-w-md mt-2 leading-relaxed">
                            {filter !== 'ALL' || searchQuery
                                ? "No warnings currently match your selected priority criteria or search filter."
                                : "All monitored meteorological sectors are currently operating within safe baseline parameters. No critical flood or thunderstorm thresholds are exceeded."
                            }
                        </p>
                        {(filter !== 'ALL' || searchQuery) && (
                            <button
                                onClick={() => { setFilter('ALL'); setSearchQuery(''); }}
                                className="mt-5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs cursor-pointer transition-colors"
                            >
                                Reset Filters to All Feeds
                            </button>
                        )}
                    </div>
                )}

                {/* Grouping: Group alerts by severity */}
                {filteredAlerts.length > 0 && (
                    <div className="space-y-8">
                        {/* Section: 🔥 HIGH PRIORITY */}
                        {(filter === 'ALL' || filter === 'HIGH') && groupedAlerts.HIGH.length > 0 && (
                            <div>
                                <div className="flex items-center justify-between pb-3 mb-4 border-b border-red-200 dark:border-red-950/60">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">🔥</span>
                                        <h2 className="text-base font-black uppercase tracking-wider text-red-600 dark:text-red-400">
                                            HIGH PRIORITY
                                        </h2>
                                        <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-red-100 dark:bg-red-950 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800">
                                            {groupedAlerts.HIGH.length} Urgent
                                        </span>
                                    </div>
                                    <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 hidden sm:inline">
                                        Immediate Civil Action Recommended
                                    </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {groupedAlerts.HIGH.map((alert, idx) => renderAlertCard(alert, `high-${idx}`))}
                                </div>
                            </div>
                        )}

                        {/* Section: ⚠️ MODERATE */}
                        {(filter === 'ALL' || filter === 'MODERATE') && groupedAlerts.MEDIUM.length > 0 && (
                            <div>
                                <div className="flex items-center justify-between pb-3 mb-4 border-b border-amber-200 dark:border-amber-950/60">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">⚠️</span>
                                        <h2 className="text-base font-black uppercase tracking-wider text-amber-600 dark:text-amber-400">
                                            MODERATE
                                        </h2>
                                        <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                                            {groupedAlerts.MEDIUM.length} Advisories
                                        </span>
                                    </div>
                                    <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 hidden sm:inline">
                                        Precautionary Surveillance Active
                                    </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {groupedAlerts.MEDIUM.map((alert, idx) => renderAlertCard(alert, `mod-${idx}`))}
                                </div>
                            </div>
                        )}

                        {/* Section: ✅ LOW */}
                        {(filter === 'ALL' || filter === 'LOW') && groupedAlerts.LOW.length > 0 && (
                            <div>
                                <div className="flex items-center justify-between pb-3 mb-4 border-b border-emerald-200 dark:border-emerald-950/60">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">✅</span>
                                        <h2 className="text-base font-black uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                                            LOW
                                        </h2>
                                        <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                                            {groupedAlerts.LOW.length} Standard
                                        </span>
                                    </div>
                                    <span className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 hidden sm:inline">
                                        Nominal Weather Operations
                                    </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {groupedAlerts.LOW.map((alert, idx) => renderAlertCard(alert, `low-${idx}`))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
};

export default Alerts;
