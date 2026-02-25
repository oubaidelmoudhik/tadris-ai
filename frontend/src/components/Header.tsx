import Link from "next/link";
import { Translations } from "../lib/translations";

interface HeaderProps {
  language: "fr" | "ar";
  toggleLanguage: () => void;
  translations: Translations;
}

export default function Header({ language, toggleLanguage, translations }: HeaderProps) {
  const t = (key: string) => translations[language][key] || key;
  // const isRtl = language === "ar";
  
  return (
    <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-100 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          
          {/* Left Side: Logo & Title */}
          <div className="flex items-center gap-3">
             <Link href="/">
                <div className="bg-gradient-to-tr from-blue-600 to-indigo-600 p-2 rounded-lg shadow-md cursor-pointer hover:opacity-90 transition-opacity">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                </div>
             </Link>
             <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent hidden sm:block">
                  {t("appTitle")}
                </h1>
             </div>
          </div>
          
          {/* Right Side: Actions */}
          <div className="flex items-center gap-4">
            
            {/* Home Link (Accueil) - Only visible if not already on home? User requested "logo-accueil...". Let's add it. */}
             <Link 
              href="/"
              className="p-2 rounded-full hover:bg-gray-100 text-gray-600 hover:text-blue-600 transition-colors"
              title={language === 'fr' ? "Accueil" : "الرئيسية"}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </Link>

            <Link 
              href="/profile"
              className="p-2 rounded-full hover:bg-gray-100 text-gray-600 hover:text-blue-600 transition-colors"
              title={t("profileTitle")}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </Link>

            <button
              onClick={toggleLanguage}
              className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium transition-colors text-sm flex items-center gap-2"
            >
              <span>{language === "fr" ? "🇫🇷" : "🇲🇦"}</span>
              <span className="hidden sm:inline">{language === "fr" ? "FR" : "AR"}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
