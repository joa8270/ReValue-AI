import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font, Svg, Path, Circle, Rect, Defs, LinearGradient, Stop, G, Line } from '@react-pdf/renderer';

// 註冊字體：使用 Noto Sans TC (繁體中文)
// 請確保 public/fonts/SourceHanSansTC-Regular.otf 存在
Font.register({
    family: "Noto Sans TC",
    src: "/fonts/SourceHanSansTC-Regular.otf"
});

const styles = StyleSheet.create({
    page: {
        flexDirection: 'column',
        backgroundColor: '#0f172a', // Slate 900
        color: '#ffffff',
        fontFamily: 'Noto Sans TC',
        padding: 0, // Full bleed
    },
    // Cover Page Styles
    coverContainer: {
        height: '100%',
        padding: 40,
        justifyContent: 'space-between',
        position: 'relative',
    },
    coverBackground: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        opacity: 0.1,
        zIndex: -1,
    },
    coverHeader: {
        marginTop: 40,
    },
    brandTitle: {
        fontSize: 14,
        letterSpacing: 4,
        color: '#a855f7', // Purple 500
        marginBottom: 10,
        textTransform: 'uppercase',
        fontWeight: 'bold',
    },
    reportTitle: {
        fontSize: 48,
        fontWeight: 'black', // Heavy
        color: '#ffffff',
        lineHeight: 1.1,
        marginBottom: 20,
    },
    reportSubtitle: {
        fontSize: 18,
        color: '#94a3b8', // Slate 400
        maxWidth: '80%',
    },
    coverFooter: {
        borderTopWidth: 1,
        borderTopColor: '#334155',
        paddingTop: 20,
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    footerText: {
        fontSize: 10,
        color: '#64748b',
    },
    // Chart Section
    chartSection: {
        marginVertical: 30,
        backgroundColor: '#1e293b',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
    },
    // Content Page Styles
    contentContainer: {
        padding: 40, // Increased from 30
        paddingTop: 40,
    },
    sectionTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#22d3ee', // Cyan 400
        marginBottom: 15,
        textTransform: 'uppercase',
        letterSpacing: 1,
        borderBottomWidth: 1,
        borderBottomColor: '#334155',
        paddingBottom: 8,
        marginTop: 10,
    },
    // Grid System
    row: {
        flexDirection: 'row',
        marginBottom: 10,
        gap: 10,
        flexWrap: 'wrap', // added wrap safety
    },
    col: {
        flex: 1,
    },
    card: {
        backgroundColor: '#1e293b', // Slate 800
        borderRadius: 8,
        padding: 12,
        marginBottom: 8,
        overflow: 'hidden', // prevent spill
    },
    // Persona Card
    personaCard: {
        backgroundColor: '#1e293b',
        borderRadius: 8,
        padding: 12,
        marginBottom: 10,
        borderLeftWidth: 3,
        // width handled in render
    },
    personaHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 6,
        alignItems: 'center',
    },
    personaName: {
        fontSize: 11,
        fontWeight: 'bold',
        color: '#f1f5f9',
        maxWidth: 80, // Limit name width
        maxLines: 1,
    },
    personaMeta: {
        fontSize: 9,
        color: '#94a3b8',
    },
    personaText: {
        fontSize: 10,
        lineHeight: 1.5,
        color: '#cbd5e1',
        maxWidth: '100%',
    },
    badge: {
        fontSize: 8,
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 4,
        color: '#ffffff',
    },
    positiveBadge: { backgroundColor: '#10b981', color: '#fff' },
    negativeBadge: { backgroundColor: '#ef4444', color: '#fff' },
    neutralBadge: { backgroundColor: '#64748b', color: '#fff' },

    // Strategic Section
    strategyBox: {
        backgroundColor: 'rgba(127, 29, 29, 0.2)', // Red/Dark tint
        borderWidth: 1,
        borderColor: '#a855f7',
        borderRadius: 8,
        padding: 15,
        marginVertical: 10,
    },
    strategyText: {
        fontSize: 10,
        lineHeight: 1.6,
        color: '#e2e8f0',
        marginBottom: 8,
        textAlign: 'justify', // better alignment
    },

    // Header on standard pages
    pageHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#334155',
        paddingBottom: 10,
    },
    pageTitle: {
        fontSize: 18,
        color: '#a855f7',
        fontWeight: 'bold',
    },
    pageNumber: {
        position: 'absolute',
        bottom: 20,
        right: 30,
        fontSize: 9,
        color: '#64748b',
    }
});

