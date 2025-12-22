// JavaScript/TypeScript Client für Auth Service

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
}

export interface UserProfile {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  is_active: boolean;
  is_verified: boolean;
  date_joined: string;
  last_login: string;
}

export interface Tokens {
  access: string;
  refresh: string;
}

export interface PermissionsResponse {
  user_id: string;
  user_email: string;
  website_id: string | null;
  website_name: string | null;
  global_permissions: string[];
  local_permissions: string[];
  roles: string[];
}

export class AuthServiceClient {
  private baseUrl: string;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.loadTokensFromStorage();
  }

  /**
   * Lädt Tokens aus dem localStorage
   */
  private loadTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  /**
   * Speichert Tokens im localStorage
   */
  private saveTokensToStorage(): void {
    if (typeof window !== 'undefined') {
      if (this.accessToken) {
        localStorage.setItem('access_token', this.accessToken);
      }
      if (this.refreshToken) {
        localStorage.setItem('refresh_token', this.refreshToken);
      }
    }
  }

  /**
   * Entfernt Tokens aus dem localStorage
   */
  private clearTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  /**
   * Gibt die HTTP-Header mit Authorization zurück
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    return headers;
  }

  /**
   * Macht eine HTTP-Anfrage mit automatischem Token-Refresh
   */
  private async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    let response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    // Token abgelaufen? Versuche zu erneuern
    if (response.status === 401 && this.refreshToken) {
      await this.refreshAccessToken();
      
      // Anfrage wiederholen mit neuem Token
      response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(JSON.stringify(error));
    }

    return response.json();
  }

  /**
   * Registriert einen neuen Benutzer
   */
  async register(data: RegisterData): Promise<{ user: UserProfile; tokens: Tokens; message: string }> {
    const response = await this.request<{ user: UserProfile; tokens: Tokens; message: string }>(
      `${this.baseUrl}/api/accounts/register/`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );

    this.accessToken = response.tokens.access;
    this.refreshToken = response.tokens.refresh;
    this.saveTokensToStorage();

    return response;
  }

  /**
   * Meldet einen Benutzer an
   */
  async login(credentials: LoginCredentials): Promise<Tokens> {
    const tokens = await this.request<Tokens>(
      `${this.baseUrl}/api/accounts/login/`,
      {
        method: 'POST',
        body: JSON.stringify(credentials),
      }
    );

    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
    this.saveTokensToStorage();

    return tokens;
  }

  /**
   * Meldet den aktuellen Benutzer ab
   */
  async logout(): Promise<{ message: string }> {
    const response = await this.request<{ message: string }>(
      `${this.baseUrl}/api/accounts/logout/`,
      {
        method: 'POST',
        body: JSON.stringify({ refresh: this.refreshToken }),
      }
    );

    this.accessToken = null;
    this.refreshToken = null;
    this.clearTokensFromStorage();

    return response;
  }

  /**
   * Erneuert den Access Token
   */
  async refreshAccessToken(): Promise<string> {
    const response = await fetch(`${this.baseUrl}/api/accounts/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: this.refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    this.accessToken = data.access;
    this.saveTokensToStorage();

    return this.accessToken;
  }

  /**
   * Ruft das Benutzerprofil ab
   */
  async getProfile(): Promise<UserProfile> {
    return this.request<UserProfile>(`${this.baseUrl}/api/accounts/profile/`);
  }

  /**
   * Aktualisiert das Benutzerprofil
   */
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return this.request<UserProfile>(`${this.baseUrl}/api/accounts/profile/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  /**
   * Ändert das Passwort
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `${this.baseUrl}/api/accounts/change-password/`,
      {
        method: 'POST',
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
          new_password2: newPassword,
        }),
      }
    );
  }

  /**
   * Prüft den Zugriff auf eine Website
   */
  async verifyAccess(websiteId: string): Promise<{
    has_access: boolean;
    user: UserProfile;
    website: any;
  }> {
    return this.request(
      `${this.baseUrl}/api/accounts/verify-access/`,
      {
        method: 'POST',
        body: JSON.stringify({ website_id: websiteId }),
      }
    );
  }

  /**
   * Ruft alle Berechtigungen des Benutzers ab
   */
  async getAllPermissions(websiteId?: string): Promise<PermissionsResponse> {
    let url = `${this.baseUrl}/api/permissions/check/me/`;
    if (websiteId) {
      url += `?website_id=${websiteId}`;
    }

    return this.request<PermissionsResponse>(url);
  }

  /**
   * Prüft eine spezifische Berechtigung
   */
  async checkPermission(
    permissionCodename: string,
    websiteId?: string
  ): Promise<boolean> {
    const data: any = { permission_codename: permissionCodename };
    if (websiteId) {
      data.website_id = websiteId;
    }

    const response = await this.request<{ has_permission: boolean }>(
      `${this.baseUrl}/api/permissions/check-permission/`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );

    return response.has_permission;
  }

  /**
   * Prüft ob der Benutzer eingeloggt ist
   */
  isAuthenticated(): boolean {
    return this.accessToken !== null;
  }

  /**
   * Gibt den aktuellen Access Token zurück
   */
  getAccessToken(): string | null {
    return this.accessToken;
  }

  /**
   * Gibt den aktuellen Refresh Token zurück
   */
  getRefreshToken(): string | null {
    return this.refreshToken;
  }
}

// Singleton-Instanz exportieren
export const authClient = new AuthServiceClient();

// Default Export
export default AuthServiceClient;
