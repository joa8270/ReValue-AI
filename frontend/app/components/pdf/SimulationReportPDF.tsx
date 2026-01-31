import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font, Svg, Circle, Defs, LinearGradient, Stop } from '@react-pdf/renderer';

// 註冊字體：使用 Noto Sans TC (繁體中文)
Font.register({
    family: "Noto Sans TC",
    src: "/fonts/SourceHanSansTC-Regular.otf"
});

const styles = StyleSheet.create({
    page: {
        flexDirection: 'column',
        backgroundColor: '#0f172a',
        color: '#ffffff',
        fontFamily: 'Noto Sans TC',
        padding: 0,
    },
    // Cover Page Styles
    coverContainer: {
        height: '100%',
        padding: 40,
        justifyContent: 'space-between',
        position: 'relative',
    },
    coverHeader: {
        marginTop: 40,
    },
    brandTitle: {
        fontSize: 14,
        letterSpacing: 4,
        color: '#a855f7',
        marginBottom: 10,
        textTransform: 'uppercase',
        fontWeight: 'bold',
    },
    reportTitle: {
        fontSize: 42,
        fontWeight: 'bold',
        color: '#ffffff',
        marginBottom: 15,
    },
    productName: {
        fontSize: 20,
        color: '#22d3ee',
        marginBottom: 8,
        fontWeight: 'bold',
    },
    productMeta: {
        fontSize: 12,
        color: '#94a3b8',
        marginBottom: 4,
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
        marginVertical: 25,
        backgroundColor: '#1e293b',
        borderRadius: 12,
        padding: 20,
        alignItems: 'center',
    },
    // Content Page Styles
    contentContainer: {
        padding: 35,
        paddingTop: 35,
    },
    sectionTitle: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#22d3ee',
        marginBottom: 12,
        textTransform: 'uppercase',
        letterSpacing: 1,
        borderBottomWidth: 1,
        borderBottomColor: '#334155',
        paddingBottom: 6,
        marginTop: 8,
    },
    row: {
        flexDirection: 'row',
        marginBottom: 8,
        gap: 8,
    },
    col: {
        flex: 1,
    },
    card: {
        backgroundColor: '#1e293b',
        borderRadius: 8,
        padding: 10,
        marginBottom: 6,
    },
    // Persona Card
    personaCard: {
        backgroundColor: '#1e293b',
        borderRadius: 8,
        padding: 10,
        marginBottom: 8,
        borderLeftWidth: 3,
    },
    personaHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 4,
        alignItems: 'center',
    },
    personaName: {
        fontSize: 10,
        fontWeight: 'bold',
        color: '#f1f5f9',
    },
    personaText: {
        fontSize: 9,
        lineHeight: 1.5,
        color: '#cbd5e1',
    },
    badge: {
        fontSize: 7,
        paddingHorizontal: 5,
        paddingVertical: 2,
        borderRadius: 4,
        color: '#ffffff',
    },
    positiveBadge: { backgroundColor: '#10b981' },
    negativeBadge: { backgroundColor: '#ef4444' },
    neutralBadge: { backgroundColor: '#64748b' },
    // Strategic Section
    strategyBox: {
        backgroundColor: '#1e1b4b',
        borderWidth: 1,
        borderColor: '#a855f7',
        borderRadius: 8,
        padding: 12,
        marginVertical: 8,
    },
    strategyText: {
        fontSize: 10,
        lineHeight: 1.6,
        color: '#e2e8f0',
        marginBottom: 6,
    },
    // Header on standard pages
    pageHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 15,
        borderBottomWidth: 1,
        borderBottomColor: '#334155',
        paddingBottom: 8,
    },
    pageTitle: {
        fontSize: 16,
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
    const radius = 55;
    const strokeWidth = 10;
    const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';

    return (
        <View style={{ alignItems: 'center', justifyContent: 'center', height: 130 }}>
            <Svg height="130" width="180" viewBox="0 0 180 130">
                <Defs>
                    <LinearGradient id="grad" x1="0" y1="0" x2="1" y2="0">
                        <Stop offset="0" stopColor="#a855f7" stopOpacity="1" />
                        <Stop offset="1" stopColor={color} stopOpacity="1" />
                    </LinearGradient>
                </Defs>
                <Circle cx="90" cy="65" r={radius} stroke="#334155" strokeWidth={strokeWidth} fillOpacity="0" />
                <Circle cx="90" cy="65" r={radius} stroke="url('#grad')" strokeWidth={strokeWidth} fillOpacity="0"
                    strokeDasharray={`${score * 3.4}, 1000`} strokeLinecap="round" transform="rotate(-90 90 65)" />
                <Text x="90" y="70" textAnchor="middle" style={{ fontSize: 32, fill: '#ffffff', fontWeight: 'bold', fontFamily: 'Noto Sans TC' }}>
                    {score}
                </Text>
                <Text x="90" y="90" textAnchor="middle" style={{ fontSize: 9, fill: '#94a3b8', fontFamily: 'Noto Sans TC' }}>
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
        <View style={{ marginTop: 8 }}>
            <Text style={{ fontSize: 8, color: '#94a3b8', marginBottom: 4 }}>輿論情緒分佈</Text>
            <View style={{ flexDirection: 'row', height: 6, borderRadius: 3, overflow: 'hidden', backgroundColor: '#334155' }}>
                {wPos > 0 && <View style={{ width: `${wPos}%`, backgroundColor: '#10b981' }} />}
                {wNeu > 0 && <View style={{ width: `${wNeu}%`, backgroundColor: '#64748b' }} />}
                {wNeg > 0 && <View style={{ width: `${wNeg}%`, backgroundColor: '#ef4444' }} />}
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 3 }}>
                <Text style={{ fontSize: 7, color: '#10b981' }}>正面 {Math.round(wPos)}%</Text>
                <Text style={{ fontSize: 7, color: '#94a3b8' }}>中立 {Math.round(wNeu)}%</Text>
                <Text style={{ fontSize: 7, color: '#ef4444' }}>負面 {Math.round(wNeg)}%</Text>
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
        <View style={{ marginTop: 8 }}>
            <Text style={{ fontSize: 8, color: '#94a3b8', marginBottom: 4 }}>五行受眾分佈</Text>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', height: 50, paddingBottom: 12, borderBottomWidth: 1, borderBottomColor: '#334155' }}>
                {data.map((d, i) => (
                    <View key={i} style={{ alignItems: 'center', flex: 1 }}>
                        <View style={{
                            width: 10,
                            height: `${(d.value / maxVal) * 100}%`,
                            backgroundColor: d.color,
                            borderRadius: 2,
                            minHeight: 2
                        }} />
                        <Text style={{ fontSize: 7, color: '#94a3b8', marginTop: 3 }}>{d.label}</Text>
                    </View>
                ))}
            </View>
        </View>
    );
}

