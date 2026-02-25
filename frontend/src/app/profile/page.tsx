"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import { API_URL, TeacherInfo } from "../../lib/api";
import { translations } from "../../lib/translations";
import { useLanguage } from "../../context/LanguageContext";
import { useAuth } from "../../context/AuthContext";

// Define interface for the flat API response
interface TeacherInfoData {
  user: number;
  ppr: string;
  annee_scolaire: string;
  nom: string;
  etablissement: string;
  niveau: string;
  nom_ar: string;
  etablissement_ar: string;
  niveau_ar: string;
  updated_at: string;
}

export default function ProfilePage() {
  const { language } = useLanguage();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const t = (key: string) => translations[language][key] || key;

  const [info, setInfo] = useState<TeacherInfo>({
    fr: {
      Nom: "",
      PPR: "",
      "Année Scolaire": "",
      Établissement: "",
      Niveau: "",
    },
    ar: {
      Professor: "",
      "رقم التأجير": "",
      "السنة الدراسية": "",
      المؤسسة: "",
      المستوى: "",
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleSharedChange = (fieldKey: "PPR" | "Year", value: string) => {
    setInfo((prev) => {
        const newInfo = { ...prev };
        if (fieldKey === "PPR") {
            newInfo.fr.PPR = value;
            newInfo.ar["رقم التأجير"] = value;
        } else if (fieldKey === "Year") {
            newInfo.fr["Année Scolaire"] = value;
            newInfo.ar["السنة الدراسية"] = value;
        }
        return newInfo;
    });
  };

  const handleFrChange = (field: keyof TeacherInfo["fr"], value: string) => {
    setInfo((prev) => ({
      ...prev,
      fr: { ...prev.fr, [field]: value },
    }));
  };

  const handleArChange = (field: keyof TeacherInfo["ar"], value: string) => {
    setInfo((prev) => ({
      ...prev,
      ar: { ...prev.ar, [field]: value },
    }));
  };

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
      return;
    }

    if (isAuthenticated) {
      const token = Cookies.get("access_token");
      fetch(`${API_URL}/teacher-info/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
        .then((res) => {
          if (!res.ok) throw new Error("Server error");
          return res.json();
        })
        .then((data: TeacherInfoData) => {
          if (data) {
            setInfo({
              fr: { 
                Nom: data.nom || "", 
                PPR: data.ppr || "",
                "Année Scolaire": data.annee_scolaire || "",
                Établissement: data.etablissement || "",
                Niveau: data.niveau || "",
              },
              ar: { 
                Professor: data.nom_ar || "", 
                "رقم التأجير": data.ppr || "",
                "السنة الدراسية": data.annee_scolaire || "",
                المؤسسة: data.etablissement_ar || "",
                المستوى: data.niveau_ar || "",
              },
            });
          }
        })
        .catch((err) => console.error("Failed to load info", err))
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated, authLoading, router]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    
    if (!info.fr.Nom.trim() && !info.ar.Professor.trim()) {
        setMessage(t("fillNameError"));
        setSaving(false);
        return;
    }

    const token = Cookies.get("access_token");
    
    // Convert to flat format for API
    const payload = {
      fr: info.fr,
      ar: {
        Professor: info.ar.Professor,
        "رقم التأجير": info.ar["رقم التأجير"],
        "السنة الدراسية": info.ar["السنة الدراسية"],
        المؤسسة: info.ar.المؤسسة,
        المستوى: info.ar.المستوى,
      },
    };
    
    try {
      const res = await fetch(`${API_URL}/teacher-info/`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setMessage(t("profileSaved"));
      } else {
        setMessage(t("failedSave"));
      }
    } catch {
      setMessage(t("errorSaving"));
    } finally {
      setSaving(false);
    }
  };

  if (loading || authLoading) return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center">
      <div className="p-10 text-center text-gray-700 dark:text-gray-300">{t("loading")}</div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <main className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">{t("profileTitle")}</h2>
            <p className="mb-6 text-gray-600 dark:text-gray-400">
                {t("profileDescription")}
            </p>

            {message && (
                <div className={`mb-6 p-4 rounded-lg ${message.includes("success") || message === t("profileSaved") ? "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400" : "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-400"}`}>
                    {message}
                </div>
            )}

            {/* Shared Info Section */}
            <div className="mb-8 p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
                
                <div className="grid md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            {t("ppr")}
                        </label>
                        <input
                            type="text"
                            value={info.fr.PPR}
                            onChange={(e) => handleSharedChange("PPR", e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                            placeholder="123456"
                            dir="ltr" 
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            {t("schoolYear")}
                        </label>
                        <input
                            type="text"
                            value={info.fr["Année Scolaire"]}
                            onChange={(e) => handleSharedChange("Year", e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                            placeholder="202X/202X"
                            dir="ltr"
                        />
                    </div>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                {/* French Section */}
                <div dir="ltr">
                    <h2 className="text-xl font-bold text-blue-600 dark:text-blue-400 mb-4 border-b border-gray-200 dark:border-gray-600 pb-2 flex items-center gap-2">
                        <span>🇫🇷</span> {t("frenchSection")}
                    </h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Nom <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                value={info.fr.Nom}
                                onChange={(e) => handleFrChange("Nom", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="Nom"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Établissement
                            </label>
                            <input
                                type="text"
                                value={info.fr.Établissement}
                                onChange={(e) => handleFrChange("Établissement", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="Établissement"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Niveau
                            </label>
                            <input
                                type="text"
                                value={info.fr.Niveau}
                                onChange={(e) => handleFrChange("Niveau", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="Niveau"
                            />
                        </div>
                    </div>
                </div>

                {/* Arabic Section */}
                <div dir="rtl">
                    <h2 className="text-xl font-bold text-green-600 dark:text-green-400 mb-4 border-b border-gray-200 dark:border-gray-600 pb-2 flex items-center gap-2">
                        <span>🇲🇦</span> {t("arabicSection")}
                    </h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                الأستاذ <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                value={info.ar.Professor}
                                onChange={(e) => handleArChange("Professor", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="الأستاذ"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                المؤسسة
                            </label>
                            <input
                                type="text"
                                value={info.ar.المؤسسة}
                                onChange={(e) => handleArChange("المؤسسة", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="المؤسسة"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                المستوى
                            </label>
                            <input
                                type="text"
                                value={info.ar.المستوى}
                                onChange={(e) => handleArChange("المستوى", e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400"
                                placeholder="المستوى"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-8 flex justify-center">
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {saving ? t("saving") : t("saveProfile")}
                </button>
            </div>
        </div>
      </main>
    </div>
  );
}
