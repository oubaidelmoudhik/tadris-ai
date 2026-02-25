export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// French teacher info structure
export interface TeacherInfoFR {
  Nom: string;
  PPR: string;
  "Année Scolaire": string;
  Établissement: string;
  Niveau: string;
}

// Arabic teacher info structure
export interface TeacherInfoAR {
  Professor: string;
  "رقم التأجير": string;
  "السنة الدراسية": string;
  المؤسسة: string;
  المستوى: string;
}

export interface TeacherInfo {
  fr: TeacherInfoFR;
  ar: TeacherInfoAR;
}

// For internal state management
export interface TeacherInfoData {
  [key: string]: string | number;
}

export interface CsvData {
  [key: string]: string | number;
}

export interface LessonResponse {
  title: string;
  lesson_data: Record<string, unknown>;
  pdf_path: string | null;
}

export interface UploadLessonResponse {
  message: string;
  lesson_id: number;
  title: string;
  subject: string;
  level: string;
  period: string;
  week: string;
  session: string;
}

// ====================
// Auth Types
// ====================

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface AuthTokens {
  refresh: string;
  access: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

// ====================
// Auth Functions
// ====================

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

async function fetchWithAuth(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const response = await fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  return response;
}

export async function login(
  credentials: LoginCredentials
): Promise<AuthResponse> {
  const response = await fetchWithAuth(`${API_URL}/auth/login/`, {
    method: "POST",
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Login failed");
  }

  return (await response.json()) as AuthResponse;
}

export async function register(data: RegisterData): Promise<AuthResponse> {
  const response = await fetchWithAuth(`${API_URL}/auth/register/`, {
    method: "POST",
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.username?.[0] || error.email?.[0] || "Registration failed");
  }

  return (await response.json()) as AuthResponse;
}

export async function logout(refreshToken: string): Promise<void> {
  const response = await fetchWithAuth(`${API_URL}/auth/logout/`, {
    method: "POST",
    body: JSON.stringify({ refresh: refreshToken }),
  });

  // Even if server fails, we clear local tokens
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    console.warn("Logout warning:", error.message);
  }
}

export async function getCurrentUser(accessToken: string): Promise<User> {
  const response = await fetchWithAuth(`${API_URL}/auth/me/`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to get user");
  }

  return (await response.json()) as User;
}

export async function refreshAccessToken(
  refreshToken: string
): Promise<AuthTokens> {
  const response = await fetchWithAuth(`${API_URL}/auth/refresh/`, {
    method: "POST",
    body: JSON.stringify({ refresh: refreshToken }),
  });

  if (!response.ok) {
    throw new Error("Token refresh failed");
  }

  const data = (await response.json()) as { tokens: AuthTokens };
  return data.tokens;
}

// ====================
// Lesson Functions
// ====================

export async function generateLesson(
  formData: FormData
): Promise<LessonResponse> {
  const response = await fetch(`${API_URL}/lessons/generate/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Unknown error during generation");
  }

  return (await response.json()) as LessonResponse;
}

export async function uploadLesson(
  file: File
): Promise<UploadLessonResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/lessons/upload/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Failed to upload lesson");
  }

  return (await response.json()) as UploadLessonResponse;
}

export async function downloadPDF(filename: string): Promise<void> {
  const response = await fetch(`${API_URL}/lessons/pdf/${filename}/`);
  if (!response.ok) throw new Error("PDF not found");

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}
