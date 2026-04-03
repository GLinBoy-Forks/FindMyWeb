import { jwtDecode } from "jwt-decode";
import type { Middleware } from "openapi-fetch";
import createClient from "openapi-fetch";
import { type ErrorResponse } from "openapi-typescript-helpers";

import type { paths, components } from "./schema.d.ts";

export const API_BASE_URL = import.meta.env.VITE_API_URL;

export type Location = components["schemas"]["Location"];

export type Accessory = components["schemas"]["Accessory"];
export type LocationInfo =
  | components["schemas"]["FruityTagLocationInfo"]
  | null;
export type UserInfo = components["schemas"]["UserInfo"];

export enum AccessoryType {
  FRUITYTAG_STATIC = "FruityTagStatic",
  FRUITYTAG_ROLLING = "FruityTagRolling",
}

export enum BatteryLevel {
  Full = "Full",
  Medium = "Medium",
  Low = "Low",
  Critical = "Critical",
  Unknown = "Unknown",
}

export enum LocationType {
  BASIC = "Basic",
  FRUITYTAG = "FruityTag",
}

export enum Permissions {
  USER = 0b0,
  ADMIN = 0b1,
}

export type TokenData = {
  userid: string;
  username: string;
  permissions: number;
};

type HTTPValidationError = components["schemas"]["HTTPValidationError"];

type AccessoriesResponse =
  paths["/api/accessory"]["get"]["responses"]["200"]["content"]["application/json"];

type CreateAccessoryOptions =
  paths["/api/accessory"]["post"]["requestBody"]["content"]["application/json"];

type CreateAccessoryResponse =
  paths["/api/accessory"]["post"]["responses"]["200"]["content"]["application/json"];

type GetAccessoryResponse =
  paths["/api/accessory/{id}"]["get"]["responses"]["200"]["content"]["application/json"];

type RemoveAccessoryResponse =
  paths["/api/accessory/{id}"]["delete"]["responses"]["200"]["content"]["application/json"];

type UpdateAccessoryResponse =
  paths["/api/accessory/{id}"]["post"]["responses"]["200"]["content"]["application/json"];
type UpdateAccessoryOptions =
  paths["/api/accessory/{id}"]["post"]["requestBody"]["content"]["application/json"];

type GetLocationResponse =
  paths["/api/location/{accessory_id}"]["get"]["responses"]["200"]["content"]["application/json"];

type GetLocationInfoResponse =
  paths["/api/location/info/{accessory_id}/{location_id}"]["get"]["responses"]["200"]["content"]["application/json"];

type GetLocationsResponse =
  paths["/api/location/duration/{accessory_id}"]["post"]["responses"]["200"]["content"]["application/json"];

type LoginUserResponse =
  paths["/api/login"]["post"]["responses"]["200"]["content"]["application/json"];

type LogoutUserResponse =
  paths["/api/login"]["delete"]["responses"]["200"]["content"]["application/json"];
// @ts-ignore
type LoginRefreshResponse =
  paths["/api/login/refresh"]["get"]["responses"]["200"]["content"]["application/json"];

type GetUsersResponse =
  paths["/api/user/list"]["get"]["responses"]["200"]["content"]["application/json"];

type CreateUserResponse =
  paths["/api/user/create"]["post"]["responses"]["200"]["content"]["application/json"];

type RemoveUserResponse =
  paths["/api/user/{id}"]["delete"]["responses"]["200"]["content"]["application/json"];

type UpdateUserResponse =
  paths["/api/user/{id}"]["post"]["responses"]["200"]["content"]["application/json"];

type ChangePasswordResponse =
  paths["/api/user/change_password"]["post"]["responses"]["200"]["content"]["application/json"];

const client = createClient<paths>({ baseUrl: API_BASE_URL });

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

export class FileData {
  blob: Blob;
  filename: string;
  constructor(blob: Blob, filename: string) {
    this.blob = blob;
    this.filename = filename;
  }
}

function decodePermissions(perm: number): Array<number> {
  let perms: Array<number> = [];
  for (let key in Permissions) {
    if (!isNaN(Number(key))) {
      continue;
    }
    let value = Number(Permissions[key]);
    if (perm & value) {
      perms.push(value);
    }
  }
  return perms;
}

export function hasPermission(
  permsission_num: number,
  permission: Permissions,
): boolean {
  const permissions = decodePermissions(permsission_num);
  return permissions.includes(permission);
}

