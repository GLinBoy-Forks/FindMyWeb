import { type Location } from "./FindMyWeb.ts";

const dateTimeFormatter = new Intl.DateTimeFormat([], {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "numeric",
  minute: "numeric",
  second: "numeric",
});

const base64regex =
  /^([0-9a-zA-Z+/]{4})*(([0-9a-zA-Z+/]{2}==)|([0-9a-zA-Z+/]{3}=))?$/;

const base64Bytes28regex = /^[0-9a-zA-Z+/]{38}==$/;
const base64Bytes32regex = /^[0-9a-zA-Z+/]{43}=$/;

const hexBytes28regex = /^[0-9a-fA-F]{56}$/;
const hexBytes32regex = /^[0-9a-fA-F]{64}$/;

export async function locationDate(location: Location): Promise<Date | null> {
  if (!location.timestamp) {
    return null;
  }
  // Append 'Z' so ts knows this is a UTC date
  return new Date(location.timestamp + "Z");
}

export async function locationDateString(location: Location): Promise<string> {
  const date = await locationDate(location);
  if (!date) {
    return "No timestamp";
  }
  return dateTimeFormatter.format(date);
}

export async function isBase64(str: string) {
  return str.match(base64regex);
}

export async function isBytes28Base64(str: string) {
  return str.match(base64Bytes28regex);
}

export async function isBytes32Base64(str: string) {
  return str.match(base64Bytes32regex);
}

export async function isBytes28Hex(str: string) {
  return str.match(hexBytes28regex);
}

export async function isBytes32Hex(str: string) {
  return str.match(hexBytes32regex);
}

export function hexToBase64(str: string) {
  var bytes = "";
  for (var i = 0; i < str.length; i += 2) {
    bytes += String.fromCharCode(parseInt(str.slice(i, i + 2), 16));
  }
  return btoa(bytes);
}