// --- Chart Components ---

const ScoreGauge = ({ score }: { score: number }) => {
    // Simple gauge visualization
    // Arc path is complex in pure SVG path without d3-shape, so we use a simplified approach:
    // A background gray arc and a foreground colored arc
    // Since calculating paths manually is verbose, we'll use a simple progress bar fan or just a clear numeric display with a ring.

    const radius = 60;
    const strokeWidth = 12;
    const center = 100;

    // Calculate color based on score
    const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';

    // Simple Circle approach for stability in react-pdf
    return (
        <View style={{ alignItems: 'center', justifyContent: 'center', height: 140 }}>
            <Svg height="140" width="200" viewBox="0 0 200 140">
                <Defs>
                    <LinearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
                        <Stop offset="0" stopColor="#a855f7" stopOpacity="1" />
                        <Stop offset="1" stopColor={color} stopOpacity="1" />
                    </LinearGradient>
                </Defs>

                {/* Background Arc Effect (Simplified as multiple opacity circles or just a container) */}
                <Circle cx="100" cy="70" r={radius} stroke="#334155" strokeWidth={strokeWidth} fillOpacity="0" />

                {/* We can't easily do a partial arc without Path 'd'. 
                    Let's use a simpler visual: A glowing ring with the score in middle.
                */}
                <Circle cx="100" cy="70" r={radius} stroke="url('#grad')" strokeWidth={strokeWidth} fillOpacity="0" strokeDasharray={`${score * 3.7}, 1000`} strokeLinecap="round" transform="rotate(-90 100 70)" />

                <Text x="100" y="75" textAnchor="middle" style={{ fontSize: 36, fill: '#ffffff', fontWeight: 'black', fontFamily: 'Noto Sans TC' }}>
                    {score}
                </Text>
                <Text x="100" y="95" textAnchor="middle" style={{ fontSize: 10, fill: '#94a3b8', fontFamily: 'Noto Sans TC' }}>
                    市場購買意向
                </Text>
            </Svg>
        </View>
    );
};

const SentimentBar = ({ comments }: { comments: any[] }) => {
    const total = Math.max(comments.length, 1);
    const pos = comments.filter(c => c.sentiment === 'positive').length;
    const neg = comments.filter(c => c.sentiment === 'negative').length;
    const neu = total - pos - neg;

    const wPos = (pos / total) * 100;
    const wNeu = (neu / total) * 100;
    const wNeg = (neg / total) * 100;

    return (
        <View style={{ marginTop: 10 }}>
            <Text style={{ fontSize: 9, color: '#94a3b8', marginBottom: 4 }}>輿論情緒分佈</Text>
            <View style={{ flexDirection: 'row', height: 8, borderRadius: 4, overflow: 'hidden', backgroundColor: '#334155' }}>
                {wPos > 0 && <View style={{ width: `${wPos}%`, backgroundColor: '#10b981' }} />}
                {wNeu > 0 && <View style={{ width: `${wNeu}%`, backgroundColor: '#64748b' }} />}
                {wNeg > 0 && <View style={{ width: `${wNeg}%`, backgroundColor: '#ef4444' }} />}
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 }}>
                <Text style={{ fontSize: 8, color: '#10b981' }}>正面 {Math.round(wPos)}%</Text>
                <Text style={{ fontSize: 8, color: '#94a3b8' }}>中立 {Math.round(wNeu)}%</Text>
                <Text style={{ fontSize: 8, color: '#ef4444' }}>負面 {Math.round(wNeg)}%</Text>
            </View>
        </View>
    );
};

const BaziChart = ({ distribution }: { distribution: any }) => {
    const data = [
        { label: '木', color: '#10b981', value: distribution?.Wood || 20 },
        { label: '火', color: '#f97316', value: distribution?.Fire || 20 },
        { label: '土', color: '#eab308', value: distribution?.Earth || 20 },
        { label: '金', color: '#cbd5e1', value: distribution?.Metal || 20 },
        { label: '水', color: '#06b6d4', value: distribution?.Water || 20 },
    ];

    const maxVal = Math.max(...data.map(d => d.value), 1);

    return (
        <View style={{ marginTop: 10 }}>
            <Text style={{ fontSize: 9, color: '#94a3b8', marginBottom: 6 }}>五行受眾分佈</Text>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', height: 60, paddingBottom: 15, borderBottomWidth: 1, borderBottomColor: '#334155' }}>
                {data.map((d, i) => (
                    <View key={i} style={{ alignItems: 'center', flex: 1 }}>
                        {/* Bar */}
                        <View style={{
                            width: 12,
                            height: `${(d.value / maxVal) * 100}%`,
                            backgroundColor: d.color,
                            borderRadius: 2,
                            minHeight: 2
                        }} />
                        <Text style={{ fontSize: 8, color: '#94a3b8', marginTop: 4 }}>{d.label}</Text>
                    </View>
                ))}
            </View>
        </View>
    );
}