async function setToken(token: string | null) {
  if (!token) {
    localStorage.removeItem("token");
  } else {
    localStorage.setItem("token", token);
  }
}

async function getToken(): Promise<string> {
  let token = localStorage.getItem("token");
  if (token == null) {
    throw new Error("Token was not found in local storage");
  }
  return token;
}

const UNPROTECTED_ROUTES = ["/api/login/refresh"];

const authMiddleware: Middleware = {
  async onRequest({ schemaPath, request }) {
    if (
      UNPROTECTED_ROUTES.some((pathname) => schemaPath.startsWith(pathname)) ||
      (request.method == "POST" && schemaPath == "/api/login")
    ) {
      return undefined;
    }
    const jwt = jwtDecode(await getToken());
    var current_time = Date.now() / 1000;
    if (jwt.exp && jwt.exp < current_time) {
      const {
        data,
        error: fetchError,
        // @ts-ignore
        response,
      } = await client.GET("/api/login/refresh");
      if (fetchError) {
        await setToken(null);
        return undefined;
      }
      await setToken(data.access_token);
    }
    request.headers.set("Authorization", `Bearer ${await getToken()}`);
    return request;
  },
};

client.use(authMiddleware);

export default class FindMyWeb {
  constructor() {}
  async _decodeJWT(): Promise<TokenData | null> {
    let decoded = null;
    try {
      decoded = jwtDecode(await getToken());
    } catch (error) {
      return null;
    }
    return decoded as TokenData;
  }

  async _httpValidationErrorToString(error: HTTPValidationError) {
    if (!error.detail) {
      return "Unknown error occured :(";
    } else if (typeof error.detail == "string") {
      return error.detail;
    }

    let text = "";
    for (let i = 0; i < error.detail.length; i++) {
      let detail = error.detail[i];
      text += `- ${detail.msg} (${detail.type}) at `;
      if (!detail.loc) {
        continue;
      }
      for (let x = 0; x < detail.loc.length; x++) {
        text += `/${detail.loc[x]}`;
      }
      if (i < error.detail.length) {
        text += "\n";
      }
    }
    return text;
  }

  async _verifyResponse<T>(
    data: T | undefined,
    error: ErrorResponse<any>,
    response: Response,
  ): Promise<T> {
    if (error) {
      let detailStr = "Unknown";
      if ((error.detail as HTTPValidationError) !== undefined) {
        detailStr = await this._httpValidationErrorToString(error);
      }
      throw new FindMyWebError(response.statusText, response.status, detailStr);
    }
    if (!data) {
      throw new FindMyWebError(
        "Unexpected error occured",
        500,
        "Endpoint didn't return any data but response was successful",
      );
    }
    return data as T;
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
    return jwt.username;
  }

