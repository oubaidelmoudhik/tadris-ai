"use client";

import { useLanguage } from "../context/LanguageContext";
import { useTheme } from "../context/ThemeContext";
import { translations } from "../lib/translations";

export default function Footer() {
  const { language } = useLanguage();
  const { resolvedTheme, theme, setTheme } = useTheme();
  const t = (key: string) => translations[language][key] || key;
  
  const cycleTheme = () => {
    if (theme === "light") {
      setTheme("dark");
    } else if (theme === "dark") {
      setTheme("system");
    } else {
      setTheme("light");
    }
  };

  const getThemeIcon = () => {
    if (theme === "system") {
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      );
    }
    return resolvedTheme === "dark" ? (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    ) : (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
    );
  };

  const getThemeLabel = () => {
    if (theme === "system") return t("systemTheme");
    return resolvedTheme === "dark" ? t("darkMode") : t("lightMode");
  };

  return (
    <footer className="bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm border-t border-gray-100 dark:border-gray-800 mt-auto transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {language === "fr" 
              ? "Tadris AI - Générateur de Leçons" 
              : "Tadris AI - مولد الدروس"}
          </p>
          
          {/* Theme Toggle Button */}
          <button
            onClick={cycleTheme}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium transition-colors text-sm"
            title={t("switchTheme")}
          >
            {getThemeIcon()}
            <span className="hidden sm:inline">{getThemeLabel()}</span>
          </button>
        </div>
      </div>
    </footer>
  );
}
