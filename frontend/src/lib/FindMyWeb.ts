import { jwtDecode, type JwtPayload } from "jwt-decode";

export const API_BASE_URL = import.meta.env.VITE_API_URL;

export class FindMyWebError extends Error {
  detail_str: string;
  status_code: number | null;

  constructor(message: string, statusCode: number | null, detail: string) {
    super(message);
    this.name = "FindMyWebError";
    this.status_code = statusCode;
    this.detail_str = detail;
    Object.setPrototypeOf(this, FindMyWebError.prototype);
  }

  detail(): string {
    return this.detail_str;
  }
  statusCode(): number | null {
    return this.status_code;
  }
}

export enum BatteryLevel {
  Full = 0b00,
  Medium = 0b01,
  Low = 0b10,
  Critical = 0b11,
}

export class Location {
  id?: string;
  lat?: number;
  lon?: number;
  timestamp?: string;
  battery_level?: BatteryLevel;
  status?: number;
  confidence?: number;
  horizontal_accuracy?: number;
  accessory_key?: string;
}

export class BasicLocation {
  id?: string;
  lat?: number;
  lon?: number;
  timestamp?: string;
}

export class Accessory {
  private_key?: string;
  name?: string;
  color?: string;
  icon?: string;
  user_id?: string;
}

export class CreateAccessoryOptions {
  name: string;
  color: string;
  icon: string;
  private_key: string | null = null;
  constructor(
    name: string,
    color: string,
    icon: string,
    private_key: string | null = null,
  ) {
    this.name = name;
    this.color = color;
    this.icon = icon;
    this.private_key = private_key;
  }
}

export class AccessoriesResponse {
  accessories?: Accessory[];
}

export class AccessoryResponse {
  accessory?: Accessory;
}

export class AdvertisementResponse {
  advertisement_key?: string;
}

export class LocationsResponse {
  locations?: BasicLocation[];
}

export class LocationResponse {
  location?: Location;
}

export class PrivateKeyResponse {
  private_key?: string;
}

export class UserInfo {
  name?: string;
  is_admin?: boolean;
  superuser?: boolean;
}

export class UsersResponse {
  users?: UserInfo[];
}

export default class FindMyWeb {
  private baseUrl: string;
  private tokenRefresh: boolean;

  constructor() {
    this.baseUrl = API_BASE_URL;
    this.tokenRefresh = false;
  }

  async _parseJwt(token: string) {
    var base64Url = token.split(".")[1];
    var base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    var jsonPayload = decodeURIComponent(
      window
        .atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join(""),
    );

    return JSON.parse(jsonPayload);
  }

  async _verifyResponse(response: Response | null) {
    if (!response) {
      throw new FindMyWebError(`No request sent`, null, "No request sent");
    }

    if (!response.ok) {
      let responseJs = await response.json();
      let errorDetail = responseJs.detail
        ? responseJs.detail
        : "No error provided by API";
      throw new FindMyWebError(
        `Error sending request to ${response.url}: ${response.statusText}`,
        response.status,
        errorDetail,
      );
    }
  }