  async userHasPermission(permission: Permissions) {
    const jwt = await this._decodeJWT();
    if (!jwt) {
      throw new FindMyWebError(
        "Couldn't decode jwt",
        404,
        "Couldn't decode jwt",
      );
    }
    return hasPermission(jwt.permissions, permission);
  }
  async login(username: string, password: string): Promise<LoginUserResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/login", {
      body: {
        password: password,
        username: username,
        scope: "client",
      },
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    const responseData = await this._verifyResponse<LoginUserResponse>(
      data,
      fetchError,
      response,
    );
    await setToken(responseData.access_token);
    return responseData;
  }

  async logout() {
    const {
      data,
      error: fetchError,
      response,
    } = await client.DELETE("/api/login", {});
    await setToken(null);
    await this._verifyResponse<LogoutUserResponse>(data, fetchError, response);
  }

  async getAccessories(): Promise<AccessoriesResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.GET("/api/accessory", {});
    return await this._verifyResponse<AccessoriesResponse>(
      data,
      fetchError,
      response,
    );
  }

  async getAccessory(accessoryID: string): Promise<GetAccessoryResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.GET("/api/accessory/{id}", {
      params: {
        path: {
          id: accessoryID,
        },
      },
    });
    return await this._verifyResponse<GetAccessoryResponse>(
      data,
      fetchError,
      response,
    );
  }

  async getLocations(
    accessoryID: string,
    startDate: Date,
    endDate: Date,
  ): Promise<GetLocationsResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/location/duration/{accessory_id}", {
      params: {
        path: {
          accessory_id: accessoryID,
        },
      },
      body: {
        start: startDate.toISOString(),
        end: endDate.toISOString(),
      },
    });
    return await this._verifyResponse<GetLocationsResponse>(
      data,
      fetchError,
      response,
    );
  }

  async getLocationInfo(
    accessoryID: string,
    locationID: string,
  ): Promise<GetLocationInfoResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.GET("/api/location/info/{accessory_id}/{location_id}", {
      params: {
        path: {
          accessory_id: accessoryID,
          location_id: locationID,
        },
      },
    });
    return await this._verifyResponse<GetLocationInfoResponse>(
      data,
      fetchError,
      response,
    );
  }

  async getLastLocation(accessoryID: string): Promise<GetLocationResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.GET("/api/location/{accessory_id}", {
      params: {
        path: {
          accessory_id: accessoryID,
        },
      },
    });
    return await this._verifyResponse<GetLocationResponse>(
      data,
      fetchError,
      response,
    );
  }

  async createAccessory(
    accessoryOptions: CreateAccessoryOptions,
  ): Promise<CreateAccessoryResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/accessory", {
      body: accessoryOptions,
    });
    return await this._verifyResponse<CreateAccessoryResponse>(
      data,
      fetchError,
      response,
    );
  }

  async updateAccessory(
    accessoryID: string,
    accessoryOptions: UpdateAccessoryOptions,
  ): Promise<UpdateAccessoryResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/accessory/{id}", {
      params: {
        path: {
          id: accessoryID,
        },
      },
      body: accessoryOptions,
    });
    return await this._verifyResponse<UpdateAccessoryResponse>(
      data,
      fetchError,
      response,
    );
  }

  async updatePassword(
    oldPassword: string,
    newPassword: string,
  ): Promise<ChangePasswordResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/user/change_password", {
      body: {
        old_password: oldPassword,
        new_password: newPassword,
      },
    });
    return await this._verifyResponse<ChangePasswordResponse>(
      data,
      fetchError,
      response,
    );
  }

  async removeAccessory(accessoryID: string): Promise<RemoveAccessoryResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.DELETE("/api/accessory/{id}", {
      params: {
        path: {
          id: accessoryID,
        },
      },
    });
    return await this._verifyResponse<RemoveAccessoryResponse>(
      data,
      fetchError,
      response,
    );
  }

  async getUsers(): Promise<GetUsersResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.GET("/api/user/list", {});
    return await this._verifyResponse<GetUsersResponse>(
      data,
      fetchError,
      response,
    );
  }

  async createUser(
    name: string,
    password: string,
    permissions: components["schemas"]["Permissions"],
  ): Promise<CreateUserResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/user/create", {
      body: {
        name: name,
        password: password,
        permissions: permissions,
      },
    });
    return await this._verifyResponse<CreateUserResponse>(
      data,
      fetchError,
      response,
    );
  }

  async deleteUser(id: string): Promise<RemoveUserResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.DELETE("/api/user/{id}", {
      params: {
        path: {
          id: id,
        },
      },
    });
    return await this._verifyResponse<RemoveUserResponse>(
      data,
      fetchError,
      response,
    );
  }

  async updateUser(
    id: string,
    name: string | null = null,
    password: string | null = null,
    permissions: components["schemas"]["Permissions"] | null = null,
  ): Promise<UpdateUserResponse> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/user/{id}", {
      params: {
        path: {
          id: id,
        },
      },
      body: {
        name: name,
        password: password,
        permissions: permissions,
      },
    });
    return await this._verifyResponse<UpdateUserResponse>(
      data,
      fetchError,
      response,
    );
  }

  async exportGPX(
    accessoryID: string,
    startDate: Date,
    endDate: Date,
  ): Promise<FileData> {
    const {
      data,
      error: fetchError,
      response,
    } = await client.POST("/api/export/gpx/{accessory_id}", {
      params: {
        path: {
          accessory_id: accessoryID,
        },
      },
      body: {
        start: startDate.toISOString(),
        end: endDate.toISOString(),
      },
      parseAs: "blob",
    });
    const responseBlob = await this._verifyResponse<Blob>(
      data,
      fetchError,
      response,
    );

    if (!responseBlob) {
      throw new FindMyWebError(
        "No GPX data provided",
        null,
        "Server didn't return any data",
      );
    }
    let fileName = `${accessoryID}.gpx`;
    let contentDisposition = response?.headers.get("content-disposition");
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?(.+?)"?$/);
      if (match != null && match.length === 2) {
        fileName = match[1];
        fileName = fileName.replace(/\+/g, "%20");
        fileName = decodeURIComponent(fileName);
      }
    }
    return new FileData(responseBlob, fileName);
  }
}
