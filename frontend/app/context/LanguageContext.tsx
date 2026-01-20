"use client"

import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations, Language } from '../lib/translations';

type LanguageContextType = {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string) => string;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [language, setLanguage] = useState<Language>('zh-TW');

    useEffect(() => {
        // Load saved language or default to zh-TW
        const savedLang = localStorage.getItem('mirra-lang') as Language;
        if (savedLang && (savedLang === 'zh-TW' || savedLang === 'zh-CN' || savedLang === 'en')) {
            setLanguage(savedLang);
        }
    }, []);

    const handleSetLanguage = (lang: Language) => {
        setLanguage(lang);
        localStorage.setItem('mirra-lang', lang);
    };

    // Translation helper function
    // Supports nested keys like 'home.title'
    const t = (key: string) => {
        const keys = key.split('.');
        let value: any = translations[language];

        for (const k of keys) {
            value = value?.[k];
            if (!value) return key; // Fallback to key if not found
        }

        return value as string;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