// --- Main Report ---

interface SimulationReportPDFProps {
    data: any;
}

const SimulationReportPDF: React.FC<SimulationReportPDFProps> = ({ data }) => {
    const score = data.score || 0;
    // Format summary paragraphs
    const summaryStr = data.summary || "分析運算中...";
    const summaryParagraphs = summaryStr.split('\n').filter((p: string) => p.trim().length > 0);
    const comments = data.arena_comments || [];

    const baziDist = data.simulation_metadata?.bazi_distribution || { Fire: 20, Wood: 20, Earth: 20, Metal: 20, Water: 20 };

    return (
        <Document>
            {/* === PAGE 1: COVER & EXECUTIVE SUMMARY === */}
            <Page size="A4" style={styles.page}>
                <View style={styles.coverContainer}>
                    {/* Header */}
                    <View style={styles.coverHeader}>
                        <Text style={styles.brandTitle}>MIRRA INTELLIGENCE</Text>
                        <Text style={styles.reportTitle}>鏡界預演報告</Text>
                        <Text style={styles.reportSubtitle}>
                            針對 {data.simulation_metadata?.product_category ? data.simulation_metadata.product_category.toUpperCase() : 'PRODUCT'} 之深度市場推演
                        </Text>
                    </View>

                    {/* Central Visual: Score */}
                    <View style={styles.chartSection}>
                        <ScoreGauge score={score} />
                        <View style={{ width: '100%', flexDirection: 'row', gap: 20, marginTop: 20 }}>
                            <View style={{ flex: 1 }}>
                                <SentimentBar comments={comments} />
                            </View>
                            <View style={{ flex: 1 }}>
                                <BaziChart distribution={baziDist} />
                            </View>
                        </View>
                    </View>

                    {/* Key Metrics Grid */}
                    <View style={styles.row}>
                        <View style={[styles.card, styles.col]}>
                            <Text style={{ fontSize: 8, color: '#94a3b8' }}>參與市民</Text>
                            <Text style={{ fontSize: 18, fontWeight: 'bold' }}>{data.genesis?.sample_size || 1000} 人</Text>
                        </View>
                        <View style={[styles.card, styles.col]}>
                            <Text style={{ fontSize: 8, color: '#94a3b8' }}>市場均價</Text>
                            <Text style={{ fontSize: 18, fontWeight: 'bold' }}>${data.market_prices?.avg_price || 'N/A'}</Text>
                        </View>
                        <View style={[styles.card, styles.col]}>
                            <Text style={{ fontSize: 8, color: '#94a3b8' }}>轉換潛力</Text>
                            <Text style={{ fontSize: 18, fontWeight: 'bold', color: score >= 80 ? '#10b981' : '#f59e0b' }}>
                                {score >= 80 ? 'HIGH' : score >= 60 ? 'MED' : 'LOW'}
                            </Text>
                        </View>
                    </View>

                    {/* Footer */}
                    <View style={styles.coverFooter}>
                        <Text style={styles.footerText}>REPORT ID: {data.id?.slice(0, 8) || 'SIM-PREVIEW'}</Text>
                        <Text style={styles.footerText}>{new Date().toLocaleDateString('zh-TW')} | MIRRA AI ENGINE V2</Text>
                    </View>
                </View>
            </Page>

            {/* === PAGE 2: STRATEGIC ANALYSIS === */}
            <Page size="A4" style={[styles.page, styles.contentContainer]}>
                <View style={styles.pageHeader}>
                    <Text style={styles.pageTitle}>戰略神諭 STRATEGIC ORACLE</Text>
                    <Text style={{ color: '#94a3b8', fontSize: 10 }}>深度解析</Text>
                </View>

                {/* Main Analysis Content */}
                <View style={{ marginBottom: 20 }}>
                    {/* Assume Summary follows structure: [解析]... [優化]... [戰略]... 
                         We can try to parse it or just dump it nicely. 
                     */}
                    {summaryParagraphs.map((para: string, idx: number) => {
                        const isStrategic = para.includes("[戰略]") || para.includes("戰略建議");
                        return (
                            <View key={idx} style={isStrategic ? styles.strategyBox : { marginBottom: 12 }}>
                                {isStrategic && <Text style={{ fontSize: 10, color: '#a855f7', fontWeight: 'bold', marginBottom: 4 }}>CORE STRATEGY</Text>}
                                <Text style={styles.strategyText}>{para}</Text>
                            </View>
                        )
                    })}
                </View>

                {/* Action Plan / Suggestions */}
                {data.suggestions && data.suggestions.length > 0 && (
                    <View>
                        <Text style={styles.sectionTitle}>執行戰術 ACTION PLAN</Text>
                        {data.suggestions.slice(0, 3).map((s: any, i: number) => (
                            <View key={i} style={styles.card}>
                                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                                    <Text style={{ fontSize: 11, fontWeight: 'bold', color: '#22d3ee' }}>👉 {s.target || '戰術目標'}</Text>
                                    <Text style={{ fontSize: 9, color: '#10b981' }}>{s.score_improvement}</Text>
                                </View>
                                <Text style={[styles.personaText, { marginBottom: 6 }]}>{s.advice}</Text>
                                {s.execution_plan && (
                                    <View style={{ paddingLeft: 8, borderLeftWidth: 1, borderLeftColor: '#475569', marginTop: 4 }}>
                                        {s.execution_plan.slice(0, 3).map((step: string, k: number) => (
                                            <Text key={k} style={{ fontSize: 9, color: '#94a3b8', marginBottom: 2 }}>• {step}</Text>
                                        ))}
                                    </View>
                                )}
                            </View>
                        ))}
                    </View>
                )}

                <Text style={styles.pageNumber} render={({ pageNumber, totalPages }) => `${pageNumber} / ${totalPages}`} fixed />
            </Page>

            {/* === PAGE 3: VOX POPULI (CITIZEN VOICES) === */}
            <Page size="A4" style={[styles.page, styles.contentContainer]}>
                <View style={styles.pageHeader}>
                    <Text style={styles.pageTitle}>輿論競技場 VOX POPULI</Text>
                    <Text style={{ color: '#94a3b8', fontSize: 10 }}>精選反饋</Text>
                </View>

                <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' }}>
                    {comments.slice(0, 8).map((comment: any, i: number) => {
                        const isPos = comment.sentiment === 'positive';
                        const isNeg = comment.sentiment === 'negative';
                        const color = isPos ? '#10b981' : isNeg ? '#ef4444' : '#64748b';
                        const borderColor = isPos ? '#10b981' : isNeg ? '#ef4444' : '#475569';

                        // Element Config
                        const elemMap: Record<string, string> = { "Fire": "火", "Water": "水", "Metal": "金", "Wood": "木", "Earth": "土" };
                        const elem = elemMap[comment.persona?.element] || "命";

                        return (
                            <View key={i} style={[styles.personaCard, { width: '48%', borderLeftColor: borderColor }]}>
                                <View style={styles.personaHeader}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
                                        <View style={{ width: 16, height: 16, borderRadius: 8, backgroundColor: borderColor, alignItems: 'center', justifyContent: 'center' }}>
                                            <Text style={{ fontSize: 8 }}>{elem}</Text>
                                        </View>
                                        <Text style={styles.personaName}>{comment.persona?.name}</Text>
                                    </View>
                                    <Text style={[styles.badge, isPos ? styles.positiveBadge : isNeg ? styles.negativeBadge : styles.neutralBadge]}>
                                        {isPos ? 'POS' : isNeg ? 'NEG' : 'NEU'}
                                    </Text>
                                </View>
                                <Text style={{ fontSize: 8, color: '#64748b', marginBottom: 4 }}>
                                    {comment.persona?.age}歲 | {comment.persona?.occupation} | {comment.persona?.pattern || '格局未知'}
                                </Text>
                                <Text style={styles.personaText}>
                                    "{comment.text}"
                                </Text>
                            </View>
                        );
                    })}
                </View>

                <Text style={styles.pageNumber} render={({ pageNumber, totalPages }) => `${pageNumber} / ${totalPages}`} fixed />
            </Page>
        </Document>
    );
};

export default SimulationReportPDF;