// --- Localized Helper ---
const getLocalizedValue = (val: any, lang: string): string => {
    if (!val) return "";
    if (typeof val === 'string') return val;
    if (typeof val === 'object') {
        const key = lang === 'zh-TW' ? 'TW' : lang === 'zh-CN' ? 'CN' : 'US';
        return val[key] || val['TW'] || ""; // Fallback to TW
    }
    return String(val);
};

// --- Main Report ---

interface SimulationReportPDFProps {
    data: any;
    language: string;
}

const SimulationReportPDF: React.FC<SimulationReportPDFProps> = ({ data, language }) => {
    const score = data.score || 0;
    const productName = data.product_name || data.productName || '未命名產品';
    const productPrice = data.price || data.market_prices?.avg_price || 'N/A';
    const productDescription = data.description || '';
    const summaryStr = data.summary || "分析運算中...";
    const summaryParagraphs = summaryStr.split('\n').filter((p: string) => p.trim().length > 0);
    const comments = data.arena_comments || [];
    const baziDist = data.simulation_metadata?.bazi_distribution || data.bazi_distribution || { Fire: 20, Wood: 20, Earth: 20, Metal: 20, Water: 20 };
    const suggestions = data.suggestions || [];

    return (
        <Document>
            {/* === PAGE 1: COVER & EXECUTIVE SUMMARY === */}
            <Page size="A4" style={styles.page}>
                <View style={styles.coverContainer}>
                    {/* Header */}
                    <View style={styles.coverHeader}>
                        <Text style={styles.brandTitle}>MIRRA INTELLIGENCE</Text>
                        <Text style={styles.reportTitle}>鏡界預演報告</Text>
                        <Text style={styles.productName}>{productName}</Text>
                        {productPrice !== 'N/A' && (
                            <Text style={styles.productMeta}>建議售價: NT$ {productPrice}</Text>
                        )}
                        {productDescription && (
                            <Text style={[styles.productMeta, { marginTop: 6, maxWidth: '90%' }]}>
                                {productDescription.slice(0, 150)}{productDescription.length > 150 ? '...' : ''}
                            </Text>
                        )}
                    </View>

                    {/* Central Visual: Score */}
                    <View style={styles.chartSection}>
                        <ScoreGauge score={score} />
                        <View style={{ width: '100%', flexDirection: 'row', gap: 15, marginTop: 15 }}>
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
                            <Text style={{ fontSize: 7, color: '#94a3b8' }}>參與市民</Text>
                            <Text style={{ fontSize: 16, fontWeight: 'bold' }}>{data.genesis?.sample_size || comments.length || 0} 人</Text>
                        </View>
                        <View style={[styles.card, styles.col]}>
                            <Text style={{ fontSize: 7, color: '#94a3b8' }}>市場均價</Text>
                            <Text style={{ fontSize: 16, fontWeight: 'bold' }}>${data.market_prices?.avg_price || productPrice}</Text>
                        </View>
                        <View style={[styles.card, styles.col]}>
                            <Text style={{ fontSize: 7, color: '#94a3b8' }}>轉換潛力</Text>
                            <Text style={{ fontSize: 16, fontWeight: 'bold', color: score >= 80 ? '#10b981' : '#f59e0b' }}>
                                {score >= 80 ? 'HIGH' : score >= 60 ? 'MED' : 'LOW'}
                            </Text>
                        </View>
                    </View>

                    {/* Footer */}
                    <View style={styles.coverFooter}>
                        <Text style={styles.footerText}>REPORT ID: {data.id?.slice(0, 8) || 'SIM-PREVIEW'}</Text>
                        <Text style={styles.footerText}>{new Date().toLocaleDateString('zh-TW')} | MIRRA AI V2</Text>
                    </View>
                </View>
            </Page>

            {/* === PAGE 2: STRATEGIC ANALYSIS === */}
            <Page size="A4" style={[styles.page, styles.contentContainer]}>
                <View style={styles.pageHeader}>
                    <Text style={styles.pageTitle}>戰略神諭 STRATEGIC ORACLE</Text>
                    <Text style={{ color: '#94a3b8', fontSize: 9 }}>深度解析</Text>
                </View>

                {/* Main Analysis Content */}
                <View style={{ marginBottom: 15 }}>
                    {summaryParagraphs.slice(0, 6).map((para: string, idx: number) => {
                        const isStrategic = para.includes("[戰略]") || para.includes("戰略建議") || para.includes("建議");
                        return (
                            <View key={idx} style={isStrategic ? styles.strategyBox : { marginBottom: 10 }}>
                                {isStrategic && <Text style={{ fontSize: 9, color: '#a855f7', fontWeight: 'bold', marginBottom: 3 }}>STRATEGY</Text>}
                                <Text style={styles.strategyText}>{para}</Text>
                            </View>
                        )
                    })}
                </View>

                {/* Action Plan / Suggestions */}
                {suggestions.length > 0 && (
                    <View>
                        <Text style={styles.sectionTitle}>執行戰術 ACTION PLAN</Text>
                        {suggestions.slice(0, 3).map((s: any, i: number) => (
                            <View key={i} style={styles.card}>
                                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 3 }}>
                                    <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#22d3ee' }}>{s.target || '戰術目標'}</Text>
                                    {s.score_improvement && <Text style={{ fontSize: 8, color: '#10b981' }}>{s.score_improvement}</Text>}
                                </View>
                                <Text style={[styles.personaText, { marginBottom: 5 }]}>{s.advice}</Text>
                                {s.execution_plan && s.execution_plan.length > 0 && (
                                    <View style={{ paddingLeft: 6, borderLeftWidth: 1, borderLeftColor: '#475569', marginTop: 3 }}>
                                        {s.execution_plan.slice(0, 3).map((step: string, k: number) => (
                                            <Text key={k} style={{ fontSize: 8, color: '#94a3b8', marginBottom: 2 }}>• {step}</Text>
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
                    <Text style={{ color: '#94a3b8', fontSize: 9 }}>精選反饋</Text>
                </View>

                <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' }}>
                    {comments.slice(0, 8).map((comment: any, i: number) => {
                        const isPos = comment.sentiment === 'positive';
                        const isNeg = comment.sentiment === 'negative';
                        const borderColor = isPos ? '#10b981' : isNeg ? '#ef4444' : '#475569';
                        const elemMap: Record<string, string> = { "Fire": "火", "Water": "水", "Metal": "金", "Wood": "木", "Earth": "土" };
                        const elem = elemMap[comment.persona?.element] || "命";
                        const localizedName = getLocalizedValue(comment.persona?.name, language);
                        const localizedJob = getLocalizedValue(comment.persona?.occupation, language);

                        return (
                            <View key={i} style={[styles.personaCard, { width: '48%', borderLeftColor: borderColor }]}>
                                <View style={styles.personaHeader}>
                                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                                        <View style={{ width: 14, height: 14, borderRadius: 7, backgroundColor: borderColor, alignItems: 'center', justifyContent: 'center' }}>
                                            <Text style={{ fontSize: 7, color: '#fff' }}>{elem}</Text>
                                        </View>
                                        <Text style={styles.personaName}>{localizedName || '匿名'}</Text>
                                    </View>
                                    <Text style={[styles.badge, isPos ? styles.positiveBadge : isNeg ? styles.negativeBadge : styles.neutralBadge]}>
                                        {isPos ? 'POS' : isNeg ? 'NEG' : 'NEU'}
                                    </Text>
                                </View>
                                <Text style={{ fontSize: 7, color: '#64748b', marginBottom: 3 }}>
                                    {comment.persona?.age}歲 | {localizedJob || '市民'} | {comment.persona?.pattern || '格局未知'}
                                </Text>
                                <Text style={styles.personaText}>
                                    &quot;{(comment.text || '').slice(0, 120)}{(comment.text || '').length > 120 ? '...' : ''}&quot;
                                </Text>
                            </View>
                        );
                    })}
                </View>

                <Text style={styles.pageNumber} render={({ pageNumber, totalPages }) => `${pageNumber} / ${totalPages}`} fixed />
            </Page>

            {/* === PAGE 4: MORE VOICES (if > 8 comments) === */}
            {comments.length > 8 && (
                <Page size="A4" style={[styles.page, styles.contentContainer]}>
                    <View style={styles.pageHeader}>
                        <Text style={styles.pageTitle}>更多市民心聲</Text>
                        <Text style={{ color: '#94a3b8', fontSize: 9 }}>延續反饋</Text>
                    </View>

                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' }}>
                        {comments.slice(8, 16).map((comment: any, i: number) => {
                            const isPos = comment.sentiment === 'positive';
                            const isNeg = comment.sentiment === 'negative';
                            const borderColor = isPos ? '#10b981' : isNeg ? '#ef4444' : '#475569';
                            const elemMap: Record<string, string> = { "Fire": "火", "Water": "水", "Metal": "金", "Wood": "木", "Earth": "土" };
                            const elem = elemMap[comment.persona?.element] || "命";
                            const localizedName = getLocalizedValue(comment.persona?.name, language);
                            const localizedJob = getLocalizedValue(comment.persona?.occupation, language);

                            return (
                                <View key={i} style={[styles.personaCard, { width: '48%', borderLeftColor: borderColor }]}>
                                    <View style={styles.personaHeader}>
                                        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
                                            <View style={{ width: 14, height: 14, borderRadius: 7, backgroundColor: borderColor, alignItems: 'center', justifyContent: 'center' }}>
                                                <Text style={{ fontSize: 7, color: '#fff' }}>{elem}</Text>
                                            </View>
                                            <Text style={styles.personaName}>{localizedName || '匿名'}</Text>
                                        </View>
                                        <Text style={[styles.badge, isPos ? styles.positiveBadge : isNeg ? styles.negativeBadge : styles.neutralBadge]}>
                                            {isPos ? 'POS' : isNeg ? 'NEG' : 'NEU'}
                                        </Text>
                                    </View>
                                    <Text style={{ fontSize: 7, color: '#64748b', marginBottom: 3 }}>
                                        {comment.persona?.age}歲 | {localizedJob || '市民'}
                                    </Text>
                                    <Text style={styles.personaText}>
                                        &quot;{(comment.text || '').slice(0, 120)}{(comment.text || '').length > 120 ? '...' : ''}&quot;
                                    </Text>
                                </View>
                            );
                        })}
                    </View>

                    <Text style={styles.pageNumber} render={({ pageNumber, totalPages }) => `${pageNumber} / ${totalPages}`} fixed />
                </Page>
            )}
        </Document>
    );
};

export default SimulationReportPDF;