  async _get<T>(sub_url: string, shouldRefresh: boolean = true): Promise<T> {
    let response = null;
    for (let i = 0; i < 2; i++) {
      response = await fetch(`${this.baseUrl}/${sub_url}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${await this.getToken()}`,
        },
      });
      if (response.status == 401 && shouldRefresh) {
        await this.refreshToken();
        continue;
      }
      break;
    }

    await this._verifyResponse(response);

    return (await response?.json()) as T;
  }

  async _delete(
    sub_url: string,
    shouldRefresh: boolean = true,
  ): Promise<boolean> {
    let response = null;
    for (let i = 0; i < 2; i++) {
      response = await fetch(`${this.baseUrl}/${sub_url}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${await this.getToken()}`,
        },
      });
      if (response.status == 401 && shouldRefresh) {
        await this.refreshToken();
        continue;
      }
      break;
    }

    await this._verifyResponse(response);

    return true;
  }

  async _post<T>(sub_url: string, body: any, shouldRefresh: boolean = true) {
    let response = null;
    for (let i = 0; i < 2; i++) {
      response = await fetch(`${this.baseUrl}/${sub_url}`, {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${await this.getToken()}`,
        },
      });
      if (response.status == 401 && shouldRefresh) {
        await this.refreshToken();
        continue;
      }
      break;
    }
    await this._verifyResponse(response);

    return (await response?.json()) as T;
  }

  async _decodeJWT(): Promise<JwtPayload | null> {
    let decoded = null;
    try {
      decoded = jwtDecode(await this.getToken());
    } catch (error) {
      return null;
    }
    return decoded;
  }

  async getUsername(): Promise<string> {
    const jwt = await this._decodeJWT();
    if (!jwt) {
      throw new FindMyWebError(
        "Couldn't decode jwt",
        404,
        "Couldn't decode jwt",
      );
    }
    // @ts-ignore: Property does not exist on type
    return jwt.username;
  }

  async isAdmin(): Promise<boolean> {
    const jwt = await this._decodeJWT();
    if (!jwt) {
      throw new FindMyWebError(
        "Couldn't decode jwt",
        404,
        "Couldn't decode jwt",
      );
    }
    // @ts-ignore: Property does not exist on type
    return jwt.is_admin;
  }

  async setToken(token: string) {
    if (!token) {
      throw new Error("API didn't provide a token");
    }
    localStorage.setItem("token", token);
  }

  async getToken(): Promise<string> {
    while (this.tokenRefresh) {
      await new Promise((f) => setTimeout(f, 10));
    }

    let token = localStorage.getItem("token");
    if (token == null) {
      throw new Error("Token was not found in local storage");
    }
    return token;
  }

  async refreshToken() {
    if (this.tokenRefresh) {
      return;
    }

    this.tokenRefresh = true;
    try {
      const response = await fetch(`${this.baseUrl}/login/refresh`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const responseJSON = await response.json();
      const token = responseJSON["access_token"];
      await this.setToken(token);
    } finally {
      this.tokenRefresh = false;
    }
  }

  async login(username: string, password: string): Promise<any> {
    const data = new FormData();
    data.append("username", username);
    data.append("password", password);

    const response = await fetch(`${this.baseUrl}/login`, {
      method: "POST",
      body: data,
    });

    if (!response.ok) {
      throw new Error("Login failed: " + response.statusText);
    }

    const responseJSON = await response.json();

    const token = responseJSON["access_token"];
    await this.setToken(token);

    return token;
  }

  async logout() {
    await this._delete("login");
    localStorage.removeItem("token");
  }

  async getAccessories(): Promise<AccessoriesResponse> {
    return await this._get<AccessoriesResponse>("accessory");
  }

  async getAccessory(accessoryName: string): Promise<AccessoryResponse> {
    return await this._post<AccessoryResponse>(`accessory`, {
      name: accessoryName,
    });
  }

  async getLocations(
    accessoryName: string,
    startDate: Date,
    endDate: Date,
  ): Promise<LocationsResponse> {
    return await this._post<LocationsResponse>(`location/duration`, {
      name: accessoryName,
      start: startDate.toISOString(),
      end: endDate.toISOString(),
    });
  }

  async getLocation(
    accessoryName: string,
    locationId: string | undefined = undefined,
  ): Promise<LocationResponse> {
    return await this._post<LocationResponse>(`location`, {
      name: accessoryName,
      location_id: locationId,
    });
  }

  async getPrivateKey(): Promise<PrivateKeyResponse> {
    return await this._get<PrivateKeyResponse>(`accessory/privatekey`);
  }

  async getAdvertisementKey(name: string): Promise<AdvertisementResponse> {
    return await this._post<AdvertisementResponse>(`accessory/advertisement`, {
      name: name,
    });
  }

  async createAccessory(
    accessoryOptions: CreateAccessoryOptions,
  ): Promise<Accessory> {
    return await this._post("accessory/create", accessoryOptions);
  }

  async updateAccessory(
    accessoryOptions: CreateAccessoryOptions,
  ): Promise<Accessory> {
    return await this._post("accessory/update", accessoryOptions);
  }

  async updatePassword(oldPassword: string, newPassword: string) {
    await this._post("user/change_password", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  }

  async removeAccessory(accessoryName: string) {
    return await this._post("accessory/remove", { name: accessoryName });
  }

  async getUsers(): Promise<UsersResponse> {
    return await this._get("user/list");
  }

  async createUser(name: string, password: string, isAdmin: boolean) {
    return await this._post("user/create", {
      name: name,
      password: password,
      is_admin: isAdmin,
    });
  }

  async deleteUser(name: string) {
    return await this._post("user/remove", { name: name });
  }

  async updateUser(name: string, password: string, isAdmin: boolean) {
    return await this._post("user/update", {
      name: name,
      password: password,
      is_admin: isAdmin,
    });
  }
}
